/**
 * book.js — Logic untuk halaman detail buku, rating, dan komentar.
 */

document.addEventListener('DOMContentLoaded', async () => {
  renderNavbar();

  const params = new URLSearchParams(window.location.search);
  const volumeId = params.get('id');

  const loading = document.getElementById('loading');
  const bookDetail = document.getElementById('book-detail');
  const errorState = document.getElementById('error-state');

  if (!volumeId) {
    loading.style.display = 'none';
    errorState.classList.remove('hidden');
    return;
  }

  try {
    const book = await apiGetBookDetail(volumeId);
    renderBookInfo(book);
    
    // After book info is loaded, show the container
    loading.style.display = 'none';
    bookDetail.classList.remove('hidden');

    // Load secondary data asynchronously
    loadRatingSummary();
    renderRatingInput();
    renderCommentForm();
    loadComments();

  } catch (err) {
    loading.style.display = 'none';
    errorState.classList.remove('hidden');
  }

  // ── Render Book Info ──
  function renderBookInfo(book) {
    document.title = `${book.title} — BOOKSEARCH`;

    const coverContainer = document.getElementById('book-cover');
    if (book.thumbnail) {
      // Ubah http ke https agar tidak terkena blokir mixed-content oleh browser, dan gunakan thumbnail bawaan
      const secureThumb = book.thumbnail.replace('http:', 'https:');
      coverContainer.innerHTML = `<img src="${escapeHtml(secureThumb)}" alt="${escapeHtml(book.title)}">`;
    } else {
      coverContainer.innerHTML = '<span class="book-card-no-cover">NO COVER AVAILABLE</span>';
    }

    document.getElementById('book-title').textContent = book.title;

    const meta = document.getElementById('book-meta');
    let metaHtml = '';
    if (book.authors.length) metaHtml += `<span>Penulis: <strong>${escapeHtml(book.authors.join(', '))}</strong></span>`;
    if (book.publisher) metaHtml += `<span>Penerbit: <strong>${escapeHtml(book.publisher)}</strong></span>`;
    if (book.published_date) metaHtml += `<span>Tahun: <strong>${escapeHtml(book.published_date.substring(0, 4))}</strong></span>`;
    if (book.page_count) metaHtml += `<span>Halaman: <strong>${book.page_count}</strong></span>`;
    if (book.language) metaHtml += `<span>Bahasa: <strong style="text-transform:uppercase">${escapeHtml(book.language)}</strong></span>`;
    meta.innerHTML = metaHtml;

    document.getElementById('book-desc').innerHTML = book.description || 'Tidak ada deskripsi.';

    const tags = document.getElementById('book-tags');
    if (book.categories && book.categories.length) {
      tags.innerHTML = book.categories.map(c => `<span class="book-tag">${escapeHtml(c)}</span>`).join('');
    }

    const preview = document.getElementById('book-preview');
    if (book.preview_link) {
      preview.innerHTML = `<a href="${escapeHtml(book.preview_link)}" target="_blank" class="book-preview-link">BACA PREVIEW DI GOOGLE BOOKS →</a>`;
    }
  }

  // ── Ratings ──
  async function loadRatingSummary() {
    try {
      const summary = await apiGetRatingSummary(volumeId);
      document.getElementById('rating-avg').textContent = summary.average_rating.toFixed(1);
      document.getElementById('rating-total').textContent = `${summary.total_ratings.toLocaleString('id-ID')} penilaian`;
    } catch (e) {
      console.error('Failed to load rating summary', e);
    }
  }

  async function renderRatingInput() {
    const area = document.getElementById('rating-input-area');
    if (!isLoggedIn()) {
      area.innerHTML = `
        <div class="login-prompt">
          <p>Anda harus masuk untuk memberikan rating.</p>
          <a href="/auth.html" class="btn btn-ghost-dark">MASUK / DAFTAR</a>
        </div>
      `;
      return;
    }

    let myRating = 0;
    try {
      const res = await apiGetMyRating(volumeId);
      if (res && res.score !== undefined) {
        myRating = res.score;
      }
    } catch (e) {}

    let dotsHtml = '';
    for (let i = 0; i <= 10; i++) {
      dotsHtml += `<div class="rating-dot ${i === myRating ? 'selected' : ''}" data-score="${i}">${i}</div>`;
    }

    area.innerHTML = `
      <div class="rating-input-section">
        <div class="rating-input-label">Beri Rating (0-10):</div>
        <div class="rating-slider-container">
          <div class="rating-dots" id="rating-dots">
            ${dotsHtml}
          </div>
          <div class="rating-current-value" id="rating-current-value">${myRating}</div>
        </div>
      </div>
    `;

    // Add events
    const dots = document.querySelectorAll('.rating-dot');
    const currentValue = document.getElementById('rating-current-value');
    
    dots.forEach(dot => {
      dot.addEventListener('click', async () => {
        const score = parseInt(dot.dataset.score);
        try {
          await apiUpsertRating(volumeId, score);
          // Update UI
          dots.forEach(d => d.classList.remove('selected'));
          dot.classList.add('selected');
          currentValue.textContent = score;
          showToast('Rating berhasil disimpan');
          // Refresh summary
          loadRatingSummary();
        } catch (e) {
          showToast('Gagal menyimpan rating: ' + e.message);
        }
      });
    });
  }

  // ── Comments ──
  function renderCommentForm() {
    const area = document.getElementById('comment-form-area');
    if (!isLoggedIn()) {
      area.innerHTML = `
        <div class="login-prompt">
          <p>Anda harus masuk untuk menulis komentar.</p>
          <a href="/auth.html" class="btn btn-ghost-dark">MASUK / DAFTAR</a>
        </div>
      `;
      return;
    }

    area.innerHTML = `
      <form class="comment-form" id="comment-form">
        <textarea class="comment-input" id="comment-input" placeholder="Tulis komentar Anda di sini..." required maxlength="2000"></textarea>
        <button type="submit" class="btn btn-filled" id="btn-submit-comment">KIRIM</button>
      </form>
    `;

    document.getElementById('comment-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = document.getElementById('comment-input');
      const content = input.value.trim();
      if (!content) return;

      const btn = document.getElementById('btn-submit-comment');
      btn.disabled = true;
      btn.textContent = '...';

      try {
        await apiCreateComment(volumeId, content);
        input.value = '';
        showToast('Komentar berhasil ditambahkan');
        loadComments();
      } catch (err) {
        showToast(err.message);
      } finally {
        btn.disabled = false;
        btn.textContent = 'KIRIM';
      }
    });
  }

  async function loadComments() {
    const list = document.getElementById('comment-list');
    try {
      const comments = await apiGetComments(volumeId);
      
      if (!comments.length) {
        list.innerHTML = `<div class="comment-empty">Belum ada komentar. Jadilah yang pertama!</div>`;
        return;
      }

      const currentUser = getCachedUser();
      const myUserId = currentUser ? currentUser.id : null;

      list.innerHTML = comments.map(c => `
        <div class="comment-item">
          <div class="comment-header">
            <div>
              <span class="comment-username">${escapeHtml(c.username)}</span>
              <span class="comment-date"> • ${formatDate(c.created_at)}</span>
            </div>
            ${myUserId === c.user_id ? `<button class="btn btn-danger btn-sm" onclick="deleteComment(${c.id})">HAPUS</button>` : ''}
          </div>
          <div class="comment-content">${escapeHtml(c.content)}</div>
        </div>
      `).join('');
    } catch (err) {
      list.innerHTML = `<div class="comment-empty" style="color:var(--danger)">Gagal memuat komentar.</div>`;
    }
  }

  window.deleteComment = async function(commentId) {
    if (!confirm('Apakah Anda yakin ingin menghapus komentar ini?')) return;
    
    try {
      await apiDeleteComment(volumeId, commentId);
      showToast('Komentar berhasil dihapus');
      loadComments();
    } catch (e) {
      showToast('Gagal menghapus komentar: ' + e.message);
    }
  };

});
