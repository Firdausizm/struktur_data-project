"""
Service untuk operasi rating dan komentar di database PostgreSQL.

Aturan bisnis:
- Rating: Satu user hanya boleh satu rating per buku, bisa di-update.
- Komentar: User boleh berkomentar berkali-kali, bisa dihapus tapi tidak bisa diedit.
"""

from backend.database import get_connection


# ==================== Rating Operations ====================


def upsert_rating(user_id: int, book_id: str, score: int) -> dict:
    """
    Buat atau update rating untuk sebuah buku.
    Jika user sudah pernah memberi rating, score akan di-update.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO ratings (user_id, book_id, score)
               VALUES (%s, %s, %s)
               ON CONFLICT (user_id, book_id)
               DO UPDATE SET score = EXCLUDED.score, updated_at = CURRENT_TIMESTAMP
               RETURNING id, user_id, book_id, score, created_at, updated_at""",
            (user_id, book_id, score),
        )
        rating = cur.fetchone()
        conn.commit()

        # Ambil username untuk response
        cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        result = dict(rating)
        result["username"] = user["username"]
        return result
    finally:
        cur.close()
        conn.close()


def get_rating_summary(book_id: str) -> dict:
    """Ambil rata-rata rating dan jumlah total untuk sebuah buku."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT
                   COALESCE(AVG(score), 0) AS average_rating,
                   COUNT(*) AS total_ratings
               FROM ratings
               WHERE book_id = %s""",
            (book_id,),
        )
        result = cur.fetchone()
        return {
            "book_id": book_id,
            "average_rating": round(float(result["average_rating"]), 1),
            "total_ratings": int(result["total_ratings"]),
        }
    finally:
        cur.close()
        conn.close()


def get_user_rating(user_id: int, book_id: str) -> dict | None:
    """Ambil rating milik user tertentu untuk sebuah buku."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT r.id, r.user_id, u.username, r.book_id, r.score,
                      r.created_at, r.updated_at
               FROM ratings r
               JOIN users u ON r.user_id = u.id
               WHERE r.user_id = %s AND r.book_id = %s""",
            (user_id, book_id),
        )
        rating = cur.fetchone()
        return dict(rating) if rating else None
    finally:
        cur.close()
        conn.close()


# ==================== Comment Operations ====================


def create_comment(user_id: int, book_id: str, content: str) -> dict:
    """Buat komentar baru. User boleh berkomentar berkali-kali pada buku yang sama."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO comments (user_id, book_id, content)
               VALUES (%s, %s, %s)
               RETURNING id, user_id, book_id, content, created_at""",
            (user_id, book_id, content),
        )
        comment = cur.fetchone()
        conn.commit()

        # Ambil username untuk response
        cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        result = dict(comment)
        result["username"] = user["username"]
        return result
    finally:
        cur.close()
        conn.close()


def get_comments(book_id: str) -> list[dict]:
    """Ambil semua komentar untuk sebuah buku, diurutkan dari yang terbaru."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT c.id, c.user_id, u.username, c.book_id, c.content, c.created_at
               FROM comments c
               JOIN users u ON c.user_id = u.id
               WHERE c.book_id = %s
               ORDER BY c.created_at DESC""",
            (book_id,),
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def delete_comment(comment_id: int, user_id: int) -> bool:
    """
    Hapus komentar. Hanya pemilik komentar yang bisa menghapus.
    Return True jika berhasil dihapus, False jika tidak ditemukan atau bukan pemilik.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "DELETE FROM comments WHERE id = %s AND user_id = %s RETURNING id",
            (comment_id, user_id),
        )
        deleted = cur.fetchone()
        conn.commit()
        return deleted is not None
    finally:
        cur.close()
        conn.close()
