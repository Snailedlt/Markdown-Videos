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

@pytest.mark.parametrize(
    "url, expected",
    [
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


@pytest.mark.parametrize("status", [401, 403, 429, 500, 503])
def test_refusals_and_outages_are_a_502_not_a_404(upstream, status):
    routes, _ = upstream
    routes["https://i.imgur.com/"] = FakeResponse(status=status)
    response = client.get("/imgur/A61SaA1")
    assert response.status_code == 502
    assert f"Couldn't get a thumbnail from Imgur right now (Imgur answered {status})" in response.json()["detail"]
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


# --- Loom, Dailymotion, Streamable -------------------------------------------------

LOOM_ID = "0281766fa2d04bb788eaf19e65135184"


@pytest.mark.parametrize(
    "url, expected",
    [
        (f"https://www.loom.com/share/{LOOM_ID}", ("loom", LOOM_ID)),
        (f"https://www.loom.com/share/My-demo-video-{LOOM_ID}?sid=abc", ("loom", LOOM_ID)),
        (f"loom.com/embed/{LOOM_ID}", ("loom", LOOM_ID)),
        ("https://www.dailymotion.com/video/x7tgad0", ("dailymotion", "x7tgad0")),
        ("https://www.dailymotion.com/video/x7tgad0_some-title", ("dailymotion", "x7tgad0")),
        ("https://dai.ly/x7tgad0", ("dailymotion", "x7tgad0")),
        ("https://www.dailymotion.com/embed/video/x7tgad0?autoplay=1", ("dailymotion", "x7tgad0")),
        ("https://geo.dailymotion.com/player/xabc1.html?video=x7tgad0", ("dailymotion", "x7tgad0")),
        ("https://streamable.com/moo", ("streamable", "moo")),
        ("https://streamable.com/e/moo?autoplay=1", ("streamable", "moo")),
    ],
)
def test_recognises_more_links(url, expected):
    provider, ref = providers.match(url)
    assert (provider.key, ref) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://www.loom.com/share/abc",
        "https://www.loom.com/looms/videos",
        "https://www.dailymotion.com/user/someone",
        "https://streamable.com/login",
        "https://streamable.com/upload",
        "https://streamable.com/",
    ],
)
def test_ignores_more_non_video_links(url):
    assert providers.match(url) is None


def test_loom_thumbnail(upstream):
    routes, calls = upstream
    routes["https://www.loom.com/v1/oembed"] = FakeResponse(
        data={"thumbnail_url": f"https://cdn.loom.com/sessions/thumbnails/{LOOM_ID}-00001.gif"}
    )
    routes["https://cdn.loom.com/"] = FakeResponse(content=jpeg((1280, 720)))
    response = client.get(f"/loom/{LOOM_ID}")
    assert response.status_code == 200
    assert calls[0] == (
        "https://www.loom.com/v1/oembed?url=https%3A%2F%2Fwww.loom.com%2Fshare%2F"
        f"{LOOM_ID}&format=json"
    )


def test_dailymotion_thumbnail(upstream):
    routes, calls = upstream
    routes["https://api.dailymotion.com/video/x7tgad0"] = FakeResponse(
        data={"thumbnail_720_url": "https://s1.dmcdn.net/v/abc/x720"}
    )
    routes["https://s1.dmcdn.net/"] = FakeResponse(content=jpeg((1280, 720)))
    response = client.get("/url", params={"url": "https://dai.ly/x7tgad0"})
    assert response.status_code == 200
    assert calls == [
        "https://api.dailymotion.com/video/x7tgad0?fields=thumbnail_720_url",
        "https://s1.dmcdn.net/v/abc/x720",
    ]


def test_missing_dailymotion_video_is_a_404(upstream):
    routes, _ = upstream
    routes["https://api.dailymotion.com/"] = FakeResponse(status=404, data={"error": {"code": 404}})
    response = client.get("/dailymotion/xmissing1")
    assert response.status_code == 404
    assert "No Dailymotion video found" in response.json()["detail"]


def test_streamable_thumbnail_with_protocol_relative_url(upstream):
    routes, calls = upstream
    routes["https://api.streamable.com/oembed.json"] = FakeResponse(
        data={"thumbnail_url": "//cdn-cf-east.streamable.com/image/moo.jpg?Expires=1"}
    )
    routes["https://cdn-cf-east.streamable.com/"] = FakeResponse(content=jpeg((1280, 720)))
    response = client.get("/streamable/moo?width=640&height=360")
    assert response.status_code == 200
    assert Image.open(io.BytesIO(response.content)).size == (640, 360)
    assert calls[1] == "https://cdn-cf-east.streamable.com/image/moo.jpg?Expires=1"


@pytest.mark.parametrize(
    "path", ["/loom/not-hex", "/dailymotion/7tgad0", "/streamable/has-dash"]
)
def test_malformed_ids_are_rejected(path):
    assert client.get(path).status_code == 422


# --- Rumble ---------------------------------------------------------------------

RUMBLE = "https://rumble.com/vdmum1-moose-the-dog-helps-girls-dig-a-snow-fort.html"


@pytest.mark.parametrize(
    "url, expected",
    [
        (RUMBLE, ("rumble", RUMBLE)),
        (RUMBLE + "?e9s=src_v1_upp", ("rumble", RUMBLE)),
    ],
)
def test_recognises_rumble(url, expected):
    provider, ref = providers.match(url)
    assert (provider.key, ref) == expected


@pytest.mark.parametrize("url", ["https://rumble.com/c/SomeChannel", "https://rumble.com/user/someone"])
def test_ignores_rumble_pages(url):
    assert providers.match(url) is None


def test_rumble_thumbnail_through_oembed(upstream):
    routes, calls = upstream
    routes["https://rumble.com/api/Media/oembed.json"] = FakeResponse(
        data={"thumbnail_url": "https://sp.rmbl.ws/s8/1/a/b/c/d/x.OvCc.1.jpg"}
    )
    routes["https://sp.rmbl.ws/"] = FakeResponse(content=jpeg((1280, 720)))
    response = client.get("/url", params={"url": RUMBLE})
    assert response.status_code == 200
    assert calls[0].startswith("https://rumble.com/api/Media/oembed.json?url=https%3A%2F%2Frumble.com%2Fvdmum1-")


def test_rumble_has_no_id_route():
    assert client.get("/rumble/vdmum1").status_code == 404


# --- Instagram, Facebook (Meta Graph API; need credentials) -------------------------


@pytest.fixture
def meta_credentials(monkeypatch):
    from src import config

    monkeypatch.setattr(config.settings, "meta_app_id", "123")
    monkeypatch.setattr(config.settings, "meta_client_token", "abc")
    monkeypatch.setattr(config.settings, "meta_access_token", "")


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://www.instagram.com/p/C1a2B3c4D5e/", ("instagram", "C1a2B3c4D5e")),
        ("https://www.instagram.com/reel/C1a2B3c4D5e/?igsh=abc", ("instagram", "C1a2B3c4D5e")),
        ("https://instagram.com/someuser/reel/C1a2B3c4D5e", ("instagram", "C1a2B3c4D5e")),
        ("https://www.facebook.com/SomePage/videos/1234567890123456/", ("facebook", "1234567890123456")),
        ("https://www.facebook.com/watch/?v=1234567890123456", ("facebook", "1234567890123456")),
        ("https://www.facebook.com/reel/1234567890123456", ("facebook", "1234567890123456")),
    ],
)
def test_recognises_meta_links(url, expected):
    provider, ref = providers.match(url)
    assert (provider.key, ref) == expected


@pytest.mark.parametrize("url", ["https://www.instagram.com/someuser/", "https://www.facebook.com/SomePage"])
def test_ignores_meta_profiles(url):
    assert providers.match(url) is None


@pytest.mark.parametrize("path", ["/instagram/C1a2B3c4D5e", "/facebook/1234567890123456"])
def test_meta_services_say_when_they_are_not_set_up(upstream, monkeypatch, path):
    from src import config

    for name in ("meta_app_id", "meta_client_token", "meta_access_token"):
        monkeypatch.setattr(config.settings, name, "")
    routes, calls = upstream
    response = client.get(path)
    assert response.status_code == 501
    assert "META_APP_ID and META_CLIENT_TOKEN" in response.json()["detail"]
    assert "cache-control" not in response.headers
    assert calls == []  # nothing was requested from Meta


def test_instagram_thumbnail(upstream, meta_credentials):
    routes, calls = upstream
    routes["https://graph.facebook.com/instagram_oembed"] = FakeResponse(
        data={"thumbnail_url": "https://scontent.cdninstagram.com/v/t51/x.jpg?stp=1"}
    )
    routes["https://scontent.cdninstagram.com/"] = FakeResponse(content=jpeg((640, 1136)))
    response = client.get("/url", params={"url": "https://www.instagram.com/reel/C1a2B3c4D5e/"})
    assert response.status_code == 200
    assert calls[0] == (
        "https://graph.facebook.com/instagram_oembed?url=https%3A%2F%2Fwww.instagram.com%2Fp%2FC1a2B3c4D5e%2F"
        "&fields=thumbnail_url&access_token=123%7Cabc"
    )


def test_facebook_thumbnail_uses_an_access_token_when_given(upstream, monkeypatch):
    from src import config

    monkeypatch.setattr(config.settings, "meta_access_token", "EAAG-token")
    routes, calls = upstream
    routes["https://graph.facebook.com/1234567890123456"] = FakeResponse(data={"picture": "https://scontent.xx.fbcdn.net/p.jpg"})
    routes["https://scontent.xx.fbcdn.net/"] = FakeResponse(content=jpeg((1280, 720)))
    assert client.get("/facebook/1234567890123456").status_code == 200
    assert calls[0] == "https://graph.facebook.com/1234567890123456?fields=picture&access_token=EAAG-token"


@pytest.mark.parametrize(
    "status, code, expected",
    [(400, 100, 404), (404, 803, 404), (400, 190, 502), (403, 200, 502), (400, 4, 502), (500, 1, 502)],
)
def test_meta_errors(upstream, meta_credentials, status, code, expected):
    routes, _ = upstream
    routes["https://graph.facebook.com/"] = FakeResponse(status=status, data={"error": {"code": code}})
    assert client.get("/instagram/C1a2B3c4D5e").status_code == expected
