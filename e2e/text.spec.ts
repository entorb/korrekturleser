import { expect, test } from '@playwright/test'

import { login } from './helpers'

test('processes text with the Mock provider', async ({ page }) => {
  await login(page)

  const input = page.getByPlaceholder('Text hier eingeben...')
  const processButton = page.locator('button:has(i:has-text("auto_fix_high"))')

  await input.fill('Hallo Welt')
  await processButton.click()

  await expect(page.getByPlaceholder('KI-verbesserter Text erscheint hier...')).toHaveValue(
    /Mocked Hallo Welt response/
  )
  await expect(page.getByText(/LLM: Mock/)).toBeVisible()
  await expect(page.locator('.diff-container')).toBeVisible()
})

test('disables processing while input is empty', async ({ page }) => {
  await login(page)
  await expect(page.locator('button:has(i:has-text("auto_fix_high"))')).toBeDisabled()
})
