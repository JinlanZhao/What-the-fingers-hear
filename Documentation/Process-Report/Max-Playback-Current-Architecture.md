# Max/MSP Playback — Current Confirmed Architecture

**Project:** Braille Score Reading Aid  
**Status date:** October 4, 2026

## 1. Scope

This document records only the current confirmed Max/MSP playback structure.

The system has two separate playback paths:

1. **Selected-stem playback** uses the synchronized local stem engine and shared real-time Reverb.
2. **Full Mix playback** uses one stereo `sfplay~ 2` player.

The Full Mix path does not open all 29 local stems. The local stem engine is used only when one or more specific Track IDs are requested.

## 2. OSC Input Contract

Max receives OSC on:

```text
127.0.0.1:7400
```

The command router is:

```max
udpreceive 7400
→ route /play_stems /play_all /stop /bar
```

The Python CLI accepts an inclusive Start Measure and End Measure, but converts the range before sending OSC:

```text
number_of_bars = end_measure - start_measure + 1
```

Therefore Max always receives:

```text
start_measure number_of_bars
```

Example:

```text
CLI: play_stems 5 8 fl1 fl2 vln1
OSC: /play_stems 5 4 fl1 fl2 vln1
```

```text
CLI: play_all 5 8
OSC: /play_all 5 4
```

The Max Console has confirmed that `/play_all 5 4` reaches the `/play_all` outlet as the list `5 4`.

## 3. Global Stop

`/stop` and the pre-play reset operations share one Global Stop chain:

```max
t b b
```

The two bangs perform:

```text
stop → line~ @activeout 1
0    → sfplay~ 2
```

Global Stop therefore stops both possible playback engines:

- the local shared-playhead stem engine;
- the stereo Full Mix player.

`all 0.` is not part of Global Stop. It belongs only to selected-stem preparation.

## 4. Selected-Stem Command: `/play_stems`

The `/play_stems` outlet feeds:

```max
t l l b b
```

Because Max executes `trigger` outlets from right to left, the runtime order is:

```text
Global Stop
→ mute all local stems
→ enable requested Track IDs
→ update playback range
→ Local PLAY
```

### 4.1 Outlet connections

From left to right, the four outlets are connected as follows.

#### First `l`: playback range

```text
first l
→ range-side zl slice 2
→ left outlet containing the first two values
→ t b l
```

The first two values are:

```text
start_measure number_of_bars
```

The `t b l` updates the range before triggering playback:

```text
right l → unpack i i
          → Start Bar
          → Number of Bars

left b  → Local PLAY
```

#### Second `l`: requested Track IDs

```text
second l
→ track-side zl slice 2
→ right outlet containing the remaining Track IDs
→ zl iter 1
→ $1 1.
→ s braille_track_gain
```

For example:

```text
5 4 fl1 fl2 vln1
```

produces:

```text
fl1 1.
fl2 1.
vln1 1.
```

#### First `b`

```text
all 0.
→ s braille_track_gain
```

This clears the previous stem selection before the requested Track IDs are enabled.

#### Rightmost `b`

```text
rightmost b
→ Global Stop
```

## 5. Full Mix Range Command: `/play_all`

`/play_all` means bounded playback of the stereo Full Mix. It does not mean enabling all 29 local stems.

The `/play_all` outlet feeds:

```max
t b l b
```

The connections are:

```text
rightmost b → Global Stop
middle l    → unpack i i
              → Start Bar
              → Number of Bars
leftmost b  → Full Mix range zl reg
              → seek $1 $2
              → sfplay~ 2
```

Execution order:

```text
Global Stop
→ update Start Bar and Number of Bars
→ update the stored millisecond range
→ send seek start_ms end_ms to sfplay~ 2
```

The `/play_all` branch does not connect to:

```text
all 1.
s braille_track_gain
Local PLAY
line~
```

## 6. Legacy `/bar` Input

The `/bar` route remains available for compatibility with the existing position-control path.

Its current range calculation begins with:

```text
/bar N
→ number box
→ t b i i
```

The two integer branches update:

```text
Start Bar      = N
Number of Bars = 17 - N
```

This represents playback from Measure `N` through Measure 16.

The new typed multistem interface uses `/play_stems`, `/play_all`, and `/stop`; it does not depend on `/bar`.

## 7. Shared Range Calculation

The score currently uses:

```text
Tempo:        144 BPM
Time:         4/4
Score length: 16 Measures
Bar duration: 1666.667 ms
```

The shared calculations are:

```text
start_time_ms = (Start Bar - 1) × 1666.667
duration_ms   = Number of Bars × 1666.667
end_time_ms   = start_time_ms + duration_ms
```

These three values are collected as:

```max
pak 0. 0. 0.
```

with the list format:

```text
start_time_ms end_time_ms duration_ms
```

The list is stored in two separate `zl reg` objects because the two playback engines require different trigger messages.

### Local stem transport

```text
Local PLAY
→ local zl reg
→ $1, $2 $3
→ line~ @activeout 1
```

### Full Mix range transport

```text
Full Mix range trigger
→ Full Mix zl reg
→ seek $1 $2
→ sfplay~ 2
```

## 8. Shared Local Stem Transport

`line~ @activeout 1` has three current outputs:

```text
left signal   → s~ braille_playhead
middle signal → s~ braille_playgate
right bang    → playback-finished indicator only
```

The right completion bang does not control Global Stop, Track gain, Master gain, or Reverb gain.

Every `stem_player` abstraction receives the same `braille_playhead`, so all selected stems read the same position at signal rate.

## 9. `stem_player.maxpat`

Each abstraction is instantiated with:

```max
stem_player filename.wav track_id
```

Inside each instance:

```text
buffer~ #0_stem #1
r~ braille_playhead
→ play~ #0_stem 2
```

The playback gate is:

```text
r~ braille_playgate
→ rampsmooth~ 240 240
→ stereo *~ objects
```

The confirmed stereo audio path is:

```text
play~ stereo outputs
→ playback-gate *~ objects
→ live.gain~
→ s~ braille_stem_L
→ s~ braille_stem_R
```

Track selection is received through:

```text
r braille_track_gain
→ route #2 all
→ sel 0 1
```

Gain states are:

```text
0 → -70 dB
1 → 0 dB
```

## 10. Local Dry/Wet Output

The 29 local stems are summed through:

```text
r~ braille_stem_L
r~ braille_stem_R
```

The bus splits into parallel Dry and Wet paths.

### Dry path

```text
r~ braille_stem_L/R
→ s~ braille_master_L/R
```

### Wet path

```text
r~ braille_stem_L/R
→ ValhallaVintageVerb
→ *~ 0.283
→ s~ braille_master_L/R
```

Confirmed Reverb settings relevant to routing:

```text
Mix = 1.0
Wet return multiplier = 0.283
```

No `braille_playgate` connection exists after the Valhalla output. The Wet return is therefore free to decay after local Dry input stops.

## 11. Full Mix Player

The current Full Mix file is:

```text
Mx_FullMix_L18_144bpm.wav
```

It is played by:

```max
sfplay~ 2
```

Its stereo outputs currently go directly to:

```text
s~ braille_master_L
s~ braille_master_R
```

Therefore the current Full Mix path bypasses `braille_stem_L/R` and ValhallaVintageVerb.

The file contains its own ending tail after the 16-measure score. That tail is available when playback reaches the end of the rendered file. A bounded `/play_all` command that stops earlier does not generate a new real-time Reverb tail at the selected endpoint.

No Dry Full Mix replacement or Full Mix rerouting has been applied.

## 12. Master Output

All audio reaches:

```text
r~ braille_master_L
r~ braille_master_R
→ stereo live.gain~
→ ezdac~
```

The Master output combines:

- local selected-stem Dry signal;
- local selected-stem Wet return;
- stereo Full Mix playback.

## 13. Current Command Summary

| OSC command | Playback source | Range format received by Max | Real-time Valhalla tail |
|---|---|---|---|
| `/play_stems start count tracks...` | Requested local stems | Start Measure + Number of Bars | Yes |
| `/play_all start count` | Stereo Full Mix through `sfplay~ 2` | Start Measure + Number of Bars | No; current Full Mix bypasses Valhalla |
| `/stop` | Stops local transport and Full Mix | None | Existing local Wet return remains free to decay |
| `/bar N` | Compatibility range path | Start Measure only | Existing compatibility behavior retained |

## 14. Excluded Designs

The following are not part of the current Max patch architecture and are intentionally excluded:

- opening all 29 local stems for `/play_all`;
- an `all 1.` operation in the `/play_all` branch;
- routing `/play_all` into Local PLAY;
- sending the `line~` completion bang into Global Stop;
- a Dry Full Mix file routed through the shared Reverb;
- physical Button integration beyond the current Max UI controls.
