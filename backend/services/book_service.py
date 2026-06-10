"""
Service untuk integrasi Google Books API dan manajemen Trie autocomplete.
"""

import requests
from backend.config import settings
from backend.trie import Trie

# Instance Trie global — hidup selama server berjalan (in-memory)
book_trie = Trie()

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"


def search_books(query: str, max_results: int = 20) -> dict:
    """
    Cari buku via Google Books API.
    Setiap judul buku dari hasil pencarian di-insert ke Trie untuk autocomplete.
    Query itu sendiri juga di-insert ke Trie.
    """
    params = {
        "q": query,
        "maxResults": min(max_results, 40),  # Google Books API max 40
        "key": settings.GOOGLE_BOOKS_API_KEY,
    }

    response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
    response.raise_for_status()
    data = response.json()

    total = data.get("totalItems", 0)
    items = data.get("items", [])

    books = []
    for item in items:
        info = item.get("volumeInfo", {})
        book = {
            "volume_id": item.get("id", ""),
            "title": info.get("title", ""),
            "authors": info.get("authors", []),
            "published_date": info.get("publishedDate", ""),
            "thumbnail": info.get("imageLinks", {}).get("thumbnail", ""),
            "description": (
                info.get("description", "")[:300]
                if info.get("description")
                else ""
            ),
        }
        books.append(book)

        # Insert judul buku ke Trie untuk autocomplete
        if book["title"]:
            book_trie.insert(book["title"])

    # Insert query itu sendiri ke Trie
    book_trie.insert(query)

    return {
        "query": query,
        "total_results": total,
        "books": books,
    }


def get_book_detail(volume_id: str) -> dict | None:
    """Ambil detail satu buku dari Google Books API berdasarkan volumeId."""
    url = f"{GOOGLE_BOOKS_API_URL}/{volume_id}"
    params = {"key": settings.GOOGLE_BOOKS_API_KEY}

    response = requests.get(url, params=params)
    if response.status_code == 404:
        return None
    response.raise_for_status()

    item = response.json()
    info = item.get("volumeInfo", {})

    return {
        "volume_id": item.get("id", ""),
        "title": info.get("title", ""),
        "authors": info.get("authors", []),
        "published_date": info.get("publishedDate", ""),
        "thumbnail": info.get("imageLinks", {}).get("thumbnail", ""),
        "description": info.get("description", ""),
        "publisher": info.get("publisher", ""),
        "page_count": info.get("pageCount", 0),
        "categories": info.get("categories", []),
        "language": info.get("language", ""),
        "preview_link": info.get("previewLink", ""),
    }


def get_suggestions(prefix: str, limit: int = 10) -> list[str]:
    """Dapatkan saran autocomplete dari Trie berdasarkan prefix."""
    return book_trie.get_suggestions(prefix, limit)
