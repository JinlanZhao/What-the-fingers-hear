# Midterm Slide Content Plan

11 slides, following the supplied presentation guideline in its original order.
Total: 12 minutes, including four minutes of demonstration.
Slide copy is in English; production notes are in Chinese.

| Slide | Guideline section | Duration | Timeline |
|---|---|---|---|
| 1 | Project Title | 0:15 | 0:00–0:15 |
| 2 | Why this Project? | 1:45 | 0:15–2:00 |
| 3 | Related Work | 0:45 | 2:00–2:45 |
| 4 | System Architecture | 0:45 | 2:45–3:30 |
| 5 | Technical Approach | 1:30 | 3:30–5:00 |
| 6 | Demo! | 4:00 | 5:00–9:00 |
| 7 | Results — Quantitative | 0:45 | 9:00–9:45 |
| 8 | Results — Qualitative | 0:30 | 9:45–10:15 |
| 9 | Challenges and Solutions | 0:25 | 10:15–10:40 |
| 10 | Accomplishments | 0:20 | 10:40–11:00 |
| 11 | Future Work | 1:00 | 11:00–12:00 |

The timing retains the earlier assignment's 2-minute introduction, 3-minute technical approach, 4-minute demo, 2-minute results/learning, and 1-minute reflection/Q&A.

## 1. Project Title

**Slide copy**

Musical Score Correction with M2BERT

Predicting pitch, duration, and accidentals from musical context

Jinlan Zhao · MTEC-345
[Presentation date]

**画面**：一小段乐谱，突出一个待纠正音符；日期按实际课程 section 填入。

**口头重点**：一句话说明项目，把问题和动机留到下一页。

## 2. Why this Project?

**Slide copy**

- Recognition errors change melody, rhythm, and harmony.
- Manual correction takes time.
- I use musical context to suggest note corrections.
- Accurate scores support playback and Braille preparation.

**画面**：上方用同一小段乐谱标出 wrong pitch / wrong duration / wrong accidental。下方画目标流程：digitized score → correction → playback / Braille preparation。Braille 连接标注为应用目标。

**口头重点**：说明音乐问题、面向需要编辑数字乐谱的音乐人、个人动机，以及与 What the Fingers Hear 的关系。用原演讲稿 Introduction 的主体。

## 3. Related Work

**Slide copy**

| Related work | Contribution | Task scope | My connection |
|---|---|---|---|
| OMR Spellchecker — de Reuse & Fujinaga, 2022 | Flags musically unlikely symbols | Error detection; users review flagged locations | I predict a replacement at a selected note |
| M2BERT / MoEmb — Wang et al., 2026 | Learns contextual representations of symbolic music | Motif analysis; correction requires task-specific heads | I adapt the backbone for note correction |

**画面**：两张并排卡片；每项保留任务、贡献、适用边界、与本项目关系。文献全名放页脚或演讲备注。

**口头重点**：第一项解释音乐上下文为什么适合帮助查错；第二项解释预训练音乐表示的来源和用途。两项共同定位本项目：context-based correction of a selected note attribute。

**Sources**

- de Reuse & Fujinaga, *A Transformer-Based “Spellchecker” for Detecting Errors in OMR Output*, ISMIR 2022: https://zenodo.org/records/7316782
- Wang, Lin & Su, *Learning Motif-centric Representations for Motive Discovery and Structure Similarity in Symbolic Music Data*, official implementation: https://github.com/york135/MoEmb

## 4. System Architecture

**Slide copy / diagram labels**

MusicXML + target note + correction task
→ Parse notes
→ Encode note attributes
→ M2BERT + task head
→ Ranked candidates
→ Corrected MusicXML + MIDI

Under the model node:

- Pitch: joint backbone + pitch head + context branch
- Duration: joint backbone + duration head
- Accidentals: separate fine-tuned model

Tools: Python · PyTorch · Transformers · lxml · mido
Hardware: Mac · MPS acceleration

**画面**：主区域只放数据流图。用箭头标出用户选择目标的位置。工具与硬件放底部一行。

**口头重点**：沿箭头讲输入、处理、输出；说明 pitch/duration 共享骨干，accidental 使用单独 checkpoint。图中三个任务是调用路径。

## 5. Technical Approach

**Slide copy**

**Model**
- 12-layer bidirectional Transformer
- 768-dimensional hidden states
- Pitch / duration / accidental: 52 / 28 / 5 classes

**Data**
- OLiMPiC synthetic: 17,945 excerpts
- Pitch & duration: 9,998 train / 499 validation
- 66.6% of the training split
- Accidentals: 15,012 train / 1,437 validation

**Features**
- Per note: bar boundary, position, pitch, duration
- Pitch context: key, time signature, voice, staff

**Training → inference**
- Fine-tune last 2 encoder layers + task heads
- Freeze joint model; train pitch context branch
- Mask target attribute → predict class → edit score

**画面**：四个小区块；特征区增加一个示例：quarter-note C4 → [bar, position, pitch, duration]。数字编码或 embedding 的详细讲解放备注或问答。

**口头重点**：回答 input/output、12 层、dataset 用量、音符表示和训练方式。强调 9,998 的单位是片段，每个片段为每项任务选择一个目标音符。将优化器、learning rate、epoch 日志放演讲备注。

**Dataset reference**：Mayer et al., *Practical End-to-End Optical Music Recognition for Pianoform Music*, 2024: https://arxiv.org/abs/2403.13763

## 6. Demo!

**Slide copy**

Select → Predict → Listen

1. Pitch: C4 → E4
2. Duration: 3 beats → 1/2 beat
3. Accidental: flat → sharp
4. Candidate comparison: reference D4, prediction E4

**画面**：大面积演示窗口或视频，保留目标音符高亮；底部显示 input → prediction → output。

**四分钟分配**

- 0:00–1:15：选定音符，运行音高推理，播放前后对比。
- 1:15–2:10：运行时值纠错，展示八分音符输出并播放。
- 2:10–2:45：打开保存的升降号推理结果。
- 2:45–3:40：展示 D4/E4 案例及候选列表。
- 3:40–4:00：展示 MusicXML、MIDI、prediction JSON。

**准备**：提前加载模型、打开文件、录制相同流程的视频备份。现场演示注明所用 checkpoint；最佳模型的整体验证集指标集中放第 7 页。

## 7. Results — Quantitative

**Slide copy**

| Task / model | Validation top-1 | Evaluation size |
|---|---:|---:|
| Pitch — custom Transformer | 16.63% | 499 |
| Pitch — M2BERT + context v3 | 64.93% | 499 |
| Duration — joint model | 87.78% | 499 |
| Accidentals — v2 | 87.68% | 1,437 |

Pitch top-5: 87.98%

**画面**：表格旁放音高实验进展图：16.63% custom → 61.32% initial M2BERT → 62.12% joint → 64.93% joint + context。后续版本承接各自训练设置，这张图表达实验进展。所有指标注明 Validation。

**口头重点**：预训练带来最大提升，上下文分支进一步提升音高；时值和升降号准确率约 88%。不要把不同任务、不同分母连成一条性能曲线。

## 8. Results — Qualitative

**Slide copy**

| Example | Reference | Prediction | Observation |
|---|---|---|---|
| Pitch | E4 | E4 | Restores the reference pitch |
| Duration | Eighth note | Eighth note | Restores the reference note length |
| Pitch candidate ranking | D4 | E4; D4 ranked third | Useful candidate, wrong first choice |

**画面**：每例用目标音符的局部乐谱截图；至少展示一组 corrupted / reference / corrected 对照。第三例旁显示前三个候选 E4 / C4 / D4。

**口头重点**：直接描述结果的声音、记谱变化和错误形态；第 6 页演示操作，第 8 页解释观察。

## 9. Challenges and Solutions

**Slide copy**

| Challenge | My solution | Outcome |
|---|---|---|
| Low pitch accuracy from scratch | Adapt pretrained M2BERT | Initial pitch accuracy reached 61.32% |
| Incorrect exported duration | Use quarter-note units consistently | 1/2 QL exports as an eighth note |
| Rare accidental classes | Add 400 double-accidental examples | Macro F1: 0.512 → 0.542 |

**画面**：三行 problem → action → result，最多各一句。

**口头重点**：三项具体问题与处理方式。rare-class augmentation 改善类别平衡；accuracy 变化已在讲稿中保留，不把该结果描述为所有类别问题已解决。

## 10. Accomplishments

**Slide copy**

**Completed**
- Pitch, duration, and accidental correction models
- MusicXML → inference → MusicXML / MIDI workflow
- Baseline comparisons and experiment records

**In progress**
- One interface for the adopted checkpoints
- OMR-produced score evaluation

**What I learned**
- Musical representation and selective fine-tuning shaped my results.

**画面**：Completed 与 In progress 两列，下方一句学习收获。

**口头重点**：明确完成项与仍在推进的项，满足指南要求。完成目标是数据输入、ML 推理、可检查和播放的音乐输出；这些为后续数字乐谱准备提供基础。

## 11. Future Work

**Slide copy**

1. Bring the adopted models into one interface.
2. Evaluate corrections on OMR-produced scores.
3. Connect correction to playback and Braille preparation.

How can I help a musician review a correction quickly?

Questions?

**画面**：三步路线图，底部保留问题和 Q&A。

**口头重点**：明确继续推进的方向，连接 final project；约 40–45 秒讲述，余下时间留一个简短问题。

## Guideline coverage

- Slide 1: title, name, class, presentation date.
- Slide 2: musical problem, project context, motivation, relevance, goal.
- Slide 3: two related projects, relationship, strengths, task boundaries, relevance.
- Slide 4: implementation blueprint, software/hardware, data-flow visual, user input.
- Slide 5: ML model, dataset, features, training and inference.
- Slide 6: functioning demo, musical input/output, video backup preparation.
- Slide 7: metrics and graph.
- Slide 8: example outputs and observations.
- Slide 9: three problems and solutions.
- Slide 10: completed/in-progress work, learning, achieved goals, value.
- Slide 11: continuation plan, final-project connection, brief Q&A.
