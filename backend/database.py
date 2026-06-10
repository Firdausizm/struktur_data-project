import psycopg2
from psycopg2.extras import RealDictCursor
from backend.config import settings


def get_connection():
    """Buat koneksi baru ke PostgreSQL. Caller harus menutup koneksi sendiri."""
    return psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        dbname=settings.DB_NAME,
        cursor_factory=RealDictCursor,
    )


def init_db():
    """Buat tabel-tabel yang dibutuhkan jika belum ada."""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Tabel users — menyimpan data login
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabel ratings — satu user satu rating per buku, bisa di-update
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                book_id VARCHAR(50) NOT NULL,
                score INTEGER NOT NULL CHECK (score >= 0 AND score <= 10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, book_id)
            )
        """)

        # Tabel comments — user boleh berkomentar berkali-kali, bisa dihapus tapi tidak diedit
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                book_id VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
    finally:
        cur.close()
        conn.close()
