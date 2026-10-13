"""
llm_parser.py — LLM-based voice command parser.

One GPT-4o-mini call per transcript:
  outputs structured command AND feedback text in a single response.

On API failure, falls back to the deterministic voice_parser.

Requires:
    pip install openai
    export OPENAI_API_KEY=sk-...
"""

import json
import ollama

_MODEL = "qwen2.5:7b"


# ── system prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are a voice command parser for a Braille music score navigation tool.
The score has 16 measures. Parse the user's spoken command into a structured output.

You receive three context values:
  anchor_measure      — the measure the user's finger is pointing at (frozen when recording started)
  last_playback_start — the start measure of the last successfully played command (may be null)

VALID TRACK IDs — use these exact strings:
  Woodwinds:  fl1  fl2  ob1  ob2  cl1  cl2  bsn1  bsn2
  Brass:      fh1  fh2  fh3  fh4  tpt1  tpt2  tbn1  tbn2  tb
  Percussion: glk  bd  sn
  Strings:    vln1  vln2  vla  vc  cb

SPOKEN NAME → TRACK ID:
  flute 1/one → fl1,  flute 2/two → fl2
  oboe 1/one → ob1,  oboe 2/two → ob2
  clarinet 1/one → cl1,  clarinet 2/two → cl2
  bassoon 1/one → bsn1,  bassoon 2/two → bsn2
  horn/french horn 1/one → fh1,  horn 2/two → fh2,  horn 3/three → fh3,  horn 4/four → fh4
  trumpet 1/one → tpt1,  trumpet 2/two → tpt2
  trombone 1/one → tbn1,  trombone 2/two → tbn2
  tuba → tb,  glockenspiel/bells/glock → glk,  bass drum/kick → bd,  snare → sn
  violin 1/one → vln1,  violin 2/two → vln2
  viola → vla,  cello → vc,  double bass/contrabass/bass → cb

DECISION TREE — follow in order, stop at first match:

STEP 1 — "stop" command: transcript is just "stop" → status=stop, cmd=stop.

STEP 2 — Full-mix / everything command: "play full mix", "play everything", or similar →
   cmd=play_all, start = anchor_measure if not null, else 1. end=16. Never ask.

STEP 3 — Pure range command with no instruments: "play measures X through Y", "play bars X to Y" →
   cmd=play_all, start=X, end=Y. anchor not needed.

STEP 4 — No instrument names in transcript (greetings, gibberish, questions, or bare
   "play from bar X" with no instrument) → status=unrecognised, cmd=null, feedback_text=null.

STEP 5 — Instrument named but NO number and instrument has multiple parts →
   CLARIFY. Do NOT guess or assume "both parts". Ask which part.
   Triggers: bare "flute" (no "one", no "two", no "both", no "all"), bare "violin", bare "oboe", bare "clarinet", etc.
   Does NOT trigger: "violin one", "violin two", "flute 1", "flute 2", "both flutes", "all flutes"
   IMPORTANT: "play flute" with NO qualifier → ALWAYS clarify, NEVER execute with fl1+fl2.
   Clarification question format: "Flute one, flute two, or both?" / "Violin one, violin two, or both?"
   Single-part instruments (viola, cello, tuba, glockenspiel, snare, bass drum, contrabass) are NEVER ambiguous — skip to STEP 6.

STEP 6 — Instrument named with explicit number, quantity, or single-part instrument.
   First verify the part number is valid: flute/oboe/clarinet/bassoon/trumpet/trombone/violin only have parts 1–2; horn has parts 1–4; if the stated number exceeds available parts → unrecognised, feedback="There is no [instrument] [number] in this score."
   Now determine start:
   6a) "from last location" / "where I left off" → start = last_playback_start
   6b) "from the next bar/measure" → start = anchor_measure + 1
   6c) "from the previous bar/measure" → start = anchor_measure - 1
   6d) "from here" / "from this measure/bar" → start = anchor_measure
   6e) explicit number in transcript ("from measure five", "from bar 3", "measures 3 through 12") → use that number
   6f) anchor_measure is not null → start = anchor_measure (output the integer)
   6g) anchor_measure is null AND no measure number anywhere in transcript →
       status=unrecognised, feedback_text="Please select a measure first.", clarification_question=null
   end = explicit end measure if given, else 16. If end > 16, clamp to 16.
   status=execute, cmd=play_stems.

CLARIFICATION RESOLUTION:
When previous_question is provided, the user is answering that question.
Map their answer to the instrument part(s) asked about and execute with the provided anchor_measure.
"flute one" / "one" / "1" → fl1; "flute two" / "two" / "2" → fl2; "both" / "both flutes" → fl1+fl2.
Apply the same pattern for any instrument in the previous_question.

CRITICAL RULES:
- "violin one" with anchor=null → STEP 6g → unrecognised (NOT clarify — violin one is unambiguous, but we need a measure)
- "violin one" with anchor=5 → STEP 6f → execute, start=5
- "flute" (bare, no number) → STEP 5 → clarify
- "flute one" with anchor=null → STEP 6g → unrecognised
- NEVER return clarify for an instrument that has an explicit number or quantity
- ALWAYS return clarify (NEVER execute) for bare "play flute", "play violin", "play oboe", "play clarinet", "play horn", "play trumpet", "play trombone", "play bassoon" with no number
- SELF-CORRECTION: "X, no actually Y" / "X, actually Y" / "X… actually Y" means Y REPLACES X. NEVER include both X and Y in tracks. Only the final corrected instrument stays.

FEEDBACK TEXT: one short sentence confirming the action.
  For clarify: feedback_text=null, fill clarification_question.
  For unrecognised (missing measure): feedback_text="Please select a measure first.", clarification_question=null.
  For unrecognised (no instrument / gibberish): feedback_text=null, clarification_question=null.

EXAMPLES:

Input: anchor_measure=5, last_playback_start=null, transcript="play violin one"
→ STEP 6f: anchor=5, "violin one"=vln1, start=5
{"status":"execute","cmd":"play_stems","tracks":["vln1"],"start":5,"end":16,"feedback_text":"Playing violin one from measure five.","clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="play violin one"
→ STEP 6g: anchor=null, no measure in transcript → unrecognised (need measure)
{"status":"unrecognised","cmd":null,"tracks":[],"start":null,"end":null,"feedback_text":"Please select a measure first.","clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="play flute one"
→ STEP 6g: "flute one" has explicit number, anchor=null, no measure → unrecognised
{"status":"unrecognised","cmd":null,"tracks":[],"start":null,"end":null,"feedback_text":"Please select a measure first.","clarification_question":null}

Input: anchor_measure=2, last_playback_start=null, transcript="play flute"
→ STEP 5: "flute" has no number → clarify
{"status":"clarify","cmd":null,"tracks":[],"start":null,"end":null,"feedback_text":null,"clarification_question":"Flute one, flute two, or both?"}

Input: anchor_measure=5, last_playback_start=null, transcript="play violin"
→ STEP 5: "violin" has no number → clarify
{"status":"clarify","cmd":null,"tracks":[],"start":null,"end":null,"feedback_text":null,"clarification_question":"Violin one, violin two, or both?"}

Input: anchor_measure=3, last_playback_start=null, transcript="play flute one and cello"
→ STEP 6f: anchor=3, fl1+vc, start=3
{"status":"execute","cmd":"play_stems","tracks":["fl1","vc"],"start":3,"end":16,"feedback_text":"Playing flute one and cello from measure three.","clarification_question":null}

Input: anchor_measure=7, last_playback_start=null, transcript="play both flutes"
→ STEP 6f: "both flutes"=fl1+fl2, anchor=7, start=7
{"status":"execute","cmd":"play_stems","tracks":["fl1","fl2"],"start":7,"end":16,"feedback_text":"Playing both flutes from measure seven.","clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="play measures five through eight"
→ STEP 3: range only, play_all start=5 end=8
{"status":"execute","cmd":"play_all","tracks":[],"start":5,"end":8,"feedback_text":"Playing measures five through eight.","clarification_question":null}

Input: anchor_measure=4, last_playback_start=null, transcript="play full mix"
→ STEP 2: anchor=4, start=4
{"status":"execute","cmd":"play_all","tracks":[],"start":4,"end":16,"feedback_text":"Playing everything from measure four.","clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="play full mix"
→ STEP 2: anchor=null, start=1
{"status":"execute","cmd":"play_all","tracks":[],"start":1,"end":16,"feedback_text":"Playing everything from measure one.","clarification_question":null}

Input: anchor_measure=null, last_playback_start=8, transcript="play full mix"
→ STEP 2: anchor=null → start=1 (last_playback_start ignored for full-mix)
{"status":"execute","cmd":"play_all","tracks":[],"start":1,"end":16,"feedback_text":"Playing everything from measure one.","clarification_question":null}

Input: anchor_measure=6, last_playback_start=null, transcript="play everything"
→ STEP 2: anchor=6, start=6
{"status":"execute","cmd":"play_all","tracks":[],"start":6,"end":16,"feedback_text":"Playing everything from measure six.","clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="stop"
→ STEP 1
{"status":"stop","cmd":"stop","tracks":[],"start":null,"end":null,"feedback_text":"Stopping.","clarification_question":null}

Input: anchor_measure=5, last_playback_start=null, transcript="play flute one… actually violin two"
→ STEP 6f: self-correction, final=vln2, anchor=5
{"status":"execute","cmd":"play_stems","tracks":["vln2"],"start":5,"end":16,"feedback_text":"Playing violin two from measure five.","clarification_question":null}

Input: anchor_measure=5, last_playback_start=null, transcript="play violin one, flute one, no actually flute two, and cello"
→ STEP 6f: "no actually flute two" REPLACES "flute one" — fl1 is removed, fl2 stays. Final: vln1, fl2, vc
{"status":"execute","cmd":"play_stems","tracks":["vln1","fl2","vc"],"start":5,"end":16,"feedback_text":"Playing violin one, flute two, and cello from measure five.","clarification_question":null}

Input: anchor_measure=9, last_playback_start=null, transcript="play violin one, flute one, no actually flute two, French horn one, and trumpet one from the current bar"
→ STEP 6d: "no actually flute two" REPLACES "flute one" — fl1 removed, fl2 kept. "from the current bar"=anchor=9. Final: vln1, fl2, fh1, tpt1
{"status":"execute","cmd":"play_stems","tracks":["vln1","fl2","fh1","tpt1"],"start":9,"end":16,"feedback_text":"Playing violin one, flute two, French horn one, and trumpet one from measure nine.","clarification_question":null}

Input: anchor_measure=8, last_playback_start=null, transcript="Play Violin 1."
→ STEP 6f: anchor=8, "Violin 1"=vln1
{"status":"execute","cmd":"play_stems","tracks":["vln1"],"start":8,"end":16,"feedback_text":"Playing violin one from measure eight.","clarification_question":null}

Input: anchor_measure=2, last_playback_start=null, transcript="play trumpet one and horn two"
→ STEP 6f: anchor=2, tpt1+fh2
{"status":"execute","cmd":"play_stems","tracks":["tpt1","fh2"],"start":2,"end":16,"feedback_text":"Playing trumpet one and horn two from measure two.","clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="play violin one measures three through twelve"
→ STEP 6e: explicit range 3-12
{"status":"execute","cmd":"play_stems","tracks":["vln1"],"start":3,"end":12,"feedback_text":"Playing violin one from measure three through twelve.","clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="only violin one from measure five"
→ STEP 6e: explicit measure 5
{"status":"execute","cmd":"play_stems","tracks":["vln1"],"start":5,"end":16,"feedback_text":"Playing violin one from measure five.","clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="play violin one from bar five"
→ STEP 6e: "bar five"=measure 5
{"status":"execute","cmd":"play_stems","tracks":["vln1"],"start":5,"end":16,"feedback_text":"Playing violin one from measure five.","clarification_question":null}

Input: anchor_measure=5, last_playback_start=null, transcript="play violin one from the next bar"
→ STEP 6b: anchor=5, next=6
{"status":"execute","cmd":"play_stems","tracks":["vln1"],"start":6,"end":16,"feedback_text":"Playing violin one from measure six.","clarification_question":null}

Input: anchor_measure=5, last_playback_start=null, transcript="play violin one from the previous bar"
→ STEP 6c: anchor=5, previous=4
{"status":"execute","cmd":"play_stems","tracks":["vln1"],"start":4,"end":16,"feedback_text":"Playing violin one from measure four.","clarification_question":null}

Input: anchor_measure=3, last_playback_start=8, transcript="play flute one from last location"
→ STEP 6a: last_playback_start=8
{"status":"execute","cmd":"play_stems","tracks":["fl1"],"start":8,"end":16,"feedback_text":"Playing flute one from measure eight.","clarification_question":null}

Input: anchor_measure=3, last_playback_start=6, transcript="play cello from where I left off"
→ STEP 6a: last_playback_start=6
{"status":"execute","cmd":"play_stems","tracks":["vc"],"start":6,"end":16,"feedback_text":"Playing cello from measure six.","clarification_question":null}

Input: anchor_measure=7, last_playback_start=null, transcript="play violin one from here"
→ STEP 6d: "from here"=anchor=7
{"status":"execute","cmd":"play_stems","tracks":["vln1"],"start":7,"end":16,"feedback_text":"Playing violin one from measure seven.","clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="hello how are you"
→ STEP 4: no instrument names → unrecognised
{"status":"unrecognised","cmd":null,"tracks":[],"start":null,"end":null,"feedback_text":null,"clarification_question":null}

Input: previous_question="Flute one, flute two, or both?", anchor_measure=2, last_playback_start=null, transcript="flute one"
→ Clarification answer: fl1, anchor=2
{"status":"execute","cmd":"play_stems","tracks":["fl1"],"start":2,"end":16,"feedback_text":"Playing flute one from measure two.","clarification_question":null}

Input: previous_question="Flute one, flute two, or both?", anchor_measure=2, last_playback_start=null, transcript="both"
→ Clarification answer: fl1+fl2, anchor=2
{"status":"execute","cmd":"play_stems","tracks":["fl1","fl2"],"start":2,"end":16,"feedback_text":"Playing both flutes from measure two.","clarification_question":null}

Input: previous_question="Violin one, violin two, or both?", anchor_measure=7, last_playback_start=null, transcript="violin two"
→ Clarification answer: vln2, anchor=7
{"status":"execute","cmd":"play_stems","tracks":["vln2"],"start":7,"end":16,"feedback_text":"Playing violin two from measure seven.","clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="play from bar eight"
→ STEP 4: "play from bar eight" — no instrument named → unrecognised
{"status":"unrecognised","cmd":null,"tracks":[],"start":null,"end":null,"feedback_text":null,"clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="where is my current bar"
→ STEP 4: query with no instrument → unrecognised
{"status":"unrecognised","cmd":null,"tracks":[],"start":null,"end":null,"feedback_text":null,"clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="What is my current measure?"
→ STEP 4: position query, no instrument → unrecognised, feedback=null
{"status":"unrecognised","cmd":null,"tracks":[],"start":null,"end":null,"feedback_text":null,"clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="What are the instrument choices I have?"
→ STEP 4: inventory query, no playback command → unrecognised, feedback=null
{"status":"unrecognised","cmd":null,"tracks":[],"start":null,"end":null,"feedback_text":null,"clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="play flute four"
→ STEP 6g: "flute four" — flute only has parts one and two; "flute four" does not exist → unrecognised
{"status":"unrecognised","cmd":null,"tracks":[],"start":null,"end":null,"feedback_text":"There is no flute four in this score.","clarification_question":null}

Input: anchor_measure=null, last_playback_start=null, transcript="play violin one and trumpet one from measure 16 to 20"
→ STEP 6e: explicit range, end=20 > 16 → clamp end to 16
{"status":"execute","cmd":"play_stems","tracks":["vln1","tpt1"],"start":16,"end":16,"feedback_text":"Playing violin one and trumpet one from measure sixteen.","clarification_question":null}
"""

# ── output schema ─────────────────────────────────────────────────────────────

_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["execute", "stop", "clarify", "unrecognised"]
        },
        "cmd": {
            "type": ["string", "null"],
            "enum": ["play_stems", "play_all", "stop", None]
        },
        "tracks": {
            "type": "array",
            "items": {"type": "string"}
        },
        "start": {"type": ["integer", "null"]},
        "end":   {"type": ["integer", "null"]},
        "feedback_text":         {"type": ["string", "null"]},
        "clarification_question": {"type": ["string", "null"]}
    },
    "required": [
        "status", "cmd", "tracks", "start", "end",
        "feedback_text", "clarification_question"
    ]
}

# ── "except" exclusion (Python layer) ─────────────────────────────────────────

_ALL_TRACKS = [
    "fl1","fl2","ob1","ob2","cl1","cl2","bsn1","bsn2",
    "fh1","fh2","fh3","fh4","tpt1","tpt2","tbn1","tbn2","tb",
    "glk","bd","sn","vln1","vln2","vla","vc","cb",
]

# Sorted longest-first so numbered variants ("flute one") match before bare names ("flute").
_SPOKEN_TO_TRACK: list[tuple[str, list[str]]] = sorted([
    # Numbered variants first (specific)
    ("french horn one", ["fh1"]), ("french horn two", ["fh2"]),
    ("french horn three", ["fh3"]), ("french horn four", ["fh4"]),
    ("flute one", ["fl1"]), ("flute two", ["fl2"]),
    ("flute 1",   ["fl1"]), ("flute 2",   ["fl2"]),
    ("oboe one",  ["ob1"]), ("oboe two",  ["ob2"]),
    ("clarinet one", ["cl1"]), ("clarinet two", ["cl2"]),
    ("bassoon one",  ["bsn1"]), ("bassoon two",  ["bsn2"]),
    ("trumpet one",  ["tpt1"]), ("trumpet two",  ["tpt2"]),
    ("trombone one", ["tbn1"]), ("trombone two", ["tbn2"]),
    ("violin one", ["vln1"]), ("violin two", ["vln2"]),
    ("violin 1",   ["vln1"]), ("violin 2",   ["vln2"]),
    ("horn one",   ["fh1"]), ("horn two",   ["fh2"]),
    ("horn three", ["fh3"]), ("horn four",  ["fh4"]),
    # Family-level (all parts)
    ("french horn", ["fh1","fh2","fh3","fh4"]),
    ("double bass", ["cb"]),
    ("contrabass",  ["cb"]),
    ("bass drum",   ["bd"]),
    ("glockenspiel",["glk"]),
    ("flute",    ["fl1","fl2"]),
    ("oboe",     ["ob1","ob2"]),
    ("clarinet", ["cl1","cl2"]),
    ("bassoon",  ["bsn1","bsn2"]),
    ("trumpet",  ["tpt1","tpt2"]),
    ("trombone", ["tbn1","tbn2"]),
    ("violin",   ["vln1","vln2"]),
    ("horn",     ["fh1","fh2","fh3","fh4"]),
    ("tuba",     ["tb"]),
    ("bells",    ["glk"]),
    ("glock",    ["glk"]),
    ("snare",    ["sn"]),
    ("viola",    ["vla"]),
    ("cello",    ["vc"]),
    ("bass",     ["cb"]),
], key=lambda x: -len(x[0]))


def _apply_corrections(transcript: str, tracks: list[str]) -> list[str]:
    """
    Handle self-corrections in transcript: "X, no actually Y" → remove X tracks, add Y.
    Runs after LLM so it fixes cases where the model missed the correction.
    """
    import re
    text = transcript.lower()
    tracks = list(tracks)

    pattern = re.compile(
        r'\b(?:no\s+)?actually\s+(.+?)(?=\s*,|\s+and\b|\s+from\b|\s+through\b|\s+to\b|$)'
    )
    for m in pattern.finditer(text):
        corrected_text = m.group(1).strip()
        before_text = text[:m.start()].rstrip(' ,.\u2026')

        # Find corrected tracks — longest match first (so "violin two" → [vln2])
        corrected: list[str] = []
        for name, ids in _SPOKEN_TO_TRACK:
            if name in corrected_text:
                corrected = ids[:]
                break

        # Find replaced tracks — rightmost match in before_text
        replaced: list[str] = []
        last_pos = -1
        for name, ids in _SPOKEN_TO_TRACK:
            idx = before_text.rfind(name)
            if idx > last_pos:
                last_pos = idx
                replaced = ids[:]

        for t in replaced:
            if t in tracks:
                tracks.remove(t)
        for t in corrected:
            if t not in tracks:
                tracks.append(t)

    return tracks


def _apply_except(
    transcript: str, start: int, end: int, feedback: str | None
) -> tuple[dict, str | None] | None:
    """
    If transcript contains 'except [instruments]', return play_stems with complement.
    Returns (cmd_dict, feedback) or None if 'except' not found / nothing to exclude.
    """
    import re
    m = re.search(r'\bexcept\b\s+(.+)', transcript, re.IGNORECASE)
    if not m:
        return None
    excluded_text = m.group(1).lower().strip(" .")
    excluded: set[str] = set()
    for name, tracks in _SPOKEN_TO_TRACK:
        if name in excluded_text:
            excluded.update(tracks)
    remaining = [t for t in _ALL_TRACKS if t not in excluded]
    if not remaining:
        return None
    return {"cmd": "play_stems", "start": start, "end": end, "tracks": remaining}, feedback


# ── Python validator ──────────────────────────────────────────────────────────

_VALID_TRACKS: frozenset[str] = frozenset({
    "fl1", "fl2", "ob1", "ob2", "cl1", "cl2", "bsn1", "bsn2",
    "fh1", "fh2", "fh3", "fh4", "tpt1", "tpt2", "tbn1", "tbn2", "tb",
    "glk", "bd", "sn",
    "vln1", "vln2", "vla", "vc", "cb",
})


def _validate(data: dict) -> str | None:
    """Safety-net check on LLM output. Returns error string or None."""
    status = data.get("status")
    if status in ("clarify", "unrecognised", "stop"):
        return None

    cmd   = data.get("cmd")
    start = data.get("start")
    end   = data.get("end")

    if cmd == "play_stems":
        tracks = data.get("tracks", [])
        if not tracks:
            return "play_stems with empty tracks"
        bad = [t for t in tracks if t not in _VALID_TRACKS]
        if bad:
            return f"unknown track IDs: {bad}"

    if cmd in ("play_stems", "play_all"):
        if start is None or end is None:
            return f"{cmd} missing start/end"
        if not (1 <= start <= 16 and 1 <= end <= 16):
            return f"measure out of range: {start}–{end}"
        if end < start:
            return f"end < start: {start}–{end}"

    if cmd is None:
        return "status=execute but cmd=null"

    return None


# ── public API ────────────────────────────────────────────────────────────────

def parse_command(
    transcript: str,
    anchor_measure: int | None,
    last_start: int | None = None,
    pending_question: str | None = None,
) -> tuple[dict | None, str | None]:
    """
    Parse an ASR transcript into a command dict and feedback text.

    Parameters
    ----------
    transcript      : ASR output text.
    anchor_measure  : Measure frozen at RECORD press (camera reading).
    last_start      : Start measure of the last successfully executed command.
                      Used to resolve "from last location" references.

    Returns
    -------
    (command, feedback)
        command : {"cmd": "stop"} | {"cmd": "play_stems", ...} | {"cmd": "play_all", ...} | None
        feedback : confirmation sentence, clarification question, or None
    """
    try:
        parts = []
        if pending_question:
            parts.append(f"previous_question: {pending_question}")
        parts.append(f"anchor_measure: {anchor_measure if anchor_measure is not None else 'null'}")
        parts.append(f"last_playback_start: {last_start if last_start is not None else 'null'}")
        parts.append(f"transcript: {transcript}")
        user_msg = "\n".join(parts)
        response = ollama.chat(
            model=_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            format=_SCHEMA,
            options={"temperature": 0},
        )
        data = json.loads(response.message.content)

    except Exception as e:
        print(f"  [LLM] error: {e} — falling back to regex parser")
        from voice_parser import parse_command as _fallback
        return _fallback(transcript, anchor_measure), None

    err = _validate(data)
    if err:
        print(f"  [LLM] validator rejected output ({err})")
        if "out of range" in err:
            return None, "This piece only has measures one through sixteen."
        if "empty tracks" in err:
            return None, "Which instrument would you like to play?"
        return None, None

    status   = data["status"]
    feedback = data.get("feedback_text") or data.get("clarification_question")

    # Handle stop regardless of status — LLM occasionally returns status=execute with cmd=stop
    if status == "stop" or data.get("cmd") == "stop":
        return {"cmd": "stop"}, feedback or "Stopping."

    if status == "execute":
        cmd    = data["cmd"]
        start  = data["start"]
        end    = data["end"]
        tracks = data["tracks"]
        if cmd == "play_all":
            # "except" exclusion: Python computes complement, LLM only identifies intent.
            exc = _apply_except(transcript, start, end, feedback)
            if exc is not None:
                return exc
            # Enforce: full-mix with no anchor starts at 1.
            # Only fires when start == last_start (LLM used last_playback_start).
            if anchor_measure is None and last_start is not None and start == last_start:
                start = 1
                feedback = "Playing everything from measure one."
            return {"cmd": "play_all", "start": start, "end": end}, feedback
        if cmd == "play_stems":
            tracks = _apply_corrections(transcript, tracks)
            return {"cmd": "play_stems", "start": start, "end": end,
                    "tracks": tracks}, feedback

    # clarify or unrecognised
    return None, feedback
