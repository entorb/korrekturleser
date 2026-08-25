import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  timeout: 10_000,
  fullyParallel: false,
  workers: 4,
  quiet: true,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:5173/korrekturleser-vue/',
    trace: 'on-first-retry'
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    {
      command:
        'LLM_PROVIDERS=Mock uv run uvicorn fastapi_app.main:app --host localhost --port 9002',
      url: 'http://localhost:9002/health',
      reuseExistingServer: !process.env.CI,
      timeout: 120_000
    },
    {
      command: 'pnpm dev',
      url: 'http://localhost:5173/korrekturleser-vue/',
      reuseExistingServer: !process.env.CI,
      timeout: 120_000
    }
  ]
})
