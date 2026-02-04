"""
Screenshot capture script for dashboard
"""
import asyncio
from playwright.async_api import async_playwright

async def capture_dashboard():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navigate to dashboard
        await page.goto('http://127.0.0.1:8050')
        await page.wait_for_timeout(5000)  # Wait for page to load
        
        # Screenshot 1: Executive Summary (default page)
        await page.screenshot(path='screenshot_1_executive_summary.png', full_page=True)
        print("✓ Screenshot 1: Executive Summary")
        
        # Click on Delivery Performance tab
        await page.click('text=🚚 Delivery Performance')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='screenshot_2_delivery_performance.png', full_page=True)
        print("✓ Screenshot 2: Delivery Performance")
        
        # Click on Agent Performance tab
        await page.click('text=👤 Agent Performance')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='screenshot_3_agent_performance.png', full_page=True)
        print("✓ Screenshot 3: Agent Performance")
        
        await browser.close()
        print("\n✓ All screenshots captured successfully!")

if __name__ == "__main__":
    asyncio.run(capture_dashboard())
