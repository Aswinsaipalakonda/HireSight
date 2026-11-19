-- ============================================================================
-- 02_joins_aggregations.sql — multi-table joins, GROUP BY, HAVING, aggregates
-- ============================================================================

USE hiresight;

-- ----------------------------------------------------------------------------
-- Q1. Which departments have the highest application volume?
-- Interpretation: Technology and Sales typically dominate; that is where
-- screening capacity should be allocated first.
SELECT j.department, COUNT(a.application_id) AS applications,
       COUNT(DISTINCT a.candidate_id)       AS unique_candidates
FROM applications a
JOIN jobs j ON a.job_id = j.job_id
GROUP BY j.department
ORDER BY applications DESC;

-- ----------------------------------------------------------------------------
-- Q2. What are average and median offered salaries by department?
-- Interpretation: LEFT JOIN keeps departments that made no offers; their
-- aggregates show as NULL rather than disappearing (an INNER JOIN would hide
-- hiring gaps).
SELECT j.department,
       COUNT(o.offer_id)                       AS offers,
       ROUND(AVG(o.offered_salary_inr), 0)     AS avg_salary_inr,
       MIN(o.offered_salary_inr)                AS min_salary_inr,
       MAX(o.offered_salary_inr)                AS max_salary_inr
FROM jobs j
LEFT JOIN applications a ON a.job_id = j.job_id
LEFT JOIN offers o       ON o.application_id = a.application_id
GROUP BY j.department
ORDER BY offers DESC;

-- ----------------------------------------------------------------------------
-- Q3. Which sources generate the most applications, and which categories do
--     they belong to?
-- Interpretation: Exclude source_id = 8 ('Unknown / Not Recorded') — those 15
-- rows are a data-quality artefact, not a real channel.
SELECT s.source_name, s.source_category,
       COUNT(a.application_id) AS applications
FROM recruitment_sources s
JOIN applications a ON a.source_id = s.source_id
WHERE s.source_id <> 8
GROUP BY s.source_name, s.source_category
ORDER BY applications DESC;

-- ----------------------------------------------------------------------------
-- Q4. Which jobs have hires but fewer than 50 applications?
-- Interpretation: Efficient niche roles — useful benchmarks for 'how easy can
-- hiring be' comparisons.
SELECT j.job_title, j.department,
       COUNT(a.application_id) AS applications,
       SUM(a.current_status = 'hired') AS hires
FROM jobs j
JOIN applications a ON a.job_id = j.job_id
GROUP BY j.job_title, j.department
HAVING hires > 0 AND applications < 50
ORDER BY applications DESC;

-- ----------------------------------------------------------------------------
-- Q5. How do application outcomes distribute by candidate education level?
-- Interpretation: NULL education values are retained (not imputed) and appear
-- as their own group; treat them as 'unknown', not a real education level.
SELECT c.highest_education,
       COUNT(*)                                     AS applications,
       SUM(a.current_status = 'hired')              AS hired,
       ROUND(100.0 * SUM(a.current_status = 'hired') / COUNT(*), 1) AS hire_rate_pct
FROM applications a
JOIN candidates c ON a.candidate_id = c.candidate_id
GROUP BY c.highest_education
ORDER BY applications DESC;

-- ----------------------------------------------------------------------------
-- Q6. How many screening passes, interviews, and offers did each department's
--     applications reach? (multi-stage reach, grain-safe)
-- Interpretation: COUNT(DISTINCT application_id) prevents stage-history row
-- multiplication — one application contributes at most 1 to each stage.
SELECT j.department,
       COUNT(DISTINCT a.application_id) AS applications,
       COUNT(DISTINCT CASE WHEN h.stage_name = 'screened' THEN a.application_id END) AS reached_screening,
       COUNT(DISTINCT CASE WHEN h.stage_name = 'interview' THEN a.application_id END) AS reached_interview,
       COUNT(DISTINCT CASE WHEN h.stage_name = 'offer'    THEN a.application_id END) AS reached_offer
FROM applications a
JOIN jobs j ON a.job_id = j.job_id
JOIN application_stage_history h ON h.application_id = a.application_id
GROUP BY j.department
ORDER BY applications DESC;

-- ----------------------------------------------------------------------------
-- Q7. Which employment types receive the highest share of withdrawals?
-- Interpretation: A high withdrawal share can signal slow processes or
-- competing offers.
SELECT j.employment_type,
       COUNT(*) AS applications,
       SUM(a.current_status = 'withdrawn') AS withdrawn,
       ROUND(100.0 * SUM(a.current_status = 'withdrawn') / COUNT(*), 1) AS withdraw_rate_pct
FROM applications a
JOIN jobs j ON a.job_id = j.job_id
GROUP BY j.employment_type
ORDER BY withdraw_rate_pct DESC;
