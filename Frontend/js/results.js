/**
 * results.js — Logic untuk halaman hasil pencarian buku.
 */

document.addEventListener('DOMContentLoaded', () => {
  renderNavbar();

  const params = new URLSearchParams(window.location.search);
  const query = params.get('q') || '';

  const searchInput = document.getElementById('search-input');
  const searchForm = document.getElementById('search-form');
  const bookGrid = document.getElementById('book-grid');
  const resultsQuery = document.getElementById('results-query');
  const loading = document.getElementById('loading');
  const emptyState = document.getElementById('empty-state');
  const dropdown = document.getElementById('autocomplete-dropdown');

  // Pre-fill search input
  searchInput.value = query;

  // ── Search Form ──
  searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const q = searchInput.value.trim();
    if (q) {
      window.location.href = `/results.html?q=${encodeURIComponent(q)}`;
    }
  });

  // ── Autocomplete (same as home.js) ──
  let debounceTimer = null;
  let activeIndex = -1;
  let suggestions = [];

  searchInput.addEventListener('input', () => {
    const q = searchInput.value.trim();
    clearTimeout(debounceTimer);
    activeIndex = -1;

    if (q.length < 1) {
      hideDropdown();
      return;
    }

    debounceTimer = setTimeout(async () => {
      try {
        const data = await apiGetSuggestions(q, 8);
        suggestions = data.suggestions || [];
        renderSuggestions(suggestions, q);
      } catch {
        hideDropdown();
      }
    }, 300);
  });

  searchInput.addEventListener('keydown', (e) => {
    const items = dropdown.querySelectorAll('.autocomplete-item');
    if (!items.length) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      activeIndex = Math.min(activeIndex + 1, items.length - 1);
      updateActiveItem(items);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      activeIndex = Math.max(activeIndex - 1, -1);
      updateActiveItem(items);
    } else if (e.key === 'Enter' && activeIndex >= 0) {
      e.preventDefault();
      const selected = suggestions[activeIndex];
      searchInput.value = selected;
      hideDropdown();
      window.location.href = `/results.html?q=${encodeURIComponent(selected)}`;
    } else if (e.key === 'Escape') {
      hideDropdown();
    }
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('#search-container')) {
      hideDropdown();
    }
  });

  function renderSuggestions(items, q) {
    if (!items.length) { hideDropdown(); return; }
    dropdown.innerHTML = items.map((item, i) => {
      const highlighted = highlightMatch(item, q);
      return `<div class="autocomplete-item" data-index="${i}">${highlighted}</div>`;
    }).join('');
    dropdown.classList.add('active');
    dropdown.querySelectorAll('.autocomplete-item').forEach(el => {
      el.addEventListener('click', () => {
        const idx = parseInt(el.dataset.index);
        searchInput.value = items[idx];
        hideDropdown();
        window.location.href = `/results.html?q=${encodeURIComponent(items[idx])}`;
      });
    });
  }

  function highlightMatch(text, q) {
    const lowerText = text.toLowerCase();
    const lowerQ = q.toLowerCase();
    const idx = lowerText.indexOf(lowerQ);
    if (idx === -1) return escapeHtml(text);
    const before = text.slice(0, idx);
    const match = text.slice(idx, idx + q.length);
    const after = text.slice(idx + q.length);
    return `${escapeHtml(before)}<strong style="color:var(--on-primary)">${escapeHtml(match)}</strong>${escapeHtml(after)}`;
  }

  function updateActiveItem(items) {
    items.forEach((el, i) => el.classList.toggle('active', i === activeIndex));
    if (activeIndex >= 0) searchInput.value = suggestions[activeIndex];
  }

  function hideDropdown() {
    dropdown.classList.remove('active');
    dropdown.innerHTML = '';
    activeIndex = -1;
  }

  // ── Fetch & Render Books ──
  if (query) {
    fetchBooks(query);
  } else {
    resultsQuery.innerHTML = 'Masukkan kata kunci untuk mencari buku';
  }

  async function fetchBooks(q) {
    loading.style.display = 'flex';
    bookGrid.innerHTML = '';
    emptyState.classList.add('hidden');

    try {
      const data = await apiSearchBooks(q);
      loading.style.display = 'none';

      resultsQuery.innerHTML = `Menampilkan hasil untuk "<strong>${escapeHtml(q)}</strong>" — ${data.total_results.toLocaleString('id-ID')} buku ditemukan`;

      if (!data.books || data.books.length === 0) {
        emptyState.classList.remove('hidden');
        return;
      }

      bookGrid.innerHTML = data.books.map((book, i) => renderBookCard(book, i)).join('');
    } catch (err) {
      loading.style.display = 'none';
      resultsQuery.innerHTML = `<span style="color:var(--danger)">Error: ${escapeHtml(err.message)}</span>`;
    }
  }

  function renderBookCard(book, index) {
    const coverHtml = book.thumbnail
      ? `<img src="${escapeHtml(book.thumbnail)}" alt="${escapeHtml(book.title)}" loading="lazy">`
      : `<span class="book-card-no-cover">No Cover</span>`;

    const authors = book.authors.length ? book.authors.join(', ') : 'Penulis tidak diketahui';
    const year = book.published_date ? book.published_date.substring(0, 4) : '';
    const desc = book.description
      ? (book.description.length > 150 ? book.description.substring(0, 150) + '...' : book.description)
      : '';

    return `
      <div class="book-card" style="animation-delay: ${index * 0.05}s" onclick="window.location.href='/book.html?id=${encodeURIComponent(book.volume_id)}'">
        <div class="book-card-cover">${coverHtml}</div>
        <div class="book-card-body">
          <div class="book-card-title">${escapeHtml(book.title)}</div>
          <div class="book-card-author">${escapeHtml(authors)}</div>
          ${year ? `<div class="book-card-year">${escapeHtml(year)}</div>` : ''}
          ${desc ? `<div class="book-card-desc">${escapeHtml(desc)}</div>` : ''}
        </div>
      </div>
    `;
  }
});
