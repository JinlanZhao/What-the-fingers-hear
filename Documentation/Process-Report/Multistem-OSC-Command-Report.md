# Multistem OSC Command Module Report

**Report date:** October 4, 2026

---

## 1. Scope

This report documents `camera/osc_cmd.py`, the typed-command interface for
multistem playback. It covers the OSC message format, the conversion from
user-facing measure ranges to the wire format Max receives, validation rules,
and the CLI test entry point.

This module implements Phase B of the Voice-Multistem System Architecture
(typed-command test client). It is independent of the camera pipeline and ASR;
it can be run standalone to test Max/MSP playback behaviour.

---

## 2. OSC command contract

### 2.1 Wire format

Max receives on `udpreceive 7400`:

```text
/play_stems <start_measure> <num_bars> <track_1> [track_2 ...]
/play_all   <start_measure> <num_bars>
/stop
```

`start_measure` and `num_bars` are integers. Track IDs are strings.

### 2.2 Why `num_bars` instead of `end_measure`

The CLI and voice layer use an inclusive end measure (e.g. measures 5–8).
Before sending, Python converts:

```python
num_bars = end_measure - start_measure + 1
```

Max then needs only two independent multiplications to compute timing:

```text
start_ms    = (start_measure - 1) × 1666.667
duration_ms = num_bars × 1666.667
```

This avoids any cross-variable subtraction in Max and keeps both arguments
to the OSC message independent of each other.

### 2.3 Example

Terminal input:
```text
play_stems 5 8 fl1 fl2 vln1
```

OSC sent:
```text
/play_stems 5 4 fl1 fl2 vln1
```

`num_bars = 8 − 5 + 1 = 4`. The inclusive range 5–8 is preserved.

---

## 3. Validation

All validation runs in Python before any OSC packet is sent. An invalid
command raises `ValidationError` and nothing is transmitted.

| Check | Rule |
|-------|------|
| `start_measure` in range | 1 ≤ start ≤ 16 |
| `end_measure` in range | 1 ≤ end ≤ 16 |
| Range order | end ≥ start |
| Track list non-empty | at least one track required for `play_stems` |
| Track IDs valid | every ID must be in the 29-track canonical set |

### 2.4 Canonical track IDs

```text
Woodwinds:  fl1 fl2 ob1 ob2 cl1 cl2 bsn1 bsn2
Brass:      fh1 fh2 fh3 fh4 tpt1 tpt2 tbn1 tbn2 tb
Percussion: glk bd sn
Strings:    vln1 vln2 vla vc cb
Others:     crash riser room stem
```

These match the `#2` argument of each `stem_player` instance in `main.maxpat`.

---

## 4. Module API

```python
from camera.osc_cmd import send_play_stems, send_play_all, send_stop
from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 7400)

send_play_stems(5, 8, ["fl1", "fl2", "vln1"], client)
# sends: /play_stems 5 4 fl1 fl2 vln1

send_play_all(1, 16, client)
# sends: /play_all 1 16

send_stop(client)
# sends: /stop
```

All three functions validate inputs and raise `ValidationError` on failure.

---

## 5. CLI usage

```bash
# Automated validation tests (no OSC sent)
python3 camera/osc_cmd.py --test

# Interactive typed-command session
python3 camera/osc_cmd.py

# Single-shot from shell
python3 camera/osc_cmd.py play_stems 5 8 fl1 fl2 vln1
python3 camera/osc_cmd.py play_all 1 16
python3 camera/osc_cmd.py stop
```

The interactive session accepts `tracks` to list all valid IDs and `help` for
command syntax.

---

## 6. Test results

```
python3 camera/osc_cmd.py --test

Result: 16/16 tests passed

  PASS  T1  validate_measures 1 16 → ok
  PASS  T2  validate_measures 5 8 → ok
  PASS  T3  validate_measures 7 7 (single measure) → ok
  PASS  T4  start=0 → error
  PASS  T5  end=17 → error
  PASS  T6  end < start → error
  PASS  T7  validate_tracks ['fl1'] → ok
  PASS  T8  validate_tracks ['fl1','fl2','vln1'] → ok
  PASS  T9  validate_tracks all 29 tracks → ok
  PASS  T10 empty track list → error
  PASS  T11 unknown track id → error
  PASS  T12 mixed valid+invalid → error
  PASS  T13 bars(5,8) = 4
  PASS  T14 bars(1,1) = 1  (single measure)
  PASS  T15 bars(1,16) = 16  (full piece)
  PASS  T16 bars(16,16) = 1
```

---

## 7. Max-side contract (summary)

Max receives `/play_stems` or `/play_all` and executes in this order:

```text
stop current playback
→ all 0.             (mute all stems)
→ <track> 1.  × N   (enable each requested stem)   — play_stems only
→ all 1.             (enable all stems)             — play_all only
→ start_ms    = (start_measure - 1) × 1666.667
→ duration_ms = num_bars × 1666.667
→ start playhead from start_ms for duration_ms
```

The `/stop` command stops the shared playhead. The reverb tail continues
naturally after the dry stems stop.

---

## 8. Relation to existing commands

`/bar N` (the original gesture-triggered command in `finger_measure_test.py`)
remains functional. It plays all stems from measure N to the end of measure 16
using the same shared playhead. New code should prefer `/play_stems` or
`/play_all` for explicit range and track control.
