-- ============================================================================
-- 01_basic_queries.sql — SELECT / WHERE / ORDER BY / LIMIT fundamentals
-- Each query states its business question and how to read the output.
-- ============================================================================

USE hiresight;

-- ----------------------------------------------------------------------------
-- Q1. How many applications were received in total, and how many unique
--     candidates applied?
-- Interpretation: 8,000 applications came from 3,500 unique candidates, so the
-- average candidate applied to about 2.3 jobs.
SELECT COUNT(*)            AS total_applications,
       COUNT(DISTINCT candidate_id) AS unique_candidates
FROM applications;

-- ----------------------------------------------------------------------------
-- Q2. What were the 10 jobs with the most applications?
-- Interpretation: High-volume roles (typically Sales Executives and Data
-- Analysts) absorb the most screening effort.
SELECT j.job_title, j.department, COUNT(a.application_id) AS applications
FROM applications a
JOIN jobs j ON a.job_id = j.job_id
GROUP BY j.job_title, j.department
ORDER BY applications DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Q3. Which jobs received fewer than 50 applications (potential sourcing gaps)?
-- Interpretation: Low-volume roles may need broader sourcing or better employer
-- branding; compare with their time-to-hire before acting.
SELECT j.job_title, j.department, COUNT(a.application_id) AS applications
FROM jobs j
LEFT JOIN applications a ON a.job_id = j.job_id
GROUP BY j.job_title, j.department
HAVING applications < 50
ORDER BY applications ASC;

-- ----------------------------------------------------------------------------
-- Q4. How many applications are currently active (still in process) versus
--     finished, split by status?
-- Interpretation: 'screening', 'interview', and 'offer' are ACTIVE — never
-- count these candidates as drop-offs. Final states are rejected/withdrawn/
-- hired/declined.
SELECT current_status, COUNT(*) AS applications
FROM applications
GROUP BY current_status
ORDER BY applications DESC;

-- ----------------------------------------------------------------------------
-- Q5. How many jobs are open, closed, or on hold right now?
-- Interpretation: Open and on-hold jobs define live recruiter workload.
SELECT job_status, COUNT(*) AS jobs
FROM jobs
GROUP BY job_status
ORDER BY jobs DESC;

-- ----------------------------------------------------------------------------
-- Q6. Which full-time jobs pay above 1,000,000 INR at the top of the band?
-- Interpretation: Senior/expensive roles usually have longer funnels; compare
-- their time-to-hire with the company average in 05_time_to_hire.sql.
SELECT job_title, department, salary_min_inr, salary_max_inr
FROM jobs
WHERE employment_type = 'Full-time'
  AND salary_max_inr > 1000000
ORDER BY salary_max_inr DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Q7. How did application volume break down by month?
-- Interpretation: Notice the seasonal dips/spikes; monthly weight informs
-- recruiter capacity planning.
SELECT YEAR(applied_at) AS yr, MONTH(applied_at) AS mo, COUNT(*) AS applications
FROM applications
GROUP BY YEAR(applied_at), MONTH(applied_at)
ORDER BY yr, mo;

-- ----------------------------------------------------------------------------
-- Q8. What do the first 10 applications in the dataset look like (spot check)?
-- Interpretation: A quick sanity check that statuses and dates look reasonable
-- after loading.
SELECT a.application_id, c.candidate_id, j.job_title, s.source_name,
       a.applied_at, a.current_status
FROM applications a
JOIN candidates c ON a.candidate_id = c.candidate_id
JOIN jobs j       ON a.job_id = j.job_id
JOIN recruitment_sources s ON a.source_id = s.source_id
ORDER BY a.application_id
LIMIT 10;
