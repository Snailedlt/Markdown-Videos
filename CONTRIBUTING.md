# Contributing to Markdown Videos

Thanks for wanting to help! You can contribute by:

- **Reporting a bug or suggesting a feature:** [open an issue](https://github.com/Snailedlt/Markdown-Videos/issues).
- **Fixing something:** if you know how to solve an issue, open a pull request and I'll review it promptly. Issues labelled [`good first issue`](https://github.com/Snailedlt/Markdown-Videos/labels/good%20first%20issue) are a nice place to start.
- **Supporting the project:** [buy me a coffee on Ko-fi](https://ko-fi.com/H2H0GY0OU).

## Project layout

This is a [pnpm](https://pnpm.io) + [Turborepo](https://turbo.build) monorepo with two apps:

| Folder | What | Built with |
|---|---|---|
| [`apps/api`](apps/api) | The API that turns a video link into a thumbnail with a play button | Python, FastAPI, Pillow, Pipenv |
| [`apps/web`](apps/web) | The website ([markdown-videos.jorgenkh.no](https://markdown-videos.jorgenkh.no)) | Svelte 5, Vite, TypeScript |

Both are deployed to Vercel. Each app also has its own README with app-specific details.

## Development setup

### Option 1: dev container (nothing to install)

The repo has a [dev container](.devcontainer/devcontainer.json) with Python, Node, pnpm and pipenv, and it installs all dependencies for you. Open the repo in any of these:

- **GitHub Codespaces:** on GitHub, click **Code → Codespaces → Create codespace**.
- **[Ona](https://ona.com)** (formerly Gitpod), which also uses dev containers.
- **VS Code** with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension and Docker: run **Dev Containers: Reopen in Container**.

When setup finishes, run `pnpm dev`. The website opens on port 5173 and the API runs on port 8000.

> **Codespaces:** the setup script points the website at the API's forwarded URL. Make port 8000 **public** in the Ports panel so the browser can load thumbnails from it.

### Option 2: on your own machine

Prerequisites:

- [Python](https://www.python.org/downloads/) 3.11 or higher
- [pipenv](https://pipenv.pypa.io/en/latest/)
- [Node.js](https://nodejs.org/en) 20.19 or higher
- [pnpm](https://pnpm.io/installation)

I recommend [VS Code](https://code.visualstudio.com/) with the workspace's [recommended extensions](https://code.visualstudio.com/docs/editor/extension-marketplace#_recommended-extensions).

Install the dependencies:

```sh
pnpm install      # website and tooling
pnpm api:install  # API (runs pipenv install)
```

Create a `.env` file from the example. The default points the website at your local API:

```sh
cp .env.example .env
```

Start the API and the website together:

```sh
pnpm dev
```

Want to work on only one app? See the [API README](apps/api/README.md) or the [website README](apps/web/README.md).

## Before you open a pull request

Run the linters and tests:

```sh
pnpm lint
pnpm test
```

`pnpm test:coverage` also shows test coverage for both apps.

- **Website tests** use Vitest and Testing Library and live next to the code (`apps/web/src/**/*.test.ts`).
- **API tests** use pytest and live in `apps/api/tests`. Some of them download real thumbnails from YouTube and Vimeo, so they need internet access.

### What CI runs

Every pull request runs the **Build and Test** workflow. It only runs the checks for the app you changed:

- `apps/web/**`: website build, tests and lint.
- `apps/api/**`: API tests and lint on Python 3.11, 3.13 and 3.14.
- Shared files (the lockfile, root `package.json`, the workflow): both.
- Docs-only changes: the checks pass straight away.

Each run's summary page shows test coverage.

## Code style

- **Python:** [PEP 8](https://peps.python.org/pep-0008/), linted with [ruff](https://docs.astral.sh/ruff/) (`apps/api/ruff.toml`) and formatted with [black](https://black.readthedocs.io/).
- **TypeScript and Svelte:** checked with `svelte-check` and formatted with Prettier.

The VS Code workspace settings format files on save with these tools.

> **Don't add an `apps/api/pyproject.toml`.** Vercel installs the API's dependencies from `pyproject.toml` when one exists, instead of from `Pipfile.lock`. Tool settings go in their own files (`ruff.toml`, `.coveragerc`).
