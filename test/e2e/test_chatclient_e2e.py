# E2Eテスト: ChatClientからの操作をChromium(Python+Playwright)で模倣
# 実行には playwright のインストールとブラウザセットアップが必要です
#   pip install playwright
#   playwright install chromium

import asyncio
from playwright.async_api import async_playwright

CHATCLIENT_URL = "http://localhost:5173"  # ChatClientのローカルURL（docker-composeでポートマッピングしている場合は適宜変更）

async def run_e2e():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(CHATCLIENT_URL)
        # 例: チャット入力欄にテキストを入力し送信ボタンをクリック
        await page.fill('input[type="text"]', 'CPUメトリクスを教えて')
        await page.click('button[type="submit"]')
        # レスポンスが表示されるまで待機
        await page.wait_for_selector('.chat-message', timeout=5000)
        messages = await page.query_selector_all('.chat-message')
        assert len(messages) > 0
        print("E2E: ChatClientからの送信・応答取得OK")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_e2e())
