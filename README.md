<p align="center">
  <img src="images/logo.png" alt="HireSight — Recruitment Analytics & Intelligence" width="480">
</p>

# HireSight — Recruitment Analytics & Intelligence Platform

HireSight is an end-to-end recruitment analytics portfolio project. It transforms a
synthetic Applicant Tracking System (ATS) dataset into reliable operational metrics and
actionable business insights: recruitment demand, source effectiveness, hiring-funnel
conversion, time-to-hire, offer outcomes, and descriptive analysis of simulated AI
screening scores.

The project demonstrates the practical skills expected of a data analyst: spreadsheet
analysis, SQL, data cleaning, exploratory data analysis, dashboard development, KPI
definition, statistical reasoning, and communicating findings to non-technical stakeholders.

> **Integrity statement:** HireSight is an independent portfolio project using synthetic
> data. It is not affiliated with SphinxHire and does not use any real customer data.
> AI screening scores and outcomes are illustrative; no observed association establishes
> causation, model accuracy, or fairness.

## Repository structure

```text
HireSight/
├── README.md               This file
├── PRD.md                  Product requirements document (source of truth)
├── requirements.txt        Pinned Python dependencies
├── data/
│   ├── raw/                Generated CSVs + generation metadata (immutable)
│   ├── processed/          Cleaned analysis-ready data (Phase 2)
│   └── README.md           Dataset provenance, seed, and limitations
├── database/               MySQL schema and SQL analysis queries (Phase 3)
├── scripts/
│   ├── generate_dataset.py Fixed-seed synthetic data generator
│   └── profile_data.py     Data profiling / validation report
├── notebooks/              Python EDA notebook (Phase 4)
├── excel/                  Analysis workbook (Phase 5)
├── powerbi/                Power BI report and screenshots (Phase 6)
├── reports/
│   ├── data_dictionary.md  Field-by-field definitions
│   └── business_insights.md (Phase 7)
├── docs/                   Metric definitions and methodology (Phase 7)
└── images/
    ├── logo.png            Project logo (README header)
    └── icon.png            Project icon — reserved as favicon for the optional
                            read-only web interface (PRD FR-10)
```

## Setup

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Reproduce the dataset

```bash
python scripts/generate_dataset.py   # writes data/raw/*.csv (seed = 42, deterministic)
python scripts/profile_data.py       # writes data/raw/profile_summary.md + validation checks
```

## Analysis pipeline (planned phases)

1. **Data foundation** — generate and validate the synthetic dataset (done).
2. **Data quality & cleaning** — profile, clean, and export processed data (done).
3. **MySQL & SQL** — relational schema, load, documented analysis queries.
4. **Python EDA** — notebook with cleaning checks, trends, funnel, and statistics.
5. **Excel workbook** — formulas, lookups, pivot tables, and charts.
6. **Power BI dashboard** — five analytical pages with slicers and defined KPIs.
7. **Insights & publish** — evidence-backed findings, validation, final README.

Clean the raw data (writes `data/processed/` plus an audit log):

```bash
python scripts/clean_data.py
```

## Key metric definitions

Every KPI (application-to-hire rate, offer acceptance rate, median time-to-hire, stage
conversion, cost per hire) has a written definition with numerator, denominator, date
basis, and filter behaviour. See `docs/metric_definitions.md` (Phase 7) and
`reports/data_dictionary.md` for field-level detail.

## Limitations

- All data is synthetic; results illustrate methodology, not real recruitment performance.
- AI screening scores are simulated with intentional overlap between outcomes. Association
  between score and outcome does not establish causation, predictive validity, or fairness.
- Time-to-hire is right-skewed; median is reported alongside the mean.
- Cost per hire depends on simulated source-cost attribution assumptions.

## Status

- [x] Phase 1 — Data foundation (generator, data dictionary, validation)
- [x] Phase 2 — Data quality & cleaning (clean_data.py, audit log, processed datasets)
- [ ] Phase 3 — MySQL schema & SQL queries
- [ ] Phase 4 — Python EDA notebook
- [ ] Phase 5 — Excel workbook
- [ ] Phase 6 — Power BI dashboard
- [ ] Phase 7 — Insights report & final validation
