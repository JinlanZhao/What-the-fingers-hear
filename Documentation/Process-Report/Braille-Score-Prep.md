# Orchestral Braille Score Preparation

**Working excerpt:** *ReScore – Journey*, 16 measures, 4/4, 144 BPM  
**Report date:** September 12, 2026

## 1. Scope Established

- The prototype will not be limited to a solo or single instrumental part.
- The selected source is a 16-measure excerpt from the composer's own full orchestral composition.
- The Braille transcription uses the complete orchestral score so a blind musician can inspect the orchestration, not only one extracted part.
- A single full-score MusicXML file is used for Braille conversion. Individual instrumental MusicXML files were not used.
- Future audio playback will support separate instrumental stems, but stem rendering has not yet been completed.

## 2. Source Score Preparation

The excerpt was prepared in Dorico with the following score-level properties:

| Property | Value |
|---|---|
| Length | 16 measures |
| Meter | 4/4 |
| Tempo | 144 BPM |
| Score type | Full orchestral score |
| Export format | MusicXML |

The final source contains 25 instrumental parts:

- Flute 1, Flute 2
- Oboe 1, Oboe 2
- Clarinet in B-flat 1, Clarinet in B-flat 2
- Bassoon 1, Bassoon 2
- Horn in F 1–4
- Trumpet in C 1, Trumpet in C 2
- Trombone 1, Trombone 2
- Tuba
- Glockenspiel
- Snare Drum
- Bass Drum
- Violin 1, Violin 2
- Viola
- Violoncello
- Double Bass

## 3. MusicXML Revision History

### Version 1: `Orchestration_Bars16_4-4_144bpm.musicxml`

- Contained 26 parts, each with 16 measures.
- Included an unintended Shaker part.
- Clarinet names contained duplicated transposition text: `Clarinet (B Flat) (B Flat)`.
- Trumpets were labeled as B-flat instruments.
- This version was rejected.

### Version 2: `Orchestration_Bars16_4-4_144bpm(1).musicxml`

- Reduced the score to 25 parts by removing Shaker.
- Preserved separate Clarinet 1/2 and Trumpet 1/2 parts.
- Clarinet names still contained duplicated B-flat text.
- Trumpets were still labeled as B-flat instruments.
- This version was rejected.

### Version 3: `Orchestration_Bars16_4-4_144bpm(2).musicxml`

- Contained 25 parts and 16 measures in every part.
- Corrected the clarinet names to `Clarinet (B Flat) 1/2`.
- Corrected the trumpet names to `Trumpet (C) 1/2`.
- Preserved all other orchestral parts.
- Used as the corrected musical source for Braille conversion.

## 4. Dorico Layout Configuration for Braille Export

The original MusicXML did not contain a `new-system="yes"` instruction before each measure. In the inspected source, Measures 7 and 13 began new print pages, while the other adjacent measures generally contained `new-system="no"`. SM BungSang therefore attempted to place some adjacent measures in the same Braille parallel.

The Dorico Full Score layout was changed specifically for Braille export:

1. Opened `Layout Options` with `Cmd + Shift + L`.
2. Selected only the Full Score/Braille export layout.
3. Opened `Staves and Systems`.
4. Opened the `Casting Off` section.
5. Enabled `Fixed number of bars per system`.
6. Set the value to `1`.
7. Applied the setting and exported the score to MusicXML again.

This forced each printed measure to begin a new system. Because `System break` was enabled in SM BungSang's `Begin new parallel at` settings, each measure then began a separate Braille parallel.

## 5. Braille Translation Tool

- GOODFEEL was considered but not used because of its cost.
- SM BungSang for macOS was selected as the MusicXML-to-Braille translator.
- The conversion was performed from the full orchestral MusicXML rather than from separate player parts.

## 6. SM BungSang Configuration

### 6.1 Music format

| Setting | Selected value |
|---|---|
| Format type | `Bar-over-bar` |
| Transcription mode | `Orchestra and Chamber` |
| Always mark octave at first note of measure | Off |
| Show original print line number | Off |
| Show original print page number | Off |
| Measure numbering | Enabled for measure-level identification |
| Braille page numbering | Enabled, beginning at Page 1 |
| Keep parallel together | Enabled |

### 6.2 Braille page format

| Setting | Value |
|---|---:|
| Characters per line (`CPL`) | 40 |
| Lines per page (`LPP`) | 25 |

### 6.3 `Begin new parallel at`

All available conditions were enabled:

- `Print page`
- `Section break or double barline`
- `Backward repeat barline`
- `Key or time signature change`
- `Repeat indication text`
- `Segno sign`
- `Coda sign`
- `System break`
- `Rehearsal mark`

These settings do not create a break at every measure by themselves. The one-measure-per-system Dorico layout supplies the required `System break` information.

### 6.4 Music signs and slurs

| Setting | Selected value |
|---|---|
| General musical signs | Retained |
| Print clef signs | Hidden |
| Bracket slur | Enabled for the English-language/BANA-oriented profile |

### 6.5 Braille repeats

For this validation prototype, Braille compression through repeats was disabled so the converted content could be compared more directly with the MusicXML and every measure could remain explicit.

| Repeat category | Selected value |
|---|---|
| Full-measure repeats | Disabled/None |
| Part-measure repeats | Disabled/None |
| Repeats for special rhythms | Disabled/None |
| Part-measure repeats of different lengths | Off |
| Part-measure repeats for uneven beats only | Off |
| Repeats within tuplets | Disabled/None |
| Passage repeats | Disabled |
| Backward numeral repeats | Disabled |
| Measure-number repeats used as content substitution | Disabled |

The exact wording of the disabled dropdown value varies by SM BungSang control; the working profile selected the available `None`, `Never`, or `Do not use` equivalent.

### 6.6 Text and file encoding

| Setting | Selected value |
|---|---|
| Text language/table | English/UEB-oriented text profile |
| Unicode Braille output | `.txt` |
| ASCII Braille output | `.brf` |
| BRF encoding | ASCII, North American |

## 7. Braille Conversion and Debugging History

### Initial conversion: `Orchestration_Bars16_4-4_144bpm_braille.txt`

- Produced 330 text lines.
- Contained no form-feed page separators.
- Contained a line up to 84 cells wide.
- Included placeholder metadata such as `Project Copyright` and `Project Lyricist`.
- Rejected because the page structure and line width were unsuitable for a 40-cell Braille page.

### Repeat-disabled conversion: `Orchestration_Bars16_4-4_144bpm_braille(1).txt`

- Produced 18 pages with 17 form-feed separators.
- Used 25 lines per page.
- Expanded to 449 newline-delimited text rows after disabling repeat compression.
- Preserved the 25-part orchestral instrument key.
- Still contained two over-width parallel headings:
  - Measures 5–6 heading: 84 cells.
  - Measures 10–11 heading: 63 cells.
- Rejected for physical output because these lines exceeded the 40-cell limit.

### Dorico system-break correction

- Dorico was configured to use one bar per system in the Braille export layout.
- MusicXML was exported again and converted with the same SM BungSang settings.
- This prevented adjacent measure headings from being placed in a single over-width parallel.

### Final Unicode conversion: `Orchestration_Bars16_4-4_144bpm_braille(2).txt`

- Produced 18 Braille pages with 17 form-feed separators.
- Every page contained 25 lines.
- Maximum line width was 39 cells.
- No line exceeded the 40-cell limit.
- All 16 measure headings were present and separated into distinct parallels.
- The earlier 84-cell and 63-cell lines were eliminated.
- The title page still contained `Test`, `Project Copyright`, and `Project Lyricist`.

### Final ASCII conversion: `Orchestration_Bars16_4-4_144bpm_braille(1).brf`

- Produced 18 Braille pages with 17 form-feed separators.
- Maximum line width was 39 cells.
- No line exceeded the 40-cell limit.
- Page 1 contained 22 lines; Pages 2–18 contained 25 lines each.
- After conversion from North American Braille ASCII to Unicode Braille, the musical content matched the final Unicode file.
- The only substantive difference was the removal of `Project Copyright` and `Project Lyricist` from the BRF title page.
- `Test` remained on the title page.

## 8. Final Structural Validation

The following checks were completed programmatically:

| Check | Result |
|---|---|
| MusicXML part count | 25 |
| Measures per part | 16 |
| Clarinet 1 and 2 retained | Pass |
| Trumpet 1 and 2 retained | Pass |
| Meter | 4/4 |
| Tempo | 144 BPM |
| Final Braille page count | 18 |
| Form-feed separators | 17 |
| Maximum final line width | 39 cells |
| Lines exceeding 40 cells | 0 |
| Measure headings detected | 16 |
| Separate measure parallels | Pass |
| Final BRF/Unicode musical-content comparison | Pass |

The final BRF passed structural checks for the selected 40-cell by 25-line format.

## 9. Current Limitations

- Structural validation does not prove that every note, octave, duration, articulation, slur, in-accord, and transposition was translated correctly.
- Automated Braille music output still requires sample-based review by an experienced Braille music reader or transcriber before it is treated as publication-quality.
- The body of the orchestral transcription uses shared short instrument labels for paired instruments. The usability of distinguishing paired parts by order should be tested with a Braille music reader.
- A complete orchestral measure can occupy most of a Braille page or continue onto another page. In the current output, Measure 1 continues from Page 2 to Page 3, and Measure 16 continues from Page 17 to Page 18.
- The future camera map must therefore store `page + measure + continuation region`, rather than assuming that each measure occupies one uninterrupted region on one page.
- The subtitle `Test` must be removed unless it is intentional.

## 10. Current Deliverables

| File | Status | Purpose |
|---|---|---|
| `Orchestration_Bars16_4-4_144bpm(2).musicxml` | Corrected musical source before the final Dorico layout pass | Verified 25-part, 16-measure source |
| `Orchestration_Bars16_4-4_144bpm_braille(2).txt` | Final Unicode Braille reference | Visual inspection and programmatic validation |
| `Orchestration_Bars16_4-4_144bpm_braille(1).brf` | Final ASCII Braille candidate | Embosser/refreshable Braille output |

## 11. Work Not Yet Completed

- Remove or confirm the `Test` subtitle.
- Obtain a Braille music reader/transcriber review of selected measures.
- Emboss the final BRF and verify tactile page layout.
- Photograph or scan each embossed page and construct `page_map.json` with measure and continuation regions.
- Export synchronized instrumental stems from the same Dorico project.
- Generate the tempo map and `bar_times.json`.
- Implement Max/MSP playback, camera registration, finger tracking, voice control, and reading-behavior ML.
