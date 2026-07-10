# ZoTok Video-to-Manual Pipeline

Scripts for extracting structured user manuals from software walkthrough videos (MP4 screen recordings with UI clicks). Automates frame extraction, scene change detection, OCR text extraction, click-flow reconstruction, and DOCX document generation.

Originally developed from two ZoTok product walkthroughs:
- **Home and Threads.mp4** → `ZoTok_User_Manual_Home_and_Threads.docx`
- **GROW AND CAMPAIGN.mp4** → 4 campaign documentation pages in `docs/campaigns/`

## Scripts

| File | Purpose |
|--------|---------|
| `generate_docx.py` (603 lines) | Full DOCX builder — reads enhanced frames + navigation asset, writes structured manual with cover, TOC, chapters, tables, and embedded screenshots via python-docx |
| `ocr_frames.py` (28 lines) | Runs RapidOCR on extracted key frames, prints all visible text per frame |

## Workflow

1. **Analyze video** — Check codec, FPS, resolution, duration (OpenCV)
2. **Extract frames** — Sample every 5th frame from source MP4 (in `/videos/`)
3. **Detect scene transitions** — Histogram differencing (CHISQR, threshold ~8.0)
4. **Deduplicate** — Structural similarity at 160×90 (mean diff threshold 30) to get ~13 key frames
5. **OCR** — RapidOCR on each deduped frame to extract UI text
6. **Map click flow** — Compare consecutive frames to identify click regions and state changes
7. **Generate DOCX** — python-docx builds structured document with cover, TOC, chapters, tables, images

## Dependencies

```bash
python3 -m venv /tmp/video-env
source /tmp/video-env/bin/activate
pip install opencv-python-headless Pillow rapidocr-onnxruntime python-docx
```

## Output

- Generated DOCX files go to `../output/`
- Screenshots for the docs site go to `../static/screenshots/<module>/`

## Pitfalls

- **PEP 668** — Always use a venv (`python3 -m venv /tmp/xxx`)
- **No sudo** — No system packages; use Python-only solutions
- **Large videos** — 4 min @ 30fps = 7200 frames. Extract at 1-2 fps, full res only at transitions
- **No audio** — OCR is the only text source for silent recordings. Use STT if audio exists
- **No cursor** — Click detection relies on frame differences only
- **OCR quality** — Use CLAHE preprocessing (`cv2.createCLAHE`) before OCR
- **OCR timeout** — 56+ histogram frames cause RapidOCR timeout. Always deduplicate to ~13 before OCR
- **Output folder** — Use a dedicated subdirectory per video to avoid mixing frames

## See Also

The `zotok-video-manual-pipeline` skill has detailed step-by-step instructions with code snippets.
