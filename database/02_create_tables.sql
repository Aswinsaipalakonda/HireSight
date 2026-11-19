-- HireSight: table definitions (PRD Section 8)
-- Load AFTER 01_create_database.sql. Grain-safe design:
--   * applications is the central fact table
--   * application_stage_history is event-grain (many rows per application)

USE hiresight;

CREATE TABLE candidates (
    candidate_id      INT           NOT NULL,
    experience_years  DECIMAL(4,1)  NULL,
    highest_education VARCHAR(60)   NULL,
    candidate_city    VARCHAR(80)   NOT NULL,
    created_at        DATETIME(6)   NOT NULL,
    PRIMARY KEY (candidate_id),
    CONSTRAINT chk_candidates_exp CHECK (experience_years IS NULL OR (experience_years >= 0 AND experience_years <= 20))
) ENGINE=InnoDB;

CREATE TABLE jobs (
    job_id           INT           NOT NULL,
    job_title        VARCHAR(120)  NOT NULL,
    department       VARCHAR(80)   NOT NULL,
    location         VARCHAR(80)   NOT NULL,
    employment_type  VARCHAR(40)   NOT NULL,
    salary_min_inr   DECIMAL(12,2)  NOT NULL,
    salary_max_inr   DECIMAL(12,2)  NOT NULL,
    posted_date      DATE          NOT NULL,
    closed_date      DATE          NULL,
    job_status       VARCHAR(30)   NOT NULL,
    PRIMARY KEY (job_id),
    CONSTRAINT chk_jobs_salary CHECK (salary_min_inr > 0 AND salary_max_inr >= salary_min_inr),
    CONSTRAINT chk_jobs_status CHECK (job_status IN ('open', 'closed', 'on hold')),
    CONSTRAINT chk_jobs_dates  CHECK (closed_date IS NULL OR closed_date >= posted_date)
) ENGINE=InnoDB;

CREATE TABLE recruitment_sources (
    source_id       INT          NOT NULL,
    source_name     VARCHAR(80)  NOT NULL,
    source_category VARCHAR(50)  NOT NULL,
    PRIMARY KEY (source_id)
) ENGINE=InnoDB;

CREATE TABLE applications (
    application_id INT          NOT NULL,
    candidate_id    INT          NOT NULL,
    job_id          INT          NOT NULL,
    source_id       INT          NOT NULL,
    applied_at      DATETIME(6)  NOT NULL,
    current_status  VARCHAR(30) NOT NULL,
    PRIMARY KEY (application_id),
    CONSTRAINT fk_app_candidate FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id),
    CONSTRAINT fk_app_job       FOREIGN KEY (job_id)       REFERENCES jobs (job_id),
    CONSTRAINT fk_app_source    FOREIGN KEY (source_id)    REFERENCES recruitment_sources (source_id),
    CONSTRAINT chk_app_status CHECK (current_status IN
        ('screening', 'interview', 'offer', 'rejected', 'withdrawn', 'hired', 'declined'))
) ENGINE=InnoDB;

-- source_id = 8 ("Unknown / Not Recorded") exists in the processed data, so the
-- NOT NULL + FK design still holds; the cleaning pipeline resolved missing sources.

CREATE TABLE screening_results (
    screening_id       INT          NOT NULL,
    application_id     INT          NOT NULL,
    screening_date     DATETIME(6)  NOT NULL,
    ai_score           DECIMAL(5,2) NOT NULL,
    screening_decision VARCHAR(30)  NOT NULL,
    score_version      VARCHAR(30)  NOT NULL,
    PRIMARY KEY (screening_id),
    CONSTRAINT fk_screen_app FOREIGN KEY (application_id) REFERENCES applications (application_id),
    CONSTRAINT chk_screen_score CHECK (ai_score >= 0 AND ai_score <= 100),
    CONSTRAINT chk_screen_decision CHECK (screening_decision IN ('Pass', 'Review', 'Reject'))
) ENGINE=InnoDB;

CREATE TABLE application_stage_history (
    stage_event_id       INT           NOT NULL,
    application_id       INT           NOT NULL,
    stage_name           VARCHAR(40)   NOT NULL,
    stage_status         VARCHAR(30)   NOT NULL,
    stage_timestamp      DATETIME(6)   NOT NULL,
    stage_duration_hours DECIMAL(10,2) NULL,
    PRIMARY KEY (stage_event_id),
    CONSTRAINT fk_stage_app FOREIGN KEY (application_id) REFERENCES applications (application_id),
    CONSTRAINT chk_stage_name CHECK (stage_name IN
        ('applied', 'screened', 'interview', 'offer', 'hired', 'rejected')),
    CONSTRAINT chk_stage_status CHECK (stage_status IN
        ('entered', 'passed', 'failed', 'withdrawn'))
) ENGINE=InnoDB;

CREATE TABLE offers (
    offer_id           INT          NOT NULL,
    application_id     INT          NOT NULL,
    offer_date         DATE         NOT NULL,
    offered_salary_inr DECIMAL(12,2) NOT NULL,
    offer_status       VARCHAR(30)  NOT NULL,
    response_date      DATE         NULL,
    PRIMARY KEY (offer_id),
    CONSTRAINT fk_offer_app FOREIGN KEY (application_id) REFERENCES applications (application_id),
    CONSTRAINT chk_offer_status CHECK (offer_status IN ('accepted', 'declined', 'withdrawn', 'pending')),
    CONSTRAINT chk_offer_salary CHECK (offered_salary_inr >= 0),
    CONSTRAINT chk_offer_dates CHECK (response_date IS NULL OR response_date >= offer_date)
) ENGINE=InnoDB;

CREATE TABLE source_costs (
    source_cost_id INT          NOT NULL,
    source_id      INT          NOT NULL,
    month_start    DATE         NOT NULL,
    cost_inr       DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (source_cost_id),
    CONSTRAINT fk_cost_source FOREIGN KEY (source_id) REFERENCES recruitment_sources (source_id),
    CONSTRAINT chk_cost CHECK (cost_inr >= 0)
) ENGINE=InnoDB;
