# Finger-to-Measure Detection Report

**Report date:** September 21, 2026

---

## 1. Objective

Connect the existing camera pipeline to real-time Braille measure identification:
detect the index fingertip via MediaPipe, project it through the locked homography
into canonical 1100×1700 coordinates, and look up the corresponding measure in
`data/page_map.json`.

This report covers `camera/finger_measure_test.py`.

---

## 2. Pipeline overview

```
Camera frame
  └─ ArUco detection  →  locked homography  (from aruco_realtime_registration.py)
  └─ MediaPipe Hands  →  index fingertip  (landmark 8, normalized)
       └─ × frame dimensions  →  camera pixel (cx, cy)
            └─ cv2.perspectiveTransform(H)  →  canonical (1100×1700) pixel
                 └─ lookup_region()  →  page_number / measure / continuation_index
```

Status displayed per frame:

| Status | Condition |
|--------|-----------|
| `WAITING` | Homography not yet locked |
| `NO_HAND` | Locked, no hand detected |
| `OUTSIDE_PAGE` | Fingertip outside all measure regions |
| `MEASURE N` | Fingertip inside measure N's bounding box |

---

## 3. MediaPipe installation

### Initial attempt — mediapipe 1.0.1

mediapipe 1.0.1 has a Python 3.13 wheel and installs without error, but crashes
at runtime on macOS ARM regardless of delegate setting:

```
F0000  graph_service.h:139] Check failed: service_ Service is unavailable.
-[DrishtiMetalHelper initWithCalculatorContext:]
mediapipe::api2::TensorsToDetectionsCalculator::Open()
```

Root cause: mediapipe 1.0.1 on macOS ARM always initialises the Metal GPU backend
(`DrishtiMetalHelper`) from a worker thread, regardless of the `CPU` delegate
flag. No environment variable or API option prevents this.

Python 3.12 was not available on the system, so `.venv` was not replaced.

### Resolution — mediapipe 0.10.35

`mediapipe==0.10.35` has a `py3-none-macosx_11_0_arm64` wheel (Python-version
agnostic, ARM native) that does not exhibit the Metal crash. It uses the same
Tasks API path as 1.0.1.

```
Python   : 3.13.4
MediaPipe: 0.10.35   ← downgraded from 1.0.1
OpenCV   : 5.0.0
NumPy    : 2.5.3
pip check: No broken requirements found
```

### Model file

Downloaded `data/hand_landmarker.task` (7.5 MB, float16) from the MediaPipe
models repository.

---

## 4. API used

```python
from mediapipe.tasks.python.vision.hand_landmarker import (
    HandLandmarker, HandLandmarkerOptions,
)
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode,
)

opts = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="data/hand_landmarker.task"),
    running_mode=VisionTaskRunningMode.VIDEO,
    num_hands=1,
)
landmarker = HandLandmarker.create_from_options(opts)

# Per frame (monotonic timestamp required):
mp_result = landmarker.detect_for_video(mp_img, timestamp_ms)

# Landmark 8 = index fingertip
lm = mp_result.hand_landmarks[0][8]
cam_x, cam_y = int(lm.x * frame_w), int(lm.y * frame_h)
```

Running mode `VIDEO` (not `LIVE_STREAM`) allows synchronous per-frame detection
without a callback, which fits the existing OpenCV loop.

---

## 5. Code structure

`finger_measure_test.py` imports all camera-selection and registration logic
from `aruco_realtime_registration.py` without copying it:

| Imported from `aruco_realtime_registration` | Purpose |
|---------------------------------------------|---------|
| `make_detector`, `get_page_id` | ArUco detection |
| `compute_locked_homography` | Median homography calibration |
| `scan_cameras`, `open_camera`, etc. | Camera selection (unchanged) |
| `scale_for_display` | Display scaling |
| `FRAME_IDS`, `INNER_CORNER`, `PAGE_CONFIRM_FRAMES`, etc. | Shared constants |
| State constants `WAITING_FOR_PAGE`, `CALIBRATING`, `LOCKED` | Same state machine protocol |

New functions in `finger_measure_test.py`:

| Function | Purpose |
|----------|---------|
| `load_page_map()` | Load regions from `data/page_map.json` |
| `lookup_region(regions, page_marker_id, cx, cy)` | Hit-test canonical point |
| `make_hand_landmarker()` | Instantiate MediaPipe landmarker |
| `fingertip_camera_px(result, w, h)` | Extract landmark 8 pixel coords |
| `canonical_coords(cam_pt, H)` | `cv2.perspectiveTransform` wrapper |
| `_run_tests()` | Pure-function tests, no camera |

---

## 6. Bug fix during development — PAGE_ID_TO_PAGE

`aruco_realtime_registration.py` originally only mapped IDs 10–11 (pages 1–2):

```python
PAGE_ID_TO_PAGE = {10: 1, 11: 2}
```

All 18 physical pages have printed markers. IDs 12–27 were being displayed as
`Page: ? (ID N)` and the state label for those pages was incorrect. Fixed to
match the `PAGE_MARKER_MAP` convention in `build_page_map.py`:

```python
PAGE_ID_TO_PAGE = {9 + n: n for n in range(1, 19)}
# {10:1, 11:2, 12:3, ..., 27:18}
```

---

## 7. Test results

### Pure-function tests

```
python3 camera/finger_measure_test.py --test

Result: 10/10 tests passed

  PASS  T1  lookup_region inside region → measure 1 cont 1
  PASS  T2  lookup_region wrong page_marker_id → None
  PASS  T3  lookup_region above y range → None
  PASS  T4  lookup_region below y range → None
  PASS  T5  lookup_region page 3 → measure 1 cont 2
  PASS  T6  canonical_coords identity → point unchanged
  PASS  T7  canonical_coords 2× scale homography
  PASS  T8  full pipeline cam→canonical→region
  PASS  T9  fingertip_camera_px no-hand → None
  PASS  T10 fingertip_camera_px mock landmark → normalized to pixel
```

### 12-page sequential test

All 18 ArUco page markers are printed. Pages 1–12 were tested sequentially in a
single session:

```
Page 1  (ID 10) confirmed → CALIBRATING → LOCKED  (calibration #1)
Page 2  (ID 11) detected  → recalibrating → LOCKED  (#2)
Page 3  (ID 12) detected  → recalibrating → LOCKED  (#3)
Page 4  (ID 13) → LOCKED  (#4)
Page 5  (ID 14) → LOCKED  (#5)
Page 6  (ID 15) → LOCKED  (#6)
Page 7  (ID 16) → LOCKED  (#7)
Page 8  (ID 17) → LOCKED  (#8)
Page 9  (ID 18) → LOCKED  (#9)
Page 10 (ID 19) → LOCKED  (#10)
Page 11 (ID 20) → LOCKED  (#11)
Page 12 (ID 21) → LOCKED  (#12)
```

Every page ID was recognised correctly and homography locked on each transition.

### Manual tests (live camera, camera fixed)

| Test | Result |
|------|--------|
| Fingertip on Page 2 Measure 1 region | `MEASURE 1` ✓ |
| Fingertip on non-measure area (title / instrument) | `OUTSIDE_PAGE` ✓ |
| Hand leaves frame | `NO_HAND` immediately ✓ |
| ArUco markers occluded by hand | Locked homography continues, `MEASURE N` maintained ✓ |

**Constraint confirmed:** the system requires the camera to be physically fixed.
Locked homography is computed once at calibration time; camera movement
invalidates the coordinate mapping. In the performance setup, the camera will be
mounted on a fixed stand — this is not a limitation in practice.

---

## 8. Known warnings (benign)

| Warning | Source | Impact |
|---------|--------|--------|
| `landmark_projection_calculator.cc:81` Using NORM_RECT without IMAGE_DIMENSIONS | MediaPipe internal | None; detection works correctly |
| `E0000 portable_clearcut_uploader` Failed to send to clearcut | MediaPipe telemetry upload to Google servers | None |
| `inference_feedback_manager.cc:121` Feedback manager requires single-signature model | MediaPipe model loading | None |

---

## 9. Next step

**OSC → Max integration:** send the detected `measure` number from Python to
Max/MSP via OSC on each new detection, replacing the manual playback trigger
with automatic measure-based audio playback.
