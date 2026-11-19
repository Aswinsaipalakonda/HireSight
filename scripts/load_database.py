"""
HireSight database loader (Phase 3).

Executes database/01_create_database.sql and 02_create_tables.sql, loads the
processed CSVs from data/processed/ into the `hiresight` database, then applies
database/03_constraints_indexes.sql. Finally verifies that loaded row counts
match the processed CSVs and that referential integrity holds (FK checks were
enforced on insert).

Credentials come from .env (see .env.example). Works with MySQL 8.0+ and
MariaDB 10.4+ (XAMPP).
"""

import os
from pathlib import Path

import pandas as pd
import pymysql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "database"
PROC = ROOT / "data" / "processed"

TABLES = [
    "candidates", "jobs", "recruitment_sources", "applications",
    "screening_results", "application_stage_history", "offers", "source_costs",
]
DATE_COLS = {
    "candidates": ["created_at"],
    "jobs": ["posted_date", "closed_date"],
    "applications": ["applied_at"],
    "screening_results": ["screening_date"],
    "application_stage_history": ["stage_timestamp"],
    "offers": ["offer_date", "response_date"],
    "source_costs": ["month_start"],
}


def run_script(conn, path):
    text = "\n".join(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith("--")
    )
    statements = [s.strip() for s in text.split(";") if s.strip()]
    with conn.cursor() as cur:
        for stmt in statements:
            cur.execute(stmt)
    print(f"  executed {path.name} ({len(statements)} statements)")


def insert_table(conn, name):
    df = pd.read_csv(PROC / f"{name}.csv", parse_dates=DATE_COLS.get(name, []))
    # object dtype first so None survives; float columns would re-cast None to NaN
    df = df.astype(object).where(pd.notna(df), None)
    cols = ", ".join(f"`{c}`" for c in df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    sql = f"INSERT INTO {name} ({cols}) VALUES ({placeholders})"
    rows = list(df.itertuples(index=False, name=None))
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    print(f"  loaded {name}: {len(rows):,} rows")


def verify(conn):
    ok = True
    with conn.cursor() as cur:
        for name in TABLES:
            df = pd.read_csv(PROC / f"{name}.csv")
            cur.execute(f"SELECT COUNT(*) FROM {name}")
            db_n = cur.fetchone()[0]
            match = db_n == len(df)
            ok &= match
            print(f"  [{'PASS' if match else 'FAIL'}] {name}: csv={len(df):,} db={db_n:,}")
        # referential integrity spot checks
        checks = [
            ("applications -> candidates/jobs/sources", """
                SELECT COUNT(*) FROM applications a
                LEFT JOIN candidates c ON a.candidate_id = c.candidate_id
                LEFT JOIN jobs j ON a.job_id = j.job_id
                LEFT JOIN recruitment_sources s ON a.source_id = s.source_id
                WHERE c.candidate_id IS NULL OR j.job_id IS NULL OR s.source_id IS NULL"""),
            ("stage/screening/offers -> applications", """
                SELECT
                  (SELECT COUNT(*) FROM application_stage_history h
                   LEFT JOIN applications a ON h.application_id = a.application_id
                   WHERE a.application_id IS NULL)
                  + (SELECT COUNT(*) FROM screening_results sr
                     LEFT JOIN applications a ON sr.application_id = a.application_id
                     WHERE a.application_id IS NULL)
                  + (SELECT COUNT(*) FROM offers o
                     LEFT JOIN applications a ON o.application_id = a.application_id
                     WHERE a.application_id IS NULL)"""),
        ]
        for label, sql in checks:
            cur.execute(sql)
            orphans = cur.fetchone()[0]
            ok &= orphans == 0
            print(f"  [{'PASS' if orphans == 0 else 'FAIL'}] orphans {label}: {orphans}")
    return ok


def main():
    load_dotenv(ROOT / ".env")
    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        charset="utf8mb4",
    )
    try:
        print("Creating schema...")
        run_script(conn, DB / "01_create_database.sql")
        run_script(conn, DB / "02_create_tables.sql")

        print("Loading processed CSVs...")
        conn.begin()
        try:
            for name in TABLES:
                insert_table(conn, name)
            conn.commit()
        except Exception:
            conn.rollback()
            raise

        print("Applying indexes...")
        run_script(conn, DB / "03_constraints_indexes.sql")

        print("Verifying...")
        conn.select_db(os.getenv("DB_NAME", "hiresight"))
        if not verify(conn):
            raise SystemExit("Verification FAILED: row counts or integrity mismatch")
        print("\nDatabase loaded and verified.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
