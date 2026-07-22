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
    if (isGlobal) {
        setTimeout(() => { el.textContent = ''; el.className = 'status-msg'; }, 3000);
    }
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
        const res = await fetch('/api/videos?limit=1', { headers: { 'X-Admin-Token': token } });
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
        const [videosRes, tracksRes, galleryRes] = await Promise.all([
            fetch('/api/videos?limit=50').then(r => r.json()),
            fetch('/api/music/tracks?limit=100').then(r => r.json()),
            fetch('/api/gallery').then(r => r.json())
        ]);

        const videos = videosRes.videos || videosRes || [];
        const tracks = tracksRes.tracks || tracksRes || [];
        const gallery = galleryRes || [];

        document.getElementById('stat-videos').textContent = videos.length;
        document.getElementById('stat-tracks').textContent = tracks.length;
        document.getElementById('stat-gallery').textContent = gallery.length;

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
                                <div style="font-size:12px; color:var(--text-secondary);">${v.category || 'Video'} • ${v.views || 0} views</div>
                            </div>
                        </div>
                        <div class="list-item-actions">
                            <button class="btn btn-outline btn-sm del-v" data-id="${v.id}">Delete</button>
                        </div>
                    `;
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
                                <div style="font-size:12px; color:var(--text-secondary);">${t.artist_name} • ${t.streams || 0} streams</div>
                            </div>
                        </div>
                        <div class="list-item-actions">
                            <button class="btn btn-outline btn-sm del-t" data-id="${t.id}">Delete</button>
                        </div>
                    `;
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
                            <img src="${g.url}" alt="${g.alt_text}" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2248%22 height=%2248%22><rect width=%2248%22 height=%2248%22 fill=%22%23333%22/></svg>'">
                            <div>
                                <div style="font-weight:600;">${g.alt_text}</div>
                                <div style="font-size:12px; color:var(--text-secondary);">Order: ${g.order || 0}</div>
                            </div>
                        </div>
                        <div class="list-item-actions">
                            <button class="btn btn-outline btn-sm del-g" data-id="${g.id}">Delete</button>
                        </div>
                    `;
            glist.appendChild(el);
        });

        // Attach delete listeners
        document.querySelectorAll('.del-v').forEach(btn => btn.addEventListener('click', async (e) => {
            if (!confirm('Delete this video?')) return;
            try {
                await deleteReq(`/api/admin/videos/${e.target.dataset.id}`);
                setStatus('Video deleted.', false, true);
                refreshLists();
            } catch (err) { setStatus(err.message, true, true); }
        }));

        document.querySelectorAll('.del-t').forEach(btn => btn.addEventListener('click', async (e) => {
            if (!confirm('Delete this track?')) return;
            try {
                await deleteReq(`/api/admin/tracks/${e.target.dataset.id}`);
                setStatus('Track deleted.', false, true);
                refreshLists();
            } catch (err) { setStatus(err.message, true, true); }
        }));

        document.querySelectorAll('.del-g').forEach(btn => btn.addEventListener('click', async (e) => {
            if (!confirm('Delete this image?')) return;
            try {
                await deleteReq(`/api/admin/gallery/${e.target.dataset.id}`);
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
    try {
        const res = await fetch('/api/admin/login', {
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
    payload.is_featured = event.target.is_featured.checked;
    try {
        await postJson('/api/admin/videos', payload);
        setStatus('Video saved successfully.', false, true);
        event.target.reset();
        await refreshLists();
    } catch (error) {
        setStatus(error.message, true, true);
    }
});

document.getElementById('track-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(event.target));
    payload.track_number = Number(payload.track_number);
    payload.artist_id = Number(payload.artist_id);
    try {
        await postJson('/api/admin/tracks', payload);
        setStatus('Track saved successfully.', false, true);
        event.target.reset();
        await refreshLists();
    } catch (error) {
        setStatus(error.message, true, true);
    }
});

document.getElementById('gallery-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(event.target));
    payload.order = Number(payload.order);
    try {
        await postJson('/api/admin/gallery', payload);
        setStatus('Gallery image saved successfully.', false, true);
        event.target.reset();
        await refreshLists();
    } catch (error) {
        setStatus(error.message, true, true);
    }
});