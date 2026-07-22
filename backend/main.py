import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging

from database.database import Base, SessionLocal, engine
from models import models
from routes.routes import router

load_dotenv()

app = FastAPI(
    title="Vida Brown API",
    description="Backend for the Vida Brown portfolio and admin dashboard",
    version="1.0.0",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vidabrown")

# FIXED: Cannot use allow_credentials=True with allow_origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change to your specific Vercel/Render URL in production
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

# Mount static files safely
if (FRONTEND_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

# FIXED: Added missing cache functions to prevent NameError
_cache: dict[str, tuple[object, datetime]] = {}
def get_cached(key: str):
    if key in _cache:
        data, timestamp = _cache[key]
        if datetime.now() - timestamp < timedelta(seconds=300):
            return data
    return None

def set_cache(key: str, value: object):
    _cache[key] = (value, datetime.now())

def seed_database() -> None:
    db = SessionLocal()
    try:
        artist = db.query(models.Artist).first()
        if not artist:
            artist = models.Artist(
                name="Vida Brown", title="Singer • Songwriter • Producer",
                bio="Born Vida Ezra Gérmaño, known as Vida (Veeda) - a Malawian artist creating music, arts, and culture content.",
                followers=82,
            )
            db.add(artist)
            db.flush()

        if not db.query(models.Video).first():
            db.add_all([
                models.Video(title="Diamond Platnumz - Happy", youtube_id="nWA4D9U-q48", embed_url="https://www.youtube.com/embed/nWA4D9U-q48", category="HIT OR MISS", views=10700, likes=330, duration="5:26", upload_date="Mar 2026", description="VIDEO REVIEW", is_featured=True),
                models.Video(title="Adekunle Gold ft Davido", youtube_id="JqEXp4EJjlw", embed_url="https://www.youtube.com/embed/JqEXp4EJjlw", category="HIT OR MISS", views=210, likes=48, duration="5:06", upload_date="Feb 2026", description="Reviewing collaboration"),
                models.Video(title="AYRA STARR - ALL THE LOVE", youtube_id="UujBzYu6z0E", embed_url="https://www.youtube.com/embed/UujBzYu6z0E", category="REACTION", views=4600, likes=92, duration="5:03", upload_date="Feb 2025", description="Fresh reaction"),
            ])

        if not db.query(models.Track).first():
            db.add_all([
                models.Track(track_number=1, title="Umbrella", artist_name="Vida Brown", year="2024", streams=12400, track_type="Single", artist_id=artist.id),
                models.Track(track_number=2, title="PON ME (Everything)", artist_name="Vida Brown", year="2025", streams=8200, track_type="Single", artist_id=artist.id),
            ])

        if not db.query(models.GalleryImage).first():
            db.add_all([
                models.GalleryImage(url="https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=900", alt_text="Vida Brown on stage", order=1),
                models.GalleryImage(url="https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=900", alt_text="Studio session", order=2),
            ])
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"Seeding skipped (data may already exist): {e}")
    finally:
        db.close()

def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    seed_database()

# FIXED: Removed manual initialize_database() call at the bottom to prevent double execution
@app.on_event("startup")
def startup_event() -> None:
    initialize_database()

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}

# FIXED: Use FileResponse instead of read_text() for proper HTML serving
@app.get("/")
def serve_index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/admin")
def serve_admin() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "admin.html")

@app.get("/api/spotify/tracks")
async def get_spotify_tracks(limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    cache_key = f"spotify_tracks_{limit}_{offset}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    artist_id = os.getenv("SPOTIFY_ARTIST_ID", "3ihbWDeubJO4XmeZlCGqZL")
    # Note: You must add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET to Render env vars to get a real token
    token = os.getenv("SPOTIFY_ACCESS_TOKEN", "") 
    
    try:
        response = requests.get(f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks", params={"market": "US"}, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch tracks from Spotify")
        data = response.json()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch tracks") from exc

    tracks = [{"id": track["id"], "trackNumber": idx, "title": track["name"], "artist": track["artists"][0]["name"], "album": track["album"]["name"], "popularity": track["popularity"]} for idx, track in enumerate(data.get("tracks", [])[offset: offset + limit], start=1)]
    
    result = {"tracks": tracks, "total": len(tracks)}
    set_cache(cache_key, result)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)