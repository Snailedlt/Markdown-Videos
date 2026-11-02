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


# --- Twitch, Reddit (app-only OAuth; need credentials) -------------------------------


@pytest.fixture
def oauth(upstream, monkeypatch):
    """Twitch and Reddit credentials plus a fake token endpoint."""
    from src import config

    for name, value in {
        "twitch_client_id": "tw-id",
        "twitch_client_secret": "tw-secret",
        "reddit_client_id": "rd-id",
        "reddit_client_secret": "rd-secret",
    }.items():
        monkeypatch.setattr(config.settings, name, value)
    providers._tokens.clear()
    tokens = []

    def fake_post(url, **kwargs):
        tokens.append(url)
        return FakeResponse(data={"access_token": f"token-{len(tokens)}", "expires_in": 3600})

    monkeypatch.setattr(providers, "_post", fake_post)
    routes, calls = upstream
    return routes, calls, tokens


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://clips.twitch.tv/FaintLightGullWholeWheat", ("twitch", "clip/FaintLightGullWholeWheat")),
        ("https://www.twitch.tv/some_streamer/clip/FaintLightGullWholeWheat-AbC?filter=clips", ("twitch", "clip/FaintLightGullWholeWheat-AbC")),
        ("https://clips.twitch.tv/embed?clip=FaintLightGullWholeWheat&parent=x", ("twitch", "clip/FaintLightGullWholeWheat")),
        ("https://www.twitch.tv/videos/635475444", ("twitch", "video/635475444")),
        ("https://www.reddit.com/r/videos/comments/6rrwyj/that_small_heart_attack/", ("reddit", "6rrwyj")),
        ("https://old.reddit.com/comments/6RRWYJ", ("reddit", "6rrwyj")),
        ("https://redd.it/6rrwyj", ("reddit", "6rrwyj")),
        ("https://www.reddit.com/r/videos/s/AbCdEf1234?utm=x", ("reddit", "https://www.reddit.com/r/videos/s/AbCdEf1234")),
    ],
)
def test_recognises_twitch_and_reddit_links(url, expected):
    provider, ref = providers.match(url)
    assert (provider.key, ref) == expected


@pytest.mark.parametrize(
    "url", ["https://clips.twitch.tv/embed", "https://www.twitch.tv/some_streamer", "https://www.reddit.com/r/videos/"]
)
def test_ignores_twitch_and_reddit_pages(url):
    assert providers.match(url) is None


@pytest.mark.parametrize(
    "url, needs",
    [
        ("https://www.twitch.tv/videos/635475444", "TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET"),
        ("https://redd.it/6rrwyj", "REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET"),
    ],
)
def test_twitch_and_reddit_say_when_they_are_not_set_up(upstream, monkeypatch, url, needs):
    from src import config

    for name in ("twitch_client_id", "twitch_client_secret", "reddit_client_id", "reddit_client_secret"):
        monkeypatch.setattr(config.settings, name, "")
    response = client.get("/url", params={"url": url})
    assert response.status_code == 501
    assert needs in response.json()["detail"]


def test_twitch_clip_thumbnail_and_token_reuse(oauth):
    routes, calls, tokens = oauth
    routes["https://api.twitch.tv/helix/clips"] = FakeResponse(
        data={"data": [{"thumbnail_url": "https://clips-media-assets2.twitch.tv/x-preview-480x272.jpg"}]}
    )
    routes["https://clips-media-assets2.twitch.tv/"] = FakeResponse(content=jpeg((480, 272)))
    for _ in range(2):
        assert client.get("/url", params={"url": "https://clips.twitch.tv/FaintLightGullWholeWheat"}).status_code == 200
    assert calls[0] == "https://api.twitch.tv/helix/clips?id=FaintLightGullWholeWheat"
    assert tokens == ["https://id.twitch.tv/oauth2/token"]  # the app token is cached


def test_twitch_video_fills_in_the_thumbnail_size(oauth):
    routes, calls, _ = oauth
    routes["https://api.twitch.tv/helix/videos"] = FakeResponse(
        data={"data": [{"thumbnail_url": "https://static-cdn.jtvnw.net/cf_vods/x/thumb0-%{width}x%{height}.jpg"}]}
    )
    routes["https://static-cdn.jtvnw.net/"] = FakeResponse(content=jpeg((1280, 720)))
    assert client.get("/url", params={"url": "https://www.twitch.tv/videos/635475444"}).status_code == 200
    assert calls[1] == "https://static-cdn.jtvnw.net/cf_vods/x/thumb0-1280x720.jpg"


def test_twitch_refreshes_an_expired_token(oauth):
    routes, calls, tokens = oauth
    answers = iter([FakeResponse(status=401), FakeResponse(data={"data": [{"thumbnail_url": "https://cdn.test/t.jpg"}]})])
    routes["https://api.twitch.tv/"] = lambda url: next(answers)
    routes["https://cdn.test/"] = FakeResponse(content=jpeg((1280, 720)))
    assert client.get("/url", params={"url": "https://www.twitch.tv/videos/635475444"}).status_code == 200
    assert len(tokens) == 2


@pytest.mark.parametrize("data", [{"data": []}, {"data": [{"thumbnail_url": ""}]}])
def test_missing_or_processing_twitch_video_is_a_404(oauth, data):
    routes, _, _ = oauth
    routes["https://api.twitch.tv/"] = FakeResponse(data=data)
    assert client.get("/url", params={"url": "https://www.twitch.tv/videos/635475444"}).status_code == 404


def test_reddit_preview_image(oauth):
    routes, calls, tokens = oauth
    routes["https://oauth.reddit.com/by_id/t3_6rrwyj"] = FakeResponse(
        data={"data": {"children": [{"data": {"preview": {"images": [{"source": {"url": "https://preview.redd.it/a.jpg?s=1"}}]}}}]}}
    )
    routes["https://preview.redd.it/"] = FakeResponse(content=jpeg((1280, 720)))
    response = client.get("/reddit/6rrwyj")
    assert response.status_code == 200
    assert calls == ["https://oauth.reddit.com/by_id/t3_6rrwyj?raw_json=1", "https://preview.redd.it/a.jpg?s=1"]
    assert tokens == ["https://www.reddit.com/api/v1/access_token"]


def test_reddit_share_links_are_followed(oauth):
    routes, calls, _ = oauth
    routes["https://www.reddit.com/r/videos/s/"] = FakeResponse(url="https://www.reddit.com/r/videos/comments/6rrwyj/x/")
    routes["https://oauth.reddit.com/"] = FakeResponse(
        data={"data": {"children": [{"data": {"thumbnail": "https://b.thumbs.redditmedia.com/t.jpg"}}]}}
    )
    routes["https://b.thumbs.redditmedia.com/"] = FakeResponse(content=jpeg((140, 78)))
    assert client.get("/url", params={"url": "https://www.reddit.com/r/videos/s/AbCdEf1234"}).status_code == 200
    assert calls[1] == "https://oauth.reddit.com/by_id/t3_6rrwyj?raw_json=1"


@pytest.mark.parametrize(
    "children", [[], [{"data": {"thumbnail": "self"}}], [{"data": {"thumbnail": "nsfw"}}]]
)
def test_reddit_posts_without_an_image_are_a_404(oauth, children):
    routes, _, _ = oauth
    routes["https://oauth.reddit.com/"] = FakeResponse(data={"data": {"children": children}})
    assert client.get("/reddit/6rrwyj").status_code == 404


def test_wrong_credentials_are_a_502(upstream, oauth, monkeypatch):
    monkeypatch.setattr(providers, "_post", lambda url, **kw: FakeResponse(status=401))
    providers._tokens.clear()
    response = client.get("/reddit/6rrwyj")
    assert response.status_code == 502
    assert "Reddit answered 401" in response.json()["detail"]


# --- Page preview images ---------------------------------------------------------
# No service uses this right now, so these call it with an example service.

EXAMPLE = providers.Provider(key="example", name="Example", patterns=(), color=(0, 0, 0), fetch=lambda p, r: None)
VIDEO_PAGE = "https://video.example.test/watch/abc123"
PAGE = """<html><head><title>x</title>
<meta property="og:title" content="A video">
<meta property="og:image" content="https://img.example.test/covers/abc123.jpg?a=1&amp;b=2">
</head><body></body></html>"""


def preview():
    return providers.page_preview_image(EXAMPLE, "abc123", VIDEO_PAGE, lambda url: url.endswith("/watch/abc123"))


def test_reads_the_pages_preview_image(upstream):
    routes, calls = upstream
    routes[VIDEO_PAGE] = FakeResponse(content=PAGE.encode(), url=VIDEO_PAGE)
    routes["https://img.example.test/"] = FakeResponse(content=jpeg((1280, 720)))
    assert preview().size == (1280, 720)
    # HTML entities in the content attribute are decoded
    assert calls[1] == "https://img.example.test/covers/abc123.jpg?a=1&b=2"


@pytest.mark.parametrize(
    "tag",
    [
        '<meta content="//img.example.test/a.jpg" property="og:image">',  # attribute order, protocol-relative
        '<meta name="twitter:image" content="/a.jpg">',  # relative to the page
        '<meta itemprop="image" content="https://img.example.test/a.jpg">',
    ],
)
def test_preview_image_variants(upstream, tag):
    routes, calls = upstream
    routes[VIDEO_PAGE] = FakeResponse(content=f"<head>{tag}</head>".encode(), url=VIDEO_PAGE)
    routes["https://img.example.test/"] = FakeResponse(content=jpeg((1280, 720)))
    routes["https://video.example.test/a.jpg"] = FakeResponse(content=jpeg((1280, 720)))
    preview()
    assert calls[1] in ("https://img.example.test/a.jpg", "https://video.example.test/a.jpg")


def test_page_without_a_preview_image_is_not_found(upstream):
    routes, _ = upstream
    routes[VIDEO_PAGE] = FakeResponse(content=b"<html><head></head></html>", url=VIDEO_PAGE)
    with pytest.raises(providers.VideoNotFound):
        preview()


@pytest.mark.parametrize(
    "landed_on",
    [
        "https://video.example.test/login",
        # Login and error pages often carry the original URL in the query
        # string. That must not count as still being on the video's page.
        "https://video.example.test/404?redirectPath=https%3A%2F%2Fvideo.example.test%2Fwatch%2Fabc123",
        "https://video.example.test/login?redirectPath=https://video.example.test/watch/abc123",
    ],
)
def test_redirect_away_from_the_video_is_a_refusal(upstream, landed_on):
    routes, calls = upstream
    # The page we're sent to has a preview image too (usually the site's logo)
    routes[VIDEO_PAGE] = FakeResponse(content=PAGE.encode(), url=landed_on)
    with pytest.raises(providers.UpstreamError) as refused:
        preview()
    assert "sent us to another page instead of the video" in refused.value.detail
    assert len(calls) == 1  # the logo is never downloaded
