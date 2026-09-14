# PASS WITH WARNINGS — Audio Stem Validation

检查对象：`Audio/STEMs` 中 29 个 WAV；所有 WAV 与 MusicXML 均以只读方式检查，检查前后 SHA-256 未改变。

## 结论

- **文件数通过**：29 个 WAV，包含 25 个 score stems 和 4 个 `OTH` effects。
- **编号通过**：采用更新后的规范，score stems 为 `01–25`，`OTH` effects 为 `26–29`；实际编号完整连续，无缺失或重复。
- **Tuba 文件名通过**：当前文件为 `17_BRS_tb.wav`。已特别检查文件名，没有执行重命名或任何 WAV 修改；旧的 `BRS_tb__18.wav` 名称不再作为本次交付要求。
- **格式、长度与同步通过**：29/29 均为完整可解码 WAV，不是 Git LFS pointer；全部为 48 kHz、24-bit PCM、Stereo、1,280,000 samples、26.666666667 秒。
- **音乐时间基准通过**：144 BPM、4/4 时每拍 20,000 samples，每小节 80,000 samples，16 小节合计 1,280,000 samples。
- **信号完整性通过**：无空文件、无损坏文件、无单轨 clipping、无 dual mono、无超过 0.001 的 DC offset。
- **25 条 score stems 求和通过**：排除 4 条 `OTH` 后，浮点求和峰值为 **−1.8651 dBFS**，0 个 samples 达到或超过 0 dBFS。防止 clipping 所需 attenuation 为 **0 dB**；以 −1 dBFS 为 ceiling 时建议的 Max global attenuation 仍为 **0 dB**。
- **MusicXML 映射通过**：25/25 score stems 可依 stem slug 对应 MusicXML 的 25 个 parts；4 条 `OTH` 均排除。完整 draft 见 `tracks.json`。

## Warnings

没有自动检测到文件结构、格式、长度、同步或信号完整性错误。状态保留为 `PASS WITH WARNINGS`，是因为音乐内容和预期 panning 仍需人工听辨，不能由技术统计完全证明。

## Level、stereo 与静音分析

- 所有 29 条音频左右声道均存在可测差异；dual mono 数量为 **0**。这证明 stereo/pan 信息已写入文件，但不能自动证明 pan 位置符合预期的管弦乐座位。
- Stereo correlation 范围约为 **−0.1894 至 0.9020**；没有接近完全相同的双声道文件。
- 最大 L/R RMS 偏差为 `25_STR_cb.wav`：右声道比左声道高 **25.56 dB**。其他较大偏差包括 Tuba +14.35 dB、Violin 1 −12.14 dB、Violoncello +10.36 dB、Trombone 1 +10.70 dB。它们表明明显 panning，位置正确性仍需听辨。
- 单轨最高峰值为 `19_PRC_bd.wav` 的约 **−2.15 dBFS**，仍未 clipping。
- 全文件 −90 dBFS 静音比例较高的 score stems 包括 Horn 4（84.97%）和 Glockenspiel（65.60%）；effects 中 Crash 为 84.19%、Riser 为 79.35%。这些可能来自正常休止或稀疏效果，不能仅凭比例判为错误，应对照乐谱试听。
- 最大测得 DC offset 约为 `0.0001364`（Bass Drum），低于脚本的 `0.001` warning threshold。

## Score stems 与 MusicXML parts

映射基于 stem slug，而不是当前错误编号。需要注意打击乐文件顺序与 MusicXML part ID 不同：

- `PRC_glk` → P18 Glockenspiel
- `PRC_sn` → P19 Snare Drum
- `PRC_bd` → P20 Bass Drum
- `BRS_tb` → P17 Tuba
- 其余木管、铜管和弦乐均按名称一一对应；详见 `tracks.json`。
- `OTH_crash`、`OTH_riser`、`OTH_room`、`OTH_stem` 不对应 MusicXML part，也没有加入 25-stem sum。

## 仍需人工确认

自动检查可以证明文件结构、长度、同步、技术格式、信号统计和名称映射，但不能证明以下音乐内容准确性：

- 每条 stem 是否确实演奏对应乐器与 MusicXML 中的正确音符、休止、节奏和奏法；
- 起音是否精确落在预期小节/拍点，尾音是否符合编曲意图；
- 左右声道偏差是否等于最终预期的 orchestral panning；
- Horn 4、Glockenspiel 和稀疏 effects 的长静音是否与作品内容一致；
- 当前 `01–29` 编号与 `17_BRS_tb.wav` 命名是否与下游 Max patch、素材清单和发布文档保持一致。

## 复现

```bash
python3 scripts/check_audio_stems.py
```

脚本当前返回 exit code `0`，状态为 `PASS WITH WARNINGS`。脚本依赖 `numpy` 与 `soundfile`。
