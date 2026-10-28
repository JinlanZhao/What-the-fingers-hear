# OLiMPiC Correction — Context Baseline Report

**Date**: 2026-10-27
**Script**: `ml/tools/context_baseline.py`
**Artifacts**: `ml/data/runs/context_baselines/context_baseline_results.json`

---

## 1. Motivation

v3 (128/3/512 Transformer, 10K train) reaches 55/499 = 11.02% dev top-1.
The question: does that performance come from learning genuine pitch-context relationships,
or does it mostly reproduce what simple pitch-neighbourhood rules already know?

This experiment tests two rule-based context baselines — `prev_pitch` (nearest preceding
same-voice pitch in the window) and `next_pitch` (nearest following same-voice pitch) —
against the model and the MFC_10k baseline, with no training.

---

## 2. Comparison Table — Full 499 Dev Examples

| Method | Hits | Top-1 | Notes |
|--------|------|-------|-------|
| MFC_10k | 26/499 | **5.21%** | Always predict F4 (most frequent in 10K train) |
| prev_pitch | 20/499 | 4.01% | Fallback to MFC on 23/499 examples |
| next_pitch | 17/499 | 3.41% | Fallback to MFC on 30/499 examples |
| **v3** | **55/499** | **11.02%** | 128/3/512 Transformer, epoch 5 |

Both context baselines fall **below** MFC. Pitch-neighbour copying is actively harmful
compared to always guessing the most common pitch.

Coverage (same-voice neighbour found within window):

| Baseline | Neighbour found | Coverage |
|----------|----------------|----------|
| prev_pitch | 476/499 | 95.39% |
| next_pitch | 469/499 | 93.99% |

Coverage is high. The failure is not missing neighbours — it is that neighbours give
wrong predictions.

---

## 3. Subset Accuracy (Neighbour-Available Examples Only)

Comparing all methods on the same subset isolates whether pitch repetition beats chance
when a neighbour exists.

| Subset | n | prev/next | MFC | v3 |
|--------|---|-----------|-----|----|
| prev available | 476 | 18/476 = **3.78%** | 24/476 = 5.04% | 52/476 = 10.92% |
| next available | 469 | 15/469 = **3.20%** | 24/469 = 5.12% | 53/469 = 11.30% |

Within the neighbour-available subset, both baselines still underperform MFC.
v3 is 2.2–3.5× better than MFC on the same subsets.

---

## 4. Venn Overlap — v3 vs Context Baselines

### v3 vs prev_pitch (n = 499)

| | prev correct | prev wrong | Total |
|---|---|---|---|
| **v3 correct** | 1 | 54 | 55 |
| **v3 wrong** | 19 | 425 | 444 |
| **Total** | 20 | 479 | 499 |

- Both correct: **1**
- Only v3 correct: **54**
- Only prev correct: **19**
- Neither correct: **425**

### v3 vs next_pitch (n = 499)

| | next correct | next wrong | Total |
|---|---|---|---|
| **v3 correct** | 2 | 53 | 55 |
| **v3 wrong** | 15 | 429 | 444 |
| **Total** | 17 | 469 | 499 |

- Both correct: **2**
- Only v3 correct: **53**
- Only next correct: **15**
- Neither correct: **429**

The overlap between v3 and the context baselines is near zero (1–2 examples). The model
correct set and the pitch-neighbour correct set are nearly disjoint. v3 is not replicating
what pitch-copying does.

---

## 5. Case Diffs

### v3 correct, prev_pitch wrong (54 cases — 3 shown)

**Case 1** — `samples/6456450/p6-s3`, orig_pos=176, voice=`voice:5`
```
context: ...A3 quarter chord [B4] quarter rest quarter...
replacement='B4'  target='D4'
v3='D4'  prev='A3'  next='D3'
```
prev gives A3 (wrong); v3 predicts D4 correctly despite B4 → D4 being a non-trivial
2-octave register shift. Neither the preceding nor following voice:5 pitch matches.

**Case 2** — `samples/6202660/p2-s1`, orig_pos=209, voice=`voice:1`
```
context: ...eighth beam:begin chord [C7] eighth A4 eighth...
replacement='C7'  target='D5'
v3='D5'  prev='A4'  next='A4'
```
C7 is an extreme outlier (7th octave). Both the prev and next neighbour give A4;
v3 recognises the octave implausibility and predicts D5 (reasonable soprano range).

**Case 3** — `samples/6264558/p1-s2`, orig_pos=80, voice=`voice:1`
```
context: ...G2 whole measure [B1] voice:1 eighth stem:up...
replacement='B1'  target='E4'
v3='E4'  prev='G3'  next='C4'
```
B1 is far below treble-clef range; context neighbours (G3, C4) are not E4.
v3 identifies the correct register-corrected pitch despite neighbours not matching.

### prev_pitch correct, v3 wrong (19 cases — 3 shown)

**Case 4** — `samples/5935864/p6-s4`, orig_pos=112, voice=`voice:6`
```
context: ...tremolo:3 backup whole [A0] voice:6 half dot...
replacement='A0'  target='F2'
v3='C4'  prev='F2'  next='A2'
```
F2 repeats exactly from the preceding voice:6 note. v3 predicts C4 (a common pitch)
instead of trusting the local repetition. This is the case where pitch-copying wins.

**Case 5** — `samples/6085883/p1-s2`, orig_pos=69, voice=`voice:5`
```
context: ...eighth dot beam:begin [C5] 16th beam:end beam:backward-hook...
replacement='C5'  target='G3'
v3='D4'  prev='G3'  next='F3'
```
Target G3 matches the preceding voice:5 note exactly. v3 predicts D4 instead.

**Case 6** — `samples/5058194/p1-s3`, orig_pos=172, voice=`voice:5`
```
context: ...beam:end backup whole [E4] voice:5 whole staff:2...
replacement='E4'  target='D2'
v3='B4'  prev='D2'  next=None
```
Target D2 is a low bass note; prev is also D2. v3 predicts B4 (treble range).
The model fails on low-register corrections where the preceding note is a reliable cue.

---

## 6. Summary of Findings

1. **Pitch-neighbour baselines are below MFC.** Copying the nearest same-voice pitch
   (4.01% / 3.41%) is worse than always predicting F4 (5.21%). The task is not
   solved by local pitch repetition.

2. **v3 is 2× MFC and largely disjoint from context baselines.** The overlap between
   v3-correct and context-correct is ≤2 examples (out of 55 v3 hits). The model is
   extracting a different signal than pitch copying.

3. **The 19 prev-beats-v3 cases share a pattern.** They tend to be exact pitch
   repetitions across adjacent same-voice notes (especially in low registers that the
   model underpredicts). These are the "easy" cases where pure repetition works.

4. **The 54 v3-beats-prev cases involve register correction.** The replacement token
   is in an implausible register (e.g., C7, B1, A0); the correct pitch is elsewhere,
   and the context neighbours do not happen to be the target. The model has learned
   some notion of pitch plausibility beyond what neighbours alone encode.

---

## 7. Recommended Next Hypothesis

**Hypothesis: v3's signal comes from pitch-class frequency conditioned on voice token.**

The model may be learning "given voice:N, predict the pitch class that appears most
often in that voice in the training data" rather than reading local melodic context.
This would explain why:
- It outperforms generic MFC (which ignores voice)
- It beats pitch-neighbour copying (which is context-dependent but noisy)
- Its correct cases cluster around common pitches (D4, E4, D5 are all in the top-5
  training targets)

**Test**: Compute per-voice MFC from training data. Evaluate `voice_mfc` on the dev set.
If `voice_mfc` ≥ v3, the model has essentially learned this lookup table. If v3 > `voice_mfc`
by a significant margin, the model is extracting something beyond marginal voice-conditional
distributions.

This test requires only loading pitch_classes and computing per-voice frequency from the
train JSONL — no model inference needed.
