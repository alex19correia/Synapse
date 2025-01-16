import { test, expect, Page } from '@playwright/test';

// Test data
const TEST_USER = {
  email: 'test@example.com',
  password: 'Test@123456',
  name: 'Test User',
  bio: 'This is a test bio'
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

test.describe('Profile Tests', () => {
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
    await page.goto('/profile');
  });

  test('profile page loads correctly', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Profile');
    await expect(page.locator('[data-testid=profile-form]')).toBeVisible();
  });

  test('can update profile information', async ({ page }) => {
    // Fill profile form
    await page.locator('[data-testid=profile-name]').fill(TEST_USER.name);
    await page.locator('[data-testid=profile-bio]').fill(TEST_USER.bio);
    
    // Submit form
    await page.locator('[data-testid=save-profile]').click();
    
    // Verify success message
    await expect(page.locator('[data-testid=success-message]')).toBeVisible();
    
    // Reload page and verify persistence
    await page.reload();
    await expect(page.locator('[data-testid=profile-name]')).toHaveValue(TEST_USER.name);
    await expect(page.locator('[data-testid=profile-bio]')).toHaveValue(TEST_USER.bio);
  });

  test('validates required fields', async ({ page }) => {
    // Clear required fields
    await page.locator('[data-testid=profile-name]').fill('');
    await page.locator('[data-testid=save-profile]').click();
    
    // Verify error messages
    await expect(page.locator('[data-testid=name-error]')).toBeVisible();
  });

  test('can upload profile picture', async ({ page }) => {
    const fileInput = page.locator('[data-testid=avatar-input]');
    
    // Upload image
    await fileInput.setInputFiles({
      name: 'avatar.jpg',
      mimeType: 'image/jpeg',
      buffer: Buffer.from('fake-image-content')
    });
    
    // Verify upload success
    await expect(page.locator('[data-testid=avatar-preview]')).toBeVisible();
    await expect(page.locator('[data-testid=upload-success]')).toBeVisible();
  });

  test('handles large file upload errors', async ({ page }) => {
    const fileInput = page.locator('[data-testid=avatar-input]');
    
    // Create large file buffer (6MB)
    const largeBuffer = Buffer.alloc(6 * 1024 * 1024);
    
    // Try to upload large file
    await fileInput.setInputFiles({
      name: 'large-avatar.jpg',
      mimeType: 'image/jpeg',
      buffer: largeBuffer
    });
    
    // Verify error message
    await expect(page.locator('[data-testid=file-size-error]')).toBeVisible();
  });

  test('can delete profile picture', async ({ page }) => {
    // Assuming there's a profile picture
    await page.locator('[data-testid=delete-avatar]').click();
    
    // Confirm deletion
    await page.locator('[data-testid=confirm-delete]').click();
    
    // Verify default avatar is shown
    await expect(page.locator('[data-testid=default-avatar]')).toBeVisible();
  });

  test('profile data is properly sanitized', async ({ page }) => {
    const scriptText = '<script>alert("xss")</script>';
    
    // Try to inject script in bio
    await page.locator('[data-testid=profile-bio]').fill(scriptText);
    await page.locator('[data-testid=save-profile]').click();
    
    // Reload and verify script was sanitized
    await page.reload();
    const bioContent = await page.locator('[data-testid=profile-bio]').inputValue();
    expect(bioContent).not.toContain('<script>');
  });

  test('can toggle profile visibility', async ({ page }) => {
    // Toggle profile visibility
    await page.locator('[data-testid=visibility-toggle]').click();
    
    // Save changes
    await page.locator('[data-testid=save-profile]').click();
    
    // Verify success message
    await expect(page.locator('[data-testid=success-message]')).toBeVisible();
    
    // Verify visibility status
    await expect(page.locator('[data-testid=visibility-status]')).toContainText('Private');
  });
}); 