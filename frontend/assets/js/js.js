// Theme Toggle Logic
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
const htmlEl = document.documentElement;

// Load saved theme preference or default to dark
const savedTheme = localStorage.getItem('theme') || 'dark';
if (savedTheme === 'light') {
    htmlEl.classList.remove('dark');
    themeIcon.textContent = 'light_mode';
}

themeToggle.addEventListener('click', () => {
    htmlEl.classList.toggle('dark');
    const isDark = htmlEl.classList.contains('dark');
    themeIcon.textContent = isDark ? 'dark_mode' : 'light_mode';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

// Header Scroll Effect
const header = document.querySelector('.site-header');
window.addEventListener('scroll', () => {
    header.style.padding = window.scrollY > 50 ? '8px 64px' : '16px 64px';
});

// Parallax effect for hero portrait
const heroImage = document.querySelector('.hero-image-wrapper');
window.addEventListener('mousemove', (e) => {
    if (!heroImage) return;
    const speed = 0.02;
    const x = (window.innerWidth - e.pageX * 4) * speed;
    const y = (window.innerHeight - e.pageY * 4) * speed;
    heroImage.style.transform = `translate(${x}px, ${y}px)`;
});

// ============================================
// Vida Brown - Frontend API Pipeline
// ============================================

// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000/api',
    TIMEOUT: 10000,
    HEADERS: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
};

// ============================================
// API Client Class
// ============================================
class APIClient {
    constructor(config) {
        this.baseUrl = config.BASE_URL;
        this.timeout = config.TIMEOUT;
        this.headers = config.HEADERS;
    }

    async request(endpoint, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                headers: { ...this.headers, ...options.headers },
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            console.error(`API Request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    // Artist endpoints
    async getArtistProfile() {
        return this.request('/artist/profile');
    }

    // Video endpoints
    async getVideos(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/videos${query ? '?' + query : ''}`);
    }

    async getFeaturedVideo() {
        return this.request('/videos/featured');
    }

    // Music endpoints
    async getTracks(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/music/tracks${query ? '?' + query : ''}`);
    }

    // Gallery endpoints
    async getGallery(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/gallery${query ? '?' + query : ''}`);
    }

    // Products endpoints
    async getProducts(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/products${query ? '?' + query : ''}`);
    }

    // Newsletter
    async subscribeNewsletter(email) {
        return this.request('/newsletter/subscribe', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    }
}

// ============================================
// Renderer Class - DOM Manipulation
// ============================================
class Renderer {
    constructor() {
        this.cache = new Map();
    }

    // Artist Profile Renderer
    renderArtistProfile(artist) {
        const heroContent = document.querySelector('.hero-content');
        if (!heroContent) return;

        const h1 = heroContent.querySelector('h1');
        const h2 = heroContent.querySelector('h2');
        const p = heroContent.querySelector('p');

        if (h1) h1.textContent = artist.name;
        if (h2) h2.textContent = artist.title;
        if (p) p.textContent = artist.bio;
    }

    // Video Card Renderer
    createVideoCard(video) {
        const badgeClass = this.getBadgeClass(video.category);
        return `
            <div class="glass-card video-card">
                <div class="video-wrapper">
                    <iframe src="${video.embed_url}" title="${video.title}" 
                        frameborder="0" 
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                        allowfullscreen></iframe>
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

    // Featured Video Renderer
    renderFeaturedVideo(video, containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container || !video) return;

        container.innerHTML = `
            <div class="video-wrapper">
                <iframe src="${video.embed_url}" title="${video.title}" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                    allowfullscreen></iframe>
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

    // Video Grid Renderer
    renderVideoGrid(videos, containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        const html = videos.map(video => this.createVideoCard(video)).join('');
        container.innerHTML = html;
    }

    // Track List Renderer
    renderTrackList(tracks) {
        const trackList = document.querySelector('.track-list');
        if (!trackList) return;

        const html = tracks.map((track, index) => `
            <div class="track-item" data-track-id="${track.id}">
                <div class="track-info">
                    <span class="track-num">${String(track.track_number).padStart(2, '0')}</span>
                    <div>
                        <div class="track-title">${track.title}</div>
                        <div class="track-artist">${track.artist_name}${track.featured_artist ? ' feat. ' + track.featured_artist : ''}${track.year ? ' • ' + track.year : ''}</div>
                    </div>
                </div>
                <div class="track-meta">
                    <span>${track.streams} streams</span>
                    <button class="track-more" onclick="trackActions.showMenu(${track.id})">
                        <span class="material-symbols-outlined">more_horiz</span>
                    </button>
                </div>
            </div>
        `).join('');

        trackList.innerHTML = html;
    }

    // Gallery Renderer
    renderGallery(images) {
        const galleryGrid = document.querySelector('.gallery-grid');
        if (!galleryGrid) return;

        const html = images.map(img => `
            <div class="item">
                <img src="${img.url}" alt="${img.alt_text}" loading="lazy">
            </div>
        `).join('');

        galleryGrid.innerHTML = html;
    }

    // Products Renderer
    renderProducts(products) {
        const productsContainer = document.querySelector('.section:has(.section-tag:contains("Coming Soon"))');
        // Products section rendering logic
        console.log('Products loaded:', products);
    }

    // Helper: Get badge class based on category
    getBadgeClass(category) {
        const classes = {
            'HIT OR MISS': 'badge-primary',
            'REACTION': 'badge-secondary',
            'MALAWI MUSIC': 'badge-tertiary'
        };
        return classes[category] || 'badge-primary';
    }
}

// ============================================
// Track Actions Handler
// ============================================
const trackActions = {
    showMenu(trackId) {
        console.log(`Show menu for track ${trackId}`);
        // Implement dropdown menu
    },

    async favorite(trackId) {
        try {
            // POST to API
            console.log(`Favorited track ${trackId}`);
        } catch (error) {
            console.error('Failed to favorite track:', error);
        }
    },

    async addToPlaylist(trackId) {
        try {
            console.log(`Added track ${trackId} to playlist`);
        } catch (error) {
            console.error('Failed to add to playlist:', error);
        }
    }
};

// ============================================
// Data Pipeline Orchestrator
// ============================================
class DataPipeline {
    constructor(apiClient, renderer) {
        this.api = apiClient;
        this.renderer = renderer;
        this.cache = new Map();
    }

    async fetchWithCache(key, fetchFn, ttl = 300000) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < ttl) {
            return cached.data;
        }

        const data = await fetchFn();
        this.cache.set(key, { data, timestamp: Date.now() });
        return data;
    }

    async initialize() {
        console.log('🚀 Initializing Vida Brown Data Pipeline...');

        try {
            // Run all data fetches in parallel for performance
            await Promise.allSettled([
                this.loadArtistProfile(),
                this.loadTrendingVideos(),
                this.loadLatestShows(),
                this.loadTracks(),
                this.loadGallery(),
                this.loadProducts()
            ]);

            console.log('✅ Pipeline initialization complete');
        } catch (error) {
            console.error('❌ Pipeline initialization failed:', error);
            this.showFallbackContent();
        }
    }

    async loadArtistProfile() {
        try {
            const artist = await this.fetchWithCache('artist', () => this.api.getArtistProfile());
            this.renderer.renderArtistProfile(artist);
        } catch (error) {
            console.warn('Failed to load artist profile');
        }
    }

    async loadTrendingVideos() {
        try {
            const [featured, videosData] = await Promise.all([
                this.fetchWithCache('featured-trending', () => this.api.getFeaturedVideo()),
                this.fetchWithCache('trending-videos', () => this.api.getVideos({ limit: 3 }))
            ]);

            // Target the first video section (Trending Now)
            const sections = document.querySelectorAll('.section');
            const trendingSection = sections[0];
            if (trendingSection) {
                const featuredEl = trendingSection.querySelector('.featured-video');
                const gridEl = trendingSection.querySelector('.video-grid');
                if (featuredEl) this.renderer.renderFeaturedVideo(featured, '.section:first-of-type .featured-video');
                if (gridEl) this.renderer.renderVideoGrid(videosData.videos, '.section:first-of-type .video-grid');
            }
        } catch (error) {
            console.warn('Failed to load trending videos');
        }
    }

    async loadLatestShows() {
        try {
            const videosData = await this.fetchWithCache('latest-shows', () => 
                this.api.getVideos({ limit: 5, category: 'HIT OR MISS' })
            );
            // Target the second video section (Latest Shows)
            this.renderer.renderVideoGrid(videosData.videos, '.section:nth-of-type(2) .video-grid');
        } catch (error) {
            console.warn('Failed to load latest shows');
        }
    }

    async loadTracks() {
        try {
            const tracksData = await this.fetchWithCache('tracks', () => this.api.getTracks());
            this.renderer.renderTrackList(tracksData.tracks);
        } catch (error) {
            console.warn('Failed to load tracks');
        }
    }

    async loadGallery() {
        try {
            const images = await this.fetchWithCache('gallery', () => this.api.getGallery());
            this.renderer.renderGallery(images);
        } catch (error) {
            console.warn('Failed to load gallery');
        }
    }

    async loadProducts() {
        try {
            const products = await this.fetchWithCache('products', () => this.api.getProducts());
            this.renderer.renderProducts(products);
        } catch (error) {
            console.warn('Failed to load products');
        }
    }

    showFallbackContent() {
        console.log('📦 Using fallback static content');
        // Keep existing static HTML content if API fails
    }
}

// ============================================
// Theme Toggle
// ============================================
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    
    if (!themeToggle) return;

    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    themeIcon.textContent = savedTheme === 'dark' ? 'dark_mode' : 'light_mode';

    themeToggle.addEventListener('click', () => {
        const isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        themeIcon.textContent = isDark ? 'dark_mode' : 'light_mode';
    });
}

// ============================================
// Newsletter Subscription Handler
// ============================================
function initNewsletterForm() {
    const form = document.querySelector('.newsletter-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = form.querySelector('input[type="email"]').value;
        
        try {
            await api.subscribeNewsletter(email);
            alert('Successfully subscribed!');
            form.reset();
        } catch (error) {
            alert('Subscription failed. Please try again.');
        }
    });
}

// ============================================
// Application Bootstrap
// ============================================
const api = new APIClient(API_CONFIG);
const renderer = new Renderer();
const pipeline = new DataPipeline(api, renderer);

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎵 Vida Brown Website Loaded');
    
    initThemeToggle();
    initNewsletterForm();
    
    // Start the data pipeline
    pipeline.initialize();
});

// Expose for debugging
window.VidaBrown = {
    api,
    renderer,
    pipeline,
    trackActions
};

// API Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000/api',
    TIMEOUT: 10000
};

// API Client
class APIClient {
    constructor() {
        this.baseUrl = API_CONFIG.BASE_URL;
    }

    async request(endpoint) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    // Artist
    async getArtistProfile() {
        return this.request('/artist/profile');
    }

    // YouTube
    async getYouTubeVideos(limit = 10, offset = 0) {
        return this.request(`/youtube/videos?limit=${limit}&offset=${offset}`);
    }

    async getFeaturedVideo() {
        return this.request('/videos/featured');
    }

    async getYouTubeChannel() {
        return this.request('/youtube/channel');
    }

    // Spotify
    async getSpotifyArtist() {
        return this.request('/spotify/artist');
    }

    async getSpotifyTracks(limit = 20) {
        return this.request(`/spotify/tracks?limit=${limit}`);
    }

    async getSpotifyAlbums() {
        return this.request('/spotify/albums');
    }
}

// Renderer
class Renderer {
    // Artist Profile
    renderArtistProfile(artist) {
        const elements = {
            name: document.getElementById('artist-name'),
            title: document.getElementById('artist-title'),
            bio: document.getElementById('artist-bio'),
            image: document.getElementById('artist-image'),
            followers: document.getElementById('follower-count')
        };

        if (elements.name) elements.name.textContent = artist.name;
        if (elements.title) elements.title.textContent = artist.title;
        if (elements.bio) elements.bio.textContent = artist.bio;
        if (elements.followers) elements.followers.textContent = parseInt(artist.followers).toLocaleString();
        
        if (elements.image && artist.images?.youtube) {
            elements.image.src = artist.images.youtube;
        }
    }

    // Featured Video
    renderFeaturedVideo(video) {
        const container = document.getElementById('featured-video');
        if (!container || !video) return;

        container.innerHTML = `
            <div class="video-wrapper">
                <iframe src="${video.embedUrl}" title="${video.title}" frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen></iframe>
            </div>
            <div class="video-info">
                <div class="badges">
                    <span class="badge badge-secondary">${video.category || 'HIT OR MISS'}</span>
                    <span class="badge badge-outline">${new Date(video.publishedAt).getFullYear()}</span>
                </div>
                <h3>${video.title}</h3>
                <p>${video.description?.substring(0, 200)}...</p>
                <div class="video-stats">
                    <span><span class="material-symbols-outlined">visibility</span> ${video.views} views</span>
                    <span><span class="material-symbols-outlined">thumb_up</span> ${video.likes} likes</span>
                    <span><span class="material-symbols-outlined">schedule</span> ${video.duration}</span>
                </div>
            </div>
        `;
    }

    // Video Grid
    renderVideoGrid(videos, containerId) {
        const container = document.getElementById(containerId);
        if (!container || !videos?.length) return;

        const html = videos.map(video => `
            <div class="glass-card video-card" data-video-id="${video.id}">
                <div class="video-wrapper">
                    <iframe src="${video.embedUrl}" title="${video.title}" frameborder="0" 
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                        allowfullscreen></iframe>
                </div>
                <div class="video-card-info">
                    <div class="badges">
                        <span class="badge badge-primary">${video.category || 'HIT OR MISS'}</span>
                        <span class="meta-time">• ${video.duration}</span>
                    </div>
                    <h4>${video.title}</h4>
                    <p>${video.description?.substring(0, 100)}...</p>
                    <div class="video-stats">
                        <span>${video.views} views</span>
                        <span>•</span>
                        <span>${new Date(video.publishedAt).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}</span>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    // Track List
    renderTrackList(tracks) {
        const container = document.getElementById('track-list');
        if (!container || !tracks?.length) return;

        const html = tracks.map((track, index) => `
            <div class="track-item" data-track-id="${track.id}">
                <div class="track-info">
                    <span class="track-num">${String(index + 1).padStart(2, '0')}</span>
                    <div>
                        <div class="track-title">${track.title}</div>
                        <div class="track-artist">${track.artist}${track.album ? ' • ' + track.album : ''}</div>
                    </div>
                </div>
                <div class="track-meta">
                    <span>Popularity: ${track.popularity}</span>
                    <button class="track-more" onclick="trackActions.showMenu('${track.id}')">
                        <span class="material-symbols-outlined">more_horiz</span>
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }
}

// Track Actions
const trackActions = {
    showMenu(trackId) {
        console.log(`Show menu for track: ${trackId}`);
        // Implement dropdown menu
    },

    async playTrack(trackId) {
        console.log(`Play track: ${trackId}`);
    },

    async addToPlaylist(trackId) {
        console.log(`Add to playlist: ${trackId}`);
    }
};

// Initialize
const api = new APIClient();
const renderer = new Renderer();

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎵 Vida Brown Website - Loading from YouTube & Spotify APIs');

    try {
        // Load artist profile
        const artist = await api.getArtistProfile();
        renderer.renderArtistProfile(artist);

        // Load featured video
        const featuredVideo = await api.getFeaturedVideo();
        renderer.renderFeaturedVideo(featuredVideo);

        // Load trending videos
        const trendingVideos = await api.getYouTubeVideos(3);
        renderer.renderVideoGrid(trendingVideos.videos, 'trending-grid');

        // Load shows
        const shows = await api.getYouTubeVideos(5);
        renderer.renderVideoGrid(shows.videos, 'shows-grid');

        // Load Spotify tracks
        const tracks = await api.getSpotifyTracks(8);
        renderer.renderTrackList(tracks.tracks);

        console.log('✅ All data loaded successfully from APIs');
    } catch (error) {
        console.error('❌ Failed to load data:', error);
    }
});

// Expose for debugging
window.VidaBrown = {
    api,
    renderer,
    trackActions
};