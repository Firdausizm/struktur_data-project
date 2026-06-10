"""
Router untuk rating dan komentar pada buku.

Aturan:
- Rating: satu user satu rating per buku, bisa di-update (POST = upsert).
- Komentar: user boleh berkomentar berkali-kali, bisa dihapus tapi tidak bisa diedit.
"""

from fastapi import APIRouter, HTTPException, Depends
from backend.models.schemas import (
    RatingRequest,
    RatingResponse,
    RatingSummaryResponse,
    CommentRequest,
    CommentResponse,
)
from backend.services import review_service
from backend.routers.auth import get_current_user

router = APIRouter()


# ==================== Rating Endpoints ====================


@router.post("/{volume_id}/rating", response_model=RatingResponse)
def upsert_rating(
    volume_id: str,
    data: RatingRequest,
    current_user: dict = Depends(get_current_user),
):
    """Buat atau update rating untuk sebuah buku (satu user satu rating per buku)."""
    rating = review_service.upsert_rating(
        current_user["id"], volume_id, data.score
    )
    return rating


@router.get("/{volume_id}/rating-summary", response_model=RatingSummaryResponse)
def get_rating_summary(volume_id: str):
    """Rata-rata rating dan jumlah total review untuk sebuah buku."""
    return review_service.get_rating_summary(volume_id)


@router.get("/{volume_id}/my-rating")
def get_my_rating(
    volume_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Ambil rating milik user yang sedang login untuk sebuah buku."""
    rating = review_service.get_user_rating(current_user["id"], volume_id)
    if rating is None:
        return {"message": "Anda belum memberikan rating untuk buku ini"}
    return rating


# ==================== Comment Endpoints ====================


@router.post(
    "/{volume_id}/comments", response_model=CommentResponse, status_code=201
)
def create_comment(
    volume_id: str,
    data: CommentRequest,
    current_user: dict = Depends(get_current_user),
):
    """Tambah komentar pada sebuah buku. User boleh berkomentar berkali-kali."""
    comment = review_service.create_comment(
        current_user["id"], volume_id, data.content
    )
    return comment


@router.get("/{volume_id}/comments", response_model=list[CommentResponse])
def get_comments(volume_id: str):
    """Lihat semua komentar untuk sebuah buku (terbaru duluan)."""
    return review_service.get_comments(volume_id)


@router.delete("/{volume_id}/comments/{comment_id}", status_code=204)
def delete_comment(
    volume_id: str,
    comment_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Hapus komentar milik sendiri. Komentar tidak bisa diedit, hanya bisa dihapus."""
    deleted = review_service.delete_comment(comment_id, current_user["id"])
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Komentar tidak ditemukan atau Anda bukan pemilik komentar ini",
        )
