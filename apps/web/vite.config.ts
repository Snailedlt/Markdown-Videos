/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { svelteTesting } from '@testing-library/svelte/vite'
import { withRelatedProject } from '@vercel/related-projects'

// On a Vercel preview deployment, use the API preview built from the same
// branch (see relatedProjects in vercel.json), so API changes can be tried
// from the website's preview. Production and local builds keep using
// VITE_API_BASE_URL.
const previewApi =
  process.env.VERCEL_ENV === 'preview'
    ? withRelatedProject({ projectName: 'markdown-videos-api', defaultHost: '' })
    : ''
if (previewApi) console.log(`Using the API preview at ${previewApi}`)

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte(), svelteTesting()],
  define: previewApi ? { 'import.meta.env.VITE_API_BASE_URL': JSON.stringify(previewApi) } : {},
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.ts'],
    env: { VITE_API_BASE_URL: 'https://api.example.test' },
    coverage: {
      provider: 'v8',
      include: ['src/**/*.{ts,svelte}'],
      exclude: ['src/**/*.test.ts', 'src/test/**', 'src/**/*.d.ts'],
      reporter: ['text', 'lcov', 'json-summary'],
    },
  },
})
