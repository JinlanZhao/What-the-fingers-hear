# OLiMPiC Correction Model — Experiment Log: v2 & v3

**Date**: 2026-10-27
**Author**: Jinlan Zhao
**Scope**: Diagnosis of correction_v1 failure + two controlled experiments to test data quantity and model capacity as explanations.

---

## 1. Background: Why v1 Failed

### v1 Baseline Results (for reference)

| Metric | Model (v1) | MFC Baseline |
|--------|-----------|--------------|
| Dev top-1 | 30/499 = **6.01%** | 26/499 = 5.21% |
| Dev top-5 | 154/499 = **30.86%** | 155/499 = 31.06% |
| Best epoch | **1** | — |

v1 barely beat the most-frequent-class baseline. The decisive symptom was **best epoch = 1**: the model peaked on dev before learning anything meaningful, then overfit immediately. By epoch 6, train top-1 had climbed to ~23.7% while dev stayed ~6%.

### Diagnosis

The architecture (d_model=64, 2 Transformer layers, ff=256 → 131K parameters) has enough capacity to memorize 3,000 training examples. With 3K examples for 131K parameters, that is roughly 22 examples per parameter — insufficient for generalization.

### Why the Task Is Learnable at All

85.2% of training examples have the correct target octave already present among neighboring pitches. This means local pitch context (the sequence of nearby notes) statistically constrains the correct answer. A model that reads context well should outperform a frequency-only baseline.

---

## 2. Experimental Design

Two experiments, each testing one variable with the other held constant.

### Run 1 — Data Quantity (v2)

- **Hypothesis**: Overfitting is data-limited. 10K examples reduces the train/dev gap and improves dev top-1 above 30/499.
- **Architecture**: unchanged — d_model=64, nhead=4, num_layers=2, dim_ff=256, dropout=0.1 (131K params)
- **Data**: `correction_train_10k.jsonl` — 9,998 examples, seed=44, train split only
- **Output**: `ml/data/runs/correction_v2/`

### Run 2 — Model Capacity (v3)

- **Hypothesis**: If v2 helps, a larger model extracts more signal from the same 10K data.
- **Architecture**: d_model=128, nhead=4, num_layers=3, dim_ff=512 (658K params — ~5× larger)
- **Data**: same `correction_train_10k.jsonl`
- **Output**: `ml/data/runs/correction_v3/`

Both runs use the **fixed** 499-example dev set (`correction_dev_v1.jsonl`) with no changes. The original v1 artifacts, dev/test sets, and checkpoints are untouched.

---

## 3. What Was Changed in the Codebase

### File: `ml/tools/run_experiment_v1.py`

Three minimal edits — no logic changes, no refactoring of unrelated code.

#### 3a. New CLI arguments (3 lines added after `--time-limit`, before `--overwrite`)

```python
parser.add_argument("--d-model",    type=int, default=D_MODEL)
parser.add_argument("--num-layers", type=int, default=N_LAYERS)
parser.add_argument("--dim-ff",     type=int, default=DIM_FF)
```

Defaults equal the original constants (`D_MODEL=64`, `N_LAYERS=2`, `DIM_FF=256`), so all existing usage of the script is unchanged.

`nhead` is intentionally kept hardcoded at 4. Both d_model=64 and d_model=128 are divisible by 4, and mixing nhead independently would risk incompatible configurations without adding experimental value.

#### 3b. Config dict — constants replaced with CLI args

```python
# before
"d_model":         D_MODEL,
"num_layers":      N_LAYERS,
"dim_feedforward": DIM_FF,

# after
"d_model":         args.d_model,
"num_layers":      args.num_layers,
"dim_feedforward": args.dim_ff,
```

#### 3c. Print statement updated to match

```python
# before
print(f"\nModel: d_model={D_MODEL}, nhead={N_HEADS}, layers={N_LAYERS}, ff={DIM_FF}, ...")

# after
print(f"\nModel: d_model={args.d_model}, nhead={N_HEADS}, layers={args.num_layers}, ff={args.dim_ff}, ...")
```

### Files Created

| Path | Description |
|------|-------------|
| `ml/data/processed/correction_train_10k.jsonl` | 9,998 training examples (seed=44) |
| `ml/data/runs/correction_v2/` | All v2 artifacts |
| `ml/data/runs/correction_v3/` | All v3 artifacts |

Each run directory contains: `vocab.json`, `pitch_classes.json`, `model_config.json`, `best_checkpoint.pt`, `metrics.csv`, `metrics.json`, `dev_predictions.json`.

---

## 4. Data Generation

### Command

```bash
python3 ml/tools/build_correction_dataset.py \
    --dataset-root ml/dataset/olimpic-1.0-synthetic \
    --output ml/data/processed/correction_train_10k.jsonl \
    --split train --limit 10000 --seed 44
```

### Output

```
Generated: 9998, Skipped: 2
Score-level overlap check: CLEAN (1092 unique scores)
Verification: PASSED (all 9998 examples)
```

2 examples skipped = scores with no pitch tokens (not usable as correction examples). The builder verified all 9,998 saved examples against source LMX files.

### Dataset Stats (Train, v2/v3)

| Property | Value |
|----------|-------|
| Examples | 9,998 |
| Unique scores | 1,092 |
| UNK rate | 0.0000% |
| Window length (min/max/mean) | 46 / 257 / 229.7 |
| Target classes covered | 48 / 52 |
| Top-5 targets | F4=690, D4=681, E4=680, C4=615, B3=583 |

---

## 5. Training Commands

### Run 1 (v2)

```bash
python3 ml/tools/run_experiment_v1.py \
    --train-examples ml/data/processed/correction_train_10k.jsonl \
    --dev-examples   ml/data/processed/correction_dev_v1.jsonl \
    --dataset-root   ml/dataset/olimpic-1.0-synthetic \
    --output-dir     ml/data/runs/correction_v2 \
    --seed 42
```

All other flags at defaults: batch=32, lr=1e-3, wd=0.01, max-epochs=30, patience=5.

### Run 2 (v3)

```bash
python3 ml/tools/run_experiment_v1.py \
    --train-examples ml/data/processed/correction_train_10k.jsonl \
    --dev-examples   ml/data/processed/correction_dev_v1.jsonl \
    --dataset-root   ml/dataset/olimpic-1.0-synthetic \
    --output-dir     ml/data/runs/correction_v3 \
    --seed 42 \
    --d-model 128 --num-layers 3 --dim-ff 512
```

---

## 6. Training Curves

### v2 (d_model=64, 2 layers, 10K data)

| Epoch | Train loss | Train top-1 | Dev loss | Dev top-1 |
|-------|-----------|------------|---------|----------|
| 0 | 4.1098 | 2.14% | 4.0702 | 1.60% |
| 1 | 3.3696 | 6.37% | 3.3144 | 4.21% |
| 2 | 3.3141 | 7.26% | 3.2873 | 5.81% |
| **3** ← best | **3.2097** | **9.05%** | **3.2129** | **8.82%** |
| 4 | 3.0931 | 11.43% | 3.2473 | 7.41% |
| 5 | 2.9720 | 14.17% | 3.2607 | 7.82% |
| 6 | 2.8431 | 17.57% | 3.3481 | 10.62% |
| 7 | 2.7203 | 20.87% | 3.4130 | 7.62% |
| 8 | 2.5927 | 24.51% | 3.4864 | 10.42% |

Early stop at epoch 8 (patience=5 from epoch 3). Total wall time: 24s.

### v3 (d_model=128, 3 layers, 10K data)

| Epoch | Train loss | Train top-1 | Dev loss | Dev top-1 |
|-------|-----------|------------|---------|----------|
| 0 | 4.1243 | 1.78% | 4.1239 | 1.40% |
| 1 | 3.3648 | 6.81% | 3.3280 | 4.81% |
| 2 | 3.3073 | 6.70% | 3.2567 | 6.21% |
| 3 | 3.2157 | 7.93% | 3.2084 | 8.82% |
| 4 | 3.1567 | 9.21% | 3.2421 | 6.81% |
| **5** ← best | **3.0785** | **11.50%** | **3.2080** | **11.02%** |
| 6 | 2.9748 | 13.62% | 3.2281 | 8.42% |
| 7 | 2.8516 | 16.33% | 3.3115 | 8.22% |
| 8 | 2.6929 | 20.90% | 3.4154 | 8.22% |
| 9 | 2.5173 | 25.24% | 3.4658 | 9.82% |
| 10 | 2.3140 | 30.92% | 3.6518 | 8.82% |

Early stop at epoch 10 (patience=5 from epoch 5). Total wall time: 50s.

---

## 7. Results Summary

| Run | Train | Architecture | Params | Dev top-1 | Dev top-5 | Best epoch |
|-----|-------|-------------|--------|-----------|-----------|------------|
| MFC baseline | — | — | — | 26/499 = 5.21% | 155/499 = 31.06% | — |
| v1 | 3K | 64/2/256 | 131K | 30/499 = 6.01% | 154/499 = 30.86% | 1 |
| **v2** | 10K | 64/2/256 | 131K | 44/499 = **8.82%** | 182/499 = 36.47% | **3** |
| **v3** | 10K | 128/3/512 | 658K | 55/499 = **11.02%** | 183/499 = 36.67% | **5** |

---

## 8. Interpretation

### Hypothesis 1: Confirmed

More data (3K → 10K, same architecture) improved dev top-1 from 6.01% to 8.82% (+2.81 pp), and best epoch moved from 1 to 3. Overfitting is less acute but not eliminated: by epoch 8, train top-1 is 24.5% while dev peaks at 8.82%.

### Hypothesis 2: Confirmed

Larger capacity (v3, 658K params, same 10K data) improved dev top-1 further to 11.02% and best epoch moved to 5. Both runs substantially beat the MFC baseline (5.21%). The larger model did not overfit faster — it extracted more signal before diverging.

### Overfitting Is Not Gone

In both runs, train top-1 continues climbing well past the best dev epoch. The train/dev gap at best epoch is:

- v2: train=9.05%, dev=8.82% → gap ≈ 0.2 pp (negligible at best epoch)
- v3: train=11.50%, dev=11.02% → gap ≈ 0.5 pp (also small at best epoch)

The model is learning rather than immediately memorizing, but dev performance stops improving around epoch 3–5 while training continues to fit. This points to a data ceiling at 10K for these architectures.

---

## 9. Known Limitations (Unchanged from v1)

### Window Truncation

51.6% of examples exceed 257 tokens and are hard-truncated to `MAX_LEN=257`. The informative context (neighboring pitches that determine the correct octave) may be cut off before reaching the model. This is a likely ceiling on dev performance regardless of data quantity or model size.

### Error-Position Representation

The model extracts the hidden state at the error position. That position contains the (obviously wrong) replacement token. Attention may collapse onto this anomalous token rather than attending to its neighbors to infer the correct pitch. A positional mask or context-only encoding could mitigate this.

### Task Scope

All results are for **synthetic pitch-replacement errors only** on OLiMPiC-1.0-synthetic. This is not final test performance and cannot be compared to real OMR systems without further evaluation.

---

## 10. Next Steps (If Further Experiments Are Warranted)

These are not planned — a new explicit plan is required before any of these are attempted.

1. **Fix window truncation**: Increase `MAX_LEN` or use a sliding-window approach to include more context. The 51.6% truncation rate is the most mechanically obvious bottleneck.
2. **More data**: 10K → 30K or all available train examples. v2→v3 showed consistent returns; the ceiling has not been found.
3. **Context-only encoding**: Mask the error position in the input (replace replacement token with a `[MASK]` token) so the model is forced to predict from context rather than from the anomalous token.
4. **Stronger regularization**: Higher dropout, label smoothing, or data augmentation to further reduce the post-best-epoch divergence.

---

## 11. File Index

```
ml/
├── tools/
│   └── run_experiment_v1.py          ← modified: +3 CLI args (--d-model, --num-layers, --dim-ff)
├── data/
│   ├── processed/
│   │   ├── correction_train_v1.jsonl  (original 3K, untouched)
│   │   ├── correction_dev_v1.jsonl    (499 examples, untouched)
│   │   └── correction_train_10k.jsonl (new: 9,998 examples, seed=44)
│   └── runs/
│       ├── correction_v1/             (original run, untouched)
│       ├── correction_v2/             (new: Run 1 artifacts)
│       │   ├── vocab.json
│       │   ├── pitch_classes.json
│       │   ├── model_config.json
│       │   ├── best_checkpoint.pt     (epoch 3)
│       │   ├── metrics.csv
│       │   ├── metrics.json
│       │   └── dev_predictions.json
│       └── correction_v3/             (new: Run 2 artifacts)
│           ├── vocab.json
│           ├── pitch_classes.json
│           ├── model_config.json
│           ├── best_checkpoint.pt     (epoch 5)
│           ├── metrics.csv
│           ├── metrics.json
│           └── dev_predictions.json
└── correction_v2_v3_experiment_log.md ← this file
```
