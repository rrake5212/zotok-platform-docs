# ZoTok Platform Documentation

A Docusaurus 3.10 documentation site for the ZoTok field operations and distributor management platform, with an integrated video-to-manual pipeline.

**Live site:** https://rrake5212.github.io/zotok-platform-docs/  
**Repository:** https://github.com/rrake5212/zotok-platform-docs

## Repository Structure

```
platform-docs/
├── docs/                        # Markdown documentation (68 pages across 30+ topics)
├── src/                         # Docusaurus React source
├── static/screenshots/          # Screenshots organized by module (25+ module folders)
│   ├── dashboard/               #   Video pipeline frames + Playwright captures
│   ├── threads/                 #   Video pipeline frames
│   ├── settings/                #   Video pipeline frames
│   ├── campaigns/               #   13 screenshots from GROW & CAMPAIGN video
│   ├── customers/               #   Playwright live capture screenshots
│   ├── orders/                  #   Playwright live capture screenshots
│   └── ... (25+ module folders)
├── pipeline/                    # Extraction scripts (video + Playwright)
│   ├── generate_docx.py         #   DOCX generator (603 lines, python-docx)
│   ├── ocr_frames.py            #   RapidOCR extractor
│   ├── discover_app.py          #   Phase 1: Playwright navigation crawler
│   ├── capture_module.py        #   Phase 2: Playwright per-module deep capture
│   ├── restructure.py           #   Phase 3: Capture data → Docusaurus pages
│   ├── fix_screenshots.py       #   Screenshot organizer
│   ├── discovery/               #   Navigation tree and cookie data
│   ├── capture/                 #   Raw capture JSON per module (gitignored: /screenshots/)
│   └── README.md                #   Pipeline workflow documentation
├── output/                      # Generated DOCX artifacts
│   ├── ZoTok_User_Manual_Home_and_Threads.docx  # (703 KB, complete manual)
│   └── README.md                #   Artifact manifest
├── videos/                      # Source MP4 walkthroughs (gitignored, ~400 MB)
│   ├── Home and Threads.mp4
│   └── GROW AND CAMPAIGN.mp4
├── .github/workflows/deploy.yml # GitHub Actions → GitHub Pages CI/CD
├── docusaurus.config.ts         # Site config (GH Pages target)
├── sidebars.ts                  # 11 module categories, 68 pages
└── package.json                 # Docusaurus 3.10 + React 19
```

## Content Coverage

| Module | Pages | Screenshots | Source |
|--------|-------|-------------|--------|
| Intro | 1 | — | Manual |
| Getting Started | 1 | — | Manual |
| Dashboard | 6 | 10 | Video pipeline + Playwright |
| Sales (Grow, Campaigns, AI Agent) | 3 | 3 | Playwright |
| Customers | 1 | 1 | Playwright |
| Products | 1 | 1 | Playwright |
| Orders | 1 | 1 | Playwright |
| Invoices | 1 | 1 | Playwright |
| Payments | 1 | 1 | Playwright |
| Ledger | 1 | 1 | Playwright |
| Field Ops | 1 | 1 | Playwright |
| Schemes | 1 | 1 | Playwright |
| Price List | 1 | 1 | Playwright |
| Forms | 1 | 1 | Playwright |
| Threads | 2 | 7 | Video pipeline + Playwright |
| Queries Management | 1 | — | Manual |
| Campaigns (Grow) | 4 | 14 | Video pipeline + Playwright |
| Reports (13 modules) | 13 | 13 | Playwright |
| Settings & Account (6 modules) | 6 | 6 | Playwright |
| WhatsApp & Communication | 2 | 2 | Playwright |
| Integrations & Data | 5 | 5 | Playwright |
| Configuration | 3 | 3 | Playwright |
| **Total** | **68** | **75+** | |

## Local Development

```bash
npm install
npm start          # Dev server at localhost:3000 (hot reload)
npm run build      # Static build to /build/
npm run serve      # Serve built site locally
npx tsc --noEmit   # TypeScript typecheck
```

## Pipeline Usage

Two pipelines are available in `pipeline/`:

### Video-to-Manual (Original)
Extract user manuals from screen-recorded MP4 walkthroughs via OpenCV frame extraction, scene change detection, OCR, and DOCX generation.
See `pipeline/README.md` for the full workflow.

### Playwright Live Capture (New)
Extract documentation directly from the live platform at `https://app-qa.zotok.ai` using Playwright browser automation. This pipeline captures live UI data — KPIs, tables, forms, buttons, and screenshots — without requiring video recordings.

**Pipeline steps:**
1. `discover_app.py` — Login + crawl sidebar → build navigation tree
2. `capture_module.py` — Per-module deep capture (screenshots + DOM extraction)
3. `restructure.py` — Convert capture data to Docusaurus markdown pages
4. `fix_screenshots.py` — Copy screenshots to `static/screenshots/<module>/`

## How the Site Was Built

This site started as two separate folders:
- **`zotok user manual/`** — raw video extraction artifacts (scripts, frames, MP4s, DOCX)
- **`platform-docs/`** — Docusaurus documentation site

**July 10, 2026 — Consolidation:**
- Pipeline scripts moved to `pipeline/`
- DOCX deliverables moved to `output/`
- Source videos consolidated in `videos/` (gitignored)
- Screenshots from the video pipeline distributed into `static/screenshots/<module>/`
- Old `zotok user manual/` folder left as backup

**July 10, 2026 — Playwright Expansion:**
- A Playwright browser automation pipeline was built to capture live UI data from `https://app-qa.zotok.ai`
- 44 pages across Sales, Reports, and Settings modules were captured and converted to Docusaurus markdown
- Documentation expanded from 29 pages to 68 pages
- All Playwright scripts live in `pipeline/` (discover_app.py, capture_module.py, restructure.py, fix_screenshots.py)
- Live screenshots replaced placeholder content in previously thin modules (Customers, Orders, Invoices, etc.)

## Deployment

Automatically deployed to GitHub Pages via `.github/workflows/deploy.yml` on every push to `main`.

```bash
# Trigger manually from GitHub Actions:
#   https://github.com/rrake5212/zotok-platform-docs/actions
```

## Tech Stack

- **Docusaurus 3.10** (TypeScript, React 19, MDX)
- **GitHub Pages** with Actions CI/CD
- **OpenCV + RapidOCR + python-docx** (video pipeline, in `pipeline/`)
- **Playwright** (live capture pipeline, in `pipeline/`)
