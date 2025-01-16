import { Page, expect } from '@playwright/test';

// Test user data
export const TEST_USER = {
  email: 'test@example.com',
  password: 'Test@123456',
  name: 'Test User',
  bio: 'This is a test bio'
};

// Helper function for login
export async function loginUser(page: Page) {
  await page.goto('/login');
  await page.waitForSelector('iframe[src*="clerk"]');
  const frame = page.frameLocator('iframe[src*="clerk"]').first();
  await frame.locator('input[name="email"]').fill(TEST_USER.email);
  await frame.locator('input[name="password"]').fill(TEST_USER.password);
  await frame.locator('button[type="submit"]').click();
  await page.waitForURL('/dashboard');
}

// Helper function to wait for network idle
export async function waitForNetworkIdle(page: Page) {
  await page.waitForLoadState('networkidle');
}

// Helper function to check if element exists
export async function elementExists(page: Page, selector: string): Promise<boolean> {
  const elements = await page.$$(selector);
  return elements.length > 0;
}

// Helper function to check if URL is protected
export async function isProtectedURL(page: Page, url: string): Promise<boolean> {
  await page.goto(url);
  await waitForNetworkIdle(page);
  return page.url().includes('/login');
}

// Helper function to generate test data
export function generateTestData() {
  const timestamp = Date.now();
  return {
    email: `test${timestamp}@example.com`,
    password: `Test${timestamp}@123456`,
    name: `Test User ${timestamp}`,
    bio: `This is a test bio ${timestamp}`
  };
}

// Helper function to clear test data
export async function clearTestData(page: Page) {
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}

// Helper function to mock API responses
export async function mockAPIResponse(page: Page, url: string, response: any) {
  await page.route(url, route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify(response)
    });
  });
}

// Helper function to check for error messages
export async function checkErrorMessage(page: Page, message: string) {
  const errorElement = page.locator('[data-testid=error-message]');
  await expect(errorElement).toBeVisible();
  await expect(errorElement).toContainText(message);
}

// Helper function to check for success messages
export async function checkSuccessMessage(page: Page, message: string) {
  const successElement = page.locator('[data-testid=success-message]');
  await expect(successElement).toBeVisible();
  await expect(successElement).toContainText(message);
}

// Helper function to handle file uploads
export async function uploadFile(page: Page, selector: string, fileContent: Buffer, fileName: string) {
  const fileInput = page.locator(selector);
  await fileInput.setInputFiles({
    name: fileName,
    mimeType: 'application/octet-stream',
    buffer: fileContent
  });
}

// Helper function to check form validation
export async function checkFormValidation(page: Page, formSelector: string) {
  await page.locator(formSelector).evaluate((form: HTMLFormElement) => form.reportValidity());
  const invalidFields = await page.$$('[aria-invalid="true"]');
  return invalidFields.length > 0;
}

// Helper function to handle confirmation dialogs
export async function handleConfirmationDialog(page: Page, confirm: boolean) {
  page.on('dialog', dialog => {
    if (confirm) {
      dialog.accept();
    } else {
      dialog.dismiss();
    }
  });
}

// Helper function to check accessibility
export async function checkAccessibility(page: Page) {
  // Note: This requires @axe-core/playwright to be installed
  // await new AxeBuilder({ page }).analyze();
}

// Helper function to test responsive behavior
export async function testResponsive(page: Page, selector: string) {
  const viewports = [
    { width: 1920, height: 1080 }, // Desktop
    { width: 1024, height: 768 },  // Tablet
    { width: 375, height: 667 }    // Mobile
  ];

  for (const viewport of viewports) {
    await page.setViewportSize(viewport);
    await expect(page.locator(selector)).toBeVisible();
  }
}

// Helper function to test keyboard navigation
export async function testKeyboardNavigation(page: Page, elements: string[]) {
  await page.keyboard.press('Tab');
  for (const element of elements) {
    await expect(page.locator(element)).toBeFocused();
    await page.keyboard.press('Tab');
  }
}

// Common test selectors
export const SELECTORS = {
  // Auth
  loginButton: '[data-testid=login-button]',
  signupButton: '[data-testid=signup-button]',
  logoutButton: '[data-testid=logout-button]',
  
  // Navigation
  navbar: '[data-testid=navbar]',
  sidebar: '[data-testid=sidebar]',
  
  // Forms
  form: '[data-testid=form]',
  submitButton: '[data-testid=submit-button]',
  
  // Messages
  errorMessage: '[data-testid=error-message]',
  successMessage: '[data-testid=success-message]',
  
  // Common elements
  loader: '[data-testid=loader]',
  modal: '[data-testid=modal]',
  toast: '[data-testid=toast]'
}; 