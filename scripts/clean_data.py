"""
HireSight data cleaning pipeline (Phase 2).

Reads data/raw/*.csv, resolves or quarantines the documented data-quality
issues, and writes analysis-ready CSVs to data/processed/ plus an audit
log (data/processed/cleaning_log.md). Raw files are never modified.

Cleaning decisions (documented in the audit log):
  1. Text standardization: strip whitespace and map casing variants to
     canonical category values across candidates, jobs, stage history,
     and screening decisions.
  2. Missing source_id (15 rows): attributed to a new source record
     "Unknown / Not Recorded" (source_id = 8, category "unclassified")
     so referential integrity holds and the rows stay analysable.
  3. Out-of-range screening scores (10 rows): quarantined to
     data/processed/quarantine/ and excluded from the clean dataset.
     Scores are not fabricated or clipped.
  4. Disordered stage timestamps (8 rows): repaired to previous event
     + 1 hour, keeping per-application chronology.
  5. stage_duration_hours: recomputed for every application from the
     (possibly repaired) ordered event sequence.
  6. Near-duplicate candidate profiles (12): merged into their original
     profile by reassigning the duplicate's applications; duplicate rows
     are then removed.
  7. Missing experience_years / highest_education: retained as NULL.
     These are legitimate optional fields; imputing them would fabricate
     data.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
QUAR = PROC / "quarantine"

STEP_LOG = []


def log(step, action, rows, detail=""):
    entry = {"step": step, "action": action, "rows_affected": int(rows), "detail": detail}
    STEP_LOG.append(entry)
    print(f"  {step}: {action} -> {rows:,} rows {detail}")


def canonical_map(series, canonical):
    """Map values to canonical form by strip+lower lookup; count changes."""
    norm = series.astype("string").map(lambda v: canonical.get(str(v).strip().lower(), v) if pd.notna(v) else v)
    changed = int((norm.fillna("") != series.fillna("")).sum())
    return norm, changed


def load_raw():
    tables = {
        "candidates": pd.read_csv(RAW / "candidates.csv"),
        "jobs": pd.read_csv(RAW / "jobs.csv"),
        "recruitment_sources": pd.read_csv(RAW / "recruitment_sources.csv"),
        "applications": pd.read_csv(RAW / "applications.csv"),
        "screening_results": pd.read_csv(RAW / "screening_results.csv"),
        "application_stage_history": pd.read_csv(RAW / "application_stage_history.csv"),
        "offers": pd.read_csv(RAW / "offers.csv"),
        "source_costs": pd.read_csv(RAW / "source_costs.csv"),
    }
    for name, df in tables.items():
        for col in df.columns:
            if col.endswith(("_at", "_date", "_timestamp")) or col == "month_start":
                df[col] = pd.to_datetime(df[col], errors="coerce")
    return tables


def clean(t, meta):
    # ---- 1. Text standardization -------------------------------------
    print("1. Standardizing text values")
    CITY = {"mumbai": "Mumbai", "delhi ncr": "Delhi NCR", "bengaluru": "Bengaluru",
            "chennai": "Chennai", "hyderabad": "Hyderabad", "pune": "Pune",
            "kolkata": "Kolkata", "ahmedabad": "Ahmedabad", "jaipur": "Jaipur",
            "kochi": "Kochi", "indore": "Indore", "lucknow": "Lucknow"}
    EDU = {"btech": "BTech", "bsc": "BSc", "bcom": "BCom", "ba": "BA", "mtech": "MTech",
           "mba": "MBA", "mcom": "MCom", "msc": "MSc", "phd": "PhD", "diploma": "Diploma"}
    DEPT = {"technology": "Technology", "sales": "Sales", "operations": "Operations",
            "finance": "Finance", "human resources": "Human Resources",
            "customer support": "Customer Support"}
    EMP = {"full-time": "Full-time", "contract": "Contract", "part-time": "Part-time",
           "full time": "Full-time"}
    STAGE = {"applied": "applied", "screened": "screened", "interview": "interview",
             "offer": "offer", "hired": "hired", "rejected": "rejected"}
    STSTATUS = {"entered": "entered", "passed": "passed", "failed": "failed",
                "withdrawn": "withdrawn"}
    DEC = {"pass": "Pass", "review": "Review", "reject": "Reject"}
    JSTATUS = {"open": "open", "closed": "closed", "on hold": "on hold"}

    c = t["candidates"]
    c["candidate_city"], n = canonical_map(c["candidate_city"], CITY)
    log("candidates.candidate_city", "casing/whitespace standardized", n)
    c["highest_education"], n = canonical_map(c["highest_education"], EDU)
    log("candidates.highest_education", "casing/whitespace standardized", n)

    j = t["jobs"]
    j["department"], n = canonical_map(j["department"], DEPT)
    log("jobs.department", "casing/whitespace standardized", n)
    j["employment_type"], n = canonical_map(j["employment_type"], EMP)
    log("jobs.employment_type", "casing/whitespace standardized", n)
    j["job_status"], n = canonical_map(j["job_status"], JSTATUS)
    log("jobs.job_status", "casing/whitespace standardized", n)

    sh = t["application_stage_history"]
    sh["stage_name"], n = canonical_map(sh["stage_name"], STAGE)
    log("stage_history.stage_name", "casing/whitespace standardized", n)
    sh["stage_status"], n = canonical_map(sh["stage_status"], STSTATUS)
    log("stage_history.stage_status", "casing/whitespace standardized", n)

    s = t["screening_results"]
    s["screening_decision"], n = canonical_map(s["screening_decision"], DEC)
    log("screening_results.screening_decision", "casing/whitespace standardized", n)

    of = t["offers"]
    for col, m in [("offer_status", {"accepted": "accepted", "declined": "declined",
                                     "withdrawn": "withdrawn", "pending": "pending"})]:
        of[col], n = canonical_map(of[col], m)
        log(f"offers.{col}", "casing/whitespace standardized", n)

    a = t["applications"]
    a["current_status"], n = canonical_map(
        a["current_status"], {k: k for k in ["screening", "interview", "offer",
                                             "rejected", "withdrawn", "hired", "declined"]})
    log("applications.current_status", "casing/whitespace standardized", n)

    # ---- 2. Missing source_id ----------------------------------------
    print("2. Resolving missing source_id")
    missing = a["source_id"].isna()
    n_missing = int(missing.sum())
    t["recruitment_sources"] = pd.concat([
        t["recruitment_sources"],
        pd.DataFrame([{"source_id": 8, "source_name": "Unknown / Not Recorded",
                       "source_category": "unclassified"}]),
    ], ignore_index=True)
    a.loc[missing, "source_id"] = 8
    a["source_id"] = a["source_id"].astype(int)
    log("applications.source_id", "imputed as source_id=8 (Unknown / Not Recorded)",
        n_missing, "(FK integrity preserved; rows retained for volume analysis)")

    # ---- 3. Out-of-range screening scores (quarantine) ----------------
    print("3. Quarantining out-of-range screening scores")
    bad_score = (s["ai_score"] < 0) | (s["ai_score"] > 100)
    n_bad = int(bad_score.sum())
    QUAR.mkdir(parents=True, exist_ok=True)
    quarantined = s.loc[bad_score].copy()
    quarantined["quarantine_reason"] = "ai_score outside 0-100"
    quarantined.to_csv(QUAR / "screening_out_of_range.csv", index=False)
    s = s.loc[~bad_score].reset_index(drop=True)
    # keep screening_id sequence stable: screening_id is retained from raw
    t["screening_results"] = s
    log("screening_results", "quarantined to processed/quarantine/screening_out_of_range.csv",
        n_bad, "(applications retained; only their screening rows excluded)")

    # ---- 4. Near-duplicate candidates (merge) -------------------------
    print("4. Merging near-duplicate candidate profiles")
    dup_pairs = meta["near_duplicate_candidate_pairs"]
    reassign = {p["duplicate_candidate_id"]: p["original_candidate_id"] for p in dup_pairs}
    a["candidate_id"] = a["candidate_id"].map(lambda x: reassign.get(x, x)).astype(int)
    t["candidates"] = t["candidates"].loc[~t["candidates"]["candidate_id"].isin(reassign)] \
        .reset_index(drop=True)
    log("candidates", "merged duplicate profiles into originals "
        "(applications reassigned, duplicate rows removed)", len(reassign),
        f"(pairs: {len(reassign)}, applications reassigned: "
        f"{int(sum(1 for x in reassign))} candidate IDs remapped)")

    n_reassigned = int(a["candidate_id"].isin(reassign.values()).sum())
    log("applications.candidate_id", "reassigned from duplicate to original candidate",
        n_reassigned)

    # ---- 5. Repair disordered stage timestamps -------------------------
    print("5. Repairing disordered stage timestamps")
    sh = sh.sort_values(["application_id", "stage_event_id"]).reset_index(drop=True)
    t["application_stage_history"] = sh
    prev_ts = sh.groupby("application_id")["stage_timestamp"].shift(1)
    disordered = sh["stage_timestamp"] < prev_ts
    n_dis = int(disordered.sum())
    sh.loc[disordered, "stage_timestamp"] = prev_ts[disordered] + pd.Timedelta(hours=1)
    log("application_stage_history.stage_timestamp",
        "repaired to previous event + 1 hour", n_dis,
        "(chronology per application restored)")

    # ---- 6. Recompute stage durations ----------------------------------
    print("6. Recomputing stage durations")
    prev = sh.groupby("application_id")["stage_timestamp"].shift(1)
    sh["stage_duration_hours"] = ((sh["stage_timestamp"] - prev).dt.total_seconds() / 3600).round(2)
    log("application_stage_history.stage_duration_hours",
        "recomputed from ordered event sequence", len(sh))

    # ---- 7. Missing optional candidate fields (retain as NULL) ---------
    print("7. Documenting retained NULLs (no imputation)")
    log("candidates.experience_years", "retained as NULL (optional field, not imputed)",
        int(c["experience_years"].isna().sum()))
    log("candidates.highest_education", "retained as NULL (optional field, not imputed)",
        int(c["highest_education"].isna().sum()))

    return t


def validate(t):
    print("\nValidation of processed dataset")
    failures = []

    def chk(name, ok, detail):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
        if not ok:
            failures.append(name)

    a, c, j, s, sh, of = (t["applications"], t["candidates"], t["jobs"],
                          t["screening_results"], t["application_stage_history"], t["offers"])
    chk("PK candidates", c["candidate_id"].is_unique, f"{len(c)} rows")
    chk("PK applications", a["application_id"].is_unique, f"{len(a)} rows")
    chk("FK applications.candidate_id", a["candidate_id"].isin(c["candidate_id"]).all(),
        f"orphans={int((~a['candidate_id'].isin(c['candidate_id'])).sum())}")
    chk("FK applications.source_id", a["source_id"].isin(t["recruitment_sources"]["source_id"]).all(),
        f"nulls={int(a['source_id'].isna().sum())}")
    chk("FK screening.application_id", s["application_id"].isin(a["application_id"]).all(),
        "all resolve")
    chk("Screening scores in 0-100",
        bool(((s["ai_score"] >= 0) & (s["ai_score"] <= 100)).all()),
        f"min={s['ai_score'].min()}, max={s['ai_score'].max()}")
    sh_sorted = sh.sort_values(["application_id", "stage_event_id"])
    prev = sh_sorted.groupby("application_id")["stage_timestamp"].shift(1)
    disordered = int((sh_sorted["stage_timestamp"] < prev).sum())
    chk("Stage history chronological", disordered == 0, f"disordered rows={disordered}")
    hired_apps = set(a.loc[a["current_status"] == "hired", "application_id"])
    hired_events = set(sh.loc[sh["stage_name"] == "hired", "application_id"])
    chk("Canonical hire rule", hired_apps == hired_events,
        f"status={len(hired_apps)}, events={len(hired_events)}")
    for col, allowed in [("jobs.job_status", {"open", "closed", "on hold"}),
                         ("offers.offer_status", {"accepted", "declined", "withdrawn", "pending"}),
                         ("screening_results.screening_decision", {"Pass", "Review", "Reject"})]:
        df, colname = col.split(".")
        bad = set(t[df][colname].dropna().unique()) - allowed
        chk(f"Categories {col}", len(bad) == 0, f"unexpected={bad or 'none'}")

    if failures:
        raise SystemExit(f"Validation failed: {failures}")
    print("  All processed-data checks passed.")


def write_outputs(t, meta):
    PROC.mkdir(parents=True, exist_ok=True)
    for name, df in t.items():
        df.to_csv(PROC / f"{name}.csv", index=False)

    md = ["# HireSight Cleaning Log", "",
          "Produced by `scripts/clean_data.py` from `data/raw/` (seed "
          f"{meta['seed']}). Raw files are never modified.", "",
          "| # | Table / field | Action | Rows affected | Notes |",
          "|---|---|---|---|---|"]
    for i, e in enumerate(STEP_LOG, 1):
        md.append(f"| {i} | {e['step']} | {e['action']} | {e['rows_affected']:,} | {e['detail']} |")
    md += ["", "## Output row counts", "", "| Table | Raw | Processed | Change |", "|---|---|---|---|"]
    for name in ["candidates", "jobs", "recruitment_sources", "applications",
                 "screening_results", "application_stage_history", "offers", "source_costs"]:
        raw_n = meta["row_counts"][name]
        md.append(f"| {name} | {raw_n:,} | {len(t[name]):,} | {len(t[name]) - raw_n:+,} |")
    md += ["", "## Summary of decisions", "",
           "- **Standardization:** all category fields mapped to canonical values "
           "(strip + case-insensitive lookup).",
           "- **Missing `source_id`:** attributed to a new source record "
           "`Unknown / Not Recorded` (source_id = 8, category `unclassified`) so rows stay "
           "analysable and FK integrity holds. Exclude this source from channel "
           "effectiveness comparisons.",
           "- **Out-of-range AI scores:** quarantined to "
           "`processed/quarantine/screening_out_of_range.csv`; the 10 applications keep all "
           "other records. Scores were never clipped or fabricated.",
           "- **Disordered stage timestamps:** set to previous event + 1 hour; all durations "
           "then recomputed from the ordered sequence.",
           "- **Near-duplicate candidates:** the 12 duplicate profiles were merged into their "
           "original candidate (applications reassigned); pairs are listed in "
           "`data/raw/generation_metadata.json`.",
           "- **Missing optional fields (`experience_years`, `highest_education`):** retained "
           "as NULL — imputing would fabricate candidate attributes.",
           "", "## Exclusions from processed data", "",
           f"- 10 screening rows (out-of-range scores) -> quarantine file",
           f"- 12 duplicate candidate rows (merged into originals)",
           "", "All other raw rows are present in the processed dataset."]
    (PROC / "cleaning_log.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nWrote processed CSVs, quarantine file, and cleaning_log.md to {PROC}")


def main():
    meta = json.loads((RAW / "generation_metadata.json").read_text())
    t = load_raw()
    t = clean(t, meta)
    validate(t)
    write_outputs(t, meta)


if __name__ == "__main__":
    main()
