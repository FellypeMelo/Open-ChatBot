import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    outDir: '../../static',
    emptyOutDir: true,
  },
  server: {
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
