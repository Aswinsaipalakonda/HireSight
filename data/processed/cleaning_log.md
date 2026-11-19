# HireSight Cleaning Log

Produced by `scripts/clean_data.py` from `data/raw/` (seed 42). Raw files are never modified.

| # | Table / field | Action | Rows affected | Notes |
|---|---|---|---|---|
| 1 | candidates.candidate_city | casing/whitespace standardized | 40 |  |
| 2 | candidates.highest_education | casing/whitespace standardized | 29 |  |
| 3 | jobs.department | casing/whitespace standardized | 0 |  |
| 4 | jobs.employment_type | casing/whitespace standardized | 0 |  |
| 5 | jobs.job_status | casing/whitespace standardized | 0 |  |
| 6 | stage_history.stage_name | casing/whitespace standardized | 100 |  |
| 7 | stage_history.stage_status | casing/whitespace standardized | 50 |  |
| 8 | screening_results.screening_decision | casing/whitespace standardized | 40 |  |
| 9 | offers.offer_status | casing/whitespace standardized | 0 |  |
| 10 | applications.current_status | casing/whitespace standardized | 0 |  |
| 11 | applications.source_id | imputed as source_id=8 (Unknown / Not Recorded) | 15 | (FK integrity preserved; rows retained for volume analysis) |
| 12 | screening_results | quarantined to processed/quarantine/screening_out_of_range.csv | 10 | (applications retained; only their screening rows excluded) |
| 13 | candidates | merged duplicate profiles into originals (applications reassigned, duplicate rows removed) | 12 | (pairs: 12, applications reassigned: 12 candidate IDs remapped) |
| 14 | applications.candidate_id | reassigned from duplicate to original candidate | 38 |  |
| 15 | application_stage_history.stage_timestamp | repaired to previous event + 1 hour | 8 | (chronology per application restored) |
| 16 | application_stage_history.stage_duration_hours | recomputed from ordered event sequence | 23,835 |  |
| 17 | candidates.experience_years | retained as NULL (optional field, not imputed) | 176 |  |
| 18 | candidates.highest_education | retained as NULL (optional field, not imputed) | 105 |  |

## Output row counts

| Table | Raw | Processed | Change |
|---|---|---|---|
| candidates | 3,512 | 3,500 | -12 |
| jobs | 45 | 45 | +0 |
| recruitment_sources | 7 | 8 | +1 |
| applications | 8,000 | 8,000 | +0 |
| screening_results | 7,551 | 7,541 | -10 |
| application_stage_history | 23,835 | 23,835 | +0 |
| offers | 869 | 869 | +0 |
| source_costs | 84 | 84 | +0 |

## Summary of decisions

- **Standardization:** all category fields mapped to canonical values (strip + case-insensitive lookup).
- **Missing `source_id`:** attributed to a new source record `Unknown / Not Recorded` (source_id = 8, category `unclassified`) so rows stay analysable and FK integrity holds. Exclude this source from channel effectiveness comparisons.
- **Out-of-range AI scores:** quarantined to `processed/quarantine/screening_out_of_range.csv`; the 10 applications keep all other records. Scores were never clipped or fabricated.
- **Disordered stage timestamps:** set to previous event + 1 hour; all durations then recomputed from the ordered sequence.
- **Near-duplicate candidates:** the 12 duplicate profiles were merged into their original candidate (applications reassigned); pairs are listed in `data/raw/generation_metadata.json`.
- **Missing optional fields (`experience_years`, `highest_education`):** retained as NULL — imputing would fabricate candidate attributes.

## Exclusions from processed data

- 10 screening rows (out-of-range scores) -> quarantine file
- 12 duplicate candidate rows (merged into originals)

All other raw rows are present in the processed dataset.