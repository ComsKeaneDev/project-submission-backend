from pathlib import Path
import os
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DEFAULT_SQLITE = f"file:{(DATA_DIR / 'app.db').as_posix()}?mode=rwc&cache=shared"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE)

def get_conn():
    if DATABASE_URL.startswith(("postgres://", "postgresql://")):
        import psycopg2  # pip install psycopg2-binary
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(
        DATABASE_URL if DATABASE_URL.endswith(".db") else DEFAULT_SQLITE,
        uri=DATABASE_URL.startswith("file:")
    )

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        # Cross-DB friendly schema for a simple registration
        cur.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            year_of_study INTEGER NOT NULL,
            course_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
