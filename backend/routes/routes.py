from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import os

from database.database import get_db
import crud.crud as crud
import schemas.schemas as schemas

router = APIRouter(prefix="/api", tags=["Vida Brown API"])

# --- Schemas ---
class AdminLogin(BaseModel):
    password: str

# --- Dependencies ---
def admin_required(x_admin_token: str = Header(None, alias="X-Admin-Token")):
    """
    Simple admin token check. 
    Requires ADMIN_TOKEN environment variable to be set.
    """
    expected = os.getenv("ADMIN_TOKEN")
    if not expected:
        # Fail loudly in production if env var is missing
        raise HTTPException(status_code=500, detail="Server configuration error: ADMIN_TOKEN not set")
    
    if x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid admin token")
    return True

# --- Artist Routes ---
@router.get("/artist/profile", response_model=schemas.ArtistResponse)
async def get_artist_profile(db: Session = Depends(get_db)):
    """Get artist profile information"""
    artist = crud.get_artist_by_name(db, name="Vida Brown")
    if not artist:
        # Create default artist if not exists
        artist_data = schemas.ArtistCreate(
            name="Vida Brown",
            title="Singer • Songwriter • Producer",
            bio="Born Vida Ezra Gérmaño, known as Vida (Veeda) - a Malawian artist creating music, arts, and culture content.",
            followers=82
        )
        artist = crud.create_artist(db, artist_data)
    return artist

# --- Video Routes ---
@router.get("/videos", response_model=schemas.VideosResponse)
async def get_videos(
    category: Optional[str] = Query(None, description="Filter by category: HIT OR MISS, REACTION, MALAWI MUSIC"),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get list of videos with optional filtering"""
    videos = crud.get_videos(db, skip=offset, limit=limit, category=category)
    total = crud.get_video_count(db, category=category)
    return {"videos": videos, "total": total}

@router.get("/videos/featured", response_model=schemas.VideoResponse)
async def get_featured_video(db: Session = Depends(get_db)):
    """Get the featured video"""
    video = crud.get_featured_video(db)
    if not video:
        raise HTTPException(status_code=404, detail="No featured video found")
    return video

@router.get("/videos/{video_id}", response_model=schemas.VideoResponse)
async def get_video(video_id: int, db: Session = Depends(get_db)):
    """Get a specific video by ID"""
    # FIXED: Now actually uses the video_id parameter
    video = crud.get_video_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

# --- Music Routes ---
@router.get("/music/tracks", response_model=schemas.TracksResponse)
async def get_tracks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all music tracks"""
    tracks = crud.get_tracks(db, skip=offset, limit=limit)
    total = crud.get_track_count(db)
    return {"tracks": tracks, "total": total}

# --- Gallery Routes ---
@router.get("/gallery", response_model=List[schemas.GalleryImageResponse])
async def get_gallery(
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get gallery images"""
    return crud.get_gallery_images(db, skip=offset, limit=limit)

# --- Products Routes ---
@router.get("/products", response_model=List[schemas.ProductResponse])
async def get_products(
    available_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get merchandise products"""
    return crud.get_products(db, skip=offset, limit=limit, available_only=available_only)

# --- Newsletter Routes ---
@router.post("/newsletter/subscribe")
async def subscribe_newsletter(
    subscription: schemas.NewsletterSubscribe,
    db: Session = Depends(get_db)
):
    """Subscribe to newsletter"""
    existing = crud.get_subscriber_by_email(db, subscription.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already subscribed")
    
    crud.create_subscriber(db, subscription.email)
    return {"message": "Successfully subscribed to newsletter!"}


# --- Admin Routes (Content Management) ---

@router.get("/admin/me")
async def get_admin_info(admin: bool = Depends(admin_required)):
    """Verify the admin token is actually valid"""
    return {"status": "authenticated", "role": "admin"}

@router.post("/admin/login")
async def admin_login(payload: AdminLogin):
    """Exchange admin password for a bearer token"""
    # FIXED: Uses proper Pydantic model instead of raw dict
    expected_password = os.getenv("ADMIN_PASSWORD")
    if not expected_password:
        raise HTTPException(status_code=500, detail="Server configuration error: ADMIN_PASSWORD not set")
        
    if payload.password != expected_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = os.getenv("ADMIN_TOKEN")
    return {"token": token}

@router.post("/admin/videos", response_model=schemas.VideoResponse)
async def create_video(
    video: schemas.VideoCreate,
    db: Session = Depends(get_db),
    admin: bool = Depends(admin_required)
):
    """Create a new video (Admin)"""
    return crud.create_video(db, video)

@router.put("/admin/videos/{video_id}", response_model=schemas.VideoResponse)
async def update_video(
    video_id: int, 
    video: schemas.VideoCreate, 
    db: Session = Depends(get_db), 
    admin: bool = Depends(admin_required)
):
    """Update an existing video (Admin)"""
    updated = crud.update_video(db, video_id, video)
    if not updated:
        raise HTTPException(status_code=404, detail="Video not found")
    return updated

@router.delete("/admin/videos/{video_id}")
async def delete_video(
    video_id: int, 
    db: Session = Depends(get_db), 
    admin: bool = Depends(admin_required)
):
    """Delete a video (Admin)"""
    success = crud.delete_video(db, video_id)
    if not success:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"message": "Video deleted successfully"}

@router.post("/admin/tracks", response_model=schemas.TrackResponse)
async def create_track(
    track: schemas.TrackCreate,
    db: Session = Depends(get_db),
    admin: bool = Depends(admin_required)
):
    """Create a new track (Admin)"""
    return crud.create_track(db, track)

@router.put("/admin/tracks/{track_id}", response_model=schemas.TrackResponse)
async def update_track(
    track_id: int, 
    track: schemas.TrackCreate, 
    db: Session = Depends(get_db), 
    admin: bool = Depends(admin_required)
):
    """Update an existing track (Admin)"""
    updated = crud.update_track(db, track_id, track)
    if not updated:
        raise HTTPException(status_code=404, detail="Track not found")
    return updated

@router.delete("/admin/tracks/{track_id}")
async def delete_track(
    track_id: int, 
    db: Session = Depends(get_db), 
    admin: bool = Depends(admin_required)
):
    """Delete a track (Admin)"""
    success = crud.delete_track(db, track_id)
    if not success:
        raise HTTPException(status_code=404, detail="Track not found")
    return {"message": "Track deleted successfully"}

@router.post("/admin/gallery", response_model=schemas.GalleryImageResponse)
async def create_gallery_image(
    image: schemas.GalleryImageCreate,
    db: Session = Depends(get_db),
    admin: bool = Depends(admin_required)
):
    """Add image to gallery (Admin)"""
    return crud.create_gallery_image(db, image)

@router.put("/admin/gallery/{image_id}", response_model=schemas.GalleryImageResponse)
async def update_gallery(
    image_id: int, 
    image: schemas.GalleryImageCreate, 
    db: Session = Depends(get_db), 
    admin: bool = Depends(admin_required)
):
    """Update an existing gallery image (Admin)"""
    updated = crud.update_gallery_image(db, image_id, image)
    if not updated:
        raise HTTPException(status_code=404, detail="Image not found")
    return updated

@router.delete("/admin/gallery/{image_id}")
async def delete_gallery(
    image_id: int, 
    db: Session = Depends(get_db), 
    admin: bool = Depends(admin_required)
):
    """Delete a gallery image (Admin)"""
    success = crud.delete_gallery_image(db, image_id)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}