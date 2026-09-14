# Max/MSP Playback Engine — Implementation Report

**Project:** Braille Score prototype  
**Date:** 14 September 2026

## 1. Scope

Built the Max/MSP playback layer for synchronized, bar-based playback of the *ReScore – Journey* excerpt:

- 16 bars, 4/4, 144 BPM
- 29 stereo audio files: 25 instrumental stems and 4 additional effects/room stems
- One shared transport controlling every stem
- Stereo master output

Max was retained instead of a web page because the current requirement is local multistem audio playback, with Python/OSC control to be added later.

## 2. Bar-to-Time Calculation

For the current fixed-tempo excerpt:

- Beat duration: `60 / 144 = 0.416667 s`
- Bar duration: `0.416667 × 4 = 1.666667 s = 1666.667 ms`
- Start time: `(Start Bar - 1) × 1666.667`
- Duration: `Number of Bars × 1666.667`
- End time: `Start Time + Duration`

`Number of Bars` is a duration, not a destination bar. Example: Start Bar 5 with 4 bars plays Bars 5–8 and stops at the beginning of Bar 9.

## 3. Initial Playback Prototype

The first version used one `sfplay~ 2` per stem with a dynamically generated `seek start_ms end_ms` message. `pak`, `expr`, and `zl reg` were used to calculate and store the playback range so parameter changes did not trigger playback automatically.

This version was abandoned after the stems were aligned in Logic but played slightly out of alignment in Max. Independent `sfplay~` instances receiving `seek` were not sufficiently synchronized for this application.

## 4. Reusable Stem Player

Created a reusable abstraction, `stem_player.maxpat`, instantiated in the main patch as:

```max
stem_player filename.wav
```

Inside each abstraction:

- `#1` supplies that instance's audio filename.
- `buffer~ #0_stem #1` loads the file into a uniquely named buffer.
- `r~ braille_playhead` drives `play~ #0_stem 2`.
- `r~ braille_playgate` passes through `rampsmooth~ 240 240` and controls two `*~` objects.
- Stereo output passes through `live.gain~` to `s~ braille_master_L` and `s~ braille_master_R`.

All 29 abstraction instances were created and assigned their exact `.wav` filenames. Max's search path was configured so the files load correctly.

## 5. Shared Transport and Sample-Synchronous Playback

The main patch now creates one shared signal-rate playhead:

1. Start Time, End Time, and Duration enter `pak 0. 0. 0.`.
2. The list is stored in the right inlet of `zl reg`.
3. The PLAY button bangs the left inlet of `zl reg`.
4. `$1, $2 $3` sends an immediate start position followed by a timed ramp to `line~ @activeout 1`.
5. The left signal outlet is sent to `s~ braille_playhead`.
6. The active-state signal is sent to `s~ braille_playgate`.
7. The completion bang indicates playback has finished.

Because every `play~` receives the same signal-rate playhead, all stems read the same sample position at the same time.

`stop` is sent directly to `line~`. The previous `sfplay~` pause/resume controls are not part of the current transport.

## 6. Master Output

The main patch receives:

- `r~ braille_master_L`
- `r~ braille_master_R`

These feed one stereo `live.gain~` and one `ezdac~`. No audio outlets are required on `stem_player.maxpat`; named `send~`/`receive~` buses carry the audio.

## 7. Verification

A null-test section was built using `ReferenceMix.wav`:

- The reference uses the same `braille_playhead` and `braille_playgate` signals.
- Left and right reference channels are subtracted from the corresponding stem-master channels.
- `peakamp~ 100` and `atodb` measure the residual.

The first comparison did not null (`-7.723 dB` left, `-4.360 dB` right). That result alone could not distinguish transport drift from a mismatch in the reference mix. A valid null test requires the reference to be the exact unity-gain sum of the same 29 files, starting at sample 0, with no normalization, sends, plug-ins, or master processing. After rechecking the source setup and playback, the current result is considered operationally correct; no final `-inf` measurement was recorded.

## 8. Current Status

Completed:

- Bar-range calculation for the fixed 144 BPM / 4/4 excerpt
- 29 reusable stereo stem players
- Shared signal-rate playhead and playback gate
- Stereo master bus and output
- PLAY, STOP, and playback-finished indication
- Reference/null-test diagnostic patch

Still required:

- Replace the fixed `1666.667 ms` calculation with `bar_times.json`
- Validate and clamp bar inputs to the available excerpt
- Rebuild and test pause/resume for the shared-playhead system if required
- Add full-piece playback including the two-bar reverb tail
- Add per-stem mute/solo and accessible track controls
- Add OSC control and status exchange with Python
- Connect the later camera, voice, and ML layers
