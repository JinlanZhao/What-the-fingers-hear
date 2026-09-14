# Braille Score Verification — Issues and Review Record

Date: 2026-09-13  
Status: **NEEDS EXPERT REVIEW** — deterministic checks passed; musical equivalence is not yet independently proven.

## Files checked (read-only)

- `Score-prep/Score_Bars16_4-4_144bpm.musicxml`
- `Score-prep/Score_Bars16_4-4_144bpm_braille.txt`
- `Score-prep/Score_Bars16_4-4_144bpm_braille.brf`
- Companion observation: `Score-prep/Score_Bars16_4-4_144bpm_braille.pdf`

The verifier compared input hashes before and after the run. All input hashes were unchanged.

## Problems and unresolved risks

### 1. Placeholder metadata remains in final-source content

Severity: warning; should be resolved before publication.

- MusicXML contains `Project Copyright` once, `Project Lyricist` once, and `Test` in 16 title/credit locations.
- Unicode Braille contains `Project Copyright` and `Project Lyricist` on its title page.
- BRF omits the two `Project ...` lines, so the Unicode and BRF title metadata are not identical.
- `Test` appears in both Braille encodings and may be an unintended movement title.

Required decision: replace these values with final metadata or explicitly confirm that `Test` is intentional. Then regenerate every final format together.

### 2. Full musical equivalence is not independently verified

Severity: mandatory expert-review gap, not a confirmed notation error.

The script verifies MusicXML structure and timing internally, and it verifies Braille encoding/ordering. It does **not** reverse-decode Music Braille into an independent event model. Therefore it cannot honestly certify exact equality for:

- 817 pitched notes, 82 unpitched events, 314 rests, and 1,213 durations;
- 203 accidentals and 63 augmentation dots;
- 8 XML ties plus 8 notation ties, 82 slur elements, and 563 articulation groups;
- 28 dynamics and 44 wedge elements;
- 12 time-modification elements and 8 tuplets;
- 7 transpositions, 29 clefs, keys, octave placement, and in-accord/voice meaning.

Required action: complete a final review with an independent Music Braille decoder or a qualified Music Braille transcriber. The highest-value review targets are:

- Snare Drum measures 3, 7, 11, and 15 for tuplets;
- Violin 1 and 2 across measures 3–4 and 11–12 for ties;
- Clarinet in B-flat, Horn in F, and Glockenspiel from measure 1 for transposition/octave treatment;
- Horn measures 2, 4, and 7 for clef changes;
- Snare Drum and Bass Drum throughout for unpitched notation;
- measures 1 and 16 at page continuations;
- all dynamics, wedges, slurs, accidentals, and articulations, using the verifier's JSON `feature_locations` list.

### 3. Companion Braille PDF is not synchronized with the Unicode/BRF export

Severity: warning; PDF must not be treated as an equivalent final copy until reviewed.

- Unicode TXT and BRF each contain 18 logical pages and 17 form feeds.
- The Braille PDF reports 25 pages.
- After PDF text extraction and removal of whitespace, the Unicode TXT contains 4,469 Braille cells while the PDF-derived text contains 4,585; the first extracted-content difference occurs at compacted cell index 16.

PDF text extraction can be affected by font encoding, so this does not by itself prove a musical-symbol error. It does prove that the PDF is not currently machine-equivalent to the verified TXT/BRF sequence. Regenerate it from the approved source or compare it visually/cell-by-cell before distribution.

## Deterministic checks that passed

- MusicXML is well-formed `score-partwise` version 4.0.
- MusicXML contains 25 declared/actual parts, each with measures 1–16 (400 measure elements total).
- Every measured part span equals the active 4/4 meter; zero duration-span errors were found.
- XML tie, tied-notation, slur, and hairpin start/stop counts are balanced.
- XML tempo is 144 BPM.
- Unicode Braille is strict UTF-8 and contains no replacement characters, NULs, unexpected controls, non-Braille text, or 7/8-dot Unicode cells.
- Unicode layout is 18 logical pages, maximum 39 cells per line and 25 lines per page, within the configured 40×25 limits.
- BRF is strict ASCII and converts successfully through the installed SM BungSang `en-nabcc.utb` table.
- After removing only the two documented placeholder lines (`Project Copyright`, `Project Lyricist`) and ignoring empty title-page rows, BRF and Unicode Braille match cell-for-cell.
- The Braille instrument table matches all 25 MusicXML part names in order.
- Braille measure headings are exactly 1 through 16.
- Every instrument abbreviation used in the Braille music body is declared in its instrument list.

## Reproduction

Run from the project root:

```bash
python3 tools/verify_braille_score.py \
  --musicxml Score-prep/Score_Bars16_4-4_144bpm.musicxml \
  --braille Score-prep/Score_Bars16_4-4_144bpm_braille.txt \
  --brf Score-prep/Score_Bars16_4-4_144bpm_braille.brf \
  --json
```

Current expected exit code is `2`, meaning deterministic checks found no confirmed error but independent musical review remains incomplete. Exit code `1` means a confirmed machine-detectable error; exit code `0` means no error or mandatory review finding.

Current input SHA-256 values:

- MusicXML: `410ca7145011115efc6ca0a36552322a49993bef674b35c04d1cb36568c871cc`
- Unicode Braille TXT: `498a55b9f1cbd8d658d304f5d92598e3419ba0d7fa1605dcf8d65bb62822a39d`
- BRF: `cf9a3cd6089d8bfbe47b61c1a750fe0e48efc96754230595de086aa1e5fdb6c7`

## Reference basis

- MusicXML 4.0 structure and schema: <https://www.musicxml.com/for-developers/>
- BANA Music Braille Code 2015: <https://brailleauthority.org/music-braille-code>
- New International Manual of Braille Music Notation: <https://www.ukaaf.org/wp-content/uploads/2020/03/New-International-Manual-of-Braille-Music-Notation-PDF.pdf>
- Sao Mai Braille documentation: <https://saomaicenter.org/en/blog/sao-mai-braille-user-guide>
