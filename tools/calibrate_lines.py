#!/usr/bin/env python3
"""
Interactive Braille grid calibration for page coordinate mapping.

Displays a 40-column × 25-row grid overlay on a rectified Braille page image.
Row 25 is the Braille page-number row (shown in a different colour).
Align the grid so each cell covers exactly one Braille cell.

Controls
--------
  Arrow keys          Move grid origin (x / y)
  [ / ]               Decrease / increase column width  (cell_width)
  - / =               Decrease / increase row height    (line_height)
  S                   Save to data/braille_grid_calibration.json
  R                   Reset to defaults
  Q / Esc             Quit without saving

Usage
-----
    python3 tools/calibrate_lines.py camera/output/page_02_snapshot_2.jpg
    python3 tools/calibrate_lines.py --page 2   # auto-find the page 2 snapshot
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT       = Path(__file__).parent.parent
DATA_DIR   = ROOT / "data"
CALIB_PATH = DATA_DIR / "braille_grid_calibration.json"
OUTPUT_DIR = ROOT / "camera" / "output"

CANONICAL_W  = 1100
CANONICAL_H  = 1700
COLUMNS      = 40
ROWS         = 25   # row 25 = Braille page-number row
CONTENT_ROWS = 24   # rows 1–24 carry score content

# Initial estimates based on standard Braille 6 mm / 10 mm cell pitch
# at canonical 1100×1700 resolution (≈ 4.33 DPI on tabloid).
DEFAULT_X_ORIGIN  = 78.0
DEFAULT_Y_ORIGIN  = 358.0
DEFAULT_CELL_W    = 23.6
DEFAULT_LINE_H    = 39.4

DISPLAY_SCALE = 0.5        # show window at 550×850
MOVE_STEP     = 1.0        # px per arrow key press
SPACING_STEP  = 0.1        # px per [ ] - = key press

# macOS Cocoa backend arrow key codes (cv2.waitKeyEx)
KEY_UP    = 63232
KEY_DOWN  = 63233
KEY_LEFT  = 63234
KEY_RIGHT = 63235


def find_snapshot(page_number: int) -> Path | None:
    for suffix in ("_snapshot_1", "_snapshot_2", "_snapshot_3",
                   "_test_rectified", "_test2_rectified"):
        p = OUTPUT_DIR / f"page{page_number:02d}{suffix}.jpg"
        if p.exists():
            return p
    for n in range(1, 4):
        p = OUTPUT_DIR / f"page_{page_number:02d}_snapshot_{n}.jpg"
        if p.exists():
            return p
    return None


def draw_grid(base: np.ndarray,
              x_origin: float, y_origin: float,
              cell_w: float, line_h: float) -> np.ndarray:
    """Return a copy of base with the 40×25 Braille grid drawn on it."""
    img = base.copy()

    x_end = x_origin + COLUMNS * cell_w
    y_end = y_origin + ROWS    * line_h
    y_content_end = y_origin + CONTENT_ROWS * line_h

    # Outer boundary
    cv2.rectangle(img,
                  (round(x_origin), round(y_origin)),
                  (round(x_end),    round(y_end)),
                  (0, 220, 255), 2)

    # Content / page-number separator
    cv2.line(img,
             (round(x_origin), round(y_content_end)),
             (round(x_end),    round(y_content_end)),
             (0, 140, 255), 2)

    # Column lines
    for c in range(1, COLUMNS):
        x = round(x_origin + c * cell_w)
        cv2.line(img, (x, round(y_origin)), (x, round(y_end)),
                 (60, 60, 180), 1)

    # Row lines (content rows green, page-number row orange)
    for r in range(1, ROWS):
        y = round(y_origin + r * line_h)
        color = (40, 160, 40) if r < CONTENT_ROWS else (0, 140, 255)
        cv2.line(img, (round(x_origin), y), (round(x_end), y), color, 1)

    # Row number labels every 5 rows
    for r in range(5, ROWS + 1, 5):
        y = round(y_origin + (r - 0.5) * line_h)
        label = str(r) if r < ROWS else "25\n(pg#)"
        cv2.putText(img, str(r),
                    (max(0, round(x_origin) - 32), y + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 220, 255), 1)

    # Page-number row label
    y25_mid = round(y_content_end + line_h * 0.5)
    cv2.putText(img, "r25 pg#",
                (max(0, round(x_origin) - 58), y25_mid + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 140, 255), 1)

    # Column number labels every 5 columns
    for c in range(5, COLUMNS + 1, 5):
        x = round(x_origin + (c - 0.5) * cell_w)
        cv2.putText(img, str(c),
                    (x - 8, max(16, round(y_origin) - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 220, 255), 1)

    # Current parameter readout (bottom)
    param_str = (f"x={x_origin:.1f}  y={y_origin:.1f}  "
                 f"col_w={cell_w:.2f}  row_h={line_h:.2f}")
    cv2.putText(img, param_str, (10, CANONICAL_H - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 180), 1)

    # Key hint (top)
    hint = "Arrows:move  [/]:col-w  -/=:row-h  S:save  R:reset  Q:quit"
    cv2.putText(img, hint, (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.46, (160, 160, 160), 1)

    return img


def calibrate(image_path: Path):
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"ERROR: cannot read image: {image_path}", file=sys.stderr)
        sys.exit(1)

    h, w = img.shape[:2]
    if (h, w) != (CANONICAL_H, CANONICAL_W):
        img = cv2.resize(img, (CANONICAL_W, CANONICAL_H))
        print(f"  Resized to {CANONICAL_W}×{CANONICAL_H}")

    base = img.copy()

    x_origin = DEFAULT_X_ORIGIN
    y_origin = DEFAULT_Y_ORIGIN
    cell_w   = DEFAULT_CELL_W
    line_h   = DEFAULT_LINE_H

    dw = round(CANONICAL_W * DISPLAY_SCALE)
    dh = round(CANONICAL_H * DISPLAY_SCALE)

    win = "Braille grid calibration  (Q = quit without saving)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win, dw, dh)

    print(f"\nCalibrating from: {image_path.name}")
    print("Arrow keys: move grid   [ / ]: column width   - / =: row height")
    print("S: save   R: reset   Q / Esc: quit without saving\n")

    while True:
        frame = draw_grid(base, x_origin, y_origin, cell_w, line_h)
        cv2.imshow(win, cv2.resize(frame, (dw, dh)))

        key = cv2.waitKeyEx(20)
        if key < 0:
            continue

        if key in (ord('q'), ord('Q'), 27):
            print("Quit — calibration not saved.")
            break

        elif key == KEY_UP:
            y_origin -= MOVE_STEP
        elif key == KEY_DOWN:
            y_origin += MOVE_STEP
        elif key == KEY_LEFT:
            x_origin -= MOVE_STEP
        elif key == KEY_RIGHT:
            x_origin += MOVE_STEP

        elif key == ord('['):
            cell_w = max(1.0, cell_w - SPACING_STEP)
        elif key == ord(']'):
            cell_w += SPACING_STEP

        elif key == ord('-'):
            line_h = max(1.0, line_h - SPACING_STEP)
        elif key in (ord('='), ord('+')):
            line_h += SPACING_STEP

        elif key in (ord('r'), ord('R')):
            x_origin = DEFAULT_X_ORIGIN
            y_origin = DEFAULT_Y_ORIGIN
            cell_w   = DEFAULT_CELL_W
            line_h   = DEFAULT_LINE_H
            print("  Reset to defaults.")

        elif key in (ord('s'), ord('S')):
            calib = {
                "source_image":  str(image_path.relative_to(ROOT)),
                "x_origin":      round(x_origin, 2),
                "y_origin":      round(y_origin, 2),
                "cell_width":    round(cell_w,   3),
                "line_height":   round(line_h,   3),
                "columns":       COLUMNS,
                "rows":          ROWS,
                "content_rows":  CONTENT_ROWS,
                "method":        "grid_interactive",
            }
            DATA_DIR.mkdir(exist_ok=True)
            CALIB_PATH.write_text(json.dumps(calib, indent=2))
            print(f"\nCalibration saved: {CALIB_PATH}")
            print(f"  x_origin={x_origin:.1f}  y_origin={y_origin:.1f}")
            print(f"  cell_width={cell_w:.3f}  line_height={line_h:.3f}")
            print(f"\nNext step:  python3 tools/build_page_map.py")
            break

    cv2.destroyAllWindows()


def parse_args():
    p = argparse.ArgumentParser(description="Interactive Braille grid calibration")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("image", nargs="?",
                       help="Path to a rectified page image")
    group.add_argument("--page", type=int, metavar="N",
                       help="Page number; auto-find its snapshot in camera/output/")
    return p.parse_args()


def main():
    args = parse_args()
    if args.page is not None:
        img_path = find_snapshot(args.page)
        if img_path is None:
            print(f"ERROR: no snapshot found for page {args.page} in {OUTPUT_DIR}",
                  file=sys.stderr)
            sys.exit(1)
    else:
        img_path = Path(args.image).resolve()
        if not img_path.exists():
            print(f"ERROR: image not found: {img_path}", file=sys.stderr)
            sys.exit(1)
    calibrate(img_path)


if __name__ == "__main__":
    main()
