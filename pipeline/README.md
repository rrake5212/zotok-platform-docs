# ZoTok Video-to-Manual Pipeline

Scripts for extracting structured user manuals from software walkthrough videos.

## Files

| Script | Purpose |
|--------|---------|
| `generate_docx.py` (603 lines) | Full DOCX builder — reads enhanced frames + navigation asset, writes structured manual with cover, TOC, chapters, tables, and embedded screenshots |
| `ocr_frames.py` (28 lines) | Runs RapidOCR on extracted key frames, prints all visible text per frame |

## Workflow

1. **Extract frames** from source MP4 (in `/videos/`) using OpenCV
2. **Detect scene transitions** via histogram differencing (CHISQR)
3. **Deduplicate** with structural similarity at 160×90 to get ~13 key frames
4. **Run OCR** using RapidOCR on each key frame
5. **Map click flow** by comparing consecutive frames
6. **Generate DOCX** with python-docx

## Dependencies

```bash
python3 -m venv /tmp/video-env
source /tmp/video-env/bin/activate
pip install opencv-python-headless Pillow rapidocr-onnxruntime python-docx
```

## Output

Generated DOCX files go to `/output/`. Screenshots for the docs site go to `/static/screenshots/<module>/`.

See the `zotok-video-manual-pipeline` skill for detailed steps.
