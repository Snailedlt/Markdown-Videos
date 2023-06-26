import util
from platforms import Platforms

from bs4 import BeautifulSoup as bs

from fastapi import FastAPI

app = FastAPI(
    title="Youtube Thumbnail Embedder",
    description="An open source API that adds a play button and a backdrop to a video thumbnail, provided the video ID.<br/>[Mardown Videos](https://github.com/Snailedlt/Youtube-Thumbnail-Embedder) lets you embed videos into GitHub markdown with ease!",
    version="0.0.1-alpha",
    terms_of_service="https://choosealicense.com/licenses/mit/",
    contact={
        "name": "Jørgen Kalsnes Hagen",
        "url": "https://github.com/Snailedlt",
        "email": "jorgenkalsnes.hagen@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://choosealicense.com/licenses/mit/",
    },
)


@app.get('/youtube/{video_id}')
def youtube_thumbnail (video_id: str, width: int = 320, height: int = 180):
    image = util.get_edited_thumbnail_img(
        platform = Platforms.youtube,
        video_id = video_id,
        width = width,
        height = height,
        )
    return util.img_to_streaming_response(image)


@app.get('/vimeo/{video_id}')
def vimeo_thumbnail (video_id: str, width: int = 320, height: int = 180):
    image = util.get_edited_thumbnail_img(
        platform = Platforms.vimeo,
        video_id = video_id,
        width = width,
        height = height,
        )
    return util.img_to_streaming_response(image)
