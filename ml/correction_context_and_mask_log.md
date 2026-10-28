# OLiMPiC Correction — Context Baselines & [MASK] Experiment Log

**Date**: 2026-10-27
**Author**: Jinlan Zhao
**Scope**: Everything after v2/v3. Four rounds of work:
context rule baselines → voice-conditional baseline → v4 [MASK] (loss criterion) →
v4 [MASK] (top-1 criterion) + v3 top-1 re-run for comparison.

**Starting point**: v3 (128/3/512, 10K train, seed=42, dev-loss checkpoint) = 55/499 = 11.02% dev top-1.

---

## 1. Motivation for This Round

v3 reaches 11.02% — roughly 2× the MFC baseline. The open question was:
how much of that signal comes from genuine musical context understanding
vs. simple pitch-frequency memorisation?

Three diagnostic questions drove this round:

1. Do simple pitch-neighbourhood rules already explain most of v3's correct answers?
2. Does conditioning on voice token (per-voice MFC) narrow the gap with v3?
3. Does masking the replacement token — forcing the model to use context alone — help or hurt?

---

## 2. Scripts and Artifacts Created

| File | Purpose |
|------|---------|
| `ml/tools/context_baseline.py` | Prev/next-pitch and MFC_10k baselines |
| `ml/tools/voice_mfc_baseline.py` | Per-voice MFC baseline |
| `ml/tools/run_experiment_v4_mask.py` | v4 training with `[MASK]` + `--checkpoint-by` flag |
| `ml/tools/run_experiment_v1.py` | Added `--checkpoint-by` flag (4-line edit) |
| `ml/data/runs/context_baselines/` | context_baseline_results.json (499 records) |
| `ml/data/runs/correction_v4_mask/` | v4 artifacts (loss checkpoint) |
| `ml/data/runs/correction_v4_mask_top1/` | v4 artifacts (top-1 checkpoint) |
| `ml/data/runs/correction_v3_top1/` | v3 re-run (top-1 checkpoint) |
| `ml/correction_context_baseline_report.md` | Context baseline results |
| `ml/correction_v4_mask_report.md` | v4 [MASK] experiment report |
| `ml/correction_v2_v3_addendum.md` | Five corrections to the v2/v3 log |

---

## 3. Round 1 — Context Rule Baselines

**Script**: `context_baseline.py`
**Hypothesis**: If pitch-neighbourhood rules (copy the nearest same-voice note) already
explain most of v3's correct answers, the model is not learning genuine musical context.

### Method

For each dev example, the same 257-token window the model sees is processed with a
`build_voice_map` function that tracks voice labels per pitch position using the LMX
voice token convention (standalone notes: `voice:N` immediately follows the pitch;
chord notes inherit the running voice). Two rule-based predictions:

- **prev_pitch**: nearest preceding same-voice pitch in the window; fall back to MFC if none.
- **next_pitch**: nearest following same-voice pitch in the window; fall back to MFC if none.

Coverage was high (95%+ found a neighbour). The comparison was fair: both rules and v3
operate on the same windowed sequence.

### Results

| Method | Top-1 | Notes |
|--------|-------|-------|
| MFC_10k (F4) | 26/499 = 5.21% | — |
| prev_pitch | 20/499 = 4.01% | 23 fallbacks |
| next_pitch | 17/499 = 3.41% | 30 fallbacks |
| v3 | 55/499 = 11.02% | — |

**Finding**: Both pitch-neighbour rules fell *below* MFC. Copying the nearest same-voice
pitch is actively harmful compared to always predicting F4. The Venn overlap between v3's
correct set and the context baselines was near zero (1–2 shared examples out of 55 v3
hits). v3 is not doing pitch-copying.

The 19 cases where prev_pitch beats v3 are mostly exact pitch repetitions in low registers.
The 54 cases where v3 beats prev_pitch tend to involve implausible-register replacement
tokens (C7, B1, A0) where the model somehow predicts the correct pitch despite neighbours
being unhelpful.

---

## 4. Round 2 — Voice-Conditional MFC Baseline

**Script**: `voice_mfc_baseline.py`
**Hypothesis**: v3's signal comes from learning per-voice pitch frequency, not from
reading local melodic context. Test: does per-voice MFC match v3?

### Method

Apply `build_voice_map` to each training example (same window logic as above) to
identify the voice at the error position. Build a per-voice Counter of target pitch
frequencies. Predict the most frequent target for that voice; fall back to global MFC
if voice unseen (0 fallbacks in practice).

### Per-voice frequency table (10K train)

| Voice | n train | MFC | Top-3 targets |
|-------|---------|-----|---------------|
| voice:1 | 5,283 | F4 | F4=494, G4=459, E4=453 |
| voice:2 | 704 | E4 | E4=96, D4=85, F4=72 |
| voice:5 | 3,589 | A3 | A3=284, F3=274, E3=251 |
| voice:6 | 383 | A2 | A2=32, B2=30, D2=30 |
| voice:3/4/7/8 | <20 each | varied | — |

The pattern is musically sensible: voice:1 (soprano) clusters in F4–G4; voice:5 (alto/tenor)
clusters in A3; voice:6 (bass) tops at A2.

### Results

| Method | Top-1 |
|--------|-------|
| MFC_10k (global) | 26/499 = 5.21% |
| prev_pitch | 20/499 = 4.01% |
| voice_mfc | 46/499 = 9.22% |
| v3 | 55/499 = 11.02% |

**Finding**: voice_mfc is a large jump over global MFC (+20 examples), confirming that
voice-conditional pitch frequency is real signal. But v3 still exceeds voice_mfc by 9
examples. Crucially, the Venn overlap between v3-correct and voice_mfc-correct is only
1 example (out of 55). They are finding almost entirely different correct answers:
voice_mfc tends to get voice:5 cases right (A3 is the mode); v3 tends to get cases
with extreme replacement tokens right.

**Interpretation update**: v3 is not simply learning per-voice MFC either. The two
correct sets being nearly disjoint is a strong signal that v3 has learned some third
strategy, not easily characterised by these simple rules.

---

## 5. Round 3 — v4 [MASK] Experiment

### 5a. Hypothesis

The replacement token at the error position is an obviously wrong pitch. v3 sees it.
Two competing effects:

1. **Helpful**: extreme replacement tokens (C7, F7, A0) signal "this is implausible" and
   the model uses that signal to narrow range predictions.
2. **Harmful**: the model's attention may partially anchor on the replacement token's pitch
   class or octave, introducing noise into predictions for cases where the replacement is
   close to real pitches.

Masking the replacement with `[MASK]` removes both effects simultaneously and forces
the model to rely on surrounding context alone.

### 5b. Implementation

Single change to data loading: after `window_tokens()` extracts the windowed sequence,
`window[w_pos] = "[MASK]"` before tokenisation. Applied identically to train and dev.

- New token `[MASK]` added to vocabulary with ID 183 (vocab_size 183 → 184).
- All existing token IDs and output pitch classes unchanged.
- Extra parameter count: +128 (one embedding row at d_model=128). v4: 657,972 params.
- Architecture, data (10K train), seed (42), optimizer, LR (1e-3), WD (0.01),
  batch (32), dropout (0.1), max_epochs (30), patience (5): identical to v3.
- Checkpoint criterion: **dev loss** (same as v3). Output: `correction_v4_mask/`.

### 5c. Training curve (loss criterion)

| Epoch | Train top-1 | Dev loss | Dev top-1 |
|-------|------------|---------|----------|
| 0 | 0.84% | 4.0992 | 0.60% |
| 1 | 6.36% | 3.3049 | 7.21% |
| 2 | 7.52% | 3.2535 | 7.82% |
| 3 | 8.06% | 3.2065 | 7.62% |
| **4** | 9.43% | 3.2020 | **11.22%** ← peak top-1 |
| 5 | 10.09% | 3.1885 | 11.22% |
| 6 | 10.75% | 3.1802 | 10.22% |
| 7 | 11.21% | 3.1910 | 9.02% |
| **8** ← loss best | 12.60% | **3.1738** | 9.22% |
| 9 | 13.93% | 3.2113 | 8.02% |
| 10 | 15.02% | 3.1814 | 11.02% |
| 11 | 16.73% | 3.2936 | 7.82% |
| 12 | 18.85% | 3.3449 | 9.22% |
| 13 ← stop | 20.53% | 3.3777 | 8.82% |

Best dev loss = 3.1738 at epoch 8. Best dev top-1 during training = 11.22% at epochs 4–5.

### 5d. Result (loss criterion)

| Method | Top-1 | Top-5 | Best epoch | Dev loss |
|--------|-------|-------|-----------|---------|
| v3 | 55/499 = 11.02% | 183/499 = 36.67% | 5 | 3.2080 |
| v4 [MASK] (loss) | **46/499 = 9.22%** | **196/499 = 39.28%** | 8 | **3.1738** |

**Initial interpretation**: masking hurt top-1 (−9) but improved top-5 (+13) and achieved
lower dev loss (3.1738 < 3.2080). The model is better calibrated but predicts the wrong
mode.

The divergence between best-loss epoch (8, top-1=9.22%) and best-top-1 epoch (4–5,
top-1=11.22%) in v4 is notable. v3 had no such divergence: its best-loss epoch (5) was
also its best-top-1 epoch.

---

## 6. Round 4 — Checkpoint Criterion Experiments

### 6a. Observation

In v4 (loss), the best dev top-1 (11.22%) occurred at epochs 4–5 but the loss criterion
saved epoch 8 (top-1=9.22%). For v3, epochs 5's best loss also happened to be best top-1.
This raises the question: is v4 actually better than v3, but the wrong criterion was used?

### 6b. v4 [MASK] re-run with top-1 criterion

Same command as v4 (loss) plus `--checkpoint-by top1`.
Output: `correction_v4_mask_top1/`.

Training curve (relevant epochs):

| Epoch | Train top-1 | Dev loss | Dev top-1 |
|-------|------------|---------|----------|
| 1 | 6.26% | 3.2973 | 8.42% |
| ... | | | |
| 6 | 9.74% | 3.2353 | **11.22%** ← 1st save |
| ... | | | |
| 9 | 12.02% | 3.1833 | 12.42% ← 2nd save |
| 10 | 13.36% | 3.1578 | 12.22% |
| **11** ← top-1 best | 14.74% | 3.1743 | **12.63%** ← saved |
| 12 | 16.05% | 3.2306 | 8.62% |
| ... | | | |
| 14 | 18.09% | 3.2816 | 12.63% (ties, patience continues) |
| 16 ← stop | 21.14% | 3.2894 | 9.62% |

**Result**: 63/499 = 12.63% top-1, 197/499 = 39.48% top-5, best epoch 11.

Note: this run's training curve diverges from the v4 (loss) run despite the same seed.
Epochs 1–2 differ (v4 loss ep1: dev_top1=7.21%; v4 top-1 ep1: dev_top1=8.42%). MPS
(Metal) does not guarantee bit-identical results across separate runs even with the same
seed. All four runs in this section should be treated as samples from the same
distribution, not as identical-seed controlled comparisons.

### 6c. v3 re-run with top-1 criterion

To make the comparison symmetric, v3 was re-run with `--checkpoint-by top1`.
Output: `correction_v3_top1/`.

Training curve (peak epoch):

| Epoch | Train top-1 | Dev loss | Dev top-1 |
|-------|------------|---------|----------|
| ... | | | |
| **10** ← top-1 best | 12.11% | 3.2662 | **9.42%** ← saved |
| 11 | 13.06% | 3.2941 | 8.22% |
| ... | | | |
| 15 ← stop | 20.68% | 3.4226 | 8.22% |

**Result**: 47/499 = 9.42% top-1, 181/499 = 36.27% top-5, best epoch 10.

Critically: v3 (top-1 criterion) peaked at 9.42%, never reaching the 11.02% that the
original v3 (loss criterion) achieved. The original v3's epoch 5 had dev_loss=3.2080
*and* dev_top1=11.02%; this run's epoch 5 had dev_top1=8.22%. The two trajectories
diverged from epoch 2 (loss: 3.2567 vs 3.2689). This confirms MPS non-determinism.

---

## 7. Summary Table — All Runs

| Run | Checkpoint by | Top-1 | Top-5 | Best epoch | Dev loss at ckpt | Params |
|-----|--------------|-------|-------|-----------|-----------------|--------|
| MFC (F4) | — | 26/499 = **5.21%** | 155/499 = 31.06% | — | — | — |
| prev_pitch | — | 20/499 = 4.01% | — | — | — | — |
| next_pitch | — | 17/499 = 3.41% | — | — | — | — |
| voice_mfc | — | 46/499 = 9.22% | — | — | — | — |
| v3 | loss | 55/499 = **11.02%** | 183/499 = 36.67% | 5 | 3.2080 | 657,844 |
| v4 [MASK] | loss | 46/499 = 9.22% | 196/499 = **39.28%** | 8 | **3.1738** | 657,972 |
| v4 [MASK] | top-1 | **63/499 = 12.63%** | 197/499 = **39.48%** | 11 | 3.1743 | 657,972 |
| v3 (re-run) | top-1 | 47/499 = 9.42% | 181/499 = 36.27% | 10 | 3.2662 | 657,844 |

---

## 8. Cross-Run Venn Analysis (all four model runs)

Pairwise overlap between correct sets:

| Pair | Overlap | Out of (smaller set) |
|------|---------|----------------------|
| v3(loss) ∩ v4(loss) | 11 | 46 = 23.9% |
| v3(loss) ∩ v4(top1) | 22 | 55 = 40.0% |
| v3(loss) ∩ v3(top1) | 16 | 47 = 34.0% |
| v4(loss) ∩ v4(top1) | 14 | 46 = 30.4% |
| v3(top1) ∩ v4(loss) | 17 | 46 = 37.0% |
| v3(top1) ∩ v4(top1) | 20 | 47 = 42.6% |

Examples correct in **all four** runs: **3/499**.
Examples wrong in **all four** runs: **363/499 = 72.7%**.

Even two runs of the same model with the same seed (v3 loss vs v3 top-1) only share 16/47
correct examples. The task is hard and the 499-example dev set is noisy enough that which
examples get correctly predicted changes substantially between runs.

---

## 9. What These Results Show

### 9a. Established findings

1. **Pitch-neighbour copying is below MFC** (4.01%/3.41% vs 5.21%). The model is not
   doing simple pitch repetition.

2. **Voice-conditional MFC is real signal** (9.22%), significantly above global MFC,
   and sensible musically (voice:1 = soprano range; voice:6 = bass range).

3. **v3 is not just voice-MFC**. v3 (11.02%) exceeds voice_mfc (9.22%) and their correct
   sets have near-zero overlap (1 shared example). v3 must be exploiting something
   beyond marginal voice-pitch frequency.

4. **All four model runs are largely disjoint in what they get right**. Only 3 examples
   are correct in all four runs. 72.7% are wrong in all four runs. Models of this size
   on this dataset are each finding a partial, different solution to the task.

### 9b. What is ambiguous

5. **The [MASK] hypothesis cannot be cleanly tested on MPS**. v4(loss) vs v3(loss) under
   identical-seed conditions is not bit-reproducible on MPS hardware. The four runs are
   four different stochastic trajectories. "v4(top1) = 63 > v3(loss) = 55" is a true
   empirical fact, but attributing the difference solely to masking requires caution.

6. **Checkpoint criterion interacts strongly with the result**:
   - v3(loss) = 55, v4(loss) = 46 → loss criterion favours v3
   - v3(top1) = 47, v4(top1) = 63 → top-1 criterion favours v4 by 16 examples
   - Under neither criterion does the "same" model appear twice, due to non-determinism

7. **The top-1 criterion may be selecting noisy peaks**. Dev top-1 on 499 examples
   fluctuates by ~5–8 pp between adjacent epochs (see v4-top1 ep8=11.22%, ep9=12.42%,
   ep10=12.22%, ep11=12.63%, ep12=8.62%). A run that happens to hit a high peak epoch
   will look better than a run that doesn't. Loss is smoother and arguably less subject
   to this noise.

8. **The original v3 (11.02%) may have been a lucky epoch**. In the v3 re-run with the
   same seed, the same epoch-5 only reached 8.22% top-1 (vs 11.02% originally). The
   training trajectory diverged from epoch 2 onward. The "11.02%" figure is one sample
   from a distribution, not a fixed point.

### 9c. The v3 advantage over context rules

Looking at cases where v3 is correct but context rules fail, a pattern emerges:
the replacement token is often an extreme out-of-range pitch (C7, F7, E6, A0). v3 seems
to have learned "when I see an octave-7 or octave-0 pitch, the target is probably in
a mid-range octave." This is not musical context understanding in the traditional sense
— it is a replacement-token-to-target-range mapping. Masking removes this shortcut,
which partially explains why v4(loss) drops below v3(loss): v4 loses those 44 cases
but gains 35 others.

Whether the 35 cases v4 gains represent genuine context-based prediction (unambiguous
from surrounding notes) or are simply a different noisy partial solution is unclear.
Of the 5 shown v4-gains, the patterns look musical (exact pitch repetition caught without
seeing the replacement), but 5 cases is not enough to conclude.

---

## 10. Open Questions

1. **Is the 63 real?** The v4(top1) result is 63/499 on this run. Running the same config
   from a different seed would test whether this is repeatable or a lucky trajectory.

2. **Is the training-curve noise a problem?** Dev top-1 varies by ~8 pp epoch-to-epoch
   on 499 examples. With k=499, a 1% shift is ~5 examples. The noise floor may be
   limiting how much we can conclude from single runs.

3. **What is v3 actually learning?** The correct sets of all four runs are largely
   disjoint from each other and from all rule-based baselines. Either the model is
   learning something genuinely different in each run, or each run is finding a
   different noisy partial memorisation of the dev set distribution.

4. **Does masking help on CPU (deterministic)?** Running v3 and v4 on CPU with a fixed
   seed would give exactly reproducible results and allow a clean comparison. The trade-off
   is speed (~10–20× slower than MPS for this model size).

---

## 11. Recommended Next Step

**Test reproducibility before changing the model further.**

Run v3 and v4(mask) both from the same seed (42) on CPU, identical in every way
except the masking. If the training curves are deterministic, this gives a clean
A/B comparison. If v4(CPU) > v3(CPU) on top-1 with either checkpoint criterion,
masking is confirmed as useful. If they are within noise of each other, the current
evidence is inconclusive and the question requires a larger dev set or multiple seeds.

This addresses the core ambiguity without adding any new hypotheses, architectures,
or data.
