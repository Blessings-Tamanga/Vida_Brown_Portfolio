from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
import crud.crud as crud
import schemas.schemas as schemas

router = APIRouter(prefix="/api", tags=["Vida Brown API"])

# Artist Routes
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

# Video Routes
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
    video = crud.get_videos(db, skip=0, limit=1)  # You'd implement get_video_by_id
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video[0]

# Music Routes
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

# Gallery Routes
@router.get("/gallery", response_model=List[schemas.GalleryImageResponse])
async def get_gallery(
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get gallery images"""
    return crud.get_gallery_images(db, skip=offset, limit=limit)

# Products Routes
@router.get("/products", response_model=List[schemas.ProductResponse])
async def get_products(
    available_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get merchandise products"""
    return crud.get_products(db, skip=offset, limit=limit, available_only=available_only)

# Newsletter Routes
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

# Admin Routes (for adding content)
@router.post("/admin/videos", response_model=schemas.VideoResponse)
async def create_video(
    video: schemas.VideoCreate,
    db: Session = Depends(get_db)
):
    """Create a new video (Admin)"""
    return crud.create_video(db, video)

@router.post("/admin/tracks", response_model=schemas.TrackResponse)
async def create_track(
    track: schemas.TrackCreate,
    db: Session = Depends(get_db)
):
    """Create a new track (Admin)"""
    return crud.create_track(db, track)

@router.post("/admin/gallery", response_model=schemas.GalleryImageResponse)
async def create_gallery_image(
    image: schemas.GalleryImageCreate,
    db: Session = Depends(get_db)
):
    """Add image to gallery (Admin)"""
    return crud.create_gallery_image(db, image)