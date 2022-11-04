import sys
from PIL import Image
import requests
from io import BytesIO,StringIO
from base64 import b64encode


from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()



@app.get("/{video_id}", response_class=HTMLResponse)
async def read_items(video_id):
    thumbnail = read_img_from_url(f"https://i.ytimg.com/vi_webp/{video_id}/mqdefault.webp")
    thumbnail_w_play_btn = add_play_button_to_thumbnail(thumbnail)
    return pil_img_to_html(thumbnail_w_play_btn)


def pil_img_to_html(img):
    image_io = BytesIO()
    img.save(image_io, 'PNG')
    dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')
    return f"<img src='{dataurl}'/>"


def read_img_from_url(url: str):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img


def add_play_button_to_thumbnail(thumbnail: Image):
    #Read the two images
    play = Image.open('resources/youtube_play_button.png')
    backdrop = Image.open('resources/backdrop.png')
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


if __name__ == '__main__':
    if len(sys.argv) > 1:
        globals()[sys.argv[1]]()
    else:
        main()