#!/usr/bin/env python3
"""
Click-test tool for page_map.json.

Opens a rectified image in a window. Click anywhere to print the
page / measure / continuation_index for that pixel. Blank areas print None.

Usage
-----
    python3 tools/click_test.py --page 2
    python3 tools/click_test.py --page 2 camera/output/page_02_snapshot_2.jpg
    python3 tools/click_test.py --page 17 camera/output/page_17_snapshot_1.jpg
"""

import argparse
import json
import sys
from pathlib import Path

import cv2

ROOT      = Path(__file__).parent.parent
MAP_PATH  = ROOT / "data" / "page_map.json"
OUT_DIR   = ROOT / "camera" / "output"


def find_snapshot(page_number: int) -> Path | None:
    for n in range(1, 4):
        p = OUT_DIR / f"page_{page_number:02d}_snapshot_{n}.jpg"
        if p.exists():
            return p
    return None


def load_page_regions(page_number: int) -> list[dict]:
    if not MAP_PATH.exists():
        print(f"ERROR: {MAP_PATH} not found.\nRun: python3 tools/build_page_map.py",
              file=sys.stderr)
        sys.exit(1)
    data = json.loads(MAP_PATH.read_text())
    return [r for r in data["regions"] if r["page_number"] == page_number]


def hit_test(x: int, y: int, regions: list[dict]) -> dict | None:
    """Return the first region that contains (x, y), or None."""
    for r in regions:
        if r["x1"] <= x <= r["x2"] and r["y1"] <= y <= r["y2"]:
            return r
    return None


def run(page_number: int, img_path: Path, regions: list[dict]):
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"ERROR: cannot read {img_path}", file=sys.stderr)
        sys.exit(1)

    # Draw regions on the display copy
    base = img.copy()
    for r in regions:
        cv2.rectangle(base, (r["x1"], r["y1"]), (r["x2"], r["y2"]),
                      (0, 200, 255), 1)
        label = f"M{r['measure']}"
        if r["continuation_index"] > 1:
            label += f"c{r['continuation_index']}"
        cv2.putText(base, label, (r["x1"] + 4, r["y1"] + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

    display = base.copy()
    last_result = None

    def on_mouse(event, x, y, flags, param):
        nonlocal display, last_result
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        hit = hit_test(x, y, regions)
        if hit:
            result = (f"page={hit['page_number']}  "
                      f"measure={hit['measure']}  "
                      f"continuation={hit['continuation_index']}  "
                      f"lines={hit['source_line_start']}–{hit['source_line_end']}")
            print(f"  ({x:4d}, {y:4d}) → {result}")
        else:
            print(f"  ({x:4d}, {y:4d}) → None")
        last_result = hit

        # Highlight hit region
        display = base.copy()
        if hit:
            cv2.rectangle(display, (hit["x1"], hit["y1"]),
                          (hit["x2"], hit["y2"]), (0, 255, 0), 3)
        cv2.drawMarker(display, (x, y), (0, 0, 255),
                       cv2.MARKER_CROSS, 20, 2)

    win = f"Click test — page {page_number} (Q to quit)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win, 660, 1020)
    cv2.setMouseCallback(win, on_mouse)

    print(f"\nPage {page_number}: {len(regions)} regions loaded from {MAP_PATH.name}")
    print(f"Image: {img_path.name}")
    print("Click anywhere. Press Q or Esc to quit.\n")

    while True:
        cv2.imshow(win, display)
        key = cv2.waitKey(20) & 0xFF
        if key in (ord('q'), ord('Q'), 27):
            break

    cv2.destroyAllWindows()


def parse_args():
    p = argparse.ArgumentParser(description="Click-test for page_map.json")
    p.add_argument("--page", type=int, required=True,
                   help="Page number to test")
    p.add_argument("image", nargs="?",
                   help="Path to rectified image (optional; auto-detected if omitted)")
    return p.parse_args()


def main():
    args = parse_args()
    regions = load_page_regions(args.page)
    if not regions:
        print(f"WARNING: no regions found for page {args.page} in {MAP_PATH.name}")

    if args.image:
        img_path = Path(args.image).resolve()
    else:
        img_path = find_snapshot(args.page)
    if img_path is None or not img_path.exists():
        print(f"ERROR: no rectified image found for page {args.page}.\n"
              f"Provide image path explicitly.", file=sys.stderr)
        sys.exit(1)

    run(args.page, img_path, regions)


if __name__ == "__main__":
    main()
