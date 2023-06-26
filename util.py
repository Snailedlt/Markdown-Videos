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


def img_to_streaming_response(image: Image):
    imgio = BytesIO()
    image.save(imgio, 'PNG')
    imgio.seek(0)
    return StreamingResponse(content=imgio, media_type="image/png")


def get_youtube_thumbnail(video_id: str):
    return read_img_from_url(f"https://i.ytimg.com/vi_webp/{video_id}/mqdefault.webp")


def get_vimeo_thumbnail(video_id: str):
    return read_img_from_url(f"https://vumbnail.com/{video_id}.jpg")
