// ============================================
// Vida Brown - Frontend Application Script
// ============================================

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000/api' 
    : '/api'; // Fallback for production deployment

// --- API Client ---
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            ...options
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `API Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`API Request failed for ${endpoint}:`, error);
        throw error;
    }
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

    window.addEventListener('mousemove', (e) => {
        const speed = 0.02;
        const x = (window.innerWidth - e.pageX * 4) * speed;
        const y = (window.innerHeight - e.pageY * 4) * speed;
        heroImage.style.transform = `translate(${x}px, ${y}px)`;
    });
}

// --- Helper: Safe Text Setter ---
function setText(selector, value) {
    const el = document.querySelector(selector);
    if (el && value !== undefined && value !== null) el.textContent = value;
}

// --- Helper: Get Badge Class ---
function getBadgeClass(category) {
    if (category === 'REACTION') return 'badge-secondary';
    if (category === 'MALAWI MUSIC') return 'badge-tertiary';
    return 'badge-primary'; // Default / HIT OR MISS
}

// --- Renderers ---
function renderArtistProfile(artist) {
    setText('#artist-name', artist.name);
    setText('#artist-title', artist.title);
    setText('#artist-bio', artist.bio);
    setText('#music-artist-name', artist.name);
    setText('#music-artist-title', artist.title);
    setText('#follower-count', artist.followers);
}

function createVideoCard(video) {
    const badgeClass = getBadgeClass(video.category);
    return `
        <div class="glass-card video-card">
            <div class="video-wrapper">
                <iframe src="${video.embed_url}" title="${video.title}" frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen loading="lazy"></iframe>
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

function renderFeaturedVideo(video) {
    const iframe = document.getElementById('featured-video-iframe');
    if (iframe) iframe.src = video.embed_url;

    setText('#featured-video-title', video.title);
    setText('#featured-video-description', video.description);
    setText('#featured-views', video.views_display);
    setText('#featured-likes', video.likes_display);
    setText('#featured-duration', video.duration);

    const badges = document.getElementById('featured-video-badges');
    if (badges) {
        const badgeClass = getBadgeClass(video.category);
        badges.innerHTML = `
            <span class="badge ${badgeClass}">${video.category}</span>
            <span class="badge badge-outline">${video.upload_date}</span>
        `;
    }
}

function renderVideoGrid(videos, containerId) {
    const container = document.getElementById(containerId);
    if (!container || !videos?.length) return;

    let html = videos.map(createVideoCard).join('');
    
    // Append the subscribe card specifically to the Shows grid
    if (containerId === 'shows-grid') {
        html += `
            <a href="https://www.youtube.com/@VidaBrownOfficial" target="_blank" class="glass-card video-card subscribe-card">
                <div class="subscribe-icon"><span class="material-symbols-outlined">subscriptions</span></div>
                <h4>Subscribe to Channel</h4>
                <p>Get the latest music reviews and reactions</p>
                <span class="view-all" style="justify-content:center;">VIEW CHANNEL <span class="material-symbols-outlined">arrow_forward</span></span>
            </a>
        `;
    }

    container.innerHTML = html;
}

function renderTrackList(tracks) {
    const container = document.getElementById('track-list');
    if (!container || !tracks?.length) return;

    const html = tracks.map((track) => {
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

    container.innerHTML = html;
}

function renderGallery(images) {
    const container = document.getElementById('gallery-grid');
    if (!container || !images?.length) return;

    container.innerHTML = images.map(img => `
        <div class="item">
            <img src="${img.url}" alt="${img.alt_text}" loading="lazy">
        </div>
    `).join('');
}

// --- Newsletter ---
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
            await apiRequest('/newsletter/subscribe', {
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

// --- Data Pipeline ---
async function initializePipeline() {
    try {
        // Run all data fetches in parallel for maximum performance
        const [artist, featured, videosData, tracksData, gallery] = await Promise.allSettled([
            apiRequest('/artist/profile'),
            apiRequest('/videos/featured'),
            apiRequest('/videos?limit=6'),
            apiRequest('/music/tracks?limit=10'),
            apiRequest('/gallery?limit=20')
        ]);

        if (artist.status === 'fulfilled') renderArtistProfile(artist.value);
        if (featured.status === 'fulfilled') renderFeaturedVideo(featured.value);
        
        if (videosData.status === 'fulfilled') {
            const videos = videosData.value.videos || [];
            renderVideoGrid(videos.slice(0, 3), 'trending-grid');
            renderVideoGrid(videos.slice(0, 5), 'shows-grid');
        }

        if (tracksData.status === 'fulfilled') renderTrackList(tracksData.value.tracks || []);
        if (gallery.status === 'fulfilled') renderGallery(gallery.value || []);

    } catch (error) {
        console.error('Pipeline initialization failed:', error);
    }
}

// --- Bootstrap ---
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎵 Vida Brown Website Loaded');
    
    initThemeToggle();
    initHeaderEffects();
    initHeroMotion();
    initNewsletter();
    
    initializePipeline();
});

// Expose for debugging
window.VidaBrown = { apiRequest };