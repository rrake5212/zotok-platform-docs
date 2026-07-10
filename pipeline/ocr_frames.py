"""OCR on key frames from Zotok Home and Threads video"""
import os
from rapidocr_onnxruntime import RapidOCR

engine = RapidOCR()

frame_dir = "/tmp/zotok_manual_frames_v2/"
files = sorted([f for f in os.listdir(frame_dir) if f.endswith(".jpg") and "enhanced" not in f])

for fname in files:
    path = os.path.join(frame_dir, fname)
    result, elapse = engine(path)
    
    print(f"\n=== {fname} ===")
    if result:
        texts = []
        for box, text, score in result:
            if text and text.strip():
                texts.append(text.strip())
        # Join and show
        if texts:
            print("  Texts found:")
            for t in texts:
                print(f"    - {t}")
        else:
            print("  No text detected")
    else:
        print("  No text detected")
