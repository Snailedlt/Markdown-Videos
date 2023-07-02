from fastapi.testclient import TestClient
from PIL import Image, ImageSequence
import io

import pytest

from .main import app

client = TestClient(app)

youtube_example_video_id = "dQw4w9WgXcQ"
vimeo_example_video_id = "375468729"
default_img_width = 320
default_img_height = 180
default_gif_frame_duration = 500

alt_img_width = 1920
alt_img_height = 1080
alt_gif_frame_duration = 1000


def test_main_response():
    response = client.get("/")
    assert response.status_code == 200


def test_youtube_thumbnail_default_params():
    response = client.get(f"/youtube/{youtube_example_video_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    # Read the image from the response content
    image = Image.open(io.BytesIO(response.content))

    # Check the size of the image
    assert image.size == (default_img_width, default_img_height)


def test_youtube_thumbnail_size_params():
    response = client.get(
        f"/youtube/{youtube_example_video_id}?width={alt_img_width}&height={alt_img_height}"
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    # Read the image from the response content
    image = Image.open(io.BytesIO(response.content))

    # Check the size of the image
    assert image.size == (alt_img_width, alt_img_height)


def test_youtube_gif_thumbnail_default_params():
    response = client.get(f"/youtube/{youtube_example_video_id}.gif")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/gif"

    # Read the image from the response content
    gif = Image.open(io.BytesIO(response.content))

    # check each frame of the gif
    for frame in ImageSequence.Iterator(gif):
        assert frame.size == (default_img_width, default_img_height)
        frame_duration = frame.info.get("duration")  # Check size
        assert frame_duration == pytest.approx(
            default_gif_frame_duration, abs=1
        )  # Check duration


def test_youtube_gif_thumbnail_size_and_duration_params():
    response = client.get(f"/youtube/{youtube_example_video_id}.gif?")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/gif"

    # Read the image from the response content
    gif = Image.open(io.BytesIO(response.content))

    # check each frame of the gif
    for frame in ImageSequence.Iterator(gif):
        assert frame.size == (default_img_width, default_img_height)
        frame_duration = frame.info.get("duration")  # Check size
        assert frame_duration == pytest.approx(
            default_gif_frame_duration, abs=1
        )  # Check duration


def test_vimeo_thumbnail_default_params():
    response = client.get(f"/vimeo/{vimeo_example_video_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    # Read the image from the response content
    image = Image.open(io.BytesIO(response.content))

    # Check the size of the image
    assert image.size == (default_img_width, default_img_height)


def test_vimeo_thumbnail_size_params():
    response = client.get(
        f"/vimeo/{vimeo_example_video_id}?width={alt_img_width}&height={alt_img_height}"
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    # Read the image from the response content
    image = Image.open(io.BytesIO(response.content))

    # Check the size of the image
    assert image.size == (alt_img_width, alt_img_height)
