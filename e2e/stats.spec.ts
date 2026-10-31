import { expect, test as it } from "@playwright/test"

import { login } from "./helpers.ts"

// usage row seeded in e2e/global-setup.ts
it("shows usage statistics", async ({ page }) => {
  await login(page)

  await page.locator('button:has(i:has-text("bar_chart"))').click()
  await expect(page.getByText("Gesamt")).toBeVisible()
  await expect(page.getByText("Täglich")).toBeVisible()
  await expect(page.locator("tbody", { hasText: "Torben" })).toHaveCount(2)
})
