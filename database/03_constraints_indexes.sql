-- HireSight: indexes for the analysis queries
-- Load AFTER 02_create_tables.sql AND after the data load (faster bulk insert),
-- or before it -- both work; indexes build incrementally either way.

USE hiresight;

-- Foreign-key lookup columns (MySQL/InnoDB auto-creates FK indexes; kept explicit
-- so the intent is documented and identical on engines that do not).

-- Funnel / time-based queries
CREATE INDEX idx_app_applied_at ON applications (applied_at);
CREATE INDEX idx_app_status     ON applications (current_status);
CREATE INDEX idx_app_candidate  ON applications (candidate_id);
CREATE INDEX idx_app_job         ON applications (job_id);
CREATE INDEX idx_app_source      ON applications (source_id);

CREATE INDEX idx_stage_app       ON application_stage_history (application_id);
CREATE INDEX idx_stage_name      ON application_stage_history (stage_name, stage_status);
CREATE INDEX idx_stage_timestamp ON application_stage_history (stage_timestamp);

CREATE INDEX idx_screen_app      ON screening_results (application_id);
CREATE INDEX idx_screen_date     ON screening_results (screening_date);

CREATE INDEX idx_offer_app       ON offers (application_id);
CREATE INDEX idx_offer_status    ON offers (offer_status);

-- Source cost aggregation
CREATE INDEX idx_cost_source_month ON source_costs (source_id, month_start);

-- Job listing filters
CREATE INDEX idx_jobs_dept      ON jobs (department);
CREATE INDEX idx_jobs_posted    ON jobs (posted_date);
