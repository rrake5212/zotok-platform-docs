#!/usr/bin/env python3
"""Deep probe: dump sidebar HTML + try expanding every clickable element."""
import json, os
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
        if filled >= 4: break
        p.wait_for_timeout(1000)
    p.locator('button:has-text("Verify OTP")').first.click()
    p.wait_for_timeout(10000)

    print(f"URL: {p.url}")

    # Dismiss any overlay/notification
    p.keyboard.press("Escape")
    p.wait_for_timeout(2000)
    for btn_text in ["Ok, Got it", "Close", "Dismiss", "Got it"]:
        try:
            btn = p.locator(f'button:has-text("{btn_text}")')
            if btn.count() > 0:
                btn.click()
                p.wait_for_timeout(1000)
        except:
            pass

    # ---- DUMP SIDEBAR HTML ----
    sidebar_html = p.evaluate("""
    () => {
        const sb = document.querySelector('[class*="sidebar"]');
        if (!sb) return 'NO SIDEBAR FOUND';
        return sb.outerHTML;
    }
    """)
    print(f"\n=== SIDEBAR HTML ({len(sidebar_html)} chars) ===\n")
    print(sidebar_html[:5000])

    # ---- FIND ALL PRIMARY ITEMS AND SUB-ITEMS ----
    print("\n=== SIDEBAR STRUCTURE ===")
    structure = p.evaluate("""
    () => {
        const sb = document.querySelector('[class*="sidebar"]');
        if (!sb) return [];
        
        const items = [];
        // Find all primary wrappers
        const wrappers = sb.querySelectorAll('.primary-item-wrapper');
        wrappers.forEach((w, idx) => {
            const textEl = w.querySelector('a, button, span, [class*="text"], [class*="label"]');
            const text = textEl ? textEl.textContent.trim() : w.textContent.trim();
            
            // Check for sub-items
            const subItems = [];
            const subs = w.querySelectorAll('[class*="secondary"], [class*="sub"], [class*="child"], ul a, ul li, [class*="MuiListItem"]');
            subs.forEach(s => {
                const t = (s.textContent || '').trim();
                if (t) subItems.push(t.substring(0, 60));
            });
            
            items.push({
                index: idx,
                text: text.substring(0, 80),
                class: (w.className || '').substring(0, 80),
                has_arrow: w.innerHTML.includes('arrow') || w.innerHTML.includes('chevron') || w.innerHTML.includes('expand'),
                sub_items: subItems,
                html: w.innerHTML.substring(0, 1000)
            });
        });
        return items;
    }
    """)
    
    for item in structure:
        print(f"\n  [{item['index']}] {item['text']}")
        print(f"      class: {item['class']}")
        print(f"      has_arrow: {item['has_arrow']}")
        if item['sub_items']:
            print(f"      sub_items: {item['sub_items']}")
        print(f"      html snippet: {item['html'][:300]}")

    # ---- CLICK EACH TAB TO SEE WHAT OPENS ----
    print("\n=== EXPLORING EACH TAB ===")
    tabs = p.locator('.swicth-tab-button, .primary-item-wrapper')
    tab_count = tabs.count()
    print(f"Found {tab_count} clickable tab elements")

    for i in range(tab_count):
        try:
            text = tabs.nth(i).text_content(timeout=2000)
            text = text.strip()[:40] if text else f"tab_{i}"
        except:
            text = f"tab_{i}"
        
        print(f"\n  ➡ [{i}] {text}")
        before_url = p.url
        
        try:
            tabs.nth(i).click()
            p.wait_for_timeout(3000)
        except Exception as e:
            print(f"     Click failed: {e}")
            continue
        
        after_url = p.url
        print(f"     URL: {before_url} → {after_url}")
        print(f"     Same page: {before_url == after_url}")
        
        # Check if any new sub-items appeared
        new_structure = p.evaluate("""
        () => {
            const sb = document.querySelector('[class*="sidebar"]');
            if (!sb) return [];
            const items = [];
            sb.querySelectorAll('[class*="secondary"], [class*="sub"]').forEach(el => {
                const t = (el.textContent || '').trim();
                if (t) items.push(t.substring(0, 60));
            });
            return items;
        }
        """)
        if new_structure:
            print(f"     Sub-items now visible: {new_structure}")

    ctx.close()
    b.close()
