# Youtube Thumbnail Embedder

An open source API that adds a play button to a youtube video thumbnail, provided the video ID.

This lets you embed Youtube videos into GitHub markdown with ease!

## Usage

### Documentation

- [Swagger UI](https://github.com/swagger-api/swagger-ui) documentation: <http://127.0.0.1:8000/docs>
- [ReDoc](https://github.com/Rebilly/ReDoc) documentation: <http://127.0.0.1:8000/redoc>

### How to use in GitHub Markdown

*This is still a WIP feature, and will be updated*

#### template

```md
[![](http://127.0.0.1:8000/{video_id})](https://youtu.be/{video_id})
```

#### example

```md
[![](http://127.0.0.1:8000/WHyOHQ_GkNo)](https://youtu.be/WHyOHQ_GkNo)
```

## Techstack

Made using [Python](https://www.python.org/)'s [FastAPI](https://fastapi.tiangolo.com/) framework

## Building

### Install Dependencies

`pip install fastapi`
`pip install "uvicorn[standard]"`
ref: https://fastapi.tiangolo.com/#installation

### Run Locally
`uvicorn main:app --reload` or if that doesn't work: `python -m uvicorn main:app --reload`
ref: https://fastapi.tiangolo.com/#run-it
