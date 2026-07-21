from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from database.database import Base

class Artist(Base):
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    title = Column(String)
    bio = Column(Text)
    followers = Column(Integer, default=0)
    # FIXED: Use func.now() for timezone-aware, DB-native timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tracks = relationship("Track", back_populates="artist")


class Track(Base):
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    track_number = Column(Integer)
    title = Column(String, index=True)
    artist_name = Column(String)
    featured_artist = Column(String, nullable=True)
    year = Column(String, nullable=True)
    # FIXED: Changed from String to Integer to prevent parsing crashes and allow sorting
    streams = Column(Integer, default=0)
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
    # FIXED: Changed from String to Integer for reliable math and sorting
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    duration = Column(String)  # Keep as String (e.g., "5:06")
    is_featured = Column(Boolean, default=False)
    upload_date = Column(String)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GalleryImage(Base):
    __tablename__ = "gallery_images"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    alt_text = Column(String)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    # Note: Storing price as Integer is best practice (representing cents, e.g., 1999 = $19.99)
    price = Column(Integer)
    image_url = Column(String)
    is_available = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now())