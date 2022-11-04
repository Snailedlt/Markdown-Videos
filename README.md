# Youtube Thumbnail Embedder

An open source API that adds a play button to a youtube video thumbnail, provided the video ID.
Youtube Thumbnail Embedder lets you embed Youtube videos into GitHub markdown with ease!

## Showcase

||Preview|Info|
|--|--|--|
|Before|![image](https://user-images.githubusercontent.com/43886029/200039001-212c6961-7220-472a-aa5d-1083a7770873.png)|<ul><li>Hard to see that it's a video</li><li>No play button</li><li>Black bars around thumbnail</li></ul>|
|After|![image](https://user-images.githubusercontent.com/43886029/200038762-abd67dd6-d72d-43e9-94b7-9fd0d57b87a4.png)|<ul><li>Clearly shows it's a video</li><li>Play button and backdrop added</li><li>Black bars removed</li></ul>|

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

```sh
pip install fastapi
pip install "uvicorn[standard]"
```

ref: <https://fastapi.tiangolo.com/#installation>

### Run Locally

```sh
uvicorn main:app --reload
```

or if that doesn't work:

```sh
python -m uvicorn main:app --reload
```

ref: <https://fastapi.tiangolo.com/#run-it>
