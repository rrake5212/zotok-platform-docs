#!/usr/bin/env python3
"""
Debug login to https://app-qa.zotok.ai — step-by-step screenshots.
"""

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

BASE_URL = "https://app-qa.zotok.ai"
PHONE = "3203220232"
OUTPUT_DIR = Path("/mnt/d/AgentWork/platform-docs/pipeline/discovery")
os.makedirs(OUTPUT_DIR, exist_ok=True)
DBG = OUTPUT_DIR / "debug"
os.makedirs(DBG, exist_ok=True)


def debug_login():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        # Listen for all navigations/requests
        page.on("response", lambda resp: print(f"  RESP {resp.status} {resp.url[:100]}"))

        print(f"1. Navigating to {BASE_URL}")
        page.goto(BASE_URL, wait_until="load", timeout=30000)
        page.wait_for_timeout(5000)
        page.screenshot(path=str(DBG / "01_initial_load.png"))

        # Dump page info
        print(f"   URL: {page.url}")
        print(f"   Title: {page.title()}")

        # Find all inputs
        inputs = page.evaluate("""
        () => Array.from(document.querySelectorAll('input, button')).map(el => ({
            tag: el.tagName,
            type: el.type || '',
            name: el.name || '',
            id: el.id || '',
            placeholder: el.placeholder || '',
            text: (el.textContent || '').trim().substring(0, 50),
            class: (el.className || '').substring(0, 60),
            visible: el.offsetParent !== null
        }))
        """)
        print(f"   Found {len(inputs)} input/button elements:")
        for inp in inputs:
            print(f"     [{inp['tag']}] type={inp['type']:12s} name={inp['name']:15s} pl={inp['placeholder']:15s} text={inp['text'][:40]:40s} visible={inp['visible']}")

        # Enter phone
        print(f"\n2. Entering phone: {PHONE}")
        phone_input = page.locator('input[name="loginVal"]').first
        phone_input.wait_for(state="visible", timeout=10000)
        phone_input.fill(PHONE)
        page.wait_for_timeout(500)
        page.screenshot(path=str(DBG / "02_phone_entered.png"))

        # Click Continue
        print("3. Clicking Continue...")
        cont_btn = page.locator('button:has-text("Continue")').first
        print(f"   Continue btn exists: {cont_btn.count()}")
        if cont_btn.count() > 0:
            cont_btn.click()
        else:
            # Try any submit button
            page.locator('button[type="submit"], button:has-text("Send"), button:has-text("Login")').first.click()

        page.wait_for_timeout(3000)
        page.screenshot(path=str(DBG / "03_after_continue.png"))
        print(f"   URL after continue: {page.url}")

        # Check for OTP inputs
        otp_count = page.locator('input[type="number"]').count()
        print(f"\n4. OTP inputs visible: {otp_count}")

        all_inputs_after = page.evaluate("""
        () => Array.from(document.querySelectorAll('input, button')).map(el => ({
            tag: el.tagName,
            type: el.type || '',
            name: el.name || '',
            id: el.id || '',
            placeholder: el.placeholder || '',
            text: (el.textContent || '').trim().substring(0, 50),
            class: (el.className || '').substring(0, 60),
            visible: el.offsetParent !== null,
            value: el.value || ''
        }))
        """)
        for inp in all_inputs_after:
            print(f"     [{inp['tag']}] type={inp['type']:12s} name={inp['name']:15s} pl={inp['placeholder']:15s} text={inp['text'][:40]:40s} value={inp['value']:10s} visible={inp['visible']}")

        # Wait for auto-OTP fill
        print("\n5. Waiting for auto-OTP fill...")
        otp_inputs = page.locator('input[type="number"]')
        for attempt in range(30):
            count = otp_inputs.count()
            filled = sum(1 for i in range(count) if otp_inputs.nth(i).input_value())
            if filled >= count and count >= 4:
                print(f"   OTP filled after {attempt+1}s: {filled}/{count} digits")
                break
            page.wait_for_timeout(1000)
        else:
            print(f"   OTP did NOT auto-fill within 30s. Current fills: ", end="")
            for i in range(otp_inputs.count()):
                print(otp_inputs.nth(i).input_value(), end="")
            print()

        page.screenshot(path=str(DBG / "04_otp_filled.png"))

        # Check what buttons are available now
        verify_btns = page.evaluate("""
        () => Array.from(document.querySelectorAll('button')).map(el => ({
            text: (el.textContent || '').trim().substring(0, 50),
            type: el.type || '',
            class: (el.className || '').substring(0, 60),
            disabled: el.disabled,
            visible: el.offsetParent !== null
        }))
        """)
        print("\n6. Available buttons:")
        for btn in verify_btns:
            print(f"     text='{btn['text']:40s}' type={btn['type']:12s} disabled={btn['disabled']} visible={btn['visible']}")

        # Try clicking verify OTP
        verify = page.locator('button:has-text("Verify OTP")').first
        if verify.count() > 0 and verify.is_visible():
            print("\n7. Clicking 'Verify OTP'...")
            verify.click()
        else:
            # Try other buttons
            for btn_text in ["Verify", "Submit", "Login", "Next"]:
                btn = page.locator(f'button:has-text("{btn_text}")').first
                if btn.count() > 0 and btn.is_visible():
                    print(f"\n7. Clicking '{btn_text}' instead...")
                    btn.click()
                    break

        page.wait_for_timeout(5000)
        page.screenshot(path=str(DBG / "05_after_verify.png"))
        print(f"   URL after verify: {page.url}")
        print(f"   Title after verify: {page.title()}")

        # Check if we're logged in
        if "login" in page.url.lower():
            print("\n8. Still on login page. Checking for error messages...")
            body_text = page.evaluate("() => document.body.innerText")
            print(f"   Page body text (first 1000 chars):\n{body_text[:1000]}")

            # Check localStorage for session
            ls = page.evaluate("() => JSON.stringify(window.localStorage)")
            print(f"\n   localStorage keys: {len(ls)} chars")

            # Check for hidden iframes or redirects
            frames = page.frames
            print(f"\n   Frames: {len(frames)}")
            for i, f in enumerate(frames):
                print(f"     [{i}] {f.url[:100]}")
        else:
            print("\n8. Login appears successful!")
            page.screenshot(path=str(DBG / "06_logged_in.png"))

        browser.close()


if __name__ == "__main__":
    debug_login()
