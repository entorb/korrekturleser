import process from "node:process"
import { defineConfig, devices } from "@playwright/test"

// e2e uses its own DB, auto-created with mock user (secret "test")
const E2E_ENV = "DB_PATH=db-e2e.sqlite LLM_PROVIDERS=Mock"

export default defineConfig({
  testDir: "./e2e",
  timeout: 10_000,
  fullyParallel: false,
  workers: 4,
  quiet: true,
  retries: 0,
  reporter: "list",
  globalSetup: "./e2e/global-setup.ts",
  use: {
    baseURL: "http://localhost:5173/korrekturleser-vue/",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `${E2E_ENV} uv run uvicorn fastapi_app.main:app --host localhost --port 9002`,
      url: "http://localhost:9002/health",
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: "pnpm dev",
      url: "http://localhost:5173/korrekturleser-vue/",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  ],
})
