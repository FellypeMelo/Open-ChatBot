import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Self-hosted fonts (offline / local-first — no external Google Fonts request).
import '@fontsource-variable/outfit/index.css'
import '@fontsource-variable/jetbrains-mono/index.css'
import '@fontsource/crimson-text/400.css'
import '@fontsource/crimson-text/400-italic.css'
import '@fontsource/crimson-text/600.css'
import '@fontsource/crimson-text/600-italic.css'
import '@fontsource/crimson-text/700.css'
import '@fontsource/crimson-text/700-italic.css'
import '@fontsource-variable/material-symbols-outlined/index.css'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// Register the PWA service worker for offline shell resilience. Guarded so
// it is a no-op in dev/test: `vite-plugin-pwa` only emits a service worker
// on a real `vite build` (import.meta.env.PROD), and the `serviceWorker`
// feature check keeps this inert under Vitest's jsdom environment (which
// has no navigator.serviceWorker) and in any browser without SW support.
// The dynamic import means 'virtual:pwa-register' is never resolved at all
// outside this branch, so it costs nothing in dev/test.
if (import.meta.env.PROD && typeof navigator !== 'undefined' && 'serviceWorker' in navigator) {
  import('virtual:pwa-register').then(({ registerSW }) => {
    registerSW({ immediate: true })
  })
}
