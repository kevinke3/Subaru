const API_BASE = '';
const AUTH_KEY = 'classmate_token';

const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

function api(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  const token = localStorage.getItem(AUTH_KEY);
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return fetch(`${API_BASE}${path}`, { ...opts, headers }).then(r => {
    if (r.status === 401) { logout(); throw new Error('Unauthorized'); }
    if (r.status === 204) return null;
    return r.json().then(data => {
      if (!r.ok) throw new Error(data.error || data.message || `Request failed (${r.status})`);
      return data;
    }).catch(err => {
      if (err.message) throw err;
      return {};
    });
  });
}

function getToken() { return localStorage.getItem(AUTH_KEY); }
function getCurrentUser() {
  try { return JSON.parse(localStorage.getItem('classmate_user')); } catch { return null; }
}
function logout() {
  localStorage.removeItem(AUTH_KEY);
  localStorage.removeItem('classmate_user');
  window.location.href = '/login';
}

function initSidebar() {
  const sidebar = $('.sidebar');
  const toggleBtn = $('.sidebar-toggle');
  if (!sidebar || !toggleBtn) return;
  const saved = localStorage.getItem('sidebar_expanded') === 'true';
  if (saved || window.innerWidth > 1024) sidebar.classList.add('expanded');
  toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('expanded');
    localStorage.setItem('sidebar_expanded', sidebar.classList.contains('expanded'));
  });
  if (window.innerWidth <= 768) {
    $('.mobile-menu-btn')?.addEventListener('click', () => {
      sidebar.classList.add('mobile-open');
      $('.sidebar-backdrop')?.classList.add('active');
    });
    $('.sidebar-backdrop')?.addEventListener('click', () => {
      sidebar.classList.remove('mobile-open');
      $('.sidebar-backdrop')?.classList.remove('active');
    });
  }
}

function initDropdowns() {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.has-dropdown')) return;
    const menu = e.target.closest('.has-dropdown').querySelector('.dropdown-menu');
    if (menu) menu.classList.toggle('active');
  });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown-menu') && !e.target.closest('.has-dropdown')) {
      $$('.dropdown-menu').forEach(m => m.classList.remove('active'));
    }
  });
}

function animateCounters() {
  $$('.counter').forEach(el => {
    const target = parseInt(el.dataset.target || '0', 10);
    const current = parseInt(el.textContent.replace(/[^0-9]/g, '') || '0', 10);
    if (!target) return;
    const duration = 1200;
    const step = target / (duration / 16);
    let val = current;
    const timer = setInterval(() => {
      val += step;
      if (val >= target) { val = target; clearInterval(timer); }
      el.textContent = Number.isInteger(target) ? Math.floor(val).toLocaleString() : val.toFixed(1);
    }, 16);
  });
}

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed; bottom: 24px; right: 24px;
    background: ${type === 'error' ? '#ff2d55' : type === 'success' ? '#0fb06b' : '#0a0a0a'};
    color: #fff; padding: 14px 20px; border-radius: 12px;
    font-size: 0.875rem; font-weight: 500; z-index: 9999;
    box-shadow: 0 20px 48px rgba(0,0,0,0.22);
    animation: fadeSlideIn 0.3s ease;
  `;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; }, 2800);
  setTimeout(() => toast.remove(), 3200);
}

function openModal(id) { $('#' + id)?.classList.add('active'); }
function closeModal(id) { $('#' + id)?.classList.remove('active'); }

function renderSkeleton(containerId, count, type = 'card') {
  const container = $('#' + containerId);
  if (!container) return;
  container.innerHTML = '';
  for (let i = 0; i < count; i++) {
    const el = document.createElement('div');
    el.className = `skeleton-${type}`;
    container.appendChild(el);
  }
}

function navigateTo(route) {
  const map = {
    'dashboard': '/dashboard',
    'students': '/students',
    'teachers': '/teachers',
    'academics': '/academics',
    'attendance': '/attendance',
    'finance': '/finance',
    'exams': '/exams',
    'messages': '/messages',
    'settings': '/settings',
    'administration': '/administration',
    'login': '/login',
    'register': '/register',
  };
  window.location.href = map[route] || '/';
}

document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initDropdowns();
  animateCounters();
  const user = getCurrentUser();
  if (user) {
    const avatar = $('#topbar-avatar');
    const name = $('#topbar-name');
    if (avatar) avatar.textContent = ((user.first_name || 'U')[0] || 'U') + ' ' + ((user.last_name || '')[0] || 'D');
    if (name) name.textContent = (user.first_name || 'User') + ' ' + (user.last_name || '');
  }
});
