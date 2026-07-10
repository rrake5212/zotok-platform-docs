#!/usr/bin/env python3
"""
Phase 1: Discovery & Navigation Map
====================================
Crawl https://app-qa.zotok.ai to discover every module, page, route,
and overlay. Build a complete navigation tree for downstream capture.
"""

import json
import os
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

BASE_URL = "https://app-qa.zotok.ai"
PHONE = "3203220232"
OUTPUT_DIR = Path(__file__).parent / "discovery"
SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"
COOKIE_FILE = OUTPUT_DIR / "cookies.json"
NAV_TREE_FILE = OUTPUT_DIR / "navigation_tree.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def login(page):
    """Login with phone + auto-OTP."""
    print("--- LOGIN ---")
    page.goto(BASE_URL, wait_until="load", timeout=30000)
    page.wait_for_timeout(5000)
    page.locator('input[name="loginVal"]').first.fill(PHONE)
    page.wait_for_timeout(500)
    page.locator('button:has-text("Continue")').first.click()
    page.wait_for_timeout(3000)
    otp = page.locator('input[type="number"]')
    for i in range(30):
        filled = sum(1 for j in range(otp.count()) if otp.nth(j).input_value())
        if filled >= 4:
            break
        page.wait_for_timeout(1000)
    page.locator('button:has-text("Verify OTP")').first.click()
    try:
        page.wait_for_url("**/admin/**", timeout=15000)
    except PwTimeout:
        pass
    page.wait_for_timeout(5000)
    print(f"URL: {page.url}")
    return "login" not in page.url.lower()


def dismiss_overlays(page):
    """Dismiss any onboarding/notification popups."""
    for _ in range(3):
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
    for btn_text in ["Ok, Got it", "Got it", "Close", "Dismiss", "Skip"]:
        try:
            btn = page.get_by_text(btn_text)
            if btn.count() > 0:
                btn.click()
                page.wait_for_timeout(1000)
        except:
            pass


def discover_sidebar(page, screenshot_dir):
    """
    Discover the full sidebar structure (primary + secondary).
    Returns dict of primary items with their sub-items.
    """
    print("\n--- DISCOVERING SIDEBAR ---")
    dismiss_overlays(page)

    # Find all primary sidebar items (icons with aria-label)
    primary_items = page.evaluate("""
    () => {
        const items = [];
        document.querySelectorAll('.primary-item-wrapper').forEach(el => {
            const label = el.getAttribute('aria-label') || '';
            const cls = el.className;
            const is_active = cls.includes('is-active') || cls.includes('active');
            items.push({
                label: label,
                is_active: is_active,
                classes: cls.substring(0, 100)
            });
        });
        return items;
    }
    """)
    print(f"Found {len(primary_items)} primary sidebar items:")
    for item in primary_items:
        print(f"  • {item['label']:15s} active={item['is_active']}")

    # Also check what's currently visible secondary panel
    secondary_items_initial = page.evaluate("""
    () => {
        // Look for secondary/second level nav panel
        const panels = document.querySelectorAll(
            '[class*="secondary"], [class*="Secondary"], [class*="sub-nav"], [class*="subNav"], [class*="submenu"], [class*="subMenu"]'
        );
        const items = [];
        panels.forEach(p => {
            p.querySelectorAll('a, button, [role="button"], span, div').forEach(el => {
                const text = (el.textContent || '').trim();
                if (text && text.length < 60 && text.length > 0) {
                    items.push(text.substring(0, 60));
                }
            });
        });
        return items;
    }
    """)
    if secondary_items_initial:
        print(f"Initial secondary items visible: {secondary_items_initial}")

    # Now explore each primary item and its secondary menu
    nav_tree = {}
    homepage = page.url

    for item in primary_items:
        label = item["label"]
        if not label:
            continue

        print(f"\n--- Clicking primary: '{label}' ---")
        try:
            # Click by aria-label
            primary_el = page.locator(f'.primary-item-wrapper[aria-label="{label}"]').first
            primary_el.wait_for(state="visible", timeout=5000)
            primary_el.click()
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"  Click failed: {e}")
            continue

        after_url = page.url
        print(f"  URL: {after_url}")
        page.screenshot(path=str(screenshot_dir / f"primary_{label.lower()}.png"), full_page=True)

        # Now check the secondary panel that appeared
        sec_items = page.evaluate("""
        () => {
            const items = [];
            // Find all text elements in the secondary panel area
            const panels = document.querySelectorAll(
                '[class*="secondary"], [class*="Secondary"], [class*="sub-nav"]'
            );
            panels.forEach(p => {
                p.querySelectorAll('a, button, [role="button"], span, div').forEach(el => {
                    const text = (el.textContent || '').trim();
                    if (text && text.length < 60 && text.length > 1) {
                        const href = el.getAttribute('href') || el.getAttribute('to') || '';
                        items.push({
                            text: text.substring(0, 60),
                            href: href.substring(0, 120),
                            tag: el.tagName
                        });
                    }
                });
            });

            // Fallback: look for any newly appeared nav-like text elements
            // after clicking, that weren't there before
            if (items.length === 0) {
                document.querySelectorAll('[class*="item"], [class*="Item"], [class*="list"], [class*="List"]').forEach(el => {
                    const text = (el.textContent || '').trim();
                    if (text && text.length < 60 && text.length > 1) {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            items.push({
                                text: text.substring(0, 60),
                                href: '',
                                tag: el.tagName
                            });
                        }
                    }
                });
            }

            return items;
        }
        """)

        # Deduplicate secondary items
        seen = set()
        unique_sec = []
        for s in sec_items:
            t = s["text"]
            if t and t not in seen:
                seen.add(t)
                unique_sec.append(s)

        print(f"  Secondary items: {len(unique_sec)}")
        for s in unique_sec:
            print(f"    • {s['text'][:50]:50s} href={s['href'][:40]}")

        nav_tree[label] = {
            "url": after_url,
            "secondary_items": unique_sec,
        }

        # Navigate back to home
        page.goto(homepage, wait_until="load", timeout=15000)
        page.wait_for_timeout(3000)

    return nav_tree


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        page = context.new_page()

        # Login
        if not login(page):
            print("Login failed.")
            browser.close()
            return
        cookies = context.cookies()
        with open(COOKIE_FILE, "w") as f:
            json.dump(cookies, f)
        print(f"Saved {len(cookies)} cookies")

        # Discover sidebar structure
        sidebar = discover_sidebar(page, SCREENSHOT_DIR)

        # Build navigation tree
        nav_tree = {
            "base_url": BASE_URL,
            "phone": PHONE,
            "home_url": page.url,
            "sidebar": sidebar,
            "timestamp": time.time(),
        }

        with open(NAV_TREE_FILE, "w") as f:
            json.dump(nav_tree, f, indent=2)
        print(f"\n{'='*60}")
        print(f"Navigation tree saved to {NAV_TREE_FILE}")
        print(f"Discovered {len(sidebar)} primary modules:")
        for label, info in sidebar.items():
            sec = [s["text"] for s in info["secondary_items"]]
            print(f"  • {label:15s} → {len(sec)} sub-items: {', '.join(sec[:10])}{'...' if len(sec) > 10 else ''}")
        print(f"{'='*60}")

        browser.close()


if __name__ == "__main__":
    main()
