from datetime import datetime, timedelta
from pathlib import Path


from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import Request
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

# Basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vidabrown")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

cache: dict[str, tuple[object, datetime]] = {}

CACHE_DURATION_SECONDS = 300


def seed_database() -> None:
    db = SessionLocal()
    try:
        artist = db.query(models.Artist).first()
        if not artist:
            artist = models.Artist(
                name="Vida Brown",
                title="Singer • Songwriter • Producer",
                bio="Born Vida Ezra Gérmaño, known as Vida (Veeda) - a Malawian artist creating music, arts, and culture content.",
                followers=82,
            )
            db.add(artist)
            db.flush()

        if not db.query(models.Video).first():
            db.add_all(
                [
                    models.Video(
                        title="Diamond Platnumz - Happy",
                        youtube_id="nWA4D9U-q48",
                        embed_url="https://www.youtube.com/embed/nWA4D9U-q48",
                        category="HIT OR MISS",
                        views="10.7K",
                        likes="330",
                        duration="5:26",
                        upload_date="Mar 2026",
                        description="VIDEO REVIEW | HIT OR MISS - Breaking down the latest banger from Diamond Platnumz.",
                        is_featured=True,
                    ),
                    models.Video(
                        title="Adekunle Gold ft Davido - Only God Can Save Me",
                        youtube_id="JqEXp4EJjlw",
                        embed_url="https://www.youtube.com/embed/JqEXp4EJjlw",
                        category="HIT OR MISS",
                        views="210",
                        likes="48",
                        duration="5:06",
                        upload_date="Feb 2026",
                        description="Reviewing the collaboration between two Nigerian powerhouses.",
                    ),
                    models.Video(
                        title="AYRA STARR - ALL THE LOVE",
                        youtube_id="UujBzYu6z0E",
                        embed_url="https://www.youtube.com/embed/UujBzYu6z0E",
                        category="REACTION",
                        views="4.6K",
                        likes="92",
                        duration="5:03",
                        upload_date="Feb 2025",
                        description="A fresh reaction to Ayra Starr's latest release.",
                    ),
                ]
            )

        if not db.query(models.Track).first():
            db.add_all(
                [
                    models.Track(
                        track_number=1,
                        title="Umbrella",
                        artist_name="Vida Brown",
                        featured_artist=None,
                        year="2024",
                        streams="12.4K",
                        track_type="Single",
                        artist_id=artist.id,
                    ),
                    models.Track(
                        track_number=2,
                        title="PON ME (Everything)",
                        artist_name="Vida Brown",
                        featured_artist=None,
                        year="2025",
                        streams="8.2K",
                        track_type="Single",
                        artist_id=artist.id,
                    ),
                ]
            )

        if not db.query(models.GalleryImage).first():
            db.add_all(
                [
                    models.GalleryImage(
                        url="https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=900&q=80",
                        alt_text="Vida Brown on stage",
                        order=1,
                    ),
                    models.GalleryImage(
                        url="https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=900&q=80",
                        alt_text="Studio session",
                        order=2,
                    ),
                    models.GalleryImage(
                        url="https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=900&q=80",
                        alt_text="Creative portrait",
                        order=3,
                    ),
                ]
            )

        if not db.query(models.Product).first():
            db.add(
                models.Product(
                    name="Signature Tee",
                    description="Limited-edition artwork tee",
                    price=3500,
                    image_url="https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80",
                    is_available=True,
                )
            )

        db.commit()
    finally:
        db.close()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Completed request: {request.method} {request.url} -> {response.status_code}")
        return response
    except Exception:
        logger.exception("Unhandled exception during request")
        raise


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    seed_database()


@app.on_event("startup")
def startup_event() -> None:
    initialize_database()


initialize_database()


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/")
def serve_index() -> str:
    return (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/admin")
def serve_admin() -> str:
    return (FRONTEND_DIR / "admin.html").read_text(encoding="utf-8")


@app.get("/api/spotify/tracks")
async def get_spotify_tracks(
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    """Get artist's top tracks."""
    cache_key = f"spotify_tracks_{limit}_{offset}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    artist_id = "3ihbWDeubJO4XmeZlCGqZL"
    token = ""
    try:
        response = requests.get(
            f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks",
            params={"market": "US"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch tracks")
        data = response.json()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch tracks") from exc

    tracks = []
    for idx, track in enumerate(data["tracks"][offset: offset + limit], start=1):
        tracks.append(
            {
                "id": track["id"],
                "trackNumber": idx,
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "duration_ms": track["duration_ms"],
                "popularity": track["popularity"],
                "previewUrl": track["preview_url"],
                "externalUrls": track["external_urls"],
            }
        )

    result = {"tracks": tracks, "total": len(tracks)}
    set_cache(cache_key, result)
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
