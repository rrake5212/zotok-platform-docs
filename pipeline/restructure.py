#!/usr/bin/env python3
"""Restructure capture data and regenerate all pages."""
import json, os, re, shutil
from pathlib import Path

CAPTURE_DIR = Path(__file__).parent / "capture"
DOCS_DIR = Path(__file__).parent.parent / "docs"
STATIC_DIR = Path(__file__).parent.parent / "static"
SIDEBARS_FILE = Path(__file__).parent.parent / "sidebars.ts"

# Mapping: (source_dir, source_file) -> (target_slug, page_slug, label)
FILE_MAP = [
    # Sales modules
    ("sales", "grow", "grow", "overview", "Grow Dashboard"),
    ("sales", "campaign", "campaigns", "overview", "Campaigns"),
    ("sales", "customers", "customers", "overview", "Customers"),
    ("sales", "products", "products", "overview", "Products"),
    ("sales", "orders", "orders", "overview", "Orders"),
    ("sales", "invoices", "invoices", "overview", "Invoices"),
    ("sales", "payments", "payments", "overview", "Payments"),
    ("sales", "ledger", "ledger", "overview", "Ledger"),
    ("sales", "field_ops", "field-ops", "overview", "Field Ops"),
    ("sales", "schemes", "schemes", "overview", "Schemes"),
    ("sales", "price_list", "price-list", "overview", "Price List"),
    ("sales", "forms", "forms", "overview", "Forms"),
    ("sales", "ai_agent", "ai-agent", "overview", "AI Agent"),
    # Reports modules
    ("reports", "customer_analysis", "customer-analysis", "overview", "Customer Analysis"),
    ("reports", "product_analysis", "product-analysis", "overview", "Product Analysis"),
    ("reports", "sales_team_activity", "sales-team-activity", "overview", "Sales Team Activity"),
    ("reports", "sales_team_clockin_report", "sales-team-clockin-report", "overview", "Sales Team Clock-In Report"),
    ("reports", "checkins", "checkins", "overview", "Checkins"),
    ("reports", "order_report", "order-report", "overview", "Order Report"),
    ("reports", "order_items_report", "order-items-report", "overview", "Order Items Report"),
    ("reports", "invoice_report", "invoice-report", "overview", "Invoice Report"),
    ("reports", "payment_report", "payment-report", "overview", "Payment Report"),
    ("reports", "supply_tracker", "supply-tracker", "overview", "Supply Tracker"),
    ("reports", "dynamic_segments", "dynamic-segments", "overview", "Dynamic Segments"),
    ("reports", "scheme_report", "scheme-report", "overview", "Scheme Report"),
    ("reports", "trial_balance", "trial-balance", "overview", "Trial Balance"),
    # Settings modules
    ("settings", "account", "account", "overview", "Account Settings"),
    ("settings", "my_team", "my-team", "overview", "My Team"),
    ("settings", "department", "department", "overview", "Departments"),
    ("settings", "whatsapp", "whatsapp", "overview", "WhatsApp"),
    ("settings", "chat_widget", "chat-widget", "overview", "Chat Widget"),
    ("settings", "apps", "apps", "overview", "Apps & Integrations"),
    ("settings", "cfa", "cfa", "overview", "CFA"),
    ("settings", "divisions", "divisions", "overview", "Divisions"),
    ("settings", "notification", "notification", "overview", "Notifications"),
    ("settings", "bank_details", "bank-details", "overview", "Bank Details"),
    ("settings", "file_manager", "file-manager", "overview", "File Manager"),
    ("settings", "config_settings", "config-settings", "overview", "Config Settings"),
    ("settings", "jobs", "jobs", "overview", "Jobs"),
]

SIDEBAR_STRUCTURE = [
    ("Sales", [
        ("grow", "Grow Dashboard"),
        ("campaigns", "Campaigns"),
        ("ai-agent", "AI Agent"),
        ("customers", "Customers"),
        ("products", "Products"),
        ("orders", "Orders"),
        ("invoices", "Invoices"),
        ("payments", "Payments"),
        ("ledger", "Ledger"),
        ("field-ops", "Field Ops"),
        ("schemes", "Schemes"),
        ("price-list", "Price List"),
        ("forms", "Forms"),
    ]),
    ("Reports", [
        ("customer-analysis", "Customer Analysis"),
        ("product-analysis", "Product Analysis"),
        ("sales-team-activity", "Sales Team Activity"),
        ("sales-team-clockin-report", "Sales Team Clock-In Report"),
        ("checkins", "Checkins"),
        ("order-report", "Order Report"),
        ("order-items-report", "Order Items Report"),
        ("invoice-report", "Invoice Report"),
        ("payment-report", "Payment Report"),
        ("supply-tracker", "Supply Tracker"),
        ("dynamic-segments", "Dynamic Segments"),
        ("scheme-report", "Scheme Report"),
        ("trial-balance", "Trial Balance"),
    ]),
    ("Account Settings", [
        ("account", "Account"),
        ("my-team", "My Team"),
        ("department", "Departments"),
        ("notification", "Notifications"),
        ("bank-details", "Bank Details"),
    ]),
    ("WhatsApp & Communication", [
        ("whatsapp", "WhatsApp"),
        ("chat-widget", "Chat Widget"),
    ]),
    ("Integrations & Data", [
        ("apps", "Apps & Integrations"),
        ("cfa", "CFA"),
        ("divisions", "Divisions"),
        ("file-manager", "File Manager"),
        ("jobs", "Jobs"),
    ]),
    ("Configuration", [
        ("config-settings", "Config Settings"),
    ]),
]


def clean_cell(text):
    t = text.strip()
    if len(t) > 4:
        for pct in [0.5, 0.55, 0.6, 0.45]:
            split = int(len(t) * pct)
            if t[:split] == t[split:]:
                return t[:split].strip()
    return t


def generate_markdown(data, slug, label, position):
    """Generate clean markdown from capture data."""
    url = data.get("url", "")
    url_display = url.replace("https://app-qa.zotok.ai", "")
    screenshot = data.get("screenshot", "")
    ss_path = f"/screenshots/{slug}/{Path(screenshot).name}" if screenshot else None

    lines = [
        "---",
        f"sidebar_position: {position}",
        f"title: \"{label}\"",
        "---",
        "",
        f"# {label}",
        "",
        f"## Overview",
        "",
        f"This page provides access to {label.lower()} functionality within the ZöTok platform.",
        "",
    ]

    if ss_path and (STATIC_DIR / "screenshots" / slug / Path(screenshot).name).exists():
        lines.append(f"![{label}]({ss_path})")
        lines.append("")

    # KPIs
    kpis = data.get("kpis", [])
    seen = set()
    unique_kpis = []
    for k in kpis:
        k = k.strip()
        if k and k not in seen and len(k) > 3:
            seen.add(k)
            unique_kpis.append(k)

    if unique_kpis:
        lines.append("### Key Metrics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        for k in unique_kpis[:12]:
            m = re.match(r'([₹0-9,.KkLl%+-]+)\s*(.*)', k)
            if m:
                val, lbl = m.group(1), m.group(2).strip()
                lines.append(f"| {lbl} | {val} |")
            else:
                lines.append(f"| {k} | |")
        lines.append("")

    # Tables
    tables = data.get("tables", [])
    if tables:
        lines.append("### Data Table")
        lines.append("")
        for tbl in tables:
            headers = [clean_cell(h) for h in tbl.get("headers", [])]
            rows = tbl.get("rows", [])
            clean_rows = []
            for row in rows:
                clean = [clean_cell(c) for c in row]
                if clean == headers:
                    continue
                # Skip empty rows
                if all(c == "" for c in clean):
                    continue
                clean_rows.append(clean)

            if not clean_rows:
                continue

            cols = headers if headers else [f"Col {j+1}" for j in range(len(clean_rows[0]))]
            cols = cols[:8]
            lines.append("| " + " | ".join(c[:30] for c in cols) + " |")
            lines.append("| " + " | ".join("---" for _ in cols) + " |")
            for row in clean_rows[:15]:
                cells = row[:len(cols)]
                while len(cells) < len(cols):
                    cells.append("")
                lines.append("| " + " | ".join(c[:40] for c in cells) + " |")
            if len(clean_rows) > 15:
                lines.append(f"| *{len(clean_rows) - 15} more rows* |")
            lines.append("")

    # Buttons
    buttons = data.get("buttons", [])
    seen_btn = set()
    unique_btns = []
    for b in buttons:
        b = b.strip()
        if b and b not in seen_btn and len(b) > 1 and len(b) < 50:
            seen_btn.add(b)
            unique_btns.append(b)
    if unique_btns:
        lines.append("### Available Actions")
        lines.append("")
        lines.append("| Action | Description |")
        lines.append("|--------|-------------|")
        for b in unique_btns[:15]:
            lines.append(f"| **{b}** | |")
        lines.append("")

    # Form fields
    fields = data.get("form_fields", [])
    if fields:
        seen_f = set()
        uf = []
        for f in fields:
            key = f"{f.get('placeholder','')}_{f.get('name','')}"
            if key not in seen_f and (f.get('placeholder') or f.get('name')):
                seen_f.add(key)
                uf.append(f)
        if uf:
            lines.append("### Form Fields")
            lines.append("")
            lines.append("| Field | Type | Required |")
            lines.append("|-------|------|----------|")
            for f in uf[:8]:
                fname = f.get('placeholder') or f.get('name') or f.get('label') or ''
                lines.append(f"| {fname[:40]} | {f.get('type','text')[:20]} | {'Yes' if f.get('required') else 'No'} |")
            lines.append("")

    # Empty states
    es = data.get("empty_states", [])
    if es:
        lines.append("### Empty State")
        lines.append("")
        for e in es[:3]:
            lines.append(f"> {e}")
        lines.append("")

    lines.append("---")
    lines.append(f"*Route: `{url_display}`*")
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("RESTRUCTURING CAPTURE DATA & GENERATING PAGES")
    print("=" * 60)

    for src_dir, src_file, tgt_slug, page_slug, label in FILE_MAP:
        src_path = CAPTURE_DIR / src_dir / f"{src_file}.json"
        if not src_path.exists():
            print(f"  ⚠️ Missing: {src_path}")
            continue

        with open(src_path) as f:
            data = json.load(f)

        # Determine position
        position = FILE_MAP.index((src_dir, src_file, tgt_slug, page_slug, label)) + 5

        # Generate markdown
        markdown = generate_markdown(data, tgt_slug, label, position)

        # Write page
        page_dir = DOCS_DIR / tgt_slug
        os.makedirs(page_dir, exist_ok=True)
        page_path = page_dir / f"{page_slug}.md"
        with open(page_path, "w") as f:
            f.write(markdown)
        print(f"  ✅ {tgt_slug}/{page_slug}.md")

        # Copy screenshot
        screenshot = data.get("screenshot", "")
        if screenshot:
            src_ss = CAPTURE_DIR / screenshot
            if src_ss.exists():
                dest_dir = STATIC_DIR / "screenshots" / tgt_slug
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(src_ss, dest_dir / src_ss.name)

    # Update sidebars.ts
    print("\n--- Updating sidebar ---")
    with open(SIDEBARS_FILE) as f:
        content = f.read()

    # Build new sidebar entries
    new_entries = []
    for cat_label, items in SIDEBAR_STRUCTURE:
        entry = f"""    {{
      type: 'category',
      label: '{cat_label}',
      items: ["""
        for slug, _ in items:
            if (DOCS_DIR / slug / "overview.md").exists():
                entry += f"\n        '{slug}/overview',"
        entry += "\n      ],\n    },"
        new_entries.append(entry)

    # Remove old Additional Modules category if exists
    content = re.sub(
        r"    \{\s*\n\s*type: 'category',\s*\n\s*label: 'Additional Modules'.*?\n    \},",
        "",
        content,
        flags=re.DOTALL
    )

    # Insert before the closing of docsSidebar
    insert_marker = "  ],\n};"
    new_section = "\n" + "\n".join(new_entries)
    if insert_marker in content:
        # Find the last closing bracket before the marker
        # Insert new entries before that marker
        content = content.replace(insert_marker, new_section + "\n" + insert_marker)
        with open(SIDEBARS_FILE, "w") as f:
            f.write(content)
        print("  ✅ sidebars.ts updated with new categories")

    print(f"\n{'='*60}")
    print(f"Total pages generated: {len(FILE_MAP)}")
    print("Run `npm run build` to verify.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
