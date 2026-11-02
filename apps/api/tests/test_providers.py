"""Tests for the extra video services (src/providers.py) that don't need the network."""

import io
import json

import pytest
from fastapi.testclient import TestClient
from PIL import Image

import main
from src import providers

client = TestClient(main.app)


def jpeg(size, color=(200, 40, 60)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="JPEG")
    return buffer.getvalue()


class FakeResponse:
    def __init__(self, status=200, content=b"", data=None, url="", redirect=False):
        self.status_code = status
        self.content = content if data is None else json.dumps(data).encode()
        self._data = data
        self.url = url
        self.is_redirect = redirect

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


@pytest.fixture
def upstream(monkeypatch):
    """Map URL prefixes to fake responses; records every request."""
    routes = {}
    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        for prefix, response in routes.items():
            if url.startswith(prefix):
                return response(url) if callable(response) else response
        return FakeResponse(status=404)

    monkeypatch.setattr(providers, "_get", fake_get)
    return routes, calls


# --- Recognising links ----------------------------------------------------------

TIKTOK = "https://www.tiktok.com/@scout2015/video/6718335390845095173"


@pytest.mark.parametrize(
    "url, expected",
    [
        (TIKTOK, ("tiktok", TIKTOK)),
        (TIKTOK + "?is_from_webapp=1&sender_device=pc", ("tiktok", TIKTOK)),
        ("tiktok.com/@scout2015/video/6718335390845095173", ("tiktok", TIKTOK)),
        ("https://m.tiktok.com/@scout2015/video/6718335390845095173", ("tiktok", TIKTOK)),
        ("https://vm.tiktok.com/ZMabcdEfG/", ("tiktok", "https://vm.tiktok.com/ZMabcdEfG/")),
        ("https://www.tiktok.com/t/ZT8abcdEf/", ("tiktok", "https://www.tiktok.com/t/ZT8abcdEf/")),
        ("https://i.imgur.com/A61SaA1.mp4", ("imgur", "A61SaA1")),
        ("https://i.imgur.com/A61SaA1.gifv", ("imgur", "A61SaA1")),
        ("i.imgur.com/A61SaA1.gif", ("imgur", "A61SaA1")),
        ("https://imgur.com/A61SaA1", ("imgur", "A61SaA1")),
        ("https://imgur.com/A61SaA1?ref=share", ("imgur", "A61SaA1")),
    ],
)
def test_recognises_links(url, expected):
    provider, ref = providers.match(url)
    assert (provider.key, ref) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://youtu.be/dQw4w9WgXcQ",
        "https://vimeo.com/76979871",
        "https://www.tiktok.com/@scout2015",
        "https://www.tiktok.com/@scout2015/video/67183353",  # half-typed
        "https://imgur.com/a/AbCdE12",
        "https://imgur.com/gallery/some-title-AbCdE12",
        "https://imgur.com/user/someone",
        "https://example.com/A61SaA1.mp4",
    ],
)
def test_ignores_other_links(url):
    assert providers.match(url) is None


# --- Imgur ----------------------------------------------------------------------


def test_imgur_thumbnail(upstream):
    routes, calls = upstream
    routes["https://i.imgur.com/A61SaA1h.jpg"] = FakeResponse(content=jpeg((1024, 436)))

    response = client.get("/imgur/A61SaA1?width=640&height=360")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.headers["cache-control"] == main.CACHE_CONTROL
    assert Image.open(io.BytesIO(response.content)).size == (640, 360)
    assert calls == ["https://i.imgur.com/A61SaA1h.jpg"]


def test_imgur_through_url_endpoint(upstream):
    routes, _ = upstream
    routes["https://i.imgur.com/A61SaA1h.jpg"] = FakeResponse(content=jpeg((1024, 436)))
    response = client.get("/url", params={"url": "https://i.imgur.com/A61SaA1.mp4", "filetype": "png"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_removed_imgur_post_is_a_404_not_a_placeholder(upstream):
    routes, _ = upstream
    # Imgur redirects missing images to its "removed" placeholder
    routes["https://i.imgur.com/"] = FakeResponse(status=302, redirect=True)
    response = client.get("/imgur/Missing1")
    assert response.status_code == 404
    assert "No Imgur video found" in response.json()["detail"]
    assert "cache-control" not in response.headers


def test_upstream_failures_are_a_502(upstream):
    routes, _ = upstream
    routes["https://i.imgur.com/"] = FakeResponse(status=429)
    response = client.get("/imgur/A61SaA1")
    assert response.status_code == 502
    assert "Couldn't get a thumbnail from Imgur" in response.json()["detail"]
    assert "cache-control" not in response.headers


def test_imgur_is_requested_with_a_user_agent(monkeypatch):
    seen = {}

    def fake_get(url, **kwargs):
        seen.update(kwargs)
        return FakeResponse(content=jpeg((1024, 436)))

    monkeypatch.setattr(providers, "_get", fake_get)
    assert client.get("/imgur/A61SaA1").status_code == 200
    assert "Markdown-Videos" in seen["headers"]["User-Agent"]
    assert seen["allow_redirects"] is False


@pytest.mark.parametrize("video_id", ["ab", "has-dash", "waytoolongid123"])
def test_imgur_rejects_malformed_ids(video_id):
    assert client.get(f"/imgur/{video_id}").status_code == 422


# --- TikTok ---------------------------------------------------------------------


def test_tiktok_through_url_endpoint(upstream):
    routes, calls = upstream
    routes["https://www.tiktok.com/oembed"] = FakeResponse(
        data={"thumbnail_url": "https://p16-sign.tiktokcdn.com/obj/cover.jpeg?x=1"}
    )
    routes["https://p16-sign.tiktokcdn.com/"] = FakeResponse(content=jpeg((576, 1024)))

    response = client.get("/url", params={"url": TIKTOK + "?is_from_webapp=1"})
    assert response.status_code == 200
    assert Image.open(io.BytesIO(response.content)).size == (320, 180)
    assert calls[0] == (
        "https://www.tiktok.com/oembed?url="
        "https%3A%2F%2Fwww.tiktok.com%2F%40scout2015%2Fvideo%2F6718335390845095173&format=json"
    )
    assert calls[1] == "https://p16-sign.tiktokcdn.com/obj/cover.jpeg?x=1"


def test_tiktok_short_links_are_resolved(upstream):
    routes, calls = upstream
    routes["https://vm.tiktok.com/"] = FakeResponse(url=TIKTOK + "?_r=1")
    routes["https://www.tiktok.com/oembed"] = FakeResponse(data={"thumbnail_url": "//cdn.example.test/c.jpg"})
    routes["https://cdn.example.test/"] = FakeResponse(content=jpeg((576, 1024)))

    response = client.get("/url", params={"url": "https://vm.tiktok.com/ZMabcdEfG/"})
    assert response.status_code == 200
    assert "url=https%3A%2F%2Fwww.tiktok.com%2F%40scout2015%2Fvideo%2F6718335390845095173" in calls[1]
    assert calls[2] == "https://cdn.example.test/c.jpg"  # protocol-relative URL made absolute


def test_missing_tiktok_is_a_404(upstream):
    routes, _ = upstream
    routes["https://www.tiktok.com/oembed"] = FakeResponse(status=400, data={"code": 400})
    response = client.get("/url", params={"url": TIKTOK})
    assert response.status_code == 404
    assert "No TikTok video found" in response.json()["detail"]


def test_tiktok_has_no_id_route():
    assert client.get("/tiktok/6718335390845095173").status_code == 404


def test_unsupported_link_lists_the_supported_services():
    response = client.get("/url", params={"url": "https://example.com/video"})
    assert response.status_code == 400
    assert "TikTok" in response.json()["detail"] and "Imgur" in response.json()["detail"]


# --- Drawing --------------------------------------------------------------------


def test_fit_frame_crops_similar_shapes():
    out = providers.fit_frame(Image.new("RGB", (1280, 720), (10, 200, 10)), 320, 180)
    assert out.size == (320, 180)
    assert out.getpixel((5, 5)) == out.getpixel((160, 90))  # no bars


def test_fit_frame_puts_vertical_video_on_a_blurred_background():
    frame = Image.new("RGB", (576, 1024), (240, 240, 240))
    out = providers.fit_frame(frame, 320, 180)
    assert out.size == (320, 180)
    # The whole frame is visible in the middle; the sides are a darkened copy
    centre, side = out.getpixel((160, 90)), out.getpixel((5, 90))
    assert sum(centre) > sum(side) + 150


def test_play_button_is_drawn_in_the_service_colour():
    button = providers.play_button((27, 183, 110), (68, 48))
    assert button.size == (68, 48) and button.mode == "RGBA"
    r, g, b, a = button.getpixel((6, 24))
    assert (r, g, b) == pytest.approx((27, 183, 110), abs=3) and a > 200
    assert button.getpixel((36, 24))[:3] == (255, 255, 255)  # the triangle
