import { test, expect } from '@playwright/test';

test.describe('Mobile Layout & Responsiveness E2E', () => {
  test.use({ viewport: { width: 375, height: 812 } }); // iPhone dimensions

  test('Should collapse sidebar and open via hamburger menu on mobile', async ({ page }) => {
    await page.goto('/');

    // 1. Sidebar should not be visible by default on mobile
    // Wait for the app to load
    await expect(page.locator('text=Character Core')).toBeVisible();
    
    // The "Characters" button is inside the sidebar. On mobile, it's either hidden or off-screen.
    // The Sidebar component hides itself with -translate-x-full on mobile unless isOpen is true.
    const sidebar = page.locator('nav');
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
});
