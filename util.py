import sys
from PIL import Image
import requests
from io import BytesIO
from base64 import b64encode


def get_edited_thumbnail_img(video_id: str):
    thumbnail = read_img_from_url(f"https://i.ytimg.com/vi_webp/{video_id}/mqdefault.webp")
    thumbnail_w_play_btn = add_play_button_to_thumbnail(thumbnail)
    return thumbnail_w_play_btn


def get_edited_thumbnail_bytes(video_id: str):
    thumbnail_w_play_btn = get_edited_thumbnail_img(video_id)
    thumbnail_b64 = pil_img_to_b64(thumbnail_w_play_btn)
    return thumbnail_b64


def get_edited_thumbnail_html(video_id: str):
    thumbnail_b64 = get_edited_thumbnail_bytes(video_id)
    dataurl = 'data:image/png;base64,' + thumbnail_b64
    thumbnail_html = f"<img src='{dataurl}'/>".format("base64")
    return thumbnail_html


def pil_img_to_b64(img: Image):
    image_io = BytesIO()
    img.save(image_io, 'PNG')
    return b64encode(image_io.getvalue()).decode('ascii')


def read_img_from_url(url: str):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img


def add_play_button_to_thumbnail(thumbnail: Image):
    #Read the two images
    play = Image.open('img/youtube_play_button.png')
    backdrop = Image.open('img/backdrop.png')
    #resize, first image
    play = play.resize((50, 50))
    #determine position of play button image
    play_x = int(thumbnail.width/2) - int(play.width/2)
    play_y = int(thumbnail.height/2) - int(play.height/2)
    play_pos = (play_x,play_y)
    #declare new image
    merged_image = thumbnail
    #add backdrop
    merged_image.paste(backdrop, (0,0), backdrop)
    #add play button image
    merged_image.paste(play,(play_pos), play)
    return merged_image
    # merged_image.save("merged_image.jpg","JPEG")
    # merged_image.show()
    