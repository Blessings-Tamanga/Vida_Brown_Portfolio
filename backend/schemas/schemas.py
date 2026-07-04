from pydantic import BaseModel, HttpUrl, EmailStr
from typing import Optional, List
from datetime import datetime

# Artist Schemas
class ArtistBase(BaseModel):
    name: str
    title: str
    bio: str
    followers: int = 0

class ArtistCreate(ArtistBase):
    pass

class ArtistResponse(ArtistBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Track Schemas
class TrackBase(BaseModel):
    track_number: int
    title: str
    artist_name: str
    featured_artist: Optional[str] = None
    year: Optional[str] = None
    streams: str = "0"
    track_type: str = "Single"

class TrackCreate(TrackBase):
    artist_id: int

class TrackResponse(TrackBase):
    id: int
    
    class Config:
        from_attributes = True

# Video Schemas
class VideoBase(BaseModel):
    title: str
    youtube_id: str
    embed_url: str
    category: str
    views: str = "0"
    likes: str = "0"
    duration: str
    upload_date: str
    description: Optional[str] = None
    is_featured: bool = False

class VideoCreate(VideoBase):
    pass

class VideoResponse(VideoBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Gallery Schemas
class GalleryImageBase(BaseModel):
    url: str
    alt_text: str
    order: int = 0

class GalleryImageCreate(GalleryImageBase):
    pass

class GalleryImageResponse(GalleryImageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    is_available: bool = False

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Newsletter Schema
class NewsletterSubscribe(BaseModel):
    email: EmailStr

# Response Models
class VideosResponse(BaseModel):
    videos: List[VideoResponse]
    total: int

class TracksResponse(BaseModel):
    tracks: List[TrackResponse]
    total: int