import { test, expect } from '@playwright/test';

test.describe('Tag Management E2E', () => {
  test('Should create, edit and delete a tag', async ({ page }) => {
    await page.goto('/');

    // Go to Tags view
    await page.click('button:has-text("Knowledge Tags")');
    await expect(page.locator('text=System Taxonomy')).toBeVisible();

    // Create a new tag
    await page.click('button:has-text("Create New Tag")');
    
    // Fill the tag form
    await page.waitForSelector('#tag_label');
    await page.fill('#tag_label', 'E2E-Tag');
    await page.fill('#tag_instruction', 'This is an E2E test tag instruction.');
    await page.click('button[type="submit"]');

    // Wait for the tag to appear in the list
    await expect(page.locator('text=E2E-Tag')).toBeVisible();

    // Edit the tag
    await page.click('button:has-text("edit")');
    await page.fill('#tag_label', 'E2E-Tag-Updated');
    await page.click('button[type="submit"]');
    
    // Verify update
    await expect(page.locator('text=E2E-Tag-Updated')).toBeVisible();

    // Delete the tag
    page.on('dialog', dialog => dialog.accept());
    await page.click('button:has-text("delete")');

    // Verify deletion
    await expect(page.locator('text=E2E-Tag-Updated')).not.toBeVisible();
  });
});
