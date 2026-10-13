"""
shared_state.py — File-based shared state between camera and voice processes.

The camera process (finger_measure_test.py) writes the current measure;
the voice process (voice_mvp.py) reads it on button press.

File
----
    camera/.measure_state.json   (same directory as this module)

    {"current_measure": 5}   — finger pointing at measure 5
    {"current_measure": null} — hand left frame or camera not running

Both processes import this module; Path(__file__).parent resolves to the
same absolute camera/ directory in both cases.
"""

import json
from pathlib import Path

_STATE_PATH = Path(__file__).parent / ".measure_state.json"


def write_measure(measure: int | None) -> None:
    """
    Write current measure atomically (write-then-replace).
    Silently ignores I/O errors so the camera loop is never interrupted.
    """
    try:
        data = json.dumps({"current_measure": measure})
        tmp = _STATE_PATH.with_suffix(".tmp")
        tmp.write_text(data, encoding="utf-8")
        tmp.replace(_STATE_PATH)
    except Exception:
        pass


def read_measure() -> int | None:
    """
    Read current measure.
    Returns None if the file is absent, malformed, or holds a null value.
    """
    try:
        raw = _STATE_PATH.read_text(encoding="utf-8")
        v = json.loads(raw).get("current_measure")
        return int(v) if v is not None else None
    except Exception:
        return None


def clear() -> None:
    """Remove the state file (e.g., at process exit)."""
    try:
        _STATE_PATH.unlink(missing_ok=True)
    except Exception:
        pass
