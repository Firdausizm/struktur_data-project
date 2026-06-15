/**
 * home.js — Logic untuk home page: search form & autocomplete via Trie.
 */

document.addEventListener('DOMContentLoaded', () => {
  renderNavbar();

  const searchForm = document.getElementById('search-form');
  const searchInput = document.getElementById('search-input');
  const dropdown = document.getElementById('autocomplete-dropdown');

  let debounceTimer = null;
  let activeIndex = -1;
  let suggestions = [];

  // ── Search Form Submit ──
  searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = searchInput.value.trim();
    if (query) {
      window.location.href = `/results.html?q=${encodeURIComponent(query)}`;
    }
  });

  // ── Autocomplete: debounced input ──
  searchInput.addEventListener('input', () => {
    const query = searchInput.value.trim();
    clearTimeout(debounceTimer);
    activeIndex = -1;

    if (query.length < 1) {
      hideDropdown();
      return;
    }

    debounceTimer = setTimeout(async () => {
      try {
        const data = await apiGetSuggestions(query, 8);
        suggestions = data.suggestions || [];
        renderSuggestions(suggestions, query);
      } catch {
        hideDropdown();
      }
    }, 300);
  });

  // ── Keyboard navigation ──
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

  // ── Click outside to close ──
  document.addEventListener('click', (e) => {
    if (!e.target.closest('#search-container')) {
      hideDropdown();
    }
  });

  function renderSuggestions(items, query) {
    if (!items.length) {
      hideDropdown();
      return;
    }

    dropdown.innerHTML = items.map((item, i) => {
      // Highlight the matching prefix
      const highlighted = highlightMatch(item, query);
      return `<div class="autocomplete-item" data-index="${i}">${highlighted}</div>`;
    }).join('');

    dropdown.classList.add('active');

    // Click handlers for each suggestion
    dropdown.querySelectorAll('.autocomplete-item').forEach(el => {
      el.addEventListener('click', () => {
        const idx = parseInt(el.dataset.index);
        searchInput.value = items[idx];
        hideDropdown();
        window.location.href = `/results.html?q=${encodeURIComponent(items[idx])}`;
      });
    });
  }

  function highlightMatch(text, query) {
    const lowerText = text.toLowerCase();
    const lowerQuery = query.toLowerCase();
    const idx = lowerText.indexOf(lowerQuery);
    if (idx === -1) return escapeHtml(text);

    const before = text.slice(0, idx);
    const match = text.slice(idx, idx + query.length);
    const after = text.slice(idx + query.length);
    return `${escapeHtml(before)}<strong style="color:var(--on-primary)">${escapeHtml(match)}</strong>${escapeHtml(after)}`;
  }

  function updateActiveItem(items) {
    items.forEach((el, i) => {
      el.classList.toggle('active', i === activeIndex);
    });
    if (activeIndex >= 0) {
      searchInput.value = suggestions[activeIndex];
    }
  }

  function hideDropdown() {
    dropdown.classList.remove('active');
    dropdown.innerHTML = '';
    activeIndex = -1;
  }
});
