from PIL import Image
import requests
from io import BytesIO
from base64 import b64encode
from fastapi.responses import StreamingResponse

from platforms import Platforms


def get_edited_thumbnail_img(platform: Platforms, video_id: str):
    if platform == Platforms.vimeo:
        thumbnail = get_vimeo_thumbnail(video_id)
        thumbnail_w_play_btn = add_play_button_to_thumbnail(thumbnail, "img/vimeo_play_button.png")
    if platform == Platforms.youtube:
        thumbnail = get_youtube_thumbnail(video_id)
        thumbnail_w_play_btn = add_play_button_to_thumbnail(thumbnail, "img/youtube_play_button.png")
    return thumbnail_w_play_btn


def read_img_from_url(url: str):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img


def add_play_button_to_thumbnail(thumbnail: Image, play_button_path: str):
    #Read images
    play = Image.open(play_button_path).convert("RGBA")
    backdrop = Image.open('img/backdrop.png')
    #Resize
    new_thumbnail = thumbnail.resize((320,180))
    backdrop = backdrop.resize((new_thumbnail.width, new_thumbnail.height))
    #determine position of play button image
    play_x = int(new_thumbnail.width/2) - int(play.width/2)
    play_y = int(new_thumbnail.height/2) - int(play.height/2)
    play_pos = (play_x,play_y)
    #add backdrop
    new_thumbnail.paste(backdrop, (0,0), backdrop)
    #add play button image
    new_thumbnail.paste(play,(play_pos), play)
    return new_thumbnail


def img_to_streaming_response(image: Image):
    imgio = BytesIO()
    image.save(imgio, 'PNG')
    imgio.seek(0)
    return StreamingResponse(content=imgio, media_type="image/png")


def get_youtube_thumbnail(video_id: str):
    return read_img_from_url(f"https://i.ytimg.com/vi_webp/{video_id}/mqdefault.webp")


def get_vimeo_thumbnail(video_id: str):
    return read_img_from_url(f"https://vumbnail.com/{video_id}.jpg")
