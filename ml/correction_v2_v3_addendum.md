# Addendum to correction_v2_v3_experiment_log.md

**Date**: 2026-10-27
**Scope**: Five corrections to factual errors and overstated claims in the v2/v3 log.
Original log is unchanged; this file documents what should be corrected if the log is revised.

---

## Correction 1 — Ratio inversion (§1 Diagnosis)

**Original text:**
> With 3K examples for 131K parameters, that is roughly 22 examples per parameter —
> insufficient for generalization.

**Error**: The ratio is inverted. 3,000 / 131,508 = 0.023, meaning there are
**0.023 examples per parameter** (or equivalently, **~43.8 parameters per example**).
The number 22 is closer to examples/param in the other direction: 131,508 / 3,000 ≈ 43.8,
not 22.

**Correction**: Replace with "131K parameters for 3,000 examples — roughly 44 parameters
per example — insufficient for generalization."

---

## Correction 2 — "Confirmed" overstates the evidence (§8 Interpretation)

**Original text:**
> ### Hypothesis 1: Confirmed
> ...
> ### Hypothesis 2: Confirmed

**Error**: Each hypothesis was tested in a single experiment with one variable changed.
"Confirmed" implies the hypothesis is established as true and that alternative explanations
have been ruled out. That is not the case here.

For example: the v2 improvement (6.01% → 8.82%) could be explained by better alignment
between the 10K training distribution and the dev set, rather than reduced overfitting
per se. The v3 improvement could reflect better memorisation of 10K examples rather than
improved generalisation capacity.

**Correction**: Replace "Confirmed" with "Results are consistent with the hypothesis."
The stronger claim requires additional controls (e.g., comparing 10K train with the same
architecture but a different random seed, or evaluating on a held-out test set).

---

## Correction 3 — Checkpoint criterion not stated explicitly (§3, §8)

**Original text** (§3 training loop description, §8):
> Save best checkpoint (implicitly: by dev loss)

**Error**: The log does not explicitly state that checkpoints are saved by dev *loss*, not
dev *top-1*. For v3, epoch 5 happens to be both the lowest dev loss (3.2080) and the
highest dev top-1 (11.02%), so the two criteria coincide. But they are independent
criteria; a reader could incorrectly assume the checkpoint was saved by top-1.

**Correction**: Add "best checkpoint saved by dev loss (not top-1)" wherever checkpoint
selection is described. Note that for v2 and v3, the best-loss epoch and best-top-1 epoch
happen to coincide, but this is coincidental.

---

## Correction 4 — Truncation rate is from train data, not dev (§9 Window Truncation)

**Original text:**
> 51.6% of examples exceed 257 tokens and are hard-truncated to MAX_LEN=257.

**Error**: The 51.6% figure is not sourced in the log. The actual confirmed figure for the
dev set (correction_dev_v1.jsonl, 499 examples) is **232/499 = 46.5%**, as verified by the
`context_baseline.py` evaluation (each call to `window_tokens` reveals whether truncation
occurred). The 51.6% figure likely came from a rough estimate on the train data in the v1
plan document and was never verified against dev.

**Correction**: Replace "51.6%" with "46.5% of dev examples (232/499)" and note that the
train truncation rate may differ and has not been independently verified.

---

## Correction 5 — "Known limitations" are untested hypotheses (§9)

**Original text** (§9 Known Limitations):
> **Window Truncation**: The informative context ... may be cut off ... This is a *likely
> ceiling* on dev performance regardless of data quantity or model size.
>
> **Error-Position Representation**: Attention may collapse onto this anomalous token
> rather than attending to its neighbors ...

**Error**: Both limitations are listed as established facts or "likely" causes. Neither
has been empirically tested. No experiment has compared truncated vs. non-truncated
examples within the dev set, and no ablation has measured the effect of masking the error
position on dev top-1.

**Correction**: Reframe each limitation as an untested hypothesis:
- "Hypothesis (untested): window truncation is a performance ceiling. Test: compare
  accuracy on dev examples with window length < 257 vs. = 257."
- "Hypothesis (untested): attention collapse on the error token limits performance. Test:
  replace the replacement token with a [MASK] token and re-evaluate."

These remain plausible explanations. They are not yet supported by data.
