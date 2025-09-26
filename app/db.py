from pathlib import Path
import os
import sqlite3

# --- DATABASE CONNECTION LOGIC ---

def get_conn():
    # Check if running in AWS with Elastic Beanstalk's RDS variables
    if "RDS_HOSTNAME" in os.environ:
        import psycopg2
        
        hostname = os.environ['RDS_HOSTNAME']
        port = os.environ['RDS_PORT']
        username = os.environ['RDS_USERNAME']
        password = os.environ['RDS_PASSWORD']
        dbname = os.environ['RDS_DB_NAME']
        
        # Assemble the connection string from EB's variables
        conn_string = f"postgresql://{username}:{password}@{hostname}:{port}/{dbname}"
        return psycopg2.connect(conn_string)
    
    # Fallback for local development (using SQLite)
    else:
        BASE_DIR = Path(__file__).resolve().parent.parent
        DATA_DIR = BASE_DIR / "data"
        DATA_DIR.mkdir(exist_ok=True)
        db_path = (DATA_DIR / 'app.db').as_posix()
        
        return sqlite3.connect(f"file:{db_path}?mode=rwc&cache=shared", uri=True)

# --- DATABASE INITIALIZATION ---

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        
        # Use different PRIMARY KEY syntax for PostgreSQL vs SQLite
        is_postgres = hasattr(conn, 'encoding') 

        if is_postgres:
            # PostgreSQL uses SERIAL for auto-incrementing keys
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS registrations (
                id SERIAL PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                year_of_study INTEGER,
                course_name TEXT,
                additional_info TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:
            # SQLite uses INTEGER PRIMARY KEY AUTOINCREMENT
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                year_of_study INTEGER,
                course_name TEXT,
                additional_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
        cur.execute(create_table_sql)
        conn.commit()