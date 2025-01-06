from fastapi.testclient import TestClient
from PIL import Image, ImageSequence
import io
import pytest
import urllib

from src import util
from . import data_for_testing
from main import app, get_settings

client = TestClient(app)

youtube_example_video_ids = ("dQw4w9WgXcQ", "fdUpaWd6I_Y")
vimeo_example_video_id = "375468729"

default_img_width = 320
default_img_height = 180
default_gif_frame_duration = 500

alt_img_width = 1920
alt_img_height = 1080
alt_gif_frame_duration = 1000

accepted_content_types = [
    "image/jpeg",
    "image/Supported_Filetype.JPEG",
]


def test_main_response():
    response = client.get("/")
    assert response.status_code == 200


def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc():
    response = client.get("/redoc")
    assert response.status_code == 200


def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "app_name": get_settings().app_name,
        "app_description": get_settings().app_description,
        "contact": get_settings().contact,
        "analytics_api_key": get_settings().analytics_api_key,
    }


def test_youtube_thumbnail_default_params():
    for video_id in youtube_example_video_ids:
        response = client.get(f"/youtube/{video_id}")
        assert response.status_code == 200
        assert response.headers["content-type"] in accepted_content_types

        # Read the image from the response content
        image = Image.open(io.BytesIO(response.content))

        # Check the size of the image
        assert image.size == (default_img_width, default_img_height)


def test_youtube_thumbnail_all_params():
    for video_id in youtube_example_video_ids:
        for filetype in util.Supported_Filetype:
            response = client.get(
                f"/youtube/{video_id}?width={alt_img_width}&height={alt_img_height}&filetype={filetype}"
            )
            assert response.status_code == 200
            assert response.headers["content-type"] == f"image/{filetype}"

            # Read the image from the response content
            image = Image.open(io.BytesIO(response.content))

            # Check the size of the image
            assert image.size == (alt_img_width, alt_img_height)


def test_youtube_gif_thumbnail_default_params():
    for video_id in youtube_example_video_ids:
        response = client.get(f"/youtube/{video_id}.gif")
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


def test_youtube_gif_thumbnail_all_params():
    for video_id in youtube_example_video_ids:
        response = client.get(
            f"/youtube/{video_id}.gif?duration={alt_gif_frame_duration}"
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/gif"

        # Read the image from the response content
        gif = Image.open(io.BytesIO(response.content))

        # check each frame of the gif
        for frame in ImageSequence.Iterator(gif):
            assert frame.size == (default_img_width, default_img_height)
            frame_duration = frame.info.get("duration")  # Check size
            assert frame_duration == pytest.approx(
                alt_gif_frame_duration, abs=1
            )  # Check duration


def test_vimeo_thumbnail_default_params():
    response = client.get(f"/vimeo/{vimeo_example_video_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"

    # Read the image from the response content
    image = Image.open(io.BytesIO(response.content))

    # Check the size of the image
    assert image.size == (default_img_width, default_img_height)


def test_vimeo_thumbnail_all_params():
    for filetype in util.Supported_Filetype:
        response = client.get(
            f"/vimeo/{vimeo_example_video_id}?width={alt_img_width}&height={alt_img_height}&filetype={filetype}"
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == f"image/{filetype}"

        # Read the image from the response content
        image = Image.open(io.BytesIO(response.content))

        # Check the size of the image
        assert image.size == (alt_img_width, alt_img_height)


@pytest.mark.parametrize(
    "url, expected_video_id",
    data_for_testing.active_vimeo_array_url_formats
    + data_for_testing.active_youtube_array_url_formats,
)
def test_url_endpoint(url, expected_video_id):
    # Todo: test if the urls are valid

    # Did we recieve an image?
    parsed_url = urllib.parse.quote(url)
    response = client.get(f"/url?url={parsed_url}")
    assert response.status_code == 200
    assert response.headers["content-type"] in [
        "image/jpeg",
        "image/Supported_Filetype.JPEG",
    ]

    # Read the image from the response content
    image = Image.open(io.BytesIO(response.content))

    # Check the size of the image
    assert image.size == (default_img_width, default_img_height)
