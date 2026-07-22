import { defineConfig, devices } from '@playwright/test';

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  testDir: './e2e',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retries on CI */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests */
  workers: 1,
  /* Reporter */
  reporter: 'html',
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: 'http://localhost:5173',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
  },

  /* Configure projects for major browsers and devices */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: [
    {
      command: 'cd ../.. && node -e "const fs=require(\'fs\'); try{ fs.unlinkSync(\'e2e_test.db\'); }catch(e){}" && venv\\Scripts\\python -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000',
      port: 8000,
      timeout: 120 * 1000,
      // Always spin up a fresh, E2E_TESTING=1 backend -- never reuse whatever
      // happens to already be listening on 8000 (e.g. a developer's normal
      // `run.bat` instance), which would point e2e specs at the real
      // chatbot.db/chroma_db instead of the isolated e2e_test.db.
      reuseExistingServer: false,
      env: { E2E_TESTING: '1' }
    },
    {
      command: 'pnpm run dev',
      port: 5173,
      timeout: 120 * 1000,
      reuseExistingServer: !process.env.CI,
    }
  ],
});
