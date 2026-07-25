import { test, expect } from '@playwright/test';

test.describe('Open-ChatBot E2E Core Flow', () => {

  test('Should verify initial state, create a new character with tags, and interact', async ({ page }, testInfo) => {
    // The e2e webServer's SQLite DB is shared across CI's retry attempts
    // (retries: 2 in playwright.config.ts) -- a transient failure on attempt 1
    // still leaves its tag/character committed, so an un-scoped name on retry
    // creates a SECOND "Hero"/"E2E Tester" and turns a one-off timing hiccup
    // into a deterministic "resolved to 2 elements" failure on every later
    // attempt. Scope every created name by the retry index so each attempt's
    // data is independent, mirroring mobile-chat-interactions.spec.ts's
    // project-name scoping for the same reason.
    const tagLabel = `Hero-r${testInfo.retry}`;
    const charName = `E2E Tester r${testInfo.retry}`;

    await page.goto('/');

    // Check main title
    await expect(page.locator('text=Character Core')).toBeVisible();

    // 0. Create a Tag first
    await page.click('button:has-text("Knowledge Tags")');
    await page.click('button:has-text("Create New Tag")');
    await page.waitForSelector('#tag_label');
    await page.fill('#tag_label', tagLabel);
    await page.fill('#tag_instruction', 'A heroic tag.');
    await page.click('button[type="submit"]');
    // Exact match: a bare `text=...` is a case-insensitive SUBSTRING match, so
    // it would also match the tag's own instruction text -> a strict-mode
    // violation (2+ elements). Assert the tag label chip specifically.
    await expect(page.getByText(tagLabel, { exact: true })).toBeVisible();

    // 1. Initialize Persona
    await page.click('button:has-text("Characters")');
    await page.click('button:has-text("Initialize Persona")');

    // Fill out the form
    await page.fill('#char_name', charName);
    await page.fill('#char_description', 'A brave E2E test character.');

    // Select the tag
    await page.click(`button:has-text("${tagLabel}")`);

    await page.click('button[type="submit"]:has-text("Initialize")');

    // Wait for the character to appear in the library
    await expect(page.locator('text=' + charName)).toBeVisible();

    // 2. Open Chat for the character. Scoped to this test's own card (not a
    // bare 'button:has-text("Chat")') -- the webServer's DB is shared across
    // this whole e2e run, so other specs' characters (or, pre-fix, a retried
    // attempt's own leftover character) could otherwise make this ambiguous.
    const charCard = page.locator('div.group', { hasText: charName }).first();
    await charCard.getByRole('button', { name: 'Chat', exact: true }).click();

    // 3. Send a message
    // Now we are in the chat view
    // Need to make sure the chat input is selected correctly. Wait for the text area.
    await page.waitForSelector('textarea');
    // Using a more robust selector since placeholders can be tricky if they change
    await page.fill('textarea', 'Hello there!');
    
    // Press Enter to send
    await page.keyboard.press('Enter');

    // 4. Verify user message appears in chat
    await expect(page.locator('text=Hello there!')).toBeVisible();

    // 5. Verify Mock E2E response appears and completes (wait for the last token to ensure DOM stability)
    await expect(page.locator('text=changes into a Tuxedo')).toBeVisible({ timeout: 8000 });
    
    // Wait for the main input textarea to be enabled, signaling that the loading state has finished and database IDs are updated in the UI
    await expect(page.locator('textarea[placeholder^="Write a prompt"]')).toBeEnabled({ timeout: 5000 });

    // 6. Test Message Regeneration / Variants (Swipes)
    const aiMessage = page.locator('div.group', { hasText: 'Mock E2E stream response' }).first();
    await aiMessage.locator('button:has-text("Regenerate")').click({ force: true });
    // Wait for the new response to arrive (it will be the same mock text, but it increments the variant)
    // We can verify variants exist by checking the swipe indicators (e.g., 2 / 2)
    await expect(page.locator('text=2 / 2')).toBeVisible({ timeout: 5000 });
    
    // Swipe left (Previous variant)
    await page.click('button:has(.material-symbols-outlined:has-text("chevron_left"))');
    await expect(page.locator('text=1 / 2')).toBeVisible();
    
    // Swipe right (Next variant)
    await page.click('button:has(.material-symbols-outlined:has-text("chevron_right"))');
    await expect(page.locator('text=2 / 2')).toBeVisible();

    // 7. Edit the user message (force click to bypass hover requirements)
    const userMessage = page.locator('div.group', { hasText: 'Hello' }).first();
    await userMessage.locator('button[title="Edit"]').click({ force: true });
    await userMessage.locator('textarea').fill('Hello there, edited!');
    await page.click('button:has-text("SAVE")');
    await expect(page.locator('text=Hello there, edited!')).toBeVisible();
  });

});
