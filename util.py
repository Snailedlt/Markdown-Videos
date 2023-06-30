from PIL import Image
import requests
from io import BytesIO
from base64 import b64encode
from fastapi.responses import StreamingResponse

from platforms import Platforms


def get_edited_thumbnail_img(
    platform: Platforms,
    video_id: str,
    width: int,
    height: int,
    ):
    if platform == Platforms.vimeo:
        thumbnail = get_vimeo_thumbnail(video_id)
    if platform == Platforms.youtube:
        thumbnail = get_youtube_thumbnail(video_id)

    resized_thumbnail = thumbnail.resize((width, height))

    return add_play_button_to_thumbnail(
        resized_thumbnail,
        f"img/{platform}_play_button.png"
        )


def read_img_from_url(url: str):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img


def add_play_button_to_thumbnail(thumbnail: Image, play_button_path: str):
    #Read images
    play = Image.open(play_button_path).convert("RGBA")
    #Resize play button
    play_size_ideal = (int(thumbnail.width/4.75), int(thumbnail.width/4.75*0.7))
    play_size_max = (132, 84)
    play_size_new = min(play_size_ideal[0], play_size_max[0]), min(play_size_ideal[1], play_size_max[1])
    play = play.resize(play_size_new)
    #Create backdrop
    backdrop = Image.open('img/backdrop.png')
    #Resize backdrop
    backdrop = backdrop.resize((thumbnail.width, thumbnail.height))
    #Determine position of play button image
    play_x = int(thumbnail.width/2) - int(play.width/2)
    play_y = int(thumbnail.height/2) - int(play.height/2)
    play_pos = (play_x, play_y)
    #Add backdrop
    thumbnail.paste(backdrop, (0,0), backdrop)
    #Add play button image
    thumbnail.paste(play,(play_pos), play)
    return thumbnail


def get_youtube_thumbnail(video_id: str):
    return read_img_from_url(f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg")


def get_vimeo_thumbnail(video_id: str):
    return read_img_from_url(f"https://vumbnail.com/{video_id}.jpg")
