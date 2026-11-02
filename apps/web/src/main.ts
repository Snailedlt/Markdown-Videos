import { hydrate, mount } from 'svelte'
import './app.css'
import App from './App.svelte'

const target = <HTMLElement>document.getElementById('app')

// The production build prerenders the page (scripts/prerender.mjs), so reuse
// that HTML. The dev server serves an empty #app, so build it from scratch.
const app = target.firstElementChild ? hydrate(App, { target }) : mount(App, { target })

export default app
