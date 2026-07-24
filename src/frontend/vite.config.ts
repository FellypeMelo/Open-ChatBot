import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

// Same-origin backend routes this app calls (src/frontend/src/services/api.ts).
// The service worker must NEVER cache these -- live chat/streaming/settings
// data would otherwise go stale. Matched against the full request URL so it
// works regardless of host (localhost, 127.0.0.1, or a LAN IP).
const API_ROUTE_PATTERN =
  /^https?:\/\/[^/]+\/(chat|characters|users|tags|settings|lore|presets|history|chats)(?:\/|\?|$)/

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      // Service worker + workbox runtime only -- the web app manifest is
      // authored by hand at public/manifest.webmanifest and linked from
      // index.html, so PWA-plugin manifest generation/injection is disabled
      // to avoid a second, conflicting manifest.
      manifest: false,
      injectRegister: false,
      registerType: 'autoUpdate',
      // Never run in `vite dev`/Vitest -- only a real `vite build` emits a
      // service worker, keeping tests and local dev unaffected.
      devOptions: { enabled: false },
      workbox: {
        // Precache ONLY the hashed build shell (JS/CSS/self-hosted fonts,
        // including the Material Symbols icon font) plus the app-shell HTML
        // navigateFallback needs -- never the runtime-written avatar
        // uploads that also live under static/.
        globPatterns: ['assets/**/*.{js,css,woff,woff2}', 'index.html'],
        cleanupOutdatedCaches: true,
        navigateFallback: '/index.html',
        runtimeCaching: [
          {
            urlPattern: API_ROUTE_PATTERN,
            handler: 'NetworkOnly',
          },
        ],
      },
    }),
  ],
  build: {
    outDir: '../../static',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        // Function form (not the object form) so the type checker resolves
        // the correct Rollup overload; keeps the vendor React runtime in its
        // own long-lived chunk, separate from the app code that changes far
        // more often.
        manualChunks(id: string) {
          if (id.includes('node_modules/react-dom') || id.includes('node_modules/react/')) {
            return 'vendor-react'
          }
        },
      },
    },
  },
  server: {
    // Bind to all interfaces so the dev server is reachable from other
    // devices on the LAN (e.g. a phone). Vite prints the Network: URL.
    host: true,
    proxy: {
      '/chat': 'http://localhost:8000',
      '/characters': 'http://localhost:8000',
      '/users': 'http://localhost:8000',
      '/tags': 'http://localhost:8000',
      '/stats': 'http://localhost:8000',
      '/settings': 'http://localhost:8000',
      '/lore': 'http://localhost:8000',
      '/presets': 'http://localhost:8000',
      '/history': 'http://localhost:8000',
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
    exclude: ['**/e2e/**', '**/node_modules/**', '**/dist/**'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['**/e2e/**', '**/*.config.*', '**/src/test/**'],
      thresholds: {
        statements: 80,
        branches: 80,
        functions: 80,
        lines: 80,
      },
    },
  },
})
