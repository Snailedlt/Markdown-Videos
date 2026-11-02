import typing
from PIL import Image
import requests
from requests.adapters import HTTPAdapter, Retry
from io import BytesIO
from enum import Enum
import re
from functools import lru_cache

BACKDROP_PATH = "src/img/backdrop.png"


class Supported_Filetype(str, Enum):
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"


class URL_Regex(str, Enum):
    YOUTUBE = r"^(?:(?:https?://(?:www\.)?(?:m\.)?youtube\.com))/(?:(?:oembed\?url=https?%3A//(?:www\.)youtube.com/watch\?(?:v%3D)(?P<video_id_1>[A-Za-z0-9_\-]{11}))|(?:attribution_link\?a=.*watch(?:%3Fv%3D|%3Fv%3D)(?P<video_id_2>[A-Za-z0-9_\-]{11}))).*|(?:https?:)?(?:\/\/)?(?:(?:www\.|m\.)?youtube(?:-nocookie)?\.com\/(?:(?:watch)?\?(?:app=desktop&)?(?:feature=\w*&)?v=|embed\/|v\/|e\/|shorts\/)|youtu\.be\/)(?P<video_id_3>[A-Za-z0-9_\-]{11}).*$"
    """Matches all valid youtube url formats in this list: https://gist.github.com/Snailedlt/d54514e37dda68fefe15e6e056b30747"""
    VIMEO = r"(https?://)?(www.)?(player.)?vimeo.com/([a-z]*/)*(.*/)?(?P<video_id>[0-9]{6,11})[?]?.*"


def get_video_id_by_url(url, regex) -> typing.Optional[str]:
    match = re.match(regex, url, re.IGNORECASE)
    if match:
        for group_name, group_value in match.groupdict().items():
            if group_name.startswith("video_id"):
                if group_value:
                    return group_value
    else:
        return None
    raise Exception("Something went wrong while trying to get the video id.")


# One shared HTTP session per (warm) serverless instance, so connections to
# img.youtube.com / vumbnail.com are reused instead of re-negotiated per request.
_session = requests.Session()
_session.mount(
    "https://",
    HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.2, status_forcelist=(502, 503, 504))),
)

# Never let a slow upstream keep a (billed) function running for long.
REQUEST_TIMEOUT_SECONDS = 8


def request_with_retry(url: str) -> requests.Response:
    return _session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)


def read_img_from_url(url: str, alt_url: typing.Optional[str] = None) -> Image.Image:
    res = request_with_retry(url)
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError:
        if alt_url is not None and res.status_code == 404:
            res = request_with_retry(alt_url)
            res.raise_for_status()
        else:
            raise
    return Image.open(BytesIO(res.content))


@lru_cache(maxsize=None)
def _load_rgba(path: str) -> Image.Image:
    """Static overlay images are read from disk once per instance."""
    return Image.open(path).convert("RGBA")


@lru_cache(maxsize=64)
def _resized(path: str, size: typing.Tuple[int, int]) -> Image.Image:
    return _load_rgba(path).resize(size)


def add_play_button_to_thumbnail(
    thumbnail: Image.Image, play_button_path: str
) -> Image.Image:
    # Resize play button
    play_size_ideal = (int(thumbnail.width / 4.75), int(thumbnail.width / 4.75 * 0.7))
    play_size_max = (132, 84)
    play_size_new = (
        max(1, min(play_size_ideal[0], play_size_max[0])),
        max(1, min(play_size_ideal[1], play_size_max[1])),
    )
    play = _resized(play_button_path, play_size_new)
    backdrop = _resized(BACKDROP_PATH, (thumbnail.width, thumbnail.height))
    # Determine position of play button image
    play_x = int(thumbnail.width / 2) - int(play.width / 2)
    play_y = int(thumbnail.height / 2) - int(play.height / 2)
    # Add backdrop and play button
    thumbnail.paste(backdrop, (0, 0), backdrop)
    thumbnail.paste(play, (play_x, play_y), play)
    return thumbnail
