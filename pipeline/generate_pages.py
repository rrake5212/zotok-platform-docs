#!/usr/bin/env python3
"""
Phase 3: Generate Docusaurus Documentation Pages
=================================================
Convert raw capture data (JSON + screenshots) into production-grade
Docusaurus markdown pages with proper frontmatter, tables, KPIs,
screenshots, and action documentation.
"""

import json
import os
import re
import shutil
from pathlib import Path

# Paths
CAPTURE_DIR = Path(__file__).parent / "capture"
SCREENSHOT_SRC = CAPTURE_DIR / "screenshots"
DOCS_DIR = Path(__file__).parent.parent / "docs"
STATIC_DIR = Path(__file__).parent.parent / "static"
SIDEBARS_FILE = Path(__file__).parent.parent / "sidebars.ts"
CAPTURE_INDEX = CAPTURE_DIR / "capture_index.json"


# ── Module metadata ──────────────────────────────────────────────

MODULE_META = {
    "dashboard": {
        "label": "Dashboard",
        "icon": "🏠",
        "sidebar_position": 2,
        "description": "Central dashboard with KPI overview, customer data, product performance, and district-wise sales breakdown.",
    },
    "threads": {
        "label": "Threads",
        "icon": "🧵",
        "sidebar_position": 3,
        "description": "AI-powered query interface for natural language data analysis, report generation, and business insights.",
    },
    "grow": {
        "label": "Grow (Sales)",
        "icon": "📈",
        "sidebar_position": 4,
        "description": "Sales growth dashboard showing KPIs, charts, and performance metrics for the Sales module.",
    },
    "campaign": {
        "label": "Campaigns",
        "icon": "📣",
        "sidebar_position": 5,
        "description": "Plan, create, and manage marketing campaigns with customer lifecycle automation and template-based messaging.",
    },
    "ai agent": {
        "label": "AI Agent",
        "icon": "🤖",
        "sidebar_position": 6,
        "description": "Automate workflows with AI-powered agents for lead follow-ups, order confirmations, and customer engagement.",
    },
    "customers": {
        "label": "Customers",
        "icon": "👥",
        "sidebar_position": 7,
        "description": "Centralized customer directory with search, filters, profiling, and transaction history.",
    },
    "products": {
        "label": "Products (Item)",
        "icon": "📦",
        "sidebar_position": 8,
        "description": "Manage product catalog, track inventory, revenue, stock levels, and sales performance.",
    },
    "orders": {
        "label": "Orders",
        "icon": "📋",
        "sidebar_position": 9,
        "description": "Track and manage sales orders with status tracking, filters, and order processing workflows.",
    },
    "invoices": {
        "label": "Invoices",
        "icon": "🧾",
        "sidebar_position": 10,
        "description": "Create, view, and manage invoices with payment tracking and ageing analysis.",
    },
    "payments": {
        "label": "Payments",
        "icon": "💳",
        "sidebar_position": 11,
        "description": "Track incoming payments, manage receivable ageing, and configure ageing buckets.",
    },
    "ledger": {
        "label": "Ledger",
        "icon": "📒",
        "sidebar_position": 12,
        "description": "Customer-wise ledger with balance tracking, transaction history, and reconciliation.",
    },
    "field ops": {
        "label": "Field Ops",
        "icon": "📍",
        "sidebar_position": 13,
        "description": "Manage field sales operations — tour programs, beat planning, attendance tracking, and daily reporting.",
    },
    "schemes": {
        "label": "Schemes",
        "icon": "🏷️",
        "sidebar_position": 14,
        "description": "Create and manage promotional schemes, discounts, and special offers for customers.",
    },
    "price list": {
        "label": "Price List",
        "icon": "💰",
        "sidebar_position": 15,
        "description": "Configure product pricing, price tiers, and customer-specific price lists.",
    },
    "forms": {
        "label": "Forms",
        "icon": "📝",
        "sidebar_position": 16,
        "description": "Build and manage custom forms for data collection, surveys, and field reports.",
    },
    "customer analysis": {
        "label": "Customer Analysis",
        "icon": "📊",
        "sidebar_position": 17,
        "description": "Analyze customer performance with KPIs, comparison charts, and segmentation.",
    },
    "product analysis": {
        "label": "Product Analysis",
        "icon": "📉",
        "sidebar_position": 18,
        "description": "Product-wise performance analysis with sales metrics, trends, and profitability insights.",
    },
    "sales team activity": {
        "label": "Sales Team Activity",
        "icon": "👥",
        "sidebar_position": 19,
        "description": "Leaderboard and performance tracking for sales team members.",
    },
    "sales team clockin report": {
        "label": "Sales Team Clock-In Report",
        "icon": "⏰",
        "sidebar_position": 20,
        "description": "Track sales team attendance, clock-in/out times, and daily activity logs.",
    },
    "checkins": {
        "label": "Checkins",
        "icon": "📍",
        "sidebar_position": 21,
        "description": "View and analyze sales team check-in locations, routes, and field visit history.",
    },
    "order report": {
        "label": "Order Report",
        "icon": "📊",
        "sidebar_position": 22,
        "description": "Order-related analytics with KPIs, trends, and detailed breakdowns.",
    },
    "order items report": {
        "label": "Order Items Report",
        "icon": "📋",
        "sidebar_position": 23,
        "description": "Line-item level order analysis showing product-wise order quantities and values.",
    },
    "invoice report": {
        "label": "Invoice Report",
        "icon": "🧾",
        "sidebar_position": 24,
        "description": "Invoice analytics with KPIs, ageing analysis, and payment status tracking.",
    },
    "payment report": {
        "label": "Payment Report",
        "icon": "💳",
        "sidebar_position": 25,
        "description": "Payment collection analysis with trends, ageing buckets, and reconciliation reports.",
    },
    "supply tracker": {
        "label": "Supply Tracker",
        "icon": "🚚",
        "sidebar_position": 26,
        "description": "CFA/supply chain tracking with inventory levels, dispatch status, and delivery monitoring.",
    },
    "dynamic segments": {
        "label": "Dynamic Segments",
        "icon": "🔀",
        "sidebar_position": 27,
        "description": "Create and manage dynamic customer segments based on rules and conditions.",
    },
    "scheme report": {
        "label": "Scheme Report",
        "icon": "🏷️",
        "sidebar_position": 28,
        "description": "Analyze scheme performance, redemption rates, and turnover impact.",
    },
    "trial balance": {
        "label": "Trial Balance",
        "icon": "⚖️",
        "sidebar_position": 29,
        "description": "Customer-wise closing balance report with ledger reconciliation.",
    },
    "account": {
        "label": "Account Settings",
        "icon": "⚙️",
        "sidebar_position": 30,
        "description": "Manage firm account details, business information, and profile settings.",
    },
    "my team": {
        "label": "My Team",
        "icon": "👥",
        "sidebar_position": 31,
        "description": "Manage team members, roles, permissions, and user access control.",
    },
    "department": {
        "label": "Departments",
        "icon": "🏢",
        "sidebar_position": 32,
        "description": "Organize teams into departments with role-based access and hierarchy management.",
    },
    "whatsapp": {
        "label": "WhatsApp",
        "icon": "💬",
        "sidebar_position": 33,
        "description": "Configure WhatsApp Business API integration, templates, and messaging settings.",
    },
    "chat widget": {
        "label": "Chat Widget",
        "icon": "💭",
        "sidebar_position": 34,
        "description": "Customize the chat widget appearance, auto-reply rules, and bot behavior.",
    },
    "apps": {
        "label": "Apps & Integrations",
        "icon": "🔌",
        "sidebar_position": 35,
        "description": "Import/export data integrations with third-party apps and bulk data operations.",
    },
    "cfa": {
        "label": "CFA (Supply Chain)",
        "icon": "🏭",
        "sidebar_position": 36,
        "description": "Manage Clearing & Forwarding Agents for supply chain and distribution management.",
    },
    "divisions": {
        "label": "Divisions",
        "icon": "🏗️",
        "sidebar_position": 37,
        "description": "Create and manage business divisions for multi-brand or multi-vertical operations.",
    },
    "notification": {
        "label": "Notifications",
        "icon": "🔔",
        "sidebar_position": 38,
        "description": "Configure in-app and push notification preferences, alerts, and communication settings.",
    },
    "bank details": {
        "label": "Bank Details",
        "icon": "🏦",
        "sidebar_position": 39,
        "description": "Manage business bank accounts for payment collections and reconciliations.",
    },
    "file manager": {
        "label": "File Manager",
        "icon": "📁",
        "sidebar_position": 40,
        "description": "Upload, organize, and manage documents, images, and files within the platform.",
    },
    "config settings": {
        "label": "Config Settings",
        "icon": "🔧",
        "sidebar_position": 41,
        "description": "Advanced workspace configuration and system settings.",
    },
    "jobs": {
        "label": "Jobs",
        "icon": "🔄",
        "sidebar_position": 42,
        "description": "View and manage background jobs, import/export task status, and processing history.",
    },
}

# Pages that existed before this run (keep their content)
EXISTING_PAGES = {
    "dashboard/overview",
    "dashboard/kpi-cards",
    "dashboard/customer-table",
    "campaigns/overview",
    "campaigns/customer-lifecycle",
    "campaigns/creating-campaign",
    "campaigns/templates",
    "threads/overview",
    "threads/query-types",
    "settings/sales-view-settings",
    "settings/payment-view-settings",
    "getting-started/login",
    "intro",
}


# ── Helper functions ─────────────────────────────────────────────

def slugify(name):
    """Convert module name to URL-safe slug."""
    s = name.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

def safe_dir(name):
    """Convert to safe directory name."""
    return slugify(name)


def format_kpis_table(kpis):
    """Convert KPI list to markdown table."""
    if not kpis:
        return ""
    # Deduplicate and clean
    seen = set()
    unique = []
    for k in kpis[:20]:
        k_clean = k.strip()
        if k_clean and k_clean not in seen and len(k_clean) > 3:
            seen.add(k_clean)
            unique.append(k_clean)
    if not unique:
        return ""

    lines = ["| KPI | Value |", "|-----|-------|"]
    for k in unique[:15]:
        lines.append(f"| {k} | |")
    return "\n".join(lines)


def format_tables(tables):
    """Convert captured tables to markdown."""
    if not tables:
        return ""
    parts = []
    for i, tbl in enumerate(tables):
        headers = tbl.get("headers", [])
        rows = tbl.get("rows", [])
        if not headers and not rows:
            continue

        lines = []
        if headers:
            lines.append("| " + " | ".join(h for h in headers[:8]) + " |")
            lines.append("| " + " | ".join("---" for _ in headers[:8]) + " |")
        for row in rows[:15]:
            cells = row[:8] if headers else row[:5]
            lines.append("| " + " | ".join(c[:40] for c in cells) + " |")
        if len(rows) > 15:
            lines.append(f"| *{len(rows) - 15} more rows* |")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def format_buttons(buttons):
    """Convert buttons list to documentation."""
    if not buttons:
        return ""
    seen = set()
    unique = []
    for b in buttons:
        b = b.strip()
        if b and b not in seen and len(b) > 1 and len(b) < 60:
            seen.add(b)
            unique.append(b)
    if not unique:
        return ""
    lines = ["| Action | Description |", "|--------|-------------|"]
    for b in unique[:20]:
        lines.append(f"| **{b}** | |")
    return "\n".join(lines)


def format_text_sections(texts):
    """Extract meaningful text content."""
    if not texts:
        return ""
    seen = set()
    unique = []
    for t in texts:
        t = t.strip()
        if t and t not in seen and len(t) > 10:
            seen.add(t)
            unique.append(t)
    return "\n\n".join(unique[:10])


def format_empty_states(empty_states):
    """Format empty states."""
    if not empty_states:
        return ""
    return "\n".join(f"> {e}" for e in empty_states[:5])


def generate_page(data, module_slug):
    """
    Generate a complete Docusaurus markdown page from capture data.
    """
    sub_name = data.get("sub_module", "")
    module_key = module_slug
    if sub_name:
        module_key = sub_name.lower()

    meta = MODULE_META.get(module_key, {})
    label = meta.get("label", sub_name or module_slug.title().replace("-", " "))
    icon = meta.get("icon", "")
    desc = meta.get("description", "")
    pos = meta.get("sidebar_position", 50)

    # Determine screenshot path
    screenshot = data.get("screenshot", "")
    if screenshot:
        # Convert relative path to URL path
        screenshot_rel = screenshot.replace("\\", "/")
        # Extract just the filename + relative path to static
        ss_path = f"/screenshots/{module_slug}/{Path(screenshot_rel).name}"
    else:
        ss_path = None

    url = data.get("url", "")
    url_display = url.replace("https://app-qa.zotok.ai", "")

    # Headings
    headings = data.get("headings", [])
    heading_text = [h["text"] for h in headings if h.get("text")]

    # Build page
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

    # Access info
    lines.append("## Accessing This Page")
    lines.append("")
    lines.append(f"Navigate to `{url_display}` in the ZöTok platform.")
    lines.append("")

    if ss_path:
        lines.append(f"![{label} Screenshot]({ss_path})")
        lines.append("")

    # Overview from headings
    if heading_text:
        lines.append("## Page Overview")
        lines.append("")
        for h in heading_text[:5]:
            lines.append(f"- **{h}**")
        lines.append("")

    # KPIs
    kpis = data.get("kpis", [])
    if kpis:
        lines.append("## Key Metrics")
        lines.append("")
        kpi_table = format_kpis_table(kpis)
        if kpi_table:
            lines.append(kpi_table)
            lines.append("")

    # Tables
    tables = data.get("tables", [])
    if tables:
        lines.append("## Data Tables")
        lines.append("")
        tbl_text = format_tables(tables)
        if tbl_text:
            lines.append(tbl_text)
            lines.append("")

    # Buttons / Actions
    buttons = data.get("buttons", [])
    if buttons:
        lines.append("## Available Actions")
        lines.append("")
        btn_text = format_buttons(buttons)
        if btn_text:
            lines.append(btn_text)
            lines.append("")

    # Form fields
    fields = data.get("form_fields", [])
    if fields:
        lines.append("## Form Fields")
        lines.append("")
        seen_fields = set()
        lines.append("| Field | Type | Required |")
        lines.append("|-------|------|----------|")
        for f in fields:
            key = f"{f.get('placeholder','')}_{f.get('name','')}"
            if key not in seen_fields and (f.get('placeholder') or f.get('name')):
                seen_fields.add(key)
                ftype = f.get('type', 'text')
                req = "Yes" if f.get('required') else "No"
                fname = f.get('placeholder') or f.get('name') or f.get('label') or ''
                lines.append(f"| {fname[:40]} | {ftype[:20]} | {req} |")
        lines.append("")

    # Empty states
    empty_states = data.get("empty_states", [])
    if empty_states:
        lines.append("## Empty State")
        lines.append("")
        es_text = format_empty_states(empty_states)
        if es_text:
            lines.append(es_text)
            lines.append("")
            lines.append("This is shown when no data is available for this section.")
            lines.append("")

    # Text sections for body content
    text_sections = data.get("text_sections", [])
    if text_sections:
        content = format_text_sections(text_sections)
        if content:
            lines.append(content)
            lines.append("")

    # Route info
    lines.append("---")
    lines.append("")
    lines.append(f"*Page route: `{url_display}`*")
    lines.append("")

    return "\n".join(lines)


def copy_screenshots(module_slug, data):
    """Copy screenshot to static/screenshots/<module>/."""
    screenshot = data.get("screenshot", "")
    if not screenshot:
        return None

    src = CAPTURE_DIR / screenshot
    if not src.exists():
        return None

    dest_dir = STATIC_DIR / "screenshots" / module_slug
    os.makedirs(dest_dir, exist_ok=True)
    dest = dest_dir / src.name
    shutil.copy2(src, dest)
    return f"/screenshots/{module_slug}/{src.name}"


def update_sidebars(new_pages):
    """Add new module pages to sidebars.ts."""
    with open(SIDEBARS_FILE) as f:
        content = f.read()

    # Build the new category entries for pages not already in sidebars
    # Group by parent module
    module_groups = {}
    for page_path in new_pages:
        parts = page_path.split("/")
        if len(parts) >= 2:
            module = parts[0]
            page_name = parts[1]
            if module not in module_groups:
                module_groups[module] = []
            module_groups[module].append(page_path)

    # Sidebar categories we need to add
    # Find existing sidebar items
    existing_categories = set()
    for m in re.finditer(r"label:\s*'([^']+)'", content):
        existing_categories.add(m.group(1).lower())

    # Only add pages for modules not already in the sidebar
    pages_to_add = []
    for module, page_list in module_groups.items():
        module_label = module.replace("-", " ").title()
        if module_label.lower() in existing_categories:
            # Module exists — check if individual pages need adding
            for pp in page_list:
                page_id = pp.replace("/", "/")
                if page_id not in content:
                    pages_to_add.append(pp)
        else:
            # New module — add all its pages
            pages_to_add.extend(page_list)

    if not pages_to_add:
        print("  No new sidebar entries needed.")
        return

    # Add new pages to the Additional Modules category or create new ones
    # For simplicity, append new categories before the closing bracket
    print(f"  Would add {len(pages_to_add)} pages to sidebar (auto-generation pending manual review)")


def main():
    print("=" * 60)
    print("PHASE 3: GENERATE DOCUSAURUS PAGES")
    print("=" * 60)

    # Scan capture data directory for JSON files
    all_capture_files = []
    for root, dirs, files in os.walk(CAPTURE_DIR):
        for f in files:
            if f.endswith(".json") and f != "capture_index.json":
                all_capture_files.append(Path(root) / f)

    print(f"Found {len(all_capture_files)} capture JSON files")

    generated_pages = []
    skipped_existing = 0

    for cap_file in all_capture_files:
        with open(cap_file) as f:
            data = json.load(f)

        module_name = data.get("module", "").lower()
        sub_name = data.get("sub_module", "").lower()

        # Determine module slug and output path
        if module_name == "dashboard":
            module_slug = "dashboard"
            page_slug = slugify(sub_name) if sub_name else "overview"
        elif module_name == "threads":
            module_slug = "threads"
            page_slug = "overview"
        elif module_name == "sales":
            module_slug = safe_dir(sub_name) if sub_name else "sales"
            # Some modules go to specific directories
            page_slug = "overview"
        elif module_name == "reports":
            module_slug = safe_dir(sub_name) if sub_name else "reports"
            page_slug = "overview"
        elif module_name == "settings":
            module_slug = safe_dir(sub_name) if sub_name else "settings"
            page_slug = "overview"
        else:
            module_slug = safe_dir(sub_name) if sub_name else safe_dir(module_name)
            page_slug = "overview"

        # Skip existing pages that were already well-documented
        page_id = f"{module_slug}/{page_slug}"
        if page_id in EXISTING_PAGES:
            skipped_existing += 1
            continue

        # Generate markdown
        markdown = generate_page(data, module_slug)

        # Write to docs directory
        page_dir = DOCS_DIR / module_slug
        os.makedirs(page_dir, exist_ok=True)
        page_path = page_dir / f"{page_slug}.md"
        with open(page_path, "w") as f:
            f.write(markdown)
        generated_pages.append(page_id)
        print(f"  ✅ {page_path.relative_to(DOCS_DIR.parent)}")

        # Copy screenshot
        copy_screenshots(module_slug, data)

    print(f"\n{'='*60}")
    print(f"Generated: {len(generated_pages)} pages")
    print(f"Skipped (existing): {skipped_existing}")
    print(f"{'='*60}")
    print("\nPages generated:")
    for p in sorted(generated_pages):
        print(f"  docs/{p}.md")

    # Update sidebars
    print("\n--- Updating sidebar ---")
    update_sidebars(generated_pages)

    print("\nDone. Run `npm run build` to verify.")


if __name__ == "__main__":
    main()
