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
    # The following get filled out by the .env file
    analytics_api_key: str = ""
    # Optional: services that only offer thumbnails through an authenticated
    # API. Each one is switched off (answers 501) until its credentials are set.
    # Instagram and Facebook: a Meta app (https://developers.facebook.com/apps)
    # with oEmbed Read. Either the app ID + client token, or an access token.
    meta_app_id: str = ""
    meta_client_token: str = ""
    meta_access_token: str = ""
    # Twitch: an app from https://dev.twitch.tv/console/apps (client credentials)
    twitch_client_id: str = ""
    twitch_client_secret: str = ""
    # Reddit: a "script" or "web" app from https://www.reddit.com/prefs/apps
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
