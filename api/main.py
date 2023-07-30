from . import util, config

from functools import lru_cache
from io import BytesIO
from fastapi import Depends, FastAPI, Query, Response
from typing_extensions import Annotated
from api_analytics.fastapi import Analytics
from starlette.responses import RedirectResponse


@lru_cache()
def get_settings():
    return config.Settings()


app = FastAPI(
    title=get_settings().app_name,
    description=get_settings().app_description,
    version="0.0.1-alpha",
    terms_of_service="https://choosealicense.com/licenses/mit/",
    contact=get_settings().contact,
    license_info={
        "name": "MIT License",
        "url": "https://choosealicense.com/licenses/mit/",
    },
)
app.add_middleware(
    Analytics, api_key=get_settings().analytics_api_key
)  # Add middleware


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


@app.get("/info", tags=["Meta"])
async def info(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {
        "app_name": settings.app_name,
        "app_description": settings.app_description,
        "contact": settings.contact,
    }


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")
