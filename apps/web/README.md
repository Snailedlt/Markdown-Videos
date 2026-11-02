# Markdown-Videos Website

Created using `npm init vite`

Powered by Svelte, Vite, TypeScript and the [Markdown-Videos api](http://markdown-videos-api.jorgenkh.no/)

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Svelte](https://marketplace.visualstudio.com/items?itemName=svelte.svelte-vscode).

## Local development

I recommend following [CONTRIBUTING.md](https://github.com/Snailedlt/Markdown-Videos/blob/main/CONTRIBUTING.md), which sets up the API and the website together.

If you wish to only develop using svelte, keep in mind that it might not work, since this documentation is rarely updated. You might have to install additional packages and change the `package.json` scripts. If you're still willing to try, do the following.

Add a `.env` file in the `/apps/web` dir with the following code:

```yaml
VITE_API_BASE_URL="http://markdown-videos-api.jorgenkh.no" # replace with "http://127.0.0.1:8000" if you're running the markdown-videos api locally
```

install dependencies and start the development server

```sh
pnpm install
pnpm dev
```

lint

```sh
pnpm lint
```

## Testing

Tests use [Vitest](https://vitest.dev/) with [Testing Library](https://testing-library.com/docs/svelte-testing-library/intro) in a jsdom browser environment. They live next to the code they test (`src/**/*.test.ts`).

```sh
pnpm test        # run once
pnpm test:watch  # re-run on changes
```

- `src/lib/video.test.ts`: link parsing (including `?si=` links), image URLs and the Markdown/HTML snippets
- `src/lib/highlight.test.ts`: the syntax highlighter keeps the text intact and never lets code inject markup
- `src/lib/Generator.test.ts`: the generator itself: paste a link, see the thumbnail and code, switch tabs, copy, errors and options
