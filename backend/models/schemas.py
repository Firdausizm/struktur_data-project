"""
Pydantic schemas untuk validasi request dan format response.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ==================== Auth Schemas ====================


class UserRegisterRequest(BaseModel):
    """Request body untuk registrasi user baru."""

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=72)


class UserLoginRequest(BaseModel):
    """Request body untuk login."""

    email: str
    password: str


class UserResponse(BaseModel):
    """Response format untuk data user."""

    id: int
    username: str
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    """Response format setelah login berhasil."""

    access_token: str
    token_type: str = "bearer"


# ==================== Book Schemas ====================


class BookItem(BaseModel):
    """Format ringkas satu buku untuk hasil pencarian."""

    volume_id: str
    title: str
    authors: list[str] = []
    published_date: str = ""
    thumbnail: str = ""
    description: str = ""


class BookSearchResponse(BaseModel):
    """Response format untuk hasil pencarian buku."""

    query: str
    total_results: int
    books: list[BookItem]


class BookDetailResponse(BookItem):
    """Response format untuk detail satu buku — lebih lengkap dari BookItem."""

    publisher: str = ""
    page_count: int = 0
    categories: list[str] = []
    language: str = ""
    preview_link: str = ""
    average_rating: Optional[float] = None
    total_ratings: int = 0


# ==================== Rating Schemas ====================


class RatingRequest(BaseModel):
    """Request body untuk memberi/update rating."""

    score: int = Field(..., ge=0, le=10)


class RatingResponse(BaseModel):
    """Response format untuk data rating."""

    id: int
    user_id: int
    username: str
    book_id: str
    score: int
    created_at: datetime
    updated_at: datetime


class RatingSummaryResponse(BaseModel):
    """Response format untuk ringkasan rating sebuah buku."""

    book_id: str
    average_rating: float
    total_ratings: int


# ==================== Comment Schemas ====================


class CommentRequest(BaseModel):
    """Request body untuk membuat komentar."""

    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    """Response format untuk data komentar."""

    id: int
    user_id: int
    username: str
    book_id: str
    content: str
    created_at: datetime
