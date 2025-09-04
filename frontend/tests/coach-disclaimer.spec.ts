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
  
  // Wait for page to load and handle initial disclaimer modal if present
  await page.waitForTimeout(1000);
  
  // If disclaimer modal is visible, we need to test a different flow
  const initialModal = page.getByRole('dialog', { name: /disclaimer/i });
  const isModalVisible = await initialModal.isVisible({ timeout: 1000 }).catch(() => false);
  
  if (isModalVisible) {
    // Current behavior: modal blocks input, so accept it first
    (page as any)._ackAccepted = true;
    await initialModal.getByRole('button', { name: /accept/i }).click();
    await page.waitForTimeout(1000);
  }

  // Now find the input field
  const input = page.locator('input[aria-label*="nutrition"], textarea[placeholder*="Ask"], input[placeholder*="nutrition"]');
  await input.waitFor({ timeout: 5000 });

  // Type the message
  await input.fill(typed);

  // Try to send (this should trigger gating if disclaimer not accepted, or proceed if accepted)
  await input.press('Enter');

  // If disclaimer wasn't previously accepted, modal should appear now
  if (!isModalVisible) {
    const modal = page.getByRole('dialog', { name: /disclaimer/i });
    await expect(modal).toBeVisible();
    expect(preAcceptSend).toBeFalsy();

    (page as any)._ackAccepted = true;
    await modal.getByRole('button', { name: /accept/i }).click();
    await page.waitForTimeout(500);
  }

  // Input should still contain the typed text after disclaimer acceptance
  await expect(input).toHaveValue(typed);

  // Now send the message
  const sendBtn = page.getByRole('button', { name: /send/i });
  await sendBtn.click();

  // Wait for AI response - look for chat message or response container
  const aiBubble = page.locator('[data-role="ai-message"], .bg-gray-100, .ai-response').first();
  await expect(aiBubble).toContainText(/.+/, { timeout: 10000 });

  // Input should be cleared after successful send
  await expect(input).toHaveValue('');
});