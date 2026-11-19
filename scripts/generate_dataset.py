"""
HireSight synthetic ATS dataset generator.

Generates a deterministic (seed = 42) synthetic recruitment dataset:
    candidates, jobs, recruitment_sources, applications, screening_results,
    application_stage_history, offers, source_costs

All output goes to data/raw/ and is never modified in place. A controlled,
documented set of data-quality issues is injected for cleaning demonstrations
(PRD section 9.2); exact counts are written to generation_metadata.json.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

SEED = 42
rng = np.random.default_rng(SEED)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

N_CANDIDATES = 3500
N_JOBS = 45
N_APPLICATIONS = 8000  # includes 12 applications from near-duplicate profiles

PERIOD_START = pd.Timestamp("2026-01-01")
PERIOD_END = pd.Timestamp("2026-12-31 23:59:59")
SCORING_V2_FROM = pd.Timestamp("2026-07-01")

MONTH_WEIGHTS = {
    1: 1.20, 2: 1.15, 3: 1.30, 4: 1.05, 5: 0.95, 6: 0.80,
    7: 0.70, 8: 0.75, 9: 1.00, 10: 1.25, 11: 1.20, 12: 0.65,
}

CITIES = [
    "Mumbai", "Delhi NCR", "Bengaluru", "Chennai", "Hyderabad", "Pune",
    "Kolkata", "Ahmedabad", "Jaipur", "Kochi", "Indore", "Lucknow",
]
CITY_WEIGHTS = [0.16, 0.15, 0.14, 0.10, 0.11, 0.09, 0.06, 0.05, 0.04, 0.03, 0.04, 0.03]

EDUCATION = [
    "BTech", "BSc", "BCom", "BA", "MTech", "MBA", "MCom", "MSc", "PhD", "Diploma",
]
EDUCATION_WEIGHTS = [0.24, 0.10, 0.14, 0.09, 0.07, 0.13, 0.05, 0.06, 0.02, 0.10]

# (source_name, category, volume weight, screen pass prob, interview->offer prob,
#  offer accept prob, monthly base cost INR)
SOURCE_DEFS = [
    ("Employee Referral",     "referral", 0.10, 0.72, 0.35, 0.85,  18000),
    ("Company Careers Page",  "organic",  0.18, 0.55, 0.27, 0.78,  35000),
    ("Online Job Board",      "paid",     0.34, 0.38, 0.20, 0.68, 175000),
    ("Social Media Ads",      "paid",     0.12, 0.33, 0.18, 0.65, 120000),
    ("Campus Hiring",         "organic",  0.08, 0.45, 0.16, 0.75,  90000),
    ("Recruitment Agency",    "agency",   0.12, 0.60, 0.32, 0.72, 220000),
    ("Walk-in / Job Fair",    "organic",  0.06, 0.30, 0.17, 0.70,  55000),
]

# (title, department, employment_type, salary_min_inr, salary_max_inr, popularity)
JOB_DEFS = [
    ("Software Engineer",        "Technology",        "Full-time",  700000, 2200000, 1.6),
    ("Data Analyst",             "Technology",        "Full-time",  500000, 1400000, 1.8),
    ("QA Engineer",              "Technology",        "Full-time",  450000, 1100000, 1.0),
    ("DevOps Engineer",          "Technology",        "Full-time",  800000, 2400000, 0.8),
    ("Backend Developer",        "Technology",        "Full-time",  700000, 2100000, 1.3),
    ("Frontend Developer",       "Technology",        "Full-time",  600000, 1800000, 1.2),
    ("Data Scientist",           "Technology",        "Full-time",  900000, 2800000, 0.7),
    ("Systems Administrator",    "Technology",        "Full-time",  450000, 1200000, 0.7),
    ("Security Analyst",         "Technology",        "Full-time",  600000, 1800000, 0.5),
    ("Engineering Manager",      "Technology",        "Full-time", 1800000, 3600000, 0.4),
    ("Product Support Engineer", "Technology",        "Full-time",  450000, 1100000, 0.8),
    ("Mobile Developer",         "Technology",        "Contract",   600000, 1900000, 0.7),
    ("Sales Executive",          "Sales",             "Full-time",  300000,  700000, 2.0),
    ("Inside Sales Executive",   "Sales",             "Full-time",  280000,  650000, 1.7),
    ("Sales Manager",            "Sales",             "Full-time",  700000, 1600000, 0.6),
    ("Business Development Exec","Sales",            "Full-time",  320000,  750000, 1.2),
    ("Key Account Manager",      "Sales",             "Full-time",  650000, 1500000, 0.5),
    ("Regional Sales Manager",   "Sales",             "Full-time",  900000, 2000000, 0.4),
    ("Sales Operations Analyst", "Sales",             "Full-time",  400000,  950000, 0.7),
    ("Tele-Sales Executive",     "Sales",             "Full-time",  250000,  550000, 1.1),
    ("Pre-Sales Consultant",     "Sales",             "Full-time",  700000, 1700000, 0.5),
    ("Channel Sales Manager",    "Sales",             "Full-time",  750000, 1800000, 0.4),
    ("Operations Executive",     "Operations",        "Full-time",  280000,  600000, 1.3),
    ("Warehouse Coordinator",   "Operations",        "Full-time",  260000,  550000, 1.0),
    ("Supply Chain Analyst",     "Operations",        "Full-time",  420000,  950000, 0.9),
    ("Operations Manager",       "Operations",        "Full-time",  600000, 1400000, 0.5),
    ("Logistics Coordinator",    "Operations",        "Full-time",  300000,  680000, 0.8),
    ("Process Associate",        "Operations",        "Full-time",  250000,  500000, 1.2),
    ("Inventory Analyst",        "Operations",        "Contract",   350000,  750000, 0.6),
    ("Ops Team Lead",            "Operations",        "Full-time",  450000,  950000, 0.5),
    ("Financial Analyst",        "Finance",           "Full-time",  450000, 1100000, 0.9),
    ("Accounts Executive",       "Finance",           "Full-time",  280000,  620000, 1.0),
    ("Internal Auditor",         "Finance",           "Full-time",  550000, 1300000, 0.5),
    ("Finance Manager",          "Finance",           "Full-time",  900000, 2000000, 0.4),
    ("Payroll Specialist",       "Finance",           "Full-time",  350000,  750000, 0.6),
    ("HR Executive",             "Human Resources",   "Full-time",  300000,  650000, 0.9),
    ("Talent Acquisition Spec.", "Human Resources",   "Full-time",  350000,  800000, 1.0),
    ("HR Business Partner",      "Human Resources",   "Full-time",  700000, 1600000, 0.4),
    ("Recruiting Coordinator",   "Human Resources",   "Full-time",  300000,  600000, 0.6),
    ("Customer Support Exec.",   "Customer Support",  "Full-time",  260000,  520000, 1.6),
    ("Technical Support Engineer","Customer Support", "Full-time",  320000,  700000, 1.3),
    ("Support Team Lead",        "Customer Support",  "Full-time",  420000,  850000, 0.6),
    ("Customer Success Manager", "Customer Support",  "Full-time",  550000, 1200000, 0.7),
    ("Chat Support Executive",   "Customer Support",  "Part-time",   220000,  420000, 0.8),
    ("Field Service Executive",  "Customer Support",  "Full-time",  280000,  600000, 0.9),
]

DEPT_TIME_MULT = {
    "Technology": 1.4, "Finance": 1.5, "Sales": 0.8,
    "Operations": 1.0, "Human Resources": 1.1, "Customer Support": 0.7,
}

# Controlled data-quality issue counts (PRD 9.2)
INJ = {
    "missing_experience_years": 175,
    "missing_highest_education": 105,
    "casing_whitespace_candidates_city": 40,
    "casing_whitespace_candidates_education": 30,
    "casing_whitespace_jobs_department": 8,
    "casing_whitespace_jobs_employment_type": 6,
    "casing_whitespace_stage_name": 100,
    "casing_whitespace_stage_status": 50,
    "casing_whitespace_screening_decision": 40,
    "invalid_date_order_stage_rows": 8,
    "missing_source_id_applications": 15,
    "out_of_range_screening_scores": 10,
    "near_duplicate_candidate_profiles": 12,
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def delay_hours(mean_days, sigma=0.5):
    """Lognormal delay in hours around `mean_days`. Zero values are bumped to 1 hour."""
    h = rng.lognormal(np.log(mean_days * 24), sigma)
    return max(1.0, float(h))


def rand_ts(start, end):
    """Random timestamp inside [start, end], day-of-month 1..28, office hours."""
    span = (end - start).total_seconds()
    offset = rng.uniform(0, span)
    ts = start + pd.Timedelta(seconds=offset)
    return ts.replace(hour=int(rng.integers(8, 21)), minute=int(rng.integers(0, 60)),
                      second=int(rng.integers(0, 60)))


def injected_case_variants(series, n, field_label):
    """Corrupt n sampled non-null entries of a text Series with casing/whitespace issues."""
    idx = series.dropna()
    idx = idx.index[rng.permutation(len(idx))[:n]] if len(idx) >= n else idx.index
    for i in idx:
        s = str(series.loc[i])
        mode = rng.integers(0, 3)
        if mode == 0:
            series.loc[i] = s.upper()
        elif mode == 1:
            series.loc[i] = f" {s.lower()}"
        else:
            series.loc[i] = f"{s}  "
    return len(idx)


# --------------------------------------------------------------------------
# Dimension tables
# --------------------------------------------------------------------------

def build_jobs():
    rows = []
    for i, (title, dept, etype, smin, smax, pop) in enumerate(JOB_DEFS, start=1):
        posted = rand_ts(PERIOD_START, pd.Timestamp("2026-10-31")).normalize()
        status = "closed" if rng.random() < 0.60 else ("on hold" if rng.random() < 0.15 else "open")
        closed = None
        if status == "closed":
            closed = posted + pd.Timedelta(days=int(rng.integers(45, 150)))
            if closed > PERIOD_END:
                closed = PERIOD_END.normalize()
        rows.append({
            "job_id": i,
            "job_title": title,
            "department": dept,
            "location": CITIES[int(rng.choice(len(CITIES), p=CITY_WEIGHTS))],
            "employment_type": etype,
            "salary_min_inr": float(smin),
            "salary_max_inr": float(smax),
            "posted_date": posted.date(),
            "closed_date": closed,
            "job_status": status,
        })
    return pd.DataFrame(rows)


def build_sources():
    return pd.DataFrame({
        "source_id": range(1, len(SOURCE_DEFS) + 1),
        "source_name": [s[0] for s in SOURCE_DEFS],
        "source_category": [s[1] for s in SOURCE_DEFS],
    })


def build_candidates(apps_by_candidate):
    rows = []
    # IDs above N_CANDIDATES are near-duplicate profiles created separately in main()
    for cid in sorted(c for c in apps_by_candidate if c <= N_CANDIDATES):
        exp = round(float(rng.gamma(2.2, 2.3)), 1)  # mean ~5.1 yrs, right-skewed
        if exp > 20:
            exp = 20.0
        edu = EDUCATION[int(rng.choice(len(EDUCATION), p=EDUCATION_WEIGHTS))]
        first_applied = min(a["applied_at"] for a in apps_by_candidate[cid])
        created = first_applied - pd.Timedelta(hours=float(rng.uniform(1, 24 * 120)))
        if created < pd.Timestamp("2025-10-01"):
            created = pd.Timestamp("2025-10-01")
        rows.append({
            "candidate_id": cid,
            "experience_years": exp,
            "highest_education": edu,
            "candidate_city": CITIES[int(rng.choice(len(CITIES), p=CITY_WEIGHTS))],
            "created_at": created,
        })
    df = pd.DataFrame(rows)

    # Injected quality issues: missing values
    idx = rng.permutation(len(df))[:INJ["missing_experience_years"]]
    df.loc[df.index[idx], "experience_years"] = np.nan
    idx = rng.permutation(len(df))[:INJ["missing_highest_education"]]
    df.loc[df.index[idx], "highest_education"] = np.nan

    # Injected quality issues: casing / whitespace
    for col, label in [("candidate_city", "casing_whitespace_candidates_city"),
                      ("highest_education", "casing_whitespace_candidates_education")]:
        series = df[col].astype(object)
        n = injected_case_variants(series, INJ[label], label)
        df[col] = series
        injected_counts[label] = n
    return df


# --------------------------------------------------------------------------
# Application / funnel generation
# --------------------------------------------------------------------------

def generate_application(app_id, cand_id, job, source_row):
    """Simulate one application's funnel path and emit event rows."""
    src = SOURCE_DEFS[source_row - 1]
    _, _, _, p_screen, p_int_offer, p_accept, _ = src
    dept_mult = DEPT_TIME_MULT[job["department"]]
    scale = job["pop_scale"]

    t_applied = rand_ts(max(job["posted"], PERIOD_START),
                        min(job["closed"] or pd.Timestamp("2026-12-15"), PERIOD_END))
    events = [("applied", "entered", t_applied)]
    cur = t_applied

    # Withdraw before screening
    if rng.random() < 0.05:
        t = cur + pd.Timedelta(hours=delay_hours(3))
        if t > PERIOD_END:
            return events, "screening", None, None
        events.append(("applied", "withdrawn", t))
        return events, "withdrawn", None, None

    # Screening
    t_screen = cur + pd.Timedelta(hours=delay_hours(5))
    if t_screen > PERIOD_END:
        return events, "screening", None, None
    u = rng.random()
    if u < p_screen:
        decision, screen_pass = "Pass", True
        score_mean = 68
    elif u < p_screen + 0.12:
        decision, screen_pass = "Review", bool(rng.random() < 0.5)
        score_mean = 57
        t_screen = t_screen + pd.Timedelta(hours=delay_hours(2))
        if t_screen > PERIOD_END:
            return events, "screening", None, None
    else:
        decision, screen_pass = "Reject", False
        score_mean = 46
    if t_screen > PERIOD_END:
        return events, "screening", None, None
    score = float(np.clip(rng.normal(score_mean, 12), 0, 100))
    events.append(("screened", "passed" if screen_pass else "failed", t_screen))
    if not screen_pass:
        return events, "rejected", (t_screen, score, decision), None

    # Interview (1-2 rounds)
    t_int = t_screen + pd.Timedelta(hours=delay_hours(7 * dept_mult * scale))
    if t_int > PERIOD_END:
        return events, "interview", (t_screen, score, decision), None
    u = rng.random()
    if u < 0.05:
        events.append(("interview", "withdrawn", t_int))
        return events, "withdrawn", (t_screen, score, decision), None
    if u < 0.35:
        events.append(("interview", "failed", t_int))
        return events, "rejected", (t_screen, score, decision), None
    events.append(("interview", "passed", t_int))
    cur = t_int

    if rng.random() < 0.45:  # second round
        t_int2 = cur + pd.Timedelta(hours=delay_hours(6 * dept_mult * scale))
        if t_int2 > PERIOD_END:
            return events, "interview", (t_screen, score, decision), None
        u = rng.random()
        if u < 0.04:
            events.append(("interview", "withdrawn", t_int2))
            return events, "withdrawn", (t_screen, score, decision), None
        if u < 0.22:
            events.append(("interview", "failed", t_int2))
            return events, "rejected", (t_screen, score, decision), None
        events.append(("interview", "passed", t_int2))
        cur = t_int2

    # Offer (only a share of successful interviews result in an offer)
    t_offer = cur + pd.Timedelta(hours=delay_hours(4 * dept_mult * scale))
    if t_offer > PERIOD_END:
        return events, "interview", (t_screen, score, decision), None
    if rng.random() >= min(0.50, p_int_offer * 1.6):
        t_no_offer = cur + pd.Timedelta(hours=delay_hours(2))
        if t_no_offer > PERIOD_END:
            return events, "interview", (t_screen, score, decision), None
        events.append(("rejected", "failed", t_no_offer))
        return events, "rejected", (t_screen, score, decision), None
    u = rng.random()
    if u < p_accept:
        offer_status, stage_status = "accepted", "passed"
    elif u < p_accept + 0.18:
        offer_status, stage_status = "declined", "failed"
    elif u < p_accept + 0.18 + 0.06:
        offer_status, stage_status = "withdrawn", "withdrawn"
    else:
        offer_status, stage_status = "pending", "entered"
    events.append(("offer", stage_status, t_offer))

    if offer_status == "pending":
        return events, "offer", (t_screen, score, decision), (t_offer, offer_status, None)

    t_resp = t_offer + pd.Timedelta(hours=delay_hours(6))
    if t_resp > PERIOD_END:
        return events, "offer", (t_screen, score, decision), (t_offer, "pending", None)
    if offer_status == "accepted":
        events.append(("hired", "entered", t_resp))
        return events, "hired", (t_screen, score, decision), (t_offer, offer_status, t_resp)
    return events, offer_status, (t_screen, score, decision), (t_offer, offer_status, t_resp)


def main():
    global injected_counts
    injected_counts = {}

    print("Generating jobs, sources...")
    jobs_df = build_jobs()
    sources_df = build_sources()
    job_pop = np.array([pop for *_, pop in JOB_DEFS])
    job_pop = job_pop / job_pop.sum()
    source_vol = np.array([s[2] for s in SOURCE_DEFS])
    source_vol = source_vol / source_vol.sum()
    month_w = np.array([MONTH_WEIGHTS[m] for m in range(1, 13)])
    month_w = month_w / month_w.sum()

    # --- assign applications to candidates (1-5 apps each) -----------------
    print("Assigning applications to candidates...")
    counts = rng.choice([1, 2, 3, 4, 5], size=N_CANDIDATES, p=[0.30, 0.30, 0.20, 0.12, 0.08])
    target = N_APPLICATIONS - INJ["near_duplicate_candidate_profiles"]
    total = int(counts.sum())
    while total > target:
        i = int(rng.integers(0, N_CANDIDATES))
        if counts[i] > 1:
            counts[i] -= 1
            total -= 1
    while total < target:
        i = int(rng.integers(0, N_CANDIDATES))
        if counts[i] < 5:
            counts[i] += 1
            total += 1
    cand_pool = np.repeat(np.arange(1, N_CANDIDATES + 1), counts)
    cand_pool = cand_pool[rng.permutation(len(cand_pool))]
    dup_cands = list(range(N_CANDIDATES + 1, N_CANDIDATES + 1 + INJ["near_duplicate_candidate_profiles"]))
    cand_pool = np.append(cand_pool, dup_cands)  # one application per duplicate profile

    # --- simulate the funnel ---------------------------------------------
    print("Simulating application funnel...")
    jobs_meta = jobs_df.to_dict("records")
    for jm in jobs_meta:
        jm["posted"] = pd.Timestamp(jm["posted_date"])
        jm["closed"] = pd.Timestamp(jm["closed_date"]) if pd.notna(jm["closed_date"]) else None
        jm["pop_scale"] = 1.0 if jm["department"] in ("Sales", "Customer Support") else \
            {"Technology": 1.3, "Finance": 1.5, "Human Resources": 1.1, "Operations": 1.1}[jm["department"]]

    app_rows, stage_rows, screen_rows, offer_rows = [], [], [], []
    apps_by_candidate = {c: [] for c in range(1, N_CANDIDATES + 1 + len(dup_cands))}
    job_ids = rng.choice(N_JOBS, size=N_APPLICATIONS, p=job_pop) + 1
    source_ids = rng.choice(len(SOURCE_DEFS), size=N_APPLICATIONS, p=source_vol) + 1

    for i in range(N_APPLICATIONS):
        app_id = i + 1
        cand_id = int(cand_pool[i])
        job = jobs_meta[int(job_ids[i]) - 1]
        source_id = int(source_ids[i])
        events, status, screen, offer = generate_application(app_id, cand_id, job, source_id)

        # month seasonality: bias applied_at month, moving only earlier so all
        # downstream stage timestamps stay inside the period
        old_applied = events[0][2]
        if rng.random() < 0.5:
            m = int(rng.choice(12, p=month_w)) + 1
            cand_ts = old_applied.replace(month=m, day=int(rng.integers(1, 29)))
            cand_ts = cand_ts.replace(hour=int(rng.integers(8, 21)),
                                      minute=int(rng.integers(0, 60)))
            if cand_ts >= job["posted"] and cand_ts <= old_applied:
                t_applied = cand_ts
                delta = t_applied - old_applied
                events = [(s, st, t_applied if k == 0 else t + delta)
                          for k, (s, st, t) in enumerate(events)]

        app_rows.append({
            "application_id": app_id,
            "candidate_id": cand_id,
            "job_id": job["job_id"],
            "source_id": source_id,
            "applied_at": events[0][2],
            "current_status": status,
        })
        apps_by_candidate[cand_id].append({"applied_at": events[0][2]})

        for k, (stage, st_status, ts) in enumerate(events):
            prev_ts = events[k - 1][2] if k > 0 else None
            dur = None if prev_ts is None else round((ts - prev_ts).total_seconds() / 3600, 2)
            stage_rows.append({
                "stage_event_id": len(stage_rows) + 1,
                "application_id": app_id,
                "stage_name": stage,
                "stage_status": st_status,
                "stage_timestamp": ts,
                "stage_duration_hours": dur,
            })

        if screen is not None:
            t_screen, score, decision = screen
            version = "v2.1" if t_screen >= SCORING_V2_FROM else "v1.0"
            screen_rows.append({
                "screening_id": len(screen_rows) + 1,
                "application_id": app_id,
                "screening_date": t_screen,
                "ai_score": round(score, 2),
                "screening_decision": decision,
                "score_version": version,
            })
        if offer is not None:
            t_offer, offer_status, t_resp = offer
            beta = rng.beta(3, 2)
            salary = job["salary_min_inr"] + (job["salary_max_inr"] - job["salary_min_inr"]) * beta
            offer_rows.append({
                "offer_id": len(offer_rows) + 1,
                "application_id": app_id,
                "offer_date": t_offer.date(),
                "offered_salary_inr": round(float(salary) / 1000) * 1000,
                "offer_status": offer_status,
                "response_date": t_resp.date() if t_resp is not None else None,
            })

    applications = pd.DataFrame(app_rows)
    stage_history = pd.DataFrame(stage_rows)
    screening = pd.DataFrame(screen_rows)
    offers = pd.DataFrame(offer_rows)

    print("Building candidates...")
    candidates = build_candidates(apps_by_candidate)

    # Near-duplicate candidate profiles: exact attribute copies with new IDs
    dup_pairs = []
    dup_rows = []
    src_idx = rng.permutation(N_CANDIDATES)[:len(dup_cands)]
    for dup_id, src_pos in zip(dup_cands, src_idx):
        src = candidates.iloc[src_pos]
        first_applied = min(a["applied_at"] for a in apps_by_candidate[dup_id])
        created = first_applied - pd.Timedelta(hours=float(rng.uniform(1, 24 * 120)))
        if created < pd.Timestamp("2025-10-01"):
            created = pd.Timestamp("2025-10-01")
        dup_rows.append({**src.to_dict(), "candidate_id": dup_id, "created_at": created})
        dup_pairs.append({"duplicate_candidate_id": int(dup_id),
                          "original_candidate_id": int(src["candidate_id"])})
    candidates = pd.concat([candidates, pd.DataFrame(dup_rows)], ignore_index=True)
    candidates = candidates.sort_values("candidate_id").reset_index(drop=True)
    injected_counts["near_duplicate_candidate_profiles"] = len(dup_pairs)

    # --- source costs ------------------------------------------------------
    source_costs = []
    for sid, s in enumerate(SOURCE_DEFS, start=1):
        for month in range(1, 13):
            cost = s[6] * rng.uniform(0.75, 1.3)
            if s[0] == "Campus Hiring" and month in (3, 7, 8, 9):
                cost *= 1.8  # campus season spikes
            source_costs.append({
                "source_cost_id": len(source_costs) + 1,
                "source_id": sid,
                "month_start": pd.Timestamp(2026, month, 1).date(),
                "cost_inr": round(float(cost), 2),
            })
    source_costs = pd.DataFrame(source_costs)

    # --- inject remaining quality issues ----------------------------------
    print("Injecting documented data-quality issues...")

    injected_counts["casing_whitespace_jobs_department"] = injected_case_variants(
        jobs_df["department"].astype(object), INJ["casing_whitespace_jobs_department"], "jobs_department")
    injected_counts["casing_whitespace_jobs_employment_type"] = injected_case_variants(
        jobs_df["employment_type"].astype(object), INJ["casing_whitespace_jobs_employment_type"], "jobs_employment_type")

    # Missing source_id in applications
    idx = rng.permutation(len(applications))[:INJ["missing_source_id_applications"]]
    applications["source_id"] = applications["source_id"].astype("Int64")
    applications.loc[applications.index[idx], "source_id"] = pd.NA
    injected_counts["missing_source_id_applications"] = len(idx)

    # Out-of-range screening scores
    idx = rng.permutation(len(screening))[:INJ["out_of_range_screening_scores"]]
    for i in idx:
        if rng.random() < 0.5:
            screening.loc[screening.index[i], "ai_score"] = round(float(rng.uniform(102, 145)), 2)
        else:
            screening.loc[screening.index[i], "ai_score"] = round(-float(rng.uniform(1, 12)), 2)
        screening.loc[screening.index[i], "screening_decision"] = "Review"
    injected_counts["out_of_range_screening_scores"] = len(idx)

    # Casing / whitespace in stage history and screening decision
    for col, label in [("stage_name", "casing_whitespace_stage_name"),
                       ("stage_status", "casing_whitespace_stage_status")]:
        series = stage_history[col].astype(object)
        n = injected_case_variants(series, INJ[label], label)
        stage_history[col] = series
        injected_counts[label] = n
    series = screening["screening_decision"].astype(object)
    n = injected_case_variants(series, INJ["casing_whitespace_screening_decision"], "sd")
    screening["screening_decision"] = series
    injected_counts["casing_whitespace_screening_decision"] = n

    # Invalid date order in stage history: event earlier than its predecessor
    bad_ids = []
    groups = stage_history.groupby("application_id", sort=False)
    eligible = [g for _, g in groups if len(g) > 1]
    picked = [eligible[i] for i in rng.permutation(len(eligible))[:INJ["invalid_date_order_stage_rows"]]]
    for g in picked:
        pos = int(rng.integers(1, len(g)))
        row_i = g.index[pos]
        prev_i = g.index[pos - 1]
        stage_history.loc[row_i, "stage_timestamp"] = \
            stage_history.loc[prev_i, "stage_timestamp"] - pd.Timedelta(hours=float(rng.uniform(24, 240)))
        bad_ids.append(int(stage_history.loc[row_i, "stage_event_id"]))
    injected_counts["invalid_date_order_stage_rows"] = len(bad_ids)

    injected_counts["missing_experience_years"] = int(candidates["experience_years"].isna().sum())
    injected_counts["missing_highest_education"] = int(candidates["highest_education"].isna().sum())

    # --- write outputs -----------------------------------------------------
    print("Writing CSVs to data/raw/ ...")
    RAW.mkdir(parents=True, exist_ok=True)
    jobs_df.to_csv(RAW / "jobs.csv", index=False)
    sources_df.to_csv(RAW / "recruitment_sources.csv", index=False)
    candidates.to_csv(RAW / "candidates.csv", index=False)
    applications.to_csv(RAW / "applications.csv", index=False)
    screening.to_csv(RAW / "screening_results.csv", index=False)
    stage_history.to_csv(RAW / "application_stage_history.csv", index=False)
    offers.to_csv(RAW / "offers.csv", index=False)
    source_costs.to_csv(RAW / "source_costs.csv", index=False)

    metadata = {
        "seed": SEED,
        "period": {"start": "2026-01-01", "end": "2026-12-31"},
        "row_counts": {
            "candidates": len(candidates),
            "jobs": len(jobs_df),
            "recruitment_sources": len(sources_df),
            "applications": len(applications),
            "screening_results": len(screening),
            "application_stage_history": len(stage_history),
            "offers": len(offers),
            "source_costs": len(source_costs),
        },
        "outcome_summary": applications["current_status"].value_counts().to_dict(),
        "near_duplicate_candidate_pairs": dup_pairs,
        "invalid_date_order_stage_event_ids": bad_ids,
        "injected_quality_issues": injected_counts,
        "notes": (
            "All data is synthetic. No real names, emails, phone numbers or addresses. "
            "AI screening scores are simulated with intentional overlap between outcomes; "
            "no causal relationship is implied. Raw files are immutable; run "
            "scripts/clean_data.py (Phase 2) to produce data/processed outputs."
        ),
    }
    (RAW / "generation_metadata.json").write_text(json.dumps(metadata, indent=2))

    print("Done.")
    print(json.dumps(metadata["row_counts"], indent=2))
    print("Outcomes:", json.dumps(metadata["outcome_summary"]))


if __name__ == "__main__":
    main()
