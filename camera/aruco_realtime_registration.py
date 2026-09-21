"""
ArUco realtime page registration with locked homography.

States:
  WAITING_FOR_PAGE  — looking for a page marker (any non-frame ID) for 10 consecutive frames
  CALIBRATING       — collecting 15 frames of frame-marker corners for median calibration
  LOCKED            — using locked homography; markers may be occluded

Usage:
    python3 aruco_realtime_registration.py                  # interactive camera selection
    python3 aruco_realtime_registration.py --camera 2       # direct selection
    python3 aruco_realtime_registration.py --list-cameras   # list cameras and exit

Keys:
    R       — force recalibration (return to WAITING_FOR_PAGE)
    Q / Esc — quit
"""

import argparse
import sys
import time

import cv2
import numpy as np

# ── constants ─────────────────────────────────────────────────────────────────

DICT_ID      = cv2.aruco.DICT_4X4_50
FRAME_IDS    = [0, 1, 2, 3]   # TL, TR, BR, BL
OUT_W, OUT_H = 1100, 1700
SCAN_RANGE   = range(11)       # probe indices 0–10

# Inner corner of each frame marker facing the page interior
# Corners returned by ArUco: [TL=0, TR=1, BR=2, BL=3]
INNER_CORNER = {
    0: 2,   # top-left marker     → bottom-right corner
    1: 3,   # top-right marker    → bottom-left corner
    2: 0,   # bottom-right marker → top-left corner
    3: 1,   # bottom-left marker  → top-right corner
}

DST_CORNERS = np.float32([
    [0,        0],
    [OUT_W-1,  0],
    [OUT_W-1,  OUT_H-1],
    [0,        OUT_H-1],
])

DISPLAY_MAX_H       = 720   # max display height; computation always uses full resolution
PAGE_CONFIRM_FRAMES = 10    # consecutive frames required to confirm a page ID
CALIB_FRAMES        = 15    # frames collected for median corner calibration

# State names
WAITING_FOR_PAGE = "WAITING_FOR_PAGE"
CALIBRATING      = "CALIBRATING"
LOCKED           = "LOCKED"

# ── ArUco helpers ─────────────────────────────────────────────────────────────

def make_detector():
    """Create ArucoDetector once; reuse across frames."""
    aruco_dict = cv2.aruco.getPredefinedDictionary(DICT_ID)
    params     = cv2.aruco.DetectorParameters()
    return cv2.aruco.ArucoDetector(aruco_dict, params)


def get_page_id(id_map):
    """Return the first detected marker ID that is not a frame marker, or None."""
    for mid in id_map:
        if mid not in FRAME_IDS:
            return mid
    return None


def compute_locked_homography(calib_buffer):
    """
    Compute H from the median of collected corner sets.
    calib_buffer: list of np.float32 arrays, each shape (4, 2).
    Returns H matrix.
    """
    stacked    = np.array(calib_buffer, dtype=np.float32)  # (N, 4, 2)
    median_src = np.median(stacked, axis=0).astype(np.float32)  # (4, 2)
    H, _       = cv2.findHomography(median_src, DST_CORNERS)
    return H

# ── camera scanning ───────────────────────────────────────────────────────────

def scan_cameras():
    """Probe indices 0–10 via CAP_AVFOUNDATION; return list of info dicts."""
    available = []
    print("Scanning cameras 0–10…")
    for idx in SCAN_RANGE:
        cap = cv2.VideoCapture(idx, cv2.CAP_AVFOUNDATION)
        if not cap.isOpened():
            cap.release()
            continue
        ok, _ = cap.read()
        if not ok:
            cap.release()
            continue
        w       = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        backend = cap.getBackendName()
        cap.release()
        available.append({"index": idx, "w": w, "h": h, "backend": backend})
    return available


def print_camera_list(cameras):
    print("\nAvailable cameras:\n")
    for cam in cameras:
        print(f"  [{cam['index']}] {cam['w']} \u00d7 {cam['h']} \u2014 {cam['backend']}")
    print()


def no_cameras_error():
    print("ERROR: no cameras detected.", file=sys.stderr)
    print("\nTroubleshooting checklist:", file=sys.stderr)
    print("  \u2022 iPhone Continuity Camera:", file=sys.stderr)
    print("    Settings \u2192 General \u2192 AirPlay & Handoff \u2192 Continuity Camera Webcam \u2192 ON", file=sys.stderr)
    print("  \u2022 iPhone and Mac must be signed in to the same Apple Account", file=sys.stderr)
    print("  \u2022 Both Wi-Fi and Bluetooth must be enabled on both devices", file=sys.stderr)
    print("  \u2022 Terminal (or Python) must have Camera permission:", file=sys.stderr)
    print("    System Settings \u2192 Privacy & Security \u2192 Camera", file=sys.stderr)

# ── camera selection ──────────────────────────────────────────────────────────

def select_camera_interactive(cameras):
    """Prompt user to pick a camera index; retry on invalid input."""
    valid = {cam["index"] for cam in cameras}
    while True:
        try:
            raw = input("Select camera index: ").strip()
            idx = int(raw)
        except (ValueError, EOFError):
            print("  Invalid input \u2014 enter a number shown in the list above.")
            continue
        if idx in valid:
            return idx
        print(f"  {idx} is not in the list above \u2014 try again.")


def open_camera(idx):
    """Open camera at idx via CAP_AVFOUNDATION; return cap or None."""
    cap = cv2.VideoCapture(idx, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        return None
    ok, _ = cap.read()
    if not ok:
        cap.release()
        return None
    return cap

# ── display helpers ───────────────────────────────────────────────────────────

def scale_for_display(img):
    """Scale image so height ≤ DISPLAY_MAX_H; never upscale."""
    h, w = img.shape[:2]
    if h <= DISPLAY_MAX_H:
        return img
    scale = DISPLAY_MAX_H / h
    return cv2.resize(img, (int(w * scale), DISPLAY_MAX_H))


def draw_overlay(frame, id_map, fps,
                 state, confirmed_page_id,
                 page_streak, calib_progress, missing_frame):
    """
    Draw on a copy of frame:
      - marker borders (yellow) and ID labels (red)
      - green page quad when all frame markers visible
      - status panel (top-left): page, state, IDs, missing, calibration progress, FPS
    """
    out = frame.copy()

    # Marker borders and labels
    for mid, c in id_map.items():
        pts = c.astype(int)
        cv2.polylines(out, [pts], isClosed=True, color=(0, 200, 255), thickness=2)
        cx, cy = pts.mean(axis=0).astype(int)
        cv2.putText(out, str(mid), (cx - 10, cy + 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 220), 2)

    # Green quad when all frame markers present
    if not missing_frame:
        quad = np.int32([id_map[fid][INNER_CORNER[fid]] for fid in FRAME_IDS])
        cv2.polylines(out, [quad], isClosed=True, color=(0, 255, 0), thickness=2)

    # Status strings
    page_label = f"Page {confirmed_page_id}" if confirmed_page_id is not None \
                 else "Page: ---"

    if state == WAITING_FOR_PAGE:
        state_str   = f"WAITING FOR PAGE  ({page_streak}/{PAGE_CONFIRM_FRAMES})"
        state_color = (0, 160, 255)
    elif state == CALIBRATING:
        done        = calib_progress if calib_progress is not None else 0
        state_str   = f"CALIBRATING  ({done}/{CALIB_FRAMES})"
        state_color = (0, 220, 255)
    else:  # LOCKED
        state_str   = "LOCKED"
        state_color = (0, 255, 80)

    detected_ids  = sorted(id_map.keys())
    frame_ok      = not missing_frame
    frame_color   = (0, 255, 0) if frame_ok else (0, 80, 255)
    frame_str     = "Frame 0-3: OK" if frame_ok \
                    else f"Frame 0-3: LOST  missing={missing_frame}"

    lines = [
        (page_label,                  (200, 200, 200)),
        (state_str,                   state_color),
        (f"IDs: {detected_ids}",      (200, 200, 200)),
        (frame_str,                   frame_color),
        (f"FPS: {fps:.1f}",           (180, 180, 180)),
    ]
    y = 28
    for text, color in lines:
        cv2.putText(out, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        y += 26

    return out

# ── realtime loop ─────────────────────────────────────────────────────────────

def run_realtime(cap, camera_idx):
    detector = make_detector()

    # Placeholder shown when locked_H is not available
    blank = np.full((OUT_H, OUT_W, 3), 30, dtype=np.uint8)
    cv2.putText(blank, "Waiting for calibration…", (60, OUT_H // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (100, 100, 100), 2)

    # ── state machine variables ───────────────────────────────────────────────
    state               = WAITING_FOR_PAGE
    confirmed_page_id   = None    # page ID currently locked to
    locked_H            = None    # the locked homography matrix
    calib_buffer        = []      # list of (4,2) src corner arrays
    candidate_page_id   = None    # page ID being watched for confirmation
    page_streak         = 0       # consecutive frames of candidate_page_id
    diff_page_streak    = 0       # consecutive frames of different page ID (in LOCKED)
    recal_count         = 0

    # ── stats ─────────────────────────────────────────────────────────────────
    total_frames         = 0
    frame_visible_frames = 0   # frames where all 4 frame markers were detected
    locked_usable_frames = 0   # frames where locked_H was used for warp
    fps                  = 0.0
    t_start              = time.perf_counter()
    t_prev               = t_start

    print(f"\nCamera {camera_idx} opened.  R = recalibrate  |  Q / Esc = quit\n")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("WARNING: failed to read frame.", file=sys.stderr)
            continue

        total_frames += 1

        t_now  = time.perf_counter()
        fps    = 1.0 / max(t_now - t_prev, 1e-9)
        t_prev = t_now

        # Detect on full-resolution frame — no flip
        corners, ids, _ = detector.detectMarkers(frame)
        ids = ids.flatten() if ids is not None else np.array([], dtype=int)
        id_map = {int(ids[i]): corners[i][0] for i in range(len(ids))}

        missing_frame      = [fid for fid in FRAME_IDS if fid not in id_map]
        all_frame_visible  = len(missing_frame) == 0
        detected_page_id   = get_page_id(id_map)

        if all_frame_visible:
            frame_visible_frames += 1

        # ── state machine ─────────────────────────────────────────────────────

        if state == WAITING_FOR_PAGE:
            if detected_page_id is not None:
                if detected_page_id == candidate_page_id:
                    page_streak += 1
                else:
                    candidate_page_id = detected_page_id
                    page_streak       = 1
                if page_streak >= PAGE_CONFIRM_FRAMES:
                    confirmed_page_id = candidate_page_id
                    calib_buffer      = []
                    page_streak       = 0
                    state             = CALIBRATING
                    print(f"  Page {confirmed_page_id} confirmed → CALIBRATING")
            else:
                page_streak = 0

        elif state == CALIBRATING:
            # Collect frames only when all 4 frame markers are visible
            if all_frame_visible:
                src = np.float32([id_map[fid][INNER_CORNER[fid]] for fid in FRAME_IDS])
                calib_buffer.append(src)

            if len(calib_buffer) >= CALIB_FRAMES:
                locked_H    = compute_locked_homography(calib_buffer)
                recal_count += 1
                state        = LOCKED
                diff_page_streak = 0
                print(f"  Homography locked — page {confirmed_page_id}  "
                      f"(calibration #{recal_count})")

        elif state == LOCKED:
            # Watch for a different page ID appearing consistently
            if detected_page_id is not None and detected_page_id != confirmed_page_id:
                diff_page_streak += 1
                if diff_page_streak >= PAGE_CONFIRM_FRAMES:
                    # New page confirmed — pause output and recalibrate
                    confirmed_page_id = detected_page_id
                    locked_H          = None
                    calib_buffer      = []
                    diff_page_streak  = 0
                    state             = CALIBRATING
                    print(f"  New page {confirmed_page_id} detected → recalibrating")
            else:
                # Same page or page temporarily absent — keep locked homography
                diff_page_streak = 0

        # ── key handling ──────────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), ord('Q'), 27):
            break
        if key in (ord('r'), ord('R')):
            state             = WAITING_FOR_PAGE
            confirmed_page_id = None
            locked_H          = None
            calib_buffer      = []
            candidate_page_id = None
            page_streak       = 0
            diff_page_streak  = 0
            print("  R pressed → forced recalibration")

        # ── display ───────────────────────────────────────────────────────────
        if locked_H is not None:
            locked_usable_frames += 1
            rectified = cv2.warpPerspective(frame, locked_H, (OUT_W, OUT_H))
            cv2.imshow("Rectified Page", scale_for_display(rectified))
        else:
            cv2.imshow("Rectified Page", scale_for_display(blank))

        calib_progress = len(calib_buffer) if state == CALIBRATING else None
        annotated = draw_overlay(
            frame, id_map, fps,
            state, confirmed_page_id,
            page_streak, calib_progress, missing_frame,
        )
        cv2.imshow("ArUco Registration", scale_for_display(annotated))

    # ── cleanup ───────────────────────────────────────────────────────────────
    cap.release()
    cv2.destroyAllWindows()

    elapsed  = max(time.perf_counter() - t_start, 1e-9)
    avg_fps  = total_frames / elapsed
    vis_rate = frame_visible_frames / max(total_frames, 1) * 100
    use_rate = locked_usable_frames / max(total_frames, 1) * 100

    print("\n── Session summary ────────────────────────────────")
    print(f"  Total frames              : {total_frames}")
    print(f"  Frame-marker visibility   : {frame_visible_frames} frames  ({vis_rate:.1f}%)")
    print(f"  Locked-homography usable  : {locked_usable_frames} frames  ({use_rate:.1f}%)")
    print(f"  Recalibration count       : {recal_count}")
    print(f"  Average FPS               : {avg_fps:.1f}")

# ── argument parsing & main ───────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="ArUco realtime page registration")
    group  = parser.add_mutually_exclusive_group()
    group.add_argument("--camera", type=int, metavar="INDEX",
                       help="Use this camera index directly (skip interactive selection)")
    group.add_argument("--list-cameras", action="store_true",
                       help="List available cameras and exit")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.list_cameras:
        cameras = scan_cameras()
        if not cameras:
            no_cameras_error()
            sys.exit(1)
        print_camera_list(cameras)
        sys.exit(0)

    if args.camera is not None:
        cap = open_camera(args.camera)
        if cap is None:
            print(f"ERROR: cannot open camera {args.camera}.", file=sys.stderr)
            sys.exit(1)
        run_realtime(cap, args.camera)
        return

    cameras = scan_cameras()
    if not cameras:
        no_cameras_error()
        sys.exit(1)
    print_camera_list(cameras)
    idx = select_camera_interactive(cameras)
    cap = open_camera(idx)
    if cap is None:
        print(f"ERROR: failed to open camera {idx} after selection.", file=sys.stderr)
        sys.exit(1)
    run_realtime(cap, idx)


if __name__ == "__main__":
    main()
