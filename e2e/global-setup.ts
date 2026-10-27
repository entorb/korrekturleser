import { execFileSync } from "node:child_process"
import process from "node:process"

// Fresh e2e DB state: mock user 1 (secret "test"), one usage row for stats page.
// Mock LLM skips usage writes, so stats come only from this seed.
// Same DB_PATH as backend webServer in playwright.config.ts
const SEED = `
from shared.helper_db import sqlite_connection
with sqlite_connection() as con:
    con.execute("DELETE FROM history")
    con.execute("INSERT INTO history VALUES ('2026-01-01', 1, 3, 300)")
    con.commit()
`

export default function globalSetup() {
  // eslint-disable-next-line sonarjs/no-os-command-from-path -- dev/CI tool from PATH
  execFileSync("uv", ["run", "--no-build", "python", "-c", SEED], {
    env: { ...process.env, DB_PATH: "db-e2e.sqlite", LLM_PROVIDERS: "Mock" },
    stdio: "inherit",
  })
}
