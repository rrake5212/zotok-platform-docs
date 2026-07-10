# ZoTok Documentation Pipelines

Two pipelines for generating documentation from the ZoTok platform:

## 1. Video-to-Manual (Legacy)

Extracts structured user manuals from software walkthrough videos (MP4 screen recordings with UI clicks). Automates frame extraction, scene change detection, OCR text extraction, click-flow reconstruction, and DOCX document generation.

Originally developed from two ZoTok product walkthroughs:
- **Home and Threads.mp4** → `ZoTok_User_Manual_Home_and_Threads.docx`
- **GROW AND CAMPAIGN.mp4** → 4 campaign documentation pages in `docs/campaigns/`

### Scripts

| File | Purpose |
|--------|---------|
| `generate_docx.py` (603 lines) | Full DOCX builder — reads enhanced frames + navigation asset, writes structured manual with cover, TOC, chapters, tables, and embedded screenshots via python-docx |
| `ocr_frames.py` (28 lines) | Runs RapidOCR on extracted key frames, prints all visible text per frame |

### Workflow

1. **Analyze video** — Check codec, FPS, resolution, duration (OpenCV)
2. **Extract frames** — Sample every 5th frame from source MP4 (in `/videos/`)
3. **Detect scene transitions** — Histogram differencing (CHISQR, threshold ~8.0)
4. **Deduplicate** — Structural similarity at 160×90 (mean diff threshold 30) to get ~13 key frames
5. **OCR** — RapidOCR on each deduped frame to extract UI text
6. **Map click flow** — Compare consecutive frames to identify click regions and state changes
7. **Generate DOCX** — python-docx builds structured document with cover, TOC, chapters, tables, images

### Dependencies

```bash
python3 -m venv /tmp/video-env
source /tmp/video-env/bin/activate
pip install opencv-python-headless Pillow rapidocr-onnxruntime python-docx
```

### Output

- Generated DOCX files go to `../output/`
- Screenshots for the docs site go to `../static/screenshots/<module>/`

### Pitfalls

- **PEP 668** — Always use a venv (`python3 -m venv /tmp/xxx`)
- **No sudo** — No system packages; use Python-only solutions
- **Large videos** — 4 min @ 30fps = 7200 frames. Extract at 1-2 fps, full res only at transitions
- **No audio** — OCR is the only text source for silent recordings. Use STT if audio exists
- **No cursor** — Click detection relies on frame differences only
- **OCR quality** — Use CLAHE preprocessing (`cv2.createCLAHE`) before OCR
- **OCR timeout** — 56+ histogram frames cause RapidOCR timeout. Always deduplicate to ~13 before OCR
- **Output folder** — Use a dedicated subdirectory per video to avoid mixing frames

---

## 2. Playwright Live Capture (New)

Extract documentation directly from the live ZoTok platform at `https://app-qa.zotok.ai` using Playwright browser automation. Captures live UI data — KPIs, tables, forms, buttons, and screenshots — without requiring video recordings.

**Phone login with auto-OTP is supported.**

### Pipeline Scripts

| Script | Phase | Purpose |
|--------|-------|---------|
| `discover_app.py` | 1 — Discovery | Login + crawl sidebar → build navigation tree of all modules |
| `capture_module.py` | 2 — Deep Capture | Visit each module, extract KPIs, tables, forms, buttons, screenshots |
| `restructure.py` | 3 — Generation | Convert raw capture JSON → Docusaurus markdown pages |
| `fix_screenshots.py` | Post-process | Copy screenshots to `static/screenshots/<module>/` |

### Supporting Files

| Path | Purpose |
|------|---------|
| `discovery/navigation_tree.json` | Navigation map output from Phase 1 |
| `discovery/cookies.json` | Saved session cookies (reused between phases) |
| `capture/` | Raw capture data (44 JSON files as of Jul 2026) |
| `capture/screenshots/` | Raw screenshots (gitignored; copies go to `static/screenshots/`) |

### Full Run (all phases)

```bash
# Setup
python3 -m venv /tmp/manual-env
source /tmp/manual-env/bin/activate
pip install playwright Pillow
python3 -m playwright install chromium

# Phase 1: Discover navigation tree
python3 discover_app.py

# Phase 2: Capture all modules (add phone number in script)
python3 capture_module.py

# Phase 3: Generate Docusaurus pages
python3 restructure.py
python3 fix_screenshots.py
```

### Architecture Notes

- **Auth flow:** Phone input → Continue → auto-OTP fills → Verify OTP → SPA routes to `/admin/home`
- **Sidebar structure:** Two-level navigation — primary icons (Home, Threads, Sales, Reports, Settings) expand to show secondary items
- **Switch tabs:** Dashboard has content-area tabs (Sales, Payments, Item, Day Book) that change the `?tab=` parameter
- **SPA handling:** Uses `wait_until="load"` (not `networkidle` which times out on SPAs) + generous hydration waits
- **Session reuse:** Cookies saved to `discovery/cookies.json` after first login; reused on subsequent runs

### Adding More Modules

1. Update `capture_module.py` to visit additional pages
2. Run all phases again
3. Or manually capture individual pages using the same pattern

---

## See Also

The `zotok-video-manual-pipeline` skill has detailed step-by-step instructions for the video pipeline.
