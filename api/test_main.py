from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

youtube_example_video_id = "dQw4w9WgXcQ"
vimeo_example_video_id = "375468729"


def test_main_response():
    response = client.get("/")
    assert response.status_code == 200


def test_youtube_thumbnail():
    response = client.get(f'/youtube/{youtube_example_video_id}')
    assert response.status_code == 200


def test_youtube_gif_thumbnail():
    response = client.get(f'/youtube/{youtube_example_video_id}.gif')
    assert response.status_code == 200


def test_vimeo_thumbnail():
    response = client.get(f'/vimeo/{vimeo_example_video_id}')
    assert response.status_code == 200
