import typing
from PIL import Image
import requests
from io import BytesIO
from enum import Enum
import re


class Supported_Filetype(str, Enum):
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"


def get_youtube_video_id_by_url(url):
    reg = r"^((https?://(?:www\.)?(?:m\.)?youtube\.com))/((?:oembed\?url=https?%3A//(?:www\.)youtube.com/watch\?(?:v%3D)(?P<video_id_1>[\w\-]{10,20})&format=json)|(?:attribution_link\?a=.*watch(?:%3Fv%3D|%3Fv%3D)(?P<video_id_2>[\w\-]{10,20}))(?:%26feature.*))|(https?:)?(\/\/)?((www\.|m\.)?youtube(-nocookie)?\.com\/((watch)?\?(app=desktop&)?(feature=\w*&)?v=|embed\/|v\/|e\/)|youtu\.be\/)(?P<video_id_3>[\w\-]{10,20})"
    match = re.match(reg, url, re.IGNORECASE)
    if match:
        return (
            match.group("video_id_1")
            or match.group("video_id_2")
            or match.group("video_id_3")
        )
    else:
        return None


def read_img_from_url(url: str, alt_url: typing.Optional[str] = None) -> Image.Image:
    res = requests.get(url)
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError:
        if alt_url is not None and res.status_code == 404:
            res = requests.get(alt_url)
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
    backdrop = Image.open("api/img/backdrop.png")
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
