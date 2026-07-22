// --- API Configuration ---
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000/api'
    : 'https://vida-brown-portfolio-api.onrender.com/api'; // <-- Make sure this matches your exact Render backend URL

// --- Helper Functions ---
function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element && value !== undefined && value !== null) {
    element.textContent = value;
  }
}

// --- API Request Function ---
async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    // FastAPI returns errors in a "detail" field
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `API Error ${response.status}`);
  }

  const contentType = response.headers.get('content-type') || '';
  return contentType.includes('application/json') ? response.json() : response.text();
}

// --- Content Loading Functions ---
async function loadArtistProfile() {
  try {
    const artist = await request('/artist/profile');
    setText('#artist-name', artist.name);
    setText('#artist-title', artist.title);
    setText('#artist-bio', artist.bio);
    setText('#music-artist-name', artist.name);
    setText('#music-artist-title', artist.title);
    setText('#follower-count', artist.followers);
  } catch (error) {
    console.warn('Artist profile unavailable', error);
  }
}

function createVideoCard(video) {
  const badgeClass = video.category === 'REACTION' ? 'badge-secondary' : (video.category === 'MALAWI MUSIC' ? 'badge-tertiary' : 'badge-primary');
  return `
    <div class="glass-card video-card">
      <div class="video-wrapper">
        <iframe src="${video.embed_url}" title="${video.title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
      </div>
      <div class="video-card-info">
        <div class="badges">
          <span class="badge ${badgeClass}">${video.category}</span>
          <span class="meta-time">• ${video.duration}</span>
        </div>
        <h4>${video.title}</h4>
        <p>${video.description || 'Latest episode'}</p>
        <div class="video-stats">
          <span>${video.views_display} views</span>
          <span>•</span>
          <span>${video.upload_date}</span>
        </div>
      </div>
    </div>
  `;
}

async function loadFeaturedVideo() {
  try {
    const video = await request('/videos/featured');
    
    const iframe = document.getElementById('featured-video-iframe');
    if (iframe) iframe.src = video.embed_url;
    
    setText('#featured-video-title', video.title);
    setText('#featured-video-description', video.description);
    setText('#featured-views', video.views_display);
    setText('#featured-likes', video.likes_display);
    setText('#featured-duration', video.duration);
    
    const badges = document.getElementById('featured-video-badges');
    if (badges) {
      const badgeClass = video.category === 'REACTION' ? 'badge-secondary' : 'badge-primary';
      badges.innerHTML = `
        <span class="badge ${badgeClass}">${video.category}</span>
        <span class="badge badge-outline">${video.upload_date}</span>
      `;
    }
  } catch (error) {
    console.warn('Featured video unavailable', error);
  }
}

async function loadVideos() {
  try {
    const data = await request('/videos?limit=6');
    const videos = data.videos || [];
    
    const trendingGrid = document.getElementById('trending-grid');
    if (trendingGrid && videos.length > 0) {
      trendingGrid.innerHTML = videos.slice(0, 3).map(createVideoCard).join('');
    }

    const showsGrid = document.getElementById('shows-grid');
    if (showsGrid && videos.length > 0) {
      const showsHtml = videos.slice(0, 5).map(createVideoCard).join('') + 
      `<a href="https://www.youtube.com/@VidaBrownOfficial" target="_blank" class="glass-card video-card subscribe-card">
          <div class="subscribe-icon"><span class="material-symbols-outlined">subscriptions</span></div>
          <h4>Subscribe to Channel</h4>
          <p>Get the latest music reviews and reactions</p>
          <span class="view-all" style="justify-content:center;">VIEW CHANNEL <span class="material-symbols-outlined">arrow_forward</span></span>
        </a>`;
      showsGrid.innerHTML = showsHtml;
    }
  } catch (error) {
    console.warn('Videos unavailable', error);
  }
}

async function loadTracks() {
  try {
    const data = await request('/music/tracks?limit=10');
    const trackList = document.getElementById('track-list');
    
    if (trackList && data.tracks) {
      trackList.innerHTML = data.tracks.map((track) => {
        const trackNum = String(track.track_number).padStart(2, '0');
        const artistDisplay = track.featured_artist ? `${track.artist_name} feat. ${track.featured_artist}` : track.artist_name;
        const yearDisplay = track.year ? ` • ${track.year}` : '';
        
        return `
          <div class="track-item" data-track-id="${track.id}">
            <div class="track-info">
              <span class="track-num">${trackNum}</span>
              <div>
                <div class="track-title">${track.title}</div>
                <div class="track-artist">${artistDisplay}${yearDisplay}</div>
              </div>
            </div>
            <div class="track-meta">
              <span>${track.streams_display} streams</span>
              <span>${track.track_type}</span>
              <button class="track-more" data-track-id="${track.id}"><span class="material-symbols-outlined">more_horiz</span></button>
            </div>
          </div>
        `;
      }).join('');
    }
  } catch (error) {
    console.warn('Tracks unavailable', error);
  }
}

async function loadGallery() {
  try {
    const images = await request('/gallery');
    const galleryGrid = document.getElementById('gallery-grid');
    if (galleryGrid && images) {
      galleryGrid.innerHTML = images.map((img) => 
        `<div class="item"><img src="${img.url}" alt="${img.alt_text}" loading="lazy"></div>`
      ).join('');
    }
  } catch (error) {
    console.warn('Gallery unavailable', error);
  }
}

function initNewsletter() {
  const form = document.getElementById('newsletter-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const emailInput = document.getElementById('newsletter-email');
    const submitBtn = document.getElementById('subscribe-btn');
    const email = emailInput.value;

    if (!email) return;

    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Subscribing...';
    submitBtn.disabled = true;

    try {
      await request('/newsletter/subscribe', {
        method: 'POST',
        body: JSON.stringify({ email })
      });
      alert('Successfully subscribed to the newsletter! 🎉');
      emailInput.value = '';
    } catch (error) {
      alert(error.message || 'Failed to subscribe. Please try again.');
    } finally {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    }
  });
}

// --- UI Effects ---
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

// --- Initialization ---
async function initializePipeline() {
  await Promise.allSettled([
    loadArtistProfile(),
    loadFeaturedVideo(),
    loadVideos(),
    loadTracks(),
    loadGallery(),
  ]);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initHeaderEffects();
    initHeroMotion();
    initNewsletter();
    initializePipeline();
  });
} else {
  initThemeToggle();
  initHeaderEffects();
  initHeroMotion();
  initNewsletter();
  initializePipeline();
}

// Expose for potential external use
window.VidaBrown = { request };