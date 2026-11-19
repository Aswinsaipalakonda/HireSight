# Loading the HireSight Database

## Prerequisites

- MySQL 8.0+ **or** MariaDB 10.4+ (XAMPP). The schema uses only features
  available in both (foreign keys, CHECK constraints, CTEs, window functions).
- The processed CSVs in `data/processed/` (run `python scripts/clean_data.py`
  first if missing).

## Option A — automated loader (recommended)

1. Copy `.env.example` to `.env` and set your credentials:

   ```
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=      # XAMPP default: empty
   DB_NAME=hiresight
   ```

   `.env` is git-ignored — never commit credentials.

2. Run:

   ```bash
   python scripts/load_database.py
   ```

   This executes all three SQL scripts, loads the CSVs in one transaction,
   applies the indexes, and verifies row counts and referential integrity.

## Option B — manual

1. Execute the SQL scripts in order with any MySQL client:

   ```bash
   mysql -u root < database/01_create_database.sql
   mysql -u root < database/02_create_tables.sql
   ```

2. Load the CSVs (e.g. phpMyAdmin import, MySQL Workbench Table Data Import
   Wizard, or `LOAD DATA LOCAL INFILE`). Load in this order so foreign keys
   resolve:

   1. `candidates` 2. `jobs` 3. `recruitment_sources` 4. `applications`
   5. `screening_results` 6. `application_stage_history` 7. `offers`
   8. `source_costs`

   If using `LOAD DATA LOCAL INFILE`, add `SET FOREIGN_KEY_CHECKS=0;` before
   and `SET FOREIGN_KEY_CHECKS=1;` after, and ensure the MySQL server has
   `local_infile=ON`.

3. Apply indexes:

   ```bash
   mysql -u root < database/03_constraints_indexes.sql
   ```

## Verification

The loader runs these checks automatically; manually, confirm:

```sql
-- Row counts match the processed CSVs
SELECT 'candidates', COUNT(*) FROM candidates
UNION ALL SELECT 'jobs', COUNT(*) FROM jobs
UNION ALL SELECT 'recruitment_sources', COUNT(*) FROM recruitment_sources
UNION ALL SELECT 'applications', COUNT(*) FROM applications
UNION ALL SELECT 'screening_results', COUNT(*) FROM screening_results
UNION ALL SELECT 'application_stage_history', COUNT(*) FROM application_stage_history
UNION ALL SELECT 'offers', COUNT(*) FROM offers
UNION ALL SELECT 'source_costs', COUNT(*) FROM source_costs;

-- No orphan records
SELECT COUNT(*) FROM applications a
LEFT JOIN candidates c ON a.candidate_id = c.candidate_id
WHERE c.candidate_id IS NULL;
```

Expected: 3,500 / 45 / 8 / 8,000 / 7,541 / 23,835 / 869 / 84 and 0 orphans.

## Analysis queries

Documented, business-question-driven queries live in `database/queries/`:

| File | Content |
|---|---|
| `01_basic_queries.sql` | SELECT, WHERE, ORDER BY, LIMIT, patterns |
| `02_joins_aggregations.sql` | Multi-table INNER/LEFT JOIN, GROUP BY, HAVING, aggregate functions |
| `03_funnel_analysis.sql` | Stage counts, conversion, drop-off (grain-safe COUNT DISTINCT) |
| `04_source_analysis.sql` | Source volume, conversion, cost per hire |
| `05_time_to_hire.sql` | Mean and median time-to-hire by segment |
| `06_advanced_sql.sql` | CTEs, subqueries, CASE pivots, ROW_NUMBER/RANK/LAG window functions |

Each query has a business question and a plain-language interpretation in comments.
