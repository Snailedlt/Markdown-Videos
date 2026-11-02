"""Endpoint tests that don't touch the network: thumbnail downloads are stubbed."""

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageSequence

import main
from src import util

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def fake_downloads(monkeypatch):
    calls = []

    def fake_read_img_from_url(url, alt_url=None):
        calls.append(url)
        # A different colour per download, so GIF frames aren't merged as duplicates
        return Image.new("RGB", (1280, 720), (40 * len(calls) % 256, 30, 40))

    monkeypatch.setattr(util, "read_img_from_url", fake_read_img_from_url)
    return calls


@pytest.mark.parametrize(
    "path",
    [
        "/youtube/dQw4w9WgXcQ",
        "/youtube/dQw4w9WgXcQ.gif",
        "/vimeo/76979871",
        "/url?url=https%3A%2F%2Fyoutu.be%2FdQw4w9WgXcQ",
    ],
)
def test_images_are_cacheable(path):
    response = client.get(path)
    assert response.status_code == 200
    assert response.headers["cache-control"] == main.CACHE_CONTROL
    assert "s-maxage=" in response.headers["cache-control"]


@pytest.mark.parametrize("filetype", ["jpeg", "png", "webp", "gif"])
def test_content_type_and_size(filetype):
    response = client.get(f"/youtube/dQw4w9WgXcQ?width=640&height=360&filetype={filetype}")
    assert response.status_code == 200
    assert response.headers["content-type"] == f"image/{filetype}"
    assert Image.open(io.BytesIO(response.content)).size == (640, 360)


def test_gif_has_all_frames(fake_downloads):
    response = client.get("/youtube/dQw4w9WgXcQ.gif?width=480&height=270&duration=300")
    assert response.status_code == 200
    gif = Image.open(io.BytesIO(response.content))
    frames = list(ImageSequence.Iterator(gif))
    assert len(frames) == main.GIF_FRAMES
    assert all(frame.size == (480, 270) for frame in frames)
    assert len(fake_downloads) == main.GIF_FRAMES


@pytest.mark.parametrize(
    "path",
    [
        f"/youtube/dQw4w9WgXcQ?width={main.MAX_WIDTH + 1}",
        f"/youtube/dQw4w9WgXcQ?height={main.MAX_HEIGHT + 1}",
        "/youtube/dQw4w9WgXcQ?width=0",
        "/youtube/dQw4w9WgXcQ.gif?duration=5",
    ],
)
def test_out_of_range_params_are_rejected(path):
    assert client.get(path).status_code == 422


def test_invalid_url_is_a_400_and_not_cached():
    response = client.get("/url?url=https%3A%2F%2Fexample.com%2Fvideo")
    assert response.status_code == 400
    assert "cache-control" not in response.headers


def test_tiny_thumbnails_work():
    response = client.get("/youtube/dQw4w9WgXcQ?width=4&height=3")
    assert response.status_code == 200
