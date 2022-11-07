import util

from bs4 import BeautifulSoup as bs

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="Youtube Thumbnail Embedder",
    description="An open source API that adds a play button to a youtube video thumbnail, provided the video ID. [Youtube Thumbnail Embedder](https://github.com/Snailedlt/Youtube-Thumbnail-Embedder) lets you embed Youtube videos into GitHub markdown with ease!",
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


@app.get("/{video_id}", response_class=HTMLResponse)
def get_thumbnail_w_play_button(video_id: str):
    """
    Returns a thumbnail image inside an anchor tag:
    ```html
    <a href='https://youtu.be/{video_id}'>
        {thumbnail_img}
    </a>
    ```
    """
    thumbnail_img = util.get_edited_thumbnail_html(video_id)
    html_output = f"""<a href='https://youtu.be/{video_id}'>
    {thumbnail_img}
    </a>
    """
    return bs(html_output, features="html.parser").prettify()
