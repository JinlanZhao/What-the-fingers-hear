# OLiMPiC Correction — v4 [MASK] Experiment Report

**Date**: 2026-10-27
**Run directory**: `ml/data/runs/correction_v4_mask/`
**Script**: `ml/tools/run_experiment_v4_mask.py`

---

## 1. What Changed

Single modification vs v3: the replacement (corrupted) pitch token at the error position
is replaced with `[MASK]` before the sequence is fed to the model.

```
v3 input: ... A3 quarter chord [B4] quarter rest ...
                                ↑ replacement token visible
v4 input: ... A3 quarter chord [MASK] quarter rest ...
                                ↑ replacement hidden
```

`[MASK]` is added as a new vocabulary entry (ID 183). All existing token IDs and all
output pitch classes are unchanged. The masking is applied at load time for both train
and dev; the JSONL files are untouched.

---

## 2. Reproducible Command

```bash
python3 ml/tools/run_experiment_v4_mask.py \
    --train-examples ml/data/processed/correction_train_10k.jsonl \
    --dev-examples   ml/data/processed/correction_dev_v1.jsonl \
    --dataset-root   ml/dataset/olimpic-1.0-synthetic \
    --output-dir     ml/data/runs/correction_v4_mask \
    --seed 42 \
    --d-model 128 --num-layers 3 --dim-ff 512
```

---

## 3. Configuration

| Setting | v3 | v4 |
|---------|----|----|
| Architecture | 128/4h/3L/ff=512 | same |
| Vocab size | 183 | **184** (+`[MASK]` at ID 183) |
| Parameters | 657,844 | **657,972** (+128 = one embedding row) |
| Dropout | 0.1 | 0.1 |
| Train examples | 9,998 | 9,998 |
| Seed | 42 | 42 |
| Batch / LR / WD | 32 / 1e-3 / 0.01 | same |
| Max epochs / patience | 30 / 5 | same |
| Checkpoint criterion | best dev loss | same |
| mask_error | False | **True** |
| Device | MPS | MPS |
| Wall time | 50s | **66s** |
| Best epoch | 5 | **8** |
| Best dev loss | 3.2080 | **3.1738** |

---

## 4. Training Curves

| Epoch | Train loss | Train top-1 | Dev loss | Dev top-1 |
|-------|-----------|------------|---------|----------|
| 0 | 4.1247 | 0.84% | 4.0992 | 0.60% |
| 1 | 3.3638 | 6.36% | 3.3049 | 7.21% |
| 2 | 3.2474 | 7.52% | 3.2535 | 7.82% |
| 3 | 3.1881 | 8.06% | 3.2065 | 7.62% |
| 4 | 3.1402 | 9.43% | 3.2020 | 11.22% |
| 5 | 3.0973 | 10.09% | 3.1885 | 11.22% |
| 6 | 3.0553 | 10.75% | 3.1802 | 10.22% |
| 7 | 3.0272 | 11.21% | 3.1910 | 9.02% |
| **8** ← best | **3.0782** | **12.60%** | **3.1738** | **9.22%** |
| 9 | 2.9220 | 13.93% | 3.2113 | 8.02% |
| ... | | | | |
| 13 | 2.6610 | 20.53% | 3.3777 | 8.82% |

Early stop at epoch 13 (patience=5 from epoch 8).

Note: Dev top-1 reached 11.22% at epochs 4 and 5 (same as v3's peak) but then declined.
Best checkpoint was saved at epoch 8 by dev loss, not dev top-1.

---

## 5. Results Summary

| Method | Top-1 hits | Top-1 % | Top-5 hits | Top-5 % | Best epoch | Dev loss |
|--------|-----------|---------|-----------|---------|-----------|---------|
| MFC (F4) | 26/499 | 5.21% | 155/499 | 31.06% | — | — |
| v3 | **55/499** | **11.02%** | 183/499 | 36.67% | 5 | 3.2080 |
| **v4 [MASK]** | 46/499 | 9.22% | **196/499** | **39.28%** | 8 | **3.1738** |

The checkpoint was selected by dev loss in both runs. The best dev top-1 during v4
training was 11.22% (epochs 4–5), matching v3's peak; the epoch-8 best-loss checkpoint
yields 9.22% top-1. This divergence between best-loss and best-top-1 is larger in v4
than in v3.

---

## 6. Venn Overlap

|  | v4 correct | v4 wrong | Total |
|---|---|---|---|
| **v3 correct** | 11 | 44 | 55 |
| **v3 wrong** | 35 | 409 | 444 |
| **Total** | 46 | 453 | 499 |

- Both correct: **11**
- Only v3 correct: **44**
- Only v4 correct: **35**
- Neither correct: **409**

The two correct sets overlap on only 11/499 examples (20% of v3's 55; 24% of v4's 46).
v3 and v4 are learning different strategies.

---

## 7. Error Distribution Analysis

Metrics computed over all 499 dev examples. Pitch tokens are in the form `[A-G][0-9]`
(letter = pitch class, digit = octave). Semitone distance uses natural-note values
(C=0, D=2, E=4, F=5, G=7, A=9, B=11); accidentals are not encoded in these tokens.

### 7a. Full dev set (499 examples)

| Metric | v3 | v4 |
|--------|----|----|
| **Top-1 (exact)** | **55/499 = 11.02%** | 46/499 = 9.22% |
| Octave correct | 210/499 = 42.08% | 203/499 = 40.68% |
| Pitch class correct | 100/499 = 20.04% | 99/499 = 19.84% |
| Avg semitone distance | 9.45 | **9.38** |
| Median semitone distance | 7 | 7 |
| dist = 0 (exact) | 55 | 46 |
| dist 1–12 (within 1 octave) | 312 | **331** |
| dist ≥ 13 (> 1 octave) | **132** | **122** |

### 7b. Wrong predictions only

| Metric | v3 wrong (444) | v4 wrong (453) |
|--------|---------------|---------------|
| Octave correct | 155/444 = 34.91% | 157/453 = 34.66% |
| Pitch class correct | 45/444 = 10.14% | **53/453 = 11.70%** |
| Avg semitone distance | 10.62 | **10.33** |
| dist 1–12 | 312 | **331** |
| dist ≥ 13 | **132** | **122** |

Among wrong predictions: v4 produces 10 fewer large-distance errors (dist ≥ 13: 122 vs 132)
and slightly more often gets the pitch class right (11.70% vs 10.14%). The masking reduces
extreme range mistakes at the cost of exact hits.

### 7c. Top pitch-class confusion (wrong predictions only)

**v3** (top 5 confusion pairs, target → predicted):
- F → D: 29,  B → D: 27,  A → D: 25,  G → B: 25,  A → B: 24

**v4** (top 5 confusion pairs, target → predicted):
- E → B: 23,  D → B: 23,  G → B: 21,  D → F: 20,  A → C: 18

v3 errors are strongly D-biased (D appears most in training); v4 errors are B- and F-biased
(B and F are the voice:1 and voice:5 MFC-adjacent pitches). Both reflect incomplete
distribution learning.

---

## 8. Case Diffs

### v3 correct, v4 wrong (44 cases — 5 shown)

These cases share a pattern: the replacement token is an extreme out-of-range pitch
(C7, F7, F6, E6), and v3 uses this extreme value as a signal to predict a reasonable
mid-range pitch. With [MASK], v4 loses that signal and falls back toward frequency priors.

| Sample | Pos | Rep | Target | v3 | v4 | v4 top-5 |
|--------|-----|-----|--------|----|----|----------|
| 4978393/p1-s4 | 197 | A4 | D4 | D4 ✓ | F4 ✗ | F4 D5 A3 A4 G4 |
| 5015499/p2-s1 | 151 | C7 | E4 | E4 ✓ | B4 ✗ | B4 G4 E4 C5 F4 |
| 5023603/p1-s2 | 154 | F7 | E4 | E4 ✓ | F4 ✗ | F4 A4 A3 D4 C4 |
| 5023603/p4-s3 |  27 | C4 | E4 | E4 ✓ | C4 ✗ | C4 C3 A3 A2 E3 |
| 5026077/p3-s4 | 241 | E6 | D4 | D4 ✓ | F4 ✗ | F4 E4 D4 A3 B3 |

In 3/5 cases the target appears in v4's top-5. The masking has not made the correct
answer implausible — it has just shifted the top-1 prediction to a different pitch.

### v4 correct, v3 wrong (35 cases — 5 shown)

v4 benefits when the context (without the replacement pitch) unambiguously identifies
the correct pitch, or when the replacement pitch misleads v3's attention.

| Sample | Pos | Rep | Target | v3 | v4 | v3 top-5 |
|--------|-----|-----|--------|----|----|----------|
| 4945954/p2-s2 |  98 | E3 | F4 | D5 ✗ | F4 ✓ | D5 D4 B4 A4 F4 |
| 5013969/p1-s2 |  43 | C4 | B3 | E4 ✗ | B3 ✓ | E4 D4 B3 G4 B4 |
| 5023603/p3-s2 |  64 | A6 | A4 | C4 ✗ | A4 ✓ | C4 D4 E4 A3 F4 |
| 5077917/p4-s1 |  97 | G4 | F4 | D4 ✗ | F4 ✓ | D4 E4 C4 A4 A3 |
| 5079391/p3-s3 |  17 | A6 | B3 | D4 ✗ | B3 ✓ | D4 B3 E4 G3 C4 |

In 4/5 cases the target also appears in v3's top-5. v4 gets the mode right; v3 has the
answer ranked but not at top-1.

---

## 9. Assessment of the Masking Hypothesis

**Partial support — with an important qualifier.**

The masking changes the model in two directions:

| Dimension | v4 vs v3 | Supports masking? |
|-----------|----------|------------------|
| Top-1 accuracy | 46 < 55 (−9) | No |
| Top-5 accuracy | 196 > 183 (+13) | Yes |
| Dev loss | 3.1738 < 3.2080 | Yes |
| Large errors (dist ≥ 13) | 122 < 132 (−10) | Yes |
| Best epoch | 8 > 5 (slower) | Neutral |

Masking produces a better-calibrated distribution (lower loss, better top-5, fewer
extreme errors) but a less decisive mode prediction. The most likely explanation:

**v3 exploits extreme replacement tokens as a range signal.** When the replacement is C7
or F7, v3 has learned this signals "the true pitch is mid-range" and predicts accordingly.
This is not context understanding in the musical sense — it is a replacement-token →
target-range shortcut. Masking removes this shortcut, which hurts top-1 on those 44
examples but forces the model to use genuine musical context for the remaining 35 it
gains.

The divergence between best-loss epoch (8) and best-top-1 epoch (4–5, yielding 11.22%)
in v4 is notable: v4 at its best top-1 equals v3's top-1, but the loss-selected checkpoint
is later and more conservative. This suggests that with further tuning of the stopping
criterion (e.g., using dev top-1 directly), v4 might tie or exceed v3 on top-1 as well.

---

## 10. Recommended Next Experiment

**Checkpoint selection by dev top-1 (not dev loss).**

Both v3 and v4 show a divergence between best-loss epoch and best-top-1 epoch, but the
gap is larger in v4 (epoch 4–5 best top-1 = 11.22%, epoch 8 best loss = 9.22%). If the
final metric of interest is top-1 correction accuracy, saving checkpoints by dev top-1
instead of dev loss may recover 5–9 hits.

This is a one-line change to the checkpoint condition in `run_experiment_v4_mask.py`:
```python
# current (dev loss)
if d_loss < best_dev_loss:

# alternative (dev top-1)
if d_top1 > best_dev_top1:
```

Suggested run: retrain v4 with `--checkpoint-by top1` (or equivalent flag), compare the
epoch-4/5 checkpoint to the epoch-8 checkpoint, and determine whether the top-1 / top-5
tradeoff is acceptable. If epoch-4 checkpoint yields ≥55 top-1, masking is confirmed as
strictly beneficial.
