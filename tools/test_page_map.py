#!/usr/bin/env python3
"""
Automated tests for data/page_map.json.

Tests
-----
1. Measures 1–16 are all present.
2. No two regions on the same page overlap in y-coordinates.
3. All coordinates are within canonical bounds (0–1099, 0–1699).
4. Page 1 (title page) has no measure regions.
5. Measure 1 spans exactly pages [2, 3] with continuation indices [1, 2].
6. Measure 16 spans exactly pages [17, 18] with continuation indices [1, 2].
7. Continuation indices within a measure are sequential starting at 1.
8. Every region has all required fields with correct types.
9. source_line_start ≤ source_line_end for every region.
10. source_line_end ≤ CONTENT_LINES (24) for every region.

Exit 0 on all pass, 1 on any failure.

Usage
-----
    python3 tools/test_page_map.py
    python3 tools/test_page_map.py --map data/page_map.json
"""

import argparse
import json
import sys
from pathlib import Path

ROOT     = Path(__file__).parent.parent
MAP_PATH = ROOT / "data" / "page_map.json"

CANONICAL_W   = 1100
CANONICAL_H   = 1700
CONTENT_LINES = 24
TITLE_PAGE    = 1

REQUIRED_FIELDS = {
    "page_number":        int,
    "page_marker_id":     int,
    "measure":            int,
    "continuation_index": int,
    "source_line_start":  int,
    "source_line_end":    int,
    "x1": int, "y1": int,
    "x2": int, "y2": int,
}


def check(cond: bool, name: str, detail: str = "") -> bool:
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}" + (f": {detail}" if detail else ""))
    return cond


def main():
    args = parse_args()
    path = Path(args.map) if args.map else MAP_PATH

    if not path.exists():
        print(f"ERROR: {path} not found.\nRun: python3 tools/build_page_map.py",
              file=sys.stderr)
        sys.exit(1)

    data    = json.loads(path.read_text())
    regions = data.get("regions", [])
    meta    = data.get("meta", {})
    passed  = 0
    total   = 0

    def run(cond, name, detail=""):
        nonlocal passed, total
        total += 1
        if check(cond, name, detail):
            passed += 1

    print(f"=== page_map.json tests ===")
    print(f"  File    : {path}")
    print(f"  Regions : {len(regions)}\n")

    # T1: all measures 1–16 present
    found_measures = sorted({r["measure"] for r in regions})
    run(found_measures == list(range(1, 17)),
        "T1 measures 1–16 all present",
        f"found {found_measures}")

    # T2: no y-overlap on the same page
    overlap_ok = True
    by_page: dict[int, list[dict]] = {}
    for r in regions:
        by_page.setdefault(r["page_number"], []).append(r)
    for pnum, pregs in by_page.items():
        for i in range(len(pregs)):
            for j in range(i + 1, len(pregs)):
                a, b = pregs[i], pregs[j]
                if a["y1"] < b["y2"] and a["y2"] > b["y1"]:
                    overlap_ok = False
                    print(f"    overlap on page {pnum}: "
                          f"M{a['measure']} [{a['y1']}–{a['y2']}] vs "
                          f"M{b['measure']} [{b['y1']}–{b['y2']}]")
    run(overlap_ok, "T2 no y-overlap on same page")

    # T3: coordinates in bounds
    bounds_ok = all(
        0 <= r["x1"] <= r["x2"] < CANONICAL_W and
        0 <= r["y1"] <= r["y2"] < CANONICAL_H
        for r in regions
    )
    run(bounds_ok, "T3 all coordinates within canonical bounds",
        f"({CANONICAL_W}×{CANONICAL_H})")

    # T4: title page has no measure regions
    title_regions = [r for r in regions if r["page_number"] == TITLE_PAGE]
    run(len(title_regions) == 0,
        "T4 page 1 (title) has no measure regions",
        f"found {len(title_regions)}")

    # T5: measure 1 spans pages [2, 3]
    m1 = [r for r in regions if r["measure"] == 1]
    m1_pages   = [r["page_number"]        for r in m1]
    m1_conts   = [r["continuation_index"] for r in m1]
    run(m1_pages == [2, 3] and m1_conts == [1, 2],
        "T5 measure 1 spans pages [2,3] with continuation [1,2]",
        f"pages={m1_pages} conts={m1_conts}")

    # T6: measure 16 spans pages [17, 18]
    m16 = [r for r in regions if r["measure"] == 16]
    m16_pages  = [r["page_number"]        for r in m16]
    m16_conts  = [r["continuation_index"] for r in m16]
    run(m16_pages == [17, 18] and m16_conts == [1, 2],
        "T6 measure 16 spans pages [17,18] with continuation [1,2]",
        f"pages={m16_pages} conts={m16_conts}")

    # T7: continuation indices per measure are sequential from 1
    cont_ok = True
    for m in range(1, 17):
        mrs = [r for r in regions if r["measure"] == m]
        conts = [r["continuation_index"] for r in mrs]
        if conts != list(range(1, len(conts) + 1)):
            cont_ok = False
            print(f"    measure {m}: continuation indices {conts} not sequential from 1")
    run(cont_ok, "T7 continuation indices sequential from 1 per measure")

    # T8: required fields with correct types
    fields_ok = True
    for r in regions:
        for field, ftype in REQUIRED_FIELDS.items():
            if field not in r:
                fields_ok = False
                print(f"    missing field '{field}' in region {r}")
                break
            if not isinstance(r[field], ftype):
                fields_ok = False
                print(f"    field '{field}' wrong type: {type(r[field])} (expected {ftype})")
    run(fields_ok, "T8 all required fields present with correct types")

    # T9: source_line_start ≤ source_line_end
    line_order_ok = all(r["source_line_start"] <= r["source_line_end"] for r in regions)
    run(line_order_ok, "T9 source_line_start ≤ source_line_end")

    # T10: source_line_end ≤ CONTENT_LINES
    line_bound_ok = all(r["source_line_end"] <= CONTENT_LINES for r in regions)
    run(line_bound_ok, "T10 source_line_end ≤ CONTENT_LINES (24)",
        f"CONTENT_LINES={CONTENT_LINES}")

    print(f"\n{'='*40}")
    print(f"Result: {passed}/{total} tests passed")

    sys.exit(0 if passed == total else 1)


def parse_args():
    p = argparse.ArgumentParser(description="Test data/page_map.json")
    p.add_argument("--map", help="Path to page_map.json (default: data/page_map.json)")
    return p.parse_args()


if __name__ == "__main__":
    main()
