#!/usr/bin/env python3
"""
Automated tests for Controller state machine in voice_mvp.py.

Covers: Record push-to-talk flow, Stop cancels recording,
Stop invalidates stale ASR result, Serial line framing.
No hardware, no Whisper model, no OSC required.

Usage:
    python3 camera/test_controller.py
"""

import sys
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from voice_mvp import Controller, SAMPLE_RATE, MIN_DURATION

passed = 0
total = 0


def check(cond: bool, name: str, detail: str = "") -> None:
    global passed, total
    total += 1
    if cond:
        print(f"  PASS  {name}")
        passed += 1
    else:
        print(f"  FAIL  {name}" + (f": {detail}" if detail else ""))


def eq(a, b, name: str) -> None:
    check(a == b, name, f"got {a!r}, want {b!r}")


def _wait_for(ctrl: Controller, state: str, timeout: float = 2.0) -> bool:
    """Poll controller state until it matches or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        with ctrl._lock:
            if ctrl._state == state:
                return True
        time.sleep(0.01)
    return False


def _make_ctrl(anchor: int = 7) -> Controller:
    """Controller with mock model + client; no real IO."""
    return Controller(anchor, MagicMock(), MagicMock())


# 1-second audio block that passes the MIN_DURATION check.
_FAKE_AUDIO = np.zeros(int(SAMPLE_RATE * 1.0), dtype=np.float32)


# _record_until mock that actually blocks on stop_evt (matches real behaviour).
def _blocking_record(stop_evt, device=None):
    stop_evt.wait()
    return _FAKE_AUDIO


print("=== controller tests ===\n")

# ── T1: initial state ─────────────────────────────────────────────────────────

ctrl = _make_ctrl()
eq(ctrl._state,      Controller.IDLE, "T1  initial state is IDLE")
eq(ctrl.anchor,      7,               "T1  initial anchor")
eq(ctrl._request_id, 0,               "T1  initial request_id = 0")

# ── T2: push-to-talk full flow ────────────────────────────────────────────────

ctrl = _make_ctrl()
with patch("voice_mvp._record_until", side_effect=_blocking_record), \
     patch("voice_mvp._transcribe", return_value="play flute one"), \
     patch("voice_mvp._dispatch") as mock_disp:

    ctrl.on_record_start()
    eq(ctrl._state, Controller.RECORDING,  "T2  RECORDING after RECORD_START")

    ctrl.on_record_end()
    eq(ctrl._state, Controller.PROCESSING, "T2  PROCESSING immediately after RECORD_END")

    ok = _wait_for(ctrl, Controller.IDLE)
    check(ok,              "T2  IDLE after ASR + dispatch completes")
    check(mock_disp.called, "T2  _dispatch was called")

# ── T3: RECORD_START while RECORDING is silently ignored ──────────────────────

ctrl = _make_ctrl()
with patch("voice_mvp._record_until", side_effect=_blocking_record), \
     patch("voice_mvp._transcribe", return_value=""), \
     patch("voice_mvp._dispatch"):

    ctrl.on_record_start()
    rid1 = ctrl._request_id
    eq(ctrl._state, Controller.RECORDING, "T3  RECORDING started")

    ctrl.on_record_start()          # should be ignored silently (key-repeat)
    eq(ctrl._request_id, rid1,          "T3  duplicate RECORD_START — rid unchanged")
    eq(ctrl._state, Controller.RECORDING, "T3  state still RECORDING")

    ctrl.on_record_end()
    _wait_for(ctrl, Controller.IDLE)

# ── T4: Stop cancels recording — no dispatch ──────────────────────────────────

ctrl = _make_ctrl()
recording_active = threading.Event()

def _block_then_cancel(stop_evt, device=None):
    recording_active.set()
    stop_evt.wait()
    return np.zeros(1, dtype=np.float32)   # 1 sample — below MIN_DURATION

with patch("voice_mvp._record_until", side_effect=_block_then_cancel), \
     patch("voice_mvp._dispatch") as mock_disp:

    ctrl.on_record_start()
    recording_active.wait(timeout=1.0)
    eq(ctrl._state, Controller.RECORDING, "T4  RECORDING confirmed active")

    ctrl.on_stop()
    eq(ctrl._state, Controller.IDLE,      "T4  IDLE immediately after Stop")

    time.sleep(0.1)                        # let background thread exit
    check(not mock_disp.called, "T4  no dispatch after Stop cancels recording")

# ── T5: Stop during processing invalidates stale ASR result ───────────────────

ctrl = _make_ctrl()
asr_started = threading.Event()
asr_proceed = threading.Event()

def _slow_asr(audio, model):
    asr_started.set()
    asr_proceed.wait()
    return "play flute one"

with patch("voice_mvp._record_until", side_effect=_blocking_record), \
     patch("voice_mvp._transcribe",   side_effect=_slow_asr), \
     patch("voice_mvp._dispatch") as mock_disp:

    ctrl.on_record_start()
    ctrl.on_record_end()                   # → PROCESSING, ASR starts

    asr_started.wait(timeout=2.0)
    rid_before = ctrl._request_id

    ctrl.on_stop()
    check(ctrl._request_id > rid_before,
          "T5  Stop incremented request_id")
    eq(ctrl._state, Controller.IDLE,       "T5  IDLE after Stop during PROCESSING")

    asr_proceed.set()                      # let ASR finish
    time.sleep(0.2)
    check(not mock_disp.called, "T5  no dispatch — request invalidated by Stop")

# ── T6: spurious RECORD_END without active session is ignored ─────────────────

ctrl = _make_ctrl()
ctrl.on_record_end()
eq(ctrl._state,      Controller.IDLE, "T6  spurious RECORD_END — state unchanged")
eq(ctrl._request_id, 0,               "T6  request_id unchanged")

# ── T7: RECORD_END after Stop cancelled session is ignored ────────────────────

ctrl = _make_ctrl()
recording_active2 = threading.Event()

def _block2(stop_evt, device=None):
    recording_active2.set()
    stop_evt.wait()
    return np.zeros(1, dtype=np.float32)

with patch("voice_mvp._record_until", side_effect=_block2), \
     patch("voice_mvp._dispatch") as mock_disp:

    ctrl.on_record_start()
    recording_active2.wait(timeout=1.0)

    ctrl.on_stop()                         # cancels recording
    eq(ctrl._state, Controller.IDLE, "T7  IDLE after Stop")

    ctrl.on_record_end()                   # spurious release — must be ignored
    eq(ctrl._state, Controller.IDLE, "T7  still IDLE after late RECORD_END")
    time.sleep(0.1)
    check(not mock_disp.called, "T7  no dispatch after Stop + late RECORD_END")

# ── T8: Serial line framing — CRLF split across multiple reads ────────────────

events: list[str] = []

class _FakeCtrl:
    def on_record_start(self): events.append("RECORD_START")
    def on_record_end(self):   events.append("RECORD_END")
    def on_play(self):         events.append("PLAY")
    def on_stop(self):         events.append("STOP")

def _process_buf(buf: str, ctrl) -> str:
    """Replicates the buffer logic in _run_serial_listener."""
    while "\n" in buf:
        line, buf = buf.split("\n", 1)
        line = line.strip()
        if not line:
            continue
        if line == "RECORD_START":   ctrl.on_record_start()
        elif line == "RECORD_END":   ctrl.on_record_end()
        elif line == "PLAY":         ctrl.on_play()
        elif line == "STOP":         ctrl.on_stop()
    return buf

fc = _FakeCtrl()
buf = ""
# Simulate chunks where lines are split across multiple Serial.read() calls.
for chunk in ["RECORD_S", "TART\r\n", "PLAY\r\nST", "OP\r\n", "RECORD_END\r\n"]:
    buf += chunk
    buf = _process_buf(buf, fc)

eq(events, ["RECORD_START", "PLAY", "STOP", "RECORD_END"],
   "T8  Serial framing: split CRLF lines reassembled correctly")

# ── summary ───────────────────────────────────────────────────────────────────

print(f"\n{'='*40}")
print(f"Result: {passed}/{total} tests passed")
sys.exit(0 if passed == total else 1)
