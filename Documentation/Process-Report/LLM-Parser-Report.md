# LLM Voice Command Parser — Development Report

**Date:** October 12, 2026
**Status:** Functional. 31/31 test cases passing. Multiple hardware tests completed.

---

## 1. Why LLM Parser

The previous `voice_parser.py` was a deterministic regex + lookup-table parser. It handled explicit patterns ("play violin one", "play measures five through eight") but failed on:

- Natural language variation ("only violin one from measure five", "just the cello please")
- Self-correction ("play flute one… actually violin two")
- Relative references ("from the next bar", "from where I left off")
- Ambiguity detection ("play flute" → ask which part)
- Multi-turn context ("play flute" → "Flute one or two?" → "flute one")

The key insight: the LLM parser replaces code with examples. New phrase variants don't require new code — the model handles them. Test cases verify existing capability rather than defining new behavior.

---

## 2. Architecture

```
ASR transcript + {anchor_measure, last_playback_start, pending_question}
    → LLM (one call, Qwen2.5:7b via Ollama)
    → {status, cmd, tracks, start, end, feedback_text, clarification_question}
    → Python Validator (safety net)
    → Python Layer (self-correction, "except" exclusion, full-mix override)
    → OSC dispatch + terminal print + TTS (only on no-dispatch)
```

**Single LLM layer:** one call per transcript outputs both a structured command AND a feedback text string simultaneously. No separate response-generation model needed.

**Python Validator** is a safety net only. Validation failures use hard-coded error messages rather than a second LLM call.

**Python Layer** handles reasoning that Qwen2.5:7b cannot reliably perform:
- Self-correction in instrument lists ("no actually X" → remove prior, add corrected)
- "except" exclusion complement calculation
- Full-mix start=1 enforcement when anchor is null

---

## 3. Model Selection

### Development path

| Phase | Model | Reason |
|---|---|---|
| Initial plan | GPT-4o-mini (OpenAI API) | Guaranteed JSON Schema output, fast iteration |
| Switched | Qwen2.5:7b via Ollama | Free tier rate limits (50 RPD) caused development friction; $5 credit still hit daily limit |

### Why Ollama

- No rate limits — critical for rapid prompt iteration
- Free after one-time model download (4.7 GB)
- Runs locally on Apple Silicon at acceptable latency
- Prompt is fully portable — switching back to API requires only changing the client, not the prompt

### Installation

```bash
brew install ollama
brew services start ollama
ollama pull qwen2.5:7b
pip install ollama   # in project venv
```

---

## 4. Prompt Engineering — What Was Tried

### Attempt 1: Rules only (failed)

A compact rules-only prompt (~35 lines) with no examples. Issues:

- Model treated "violin one" (explicit number) as ambiguous and asked "Violin one, violin two, or both?"
- Model did not populate `start`/`end` integer fields even when `anchor_measure` was provided — would generate correct `feedback_text` ("Playing from measure five") but leave `start=null`
- Model applied "anchor=null → unrecognised" rule even when transcript contained explicit measure numbers
- "play full mix" with anchor=null returned unrecognised instead of defaulting to start=1

Root cause: small models (7B) need concrete output examples, not abstract rules. They pattern-match rather than reason from principles.

### Attempt 2: Rules + NEVER/ONLY sections (partial fix)

Added explicit negative rules ("NEVER use clarify for numbered instruments", "NEVER use clarify for missing anchor"). Fixed some cases but introduced new regressions (stop command sometimes returned cmd=null). The flat list of rules created ambiguity about priority order.

### Attempt 3: Decision tree + few-shot examples (working)

**Key structural change:** replaced flat rules with a numbered decision tree (STEP 1–6). Model processes steps in order and stops at the first match. This eliminates priority ambiguity.

**Key content change:** added 34 few-shot examples, each annotated with which STEP applies. Small models respond much more reliably to "here is the exact output format for this input" than to abstract rules.

### Post-hardware-test additions

Several issues discovered through live testing required prompt additions and Python-layer mitigations:

- **STEP 4 updated:** added "bare 'play from bar X' with no instrument" as unrecognised case (previously only gibberish/greetings)
- **STEP 6 part validation:** flute/oboe/clarinet/bassoon/trumpet/trombone/violin only have parts 1–2; horn has 1–4; invalid part number → unrecognised with specific message
- **STEP 6 end > 16 clamp:** if stated end exceeds 16, clamp to 16
- **STEP 2 IGNORE last_playback_start:** explicit instruction to avoid LLM using last_start for full-mix
- **CLARIFICATION RESOLUTION section:** added to handle multi-turn answers ("flute one" after "Flute one, flute two, or both?")
- **CRITICAL RULES:** added self-correction rule ("X, no actually Y" → Y replaces X, NEVER include both) — note: ultimately moved to Python due to Qwen instability

---

## 5. Final Prompt Structure

```
Context description (2 lines)
Context variables: anchor_measure, last_playback_start

Valid track IDs (canonical strings)
Spoken name → track ID mapping

DECISION TREE — STEP 1–6:
  STEP 1: "stop"
  STEP 2: full mix / everything (IGNORE last_playback_start; anchor null → start=1)
  STEP 3: pure range (no instruments) → play_all
  STEP 4: no instrument names (gibberish, queries, bare "play from bar X") → unrecognised
  STEP 5: instrument named, no number → clarify
  STEP 6: instrument with explicit number/quantity → validate part number, then determine start:
    6a last location, 6b next bar, 6c previous bar, 6d here,
    6e explicit measure in transcript, 6f anchor_measure, 6g neither → unrecognised

CLARIFICATION RESOLUTION:
  When previous_question is set, map answer to instrument tracks and execute.

CRITICAL RULES (6 lines: clarify vs unrecognised boundaries, self-correction rule)

FEEDBACK TEXT format

EXAMPLES (34 input→output pairs, annotated with which step applies)
```

Total prompt length: ~250 lines. The examples account for ~130 lines.

---

## 6. Output Schema

```json
{
  "status": "execute" | "stop" | "clarify" | "unrecognised",
  "cmd": "play_stems" | "play_all" | "stop" | null,
  "tracks": ["vln1", "fl1"],
  "start": 5,
  "end": 16,
  "feedback_text": "Playing violin one from measure five.",
  "clarification_question": null
}
```

Ollama receives the raw JSON Schema object (without OpenAI's `name`/`strict` wrapper).

---

## 7. Python Validator

Checks LLM output after parsing. Returns error string or None.

- `play_stems`: tracks non-empty, all IDs valid, start/end in 1–16, end ≥ start
- `play_all`: start/end in 1–16, end ≥ start
- `clarify` / `unrecognised` / `stop`: no validation needed

On validation failure — specific messages by error type:
- `"out of range"` → `"This piece only has measures one through sixteen."`
- `"empty tracks"` → `"Which instrument would you like to play?"` (triggers `_pending` → user can answer naturally)
- other → `(None, None)` — silent failure, no TTS

On API/parse error: falls back to deterministic `voice_parser.py`. Returns `(result, None)` with no feedback text.

---

## 8. Python Layer (moved from LLM)

Three operations that Qwen2.5:7b cannot reliably handle are implemented in Python post-LLM:

### `_SPOKEN_TO_TRACK`

Comprehensive mapping from spoken instrument names to track ID lists. Sorted by key length descending so numbered variants match before bare family names:

```python
("violin two", ["vln2"])   # matches before
("violin",     ["vln1","vln2"])
```

Includes: all numbered variants ("flute one", "violin 1"), family-level names ("flute", "violin"), synonyms ("double bass"→cb, "bells"→glk, "horn one"→fh1).

### `_apply_corrections(transcript, tracks)`

Scans for self-correction patterns in transcript: `"(?:no\s+)?actually\s+(.+?)"`. For each match:
1. Find the corrected instrument in the text after "actually" — longest match first
2. Find the replaced instrument — rightmost match before "actually"
3. Remove replaced tracks from list, add corrected tracks

Applied to all `play_stems` results after LLM output.

### `_apply_except(transcript, start, end, feedback)`

Scans for `"except [instruments]"` in transcript. Computes complement: all 25 tracks minus matched excluded tracks. Returns `play_stems` with the complement list.

Applied inside `play_all` branch before returning.

### Full-mix start=1 override

After LLM returns `play_all`:
```python
if anchor_measure is None and last_start is not None and start == last_start:
    start = 1
    feedback = "Playing everything from measure one."
```

Fires only when `start == last_start` (LLM incorrectly used last_playback_start). Does not affect explicit range commands (start=5 for "play measures 5 through 8").

---

## 9. Integration with voice_mvp.py

### Original integration
- `from llm_parser import parse_command as _llm_parse` (replaces `voice_parser`)
- `Controller` gains `_last_start: int | None` — updated after every successful dispatch
- `on_record_start()` freezes both `anchor` and `last_start` at RECORD press time
- `_run_recording()` passes both to `_llm_parse(text, anchor, last_start=last_start)`

### TTS (macOS `say`)
- `_speak(text)` — `subprocess.run(["say", text])`, blocking
- TTS fires **only when `cmd is None`** (clarify / error / unrecognised-with-message)
- Successful playback commands print to terminal only — no TTS

### Multi-turn clarification (`_pending`)
- `Controller._pending: dict | None = None`
- Stores `{"anchor": int|None, "question": str}` when LLM returns a clarification question
- Detection: `is_clarify = cmd is None and feedback is not None and "?" in feedback`
- On next RECORD press: reads `_pending`, uses `pending["anchor"]` (preserves original anchor), passes `pending["question"]` as `pending_question` to LLM
- `on_stop()` clears `_pending`
- When validator returns "empty tracks" error: returns `"Which instrument would you like to play?"` → also triggers `_pending`

### Whisper trailing punctuation fix
- `_transcribe()` now strips trailing punctuation: `.rstrip(" .,")`
- Fixes Whisper adding period to transcripts ("play violin one." → "play violin one")
- Prevents LLM from matching wrong few-shot example based on punctuation

### `voice_parser.py` retained as fallback only — not used in normal operation.

---

## 10. Test Results (31/31)

All 31 cases verified passing with `python3 camera/test_llm_parser.py`.

| # | Transcript | anchor | last_start | pending | Expected cmd | Expected feedback | Result |
|---|---|---|---|---|---|---|---|
| 1 | "play violin one" | 5 | — | — | play_stems vln1 5→16 | "Playing violin one from measure five." | ✅ |
| 2 | "play violin one" | None | — | — | unrecognised | "Please select a measure first." | ✅ |
| 3 | "play flute one and cello" | 3 | — | — | play_stems fl1 vc 3→16 | "Playing flute one and cello from measure three." | ✅ |
| 4 | "play both flutes" | 7 | — | — | play_stems fl1 fl2 7→16 | "Playing both flutes from measure seven." | ✅ |
| 5 | "play flute" | 2 | — | — | clarify | "Flute one, flute two, or both?" | ✅ |
| 6 | "play measures five through eight" | None | — | — | play_all 5→8 | "Playing measures five through eight." | ✅ |
| 7 | "play violin one measures three through twelve" | None | — | — | play_stems vln1 3→12 | "Playing violin one from measure three through twelve." | ✅ |
| 8 | "only violin one from measure five" | None | — | — | play_stems vln1 5→16 | "Playing violin one from measure five." | ✅ |
| 9 | "play full mix" | 4 | — | — | play_all 4→16 | "Playing everything from measure four." | ✅ |
| 10 | "play full mix" | None | — | — | play_all 1→16 | "Playing everything from measure one." | ✅ |
| 11 | "play full mix" | None | 8 | — | play_all 1→16 (Python override) | "Playing everything from measure one." | ✅ |
| 12 | "play everything" | 6 | — | — | play_all 6→16 | "Playing everything from measure six." | ✅ |
| 13 | "stop" | None | — | — | stop | "Stopping." | ✅ |
| 14 | "play flute one… actually violin two" | 5 | — | — | play_stems vln2 5→16 | "Playing violin two from measure five." | ✅ |
| 15 | "play violin one, flute one, no actually flute two, and cello" | 5 | — | — | play_stems vln1 fl2 vc 5→16 | — | ✅ |
| 16 | "hello how are you" | None | — | — | unrecognised | None | ✅ |
| 17 | "Play Violin 1." | 8 | — | — | play_stems vln1 8→16 | "Playing violin one from measure eight." | ✅ |
| 18 | "play trumpet one and horn two" | 2 | — | — | play_stems tpt1 fh2 2→16 | "Playing trumpet one and horn two from measure two." | ✅ |
| 19 | "play flute four" | 3 | — | — | unrecognised | "There is no flute four in this score." | ✅ |
| 20 | "What is my current measure?" | None | — | — | unrecognised | None (silent) | ✅ |
| 21 | "play everything except flute" | 5 | — | — | play_stems (23 tracks, no fl1/fl2) 5→16 | "Playing everything except flute from measure five." | ✅ |
| 22 | "flute one" | 2 | — | "Flute one, flute two, or both?" | play_stems fl1 2→16 | "Playing flute one from measure two." | ✅ |
| 23 | "both" | 2 | — | "Flute one, flute two, or both?" | play_stems fl1 fl2 2→16 | "Playing both flutes from measure two." | ✅ |
| 24 | "violin two" | 7 | — | "Violin one, violin two, or both?" | play_stems vln2 7→16 | "Playing violin two from measure seven." | ✅ |
| 25 | "play violin one from bar five" | None | — | — | play_stems vln1 5→16 | "Playing violin one from measure five." | ✅ |
| 26 | "play violin one from the next bar" | 5 | — | — | play_stems vln1 6→16 | "Playing violin one from measure six." | ✅ |
| 27 | "play violin one from the previous bar" | 5 | — | — | play_stems vln1 4→16 | "Playing violin one from measure four." | ✅ |
| 28 | "play flute one from last location" | 3 | 8 | — | play_stems fl1 8→16 | "Playing flute one from measure eight." | ✅ |
| 29 | "play cello from where I left off" | 3 | 6 | — | play_stems vc 6→16 | "Playing cello from measure six." | ✅ |
| 30 | "play measures five through eight" | None | — | — | play_all 5→8 | "Playing measures five through eight." | ✅ |
| 31 | "play violin one from here" | 7 | — | — | play_stems vln1 7→16 | "Playing violin one from measure seven." | ✅ |

**Note on case 15:** LLM feedback text says "flute one" (generated before Python correction). Actual `tracks` output is `['vln1', 'fl2', 'vc']` — correct. Since TTS only fires when `cmd is None`, this discrepancy is never spoken.

---

## 11. Hardware Test History

### Test 1 — Teensy buttons + Whisper, camera not running

**Working:**
- "Play violin one from measure eight." → `play_stems vln1 8→16` ✅
- "play cello and flute four, no actually flute two from measure eight to twelve." → `play_stems vc fl2 8→12` ✅
- "play full mix." / "play everything." → `play_all` ✅
- Hardware buttons (RECORD push-to-talk, PLAY, STOP) all functional ✅

**Issues found:**
1. "play full mix" with last_start=8 → LLM used start=8 instead of 1 — **fixed** (Python override)
2. "play from bar eight" with no instrument → validator rejected (empty tracks) — **fixed** (STEP 4 update + validator message)
3. "What is my current measure?" → returned "Please select a measure first." — **fixed** (STEP 4 + silent unrecognised)
4. Out-of-range command ("measures 16 to 20") → LLM gave wrong feedback — **fixed** (end clamp + specific validator message)

### Test 2 — Camera connected, anchor from shared_state

**Issues found:**
1. "play violin one." (Whisper period) + anchor=9 → "Please select a measure first." 3 times
   - Root cause: LLM matched anchor=null example for "play violin one." — **fixed** (`.rstrip(" .,")` in `_transcribe()`)
2. "play flute four" → played fh4 (French horn 4) — wrong instrument ID
   - Root cause: LLM mapped "flute four" to fh4 — **fixed** (STEP 6 part validation, prompt example)
3. Query responses returning wrong feedback — **fixed** (added query examples to prompt)

### Test 3 — Full pipeline with camera + all new features

**Working:**
- "play violin one" with anchor=9 → `play_stems vln1 9→16` ✅ (rstrip fix confirmed)
- Query commands → silent ✅
- Multi-turn clarification: "play flute" → spoken "Flute one, flute two, or both?" → "flute one" → `play_stems fl1` ✅

**Issue found:**
- "play violin one, flute one, no actually flute two, French horn one, and trumpet one from the current bar" → output included both fl1 and fl2
- Root cause: LLM kept both despite CRITICAL RULE in prompt — Qwen2.5:7b cannot reliably apply complex correction rules — **fixed** (`_apply_corrections` Python function)

### Remaining known issues

1. **ASR misrecognition of "full mix":** Whisper sometimes transcribes "play full mix" as "play four mix". LLM correctly does not recognise "four mix". `_WHISPER_PROMPT` already includes "play full mix" — may need expansion.

2. **LLM feedback text mismatch on self-correction:** When `_apply_corrections` overrides tracks, the LLM feedback text was generated before correction. Terminal may print "flute one" while actual playback uses fl2. Not spoken (TTS only for `cmd is None`). Acceptable for current use.

3. **Camera not running = anchor always None:** All tests with explicit measures work. Full integration requires running `finger_measure_test.py` concurrently.

---

## 12. Files

| File | Role |
|---|---|
| `camera/llm_parser.py` | LLM parser — prompt, schema, Python layer, `parse_command()` |
| `camera/test_llm_parser.py` | 31-case manual test script |
| `camera/voice_parser.py` | Retained as fallback (regex-based, not used in normal operation) |
| `camera/voice_mvp.py` | Controller — imports `_llm_parse`, TTS, multi-turn `_pending`, `_last_start` |
