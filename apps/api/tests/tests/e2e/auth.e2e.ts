import { test, expect } from '@playwright/test';
import {
  TEST_USER,
  loginUser,
  waitForNetworkIdle,
  checkErrorMessage,
  checkSuccessMessage,
  SELECTORS,
  clearTestData,
  generateTestData
} from './test-utils';

test.describe('Authentication Tests', () => {
  test.beforeEach(async ({ page }) => {
    await clearTestData(page);
  });

  test('login with valid credentials', async ({ page }) => {
    await loginUser(page);
    await expect(page).toHaveURL('/dashboard');
  });

  test('login with invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.waitForSelector('iframe[src*="clerk"]');
    
    const frame = page.frameLocator('iframe[src*="clerk"]').first();
    await frame.locator('input[name="email"]').fill('invalid@example.com');
    await frame.locator('input[name="password"]').fill('wrongpassword');
    await frame.locator('button[type="submit"]').click();
    
    await checkErrorMessage(page, 'Invalid credentials');
  });

  test('signup with new account', async ({ page }) => {
    const newUser = generateTestData();
    
    await page.goto('/signup');
    await page.waitForSelector('iframe[src*="clerk"]');
    
    const frame = page.frameLocator('iframe[src*="clerk"]').first();
    await frame.locator('input[name="email"]').fill(newUser.email);
    await frame.locator('input[name="password"]').fill(newUser.password);
    await frame.locator('button[type="submit"]').click();
    
    await expect(page).toHaveURL('/dashboard');
    await checkSuccessMessage(page, 'Account created successfully');
  });

  test('logout functionality', async ({ page }) => {
    await loginUser(page);
    await page.locator(SELECTORS.logoutButton).click();
    await expect(page).toHaveURL('/login');
    
    // Verify cannot access protected routes
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/login');
  });

  test('password reset flow', async ({ page }) => {
    await page.goto('/login');
    await page.waitForSelector('iframe[src*="clerk"]');
    
    const frame = page.frameLocator('iframe[src*="clerk"]').first();
    await frame.locator('[data-testid=forgot-password]').click();
    await frame.locator('input[name="email"]').fill(TEST_USER.email);
    await frame.locator('button[type="submit"]').click();
    
    await checkSuccessMessage(page, 'Reset instructions sent');
  });

  test('remember me functionality', async ({ page, context }) => {
    await page.goto('/login');
    await page.waitForSelector('iframe[src*="clerk"]');
    
    const frame = page.frameLocator('iframe[src*="clerk"]').first();
    await frame.locator('input[name="email"]').fill(TEST_USER.email);
    await frame.locator('input[name="password"]').fill(TEST_USER.password);
    await frame.locator('[data-testid=remember-me]').click();
    await frame.locator('button[type="submit"]').click();
    
    await expect(page).toHaveURL('/dashboard');
    
    // Create new page in same context
    const newPage = await context.newPage();
    await newPage.goto('/dashboard');
    await waitForNetworkIdle(newPage);
    
    // Should still be logged in
    await expect(newPage).toHaveURL('/dashboard');
  });

  test('session timeout', async ({ page }) => {
    await loginUser(page);
    
    // Mock session timeout
    await page.evaluate(() => {
      localStorage.removeItem('clerk-session');
    });
    
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/login');
  });

  test('concurrent sessions', async ({ browser }) => {
    // Create two contexts
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();
    
    // Login in both contexts
    await loginUser(page1);
    await loginUser(page2);
    
    // Verify both sessions are active
    await expect(page1).toHaveURL('/dashboard');
    await expect(page2).toHaveURL('/dashboard');
    
    // Logout from one session
    await page1.locator(SELECTORS.logoutButton).click();
    
    // Verify only one session is logged out
    await expect(page1).toHaveURL('/login');
    await expect(page2).toHaveURL('/dashboard');
  });
}); 