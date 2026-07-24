import { test, expect } from '@playwright/test';

// This file matches the `mobile-*.spec.ts` pattern in playwright.config.ts, so
// it only ever runs under the `mobile-chrome` (Pixel 5) and `mobile-safari`
// (iPhone 13) projects -- real device emulation (touch, mobile viewport/UA,
// hover:none) rather than a bare viewport override on Desktop Chrome. No
// `test.use({ viewport })` is needed here: each project's device profile
// already provides a real sub-768px mobile viewport.

test.describe('Mobile Layout & Responsiveness E2E', () => {
  test('Should collapse sidebar and open via hamburger menu on mobile', async ({ page }) => {
    await page.goto('/');

    // 1. Sidebar should not be visible by default on mobile
    // Wait for the app to load
    await expect(page.locator('text=Character Core')).toBeVisible();

    // The "Characters" button is inside the sidebar. On mobile, it's either hidden or off-screen.
    // The Sidebar component hides itself with -translate-x-full on mobile unless isOpen is true.
    // Scoped to exclude the MobileTabBar's <nav aria-label="Primary">, which is
    // also mounted on mobile and would otherwise make `nav` match two elements.
    const sidebar = page.locator('nav:not([aria-label="Primary"])');
    await expect(sidebar).toHaveClass(/.*-translate-x-full.*/);

    // 2. Click the hamburger menu
    // In App.tsx: <span className="material-symbols-outlined ...">menu</span>
    await page.click('span:text-is("menu")');

    // 3. Sidebar should now be visible
    await expect(sidebar).not.toHaveClass(/.*-translate-x-full.*/);
    await expect(page.locator('button:has-text("Knowledge Tags")')).toBeVisible();

    // 4. Click a sidebar link, it should close the sidebar
    await page.click('button:has-text("Knowledge Tags")');

    // Check that sidebar is closed again
    await expect(sidebar).toHaveClass(/.*-translate-x-full.*/);
  });

  test('Should render the bottom tab bar and switch views by tapping it', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=Character Core')).toBeVisible();

    // MobileTabBar: fixed bottom nav, only mounted under the `md` breakpoint.
    const tabBar = page.getByRole('navigation', { name: 'Primary' });
    await expect(tabBar).toBeVisible();

    const charactersTab = tabBar.getByRole('button', { name: 'Characters' });
    const chatTab = tabBar.getByRole('button', { name: 'Chat' });
    const loreTab = tabBar.getByRole('button', { name: 'Lore' });
    const tagsTab = tabBar.getByRole('button', { name: 'Tags' });

    // Characters is the default view, so it should start as the active tab.
    await expect(charactersTab).toHaveAttribute('aria-current', 'page');
    await expect(chatTab).not.toHaveAttribute('aria-current', 'page');

    // Tap Chat: aria-current moves, and the view actually switches (composer renders).
    await chatTab.click();
    await expect(chatTab).toHaveAttribute('aria-current', 'page');
    await expect(charactersTab).not.toHaveAttribute('aria-current', 'page');
    await expect(page.locator('textarea[placeholder^="Write a prompt"]')).toBeVisible();

    // Tap Lore.
    await loreTab.click();
    await expect(loreTab).toHaveAttribute('aria-current', 'page');
    await expect(page.locator('text=Lorebook & Knowledge')).toBeVisible();

    // Tap Tags.
    await tagsTab.click();
    await expect(tagsTab).toHaveAttribute('aria-current', 'page');
    await expect(page.locator('text=System Taxonomy')).toBeVisible();

    // Tap back to Characters.
    await charactersTab.click();
    await expect(charactersTab).toHaveAttribute('aria-current', 'page');
    await expect(page.locator('text=Character Core')).toBeVisible();
  });

  test('Should not overflow horizontally on a mobile viewport', async ({ page }) => {
    // Guards against e.g. a stray `w-screen` element (which ignores the
    // scrollbar) causing horizontal page scroll on a phone.
    const assertNoHorizontalOverflow = async () => {
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - window.innerWidth
      );
      expect(overflow).toBeLessThanOrEqual(1); // allow 1px of sub-pixel rounding
    };

    await page.goto('/');
    await expect(page.locator('text=Character Core')).toBeVisible();
    await assertNoHorizontalOverflow();

    await page.getByRole('navigation', { name: 'Primary' }).getByRole('button', { name: 'Tags' }).click();
    await expect(page.locator('text=System Taxonomy')).toBeVisible();
    await assertNoHorizontalOverflow();
  });
});
