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
