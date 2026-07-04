from sqlalchemy.orm import Session
from sqlalchemy import func
from models import models
from schemas import schemas
from typing import List, Optional

# Artist CRUD
def get_artist(db: Session, artist_id: int):
    return db.query(models.Artist).filter(models.Artist.id == artist_id).first()

def get_artist_by_name(db: Session, name: str):
    return db.query(models.Artist).filter(models.Artist.name == name).first()

def create_artist(db: Session, artist: schemas.ArtistCreate):
    db_artist = models.Artist(**artist.model_dump())
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist

# Track CRUD
def get_tracks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Track).order_by(models.Track.track_number).offset(skip).limit(limit).all()

def get_track_count(db: Session):
    return db.query(func.count(models.Track.id)).scalar()

def create_track(db: Session, track: schemas.TrackCreate):
    db_track = models.Track(**track.model_dump())
    db.add(db_track)
    db.commit()
    db.refresh(db_track)
    return db_track

# Video CRUD
def get_videos(db: Session, skip: int = 0, limit: int = 100, category: Optional[str] = None):
    query = db.query(models.Video)
    if category:
        query = query.filter(models.Video.category == category)
    return query.order_by(models.Video.created_at.desc()).offset(skip).limit(limit).all()

def get_featured_video(db: Session):
    return db.query(models.Video).filter(models.Video.is_featured == True).first()

def get_video_count(db: Session, category: Optional[str] = None):
    query = db.query(func.count(models.Video.id))
    if category:
        query = query.filter(models.Video.category == category)
    return query.scalar()

def create_video(db: Session, video: schemas.VideoCreate):
    db_video = models.Video(**video.model_dump())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def update_video_views(db: Session, video_id: int):
    video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if video:
        # Simple increment - in production, parse and increment properly
        current_views = int(video.views.replace("K", "000").replace("M", "000000").replace(".", ""))
        video.views = str(current_views + 1)
        db.commit()
        db.refresh(video)
    return video

# Gallery CRUD
def get_gallery_images(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.GalleryImage).order_by(models.GalleryImage.order).offset(skip).limit(limit).all()

def create_gallery_image(db: Session, image: schemas.GalleryImageCreate):
    db_image = models.GalleryImage(**image.model_dump())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# Product CRUD
def get_products(db: Session, skip: int = 0, limit: int = 100, available_only: bool = False):
    query = db.query(models.Product)
    if available_only:
        query = query.filter(models.Product.is_available == True)
    return query.offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Newsletter CRUD
def create_subscriber(db: Session, email: str):
    subscriber = models.NewsletterSubscriber(email=email)
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber

def get_subscriber_by_email(db: Session, email: str):
    return db.query(models.NewsletterSubscriber).filter(models.NewsletterSubscriber.email == email).first()