#!/usr/bin/env python3
"""Probe the DOM after login to find sidebar/nav structure."""
import json, os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://app-qa.zotok.ai"
PHONE = "3203220232"
OUT = Path("/mnt/d/AgentWork/platform-docs/pipeline/discovery")
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    p = ctx.new_page()

    # Login
    p.goto(BASE_URL, wait_until="load", timeout=30000)
    p.wait_for_timeout(5000)
    p.locator('input[name="loginVal"]').first.fill(PHONE)
    p.wait_for_timeout(500)
    p.locator('button:has-text("Continue")').first.click()
    p.wait_for_timeout(3000)
    otp = p.locator('input[type="number"]')
    for i in range(30):
        filled = sum(1 for j in range(otp.count()) if otp.nth(j).input_value())
        if filled >= 4:
            break
        p.wait_for_timeout(1000)
    p.locator('button:has-text("Verify OTP")').first.click()
    p.wait_for_timeout(10000)

    print(f"URL: {p.url}")

    # Dismiss overlay if any
    p.keyboard.press("Escape")
    p.wait_for_timeout(2000)

    # Strategy 1: Dump ALL elements to find nav-like ones
    all_els = p.evaluate("""
    () => {
        const results = [];
        document.querySelectorAll('*').forEach(el => {
            try {
                const cn = (el.className || '').toString();
                const rect = el.getBoundingClientRect();
                const text = (el.textContent || '').trim();
                if (rect.width > 0 && rect.height > 0 && text.length > 0 && text.length < 80) {
                    const is_relevant =
                        cn.includes('sidebar') || cn.includes('Sidebar') ||
                        cn.includes('nav') || cn.includes('Nav') ||
                        cn.includes('menu') || cn.includes('Menu') ||
                        cn.includes('drawer') || cn.includes('Drawer') ||
                        cn.includes('list') || cn.includes('List') ||
                        cn.includes('item') || cn.includes('Item') ||
                        cn.includes('tab') || cn.includes('Tab') ||
                        cn.includes('MuiList') || cn.includes('MuiDrawer') ||
                        cn.includes('MuiNav') || cn.includes('MuiMenuItem') ||
                        el.tagName === 'NAV' ||
                        el.tagName === 'A' || el.tagName === 'BUTTON' ||
                        el.getAttribute('role') === 'button' ||
                        el.getAttribute('role') === 'tab' ||
                        el.getAttribute('role') === 'menuitem' ||
                        el.getAttribute('role') === 'treeitem' ||
                        el.getAttribute('role') === 'navigation';

                    if (is_relevant) {
                        results.push({
                            tag: el.tagName,
                            class: cn.substring(0, 100),
                            text: text.substring(0, 60),
                            rect: `${Math.round(rect.x)},{Math.round(rect.y)} {Math.round(rect.w)}x{Math.round(rect.h)}`,
                            role: el.getAttribute('role') || '',
                            id: el.id || ''
                        });
                    }
                }
            } catch(e) {}
        });
        return results;
    }
    """)

    print(f"\nTotal relevant elements: {len(all_els)}")

    # Print only ones with known module names
    known_modules = ['Home', 'Dashboard', 'Sales', 'Payments', 'Item', 'Product', 'Day Book',
                     'Customers', 'Queries', 'Threads', 'Campaigns', 'Orders', 'Invoices',
                     'Ledger', 'Schemes', 'Price List', 'Field Ops', 'Forms', 'Settings',
                     'Grow']
    printed = set()
    for r in all_els:
        t = r['text'].strip()
        if t in known_modules and t not in printed:
            printed.add(t)
            print(f"  [{r['tag']:6s}] class={r['class'][:60]:60s} text={t:20s} rect={r['rect']:25s}")

    # Also screenshot
    p.screenshot(path=str(OUT / "probe.png"), full_page=True)

    # Save full data
    with open(OUT / "probe_elements.json", "w") as f:
        json.dump(all_els, f, indent=2)

    # Strategy 2: Dump ALL text on page to see what's visible
    body_text = p.evaluate("() => document.body.innerText")
    print(f"\n--- BODY TEXT (first 2000 chars) ---\n{body_text[:2000]}")

    # Strategy 3: Check for specific known selectors
    print("\n--- Checking specific selectors ---")
    checks = [
        ("a[href*='/admin/']", "a[href*='/admin/']"),
        ("[class*='MuiListItemButton']", "MuiListItemButton"),
        ("[class*='MuiListItem']", "MuiListItem"),
        ("[class*='MuiDrawer']", "MuiDrawer"),
        ("[role='navigation']", "role=navigation"),
        ("nav", "nav tag"),
        ("aside", "aside tag"),
        ("[class*='sidebar']", "sidebar class"),
        ("[class*='Sidebar']", "Sidebar class"),
    ]
    for sel, name in checks:
        count = len(p.query_selector_all(sel))
        print(f"  {name:30s}: {count} found")

    ctx.close()
    b.close()
