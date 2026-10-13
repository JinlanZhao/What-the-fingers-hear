#!/usr/bin/env python3
"""
Manual test script for llm_parser.py.
Sends a batch of transcripts and prints (command, feedback) for each.

Usage:
    OPENAI_API_KEY=sk-... python3 camera/test_llm_parser.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from llm_parser import parse_command

cases = [
    # (transcript, anchor, last_start, description)
    ("play violin one",                       5,    None, "stem from anchor"),
    ("play violin one",                       None, None, "stem — no anchor"),
    ("play flute one and cello",              3,    None, "two instruments"),
    ("play both flutes",                      7,    None, "both parts"),
    ("play flute",                            2,    None, "ambiguous — should clarify"),
    ("play measures five through eight",      None, None, "range only → play_all"),
    ("play violin one measures three through twelve", None, None, "stem + explicit range"),
    ("only violin one from measure five",     None, None, "natural phrasing with explicit measure"),
    ("play full mix",                         4,    None, "full mix with anchor"),
    ("play full mix",                         None, None, "full mix no anchor → start=1"),
    ("play full mix",                         None, 8,    "full mix no anchor but last_start set → still start=1"),
    ("play everything",                       6,    None, "everything alias"),
    ("stop",                                  None, None, "stop"),
    ("play flute one… actually violin two",   5,    None, "self-correction single"),
    ("play violin one, flute one, no actually flute two, and cello", 5, None, "self-correction in multi-instrument list"),
    ("hello how are you",                     None, None, "unrecognised"),
    ("Play Violin 1.",                        8,    None, "ASR capitalisation"),
    ("play trumpet one and horn two",         2,    None, "brass instruments"),
    ("play flute four",                       3,    None, "invalid part number — unrecognised"),
    ("What is my current measure?",           None, None, "position query — unrecognised silent"),
    ("play everything except flute",          5,    None, "except exclusion — play_stems minus fl1+fl2"),
    # clarification resolution (5-tuples with pending_question)
    ("flute one", 2, None, "Flute one, flute two, or both?", "clarify answer: flute one"),
    ("both",      2, None, "Flute one, flute two, or both?", "clarify answer: both"),
    ("violin two",7, None, "Violin one, violin two, or both?", "clarify answer: violin two"),
    # bar/measure synonyms and relative references
    ("play violin one from bar five",         None, None, "bar synonym"),
    ("play violin one from the next bar",     5,    None, "next bar → anchor+1=6"),
    ("play violin one from the previous bar", 5,    None, "previous bar → anchor-1=4"),
    ("play flute one from last location",     3,    8,    "last location → last_start=8"),
    ("play cello from where I left off",      3,    6,    "where I left off → last_start=6"),
    ("play measures five through eight",      None, None, "bar range synonym"),
    ("play violin one from here",             7,    None, "from here → anchor=7"),
]

print("=== llm_parser manual tests ===\n")
for case in cases:
    if len(case) == 4:
        transcript, anchor, last_start, desc = case
        pending_q = None
    else:
        transcript, anchor, last_start, pending_q, desc = case
    cmd, feedback = parse_command(transcript, anchor, last_start=last_start, pending_question=pending_q)
    print(f"[{desc}]")
    print(f"  in : {transcript!r}  anchor={anchor}  last_start={last_start}  pending={pending_q!r}")
    print(f"  cmd: {cmd}")
    print(f"  fb : {feedback!r}")
    print()
