const API_BASE = 'http://localhost:8000/api';
const ADMIN_TOKEN_KEY = 'vida_admin_token';

function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element && value !== undefined && value !== null) {
    element.textContent = value;
  }
}

function createVideoCard(video) {
  const badgeClass = video.category === 'REACTION' ? 'badge-secondary' : 'badge-primary';
  return `
    <div class="glass-card video-card">
      <div class="video-wrapper">
        <iframe src="${video.embed_url}" title="${video.title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div>
      <div class="video-card-info">
        <div class="badges">
          <span class="badge ${badgeClass}">${video.category}</span>
          <span class="meta-time">• ${video.duration}</span>
        </div>
        <h4>${video.title}</h4>
        <p>${video.description || 'Latest episode'}</p>
        <div class="video-stats">
          <span>${video.views} views</span>
          <span>•</span>
          <span>${video.upload_date}</span>
        </div>
      </div>
    </div>
  `;
}

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    ...options,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `API Error ${response.status}`);
  }

  const contentType = response.headers.get('content-type') || '';
  return contentType.includes('application/json') ? response.json() : response.text();
}

async function loadArtistProfile() {
  try {
    const artist = await request('/artist/profile');
    setText('#artist-name', artist.name);
    setText('#artist-title', artist.title);
    setText('#artist-bio', artist.bio);
  } catch (error) {
    console.warn('Artist profile unavailable', error);
  }
}

function getAdminToken() {
  return localStorage.getItem(ADMIN_TOKEN_KEY) || null;
}

function setAdminToken(token) {
  if (token) localStorage.setItem(ADMIN_TOKEN_KEY, token);
  else localStorage.removeItem(ADMIN_TOKEN_KEY);
}

async function authRequest(endpoint, options = {}) {
  const token = getAdminToken();
  const headers = { 'Content-Type': 'application/json', Accept: 'application/json' };
  if (token) headers['X-Admin-Token'] = token;
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers,
    ...options,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `API Error ${response.status}`);
  }
  const contentType = response.headers.get('content-type') || '';
  return contentType.includes('application/json') ? response.json() : response.text();
}

async function loadFeaturedVideo() {
  try {
    const video = await request('/videos/featured');
    const featured = document.querySelector('.featured-video');
    if (featured) {
      featured.innerHTML = `
        <div class="video-wrapper">
          <iframe src="${video.embed_url}" title="${video.title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
        </div>
        <div class="video-info">
          <div class="badges">
            <span class="badge badge-secondary">${video.category}</span>
            <span class="badge badge-outline">${video.upload_date}</span>
          </div>
          <h3>${video.title}</h3>
          <p>${video.description || ''}</p>
          <div class="video-stats">
            <span><span class="material-symbols-outlined">visibility</span> ${video.views} views</span>
            <span><span class="material-symbols-outlined">thumb_up</span> ${video.likes} likes</span>
            <span><span class="material-symbols-outlined">schedule</span> ${video.duration}</span>
          </div>
        </div>
      `;
    }
  } catch (error) {
    console.warn('Featured video unavailable', error);
  }
}

async function loadVideos() {
  try {
    const data = await request('/videos?limit=3');
    const firstGrid = document.querySelector('.section:first-of-type .video-grid');
    if (firstGrid) {
      firstGrid.innerHTML = data.videos.map(createVideoCard).join('');
    }

    const secondGrid = document.querySelector('.section:nth-of-type(2) .video-grid');
    if (secondGrid) {
      secondGrid.innerHTML = data.videos.map(createVideoCard).join('');
    }
  } catch (error) {
    console.warn('Videos unavailable', error);
  }
}

async function loadGallery() {
  try {
    const images = await request('/gallery');
    const galleryGrid = document.querySelector('#gallery-grid');
    if (galleryGrid) {
      galleryGrid.innerHTML = images.map((img) => `<div class="item"><img src="${img.url}" alt="${img.alt_text}" loading="lazy"></div>`).join('');
    }
  } catch (error) {
    console.warn('Gallery unavailable', error);
  }
}

function initThemeToggle() {
  const toggle = document.getElementById('themeToggle');
  const icon = document.getElementById('themeIcon');
  if (!toggle || !icon) return;

  const savedTheme = localStorage.getItem('theme') || 'dark';
  document.documentElement.classList.toggle('dark', savedTheme === 'dark');
  icon.textContent = savedTheme === 'dark' ? 'dark_mode' : 'light_mode';

  toggle.addEventListener('click', () => {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    icon.textContent = isDark ? 'dark_mode' : 'light_mode';
  });
}

function initHeaderEffects() {
  const header = document.querySelector('.site-header');
  if (!header) return;

  window.addEventListener('scroll', () => {
    header.style.padding = window.scrollY > 50 ? '8px 64px' : '16px 64px';
  });
}

function initHeroMotion() {
  const heroImage = document.querySelector('.hero-image-wrapper');
  if (!heroImage) return;

  window.addEventListener('mousemove', (event) => {
    const speed = 0.02;
    const x = (window.innerWidth - event.pageX * 4) * speed;
    const y = (window.innerHeight - event.pageY * 4) * speed;
    heroImage.style.transform = `translate(${x}px, ${y}px)`;
  });
}

async function initializePipeline() {
  await Promise.allSettled([
    loadArtistProfile(),
    loadFeaturedVideo(),
    loadVideos(),
    loadGallery(),
  ]);
  initAdminPanel();
}

function initAdminPanel() {
  const loginBtn = document.getElementById('admin-login-btn');
  const logoutBtn = document.getElementById('admin-logout-btn');
  const tokenInput = document.getElementById('admin-token-input');
  const adminPanel = document.getElementById('admin-panel');
  const adminStats = document.getElementById('admin-stats');
  const adminWelcome = document.getElementById('admin-welcome');
  const adminCreate = document.getElementById('admin-create-forms');

  const currentToken = getAdminToken();
  if (currentToken) {
    adminPanel.style.display = '';
    adminStats.style.display = '';
    adminCreate.style.display = '';
    document.getElementById('admin-login').style.display = 'none';
    logoutBtn.style.display = '';
    adminWelcome.textContent = 'Logged in (token stored)';
    fetchAdminStats();
  }

  loginBtn?.addEventListener('click', async () => {
    const token = tokenInput.value.trim();
    if (!token) return alert('Enter admin token');
    setAdminToken(token);
    try {
      await fetchAdminStats();
      adminPanel.style.display = '';
      adminStats.style.display = '';
      adminCreate.style.display = '';
      document.getElementById('admin-login').style.display = 'none';
      logoutBtn.style.display = '';
      adminWelcome.textContent = 'Logged in as admin';
      tokenInput.value = '';
    } catch (err) {
      setAdminToken(null);
      alert('Login failed: ' + err.message);
    }
  });

  logoutBtn?.addEventListener('click', () => {
    setAdminToken(null);
    adminPanel.style.display = 'none';
    document.getElementById('admin-login').style.display = '';
    logoutBtn.style.display = 'none';
    adminWelcome.textContent = 'Not logged in';
  });

  const createVideoBtn = document.getElementById('create-video-btn');
  createVideoBtn?.addEventListener('click', async () => {
    const payload = {
      title: document.getElementById('new-video-title').value,
      youtube_id: document.getElementById('new-video-youtube_id').value,
      embed_url: document.getElementById('new-video-embed').value,
      category: document.getElementById('new-video-category').value,
      duration: document.getElementById('new-video-duration').value,
      upload_date: document.getElementById('new-video-upload').value,
      description: document.getElementById('new-video-desc').value,
    };
    try {
      const res = await authRequest('/admin/videos', { method: 'POST', body: JSON.stringify(payload) });
      alert('Video created: ' + res.title);
      fetchAdminStats();
    } catch (err) {
      alert('Create failed: ' + err.message);
    }
  });
}

async function fetchAdminStats() {
  try {
    const v = await request('/videos?limit=1');
    const t = await request('/music/tracks?limit=1');
    const g = await request('/gallery');
    const a = await request('/artist/profile');
    document.getElementById('stat-videos').textContent = v.total || (v.videos ? v.videos.length : 0);
    document.getElementById('stat-tracks').textContent = t.total || (t.tracks ? t.tracks.length : 0);
    document.getElementById('stat-gallery').textContent = Array.isArray(g) ? g.length : 0;
    document.getElementById('stat-followers').textContent = a.followers || 0;
  } catch (err) {
    console.warn('Failed to fetch admin stats', err);
    throw err;
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initHeaderEffects();
    initHeroMotion();
    initializePipeline();
  });
} else {
  initThemeToggle();
  initHeaderEffects();
  initHeroMotion();
  initializePipeline();
}

window.VidaBrown = { request };
