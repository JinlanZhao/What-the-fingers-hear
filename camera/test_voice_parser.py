#!/usr/bin/env python3
"""
Automated tests for voice_parser.py.

Covers: stop, play instruments, play range, play instruments+range,
        ASR digit/word variations, ordering of multi-instrument lists,
        unrecognised inputs, missing anchor context.

Usage:
    python3 camera/test_voice_parser.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from voice_parser import parse_command, extract_tracks, _resolve_instrument

passed = 0
total  = 0


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


print("=== voice_parser tests ===\n")

# ── _resolve_instrument ───────────────────────────────────────────────────────

eq(_resolve_instrument("flute one"),    "fl1",  "instr: flute one → fl1")
eq(_resolve_instrument("flute two"),    "fl2",  "instr: flute two → fl2")
eq(_resolve_instrument("flute 1"),      "fl1",  "instr: flute 1 (digit) → fl1")
eq(_resolve_instrument("violin one"),   "vln1", "instr: violin one → vln1")
eq(_resolve_instrument("violin two"),   "vln2", "instr: violin two → vln2")
eq(_resolve_instrument("viola"),        "vla",  "instr: viola (no number) → vla")
eq(_resolve_instrument("cello"),        "vc",   "instr: cello → vc")
eq(_resolve_instrument("tuba"),         "tb",   "instr: tuba → tb")
eq(_resolve_instrument("double bass"),  "cb",   "instr: double bass → cb")
eq(_resolve_instrument("contrabass"),   "cb",   "instr: contrabass → cb")
eq(_resolve_instrument("bass"),         "cb",   "instr: bass (defaults to cb) → cb")
eq(_resolve_instrument("bass drum"),    "bd",   "instr: bass drum → bd")
eq(_resolve_instrument("kick drum"),    "bd",   "instr: kick drum → bd")
eq(_resolve_instrument("kick"),         "bd",   "instr: kick → bd")
eq(_resolve_instrument("snare drum"),   "sn",   "instr: snare drum → sn")
eq(_resolve_instrument("snare"),        "sn",   "instr: snare → sn")
eq(_resolve_instrument("glockenspiel"), "glk",  "instr: glockenspiel → glk")
eq(_resolve_instrument("bells"),        "glk",  "instr: bells → glk")
eq(_resolve_instrument("glock"),        "glk",  "instr: glock → glk")
eq(_resolve_instrument("trumpet one"),  "tpt1", "instr: trumpet one → tpt1")
eq(_resolve_instrument("trumpet two"),  "tpt2", "instr: trumpet two → tpt2")
eq(_resolve_instrument("trombone one"), "tbn1", "instr: trombone one → tbn1")
eq(_resolve_instrument("horn one"),     "fh1",  "instr: horn one → fh1")
eq(_resolve_instrument("french horn one"), "fh1", "instr: french horn one → fh1")
eq(_resolve_instrument("bassoon one"),  "bsn1", "instr: bassoon one → bsn1")
eq(_resolve_instrument("oboe one"),     "ob1",  "instr: oboe one → ob1")
eq(_resolve_instrument("clarinet one"), "cl1",  "instr: clarinet one → cl1")
eq(_resolve_instrument("piano"),        None,   "instr: piano (unknown) → None")

# ── extract_tracks ────────────────────────────────────────────────────────────

eq(extract_tracks("flute one"),                     ["fl1"],
   "tracks: single instrument")
eq(extract_tracks("flute one and violin one"),       ["fl1", "vln1"],
   "tracks: two instruments")
eq(extract_tracks("flute one, violin one"),          ["fl1", "vln1"],
   "tracks: comma-separated")
eq(extract_tracks("flute one and violin one and viola"), ["fl1", "vln1", "vla"],
   "tracks: three instruments")
eq(extract_tracks("violin one and violin one"),      ["vln1"],
   "tracks: duplicate removed")
eq(extract_tracks("cello and tuba and snare"),       ["vc", "tb", "sn"],
   "tracks: unnumbered instruments")

# ── parse_command: stop ───────────────────────────────────────────────────────

eq(parse_command("stop", None),          {"cmd": "stop"}, "cmd: stop")
eq(parse_command("Stop.", None),         {"cmd": "stop"}, "cmd: Stop. (trailing punct)")
eq(parse_command("stop playing", None),  {"cmd": "stop"}, "cmd: stop playing")

# ── parse_command: play instruments (anchor used) ────────────────────────────

eq(parse_command("play flute one", 7),
   {"cmd": "play_stems", "start": 7, "end": 16, "tracks": ["fl1"]},
   "cmd: play flute one → anchor=7")

eq(parse_command("play flute one and violin one", 5),
   {"cmd": "play_stems", "start": 5, "end": 16, "tracks": ["fl1", "vln1"]},
   "cmd: play flute one and violin one → anchor=5")

eq(parse_command("play viola", 1),
   {"cmd": "play_stems", "start": 1, "end": 16, "tracks": ["vla"]},
   "cmd: play viola → anchor=1")

# No anchor → None
eq(parse_command("play flute one", None), None,
   "cmd: play flute one, no anchor → None")

# ── parse_command: play range only ───────────────────────────────────────────

eq(parse_command("play measures five through eight", None),
   {"cmd": "play_all", "start": 5, "end": 8},
   "cmd: play measures five through eight → play_all")

eq(parse_command("play measures 5 through 8", None),
   {"cmd": "play_all", "start": 5, "end": 8},
   "cmd: play measures 5 through 8 (digit) → play_all")

eq(parse_command("play measures one to sixteen", None),
   {"cmd": "play_all", "start": 1, "end": 16},
   "cmd: play measures one to sixteen → play_all")

# ── parse_command: play instruments + range ──────────────────────────────────

eq(parse_command("play flute one measures five through eight", None),
   {"cmd": "play_stems", "start": 5, "end": 8, "tracks": ["fl1"]},
   "cmd: instruments + range, no anchor needed")

eq(parse_command("play measures five through eight flute one and violin one", None),
   {"cmd": "play_stems", "start": 5, "end": 8, "tracks": ["fl1", "vln1"]},
   "cmd: range before instruments")

eq(parse_command("play violin one and viola measures three through twelve", None),
   {"cmd": "play_stems", "start": 3, "end": 12, "tracks": ["vln1", "vla"]},
   "cmd: multiple instruments + range")

# range overrides anchor
eq(parse_command("play flute one measures two through four", 9),
   {"cmd": "play_stems", "start": 2, "end": 4, "tracks": ["fl1"]},
   "cmd: explicit range overrides anchor")

# ── parse_command: ASR capitalisation / trailing punctuation ─────────────────

eq(parse_command("Play Flute One.", 3),
   {"cmd": "play_stems", "start": 3, "end": 16, "tracks": ["fl1"]},
   "cmd: capitalised Whisper output")

eq(parse_command("Play flute 1 and violin 2.", 3),
   {"cmd": "play_stems", "start": 3, "end": 16, "tracks": ["fl1", "vln2"]},
   "cmd: digit numbers from ASR")

# ── parse_command: unrecognised ───────────────────────────────────────────────

eq(parse_command("", None),              None, "cmd: empty string → None")
eq(parse_command("hello", None),         None, "cmd: random phrase → None")
eq(parse_command("play", None),          None, "cmd: bare 'play' → None")
eq(parse_command("play piano", 1),       None, "cmd: unknown instrument → None")

# ── summary ───────────────────────────────────────────────────────────────────

print(f"\n{'='*40}")
print(f"Result: {passed}/{total} tests passed")
sys.exit(0 if passed == total else 1)
