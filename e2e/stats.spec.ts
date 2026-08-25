import { expect, test } from '@playwright/test'

import { login } from './helpers'

test('shows usage statistics after processing', async ({ page }) => {
  await login(page)

  await page.getByPlaceholder('Text hier eingeben...').fill('Hallo Welt')
  await page.locator('button:has(i:has-text("auto_fix_high"))').click()
  await expect(page.getByPlaceholder('KI-verbesserter Text erscheint hier...')).toHaveValue(
    /Mocked/
  )

  await page.locator('button:has(i:has-text("bar_chart"))').click()
  await expect(page.getByText('Gesamt')).toBeVisible()
  await expect(page.getByText('Täglich')).toBeVisible()
  await expect(page.locator('tbody', { hasText: 'Torben' })).toHaveCount(2)
})
