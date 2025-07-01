import { test, expect } from '@playwright/test';

const CHATCLIENT_URL = process.env.CHATCLIENT_URL || 'http://localhost:3000';

test('ChatClient E2E: メッセージ送信と応答表示', async ({ page }) => {
  await page.goto(CHATCLIENT_URL);
  await page.fill('div.chat-input input', 'CPUメトリクスを教えて');
  await page.click('div.chat-input button');
  await page.waitForSelector('.msg-user, .msg-ai', { timeout: 10000 });
  const messages = await page.$$('.msg-user, .msg-ai');
  expect(messages.length).toBeGreaterThan(0);
});
