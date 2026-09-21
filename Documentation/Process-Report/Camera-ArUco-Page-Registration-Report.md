# Camera ArUco Page Registration

**Report date:** September 21, 2026

## 1. Objective

The camera system identifies the physical Braille page in front of the camera and computes a stable perspective correction (homography). This allows a finger position detected in the camera frame to be transformed into a canonical page coordinate for later Braille-measure lookup and audio playback.

This report covers two scripts:

| Script | Role |
|---|---|
| `camera/aruco_page_registration.py` | Offline processing of static test images |
| `camera/aruco_realtime_registration.py` | Live camera registration with a locked homography |

## 2. Development Environment

| Component | Version / configuration |
|---|---|
| Computer | macOS on Apple Silicon |
| Camera | iPhone through macOS Continuity Camera |
| Python | 3.13 |
| OpenCV | 5.0.0 |
| `opencv-contrib-python` | 5.0.0.93 |
| NumPy | 2.5.3 |
| ArUco dictionary | `DICT_4X4_50` |

## 3. Marker Layout

Four frame markers are fixed to the registration frame. A separate page-identity marker is associated with each removable Braille page and placed in the designated identity-marker position.

| Marker ID | Position | Role |
|---|---|---|
| 0 | Top-left corner of frame | Frame reference |
| 1 | Top-right corner of frame | Frame reference |
| 2 | Bottom-right corner of frame | Frame reference |
| 3 | Bottom-left corner of frame | Frame reference |
| 10 | Page-identity position | Identifies Page 1 |

Frame IDs 0–3 define the registration quadrilateral. ID 10 identifies Page 1 and does not participate in the homography calculation.

The homography maps the inner corners of the frame markers to a canonical 1100 × 1700 px coordinate space:

| Marker | Inner corner used | Destination coordinate |
|---|---|---|
| ID 0 | Bottom-right | `(0, 0)` |
| ID 1 | Bottom-left | `(1099, 0)` |
| ID 2 | Top-left | `(1099, 1699)` |
| ID 3 | Top-right | `(0, 1699)` |

## 4. Static Image Pipeline

### 4.1 Purpose

`aruco_page_registration.py` verifies that the printed markers can be detected and that the homography produces a correctly rectified page before live-camera processing is introduced.

### 4.2 Static Robustness Test

Four photographs were tested:

- `page1_test.jpg`: baseline view;
- `page1_test2.jpg`;
- `page1_test3.jpg`;
- `page1_test4.jpg`.

The additional photographs varied camera angle and distance. The script detected IDs 0, 1, 2, 3, and 10 in all four images, and all four images produced a valid rectified page.

| Test image | Detected IDs | Registration |
|---|---|---|
| `page1_test.jpg` | 0, 1, 2, 3, 10 | Pass |
| `page1_test2.jpg` | 0, 1, 2, 3, 10 | Pass |
| `page1_test3.jpg` | 0, 1, 2, 3, 10 | Pass |
| `page1_test4.jpg` | 0, 1, 2, 3, 10 | Pass |

Annotated and rectified images are saved to `camera/output/` using the input filename stem.

## 5. Realtime Pipeline

### 5.1 Camera Selection

`aruco_realtime_registration.py` does not hardcode a camera index because the index assigned to the iPhone Continuity Camera can change.

The script can scan camera indices 0–10 with `cv2.CAP_AVFOUNDATION`, verify each device by reading a frame, display the available indices and resolutions, and allow interactive or direct selection.

```bash
python3 aruco_realtime_registration.py
python3 aruco_realtime_registration.py --camera 2
python3 aruco_realtime_registration.py --list-cameras
```

### 5.2 Initial Per-Frame Design

The first realtime implementation recalculated the homography whenever all four frame markers were detected. During simulated Braille reading, the reader's hands frequently covered one or more markers.

Initial result:

```text
Total frames          : 1822
Registered frames     : 1541
Registration rate     : 84.6%
Average FPS           : 29.2
```

The page was stable when unobstructed. The lower registration rate was caused primarily by normal hand occlusion during reading rather than unstable detection of the printed markers.

### 5.3 Locked Homography Solution

The realtime pipeline was changed to calculate the homography during an initial calibration period and then lock it. Temporary marker occlusion no longer invalidates the page coordinate system.

The state machine uses three states:

| State | Behavior |
|---|---|
| `WAITING_FOR_PAGE` | Waits for a page ID to appear for 10 consecutive frames |
| `CALIBRATING` | Collects 15 frames in which IDs 0–3 are all visible |
| `LOCKED` | Uses the stored homography even when markers become occluded |

During calibration, the script takes the coordinate-wise median of the collected marker corners and computes one homography from the median coordinates. This reduces the influence of short-term corner-coordinate jitter.

State transitions:

- `WAITING_FOR_PAGE` → confirmed page ID → `CALIBRATING`;
- `CALIBRATING` → 15 valid frames → compute and lock homography → `LOCKED`;
- `LOCKED` → current Page ID temporarily absent → retain the current page and homography;
- `LOCKED` → different Page ID confirmed for 10 frames → recalibrate for the new page;
- `R` → force a new calibration sequence;
- `Q` or `Esc` → exit safely.

### 5.4 Occlusion Robustness Result

The locked implementation was tested while hands moved naturally across the Braille page and repeatedly occluded the frame markers.

```text
Total frames                 : 1481
Frame-marker visibility      : 456 frames (30.8%)
Locked-homography usable     : 1453 frames (98.1%)
Calibration counter reported : 1
Average FPS                  : 29.9
```

Although all four frame markers were simultaneously visible in only 30.8% of frames, the previously calibrated homography remained usable in 98.1% of frames. The remaining 1.9% primarily covers the initial period before calibration was locked.

No page change was performed during this test. The reported count of 1 therefore represents the initial calibration under the current counter implementation, not a validated page-change recalibration.

This test shows that locked calibration handles marker occlusion during reading, provided that the camera, registration frame, and Braille page remain physically fixed.

### 5.5 Display

The realtime script displays two windows:

- **ArUco Registration:** camera feed with marker borders, marker IDs, frame quadrilateral, state, calibration progress, missing frame IDs, and FPS;
- **Rectified Page:** the 1100 × 1700 px perspective-corrected page.

Before the first calibration is available, the rectified window displays a placeholder. After calibration is locked, temporary marker occlusion does not clear the rectified output.

## 6. Bugs Encountered and Fixes

### 6.1 `ValueError: too many values to unpack (expected 2)`

`ArucoDetector.detectMarkers()` returns three values:

```python
# Incorrect
corners, ids = detector.detectMarkers(frame)

# Correct
corners, ids, _ = detector.detectMarkers(frame)
```

### 6.2 OpenCV 4/5 `ids` Shape Difference

OpenCV versions can return `ids` as either `(n, 1)` or `(n,)`. Flattening the array supports both forms:

```python
corners, ids, _ = detector.detectMarkers(frame)
ids = ids.flatten() if ids is not None else np.array([], dtype=int)
id_map = {int(ids[i]): corners[i][0] for i in range(len(ids))}
```

## 7. Operational Assumptions and Limitations

- The locked homography remains valid only while the camera and registration frame remain fixed.
- The Braille page must be placed in a repeatable physical position and prevented from sliding during reading.
- Pressing `R` is required if the camera, frame, or page moves after calibration.
- Page-change detection has not yet been validated because only Page 1 / ID 10 has been tested.
- The canonical 1100 × 1700 px coordinate space has not yet been validated against final measure-region boundaries.
- iPhone Continuity Camera is suitable for prototype testing, but the final camera, mounting height, field of view, lighting, latency, and exposure behavior must be tested separately.

## 8. Current Deliverables

| File | Status |
|---|---|
| `camera/aruco_page_registration.py` | Complete for static-image registration |
| `camera/aruco_realtime_registration.py` | Complete for Page 1 calibration and marker-occlusion handling |
| `camera/output/page1_test_annotated.jpg` | Marker-detection output |
| `camera/output/page1_test_rectified.jpg` | Rectified 1100 × 1700 px page |
| Additional output pairs for tests 2–4 | Generated |

## 9. Work Not Yet Completed

- Assign and print a unique identity marker for every Braille page.
- Test automatic page-change detection and recalibration with Page 2 and later pages.
- Build `page_map.json` using `page + measure + continuation region` rather than assuming that every measure occupies one uninterrupted region.
- Validate the 1100 × 1700 px canonical coordinates against the final physical page placement.
- Add finger tracking and transform the detected fingertip into canonical page coordinates.
- Connect canonical coordinates to measure lookup.
- Connect validated measure output to Max/MSP through OSC.
- Test the final fixed overhead camera across the intended lighting, distance, and interaction conditions.

