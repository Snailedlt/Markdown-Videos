import { mount } from 'svelte'
import { inject } from '@vercel/analytics'
import './app.css'
import App from './App.svelte'

// Vercel Web Analytics: anonymous page views, no cookies
inject()

const app = mount(App, {
  target: <HTMLElement>document.getElementById('app'),
})

export default app
