import { test, expect, Page } from '@playwright/test';

// Test data
const TEST_USER = {
  email: 'test@example.com',
  password: 'Test@123456'
};

// Helper function for login
async function loginUser(page: Page) {
  await page.goto('/login');
  await page.waitForSelector('iframe[src*="clerk"]');
  const frame = page.frameLocator('iframe[src*="clerk"]').first();
  await frame.locator('input[name="email"]').fill(TEST_USER.email);
  await frame.locator('input[name="password"]').fill(TEST_USER.password);
  await frame.locator('button[type="submit"]').click();
  await page.waitForURL('/dashboard');
}

test.describe('Dashboard Tests', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
  });

  test('dashboard loads correctly', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Dashboard');
    await expect(page.locator('[data-testid=user-info]')).toBeVisible();
  });

  test('navigation menu works', async ({ page }) => {
    // Test navigation items
    const navItems = [
      { selector: '[data-testid=nav-profile]', url: '/profile' },
      { selector: '[data-testid=nav-settings]', url: '/settings' },
      { selector: '[data-testid=nav-dashboard]', url: '/dashboard' }
    ];

    for (const item of navItems) {
      await page.locator(item.selector).click();
      await expect(page).toHaveURL(item.url);
    }
  });

  test('user info is displayed correctly', async ({ page }) => {
    const userInfo = page.locator('[data-testid=user-info]');
    await expect(userInfo).toContainText(TEST_USER.email);
  });

  test('logout works', async ({ page }) => {
    await page.locator('[data-testid=user-button]').click();
    await page.locator('[data-testid=logout-button]').click();
    await expect(page).toHaveURL('/login');
  });

  test('dashboard data loads', async ({ page }) => {
    // Wait for and verify dashboard components
    await expect(page.locator('[data-testid=dashboard-stats]')).toBeVisible();
    await expect(page.locator('[data-testid=recent-activity]')).toBeVisible();
    await expect(page.locator('[data-testid=quick-actions]')).toBeVisible();
  });

  test('dashboard is responsive', async ({ page }) => {
    // Test different viewport sizes
    const viewports = [
      { width: 1920, height: 1080 }, // Desktop
      { width: 1024, height: 768 },  // Tablet
      { width: 375, height: 667 }    // Mobile
    ];

    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await expect(page.locator('main')).toBeVisible();
      await expect(page.locator('nav')).toBeVisible();
    }
  });

  test('error states are handled', async ({ page }) => {
    // Simulate error by navigating to invalid dashboard section
    await page.goto('/dashboard/invalid');
    await expect(page.locator('[data-testid=error-message]')).toBeVisible();
  });
}); 