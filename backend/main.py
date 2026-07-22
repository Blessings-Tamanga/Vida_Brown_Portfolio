import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import logging

from database.database import Base, SessionLocal, engine
from models import models
from routes.routes import router

load_dotenv()

app = FastAPI(
    title="Vida Brown API",
    description="Backend API for the Vida Brown portfolio and admin dashboard",
    version="1.0.0",
    docs_url="/docs",  # This is where your endpoints will be viewed
    redoc_url="/redoc"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vidabrown")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change to your Vercel/Netlify URL in production
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(router)

# --- Database Initialization ---
def seed_database() -> None:
    db = SessionLocal()
    try:
        # Self-healing: Wipe old string data if it exists
        bad_video = db.query(models.Video).filter(models.Video.views == "10.7K").first()
        bad_track = db.query(models.Track).filter(models.Track.streams == "12.4K").first()
        
        if bad_video or bad_track:
            logger.warning("⚠️ Detected old string-based seed data. Wiping and reseeding with integers...")
            db.query(models.Video).delete()
            db.query(models.Track).delete()
            db.query(models.GalleryImage).delete()
            db.query(models.Artist).delete()
            db.commit()

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
        logger.info("✅ Database seeded successfully with clean integer data.")
    except Exception as e:
        db.rollback()
        logger.warning(f"Seeding skipped or failed: {e}")
    finally:
        db.close()

def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    seed_database()

@app.on_event("startup")
def startup_event() -> None:
    initialize_database()

@app.get("/")
def root():
    return {"message": "Welcome to the Vida Brown API. Visit /docs to view all endpoints."}

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)