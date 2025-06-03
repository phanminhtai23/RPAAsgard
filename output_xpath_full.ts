import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
    await page.goto('https://www.facebook.com/');
    await page.locator('xpath=//*[@data-testid="royal-email"]').click();
    await page.locator('xpath=//*[@data-testid="royal-email"]').fill('taikhoan');
    await page.locator('xpath=//*[@data-testid="royal-email"]').press('Tab');
    await page.locator('xpath=//*[@data-testid="royal-pass"]').fill('matkhau');
    await page.locator('xpath=//*[@data-testid="royal-login-button"]').click();
    await page.waitForTimeout(10000);
});