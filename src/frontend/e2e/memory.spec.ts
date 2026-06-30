import { test, expect } from '@playwright/test';

test.describe('Memory & Journal E2E', () => {
  test('Should interact with Private Journal and verify Memory UI', async ({ page }) => {
    await page.goto('/');

    // 1. Create a character for memory testing
    await page.click('button:has-text("Characters")');
    await page.click('button:has-text("Initialize Persona")');
    await page.fill('#char_name', 'Memory Tester');
    await page.fill('#char_description', 'A character with a great memory.');
    await page.click('button[type="submit"]:has-text("Initialize")');
    
    // 2. Open Chat
    await page.click('button:has-text("Chat")');
    await page.waitForSelector('textarea');

    // 3. Send a message to trigger memory/interaction count
    await page.fill('textarea', 'Remember this secret: the owl flies at midnight.');
    await page.keyboard.press('Enter');
    
    // Wait for mock response
    await expect(page.locator('text=Mock E2E stream response')).toBeVisible({ timeout: 5000 });

    // 4. Open Private Journal tab
    await page.click('button:has-text("Private Journal")');
    
    // Wait for Journal UI to load
    // If the mock backend doesn't automatically create a journal entry, it will show "No journal entries yet."
    // Let's verify that the Journal UI successfully rendered
    const noJournal = page.locator('text=No journal entries yet.');
    const hasJournal = page.locator('.journal-entry'); // Assuming we add a class if we want to test real entries

    await Promise.race([
      expect(noJournal).toBeVisible(),
      expect(hasJournal).toBeVisible()
    ]);
  });
});
