import {
  defineConfig,
  devices,
} from '@playwright/test'

export default defineConfig({
  testDir: './e2e',

  fullyParallel: false,

  forbidOnly:
    Boolean(process.env.CI),

  retries:
    process.env.CI
      ? 2
      : 0,

  workers:
    process.env.CI
      ? 1
      : undefined,

  reporter: [
    [
      'html',
      {
        outputFolder: 'playwright-report',
        open: 'never',
      },
    ],
    [
      'list',
    ],
  ],

  use: {
    baseURL:
      'http://127.0.0.1:5173',

    trace:
      'retain-on-failure',

    screenshot:
      'only-on-failure',

    video:
      'retain-on-failure',

    viewport: {
      width: 1440,
      height: 1000,
    },
  },

  projects: [
    {
      name: 'chromium',

      use: {
        ...devices[
          'Desktop Chrome'
        ],
      },
    },
  ],

  webServer: [
    {
      command:
        'cd .. && uvicorn backend.app.main:app --host 127.0.0.1 --port 8000',

      url:
        'http://127.0.0.1:8000/health',

      reuseExistingServer:
        !process.env.CI,

      timeout:
        120000,
    },

    {
      command:
        'npm run dev -- --port 5173',

      url:
        'http://127.0.0.1:5173',

      reuseExistingServer:
        !process.env.CI,

      timeout:
        120000,

      env: {
        VITE_API_BASE_URL:
          'http://127.0.0.1:8000',
      },
    },
  ],
})