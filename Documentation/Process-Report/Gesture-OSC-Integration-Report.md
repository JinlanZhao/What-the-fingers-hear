# Gesture Detection and OSC Integration Report

**Report date:** September 28, 2026

---

## 1. Scope

This report covers the development of gesture-based playback triggering in
`camera/finger_measure_test.py`, from the initial OSC wiring through all
iterations of gesture detection design, and documents the tradeoffs encountered
at each stage. It picks up where `Finger-Measure-Detection-Report.md` left off.

---

## 2. OSC → Max connection

### 2.1 Transport

Python uses `python-osc` (`SimpleUDPClient`) to send UDP packets to Max on
`127.0.0.1:7400`.

```python
from pythonosc.udp_client import SimpleUDPClient
osc_client = SimpleUDPClient("127.0.0.1", 7400)

osc_client.send_message("/bar", measure_number)   # int
osc_client.send_message("/stop", [])
```

Max receives with `udpreceive 7400`, which outputs OSC messages as Max lists.
`route /bar /stop` separates the two message types.

### 2.2 Bar-position calculation in Max

From the Phase 1 playback system: each bar is 1666.667 ms (144 BPM, 4/4).
When `/bar N` is received, Max computes:

```
start_time_ms = (N - 1) × 1666.667
num_bars      = 17 - N          (play from N to the end of bar 16)
```

Max then triggers `sfplay~` / `play~` at `start_time_ms` for a duration of
`num_bars × 1666.667 ms`.

### 2.3 Cache issue and fix

**Symptom:** After pointing at a new measure and triggering play, Max played
from the previous measure. Only the second trigger used the new position.

**Root cause:** When Max receives `/bar N` while audio is already playing, the
transport updates the stored `start bar` variable but the running playback
continues from its current position. The new value is only used when play is
next re-triggered.

**Fix:** Python sends `/stop` immediately before `/bar N` on every play trigger,
forcing Max into a clean stopped state before the new position is applied.

```python
osc_client.send_message("/stop", [])
osc_client.send_message("/bar", last_pointed_measure)
```

---

## 3. MediaPipe migration: HandLandmarker → GestureRecognizer

The original `finger_measure_test.py` used `HandLandmarker` for fingertip
tracking only. Adding gesture-based triggers required gesture classification as
well. Rather than running two models per frame, `GestureRecognizer` was adopted:
it returns both gesture categories and hand landmarks in a single call.

| | HandLandmarker | GestureRecognizer |
|---|---|---|
| Model file | `hand_landmarker.task` (7.5 MB) | `gesture_recognizer.task` (8.0 MB) |
| Output | `hand_landmarks` only | `gestures` + `hand_landmarks` + `hand_world_landmarks` |
| Built-in gesture classes | — | None, Closed_Fist, Open_Palm, Pointing_Up, Thumb_Up, Thumb_Down, Victory, ILoveYou |
| API call | `detect_for_video` | `recognize_for_video` |

Both use the Tasks API in `VIDEO` running mode, which allows synchronous
per-frame calls without a callback and fits the existing OpenCV loop.

**Note on `hand_world_landmarks`:** The GestureRecognizer result includes
`hand_world_landmarks` — 3D coordinates in metres, with the wrist near the
origin. These are distinct from the normalised 2D `hand_landmarks` used for
pixel-space fingertip extraction. The two outputs serve different purposes and
should not be interchanged.

---

## 4. Gesture detection: design iterations

The goal was to let the performer trigger playback deliberately and stop it
deliberately, without false triggers during normal Braille reading (index finger
pointing at the page).

### 4.1 Iteration 1 — Thumb_Up (built-in)

**Design:** Use MediaPipe's built-in `Thumb_Up` category for play, `Open_Palm`
for stop. Confidence threshold: 0.75.

**Problem:** False positives. The thumb is naturally visible and upright in many
reading orientations; the model classified normal hand positions as `Thumb_Up`
with scores above the threshold.

**Abandoned.**

### 4.2 Iteration 2 — Custom "gun gesture" via y-axis landmark comparison

The user requested a gesture combining index finger and thumb (a "gun" or "L"
shape), which is not in MediaPipe's built-in vocabulary. Custom landmark
detection was implemented.

**Design:**
```
index_up    = lm[8].y  < lm[6].y   # tip above PIP in image coords
thumb_up    = lm[4].y  < lm[3].y
middle_down = lm[12].y > lm[10].y  # tip below PIP (curled)
ring_down   = lm[16].y > lm[14].y
pinky_down  = lm[20].y > lm[18].y
```

**Problem:** The camera is mounted above the Braille page and looks down. The
hand is roughly horizontal, not upright. In this orientation, y-axis comparisons
in the 2D image are unreliable: all fingers have similar y-values regardless of
whether they are extended or curled. `Open_Palm` triggered the play gesture
because all five y-conditions happened to be satisfied simultaneously.

**Abandoned.**

### 4.3 Iteration 3 — Wrist-distance comparison on 2D landmarks

**Design:** Replace y-axis comparisons with 2D squared distance from the wrist
(landmark 0). A finger is "extended" when its tip is farther from the wrist than
its MCP joint; "curled" when closer.

```python
def d2(a): return (a.x - wx)**2 + (a.y - wy)**2  # 2D, normalised image coords

index_extended = d2(lm[8])  > d2(lm[5])
middle_curled  = d2(lm[12]) < d2(lm[9])
```

A thumb-spread condition was also added: the thumb tip must be more than 0.8×
the index finger length away from the index tip in 2D.

**Problem:** During normal reading (index pointing at page), the middle and ring
fingers are typically in a relaxed half-open position. With the camera from
above, the 2D projection of a moderately curled finger looks the same as a
relaxed extended one — both have `tip farther from wrist than MCP` in 2D. The
gesture fired during reading.

**Abandoned.**

### 4.4 Iteration 4 — 3D world landmarks

**Design:** Switch `is_play_gesture` to use `hand_world_landmarks` (3D, metres,
wrist near origin) instead of 2D image coordinates.

```python
def d2(a): return a.x**2 + a.y**2 + a.z**2   # 3D from origin ≈ wrist
```

The hypothesis: in 3D, a curled finger's tip genuinely is closer to the wrist
than its MCP, regardless of camera angle.

**Diagnostic result:** A one-second debug print added to the live loop revealed:

```
mid_curl=False rng_curl=False  (in almost every frame)
```

The middle and ring fingers were consistently detected as "not curled". The
cause: for a moderately curled position (fingers closed but not making a tight
fist), the tip is still slightly farther from the wrist in 3D than the MCP.
The condition requires a tight, fist-level curl to pass, which a natural "gun
gesture" hand shape does not produce.

MediaPipe's own classifier also returned `None` for this gesture in every frame,
confirming that the "index + thumb" shape is outside its training distribution.

**Key finding:** The "index + thumb" gun gesture is geometrically too similar to
a normal reading/pointing posture for landmark-based detection to reliably
distinguish them, regardless of whether 2D or 3D coordinates are used. Any
threshold that catches the intended gesture will also catch normal reading; any
threshold that avoids false positives in reading will miss the intended gesture.

**Abandoned. Gesture redesigned.**

### 4.5 Final design — MediaPipe built-in gestures

**Decision:** Switch to MediaPipe's built-in `Closed_Fist` for play and
`Open_Palm` for stop. Both are unambiguous and well-separated from the reading
posture (extended index finger).

| Gesture | Trigger | OSC sent |
|---------|---------|----------|
| `Closed_Fist` | play from `last_pointed_measure` | `/stop` then `/bar N` |
| `Open_Palm` | stop | `/stop` |

This eliminates all custom landmark analysis. Gesture detection reduces to a
single model output check:

```python
gesture = get_gesture(mp_result)   # returns category_name if score ≥ threshold

if gesture == "Closed_Fist":
    effective_gesture = "Closed_Fist"
elif gesture == "Open_Palm":
    effective_gesture = "Open_Palm"
else:
    effective_gesture = None
```

**Tradeoff accepted:** The performer cannot trigger play while visibly pointing
at the measure. Instead, the workflow is: point at the target measure (screen
shows `MEASURE N`) → make a fist anywhere → playback starts from that measure.
`last_pointed_measure` remembers the last measure the fingertip was over,
independent of the current gesture, so the fist does not need to be positioned
over the measure.

---

## 5. Reliability mechanisms

### 5.1 Dwell counter

A gesture must be held for `GESTURE_DWELL_FRAMES` consecutive frames before it
triggers OSC output. If the gesture changes or drops below the confidence
threshold in any frame, the counter resets.

```python
if effective_gesture == gesture_being_held:
    gesture_dwell_count += 1
else:
    gesture_being_held  = effective_gesture
    gesture_dwell_count = 1

if gesture_dwell_count == GESTURE_DWELL_FRAMES:
    # trigger once, not repeatedly
```

The trigger fires exactly once (when the counter reaches the threshold), not
every frame while the gesture is held.

### 5.2 LOCKED-state gate

The dwell counter and all OSC output are active only when the ArUco homography
is in the `LOCKED` state. During `CALIBRATING` or `WAITING_FOR_PAGE`, gestures
are ignored. This prevents accidental triggers when the performer is positioning
the camera or turning a page.

### 5.3 Confidence threshold

`GESTURE_MIN_CONFIDENCE = 0.30`. The MediaPipe GestureRecognizer's `score`
field is checked before accepting a gesture category. Values below the threshold
are treated as `None`.

The threshold is kept low (0.30 rather than the conventional 0.75) because:
- `Closed_Fist` and `Open_Palm` are visually unambiguous gestures that the model
  classifies with high confidence when clearly performed.
- The dwell counter provides the primary false-positive protection.
- A high threshold was causing `Open_Palm` to be missed when the hand was not
  held perfectly flat.

---

## 6. `last_pointed_measure` tracking

The measure the performer intends to play from is tracked independently of
gesture state:

```python
if region is not None:
    last_pointed_measure = region["measure"]   # updated whenever fingertip is over a region
elif not mp_result.hand_landmarks:
    last_pointed_measure = None                # cleared only when hand leaves the frame
```

Specifically:
- Moving the fingertip between measures updates the value immediately.
- Moving to a blank area (`OUTSIDE_PAGE`) does **not** clear it.
- Making a fist does not clear it (the fist's landmark 8 position is usually
  outside any measure region, so `region = None`, but the hand is still
  detected).
- The value is only reset to `None` when the hand completely disappears from
  the camera frame.

This means the performer can point at Measure 7, lift their hand slightly into
a non-measure area, and then make a fist — the system will still play from
Measure 7.

---

## 7. Current parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `GESTURE_DWELL_FRAMES` | 10 | ~0.33 s at 30 fps |
| `GESTURE_MIN_CONFIDENCE` | 0.30 | Per-gesture score minimum |
| `OSC_HOST` | `127.0.0.1` | Loopback only |
| `OSC_PORT` | 7400 | Max `udpreceive 7400` |
| Play gesture | `Closed_Fist` | Built-in MediaPipe category |
| Stop gesture | `Open_Palm` | Built-in MediaPipe category |

---

## 8. Known issues and future work

- **`Open_Palm` sensitivity:** At 0.30 threshold the gesture is detectable, but
  requires a fairly flat, camera-facing palm. Lowering the threshold further
  (to 0.2 or 0) could improve this at the cost of slightly higher false
  positive risk.
- **No multi-page seek:** `last_pointed_measure` stores only the measure number,
  not the page. If the same measure number appears on multiple pages, the system
  uses the currently locked page's version, which is correct but not explicitly
  surfaced to the performer.
- **Fixed-tempo assumption:** The bar-to-millisecond conversion in Max assumes
  144 BPM throughout. A variable-tempo score would require `bar_times.json` to
  be consulted directly rather than using the linear formula.
