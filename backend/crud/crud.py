from sqlalchemy.orm import Session
from sqlalchemy import func
from models import models
from schemas import schemas
from typing import List, Optional

# --- Helper for Safe DB Operations ---
def _safe_commit(db: Session):
    """
    Wraps db.commit() in a try/except block to ensure the session 
    is rolled back on failure, preventing database corruption/locks.
    """
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

# --- Artist CRUD ---
def get_artist(db: Session, artist_id: int):
    return db.query(models.Artist).filter(models.Artist.id == artist_id).first()

def get_artist_by_name(db: Session, name: str):
    return db.query(models.Artist).filter(models.Artist.name == name).first()

def create_artist(db: Session, artist: schemas.ArtistCreate):
    db_artist = models.Artist(**artist.model_dump())
    db.add(db_artist)
    _safe_commit(db)
    db.refresh(db_artist)
    return db_artist

# --- Track CRUD ---
def get_tracks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Track).order_by(models.Track.track_number).offset(skip).limit(limit).all()

def get_track_count(db: Session):
    return db.query(func.count(models.Track.id)).scalar()

def create_track(db: Session, track: schemas.TrackCreate):
    db_track = models.Track(**track.model_dump())
    db.add(db_track)
    _safe_commit(db)
    db.refresh(db_track)
    return db_track

def update_track(db: Session, track_id: int, track: schemas.TrackCreate):
    db_track = db.query(models.Track).filter(models.Track.id == track_id).first()
    if not db_track:
        return None
    for key, value in track.model_dump().items():
        setattr(db_track, key, value)
    _safe_commit(db)
    db.refresh(db_track)
    return db_track

def delete_track(db: Session, track_id: int):
    db_track = db.query(models.Track).filter(models.Track.id == track_id).first()
    if not db_track:
        return False
    db.delete(db_track)
    _safe_commit(db)
    return True

# --- Video CRUD ---
def get_videos(db: Session, skip: int = 0, limit: int = 100, category: Optional[str] = None):
    query = db.query(models.Video)
    if category:
        query = query.filter(models.Video.category == category)
    return query.order_by(models.Video.created_at.desc()).offset(skip).limit(limit).all()


def get_video_by_id(db: Session, video_id: int):
    return db.query(models.Video).filter(models.Video.id == video_id).first()

def get_featured_video(db: Session):
    # FIXED: Added order_by to ensure deterministic results if multiple are somehow marked featured
    return db.query(models.Video).filter(models.Video.is_featured == True).order_by(models.Video.created_at.desc()).first()

def get_video_count(db: Session, category: Optional[str] = None):
    query = db.query(func.count(models.Video.id))
    if category:
        query = query.filter(models.Video.category == category)
    return query.scalar()

def create_video(db: Session, video: schemas.VideoCreate):
    # FIXED: Ensure only ONE video is featured at a time
    if video.is_featured:
        db.query(models.Video).filter(models.Video.is_featured == True).update({"is_featured": False})
    
    db_video = models.Video(**video.model_dump())
    db.add(db_video)
    _safe_commit(db)
    db.refresh(db_video)
    return db_video

def update_video(db: Session, video_id: int, video: schemas.VideoCreate):
    db_video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if not db_video:
        return None
    
    # FIXED: If updating to featured, un-feature others first
    if video.is_featured and not db_video.is_featured:
        db.query(models.Video).filter(models.Video.is_featured == True).update({"is_featured": False})
        
    for key, value in video.model_dump().items():
        setattr(db_video, key, value)
    _safe_commit(db)
    db.refresh(db_video)
    return db_video

def delete_video(db: Session, video_id: int):
    db_video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if not db_video:
        return False
    db.delete(db_video)
    _safe_commit(db)
    return True

def update_video_views(db: Session, video_id: int):
    video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if video:
        # FIXED: Simple integer increment. No more brittle .replace("K", "000") logic!
        video.views = (video.views or 0) + 1
        _safe_commit(db)
        db.refresh(video)
    return video

# --- Gallery CRUD ---
def get_gallery_images(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.GalleryImage).order_by(models.GalleryImage.order).offset(skip).limit(limit).all()

def create_gallery_image(db: Session, image: schemas.GalleryImageCreate):
    db_image = models.GalleryImage(**image.model_dump())
    db.add(db_image)
    _safe_commit(db)
    db.refresh(db_image)
    return db_image

def update_gallery_image(db: Session, image_id: int, image: schemas.GalleryImageCreate):
    db_image = db.query(models.GalleryImage).filter(models.GalleryImage.id == image_id).first()
    if not db_image:
        return None
    for key, value in image.model_dump().items():
        setattr(db_image, key, value)
    _safe_commit(db)
    db.refresh(db_image)
    return db_image

def delete_gallery_image(db: Session, image_id: int):
    db_image = db.query(models.GalleryImage).filter(models.GalleryImage.id == image_id).first()
    if not db_image:
        return False
    db.delete(db_image)
    _safe_commit(db)
    return True

# --- Product CRUD ---
def get_products(db: Session, skip: int = 0, limit: int = 100, available_only: bool = False):
    query = db.query(models.Product)
    if available_only:
        query = query.filter(models.Product.is_available == True)
    return query.offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    _safe_commit(db)
    db.refresh(db_product)
    return db_product

# --- Newsletter CRUD ---
def create_subscriber(db: Session, email: str):
    subscriber = models.NewsletterSubscriber(email=email)
    db.add(subscriber)
    _safe_commit(db)
    db.refresh(subscriber)
    return subscriber

def get_subscriber_by_email(db: Session, email: str):
    return db.query(models.NewsletterSubscriber).filter(models.NewsletterSubscriber.email == email).first()