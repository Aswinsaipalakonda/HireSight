# HireSight --- Recruitment Analytics & Intelligence Platform

## Product Requirements Document (PRD)

**Document version:** 1.0\
**Status:** Build-ready project specification\
**Project type:** Portfolio / Data Analyst demonstration project\
**Primary audience:** SphinxHire Data Analyst (Fresher) application\
**Prepared:** 19 November 2026

------------------------------------------------------------------------

## 1. Executive Summary

HireSight is an end-to-end recruitment analytics project that transforms
applicant-tracking data into reliable operational metrics and actionable
business insights. It will demonstrate the practical skills expected of
an entry-level Data Analyst: spreadsheet analysis, SQL querying, data
cleaning, exploratory data analysis, dashboard development, KPI
definition, statistical reasoning, and communicating findings to
non-technical stakeholders.

The project models a fictional recruitment company operating an
Applicant Tracking System (ATS). It analyses job demand, candidate
sources, recruitment funnel conversion, time-to-hire, offer acceptance,
and the relationship between simulated AI screening scores and later
recruitment outcomes.

**Important integrity statement:** HireSight is an independent portfolio
project using synthetic or appropriately licensed public data. It is not
affiliated with SphinxHire and does not use SphinxHire customer data,
proprietary screening logic, or internal systems. AI screening scores
and outcomes in the synthetic dataset are illustrative. Any observed
association is not proof that an AI score causes a hiring outcome or
measures candidate quality fairly.

## 2. Product Vision

Give a recruiter, hiring manager, or business leader a trustworthy view
of recruitment performance, from application source through final
outcome, so they can identify bottlenecks, compare channels, and make
better-informed process decisions.

### 2.1 Product goals

1.  Build a reproducible data pipeline from raw CSV files to a
    relational database and analytics-ready outputs.
2.  Use SQL to answer realistic recruitment business questions.
3.  Apply Python for data validation, cleaning, exploratory analysis,
    and statistical summaries.
4.  Use Excel or Google Sheets for practical spreadsheet analysis,
    including formulas, lookups, pivot tables, and charts.
5.  Deliver an interactive Power BI dashboard with clearly defined
    recruitment KPIs.
6.  Produce a concise insights report that translates analysis into
    decisions and recommendations.
7.  Document assumptions, data definitions, limitations, and steps to
    reproduce the project.

### 2.2 Non-goals

-   Building a production ATS or candidate-facing recruitment portal.
-   Building, training, or deploying a real candidate-ranking model.
-   Claiming that simulated AI scores are predictive or unbiased.
-   Making automated hiring, rejection, or candidate eligibility
    decisions.
-   Collecting real candidate personal information.
-   Integrating with live job boards, LinkedIn, or commercial ATS
    platforms.
-   Building a cloud-hosted multi-user application.

## 3. Target Users and Stakeholders

  -----------------------------------------------------------------------
  User / stakeholder      Need                    HireSight capability
  ----------------------- ----------------------- -----------------------
  Founder / leadership    Understand overall      Executive KPI dashboard
                          hiring performance      and monthly trends

  Recruiter               Find bottlenecks and    Funnel, stage ageing,
                          monitor open roles      job-level views

  Hiring manager          Compare roles and       Job and department
                          departments             performance

  Sales / customer        Explain customer        Source and outcome
  success                 recruitment metrics     summaries

  Data analyst            Produce accurate,       SQL scripts, Python
                          repeatable analysis     notebooks, data
                                                  dictionary
  -----------------------------------------------------------------------

## 4. Scope and Deliverables

### 4.1 In scope

-   Synthetic ATS dataset generation or documented public dataset
    adaptation.
-   Data dictionary and documented data assumptions.
-   Data profiling and quality checks.
-   Excel workbook for selected cleaning and pivot-table exercises.
-   MySQL relational schema with primary and foreign keys.
-   SQL analysis queries covering joins, aggregations, filters, CTEs,
    subqueries, CASE expressions, and window functions.
-   Python notebook using Pandas, NumPy, and Matplotlib.
-   Power BI report with interactive filters and multiple analytical
    pages.
-   Business insights report and GitHub README.
-   Reproducible setup and validation instructions.

### 4.2 Deliverables

  -----------------------------------------------------------------------
  Deliverable             Format                  Acceptance condition
  ----------------------- ----------------------- -----------------------
  Raw source data         CSV                     Files have documented
                                                  columns and consistent
                                                  keys

  Clean data              CSV                     Validation checks pass
                                                  or exceptions are
                                                  documented

  Data dictionary         Markdown / CSV          Every field has
                                                  definition, type, and
                                                  rules

  Spreadsheet analysis    XLSX                    Formulas, lookups,
                                                  pivot tables, charts
                                                  included

  Database schema         SQL                     Tables, keys,
                                                  constraints, and
                                                  indexes documented

  Analysis queries        SQL                     Queries answer defined
                                                  business questions

  EDA notebook            IPYNB                   Reproducible cleaning,
                                                  analysis, charts, and
                                                  findings

  Power BI dashboard      PBIX                    KPI and analysis pages
                                                  work with slicers

  Insights report         PDF / Markdown          Findings supported by
                                                  metrics and caveats

  Project documentation   README.md               A new user can
                                                  reproduce the project
  -----------------------------------------------------------------------

## 5. Assumptions and Decisions

The first implementation should use these defaults to keep the scope
controlled:

-   **Database:** MySQL 8.0 or later.
-   **Dashboard:** Microsoft Power BI Desktop.
-   **Analysis:** Python 3.11+ with Pandas, NumPy, Matplotlib, and
    Jupyter.
-   **Spreadsheet:** Microsoft Excel or Google Sheets. Excel is
    preferred for the local project workbook.
-   **Dataset:** Synthetic, deterministic ATS dataset generated
    specifically for this project.
-   **Scale:** Approximately 5,000--10,000 applications, 2,000--5,000
    candidates, 30--60 jobs, and associated screening, stage, and offer
    records.
-   **Currency:** INR for illustrative salary and recruitment cost
    fields.
-   **Date range:** A synthetic 12-month period. The exact dates should
    be recorded in the dataset README.
-   **Geography:** Fictional or broad Indian city labels; no real
    candidate contact details or precise addresses.
-   **Language:** English.

Use a fixed random seed when generating synthetic data so that the
dataset and dashboard can be recreated consistently. Store the seed and
generation parameters in the repository.

## 6. Business Questions

The analysis must answer the following questions:

### 6.1 Recruitment demand

1.  How many applications were received in the selected period?
2.  Which jobs received the most and fewest applications?
3.  Which departments have the highest application volume?
4.  How does application volume change month over month?

### 6.2 Recruitment source effectiveness

1.  Which sources generate the most applications?
2.  Which sources have the highest application-to-hire conversion?
3.  Which sources have the shortest median time-to-hire?
4.  If simulated source costs are available, which sources have the
    lowest cost per hire?

### 6.3 Hiring funnel and process efficiency

1.  How many applications reach each stage?
2.  What percentage progress from one stage to the next?
3.  Where is the largest candidate drop-off?
4.  Which jobs or departments have the longest stage delays?
5.  How many applications are still active at each stage?

### 6.4 Hiring outcomes

1.  How many candidates receive offers and how many are hired?
2.  What is the offer acceptance rate?
3.  How many offers are declined, withdrawn, or pending?
4.  How do outcomes differ by job, department, and source?

### 6.5 AI screening analysis

1.  How are AI screening scores distributed?
2.  How do screening scores vary by job family or source?
3.  What is the relationship between score bands and interview
    progression?
4.  What are the counts of high-score candidates who were not hired and
    lower-score candidates who were hired?
5.  Do score patterns differ across groups in the synthetic data, and
    what limitations prevent a fairness conclusion?

## 7. Functional Requirements

Priority definitions: **P0** = essential for project completion; **P1**
= important; **P2** = optional enhancement.

### FR-01: Dataset generation and ingestion --- P0

-   Generate separate CSV files for candidates, jobs, applications,
    screening results, stage history, offers, and source costs.
-   Each entity must have a stable unique identifier.
-   Related records must use valid foreign keys.
-   Use realistic but clearly synthetic distributions, dates, job
    titles, departments, sources, and outcomes.
-   Include missing values and selected data-quality issues
    intentionally, but do not make the dataset unusably dirty.
-   Record generation rules, random seed, date range, and limitations.
-   Never generate real email addresses, phone numbers, or identifiable
    personal details.

**Acceptance criteria** - All CSVs load successfully. - Primary keys are
unique and non-null. - Foreign-key references resolve. - Date columns
parse consistently. - Dataset row counts and generation parameters are
documented.

### FR-02: Data profiling and cleaning --- P0

Use Python and/or spreadsheet tools to: - Inspect row counts, column
types, null counts, unique values, and duplicates. - Standardise text
values, dates, categories, and status labels. - Identify duplicate
applications and invalid references. - Check that dates follow logical
order. - Validate score ranges and salary/cost values. - Preserve raw
files and write cleaned outputs separately. - Record each transformation
and the number of affected rows.

**Acceptance criteria** - Raw files are never overwritten. - Cleaning
steps can be rerun. - A quality summary is generated. - Rows removed or
corrected are quantified and explained.

### FR-03: Relational database --- P0

-   Create a MySQL database named `hiresight`.
-   Implement the logical schema described in Section 8.
-   Define primary keys, foreign keys, appropriate data types, and
    indexes.
-   Add constraints for valid enumerated statuses where practical.
-   Include repeatable schema and data-loading scripts.
-   Keep credentials outside source control.

**Acceptance criteria** - Database can be created from SQL scripts. -
All cleaned CSVs can be imported. - Referential integrity checks return
no unexpected orphan records. - A user can run the analysis queries
against the loaded database.

### FR-04: SQL analysis --- P0

Provide documented SQL queries for: - SELECT, WHERE, ORDER BY, LIMIT. -
INNER JOIN and LEFT JOIN across multiple tables. - GROUP BY and
HAVING. - COUNT, SUM, AVG, MIN, MAX. - CASE expressions. - Subqueries
and CTEs. - Window functions including ROW_NUMBER, RANK, and LAG where
useful. - Date-based aggregation and conversion calculations.

Every query must include a short business question and a plain-language
interpretation of its output.

### FR-05: Spreadsheet analysis --- P0

Create an Excel workbook containing: - Raw-data inspection or a clearly
labelled sample. - Cleaned/analysis-ready table or imported data. - IF,
COUNTIF/COUNTIFS, SUMIF/SUMIFS, AVERAGEIF/AVERAGEIFS. - XLOOKUP or
VLOOKUP demonstration. - At least two pivot tables. - At least two
charts. - A short summary sheet with key metrics.

If the full dataset makes the workbook unwieldy, use a representative
analysis extract and clearly state its source and row count.

### FR-06: Python EDA --- P0

Use Pandas, NumPy, and Matplotlib to: - Load and inspect CSV files. -
Clean and transform fields. - Merge related datasets where
appropriate. - Calculate descriptive statistics. - Analyse
distributions, trends, and relationships. - Visualise monthly
applications, source performance, funnel conversion, time-to-hire, offer
outcomes, and score distributions. - Export clean datasets and/or
aggregated outputs for Power BI. - Explain important findings and
limitations in notebook Markdown.

Avoid unnecessary machine-learning models. The objective is data
analysis, not model building.

### FR-07: Power BI dashboard --- P0

Create an interactive Power BI report with the pages specified in
Section 10.

Required interactions: - Date range slicer. - Job title and department
slicers. - Recruitment source slicer. - Application status or outcome
slicer where relevant. - Cross-filtering between charts. - Clear titles,
units, definitions, and useful tooltips. - Consistent formatting and
readable labels.

**Acceptance criteria** - All KPIs respond correctly to relevant
filters. - No visual relies on unexplained or misleading denominators. -
Totals reconcile with SQL validation queries. - The report opens without
broken data sources when configured as documented.

### FR-08: Business insights --- P0

Produce a report with: - Five to eight evidence-backed findings. - At
least three practical recommendations. - A metric or chart supporting
each finding. - Limitations and assumptions. - A clear distinction
between correlation and causation. - No unsupported claims about AI
accuracy, bias, or candidate quality.

### FR-09: Documentation and reproducibility --- P0

-   Include setup instructions, dependencies, file descriptions, schema,
    metric definitions, and execution order.
-   Explain how to regenerate the dataset.
-   Explain how to load MySQL and run SQL queries.
-   Explain how to run the notebook.
-   Explain how to refresh the Power BI report.
-   Include dashboard screenshots in the README.
-   Include a project limitations section.

### FR-10: Optional enhancements --- P2

-   Add a simple Streamlit read-only interface for selected metrics.
-   Add a data-quality summary dashboard.
-   Add a cohort analysis of applications by month.
-   Add a recruiter workload analysis if recruiter assignment data is
    introduced.
-   Add a sensitivity analysis for alternative hiring-funnel
    definitions.

Do not start optional enhancements until every P0 requirement is
complete.

## 8. Data Model and Database Design

### 8.1 Logical entities

#### `candidates`

  Column              Suggested type   Description
  ------------------- ---------------- --------------------------------
  candidate_id        INT              Primary key
  experience_years    DECIMAL(4,1)     Simulated years of experience
  highest_education   VARCHAR(60)      Education category
  candidate_city      VARCHAR(80)      Broad city label
  created_at          DATETIME         Synthetic record creation time

Do not include real names, personal emails, phone numbers, or precise
addresses. If a display name is needed for demonstration, use a
generated alias and clearly label it synthetic.

#### `jobs`

  Column            Suggested type   Description
  ----------------- ---------------- ---------------------------
  job_id            INT              Primary key
  job_title         VARCHAR(120)     Role title
  department        VARCHAR(80)      Department
  location          VARCHAR(80)      Job location
  employment_type   VARCHAR(40)      Full-time, contract, etc.
  salary_min_inr    DECIMAL(12,2)    Illustrative lower salary
  salary_max_inr    DECIMAL(12,2)    Illustrative upper salary
  posted_date       DATE             Job posting date
  closed_date       DATE, nullable   Job closure date
  job_status        VARCHAR(30)      Open, closed, on hold

#### `applications`

  Column           Suggested type   Description
  ---------------- ---------------- ------------------------------------
  application_id   INT              Primary key
  candidate_id     INT              Foreign key to candidates
  job_id           INT              Foreign key to jobs
  source_id        INT              Foreign key to recruitment_sources
  applied_at       DATETIME         Application timestamp
  current_status   VARCHAR(30)      Current application status

A candidate may apply to multiple jobs. Do not assume candidate_id is
unique in this table.

#### `recruitment_sources`

  Column            Suggested type   Description
  ----------------- ---------------- -----------------------------------------
  source_id         INT              Primary key
  source_name       VARCHAR(80)      Referral, job board, careers page, etc.
  source_category   VARCHAR(50)      Referral, organic, paid, agency

#### `screening_results`

  Column               Suggested type   Description
  -------------------- ---------------- -------------------------------
  screening_id         INT              Primary key
  application_id       INT              Foreign key to applications
  screening_date       DATETIME         Screening timestamp
  ai_score             DECIMAL(5,2)     Simulated score from 0 to 100
  screening_decision   VARCHAR(30)      Pass, review, reject
  score_version        VARCHAR(30)      Synthetic score version label

A screening score is associated with an application, not just a
candidate, because one candidate can apply for different jobs.

#### `application_stage_history`

  -----------------------------------------------------------------------
  Column                  Suggested type          Description
  ----------------------- ----------------------- -----------------------
  stage_event_id          INT                     Primary key

  application_id          INT                     Foreign key to
                                                  applications

  stage_name              VARCHAR(40)             Applied, screened,
                                                  interview, offer,
                                                  hired, rejected

  stage_status            VARCHAR(30)             Entered, passed,
                                                  failed, withdrawn

  stage_timestamp         DATETIME                Event timestamp

  stage_duration_hours    DECIMAL(10,2), nullable Optional derived
                                                  duration
  -----------------------------------------------------------------------

This is an event-history table. One application can have multiple stage
events. Use it to reconstruct funnel progression and time spent in
stages.

#### `offers`

  Column               Suggested type   Description
  -------------------- ---------------- ----------------------------------------
  offer_id             INT              Primary key
  application_id       INT              Foreign key to applications
  offer_date           DATE             Offer issue date
  offered_salary_inr   DECIMAL(12,2)    Illustrative offer
  offer_status         VARCHAR(30)      Accepted, declined, withdrawn, pending
  response_date        DATE, nullable   Candidate response date

#### `source_costs` (optional but recommended)

  Column           Suggested type   Description
  ---------------- ---------------- ------------------------------------
  source_cost_id   INT              Primary key
  source_id        INT              Foreign key to recruitment_sources
  month_start      DATE             Month represented
  cost_inr         DECIMAL(12,2)    Simulated source spend

### 8.2 Relationships

-   `candidates` 1-to-many `applications`
-   `jobs` 1-to-many `applications`
-   `recruitment_sources` 1-to-many `applications`
-   `applications` 1-to-many `screening_results`
-   `applications` 1-to-many `application_stage_history`
-   `applications` 1-to-many `offers` (normally one offer per
    application in the initial dataset; schema can support multiple)
-   `recruitment_sources` 1-to-many `source_costs`

### 8.3 Data modelling rules

-   Use `application_id` as the central fact key for recruitment funnel
    analysis.
-   Avoid joining raw stage history directly to applications and then
    summing application-level metrics without deduplication; this can
    multiply rows.
-   Define whether each KPI counts candidates, applications, offers, or
    hires.
-   Use a consistent calendar table in Power BI for date analysis.
-   Use a documented rule for identifying a hire: a final `hired` stage
    event or a canonical application outcome. Do not mix definitions.
-   If multiple offers or multiple hires per application are generated,
    define how the report handles them.

## 9. Data Generation Specification

The synthetic data should be plausible, internally consistent, and
useful for analysis---not designed to guarantee impressive results.

### 9.1 Suggested distributions

-   30--60 job postings across technology, sales, operations, finance,
    HR, and customer support.
-   5,000--10,000 applications across a 12-month period.
-   2,000--5,000 unique candidate records.
-   Sources may include referrals, company careers page, job boards,
    campus hiring, agencies, and social platforms.
-   Application volume should vary by job and month.
-   A subset of applications should be withdrawn or rejected at
    different stages.
-   Some jobs should have longer time-to-hire than others.
-   Offer outcomes should include accepted, declined, withdrawn, and
    pending.
-   Screening scores should have a broad distribution with overlap
    between outcomes. Do not create a perfect relationship between score
    and hiring outcome.

### 9.2 Data-quality scenarios to include

Include a controlled number of: - Missing optional education or
experience values. - Inconsistent category casing or whitespace. -
Duplicate candidate profiles only if explicitly documented; avoid
duplicate application IDs. - Invalid date order in a small number of raw
records, for cleaning demonstrations. - Missing source values. -
Out-of-range screening scores in a small number of raw records.

The cleaning notebook should detect and resolve or quarantine these
issues with an audit summary. Keep a clean, valid final dataset for
dashboarding.

### 9.3 Reproducibility

-   Use a fixed random seed.
-   Keep the generator script under `scripts/`.
-   Write generated files to `data/raw/`.
-   Write cleaned outputs to `data/processed/`.
-   Do not manually edit generated CSVs without documenting the change.

## 10. KPI Definitions and Dashboard Requirements

Every KPI must have a written definition, numerator, denominator, date
basis, and filter behaviour.

### 10.1 Core KPI definitions

  -----------------------------------------------------------------------
  KPI                     Definition              Important caveat
  ----------------------- ----------------------- -----------------------
  Total applications      Count of distinct       Not candidate count
                          application_id in       
                          selected period         

  Unique applicants       Count of distinct       One person may apply
                          candidate_id with an    more than once
                          application             

  Jobs posted             Count of distinct       Define whether closed
                          job_id posted in        jobs remain included
                          selected period         

  Hires                   Count of distinct       Use one canonical hire
                          application_id with a   rule
                          valid hired outcome     

  Application-to-hire     Hired applications /    State the cohort and
  rate                    eligible applications   period definition

  Offer acceptance rate   Accepted offers /       Exclude pending offers
                          offers with a final     from denominator
                          response                

  Average time-to-hire    Average days from       Also show median; skew
                          applied_at to hire date can distort mean
                          for hired applications  

  Median time-to-hire     Median days from        Preferable for skewed
                          applied_at to hire date duration data

  Stage conversion rate   Distinct applications   Define the cohort and
                          passing next stage /    stage order
                          distinct applications   
                          entering prior stage    

  Stage drop-off rate     1 minus stage           Do not count
                          conversion rate         still-active records as
                                                  rejected

  Applications per job    Applications / distinct Can be misleading when
                          jobs in selected scope  jobs have different
                                                  open durations

  Cost per hire           Attributed source cost  Only if cost data and
                          / hires attributed to   attribution assumptions
                          that source             exist
  -----------------------------------------------------------------------

### 10.2 Dashboard page 1 --- Executive Overview

**Purpose:** Give leadership a fast view of recruitment performance.

Visuals: - KPI cards: applications, unique applicants, hires, offer
acceptance rate, median time-to-hire. - Monthly application and hire
trend. - Applications and hires by department. - Hiring funnel
summary. - Top recruitment sources by applications.

### 10.3 Dashboard page 2 --- Hiring Funnel

Visuals: - Funnel by stage. - Stage-to-stage conversion percentages. -
Drop-off counts by stage. - Active applications by current stage. -
Median time spent in each stage. - Filters for job, department, source,
and date.

Do not label candidates who are still waiting at a stage as drop-offs.

### 10.4 Dashboard page 3 --- Source Effectiveness

Visuals: - Applications by source. - Hires by source. -
Application-to-hire conversion by source. - Median time-to-hire by
source. - Offer acceptance by source. - Cost per hire only when source
cost data is available.

Show sample size alongside conversion rates. A source with a high
conversion rate based on very few applications should not be presented
as definitively best.

### 10.5 Dashboard page 4 --- Job and Department Performance

Visuals: - Applications by job title. - Hires by department. - Open
roles and application volume. - Median time-to-hire by job. - Jobs with
high application volume but low conversion. - Job-level detail table.

### 10.6 Dashboard page 5 --- AI Screening Analysis

Visuals: - Screening score distribution. - Candidate/application counts
by score band. - Interview progression by score band. - Hiring outcome
by score band. - High-score non-hire and lower-score hire counts. -
Score comparison by job family or source where sample size is
sufficient.

**Required warning:** This page is descriptive analysis of simulated
scores and outcomes. It does not establish model accuracy, fairness,
causation, or real-world predictive validity. Do not label a score band
as "good candidates" or "bad candidates."

### 10.7 Dashboard usability requirements

-   Use a consistent and restrained visual theme.
-   Use readable typography and meaningful chart titles.
-   Display currency as INR and durations in days.
-   Use percentage formatting consistently.
-   Provide clear empty-state behaviour when filters return no records.
-   Avoid 3D charts, excessive colours, decorative gauges, and
    unexplained abbreviations.
-   Add a definitions tooltip or metric glossary page.
-   Validate totals against SQL outputs.

## 11. Python Analysis Requirements

Recommended notebook sections:

1.  Project objective and dataset description.
2.  Imports and configuration.
3.  Load raw CSV files.
4.  Data overview: dimensions, data types, nulls, duplicates.
5.  Data-quality checks.
6.  Cleaning and standardisation.
7.  Export processed files.
8.  Recruitment volume analysis.
9.  Source effectiveness analysis.
10. Funnel conversion analysis.
11. Time-to-hire analysis.
12. Offer outcomes.
13. AI score distribution and outcome association.
14. Summary of findings and limitations.

### 11.1 Statistical practices

-   Report mean and median for skewed measures such as time-to-hire.
-   Include counts with percentages.
-   Be careful with small sample sizes.
-   Use distributions and percentiles, not just averages.
-   If calculating correlation, explain what it measures and what it
    does not.
-   Avoid causal claims from observational or synthetic data.
-   Do not use demographic attributes to make hiring recommendations.
-   Do not infer protected characteristics from names, locations, or
    other proxy fields.

## 12. Spreadsheet Workbook Requirements

Suggested workbook tabs:

1.  `Read_Me` --- workbook purpose, data source, refresh date,
    limitations.
2.  `Data_Quality` --- nulls, duplicates, invalid categories, date
    checks.
3.  `Applications` --- analysis-ready application-level data.
4.  `Lookup_Analysis` --- XLOOKUP/VLOOKUP examples.
5.  `Pivot_Source` --- source-wise application and hire summary.
6.  `Pivot_Job` --- job-wise application and outcome summary.
7.  `KPI_Summary` --- formulas and charts.

Demonstrate: - XLOOKUP or VLOOKUP. - IF and IFERROR. -
COUNTIF/COUNTIFS. - SUMIF/SUMIFS. - AVERAGEIF/AVERAGEIFS. - Pivot tables
with filters. - Charts with titles and labelled axes.

## 13. Non-Functional Requirements

### NFR-01: Accuracy

All displayed metrics must reconcile with validated SQL calculations,
subject to documented rounding.

### NFR-02: Reproducibility

A new user should be able to regenerate data, load the database, run
analysis, and refresh outputs by following the README.

### NFR-03: Data privacy

Use synthetic or licensed public data only. Do not commit real personal
data, credentials, API keys, or private customer information.

### NFR-04: Maintainability

Use clear file names, modular scripts, comments for non-obvious logic,
and a central data dictionary.

### NFR-05: Performance

The project should run on a typical student laptop. Avoid unnecessary
infrastructure and heavy dependencies.

### NFR-06: Explainability

Every KPI and business recommendation must be explainable in plain
English.

### NFR-07: Honest representation

Clearly distinguish generated data, observed results, assumptions, and
limitations. Never represent simulated data as actual company data.

## 14. Recommended Repository Structure

``` text
HireSight/
├── README.md
├── PRD.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
├── database/
│   ├── 01_create_database.sql
│   ├── 02_create_tables.sql
│   ├── 03_constraints_indexes.sql
│   ├── 04_load_instructions.md
│   └── queries/
│       ├── 01_basic_queries.sql
│       ├── 02_joins_aggregations.sql
│       ├── 03_funnel_analysis.sql
│       ├── 04_source_analysis.sql
│       ├── 05_time_to_hire.sql
│       └── 06_advanced_sql.sql
├── scripts/
│   ├── generate_dataset.py
│   ├── profile_data.py
│   └── clean_data.py
├── notebooks/
│   └── recruitment_eda.ipynb
├── excel/
│   └── hiresight_analysis.xlsx
├── powerbi/
│   ├── HireSight.pbix
│   └── screenshots/
├── reports/
│   ├── business_insights.md
│   └── data_dictionary.md
└── docs/
    ├── metric_definitions.md
    └── methodology_and_limitations.md
```

## 15. Implementation Plan

A seven-day schedule is an aggressive target. If data modelling or Power
BI is new, allow 10--14 days rather than rushing and publishing
incorrect metrics.

  -----------------------------------------------------------------------
  Phase                   Tasks                   Output
  ----------------------- ----------------------- -----------------------
  1\. Scope and data      Finalise fields,        Raw CSVs and data
                          generate data, document dictionary
                          assumptions             

  2\. Data quality        Profile, clean,         Clean CSVs and quality
                          validate, export        report
                          processed data          

  3\. SQL                 Create schema, load     Database and SQL
                          tables, write and       portfolio
                          validate queries        

  4\. Spreadsheet         Build formulas,         Excel workbook
                          lookups, pivot tables,  
                          charts                  

  5\. Python EDA          Explore trends, funnel, Reproducible notebook
                          sources, durations,     
                          scores                  

  6\. Power BI            Model relationships,    PBIX dashboard
                          create measures, build  
                          report pages            

  7\. Insights and polish Validate numbers, write Complete GitHub
                          findings, document and  repository
                          publish                 
  -----------------------------------------------------------------------

### Suggested effort allocation

-   Data generation and quality: 20%
-   SQL and relational modelling: 20%
-   Python and spreadsheet analysis: 20%
-   Power BI dashboard: 25%
-   Validation, insights, and documentation: 15%

## 16. Testing and Validation Plan

### 16.1 Data tests

-   Primary keys contain no nulls or duplicates.
-   Foreign keys reference existing records.
-   Screening scores fall within 0--100 after cleaning.
-   Offer salary and source costs are non-negative.
-   Dates follow logical sequences.
-   Application IDs are unique in the applications table.
-   Stage history has valid application references.
-   Raw and processed row counts are reconciled with documented
    exclusions.

### 16.2 Metric tests

-   Total applications match the distinct application count in SQL.
-   Unique applicants match the distinct candidate count.
-   Hires match the documented canonical hire definition.
-   Offer acceptance denominator excludes pending offers.
-   Median time-to-hire uses hired applications only.
-   Funnel conversion uses distinct applications and a documented
    cohort.
-   Power BI values match independent SQL calculations.

### 16.3 Dashboard tests

-   Each slicer filters intended visuals.
-   Clearing filters restores totals.
-   No-data selections display clearly.
-   Tooltips and labels are understandable.
-   Percentages and currency units are formatted correctly.

### 16.4 Reproducibility test

Clone the repository into a clean folder and follow the README without
relying on undocumented local files. Record any manual configuration
that is necessary.

## 17. Risks and Mitigations

  -----------------------------------------------------------------------
  Risk                    Impact                  Mitigation
  ----------------------- ----------------------- -----------------------
  Synthetic data looks    Analysis lacks          Include realistic
  too perfect             credibility             variation and
                                                  documented edge cases

  Incorrect joins         Misleading KPIs         Use grain-aware queries
  multiply counts                                 and distinct
                                                  application IDs

  Funnel denominator is   Conversion rates are    Document cohort and
  inconsistent            wrong                   stage-entry definitions

  Mean time-to-hire is    Misleading duration     Show median and
  skewed                  summary                 distribution

  AI score is treated as  Unsupported conclusions Use cautious language
  ground truth                                    and limitations

  Dashboard becomes too   Hard to explain in      Prioritise five clear
  complex                 interview               pages

  Time is spent on        Core deliverables       Complete all P0
  optional UI             remain incomplete       requirements first

  Dataset or metrics are  Project cannot be       Fixed seed, scripts,
  not reproducible        verified                validation queries
  -----------------------------------------------------------------------

## 18. Definition of Done

HireSight is complete when all of the following are true:

-   [ ] Synthetic/public dataset source and limitations are documented.
-   [ ] Data dictionary is complete.
-   [ ] Raw and processed data are stored separately.
-   [ ] Data-quality checks are implemented and results documented.
-   [ ] MySQL schema and loading process work from a clean setup.
-   [ ] SQL examples demonstrate joins, aggregations, CTEs, subqueries,
    and window functions.
-   [ ] Excel workbook includes formulas, lookup, pivot tables, and
    charts.
-   [ ] Python notebook performs reproducible cleaning and EDA using
    Pandas, NumPy, and Matplotlib.
-   [ ] Power BI dashboard contains all five specified analytical pages.
-   [ ] Core dashboard metrics reconcile with SQL.
-   [ ] Business insights report includes evidence-backed findings and
    practical recommendations.
-   [ ] AI screening analysis is clearly labelled as simulated and
    non-causal.
-   [ ] README explains setup, execution, refresh, and limitations.
-   [ ] Repository contains no secrets or private personal data.
-   [ ] Screenshots and a short project walkthrough are prepared for
    interviews.

## 19. Interview Demonstration Plan

Prepare a five-minute walkthrough:

1.  **Problem (30 seconds):** Explain why recruitment teams need
    visibility into funnel conversion, source effectiveness, and
    time-to-hire.
2.  **Data model (45 seconds):** Show the application-centred relational
    schema and explain why stage history is stored separately.
3.  **SQL (60 seconds):** Demonstrate one multi-table join, one grouped
    metric, and one CTE or window-function query.
4.  **Dashboard (90 seconds):** Show the executive page, funnel, source
    analysis, and AI score analysis.
5.  **Insight (45 seconds):** Present one meaningful finding, its
    evidence, and a practical recommendation.
6.  **Limitations (30 seconds):** Explain the synthetic dataset, metric
    definitions, and why score association does not establish model
    quality or fairness.

Be ready to explain: - Why you used `COUNT(DISTINCT application_id)` in
certain queries. - How you handled missing and duplicate records. - Why
median time-to-hire can be more informative than average. - How you
defined offer acceptance rate. - How you prevented stage-history joins
from inflating counts. - What a high screening score does---and does
not---mean in this project.

## 20. First Build Session: Exact Starting Tasks

Do not start by designing the dashboard. Build the data foundation
first.

1.  Create the repository and folders from Section 14.
2.  Create a Python virtual environment.
3.  Install the dependencies listed below.
4.  Implement `scripts/generate_dataset.py` with a fixed seed.
5.  Generate the CSV files and save generation metadata.
6.  Create `reports/data_dictionary.md`.
7.  Run initial checks for primary keys, foreign keys, dates, and score
    ranges.
8.  Only after the generated dataset passes these checks, begin the
    MySQL schema.

### Suggested Python dependencies

``` text
pandas
numpy
matplotlib
seaborn
jupyter
sqlalchemy
pymysql
openpyxl
python-dotenv
```

`seaborn` is optional; Matplotlib is sufficient for the required
analysis. Pin tested package versions in `requirements.txt` after the
environment is working.

### Suggested setup commands

``` bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Install project dependencies
pip install pandas numpy matplotlib jupyter sqlalchemy pymysql openpyxl python-dotenv

# Save installed versions
pip freeze > requirements.txt
```

## 21. Success Criteria for the SphinxHire Application

The project should help demonstrate the capabilities in the job
description:

  SphinxHire requirement     HireSight evidence
  -------------------------- ----------------------------------------------------
  Excel / Google Sheets      Formulas, XLOOKUP, pivot tables, charts
  Basic SQL                  SELECT, WHERE, GROUP BY, JOIN
  Reporting and dashboards   Power BI interactive report
  Hiring metrics             Funnel, time-to-hire, source, offer acceptance
  AI screening analysis      Score distribution and outcome association
  Statistics                 Descriptive statistics, trends, distributions
  Data accuracy              Data-quality checks and metric reconciliation
  Communication              Business insights report and interview walkthrough
  Python (good to have)      Pandas, NumPy, Matplotlib notebook

**Final positioning:** HireSight is a data analytics portfolio project,
not a production recruitment product. Its value is the complete,
verifiable analytical workflow: raw data → cleaning → SQL → analysis →
dashboard → business recommendation.
