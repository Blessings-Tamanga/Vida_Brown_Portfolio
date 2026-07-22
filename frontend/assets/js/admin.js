// --- API Configuration ---
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000/api'
    : 'https://vida-brown-portfolio-api.onrender.com/api'; // <-- REPLACE WITH YOUR ACTUAL RENDER URL

// --- UI Logic ---
const tabs = document.querySelectorAll('.admin-nav-link[data-tab]');
const sections = document.querySelectorAll('.admin-section');
const pageTitle = document.getElementById('page-title');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const target = tab.getAttribute('data-tab');
        sections.forEach(sec => sec.classList.remove('active'));
        document.getElementById(target).classList.add('active');
        pageTitle.textContent = tab.textContent.trim();
    });
});

// --- Auth & API Logic ---
const globalStatus = document.getElementById('global-status');
const loginStatus = document.getElementById('login-status');

const setStatus = (message, isError = false, isGlobal = false) => {
    const el = isGlobal ? globalStatus : loginStatus;
    el.textContent = message;
    el.className = 'status-msg ' + (isError ? 'error' : 'success');
    if (isGlobal) setTimeout(() => { el.textContent = ''; el.className = 'status-msg'; }, 4000);
};

const TOKEN_KEY = 'vida_admin_token';
function setToken(token) { if (token) localStorage.setItem(TOKEN_KEY, token); else localStorage.removeItem(TOKEN_KEY); }
function getToken() { return localStorage.getItem(TOKEN_KEY); }

async function postJson(url, payload) {
    const headers = { 'Content-Type': 'application/json' };
    const token = getToken();
    if (token) headers['X-Admin-Token'] = token;
    const response = await fetch(url, { method: 'POST', headers, body: JSON.stringify(payload) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || 'Request failed');
    return data;
}

async function deleteReq(url) {
    const headers = {};
    const token = getToken();
    if (token) headers['X-Admin-Token'] = token;
    const response = await fetch(url, { method: 'DELETE', headers });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || 'Request failed');
    return data;
}

async function ensureAuth() {
    const token = getToken();
    if (!token) return false;
    try {
        // FIXED: Now checks a protected admin endpoint, not the public /videos endpoint
        const res = await fetch(`${API_BASE}/admin/me`, { headers: { 'X-Admin-Token': token } });
        if (res.status === 401) { setToken(null); return false; }
        return true;
    } catch (e) { setToken(null); return false; }
}

async function showAuthenticatedUI() {
    document.getElementById('login-overlay').style.display = 'none';
    document.getElementById('admin-layout').style.display = 'grid';
    await refreshLists();
}

async function refreshLists() {
    try {
        const [videosRes, tracksRes, galleryRes, artistRes] = await Promise.all([
            fetch(`${API_BASE}/videos?limit=50`).then(r => r.json()),
            fetch(`${API_BASE}/music/tracks?limit=100`).then(r => r.json()),
            fetch(`${API_BASE}/gallery`).then(r => r.json()),
            fetch(`${API_BASE}/artist/profile`).then(r => r.json()) // FIXED: Get real follower count
        ]);

        const videos = videosRes.videos || [];
        const tracks = tracksRes.tracks || [];
        const gallery = galleryRes || [];

        document.getElementById('stat-videos').textContent = videos.length;
        document.getElementById('stat-tracks').textContent = tracks.length;
        document.getElementById('stat-gallery').textContent = gallery.length;
        document.getElementById('stat-followers').textContent = artistRes.followers || 0; // FIXED

        // Render Videos
        const vlist = document.getElementById('videos-list');
        vlist.innerHTML = videos.length ? '' : '<p style="color:var(--text-secondary); padding: 16px;">No videos found.</p>';
        videos.forEach(v => {
            const el = document.createElement('div');
            el.className = 'list-item';
            el.innerHTML = `
                <div class="list-item-info">
                    <div>
                        <div style="font-weight:600;">${v.title}</div>
                        <div style="font-size:12px; color:var(--text-secondary);">${v.category} • ${v.views_display || 0} views</div>
                    </div>
                </div>
                <div class="list-item-actions">
                    <button class="btn btn-outline btn-sm del-v" data-id="${v.id}">Delete</button>
                </div>`;
            vlist.appendChild(el);
        });

        // Render Tracks
        const tlist = document.getElementById('tracks-list');
        tlist.innerHTML = tracks.length ? '' : '<p style="color:var(--text-secondary); padding: 16px;">No tracks found.</p>';
        tracks.forEach(t => {
            const el = document.createElement('div');
            el.className = 'list-item';
            el.innerHTML = `
                <div class="list-item-info">
                    <div>
                        <div style="font-weight:600;">${t.title}</div>
                        <div style="font-size:12px; color:var(--text-secondary);">${t.artist_name} • ${t.streams_display || 0} streams</div>
                    </div>
                </div>
                <div class="list-item-actions">
                    <button class="btn btn-outline btn-sm del-t" data-id="${t.id}">Delete</button>
                </div>`;
            tlist.appendChild(el);
        });

        // Render Gallery
        const glist = document.getElementById('gallery-list');
        glist.innerHTML = gallery.length ? '' : '<p style="color:var(--text-secondary); padding: 16px;">No images found.</p>';
        gallery.forEach(g => {
            const el = document.createElement('div');
            el.className = 'list-item';
            el.innerHTML = `
                <div class="list-item-info">
                    <img src="${g.url}" alt="${g.alt_text}" onerror="this.style.display='none'">
                    <div>
                        <div style="font-weight:600;">${g.alt_text}</div>
                        <div style="font-size:12px; color:var(--text-secondary);">Order: ${g.order || 0}</div>
                    </div>
                </div>
                <div class="list-item-actions">
                    <button class="btn btn-outline btn-sm del-g" data-id="${g.id}">Delete</button>
                </div>`;
            glist.appendChild(el);
        });

        // Attach delete listeners
        document.querySelectorAll('.del-v').forEach(btn => btn.addEventListener('click', async (e) => {
            if (!confirm('Delete this video?')) return;
            try {
                await deleteReq(`${API_BASE}/admin/videos/${e.target.dataset.id}`);
                setStatus('Video deleted.', false, true);
                refreshLists();
            } catch (err) { setStatus(err.message, true, true); }
        }));

        document.querySelectorAll('.del-t').forEach(btn => btn.addEventListener('click', async (e) => {
            if (!confirm('Delete this track?')) return;
            try {
                await deleteReq(`${API_BASE}/admin/tracks/${e.target.dataset.id}`);
                setStatus('Track deleted.', false, true);
                refreshLists();
            } catch (err) { setStatus(err.message, true, true); }
        }));

        document.querySelectorAll('.del-g').forEach(btn => btn.addEventListener('click', async (e) => {
            if (!confirm('Delete this image?')) return;
            try {
                await deleteReq(`${API_BASE}/admin/gallery/${e.target.dataset.id}`);
                setStatus('Image deleted.', false, true);
                refreshLists();
            } catch (err) { setStatus(err.message, true, true); }
        }));

    } catch (e) {
        console.warn('Refresh failed', e);
    }
}

// Initialize
(async () => {
    const ok = await ensureAuth();
    if (ok) await showAuthenticatedUI();
})();

// Login
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const pw = document.getElementById('admin-password').value;
    const btn = e.target.querySelector('button');
    btn.textContent = 'Checking...';
    btn.disabled = true;
    
    try {
        const res = await fetch(`${API_BASE}/admin/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: pw })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Login failed');
        setToken(data.token);
        await showAuthenticatedUI();
    } catch (err) {
        setStatus(err.message, true, false);
        document.getElementById('admin-password').value = ''; // FIXED: Clear password on fail
    } finally {
        btn.textContent = 'Login';
        btn.disabled = false;
    }
});

// Logout
document.getElementById('logout-btn').addEventListener('click', () => {
    setToken(null);
    document.getElementById('admin-layout').style.display = 'none';
    document.getElementById('login-overlay').style.display = 'flex';
    document.getElementById('admin-password').value = '';
    loginStatus.textContent = '';
});

// Forms
document.getElementById('video-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(event.target));
    
    // FIXED: Convert strings to numbers for backend
    payload.views = Number(payload.views) || 0;
    payload.likes = Number(payload.likes) || 0;
    payload.is_featured = event.target.is_featured.checked;
    
    const btn = event.target.querySelector('button[type="submit"]');
    btn.textContent = 'Saving...'; btn.disabled = true;

    try {
        await postJson(`${API_BASE}/admin/videos`, payload);
        setStatus('Video saved successfully.', false, true);
        event.target.reset();
        await refreshLists();
    } catch (error) {
        setStatus(error.message, true, true);
    } finally {
        btn.textContent = 'Save Video'; btn.disabled = false;
    }
});

document.getElementById('track-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(event.target));
    
    // FIXED: Convert strings to numbers
    payload.track_number = Number(payload.track_number);
    payload.artist_id = Number(payload.artist_id);
    payload.streams = Number(payload.streams) || 0;
    
    const btn = event.target.querySelector('button[type="submit"]');
    btn.textContent = 'Saving...'; btn.disabled = true;

    try {
        await postJson(`${API_BASE}/admin/tracks`, payload);
        setStatus('Track saved successfully.', false, true);
        event.target.reset();
        await refreshLists();
    } catch (error) {
        setStatus(error.message, true, true);
    } finally {
        btn.textContent = 'Save Track'; btn.disabled = false;
    }
});

document.getElementById('gallery-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(event.target));
    payload.order = Number(payload.order) || 0;
    
    const btn = event.target.querySelector('button[type="submit"]');
    btn.textContent = 'Saving...'; btn.disabled = true;

    try {
        await postJson(`${API_BASE}/admin/gallery`, payload);
        setStatus('Gallery image saved successfully.', false, true);
        event.target.reset();
        await refreshLists();
    } catch (error) {
        setStatus(error.message, true, true);
    } finally {
        btn.textContent = 'Save Image'; btn.disabled = false;
    }
});