# Markdown-Videos Website

Created using `npm init vite`

Powered by Svelte, Vite, TypeScript, SCSS and the [Markdown-Videos api](http://markdown-videos-api.jorgenkh.no/)

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Svelte](https://marketplace.visualstudio.com/items?itemName=svelte.svelte-vscode).

## Local development

I recommend using the root [README](https://github.com/Snailedlt/Markdown-Videos/blob/main/README.md).

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
