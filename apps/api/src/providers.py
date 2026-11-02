"""Video services beyond YouTube and Vimeo.

Each provider knows which links belong to it, how to fetch a thumbnail for a
video without an API key, and the colour of its play button. YouTube and Vimeo
keep their own endpoints in main.py (they predate this module and YouTube also
has animated GIFs).

Adding a service = adding one Provider to PROVIDERS (and a test).
"""

from __future__ import annotations

import re
import typing
from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO
from urllib.parse import quote, urljoin

import requests
from fastapi import HTTPException
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from src import util

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
    def __init__(self, provider: "Provider", status: typing.Optional[int] = None):
        reason = f" ({provider.name} answered {status})" if status else ""
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


def _tiktok(provider: Provider, ref: str) -> Image.Image:
    video_url = ref
    if not re.match(r"^https://www\.tiktok\.com/@", ref):
        # Short share links (vm.tiktok.com/..., tiktok.com/t/...) redirect to the
        # full link, which is what TikTok's oEmbed understands.
        res = _get(ref, headers=OEMBED_HEADERS, allow_redirects=True)
        video_url = res.url.split("?")[0]
        if "/video/" not in video_url:
            raise VideoNotFound(provider, ref)
    return oembed_thumbnail("https://www.tiktok.com/oembed", video_url, provider, ref)


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


def _tiktok_ref(m: re.Match) -> str:
    if m.groupdict().get("user"):
        return f"https://www.tiktok.com/@{m.group('user')}/video/{m.group('id')}"
    return m.group(0).split("?")[0]


PROVIDERS: typing.Tuple[Provider, ...] = (
    Provider(
        key="tiktok",
        name="TikTok",
        patterns=(
            # Video IDs are 19 digits today; allow a little growth, and require the
            # ID to end so a half-typed link isn't taken for a different video
            re.compile(r"^(?:https?://)?(?:www\.|m\.)?tiktok\.com/@(?P<user>[\w.-]+)/video/(?P<id>\d{19,21})(?=[/?#]|$)", re.I),
            re.compile(r"^(?:https?://)?(?:vm|vt)\.tiktok\.com/(?P<id>[A-Za-z0-9]+)/?(?:[?#].*)?$", re.I),
            re.compile(r"^(?:https?://)?(?:www\.)?tiktok\.com/t/(?P<id>[A-Za-z0-9]+)/?(?:[?#].*)?$", re.I),
        ),
        color=(0, 0, 0),
        fetch=_tiktok,
        ref=_tiktok_ref,
        # TikTok's oEmbed needs the full link (with the username), so TikTok
        # videos go through /url?url=... instead of /tiktok/{id}.
        id_route=False,
    ),
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

    Close to the target shape: crop to fill. Very different (a vertical TikTok
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
