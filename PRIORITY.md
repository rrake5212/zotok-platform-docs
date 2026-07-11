# ZoTok Platform Docs — Priority Roadmap

**Last updated:** July 11, 2026  
**Site:** Docusaurus 3.10 (reverted from v2 Markdoc migration — too complex)  
**Live:** https://rrake5212.github.io/zotok-platform-docs/  

---

## Background

The v2 migration to Vite + Markdoc + React + Tailwind was abandoned on July 11, 2026.
Reason: unnecessary complexity for a documentation site that Docusaurus already handles well.
All v2 artifacts (platform-docs-v2/, migration_inventory.md, playwright_validation_plan.md,
visual-tests/) have been deleted. Deploy workflow reverted to build from root (Docusaurus).

The Docusaurus site is the single source of truth. 57 markdown pages, 83 screenshots,
8 sidebar categories, GitHub Pages CI/CD on push to main.

---

## Known Issues in Current Content

**Duplicated table blocks** — 27 of 57 pages have the main data table duplicated
back-to-back (a Playwright capture bug where textContent concatenated nested elements
and the restructure script emitted the table twice). Affected modules:
ai-agent, bank-details, cfa, checkins, customer-analysis, customers, department,
divisions, forms, invoice-report, invoices, jobs, ledger, my-team, order-items-report,
order-report, orders, payment-report, payments, price-list, product-analysis, products,
sales-team-activity, schemes, supply-tracker, trial-balance, whatsapp.

**5 orphan pages** missing from sidebar (content exists but not navigable):
day-book/overview, queries/overview, sales/overview,
settings/sales-view-settings, settings/payment-view-settings.

**3 dead relative links** using `../path.md` syntax:
- dashboard/customer-table.md → ../settings/sales-view-settings.md
- day-book/overview.md → ../ledger/overview.md
- day-book/overview.md → ../payments/overview.md

---

## PRIORITY 1 — Content Re-Capture with Improved DOM Extraction

**Goal:** Re-run the Playwright live capture pipeline with smarter DOM extraction to
produce clean, non-duplicated, richer documentation content. Then regenerate the
Docusaurus markdown pages from the clean data.

### Step 1: Improve capture_module.py table extraction

**Problem:** `page.evaluate()` using `textContent` concatenates nested React elements,
producing "NPNitin PadmawarNitin Padmawar" and duplicating table rows.

**Fix:** Replace `textContent` with a child-node walker that only extracts direct
text nodes (nodeType 3):

```python
table_data = page.evaluate("""
() => {
    return Array.from(document.querySelectorAll('table')).map(table => ({
        headers: Array.from(table.querySelectorAll('th')).map(th => {
            const texts = [];
            th.childNodes.forEach(n => {
                if (n.nodeType === 3) texts.push(n.nodeValue.trim());
            });
            return texts.join(' ') || th.textContent.trim().substring(0, 30);
        }),
        rows: Array.from(table.querySelectorAll('tr')).map(tr =>
            Array.from(tr.querySelectorAll('td')).map(td => {
                const texts = [];
                td.childNodes.forEach(n => {
                    if (n.nodeType === 3) texts.push(n.nodeValue.trim());
                });
                return texts.join(' ') || td.textContent.trim().substring(0, 40);
            })
        )
    }));
}
""")
```

### Step 2: Add KPI card extraction

Find by CSS selector pattern `[class*="kpi"]`, then extract label/value from child
spans separately. Avoid concatenation.

### Step 3: Add form field label extraction

Walk up DOM from each `<input>` to find associated `<label>` element. Use
`aria-label` as fallback when `textContent` is empty.

### Step 4: Add interaction deep-dive

For each module page, don't just capture initial state:
1. Click each button → capture resulting state/modal
2. Open each dropdown → capture options
3. Type in each input → capture placeholder hints
4. Toggle switches/checkboxes → capture label text
5. Paginate tables → capture page 2 data
6. Capture empty-state messages ("no data" experience)
7. Capture breadcrumb structure

### Step 5: Intercept XHR responses

Add `page.route()` or `page.on('response')` to intercept XHR/fetch calls and capture
clean JSON API responses. This gives structured data without DOM parsing bugs.

### Step 6: Regenerate markdown

Update `restructure.py` to consume the improved capture JSON and emit clean
Docusaurus markdown. The output must:
- Emit each table exactly once (dedup guard)
- Format KPIs as labeled key-value pairs
- Include form field tables with proper labels
- Add interaction flow sections (button → result)
- Fix all relative links to Docusaurus-compatible format

### Step 7: Fix orphans and dead links

- Add 5 orphan pages to sidebars.ts in correct categories
- Fix 3 relative links to use Docusaurus path format (not ../x/y.md)

### Affected files

- pipeline/capture_module.py (core extraction rewrite)
- pipeline/restructure.py (regeneration logic)
- pipeline/discover_app.py (if new modules added)
- docs/*.md (all 57 pages regenerated)
- sidebars.ts (add 5 orphans)

---

## PRIORITY 2 — Playwright Validation Suite for the Docusaurus Site

**Goal:** Build and run a comprehensive Playwright test suite that validates every
aspect of the live Docusaurus documentation site — links, components, responsive
layout, search, accessibility, and performance.

### Step 1: Setup

```bash
python3 -m venv /tmp/validation-env
source /tmp/validation-env/bin/activate
pip install playwright @axe-core/playwright lighthouse
python3 -m playwright install chromium
mkdir -p visual-tests/{screenshots,reports,video}
```

### Step 2: Link integrity (verify-links.js)

For all 57 doc pages:
- Assert every `<a>` href resolves (200, not 404)
- Assert internal doc links navigate to correct page
- Assert sidebar links navigate correctly
- Assert prev/next navigation links work
- Assert navbar/footer links work

### Step 3: Component presence (verify-components.js)

Per page, check:
- Navbar visible with logo + search + GitHub link
- Sidebar visible at desktop, correct section active
- TOC/pricing present (Docusaurus built-in)
- Prev/Next nav links present and correct
- Images load (200 status, alt text present)
- Tables render with Docusaurus table styles
- Code blocks render with Prism syntax highlighting
- Callouts/admonitions render correctly

### Step 4: Responsive screenshots (screenshot-pages.js)

Screenshot 10 representative pages at 3 widths:
- 1440px (desktop — full sidebar)
- 768px (tablet — collapsed sidebar)
- 375px (mobile — hamburger menu)

Representative pages:
1. /docs/intro — Home
2. /docs/dashboard/overview — Page with tables
3. /docs/campaigns/creating-campaign — Steps/instructions
4. /docs/orders/overview — Data tables
5. /docs/ai-agent/overview — Short page
6. /docs/settings/sales-view-settings — Settings
7. /docs/threads/overview — Conversation module
8. /docs/customers/overview — Customer module
9. /docs/getting-started/login — Getting started
10. /docs/field-ops/overview — Field ops

30 screenshots total → visual-tests/screenshots/

### Step 5: Search functionality (verify-search.js)

- Type query in search bar
- Assert results appear (DocusaurusAlgolia or local search)
- Assert first result is relevant
- Press Enter → navigates to correct page
- Assert empty state for no-match query

### Step 6: Accessibility audit (verify-a11y.js)

- Run @axe-core/playwright against 5 representative pages
- Assert 0 critical/serious violations
- Assert correct heading hierarchy (no skipped levels)
- Assert focus rings visible on keyboard navigation
- Assert all images have alt text

### Step 7: Performance (verify-performance.js)

- Lighthouse CI on home page + one table-heavy page
- Target: Performance >= 85, Accessibility >= 95

### Step 8: Deliverables

| Artifact | Path |
|----------|------|
| Validation report | visual-tests/reports/validation-report.md |
| Accessibility report | visual-tests/reports/a11y-report.json |
| Performance report | visual-tests/reports/perf-report.json |
| Screenshots | visual-tests/screenshots/ (30 images) |

---

## Execution Order

1. **P1 Steps 1-6** — Re-capture and regenerate content (~45 min)
2. **P1 Step 7** — Fix orphans + dead links in sidebars.ts (~5 min)
3. **Commit + push** — Triggers Docusaurus deploy to GH Pages
4. **P2 Steps 1-8** — Run full validation suite against live site (~60 min)
5. **Commit reports** — Save validation outputs to visual-tests/reports/

Total estimated time: ~110 min