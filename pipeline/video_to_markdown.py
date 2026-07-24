#!/usr/bin/env python3
"""
Video-to-Markdown Pipeline
===========================
Extract frames from .mov screen recordings, OCR them with RapidOCR,
and generate clean Docusaurus markdown pages.

Usage:
    source /tmp/video-env/bin/activate
    python3 pipeline/video_to_markdown.py [module_name ...]
    
    If no module names given, processes all 11 .mov files.
"""

import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
from skimage.metrics import structural_similarity as ssim

# ── Paths ──────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DOCS_DIR = PROJECT_DIR / "docs"
STATIC_DIR = PROJECT_DIR / "static"
SCREENSHOTS_DIR = STATIC_DIR / "screenshots"
VIDEO_DIR = Path("/mnt/d/AgentWork/zotok user manual")
OCR_DB_DIR = SCRIPT_DIR / "ocr_data"
os.makedirs(OCR_DB_DIR, exist_ok=True)

OCR_MAX_WIDTH = 800  # resize to this width before OCR (speed vs quality tradeoff)

# ── Module configuration ───────────────────────────────────────────
MODULE_CONFIG = {
    "ai agent": {
        "slug": "ai-agent",
        "label": "AI Agent",
        "icon": "🤖",
        "description": "Automate workflows with AI-powered agents for lead follow-ups, order confirmations, and customer engagement.",
        "sidebar_position": 6,
    },
    "checkin": {
        "slug": "checkins",
        "label": "Checkins",
        "icon": "📍",
        "description": "View and analyze sales team check-in locations, routes, and field visit history.",
        "sidebar_position": 21,
    },
    "customers": {
        "slug": "customers",
        "label": "Customers",
        "icon": "👥",
        "description": "Centralized customer directory with search, filters, profiling, and transaction history.",
        "sidebar_position": 7,
    },
    "fieldops": {
        "slug": "field-ops",
        "label": "Field Ops",
        "icon": "📍",
        "description": "Manage field sales operations — tour programs, beat planning, attendance tracking, and daily reporting.",
        "sidebar_position": 13,
    },
    "invoices": {
        "slug": "invoices",
        "label": "Invoices",
        "icon": "🧾",
        "description": "Create, view, and manage invoices with payment tracking and ageing analysis.",
        "sidebar_position": 10,
    },
    "ledger": {
        "slug": "ledger",
        "label": "Ledger",
        "icon": "📒",
        "description": "Customer-wise ledger with balance tracking, transaction history, and reconciliation.",
        "sidebar_position": 12,
    },
    "orders": {
        "slug": "orders",
        "label": "Orders",
        "icon": "📋",
        "description": "Track and manage sales orders with status tracking, filters, and order processing workflows.",
        "sidebar_position": 9,
    },
    "payments": {
        "slug": "payments",
        "label": "Payments",
        "icon": "💳",
        "description": "Track incoming payments, manage receivable ageing, and configure ageing buckets.",
        "sidebar_position": 11,
    },
    "price list": {
        "slug": "price-list",
        "label": "Price List",
        "icon": "💰",
        "description": "Configure product pricing, price tiers, and customer-specific price lists.",
        "sidebar_position": 15,
    },
    "products": {
        "slug": "products",
        "label": "Products (Item)",
        "icon": "📦",
        "description": "Manage product catalog, track inventory, revenue, stock levels, and sales performance.",
        "sidebar_position": 8,
    },
    "schemes": {
        "slug": "schemes",
        "label": "Schemes",
        "icon": "🏷️",
        "description": "Create and manage promotional schemes, discounts, and special offers for customers.",
        "sidebar_position": 14,
    },
}

FILENAME_TO_KEY = {
    "Ai Agent.mov": "ai agent",
    "checkin.mov": "checkin",
    "customers.mov": "customers",
    "fieldops.mov": "fieldops",
    "invoices.mov": "invoices",
    "ledger.mov": "ledger",
    "orders.mov": "orders",
    "payments.mov": "payments",
    "price list.mov": "price list",
    "products.mov": "products",
    "schemes.mov": "schemes",
}


# ── Frame Extraction ───────────────────────────────────────────────

def extract_frames(video_path, sample_interval_sec=4.0):
    """
    Extract frames by sampling at fixed time intervals.
    Uses grab+retrieve for performance.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"  ❌ Cannot open video: {video_path}")
        return []
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fps <= 0:
        fps = 30.0
    
    duration = total_frames / fps
    print(f"  Video: {total_frames} frames, {fps:.1f} fps, {duration:.1f}s")
    
    skip_frames = max(1, int(fps * sample_interval_sec))
    frames = []
    frame_num = 0
    
    while True:
        ret = cap.grab()
        if not ret:
            break
        
        if frame_num % skip_frames == 0:
            ret2, frame = cap.retrieve()
            if ret2:
                timestamp = frame_num / fps
                frames.append((frame_num, timestamp, frame.copy()))
        
        frame_num += 1
    
    cap.release()
    print(f"  Sampled {len(frames)} frames (every {sample_interval_sec}s)")
    return frames


# ── Frame Deduplication ────────────────────────────────────────────

def deduplicate_frames(frames, keep_threshold=82, width=160, height=90):
    """Remove near-duplicate frames via SSIM."""
    if not frames:
        return []
    
    unique = [frames[0]]
    prev_gray = cv2.cvtColor(frames[0][2], cv2.COLOR_BGR2GRAY)
    prev_small = cv2.resize(prev_gray, (width, height))
    
    for frame_num, timestamp, frame in frames[1:]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, (width, height))
        
        score = ssim(prev_small, small, data_range=small.max() - small.min())
        score_pct = score * 100
        
        if score_pct < keep_threshold:
            unique.append((frame_num, timestamp, frame))
            prev_small = small
    
    removed = len(frames) - len(unique)
    if removed > 0:
        print(f"  Dedup removed {removed} similar frames")
    print(f"  Unique frames: {len(unique)}")
    return unique


# ── OCR Processing ─────────────────────────────────────────────────

def ocr_frames(frames_data, engine):
    """Run RapidOCR on each frame (resized to OCR_MAX_WIDTH)."""
    results = []
    start = time.time()
    
    for i, (frame_num, timestamp, frame_bgr) in enumerate(frames_data):
        # Resize to speed up OCR
        h, w = frame_bgr.shape[:2]
        if w > OCR_MAX_WIDTH:
            scale = OCR_MAX_WIDTH / w
            new_w = OCR_MAX_WIDTH
            new_h = int(h * scale)
            resized = cv2.resize(frame_bgr, (new_w, new_h))
        else:
            resized = frame_bgr
        
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        
        result, elapsed = engine(pil_img)
        
        texts = []
        if result:
            for box, text, score in result:
                if text and text.strip():
                    texts.append(text.strip())
        
        results.append({
            "frame_num": frame_num,
            "timestamp": round(timestamp, 2),
            "frame_index": i,
            "texts": texts,
        })
        
        elapsed = time.time() - start
        per_frame = elapsed / (i + 1)
        remaining = per_frame * (len(frames_data) - i - 1)
        print(f"  OCR [{i+1}/{len(frames_data)}] frame {frame_num} — {len(texts)} texts — {remaining:.0f}s remaining")
    
    print(f"  OCR complete in {time.time()-start:.1f}s")
    return results


# ── Screenshot Saving ──────────────────────────────────────────────

def save_screenshots(frames_data, module_slug):
    """Save frames as JPG screenshots."""
    dest_dir = SCREENSHOTS_DIR / module_slug
    os.makedirs(dest_dir, exist_ok=True)
    
    # Clear old screenshots for this module
    for f in dest_dir.glob("screenshot-*.jpg"):
        f.unlink()
    
    filenames = []
    for i, (frame_num, timestamp, frame) in enumerate(frames_data):
        filename = f"screenshot-{i:02d}.jpg"
        path = dest_dir / filename
        cv2.imwrite(str(path), frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        filenames.append(filename)
    
    print(f"  Saved {len(filenames)} screenshots")
    return filenames


# ── Markdown Generation ────────────────────────────────────────────

def organize_ocr_texts(ocr_results):
    """Organize OCR texts into structured sections."""
    all_texts = []
    for r in ocr_results:
        all_texts.extend(r["texts"])
    
    kpis = []
    buttons = []
    general = []
    
    kpi_patterns = [
        r'^\d{1,3}(\.\d{1,2})?\s*(K|L|Cr|%)\s*$',
        r'^[₹$€]\s*[\d,]+',
        r'^\d+[,.]?\d*\s*(%|L|K|Cr|₹|\$|€)?$',
    ]
    button_endings = ['add', 'create', 'new', 'save', 'cancel', 'delete',
                       'edit', 'download', 'upload', 'export', 'import',
                       'apply', 'clear', 'refresh', 'view', 'manage']
    
    seen_lower = set()
    for text in all_texts:
        t = text.strip()
        if not t or len(t) < 2 or t.lower() in seen_lower:
            continue
        seen_lower.add(t.lower())
        
        tl = t.lower()
        
        # Check KPI (starts with number or currency)
        is_kpi = any(re.match(pat, t) for pat in kpi_patterns)
        if is_kpi:
            kpis.append(t)
            continue
        
        # Check button-like
        if any(tl.endswith(kw) or tl.startswith(kw) for kw in button_endings):
            if len(t) < 30:
                buttons.append(t)
                continue
        
        if len(t) > 3:
            general.append(t)
    
    return {
        "kpis": kpis[:20],
        "buttons": buttons[:15],
        "texts": general[:40],
    }


def generate_markdown(module_cfg, ocr_organized, screenshot_filenames):
    """Generate a clean Docusaurus markdown page (no duplicated tables)."""
    slug = module_cfg["slug"]
    label = module_cfg["label"]
    icon = module_cfg["icon"]
    desc = module_cfg["description"]
    pos = module_cfg["sidebar_position"]
    
    lines = [
        "---",
        f"sidebar_position: {pos}",
        f'title: "{label}"',
        "---",
        "",
        f"# {icon} {label}",
        "",
    ]
    
    if desc:
        lines.append(desc)
        lines.append("")
    
    lines.append("## Overview")
    lines.append("")
    lines.append(f"This page covers the {label} module in the ZöTok platform.")
    lines.append("")
    
    # Screenshots
    for i, ss_name in enumerate(screenshot_filenames):
        lines.append(f"![{label} Screenshot {i+1}](/screenshots/{slug}/{ss_name})")
        lines.append("")
    
    # KPIs
    kpis = ocr_organized.get("kpis", [])
    if kpis:
        lines.append("## Key Metrics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        for k in kpis:
            lines.append(f"| | {k} |")
        lines.append("")
    
    # Buttons/Actions
    buttons = ocr_organized.get("buttons", [])
    if buttons:
        lines.append("## Available Actions")
        lines.append("")
        lines.append("| Action | Description |")
        lines.append("|--------|-------------|")
        for b in buttons:
            lines.append(f"| **{b}** | |")
        lines.append("")
    
    # Feature list from OCR text
    texts = ocr_organized.get("texts", [])
    if texts:
        lines.append("## Features")
        lines.append("")
        # Filter out chrome/UI noise
        skip_patterns = ['app.zotok.ai', '×', '☆', '⚙', 'http', '.com/', 'admin/']
        substantive = []
        for t in texts:
            if not any(s in t.lower() for s in skip_patterns):
                substantive.append(t)
        for t in substantive[:20]:
            lines.append(f"- {t}")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("*Page generated from video walkthrough via OCR pipeline.*")
    lines.append("")
    
    return "\n".join(lines)


# ── Main Processing ────────────────────────────────────────────────

def process_module(key, engine):
    """Process a single module end-to-end."""
    print(f"\n{'='*60}")
    print(f"Processing: {key}")
    print(f"{'='*60}")
    
    module_cfg = MODULE_CONFIG[key]
    slug = module_cfg["slug"]
    
    # Find video file
    mov_filename = None
    for fname, k in FILENAME_TO_KEY.items():
        if k == key:
            mov_filename = fname
            break
    if not mov_filename:
        print(f"  ❌ No mapping for '{key}'")
        return False
    
    video_path = VIDEO_DIR / mov_filename
    if not video_path.exists():
        print(f"  ❌ Video not found: {video_path}")
        return False
    
    # Step 1: Extract frames (sampling)
    print(f"  Extracting frames from {mov_filename}...")
    t0 = time.time()
    frames = extract_frames(str(video_path))
    if not frames:
        print(f"  ❌ No frames extracted")
        return False
    print(f"  Extraction: {time.time()-t0:.1f}s")
    
    # Step 2: Deduplicate
    t0 = time.time()
    unique_frames = deduplicate_frames(frames)
    if not unique_frames:
        print(f"  ❌ All frames were duplicates")
        return False
    print(f"  Dedup: {time.time()-t0:.1f}s")
    
    # Step 3: OCR
    print(f"  Running OCR on {len(unique_frames)} frames...")
    t0 = time.time()
    ocr_results = ocr_frames(unique_frames, engine)
    print(f"  OCR: {time.time()-t0:.1f}s")
    
    # Save OCR data
    ocr_path = OCR_DB_DIR / f"ocr_{slug}.json"
    with open(ocr_path, "w") as f:
        json.dump(ocr_results, f, indent=2, ensure_ascii=False)
    
    # Step 4: Save screenshots (use the full-res unique frames)
    t0 = time.time()
    screenshot_filenames = save_screenshots(unique_frames, slug)
    
    # Step 5: Generate markdown
    ocr_organized = organize_ocr_texts(ocr_results)
    markdown = generate_markdown(module_cfg, ocr_organized, screenshot_filenames)
    
    page_dir = DOCS_DIR / slug
    os.makedirs(page_dir, exist_ok=True)
    page_path = page_dir / "overview.md"
    with open(page_path, "w") as f:
        f.write(markdown)
    print(f"  ✅ Written: {page_path}")
    print(f"  Total time: {time.time()-t0:.1f}s")
    
    return True


def main():
    print("=" * 60)
    print("VIDEO-TO-MARKDOWN PIPELINE")
    print("=" * 60)
    print(f"Video dir: {VIDEO_DIR}")
    print(f"OCR resize: {OCR_MAX_WIDTH}px wide")
    print()
    
    # Determine modules
    args = sys.argv[1:]
    if args:
        keys_to_process = [a for a in args if a in MODULE_CONFIG]
        if not keys_to_process:
            print(f"Unknown module(s): {args}")
            print(f"Available: {list(MODULE_CONFIG.keys())}")
            return 1
    else:
        keys_to_process = list(MODULE_CONFIG.keys())
    
    print(f"Modules to process: {len(keys_to_process)}")
    for k in keys_to_process:
        print(f"  - {k} → {MODULE_CONFIG[k]['slug']}")
    
    # Init OCR engine
    print("\nInitializing RapidOCR engine...")
    engine = RapidOCR()
    print("Engine ready.\n")
    
    global_start = time.time()
    success = 0
    fail = 0
    
    for key in keys_to_process:
        try:
            if process_module(key, engine):
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            fail += 1
        elapsed = time.time() - global_start
        done = success + fail
        total = len(keys_to_process)
        per_item = elapsed / done if done else 0
        remaining = per_item * (total - done)
        print(f"  ⏱  Elapsed: {elapsed:.0f}s, Est. remaining: {remaining:.0f}s")
    
    total_time = time.time() - global_start
    print(f"\n{'='*60}")
    print(f"Pipeline complete: {success} succeeded, {fail} failed")
    print(f"Total time: {total_time/60:.1f} min")
    print(f"{'='*60}")
    print("\nNext: `npm run build` to verify generated pages.")
    
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
