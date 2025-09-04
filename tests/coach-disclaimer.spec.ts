import { test, expect } from '@playwright/test';

test('Coach: gate until Accept, preserve input, and respond after Accept', async ({ page }) => {
  const typed = 'create meal plan';
  let preAcceptSend = false;

  // Detect any coach API calls before Accept
  await page.route('**/api/coach/**', route => {
    if (!(page as any)._ackAccepted) preAcceptSend = true;
    route.continue();
  });

  await page.goto(process.env.E2E_BASE_URL + '/coach');

  const input = page.locator('textarea, input[aria-label*="nutrition"], textarea');

  await input.fill(typed);
  await input.press('Enter');

  const modal = page.getByRole('dialog', { name: /disclaimer/i });
  await expect(modal).toBeVisible();
  expect(preAcceptSend).toBeFalsy();

  (page as any)._ackAccepted = true;
  await modal.getByRole('button', { name: /accept/i }).click();

  await expect(input).toHaveValue(typed);           // must still show after Accept

  const sendBtn = page.getByRole('button', { name: /send/i });
  await sendBtn.click();

  const aiBubble = page.locator('[data-role="ai-message"]').first();
  await expect(aiBubble).toContainText(/.+/);       // non-empty AI response

  await expect(input).toHaveValue('');              // cleared only after 2xx
});