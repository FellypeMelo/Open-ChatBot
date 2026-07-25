import { test, expect } from '@playwright/test';

test.describe('Tag Management E2E', () => {
  test('Should create, edit and delete a tag', async ({ page }, testInfo) => {
    // CI retries (retries: 2) reuse the same webServer/DB -- if this test ever
    // fails after creating (but before deleting) its tag, an un-scoped retry
    // would find the still-committed original tag alongside its new one,
    // turning a `text=E2E-Tag` lookup into a strict-mode "2 elements" failure.
    // Scope every created/edited label by the retry index so each attempt is
    // independent, regardless of whether a prior attempt cleaned up.
    const tagLabel = `E2E-Tag-r${testInfo.retry}`;
    const tagLabelUpdated = `E2E-Tag-Updated-r${testInfo.retry}`;

    await page.goto('/');

    // Go to Tags view
    await page.click('button:has-text("Knowledge Tags")');
    await expect(page.locator('text=System Taxonomy')).toBeVisible();

    // Create a new tag
    await page.click('button:has-text("Create New Tag")');

    // Fill the tag form
    await page.waitForSelector('#tag_label');
    await page.fill('#tag_label', tagLabel);
    await page.fill('#tag_instruction', 'This is an E2E test tag instruction.');
    await page.click('button[type="submit"]');

    // Wait for the tag to appear in the list
    await expect(page.locator('text=' + tagLabel)).toBeVisible();

    // Edit the tag. Scoped to this tag's own card (TagManagementView renders
    // one `div.group` per tag, exactly like CharactersView's character cards)
    // so a leftover tag from an earlier attempt -- or any other tag in the
    // shared DB, e.g. chat.spec.ts's "Hero-rN" -- can't make the Edit button
    // ambiguous. A bare 'div' with hasText matches every ANCESTOR div too
    // (the whole grid container, the page root, ...), which still contains
    // every OTHER tag's buttons -- exactly the bug this scoping avoids.
    const tagRow = page.locator('div.group', { hasText: tagLabel }).first();
    await tagRow.getByRole('button', { name: 'Edit', exact: true }).click();
    await page.fill('#tag_label', tagLabelUpdated);
    await page.click('button[type="submit"]');

    // Verify update
    await expect(page.locator('text=' + tagLabelUpdated)).toBeVisible();

    // Delete the tag
    page.on('dialog', dialog => dialog.accept());
    const updatedRow = page.locator('div.group', { hasText: tagLabelUpdated }).first();
    await updatedRow.getByRole('button', { name: 'Delete', exact: true }).click();

    // Verify deletion
    await expect(page.locator('text=' + tagLabelUpdated)).not.toBeVisible();
  });
});
