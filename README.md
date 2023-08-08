# Markdown Videos
[![wakatime](https://wakatime.com/badge/github/Snailedlt/Markdown-Videos.svg)](https://wakatime.com/badge/github/Snailedlt/Markdown-Videos)
![Vercel](https://therealsujitk-vercel-badge.vercel.app/?app=markdown-videos)
![License](https://img.shields.io/badge/license-MIT-blue)
![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

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

## How to use?

The simplest way to use markdown-videos is to use [the website](https://markdown-videos.vercel.app/).

If you want to use the API, see the [API README](https://github.com/Snailedlt/Markdown-Videos/blob/main/apps/api/README.md)

## Contributing

Markdown Videos is still under development, please open an [issue](https://github.com/Snailedlt/Markdown-Videos/issues) if you find any bugs, or if you want to suggest new features.

I also accept and highly appreciate Pull Requests. If you have anything to contribute, please read on.

### Local development

### Prerequisites

- [python](https://www.python.org/downloads/) 3.8 or higher
- [pipenv](https://pipenv.pypa.io/en/latest/)
- [pnpm](https://pnpm.io/installation)

Wanna work only with the python or javascript stuff? check out [Additional info](#additional-info)

### install, run, build, etc...

install dependencies

```sh
pnpm install # installs web dependencies
pnpm api:install # installs api dependencies
```

run the api and website

```sh
pnpm dev
```

If you make changes make sure to run linting and testing before opening a PR

```sh
pnpm lint
pnpm test
```

## Additional info

In case you want more documentation on either the website or the api.

The API is built with Python, FastAPI, Pillow and Pipenv
- [API README](https://github.com/Snailedlt/Markdown-Videos/blob/main/apps/api/README.md)

The website is built with Svelte, Vite, Typescript, SCSS and pnpm
- [Website README](https://github.com/Snailedlt/Markdown-Videos/blob/main/apps/web/README.md)