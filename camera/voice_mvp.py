#!/usr/bin/env python3
"""
voice_mvp.py — Voice MVP for multistem playback.

Push-to-talk recording via keyboard SPACE or Teensy RECORD button.
Physical buttons connect via --serial; keyboard is always active as fallback.

Usage
-----
    python3 camera/voice_mvp.py [--anchor N] [--model tiny|base|small]
                                 [--device INDEX] [--serial PORT] [--baud RATE]

Keys (keyboard, always active)
----
    SPACE (hold)     record (push-to-talk)
    1 – 9            set anchor_measure manually
    Q / Esc          quit

Buttons (Teensy, when --serial is given)
-----------------------------------------
    RECORD (hold)    push-to-talk: RECORD_START on press, RECORD_END on release
    PLAY             /play_all anchor–16  (Full Mix via sfplay~ 2)
    STOP             /stop + cancel any active recording or pending request

OSC output  (127.0.0.1:7400)
----------
    /play_stems <start> <num_bars> <track1> [track2 ...]
    /play_all   <start> <num_bars>
    /stop
"""

import argparse
import sys
import threading
from pathlib import Path

import numpy as np
import sounddevice as sd

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from osc_cmd import (
    OSC_HOST, OSC_PORT,
    ValidationError,
    send_play_stems, send_play_all, send_stop,
)
from voice_parser import parse_command
from pythonosc.udp_client import SimpleUDPClient

SAMPLE_RATE = 16_000          # Hz — Whisper's expected input rate
MIN_DURATION = 0.4            # seconds — shorter recordings are discarded

_SERIAL_BAUD_DEFAULT = 115200


# ── audio recording ───────────────────────────────────────────────────────────

def _record_until(stop_event: threading.Event,
                  device: int | None = None) -> np.ndarray:
    """Record mono float32 audio until stop_event is set."""
    chunks: list[np.ndarray] = []

    def _cb(indata, frames, time_info, status):
        chunks.append(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                        dtype="float32", device=device, callback=_cb):
        stop_event.wait()

    if not chunks:
        return np.array([], dtype=np.float32)
    return np.concatenate(chunks, axis=0).flatten()


# ── ASR ───────────────────────────────────────────────────────────────────────

def _transcribe(audio: np.ndarray, model) -> str:
    """Run Whisper on a mono float32 array. Returns empty string if too short."""
    if len(audio) < SAMPLE_RATE * MIN_DURATION:
        return ""
    result = model.transcribe(audio, language="en", fp16=False)
    return result["text"].strip()


# ── OSC dispatch ──────────────────────────────────────────────────────────────

def _dispatch(cmd: dict, client: SimpleUDPClient) -> None:
    try:
        if cmd["cmd"] == "stop":
            send_stop(client)
        elif cmd["cmd"] == "play_stems":
            send_play_stems(cmd["start"], cmd["end"], cmd["tracks"], client)
        elif cmd["cmd"] == "play_all":
            send_play_all(cmd["start"], cmd["end"], client)
    except ValidationError as e:
        print(f"  Validation error: {e}")


# ── Recording + playback state machine ───────────────────────────────────────

class Controller:
    """
    Thread-safe state machine for recording, ASR, and playback.

    States
    ------
    IDLE       → can start recording or play Full Mix
    RECORDING  → microphone is open; recording ends on on_record_end()
    PROCESSING → ASR + parse running in background thread

    on_stop() is always accepted regardless of current state.

    Request IDs
    -----------
    Each recording session gets a unique _request_id.  on_stop() increments
    it, so the background thread can detect cancellation by comparing its
    captured rid against self._request_id at each checkpoint.
    """

    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"

    def __init__(self, anchor: int | None, model,
                 client: SimpleUDPClient, device: int | None = None):
        self._lock = threading.Lock()
        self._anchor = anchor
        self._model = model
        self._client = client
        self._device = device
        self._state = self.IDLE
        self._stop_evt: threading.Event | None = None
        self._request_id = 0

    # ── anchor ───────────────────────────────────────────────────────────

    @property
    def anchor(self) -> int | None:
        with self._lock:
            return self._anchor

    def set_anchor(self, n: int) -> None:
        with self._lock:
            self._anchor = n
        print(f"\n  anchor_measure → {n}")

    def print_status(self) -> None:
        a = self.anchor
        print(f"\n  anchor_measure = {a if a is not None else '(none)'}"
              f"  |  SPACE=record  1–9=anchor  Q=quit")

    # ── event handlers ───────────────────────────────────────────────────

    def on_record_start(self) -> None:
        """RECORD pressed (or SPACE held) — start push-to-talk recording."""
        with self._lock:
            if self._state == self.RECORDING:
                # Key-repeat or duplicate hardware event — ignore silently.
                return
            if self._state == self.PROCESSING:
                print("  (busy — processing, ignoring RECORD_START)")
                return
            # IDLE → RECORDING
            anchor = self._anchor
            self._request_id += 1
            rid = self._request_id
            evt = threading.Event()
            self._stop_evt = evt
            self._state = self.RECORDING

        # Stop any active playback before opening the microphone.
        try:
            send_stop(self._client)
        except ValidationError:
            pass

        print(f"\n  [REC ▶]  anchor frozen = {anchor}")
        threading.Thread(
            target=self._run_recording,
            args=(evt, anchor, rid),
            daemon=True,
            name=f"recording-{rid}",
        ).start()

    def on_record_end(self) -> None:
        """RECORD released (or SPACE released) — end recording, hand off to ASR."""
        with self._lock:
            if self._state != self.RECORDING:
                # Spurious release after Stop already cancelled the session.
                return
            evt = self._stop_evt
            self._stop_evt = None
            self._state = self.PROCESSING

        if evt:
            evt.set()
        print("  [REC ■]  processing …")

    def on_stop(self) -> None:
        """STOP pressed — send /stop, cancel recording or pending ASR request."""
        with self._lock:
            old_state = self._state
            self._request_id += 1          # invalidate any in-flight request
            if self._stop_evt:
                self._stop_evt.set()
                self._stop_evt = None
            self._state = self.IDLE

        try:
            send_stop(self._client)
        except ValidationError:
            pass

        if old_state == self.RECORDING:
            print("\n  [STOP]  recording cancelled — /stop sent")
        elif old_state == self.PROCESSING:
            print("\n  [STOP]  pending command invalidated — /stop sent")
        else:
            print("\n  [STOP]  /stop sent")

    def on_play(self) -> None:
        """PLAY pressed — play Full Mix from current anchor to measure 16."""
        with self._lock:
            if self._state != self.IDLE:
                print(f"  (busy — {self._state}, ignoring PLAY)")
                return
            anchor = self._anchor

        if anchor is None:
            print("  (no anchor — use --anchor N or digit keys 1–9)")
            return

        try:
            send_play_all(anchor, 16, self._client)
        except ValidationError as e:
            print(f"  Validation error: {e}")

    # ── background recording + ASR thread ────────────────────────────────

    def _run_recording(self, stop_evt: threading.Event,
                       anchor: int | None, rid: int) -> None:
        """
        Record until stop_evt, then run ASR → parse → OSC dispatch.
        Checks request_id at every checkpoint; returns without dispatching
        if on_stop() has been called since this session started.
        """
        audio = _record_until(stop_evt, device=self._device)
        duration = len(audio) / SAMPLE_RATE

        with self._lock:
            if self._request_id != rid:
                print("  (recording cancelled — audio discarded)")
                return

        if duration < MIN_DURATION:
            print(f"  (recording too short: {duration:.2f}s — ignored)")
            with self._lock:
                if self._request_id == rid:
                    self._state = self.IDLE
            return

        rms = float(np.sqrt(np.mean(audio ** 2)))
        print(f"  Transcribing {duration:.1f}s  RMS={rms:.5f} …")
        text = _transcribe(audio, self._model)

        # Stop may have been pressed during ASR inference.
        with self._lock:
            if self._request_id != rid:
                print("  (request cancelled — transcript discarded)")
                return

        if not text:
            print("  (empty transcript)")
            with self._lock:
                if self._request_id == rid:
                    self._state = self.IDLE
            return

        print(f"  Transcript: {text!r}")
        cmd = parse_command(text, anchor)

        if cmd is None:
            print("  Unrecognised — no OSC sent")
            with self._lock:
                if self._request_id == rid:
                    self._state = self.IDLE
            return

        # Final check before dispatch.
        with self._lock:
            if self._request_id != rid:
                print("  (request cancelled — not sending OSC)")
                return
            self._state = self.IDLE

        _dispatch(cmd, self._client)


# ── Serial listener ───────────────────────────────────────────────────────────

def _run_serial_listener(port: str, baud: int,
                         controller: Controller) -> None:
    """
    Daemon thread: read Teensy Serial events and dispatch to controller.

    Handles CRLF line endings and partial-line buffering across read() calls.
    On disconnect, calls on_stop() to cancel any active session.
    Exits the process if the port cannot be opened.
    """
    try:
        import serial as pyserial
    except ImportError:
        print("  Serial: pyserial not installed — run: pip install pyserial",
              file=sys.stderr)
        return

    try:
        ser = pyserial.Serial(port, baud, timeout=0.1)
    except Exception as e:
        print(f"  Serial: cannot open {port}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"  Serial: {port} @ {baud} baud")
    buf = ""
    try:
        while True:
            try:
                raw = ser.read(64)
            except Exception as e:
                print(f"\n  Serial: read error — {e}", file=sys.stderr)
                break
            if not raw:
                continue
            buf += raw.decode("ascii", errors="replace")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()          # removes CR and trailing whitespace
                if not line:
                    continue
                print(f"  [BTN]  {line}")
                if line == "RECORD_START":
                    controller.on_record_start()
                elif line == "RECORD_END":
                    controller.on_record_end()
                elif line == "PLAY":
                    controller.on_play()
                elif line == "STOP":
                    controller.on_stop()
                else:
                    print(f"  [BTN]  unknown event: {line!r} — ignored")
    finally:
        ser.close()
        print("\n  Serial: port closed — cancelling any active session")
        controller.on_stop()


# ── main loop ─────────────────────────────────────────────────────────────────

def run(initial_anchor: int | None, model_name: str,
        device: int | None = None,
        serial_port: str | None = None,
        serial_baud: int = _SERIAL_BAUD_DEFAULT) -> None:
    from pynput import keyboard as kb

    print(f"Loading Whisper '{model_name}' model …")
    import whisper
    model = whisper.load_model(model_name)
    client = SimpleUDPClient(OSC_HOST, OSC_PORT)

    ctrl = Controller(initial_anchor, model, client, device=device)

    if serial_port:
        threading.Thread(
            target=_run_serial_listener,
            args=(serial_port, serial_baud, ctrl),
            daemon=True,
            name="serial-listener",
        ).start()

    ctrl.print_status()
    print(f"  OSC → {OSC_HOST}:{OSC_PORT}\n")

    def on_press(key):
        # SPACE: push-to-talk record
        if key == kb.Key.space:
            ctrl.on_record_start()
            return

        # Digit keys: update anchor
        if hasattr(key, "char") and key.char and key.char.isdigit():
            n = int(key.char)
            if 1 <= n <= 9:
                ctrl.set_anchor(n)

        # Q / Esc: quit
        if key == kb.Key.esc:
            return False
        if hasattr(key, "char") and key.char in ("q", "Q"):
            return False

    def on_release(key):
        if key == kb.Key.space:
            ctrl.on_record_end()

    with kb.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    print("\nQuitting.")


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Voice MVP — hold SPACE or RECORD button to record a playback command"
    )
    p.add_argument("--anchor", type=int, metavar="N", default=None,
                   help="Initial anchor measure (1–16)")
    p.add_argument("--model", default="base",
                   choices=["tiny", "base", "small"],
                   help="Whisper model size (default: base)")
    p.add_argument("--device", type=int, metavar="INDEX", default=None,
                   help="Input device index (see --list-devices)")
    p.add_argument("--list-devices", action="store_true",
                   help="Print available input devices and exit")
    p.add_argument("--serial", metavar="PORT", default=None,
                   help="Teensy Serial port (e.g. /dev/cu.usbmodem154611801)")
    p.add_argument("--baud", type=int, default=_SERIAL_BAUD_DEFAULT,
                   help=f"Serial baud rate (default: {_SERIAL_BAUD_DEFAULT})")
    args = p.parse_args()

    if args.list_devices:
        print("Available input devices:")
        for i, d in enumerate(sd.query_devices()):
            if d["max_input_channels"] > 0:
                default = " ← default" if i == sd.default.device[0] else ""
                print(f"  [{i}] {d['name']}{default}")
        sys.exit(0)

    if args.anchor is not None and not (1 <= args.anchor <= 16):
        print("Error: --anchor must be 1–16", file=sys.stderr)
        sys.exit(1)

    if args.device is not None:
        dev_name = sd.query_devices(args.device)["name"]
        print(f"Input device: [{args.device}] {dev_name}")
    else:
        dev_info = sd.query_devices(kind="input")
        print(f"Input device: [{dev_info['index']}] {dev_info['name']}  "
              f"(use --device to change)")

    run(args.anchor, args.model,
        device=args.device,
        serial_port=args.serial,
        serial_baud=args.baud)


if __name__ == "__main__":
    main()
