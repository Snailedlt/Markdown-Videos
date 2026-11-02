import { mount } from 'svelte'
import './app.css'
import App from './App.svelte'

const app = mount(App, {
  target: <HTMLElement>document.getElementById('app'),
})

export default app
