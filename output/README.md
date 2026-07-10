# Generated Manuals

Output artifacts from the ZoTok video-to-manual pipeline.

| File | Source Video | Size | Description |
|------|-------------|------|-------------|
| `ZoTok_User_Manual_Home_and_Threads.docx` | `Home and Threads.mp4` | 703 KB | Full user manual — 7 chapters with cover page, TOC, numbered sections, data tables, and embedded CLAHE-enhanced screenshots |

## Processing Status

| Video | Status | Output |
|-------|--------|--------|
| `Home and Threads.mp4` | ✅ DOCX generated | `ZoTok_User_Manual_Home_and_Threads.docx` |
| `GROW AND CAMPAIGN.mp4` | ✅ Frames extracted + OCR + docs generated | 4 campaign pages under `../docs/campaigns/` |

## Notes

- Screenshots from extracted frames are distributed into `../static/screenshots/<module>/` for use in the Docusaurus documentation site
- Source videos are in `../videos/` (gitignored)
- The pipeline scripts are in `../pipeline/`
