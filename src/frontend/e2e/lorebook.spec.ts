import { test, expect } from '@playwright/test';

test.describe('Lorebook Management E2E', () => {
  test('Should create and search a lorebook entry', async ({ page }) => {
    await page.goto('/');

    // Go to Lorebook view
    await page.click('button:has-text("Lorebook")');
    await expect(page.locator('text=Lorebook & Knowledge')).toBeVisible();

    // Fill the entry form (it is inline on the page, no New Entry button needed)
    await page.fill('input[placeholder="Keyword (e.g. \'Silver Dragon\')"]', 'E2E-Lore');
    await page.fill('textarea[placeholder="What should the character remember when this keyword is mentioned?"]', 'This is a test lore entry.');
    await page.click('button:has-text("Add Knowledge Entry")');

    // Wait for the entry to appear in the list
    await expect(page.locator('text=E2E-Lore')).toBeVisible();

    // Search for the entry
    await page.fill('input[placeholder="Search lore..."]', 'E2E-Lore');
    await expect(page.locator('text=E2E-Lore')).toBeVisible();

    // Delete the entry (in-app ConfirmDialog, not a native browser dialog)
    await page.click('button:has-text("delete")');
    await page.getByRole('alertdialog').getByRole('button', { name: 'Delete' }).click();

    // Verify deletion
    await expect(page.locator('text=E2E-Lore')).not.toBeVisible();
  });
});
