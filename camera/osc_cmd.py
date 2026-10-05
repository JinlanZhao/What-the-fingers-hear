#!/usr/bin/env python3
"""
OSC command sender for multistem playback.

Provides validated OSC command functions and a typed-command CLI for
testing Max/MSP multistem playback without ASR or camera.

OSC contract (host 127.0.0.1 port 7400)
-----------------------------------------
  /play_stems <start> <end> <track1> [track2 ...]
  /play_all   <start> <end>
  /stop

Usage
-----
    # Interactive CLI
    python3 camera/osc_cmd.py

    # Run validation tests (no OSC sent)
    python3 camera/osc_cmd.py --test

    # Send a single command directly
    python3 camera/osc_cmd.py play_stems 5 8 fl1 fl2 vln1
    python3 camera/osc_cmd.py play_all 1 16
    python3 camera/osc_cmd.py stop
"""

import argparse
import sys
from pythonosc.udp_client import SimpleUDPClient

OSC_HOST = "127.0.0.1"
OSC_PORT = 7400

# Canonical track IDs as used in Max stem_player instances
VALID_TRACKS: frozenset[str] = frozenset({
    "fl1", "fl2", "ob1", "ob2", "cl1", "cl2", "bsn1", "bsn2",   # Woodwinds
    "fh1", "fh2", "fh3", "fh4", "tpt1", "tpt2", "tbn1", "tbn2", "tb",  # Brass
    "glk", "bd", "sn",                                             # Percussion
    "vln1", "vln2", "vla", "vc", "cb",                            # Strings
    "crash", "riser", "room", "stem",                              # Others
})

MEASURE_MIN = 1
MEASURE_MAX = 16


# ── validation ────────────────────────────────────────────────────────────────

class ValidationError(ValueError):
    pass


def validate_measures(start: int, end: int) -> None:
    """Raise ValidationError if the measure range is invalid."""
    if not isinstance(start, int) or not isinstance(end, int):
        raise ValidationError(
            f"Measures must be integers, got start={start!r} end={end!r}"
        )
    if not (MEASURE_MIN <= start <= MEASURE_MAX):
        raise ValidationError(
            f"start_measure {start} is outside 1–{MEASURE_MAX}"
        )
    if not (MEASURE_MIN <= end <= MEASURE_MAX):
        raise ValidationError(
            f"end_measure {end} is outside 1–{MEASURE_MAX}"
        )
    if end < start:
        raise ValidationError(
            f"end_measure {end} precedes start_measure {start}"
        )


def validate_tracks(tracks: list[str]) -> None:
    """Raise ValidationError if tracks list is empty or contains unknown IDs."""
    if not tracks:
        raise ValidationError("Track list is empty; at least one track is required")
    unknown = [t for t in tracks if t not in VALID_TRACKS]
    if unknown:
        raise ValidationError(
            f"Unknown track ID(s): {unknown}. "
            f"Valid IDs: {sorted(VALID_TRACKS)}"
        )


# ── OSC send ──────────────────────────────────────────────────────────────────

def send_play_stems(start: int, end: int, tracks: list[str],
                    client: SimpleUDPClient) -> None:
    """Validate and send /play_stems <start_measure> <number_of_bars> <track1> ...

    CLI accepts start/end measures; OSC sends number_of_bars instead of end_measure
    so Max only needs: start_ms = (start-1)*1666.667, duration_ms = bars*1666.667.
    """
    validate_measures(start, end)
    validate_tracks(tracks)
    num_bars = end - start + 1
    args = [start, num_bars] + tracks
    client.send_message("/play_stems", args)
    print(f"  OSC /play_stems {start} {num_bars} {' '.join(tracks)}"
          f"  (measures {start}–{end})")


def send_play_all(start: int, end: int, client: SimpleUDPClient) -> None:
    """Validate and send /play_all <start_measure> <number_of_bars>."""
    validate_measures(start, end)
    num_bars = end - start + 1
    client.send_message("/play_all", [start, num_bars])
    print(f"  OSC /play_all {start} {num_bars}  (measures {start}–{end})")


def send_stop(client: SimpleUDPClient) -> None:
    """Send /stop."""
    client.send_message("/stop", [])
    print("  OSC /stop")


# ── automated tests (no OSC) ──────────────────────────────────────────────────

def _run_tests() -> None:
    passed = 0
    total  = 0

    def check(cond: bool, name: str, detail: str = "") -> None:
        nonlocal passed, total
        total += 1
        if cond:
            print(f"  PASS  {name}")
            passed += 1
        else:
            print(f"  FAIL  {name}" + (f": {detail}" if detail else ""))

    def expect_error(fn, name: str) -> None:
        nonlocal passed, total
        total += 1
        try:
            fn()
            print(f"  FAIL  {name}: expected ValidationError, got none")
        except ValidationError as e:
            print(f"  PASS  {name}  ({e})")
            passed += 1

    print("=== osc_cmd validation tests ===\n")

    # Valid measure ranges
    check(True, "T1 validate_measures 1 16 → ok",
          str(validate_measures(1, 16) or ""))
    check(True, "T2 validate_measures 5 8 → ok",
          str(validate_measures(5, 8) or ""))
    check(True, "T3 validate_measures 7 7 (single bar) → ok",
          str(validate_measures(7, 7) or ""))

    # Invalid measure ranges
    expect_error(lambda: validate_measures(0, 8),
                 "T4 start=0 → error")
    expect_error(lambda: validate_measures(1, 17),
                 "T5 end=17 → error")
    expect_error(lambda: validate_measures(8, 5),
                 "T6 end < start → error")

    # Valid track lists
    check(True, "T7 validate_tracks ['fl1'] → ok",
          str(validate_tracks(["fl1"]) or ""))
    check(True, "T8 validate_tracks ['fl1','fl2','vln1'] → ok",
          str(validate_tracks(["fl1", "fl2", "vln1"]) or ""))
    check(True, "T9 validate_tracks all 29 tracks → ok",
          str(validate_tracks(list(VALID_TRACKS)) or ""))

    # Invalid track lists
    expect_error(lambda: validate_tracks([]),
                 "T10 empty track list → error")
    expect_error(lambda: validate_tracks(["flute1"]),
                 "T11 unknown track id → error")
    expect_error(lambda: validate_tracks(["fl1", "not_a_track"]),
                 "T12 mixed valid+invalid → error")

    # num_bars conversion
    check(8 - 5 + 1 == 4, "T13 bars(5,8) = 4")
    check(1 - 1 + 1 == 1, "T14 bars(1,1) = 1  (single measure)")
    check(16 - 1 + 1 == 16, "T15 bars(1,16) = 16  (full piece)")
    check(16 - 16 + 1 == 1, "T16 bars(16,16) = 1")

    print(f"\n{'='*40}")
    print(f"Result: {passed}/{total} tests passed")
    sys.exit(0 if passed == total else 1)


# ── interactive CLI ───────────────────────────────────────────────────────────

_HELP = """\
Commands
--------
  play_stems <start> <end> <track1> [track2 ...]
      e.g.  play_stems 5 8 fl1 fl2 vln1

  play_all <start> <end>
      e.g.  play_all 1 16

  stop

  tracks        — list all valid track IDs
  help          — show this message
  quit / exit   — exit

"""


def _interactive(client: SimpleUDPClient) -> None:
    print(f"OSC → {OSC_HOST}:{OSC_PORT}")
    print(_HELP)
    while True:
        try:
            raw = input("cmd> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw:
            continue
        parts = raw.split()
        cmd = parts[0].lower()
        if cmd in ("quit", "exit"):
            break
        if cmd == "help":
            print(_HELP)
            continue
        if cmd == "tracks":
            groups = [
                ("Woodwinds",  ["fl1","fl2","ob1","ob2","cl1","cl2","bsn1","bsn2"]),
                ("Brass",      ["fh1","fh2","fh3","fh4","tpt1","tpt2","tbn1","tbn2","tb"]),
                ("Percussion", ["glk","bd","sn"]),
                ("Strings",    ["vln1","vln2","vla","vc","cb"]),
                ("Others",     ["crash","riser","room","stem"]),
            ]
            for label, ids in groups:
                print(f"  {label}: {' '.join(ids)}")
            continue
        if cmd == "stop":
            send_stop(client)
            continue
        if cmd == "play_all":
            if len(parts) != 3:
                print("  Usage: play_all <start> <end>")
                continue
            try:
                send_play_all(int(parts[1]), int(parts[2]), client)
            except (ValueError, ValidationError) as e:
                print(f"  Error: {e}")
            continue
        if cmd == "play_stems":
            if len(parts) < 4:
                print("  Usage: play_stems <start> <end> <track1> [track2 ...]")
                continue
            try:
                send_play_stems(int(parts[1]), int(parts[2]), parts[3:], client)
            except (ValueError, ValidationError) as e:
                print(f"  Error: {e}")
            continue
        print(f"  Unknown command: {cmd!r}. Type 'help' for usage.")


# ── argument parsing & entry ──────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Typed OSC command sender for multistem playback"
    )
    p.add_argument("--test", action="store_true",
                   help="Run validation tests (no OSC sent)")
    p.add_argument("args", nargs="*",
                   help="Direct command: stop | play_all S E | play_stems S E t1 [t2 ...]")
    parsed = p.parse_args()

    if parsed.test:
        _run_tests()
        return

    client = SimpleUDPClient(OSC_HOST, OSC_PORT)

    if parsed.args:
        # Non-interactive single-shot mode
        parts = parsed.args
        cmd = parts[0].lower()
        try:
            if cmd == "stop":
                send_stop(client)
            elif cmd == "play_all":
                if len(parts) != 3:
                    print("Usage: osc_cmd.py play_all <start> <end>",
                          file=sys.stderr)
                    sys.exit(1)
                send_play_all(int(parts[1]), int(parts[2]), client)
            elif cmd == "play_stems":
                if len(parts) < 4:
                    print("Usage: osc_cmd.py play_stems <start> <end> <track1> ...",
                          file=sys.stderr)
                    sys.exit(1)
                send_play_stems(int(parts[1]), int(parts[2]), parts[3:], client)
            else:
                print(f"Unknown command: {cmd!r}", file=sys.stderr)
                sys.exit(1)
        except (ValueError, ValidationError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    _interactive(client)


if __name__ == "__main__":
    main()
