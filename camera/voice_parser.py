"""
voice_parser.py — deterministic voice command parser.

Pure functions only; no IO, no ML, no side effects.
Converts a normalised ASR transcript into a structured command dict.

Supported phrases
-----------------
  "stop"
  "play <instruments>"
  "play measures <N> through <M>"
  "play <instruments> measures <N> through <M>"
  "play measures <N> through <M> <instruments>"

Output dicts
------------
  {"cmd": "stop"}
  {"cmd": "play_stems", "start": int, "end": int, "tracks": list[str]}
  {"cmd": "play_all",   "start": int, "end": int}
  None  — unrecognised
"""

import re

# ── number word → int ─────────────────────────────────────────────────────────

_WORD_NUM: dict[str, int] = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16,
}


def _to_int(token: str) -> int | None:
    t = token.strip().lower()
    if t in _WORD_NUM:
        return _WORD_NUM[t]
    try:
        return int(t)
    except ValueError:
        return None


# ── instrument name → track ID ────────────────────────────────────────────────
# Longer multi-word phrases must appear before shorter overlapping ones.

_INSTRUMENTS: list[tuple[str, str, bool]] = [
    # (match phrase,  track prefix or id,  numbered?)
    ("french horn",  "fh",  True),
    ("double bass",  "cb",  False),
    ("contrabass",   "cb",  False),
    ("bass drum",    "bd",  False),
    ("kick drum",    "bd",  False),
    ("snare drum",   "sn",  False),
    ("glockenspiel", "glk", False),
    ("bassoon",      "bsn", True),
    ("clarinet",     "cl",  True),
    ("trumpet",      "tpt", True),
    ("trombone",     "tbn", True),
    ("violin",       "vln", True),
    ("oboe",         "ob",  True),
    ("flute",        "fl",  True),
    ("horn",         "fh",  True),     # must come after "french horn"
    ("viola",        "vla", False),
    ("cello",        "vc",  False),
    ("tuba",         "tb",  False),
    ("snare",        "sn",  False),    # must come after "snare drum"
    ("kick",         "bd",  False),    # must come after "kick drum"
    ("bass",         "cb",  False),    # must come after "double bass" / "bass drum"
    ("bells",        "glk", False),
    ("glock",        "glk", False),
]

# Track IDs that are valid in Max (copied from osc_cmd.py to avoid circular import)
_VALID_TRACKS: frozenset[str] = frozenset({
    "fl1", "fl2", "ob1", "ob2", "cl1", "cl2", "bsn1", "bsn2",
    "fh1", "fh2", "fh3", "fh4", "tpt1", "tpt2", "tbn1", "tbn2", "tb",
    "glk", "bd", "sn",
    "vln1", "vln2", "vla", "vc", "cb",
    "crash", "riser", "room", "stem",
})


def _resolve_instrument(segment: str) -> str | None:
    """
    Match a single instrument phrase to a canonical track ID.
    Returns track ID string or None if no match.
    """
    s = segment.lower().strip()
    for phrase, prefix, numbered in _INSTRUMENTS:
        if phrase not in s:
            continue
        if not numbered:
            return prefix          # e.g. "vla", "tb", "sn"
        # Extract the number that follows the phrase
        rest = s[s.index(phrase) + len(phrase):]
        for token in rest.split():
            n = _to_int(token)
            if n is not None:
                cand = f"{prefix}{n}"
                return cand if cand in _VALID_TRACKS else None
        # No explicit number — default to 1
        cand = f"{prefix}1"
        return cand if cand in _VALID_TRACKS else None
    return None


def extract_tracks(text: str) -> list[str]:
    """
    Extract all track IDs from an instrument list string.
    Splits on 'and' / ',' and matches each segment independently.
    Duplicate track IDs are removed while preserving order.
    """
    segments = re.split(r"\band\b|,", text, flags=re.IGNORECASE)
    seen: set[str] = set()
    tracks: list[str] = []
    for seg in segments:
        tid = _resolve_instrument(seg.strip())
        if tid and tid not in seen:
            tracks.append(tid)
            seen.add(tid)
    return tracks


# ── measure range extraction ──────────────────────────────────────────────────

_RANGE_RE = re.compile(
    r"measures?\s+(\w+)\s+(?:through|thru|to|-)\s+(\w+)",
    re.IGNORECASE,
)


def _extract_measure_range(text: str) -> tuple[int | None, int | None, str]:
    """
    Find and remove a measure range expression from text.
    Returns (start, end, remaining_text).
    """
    m = _RANGE_RE.search(text)
    if not m:
        return None, None, text
    start = _to_int(m.group(1))
    end   = _to_int(m.group(2))
    if start is None or end is None:
        return None, None, text
    remaining = (text[: m.start()] + text[m.end() :]).strip()
    return start, end, remaining


# ── top-level parse ───────────────────────────────────────────────────────────

def parse_command(
    text: str,
    anchor_measure: int | None,
) -> dict | None:
    """
    Parse an ASR transcript into a command dict.

    Parameters
    ----------
    text : str
        Raw transcript from ASR (not yet normalised).
    anchor_measure : int | None
        The measure currently pointed at, frozen at recording start.
        Used as start measure when no range appears in the phrase.
        If None and no range is specified, returns None (no context).

    Returns
    -------
    dict | None
        {"cmd": "stop"}
        {"cmd": "play_stems", "start": int, "end": int, "tracks": list[str]}
        {"cmd": "play_all",   "start": int, "end": int}
        None if unrecognised.
    """
    t = text.lower().strip().rstrip(".,!?")

    # ── stop ──────────────────────────────────────────────────────────────
    if re.fullmatch(r"stop(?:\s+playing)?", t):
        return {"cmd": "stop"}

    # ── play ──────────────────────────────────────────────────────────────
    if not t.startswith("play"):
        return None
    rest = t[4:].strip()

    # Extract measure range (removes it from rest)
    start, end, rest = _extract_measure_range(rest)

    # Extract instrument list from what remains
    tracks = extract_tracks(rest)

    if not tracks:
        # "play measures N through M" with no instruments stated
        if start is not None:
            return {"cmd": "play_all", "start": start, "end": end}
        return None  # bare "play" → unrecognised

    # No measure range given → use anchor context
    if start is None:
        if anchor_measure is None:
            return None
        start = anchor_measure
        end   = 16

    return {"cmd": "play_stems", "start": start, "end": end, "tracks": tracks}
