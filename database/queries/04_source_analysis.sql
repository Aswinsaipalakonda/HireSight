-- ============================================================================
-- 04_source_analysis.sql — channel volume, conversion, time-to-hire, cost
-- All conversion metrics use applications as the unit; source_id = 8
-- ('Unknown / Not Recorded') is a cleaning artefact and excluded from
-- channel comparisons.
-- ============================================================================

USE hiresight;

-- ----------------------------------------------------------------------------
-- Q1. Which sources generate the most applications?
SELECT s.source_name, s.source_category,
       COUNT(a.application_id) AS applications
FROM applications a
JOIN recruitment_sources s ON a.source_id = s.source_id
WHERE s.source_id <> 8
GROUP BY s.source_name, s.source_category
ORDER BY applications DESC;

-- ----------------------------------------------------------------------------
-- Q2. Which sources have the highest application-to-hire conversion?
-- Interpretation: Referral and agency channels typically lead; always read
-- conversion next to volume (Q1) — small channels convert on luck.
SELECT s.source_name,
       COUNT(a.application_id) AS applications,
       SUM(a.current_status = 'hired') AS hires,
       ROUND(100.0 * SUM(a.current_status = 'hired') / COUNT(*), 2) AS app_to_hire_pct
FROM applications a
JOIN recruitment_sources s ON a.source_id = s.source_id
WHERE s.source_id <> 8
GROUP BY s.source_name
ORDER BY app_to_hire_pct DESC;

-- ----------------------------------------------------------------------------
-- Q3. Which sources have the shortest median time-to-hire?
-- Interpretation: Median, not mean — time-to-hire is right-skewed. Sources
-- below are 'faster to close' given their hires.
WITH hired_apps AS (
    SELECT a.application_id, a.source_id,
           TIMESTAMPDIFF(DAY, a.applied_at,
               (SELECT h.stage_timestamp FROM application_stage_history h
                WHERE h.application_id = a.application_id AND h.stage_name = 'hired'
                LIMIT 1)) AS days_to_hire
    FROM applications a
    WHERE a.current_status = 'hired'
),
ranked AS (
    SELECT sr.source_name, days_to_hire,
           ROW_NUMBER() OVER (PARTITION BY a.source_id ORDER BY days_to_hire) AS rn,
           COUNT(*) OVER (PARTITION BY a.source_id) AS n
    FROM hired_apps a
    JOIN recruitment_sources sr ON sr.source_id = a.source_id
)
SELECT source_name,
       ROUND(AVG(CASE WHEN rn IN (FLOOR(n/2), FLOOR(n/2)+1) THEN days_to_hire END), 1) AS median_days_to_hire
FROM ranked
GROUP BY source_name
ORDER BY median_days_to_hire;

-- ----------------------------------------------------------------------------
-- Q4. What is the offer acceptance rate by source?
-- Interpretation: Denominator excludes pending offers (no final response yet).
SELECT s.source_name,
       COUNT(o.offer_id) AS offers_decided,
       SUM(o.offer_status = 'accepted') AS accepted,
       ROUND(100.0 * SUM(o.offer_status = 'accepted') / COUNT(o.offer_id), 1) AS acceptance_pct
FROM offers o
JOIN applications a ON a.application_id = o.application_id
JOIN recruitment_sources s ON s.source_id = a.source_id
WHERE s.source_id <> 8
  AND o.offer_status <> 'pending'
GROUP BY s.source_name
ORDER BY acceptance_pct DESC;

-- ----------------------------------------------------------------------------
-- Q5. Which sources have the lowest cost per hire?
-- Interpretation: Attribution assumption — a hire's cost is the spend of its
-- source in the calendar month of the hire. Cost per hire = that spend / hires
-- that month. Costs are simulated; treat as a method demonstration.
WITH monthly_cost AS (
    SELECT source_id, MONTH(month_start) AS mo,
           SUM(cost_inr) AS month_cost
    FROM source_costs
    WHERE source_id <> 8
    GROUP BY source_id, MONTH(month_start)
),
monthly_hires AS (
    SELECT a.source_id, MONTH(h.stage_timestamp) AS mo,
           COUNT(DISTINCT a.application_id) AS hires
    FROM applications a
    JOIN application_stage_history h
         ON h.application_id = a.application_id AND h.stage_name = 'hired'
    WHERE a.source_id <> 8
    GROUP BY a.source_id, MONTH(h.stage_timestamp)
)
SELECT s.source_name,
       SUM(mc.month_cost) AS total_cost_inr,
       SUM(mh.hires) AS hires,
       ROUND(SUM(mc.month_cost) / SUM(mh.hires), 0) AS cost_per_hire_inr
FROM monthly_cost mc
JOIN monthly_hires mh ON mh.source_id = mc.source_id AND mh.mo = mc.mo
JOIN recruitment_sources s ON s.source_id = mc.source_id
GROUP BY s.source_name
ORDER BY cost_per_hire_inr;

-- ----------------------------------------------------------------------------
-- Q6. Which paid channels give the best hire yield per 100 applications?
-- Interpretation: A compact 'value for volume' view combining volume,
-- conversion and cost, for budget conversations.
SELECT s.source_name, s.source_category,
       COUNT(a.application_id) AS applications,
       SUM(a.current_status = 'hired') AS hires,
       ROUND(100.0 * SUM(a.current_status = 'hired') / COUNT(*), 1) AS hires_per_100_apps
FROM applications a
JOIN recruitment_sources s ON s.source_id = a.source_id
WHERE s.source_category = 'paid'
GROUP BY s.source_name, s.source_category
ORDER BY hires_per_100_apps DESC;
