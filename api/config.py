from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Markdown-Videos"
    app_description: str = (
        "An open source API that adds a play button and a backdrop to a video"
        " thumbnail, provided the video"
        " ID.<br/>[Markdown-Videos](https://github.com/Snailedlt/Youtube-Thumbnail-Embedder)"
        " lets you embed videos into GitHub markdown with ease! <br/> <br/>"
        " Documentation alternatives: [Redoc](/redoc) | [Swagger](/docs) | [GitHub"
        " README](https://github.com/Snailedlt/Youtube-Thumbnail-Embedder#readme) "
    )
    contact: object = {
        "name": "Jørgen Kalsnes Hagen",
        "url": "https://jorgenkh.no",
        "email": "jorgenkalsnes.hagen@gmail.com",
    }
    analytics_api_key: str = ""  # This gets filled out by the .env file
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
