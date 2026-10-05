# Voice MVP Implementation Report

**Report date:** October 4, 2026

---

## 1. Scope

This report documents the Voice MVP for multistem playback control. The MVP
covers: push-to-talk microphone recording (keyboard and Teensy hardware
buttons), Whisper ASR, deterministic command parsing, anchor measure freezing,
and OSC dispatch via `osc_cmd.py`.

**Not included in this phase:** LLM parser, TTS, clarification dialogue,
camera live-anchor integration, Max patch changes.

---

## 2. Files

| File | Role |
|------|------|
| `camera/voice_parser.py` | Pure parser: instrument map, phrase matching, `parse_command()` |
| `camera/voice_mvp.py` | Audio recording, Whisper ASR, `Controller` state machine, Serial listener, OSC dispatch |
| `camera/test_voice_parser.py` | 54 automated parser tests |
| `camera/test_controller.py` | 22 automated controller state-machine tests |
| `Hardware/Buttons/Buttons.ino` | Teensy 4.0 firmware: RECORD push-to-talk, PLAY, STOP |

---

## 3. Architecture

```
RECORD pressed (button or SPACE held)
  │
  ▼
Controller.on_record_start()      send /stop, freeze anchor, open microphone
  │
  ▼  (background thread)
_record_until(stop_evt)           sounddevice, 16 kHz mono float32
  │
RECORD released (button or SPACE released)
  │
  ▼
Controller.on_record_end()        signal stop_evt → hand off to ASR thread
  │
  ▼
_transcribe()                     openai-whisper "base" model, language="en"
  │
  ▼
parse_command(text, anchor)       voice_parser.py — deterministic regex + table
  │
  ├── {"cmd":"stop"}           → send_stop()
  ├── {"cmd":"play_stems",...} → send_play_stems()   osc_cmd.py
  └── {"cmd":"play_all",...}   → send_play_all()     osc_cmd.py

STOP button (or on_stop() call)
  ──► send /stop immediately
  ──► cancel recording OR invalidate in-flight ASR request
```

The Serial listener and recording both run in daemon threads; the keyboard
listener runs on the main thread. None of these blocks the others.

---

## 4. Controller state machine

`Controller` in `voice_mvp.py` manages three states:

| State | Enters from | Exits to |
|-------|------------|----------|
| `IDLE` | initial; after dispatch completes; after Stop | `RECORDING` |
| `RECORDING` | `on_record_start()` | `PROCESSING` (release) or `IDLE` (Stop) |
| `PROCESSING` | `on_record_end()` | `IDLE` (done or Stop) |

`on_stop()` is accepted in any state:
- During `RECORDING`: signals the recording thread to stop; discards audio.
- During `PROCESSING`: increments `_request_id`, which the background thread
  checks before each checkpoint (post-record, post-ASR, pre-dispatch); the
  thread returns without sending OSC when it detects a mismatch.

PLAY and a second RECORD_START are ignored during `RECORDING` or `PROCESSING`.
A `RECORD_END` that arrives with no active session (e.g., after Stop already
cancelled it) is also silently ignored.

---

## 5. Anchor measure

`anchor_measure` is the measure currently pointed at (from the camera
pipeline in a future phase). When RECORD is pressed, its value is captured
into a local variable for that recording session — this is the "freeze."

In standalone mode the anchor is set via `--anchor N` (CLI, 1–16) or digit
keys `1`–`9` during the session. Integration with the camera pipeline
(`last_pointed_measure` feed) is left for the next phase.

---

## 6. Hardware integration

### 6.1 Teensy firmware (`Hardware/Buttons/Buttons.ino`)

| Button | Pin | INPUT_PULLUP | Events sent |
|--------|-----|--------------|-------------|
| RECORD | 2 | yes | `RECORD_START` (press), `RECORD_END` (release) |
| PLAY | 4 | yes | `PLAY` (press) |
| STOP | 6 | yes | `STOP` (press) |

Debounce: 20 ms (Bounce library, Teensy). Serial: 115200 baud, `Serial.println()`
(CRLF line endings). Holding RECORD does not repeat events; only the
leading `fallingEdge()` and trailing `risingEdge()` are sent.

LED is hardware-wired to the button circuit; the firmware does not control it.

### 6.2 Serial listener (`_run_serial_listener`)

Runs as a daemon thread. Reads up to 64 bytes per call and accumulates a string
buffer to handle lines arriving split across multiple reads. Strips CR before
dispatching. Unknown event strings are logged and ignored. On disconnect,
calls `on_stop()` to cancel any active session.

Port and baud rate are specified via `--serial` and `--baud` CLI arguments.
If the port cannot be opened, the process exits with an error message rather
than selecting a fallback device.

### 6.3 PLAY button behaviour

Sends `/play_all anchor 16` using the current anchor at press time.
Full Mix playback is via `sfplay~ 2` in Max (see `Max-Playback-Current-Architecture.md`).
PLAY is ignored during `RECORDING` or `PROCESSING`.

---

## 7. Deterministic parser design

### 7.1 Supported phrases

| Phrase pattern | Command sent |
|----------------|-------------|
| `"stop"` / `"stop playing"` | `/stop` |
| `"play <instruments>"` | `/play_stems anchor 16 <tracks>` |
| `"play measures N through M"` | `/play_all N M` |
| `"play <instruments> measures N through M"` | `/play_stems N M <tracks>` |
| `"play measures N through M <instruments>"` | `/play_stems N M <tracks>` |

### 7.2 Instrument → track ID

Each instrument phrase is matched against an ordered table of `(phrase,
prefix, numbered)` tuples. Longer multi-word phrases are listed first to
prevent partial matches (e.g. `"bass drum"` before `"bass"`).

### 7.3 Number normalisation

Both spoken words (`"five"`) and ASR digit output (`"5"`) are accepted.
Supported range: zero–sixteen (0–16).

### 7.4 Measure range extraction

Pattern: `measures? <N> (through|thru|to|-) <M>`

The matched span is removed from the text before instrument extraction, so
instruments can appear before or after the range phrase.

---

## 8. ASR choice: openai-whisper

Whisper was chosen for three reasons:
1. **Offline** — no API key, no network dependency during performance.
2. **Robustness** — handles musical instrument names reliably.
3. **Simple integration** — `whisper.transcribe(audio_array)` returns a plain
   string.

The `base` model (74 MB) is the default. `tiny` is available for faster
turnaround; `small` can be used if instrument recognition proves unreliable.

---

## 9. Test results

### 9.1 Parser tests (no hardware required)

```
python3 camera/test_voice_parser.py
Result: 54/54 tests passed
```

### 9.2 Controller state-machine tests (no hardware required)

```
python3 camera/test_controller.py
Result: 22/22 tests passed
```

Tests cover:
- `T1` Initial state
- `T2` Push-to-talk full flow (RECORD_START → RECORD_END → ASR → dispatch → IDLE)
- `T3` Duplicate RECORD_START during RECORDING is ignored silently
- `T4` Stop cancels recording — no dispatch
- `T5` Stop during PROCESSING invalidates stale ASR result — no dispatch
- `T6` Spurious RECORD_END with no active session is ignored
- `T7` RECORD_END after Stop-cancelled session is ignored
- `T8` Serial line framing: CRLF split across reads reassembles correctly

---

## 10. Usage

```bash
# First run: install dependencies (use python3 -m pip to match the active env)
python3 -m pip install pyserial

# Keyboard only (no Teensy)
python3 camera/voice_mvp.py --anchor 7 --device 5

# Keyboard + Teensy buttons
python3 camera/voice_mvp.py --anchor 7 --device 5 \
    --serial /dev/cu.usbmodem154611801

# Smaller model
python3 camera/voice_mvp.py --anchor 1 --model tiny \
    --serial /dev/cu.usbmodem154611801

# List available audio input devices
python3 camera/voice_mvp.py --list-devices
```

Keys during session (keyboard, always active):

| Key | Action |
|-----|--------|
| SPACE (hold) | Record (push-to-talk) |
| 1 – 9 | Set anchor_measure |
| Q / Esc | Quit |

Hardware buttons (when `--serial` is given):

| Button | Action |
|--------|--------|
| RECORD (hold) | Push-to-talk: press = start, release = end |
| PLAY | `/play_all anchor–16` (Full Mix) |
| STOP | `/stop` + cancel active recording / pending request |

Expected behaviour:
- Press PLAY → Full Mix plays from `--anchor` to measure 16.
- Press STOP → playback stops; no queued command fires.
- Hold RECORD → playback stops, recording starts; release → ASR runs → OSC sent.
- Hold RECORD, press STOP before releasing → recording cancelled; RECORD
  release is ignored; no ASR, no playback.
- Hold RECORD, release, press STOP before ASR finishes → OSC is not sent.

---

## 11. Known limitations

| Limitation | Cause | Plan |
|------------|-------|------|
| Anchor is set manually | No live camera feed integration | Next phase: watch shared state from camera pipeline |
| Keyboard anchor only supports 1–9 | Single keypress | Use `--anchor` CLI for measures 10–16 |
| Whisper latency ~0.5–2 s | CPU inference | Acceptable; switch to `faster-whisper` if needed |
| Parser has no tolerance for ASR variation | Deterministic regex | Next phase: replace with LLM parser (Qwen via Ollama, per D16 in architecture spec) |
| No TTS feedback | Excluded from MVP | Future phase |

---

## 12. Hardware verification status

Automated tests (no hardware): **passed** (22/22 controller, 54/54 parser).

The following require physical Teensy hardware and are **not yet verified**:

- One complete RECORD press produces exactly one `RECORD_START` + `RECORD_END` pair.
- Holding RECORD does not repeat events.
- PLAY sends correct OSC and Full Mix starts.
- STOP stops playback and cancels active recording.
- Stop before RECORD release does not trigger ASR or playback.
- Serial port opens correctly at `/dev/cu.usbmodem154611801`.
