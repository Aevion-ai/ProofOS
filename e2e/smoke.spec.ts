import { test, expect } from '@playwright/test';

test('aevion.ai renders correctly', async ({ page }) => {
  // Serve the built dist folder locally
  // Set a short timeout for font loading to prevent hanging
  await page.route('**/*.woff2', route => route.abort());
  await page.route('**/fonts.googleapis.com**', route => route.abort());
  await page.goto('http://localhost:4173', { waitUntil: 'domcontentloaded' });

  // Title
  await expect(page).toHaveTitle(/Aevion/);

  // Hero headline
  await expect(page.locator('h1')).toContainText(/Proof|Governance|Aevion/i, { timeout: 10000 });

  // KPI dashboard — exact match to avoid strict mode violation with supporting text
  await expect(page.getByText('1,252', { exact: true })).toBeVisible({ timeout: 10000 });
  await expect(page.getByText('96%', { exact: true })).toBeVisible();
  await expect(page.getByText('104', { exact: true })).toBeVisible();

  // Verify hero content is visible
  await expect(page.getByText('Proof-Native')).toBeVisible({ timeout: 10000 });
  await expect(page.getByText('GOVERNANCE')).toBeVisible();
  await expect(page.getByText('for Frontier AI')).toBeVisible();
  await expect(page.getByText('NIST published the proof')).toBeVisible();

  // Verify KPI cards
  await expect(page.getByText('1,252', { exact: true })).toBeVisible();
  await expect(page.getByText('96%', { exact: true })).toBeVisible();
  await expect(page.getByText('88%', { exact: true })).toBeVisible();

  // Navigate to Platform Products tab
  await page.getByText('Platform Products').click();
  await page.waitForTimeout(500);

  // Verify product cards are visible (use exact to avoid strict mode on summary text)
  await expect(page.getByText('Constitutional Halt Gate', { exact: true })).toBeVisible({ timeout: 5000 });
  await expect(page.getByText('Receipt Chain', { exact: true })).toBeVisible();
  await expect(page.getByText('Agent Counsel Colony', { exact: true })).toBeVisible();
  await expect(page.getByText('ProofDB', { exact: true })).toBeVisible();

  // Screenshot
  await page.screenshot({ path: 'e2e/screenshots/aevion-homepage.png' });
  console.log('All content verified + screenshot saved.');
});
