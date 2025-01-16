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

test.describe('Settings Tests', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
    await page.goto('/settings');
  });

  test('settings page loads correctly', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Settings');
    await expect(page.locator('[data-testid=settings-form]')).toBeVisible();
  });

  test('can toggle dark mode', async ({ page }) => {
    // Toggle dark mode
    await page.locator('[data-testid=theme-toggle]').click();
    
    // Verify dark mode is active
    await expect(page.locator('html')).toHaveClass(/dark/);
    
    // Verify persistence after reload
    await page.reload();
    await expect(page.locator('html')).toHaveClass(/dark/);
  });

  test('can update notification preferences', async ({ page }) => {
    // Toggle different notification types
    const notificationToggles = [
      'email-notifications',
      'push-notifications',
      'newsletter'
    ];

    for (const toggle of notificationToggles) {
      await page.locator(`[data-testid=${toggle}]`).click();
    }

    // Save preferences
    await page.locator('[data-testid=save-notifications]').click();
    
    // Verify success message
    await expect(page.locator('[data-testid=success-message]')).toBeVisible();
    
    // Verify persistence after reload
    await page.reload();
    for (const toggle of notificationToggles) {
      await expect(page.locator(`[data-testid=${toggle}]`)).toBeChecked();
    }
  });

  test('can change language preference', async ({ page }) => {
    // Open language selector
    await page.locator('[data-testid=language-select]').click();
    
    // Select Portuguese
    await page.locator('[data-testid=language-pt]').click();
    
    // Save changes
    await page.locator('[data-testid=save-language]').click();
    
    // Verify success message
    await expect(page.locator('[data-testid=success-message]')).toBeVisible();
    
    // Verify UI language changed
    await expect(page.locator('h1')).toContainText('Configurações');
  });

  test('can manage connected accounts', async ({ page }) => {
    // Open connected accounts section
    await page.locator('[data-testid=connected-accounts]').click();
    
    // Connect GitHub account
    await page.locator('[data-testid=connect-github]').click();
    
    // Handle OAuth flow (mock)
    await page.route('**/oauth/github', route => {
      route.fulfill({
        status: 200,
        body: JSON.stringify({ success: true })
      });
    });
    
    // Verify connection success
    await expect(page.locator('[data-testid=github-connected]')).toBeVisible();
  });

  test('can change password', async ({ page }) => {
    // Open security settings
    await page.locator('[data-testid=security-settings]').click();
    
    // Fill password change form
    await page.locator('[data-testid=current-password]').fill(TEST_USER.password);
    await page.locator('[data-testid=new-password]').fill('NewTest@123456');
    await page.locator('[data-testid=confirm-password]').fill('NewTest@123456');
    
    // Submit form
    await page.locator('[data-testid=change-password]').click();
    
    // Verify success message
    await expect(page.locator('[data-testid=success-message]')).toBeVisible();
  });

  test('validates password requirements', async ({ page }) => {
    await page.locator('[data-testid=security-settings]').click();
    
    // Try weak password
    await page.locator('[data-testid=current-password]').fill(TEST_USER.password);
    await page.locator('[data-testid=new-password]').fill('weak');
    await page.locator('[data-testid=confirm-password]').fill('weak');
    
    // Submit form
    await page.locator('[data-testid=change-password]').click();
    
    // Verify error messages
    await expect(page.locator('[data-testid=password-requirements]')).toBeVisible();
  });

  test('can enable two-factor authentication', async ({ page }) => {
    await page.locator('[data-testid=security-settings]').click();
    
    // Start 2FA setup
    await page.locator('[data-testid=setup-2fa]').click();
    
    // Verify QR code is displayed
    await expect(page.locator('[data-testid=2fa-qr-code]')).toBeVisible();
    
    // Enter verification code (mock)
    await page.locator('[data-testid=2fa-code]').fill('123456');
    await page.locator('[data-testid=verify-2fa]').click();
    
    // Verify success message
    await expect(page.locator('[data-testid=success-message]')).toBeVisible();
    
    // Verify 2FA is enabled
    await expect(page.locator('[data-testid=2fa-enabled]')).toBeVisible();
  });

  test('can export user data', async ({ page, context }) => {
    // Start data export
    await page.locator('[data-testid=export-data]').click();
    
    // Handle download
    const downloadPromise = page.waitForEvent('download');
    await page.locator('[data-testid=confirm-export]').click();
    const download = await downloadPromise;
    
    // Verify download started
    expect(download.suggestedFilename()).toContain('user-data');
  });

  test('can delete account', async ({ page }) => {
    // Open danger zone
    await page.locator('[data-testid=danger-zone]').click();
    
    // Start account deletion
    await page.locator('[data-testid=delete-account]').click();
    
    // Confirm deletion
    await page.locator('[data-testid=confirm-delete]').fill('DELETE');
    await page.locator('[data-testid=confirm-deletion]').click();
    
    // Verify redirect to home
    await expect(page).toHaveURL('/');
    
    // Verify cannot access protected routes
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/login');
  });
}); 