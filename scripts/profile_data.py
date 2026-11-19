"""
HireSight data profiling and validation.

Loads data/raw/*.csv, reports row counts, dtypes, nulls, duplicates and
distinct keys, and runs the Phase-1 validation checks from the PRD
(Section 20, step 7):

    - primary keys unique and non-null
    - foreign keys resolve (or are counted as documented missing)
    - date columns parse consistently
    - screening scores within 0-100 (out-of-range rows are expected and counted)
    - logical date order within stage history (disordered rows expected and counted)
    - raw file row counts reconcile with generation_metadata.json

Writes data/raw/profile_summary.md and prints the same results.
Exit code 1 if any check fails.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

FAILURES = []
LINES = []


def check(name, passed, detail):
    status = "PASS" if passed else "FAIL"
    line = f"[{status}] {name}: {detail}"
    print(line)
    LINES.append(line)
    if not passed:
        FAILURES.append(line)
    return line


def load_tables():
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
    for col in ["applied_at", "screening_date", "stage_timestamp"]:
        for df in tables.values():
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["created_at"]:
        if col in tables["candidates"].columns:
            tables["candidates"][col] = pd.to_datetime(tables["candidates"][col], errors="coerce")
    for col in ["posted_date", "closed_date", "offer_date", "response_date", "month_start"]:
        for name, df in tables.items():
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
    return tables


def pk_fk_checks(t, meta):
    out = []
    pks = {
        "candidates": "candidate_id", "jobs": "job_id",
        "recruitment_sources": "source_id", "applications": "application_id",
        "screening_results": "screening_id",
        "application_stage_history": "stage_event_id",
        "offers": "offer_id", "source_costs": "source_cost_id",
    }
    for name, col in pks.items():
        df = t[name]
        out.append(check(f"PK {name}.{col}", df[col].notna().all() and df[col].is_unique,
                         f"{len(df)} rows, {df[col].nunique()} distinct, nulls={int(df[col].isna().sum())}"))

    fks = [
        ("applications.candidate_id", t["applications"]["candidate_id"], t["candidates"]["candidate_id"], 0),
        ("applications.job_id", t["applications"]["job_id"], t["jobs"]["job_id"], 0),
        ("applications.source_id", t["applications"]["source_id"], t["recruitment_sources"]["source_id"],
         meta["injected_quality_issues"]["missing_source_id_applications"]),
        ("screening_results.application_id", t["screening_results"]["application_id"],
         t["applications"]["application_id"], 0),
        ("application_stage_history.application_id", t["application_stage_history"]["application_id"],
         t["applications"]["application_id"], 0),
        ("offers.application_id", t["offers"]["application_id"], t["applications"]["application_id"], 0),
        ("source_costs.source_id", t["source_costs"]["source_id"],
         t["recruitment_sources"]["source_id"], 0),
    ]
    for name, child, parent, expected_missing in fks:
        child_valid = child.dropna()
        orphans = (~child_valid.isin(parent)).sum()
        nulls = int(child.isna().sum())
        ok = orphans == 0 and nulls == expected_missing
        out.append(check(f"FK {name}", ok,
                         f"orphans={int(orphans)}, nulls={nulls} (expected nulls={expected_missing})"))


def date_and_value_checks(t, meta):
    out = []
    inj = meta["injected_quality_issues"]

    # Date parsing succeeded everywhere
    for name, df, cols in [
        ("applications", t["applications"], ["applied_at"]),
        ("screening_results", t["screening_results"], ["screening_date"]),
        ("application_stage_history", t["application_stage_history"], ["stage_timestamp"]),
        ("candidates", t["candidates"], ["created_at"]),
        ("jobs", t["jobs"], ["posted_date"]),
        ("offers", t["offers"], ["offer_date"]),
        ("source_costs", t["source_costs"], ["month_start"]),
    ]:
        bad = int(sum(df[c].isna().sum() for c in cols))
        out.append(check(f"Date parse {name}", bad == 0, f"unparseable dates={bad}"))

    # Screening scores
    s = t["screening_results"]["ai_score"]
    out_of_range = int(((s < 0) | (s > 100)).sum())
    out.append(check("Screening scores 0-100 (raw)", out_of_range == inj["out_of_range_screening_scores"],
                     f"out-of-range={out_of_range}, expected={inj['out_of_range_screening_scores']}"))

    # Salaries / costs non-negative
    jobs = t["jobs"]
    out.append(check("Job salary ranges", bool(
        (jobs["salary_min_inr"] > 0).all() and (jobs["salary_max_inr"] >= jobs["salary_min_inr"]).all()),
        f"min range violation={int(((jobs['salary_min_inr'] <= 0) | (jobs['salary_max_inr'] < jobs['salary_min_inr'])).sum())}"))
    out.append(check("Offer salaries non-negative", bool((t["offers"]["offered_salary_inr"] >= 0).all()),
                     f"negative={int((t['offers']['offered_salary_inr'] < 0).sum())}"))
    out.append(check("Source costs non-negative", bool((t["source_costs"]["cost_inr"] >= 0).all()),
                     f"negative={int((t['source_costs']['cost_inr'] < 0).sum())}"))

    # Stage history chronological order (per application), ignoring injected rows.
    # Stage names/statuses are normalized first because a controlled number of
    # rows intentionally carry casing/whitespace issues.
    sh = t["application_stage_history"].sort_values(["application_id", "stage_event_id"])
    ts_prev = sh.groupby("application_id")["stage_timestamp"].shift(1)
    disordered_mask = sh["stage_timestamp"] < ts_prev
    disordered_ids = set(sh.loc[disordered_mask, "stage_event_id"])
    expected_ids = set(meta["invalid_date_order_stage_event_ids"])
    out.append(check("Stage history chronological (raw)",
                     disordered_ids == expected_ids,
                     f"disordered rows={len(disordered_ids)}, expected={len(expected_ids)}, "
                     f"match={disordered_ids == expected_ids}"))

    stage_norm = sh["stage_name"].astype(str).str.strip().str.lower()
    casing_rows = int((stage_norm != sh["stage_name"]).sum())
    out.append(check("Stage name casing issues (raw, intentional)",
                     casing_rows == inj["casing_whitespace_stage_name"],
                     f"corrupted rows={casing_rows}, expected={inj['casing_whitespace_stage_name']}"))

    # Offers: response date order
    of = t["offers"]
    resp_bad = int(((of["offer_status"] != "pending") &
                    of["response_date"].notna() & (of["response_date"] < of["offer_date"])).sum())
    out.append(check("Offer response >= offer date", resp_bad == 0, f"violations={resp_bad}"))
    out.append(check("Pending offers have no response date",
                     bool(of.loc[of["offer_status"] == "pending", "response_date"].isna().all()),
                     f"pending with response_date={int(of.loc[of['offer_status'] == 'pending', 'response_date'].notna().sum())}"))

    # Hired applications have a hired stage event (canonical hire rule)
    hired_apps = set(t["applications"].loc[t["applications"]["current_status"] == "hired", "application_id"])
    hired_events = set(sh.loc[stage_norm == "hired", "application_id"])
    out.append(check("Canonical hire rule", hired_apps == hired_events,
                     f"status hired={len(hired_apps)}, hired events={len(hired_events)}"))

    # Every application has exactly one 'applied/entered' event
    # (pre-screen withdrawals add a second applied/withdrawn row, which is valid)
    status_norm = sh["stage_status"].astype(str).str.strip().str.lower()
    applied_counts = sh.loc[(stage_norm == "applied") & (status_norm == "entered")] \
        .groupby("application_id").size()
    withdrawn_pre_screen = int(((stage_norm == "applied") & (status_norm == "withdrawn")).sum())
    out.append(check("One 'applied/entered' event per application",
                     bool((applied_counts == 1).all()) and len(applied_counts) == len(t["applications"]),
                     f"apps with applied event={len(applied_counts)}, non-single="
                     f"{int((applied_counts != 1).sum())}, pre-screen withdrawals={withdrawn_pre_screen}"))

    # Offer existence matches offer-stage events
    offer_events = set(sh.loc[stage_norm == "offer", "application_id"])
    offer_apps = set(of["application_id"])
    out.append(check("Offer rows match offer stage events", offer_events == offer_apps,
                     f"offer events={len(offer_events)}, offer rows={len(offer_apps)}"))

    # Row counts reconcile with metadata
    for name, df in t.items():
        ok = len(df) == meta["row_counts"][name]
        out.append(check(f"Row count {name}", ok,
                         f"file={len(df)}, metadata={meta['row_counts'][name]}"))


def write_summary(t, meta, lines):
    parts = ["# HireSight Raw Data Profile Summary", "",
             f"Generated by `scripts/profile_data.py` — seed {meta['seed']}, "
             f"period {meta['period']['start']} to {meta['period']['end']}.", "",
             "## Row counts", "", "| Table | Rows |", "|---|---|"]
    for name, df in t.items():
        parts.append(f"| {name} | {len(df):,} |")
    parts += ["", "## Validation results", "", "```"]
    parts += lines
    parts += ["```", "", "## Column overview", ""]
    for name, df in t.items():
        parts += [f"### {name}", "", "| Column | Dtype | Nulls | Distinct | Example |",
                  "|---|---|---|---|---|"]
        for col in df.columns:
            ex = df[col].dropna().iloc[0] if df[col].notna().any() else ""
            ex = str(ex)[:40]
            parts.append(f"| {col} | {df[col].dtype} | {int(df[col].isna().sum()):,} "
                         f"| {df[col].nunique():,} | {ex} |")
        parts.append("")
    parts += ["## Intentional quality issues (from generation_metadata.json)", ""]
    for k, v in meta["injected_quality_issues"].items():
        parts.append(f"- {k}: {v}")
    parts.append("")
    (RAW / "profile_summary.md").write_text("\n".join(parts), encoding="utf-8")


def main():
    meta = json.loads((RAW / "generation_metadata.json").read_text())
    t = load_tables()

    print("=== Primary and foreign key checks ===")
    pk_fk_checks(t, meta)
    print()
    print("=== Date, value, and consistency checks ===")
    date_and_value_checks(t, meta)

    write_summary(t, meta, LINES)
    print()
    print("Summary written to", RAW / "profile_summary.md")

    if FAILURES:
        print(f"\n{len(FAILURES)} CHECK(S) FAILED")
        raise SystemExit(1)
    print("\nAll checks passed (intentional issues found exactly as documented).")


if __name__ == "__main__":
    main()
