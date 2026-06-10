"""
Service untuk autentikasi: hashing password, JWT token, dan operasi user di database.
"""

import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from backend.config import settings
from backend.database import get_connection

# Konteks hashing password menggunakan bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password menggunakan bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi password terhadap hash bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, username: str) -> str:
    """Buat JWT access token dengan masa berlaku tertentu."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> dict | None:
    """Decode JWT token. Return None jika token tidak valid atau sudah kadaluarsa."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def register_user(username: str, email: str, password: str) -> dict:
    """
    Registrasi user baru ke database.
    Raise ValueError jika email atau username sudah terdaftar.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Cek apakah email atau username sudah ada
        cur.execute(
            "SELECT id FROM users WHERE email = %s OR username = %s",
            (email, username),
        )
        if cur.fetchone():
            raise ValueError("Email atau username sudah terdaftar")

        password_hash = hash_password(password)
        cur.execute(
            """INSERT INTO users (username, email, password_hash)
               VALUES (%s, %s, %s)
               RETURNING id, username, email, created_at""",
            (username, email, password_hash),
        )
        user = cur.fetchone()
        conn.commit()
        return dict(user)
    finally:
        cur.close()
        conn.close()


def authenticate_user(email: str, password: str) -> dict | None:
    """
    Autentikasi user berdasarkan email dan password.
    Return data user jika berhasil, None jika gagal.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, username, email, password_hash, created_at FROM users WHERE email = %s",
            (email,),
        )
        user = cur.fetchone()
        if not user:
            return None
        if not verify_password(password, user["password_hash"]):
            return None
        return dict(user)
    finally:
        cur.close()
        conn.close()


def get_user_by_id(user_id: int) -> dict | None:
    """Ambil data user berdasarkan ID."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        user = cur.fetchone()
        return dict(user) if user else None
    finally:
        cur.close()
        conn.close()
