import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Loads .env locally.
# On Vercel, environment variables come from Vercel settings.
load_dotenv(BASE_DIR / ".env")


DATABASE_URL = os.getenv("DATABASE_URL")


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    """
    Create and return a PostgreSQL database connection.
    """

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not configured. "
            "Add DATABASE_URL to your environment variables."
        )

    try:
        connection = psycopg.connect(
            DATABASE_URL,
            row_factory=dict_row,
            connect_timeout=10
        )

        return connection

    except Exception as e:
        print("DATABASE CONNECTION ERROR:")
        print(str(e))

        raise RuntimeError(
            "Unable to connect to PostgreSQL database."
        ) from e


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def create_database():
    """
    Create all required HireIQ tables if they don't exist.

    This function is safe to run multiple times because
    CREATE TABLE IF NOT EXISTS is used.
    """

    try:
        conn = get_connection()

        try:

            # -------------------------------------------------
            # USERS TABLE
            # -------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )


            # -------------------------------------------------
            # RESUMES TABLE
            # -------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS resumes (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    job_role TEXT NOT NULL,
                    resume_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT fk_resume_user
                    FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
                )
                """
            )


            # -------------------------------------------------
            # RESUME ANALYSIS TABLE
            # -------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS resume_analysis (
                    id SERIAL PRIMARY KEY,
                    resume_id INTEGER NOT NULL,
                    ats_score INTEGER,
                    analysis JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT fk_analysis_resume
                    FOREIGN KEY (resume_id)
                    REFERENCES resumes(id)
                    ON DELETE CASCADE
                )
                """
            )


            # -------------------------------------------------
            # INDEXES
            # -------------------------------------------------

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_resumes_user_id
                ON resumes(user_id)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_analysis_resume_id
                ON resume_analysis(resume_id)
                """
            )


            conn.commit()

            print("DATABASE INITIALIZATION SUCCESSFUL")

        finally:
            conn.close()

    except Exception as e:

        print("DATABASE INITIALIZATION ERROR:")
        print(str(e))

        # IMPORTANT:
        # Do not crash the whole FastAPI application during startup.
        #
        # The application can still start, and the actual API
        # request will show the database error if the database
        # is unavailable.

        return False

    return True


# =========================================================
# DATABASE HEALTH CHECK
# =========================================================

def check_database():
    """
    Check whether PostgreSQL is available.
    """

    try:

        conn = get_connection()

        try:
            result = conn.execute(
                "SELECT 1 AS health"
            ).fetchone()

            return result is not None

        finally:
            conn.close()

    except Exception as e:

        print("DATABASE HEALTH CHECK FAILED:")
        print(str(e))

        return False