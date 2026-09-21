from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException
)

from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import tempfile
import os

from psycopg.types.json import Jsonb

from backend.resume_parser import extract_text
from backend.analyzer import analyze_Resume
from backend.database import create_database, get_connection

from backend.auth import (
    hash_password,
    verify_password,
    create_token,
    get_current_user
)

load_dotenv()

app = FastAPI(title="HireIQ API")

BASE_DIR = Path(__file__).resolve().parent.parent


@app.get("/")
def frontend():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/style.css")
def css():
    return FileResponse(BASE_DIR / "style.css")


@app.get("/script.js")
def javascript():
    return FileResponse(BASE_DIR / "script.js")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    from backend.database import check_database

    database_status = check_database()

    return {
        "status": "ok",
        "database": "connected" if database_status else "unavailable"
    }


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@app.get("/api/")
def home():
    return {
        "message": "HireIQ API is running 🚀"
    }


# =========================================================
# REGISTER
# =========================================================

@app.post("/api/register")
def register(data: RegisterRequest):

    name = data.name.strip()
    email = data.email.strip().lower()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Name is required"
        )

    if len(data.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters"
        )

    with get_connection() as conn:

        existing = conn.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        ).fetchone()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        hashed = hash_password(data.password)

        cursor = conn.execute(
            """
            INSERT INTO users
            (name, email, password)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (name, email, hashed)
        )

        user_id = cursor.fetchone()["id"]

        conn.commit()

    token = create_token(user_id)

    return {
        "message": "Account created successfully",
        "token": token
    }


# =========================================================
# LOGIN
# =========================================================

@app.post("/api/login")
def login(data: LoginRequest):

    email = data.email.strip().lower()

    with get_connection() as conn:

        user = conn.execute(
            """
            SELECT
                id,
                name,
                email,
                password
            FROM users
            WHERE email = %s
            """,
            (email,)
        ).fetchone()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        data.password,
        user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_token(user["id"])

    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "name": user["name"],
            "email": user["email"]
        }
    }


# =========================================================
# CURRENT USER
# =========================================================

@app.get("/api/me")
def me(user=Depends(get_current_user)):
    return user


# =========================================================
# RESUME ANALYZER
# =========================================================

@app.post("/api/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_role: str = Form(...),
    user=Depends(get_current_user)
):

    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select a resume"
        )

    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF resume"
        )

    content = await resume.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp:

            temp.write(content)
            temp_path = temp.name

        resume_text = extract_text(temp_path)

        if not resume_text or not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )

        result = analyze_Resume(
            resume_text,
            job_role
        )

        if "error" in result:
            raise HTTPException(
                status_code=502,
                detail=result["error"]
            )
        ats_score = result.get(
            "ats_score",
            0
        )

        if isinstance(result, dict):

            possible_score_keys = [
                "score",
                "ats_score",
                "atsScore",
                "ATS Score"
            ]

            for key in possible_score_keys:

                if key in result:

                    try:
                        ats_score = int(float(result[key]))
                    except (ValueError, TypeError):
                        ats_score = None

                    break

        with get_connection() as conn:

            resume_cursor = conn.execute(
                """
                INSERT INTO resumes
                (
                    user_id,
                    filename,
                    resume_text,
                    job_role
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id
                """,
                (
                    user["id"],
                    resume.filename,
                    resume_text,
                    job_role
                )
            )

            resume_id = resume_cursor.fetchone()["id"]

            conn.execute(
                """
                INSERT INTO resume_analysis
                (
                    resume_id,
                    ats_score,
                    analysis
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    resume_id,
                    ats_score,
                    Jsonb(result)
                )
            )

            conn.commit()

        return result

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# =========================================================
# RESUME HISTORY
# =========================================================

@app.get("/api/resumes")
def get_resumes(user=Depends(get_current_user)):

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT
                r.id,
                r.filename,
                r.job_role,
                r.created_at,
                a.ats_score,
                a.analysis
            FROM resumes r
            LEFT JOIN resume_analysis a
                ON a.resume_id = r.id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
            """,
            (user["id"],)
        ).fetchall()

    return {
        "resumes": rows
    }


# =========================================================
# GET SINGLE RESUME
# =========================================================

@app.get("/api/resumes/{resume_id}")
def get_resume(
    resume_id: int,
    user=Depends(get_current_user)
):

    with get_connection() as conn:

        resume = conn.execute(
            """
            SELECT
                r.id,
                r.filename,
                r.job_role,
                r.created_at,
                a.ats_score,
                a.analysis
            FROM resumes r
            LEFT JOIN resume_analysis a
                ON a.resume_id = r.id
            WHERE
                r.id = %s
                AND r.user_id = %s
            """,
            (
                resume_id,
                user["id"]
            )
        ).fetchone()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    return resume


# =========================================================
# DELETE RESUME
# =========================================================

@app.delete("/api/resumes/{resume_id}")
def delete_resume(
    resume_id: int,
    user=Depends(get_current_user)
):

    with get_connection() as conn:

        result = conn.execute(
            """
            DELETE FROM resumes
            WHERE
                id = %s
                AND user_id = %s
            """,
            (
                resume_id,
                user["id"]
            )
        )

        conn.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    return {
        "message": "Resume deleted successfully"
    }
