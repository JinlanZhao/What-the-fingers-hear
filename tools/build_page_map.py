#!/usr/bin/env python3
"""
Build data/page_map.json from the BRF source + line calibration.

Workflow
--------
1. Parse BRF → verify page count, line counts, measure regions.
2. Load data/braille_grid_calibration.json (must exist; run calibrate_lines.py first).
3. Convert each BRF line range → pixel rectangle in the canonical 1100×1700 image.
4. Write data/page_map.json.
5. Generate overlay images in camera/output/ (unless --no-overlay).

Usage
-----
    python3 tools/build_page_map.py
    python3 tools/build_page_map.py --no-overlay
    python3 tools/build_page_map.py --verify-only     # step 1 only; no JSON written
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).parent.parent
BRF_PATH   = ROOT / "Score-prep" / "Score_Bars16_4-4_144bpm_braille.brf"
DATA_DIR   = ROOT / "data"
CALIB_PATH = DATA_DIR / "braille_grid_calibration.json"
MAP_PATH   = DATA_DIR / "page_map.json"
OUTPUT_DIR = ROOT / "camera" / "output"

# ── constants ──────────────────────────────────────────────────────────────────
CANONICAL_W    = 1100
CANONICAL_H    = 1700
LINES_PER_PAGE = 25          # line 25 on each content page = Braille page number
CONTENT_LINES  = 24          # lines 1–24 carry content (includes intentional blanks)
TITLE_PAGE     = 1           # page 1 is the title page; never maps to a measure

# Proposed ArUco marker ID → page number mapping.
# Extends the existing code convention (ID 10 = page 1, ID 11 = page 2).
# IDs for pages 3–18 have not yet been printed/programmed.
# Confirm and update PAGE_MARKER_MAP below, then regenerate.
PAGE_MARKER_MAP = {9 + n: n for n in range(1, 19)}
# Result: {10:1, 11:2, 12:3, ..., 27:18}

# ── BRF digit-letter decoder ───────────────────────────────────────────────────
_D = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5,
      "f": 6, "g": 7, "h": 8, "i": 9, "j": 0}


def _decode_measure(s: str) -> int | None:
    """
    Decode a BRF measure-number token.
    SM BungSang bar-over-bar format uses digit-letter cells without the # indicator
    for inline measure numbers: a=1, b=2, …, i=9, aj=10, aa=11, ab=12, …
    Returns None if the string is not a valid measure token.
    """
    s = s.strip()
    if not s or not all(c in _D for c in s):
        return None
    result = 0
    for c in s:
        result = result * 10 + _D[c]
    return result if result > 0 else None


def _last_content_line(lines: list[str]) -> int:
    """Return the 1-indexed number of the last non-blank line, capped at CONTENT_LINES."""
    for i in range(min(CONTENT_LINES, len(lines)) - 1, -1, -1):
        if lines[i].strip():
            return i + 1
    return 1


def _trim_end(lines: list[str], start: int, raw_end: int) -> int:
    """Trim trailing blank lines in [start, raw_end] (1-indexed). Return adjusted end."""
    for i in range(min(raw_end, CONTENT_LINES) - 1, start - 2, -1):
        if lines[i].strip():
            return i + 1
    return start

# ── BRF parser ─────────────────────────────────────────────────────────────────

def parse_brf(brf_path: Path) -> list[dict]:
    """
    Parse BRF → list of region dicts (source-level, no pixel coords yet).

    Each dict: page_number, measure, continuation_index,
               source_line_start, source_line_end
    """
    raw   = brf_path.read_bytes()
    pages = raw.split(b"\x0c")

    if len(pages) != 18:
        raise ValueError(
            f"Expected 18 pages in BRF (form-feed separated), found {len(pages)}.\n"
            f"File: {brf_path}"
        )

    regions: list[dict] = []
    measure_cont: dict[int, int] = {}
    last_measure: int | None = None

    for pi, pb in enumerate(pages):
        pnum = pi + 1
        if pnum == TITLE_PAGE:
            continue

        lines = [ln.decode("ascii", errors="replace")
                 for ln in pb.split(b"\n")]

        # Collect measure-indicator lines (lines 1..CONTENT_LINES only)
        mstarts: list[tuple[int, int]] = []
        for li in range(1, LINES_PER_PAGE):          # 1-indexed, skips line 25
            if li > len(lines):
                break
            m = _decode_measure(lines[li - 1])
            if m is not None:
                mstarts.append((li, m))

        if not mstarts:
            # Continuation page: no new measure begins here
            if last_measure is None:
                raise ValueError(
                    f"Page {pnum}: no measure indicator and no previous measure to continue."
                )
            end = _last_content_line(lines)
            measure_cont[last_measure] = measure_cont.get(last_measure, 1) + 1
            regions.append({
                "page_number": pnum,
                "measure": last_measure,
                "continuation_index": measure_cont[last_measure],
                "source_line_start": 1,
                "source_line_end": end,
            })
            continue

        for i, (sl, mnum) in enumerate(mstarts):
            if i + 1 < len(mstarts):
                el = _trim_end(lines, sl, mstarts[i + 1][0] - 1)
            else:
                el = _last_content_line(lines)

            measure_cont[mnum] = measure_cont.get(mnum, 0) + 1
            regions.append({
                "page_number": pnum,
                "measure": mnum,
                "continuation_index": measure_cont[mnum],
                "source_line_start": sl,
                "source_line_end": el,
            })
            last_measure = mnum

    return regions

# ── verification report ────────────────────────────────────────────────────────

def print_verification(regions: list[dict]) -> bool:
    """Print SOP step-1 verification report. Return True if all checks pass."""
    ok = True

    measures_found = sorted({r["measure"] for r in regions})
    measures_expected = list(range(1, 17))

    print("=== BRF Verification Report ===")
    print(f"  Source        : {BRF_PATH.name}")
    print(f"  Regions found : {len(regions)}")
    print(f"  Measures found: {measures_found}")
    print(f"  Expected 1–16 : {measures_expected}")

    if measures_found != measures_expected:
        print("  ERROR: measure set mismatch")
        ok = False
    else:
        print("  Measure set   : OK")

    # Cross-page checks
    m1_pages  = [r["page_number"] for r in regions if r["measure"] == 1]
    m16_pages = [r["page_number"] for r in regions if r["measure"] == 16]
    p1_regions = [r for r in regions if r["page_number"] == TITLE_PAGE]

    print(f"  Measure 1  pages: {m1_pages}  (expected [2, 3])")
    print(f"  Measure 16 pages: {m16_pages} (expected [17, 18])")
    print(f"  Title page regions: {len(p1_regions)}  (expected 0)")

    if m1_pages != [2, 3]:
        print("  ERROR: measure 1 cross-page mismatch"); ok = False
    if m16_pages != [17, 18]:
        print("  ERROR: measure 16 cross-page mismatch"); ok = False
    if p1_regions:
        print("  ERROR: title page has measure regions"); ok = False

    print()
    print(f"  {'M':>3} {'cont':>4} {'page':>5} {'lines':>12}")
    print("  " + "-" * 30)
    for r in regions:
        print(f"  M{r['measure']:>2}  [{r['continuation_index']}]"
              f"   p{r['page_number']:>2}   "
              f"line {r['source_line_start']:>2} – {r['source_line_end']:>2}")
    print()

    if ok:
        print("  Result: ALL CHECKS PASSED")
    else:
        print("  Result: FAILED — do not generate page_map.json")
    print()
    return ok

# ── calibration loader ─────────────────────────────────────────────────────────

def load_calibration(path: Path) -> dict:
    """Load braille_grid_calibration.json. Raise if missing or invalid."""
    if not path.exists():
        raise FileNotFoundError(
            f"Calibration file not found: {path}\n"
            f"Run first:  python3 tools/calibrate_lines.py"
        )
    calib = json.loads(path.read_text())
    required = {"x_origin", "y_origin", "cell_width", "line_height"}
    missing = required - calib.keys()
    if missing:
        raise ValueError(f"Calibration file missing keys: {missing}")
    cols = calib.get("columns", 40)
    if not (0 <= calib["x_origin"] < CANONICAL_W):
        raise ValueError(f"Calibration x_origin out of range: {calib['x_origin']}")
    if not (0 <= calib["y_origin"] < CANONICAL_H):
        raise ValueError(f"Calibration y_origin out of range: {calib['y_origin']}")
    if calib["cell_width"] <= 0 or calib["line_height"] <= 0:
        raise ValueError("cell_width and line_height must be positive")
    return calib

# ── pixel coordinate conversion ────────────────────────────────────────────────

def region_to_pixels(region: dict, calib: dict) -> dict:
    """Add x1, y1, x2, y2 (pixel coords in canonical image) to a region dict."""
    x_origin = calib["x_origin"]
    y_origin = calib["y_origin"]
    cell_w   = calib["cell_width"]
    line_h   = calib["line_height"]
    cols     = calib.get("columns", 40)

    l1 = region["source_line_start"]
    l2 = region["source_line_end"]

    x1 = round(x_origin)
    x2 = round(x_origin + cols * cell_w)
    y1 = round(y_origin + (l1 - 1) * line_h)
    y2 = round(y_origin +  l2      * line_h)

    return {**region,
            "page_marker_id": _page_to_marker(region["page_number"]),
            "x1": x1,
            "y1": max(0, y1),
            "x2": min(CANONICAL_W - 1, x2),
            "y2": min(CANONICAL_H - 1, y2)}


def _page_to_marker(page_number: int) -> int:
    """Return the ArUco marker ID for a given page number."""
    for mid, pnum in PAGE_MARKER_MAP.items():
        if pnum == page_number:
            return mid
    raise ValueError(f"No marker ID defined for page {page_number}")

# ── overlay image generator ────────────────────────────────────────────────────

def _find_rectified(page_number: int) -> Path | None:
    """Return the first available rectified image for this page, or None."""
    marker_id = _page_to_marker(page_number)
    candidates = [
        OUTPUT_DIR / f"page_{page_number:02d}_snapshot_1.jpg",
        OUTPUT_DIR / f"page_{page_number:02d}_snapshot_2.jpg",
        OUTPUT_DIR / f"page_{page_number:02d}_snapshot_3.jpg",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def generate_overlay(page_number: int, page_regions: list[dict]) -> Path | None:
    """Draw measure regions onto the rectified image; save to output/."""
    img_path = _find_rectified(page_number)
    if img_path is None:
        return None

    img = cv2.imread(str(img_path))
    if img is None:
        return None

    # Resize to canonical if needed
    if img.shape[:2] != (CANONICAL_H, CANONICAL_W):
        img = cv2.resize(img, (CANONICAL_W, CANONICAL_H))

    colors = [
        (0, 200, 255), (0, 255, 100), (255, 180, 0),
        (200, 0, 255), (0, 140, 255), (100, 255, 0),
    ]
    for i, r in enumerate(page_regions):
        color = colors[i % len(colors)]
        x1, y1, x2, y2 = r["x1"], r["y1"], r["x2"], r["y2"]
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        label = f"M{r['measure']}"
        if r["continuation_index"] > 1:
            label += f" cont{r['continuation_index']}"
        cv2.putText(img, label, (x1 + 6, y1 + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    out_path = OUTPUT_DIR / f"page_{page_number:02d}_overlay.jpg"
    cv2.imwrite(str(out_path), img)
    return out_path

# ── main ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Build data/page_map.json")
    p.add_argument("--verify-only", action="store_true",
                   help="Run BRF verification only; do not write any files")
    p.add_argument("--no-overlay", action="store_true",
                   help="Skip overlay image generation")
    return p.parse_args()


def main():
    args = parse_args()

    # Step 1: parse and verify BRF
    print("Step 1: Parsing BRF source…")
    regions = parse_brf(BRF_PATH)
    ok = print_verification(regions)
    if not ok:
        sys.exit(1)

    if args.verify_only:
        print("--verify-only: stopping here.")
        sys.exit(0)

    # Step 2: load calibration
    print("Step 2: Loading line calibration…")
    calib = load_calibration(CALIB_PATH)
    print(f"  x_origin={calib['x_origin']}  y_origin={calib['y_origin']}"
          f"  cell_width={calib['cell_width']}  line_height={calib['line_height']}")
    print(f"  → columns={calib.get('columns', 40)}\n")

    # Step 3: convert to pixel coordinates
    print("Step 3: Converting line ranges to pixel coordinates…")
    full_regions = [region_to_pixels(r, calib) for r in regions]

    # Step 4: write page_map.json
    print("Step 4: Writing data/page_map.json…")
    DATA_DIR.mkdir(exist_ok=True)
    page_map = {
        "meta": {
            "canonical_width":  CANONICAL_W,
            "canonical_height": CANONICAL_H,
            "brf_source":       str(BRF_PATH.relative_to(ROOT)),
            "content_lines_per_page": CONTENT_LINES,
            "grid_calibration": str(CALIB_PATH.relative_to(ROOT)),
            "note_page_marker_ids": (
                "IDs 10–11 confirmed. IDs 12–27 (pages 3–18) follow the "
                "convention ID = page_number + 9. Confirm before printing markers."
            ),
        },
        "page_marker_ids": {str(k): v for k, v in sorted(PAGE_MARKER_MAP.items())},
        "regions": full_regions,
    }
    MAP_PATH.write_text(json.dumps(page_map, indent=2))
    print(f"  Saved: {MAP_PATH}\n")

    # Step 5: overlay images
    if not args.no_overlay:
        print("Step 5: Generating overlay images…")
        pages_with_regions = sorted({r["page_number"] for r in full_regions})
        for pnum in pages_with_regions:
            page_regions = [r for r in full_regions if r["page_number"] == pnum]
            out = generate_overlay(pnum, page_regions)
            if out:
                print(f"  p{pnum:>2}: saved {out.name}")
            else:
                print(f"  p{pnum:>2}: no rectified image available — skipped")
        print()

    print("Done.")


if __name__ == "__main__":
    main()
