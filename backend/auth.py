import os
import jwt

from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash

from fastapi import Header, HTTPException

from backend.database import get_connection
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "change-this-development-secret"
)

ALGORITHM = "HS256"


def hash_password(password):
    return password_hash.hash(password)


def verify_password(password, hashed_password):
    return password_hash.verify(
        password,
        hashed_password
    )


def create_token(user_id):

    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=24)
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_user(
    authorization: str = Header(None)
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    try:

        scheme, token = authorization.split()

        if scheme.lower() != "bearer":
            raise ValueError()

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = int(payload["sub"])

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


    conn = get_connection()

    user = conn.execute(
        """
        SELECT id, name, email
        FROM users
        WHERE id = %s
        """,
        (user_id,)
    ).fetchone()

    conn.close()


    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )


    return user