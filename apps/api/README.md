# Get Started

## How to use in GitHub Markdown

#### template

```markdown
[![Alt text](http://markdown-videos-api.jorgenkh.no/youtube/{video_id})](https://youtu.be/{video_id})
```
### example

```markdown
[![Pull Requests in 100 seconds](http://markdown-videos-api.jorgenkh.no/youtube/8lGpZkjnkt4)](https://youtu.be/8lGpZkjnkt4)
```

<details>
  <summary>Preview</summary>

  [![Pull Requests in 100 seconds](http://markdown-videos-api.jorgenkh.no/youtube/8lGpZkjnkt4)](https://youtu.be/8lGpZkjnkt4)
</details>

### How to use in HTML

### template

```html
<a href=https://youtu.be/{video_id}>
  <img src=http://markdown-videos-api.jorgenkh.no/youtube/{video_id} />
</a>
```

### example

```html
<a href=https://youtu.be/8lGpZkjnkt4>
  <img src=http://markdown-videos-api.jorgenkh.no/youtube/8lGpZkjnkt4 />
</a>
```

<details>
  <summary>Preview</summary>

<a href=https://youtu.be/8lGpZkjnkt4>
  <img src=http://markdown-videos-api.jorgenkh.no/youtube/8lGpZkjnkt4 />
</a>
</details>

---
## Supported services

| Service | Endpoint | Notes |
|---|---|---|
| YouTube | `/youtube/{video_id}`, `/youtube/{video_id}.gif` | The only service with animated GIFs |
| Vimeo | `/vimeo/{video_id}` | |
| Imgur | `/imgur/{video_id}` | Videos, GIFs and images (`imgur.com/ID`, `i.imgur.com/ID.mp4`). Not albums or galleries. |
| TikTok | `/url?url={tiktok_link}` | Needs the full link (`tiktok.com/@user/video/ID` or a `vm.tiktok.com` short link) |

Every service also works through `/url?url={link}`. Thumbnails from the newer services (Imgur, TikTok) keep their shape: frames with a different aspect ratio, such as vertical TikToks, sit on a blurred copy of themselves instead of being stretched.

## Documentation
For the full documentation see the Swagger and ReDoc docs
- [Swagger UI](https://github.com/swagger-api/swagger-ui) documentation: <http://markdown-videos-api.jorgenkh.no/docs>
- [ReDoc](https://github.com/Rebilly/ReDoc) documentation: <http://markdown-videos-api.jorgenkh.no/redoc>
### Optional parameters
|Name     |Data Type |Default Value                |Description                                                              |Example                                                                                                            |Availability               |
|---------|----------|-----------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|---------------------------|
|width    |int       |320                          |The width of the thumbnail                                               |http://markdown-videos-api.jorgenkh.no/youtube/8lGpZkjnkt4?width=320                                                   |All Endpoints              |
|height   |int       |180                          |The height of the thumbnail                                              |http://markdown-videos-api.jorgenkh.no/youtube/8lGpZkjnkt4?height=180                                                  |All Endpoints              |
|duration |int       |500                          |The duration you want to display each image in the gif (in milliseconds, 20–10000) |http://markdown-videos-api.jorgenkh.no/youtube/8lGpZkjnkt4.gif?duration=500                                            |Endpoints ending with .gif |
|filetype |str       |jpeg                         |Valid filetypes are: `jpeg`, `jpg`, `png`, `webp`, `bmp`, `gif`          |http://markdown-videos-api.jorgenkh.no/youtube/8lGpZkjnkt4.gif?filetype=jpeg                                           |All still-image endpoints  |
|url      |str       |https://youtu.be/dQw4w9WgXcQ |The url of the video you want the thumbnail of                           |http://markdown-videos-api.jorgenkh.no/url?url=https%3A%2F%2Fyoutu.be%2FdQw4w9WgXcQ&width=320&height=180&filetype=jpeg |/url                       |

Responses are cached by browsers, GitHub's image proxy and Vercel's CDN (`Cache-Control: public, max-age=86400, s-maxage=2592000`), so a changed YouTube thumbnail can take up to 30 days to show up.

Examples with multiple parameters:
- normal -> http://markdown-videos-api.jorgenkh.no/youtube/8lGpZkjnkt4?width=320&height=180&filetype=jpeg
- GIF -> http://markdown-videos-api.jorgenkh.no/youtube/8lGpZkjnkt4.gif?width=320&height=180&duration=500

## Contributing

Markdown Videos is still under development, please open an [issue](https://github.com/Snailedlt/Markdown-Videos/issues) if you find any bugs, or if you want to suggest new features

### Techstack

Made using
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)'s
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)

Hosted on
[![Vercel](https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)

### Local development
It is recommended that you follow [CONTRIBUTING.md](https://github.com/Snailedlt/Markdown-Videos/blob/main/CONTRIBUTING.md), which sets up the API and the website together

Install [pipenv](https://pipenv.pypa.io/en/latest/) if you haven't already

```sh
pip install --user pipenv
```

Install dependencies

```sh
pipenv install
```

#### Run Locally

```sh
pipenv dev # in development

# run the following in production environment
# pipenv start
```

ref: <https://fastapi.tiangolo.com/#run-it>

#### Running tests

For detailed instructions see the Fast API tutorial for [Testing](https://fastapi.tiangolo.com/tutorial/testing/)

```sh
pipenv test
```

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/H2H0GY0OU)
