#!/usr/bin/env python3
"""
Phase 2: Per-Module Deep Capture
=================================
For each module in the navigation tree, capture:
- Full-page screenshot
- KPIs, tables, forms, buttons
- All visible text and UI structure
- Route information
Saves structured JSON per module for Phase 3 generation.
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

BASE_URL = "https://app-qa.zotok.ai"
PHONE = "3203220232"
DISCOVERY_DIR = Path(__file__).parent / "discovery"
CAPTURE_DIR = Path(__file__).parent / "capture"
SCREENSHOT_DIR = CAPTURE_DIR / "screenshots"
COOKIE_FILE = DISCOVERY_DIR / "cookies.json"
NAV_TREE_FILE = DISCOVERY_DIR / "navigation_tree.json"

os.makedirs(CAPTURE_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def load_nav_tree():
    with open(NAV_TREE_FILE) as f:
        return json.load(f)


def login(page):
    """Login using saved cookies or fresh auth."""
    page.goto(BASE_URL, wait_until="load", timeout=30000)
    page.wait_for_timeout(3000)

    # Try to load cookies first
    if COOKIE_FILE.exists():
        with open(COOKIE_FILE) as f:
            cookies = json.load(f)
        if cookies:
            page.context.add_cookies(cookies)
            page.goto(BASE_URL, wait_until="load", timeout=30000)
            page.wait_for_timeout(5000)
            if "login" not in page.url.lower() and "/admin/" in page.url:
                print("  Session restored from cookies.")
                return True

    # Fresh login
    print("  Fresh login required...")
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

    # Save cookies for next run
    cookies = page.context.cookies()
    with open(COOKIE_FILE, "w") as f:
        json.dump(cookies, f)

    return "login" not in page.url.lower()


def dismiss_overlays(page):
    """Dismiss any popups/notifications."""
    for _ in range(3):
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
    for btn_text in ["Ok, Got it", "Got it", "Close", "Dismiss", "Skip", "No thanks"]:
        try:
            btn = page.get_by_text(btn_text)
            if btn.count() > 0:
                btn.click()
                page.wait_for_timeout(500)
        except:
            pass


def capture_page_data(page, module_name, sub_name=""):
    """
    Extract all useful data from the current page.
    Returns a dict with KPIs, tables, forms, buttons, text content.
    """
    page_data = {
        "url": page.url,
        "title": page.title(),
        "module": module_name,
        "sub_module": sub_name,
        "timestamp": datetime.now().isoformat(),
    }

    # Extract ALL visible text content (structured)
    extracted = page.evaluate("""
    () => {
        const data = {};

        // 1. All heading text (h1-h6)
        data.headings = [];
        document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(el => {
            const t = (el.textContent || '').trim();
            if (t) data.headings.push({ tag: el.tagName, text: t.substring(0, 200) });
        });

        // 2. KPI cards — look for value+label pairs
        data.kpis = [];
        // Common KPI card patterns
        document.querySelectorAll(
            '[class*="kpi"], [class*="KPI"], [class*="card"], [class*="Card"], ' +
            '[class*="stat"], [class*="Stat"], [class*="metric"], [class*="Metric"], ' +
            '[class*="widget"], [class*="Widget"], [class*="summary"], [class*="Summary"]'
        ).forEach(el => {
            const text = (el.textContent || '').trim();
            // KPI cards typically have a number/amount and a label
            if (text && text.length < 200 && /[₹0-9]/.test(text)) {
                data.kpis.push(text.substring(0, 150));
            }
        });

        // 3. Tables — headers and rows
        data.tables = [];
        document.querySelectorAll('table, [role="grid"], [class*="table"], [class*="Table"]').forEach(tbl => {
            const headers = [];
            const rows = [];
            // Headers
            tbl.querySelectorAll('th, [role="columnheader"]').forEach(th => {
                const t = (th.textContent || '').trim();
                if (t) headers.push(t.substring(0, 80));
            });
            // Rows
            tbl.querySelectorAll('tr, [role="row"]').forEach(tr => {
                const cells = [];
                tr.querySelectorAll('td, th, [role="cell"], [role="gridcell"], [role="columnheader"]').forEach(td => {
                    const t = (td.textContent || '').trim();
                    if (t) cells.push(t.substring(0, 80));
                });
                if (cells.length > 0) rows.push(cells);
            });
            if (headers.length > 0 || rows.length > 0) {
                data.tables.push({ headers, rows });
            }
        });

        // 4. Buttons and actions
        data.buttons = [];
        document.querySelectorAll('button, [role="button"], a[class*="btn"], a[class*="Button"]').forEach(el => {
            const t = (el.textContent || '').trim();
            if (t && t.length < 80) {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    data.buttons.push(t.substring(0, 60));
                }
            }
        });

        // 5. Form fields
        data.form_fields = [];
        document.querySelectorAll('input, select, textarea, [role="combobox"], [role="textbox"]').forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                const label = el.getAttribute('placeholder') || el.getAttribute('name') || el.getAttribute('aria-label') || '';
                data.form_fields.push({
                    type: el.type || el.getAttribute('role') || el.tagName,
                    name: el.name || '',
                    placeholder: (el.getAttribute('placeholder') || '').substring(0, 60),
                    label: label.substring(0, 60),
                    required: el.required || false
                });
            }
        });

        // 6. All visible paragraph/span text (for body content)
        data.text_sections = [];
        document.querySelectorAll('p, li, [class*="text"], [class*="description"], [class*="content"]').forEach(el => {
            const t = (el.textContent || '').trim();
            if (t && t.length > 5 && t.length < 500) {
                data.text_sections.push(t.substring(0, 300));
            }
        });

        // 7. Empty states
        data.empty_states = [];
        document.querySelectorAll('[class*="empty"], [class*="Empty"], [class*="no-data"], [class*="placeholder"]').forEach(el => {
            const t = (el.textContent || '').trim();
            if (t) data.empty_states.push(t.substring(0, 200));
        });

        // 8. Dropdown/select options
        data.select_options = [];
        document.querySelectorAll('select option, [role="option"], li[role]').forEach(el => {
            const t = (el.textContent || '').trim();
            if (t && t.length < 100) data.select_options.push(t.substring(0, 60));
        });

        return data;
    }
    """)

    page_data.update(extracted)
    return page_data


def capture_module(page, primary_label, sub_items, screenshot_dir):
    """
    Capture all pages under a primary module.
    Returns list of capture results.
    """
    results = []
    homepage = "https://app-qa.zotok.ai/admin/home"

    # First, click the primary item to show secondary panel
    try:
        primary_el = page.locator(f'.primary-item-wrapper[aria-label="{primary_label}"]').first
        primary_el.wait_for(state="visible", timeout=5000)
        primary_el.click()
        page.wait_for_timeout(3000)
    except Exception as e:
        print(f"  Cannot click primary '{primary_label}': {e}")
        return results

    # Click each secondary sub-item
    for sub in sub_items:
        sub_name = sub["text"]
        safe_name = sub_name.lower().replace(" ", "_").replace("/", "_")
        print(f"\n  📄 Capturing: {primary_label} → {sub_name}")

        # Try clicking the sub-item
        try:
            # First try exact text match in the secondary panel
            sub_el = page.get_by_text(sub_name, exact=True).first
            if sub_el.count() == 0:
                sub_el = page.get_by_text(sub_name).first
            sub_el.wait_for(state="visible", timeout=5000)
            sub_el.click()
            page.wait_for_timeout(5000)
        except Exception as e:
            print(f"    Click sub-item failed: {e}")
            continue

        # Capture the page
        data = capture_page_data(page, primary_label, sub_name)
        results.append(data)

        # Screenshot
        ss_path = screenshot_dir / f"{SafeDirName(primary_label)}_{safe_name}.png"
        page.screenshot(path=str(ss_path), full_page=True)
        data["screenshot"] = str(ss_path.relative_to(CAPTURE_DIR.parent))

        print(f"    URL: {data['url']}")
        print(f"    Headings: {len(data.get('headings', []))}")
        print(f"    KPIs: {len(data.get('kpis', []))}")
        print(f"    Tables: {len(data.get('tables', []))}")
        print(f"    Buttons: {len(data.get('buttons', []))}")
        print(f"    Form fields: {len(data.get('form_fields', []))}")

        # Save individual capture JSON
        mod_dir = CAPTURE_DIR / SafeDirName(primary_label)
        os.makedirs(mod_dir, exist_ok=True)
        with open(mod_dir / f"{safe_name}.json", "w") as f:
            json.dump(data, f, indent=2)

    return results


def SafeDirName(name):
    """Convert arbitrary string to safe directory name."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower())


def capture_dashboard(page, screenshot_dir):
    """Capture the home/dashboard page with its switch tabs."""
    print("\n--- Capturing: Home / Dashboard ---")
    results = []

    # Ensure we're on the home page
    page.goto("https://app-qa.zotok.ai/admin/home", wait_until="load", timeout=15000)
    page.wait_for_timeout(5000)
    dismiss_overlays(page)

    # Capture current dashboard view
    data = capture_page_data(page, "Dashboard", "Overview")
    ss_path = screenshot_dir / "dashboard_overview.png"
    page.screenshot(path=str(ss_path), full_page=True)
    data["screenshot"] = str(ss_path.relative_to(CAPTURE_DIR.parent))
    results.append(data)

    # Save
    mod_dir = CAPTURE_DIR / "dashboard"
    os.makedirs(mod_dir, exist_ok=True)
    with open(mod_dir / "overview.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"  Dashboard Overview: {data['url']}")
    print(f"    Headings: {len(data.get('headings', []))}")

    # Now try clicking the switch-tab buttons to capture different views
    switch_tabs = page.locator('.swicth-tab-button')
    tab_count = switch_tabs.count()
    print(f"  Found {tab_count} switch tabs")

    for i in range(tab_count):
        try:
            tab_text = switch_tabs.nth(i).text_content(timeout=2000)
            tab_text = tab_text.strip()[:30] if tab_text else f"tab_{i}"
        except:
            tab_text = f"tab_{i}"

        # Skip if it's the currently active tab
        try:
            cls = switch_tabs.nth(i).get_attribute("class")
            if cls and "active" in cls:
                print(f"  Skipping active tab: {tab_text}")
                continue
        except:
            pass

        print(f"\n  Swicthing to tab: {tab_text}")
        try:
            switch_tabs.nth(i).click()
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"    Click failed: {e}")
            continue

        safe_tab = tab_text.lower().replace(" ", "_")
        data = capture_page_data(page, "Dashboard", tab_text)
        ss_path = screenshot_dir / f"dashboard_{safe_tab}.png"
        page.screenshot(path=str(ss_path), full_page=True)
        data["screenshot"] = str(ss_path.relative_to(CAPTURE_DIR.parent))
        results.append(data)

        with open(mod_dir / f"{safe_tab}.json", "w") as f:
            json.dump(data, f, indent=2)

        print(f"    URL: {data['url']}")
        print(f"    Headings: {len(data.get('headings', []))}")
        print(f"    Tables: {len(data.get('tables', []))}")

    return results


def capture_threads(page, screenshot_dir):
    """Capture Threads module."""
    print("\n--- Capturing: Threads ---")
    results = []

    homepage = "https://app-qa.zotok.ai/admin/home"
    page.goto(homepage, wait_until="load", timeout=15000)
    page.wait_for_timeout(3000)

    # Click Threads primary
    try:
        page.locator('.primary-item-wrapper[aria-label="Threads"]').first.click()
        page.wait_for_timeout(3000)
    except:
        print("  Could not click Threads")
        return results

    # Click "Threads" sub-item
    try:
        sub = page.get_by_text("Threads", exact=True).first
        if sub.count() == 0:
            sub = page.get_by_text("Threads").first
        sub.wait_for(state="visible", timeout=5000)
        sub.click()
        page.wait_for_timeout(5000)
    except Exception as e:
        print(f"  Click Threads sub-item failed: {e}")
        return results

    data = capture_page_data(page, "Threads", "Threads")
    ss_path = screenshot_dir / "threads_main.png"
    page.screenshot(path=str(ss_path), full_page=True)
    data["screenshot"] = str(ss_path.relative_to(CAPTURE_DIR.parent))
    results.append(data)

    mod_dir = CAPTURE_DIR / "threads"
    os.makedirs(mod_dir, exist_ok=True)
    with open(mod_dir / "overview.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"  Threads: {data['url']}")
    print(f"    Headings: {len(data.get('headings', []))}")
    print(f"    Tables: {len(data.get('tables', []))}")

    return results


def main():
    nav_tree = load_nav_tree()
    sidebar = nav_tree.get("sidebar", {})

    print("=" * 60)
    print("PHASE 2: PER-MODULE DEEP CAPTURE")
    print("=" * 60)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        page = context.new_page()

        # Login
        print("\n--- LOGIN ---")
        if not login(page):
            print("Login failed.")
            browser.close()
            return
        dismiss_overlays(page)

        all_captures = {}

        # 1. Dashboard + switch tabs
        dash_data = capture_dashboard(page, SCREENSHOT_DIR)
        all_captures["dashboard"] = dash_data

        # 2. Threads
        threads_data = capture_threads(page, SCREENSHOT_DIR)
        all_captures["threads"] = threads_data

        # 3. Sales modules (Grow, Campaign, AI Agent, Customers, Products, etc.)
        if "Sales" in sidebar:
            print("\n--- Capturing: Sales modules ---")
            all_captures["sales"] = capture_module(
                page, "Sales", 
                [s for s in sidebar["Sales"]["secondary_items"] if s["text"] != "Grow" or True],
                SCREENSHOT_DIR
            )

        # 4. Reports modules
        if "Reports" in sidebar:
            print("\n--- Capturing: Reports modules ---")
            all_captures["reports"] = capture_module(
                page, "Reports",
                sidebar["Reports"]["secondary_items"],
                SCREENSHOT_DIR
            )

        # 5. Settings modules
        if "Settings" in sidebar:
            print("\n--- Capturing: Settings modules ---")
            all_captures["settings"] = capture_module(
                page, "Settings",
                sidebar["Settings"]["secondary_items"],
                SCREENSHOT_DIR
            )

        # Save master capture index
        index_path = CAPTURE_DIR / "capture_index.json"
        summary = {}
        for area, captures in all_captures.items():
            summary[area] = len(captures)
        with open(index_path, "w") as f:
            json.dump({"captures": summary, "timestamp": datetime.now().isoformat()}, f, indent=2)

        print(f"\n{'='*60}")
        print("CAPTURE COMPLETE")
        print(f"{'='*60}")
        total = sum(len(v) for v in all_captures.values())
        print(f"Total pages captured: {total}")
        for area, captures in all_captures.items():
            print(f"  {area}: {len(captures)} pages")
        print(f"\nScreenshots: {SCREENSHOT_DIR}")
        print(f"Capture data: {CAPTURE_DIR}")

        browser.close()


if __name__ == "__main__":
    main()
