from src import util, config, providers

from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from io import BytesIO
from fastapi import Depends, FastAPI, HTTPException, Path, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from typing_extensions import Annotated
from api_analytics.fastapi import Analytics
from starlette.responses import RedirectResponse


@lru_cache()
def get_settings():
    return config.Settings()


app = FastAPI(
    title=get_settings().app_name,
    description=get_settings().app_description,
    version="0.4.0",
    terms_of_service="https://choosealicense.com/licenses/mit/",
    contact=get_settings().contact,
    license_info={
        "name": "MIT License",
        "url": "https://choosealicense.com/licenses/mit/",
    },
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
if get_settings().analytics_api_key is not None:
    app.add_middleware(Analytics, api_key=get_settings().analytics_api_key)


# Thumbnails almost never change, so let browsers, GitHub's image proxy (camo)
# and Vercel's edge cache keep them. Repeat views are then served from the CDN
# and never invoke the (metered) serverless function.
#   max-age:                 browsers / camo keep it for a day
#   s-maxage:                Vercel's edge keeps it for 30 days
#   stale-while-revalidate:  serve the cached copy while refreshing it
CACHE_CONTROL = "public, max-age=86400, s-maxage=2592000, stale-while-revalidate=86400"

# Upper bounds keep a single request from doing an unreasonable amount of work.
MAX_WIDTH = 1920
MAX_HEIGHT = 1080
Width = Annotated[int, Query(ge=1, le=MAX_WIDTH, description="Width in pixels")]
Height = Annotated[int, Query(ge=1, le=MAX_HEIGHT, description="Height in pixels")]
GIF_FRAMES = 4


def image_response(image, filetype: str, **save_kwargs) -> Response:
    buffer = BytesIO()
    image.save(buffer, format=filetype.upper(), **save_kwargs)
    return Response(
        buffer.getvalue(),
        media_type=f"image/{filetype}",
        headers={"Cache-Control": CACHE_CONTROL},
    )


def youtube_frame(video_id: str, frame: int, width: int, height: int):
    """Frame 0 is the main thumbnail; frames 1-3 are YouTube's auto-generated stills."""
    if frame == 0:
        base_url = f"https://img.youtube.com/vi/{video_id}"
        image = util.read_img_from_url(
            url=f"{base_url}/maxresdefault.jpg", alt_url=f"{base_url}/0.jpg"
        )
    else:
        image = util.read_img_from_url(f"https://i.ytimg.com/vi/{video_id}/{frame}.jpg")
    return util.add_play_button_to_thumbnail(
        image.convert("RGB").resize((width, height)), "src/img/youtube_play_button.png"
    )


@app.get("/youtube/{video_id}.gif", tags=["Youtube"])
def youtube_gif_thumbnail(
    video_id: str,
    width: Width = 320,
    height: Height = 180,
    duration: int = Query(
        500,
        ge=20,
        le=10000,
        description="Duration for each image in the GIF (measured in milliseconds)",
    ),
) -> Response:
    # Download the frames in parallel: the function is billed by wall-clock time,
    # and most of that time is spent waiting on YouTube.
    with ThreadPoolExecutor(max_workers=GIF_FRAMES) as pool:
        frames = list(
            pool.map(
                lambda i: youtube_frame(video_id, i, width, height), range(GIF_FRAMES)
            )
        )
    return image_response(
        frames[0],
        "gif",
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=duration,
    )


@app.get("/youtube/{video_id}", tags=["Youtube"])
def youtube_thumbnail(
    video_id: str,
    width: Width = 320,
    height: Height = 180,
    filetype: util.Supported_Filetype = util.Supported_Filetype.JPEG,
) -> Response:
    return image_response(youtube_frame(video_id, 0, width, height), filetype.value)


@app.get("/vimeo/{video_id}", tags=["Vimeo"])
def vimeo_thumbnail(
    video_id: str,
    width: Width = 320,
    height: Height = 180,
    filetype: util.Supported_Filetype = util.Supported_Filetype.JPEG,
) -> Response:
    image = util.add_play_button_to_thumbnail(
        util.read_img_from_url(f"https://vumbnail.com/{video_id}.jpg")
        .convert("RGB")
        .resize((width, height)),
        "src/img/vimeo_play_button.png",
    )
    return image_response(image, filetype.value)


@app.get("/info", tags=["Meta"])
async def info(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {
        "app_name": settings.app_name,
        "app_description": settings.app_description,
        "contact": settings.contact,
        "analytics_api_key": settings.analytics_api_key,
    }


def _provider_endpoint(provider: providers.Provider):
    def endpoint(
        video_id: str = Path(pattern=f"^{provider.id_pattern}$"),
        width: Width = 320,
        height: Height = 180,
        filetype: util.Supported_Filetype = util.Supported_Filetype.JPEG,
    ) -> Response:
        image = providers.thumbnail(provider, video_id, width, height)
        return image_response(image, filetype.value)

    endpoint.__name__ = f"{provider.key}_thumbnail"
    return endpoint


# /imgur/{video_id}, ... for services whose thumbnails can be found from the ID
for _provider in providers.PROVIDERS:
    if _provider.id_route:
        app.add_api_route(
            f"/{_provider.key}/{{video_id}}",
            _provider_endpoint(_provider),
            methods=["GET"],
            tags=[_provider.name],
            summary=f"{_provider.name} thumbnail",
        )


SUPPORTED_SERVICES = "YouTube, Vimeo, " + ", ".join(p.name for p in providers.PROVIDERS)


@app.get(
    "/url",
    tags=["URL"],
    description=f"Get a thumbnail from a video link ({SUPPORTED_SERVICES})",
)
def url_to_thumbnail(
    url: str = "https://youtu.be/dQw4w9WgXcQ",
    width: Width = 320,
    height: Height = 180,
    filetype: util.Supported_Filetype = util.Supported_Filetype.JPEG,
) -> Response:
    video_id = None
    try:
        video_id = util.get_video_id_by_url(url, util.URL_Regex.YOUTUBE)
        if video_id is not None:
            return youtube_thumbnail(video_id, width, height, filetype)
        video_id = util.get_video_id_by_url(url, util.URL_Regex.VIMEO)
        if video_id is not None:
            return vimeo_thumbnail(video_id, width, height, filetype)
        matched = providers.match(url)
        if matched is not None:
            provider, video_id = matched
            image = providers.thumbnail(provider, video_id, width, height)
            return image_response(image, filetype.value)
        raise HTTPException(
            status_code=400,
            detail=(
                f"{url} is an unsupported or invalid url. Supported services:"
                f" {SUPPORTED_SERVICES}."
            ),
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=406,
            detail={
                "attempted url": url,
                "found video_id": video_id,
                "message": (
                    f"{url} is not supported, is invalid or was parsed incorrectly."
                    f" Supported services: {SUPPORTED_SERVICES}. Here's the"
                    f" video_id that was parsed from the url: {video_id}. If you"
                    " think this is a mistake, please open an issue here:"
                    " https://github.com/Snailedlt/Markdown-Videos/issues"
                ),
            },
        )


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")
