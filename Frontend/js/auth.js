/**
 * auth.js — Logic untuk halaman login & register.
 */

document.addEventListener('DOMContentLoaded', () => {
  // If already logged in, redirect to home
  if (isLoggedIn()) {
    window.location.href = '/';
    return;
  }

  renderNavbar();

  const tabs = document.querySelectorAll('.auth-tab');
  const formLogin = document.getElementById('form-login');
  const formRegister = document.getElementById('form-register');
  const authTitle = document.getElementById('auth-title');
  const authSub = document.getElementById('auth-sub');
  const authFooter = document.getElementById('auth-footer');
  const authMessage = document.getElementById('auth-message');
  const switchToRegister = document.getElementById('switch-to-register');

  function switchTab(tab) {
    tabs.forEach(t => t.classList.remove('active'));
    clearMessage();

    if (tab === 'login') {
      tabs[0].classList.add('active');
      formLogin.classList.add('active');
      formRegister.classList.remove('active');
      authTitle.textContent = 'MASUK';
      authSub.textContent = 'Masuk ke akun Anda untuk melanjutkan';
      authFooter.innerHTML = 'Belum punya akun? <a href="#" id="switch-to-register">Daftar di sini</a>';
      document.getElementById('switch-to-register').addEventListener('click', (e) => {
        e.preventDefault();
        switchTab('register');
      });
    } else {
      tabs[1].classList.add('active');
      formRegister.classList.add('active');
      formLogin.classList.remove('active');
      authTitle.textContent = 'DAFTAR';
      authSub.textContent = 'Buat akun baru untuk mulai mengulas buku';
      authFooter.innerHTML = 'Sudah punya akun? <a href="#" id="switch-to-login">Masuk di sini</a>';
      document.getElementById('switch-to-login').addEventListener('click', (e) => {
        e.preventDefault();
        switchTab('login');
      });
    }
  }

  function showMessage(text, type) {
    authMessage.textContent = text;
    authMessage.className = `auth-message ${type}`;
  }

  function clearMessage() {
    authMessage.textContent = '';
    authMessage.className = 'auth-message';
  }

  // Tab click handlers
  tabs.forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  });

  // Footer link
  switchToRegister.addEventListener('click', (e) => {
    e.preventDefault();
    switchTab('register');
  });

  // Login submit
  formLogin.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessage();

    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    const btn = document.getElementById('btn-login');

    btn.disabled = true;
    btn.textContent = 'MEMPROSES...';

    try {
      await apiLogin(email, password);
      showMessage('Login berhasil! Mengalihkan...', 'success');
      setTimeout(() => {
        window.location.href = '/';
      }, 500);
    } catch (err) {
      showMessage(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'MASUK';
    }
  });

  // Register submit
  formRegister.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessage();

    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const btn = document.getElementById('btn-register');

    btn.disabled = true;
    btn.textContent = 'MEMPROSES...';

    try {
      await apiRegister(username, email, password);
      showMessage('Registrasi berhasil! Silakan masuk.', 'success');
      // Auto switch to login tab after success
      setTimeout(() => {
        switchTab('login');
        document.getElementById('login-email').value = email;
        document.getElementById('login-password').focus();
      }, 1000);
    } catch (err) {
      showMessage(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'DAFTAR';
    }
  });
});
