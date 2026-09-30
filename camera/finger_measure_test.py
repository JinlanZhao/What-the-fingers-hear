#!/usr/bin/env python3
"""
Fingertip-to-measure test.

Combines ArUco page registration with MediaPipe hand landmark detection.
Index fingertip (landmark 8) is projected via the locked homography into
canonical 1100×1700 coordinates and looked up in data/page_map.json.
On measure change, sends an OSC message to Max for audio playback.

Status shown on screen
----------------------
  WAITING        — homography not yet locked
  NO_HAND        — locked, no hand detected this frame
  OUTSIDE_PAGE   — fingertip not over any measure region
  MEASURE N      — fingertip on measure N  (cont C if continuation_index > 1)

OSC output (127.0.0.1:7400)
---------------------------
  /bar  <int N>   — finger entered measure N; Max should play bars N→16
  /stop           — finger left all measure regions (NO_HAND or OUTSIDE_PAGE)

Keys
----
  R       — force recalibration
  Q / Esc — quit

Usage
-----
    python3 camera/finger_measure_test.py
    python3 camera/finger_measure_test.py --camera 0
    python3 camera/finger_measure_test.py --list-cameras
    python3 camera/finger_measure_test.py --test    # pure-function tests, no camera

MediaPipe model
---------------
    data/hand_landmarker.task   (downloaded separately — see README)
    API: mediapipe 0.10.35  →  mediapipe.tasks.python.vision.hand_landmarker
         HandLandmarker, VIDEO running mode, CPU delegate
"""

import argparse
import json
import sys
import time
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from pythonosc.udp_client import SimpleUDPClient

# ── import shared registration code (camera/aruco_realtime_registration.py) ───
sys.path.insert(0, str(Path(__file__).parent))
from aruco_realtime_registration import (   # noqa: E402
    make_detector,
    get_page_id,
    page_label,
    compute_locked_homography,
    scan_cameras,
    print_camera_list,
    no_cameras_error,
    select_camera_interactive,
    open_camera,
    scale_for_display,
    FRAME_IDS,
    OUT_W, OUT_H,
    INNER_CORNER,
    PAGE_CONFIRM_FRAMES,
    CALIB_FRAMES,
    WAITING_FOR_PAGE,
    CALIBRATING,
    LOCKED,
)

ROOT                 = Path(__file__).parent.parent
MAP_PATH             = ROOT / "data" / "page_map.json"
MODEL_PATH           = ROOT / "data" / "hand_landmarker.task"
GESTURE_MODEL_PATH   = ROOT / "data" / "gesture_recognizer.task"
BAR_TIMES_PATH       = ROOT / "data" / "bar_times.json"

OSC_HOST = "127.0.0.1"
OSC_PORT = 7400

FINGERTIP_IDX        = 8    # MediaPipe index-finger tip landmark
GESTURE_DWELL_FRAMES   = 10   # frames a gesture must be held before triggering
GESTURE_MIN_CONFIDENCE = 0.30 # minimum score to accept a gesture

# ── page map ──────────────────────────────────────────────────────────────────

def load_page_map() -> list[dict]:
    if not MAP_PATH.exists():
        print(f"ERROR: {MAP_PATH} not found.\nRun: python3 tools/build_page_map.py",
              file=sys.stderr)
        sys.exit(1)
    return json.loads(MAP_PATH.read_text())["regions"]


def lookup_region(regions: list[dict],
                  page_marker_id: int,
                  cx: int, cy: int) -> dict | None:
    """Return the first region on this page that contains (cx, cy), or None."""
    for r in regions:
        if r["page_marker_id"] != page_marker_id:
            continue
        if r["x1"] <= cx <= r["x2"] and r["y1"] <= cy <= r["y2"]:
            return r
    return None

# ── MediaPipe ─────────────────────────────────────────────────────────────────

def make_gesture_recognizer():
    """Create a GestureRecognizer in VIDEO mode (replaces HandLandmarker).
    Returns both gesture category and hand landmarks per frame.
    """
    from mediapipe.tasks.python.vision.gesture_recognizer import (
        GestureRecognizer, GestureRecognizerOptions,
    )
    from mediapipe.tasks.python.core.base_options import BaseOptions
    from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
        VisionTaskRunningMode,
    )
    if not GESTURE_MODEL_PATH.exists():
        print(f"ERROR: gesture model not found: {GESTURE_MODEL_PATH}", file=sys.stderr)
        sys.exit(1)
    opts = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path=str(GESTURE_MODEL_PATH)),
        running_mode=VisionTaskRunningMode.VIDEO,
        num_hands=1,
    )
    return GestureRecognizer.create_from_options(opts)


def get_gesture(result) -> str | None:
    """Return gesture category name if confidence ≥ GESTURE_MIN_CONFIDENCE, else None.
    Used for Open_Palm (stop) detection only.
    """
    if not result.gestures:
        return None
    cat = result.gestures[0][0]
    if cat.score < GESTURE_MIN_CONFIDENCE:
        return None
    return cat.category_name


def fingertip_camera_px(result,
                        frame_w: int,
                        frame_h: int) -> tuple[int, int] | None:
    """
    Extract index fingertip (landmark 8) in camera pixel coords.
    Returns (x, y) or None if no hand detected.
    """
    if not result.hand_landmarks:
        return None
    lm = result.hand_landmarks[0][FINGERTIP_IDX]
    return int(lm.x * frame_w), int(lm.y * frame_h)


def canonical_coords(cam_pt: tuple[int, int],
                     H: np.ndarray) -> tuple[int, int]:
    """
    Transform a single camera pixel coordinate to canonical page coords via H.
    Returns (cx, cy) as ints.
    """
    src = np.float32([[[cam_pt[0], cam_pt[1]]]])
    dst = cv2.perspectiveTransform(src, H)
    return int(dst[0][0][0]), int(dst[0][0][1])

# ── display helpers ───────────────────────────────────────────────────────────

def _status(state, fingertip_px, region) -> tuple[str, tuple]:
    """Return (status_text, BGR_color)."""
    if state != LOCKED:
        return "WAITING", (0, 160, 255)
    if fingertip_px is None:
        return "NO_HAND", (120, 120, 120)
    if region is None:
        return "OUTSIDE_PAGE", (0, 80, 255)
    label = f"MEASURE {region['measure']}"
    if region["continuation_index"] > 1:
        label += f"  cont {region['continuation_index']}"
    return label, (0, 255, 80)


def _draw_camera_frame(frame, mp_result, id_map, fingertip_px,
                       canon_pt, state, region, fps, gesture=None) -> np.ndarray:
    out = frame.copy()

    # Hand landmarks
    if mp_result.hand_landmarks:
        fh, fw = frame.shape[:2]
        for lm in mp_result.hand_landmarks[0]:
            cv2.circle(out, (int(lm.x * fw), int(lm.y * fh)), 3, (160, 160, 0), -1)

    # Fingertip highlight
    if fingertip_px is not None:
        cv2.circle(out, fingertip_px, 10, (0, 255, 255), 2)
        cv2.drawMarker(out, fingertip_px, (0, 255, 255), cv2.MARKER_CROSS, 20, 2)

    # ArUco borders and IDs
    for mid, c in id_map.items():
        pts = c.astype(int)
        cv2.polylines(out, [pts], isClosed=True, color=(0, 200, 255), thickness=2)
        cx_m, cy_m = pts.mean(axis=0).astype(int)
        cv2.putText(out, str(mid), (cx_m - 10, cy_m + 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 220), 2)

    # Green page quad when all frame markers visible
    missing = [fid for fid in FRAME_IDS if fid not in id_map]
    if not missing:
        quad = np.int32([id_map[fid][INNER_CORNER[fid]] for fid in FRAME_IDS])
        cv2.polylines(out, [quad], isClosed=True, color=(0, 255, 0), thickness=2)

    # Status panel
    status_str, status_color = _status(state, fingertip_px, region)
    lines: list[tuple[str, tuple]] = [
        (status_str, status_color),
    ]
    if fingertip_px is not None:
        lines.append((f"cam ({fingertip_px[0]}, {fingertip_px[1]})", (160, 160, 0)))
    if canon_pt is not None:
        lines.append((f"canon ({canon_pt[0]}, {canon_pt[1]})", (0, 200, 255)))
    if gesture:
        lines.append((f"gesture: {gesture}", (200, 100, 255)))
    lines.append((f"FPS {fps:.1f}", (150, 150, 150)))

    y = 28
    for text, color in lines:
        cv2.putText(out, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.62, color, 2)
        y += 27

    return out


def _draw_canonical(rectified, canon_pt, region) -> np.ndarray:
    out = rectified.copy()

    # Matched region highlight
    if region is not None:
        cv2.rectangle(out, (region["x1"], region["y1"]),
                      (region["x2"], region["y2"]), (0, 255, 80), 3)
        cv2.putText(out,
                    f"M{region['measure']}  cont{region['continuation_index']}",
                    (region["x1"] + 6, region["y1"] + 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 80), 2)

    # Fingertip dot
    if canon_pt is not None:
        cv2.circle(out, canon_pt, 12, (0, 255, 255), 2)
        cv2.drawMarker(out, canon_pt, (0, 255, 255), cv2.MARKER_CROSS, 24, 2)
        cv2.putText(out, f"({canon_pt[0]}, {canon_pt[1]})",
                    (canon_pt[0] + 15, canon_pt[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    return out

# ── main loop ─────────────────────────────────────────────────────────────────

def run(cap, camera_idx: int):
    regions    = load_page_map()
    detector   = make_detector()
    recognizer = make_gesture_recognizer()
    osc_client = SimpleUDPClient(OSC_HOST, OSC_PORT)
    print(f"  OSC → {OSC_HOST}:{OSC_PORT}")

    blank = np.full((OUT_H, OUT_W, 3), 30, dtype=np.uint8)
    cv2.putText(blank, "Waiting for calibration…", (60, OUT_H // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (100, 100, 100), 2)

    # State machine — same protocol as aruco_realtime_registration
    state             = WAITING_FOR_PAGE
    confirmed_page_id = None
    locked_H          = None
    calib_buffer: list[np.ndarray] = []
    candidate_page_id = None
    page_streak       = 0
    diff_page_streak  = 0
    recal_count       = 0

    last_pointed_measure: int | None = None  # last measure seen under Pointing_Up
    gesture_being_held:  str | None = None  # gesture currently accumulating dwell
    gesture_dwell_count: int        = 0     # consecutive frames of gesture_being_held

    fps    = 0.0
    t_prev = time.perf_counter()

    print(f"\nCamera {camera_idx} opened.  R = recalibrate  |  Q / Esc = quit\n")

    while True:
        ok, frame = cap.read()
        if not ok:
            continue

        t_now       = time.perf_counter()
        fps         = 1.0 / max(t_now - t_prev, 1e-9)
        t_prev      = t_now
        timestamp_ms = int(t_now * 1000)   # monotonic ms for MediaPipe VIDEO mode

        fh, fw = frame.shape[:2]

        # ── ArUco detection ───────────────────────────────────────────────────
        corners, ids, _ = detector.detectMarkers(frame)
        ids    = ids.flatten() if ids is not None else np.array([], dtype=int)
        id_map = {int(ids[i]): corners[i][0] for i in range(len(ids))}

        all_frame_vis    = all(fid in id_map for fid in FRAME_IDS)
        detected_page_id = get_page_id(id_map)

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
                    print(f"  {page_label(confirmed_page_id)} confirmed → CALIBRATING")
            else:
                page_streak = 0

        elif state == CALIBRATING:
            if all_frame_vis:
                src = np.float32([id_map[fid][INNER_CORNER[fid]] for fid in FRAME_IDS])
                calib_buffer.append(src)
            if len(calib_buffer) >= CALIB_FRAMES:
                locked_H         = compute_locked_homography(calib_buffer)
                recal_count     += 1
                state            = LOCKED
                diff_page_streak = 0
                print(f"  Homography locked — {page_label(confirmed_page_id)}  "
                      f"(calibration #{recal_count})")

        elif state == LOCKED:
            if detected_page_id is not None and detected_page_id != confirmed_page_id:
                diff_page_streak += 1
                if diff_page_streak >= PAGE_CONFIRM_FRAMES:
                    confirmed_page_id = detected_page_id
                    locked_H          = None
                    calib_buffer      = []
                    diff_page_streak  = 0
                    state             = CALIBRATING
                    print(f"  {page_label(confirmed_page_id)} detected → recalibrating")
            else:
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
            print("  R → recalibrating")

        # ── MediaPipe gesture + landmark detection ────────────────────────────
        mp_img = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
        )
        mp_result    = recognizer.recognize_for_video(mp_img, timestamp_ms)
        gesture      = get_gesture(mp_result)
        fingertip_px = fingertip_camera_px(mp_result, fw, fh)

        # ── fingertip → canonical → region ───────────────────────────────────
        canon_pt = None
        region   = None
        if state == LOCKED and locked_H is not None and fingertip_px is not None:
            canon_pt = canonical_coords(fingertip_px, locked_H)
            region   = lookup_region(regions, confirmed_page_id,
                                     canon_pt[0], canon_pt[1])

        # ── track last pointed measure (gesture-independent) ─────────────────
        # Updated whenever the fingertip is over any measure region, regardless
        # of which gesture is active.  Cleared only when hand leaves frame.
        if region is not None:
            last_pointed_measure = region["measure"]
        elif not mp_result.hand_landmarks:
            last_pointed_measure = None   # hand left frame

        # ── resolve effective gesture ─────────────────────────────────────────
        # Both triggers use the GestureRecognizer model output directly:
        #   Closed_Fist → play from last_pointed_measure
        #   Open_Palm   → stop
        if gesture == "Closed_Fist":
            effective_gesture = "Closed_Fist"
        elif gesture == "Open_Palm":
            effective_gesture = "Open_Palm"
        else:
            effective_gesture = None

        # ── OSC output (LOCKED only; must hold GESTURE_DWELL_FRAMES) ─────────
        if state == LOCKED:
            if effective_gesture == gesture_being_held:
                gesture_dwell_count += 1
            else:
                gesture_being_held  = effective_gesture
                gesture_dwell_count = 1

            if gesture_dwell_count == GESTURE_DWELL_FRAMES:
                if effective_gesture == "Closed_Fist" and last_pointed_measure is not None:
                    # Stop first so Max seeks to the new position rather than
                    # updating the variable while the previous playback is running.
                    osc_client.send_message("/stop", [])
                    osc_client.send_message("/bar", last_pointed_measure)
                    print(f"  OSC /stop + /bar {last_pointed_measure}  [Closed_Fist]")
                elif effective_gesture == "Open_Palm":
                    osc_client.send_message("/stop", [])
                    print("  OSC /stop  [Open_Palm]")
        else:
            gesture_being_held  = None
            gesture_dwell_count = 0

        # ── display ───────────────────────────────────────────────────────────
        cam_disp = _draw_camera_frame(
            frame, mp_result, id_map, fingertip_px,
            canon_pt, state, region, fps, effective_gesture,
        )
        cv2.imshow("Finger Measure Test", scale_for_display(cam_disp))

        if locked_H is not None:
            rectified  = cv2.warpPerspective(frame, locked_H, (OUT_W, OUT_H))
            canon_disp = _draw_canonical(rectified, canon_pt, region)
        else:
            canon_disp = blank.copy()
        cv2.imshow("Canonical Page", scale_for_display(canon_disp))

    cap.release()
    recognizer.close()
    cv2.destroyAllWindows()

# ── pure-function tests (no camera) ──────────────────────────────────────────

def _run_tests():
    """Run pure-function tests. Exit 0 if all pass, 1 if any fail."""
    passed = 0
    total  = 0

    def check(cond: bool, name: str, detail: str = ""):
        nonlocal passed, total
        total += 1
        if cond:
            print(f"  PASS  {name}")
            passed += 1
        else:
            print(f"  FAIL  {name}" + (f": {detail}" if detail else ""))

    print("=== finger_measure_test pure-function tests ===\n")

    # Sample regions drawn from the real page_map
    regions = [
        {"page_marker_id": 11, "page_number": 2, "measure": 1,
         "continuation_index": 1, "source_line_start": 15, "source_line_end": 24,
         "x1": 59, "y1": 886, "x2": 1003, "y2": 1392},
        {"page_marker_id": 12, "page_number": 3, "measure": 1,
         "continuation_index": 2, "source_line_start": 1,  "source_line_end": 16,
         "x1": 59, "y1": 178, "x2": 1003, "y2": 987},
    ]

    # T1: hit inside region
    r = lookup_region(regions, 11, 500, 1000)
    check(r is not None and r["measure"] == 1 and r["continuation_index"] == 1,
          "T1 lookup_region inside region → measure 1 cont 1", str(r))

    # T2: wrong page_marker_id → None
    r = lookup_region(regions, 10, 500, 1000)
    check(r is None, "T2 lookup_region wrong page_marker_id → None")

    # T3: correct page but y above region → None
    r = lookup_region(regions, 11, 500, 100)
    check(r is None, "T3 lookup_region above y range → None")

    # T4: correct page but y below region → None
    r = lookup_region(regions, 11, 500, 1500)
    check(r is None, "T4 lookup_region below y range → None")

    # T5: page 3 region hit
    r = lookup_region(regions, 12, 200, 500)
    check(r is not None and r["measure"] == 1 and r["continuation_index"] == 2,
          "T5 lookup_region page 3 → measure 1 cont 2", str(r))

    # T6: canonical_coords — identity homography
    H_id = np.eye(3, dtype=np.float32)
    cx, cy = canonical_coords((342, 890), H_id)
    check(cx == 342 and cy == 890,
          "T6 canonical_coords identity → point unchanged",
          f"got ({cx},{cy})")

    # T7: canonical_coords — uniform 2× scale
    H_scale = np.diag([2.0, 2.0, 1.0]).astype(np.float32)
    cx, cy = canonical_coords((100, 200), H_scale)
    check(cx == 200 and cy == 400,
          "T7 canonical_coords 2× scale homography",
          f"got ({cx},{cy})")

    # T8: full pipeline — cam → canonical → region lookup using shift homography
    # Shift homography: canonical = cam + (200, 600)
    H_shift = np.float32([[1, 0, 200], [0, 1, 600], [0, 0, 1]])
    # cam point (300, 290) → canonical (500, 890) which is inside regions[0]
    cx2, cy2 = canonical_coords((300, 290), H_shift)
    r2 = lookup_region(regions, 11, cx2, cy2)
    check(r2 is not None and r2["measure"] == 1,
          "T8 full pipeline cam→canonical→region",
          f"canonical=({cx2},{cy2}) measure={r2 and r2['measure']}")

    # T9: fingertip_camera_px returns None when no hand
    class _NoHand:
        hand_landmarks = []
    check(fingertip_camera_px(_NoHand(), 640, 480) is None,
          "T9 fingertip_camera_px no-hand → None")

    # T10: fingertip_camera_px with mock landmark
    class _Lm:
        def __init__(self, x, y): self.x = x; self.y = y; self.z = 0.0
    class _HasHand:
        hand_landmarks = [[_Lm(0.0, 0.0)] * 8 + [_Lm(0.5, 0.5)] + [_Lm(0.0, 0.0)] * 12]
    px = fingertip_camera_px(_HasHand(), 640, 480)
    check(px == (320, 240),
          "T10 fingertip_camera_px mock landmark → normalized to pixel",
          f"got {px}")

    print(f"\n{'='*40}")
    print(f"Result: {passed}/{total} tests passed")
    sys.exit(0 if passed == total else 1)

# ── argument parsing & entry point ───────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Fingertip-to-measure test (MediaPipe + ArUco)"
    )
    g = p.add_mutually_exclusive_group()
    g.add_argument("--camera", type=int, metavar="INDEX",
                   help="Camera index (skip interactive selection)")
    g.add_argument("--list-cameras", action="store_true",
                   help="List available cameras and exit")
    g.add_argument("--test", action="store_true",
                   help="Run pure-function tests (no camera required)")
    return p.parse_args()


def main():
    args = parse_args()

    if args.test:
        _run_tests()
        return

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
        run(cap, args.camera)
        return

    cameras = scan_cameras()
    if not cameras:
        no_cameras_error()
        sys.exit(1)
    print_camera_list(cameras)
    idx = select_camera_interactive(cameras)
    cap = open_camera(idx)
    if cap is None:
        print(f"ERROR: failed to open camera {idx}.", file=sys.stderr)
        sys.exit(1)
    run(cap, idx)


if __name__ == "__main__":
    main()
