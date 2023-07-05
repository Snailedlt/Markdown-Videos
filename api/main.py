from io import BytesIO
from . import util
from fastapi import FastAPI, Query, Response
from starlette.responses import RedirectResponse

app = FastAPI(
    title="Youtube Thumbnail Embedder",
    description=(
        "An open source API that adds a play button and a backdrop to a video"
        " thumbnail, provided the video ID.<br/>"
        "[MardownVideos](https://github.com/Snailedlt/Youtube-Thumbnail-Embedder)"
        " lets you embed videos into GitHub markdown with ease!"
    ),
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


@app.get("/youtube/{video_id}.gif", tags=["Youtube"])
def youtube_gif_thumbnail(
    video_id: str,
    width: int = 320,
    height: int = 180,
    duration: int = Query(
        500, description="Duration for each image in the GIF (measured in milliseconds)"
    ),
) -> Response:
    base_url = f"https://img.youtube.com/vi/{video_id}"
    first = util.add_play_button_to_thumbnail(
        util.read_img_from_url(
            url=f"{base_url}/maxresdefault.jpg",
            alt_url=f"{base_url}/0.jpg",
        ).resize((width, height)),
        "api/img/youtube_play_button.png",
    )
    following = (
        util.add_play_button_to_thumbnail(
            util.read_img_from_url(
                f"https://i.ytimg.com/vi/{video_id}/{i+1}.jpg"
            ).resize((width, height)),
            "api/img/youtube_play_button.png",
        )
        for i in range(3)
    )
    buffer = BytesIO()
    first.save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=following,
        loop=0,
        duration=duration,
    )
    return Response(buffer.getvalue(), media_type="image/gif")


@app.get("/youtube/{video_id}", tags=["Youtube"])
def youtube_thumbnail(
    video_id: str,
    width: int = 320,
    height: int = 180,
    filetype: util.Supported_Filetype = "jpeg",
) -> Response:
    base_url = f"https://img.youtube.com/vi/{video_id}"
    image = util.add_play_button_to_thumbnail(
        util.read_img_from_url(
            url=f"{base_url}/maxresdefault.jpg",
            alt_url=f"{base_url}/0.jpg",
        ).resize((width, height)),
        "api/img/youtube_play_button.png",
    )
    buffer = BytesIO()
    image.save(buffer, format=filetype.upper())
    return Response(buffer.getvalue(), media_type=f"image/{filetype}")


@app.get("/vimeo/{video_id}", tags=["Vimeo"])
def vimeo_thumbnail(
    video_id: str,
    width: int = 320,
    height: int = 180,
    filetype: util.Supported_Filetype = "jpeg",
) -> Response:
    image = util.add_play_button_to_thumbnail(
        util.read_img_from_url(f"https://vumbnail.com/{video_id}.jpg").resize(
            (width, height)
        ),
        "api/img/vimeo_play_button.png",
    )
    buffer = BytesIO()
    image.save(buffer, format=filetype.upper())
    return Response(buffer.getvalue(), media_type=f"image/{filetype}")


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")
