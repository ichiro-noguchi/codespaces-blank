# E2Eテスト: ChatClientからの操作をChromium(Python+Playwright)で模倣
# 実行には playwright のインストールとブラウザセットアップが必要です
#   pip install playwright
#   playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

CHATCLIENT_URL = os.environ.get("CHATCLIENT_URL", "http://localhost:3000")  # ChatClientのローカルURL（docker-composeでポートマッピングしている場合は適宜変更）

async def run_e2e():
    print("[E2E] ブラウザ起動...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"[E2E] {CHATCLIENT_URL} にアクセス...")
        await page.goto(CHATCLIENT_URL)
        print("[E2E] 入力欄にテキスト入力...")
        await page.fill('div.chat-input input', 'CPUメトリクスを教えて')
        print("[E2E] 送信ボタンをクリック...")
        await page.click('div.chat-input button')
        print("[E2E] レスポンス待機...")
        await page.wait_for_selector('.msg-user, .msg-ai', timeout=5000)
        messages = await page.query_selector_all('.msg-user, .msg-ai')
        print(f"[E2E] メッセージ数: {len(messages)}")
        assert len(messages) > 0
        print("E2E: ChatClientからの送信・応答取得OK")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_e2e())
