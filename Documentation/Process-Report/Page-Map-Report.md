# Braille Page Map — Build and Calibration Report

**Report date:** September 21, 2026

---

## 1. Objective

This report covers the construction of `data/page_map.json`, which maps every
pixel coordinate in a rectified Braille page image to its corresponding measure
number. This mapping is the link between the camera system (which produces pixel
coordinates) and the Max playback system (which takes measure numbers).

The full mapping chain is:

```
BRF source file
  └─ parse_brf()  →  line ranges per measure (source-level)
       └─ braille_grid_calibration.json  →  pixel coordinates
            └─ page_map.json  →  x1 y1 x2 y2 per region
```

---

## 2. Score structure

| Property | Value |
|----------|-------|
| Source file | `Score-prep/Score_Bars16_4-4_144bpm_braille.brf` |
| Format | ASCII Braille (BRF), SM BungSang bar-over-bar |
| Pages | 18 (form-feed separated) |
| Lines per page | 25 (lines 1–24 = content; line 25 = Braille page number) |
| Measures | 16 |

Page 1 is the title page and carries no measure regions. Measure 1 spans pages 2–3
and measure 16 spans pages 17–18; all other measures fit within a single page.

### Measure-to-page table

| Measure | Cont | Page | BRF lines |
|---------|------|------|-----------|
| 1 | 1 | 2 | 15–24 |
| 1 | 2 | 3 | 1–16 |
| 2 | 1 | 4 | 1–15 |
| 3 | 1 | 5 | 1–20 |
| 4 | 1 | 6 | 1–19 |
| 5 | 1 | 7 | 1–14 |
| 6 | 1 | 8 | 1–11 |
| 7 | 1 | 9 | 1–15 |
| 8 | 1 | 10 | 1–12 |
| 9 | 1 | 11 | 1–17 |
| 10 | 1 | 12 | 1–21 |
| 11 | 1 | 13 | 1–22 |
| 12 | 1 | 14 | 1–22 |
| 13 | 1 | 15 | 1–21 |
| 14 | 1 | 16 | 1–17 |
| 15 | 1 | 17 | 1–19 |
| 16 | 1 | 17 | 20–24 |
| 16 | 2 | 18 | 1–14 |

---

## 3. BRF parsing

### Measure token decoding

SM BungSang format uses digit-letter cells without a `#` number indicator for
inline measure numbers. The mapping is:

```
a=1  b=2  c=3  d=4  e=5  f=6  g=7  h=8  i=9  j=0
Multi-digit: place value  →  aj=10, aa=11, ab=12 …
```

A line containing only a valid digit-letter token is identified as a
measure-indicator line; the content below it (up to the next indicator or end
of page) belongs to that measure.

### Cross-page continuations

Pages 3 and 18 have no measure-indicator line — they are pure continuations of
the measure that began on the preceding page. The parser tracks `last_measure`
across pages and automatically assigns `continuation_index = 2` to these pages.

Page 17 carries two measures: M15 on lines 1–19 and M16 on lines 20–24.
This is handled by collecting all measure-indicator lines on the page and
computing the end of each from the start of the next.

---

## 4. Grid calibration

### Approach

The original calibration tool used a two-click method (click top-left, click
bottom-right of content area). This proved imprecise because the content
boundary is difficult to judge by eye in a single click.

The tool was rewritten as an interactive 40-column × 25-row Braille grid
overlay. The grid is aligned cell-by-cell rather than by outer boundary, which
gives sub-pixel accuracy for individual cell positions.

### Controls

| Key | Action |
|-----|--------|
| Arrow keys | Move grid origin |
| `[` / `]` | Decrease / increase column width |
| `-` / `=` | Decrease / increase row height |
| `S` | Save |
| `R` | Reset to defaults |
| `Q` / Esc | Quit without saving |

Row 25 is shown in orange to distinguish the Braille page-number row, which is
excluded from measure regions.

### Calibration result

Calibrated from `camera/output/page_02_snapshot_2.jpg` (canonical 1100×1700 px).

```json
{
  "x_origin":    59.0,
  "y_origin":   178.0,
  "cell_width":  23.6,
  "line_height": 50.6,
  "columns":     40,
  "rows":        25,
  "content_rows": 24
}
```

Derived values:
- Content area width: 40 × 23.6 = **944 px** (x: 59–1003)
- Content area height: 24 × 50.6 = **1214.4 px** (y: 178–1392)
- Line height 50.6 px corresponds to ~10 mm at the physical page scale,
  consistent with standard Braille inter-line spacing.

---

## 5. Build and test results

### `python3 tools/build_page_map.py`

```
Step 1: BRF verification — ALL CHECKS PASSED
  18 pages, 18 regions, measures [1–16]
  Measure 1  pages: [2, 3]  ✓
  Measure 16 pages: [17, 18]  ✓
  Title page regions: 0  ✓

Step 2: Grid calibration loaded
  x_origin=59.0  y_origin=178.0  cell_width=23.6  line_height=50.6

Steps 3–4: page_map.json written (18 regions)
Step 5: page_02_overlay.jpg generated
```

### `python3 tools/test_page_map.py`

```
Result: 10/10 tests passed

  PASS  T1  measures 1–16 all present
  PASS  T2  no y-overlap on same page
  PASS  T3  all coordinates within canonical bounds (1100×1700)
  PASS  T4  page 1 (title) has no measure regions
  PASS  T5  measure 1 spans pages [2,3] with continuation [1,2]
  PASS  T6  measure 16 spans pages [17,18] with continuation [1,2]
  PASS  T7  continuation indices sequential from 1 per measure
  PASS  T8  all required fields present with correct types
  PASS  T9  source_line_start ≤ source_line_end
  PASS  T10 source_line_end ≤ CONTENT_LINES (24)
```

---

## 6. Output files

| File | Description |
|------|-------------|
| `data/braille_grid_calibration.json` | Grid calibration (re-run if page layout changes) |
| `data/page_map.json` | 18 regions with pixel coordinates — input to real-time system |
| `camera/output/page_02_overlay.jpg` | Visual verification overlay for page 2 |

### page_map.json region format

```json
{
  "page_number":        2,
  "measure":            1,
  "continuation_index": 1,
  "source_line_start":  15,
  "source_line_end":    24,
  "page_marker_id":     11,
  "x1": 59,  "y1": 886,
  "x2": 1003, "y2": 1392
}
```

---

## 7. ArUco marker ID convention

```
page_marker_id = page_number + 9
```

| ArUco ID | Page |
|----------|------|
| 10 | 1 (title) |
| 11 | 2 |
| 12 | 3 |
| … | … |
| 27 | 18 |

IDs 10–11 are confirmed in the realtime registration code. IDs 12–27 follow
the same formula and must be confirmed when ArUco markers for pages 3–18 are
printed.

---

## 8. Tools summary

| Script | Purpose |
|--------|---------|
| `tools/build_page_map.py` | Parse BRF + calibration → `page_map.json` |
| `tools/calibrate_lines.py` | Interactive grid calibration tool |
| `tools/test_page_map.py` | 10 automated tests for `page_map.json` |
| `tools/click_test.py` | Interactive pixel→measure lookup for visual verification |
| `camera/PAGE_MAP_SOP.md` | Step-by-step SOP for regenerating the map |

---

## 9. Next steps

- Photograph pages 3–18 through the ArUco registration system to collect
  rectified snapshots for overlay verification.
- Print and confirm ArUco marker IDs 12–27 for pages 3–18; update
  `PAGE_MARKER_MAP` in `build_page_map.py` if the convention differs.
- Integrate `page_map.json` lookup into the real-time finger-tracking pipeline:
  given a rectified pixel coordinate `(x, y)` and a detected `page_marker_id`,
  look up the matching region to obtain `measure` and `continuation_index`.
