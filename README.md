# ZoTok Platform Documentation

A Docusaurus 3.10 documentation site for the ZoTok field operations and distributor management platform, with an integrated video-to-manual pipeline.

**Live site:** https://rrake5212.github.io/zotok-platform-docs/  
**Repository:** https://github.com/rrake5212/zotok-platform-docs

## Repository Structure

```
platform-docs/
├── docs/                        # Markdown documentation (29 pages across 18 modules)
├── src/                         # Docusaurus React source
├── static/screenshots/          # Screenshots organized by module (12 module folders)
│   ├── dashboard/               #   01, 02, 13 frames from Home & Threads video
│   ├── threads/                 #   03, 04, 05 frames
│   ├── settings/                #   06, 07 frames
│   ├── queries/                 #   08, 09, 12 frames
│   ├── products/                #   10, 11 frames
│   └── campaigns/               #   13 screenshots from GROW & CAMPAIGN video
├── pipeline/                    # Video-to-manual extraction scripts (Python)
│   ├── generate_docx.py         #   DOCX generator (603 lines, python-docx)
│   ├── ocr_frames.py            #   RapidOCR extractor
│   └── README.md                #   Pipeline workflow documentation
├── output/                      # Generated DOCX artifacts
│   ├── ZoTok_User_Manual_Home_and_Threads.docx  # (703 KB, complete manual)
│   └── README.md                #   Artifact manifest
├── videos/                      # Source MP4 walkthroughs (gitignored, ~400 MB)
│   ├── Home and Threads.mp4
│   └── GROW AND CAMPAIGN.mp4
├── .github/workflows/deploy.yml # GitHub Actions → GitHub Pages CI/CD
├── docusaurus.config.ts         # Site config (GH Pages target)
├── sidebars.ts                  # 18 module categories, 29 pages
└── package.json                 # Docusaurus 3.10 + React 19
```

## Content Coverage

| Module | Pages | Screenshots |
|--------|-------|-------------|
| Intro | 1 | — |
| Getting Started | 1 | — |
| Dashboard | 3 | 6 (frames 01, 02, 13) |
| Sales | 1 | — |
| Payments | 1 | — |
| Products | 1 | 4 (frames 10, 11) |
| Threads | 2 | 6 (frames 03, 04, 05) |
| Queries | 1 | 6 (frames 08, 09, 12) |
| Campaigns (Grow) | 4 | 13 |
| Customers | 1 | — |
| Orders | 1 | — |
| Invoices | 1 | — |
| Ledger | 1 | — |
| Schemes | 1 | — |
| Price List | 1 | — |
| Field Ops | 1 | — |
| Forms | 1 | — |
| Day Book | 1 | — |
| Settings | 2 | 4 (frames 06, 07) |
| **Total** | **29** | **33** |

## Local Development

```bash
npm install
npm start          # Dev server at localhost:3000 (hot reload)
npm run build      # Static build to /build/
npm run serve      # Serve built site locally
npx tsc --noEmit   # TypeScript typecheck
```

## Pipeline Usage

The `pipeline/` directory contains Python scripts for extracting structured user manuals from software walkthrough videos. See `pipeline/README.md` for the full workflow.

Typical pipeline:
1. Copy source MP4 to `/mnt/d/AgentWork/zotok user manual/`
2. Extract frames via OpenCV histogram differencing (CHISQR)
3. Deduplicate with structural similarity at 160×90 resolution
4. Run OCR via RapidOCR on deduped frames (~13 per video)
5. Generate DOCX with `generate_docx.py`

## How the Site Was Built

This site started as two separate folders:
- **`zotok user manual/`** — raw video extraction artifacts (scripts, frames, MP4s, DOCX)
- **`platform-docs/`** — Docusaurus documentation site

They were merged into a single project on July 10, 2026:
- Pipeline scripts moved to `pipeline/`
- DOCX deliverables moved to `output/`
- Source videos consolidated in `videos/` (gitignored)
- Screenshots from the video pipeline distributed into `static/screenshots/<module>/`
- Old `zotok user manual/` folder left as backup

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
