import type { Page } from '@playwright/test'

export async function login(page: Page) {
  await page.goto('login')
  await page.locator('input[type="password"]').fill('test')
  await page.getByRole('button', { name: 'Anmelden' }).click()
  await page.waitForURL(/korrekturleser-vue\/$/)
}
