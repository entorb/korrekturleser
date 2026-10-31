import { expect, test as it, test } from "@playwright/test"

import { login } from "./helpers.ts"

it("processes text with the Mock provider", async ({ page }) => {
  await login(page)

  const input = page.getByPlaceholder("Text hier eingeben...")
  const processButton = page.locator('button:has(i:has-text("auto_fix_high"))')

  await input.fill("Hallo Welt")
  await processButton.click()

  await expect(page.getByPlaceholder("KI-verbesserter Text erscheint hier...")).toHaveValue(
    /Mocked Hallo Welt response/u,
  )
  await expect(page.getByText(/LLM: Mock/u)).toBeVisible()
  await expect(page.locator(".diff-container")).toBeVisible()
})

it("disables processing while input is empty", async ({ page }) => {
  await login(page)
  await expect(page.locator('button:has(i:has-text("auto_fix_high"))')).toBeDisabled()
})
