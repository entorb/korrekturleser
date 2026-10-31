import { expect, test as it, test } from "@playwright/test"

import { login } from "./helpers.ts"

it("redirects to login when not authenticated", async ({ page }) => {
  await page.goto("")
  await expect(page).toHaveURL(/korrekturleser-vue\/login$/u)
  await expect(page.getByRole("button", { name: "Anmelden" })).toBeVisible()
})

it("logs in with a valid secret", async ({ page }) => {
  await login(page)
  await expect(page.getByRole("button", { name: "Anmelden" })).toHaveCount(0)
  await expect(page.getByText("Torben")).toBeVisible()
})

it("shows an error for a wrong secret", async ({ page }) => {
  await page.goto("login")
  await page.locator('input[type="password"]').fill("wrong-secret")
  await page.getByRole("button", { name: "Anmelden" }).click()
  await expect(page.locator(".bg-negative")).toBeVisible()
  await expect(page).toHaveURL(/korrekturleser-vue\/login$/u)
})

it("logs out", async ({ page }) => {
  await login(page)
  await page.locator('button:has(i:has-text("logout"))').click()
  await expect(page).toHaveURL(/korrekturleser-vue\/login$/u)
})
