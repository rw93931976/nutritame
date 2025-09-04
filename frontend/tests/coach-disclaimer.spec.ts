import { test, expect } from '@playwright/test';

test('Coach: gate until Accept, preserve input, and respond after Accept', async ({ page }) => {
  const typed = 'create meal plan';
  let preAcceptSend = false;

  // Detect any message/session-related coach API calls before Accept (but allow feature-flags)
  await page.route('**/api/coach/message', route => {
    if (!(page as any)._ackAccepted) preAcceptSend = true;
    route.continue();
  });
  await page.route('**/api/coach/sessions', route => {
    if (!(page as any)._ackAccepted) preAcceptSend = true;
    route.continue();
  });

  await page.goto(process.env.E2E_BASE_URL + '/coach');
  
  // Wait for page to load
  await page.waitForTimeout(2000);
  
  // The interface should load without modal for first-time users
  // Find the input field - it should be accessible
  const input = page.locator('input[aria-label*="nutrition"], input[placeholder*="nutrition"]');
  await input.waitFor({ timeout: 5000 });

  // Type the message
  await input.fill(typed);

  // Try to send (this should trigger disclaimer modal due to gating)
  await input.press('Enter');
  
  // Wait for modal to appear
  await page.waitForTimeout(1000);

  // Modal should appear after send attempt
  const modal = page.getByRole('dialog', { name: /disclaimer/i });
  await expect(modal).toBeVisible();
  expect(preAcceptSend).toBeFalsy();

  // Accept the disclaimer
  (page as any)._ackAccepted = true;
  await modal.getByRole('button', { name: /accept/i }).click();
  
  // Wait for modal to disappear
  await expect(modal).not.toBeVisible({ timeout: 3000 });

  // Input should still contain the typed text after disclaimer acceptance
  await expect(input).toHaveValue(typed);

  // Now send the message (should work since disclaimer is accepted)
  const sendBtn = page.getByRole('button', { name: /send/i });
  await sendBtn.click();

  // Wait for AI response - look for chat message or response container
  const aiBubble = page.locator('[data-role="ai-message"], .bg-gray-100').first();
  await expect(aiBubble).toContainText(/.+/, { timeout: 15000 });

  // Input should be cleared after successful send
  await expect(input).toHaveValue('');
});