from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta
import re

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Vida Brown API",
    description="YouTube & Spotify Integration",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API keys from environment
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Cache storage
cache = {}
CACHE_DURATION = 300  # 5 minutes

# ============== HELPER FUNCTIONS ==============

def get_cached(key):
    """Get data from cache if not expired"""
    if key in cache:
        data, timestamp = cache[key]
        if datetime.now() - timestamp < timedelta(seconds=CACHE_DURATION):
            return data
    return None

def set_cache(key, data):
    """Set data in cache with timestamp"""
    cache[key] = (data, datetime.now())

def format_number(num):
    """Format number to K, M format"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def parse_iso_duration(duration):
    """Parse ISO 8601 duration to MM:SS format"""
    pattern = re.compile(r'P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration)
    
    if match:
        years, months, days, hours, minutes, seconds = match.groups()
        hours = int(hours or 0)
        minutes = int(minutes or 0)
        seconds = int(seconds or 0)
        
        total_minutes = hours * 60 + minutes
        
        if total_minutes > 0:
            return f"{total_minutes}:{seconds:02d}"
        return f"0:{seconds:02d}"
    
    return "0:00"

def get_spotify_token():
    """Get Spotify access token"""
    cached = get_cached("spotify_token")
    if cached:
        return cached
    
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        token_data = response.json()
        set_cache("spotify_token", token_data["access_token"])
        return token_data["access_token"]
    else:
        raise HTTPException(status_code=500, detail="Failed to get Spotify token")

# ============== YOUTUBE ENDPOINTS ==============

@app.get("/api/youtube/channel")
async def get_youtube_channel():
    """Get YouTube channel info"""
    cached = get_cached("youtube_channel")
    if cached:
        return cached
    
    # VIDA BROWN'S CHANNEL ID - Replace with actual channel ID
    channel_id = "UC_YOUR_CHANNEL_ID"  # TODO: Get from YouTube
    
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": YOUTUBE_API_KEY
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["items"]:
            channel = data["items"][0]
            result = {
                "title": channel["snippet"]["title"],
                "description": channel["snippet"]["description"],
                "thumbnail": channel["snippet"]["thumbnails"]["high"]["url"],
                "subscriberCount": format_number(int(channel["statistics"].get("subscriberCount", 0))),
                "viewCount": format_number(int(channel["statistics"].get("viewCount", 0))),
                "videoCount": channel["statistics"].get("videoCount", 0)
            }
            set_cache("youtube_channel", result)
            return result
    
    raise HTTPException(status_code=404, detail="Channel not found")

@app.get("/api/youtube/videos")
async def get_youtube_videos(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """Get YouTube videos from channel"""
    cache_key = f"youtube_videos_{limit}_{offset}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    # VIDA BROWN'S CHANNEL ID - Replace with actual channel ID
    channel_id = "UC_YOUR_CHANNEL_ID"  # TODO: Get from YouTube
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "order": "date",
        "type": "video",
        "maxResults": limit,
        "key": YOUTUBE_API_KEY
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        videos = []
        
        for item in data["items"][offset:]:
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            
            # Get video statistics
            stats_url = "https://www.googleapis.com/youtube/v3/videos"
            stats_params = {
                "part": "statistics,contentDetails",
                "id": video_id,
                "key": YOUTUBE_API_KEY
            }
            stats_response = requests.get(stats_url, params=stats_params)
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                if stats_data["items"]:
                    stats = stats_data["items"][0]["statistics"]
                    content_details = stats_data["items"][0]["contentDetails"]
                    
                    videos.append({
                        "id": video_id,
                        "title": snippet["title"],
                        "description": snippet["description"],
                        "thumbnail": snippet["thumbnails"]["high"]["url"],
                        "publishedAt": snippet["publishedAt"],
                        "embedUrl": f"https://www.youtube.com/embed/{video_id}",
                        "views": format_number(int(stats.get("viewCount", 0))),
                        "likes": format_number(int(stats.get("likeCount", 0))),
                        "duration": parse_iso_duration(content_details["duration"]),
                        "category": "HIT OR MISS"  # Default category
                    })
        
        result = {"videos": videos, "total": len(videos)}
        set_cache(cache_key, result)
        return result
    
    raise HTTPException(status_code=500, detail="Failed to fetch YouTube videos")

@app.get("/api/videos/featured")
async def get_featured_video():
    """Get most popular video"""
    videos_data = await get_youtube_videos(limit=20)
    videos = videos_data["videos"]
    
    if videos:
        # Sort by views and return the most popular
        def parse_views(view_str):
            return float(view_str.replace("K", "000").replace("M", "000000").replace(".", ""))
        
        sorted_videos = sorted(videos, key=lambda x: parse_views(x["views"]), reverse=True)
        return sorted_videos[0]
    
    raise HTTPException(status_code=404, detail="No videos found")

# ============== SPOTIFY ENDPOINTS ==============

@app.get("/api/spotify/artist")
async def get_spotify_artist():
    """Get Spotify artist info"""
    cached = get_cached("spotify_artist")
    if cached:
        return cached
    
    artist_id = "3ihbWDeubJO4XmeZlCGqZL"  # Vida Brown's Spotify ID
    token = get_spotify_token()
    
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        artist = response.json()
        result = {
            "id": artist["id"],
            "name": artist["name"],
            "genres": artist["genres"],
            "followers": artist["followers"]["total"],
            "popularity": artist["popularity"],
            "images": artist["images"],
            "externalUrls": artist["external_urls"]
        }
        set_cache("spotify_artist", result)
        return result
    
    raise HTTPException(status_code=404, detail="Artist not found")

@app.get("/api/spotify/tracks")
async def get_spotify_tracks(
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """Get artist's top tracks"""
    cache_key = f"spotify_tracks_{limit}_{offset}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    artist_id = "3ihbWDeubJO4XmeZlCGqZL"  # Vida Brown's Spotify ID
    token = get_spotify_token()
    
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    params = {"market": "US"}
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        tracks = []
        
        for idx, track in enumerate(data["tracks"][offset:offset+limit], start=1):
            tracks.append({
                "id": track["id"],
                "trackNumber": idx,
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "duration_ms": track["duration_ms"],
                "popularity": track["popularity"],
                "previewUrl": track["preview_url"],
                "externalUrls": track["external_urls"]
            })
        
        result = {"tracks": tracks, "total": len(tracks)}
        set_cache(cache_key, result)
        return result
    
    raise HTTPException(status_code=500, detail="Failed to fetch tracks")

# ============== COMBINED ENDPOINTS ==============

@app.get("/api/artist/profile")
async def get_artist_profile():
    """Get combined artist profile from YouTube and Spotify"""
    try:
        spotify_data = await get_spotify_artist()
    except:
        spotify_data = {
            "name": "Vida Brown",
            "followers": 0,
            "images": [],
            "externalUrls": {"spotify": "https://open.spotify.com/artist/3ihbWDeubJO4XmeZlCGqZL"}
        }
    
    try:
        youtube_data = await get_youtube_channel()
    except:
        youtube_data = {
            "description": "Malawian artist creating music, arts, and culture content.",
            "thumbnail": "",
            "subscriberCount": "0"
        }
    
    return {
        "name": spotify_data.get("name", "Vida Brown"),
        "title": "Singer • Songwriter • Producer",
        "bio": youtube_data.get("description", "Malawian artist creating music, arts, and culture content."),
        "followers": spotify_data.get("followers", 0),
        "youtubeSubscribers": youtube_data.get("subscriberCount", "0"),
        "images": {
            "spotify": spotify_data.get("images", [{}])[0].get("url") if spotify_data.get("images") else None,
            "youtube": youtube_data.get("thumbnail", "")
        },
        "links": {
            "youtube": "https://www.youtube.com/@VidaBrownOfficial",
            "spotify": spotify_data.get("externalUrls", {}).get("spotify", "https://open.spotify.com/artist/3ihbWDeubJO4XmeZlCGqZL")
        }
    }

# ============== ROOT & HEALTH ==============

@app.get("/")
async def root():
    return {
        "message": "Vida Brown API - YouTube & Spotify Integration",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "artist_profile": "/api/artist/profile",
            "youtube_videos": "/api/youtube/videos",
            "featured_video": "/api/videos/featured",
            "spotify_tracks": "/api/spotify/tracks"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_size": len(cache)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)