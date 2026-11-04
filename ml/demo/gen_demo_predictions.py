"""
gen_demo_predictions.py — generate prediction.json files for demo.ipynb

Run once from the ml/ directory:
    python demo/gen_demo_predictions.py

Outputs:
  demo/unified_joint/pitch_{idx}_{sid}/prediction.json  (indices 12, 72, 327)
  demo/unified_joint/pitch_72_samples_5986599_p4-s3/{ground_truth,corrupted,model_corrected}.{musicxml,mid}
  demo/unified_joint/dur_{idx}_{sid}/prediction.json    (indices 12, 57, 327)
"""

import json, re, pickle, hashlib, random
from pathlib import Path
from fractions import Fraction as _Frac
from collections import Counter

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import ModernBertConfig, ModernBertModel
from lxml import etree
import mido

ML_DIR       = Path('/Users/zhaojinlan/Desktop/Lann Projects/What-the-fingers-hear/ml')
PROCESSED    = ML_DIR / 'data' / 'processed'
PRETRAINED   = ML_DIR / 'data' / 'pretrained' / 'm2bert'
DATASET_ROOT = ML_DIR / 'dataset' / 'olimpic-1.0-synthetic'
UNIFIED_OUT  = ML_DIR / 'demo' / 'unified_joint'

DEVICE = (torch.device('mps')  if torch.backends.mps.is_available() else
          torch.device('cuda') if torch.cuda.is_available() else
          torch.device('cpu'))
print(f'DEVICE: {DEVICE}')

# ── CP vocab ──────────────────────────────────────────────────────────────────
with open(PRETRAINED / 'CP.pkl', 'rb') as f:
    _cp = pickle.load(f)
CP_TOK2ID = _cp[0]
BAR_PAD   = CP_TOK2ID['Bar']['Bar <PAD>']
POS_PAD   = CP_TOK2ID['Position']['Position <PAD>']
PITCH_PAD  = CP_TOK2ID['Pitch']['Pitch <PAD>']
PITCH_MASK = CP_TOK2ID['Pitch']['Pitch <MASK>']
DUR_PAD    = CP_TOK2ID['Duration']['Duration <PAD>']
DUR_MASK   = CP_TOK2ID['Duration']['Duration <MASK>']
CP_PAD     = [BAR_PAD, POS_PAD, PITCH_PAD, DUR_PAD]

PITCH_RE  = re.compile(r'^[A-G][0-9]$')
_SEMITONES = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
_DURATION_BASE = {
    'breve':_Frac(2), 'whole':_Frac(1), 'half':_Frac(1,2),
    'quarter':_Frac(1,4), 'eighth':_Frac(1,8), '16th':_Frac(1,16),
    '32nd':_Frac(1,32), '64th':_Frac(1,64), '128th':_Frac(1,128),
    '256th':_Frac(1,256), '512th':_Frac(1,512), '1024th':_Frac(1,1024),
}
_DECORATION = frozenset({
    'beam:begin','beam:end','beam:forward-hook','beam:backward-hook',
    'tied:start','tied:stop','tuplet:start','tuplet:stop',
    'slur:start','slur:stop','trill-mark','staccato','accent',
    'strong-accent','tenuto','fermata','arpeggiate',
    'tremolo:1','tremolo:2','tremolo:3','tremolo:4',
    'tremolo:single','tremolo:start','tremolo:stop',
})
_ACCIDENTAL = frozenset({'sharp','flat','natural','double-sharp','flat-flat','natural-sharp','natural-flat'})
_SKIP       = frozenset({'time'})
_TIME_MOD_RE = re.compile(r'^(\d+)in(\d+)$')

def _lmx_path(sid):
    p = sid.split('/')
    return DATASET_ROOT / 'samples' / p[1] / (p[2] + '.lmx')

def _xml_path(sid):
    p = sid.split('/')
    return DATASET_ROOT / 'samples' / p[1] / (p[2] + '.musicxml')

# ── LMX parser (m2bert_finetune version — measure-local onset) ───────────────
def _parse_dur_tok(tokens, i):
    if i >= len(tokens) or tokens[i] not in _DURATION_BASE:
        return None, i
    base = _DURATION_BASE[tokens[i]]; i += 1
    m = _TIME_MOD_RE.match(tokens[i]) if i < len(tokens) else None
    if m:
        base *= _Frac(int(m.group(2)), int(m.group(1))); i += 1
    n_dots = 0
    while i < len(tokens) and tokens[i] == 'dot':
        n_dots += 1; i += 1
    if n_dots:
        base *= (2 - _Frac(1, 2**n_dots))
    return base, i

def parse_lmx_notes(tokens, sample_id=''):
    notes, warnings = [], []
    current_voice = current_staff = None
    current_beats = current_beat_type = None
    measure_num   = 0
    current_onset = _Frac(0)
    chord_group_id = 0; chord_leader_onset = _Frac(0)
    i, n = 0, len(tokens)
    while i < n:
        tok = tokens[i]
        if tok == 'measure':
            measure_num += 1; current_onset = _Frac(0); i += 1; continue
        if tok in _SKIP or tok.startswith('key:'):
            i += 1; continue
        if tok.startswith('beats:'):
            try: current_beats = int(tok[6:])
            except ValueError: pass
            i += 1; continue
        if tok.startswith('beat-type:'):
            try: current_beat_type = int(tok[10:])
            except ValueError: pass
            i += 1; continue
        if tok.startswith('clef:'):
            i += 1
            if i < n and tokens[i].startswith('staff:'): i += 1
            continue
        if tok in _DECORATION:
            i += 1; continue
        span_start = i
        is_grace = is_chord = False
        if tok == 'print-object:no':
            i += 1
            if i >= n: break
            tok = tokens[i]
        if tok == 'grace':
            is_grace = True; i += 1
            if i >= n: break
            tok = tokens[i]
            if tok == 'grace:slash':
                i += 1
                if i >= n: break
                tok = tokens[i]
        if tok == 'chord':
            is_chord = True; i += 1
            if i >= n: break
            tok = tokens[i]
        pitch = None; is_rest = False; pitch_token_position = None
        if PITCH_RE.match(tok):
            pitch, pitch_token_position = tok, i; i += 1
        elif tok == 'rest':
            is_rest = True; i += 1
        elif tok == 'backup':
            i += 1; dur, i = _parse_dur_tok(tokens, i)
            if dur is not None: current_onset = max(_Frac(0), current_onset - dur)
            continue
        elif tok == 'forward':
            i += 1; dur, i = _parse_dur_tok(tokens, i)
            if dur is not None: current_onset += dur
            continue
        else:
            i += 1; continue
        if i < n and tokens[i].startswith('voice:'):
            current_voice = tokens[i]; i += 1
        duration = None
        if i < n:
            if tokens[i] in _DURATION_BASE:
                duration, i = _parse_dur_tok(tokens, i)
            elif tokens[i] == 'rest:measure':
                if current_beats is not None and current_beat_type is not None:
                    duration = _Frac(current_beats, current_beat_type)
                i += 1
        if i < n and tokens[i] in _ACCIDENTAL: i += 1
        if i < n and tokens[i].startswith('stem:'): i += 1
        if i < n and tokens[i].startswith('staff:'):
            current_staff = tokens[i]; i += 1
        while i < n and tokens[i] in _DECORATION: i += 1
        onset = chord_leader_onset if is_chord else current_onset
        if is_chord: grp = chord_group_id
        else:
            chord_group_id += 1; grp = chord_group_id
            chord_leader_onset = current_onset
        notes.append({'measure': measure_num, 'voice': current_voice, 'staff': current_staff,
                      'onset': onset, 'duration': duration, 'pitch': pitch,
                      'is_rest': is_rest, 'is_grace': is_grace, 'chord_group': grp,
                      'pitch_token_position': pitch_token_position,
                      'token_span': (span_start, i)})
        if not is_chord and not is_grace and duration is not None:
            current_onset += duration
    return notes, warnings

# ── Pitch helpers ─────────────────────────────────────────────────────────────
def _pitch_to_cp_idx(tok):
    midi = (int(tok[1]) + 1) * 12 + _SEMITONES[tok[0]]
    idx  = midi - 22
    return idx if 0 <= idx <= 85 else None

def lmx_to_cp_example(ex, pitch_classes):
    target = ex['target_token']
    if target not in pitch_classes:
        return None
    tokens  = ex['input_tokens'] if isinstance(ex['input_tokens'], list) else ex['input_tokens'].split()
    notes, _ = parse_lmx_notes(tokens, ex.get('sample_id', ''))
    err_pos  = ex['error_position']
    err_idx  = next((i for i, n in enumerate(notes) if n['pitch_token_position'] == err_pos), None)
    if err_idx is None:
        return None
    cp_ids = []; prev_meas = -1
    for i, note in enumerate(notes):
        bar  = 0 if note['measure'] != prev_meas else 1; prev_meas = note['measure']
        pos  = min(15, int(float(note['onset']) * 16))
        if i == err_idx:
            p_id = PITCH_MASK
        elif note['pitch'] and PITCH_RE.match(note['pitch']):
            p = _pitch_to_cp_idx(note['pitch'])
            p_id = p if p is not None else PITCH_PAD
        else:
            p_id = PITCH_PAD
        dur = min(63, int(float(note['duration']) * 32)) if note['duration'] is not None else DUR_PAD
        cp_ids.append([bar, pos, p_id, dur])
    return cp_ids, err_idx, pitch_classes[target]

# ── Duration helpers ──────────────────────────────────────────────────────────
_DUR_REPL_POOL = [
    (['whole'],          _Frac(1)),
    (['half'],           _Frac(1,2)),
    (['quarter'],        _Frac(1,4)),
    (['eighth'],         _Frac(1,8)),
    (['16th'],           _Frac(1,16)),
    (['half','dot'],     _Frac(3,4)),
    (['quarter','dot'],  _Frac(3,8)),
    (['eighth','dot'],   _Frac(3,16)),
]

def _find_dur_span(tokens, note):
    s, e = note['token_span']
    for i in range(s, e):
        if tokens[i] in _DURATION_BASE:
            j = i + 1
            if j < e and _TIME_MOD_RE.match(tokens[j]): j += 1
            while j < e and tokens[j] == 'dot': j += 1
            return i, j
    return None, None

def build_dur_split(sample_ids, label_map=None):
    build_map = (label_map is None)
    raw = []; skip = Counter()
    for sid in sample_ids:
        lmx_p = _lmx_path(sid)
        if not lmx_p.exists(): skip['no_lmx'] += 1; continue
        clean_toks = lmx_p.read_text().split()
        notes, _   = parse_lmx_notes(clean_toks, sid)
        cands = [ni for ni, n in enumerate(notes)
                 if not n['is_grace'] and not n['is_rest']
                 and n['duration'] is not None and n['pitch'] is not None
                 and _find_dur_span(clean_toks, n)[0] is not None]
        if not cands: skip['no_candidate'] += 1; continue
        h   = int(hashlib.md5(sid.encode()).hexdigest(), 16)
        sel = cands[h % len(cands)]
        note     = notes[sel]
        true_dur = note['duration']
        true_ql  = str(true_dur * 4)
        rng  = random.Random(h)
        pool = [(t, f) for t, f in _DUR_REPL_POOL if f != true_dur]
        rtoks, rfrac = pool[rng.randint(0, len(pool) - 1)]
        ds, de = _find_dur_span(clean_toks, note)
        corrupted = clean_toks[:ds] + rtoks + clean_toks[de:]
        raw.append({'sid': sid, 'corrupted': corrupted,
                    'epp': note['pitch_token_position'],
                    'true_ql': true_ql, 'repl_ql': str(rfrac * 4)})
    if build_map:
        ql_counts = Counter(r['true_ql'] for r in raw)
        label_map = {ql: i for i, (ql, _) in enumerate(ql_counts.most_common())}
    cp_list, details = [], []
    for r in raw:
        if r['true_ql'] not in label_map: skip['oov_dur'] += 1; continue
        cnotes, _ = parse_lmx_notes(r['corrupted'], r['sid'])
        err_idx   = next((i for i, n in enumerate(cnotes)
                          if n['pitch_token_position'] == r['epp']), None)
        if err_idx is None: skip['err_not_found'] += 1; continue
        cp_ids = []; prev_m = -1
        for i, n in enumerate(cnotes):
            bar  = 0 if n['measure'] != prev_m else 1; prev_m = n['measure']
            pos  = min(15, int(float(n['onset']) * 16))
            p_id = PITCH_PAD
            if n['pitch'] and PITCH_RE.match(n['pitch']):
                p = _pitch_to_cp_idx(n['pitch'])
                if p is not None: p_id = p
            dur = DUR_MASK if i == err_idx else (
                min(63, int(float(n['duration']) * 32)) if n['duration'] is not None else DUR_PAD)
            cp_ids.append([bar, pos, p_id, dur])
        cp_list.append({'cp_ids': cp_ids, 'error_note_idx': err_idx,
                        'target_class': label_map[r['true_ql']], 'sample_id': r['sid']})
        details.append({'sample_id': r['sid'], 'true_ql': r['true_ql'], 'repl_ql': r['repl_ql']})
    print(f'  dur split: {len(cp_list)} ok, skip={dict(skip)}')
    return cp_list, label_map, details

# ── Collate + Dataset ─────────────────────────────────────────────────────────
class CPDataset(Dataset):
    def __init__(self, data): self.data = data
    def __len__(self): return len(self.data)
    def __getitem__(self, i): return self.data[i]

def collate_cp(batch):
    max_len = max(len(ex['cp_ids']) for ex in batch)
    cp_t  = torch.full((len(batch), max_len, 4), 0, dtype=torch.long)
    mask  = torch.zeros(len(batch), max_len, dtype=torch.long)
    idx_t = torch.zeros(len(batch), dtype=torch.long)
    lbl_t = torch.zeros(len(batch), dtype=torch.long)
    for i, ex in enumerate(batch):
        L = len(ex['cp_ids'])
        cp_t[i, :L] = torch.tensor(ex['cp_ids'], dtype=torch.long)
        for a, pad in enumerate(CP_PAD):
            cp_t[i, L:, a] = pad
        mask[i, :L] = 1
        idx_t[i] = ex['error_note_idx']
        lbl_t[i] = ex['target_class']
    return cp_t, mask, idx_t, lbl_t

# ── Model classes ─────────────────────────────────────────────────────────────
class LUT(nn.Module):
    def __init__(self, n, d, pad=None):
        super().__init__(); self.lut = nn.Embedding(n, d, padding_idx=pad)
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
        embs = torch.cat([self.word_emb[i](cp_ids[:, :, i]) for i in range(4)], dim=-1)
        embs = self.in_linear(embs)
        return self.note_bert1(inputs_embeds=embs, attention_mask=attention_mask).last_hidden_state

class M2BERTJointCorrection(nn.Module):
    def __init__(self, backbone, n_pitch, n_dur):
        super().__init__()
        self.backbone   = backbone
        self.pitch_head = nn.Sequential(nn.Dropout(0.1), nn.Linear(768, n_pitch))
        self.dur_head   = nn.Sequential(nn.Dropout(0.1), nn.Linear(768, n_dur))
    def forward(self, cp_ids, error_note_idx, attention_mask=None, task='pitch'):
        hidden = self.backbone(cp_ids, attention_mask)
        err_h  = hidden[torch.arange(hidden.size(0)), error_note_idx]
        return self.pitch_head(err_h) if task == 'pitch' else self.dur_head(err_h)

class M2BERTDuration(nn.Module):
    def __init__(self, backbone, n_classes):
        super().__init__()
        self.backbone   = backbone
        self.classifier = nn.Sequential(nn.Dropout(0.1), nn.Linear(768, n_classes))
    def forward(self, cp_ids, error_note_idx, attention_mask=None):
        hidden = self.backbone(cp_ids, attention_mask)
        err_h  = hidden[torch.arange(hidden.size(0)), error_note_idx]
        return self.classifier(err_h)

# ── MusicXML / MIDI utilities ─────────────────────────────────────────────────
def _xml_tag(name, ns):
    return f'{{{ns}}}{name}' if ns else name

def set_note_pitch(note_el, pitch_token, ns=''):
    t = lambda name: _xml_tag(name, ns)
    pitch_el = note_el.find(t('pitch'))
    if pitch_el is None: return
    pitch_el.find(t('step')).text   = pitch_token[0]
    pitch_el.find(t('octave')).text = pitch_token[1:]
    alter = pitch_el.find(t('alter'))
    if alter is not None: pitch_el.remove(alter)
    acc = note_el.find(t('accidental'))
    if acc is not None: note_el.remove(acc)

def make_edited_xml(xml_path, note_index, new_pitch):
    tree  = etree.parse(str(xml_path))
    root  = tree.getroot()
    ns    = root.nsmap.get(None, '')
    t     = lambda name: _xml_tag(name, ns)
    notes = root.findall(f'.//{t("note")}')
    set_note_pitch(notes[note_index], new_pitch, ns)
    return tree

def musicxml_to_midi(xml_tree, midi_path):
    root = xml_tree.getroot()
    ns   = root.nsmap.get(None, '')
    t    = lambda name: _xml_tag(name, ns)
    TPQN = 480; divisions = 1; events = []; current_time = 0
    for measure in root.findall(f'.//{t("measure")}'):
        for attr in measure.findall(t('attributes')):
            d = attr.find(t('divisions'))
            if d is not None: divisions = int(d.text)
        scale = TPQN / divisions
        for el in measure:
            ltag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
            if ltag == 'note':
                chord_el = el.find(t('chord'))
                pitch_el = el.find(t('pitch'))
                dur_el   = el.find(t('duration'))
                rest_el  = el.find(t('rest'))
                if rest_el is not None or pitch_el is None or dur_el is None:
                    if chord_el is None and dur_el is not None:
                        current_time += int(int(dur_el.text) * scale)
                    continue
                step  = pitch_el.find(t('step')).text
                octv  = int(pitch_el.find(t('octave')).text)
                alter_el = pitch_el.find(t('alter'))
                alter = int(float(alter_el.text)) if alter_el is not None else 0
                midi  = _SEMITONES[step] + 12 * (octv + 1) + alter
                dur_t = int(int(dur_el.text) * scale)
                if chord_el is None:
                    on_time = current_time
                    current_time += dur_t
                else:
                    on_time = current_time - dur_t
                events.append((on_time, 'on',  midi))
                events.append((on_time + dur_t, 'off', midi))
            elif ltag == 'backup':
                dur_el = el.find(t('duration'))
                if dur_el is not None: current_time -= int(int(dur_el.text) * scale)
            elif ltag == 'forward':
                dur_el = el.find(t('duration'))
                if dur_el is not None: current_time += int(int(dur_el.text) * scale)
    events.sort(key=lambda e: (e[0], 0 if e[1] == 'off' else 1))
    mid = mido.MidiFile(type=0); track = mido.MidiTrack(); mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
    prev_tick = 0
    for tick, kind, note in events:
        delta = max(0, tick - prev_tick); prev_tick = tick
        vel   = 64 if kind == 'on' else 0
        track.append(mido.Message('note_on', note=note, velocity=vel, time=delta))
    mid.save(str(midi_path))

def find_error_note_index(ex):
    tokens = ex['input_tokens'] if isinstance(ex['input_tokens'], list) else ex['input_tokens'].split()
    notes, _ = parse_lmx_notes(tokens, ex.get('sample_id', ''))
    return next(i for i, n in enumerate(notes) if n['pitch_token_position'] == ex['error_position'])

# ═════════════════════════════════════════════════════════════════════════════
# PITCH MODEL SETUP
# ═════════════════════════════════════════════════════════════════════════════
print('\n── Pitch model ──────────────────────────────────────────────────')

# Pitch classes
pitches = set()
for sid in (DATASET_ROOT / 'samples.train.txt').read_text().split():
    p = _lmx_path(sid)
    if p.exists():
        pitches.update(t for t in p.read_text().split() if PITCH_RE.match(t))
pitch_classes = {p: i for i, p in enumerate(sorted(pitches))}
id2pitch      = {i: p for p, i in pitch_classes.items()}
N_PITCH       = len(pitch_classes)
print(f'Pitch classes: {N_PITCH}')

# Dev JSONL
with open(PROCESSED / 'correction_dev_v1.jsonl') as f:
    dev_raw = [json.loads(l) for l in f]
print(f'Dev examples: {len(dev_raw)}')

# Build pitch CP examples
print('Building pitch CP examples...')
dev_cp = []
for ex in dev_raw:
    res = lmx_to_cp_example(ex, pitch_classes)
    if res is None: dev_cp.append(None); continue
    cp_ids, err_idx, tgt = res
    dev_cp.append({'cp_ids': cp_ids, 'error_note_idx': err_idx,
                   'target_class': tgt, 'sample_id': ex['sample_id']})

# Load pretrained backbone
print('Loading backbone...')
bb_p  = MidiModernBERT()
pre   = torch.load(PRETRAINED / 'model_best.ckpt', map_location='cpu', weights_only=False)
bb_p.load_state_dict(pre['state_dict'], strict=True); del pre

# Load new joint model (Nov 3)
JOINT_NEW = ML_DIR / 'data' / 'runs' / 'm2bert_joint_20261103_154108'
joint = M2BERTJointCorrection(bb_p, N_PITCH, 28)
jckpt = torch.load(JOINT_NEW / 'best_checkpoint.pt', map_location='cpu', weights_only=False)
joint.load_state_dict(jckpt['model_state_dict'], strict=True); del jckpt
joint.to(DEVICE).eval()
for p in joint.parameters(): p.requires_grad_(False)
print('Pitch model (joint Nov-3) loaded.')

def run_pitch_inference(dev_idx):
    ex    = dev_raw[dev_idx]
    cp_ex = dev_cp[dev_idx]
    if cp_ex is None:
        raise ValueError(f'No CP example for index {dev_idx}')
    cp_t  = torch.tensor([cp_ex['cp_ids']], dtype=torch.long)
    mask  = torch.ones(1, len(cp_ex['cp_ids']), dtype=torch.long)
    idx_t = torch.tensor([cp_ex['error_note_idx']], dtype=torch.long)
    with torch.no_grad():
        cp_t, mask, idx_t = cp_t.to(DEVICE), mask.to(DEVICE), idx_t.to(DEVICE)
        logits = joint(cp_t, idx_t, mask, task='pitch').squeeze(0)
        probs  = F.softmax(logits, dim=0)
    top5_vals, top5_idx = probs.topk(5)
    return {
        'current_value': ex['replacement_token'],
        'prediction':    id2pitch[top5_idx[0].item()],
        'candidates':    [{'label': id2pitch[top5_idx[i].item()],
                           'prob':  round(top5_vals[i].item(), 4)} for i in range(5)],
        'context_notes': len(cp_ex['cp_ids']),
    }

# ═════════════════════════════════════════════════════════════════════════════
# DURATION MODEL SETUP
# ═════════════════════════════════════════════════════════════════════════════
print('\n── Duration model ───────────────────────────────────────────────')

DUR_RUN = ML_DIR / 'data' / 'runs' / 'm2bert_dur_20261103_153053'
dur_ckpt    = torch.load(DUR_RUN / 'best_checkpoint.pt', map_location='cpu', weights_only=False)
dur_lm      = dur_ckpt['dur_label_map']          # ql_str → class_id
dur_id2label = {v: k for k, v in dur_lm.items()}
N_DUR        = len(dur_lm)

bb_d  = MidiModernBERT()
bb_d.load_state_dict({k.replace('backbone.', ''): v
                      for k, v in dur_ckpt['model_state_dict'].items()
                      if k.startswith('backbone.')}, strict=False)
dur_model = M2BERTDuration(bb_d, N_DUR)
dur_model.load_state_dict(dur_ckpt['model_state_dict'], strict=True)
dur_model.to(DEVICE).eval()
for p in dur_model.parameters(): p.requires_grad_(False)
print('Duration model loaded.')

# Build duration CP examples (dev split)
print('Building duration CP examples...')
dev_sids = list(dict.fromkeys(ex['sample_id'] for ex in dev_raw))
dur_dev_cp, _, dur_dev_details = build_dur_split(dev_sids, label_map=dur_lm)

def run_dur_inference(dur_dev_idx):
    cp_ex  = dur_dev_cp[dur_dev_idx]
    detail = dur_dev_details[dur_dev_idx]
    cp_t   = torch.tensor([cp_ex['cp_ids']], dtype=torch.long)
    mask   = torch.ones(1, len(cp_ex['cp_ids']), dtype=torch.long)
    idx_t  = torch.tensor([cp_ex['error_note_idx']], dtype=torch.long)
    with torch.no_grad():
        cp_t, mask, idx_t = cp_t.to(DEVICE), mask.to(DEVICE), idx_t.to(DEVICE)
        logits = dur_model(cp_t, idx_t, mask)
        probs  = F.softmax(logits.squeeze(0), dim=0)
    top5_vals, top5_idx = probs.topk(min(5, N_DUR))
    return {
        'current_value': detail['repl_ql'],
        'prediction':    dur_id2label[top5_idx[0].item()],
        'candidates':    [{'label': dur_id2label[top5_idx[i].item()] + ' QL',
                           'prob':  round(top5_vals[i].item(), 4)} for i in range(len(top5_vals))],
        'context_notes': len(cp_ex['cp_ids']),
    }

# ═════════════════════════════════════════════════════════════════════════════
# GENERATE PITCH PREDICTION JSONs + XML for index 72
# ═════════════════════════════════════════════════════════════════════════════
print('\n── Generating pitch predictions ─────────────────────────────────')
PITCH_INDICES = [12, 72, 327]

for dev_idx in PITCH_INDICES:
    ex   = dev_raw[dev_idx]
    sid  = ex['sample_id']
    sid_flat = sid.replace('/', '_')
    out_dir  = UNIFIED_OUT / f'pitch_{dev_idx}_{sid_flat}'
    out_dir.mkdir(parents=True, exist_ok=True)

    pred = run_pitch_inference(dev_idx)
    with open(out_dir / 'prediction.json', 'w') as f:
        json.dump(pred, f, indent=2)
    print(f'  [{dev_idx}] {sid}  err={pred["current_value"]:>4s} '
          f'pred={pred["prediction"]:>4s}  '
          f'top-1 prob={pred["candidates"][0]["prob"]:.3f}  '
          f'context={pred["context_notes"]} notes')

    # Generate XML/MIDI files for index 72 (not in existing unified_joint)
    if dev_idx == 72:
        xml_src   = _xml_path(sid)
        note_idx  = find_error_note_index(ex)
        err_pitch = ex['replacement_token']
        tru_pitch = ex['target_token']
        prd_pitch = pred['prediction']

        gt_tree   = etree.parse(str(xml_src))
        gt_xml    = out_dir / 'ground_truth.musicxml'
        gt_tree.write(str(gt_xml), xml_declaration=True, encoding='UTF-8')
        musicxml_to_midi(gt_tree, out_dir / 'ground_truth.mid')

        corr_tree = make_edited_xml(xml_src, note_idx, err_pitch)
        corr_xml  = out_dir / 'corrupted.musicxml'
        corr_tree.write(str(corr_xml), xml_declaration=True, encoding='UTF-8')
        musicxml_to_midi(corr_tree, out_dir / 'corrupted.mid')

        pred_tree = make_edited_xml(xml_src, note_idx, prd_pitch)
        pred_xml  = out_dir / 'model_corrected.musicxml'
        pred_tree.write(str(pred_xml), xml_declaration=True, encoding='UTF-8')
        musicxml_to_midi(pred_tree, out_dir / 'model_corrected.mid')

        print(f'       XML/MIDI generated: err={err_pitch} truth={tru_pitch} pred={prd_pitch}')

# ═════════════════════════════════════════════════════════════════════════════
# GENERATE DURATION PREDICTION JSONs
# ═════════════════════════════════════════════════════════════════════════════
print('\n── Generating duration predictions ──────────────────────────────')
DUR_INDICES = [12, 57, 327]

for dur_dev_idx in DUR_INDICES:
    detail   = dur_dev_details[dur_dev_idx]
    sid      = detail['sample_id']
    sid_flat = sid.replace('/', '_')
    out_dir  = UNIFIED_OUT / f'dur_{dur_dev_idx}_{sid_flat}'
    out_dir.mkdir(parents=True, exist_ok=True)

    pred = run_dur_inference(dur_dev_idx)
    with open(out_dir / 'prediction.json', 'w') as f:
        json.dump(pred, f, indent=2)
    print(f'  [{dur_dev_idx}] {sid}  err={pred["current_value"]:>8s} '
          f'pred={pred["prediction"]:>8s}  '
          f'top-1 prob={pred["candidates"][0]["prob"]:.3f}  '
          f'context={pred["context_notes"]} notes')

print('\nDone.')
