"""
ArUco page registration — detects frame markers (ID 0-3) and page marker (ID 10),
computes homography, and rectifies the page to a canonical 1100×1700 px image.

Usage:
    python3 aruco_page_registration.py [image1 image2 ...]

Default: process all page*_test*.jpg images in ../Figure/
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

# ── constants ────────────────────────────────────────────────────────────────

DICT_ID = cv2.aruco.DICT_4X4_50
FRAME_IDS = [0, 1, 2, 3]   # TL, TR, BR, BL
PAGE_ID = 10                # identifies Page 1
OUT_W, OUT_H = 1100, 1700   # rectified output size

# Inner corner index for each frame marker (corners order: TL=0, TR=1, BR=2, BL=3)
# The "inner" corner is the one facing toward the page interior.
INNER_CORNER = {
    0: 2,   # ID 0 (top-left marker)     → bottom-right corner
    1: 3,   # ID 1 (top-right marker)    → bottom-left corner
    2: 0,   # ID 2 (bottom-right marker) → top-left corner
    3: 1,   # ID 3 (bottom-left marker)  → top-right corner
}

# Corresponding destination corners in the rectified image
DST_CORNERS = np.float32([
    [0,        0],        # ID 0 inner → page top-left
    [OUT_W-1,  0],        # ID 1 inner → page top-right
    [OUT_W-1,  OUT_H-1],  # ID 2 inner → page bottom-right
    [0,        OUT_H-1],  # ID 3 inner → page bottom-left
])

# ── detection ────────────────────────────────────────────────────────────────

def detect_markers(img):
    """Run ArUco detection; return (corners_list, ids_array)."""
    aruco_dict = cv2.aruco.getPredefinedDictionary(DICT_ID)
    params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, params)
    corners, ids, _ = detector.detectMarkers(img)
    return corners, ids


def build_id_map(corners, ids):
    """Map each detected marker ID → its corners array (shape 4×2).

    OpenCV 5 returns ids with shape (n,); older versions return (n,1).
    Normalise by flattening before indexing.
    """
    if ids is None:
        return {}
    flat_ids = ids.flatten()
    return {int(flat_ids[i]): corners[i][0] for i in range(len(flat_ids))}

# ── annotation ───────────────────────────────────────────────────────────────

def annotate(img, corners, ids, id_map):
    """Draw markers, label IDs, and connect frame quad with green lines."""
    out = img.copy()

    # Draw all detected markers (blue border)
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(out, corners, ids)

    # Label each marker ID at its center
    for mid, c in id_map.items():
        cx, cy = c.mean(axis=0).astype(int)
        cv2.putText(out, str(mid), (cx - 10, cy + 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Green quad connecting inner corners of frame markers 0–3
    if all(fid in id_map for fid in FRAME_IDS):
        quad = np.int32([id_map[fid][INNER_CORNER[fid]] for fid in FRAME_IDS])
        cv2.polylines(out, [quad], isClosed=True, color=(0, 255, 0), thickness=2)

    return out

# ── homography & rectification ───────────────────────────────────────────────

def rectify(img, id_map):
    """
    Compute homography from the 4 inner frame-marker corners and warp the page.
    Returns the rectified image, or None if frame markers are incomplete.
    """
    missing = [fid for fid in FRAME_IDS if fid not in id_map]
    if missing:
        return None, missing

    src = np.float32([id_map[fid][INNER_CORNER[fid]] for fid in FRAME_IDS])
    H, _ = cv2.findHomography(src, DST_CORNERS)
    rectified = cv2.warpPerspective(img, H, (OUT_W, OUT_H))
    return rectified, []

# ── per-image processing ─────────────────────────────────────────────────────

def process_one(img_path: Path, out_dir: Path):
    """Load, detect, annotate, and rectify a single image. Print results."""
    print(f"\n── {img_path.name} ──")

    img = cv2.imread(str(img_path))
    if img is None:
        print(f"  ERROR: cv2.imread failed to read: {img_path}", file=sys.stderr)
        return

    # Detect
    corners, ids = detect_markers(img)
    id_map = build_id_map(corners, ids)

    detected_ids = sorted(id_map.keys())
    print(f"  Detected marker IDs : {detected_ids}")

    # Frame markers check
    missing_frame = [fid for fid in FRAME_IDS if fid not in id_map]
    if missing_frame:
        print(f"  Frame IDs 0-3 present: NO  — missing: {missing_frame}")
    else:
        print("  Frame IDs 0-3 present: YES")

    # Page marker check
    print(f"  Page ID {PAGE_ID} present : {'YES' if PAGE_ID in id_map else 'NO'}")

    stem = img_path.stem

    # Annotated image
    annotated = annotate(img, corners, ids, id_map)
    ann_path = out_dir / f"{stem}_annotated.jpg"
    cv2.imwrite(str(ann_path), annotated)
    print(f"  Saved annotated      : {ann_path}")

    # Rectified page
    if missing_frame:
        print(f"  Page registration    : FAILED — missing frame markers {missing_frame}")
    else:
        rectified, _ = rectify(img, id_map)
        rect_path = out_dir / f"{stem}_rectified.jpg"
        cv2.imwrite(str(rect_path), rectified)
        print(f"  Saved rectified      : {rect_path}")
        print("  Page registration    : OK")


# ── main ─────────────────────────────────────────────────────────────────────

def parse_args():
    script_dir = Path(__file__).parent
    figure_dir = script_dir / ".." / "Figure"

    parser = argparse.ArgumentParser(description="ArUco page registration")
    parser.add_argument("images", nargs="*",
                        help="Image paths to process (default: all images in ../Figure/)")
    return parser.parse_args(), figure_dir


def main():
    args, figure_dir = parse_args()

    if args.images:
        img_paths = [Path(p).resolve() for p in args.images]
    else:
        # Default: all jpg images in ../Figure/, sorted by name
        img_paths = sorted(figure_dir.resolve().glob("*.jpg"))

    if not img_paths:
        print("ERROR: no images found.", file=sys.stderr)
        sys.exit(1)

    # Validate all paths before processing
    missing = [p for p in img_paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"ERROR: image not found: {p}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)

    for img_path in img_paths:
        process_one(img_path, out_dir)


if __name__ == "__main__":
    main()
