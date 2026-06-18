
"""
Very small MVP for testing sprite template matching against a screenshot crop.

Install optional deps:
  pip install opencv-python pandas numpy

Run:
  python sprite_template_matcher_mvp.py --image path\to\crop.png --top 10

This expects 19_SPRITE_MANIFEST_CHAMPIONS_MENU.csv to already exist.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'upload_these_files'/'19_SPRITE_MANIFEST_CHAMPIONS_MENU.csv'


def load_gray(path: Path):
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    if img.ndim == 3 and img.shape[2] == 4:
        alpha = img[:, :, 3]
        bgr = img[:, :, :3]
        bg = np.full_like(bgr, 255)
        img = np.where(alpha[:, :, None] > 0, bgr, bg)
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', required=True, help='Screenshot crop image path')
    ap.add_argument('--top', type=int, default=10)
    args = ap.parse_args()

    target = load_gray(Path(args.image))
    if target is None:
        raise SystemExit('Could not read image')
    target = cv2.resize(target, (128, 128))

    df = pd.read_csv(MANIFEST)
    results=[]
    for _, row in df.iterrows():
        rel = row.get('sprite_path_normal','')
        if not isinstance(rel, str) or not rel:
            continue
        tmpl = load_gray(ROOT/rel)
        if tmpl is None:
            continue
        tmpl = cv2.resize(tmpl, (128,128))
        score = cv2.matchTemplate(target, tmpl, cv2.TM_CCOEFF_NORMED)[0][0]
        results.append((float(score), row['pokemon_id'], row.get('pokemon_display_ko',''), rel))

    for score, pid, ko, rel in sorted(results, reverse=True)[:args.top]:
        print(f'{score:.4f}\t{pid}\t{ko}\t{rel}')

if __name__ == '__main__':
    main()
