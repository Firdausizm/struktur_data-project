/**
 * api.js — Modul komunikasi dengan backend API.
 * Mengelola token JWT, request HTTP, dan helper autentikasi.
 */

const API_BASE = window.location.origin;

// ── Token Management ──

function getToken() {
  return localStorage.getItem('access_token');
}

function setToken(token) {
  localStorage.setItem('access_token', token);
}

function removeToken() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_data');
}

function isLoggedIn() {
  return !!getToken();
}

function getCachedUser() {
  const data = localStorage.getItem('user_data');
  return data ? JSON.parse(data) : null;
}

function setCachedUser(user) {
  localStorage.setItem('user_data', JSON.stringify(user));
}

// ── HTTP Helper ──

async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Handle 204 No Content (e.g. delete comment)
  if (response.status === 204) {
    return null;
  }

  const data = await response.json();

  if (!response.ok) {
    const message = data.detail || 'Terjadi kesalahan pada server';
    throw new Error(message);
  }

  return data;
}

// ── Auth API ──

async function apiRegister(username, email, password) {
  return fetchAPI('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  });
}

async function apiLogin(email, password) {
  const data = await fetchAPI('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  // Fetch and cache user data
  const user = await apiGetMe();
  setCachedUser(user);
  return data;
}

async function apiGetMe() {
  return fetchAPI('/api/auth/me');
}

function apiLogout() {
  removeToken();
  window.location.href = '/';
}

// ── Books API ──

async function apiSearchBooks(query) {
  return fetchAPI(`/api/books/search?q=${encodeURIComponent(query)}`);
}

async function apiGetSuggestions(query, limit = 10) {
  return fetchAPI(`/api/books/suggestions?q=${encodeURIComponent(query)}&limit=${limit}`);
}

async function apiGetBookDetail(volumeId) {
  return fetchAPI(`/api/books/${encodeURIComponent(volumeId)}`);
}

// ── Rating API ──

async function apiUpsertRating(volumeId, score) {
  return fetchAPI(`/api/books/${encodeURIComponent(volumeId)}/rating`, {
    method: 'POST',
    body: JSON.stringify({ score }),
  });
}

async function apiGetRatingSummary(volumeId) {
  return fetchAPI(`/api/books/${encodeURIComponent(volumeId)}/rating-summary`);
}

async function apiGetMyRating(volumeId) {
  return fetchAPI(`/api/books/${encodeURIComponent(volumeId)}/my-rating`);
}

// ── Comments API ──

async function apiCreateComment(volumeId, content) {
  return fetchAPI(`/api/books/${encodeURIComponent(volumeId)}/comments`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

async function apiGetComments(volumeId) {
  return fetchAPI(`/api/books/${encodeURIComponent(volumeId)}/comments`);
}

async function apiDeleteComment(volumeId, commentId) {
  return fetchAPI(`/api/books/${encodeURIComponent(volumeId)}/comments/${commentId}`, {
    method: 'DELETE',
  });
}

// ── UI Helpers ──

function showToast(message) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2500);
}

function renderNavbar() {
  const nav = document.getElementById('navbar-nav');
  if (!nav) return;

  if (isLoggedIn()) {
    const user = getCachedUser();
    const username = user ? user.username : 'User';
    nav.innerHTML = `
      <span class="navbar-user">${escapeHtml(username)}</span>
      <button onclick="apiLogout()" class="navbar-nav-link">KELUAR</button>
    `;
  } else {
    nav.innerHTML = `
      <a href="/auth.html">MASUK</a>
    `;
  }
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
