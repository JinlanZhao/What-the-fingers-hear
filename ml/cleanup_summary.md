# ML Directory Cleanup Summary

**Date:** 2026-11-02

## Notebooks

| Notebook | Cells | Purpose |
|----------|-------|---------|
| `m2bert_finetune_comparison.ipynb` | 6 (was 37) | Active inference interface — `list_notes()`, `correct_musicxml()` |
| `correction_experiment_archive.ipynb` | 96 (new) | Read-only archive of all experiments (v1–v8, M2BERT, duration, joint) |

**Deleted:** `correction_experiments.ipynb` (56 cells) — fully archived into `correction_experiment_archive.ipynb` Part A.

**Main notebook minimal run order:** Cell 0 (imports) → Cell 1 (paths) → Cell 2 (model + API) → Cell 3 (demo)

## Deleted Run Directories (950 MB freed)

| Directory | Size | Reason |
|-----------|------|--------|
| `m2bert_finetune/` | 233M | Initial 4-epoch pitch run, superseded by extended |
| `m2bert_finetune_resume_20261028_*/` | 309M | Intermediate resume checkpoint |
| `m2bert_finetune_resume_20261030_*/` | 309M | Intermediate resume checkpoint |
| `correction_v1/` | 1M | Superseded by v4_mask_top1 |
| `correction_v2/` | 1M | Superseded by v4_mask_top1 |
| `correction_v3/` | 7M | Superseded by v4_mask_top1 |
| `correction_v3_top1/` | 7M | Superseded by v4_mask_top1 |
| `correction_v4_mask/` | 7M | Superseded by v4_mask_top1 |
| `sanity_check/` | 1M | One-off diagnostic |
| `v5_v4_control/` | 7M | v4 replication control, superseded |
| `v5_voice_conditioned/` | 7M | Voice experiment, superseded |
| `v6_voice_large/` | 37M | Larger model experiment, superseded |
| `v7_dynamic_mask/` | 7M | Negative result, superseded |
| `v8_struct_features/` | 7M | Structural features, superseded |

## Retained Checkpoints

| Directory | Size | Role |
|-----------|------|------|
| `m2bert_joint_20261030_213214/` | 310M | **Active** — joint pitch+duration checkpoint (epoch 2) |
| `m2bert_finetune_extended_20261030_183422/` | 310M | Best single-task pitch baseline (M2BERT) |
| `m2bert_dur_20261030_211057/` | 311M | Best single-task duration baseline |
| `correction_v4_mask_top1/` | 7M | Best from-scratch Transformer baseline |
| `context_baselines/` | 0.2M | Context-rule baseline results (no checkpoint) |
| `pretrained/m2bert/` | 715M | Official pretrained M2BERT weights |

## Other Deletions

- 6 old pitch-only demo directories under `ml/demo/` (superseded by `unified_joint/`)
- Old `demo_sample_ids.json` and `demo_summary.json` (superseded)
- `ml/__pycache__/` (36K)
- 7 `.DS_Store` files

## Bug Fix Applied

Duration label map values are in **quarterLength** units (not whole-note units).
Removed erroneous `× 4` conversion in the inference pipeline.

## Disk Usage

| | Before | After |
|--|--------|-------|
| `ml/` total | 4.6G | 3.6G |
| `ml/data/runs/` | 1.8G | 939M |

## Verification

From clean Python process, ran all 4 code cells of the slimmed notebook:
- **Pitch:** input C4 → predicted E4 (98.82%), matches ground truth ✓
- **Duration:** input 3 QL → predicted 1/2 QL (99.86%), matches ground truth ✓
- XML verification: both pass ✓
- MIDI export: both produce valid files ✓

Results identical to pre-cleanup outputs.
