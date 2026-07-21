from pydantic import BaseModel, EmailStr, ConfigDict, computed_field
from typing import Optional, List
from datetime import datetime

# --- Helper Functions ---
def format_count(value: int) -> str:
    """Formats an integer into a human-readable string (e.g., 4600 -> '4.6K')."""
    if not isinstance(value, int):
        try:
            value = int(value)
        except (ValueError, TypeError):
            return "0"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M".replace(".0", "")
    if value >= 1_000:
        return f"{value / 1_000:.1f}K".replace(".0", "")
    return str(value)

# --- Admin Schemas ---
# Moved here from routes.py to keep all schemas centralized
class AdminLogin(BaseModel):
    password: str

# --- Artist Schemas ---
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
    
    # FIXED: Updated to Pydantic V2 syntax
    model_config = ConfigDict(from_attributes=True)

# --- Track Schemas ---
class TrackBase(BaseModel):
    track_number: int
    title: str
    artist_name: str
    featured_artist: Optional[str] = None
    year: Optional[str] = None
    streams: int = 0  # FIXED: Changed from str to int for reliable math
    track_type: str = "Single"

class TrackCreate(TrackBase):
    artist_id: int

class TrackResponse(TrackBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

    # Adds a formatted string (e.g., "3.8K") to the JSON response for the frontend
    @computed_field
    @property
    def streams_display(self) -> str:
        return format_count(self.streams)

# --- Video Schemas ---
class VideoBase(BaseModel):
    title: str
    youtube_id: str
    embed_url: str
    category: str
    views: int = 0  # FIXED: Changed from str to int
    likes: int = 0  # FIXED: Changed from str to int
    duration: str
    upload_date: str
    description: Optional[str] = None
    is_featured: bool = False

class VideoCreate(VideoBase):
    pass

class VideoResponse(VideoBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

    # Adds formatted strings to the JSON response for the frontend
    @computed_field
    @property
    def views_display(self) -> str:
        return format_count(self.views)

    @computed_field
    @property
    def likes_display(self) -> str:
        return format_count(self.likes)

# --- Gallery Schemas ---
class GalleryImageBase(BaseModel):
    url: str
    alt_text: str
    order: int = 0

class GalleryImageCreate(GalleryImageBase):
    pass

class GalleryImageResponse(GalleryImageBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Product Schemas ---
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
    
    model_config = ConfigDict(from_attributes=True)

# --- Newsletter Schema ---
class NewsletterSubscribe(BaseModel):
    email: EmailStr

# --- Response Models ---
class VideosResponse(BaseModel):
    videos: List[VideoResponse]
    total: int

class TracksResponse(BaseModel):
    tracks: List[TrackResponse]
    total: int