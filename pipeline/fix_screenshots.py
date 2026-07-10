#!/usr/bin/env python3
"""Copy screenshots to static/ and fix broken image references."""
import shutil
from pathlib import Path

CAPTURE_SS_DIR = Path(__file__).parent / "capture" / "screenshots"
STATIC_DIR = Path(__file__).parent.parent / "static" / "screenshots"
DOCS_DIR = Path(__file__).parent.parent / "docs"

# Mapping: screenshot filename pattern -> destination folder
# The capture script names screenshots as "{primary}_{sub}.png"
# We need to map them to the right module folder
SCREENSHOT_MAP = {
    # Dashboard
    "dashboard_overview.png": "dashboard",
    "dashboard_payments.png": "dashboard",
    "dashboard_item.png": "dashboard",
    "dashboard_day_book.png": "dashboard",
    # Sales modules
    "sales_grow.png": "grow",
    "sales_campaign.png": "campaigns",   # → campaigns, not campaign
    "sales_ai_agent.png": "ai-agent",
    "sales_customers.png": "customers",
    "sales_products.png": "products",
    "sales_orders.png": "orders",
    "sales_invoices.png": "invoices",
    "sales_payments.png": "payments",
    "sales_ledger.png": "ledger",
    "sales_field_ops.png": "field-ops",
    "sales_schemes.png": "schemes",
    "sales_price_list.png": "price-list",
    "sales_forms.png": "forms",
    # Reports modules
    "reports_customer_analysis.png": "customer-analysis",
    "reports_product_analysis.png": "product-analysis",
    "reports_sales_team_activity.png": "sales-team-activity",
    "reports_sales_team_clockin_report.png": "sales-team-clockin-report",
    "reports_checkins.png": "checkins",
    "reports_order_report.png": "order-report",
    "reports_order_items_report.png": "order-items-report",
    "reports_invoice_report.png": "invoice-report",
    "reports_payment_report.png": "payment-report",
    "reports_supply_tracker.png": "supply-tracker",
    "reports_dynamic_segments.png": "dynamic-segments",
    "reports_scheme_report.png": "scheme-report",
    "reports_trial_balance.png": "trial-balance",
    # Settings (screenshots still in capture dir with sales_ prefix)
}

def main():
    print("=== Copying screenshots to static/ ===")
    
    copied = 0
    for ss_file in CAPTURE_SS_DIR.glob("*.png"):
        fname = ss_file.name
        
        # Determine destination folder
        dest_folder = None
        for pattern, folder in SCREENSHOT_MAP.items():
            if fname == pattern or fname.startswith(pattern.rstrip("*")):
                dest_folder = folder
                break
        
        # Fallback: extract module from filename
        if not dest_folder:
            if fname.startswith("sales_"):
                sub = fname.replace("sales_", "").replace(".png", "")
                # Map snake_case to kebab-case
                sub = sub.replace("_", "-")
                dest_folder = sub
            elif fname.startswith("reports_"):
                sub = fname.replace("reports_", "").replace(".png", "")
                sub = sub.replace("_", "-")
                dest_folder = sub
            elif fname.startswith("settings_"):
                sub = fname.replace("settings_", "").replace(".png", "")
                dest_folder = sub
            elif fname.startswith("dashboard_"):
                dest_folder = "dashboard"
            elif fname.startswith("threads_"):
                dest_folder = "threads"
        
        if dest_folder:
            dest_dir = STATIC_DIR / dest_folder
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ss_file, dest_dir / fname)
            copied += 1
            print(f"  ✅ {fname} → {dest_folder}/")
        else:
            print(f"  ⚠️  No mapping for: {fname}")
    
    # Also copy existing old screenshots from platform-docs/static/screenshots/ 
    # — they should stay as they are, they came from the video pipeline
    
    # Fix broken image references in markdown files
    print(f"\n=== Fixing broken image references ===")
    fixed = 0
    for md_file in DOCS_DIR.rglob("*.md"):
        content = md_file.read_text()
        original = content
        
        # Fix campaign → campaigns (the markdown references /screenshots/campaign/ but we put them in /screenshots/campaigns/)
        content = content.replace("/screenshots/campaign/", "/screenshots/campaigns/")
        
        if content != original:
            md_file.write_text(content)
            fixed += 1
            print(f"  ✅ Fixed: {md_file.relative_to(DOCS_DIR.parent)}")
    
    print(f"\nCopied {copied} screenshots, fixed {fixed} markdown files")
    print("Done. Run `npm run build` to verify.")

if __name__ == "__main__":
    main()
