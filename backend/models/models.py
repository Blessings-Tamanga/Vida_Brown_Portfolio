from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base

class Artist(Base):
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    title = Column(String)
    bio = Column(Text)
    followers = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tracks = relationship("Track", back_populates="artist")

class Track(Base):
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    track_number = Column(Integer)
    title = Column(String, index=True)
    artist_name = Column(String)
    featured_artist = Column(String, nullable=True)
    year = Column(String, nullable=True)
    streams = Column(String, default="0")
    track_type = Column(String, default="Single")  # Single, Album, EP
    artist_id = Column(Integer, ForeignKey("artists.id"))
    
    artist = relationship("Artist", back_populates="tracks")

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    youtube_id = Column(String, unique=True, index=True)
    embed_url = Column(String)
    category = Column(String)  # "HIT OR MISS", "REACTION", "MALAWI MUSIC"
    views = Column(String, default="0")
    likes = Column(String, default="0")
    duration = Column(String)
    is_featured = Column(Boolean, default=False)
    upload_date = Column(String)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class GalleryImage(Base):
    __tablename__ = "gallery_images"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    alt_text = Column(String)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Integer)
    image_url = Column(String)
    is_available = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)