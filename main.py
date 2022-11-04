import util

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/{video_id}", response_class=HTMLResponse)
async def read_items(video_id: str):
    thumbnail_img = util.get_edited_thumbnail_img(video_id)
    return f"<a href='https://youtu.be/{video_id}'>{thumbnail_img}</a>"
