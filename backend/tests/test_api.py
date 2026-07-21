from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_artist_profile_endpoint():
    response = client.get('/api/artist/profile')
    assert response.status_code == 200
    body = response.json()
    assert body['name'] == 'Vida Brown'


def test_videos_endpoint():
    response = client.get('/api/videos?limit=3')
    assert response.status_code == 200
    body = response.json()
    assert 'videos' in body
    assert body['total'] >= 1


def test_admin_create_video():
    # use default dev token from env in code
    headers = {"X-Admin-Token": "devtoken"}
    import time
    unique = str(int(time.time() * 1000))
    payload = {
        "title": "Automated Test Video",
        "youtube_id": f"TEST{unique}",
        "embed_url": f"https://www.youtube.com/embed/TEST{unique}",
        "category": "TEST",
        "duration": "1:00",
        "upload_date": "Jul 2026",
        "description": "Created by automated test"
    }
    response = client.post('/api/admin/videos', json=payload, headers=headers)
    assert response.status_code == 200 or response.status_code == 201
    body = response.json()
    assert body['title'] == payload['title']


def test_admin_create_track():
    # create a track linked to the seeded artist
    headers = {"X-Admin-Token": "devtoken"}
    artist_resp = client.get('/api/artist/profile')
    assert artist_resp.status_code == 200
    artist = artist_resp.json()
    payload = {
        "track_number": 99,
        "title": "Automated Test Track",
        "artist_name": artist['name'],
        "featured_artist": None,
        "year": "2026",
        "streams": "0",
        "track_type": "Single",
        "artist_id": artist['id']
    }
    response = client.post('/api/admin/tracks', json=payload, headers=headers)
    assert response.status_code == 200 or response.status_code == 201
    body = response.json()
    assert body['title'] == payload['title']
