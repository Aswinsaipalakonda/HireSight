-- ============================================================================
-- 03_funnel_analysis.sql — stage counts, conversion, drop-off
-- Definitions (see docs/metric_definitions.md):
--   * Stage reach is COUNT(DISTINCT application_id) — stage history is
--     event-grain, so unguarded joins multiply rows.
--   * Active applications (screening/interview/offer) are NOT drop-offs.
--   * Pre-screen withdrawals appear as a second 'applied/withdrawn' event and
--     must not double the applied count.
-- ============================================================================

USE hiresight;

-- ----------------------------------------------------------------------------
-- Q1. How many distinct applications reached each funnel stage?
-- Interpretation: The classic funnel shape. Applied = 8,000; each later stage
-- can only shrink. 'rejected' stage events duplicate failures already visible
-- at screened/interview, so read the funnel from applied -> screened ->
-- interview -> offer -> hired.
SELECT h.stage_name,
       COUNT(DISTINCT h.application_id) AS distinct_applications
FROM application_stage_history h
GROUP BY h.stage_name
ORDER BY FIELD(h.stage_name, 'applied', 'screened', 'interview', 'offer', 'hired');

-- ----------------------------------------------------------------------------
-- Q2. What are the stage-to-stage conversion rates?
-- Interpretation: Entry-denominator conversion. The biggest percentage loss
-- between consecutive stages is the primary bottleneck to investigate.
WITH stage_reach AS (
    SELECT application_id,
           MAX(stage_name = 'applied')   AS reached_applied,
           MAX(stage_name = 'screened')  AS reached_screened,
           MAX(stage_name = 'interview') AS reached_interview,
           MAX(stage_name = 'offer')     AS reached_offer,
           MAX(stage_name = 'hired')     AS reached_hired
    FROM application_stage_history
    GROUP BY application_id
)
SELECT
    COUNT(*) AS applications,
    SUM(reached_screened)  AS n_screened,
    ROUND(100.0 * SUM(reached_screened)  / COUNT(*), 1) AS applied_to_screened_pct,
    SUM(reached_interview) AS n_interview,
    ROUND(100.0 * SUM(reached_interview) / NULLIF(SUM(reached_screened), 0), 1) AS screened_to_interview_pct,
    SUM(reached_offer)     AS n_offer,
    ROUND(100.0 * SUM(reached_offer)     / NULLIF(SUM(reached_interview), 0), 1) AS interview_to_offer_pct,
    SUM(reached_hired)     AS n_hired,
    ROUND(100.0 * SUM(reached_hired)     / NULLIF(SUM(reached_offer), 0), 1) AS offer_to_hire_pct
FROM stage_reach;

-- ----------------------------------------------------------------------------
-- Q3. How many applications dropped out at each stage (final outcomes)?
-- Interpretation: current_status stores the canonical final outcome, so this
-- counts applications, not events. Active statuses are excluded from drop-off
-- by definition.
SELECT current_status,
       COUNT(*) AS applications,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM applications), 1) AS pct_of_all
FROM applications
GROUP BY current_status
ORDER BY applications DESC;

-- ----------------------------------------------------------------------------
-- Q4. Which stage has the largest candidate drop-off, by department?
-- Interpretation: Compare WHERE people exit, not just how many. A department
-- losing most candidates at screening has a different problem than one losing
-- them at offer.
WITH last_stage AS (
    SELECT a.application_id, j.department, a.current_status,
           (SELECT h2.stage_name
            FROM application_stage_history h2
            WHERE h2.application_id = a.application_id
            ORDER BY h2.stage_event_id DESC
            LIMIT 1) AS last_stage_name
    FROM applications a
    JOIN jobs j ON a.job_id = j.job_id
)
SELECT department, last_stage_name AS exit_stage, COUNT(*) AS applications
FROM last_stage
WHERE current_status IN ('rejected', 'withdrawn', 'declined')
GROUP BY department, last_stage_name
ORDER BY department, applications DESC;

-- ----------------------------------------------------------------------------
-- Q5. How many applications are still active at each current stage?
-- Interpretation: Live recruiter workload. These candidates are waiting —
-- never labelled drop-offs.
SELECT current_status AS active_stage, COUNT(*) AS applications
FROM applications
WHERE current_status IN ('screening', 'interview', 'offer')
GROUP BY current_status
ORDER BY applications DESC;

-- ----------------------------------------------------------------------------
-- Q6. What is the median hours spent in each stage (completed transitions)?
-- Interpretation: Median (not mean) because stage durations are right-skewed.
-- Long median screening times flag slow first response.
WITH stage_durations AS (
    SELECT h.stage_name, h.stage_status,
           PERCENT_RANK() OVER (PARTITION BY h.stage_name ORDER BY h.stage_duration_hours) AS pr,
           h.stage_duration_hours
    FROM application_stage_history h
    WHERE h.stage_duration_hours IS NOT NULL
)
SELECT stage_name,
       ROUND(AVG(CASE WHEN pr BETWEEN 0.4995 AND 0.5005 THEN stage_duration_hours END), 1) AS approx_median_hours
FROM stage_durations
GROUP BY stage_name
ORDER BY approx_median_hours DESC;

-- ----------------------------------------------------------------------------
-- Q7. Which departments have the longest median screening delays?
-- Interpretation: Screening delay = hours between the 'applied' and 'screened'
-- events of the same application. The median is used because delays are
-- right-skewed.
WITH screen_gap AS (
    SELECT j.department,
           TIMESTAMPDIFF(HOUR, h1.stage_timestamp, h2.stage_timestamp) AS gap_hours
    FROM application_stage_history h1
    JOIN application_stage_history h2
         ON h2.application_id = h1.application_id AND h2.stage_name = 'screened'
    JOIN applications a ON a.application_id = h1.application_id
    JOIN jobs j         ON j.job_id = a.job_id
    WHERE h1.stage_name = 'applied' AND h1.stage_status = 'entered'
),
ranked AS (
    SELECT department, gap_hours,
           ROW_NUMBER() OVER (PARTITION BY department ORDER BY gap_hours) AS rn,
           COUNT(*) OVER (PARTITION BY department) AS n
    FROM screen_gap
)
SELECT department,
       ROUND(AVG(CASE WHEN rn IN (FLOOR(n/2), FLOOR(n/2)+1) THEN gap_hours END), 1) AS median_screen_delay_hours
FROM ranked
GROUP BY department
ORDER BY median_screen_delay_hours DESC;
