"""Read-only voice answers and rest feedback from the score's real metadata."""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent.parent
TRACKS_PATH = ROOT / "data" / "tracks.json"
SCORE_PATH = ROOT / "Score-prep" / "Score_Bars16_4-4_144bpm.musicxml"


def _score_tracks() -> list[dict]:
    return [t for t in json.loads(TRACKS_PATH.read_text())["tracks"]
            if t["role"] == "score"]


def _name(track: dict) -> str:
    name = re.sub(r"\s*\([^)]*\)", "", track["musicxml_part_name"])
    return " ".join(name.split()).replace("Violoncello", "Cello")


def answer_query(text: str, measure: int | None) -> str | None:
    """Answer supported position/inventory questions; leave playback text alone."""
    text = " ".join(text.lower().strip(" .,!?").split())
    # These refer to transport position, which Python does not receive from Max.
    if re.search(r"\b(playing|playback)\b", text):
        return None
    is_measure = (
        re.match(r"(?:what|which)(?:'s| is)?\s+(?:(?:the|my|current|selected)\s+)*"
                 r"(?:measure|bar|position)\b", text)
        or re.match(r"where am i\b", text)
        or (re.match(r"(?:tell me|(?:can|could) you tell me)\b", text)
            and re.search(r"\b(measure|bar|position)\b", text))
    )
    if is_measure:
        if measure is None:
            return "No measure is selected. Please point at a measure first."
        return f"Your selected measure is {measure}."

    is_inventory = (
        re.match(r"(?:what|which)\b", text)
        or re.match(r"(?:list|show me|tell me|(?:can|could) you (?:list|tell me))\b", text)
    ) and re.search(r"\b(instruments|parts)\b", text)
    if is_inventory:
        try:
            names = [_name(t) for t in _score_tracks()]
        except (OSError, ValueError, KeyError):
            return "I can't read the instrument list right now."
        return "You can choose: " + ", ".join(names) + "."
    return None


def rest_feedback(command: dict) -> str | None:
    """Report selected parts with no notes in the starting measure.

    This is advisory only: it never edits or suppresses the playback command.
    Missing score metadata is not evidence that an instrument is resting.
    """
    if command["cmd"] != "play_stems":
        return None
    start = command["start"]
    try:
        parts = {p.get("id"): p for p in ET.parse(SCORE_PATH).getroot().findall("part")}
        tracks = {t["slug"].rsplit("_", 1)[-1]: t for t in _score_tracks()}
    except (OSError, ValueError, KeyError, ET.ParseError):
        return "I can't determine the instrument activity right now."

    resting = []
    for track_id in command["tracks"]:
        track = tracks.get(track_id)
        if track is None:  # Effects have no corresponding score part.
            continue
        part = parts.get(track["musicxml_part_id"])
        if part is None:
            continue
        notes = part.findall(f"measure[@number='{start}']/note")
        if notes and all(note.find("rest") is not None for note in notes):
            resting.append(_name(track))
    if not resting:
        return None
    return ", ".join(resting) + f": no notes in measure {start}."
