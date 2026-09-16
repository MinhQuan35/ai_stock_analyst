"""
Automated Playwright On-Screen UI Demo Test.
Launches browser in headed mode to demonstrate the dual-market UI:
- Global AI & Big Tech tab (NVDA, MSFT live quotes)
- Vietnam Stocks tab (FPT, VCB live quotes & RAG)
- Captures screenshots for verification.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright


async def run_on_screen_demo():
    screenshot_dir = Path("./logs/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    print("🚀 Launching Playwright On-Screen Demo Browser (Headed Mode)...")
    async with async_playwright() as p:
        # Launch headed browser with slow motion for clear visual demonstration
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        target_url = "http://127.0.0.1:8000/"
        print(f"🌐 Navigating to {target_url}...")
        connected = False
        for attempt in range(1, 6):
            try:
                await page.goto(target_url, timeout=10000)
                connected = True
                break
            except Exception as e:
                print(f"⏳ Waiting for server at {target_url} (attempt {attempt}/5)...")
                await asyncio.sleep(2)

        if not connected:
            print(f"❌ Could not connect to {target_url}. Please start the server in a terminal:")
            print("   uvicorn src.api.routes:app --reload --port 8000")
            await browser.close()
            return


        # Wait for dashboard to load
        await page.wait_for_selector(".brand")
        print("✅ Dashboard loaded successfully.")
        await page.screenshot(path=str(screenshot_dir / "01_initial_dashboard.png"))

        # Step 1: Demo Global AI & Big Tech tab
        print("⚡ Clicking on 'NVDA' AI Chips ticker card...")
        await page.click(".ticker-card:has-text('NVDA')")
        
        # Wait for agent response
        await page.wait_for_selector(".msg.agent:nth-of-type(2)", timeout=30000)
        print("✅ Global AI stock response rendered.")
        await page.screenshot(path=str(screenshot_dir / "02_global_nvda_quote.png"))

        # Step 2: Switch to Vietnam Market Tab
        print("⚡ Switching to Vietnam Stocks (VNX) tab...")
        await page.click("#btn-vn")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=str(screenshot_dir / "03_vietnam_market_tab.png"))

        # Step 3: Click FPT Ticker
        print("⚡ Clicking on 'FPT' ticker card...")
        await page.click(".ticker-card:has-text('FPT')")
        
        # Wait for agent response
        await page.wait_for_selector("#chatBoxVn .msg.agent:nth-of-type(2)", timeout=30000)
        print("✅ Vietnam stock response rendered.")
        await page.screenshot(path=str(screenshot_dir / "04_vietnam_fpt_quote.png"))

        # Step 4: Switch to Benchmark Metrics Tab
        print("⚡ Switching to RAG Benchmark Metrics tab...")
        await page.click("#btn-metrics")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(screenshot_dir / "05_metrics_benchmark.png"))

        print("\n🎉 On-screen demo completed successfully!")
        print(f"📸 Screenshots saved to {screenshot_dir.resolve()}")
        await page.wait_for_timeout(3000)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(run_on_screen_demo())
