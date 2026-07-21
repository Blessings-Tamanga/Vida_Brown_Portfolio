import os
import time
from fastapi.testclient import TestClient
from main import app

# FIXED: Ensure environment variables are set for tests so the strict auth checks don't throw 500 errors
os.environ.setdefault("ADMIN_TOKEN", "devtoken")
os.environ.setdefault("ADMIN_PASSWORD", "devpass")

client = TestClient(app)


def test_artist_profile_endpoint():
    response = client.get('/api/artist/profile')
    assert response.status_code == 200
    body = response.json()
    assert body['name'] == 'Vida Brown'
    assert 'followers' in body


def test_videos_endpoint():
    response = client.get('/api/videos?limit=3')
    assert response.status_code == 200
    body = response.json()
    assert 'videos' in body
    assert 'total' in body


def test_get_video_by_id_endpoint():
    # First, get the list of videos to find a valid ID
    list_resp = client.get('/api/videos?limit=1')
    assert list_resp.status_code == 200
    videos = list_resp.json().get('videos', [])
    
    if videos:
        video_id = videos[0]['id']
        # FIXED: Test the endpoint we just fixed in routes.py
        response = client.get(f'/api/videos/{video_id}')
        assert response.status_code == 200
        assert response.json()['id'] == video_id
    else:
        # If no videos exist, test that a fake ID returns 404
        response = client.get('/api/videos/99999')
        assert response.status_code == 404


def test_admin_login():
    payload = {"password": "devpass"}
    response = client.post('/api/admin/login', json=payload)
    assert response.status_code == 200
    body = response.json()
    assert 'token' in body
    assert body['token'] == 'devtoken'


def test_admin_create_video():
    headers = {"X-Admin-Token": "devtoken"}
    unique = str(int(time.time() * 1000))
    payload = {
        "title": "Automated Test Video",
        "youtube_id": f"TEST{unique}",
        "embed_url": f"https://www.youtube.com/embed/TEST{unique}",
        "category": "TEST",
        "views": 0,          # FIXED: Send as integer
        "likes": 0,          # FIXED: Send as integer
        "duration": "1:00",
        "upload_date": "Jul 2026",
        "description": "Created by automated test",
        "is_featured": False
    }
    response = client.post('/api/admin/videos', json=payload, headers=headers)
    # FastAPI returns 200 for successful POST with response_model, but 201 is also acceptable
    assert response.status_code in (200, 201)
    body = response.json()
    assert body['title'] == payload['title']
    assert body['youtube_id'] == payload['youtube_id']


def test_admin_create_track():
    headers = {"X-Admin-Token": "devtoken"}
    
    # Ensure artist exists to get a valid artist_id
    artist_resp = client.get('/api/artist/profile')
    assert artist_resp.status_code == 200
    artist = artist_resp.json()
    
    unique = str(int(time.time() * 1000))
    payload = {
        "track_number": 99,
        "title": f"Automated Test Track {unique}",
        "artist_name": artist['name'],
        "featured_artist": None,
        "year": "2026",
        "streams": 0,        # FIXED: Changed from "0" (string) to 0 (integer)
        "track_type": "Single",
        "artist_id": artist['id']
    }
    response = client.post('/api/admin/tracks', json=payload, headers=headers)
    assert response.status_code in (200, 201)
    body = response.json()
    assert body['title'] == payload['title']
    assert body['streams'] == 0
    # Verify the computed field is present in the response
    assert 'streams_display' in body
    assert body['streams_display'] == "0"