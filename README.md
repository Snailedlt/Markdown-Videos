# Markdown Videos
![Vercel](https://therealsujitk-vercel-badge.vercel.app/?app=markdown-videos) ![License](https://img.shields.io/badge/license-MIT-blue)

An open source API that adds a play button to a youtube video thumbnail, provided the video ID.
Markdown Videos lets you embed Youtube videos into GitHub markdown with ease!

## Showcase

||Preview|Info|
|--|--|--|
|Before|https://youtu.be/8lGpZkjnkt4|<ul><li>No Preview</li><li>Redirects to video</li></ul>|
|After|[![](https://markdown-videos.vercel.app/youtube/8lGpZkjnkt4)](https://youtu.be/8lGpZkjnkt4)|<ul><li>Clearly shows it's a youtube video</li><li>Play button and backdrop added</li><li>Black bars removed</li><li>Redirects to video</li></ul>|
|After (GIF)|[![](https://markdown-videos.vercel.app/youtube/8lGpZkjnkt4.gif)](https://youtu.be/8lGpZkjnkt4.gif)|<ul><li>Clearly shows it's a youtube video</li><li>Play button and backdrop added</li><li>:sparkles: Animated GIF :sparkles: </li><li>Redirects to video</li></ul>|


## Supported video services

- [x] Youtube
- [x] Vimeo

---
## Get Started

### How to use in GitHub Markdown

#### template

```markdown
[![](https://markdown-videos.vercel.app/youtube/{video_id})](https://youtu.be/{video_id})
```
#### example

```markdown
[![](https://markdown-videos.vercel.app/youtube/8lGpZkjnkt4)](https://youtu.be/8lGpZkjnkt4)
```

<details>
  <summary>Preview</summary>

  [![](https://markdown-videos.vercel.app/youtube/8lGpZkjnkt4)](https://youtu.be/8lGpZkjnkt4)
</details>

### How to use in HTML

#### template

```html
<a href=https://youtu.be/{video_id}><img src=https://markdown-videos.vercel.app/youtube/{video_id}></a></img>
```

#### example

```html
<a href=https://youtu.be/8lGpZkjnkt4><img src=https://markdown-videos.vercel.app/youtube/8lGpZkjnkt4></a></img>
```

<details>
  <summary>Preview</summary>

  <a href=https://youtu.be/8lGpZkjnkt4><img src=https://markdown-videos.vercel.app/youtube/8lGpZkjnkt4></a></img>
</details>

---
## Documentation
For the full documentation see the Swagger and ReDoc docs
- [Swagger UI](https://github.com/swagger-api/swagger-ui) documentation: <https://markdown-videos.vercel.app/docs>
- [ReDoc](https://github.com/Rebilly/ReDoc) documentation: <https://markdown-videos.vercel.app/redoc>
### Optional parameters
|Name     |Data Type |Default Value             |Description                                                              |Example                                                             |Availability               |
|---------|----------|--------------------------|-------------------------------------------------------------------------|--------------------------------------------------------------------|---------------------------|
|width    |int       |320                       |The width of the thumbnail                                               |https://markdown-videos.vercel.app/youtube/8lGpZkjnkt4?width=320    |All Endpoints              |
|height   |int       |180                       |The height of the thumbnail                                              |https://markdown-videos.vercel.app/youtube/8lGpZkjnkt4?height=180   |All Endpoints              |
|duration |int       |500                       |The duration you want to display each image in the gif (in milliseconds) |https://markdown-videos.vercel.app/youtube/8lGpZkjnkt4.gif?duration=500 |Endpoints ending with .gif |

Examples with multiple parameters:
- normal -> https://markdown-videos.vercel.app/youtube/8lGpZkjnkt4?width=320&height=180
- GIF -> https://markdown-videos.vercel.app/youtube/8lGpZkjnkt4.gif?width=320&height=180&duration=500

## Contributing

Markdown Videos is still under development, please open an [issue](https://github.com/Snailedlt/Markdown-Videos/issues) if you find any bugs, or if you want to suggest new features

### Techstack

Made using [Python](https://www.python.org/)'s [FastAPI](https://fastapi.tiangolo.com/) framework, and hosted by [Vercel](https://vercel.com/)

### Building

#### Install Dependencies

```sh
pip install -r requirements.txt
```

#### Run Locally

```sh
uvicorn main:app --reload
```

or if that doesn't work:

```sh
python -m uvicorn main:app --reload
```

ref: <https://fastapi.tiangolo.com/#run-it>

#### Update dependencies

Needed only when new dependencies are added

```sh
pip install pipreqs # https://pypi.org/project/pipreqs/
# cd into the project
pipreqs # updates requirements.txt
```
