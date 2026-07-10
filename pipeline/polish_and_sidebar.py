#!/usr/bin/env python3
"""
Phase 3b: Polish generated pages, update sidebars, and build.
"""
import json, os, re, shutil
from pathlib import Path

CAPTURE_DIR = Path(__file__).parent / "capture"
DOCS_DIR = Path(__file__).parent.parent / "docs"
STATIC_DIR = Path(__file__).parent.parent / "static"
SIDEBARS_FILE = Path(__file__).parent.parent / "sidebars.ts"

SAFE_MODULES = {
    "account": {"label": "Account Settings", "icon": "⚙️", "desc": "Manage firm account details, business information, and profile settings."},
    "ai-agent": {"label": "AI Agent", "icon": "🤖", "desc": "Automate workflows with AI-powered agents for lead follow-ups, order confirmations, and customer engagement."},
    "apps": {"label": "Apps & Integrations", "icon": "🔌", "desc": "Import/export data integrations with third-party apps and bulk data operations."},
    "bank-details": {"label": "Bank Details", "icon": "🏦", "desc": "Manage business bank accounts for payment collections and reconciliations."},
    "campaign": {"label": "Campaigns", "icon": "📣", "desc": "Plan, create, and manage marketing campaigns with customer lifecycle automation."},
    "cfa": {"label": "CFA (Supply Chain)", "icon": "🏭", "desc": "Manage Clearing & Forwarding Agents for supply chain and distribution."},
    "chat-widget": {"label": "Chat Widget", "icon": "💭", "desc": "Customize chat widget, auto-reply rules, and bot behavior settings."},
    "checkins": {"label": "Checkins", "icon": "📍", "desc": "View sales team check-in locations, routes, and field visit history."},
    "config-settings": {"label": "Config Settings", "icon": "🔧", "desc": "Advanced workspace configuration and system settings."},
    "customer-analysis": {"label": "Customer Analysis", "icon": "📊", "desc": "Analyze customer performance with KPIs, comparison charts, and segmentation."},
    "customers": {"label": "Customers", "icon": "👥", "desc": "Centralized customer directory with search, filters, profiling, and transaction history."},
    "dashboard": {"label": "Dashboard", "icon": "🏠", "desc": "Central dashboard with KPI overview, customer data, and sales breakdown."},
    "department": {"label": "Departments", "icon": "🏢", "desc": "Organize teams into departments with role-based access and hierarchy."},
    "divisions": {"label": "Divisions", "icon": "🏗️", "desc": "Create business divisions for multi-brand or multi-vertical operations."},
    "dynamic-segments": {"label": "Dynamic Segments", "icon": "🔀", "desc": "Create dynamic customer segments based on rules and conditions."},
    "field-ops": {"label": "Field Ops", "icon": "📍", "desc": "Manage field sales operations — tours, beats, attendance, and daily reporting."},
    "file-manager": {"label": "File Manager", "icon": "📁", "desc": "Upload, organize, and manage documents and files."},
    "forms": {"label": "Forms", "icon": "📝", "desc": "Build custom forms for data collection, surveys, and field reports."},
    "grow": {"label": "Grow (Sales)", "icon": "📈", "desc": "Sales growth dashboard with KPIs, charts, and performance metrics."},
    "invoice-report": {"label": "Invoice Report", "icon": "🧾", "desc": "Invoice analytics with KPIs, ageing analysis, and payment status."},
    "invoices": {"label": "Invoices", "icon": "🧾", "desc": "Create, view, and manage invoices with payment tracking."},
    "jobs": {"label": "Jobs", "icon": "🔄", "desc": "View and manage background jobs and import/export task status."},
    "ledger": {"label": "Ledger", "icon": "📒", "desc": "Customer-wise ledger with balance tracking and transaction history."},
    "my-team": {"label": "My Team", "icon": "👥", "desc": "Manage team members, roles, permissions, and access control."},
    "notification": {"label": "Notifications", "icon": "🔔", "desc": "Configure notification preferences and alerts."},
    "order-items-report": {"label": "Order Items Report", "icon": "📋", "desc": "Line-item level order analysis showing product-wise quantities."},
    "order-report": {"label": "Order Report", "icon": "📊", "desc": "Order-related analytics with KPIs, trends, and breakdowns."},
    "orders": {"label": "Orders", "icon": "📋", "desc": "Track and manage sales orders with status and filters."},
    "payment-report": {"label": "Payment Report", "icon": "💳", "desc": "Payment collection analysis with ageing and reconciliation."},
    "payments": {"label": "Payments", "icon": "💳", "desc": "Track payments and manage receivable ageing."},
    "price-list": {"label": "Price List", "icon": "💰", "desc": "Configure product pricing, tiers, and customer-specific lists."},
    "product-analysis": {"label": "Product Analysis", "icon": "📉", "desc": "Product-wise performance analysis with sales metrics."},
    "products": {"label": "Products (Item)", "icon": "📦", "desc": "Manage product catalog, inventory, and sales performance."},
    "sales-team-activity": {"label": "Sales Team Activity", "icon": "👥", "desc": "Leaderboard and performance tracking for sales teams."},
    "sales-team-clockin-report": {"label": "Sales Team Clock-In Report", "icon": "⏰", "desc": "Track sales team attendance and clock-in/out times."},
    "scheme-report": {"label": "Scheme Report", "icon": "🏷️", "desc": "Analyze scheme performance, redemption rates, and impact."},
    "schemes": {"label": "Schemes", "icon": "🏷️", "desc": "Create promotional schemes, discounts, and offers."},
    "supply-tracker": {"label": "Supply Tracker", "icon": "🚚", "desc": "CFA/supply chain tracking with inventory and dispatch monitoring."},
    "trial-balance": {"label": "Trial Balance", "icon": "⚖️", "desc": "Customer-wise closing balance report with reconciliation."},
    "whatsapp": {"label": "WhatsApp", "icon": "💬", "desc": "Configure WhatsApp Business API and messaging settings."},
}


def clean_cell(text):
    """Remove duplicated text in cells (DOM artifact)."""
    # Remove duplicate substrings like "NPNitin PadmawarNitin Padmawar"
    # Simple heuristic: if the first half equals the second half, take half
    t = text.strip()
    if len(t) > 4:
        half = len(t) // 2
        if t[:half] == t[half:]:
            return t[:half].strip()
        # Also check 40/60 split
        for split_pct in [0.5, 0.55, 0.6, 0.45]:
            split = int(len(t) * split_pct)
            if t[:split] == t[split:]:
                return t[:split].strip()
    return t


def regenerate_page(module_slug):
    """Regenerate a page from its capture JSON with cleaned data."""
    json_path = CAPTURE_DIR / module_slug / "overview.json"
    if not json_path.exists():
        return None
    
    with open(json_path) as f:
        data = json.load(f)
    
    meta = SAFE_MODULES.get(module_slug, {})
    label = meta.get("label", module_slug.replace("-", " ").title())
    icon = meta.get("icon", "")
    desc = meta.get("desc", "")
    
    # Determine position
    pos = list(SAFE_MODULES.keys()).index(module_slug) + 5 if module_slug in SAFE_MODULES else 50
    
    url = data.get("url", "")
    url_display = url.replace("https://app-qa.zotok.ai", "")
    
    # Screenshot
    screenshot = data.get("screenshot", "")
    ss_path = f"/screenshots/{module_slug}/{Path(screenshot).name}" if screenshot else None
    
    lines = []
    lines.append("---")
    lines.append(f"sidebar_position: {pos}")
    lines.append(f"title: \"{label}\"")
    lines.append("---")
    lines.append("")
    lines.append(f"# {icon} {label}")
    lines.append("")
    
    if desc:
        lines.append(desc)
        lines.append("")
    
    # Subtabs within the module (if any switch tabs exist)
    lines.append("## Overview")
    lines.append("")
    lines.append(f"This page is accessible from the main navigation sidebar under the **{label}** section.")
    lines.append("")
    
    if ss_path:
        lines.append(f"![{label} Screenshot]({ss_path})")
        lines.append("")
    
    # KPIs
    kpis = data.get("kpis", [])
    unique_kpis = []
    seen_kpi = set()
    for k in kpis:
        k = k.strip()
        if k and k not in seen_kpi and len(k) > 3:
            seen_kpi.add(k)
            # Try to parse value + label
            unique_kpis.append(k)
    
    if unique_kpis:
        lines.append("## Key Metrics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        for k in unique_kpis[:15]:
            # Try to split value from label
            m = re.match(r'([₹0-9,.KkLl]+)(.*)', k)
            if m:
                val, lbl = m.group(1), m.group(2).strip()
                lines.append(f"| {lbl} | {val} |")
            else:
                lines.append(f"| {k} | |")
        lines.append("")
    
    # Tables
    tables = data.get("tables", [])
    if tables:
        lines.append("## Data")
        lines.append("")
        for i, tbl in enumerate(tables):
            headers = [clean_cell(h) for h in tbl.get("headers", [])]
            rows = tbl.get("rows", [])
            
            # Skip header row if it appears as first row (duplication)
            clean_rows = []
            for row in rows:
                clean = [clean_cell(c) for c in row]
                # Skip if this row matches the headers
                if clean == headers:
                    continue
                clean_rows.append(clean)
            
            if not clean_rows:
                continue
            
            cols = headers if headers else [f"Column {j+1}" for j in range(len(clean_rows[0]))]
            lines.append("| " + " | ".join(c[:30] for c in cols) + " |")
            lines.append("| " + " | ".join("---" for _ in cols) + " |")
            for row in clean_rows[:15]:
                cells = row[:len(cols)]
                # Pad if fewer cells than columns
                while len(cells) < len(cols):
                    cells.append("")
                lines.append("| " + " | ".join(c[:40] for c in cells) + " |")
            if len(clean_rows) > 15:
                lines.append(f"| *{len(clean_rows) - 15} more rows* |")
            lines.append("")
    
    # Available Actions
    buttons = data.get("buttons", [])
    seen_btn = set()
    unique_btns = []
    for b in buttons:
        b = b.strip()
        if b and b not in seen_btn and len(b) > 1 and len(b) < 50:
            seen_btn.add(b)
            unique_btns.append(b)
    
    if unique_btns:
        lines.append("## Available Actions")
        lines.append("")
        lines.append("| Action | Purpose |")
        lines.append("|--------|---------|")
        for b in unique_btns[:20]:
            lines.append(f"| **{b}** | |")
        lines.append("")
    
    # Form fields
    fields = data.get("form_fields", [])
    if fields:
        seen_f = set()
        unique_fields = []
        for f in fields:
            key = f"{f.get('placeholder','')}_{f.get('name','')}"
            if key not in seen_f and (f.get('placeholder') or f.get('name')):
                seen_f.add(key)
                unique_fields.append(f)
        if unique_fields:
            lines.append("## Form Fields")
            lines.append("")
            lines.append("| Field | Type | Required |")
            lines.append("|-------|------|----------|")
            for f in unique_fields[:10]:
                ftype = f.get('type', 'text')[:20]
                req = "Yes" if f.get('required') else "No"
                fname = f.get('placeholder') or f.get('name') or f.get('label') or ''
                lines.append(f"| {fname[:40]} | {ftype} | {req} |")
            lines.append("")
    
    # Empty states
    empty_states = data.get("empty_states", [])
    if empty_states:
        lines.append("## Empty State")
        lines.append("")
        for e in empty_states[:3]:
            lines.append(f"> {e}")
        lines.append("")
    
    # Page route
    lines.append("---")
    lines.append("")
    lines.append(f"*Route: `{url_display}`*")
    lines.append("")
    
    return "\n".join(lines)


def update_sidebars():
    """Update sidebars.ts with all new module pages."""
    with open(SIDEBARS_FILE) as f:
        content = f.read()
    
    # Categories to add (group: [slug, label])
    new_categories = [
        # Under Sales module (primary="Sales")
        ("Sales", [
            ("grow", "Grow Dashboard"),
            ("campaign", "Campaigns"),
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
        # Reports category
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
        # Settings categories
        ("Account Settings", [
            ("account", "Account"),
            ("my-team", "My Team"),
            ("department", "Departments"),
        ]),
        ("WhatsApp & Communication", [
            ("whatsapp", "WhatsApp"),
            ("chat-widget", "Chat Widget"),
        ]),
        ("Integrations & Data", [
            ("apps", "Apps"),
            ("cfa", "CFA"),
            ("divisions", "Divisions"),
            ("file-manager", "File Manager"),
            ("jobs", "Jobs"),
        ]),
        ("Configuration", [
            ("notification", "Notifications"),
            ("bank-details", "Bank Details"),
            ("config-settings", "Config Settings"),
        ]),
    ]
    
    # Build sidebar category entries
    new_entries = []
    for cat_label, items in new_categories:
        entry = f"""    {{
      type: 'category',
      label: '{cat_label}',
      items: ["""
        for slug, label in items:
            path = f"{slug}/overview"
            # Check if page file exists
            if (DOCS_DIR / slug / "overview.md").exists():
                entry += f"\n        '{path}',"
        entry += "\n      ],\n    },"
        new_entries.append(entry)
    
    # Find insertion point — before the closing bracket of docsSidebar
    insert_marker = "  ],\n};"
    insertion = "\n" + "\n".join(new_entries) + "\n"
    
    if insert_marker in content:
        # Insert before the closing
        new_content = content.replace(insert_marker, insertion + insert_marker)
        with open(SIDEBARS_FILE, "w") as f:
            f.write(new_content)
        print("  ✅ sidebars.ts updated")
    else:
        print("  ⚠️ Could not find insertion point in sidebars.ts")


def main():
    print("=" * 60)
    print("POLISHING PAGES & UPDATING SIDEBARS")
    print("=" * 60)
    
    # Regenerate pages with cleaner output
    pages_updated = 0
    for slug in SAFE_MODULES:
        if not (DOCS_DIR / slug).exists():
            # Check if it's in capture dir
            json_path = CAPTURE_DIR / slug / "overview.json"
            if json_path.exists():
                markdown = regenerate_page(slug)
                if markdown:
                    page_dir = DOCS_DIR / slug
                    os.makedirs(page_dir, exist_ok=True)
                    with open(page_dir / "overview.md", "w") as f:
                        f.write(markdown)
                    pages_updated += 1
                    print(f"  ✅ {slug}/overview.md")
    
    # Also update dashboard child pages
    dash_pages = {"day-book": "Day Book", "item": "Items", "payments": "Payments View"}
    for slug, label in dash_pages.items():
        json_path = CAPTURE_DIR / "dashboard" / f"{slug}.json"
        if json_path.exists():
            with open(json_path) as f:
                data = json.load(f)
            pos = {"day-book": 3, "item": 2, "payments": 4}.get(slug, 5)
            url_display = data.get("url", "").replace("https://app-qa.zotok.ai", "")
            
            lines = [
                "---",
                f"sidebar_position: {pos}",
                f"title: \"{label}\"",
                "---",
                "",
                f"# {label}",
                "",
                f"Dashboard view for {label.lower()} data.",
                "",
                f"## Overview",
                "",
                f"This tab is accessible from the **Dashboard** page via the switch tabs at the top.",
                "",
                f"## Key Metrics",
                "",
                "This view displays KPIs and data relevant to {0}.".format(label.lower()),
                "",
                f"*Route: `{url_display}`*",
                "",
            ]
            with open(DOCS_DIR / "dashboard" / f"{slug}.md", "w") as f:
                f.write("\n".join(lines))
            print(f"  ✅ dashboard/{slug}.md")
    
    print(f"\nPages updated: {pages_updated + len(dash_pages)}")
    
    # Update sidebar
    print("\n--- Updating sidebar ---")
    update_sidebars()
    
    print("\nDone. Run `npm run build` to verify.")


if __name__ == "__main__":
    main()
