from fastapi.testclient import TestClient
from PIL import Image, ImageSequence
import io
import os
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
        assert response.headers["content-type"] in [
            "image/jpeg",
            "image/Supported_Filetype.JPEG",
        ]

        # Read the image from the response content
        image = Image.open(io.BytesIO(response.content))

        # Check the size of the image
        assert image.size == (default_img_width, default_img_height)


def test_youtube_thumbnail_all_params():
    for video_id in youtube_example_video_ids:
        for filetype in util.Supported_Filetype:
            response = client.get(
                f"/youtube/{video_id}?width={alt_img_width}&height={alt_img_height}&filetype={filetype.value}"
            )
            assert response.status_code == 200
            assert response.headers["content-type"] in [
                f"image/{filetype.value}",
                f"image/Supported_Filetype.{filetype.capitalize()}",
            ]

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
    assert response.headers["content-type"] in [
        "image/jpeg",
        "image/Supported_Filetype.JPEG",
    ]

    # Read the image from the response content
    image = Image.open(io.BytesIO(response.content))

    # Check the size of the image
    assert image.size == (default_img_width, default_img_height)


def test_vimeo_thumbnail_all_params():
    for filetype in util.Supported_Filetype:
        response = client.get(
            f"/vimeo/{vimeo_example_video_id}?width={alt_img_width}&height={alt_img_height}&filetype={filetype.value}"
        )
        assert response.status_code == 200
        assert response.headers["content-type"] in [
            f"image/{filetype.value}",
            f"image/Supported_Filetype.{filetype.capitalize()}",
        ]

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


# Live checks against the services added in src/providers.py. These hit the
# real services (like the YouTube and Vimeo tests above), so they also catch
# a service changing its thumbnail URLs or blocking our requests.
IMGUR_VIDEO_ID = "A61SaA1"  # a public Imgur video (.mp4)
# A long-lived public video (also used by yt-dlp's TikTok tests). TikTok's own
# oEmbed docs example (@scout2015) no longer exists.
TIKTOK_VIDEO_URL = "https://www.tiktok.com/@hankgreen1/video/7047596209028074758"


def test_imgur_thumbnail_live():
    response = client.get(f"/imgur/{IMGUR_VIDEO_ID}")
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "image/jpeg"
    assert Image.open(io.BytesIO(response.content)).size == (default_img_width, default_img_height)


def test_imgur_missing_video_live():
    response = client.get("/imgur/zzzzzzz")
    assert response.status_code == 404, response.text


def test_tiktok_thumbnail_live():
    response = client.get("/url", params={"url": TIKTOK_VIDEO_URL})
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "image/jpeg"
    assert Image.open(io.BytesIO(response.content)).size == (default_img_width, default_img_height)


# Live checks for Loom, Dailymotion and Streamable, using the example videos
# from each service's own developer documentation.
@pytest.mark.parametrize(
    "path",
    [
        "/loom/0281766fa2d04bb788eaf19e65135184",
        "/dailymotion/x7tgad0",
        "/streamable/moo",
        "/bilibili/BV1GJ411x7h7",  # Rick Astley's "Never Gonna Give You Up" on Bilibili
        "/url?url=https%3A%2F%2Frumble.com%2Fvdmum1-moose-the-dog-helps-girls-dig-a-snow-fort.html",
    ],
)
def test_more_services_live(path):
    response = client.get(path)
    assert response.status_code == 200, response.text
    assert Image.open(io.BytesIO(response.content)).size == (default_img_width, default_img_height)


# Instagram and Facebook need Meta credentials (see the API README). These run
# when they're configured, e.g. as GitHub Actions secrets.
needs_meta = pytest.mark.skipif(
    not (os.getenv("META_ACCESS_TOKEN") or (os.getenv("META_APP_ID") and os.getenv("META_CLIENT_TOKEN"))),
    reason="Meta credentials not configured",
)


# Example videos from yt-dlp's Instagram and Facebook extractor tests
@needs_meta
@pytest.mark.parametrize(
    "url",
    [
        "https://www.instagram.com/reel/Chunk8-jurw/",
        "https://www.facebook.com/cnn/videos/10155529876156509/",
    ],
)
def test_meta_live(url):
    response = client.get("/url", params={"url": url})
    assert response.status_code == 200, response.text


needs_twitch = pytest.mark.skipif(
    not (os.getenv("TWITCH_CLIENT_ID") and os.getenv("TWITCH_CLIENT_SECRET")), reason="Twitch credentials not configured"
)
needs_reddit = pytest.mark.skipif(
    not (os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET")), reason="Reddit credentials not configured"
)


# Example clips/videos/posts from yt-dlp's Twitch and Reddit extractor tests
@needs_twitch
@pytest.mark.parametrize(
    "url", ["https://clips.twitch.tv/FaintLightGullWholeWheat", "https://www.twitch.tv/videos/635475444"]
)
def test_twitch_live(url):
    response = client.get("/url", params={"url": url})
    assert response.status_code == 200, response.text


@needs_reddit
def test_reddit_live():
    response = client.get("/url", params={"url": "https://www.reddit.com/r/videos/comments/6rrwyj/that_small_heart_attack/"})
    assert response.status_code == 200, response.text


# Page preview images. These services may refuse servers outside China or
# behind a bot check; a refusal fails here with a 502 that says so.
@pytest.mark.parametrize(
    "url",
    [
        "https://v.qq.com/x/page/q326831cny0.html",
        "https://www.iqiyi.com/v_19rrojlavg.html",
        "https://www.xiaohongshu.com/explore/6411cf99000000001300b6d9",
    ],
)
def test_page_preview_services_live(url):
    response = client.get("/url", params={"url": url})
    assert response.status_code == 200, response.text
