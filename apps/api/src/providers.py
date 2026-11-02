"""Video services beyond YouTube and Vimeo.

Each provider knows which links belong to it, how to fetch a thumbnail for a
video without an API key, and the colour of its play button. YouTube and Vimeo
keep their own endpoints in main.py (they predate this module and YouTube also
has animated GIFs).

Adding a service = adding one Provider to PROVIDERS (and a test).
"""

from __future__ import annotations

import re
import threading
import time
import typing
from dataclasses import dataclass
from functools import lru_cache
from html import unescape as html_unescape
from io import BytesIO
from urllib.parse import quote, urljoin, urlsplit

import requests
from fastapi import HTTPException
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from src import config, util

# Some services answer oEmbed requests from scripts only with a browser-like
# User-Agent; identify ourselves honestly while looking like one.
OEMBED_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; Markdown-Videos/1.0;"
        " +https://github.com/Snailedlt/Markdown-Videos)"
    ),
    "Accept": "application/json",
}


class UpstreamError(HTTPException):
    def __init__(self, provider: "Provider", status: typing.Optional[int] = None, why: str = ""):
        reason = f" ({why or f'{provider.name} answered {status}'})" if (status or why) else ""
        super().__init__(
            status_code=502,
            detail=f"Couldn't get a thumbnail from {provider.name} right now{reason}. Please try again later.",
        )


# Statuses that mean "this video doesn't exist (or isn't public)". Anything
# else, notably 401/403/429 (refused or rate-limited), is the service's
# problem and becomes a 502 that says so, instead of a misleading 404.
NOT_FOUND_STATUSES = (400, 404, 410)
REFUSED_STATUSES = (401, 403, 429)


def _check(res: requests.Response, provider: "Provider", ref: str) -> None:
    if res.status_code in NOT_FOUND_STATUSES:
        raise VideoNotFound(provider, ref)
    if res.status_code in REFUSED_STATUSES or res.status_code >= 500:
        raise UpstreamError(provider, res.status_code)
    res.raise_for_status()


class NotConfigured(HTTPException):
    def __init__(self, provider: "Provider", needs: str):
        super().__init__(
            status_code=501,
            detail=(
                f"{provider.name} thumbnails aren't set up on this server: it needs {needs}."
                " See https://github.com/Snailedlt/Markdown-Videos/blob/main/apps/api/README.md#supported-services"
            ),
        )


def _setting(name: str) -> str:
    return (getattr(config.settings, name, "") or "").strip()


class VideoNotFound(HTTPException):
    def __init__(self, provider: "Provider", ref: str):
        super().__init__(
            status_code=404,
            detail=(
                f"No {provider.name} video found for {ref}. Check that the link is"
                " right and that the video is public."
            ),
        )


@dataclass(frozen=True)
class Provider:
    key: str
    """Used in endpoint paths (/imgur/{video_id}) and by the website."""
    name: str
    patterns: typing.Tuple[re.Pattern, ...]
    """Each pattern has an `id` group (and may have others used by `ref`)."""
    color: typing.Tuple[int, int, int]
    """Play button colour."""
    fetch: typing.Callable[["Provider", str], Image.Image]
    """Download the thumbnail for a reference (see `ref`)."""
    ref: typing.Callable[[re.Match], str] = lambda m: m.group("id")
    """What `fetch` needs: usually the video ID, sometimes a canonical URL."""
    id_route: bool = True
    """Whether /{key}/{video_id} exists (needs a fetch that works from the ID alone)."""
    id_pattern: str = r"[A-Za-z0-9_-]+"
    missing_credentials: typing.Optional[typing.Callable[[], typing.Optional[str]]] = None
    """For services behind an authenticated API: returns what's missing, or None when configured."""

    def match(self, url: str) -> typing.Optional[str]:
        for pattern in self.patterns:
            m = pattern.match(url.strip())
            if m:
                return self.ref(m)
        return None


# --- Fetching -----------------------------------------------------------------


def _get(url: str, **kwargs) -> requests.Response:
    return util._session.get(url, timeout=util.REQUEST_TIMEOUT_SECONDS, **kwargs)


def _image(provider: Provider, ref: str, url: str) -> Image.Image:
    res = _get(url, headers=OEMBED_HEADERS)
    _check(res, provider, ref)
    return Image.open(BytesIO(res.content))


def oembed_thumbnail(endpoint: str, video_url: str, provider: Provider, ref: str) -> Image.Image:
    """Most services publish the thumbnail URL in their oEmbed response."""
    res = _get(f"{endpoint}?url={quote(video_url, safe='')}&format=json", headers=OEMBED_HEADERS)
    _check(res, provider, ref)
    thumbnail_url = res.json().get("thumbnail_url")
    if not thumbnail_url:
        raise VideoNotFound(provider, ref)
    # Some services return protocol-relative URLs ("//cdn.example.com/...")
    return _image(provider, ref, urljoin("https:", thumbnail_url))


def _imgur(provider: Provider, video_id: str) -> Image.Image:
    # "h" is Imgur's largest thumbnail (1024px). For videos and GIFs it's a
    # still frame. Missing posts redirect to a "removed" placeholder image,
    # which must not get a play button.
    # Imgur rate-limits (429) requests with python-requests' default User-Agent
    res = _get(f"https://i.imgur.com/{video_id}h.jpg", headers=OEMBED_HEADERS, allow_redirects=False)
    if res.is_redirect:
        raise VideoNotFound(provider, video_id)
    _check(res, provider, video_id)
    return Image.open(BytesIO(res.content))


def _loom(provider: Provider, video_id: str) -> Image.Image:
    return oembed_thumbnail(
        "https://www.loom.com/v1/oembed", f"https://www.loom.com/share/{video_id}", provider, video_id
    )


def _dailymotion(provider: Provider, video_id: str) -> Image.Image:
    # Dailymotion's public Data API needs no key and answers 404 for missing
    # videos (its /thumbnail/ redirect would serve a placeholder instead)
    res = _get(
        f"https://api.dailymotion.com/video/{video_id}?fields=thumbnail_720_url",
        headers=OEMBED_HEADERS,
    )
    if res.status_code in (400, 403, 404, 410):
        raise VideoNotFound(provider, video_id)
    res.raise_for_status()
    thumbnail_url = res.json().get("thumbnail_720_url")
    if not thumbnail_url:
        raise VideoNotFound(provider, video_id)
    return _image(provider, video_id, thumbnail_url)


def _streamable(provider: Provider, video_id: str) -> Image.Image:
    return oembed_thumbnail(
        "https://api.streamable.com/oembed.json", f"https://streamable.com/{video_id}", provider, video_id
    )


# Streamable video IDs are short, so these site pages must not count as videos
_STREAMABLE_PAGES = r"(?!(?:login|signup|upload|pricing|settings|about|blog|terms|privacy|documentation|clipper|tools|enterprise)\b)"


PROVIDERS: typing.Tuple[Provider, ...] = (
    Provider(
        key="imgur",
        name="Imgur",
        patterns=(
            re.compile(r"^(?:https?://)?i\.imgur\.com/(?P<id>[A-Za-z0-9]{5,10})\.(?:mp4|gifv|webm|gif|jpe?g|png)(?:[?#].*)?$", re.I),
            re.compile(r"^(?:https?://)?(?:www\.|m\.)?imgur\.com/(?P<id>[A-Za-z0-9]{5,10})(?:[?#].*)?$", re.I),
        ),
        color=(27, 183, 110),
        fetch=_imgur,
        id_pattern=r"[A-Za-z0-9]{5,10}",
    ),
)

PROVIDERS += (
    Provider(
        key="loom",
        name="Loom",
        patterns=(
            # loom.com/share/<id> or loom.com/share/<title-slug>-<id>
            re.compile(r"^(?:https?://)?(?:www\.)?loom\.com/(?:share|embed)/(?:[\w-]*-)?(?P<id>[0-9a-f]{32})(?=[/?#]|$)", re.I),
        ),
        color=(98, 93, 245),
        fetch=_loom,
        id_pattern=r"[0-9a-f]{32}",
    ),
    Provider(
        key="dailymotion",
        name="Dailymotion",
        patterns=(
            re.compile(r"^(?:https?://)?(?:www\.)?dailymotion\.com/(?:embed/)?video/(?P<id>x[a-z0-9]{4,12})(?=[/?#_]|$)", re.I),
            re.compile(r"^(?:https?://)?dai\.ly/(?P<id>x[a-z0-9]{4,12})(?=[/?#]|$)", re.I),
            re.compile(r"^(?:https?://)?geo\.dailymotion\.com/player(?:/[\w-]+)?\.html\?(?:[^#]*&)?video=(?P<id>x[a-z0-9]{4,12})", re.I),
        ),
        color=(0, 102, 220),
        fetch=_dailymotion,
        id_pattern=r"x[a-z0-9]{4,12}",
    ),
    Provider(
        key="streamable",
        name="Streamable",
        patterns=(
            re.compile(r"^(?:https?://)?(?:www\.)?streamable\.com/(?:[eos]/)?" + _STREAMABLE_PAGES + r"(?P<id>[a-z0-9]{3,10})(?=[/?#]|$)", re.I),
        ),
        color=(15, 144, 250),
        fetch=_streamable,
        id_pattern=r"[a-z0-9]{3,10}",
    ),
)

def _rumble(provider: Provider, ref: str) -> Image.Image:
    return oembed_thumbnail("https://rumble.com/api/Media/oembed.json", ref, provider, ref)


PROVIDERS += (
    Provider(
        key="rumble",
        name="Rumble",
        patterns=(
            # rumble.com/v5abc12-some-title.html and rumble.com/embed/v4xyz9/
            re.compile(r"^(?:https?://)?(?:www\.)?rumble\.com/(?:embed/)?(?P<id>v[0-9a-z]{3,10})(?:-[\w-]*\.html|/)?(?:[?#].*)?$", re.I),
        ),
        color=(133, 199, 66),
        fetch=_rumble,
        # Rumble's oEmbed wants the page link; page and embed IDs differ, so
        # Rumble videos go through /url?url=...
        ref=lambda m: m.group(0).split("?")[0] if m.group(0).startswith("http") else f"https://{m.group(0).split('?')[0]}",
        id_route=False,
    ),
)

# --- Meta (Instagram, Facebook) ---------------------------------------------------

GRAPH_API = "https://graph.facebook.com"
# Graph API error codes that mean "we were refused" (bad/expired token,
# rate limits, app limits) rather than "this post doesn't exist"
_META_REFUSED_CODES = {4, 10, 17, 32, 190, 200, 368, 613}


def _meta_token() -> str:
    return _setting("meta_access_token") or f"{_setting('meta_app_id')}|{_setting('meta_client_token')}"


def _meta_missing() -> typing.Optional[str]:
    if _setting("meta_access_token") or (_setting("meta_app_id") and _setting("meta_client_token")):
        return None
    return "META_APP_ID and META_CLIENT_TOKEN (or META_ACCESS_TOKEN)"


def _meta_get(provider: Provider, ref: str, path: str, **params: str) -> dict:
    query = "&".join(f"{k}={quote(v, safe='')}" for k, v in {**params, "access_token": _meta_token()}.items())
    res = _get(f"{GRAPH_API}/{path}?{query}", headers=OEMBED_HEADERS)
    if res.status_code >= 400:
        try:
            code = res.json().get("error", {}).get("code")
        except ValueError:
            code = None
        if code in _META_REFUSED_CODES or res.status_code >= 500 or res.status_code == 429:
            raise UpstreamError(provider, res.status_code)
        raise VideoNotFound(provider, ref)
    return res.json()


def _instagram(provider: Provider, shortcode: str) -> Image.Image:
    data = _meta_get(
        provider,
        shortcode,
        "instagram_oembed",
        url=f"https://www.instagram.com/p/{shortcode}/",
        fields="thumbnail_url",
    )
    if not data.get("thumbnail_url"):
        raise VideoNotFound(provider, shortcode)
    return _image(provider, shortcode, data["thumbnail_url"])


def _facebook(provider: Provider, video_id: str) -> Image.Image:
    # Facebook's oEmbed has no thumbnail; the video node's `picture` does
    data = _meta_get(provider, video_id, video_id, fields="picture")
    if not data.get("picture"):
        raise VideoNotFound(provider, video_id)
    return _image(provider, video_id, data["picture"])


PROVIDERS += (
    Provider(
        key="instagram",
        name="Instagram",
        patterns=(
            # instagram.com/p/<code>/, /reel/<code>/, /reels/<code>/, /tv/<code>/
            re.compile(r"^(?:https?://)?(?:www\.|m\.)?instagram\.com/(?:[\w.]+/)?(?:p|reels?|tv)/(?P<id>[A-Za-z0-9_-]{5,40})(?=[/?#]|$)", re.I),
        ),
        color=(225, 48, 108),
        fetch=_instagram,
        id_pattern=r"[A-Za-z0-9_-]{5,40}",
        missing_credentials=_meta_missing,
    ),
    Provider(
        key="facebook",
        name="Facebook",
        patterns=(
            re.compile(r"^(?:https?://)?(?:www\.|m\.|web\.)?facebook\.com/(?:[\w.-]+/videos/(?:[\w.-]+/)?|watch/?\?(?:[^#]*&)?v=|reel/|video\.php\?(?:[^#]*&)?v=)(?P<id>\d{8,20})(?=[/?#&]|$)", re.I),
        ),
        color=(24, 119, 242),
        fetch=_facebook,
        id_pattern=r"\d{8,20}",
        missing_credentials=_meta_missing,
    ),
)

# --- App-only OAuth tokens (Twitch, Reddit) ---------------------------------------

_tokens: typing.Dict[str, typing.Tuple[str, float]] = {}
_tokens_lock = threading.Lock()


def _post(url: str, **kwargs) -> requests.Response:
    return util._session.post(url, timeout=util.REQUEST_TIMEOUT_SECONDS, **kwargs)


def _app_token(provider: Provider, fetch: typing.Callable[[], requests.Response], refresh: bool = False) -> str:
    """A cached client-credentials token, fetched again shortly before it expires."""
    with _tokens_lock:
        cached = _tokens.get(provider.key)
        if cached and not refresh and cached[1] > time.time() + 60:
            return cached[0]
        res = fetch()
        if res.status_code >= 400:
            # Wrong client ID/secret, or the service refusing us
            raise UpstreamError(provider, res.status_code)
        body = res.json()
        token = body["access_token"]
        _tokens[provider.key] = (token, time.time() + float(body.get("expires_in", 3600)))
        return token


# Twitch ----------------------------------------------------------------------------


def _twitch_missing() -> typing.Optional[str]:
    if _setting("twitch_client_id") and _setting("twitch_client_secret"):
        return None
    return "TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET"


def _twitch_token(provider: Provider, refresh: bool = False) -> str:
    return _app_token(
        provider,
        lambda: _post(
            "https://id.twitch.tv/oauth2/token",
            data={
                "client_id": _setting("twitch_client_id"),
                "client_secret": _setting("twitch_client_secret"),
                "grant_type": "client_credentials",
            },
        ),
        refresh,
    )


def _twitch(provider: Provider, ref: str) -> Image.Image:
    kind, _, ident = ref.partition("/")  # "clip/<slug>" or "video/<id>"
    url = f"https://api.twitch.tv/helix/{'clips' if kind == 'clip' else 'videos'}?id={quote(ident, safe='')}"
    for attempt in range(2):
        headers = {
            "Client-Id": _setting("twitch_client_id"),
            "Authorization": f"Bearer {_twitch_token(provider, refresh=attempt > 0)}",
        }
        res = _get(url, headers=headers)
        if res.status_code != 401:
            break
    _check(res, provider, ref)
    items = res.json().get("data") or []
    # Videos have a templated URL; it's empty while a video is still processing
    thumbnail_url = (items[0].get("thumbnail_url") if items else "") or ""
    if not thumbnail_url:
        raise VideoNotFound(provider, ref)
    return _image(provider, ref, thumbnail_url.replace("%{width}", "1280").replace("%{height}", "720"))


# Reddit ----------------------------------------------------------------------------

# Reddit asks API clients for a descriptive User-Agent
REDDIT_USER_AGENT = "web:markdown-videos:1.0 (by /u/Snailedlt; +https://github.com/Snailedlt/Markdown-Videos)"


def _reddit_missing() -> typing.Optional[str]:
    if _setting("reddit_client_id") and _setting("reddit_client_secret"):
        return None
    return "REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET"


def _reddit_token(provider: Provider, refresh: bool = False) -> str:
    return _app_token(
        provider,
        lambda: _post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(_setting("reddit_client_id"), _setting("reddit_client_secret")),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": REDDIT_USER_AGENT},
        ),
        refresh,
    )


def _reddit(provider: Provider, ref: str) -> Image.Image:
    post_id = ref
    if ref.startswith("https://"):
        # A share link (reddit.com/r/<sub>/s/<code>): follow it to the post
        target = _get(ref, headers={"User-Agent": REDDIT_USER_AGENT}, allow_redirects=True).url
        found = re.search(r"/comments/(?P<id>[a-z0-9]{5,10})", target, re.I)
        if not found:
            raise VideoNotFound(provider, ref)
        post_id = found.group("id")
    for attempt in range(2):
        headers = {
            "Authorization": f"bearer {_reddit_token(provider, refresh=attempt > 0)}",
            "User-Agent": REDDIT_USER_AGENT,
        }
        res = _get(f"https://oauth.reddit.com/by_id/t3_{post_id}?raw_json=1", headers=headers)
        if res.status_code != 401:
            break
    _check(res, provider, ref)
    children = (res.json().get("data") or {}).get("children") or []
    if not children:
        raise VideoNotFound(provider, ref)
    post = children[0].get("data", {})
    images = (post.get("preview") or {}).get("images") or []
    thumbnail_url = images[0]["source"]["url"] if images else post.get("thumbnail", "")
    if not str(thumbnail_url).startswith("https://"):
        # Text posts have no image ("self", "default", "nsfw" placeholders)
        raise VideoNotFound(provider, ref)
    return _image(provider, ref, thumbnail_url)


PROVIDERS += (
    Provider(
        key="twitch",
        name="Twitch",
        patterns=(
            re.compile(r"^(?:https?://)?clips\.twitch\.tv/(?:embed\?(?:[^#]*&)?clip=)?(?!embed(?:[/?#]|$))(?P<clip>[\w-]{5,100})(?=[/?#&]|$)", re.I),
            re.compile(r"^(?:https?://)?(?:www\.|m\.)?twitch\.tv/[\w]+/clip/(?P<clip>[\w-]{5,100})(?=[/?#]|$)", re.I),
            re.compile(r"^(?:https?://)?(?:www\.|m\.)?twitch\.tv/videos/(?P<video>\d{6,15})(?=[/?#]|$)", re.I),
        ),
        color=(145, 70, 255),
        fetch=_twitch,
        ref=lambda m: f"clip/{m.group('clip')}" if m.groupdict().get("clip") else f"video/{m.group('video')}",
        # Clips and videos share one service, so Twitch goes through /url
        id_route=False,
        missing_credentials=_twitch_missing,
    ),
    Provider(
        key="reddit",
        name="Reddit",
        patterns=(
            re.compile(r"^(?:https?://)?(?:www\.|old\.|new\.|np\.|m\.)?reddit\.com/(?:r/\w+/)?comments/(?P<id>[a-z0-9]{5,10})(?=[/?#]|$)", re.I),
            re.compile(r"^(?:https?://)?redd\.it/(?P<id>[a-z0-9]{5,10})/?(?:[?#].*)?$", re.I),
            re.compile(r"^(?:https?://)?(?:www\.)?reddit\.com/r/\w+/s/(?P<share>[A-Za-z0-9]{6,20})/?(?:[?#].*)?$", re.I),
        ),
        color=(255, 69, 0),
        fetch=_reddit,
        ref=lambda m: m.group("id").lower() if m.groupdict().get("id") else f"https://www.reddit.com{m.group(0)[m.group(0).index('/r/'):].split('?')[0]}",
        id_pattern=r"[a-z0-9]{5,10}",
        missing_credentials=_reddit_missing,
    ),
)

# --- Page preview images -------------------------------------------------------
# For a service with no thumbnail API: read the preview image a video page
# declares for link previews (og:image and friends), like chat apps do when
# they unfurl a link. We identify ourselves and don't try to get past logins
# or captchas: a page that sends us there is reported as a refusal.
# No service uses this at the moment. Rednote did, but it sends servers to a
# login or error page instead of the note.

PAGE_HEADERS = {**OEMBED_HEADERS, "Accept": "text/html,application/xhtml+xml"}
_META_IMAGE = [
    re.compile(rf'<meta[^>]+(?:property|name|itemprop)=["\']{key}["\'][^>]*content=["\']([^"\']+)', re.I)
    for key in (r"og:image(?::secure_url)?", r"twitter:image(?::src)?", "image", "thumbnailUrl")
] + [
    re.compile(rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name|itemprop)=["\']{key}["\']', re.I)
    for key in (r"og:image(?::secure_url)?", r"twitter:image(?::src)?", "image", "thumbnailUrl")
]


def page_preview_image(provider: Provider, ref: str, page_url: str, still_there: typing.Callable[[str], bool]) -> Image.Image:
    """The preview image of a video page.

    `still_there` gets the URL we ended up on after redirects, without its query
    string or fragment, and says whether it is still the video's page. The query
    is left out because login and error pages often carry the original URL in
    it (?redirectPath=...), which would make them look like the video's page.
    """
    res = _get(page_url, headers=PAGE_HEADERS, allow_redirects=True)
    _check(res, provider, ref)
    if not still_there(urlsplit(res.url)._replace(query="", fragment="").geturl()):
        # Redirected to a login, captcha or home page instead of the video
        raise UpstreamError(provider, why=f"{provider.name} sent us to another page instead of the video, e.g. a login or captcha")
    head = res.content[:1_000_000].decode(getattr(res, "encoding", None) or "utf-8", errors="replace")
    for pattern in _META_IMAGE:
        found = pattern.search(head)
        if found:
            image_url = html_unescape(found.group(1)).strip()
            return _image(provider, ref, urljoin(res.url, image_url))
    raise VideoNotFound(provider, ref)


BY_KEY = {p.key: p for p in PROVIDERS}


def match(url: str) -> typing.Optional[typing.Tuple[Provider, str]]:
    for provider in PROVIDERS:
        ref = provider.match(url)
        if ref:
            return provider, ref
    return None


# --- Drawing ------------------------------------------------------------------


@lru_cache(maxsize=64)
def play_button(color: typing.Tuple[int, int, int], size: typing.Tuple[int, int]) -> Image.Image:
    """A rounded play button in the service's colour, drawn at 4x for smooth edges."""
    scale = 4
    w, h = size[0] * scale, size[1] * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=int(h * 0.28), fill=(*color, 235))
    tri_h = h * 0.42
    tri_w = tri_h * 0.9
    cx, cy = w / 2 + tri_w * 0.08, h / 2
    draw.polygon(
        [(cx - tri_w / 2, cy - tri_h / 2), (cx - tri_w / 2, cy + tri_h / 2), (cx + tri_w / 2, cy)],
        fill=(255, 255, 255, 255),
    )
    return img.resize(size, Image.LANCZOS)


def fit_frame(image: Image.Image, width: int, height: int) -> Image.Image:
    """Fill width x height without stretching.

    Close to the target shape: crop to fill. Very different (a vertical video
    in a 16:9 thumbnail): show the whole frame on a blurred, darkened copy of
    itself, like video apps do.
    """
    image = image.convert("RGB")
    source_ratio = image.width / image.height
    target_ratio = width / height
    cover = ImageOps.fit(image, (width, height), Image.LANCZOS)
    if abs(source_ratio / target_ratio - 1) < 0.2:
        return cover
    background = cover.filter(ImageFilter.GaussianBlur(radius=max(2, max(width, height) // 25)))
    background = ImageEnhance.Brightness(background).enhance(0.55)
    foreground = ImageOps.contain(image, (width, height), Image.LANCZOS)
    background.paste(foreground, ((width - foreground.width) // 2, (height - foreground.height) // 2))
    return background


def thumbnail(provider: Provider, ref: str, width: int, height: int) -> Image.Image:
    if provider.missing_credentials is not None:
        missing = provider.missing_credentials()
        if missing:
            raise NotConfigured(provider, missing)
    try:
        source = provider.fetch(provider, ref)
        source.load()
    except HTTPException:
        raise
    except Exception as e:
        # Rate limits, timeouts, unexpected responses: say which service failed
        raise UpstreamError(provider) from e
    frame = fit_frame(source, width, height)
    return util.overlay_play_button(frame, play_button(provider.color, util.play_button_size(frame)))
