import sys, json, re, os, time, pickle, hashlib, math
from pathlib import Path
from fractions import Fraction as _Frac
from collections import Counter
from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import ModernBertConfig, ModernBertModel

ML_DIR = Path("/Users/zhaojinlan/Desktop/Lann Projects/What-the-fingers-hear/ml")
PROCESSED = ML_DIR / "data" / "processed"
PRETRAINED = ML_DIR / "data" / "pretrained" / "m2bert"
DATASET_ROOT = ML_DIR / "dataset" / "olimpic-1.0-synthetic"

DEVICE = (torch.device("mps") if torch.backends.mps.is_available() else
          torch.device("cuda") if torch.cuda.is_available() else
          torch.device("cpu"))
print(f"DEVICE: {DEVICE}")

# ── CP vocab ──
with open(PRETRAINED / "CP.pkl", "rb") as f:
    _cp = pickle.load(f)
CP_TOK2ID = _cp[0]
BAR_PAD = CP_TOK2ID["Bar"]["Bar <PAD>"]
POS_PAD = CP_TOK2ID["Position"]["Position <PAD>"]
PITCH_PAD = CP_TOK2ID["Pitch"]["Pitch <PAD>"]
PITCH_MASK = CP_TOK2ID["Pitch"]["Pitch <MASK>"]
DUR_PAD = CP_TOK2ID["Duration"]["Duration <PAD>"]
CP_PAD = [BAR_PAD, POS_PAD, PITCH_PAD, DUR_PAD]

# ── Pitch classes ──
PITCH_RE = re.compile(r"^[A-G][0-9]$")

def _lmx_path(sid):
    parts = sid.split("/")
    return DATASET_ROOT / "samples" / parts[1] / (parts[2] + ".lmx")

pitches = set()
for sid in (DATASET_ROOT / "samples.train.txt").read_text().split():
    p = _lmx_path(sid)
    if p.exists():
        pitches.update(t for t in p.read_text().split() if PITCH_RE.match(t))
pitch_classes = {p: i for i, p in enumerate(sorted(pitches))}
id2pitch = {i: p for p, i in pitch_classes.items()}
N_CLASSES = len(pitch_classes)
print(f"Pitch classes: {N_CLASSES}")

_SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

def pitch_to_midi(p):
    return _SEMITONES[p[0]] + 12 * (int(p[1]) + 1)

# ── Load data ──
with open(PROCESSED / "correction_train_10k.jsonl") as f:
    train_raw = [json.loads(l) for l in f]
with open(PROCESSED / "correction_dev_v1.jsonl") as f:
    dev_raw = [json.loads(l) for l in f]
print(f"Train: {len(train_raw)}  Dev: {len(dev_raw)}")

# ── Note-level LMX parser ──
_DURATION_BASE = {
    "breve": _Frac(2), "whole": _Frac(1), "half": _Frac(1,2),
    "quarter": _Frac(1,4), "eighth": _Frac(1,8), "16th": _Frac(1,16),
    "32nd": _Frac(1,32), "64th": _Frac(1,64), "128th": _Frac(1,128),
    "256th": _Frac(1,256), "512th": _Frac(1,512), "1024th": _Frac(1,1024),
}
_DECORATION = frozenset({
    "beam:begin","beam:end","beam:forward-hook","beam:backward-hook",
    "tied:start","tied:stop","tuplet:start","tuplet:stop",
    "slur:start","slur:stop","trill-mark","staccato","accent",
    "strong-accent","tenuto","fermata","arpeggiate",
    "tremolo:1","tremolo:2","tremolo:3","tremolo:4",
    "tremolo:single","tremolo:start","tremolo:stop",
})
_ACCIDENTAL_SET = frozenset({
    "sharp","flat","natural","double-sharp",
    "flat-flat","natural-sharp","natural-flat",
})
_SKIP = frozenset({"time"})
_TIME_MOD_RE = re.compile(r"^(\d+)in(\d+)$")

def _parse_dur(tokens, pos):
    if pos >= len(tokens):
        return _Frac(0), pos
    t = tokens[pos]
    if t not in _DURATION_BASE:
        return _Frac(0), pos
    base = _DURATION_BASE[t]; pos += 1; dots = 0
    while pos < len(tokens) and tokens[pos] == ".":
        dots += 1; pos += 1
    dur = base * (2 - _Frac(1, 2**dots)) if dots else base
    if pos < len(tokens):
        m = _TIME_MOD_RE.match(tokens[pos])
        if m:
            actual, normal = int(m.group(1)), int(m.group(2))
            dur = dur * _Frac(normal, actual); pos += 1
    return dur, pos

def parse_lmx_notes(lmx_text):
    tokens = lmx_text if isinstance(lmx_text, list) else lmx_text.split()
    notes = []; i = 0; measure = -1; voice = 1; staff = 1
    onset = _Frac(0); ts_num = 4; ts_den = 4
    chord_onset = None; grace = False
    while i < len(tokens):
        t = tokens[i]
        if t == "measure":
            measure += 1; i += 1
            onset = _Frac(measure) * _Frac(ts_num, ts_den)
            chord_onset = None; grace = False; continue
        if t == "voice":
            i += 1
            if i < len(tokens):
                try: voice = int(tokens[i])
                except ValueError: pass
            i += 1; continue
        if t == "staff":
            i += 1
            if i < len(tokens):
                try: staff = int(tokens[i])
                except ValueError: pass
            i += 1; continue
        if t == "backup":
            i += 1; dur, i = _parse_dur(tokens, i); onset -= dur; continue
        if t == "forward":
            i += 1; dur, i = _parse_dur(tokens, i); onset += dur; continue
        if t in _SKIP:
            i += 1
            while i < len(tokens) and tokens[i] not in (
                "measure","voice","staff","backup","forward",
                "rest","rest:measure","grace","chord") and not PITCH_RE.match(tokens[i]):
                i += 1
            continue
        if t == "grace":
            grace = True; i += 1; continue
        if t == "chord":
            chord_onset = onset; i += 1; continue
        if t.startswith("rest"):
            is_full = (t == "rest:measure")
            dur = _Frac(0); i += 1
            if is_full:
                dur = _Frac(ts_num, ts_den)
            else:
                dur, i = _parse_dur(tokens, i)
            while i < len(tokens) and tokens[i] in _DECORATION:
                i += 1
            if not grace:
                onset += dur
            grace = False; chord_onset = None; continue
        if PITCH_RE.match(t):
            pitch_token = t; pitch_pos = i; i += 1
            while i < len(tokens) and tokens[i] in _ACCIDENTAL_SET:
                i += 1
            dur, i = _parse_dur(tokens, i)
            while i < len(tokens) and tokens[i] in _DECORATION:
                i += 1
            note_onset = chord_onset if chord_onset is not None else onset
            notes.append({
                "pitch": pitch_token, "onset": note_onset, "duration": dur,
                "voice": voice, "staff": staff, "measure": measure,
                "grace": grace, "pitch_token_position": pitch_pos,
            })
            if chord_onset is not None:
                chord_onset = None
            elif not grace:
                onset += dur
            grace = False; continue
        if t in _DECORATION or t in _ACCIDENTAL_SET:
            i += 1; continue
        i += 1
    return notes

# ── CP builder ──
def build_cp_examples(raw_list, pitch_classes, split_name):
    examples = []; skipped = 0
    for ex in raw_list:
        sid = ex["sample_id"]
        lmx = ex.get("lmx") or ex.get("input_tokens", "")
        epp = ex.get("error_pitch_position") or ex.get("error_position")
        truth = ex.get("true_pitch") or ex.get("target_token", "")
        if truth not in pitch_classes:
            skipped += 1; continue
        notes = parse_lmx_notes(lmx)
        error_idx = None
        for ni, n in enumerate(notes):
            if n["pitch_token_position"] == epp:
                error_idx = ni; break
        if error_idx is None:
            skipped += 1; continue
        cp_seq = []
        prev_measure = -1
        for ni, n in enumerate(notes):
            bar = 0 if n["measure"] != prev_measure else 1
            prev_measure = n["measure"]
            pos = min(15, max(0, int(float(n["onset"] - n["measure"]) * 16)))
            midi = _SEMITONES[n["pitch"][0]] + 12 * (int(n["pitch"][1]) + 1)
            p_id = midi - 22 if ni != error_idx else PITCH_MASK
            p_id = max(0, min(85, p_id)) if ni != error_idx else PITCH_MASK
            d_val = min(63, int(float(n["duration"]) * 32)) if n["duration"] > 0 else DUR_PAD
            cp_seq.append([bar, pos + 2, p_id, d_val])
        examples.append({
            "sample_id": sid, "cp": cp_seq, "error_idx": error_idx,
            "label": pitch_classes[truth],
            "voice": notes[error_idx]["voice"],
            "staff": notes[error_idx]["staff"],
            "notes": notes,
        })
    print(f"[{split_name}] Built {len(examples)} examples, skipped {skipped}")
    return examples

train_cp = build_cp_examples(train_raw, pitch_classes, "train")
dev_cp = build_cp_examples(dev_raw, pitch_classes, "dev")

# ── Models ──
class LUT(nn.Module):
    def __init__(self, n, d, pad=None):
        super().__init__()
        self.lut = nn.Embedding(n, d, padding_idx=pad)
    def forward(self, x): return self.lut(x)

class MidiModernBERT(nn.Module):
    def __init__(self):
        super().__init__()
        self.word_emb = nn.ModuleList([
            LUT(4, 256, pad=BAR_PAD), LUT(18, 256, pad=POS_PAD),
            LUT(88, 256, pad=PITCH_PAD), LUT(66, 256, pad=DUR_PAD),
        ])
        self.in_linear = nn.Linear(1024, 768)
        _cfg = ModernBertConfig(
            vocab_size=10, hidden_size=768, num_hidden_layers=12,
            num_attention_heads=12, intermediate_size=1152,
            max_position_embeddings=4096, pad_token_id=0,
        )
        self.note_bert1 = ModernBertModel(_cfg)
    def forward(self, cp_ids, attention_mask=None):
        embs = torch.cat([self.word_emb[i](cp_ids[:,:,i]) for i in range(4)], dim=-1)
        embs = self.in_linear(embs)
        out = self.note_bert1(inputs_embeds=embs, attention_mask=attention_mask)
        return out.last_hidden_state

class M2BERTJointCorrection(nn.Module):
    def __init__(self, backbone, n_pitch, n_dur):
        super().__init__()
        self.backbone = backbone
        self.pitch_head = nn.Sequential(nn.Dropout(0.1), nn.Linear(768, n_pitch))
        self.dur_head = nn.Sequential(nn.Dropout(0.1), nn.Linear(768, n_dur))
    def forward(self, cp_ids, error_note_idx, attention_mask=None, task="pitch"):
        hidden = self.backbone(cp_ids, attention_mask)
        err_h = hidden[torch.arange(hidden.size(0)), error_note_idx]
        if task == "pitch": return self.pitch_head(err_h)
        return self.dur_head(err_h)

class ContextBranch(nn.Module):
    def __init__(self, n_key, n_ts, n_voice, n_staff, emb_dim, n_pitch):
        super().__init__()
        self.key_emb = nn.Embedding(n_key, emb_dim)
        self.ts_emb = nn.Embedding(n_ts, emb_dim)
        self.voice_emb = nn.Embedding(n_voice, emb_dim)
        self.staff_emb = nn.Embedding(n_staff, emb_dim)
        cat_dim = 768 + 4 * emb_dim
        self.fc = nn.Sequential(
            nn.Linear(cat_dim, 256), nn.GELU(), nn.Dropout(0.1),
            nn.Linear(256, n_pitch),
        )
        nn.init.zeros_(self.fc[-1].weight)
        nn.init.zeros_(self.fc[-1].bias)
    def forward(self, hidden, key_id, ts_id, voice_id, staff_id):
        ctx = torch.cat([
            hidden,
            self.key_emb(key_id), self.ts_emb(ts_id),
            self.voice_emb(voice_id), self.staff_emb(staff_id),
        ], dim=-1)
        return self.fc(ctx)

# ── Collate ──
def collate_cp(batch):
    max_len = max(len(ex["cp"]) for ex in batch)
    cp_t = torch.full((len(batch), max_len, 4), 0, dtype=torch.long)
    mask = torch.zeros(len(batch), max_len, dtype=torch.long)
    idx = torch.zeros(len(batch), dtype=torch.long)
    labels = torch.zeros(len(batch), dtype=torch.long)
    for i, ex in enumerate(batch):
        L = len(ex["cp"])
        cp_t[i, :L] = torch.tensor(ex["cp"], dtype=torch.long)
        for a, pad in enumerate(CP_PAD):
            cp_t[i, L:, a] = pad
        mask[i, :L] = 1
        idx[i] = ex["error_idx"]
        labels[i] = ex["label"]
    return cp_t, mask, idx, labels

class CPDataset(Dataset):
    def __init__(self, data): self.data = data
    def __len__(self): return len(self.data)
    def __getitem__(self, i): return self.data[i]

# ── Load joint + ctx_branch v2 and cache combined logits ──
import lxml.etree as ET

V2_DIR = ML_DIR / "data" / "runs" / "m2bert_ctx_pitch_v2_20261102_175504"
JOINT_CKPT = ML_DIR / "data" / "runs" / "m2bert_joint_20261030_213214" / "best_checkpoint.pt"

with open(V2_DIR / "feature_maps.json") as f:
    fmaps = json.load(f)
key_map = fmaps["key_map"]
ts_map = fmaps["ts_map"]
voice_map = fmaps["voice_map"]
staff_map = fmaps["staff_map"]
N_KEY = fmaps["sizes"]["key"]
N_TS = fmaps["sizes"]["ts"]
N_VOICE = fmaps["sizes"]["voice"]
N_STAFF = fmaps["sizes"]["staff"]

def _xml_path(sid):
    parts = sid.split("/")
    return DATASET_ROOT / "samples" / parts[1] / (parts[2] + ".musicxml")

def extract_key_fifths(sid):
    xp = _xml_path(sid)
    if not xp.exists(): return "None"
    try:
        tree = ET.parse(str(xp))
        el = tree.find(".//key/fifths")
        if el is not None and el.text: return el.text.strip()
    except: pass
    return "None"

def extract_time_sig(sid):
    xp = _xml_path(sid)
    if not xp.exists(): return "None"
    try:
        tree = ET.parse(str(xp))
        beats = tree.find(".//time/beats")
        bt = tree.find(".//time/beat-type")
        if beats is not None and bt is not None:
            return f"({beats.text.strip()}, {bt.text.strip()})"
    except: pass
    return "None"

print("Loading joint model...")
bb = MidiModernBERT()
pre = torch.load(PRETRAINED / "model_best.ckpt", map_location="cpu", weights_only=False)
bb.load_state_dict(pre["state_dict"], strict=True); del pre

joint = M2BERTJointCorrection(bb, N_CLASSES, 28)
jckpt = torch.load(JOINT_CKPT, map_location="cpu", weights_only=False)
joint.load_state_dict(jckpt["model_state_dict"], strict=True); del jckpt
joint.to(DEVICE).eval()
for p in joint.parameters():
    p.requires_grad_(False)

# Load ctx_branch v2
ctx_ckpt = torch.load(V2_DIR / "best_checkpoint.pt", map_location="cpu", weights_only=False)
cc = ctx_ckpt["ctx_config"]
ctx_branch_frozen = ContextBranch(cc["N_KEY"], cc["N_TS"], cc["N_VOICE"], cc["N_STAFF"],
                                   cc["CTX_EMB_DIM"], N_CLASSES)
ctx_branch_frozen.load_state_dict(ctx_ckpt["model_state_dict"], strict=True)
ctx_branch_frozen.to(DEVICE).eval()
for p in ctx_branch_frozen.parameters():
    p.requires_grad_(False)
print("Joint + ctx_branch_v2 loaded")

# Build context IDs
def build_ctx_ids(cp_examples):
    ctx = []
    for ex in cp_examples:
        sid = ex["sample_id"]
        k = key_map.get(extract_key_fifths(sid), 0)
        t = ts_map.get(extract_time_sig(sid), 0)
        v = voice_map.get(f"voice:{ex['voice']}", 0)
        s = staff_map.get(f"staff:{ex['staff']}", 0)
        ctx.append((k, t, v, s))
    return ctx

print("Building context features...")
train_ctx = build_ctx_ids(train_cp)
dev_ctx = build_ctx_ids(dev_cp)

# Cache combined logits (backbone + pitch_head + ctx_branch)
print("Caching combined logits...")
t0 = time.time()

def cache_combined(cp_list, ctx_list, split_name):
    loader = DataLoader(CPDataset(cp_list), batch_size=32, shuffle=False,
                        collate_fn=collate_cp, num_workers=0)
    all_logits = []; all_labels = []
    ctx_t = torch.tensor(ctx_list, dtype=torch.long)
    offset = 0
    with torch.no_grad():
        for bi, (cp_t, mask_t, idx_t, lab_t) in enumerate(loader):
            bs = cp_t.size(0)
            cp_t, mask_t, idx_t = cp_t.to(DEVICE), mask_t.to(DEVICE), idx_t.to(DEVICE)
            h = joint.backbone(cp_t, mask_t)
            err_h = h[torch.arange(bs), idx_t]
            base_logits = joint.pitch_head(err_h)
            c = ctx_t[offset:offset+bs].to(DEVICE)
            ctx_residual = ctx_branch_frozen(err_h, c[:,0], c[:,1], c[:,2], c[:,3])
            combined = base_logits + ctx_residual
            all_logits.append(combined.cpu())
            all_labels.append(lab_t)
            offset += bs
            if (bi+1) % 50 == 0:
                print(f"  [{split_name}] batch {bi+1}")
    return torch.cat(all_logits), torch.cat(all_labels)

train_logits, train_labels = cache_combined(train_cp, train_ctx, "train")
dev_logits, dev_labels = cache_combined(dev_cp, dev_ctx, "dev")
cache_time = time.time() - t0
print(f"Cached in {cache_time:.1f}s  train={train_logits.shape}  dev={dev_logits.shape}")

# Verify baseline
baseline_top1 = (dev_logits.argmax(1) == dev_labels).sum().item()
baseline_top5_count = sum(1 for i in range(len(dev_labels))
                          if dev_labels[i] in dev_logits[i].topk(5).indices)
print(f"Baseline: top1={baseline_top1}/499  top5={baseline_top5_count}/499")
assert baseline_top1 == 323, f"Expected baseline 323, got {baseline_top1}"
assert baseline_top5_count == 448, f"Expected baseline top5 448, got {baseline_top5_count}"

# ── Build reranker features (same 16 features as original) ──
print("Building reranker features...")

def build_reranker_data(cp_list, logits_t, labels_t, split_name):
    """Build per-candidate features for top-5 reranking."""
    K = 5
    features_list = []; cand_indices_list = []; target_ranks = []; valid_mask = []

    for i in range(len(cp_list)):
        ex = cp_list[i]
        logits_i = logits_t[i]
        label_i = labels_t[i].item()
        notes = ex["notes"]
        error_idx = ex["error_idx"]

        topk = logits_i.topk(K)
        cand_ids = topk.indices.tolist()
        cand_logits = topk.values.tolist()

        if label_i in cand_ids:
            target_rank = cand_ids.index(label_i)
            valid_mask.append(True)
        else:
            target_rank = -1
            valid_mask.append(False)

        target_ranks.append(target_rank)
        cand_indices_list.append(cand_ids)

        log_probs = torch.log_softmax(logits_i, dim=0)
        cand_log_probs = [log_probs[c].item() for c in cand_ids]

        err_voice = notes[error_idx]["voice"]
        err_onset = notes[error_idx]["onset"]

        same_voice = [(ni, n) for ni, n in enumerate(notes)
                      if n["voice"] == err_voice and ni != error_idx and not n["grace"]]
        prev_note = None; next_note = None
        for ni, n in same_voice:
            if n["onset"] < err_onset:
                if prev_note is None or n["onset"] > prev_note[1]["onset"]:
                    prev_note = (ni, n)
            elif n["onset"] > err_onset:
                if next_note is None or n["onset"] < next_note[1]["onset"]:
                    next_note = (ni, n)

        prev_midi = pitch_to_midi(prev_note[1]["pitch"]) if prev_note else None
        next_midi = pitch_to_midi(next_note[1]["pitch"]) if next_note else None

        simul = [n for n in notes if n["onset"] == err_onset
                 and n is not notes[error_idx] and not n["grace"]
                 and PITCH_RE.match(n["pitch"])]
        simul_midis = [pitch_to_midi(n["pitch"]) for n in simul]

        sv_midis = sorted([(abs(float(n["onset"] - err_onset)), pitch_to_midi(n["pitch"]))
                           for _, n in same_voice if PITCH_RE.match(n["pitch"])],
                          key=lambda x: x[0])
        local_midis = [m for _, m in sv_midis[:6]]
        local_median = sorted(local_midis)[len(local_midis)//2] if local_midis else 60

        feats_i = []
        for j, cid in enumerate(cand_ids):
            cand_pitch = id2pitch[cid]
            cand_midi = pitch_to_midi(cand_pitch)

            f = [
                cand_logits[j],
                cand_log_probs[j],
                float(j),
                cand_logits[j] - cand_logits[0],
                float(cand_midi - prev_midi) if prev_midi else 0.0,
                float(abs(cand_midi - prev_midi)) if prev_midi else 0.0,
                1.0 if prev_midi else 0.0,
                float(cand_midi - next_midi) if next_midi else 0.0,
                float(abs(cand_midi - next_midi)) if next_midi else 0.0,
                1.0 if next_midi else 0.0,
                float(cand_midi - local_median),
            ]
            if simul_midis:
                intervals = [cand_midi - sm for sm in simul_midis]
                f.extend([
                    float(min(intervals)),
                    float(max(intervals)),
                    float(sum(intervals)/len(intervals)),
                    float(sum(abs(iv) for iv in intervals)/len(intervals)),
                    1.0,
                ])
            else:
                f.extend([0.0, 0.0, 0.0, 0.0, 0.0])

            feats_i.append(f)
        features_list.append(feats_i)

    n_valid = sum(valid_mask)
    print(f"[{split_name}] {n_valid}/{len(cp_list)} have target in top-5")
    return features_list, cand_indices_list, target_ranks, valid_mask

train_feats, train_cands, train_tgt_ranks, train_valid = build_reranker_data(
    train_cp, train_logits, train_labels, "train")
dev_feats, dev_cands, dev_tgt_ranks, dev_valid = build_reranker_data(
    dev_cp, dev_logits, dev_labels, "dev")

# ── Normalize features ──
train_feat_flat = []
for i, feats in enumerate(train_feats):
    if train_valid[i]:
        for f in feats:
            train_feat_flat.append(f)
train_feat_t = torch.tensor(train_feat_flat, dtype=torch.float32)
feat_mean = train_feat_t.mean(0)
feat_std = train_feat_t.std(0).clamp(min=1e-6)
print(f"Feature mean: {feat_mean.tolist()}")
print(f"Feature std:  {feat_std.tolist()}")

orig_stats = torch.load(ML_DIR / "data" / "runs" / "m2bert_reranker_20261102_182741" / "norm_stats.pt",
                         map_location="cpu", weights_only=False)
print(f"Orig mean diff: {(feat_mean - orig_stats['feat_mean']).abs().max().item():.6f}")
print(f"Orig std diff:  {(feat_std - orig_stats['feat_std']).abs().max().item():.6f}")

def normalize_feats(feats_list, mean, std):
    out = []
    for feats in feats_list:
        t = torch.tensor(feats, dtype=torch.float32)
        t = (t - mean.unsqueeze(0)) / std.unsqueeze(0)
        out.append(t)
    return torch.stack(out)

train_feats_t = normalize_feats(train_feats, feat_mean, feat_std)
dev_feats_t = normalize_feats(dev_feats, feat_mean, feat_std)
print(f"Normalized features: train={train_feats_t.shape}  dev={dev_feats_t.shape}")

# ── Build training tensors (valid examples only) ──
train_indices = [i for i in range(len(train_valid)) if train_valid[i]]
train_X = train_feats_t[train_indices]
train_base_logits_top5 = torch.zeros(len(train_indices), 5)
train_target = torch.zeros(len(train_indices), dtype=torch.long)
for j, i in enumerate(train_indices):
    for k in range(5):
        train_base_logits_top5[j, k] = train_logits[i][train_cands[i][k]]
    train_target[j] = train_tgt_ranks[i]

print(f"Training set: {len(train_indices)} valid examples")

# ── Reranker MLP (same architecture) ──
class Reranker(nn.Module):
    def __init__(self, n_feat=16, hidden=64):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(n_feat, hidden),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hidden, 1),
        )
        nn.init.zeros_(self.mlp[-1].weight)
        nn.init.zeros_(self.mlp[-1].bias)

    def forward(self, feats):
        return self.mlp(feats).squeeze(-1)

# ── Training loop: 10 epochs, NO early stopping ──
torch.manual_seed(42)
reranker = Reranker(n_feat=16, hidden=64)
reranker.to(DEVICE)

n_params = sum(p.numel() for p in reranker.parameters())
print(f"Reranker params: {n_params}")

optimizer = torch.optim.AdamW(reranker.parameters(), lr=1e-3, weight_decay=0.01)
loss_fn = nn.CrossEntropyLoss()

MAX_EPOCHS = 10
BUDGET_S = 30
BATCH_SIZE = 128

train_log = []
best_top1 = 0; best_epoch = 0; best_state = None
last_state = None

t_start = time.time()
print(f"\nTraining reranker: max_epochs={MAX_EPOCHS}, NO early stopping, budget={BUDGET_S}s")
print(f"seed=42, lr=1e-3, batch_size={BATCH_SIZE}")

for epoch in range(1, MAX_EPOCHS + 1):
    elapsed = time.time() - t_start
    if elapsed > BUDGET_S:
        print(f"Budget exceeded at epoch {epoch} ({elapsed:.1f}s > {BUDGET_S}s)")
        break

    reranker.train()
    perm = torch.randperm(len(train_X))
    total_loss = 0.0; n_batches = 0
    epoch_grad_norms = []; epoch_update_norms = []

    for start in range(0, len(train_X), BATCH_SIZE):
        bi = perm[start:start+BATCH_SIZE]
        X_batch = train_X[bi].to(DEVICE)
        tgt_batch = train_target[bi].to(DEVICE)
        bl_batch = train_base_logits_top5[bi].to(DEVICE)

        params_before = {n: p.data.clone() for n, p in reranker.named_parameters()}

        residual = reranker(X_batch)
        scores = bl_batch + residual
        loss = loss_fn(scores, tgt_batch)

        optimizer.zero_grad()
        loss.backward()

        grad_norm = 0.0
        for p in reranker.parameters():
            if p.grad is not None:
                grad_norm += p.grad.data.norm(2).item() ** 2
        grad_norm = math.sqrt(grad_norm)
        epoch_grad_norms.append(grad_norm)

        optimizer.step()

        update_norm = 0.0
        for n, p in reranker.named_parameters():
            update_norm += (p.data - params_before[n]).norm(2).item() ** 2
        update_norm = math.sqrt(update_norm)
        epoch_update_norms.append(update_norm)

        total_loss += loss.item(); n_batches += 1

    avg_loss = total_loss / n_batches
    avg_grad_norm = sum(epoch_grad_norms) / len(epoch_grad_norms)
    avg_update_norm = sum(epoch_update_norms) / len(epoch_update_norms)

    reranker.eval()
    with torch.no_grad():
        dev_X_d = dev_feats_t.to(DEVICE)
        dev_residual = reranker(dev_X_d).cpu()

    top1_correct = 0; top5_correct = 0
    wrong_to_right = 0; right_to_wrong = 0
    residual_abs_vals = []

    for i in range(len(dev_cp)):
        label_i = dev_labels[i].item()
        cand_ids = dev_cands[i]

        baseline_correct = (cand_ids[0] == label_i)

        base_scores = torch.tensor([dev_logits[i][c].item() for c in cand_ids])
        reranked = base_scores + dev_residual[i]
        best_cand_idx = reranked.argmax().item()
        pred_id = cand_ids[best_cand_idx]

        reranked_correct = (pred_id == label_i)
        if reranked_correct: top1_correct += 1
        if label_i in cand_ids: top5_correct += 1

        if not baseline_correct and reranked_correct: wrong_to_right += 1
        if baseline_correct and not reranked_correct: right_to_wrong += 1

        residual_abs_vals.extend(dev_residual[i].abs().tolist())

    residual_abs_mean = sum(residual_abs_vals) / len(residual_abs_vals)
    residual_abs_max = max(residual_abs_vals)

    elapsed = time.time() - t_start

    log_entry = {
        "epoch": epoch,
        "train_loss": round(avg_loss, 6),
        "dev_top1": top1_correct,
        "dev_top5": top5_correct,
        "wrong_to_right": wrong_to_right,
        "right_to_wrong": right_to_wrong,
        "residual_abs_mean": round(residual_abs_mean, 6),
        "residual_abs_max": round(residual_abs_max, 6),
        "grad_norm_avg": round(avg_grad_norm, 6),
        "update_norm_avg": round(avg_update_norm, 6),
        "elapsed_s": round(elapsed, 1),
    }
    train_log.append(log_entry)

    print(f"Epoch {epoch}: loss={avg_loss:.6f}  top1={top1_correct}  top5={top5_correct}  "
          f"W->R={wrong_to_right}  R->W={right_to_wrong}  "
          f"res_mean={residual_abs_mean:.6f}  res_max={residual_abs_max:.6f}  "
          f"grad={avg_grad_norm:.6f}  update={avg_update_norm:.6f}  "
          f"elapsed={elapsed:.1f}s")

    last_state = {k: v.cpu().clone() for k, v in reranker.state_dict().items()}
    last_optim_state = optimizer.state_dict()

    if top1_correct > best_top1 or (top1_correct == best_top1 and epoch == 1):
        best_top1 = top1_correct; best_epoch = epoch
        best_state = {k: v.cpu().clone() for k, v in reranker.state_dict().items()}
        best_top5 = top5_correct
        best_w2r = wrong_to_right; best_r2w = right_to_wrong

train_time = time.time() - t_start

# ── Save ──
RUN_NAME = "m2bert_reranker_10ep_" + datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = ML_DIR / "data" / "runs" / RUN_NAME
RUN_DIR.mkdir(parents=True, exist_ok=True)

torch.save({
    "model_state_dict": best_state,
    "n_feat": 16, "hidden": 64,
    "feat_mean": feat_mean, "feat_std": feat_std,
    "best_epoch": best_epoch, "best_top1": best_top1,
    "parent_joint_ckpt": str(JOINT_CKPT),
    "parent_ctx_run": str(V2_DIR),
    "checkpoint_type": "reranker_only",
}, RUN_DIR / "best_checkpoint.pt")

torch.save({
    "model_state_dict": last_state,
    "optimizer_state_dict": last_optim_state,
    "n_feat": 16, "hidden": 64,
    "feat_mean": feat_mean, "feat_std": feat_std,
    "last_epoch": len(train_log),
    "parent_joint_ckpt": str(JOINT_CKPT),
    "parent_ctx_run": str(V2_DIR),
    "checkpoint_type": "reranker_only",
}, RUN_DIR / "last_checkpoint.pt")

config = {
    "task": "pitch_reranker_10ep",
    "parent_checkpoints": {
        "joint": str(JOINT_CKPT),
        "ctx_branch_v2": str(V2_DIR / "best_checkpoint.pt"),
    },
    "frozen": ["backbone", "pitch_head", "ctx_branch"],
    "trainable": ["reranker"],
    "n_feat": 16, "hidden": 64, "reranker_params": n_params,
    "train_n_total": len(train_cp),
    "train_n_valid": len(train_indices),
    "dev_n": len(dev_cp),
    "train_candidate_coverage": f"{len(train_indices)}/{len(train_cp)}",
    "dev_candidate_coverage": f"{sum(dev_valid)}/{len(dev_cp)}",
    "lr": 1e-3, "batch_size": BATCH_SIZE,
    "max_epochs": MAX_EPOCHS, "early_stopping": False,
    "budget_s": BUDGET_S,
    "seed": 42,
    "initialization": "zero-init output layer, default init for hidden",
    "baseline_top1": 323, "baseline_top5": 448,
    "best_epoch": best_epoch, "best_top1": best_top1, "best_top5": best_top5,
    "best_wrong_to_right": best_w2r, "best_right_to_wrong": best_r2w,
    "final_epoch": len(train_log),
    "final_top1": train_log[-1]["dev_top1"],
    "final_top5": train_log[-1]["dev_top5"],
    "final_wrong_to_right": train_log[-1]["wrong_to_right"],
    "final_right_to_wrong": train_log[-1]["right_to_wrong"],
    "cache_time_s": round(cache_time, 1),
    "train_time_s": round(train_time, 1),
    "total_time_s": round(cache_time + train_time, 1),
    "adopted": best_top1 > 323,
    "adopt_reason": f"top-1 {best_top1} {'>' if best_top1 > 323 else '<='} 323",
    "run_name": RUN_NAME,
    "feature_definitions": [
        "logit","log_prob","rank","logit_diff_from_top1",
        "signed_interval_prev","abs_interval_prev","has_prev",
        "signed_interval_next","abs_interval_next","has_next",
        "register_offset_from_median",
        "simul_interval_min","simul_interval_max","simul_interval_mean",
        "simul_abs_interval_mean","has_simultaneous",
    ],
    "original_reranker_run": "m2bert_reranker_20261102_182741",
}
with open(RUN_DIR / "config.json", "w") as f:
    json.dump(config, f, indent=2)

with open(RUN_DIR / "metrics.json", "w") as f:
    json.dump({"train_log": train_log,
               "best": {"epoch": best_epoch, "top1": best_top1, "top5": best_top5},
               "final": {"epoch": len(train_log),
                          "top1": train_log[-1]["dev_top1"],
                          "top5": train_log[-1]["dev_top5"]}}, f, indent=2)

reranker.load_state_dict(best_state)
reranker.eval()
with torch.no_grad():
    dev_residual_best = reranker(dev_feats_t.to(DEVICE)).cpu()

preds = []
for i in range(len(dev_cp)):
    label_i = dev_labels[i].item()
    cand_ids = dev_cands[i]
    base_scores = torch.tensor([dev_logits[i][c].item() for c in cand_ids])
    reranked = base_scores + dev_residual_best[i]
    order = reranked.argsort(descending=True)
    preds.append({
        "dev_idx": i,
        "sample_id": dev_cp[i]["sample_id"],
        "true_label": id2pitch[label_i],
        "top5": [{"label": id2pitch[cand_ids[order[j].item()]],
                   "score": round(reranked[order[j].item()].item(), 4)}
                  for j in range(5)],
        "correct_top1": cand_ids[order[0].item()] == label_i,
        "correct_top5": label_i in cand_ids,
    })

with open(RUN_DIR / "dev_predictions.json", "w") as f:
    json.dump(preds, f, indent=2)

torch.save({"feat_mean": feat_mean, "feat_std": feat_std}, RUN_DIR / "norm_stats.pt")

print(f"\n{'='*70}")
print(f"RERANKER 10-EPOCH RESULTS: {RUN_NAME}")
print(f"{'='*70}")
print(f"Epochs completed: {len(train_log)}")
print(f"Best epoch: {best_epoch}  top1={best_top1}  top5={best_top5}  W->R={best_w2r}  R->W={best_r2w}")
print(f"Last epoch: {len(train_log)}  top1={train_log[-1]['dev_top1']}  top5={train_log[-1]['dev_top5']}  "
      f"W->R={train_log[-1]['wrong_to_right']}  R->W={train_log[-1]['right_to_wrong']}")
print(f"Baseline: 323/499  top5=448/499")
print(f"\nPer-epoch trajectory:")
print(f"{'Ep':>3} {'Loss':>10} {'Top1':>5} {'Top5':>5} {'W->R':>5} {'R->W':>5} "
      f"{'Res_mean':>10} {'Res_max':>10} {'Grad':>10} {'Update':>10} {'Time':>6}")
for e in train_log:
    print(f"{e['epoch']:3d} {e['train_loss']:10.6f} {e['dev_top1']:5d} {e['dev_top5']:5d} "
          f"{e['wrong_to_right']:5d} {e['right_to_wrong']:5d} "
          f"{e['residual_abs_mean']:10.6f} {e['residual_abs_max']:10.6f} "
          f"{e['grad_norm_avg']:10.6f} {e['update_norm_avg']:10.6f} "
          f"{e['elapsed_s']:6.1f}")
print(f"\nTrain time: {train_time:.1f}s  Cache time: {cache_time:.1f}s")
print(f"Run dir: {RUN_DIR}")
