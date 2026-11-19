-- ============================================================================
-- 06_advanced_sql.sql — CTEs, subqueries, CASE pivots, window functions
-- Showcases ROW_NUMBER, RANK, LAG, and running totals on the hiring funnel.
-- ============================================================================

USE hiresight;

-- ----------------------------------------------------------------------------
-- Q1. Which jobs have the highest hires (with dense ranking, including ties)?
-- Interpretation: DENSE_RANK leaves no gaps after ties; RANK leaves gaps.
-- Use this for 'top N jobs' views where ties matter.
WITH job_hires AS (
    SELECT j.job_title, j.department,
           COUNT(DISTINCT a.application_id) AS hires
    FROM applications a
    JOIN jobs j ON j.job_id = a.job_id
    WHERE a.current_status = 'hired'
    GROUP BY j.job_title, j.department
)
SELECT job_title, department, hires,
       DENSE_RANK() OVER (ORDER BY hires DESC) AS hire_rank
FROM job_hires
ORDER BY hire_rank, job_title
LIMIT 15;

-- ----------------------------------------------------------------------------
-- Q2. Which jobs have high application volume but low conversion?
-- Interpretation: RANK applications descending, RANK conversion ascending,
-- and keep roles that are top-quartile volume AND bottom-quartile conversion:
-- these waste screening capacity.
WITH job_stats AS (
    SELECT j.job_title, j.department,
           COUNT(a.application_id) AS applications,
           ROUND(100.0 * SUM(a.current_status = 'hired') / COUNT(*), 2) AS hire_pct,
           RANK() OVER (ORDER BY COUNT(a.application_id) DESC) AS vol_rank,
           RANK() OVER (ORDER BY ROUND(100.0 * SUM(a.current_status = 'hired') / COUNT(*), 2) ASC) AS conv_rank
    FROM applications a
    JOIN jobs j ON j.job_id = a.job_id
    GROUP BY j.job_title, j.department
)
SELECT job_title, department, applications, hire_pct
FROM job_stats
WHERE vol_rank <= 15 AND conv_rank <= 15
ORDER BY applications DESC;

-- ----------------------------------------------------------------------------
-- Q3. How does screening score relate to interview progression (score bands)?
-- Interpretation: DESCRIPTIVE ONLY — synthetic scores with intentional
-- overlap. Association is not causation; a band is never 'good candidates'.
WITH score_bands AS (
    SELECT sr.application_id,
           CASE
               WHEN sr.ai_score >= 80 THEN '80-100'
               WHEN sr.ai_score >= 60 THEN '60-79'
               WHEN sr.ai_score >= 40 THEN '40-59'
               ELSE '0-39'
           END AS score_band
    FROM screening_results sr
)
SELECT sb.score_band,
       COUNT(DISTINCT sb.application_id) AS screened_apps,
       COUNT(DISTINCT CASE WHEN h.stage_name = 'interview' THEN sb.application_id END) AS reached_interview,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN h.stage_name = 'interview' THEN sb.application_id END)
             / COUNT(DISTINCT sb.application_id), 1) AS interview_rate_pct,
       COUNT(DISTINCT CASE WHEN h.stage_name = 'hired' THEN sb.application_id END) AS hires
FROM score_bands sb
LEFT JOIN application_stage_history h ON h.application_id = sb.application_id
GROUP BY sb.score_band
ORDER BY sb.score_band DESC;

-- ----------------------------------------------------------------------------
-- Q4. How many high-score candidates were NOT hired, and how many
--     lower-score candidates WERE hired?
-- Interpretation: These counts demonstrate that the score is far from decisive
-- in this synthetic data — overlap is intentional (PRD 6.5.4).
SELECT
    SUM(sr.ai_score >= 75 AND a.current_status <> 'hired') AS high_score_not_hired,
    SUM(sr.ai_score < 50 AND a.current_status = 'hired')   AS low_score_hired,
    COUNT(*) AS screened_apps
FROM screening_results sr
JOIN applications a ON a.application_id = sr.application_id;

-- ----------------------------------------------------------------------------
-- Q5. What is the month-over-month change in application volume (LAG)?
-- Interpretation: LAG(1) gives the previous month for the diff; big negative
-- diffs flag months needing capacity adjustments.
WITH monthly AS (
    SELECT YEAR(applied_at) AS yr, MONTH(applied_at) AS mo, COUNT(*) AS applications
    FROM applications
    GROUP BY YEAR(applied_at), MONTH(applied_at)
)
SELECT yr, mo, applications,
       LAG(applications) OVER (ORDER BY yr, mo) AS prev_month,
       applications - LAG(applications) OVER (ORDER BY yr, mo) AS change_vs_prev
FROM monthly;

-- ----------------------------------------------------------------------------
-- Q6. Cumulative hires by month (running total)?
-- Interpretation: The classic executive 'hiring pace' chart in SQL.
WITH monthly_hires AS (
    SELECT YEAR(h.stage_timestamp) AS yr, MONTH(h.stage_timestamp) AS mo,
           COUNT(DISTINCT h.application_id) AS hires
    FROM application_stage_history h
    WHERE h.stage_name = 'hired'
    GROUP BY YEAR(h.stage_timestamp), MONTH(h.stage_timestamp)
)
SELECT yr, mo, hires,
       SUM(hires) OVER (ORDER BY yr, mo) AS cumulative_hires
FROM monthly_hires;

-- ----------------------------------------------------------------------------
-- Q7. Top 3 most recent stage events per active application (ROW_NUMBER)?
-- Interpretation: The recruiter 'where is everyone right now' view. ROW_NUMBER
-- picks exactly the latest N events per application without fan-out.
WITH recent AS (
    SELECT a.application_id, j.job_title, h.stage_name, h.stage_status,
           h.stage_timestamp,
           ROW_NUMBER() OVER (PARTITION BY a.application_id
                              ORDER BY h.stage_event_id DESC) AS rn
    FROM applications a
    JOIN jobs j ON j.job_id = a.job_id
    JOIN application_stage_history h ON h.application_id = a.application_id
    WHERE a.current_status IN ('screening', 'interview', 'offer')
)
SELECT application_id, job_title, stage_name, stage_status, stage_timestamp
FROM recent
WHERE rn = 1
ORDER BY stage_timestamp
LIMIT 25;

-- ----------------------------------------------------------------------------
-- Q8. Which candidates applied the most times (repeat applicants)?
-- Interpretation: Repeat applicants show engagement; their final outcomes
-- indicate whether persistence pays off in this pipeline.
SELECT c.candidate_id, c.experience_years, COUNT(*) AS applications,
       SUM(a.current_status = 'hired') AS hires
FROM applications a
JOIN candidates c ON c.candidate_id = a.candidate_id
GROUP BY c.candidate_id, c.experience_years
HAVING applications >= 4
ORDER BY applications DESC, hires DESC;
