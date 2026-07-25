import { test, expect } from '@playwright/test';

test.describe('Character State & Environment E2E', () => {
  test('Should interact with character states, environment, and clothes', async ({ page }, testInfo) => {
    // CI retries (retries: 2) reuse the same webServer/DB, and this spec runs
    // alongside several others that also create characters in it -- scope the
    // name by retry index and scope the "Chat" click to this test's own card
    // (not a bare 'button:has-text("Chat")') so neither a leftover retry
    // attempt nor another spec's character can make either ambiguous.
    const charName = `State Tester r${testInfo.retry}`;

    await page.goto('/');

    // 1. Create a character to test state/environment interactions with.
    await page.click('button:has-text("Characters")');
    await page.click('button:has-text("Initialize Persona")');
    await page.fill('#char_name', charName);
    await page.fill('#char_description', 'A character for state testing.');
    await page.click('button[type="submit"]:has-text("Initialize")');
    await expect(page.locator('text=' + charName)).toBeVisible();

    // 2. Open Chat for this character specifically.
    const charCard = page.locator('div.group', { hasText: charName }).first();
    await charCard.getByRole('button', { name: 'Chat', exact: true }).click();
    await page.waitForSelector('textarea');

    // 3. Test Hunger Bar
    // The feed button decreases hunger. Initially hunger is 0 in a fresh character, but wait!
    // A fresh character has hunger = 0, so the button is disabled. 
    // We need to wait for it to be enabled or just verify the button exists and the text is there.
    await expect(page.locator('text=HUNGER')).toBeVisible();

    // 4. Test Energy (Sleep/Wake)
    await expect(page.locator('text=ENERGY')).toBeVisible();
    await page.click('button:has-text("Sleep")');
    // It should change to Wake
    await expect(page.locator('button:has-text("Wake")')).toBeVisible();

    // 5. Test Happiness
    await expect(page.locator('text=HAPPINESS')).toBeVisible();
    await page.click('button:has-text("-")'); // Decrement happiness
    await page.click('button:has-text("+")'); // Increment happiness

    // 6. Test Environment and Clothes display
    // The default location is "Living Room" and clothes "Casual"
    await expect(page.locator('text=LIVING ROOM • CASUAL')).toBeVisible();

    // 7. Test autonomous LLM-driven environment change
    // We send a specific mock trigger message "Vamos para o Baile"
    await page.fill('textarea', 'Vamos para o Baile');
    await page.keyboard.press('Enter');
    
    // The backend mock in llm.py will update the state to Ballroom / Tuxedo
    // Wait for the UI to react to the new state payload that comes with the message
    await expect(page.locator('text=BALLROOM • TUXEDO')).toBeVisible({ timeout: 5000 });
  });
});
