"""
Entry point untuk Book Search API.
Jalankan dengan: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.database import init_db
from backend.routers import auth, books, reviews


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: jalankan init_db saat server start."""
    init_db()
    print("✅ Database tables initialized successfully.")
    yield
    print("🛑 Server shutting down.")


app = FastAPI(
    title="Book Search API",
    description="API untuk pencarian buku dengan autocomplete Trie, rating, dan komentar.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — agar frontend bisa mengakses API dari domain berbeda
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Sesuaikan dengan domain frontend di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(books.router, prefix="/api/books", tags=["Books"])
app.include_router(reviews.router, prefix="/api/books", tags=["Reviews"])


@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "Book Search API is running", "docs": "/docs"}
