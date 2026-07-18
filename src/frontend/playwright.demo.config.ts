import { defineConfig, devices } from '@playwright/test';

// Dedicated config for capturing the demo GIF. Records video, single worker,
// hides no output. Reuses the E2E backend (E2E_TESTING=1, no LLM needed).
export default defineConfig({
  testDir: './e2e',
  testMatch: 'demo-showcase.spec.ts',
  fullyParallel: false,
  workers: 1,
  reporter: 'list',
  timeout: 120_000,
  use: {
    baseURL: 'http://localhost:5173',
    viewport: { width: 1120, height: 680 },
    video: { mode: 'on', size: { width: 1120, height: 680 } },
    trace: 'off',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1120, height: 680 } },
    },
  ],
  webServer: [
    {
      command:
        'venv\\Scripts\\python.exe -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000',
      cwd: 'G:\\Programas\\Open-ChatBot',
      port: 8000,
      timeout: 120_000,
      reuseExistingServer: true,
      env: { E2E_TESTING: '1' },
    },
    {
      command: 'pnpm run dev',
      port: 5173,
      timeout: 120_000,
      reuseExistingServer: true,
    },
  ],
});
