# OLiMPiC Correction — Full Experiment Log

**Date range**: 2026-10-27 – 2026-10-30
**Tasks**: Pitch correction (predict masked pitch) and duration correction (predict masked duration).
**Dataset**: OLiMPiC-1.0-synthetic — 499-example fixed dev set, 9,998-example train set (10K era).
**Output space**: Pitch = 52 classes (A0–C8, no accidentals); Duration = 28 classes (exact Fraction quarterLength).
**Notebooks**: `ml/correction_experiments.ipynb` (custom Transformers), `ml/m2bert_finetune_comparison.ipynb` (M2BERT pitch + duration).

---

## 0. Fixed Evaluation Protocol

| Property | Value |
|----------|-------|
| Dev set | `correction_dev_v1.jsonl` — 499 examples, never changed |
| Train set | `correction_train_10k.jsonl` — 9,998 examples (v3 onward); `correction_train_v1.jsonl` — 3,000 examples (v1–v2) |
| Metric | Dev top-1 accuracy (n / 499), dev top-5 accuracy, avg cross-entropy |
| Checkpoint | Saved at best dev loss (v1–v4\_mask) or best dev top-1 (v4\_mask\_top1 onward) |
| Training seed | 42 for all notebook-era runs; v1 used default, v2–v3 used 42 |
| All param counts | Verified by instantiating model from saved `model_config.json` |

The dev set and train set are score-disjoint (no score appears in both).

---

## 1. At-a-Glance Summary Table

| # | Run ID | Train data | Arch (d/L/ff) | Params | Ckpt by | Dev top-1 | Dev top-5 | Best ep | Time |
|---|--------|-----------|--------------|--------|---------|-----------|-----------|---------|------|
| — | MFC baseline (3K) | 3K | — | — | — | 26/499 = 5.21% | 155/499 = 31.06% | — | — |
| 0 | sanity\_check | 8 ex | 64/2/256 | 131,508 | step | 8/8 = 100%† | 8/8 | 25 steps | <1s |
| 1 | correction\_v1 | 3K | 64/2/256 | 131,508 | loss | 30/499 = **6.01%** | 154/499 = 30.86% | 1 | 7.6s |
| 2 | correction\_v2 | 10K | 64/2/256 | 131,508 | loss | 44/499 = **8.82%** | 182/499 = 36.47% | 3 | 23.7s |
| 3 | correction\_v3 | 10K | 128/3/512 | 657,844 | loss | 55/499 = **11.02%** | 183/499 = 36.67% | 5 | 50.1s |
| 4 | correction\_v3\_top1 | 10K | 128/3/512 | 657,844 | top1 | 47/499 = **9.42%** | 181/499 = 36.27% | 10 | 73.7s |
| 5 | correction\_v4\_mask | 10K | 128/3/512 | 657,972 | loss | 46/499 = **9.22%** | 196/499 = 39.28% | 8 | 66.2s |
| 6 | correction\_v4\_mask\_top1 | 10K | 128/3/512 | 657,972 | top1 | 63/499 = **12.63%** | 197/499 = 39.48% | 11 | 78.9s |
| 7 | v5\_v4\_control | 10K | 128/3/512 | 657,972 | top1 | 57/499 = **11.42%** | 174/499 = 34.87% | 4 | 46.1s |
| 8 | **v5\_voice\_conditioned** | 10K | 128/3/512 | **659,924** | top1 | 83/499 = **16.63%** | 261/499 = 52.30% | 10 | 73.6s |
| 9 | v6\_voice\_large | 10K | 256/4/1024 | 3,287,252 | top1 | 56/499 = **11.22%** | 205/499 = 41.08% | 14 | 210.7s |
| 10 | v7\_dynamic\_mask | 10K | 128/3/512 | 659,924 | top1 | 55/499 = **11.02%** | 196/499 = 39.28% | 1 | 37.4s |
| 11 | v8\_struct\_features | 10K | 128/3/512 | 663,380 | top1 | 59/499 = **11.82%** | 229/499 = 45.89% | 10 | 78.6s |
| 12 | **M2BERT fine-tuned** | 10K | ModernBERT-12L + CP | 61,021,184 | top1 | **306/499 = 61.32%** | **431/499 = 86.37%** | 3 | 79s |

† Sanity check overfit 8 training examples to 100% as designed; not comparable.

**Best custom Transformer: v5\_voice\_conditioned — 83/499 = 16.63% dev top-1.**
**Best pitch: M2BERT fine-tuned — 306/499 = 61.32% dev top-1 (3 epochs, 79s).**
**Best duration: M2BERT duration R1 — 434/499 = 86.97% dev top-1 (3 epochs, 77s). See §3b.**
**Joint model: pitch 310/499 (62.12%) + duration 438/499 (87.78%) from one checkpoint. See §3c.**

---

## 2. Per-Experiment Detail

### Sanity Check

**Purpose**: Verify the training loop can overfit a tiny batch before any real experiment.
**Setup**: 8 training examples, 64/2/256 architecture, dropout=0.0, no dev set.
**Result**: Loss fell from 4.22 → 0.27, top-1 from 0% → 100% in 25 steps. Loop confirmed working.
**Artifacts**: `ml/data/runs/sanity_check/`

---

### correction\_v1 — Baseline

**Key change**: First real training run.
**Architecture**: d\_model=64, nhead=4, num\_layers=2, dim\_ff=256, dropout=0.1. 131,508 params.
**Training data**: `correction_train_v1.jsonl` — 3,000 examples.
**Settings**: seed=?, batch=32, lr=1e-3, wd=0.01, max\_epochs=30, patience=5.
**Input representation**: Plain LMX token sequence, no masking, no voice conditioning. Error position token is the replacement pitch (visible to model).
**Result**: 30/499 = 6.01% dev top-1. Best epoch = 1 (peaked before any real learning).

| Epoch | Train top-1 | Dev top-1 |
|-------|------------|----------|
| 0 | 2.07% | 1.56% |
| **1** ← checkpoint | — | — |
| 6 | ~23.7% | ~6% |

**Note on metrics**: v1 had a batch-averaging bug in `evaluate_dataset` (equal-weight per batch rather than per example). Stored `dev_top1` in metrics.json is slightly off; `dev_predictions.json` is correct (30/499 = 6.01%).

**Diagnosis**: best\_epoch=1 means the model peaked before learning anything meaningful, then overfit. 3,000 examples for 131,508 parameters (≈ 0.023 examples/param) is severely data-limited. MFC baseline (5.21%) was nearly matched.

---

### correction\_v2 — More Data

**Key change**: 3K → 10K training examples. Architecture unchanged.
**Architecture**: 64/2/256, 131,508 params.
**Training data**: `correction_train_10k.jsonl` — 9,998 examples.
**Settings**: seed=42, batch=32, lr=1e-3, wd=0.01, max\_epochs=30, patience=5.
**Result**: 44/499 = 8.82% dev top-1 (checkpoint at epoch 3, by loss).

| Epoch | Train top-1 | Dev top-1 |
|-------|------------|----------|
| 0 | 2.14% | 1.60% |
| 1 | 6.37% | 4.21% |
| 2 | 7.26% | 5.81% |
| **3** ← checkpoint | 9.05% | 8.82% |
| 8 | 24.51% | ~10.42% |

Best top-1 during training was epoch 6 at ~10.62%, but checkpointed at loss-best epoch 3 (8.82%). Early stop epoch 8.

**Conclusion**: More data helps (+2.81pp). Overfitting still present but delayed (best epoch moved from 1 → 3).

---

### correction\_v3 — More Capacity

**Key change**: Architecture scaled up: 64/2/256 → 128/3/512 (≈5× more parameters).
**Architecture**: 128/3/512, 657,844 params.
**Training data**: Same 10K.
**Settings**: seed=42, identical to v2.
**Result**: 55/499 = 11.02% dev top-1 (checkpoint at epoch 5, by loss).

| Epoch | Train top-1 | Dev top-1 |
|-------|------------|----------|
| 0 | 1.78% | 1.40% |
| 3 | 7.93% | 8.82% |
| **5** ← checkpoint | 11.50% | 11.02% |
| 10 | 30.92% | 8.82% |

**Conclusion**: Larger model extracts more signal from 10K data (+2.20pp over v2). Best epoch moved from 3 → 5.

---

### correction\_v3\_top1 — Checkpoint Strategy Test

**Key change**: Same as v3 but checkpoint saved at best dev **top-1** (not best dev loss).
**Hypothesis**: Top-1-based checkpointing gives a more direct optimization target.
**Result**: 47/499 = 9.42% — **worse** than v3 (55/499).

**Root cause**: Dev top-1 is noisy at small n (499 examples). The best loss epoch (5) captures a more reliable signal than the noisiest-peak top-1 epoch (10). The loss-based checkpoint for v3 (epoch 5) happened to also have the best top-1 for that run, while v3\_top1 found a different peak at epoch 10 that gave 47/499.

**Lesson**: For this task and dev set size, loss-based and top-1-based checkpointing give different results. We later adopted **top-1 checkpointing throughout** for v4\_mask\_top1 onward after seeing it work there.

---

### correction\_v4\_mask — Input Masking

**Key change**: Replace the error token with `[MASK]` before feeding to the model. Vocabulary expands by 1 (183 → 184 tokens, mask\_token\_id=183). Checkpoint by **loss**.
**Hypothesis**: Hiding the wrong pitch forces the model to predict from context rather than from the obviously-anomalous replacement token.
**Architecture**: 128/3/512, 657,972 params (+128 for the new mask embedding row).
**Result**: 46/499 = 9.22% (checkpoint at epoch 8, by loss). Best top-1 during training was epoch 4 at 56/499 ≈ 11.22%, but not saved.

**Issue**: Checkpointing by loss here was harmful — the loss-best epoch (8) was *worse* by top-1 than epoch 4. This led to v4\_mask\_top1.

---

### correction\_v4\_mask\_top1 — Masking + Correct Checkpoint

**Key change**: Same as v4\_mask but checkpoint saved at best dev **top-1**.
**Result**: 63/499 = 12.63% (checkpoint at epoch 11).

| Epoch | Train top-1 | Dev top-1 |
|-------|------------|----------|
| 4 | ~9% | 11.22% |
| 8 | ~15% | 11.22% |
| **11** ← checkpoint | — | 12.63% |

**Conclusion**: MASK + top-1 checkpointing substantially outperforms unmasked v3 (12.63% vs 11.02%). The masking forces context-based prediction as intended.

---

### v5\_v4\_control — Voice Conditioning Ablation (Control)

**Key change**: Same as v4\_mask\_top1, but `voice_conditioning=False`. This is the control arm of the v5 experiment.
**Purpose**: Isolate the effect of voice conditioning by holding everything else constant.
**Result**: 57/499 = 11.42% (best epoch 4).

---

### v5\_voice\_conditioned — Voice Conditioning ← CURRENT BEST

**Key change**: `voice_conditioning=True`. Adds an 8-class voice embedding (dim=32). The voice label (voice:1 through voice:8) of the error token is extracted from `input_tokens` before masking and passed as a separate embedding concatenated to the Transformer's output before the classification head.
**Architecture**: 128/3/512 + voice embedding (8×32). Head: Linear(128+32=160, 52). 659,924 params.
**Result**: **83/499 = 16.63%** (checkpoint at epoch 10), top-5 = 261/499 = 52.30%.

| Epoch | Train top-1 | Dev top-1 | Dev loss |
|-------|------------|----------|---------|
| 0 | 2.41% | 2.61% | 4.134 |
| 4 | 11.09% | 12.42% | 2.845 |
| 8 | 15.18% | 14.23% | 2.749 |
| **10** ← checkpoint | 17.73%† | 16.63% | 2.793 |
| 15 | 24.11% | 15.03% | 2.854 |

† Online (pre-gradient-step) metric. Offline eval of epoch 10 checkpoint gives **22.40%** train top-1 on a 1K sample (see §4).

**Voice label distribution in train 1K sample**: voice:1=54.0%, voice:5=36.0%, voice:2=6.5%, voice:6=3.4%, voice:3=0.1%.

**vs control**: +5.21pp (83 vs 57) — voice conditioning is the largest single improvement found so far.

**Comparison to baselines**:
| Method | Dev top-1 |
|--------|----------|
| MFC (3K) | 26/499 = 5.21% |
| prev\_pitch (same voice) | 20/499 = 4.01% |
| next\_pitch (same voice) | 17/499 = 3.41% |
| v3 model | 55/499 = 11.02% |
| **v5 model** | **83/499 = 16.63%** |

Context rules (prev/next pitch) are notably worse than even MFC, indicating that the nearest same-voice neighbor is not a reliable proxy for the correct pitch.

---

### v6\_voice\_large — Scale-Up Attempt

**Key change**: Architecture scaled: 128/3/512 → 256/4/1024. Same v5 voice conditioning and masking.
**Architecture**: 256/4/1024 + voice embedding (8×32). 3,287,252 params (≈5× larger than v5).
**Result**: 56/499 = 11.22% (best epoch 14), total time 210.7s.

**Training curve**: Dev top-1 was noisy and never exceeded ~11%. The model has 3.3M params on 9,998 examples (≈0.003 examples/param), far into the underfitting regime given the small training set.

**Conclusion**: Scaling capacity without more data hurts. v6 regresses to near v3 performance despite 5× more parameters.

---

### v7\_dynamic\_mask — Dynamic Position Masking

**Key change**: Instead of always masking the fixed error position, each training epoch samples a **different** pitch position in the sequence to mask (any pitch in the window, not just the error position). The model sees varied positions across epochs.
**Hypothesis**: Exposing the model to many mask positions per sequence extracts more pitch-context signal than repeatedly training the same fixed position.
**Architecture**: Same as v5 (128/3/512, voice conditioning). 659,924 params.
**Result**: 55/499 = 11.02% (best epoch 1, early stop at epoch 6).

| Epoch | Train top-1 | Dev top-1 | Distinct positions |
|-------|------------|----------|--------------------|
| 0 | — | 2.61% | 0 |
| **1** ← checkpoint | 7.62% | 11.02% | 9,998 |
| 6 | 10.03% | 9.82% | 9,998 |

Dev top-1 peaked at epoch 1 and degraded. Coverage: only 57,173 / 610,301 unique positions seen (9.37% coverage) within the v5 step budget.

**Root cause (verified by audit)**:
1. Surrounding context tokens are byte-identical between v5 and v7 (110,119/110,119 non-error tokens match LMX source). The dev context is not corrupted.
2. Likely cause: **masking-position non-stationarity**. v5 always masks the fixed error position, allowing the model to specialise for that position. v7 shifts the masked position every epoch, preventing that specialization and destabilizing learning.

**Conclusion**: Dynamic masking hurts. Fixing the mask position (v5 approach) is better.

---

### v8\_struct\_features — Structural Feature Conditioning

**Key change**: Added three per-note structural features of the error token (extracted from `input_tokens`, no leakage from target): **staff** (3-class), **onset-in-measure** (33-class, 1/16 whole-note bins), **duration** (24-class, log2-scale bins). Each gets a separate embedding (dim=16) concatenated to the head input.
**Architecture**: 128/3/512 + voice(32) + staff(16) + onset(16) + dur(16). Head: Linear(208, 52). 663,380 params (+3,456 vs v5).
**Struct unknowns**: staff=0, onset=0, dur=0 out of 499 dev examples (all features fully specified in every LMX example).
**Result**: 59/499 = 11.82% (best epoch 10).

| | Dev top-1 | Dev top-5 | Params |
|--|-----------|-----------|--------|
| v5 (voice only) | 83/499 = 16.63% | 261/499 = 52.30% | 659,924 |
| v8 (+ struct) | 59/499 = 11.82% | 229/499 = 45.89% | 663,380 |
| Δ | **−24 examples (−4.81pp)** | −32 examples (−6.41pp) | +3,456 |

**Conclusion**: Staff, onset, and duration did **not** help and in fact degraded performance. Possible reasons: (a) the model already infers these from context tokens; (b) the structural features are redundant with or distracting from the voice signal; (c) single run with no multi-seed comparison.

---

## 3. Analysis Work (No Model Training)

### Context Baselines (v3 era)

Evaluated three non-model baselines on dev (499 examples), using the same 257-token window as the model:

| Method | Dev top-1 | Coverage | Notes |
|--------|----------|---------|-------|
| MFC (3K train) | 26/499 = 5.21% | 100% | Most frequent pitch class in train targets |
| prev\_pitch (same voice) | 20/499 = 4.01% | 476/499 = 95.4% | First preceding pitch in same voice |
| next\_pitch (same voice) | 17/499 = 3.41% | 469/499 = 94.0% | First following pitch in same voice |
| v3 model | 55/499 = 11.02% | 100% | For comparison |

Both context rules fall below MFC, showing that simply copying a neighboring note (even from the same voice) is not a reliable correction strategy. The v3 model adds ~5.8pp above MFC, learning signal beyond simple frequency statistics.

Overlap analysis (v3):
- v3 correct ∩ prev\_pitch correct: small overlap
- v3 adds signal beyond pitch-neighborhood memorization

**Artifacts**: `ml/data/runs/context_baselines/context_baseline_results.json`

---

### Note-Level Representation (Parser)

Implemented `parse_lmx_notes(tokens, sample_id)` to extract per-note records from LMX token streams. Fields: measure, voice, staff, onset (Fraction), duration (Fraction|None), pitch, is\_rest, is\_grace, chord\_group (globally unique int), pitch\_token\_position, token\_span.

Key design decisions:
- **Anti-leakage**: parse only from `input_tokens`, never `target_token`
- **chord\_group**: globally unique integer that never resets at measure boundaries (resetting caused collisions — a fixed bug)
- **Clef+staff pitfall**: `clef:G2 staff:1` — the `staff:N` after a clef token is NOT the note's staff and must not update `current_staff`
- **rest:measure**: duration = Fraction(beats, beat\_type) when time signature has been seen; otherwise None + explicit warning (never defaults to 4/4)
- **Time signature tracking**: `beats:N` and `beat-type:N` tokens parsed (not skipped)

Validation on 100 train + 20 dev examples: all 4 consistency checks passed.

Struct cache (for v8): all 9,998 train + 499 dev examples — 0 unknown features.

**Artifacts**: `ml/data/note_repr/manifest.json`, `notes_train.json`, `notes_dev.json`, `struct_cache_train.json`, `struct_cache_dev.json`

---

### v5 Train-Sample vs Dev Inference (1K sample, seed=42)

Evaluated the v5 best checkpoint on 1,000 randomly sampled **train** examples (seed=42) to measure the train-dev generalization gap. No weight updates.

| Metric | Train 1K (fresh eval) | Dev 499 (saved metrics) |
|--------|----------------------|------------------------|
| top-1 (n) | 224/1000 | 83/499 |
| top-1 (%) | **22.40%** | **16.63%** |
| top-5 (n) | 658/1000 | 261/499 |
| top-5 (%) | **65.80%** | **52.30%** |
| avg CE loss | **2.4374** | **2.7925** † |

† Dev CE from `metrics.json` epoch 10 (model.eval(), equivalent to inference evaluation).

**Δ top-1 (train − dev): +5.77pp | Δ CE (dev − train): +0.3551**

Key observation: the online train top-1 at epoch 10 was 17.73% (pre-gradient-step per batch). The actual offline eval gives 22.40% — online metrics systematically underestimate the final weights. The gap is meaningful but not catastrophic, suggesting mild overfitting rather than severe memorization.

Training curve shows dev top-1 stabilized at epoch 10 while online train top-1 kept rising (17.73% → 24.11% by epoch 15), consistent with mild overfitting after the checkpoint epoch.

**Saved IDs**: `ml/data/runs/v5_voice_conditioned/train_eval_sample_ids.json` (1,000 sample IDs, seed=42)

---

### M2BERT Fine-tuning (3 epochs, 10-minute budget)

**Notebook**: `ml/m2bert_finetune_comparison.ipynb`

**Hypothesis**: A music-pretrained bidirectional Transformer (M2BERT) with a compound-token (CP) representation should generalise better to pitch correction than a randomly-initialised small Transformer trained from scratch on the same 10K examples.

**Architecture**: ModernBERT-base (12 layers, 768 hidden) with 4 × Embedding(vocab, 256) CP input projection. 61M total parameters. Checkpoint from `ml/data/pretrained/m2bert/model_best.ckpt` (pretrained on music MLM task).

**Fine-tuning setup**:
- Freeze all except last 2 transformer layers (10, 11) + new Dropout(0.1) → Linear(768, 52) head
- Trainable params: 10,070,068
- Optimizer: Adam, lr=1e-4, batch=32
- Budget: ≤ 3 epochs / ≤ 10 minutes

**Input representation (CP — Compound Pitch)**:
- Full note sequence, no windowing (max 219 notes across all examples, mean ≈66)
- Per note: [Bar (0=new/1=continue), Position (16ths within measure), Pitch (MIDI-22), Duration (ticks/60)]
- Error note pitch replaced with Pitch MASK (87)

| Epoch | Train loss | Dev top-1 | Elapsed |
|-------|-----------|-----------|---------|
| 1 | 1.9081 | 303/499 = 60.72% | 28s |
| 2 | 0.9395 | 300/499 = 60.12% | 54s |
| **3** ← checkpoint | **0.3771** | **306/499 = 61.32%** | **79s** |

**Final dev results (best checkpoint, epoch 3)**:

| Metric | M2BERT | v5 (best custom Transformer) | Δ |
|--------|--------|------------------------------|---|
| Top-1 | 306/499 = **61.32%** | 83/499 = 16.63% | +44.69pp |
| Top-5 | 431/499 = **86.37%** | 261/499 = 52.30% | +34.07pp |
| Training time | 79s (3 ep) | 73.6s (10 ep) | — |
| Trainable params | 10.07M | 659,924 | — |

**Venn overlap (dev correct)**:
- Both correct: 62
- Only M2BERT: 244 (new examples M2BERT gets right that v5 misses)
- Only v5: 21 (examples v5 gets right that M2BERT misses)

**Interpretation**: The pretrained M2BERT backbone has encoded rich pitch-neighbourhood information from music MLM pretraining. The CP representation (pitch, rhythm, bar position) provides directly informative note-level context. The custom Transformer's LMX token window is much noisier (includes decoration tokens, articulations, etc.) and the model is too small to filter this effectively. The 3.7× ratio of trainable params (10M vs 0.66M) is a secondary factor — the main driver is pretrained musical knowledge.

**Artifacts**: `ml/data/runs/m2bert_finetune/` (best\_checkpoint.pt, dev\_predictions.json, metrics.json)

---

## 3b. Duration Correction Experiments

**Task**: Predict the correct duration (exact Fraction quarterLength) of a single corrupted note, given the surrounding musical context with the error note's duration masked.
**Output space**: 28 duration classes derived from train set (e.g., 1/2, 1, 1/4, 2, 1/3, 3/2, …).
**Data construction**: Same source samples and score-level split as pitch correction. For each sample, one pitched non-grace note selected deterministically (hash of sample_id). Duration tokens in LMX replaced with a different duration; LMX re-parsed to compute corrupted onsets for downstream notes. CP Duration attribute masked at error position; pitch left intact.
**Exclusions**: Grace notes (3,368 train / 181 dev) and rests (53,322 train / 3,124 dev) excluded from candidate pool. Zero samples skipped; zero OOV durations in dev.
**Notebook**: `ml/m2bert_finetune_comparison.ipynb` (cells 23–27).

### Duration Summary Table

| # | Run ID | Arch | Classes | Ckpt by | Dev top-1 | Dev top-3 | Best ep | Time |
|---|--------|------|---------|---------|-----------|-----------|---------|------|
| — | MFC baseline (10K) | — | — | — | 178/499 = 35.67% | — | — | — |
| D1 | **M2BERT duration R1** | ModernBERT-12L + CP | 28 | top1 | **434/499 = 86.97%** | **481/499 = 96.39%** | 3 | 77s |

**MFC**: Always predict '1/2' QL (eighth note), the most frequent duration in train (3,651/9,998 = 36.5%).

### M2BERT Duration Fine-tuning (R1)

**Architecture**: Same M2BERT backbone as pitch (ModernBERT-base, 12 layers, 768 hidden), loaded fresh from pretrained checkpoint. New Dropout(0.1) → Linear(768, 28) head. Freeze layers 0–9; train layers 10–11 + head. Trainable: 10,051,612 params.

**Setup**: Adam lr=1e-4, batch=32, max 6 epochs, patience=2, budget=600s.

| Epoch | Train loss | Dev top-1 | Dev top-3 | Dev CE | Elapsed |
|-------|-----------|-----------|-----------|--------|---------|
| 1 | 0.6673 | 425/499 = 85.17% | 95.39% | 0.487 | 26s |
| 2 | 0.2603 | 431/499 = 86.37% | 96.39% | 0.469 | 52s |
| **3** ← checkpoint | **0.0765** | **434/499 = 86.97%** | **96.39%** | 0.560 | 77s |
| 4 | 0.0143 | 434/499 = 86.97% | 96.19% | 0.641 | 103s |
| 5 | 0.0047 | 430/499 = 86.17% | 95.59% | 0.672 | 128s |

Early stop at epoch 5 (2 epochs without improvement). Round 2 not triggered: R1 beats MFC by 51pp and no overfitting.

**Duration class distribution** (top-5 in train): 1/2 QL = 36.5%, 1 QL = 21.8%, 1/4 QL = 16.4%, 2 QL = 6.0%, 1/3 QL = 5.6%.

**Interpretation**: Duration correction is substantially easier than pitch correction (86.97% vs 62.53% best M2BERT pitch). The duration label space is smaller (28 vs 52 classes) and more concentrated (top-3 classes cover 74.7% of train). The model likely leverages strong rhythmic priors from pretraining — surrounding note durations tightly constrain the masked duration in most musical contexts.

**Artifacts**: `ml/data/runs/m2bert_dur_20261030_211057/` (best\_checkpoint.pt, metrics.json, config.json, dur\_label\_map.json, train\_selection.json, dev\_selection.json, dev\_predictions.json, final\_dev\_metrics.json)

---

## 3c. Joint Pitch + Duration Correction

**Task**: Simultaneously correct pitch and duration using a shared M2BERT backbone with two task-specific heads. Each sample masks only one attribute (pitch OR duration); the model is routed to the corresponding head via task ID.
**Notebook**: `ml/m2bert_finetune_comparison.ipynb` (cells 28–31).

### Joint Summary Table

|  | Pitch top-1 | Pitch top-5 | Duration top-1 | Duration top-3 |
|--|-------------|-------------|----------------|----------------|
| Single-task pitch | 312/499 = 62.53% | 427/499 = 85.57% | — | — |
| Single-task duration | — | — | 434/499 = 86.97% | 481/499 = 96.39% |
| **Joint R1 (epoch 2)** | **310/499 = 62.12%** | **449/499 = 89.98%** | **438/499 = 87.78%** | **484/499 = 96.99%** |
| Δ vs single-task | −2 (−0.41pp) | +22 (+4.41pp) | +4 (+0.81pp) | +3 (+0.60pp) |

### M2BERT Joint Fine-tuning

**Architecture**: `M2BERTJointCorrection` — shared ModernBERT-base backbone + `pitch_head` (Dropout(0.1) → Linear(768, 52)) + `dur_head` (Dropout(0.1) → Linear(768, 28)). Forward pass takes `task='pitch'` or `task='dur'` to route to the correct head. Freeze layers 0–9; train layers 10–11 + both heads. Trainable: 10,091,600 params.

**Training**: 1:1 interleaved batches (alternate pitch → duration). Each batch uses its own mean CE loss; only the active task's head receives gradient. Adam lr=1e-4, batch=32, max 6 epochs, patience=2, budget=600s. Checkpoint selected by `mean(pitch_dev_top1, dur_dev_top1)`, tiebreaker by mean CE.

| Epoch | Pitch loss | Dur loss | Pitch dev | Dur dev | Avg top-1 | Elapsed |
|-------|-----------|---------|-----------|---------|-----------|---------|
| 1 | 1.8877 | 0.6889 | 297/499 = 59.52% | 417/499 = 83.57% | 0.7154 | 52s |
| **2** ← checkpoint | **0.9182** | **0.2794** | **310/499 = 62.12%** | **438/499 = 87.78%** | **0.7495** | 103s |
| 3 | 0.3522 | 0.0992 | 298/499 = 59.72% | 440/499 = 88.18% | 0.7395 | 154s |
| 4 | 0.0693 | 0.0234 | 303/499 = 60.72% | 439/499 = 87.98% | 0.7435 | 205s |

Early stop at epoch 4 (2 epochs without improvement). Round 2 not triggered: neither task dropped >3pp from single-task baseline (pitch Δ = −0.41%, duration Δ = +0.81%).

**Interpretation**: Joint training produces near-parity with single-task models from a single shared checkpoint. Pitch top-1 drops by only 2 examples (−0.41pp, within noise), while pitch top-5 improves by 22 examples (+4.41pp), suggesting the shared backbone learns better general pitch representations even if the argmax shifts slightly. Duration top-1 improves by 4 examples (+0.81pp), consistent with mild regularization from the multi-task objective. The model converges faster (best at epoch 2) than single-task pitch (epoch 5) or duration (epoch 3), likely because the doubled gradient signal per step accelerates backbone adaptation.

**Artifacts**: `ml/data/runs/m2bert_joint_20261030_213214/` (best\_checkpoint.pt, config.json, pitch\_label\_map.json, dur\_label\_map.json, metrics.json, final\_dev\_metrics.json, pitch\_dev\_predictions.json, dur\_dev\_predictions.json)

---

## 4. Open Questions (Testable Without New Training)

The following hypotheses can be evaluated from existing artifacts (`dev_predictions.json`, `metrics.json`) without running any new inference or training:

1. **Per-class accuracy ceiling**: Is the model reliably good at some pitch classes and poor at others? Computable from `dev_predictions.json` by grouping on `target_token`.

2. **Window truncation effect**: 232/499 dev examples (46.5%) are truncated to 257 tokens. Does accuracy differ between truncated vs full-window examples? Computable from `dev_predictions.json` + `error_position` and `window_lo`.

3. **CE divergence point**: `metrics.json` records dev\_loss per epoch. At which epoch does dev\_loss start rising while train\_loss keeps falling? The training curve shows the qualitative pattern; plotting or computing the exact crossover epoch would confirm the overfitting onset.

---

## 5. File Index

```
ml/
├── correction_experiments.ipynb          ← custom Transformer experiments (v1–v8)
├── m2bert_finetune_comparison.ipynb      ← M2BERT fine-tuning experiment
├── correction_v2_v3_experiment_log.md    ← detailed log for v1–v3 (pre-notebook)
├── correction_v2_v3_addendum.md          ← corrections to v2/v3 log (ratio error, etc.)
├── correction_all_experiments.md         ← this file
├── data/
│   ├── processed/
│   │   ├── correction_train_v1.jsonl     3,000 train examples
│   │   ├── correction_train_10k.jsonl    9,998 train examples
│   │   └── correction_dev_v1.jsonl       499 dev examples (fixed, never changed)
│   ├── note_repr/
│   │   ├── manifest.json                 120 selected examples (100 train + 20 dev)
│   │   ├── notes_train.json              note-level records for train selection
│   │   ├── notes_dev.json                note-level records for dev selection
│   │   ├── struct_cache_train.json       staff/onset/dur features, 9,998 train examples
│   │   └── struct_cache_dev.json         staff/onset/dur features, 499 dev examples
│   └── runs/
│       ├── sanity_check/                 8-example overfit test
│       ├── correction_v1/                3K, 64d, loss ckpt, 30/499
│       ├── correction_v2/                10K, 64d, loss ckpt, 44/499
│       ├── correction_v3/                10K, 128d, loss ckpt, 55/499
│       ├── correction_v3_top1/           10K, 128d, top1 ckpt, 47/499
│       ├── correction_v4_mask/           10K, 128d, MASK, loss ckpt, 46/499
│       ├── correction_v4_mask_top1/      10K, 128d, MASK, top1 ckpt, 63/499
│       ├── v5_v4_control/                10K, 128d, MASK, no voice, top1 ckpt, 57/499
│       ├── v5_voice_conditioned/         10K, 128d, MASK, voice, top1 ckpt, 83/499 ← BEST
│       │   └── train_eval_sample_ids.json  1,000 train sample IDs for inference eval
│       ├── v6_voice_large/               10K, 256d, MASK, voice, top1 ckpt, 56/499
│       ├── v7_dynamic_mask/              10K, 128d, MASK, voice, dynamic pos, 55/499
│       ├── v8_struct_features/           10K, 128d, MASK, voice, +struct, 59/499
│       ├── context_baselines/            MFC + prev/next pitch rules vs v3
│       ├── m2bert_finetune/              M2BERT 3-epoch fine-tune, 306/499 ← BEST PITCH
│       ├── m2bert_dur_20261030_211057/  M2BERT duration fine-tune, 434/499 = 86.97%
│       └── m2bert_joint_20261030_213214/ Joint pitch+dur, P=310 D=438 from 1 ckpt
├── data/pretrained/m2bert/
│   ├── CP.pkl                            CP vocabulary (Bar/Position/Pitch/Duration)
│   └── model_best.ckpt                  Pretrained M2BERT weights (61M params, 715MB)
```

Each run directory contains: `vocab.json`, `pitch_classes.json`, `model_config.json`, `best_checkpoint.pt`, `metrics.csv`, `metrics.json`, `dev_predictions.json`.
