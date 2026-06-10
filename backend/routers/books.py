"""
Router untuk pencarian buku: search via Google Books API, autocomplete via Trie, dan detail buku.
"""

from fastapi import APIRouter, HTTPException, Query
from backend.models.schemas import BookSearchResponse, BookDetailResponse
from backend.services import book_service, review_service

router = APIRouter()


@router.get("/search", response_model=BookSearchResponse)
def search_books(
    q: str = Query(..., min_length=1, description="Kata kunci pencarian"),
):
    """
    Cari buku via Google Books API.
    Judul buku dari hasil pencarian dan query itu sendiri akan di-insert ke Trie
    untuk keperluan autocomplete di kemudian hari.
    """
    try:
        result = book_service.search_books(q)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Gagal mengambil data dari Google Books API: {str(e)}",
        )


@router.get("/suggestions")
def get_suggestions(
    q: str = Query(..., min_length=1, description="Prefix untuk autocomplete"),
    limit: int = Query(10, ge=1, le=20, description="Jumlah maksimal saran"),
):
    """Dapatkan saran autocomplete dari Trie berdasarkan prefix yang diketik user."""
    suggestions = book_service.get_suggestions(q, limit)
    return {"query": q, "suggestions": suggestions}


@router.get("/{volume_id}", response_model=BookDetailResponse)
def get_book_detail(volume_id: str):
    """
    Ambil detail satu buku dari Google Books API berdasarkan volumeId.
    Response juga menyertakan rata-rata rating dari database kita.
    """
    book = book_service.get_book_detail(volume_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Buku tidak ditemukan")

    # Tambahkan info rating dari database kita
    summary = review_service.get_rating_summary(volume_id)
    book["average_rating"] = summary["average_rating"]
    book["total_ratings"] = summary["total_ratings"]

    return book
