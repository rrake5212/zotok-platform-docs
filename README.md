# ZoTok Platform Documentation

A Docusaurus 3.10 documentation site for the ZoTok field operations and distributor management platform, with an integrated video-to-manual pipeline.

## Repository Structure

```
platform-docs/
├── docs/                        # Markdown documentation (29 pages across 18 modules)
├── src/                         # Docusaurus React source
├── static/screenshots/          # Screenshots organized by module (12 module folders)
├── pipeline/                    # Video-to-manual extraction scripts (Python)
│   ├── generate_docx.py         #   DOCX generator
│   ├── ocr_frames.py            #   OCR extractor
│   └── README.md
├── output/                      # Generated DOCX artifacts
│   ├── ZoTok_User_Manual_Home_and_Threads.docx
│   └── README.md
├── videos/                      # Source MP4 walkthroughs (gitignored)
├── docusaurus.config.ts
├── sidebars.ts
└── package.json
```

## Local Development

```bash
npm install
npm start          # dev server at localhost:3000
npm run build      # static build to /build/
npm run serve      # serve built site locally
```

## Pipeline Usage

See `pipeline/README.md` for extracting manuals from new walkthrough videos.

## Deployment

Deployed via GitHub Pages — push to `main` triggers auto-build via `.github/workflows/deploy.yml`.

```bash
# Manual deploy:
GIT_USER=<username> npm run deploy
```
