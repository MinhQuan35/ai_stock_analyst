"""
Playwright Automated Test & Screenshot Capture
Runs against running server http://127.0.0.1:8000
Captures high-res OLED dark mode screenshots of the Stock Detail Dashboard:
1. NVDA (Global Tech with live quote & SVG trajectory chart)
2. AMD (Stock selection & dynamic update)
3. FPT (Vietnam VN30 Equities with live quote & trajectory)
"""
import os
import shutil
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\DELL\.gemini\antigravity-ide\brain\260ec6d3-a0f2-4cd6-b85e-6ed1ca3a23a3"
DOCS_DIR = os.path.join(os.getcwd(), "docs", "screenshots")
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def main():
    print("Starting Playwright automation against http://127.0.0.1:8000 ...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1080}, device_scale_factor=2)
        page = context.new_page()

        # 1. Navigate to Workbench
        print("Navigating to dashboard...", flush=True)
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")

        # 2. Wait for NVDA live price & SVG chart
        print("Waiting for NVDA details & trajectory chart...", flush=True)
        page.wait_for_function(
            "document.getElementById('worldBigPrice') && document.getElementById('worldBigPrice').innerText !== '--'",
            timeout=20000
        )
        page.wait_for_selector("#worldChartSvg path", timeout=10000)
        time.sleep(1.5)

        nvda_price = page.inner_text("#worldBigPrice")
        nvda_delta = page.inner_text("#worldDeltaPill")
        print(f"NVDA Loaded: ${nvda_price} ({nvda_delta})", flush=True)

        # Screenshot 1: NVDA
        nvda_file = os.path.join(DOCS_DIR, "dashboard_nvda.png")
        page.screenshot(path=nvda_file, full_page=True)
        shutil.copyfile(nvda_file, os.path.join(ARTIFACT_DIR, "dashboard_nvda.png"))
        print(f"Captured: {nvda_file}", flush=True)

        # 3. Select AMD
        print("Clicking AMD card...", flush=True)
        page.click("#card-world-AMD")
        page.wait_for_function(
            "document.getElementById('worldSymBadge') && document.getElementById('worldSymBadge').innerText === 'AMD'",
            timeout=10000
        )
        time.sleep(1.5)
        amd_price = page.inner_text("#worldBigPrice")
        print(f"AMD Loaded: ${amd_price}", flush=True)

        amd_file = os.path.join(DOCS_DIR, "dashboard_amd.png")
        page.screenshot(path=amd_file, full_page=True)
        shutil.copyfile(amd_file, os.path.join(ARTIFACT_DIR, "dashboard_amd.png"))
        print(f"Captured: {amd_file}", flush=True)

        page.on("console", lambda msg: print(f"PAGE CONSOLE: {msg.text}", flush=True))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}", flush=True))

        # 4. Switch to Vietnam Tab
        print("Switching to Vietnam Market Tab...", flush=True)
        page.evaluate("switchMarketTab('vn')")
        page.wait_for_function(
            "document.getElementById('vnBigPrice') && document.getElementById('vnBigPrice').innerText !== '--'",
            timeout=25000
        )
        page.wait_for_selector("#vnChartSvg path", timeout=10000)
        time.sleep(1.5)

        fpt_price = page.inner_text("#vnBigPrice")
        fpt_delta = page.inner_text("#vnDeltaPill")
        print(f"FPT Loaded: {fpt_price} VND ({fpt_delta})", flush=True)

        fpt_file = os.path.join(DOCS_DIR, "dashboard_fpt.png")
        page.screenshot(path=fpt_file, full_page=True)
        shutil.copyfile(fpt_file, os.path.join(ARTIFACT_DIR, "dashboard_fpt.png"))
        print(f"Captured: {fpt_file}", flush=True)

        browser.close()
        print("All 3 Playwright tests & screenshots completed successfully!", flush=True)

if __name__ == "__main__":
    main()
