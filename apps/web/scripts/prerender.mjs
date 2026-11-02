// Prerender the page into dist/index.html after `vite build`.
//
// The site is a single Svelte component. Without this step the HTML that
// search engines and link previews receive is an empty <div id="app">. Here
// the app is rendered on the server once, at build time, and the client then
// hydrates that HTML instead of building it from scratch (see src/main.ts).
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { createServer } from 'vite';

const root = fileURLToPath(new URL('..', import.meta.url));
const indexFile = fileURLToPath(new URL('../dist/index.html', import.meta.url));

const vite = await createServer({
  root,
  mode: 'production',
  logLevel: 'warn',
  appType: 'custom',
  server: { middlewareMode: true, hmr: false, ws: false },
});

try {
  const { default: App } = await vite.ssrLoadModule('/src/App.svelte');
  const { render } = await vite.ssrLoadModule('svelte/server');
  const { body, head } = render(App);

  const html = await readFile(indexFile, 'utf8');
  const placeholder = '<div id="app"></div>';
  if (!html.includes(placeholder)) {
    throw new Error(`${indexFile} has no ${placeholder} to fill`);
  }
  const out = html.replace(placeholder, `<div id="app">${body}</div>`).replace('</head>', `${head}</head>`);
  await writeFile(indexFile, out);
  console.log(`Prerendered dist/index.html (${Math.round(body.length / 1024)} kB of HTML)`);
} finally {
  await vite.close();
}
