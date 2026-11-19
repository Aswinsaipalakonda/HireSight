-- ============================================================================
-- 05_time_to_hire.sql — duration analytics (mean AND median)
-- Rule: only hired applications count. Median is preferred for reporting
-- because time-to-hire is right-skewed; both are shown per PRD 10.1.
-- ============================================================================

USE hiresight;

-- ----------------------------------------------------------------------------
-- Q1. What are the overall mean and median days-to-hire?
-- Interpretation: If mean >> median, a few very slow hires drag the average.
WITH hired AS (
    SELECT a.application_id,
           TIMESTAMPDIFF(DAY, a.applied_at, h.stage_timestamp) AS days_to_hire
    FROM applications a
    JOIN application_stage_history h
         ON h.application_id = a.application_id AND h.stage_name = 'hired'
),
ranked AS (
    SELECT days_to_hire,
           ROW_NUMBER() OVER (ORDER BY days_to_hire) AS rn,
           COUNT(*) OVER () AS n
    FROM hired
)
SELECT
    (SELECT COUNT(*) FROM hired) AS hired_apps,
    (SELECT ROUND(AVG(days_to_hire), 1) FROM hired) AS mean_days,
    (SELECT ROUND(AVG(CASE WHEN rn IN (FLOOR(n/2), FLOOR(n/2)+1) THEN days_to_hire END), 1)
     FROM ranked) AS median_days;

-- ----------------------------------------------------------------------------
-- Q2. How is time-to-hire distributed (10-day buckets)?
-- Interpretation: Shows the skew and the slow tail explicitly.
WITH hired AS (
    SELECT TIMESTAMPDIFF(DAY, a.applied_at, h.stage_timestamp) AS d
    FROM applications a
    JOIN application_stage_history h
         ON h.application_id = a.application_id AND h.stage_name = 'hired'
)
SELECT
    CASE
        WHEN d <= 10 THEN '1-10 days'
        WHEN d <= 20 THEN '11-20 days'
        WHEN d <= 30 THEN '21-30 days'
        WHEN d <= 45 THEN '31-45 days'
        WHEN d <= 60 THEN '46-60 days'
        ELSE '60+ days'
    END AS days_bucket,
    COUNT(*) AS hires
FROM hired
GROUP BY days_bucket
ORDER BY MIN(d);

-- ----------------------------------------------------------------------------
-- Q3. Which departments hire fastest (median)?
WITH hired AS (
    SELECT j.department,
           TIMESTAMPDIFF(DAY, a.applied_at, h.stage_timestamp) AS d
    FROM applications a
    JOIN jobs j ON j.job_id = a.job_id
    JOIN application_stage_history h
         ON h.application_id = a.application_id AND h.stage_name = 'hired'
),
ranked AS (
    SELECT department, d,
           ROW_NUMBER() OVER (PARTITION BY department ORDER BY d) AS rn,
           COUNT(*) OVER (PARTITION BY department) AS n
    FROM hired
)
SELECT department,
       ROUND(AVG(CASE WHEN rn IN (FLOOR(n/2), FLOOR(n/2)+1) THEN d END), 1) AS median_days,
       ROUND(AVG(d), 1) AS mean_days
FROM ranked
GROUP BY department
ORDER BY median_days;

-- ----------------------------------------------------------------------------
-- Q4. Which jobs or departments have the longest total in-process delay
--     before the offer stage?
-- Interpretation: Offer delay = applied_at to offer-stage event; long delays
--     flag slow coordination rather than candidate problems.
WITH offer_stage AS (
    SELECT a.application_id, j.department,
           TIMESTAMPDIFF(DAY, a.applied_at, h.stage_timestamp) AS d
    FROM applications a
    JOIN jobs j ON j.job_id = a.job_id
    JOIN application_stage_history h
         ON h.application_id = a.application_id AND h.stage_name = 'offer'
),
ranked AS (
    SELECT department, d,
           ROW_NUMBER() OVER (PARTITION BY department ORDER BY d) AS rn,
           COUNT(*) OVER (PARTITION BY department) AS n
    FROM offer_stage
)
SELECT department,
       COUNT(*) AS offers,
       ROUND(AVG(CASE WHEN rn IN (FLOOR(n/2), FLOOR(n/2)+1) THEN d END), 1) AS median_days_to_offer
FROM ranked
GROUP BY department
ORDER BY median_days_to_offer DESC;

-- ----------------------------------------------------------------------------
-- Q5. Did the mid-year score-version change coincide with different hiring
--     delays? (pre/post July 2026 comparison)
-- Interpretation: Descriptive only — this is a before/after snapshot, not a
-- causal claim about the scoring version.
WITH hired AS (
    SELECT a.application_id,
           a.applied_at < '2026-07-01' AS before_july,
           TIMESTAMPDIFF(DAY, a.applied_at, h.stage_timestamp) AS d
    FROM applications a
    JOIN application_stage_history h
         ON h.application_id = a.application_id AND h.stage_name = 'hired'
),
ranked AS (
    SELECT before_july, d,
           ROW_NUMBER() OVER (PARTITION BY before_july ORDER BY d) AS rn,
           COUNT(*) OVER (PARTITION BY before_july) AS n
    FROM hired
)
SELECT before_july,
       COUNT(*) AS hires,
       ROUND(AVG(d), 1) AS mean_days,
       ROUND(AVG(CASE WHEN rn IN (FLOOR(n/2), FLOOR(n/2)+1) THEN d END), 1) AS median_days
FROM ranked
GROUP BY before_july;
