from PIL import Image
import requests
from requests.adapters import HTTPAdapter, Retry
from io import BytesIO
from enum import Enum
import re


class Supported_Filetype(str, Enum):
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"


class URL_Regex(str, Enum):
    YOUTUBE = r"^(?:(?:https?://(?:www\.)?(?:m\.)?youtube\.com))/(?:(?:oembed\?url=https?%3A//(?:www\.)youtube.com/watch\?(?:v%3D)(?P<video_id_1>[A-Za-z0-9_\-]{11}))|(?:attribution_link\?a=.*watch(?:%3Fv%3D|%3Fv%3D)(?P<video_id_2>[A-Za-z0-9_\-]{11}))).*|(?:https?:)?(?:\/\/)?(?:(?:www\.|m\.)?youtube(?:-nocookie)?\.com\/(?:(?:watch)?\?(?:app=desktop&)?(?:feature=\w*&)?v=|embed\/|v\/|e\/)|youtu\.be\/)(?P<video_id_3>[A-Za-z0-9_\-]{11}).*$"
    """Matches all valid youtube url formats in this list: https://gist.github.com/Snailedlt/d54514e37dda68fefe15e6e056b30747"""
    VIMEO = r"(https?://)?(www.)?(player.)?vimeo.com/([a-z]*/)*(.*/)?(?P<video_id>[0-9]{6,11})[?]?.*"


def get_video_id_by_url(url, regex) -> None | str:
    match = re.match(regex, url, re.IGNORECASE)
    if match:
        for group_name, group_value in match.groupdict().items():
            if group_name.startswith("video_id"):
                if group_value:
                    return group_value
    else:
        return None
    raise Exception("Something went wrong while trying to get the video id.")


def read_img_from_url(url: str, alt_url: None | str = None) -> Image.Image:
    res = request_with_retry(url)
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError:
        if alt_url is not None and res.status_code == 404:
            res = request_with_retry(alt_url)
            res.raise_for_status()
    return Image.open(BytesIO(res.content))


def add_play_button_to_thumbnail(
    thumbnail: Image, play_button_path: str
) -> Image.Image:
    # Read images
    play = Image.open(play_button_path).convert("RGBA")
    # Resize play button
    play_size_ideal = (int(thumbnail.width / 4.75), int(thumbnail.width / 4.75 * 0.7))
    play_size_max = (132, 84)
    play_size_new = min(play_size_ideal[0], play_size_max[0]), min(
        play_size_ideal[1], play_size_max[1]
    )
    play = play.resize(play_size_new)
    # Create backdrop
    backdrop = Image.open("src/img/backdrop.png")
    # Resize backdrop
    backdrop = backdrop.resize((thumbnail.width, thumbnail.height))
    # Determine position of play button image
    play_x = int(thumbnail.width / 2) - int(play.width / 2)
    play_y = int(thumbnail.height / 2) - int(play.height / 2)
    play_pos = (play_x, play_y)
    # Add backdrop
    thumbnail.paste(backdrop, (0, 0), backdrop)
    # Add play button image
    thumbnail.paste(play, (play_pos), play)
    return thumbnail


def request_with_retry(url, retries: Retry | int = 5):
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s.get(url)
