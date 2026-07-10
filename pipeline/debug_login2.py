#!/usr/bin/env python3
"""
Debug login — check if app is actually logged in despite /login URL.
The SPA may keep URL as /login while rendering dashboard content.
"""

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

BASE_URL = "https://app-qa.zotok.ai"
PHONE = "3203220232"
OUTPUT_DIR = Path("/mnt/d/AgentWork/platform-docs/pipeline/discovery")
DBG = OUTPUT_DIR / "debug2"
os.makedirs(DBG, exist_ok=True)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        page = context.new_page()

        # Track API calls
        api_calls = []
        page.on("response", lambda resp: api_calls.append({"url": resp.url, "status": resp.status, "ok": resp.ok}))

        # --- LOGIN ---
        print("1. Loading page...")
        page.goto(BASE_URL, wait_until="load", timeout=30000)
        page.wait_for_timeout(5000)

        print("2. Entering phone...")
        page.locator('input[name="loginVal"]').first.fill(PHONE)
        page.wait_for_timeout(500)

        print("3. Clicking Continue...")
        page.locator('button:has-text("Continue")').first.click()
        page.wait_for_timeout(3000)

        print("4. Waiting for auto-OTP...")
        otp_inputs = page.locator('input[type="number"]')
        for attempt in range(30):
            count = otp_inputs.count()
            filled = sum(1 for i in range(count) if otp_inputs.nth(i).input_value())
            if filled >= count and count >= 4:
                print(f"   OTP filled after {attempt+1}s")
                break
            page.wait_for_timeout(1000)

        print("5. Clicking Verify OTP...")
        page.locator('button:has-text("Verify OTP")').first.click()
        page.wait_for_timeout(8000)  # Wait for post-login rendering

        # --- DIAGNOSE ---
        print(f"\n6. Current URL: {page.url}")
        page.screenshot(path=str(DBG / "state.png"), full_page=True)

        # Check if there's any auth token in localStorage
        ls = page.evaluate("() => { const k = Object.keys(localStorage); return k.map(key => ({key, val: localStorage.getItem(key).substring(0,100)})); }")
        print(f"\n   localStorage ({len(ls)} keys):")
        for item in ls:
            print(f"     {item['key']}: {item['val'][:80]}")

        # Check sessionStorage
        ss = page.evaluate("() => { const k = Object.keys(sessionStorage); return k.map(key => ({key, val: sessionStorage.getItem(key).substring(0,100)})); }")
        print(f"\n   sessionStorage ({len(ss)} keys):")
        for item in ss:
            print(f"     {item['key']}: {item['val'][:80]}")

        # Dump full body text
        body = page.evaluate("() => document.body.innerText")
        print(f"\n   Body text:\n{body[:2000]}")

        # Check for any hidden elements with auth-related content
        print(f"\n7. Looking for dashboard/sidebar elements...")
        dashboard_items = page.evaluate("""
        () => {
            const results = [];
            const selectors = [
                '[class*="sidebar"]', '[class*="Sidebar"]',
                '[class*="dashboard"]', '[class*="Dashboard"]',
                '[class*="drawer"]', '[class*="Drawer"]',
                'nav', '[role="navigation"]',
                '[class*="app-bar"]', '[class*="AppBar"]',
                '[class*="MuiDrawer"]', '[class*="MuiAppBar"]',
                '[class*="header"]', '[class*="Header"]',
                '[class*="main"]', 'main',
            ];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        results.push({
                            selector: sel,
                            classes: (el.className || '').substring(0, 80),
                            rect: `${Math.round(rect.x)},${Math.round(rect.y)} ${Math.round(rect.w)}x${Math.round(rect.h)}`,
                            text: (el.textContent || '').trim().substring(0, 80)
                        });
                    }
                });
            });
            return results;
        }
        """)
        if dashboard_items:
            print(f"   Found {len(dashboard_items)} visible structural elements:")
            for d in dashboard_items[:30]:
                print(f"     {d['selector']:35s} class={d['classes'][:50]:50s} rect={d['rect']:20s} text={d['text'][:40]}")
        else:
            print("   No structural elements found — page is likely still login.")

        # Check for hidden divs with logged-in content
        print(f"\n8. Checking for hidden app content...")
        hidden_app = page.evaluate("""
        () => {
            const divs = document.querySelectorAll('div[style*="display"]');
            return Array.from(divs).filter(d => d.textContent.length > 100 && d.textContent.includes('Dashboard')).map(d => ({
                display: d.style.display,
                visibility: d.style.visibility,
                class: (d.className || '').substring(0, 60),
                text: d.textContent.trim().substring(0, 200)
            }));
        }
        """)
        if hidden_app:
            print(f"   Found {len(hidden_app)} hidden containers with app content!")
            for h in hidden_app:
                print(f"     display={h['display']:10s} visibility={h['visibility']:10s} class={h['class']}")
                print(f"     text: {h['text'][:150]}")
        else:
            print("   No hidden app content found.")

        # Check API responses for verifyotp
        print(f"\n9. Key API responses:")
        for call in api_calls:
            if 'verifyotp' in call['url'] or 'workspaces' in call['url'] or 'roles' in call['url']:
                print(f"   {call['status']} {call['url'][:80]}")

        browser.close()


if __name__ == "__main__":
    main()
