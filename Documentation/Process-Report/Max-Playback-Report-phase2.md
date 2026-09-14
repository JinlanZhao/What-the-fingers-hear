# Max Playback System — Phase 2 Process Report

## 1. Phase 2 Scope

Phase 2 extended the existing synchronized 29-stem playback system with:

- full-piece stereo playback;
- shared reverb for local stem playback, including an audible reverb tail;
- unique control IDs for all stem-player instances;
- per-stem mute/unmute routing;
- a prototype Solo + Play command sequence.

The existing shared signal-rate `braille_playhead` and `braille_playgate` transport remained unchanged.

## 2. Full-Piece Playback

An exported 18-bar stereo file, `Mx_FullMix_L18_144bpm.wav`, was added for uninterrupted playback of the complete piece, including the two-bar ending tail.

The file is loaded and played with:

```max
sfplay~ 2
```

Its stereo outputs are sent directly to:

```max
s~ braille_master_L
s~ braille_master_R
```

This full-piece player is independent from the local 29-stem playback engine. It is used when no individual stem control is required.

## 3. Local Dry/Wet Reverb System

The 29 dry stems are summed through:

```max
r~ braille_stem_L
r~ braille_stem_R
```

The summed signal is split into two parallel paths:

### Dry path

```max
r~ braille_stem_L/R
→ s~ braille_master_L/R
```

### Wet path

```max
r~ braille_stem_L/R
→ ValhallaVintageVerb
→ wet gain
→ s~ braille_master_L/R
```

`ValhallaVintageVerb` is set to `Mix = 1`, so the plug-in output contains only the wet signal. The wet return is scaled to approximately `0.283` before being added to the master bus.

Because the reverb is placed after the shared stem bus, the dry stems stop at the requested end time while the generated reverb continues naturally. Local playback and quick retriggering were checked with this shared reverb configuration.

## 4. Stem Identification

Each `stem_player` abstraction now receives two arguments:

```max
stem_player filename.wav track_id
```

Example:

```max
stem_player 21_STR_vln1.wav vln1
```

Inside the abstraction:

- `#1` identifies the audio filename;
- `#2` identifies the control name for that stem.

The current track IDs are:

```text
Woodwinds:  fl1 fl2 ob1 ob2 cl1 cl2 bsn1 bsn2
Brass:      fh1 fh2 fh3 fh4 tpt1 tpt2 tbn1 tbn2 tb
Percussion: glk bd sn
Strings:    vln1 vln2 vla vc cb
Others:     crash riser room stem
```

## 5. Per-Stem Mute/Unmute Routing

Track-control messages are broadcast from the main patch through:

```max
s braille_track_gain
```

Each `stem_player` receives them through:

```max
r braille_track_gain
→ route #2 all
→ sel 0 1
```

The first `route` outlet accepts a command addressed to that instance's track ID. The second accepts the shared `all` command. Both feed the same `sel 0 1` control.

The selected state controls the existing stereo `live.gain~`:

```text
0 → -70 dB
1 → 0 dB
```

Example commands:

```max
vln1 0.    // mute vln1
vln1 1.    // enable vln1
all 0.     // attenuate all stems
all 1.     // restore all stems
```

The audio path inside `stem_player` remains:

```text
play~ stereo outputs
→ playback-gate *~ objects
→ live.gain~
→ s~ braille_stem_L/R
```

## 6. Solo + Play Prototype

Solo requires two track-state operations before playback:

```text
1. all 0.
2. selected_track 1.
3. Local PLAY
```

The first prototype uses `vln1` as the selected track. A `trigger` object guarantees execution order:

```max
t b b b
```

Because `trigger` fires from right to left, its outlets are assigned as follows:

```text
right outlet  → all 0.
middle outlet → vln1 1.
left outlet   → Local PLAY
```

This produces:

```text
Mute All → Enable vln1 → Start Local Playback
```

The same command structure can be reproduced for the remaining track IDs. A separate `all 1.` command restores full-stem playback.

## 7. Current Status

Completed in Phase 2:

- 18-bar full-piece stereo player;
- parallel dry and 100% wet reverb routing;
- local reverb tail after the selected playback range;
- unique control IDs for all 29 `stem_player` instances;
- shared track-control message bus;
- reusable per-instance mute/unmute routing;
- an ordered `vln1` Solo + Play prototype, ready to be used as the template for the remaining tracks.
