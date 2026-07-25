import { test, expect } from '@playwright/test';

// Matches the `mobile-*.spec.ts` pattern in playwright.config.ts, so this only
// runs under the `mobile-chrome` (Pixel 5) and `mobile-safari` (iPhone 13)
// projects -- real touch emulation, mobile viewport/UA and `hover: none`.
//
// Regression coverage for already-shipped mobile fixes that had no e2e test:
//   - tap-visible character-card actions (CharactersView, opacity-100 below `md`)
//   - the collapsible stats HUD (ChatView, collapsed by default on mobile)
//   - tap-visible message/variant action buttons (ChatView, opacity-100 below `md`)
//   - composer auto-grow (ChatView, height tracks content up to a cap)
//
// A message action button reachable only via `.hover()` or `{ force: true }`
// would fail every assertion below, since neither is used here.

test.describe('Mobile Chat Interactions E2E', () => {
  test('Should expose tap-visible actions, a collapsible stats HUD, and an auto-growing composer', async ({ page }, testInfo) => {
    // The e2e webServer (and its SQLite DB) is started once for the whole
    // `playwright test` invocation and shared by every project, so this same
    // spec running under both mobile-chrome and mobile-safari would otherwise
    // create two identically-named characters/messages -- scoped by project
    // name to keep those unambiguous. ALSO scoped by testInfo.retry: CI retries
    // (retries: 2) reuse the same DB, so a transient failure on attempt 0 still
    // leaves its character/message committed, and an un-scoped retry attempt 1
    // would then find two "Mobile QA Persona (...)" cards -- turning a one-off
    // timing hiccup into a deterministic "resolved to 2 elements" failure on
    // every subsequent attempt (this is exactly what a prior CI run showed).
    const personaName = `Mobile QA Persona (${testInfo.project.name} r${testInfo.retry})`;
    const greeting = `Mobile hello from ${testInfo.project.name} r${testInfo.retry}!`;

    await page.goto('/');
    await expect(page.locator('text=Character Core')).toBeVisible();

    // 1. Create a character (Characters is the default view on mobile too).
    await page.click('button:has-text("Initialize Persona")');
    await page.fill('#char_name', personaName);
    await page.fill('#char_description', 'A character created to exercise mobile-only tap interactions.');
    await page.click('button[type="submit"]:has-text("Initialize")');
    await expect(page.locator('text=' + personaName)).toBeVisible();

    // 2. Character-card actions must be tap-visible without any hover --
    // CharactersView ships `opacity-100 md:opacity-0 md:group-hover:opacity-100`.
    const card = page.locator('div.group', { hasText: personaName }).first();
    await expect(card.getByRole('button', { name: 'Edit', exact: true })).toBeVisible();
    await expect(card.getByRole('button', { name: 'Delete', exact: true })).toBeVisible();
    const chatButton = card.getByRole('button', { name: 'Chat', exact: true });
    await expect(chatButton).toBeVisible();

    // 3. Open chat for this character via a real tap (no `force: true`).
    await chatButton.click();
    const composer = page.locator('textarea[placeholder^="Write a prompt"]');
    await expect(composer).toBeEnabled();

    // 4. Stats HUD: collapsed by default on mobile, expands on tap.
    const statsToggle = page.locator('button', { hasText: 'REL' });
    await expect(statsToggle).toHaveAttribute('aria-expanded', 'false');
    const energyLabel = page.getByText('ENERGY', { exact: true });
    await expect(energyLabel).toBeHidden();

    await statsToggle.click();
    await expect(statsToggle).toHaveAttribute('aria-expanded', 'true');
    await expect(energyLabel).toBeVisible();

    await statsToggle.click();
    await expect(statsToggle).toHaveAttribute('aria-expanded', 'false');
    await expect(energyLabel).toBeHidden();

    // 5. Composer auto-grow: bounding-box height increases as multi-line
    // content is typed, and shrinks back down when cleared.
    const emptyHeight = (await composer.boundingBox())?.height ?? 0;
    expect(emptyHeight).toBeGreaterThan(0);

    await composer.fill('Line one\nLine two\nLine three\nLine four\nLine five\nLine six');
    await expect.poll(async () => (await composer.boundingBox())?.height ?? 0, {
      message: 'composer should grow taller as multi-line text is typed',
      timeout: 3000,
    }).toBeGreaterThan(emptyHeight);
    const grownHeight = (await composer.boundingBox())?.height ?? 0;

    await composer.fill('');
    await expect.poll(async () => (await composer.boundingBox())?.height ?? 0, {
      message: 'composer should shrink back down once cleared',
      timeout: 3000,
    }).toBeLessThan(grownHeight);

    // 6. Send a message and wait for the deterministic E2E mock reply.
    await composer.fill(greeting);
    await page.keyboard.press('Enter');
    await expect(page.locator('text=' + greeting)).toBeVisible();
    await expect(page.locator('text=changes into a Tuxedo')).toBeVisible({ timeout: 8000 });
    await expect(composer).toBeEnabled({ timeout: 5000 });

    // 7. Assistant message actions (Regenerate) must be tap-visible without hover.
    // This character/chat was just created in this test run, so its message
    // list is scoped to this run alone -- no cross-project collision to
    // guard against here (unlike the character-card lookup above, which
    // scans every character in the shared DB).
    const aiMessage = page.locator('div.group', { hasText: 'Mock E2E stream response' }).first();
    const regenerateButton = aiMessage.getByRole('button', { name: 'Regenerate response' });
    await expect(regenerateButton).toBeVisible();
    await regenerateButton.click();

    // Regenerating creates a second variant; its swipe controls must also be
    // tap-visible without hover.
    await expect(page.locator('text=2 / 2')).toBeVisible({ timeout: 8000 });
    const previousVariantButton = aiMessage.getByRole('button', { name: 'Previous variant' });
    const nextVariantButton = aiMessage.getByRole('button', { name: 'Next variant' });
    await expect(previousVariantButton).toBeVisible();
    await expect(nextVariantButton).toBeVisible();
    await previousVariantButton.click();
    await expect(page.locator('text=1 / 2')).toBeVisible();

    // 8. User-message actions (Edit) must also be tap-visible without hover.
    const userMessage = page.locator('div.group', { hasText: greeting }).first();
    const editButton = userMessage.getByRole('button', { name: 'Edit', exact: true });
    await expect(editButton).toBeVisible();
    await editButton.click();
    await expect(userMessage.locator('textarea')).toBeVisible();
    await userMessage.locator('button:has-text("CANCEL")').click();
    await expect(userMessage.locator('textarea')).toBeHidden();
  });
});
