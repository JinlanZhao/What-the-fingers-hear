# Voice queries and rest feedback

新增行为接入现有 `camera/voice_mvp.py`，启动方式、按住录音和按钮操作不变。
逻辑位于 `camera/voice_queries.py`，不增加第三方依赖，不修改 Max patch。

## 语音查询

继续按住 SPACE 或 RECORD 说话，松开后处理。

| 问法示例 | 语音回答 |
|---|---|
| “Which measure am I pointing to?” | “Your selected measure is 7.” |
| “Where am I?” | 同上；无选中小节时请用户先指向小节。 |
| “What instruments are available?” | 从 `data/tracks.json` 读取并朗读 25 个乐谱声部，不包含 4 个效果轨。 |
| “Which instruments can I play?” | 同上。 |

查询使用录音开始时的小节快照，沿用摄像头保留最后有效选中小节的规则。
回答后等待下一次操作，不发送播放命令、不更新播放历史。
查询发生在澄清过程中时，原澄清问题和原播放锚点继续保留；位置回答使用新的选中小节。
录音开始时停止音乐的既有行为保留。

## 无音符提示

针对语音解析出的 `play_stems` 命令，按 `tracks.json` 的 MusicXML part ID
查询 `Score-prep/Score_Bars16_4-4_144bpm.musicxml`。

- 只检查播放起始小节，默认是手指选中的小节；口令指定起点时，以指定小节为准。
- 例如指向第 1 小节后说 “play flute one”，会听到 “Flute 1: no notes in measure 1.”，即使长笛在第 3 小节进入也会提示。
- 多声部请求只列出在该小节休止的声部。
- 提示结束后，原命令的声部、起止小节、OSC 参数及历史更新规则保持不变。
- 提示期间按 STOP，仍通过原 request ID 机制取消未发送的播放请求。
- 缺失文件时提示无法判断，不把缺失数据当作休止。没有对应乐谱的效果轨不作休止判断。

此提示描述乐谱中的音符／休止，不代表从 Max 读取了实时播放状态，也不判断混响尾音。
Full Mix、实体 PLAY 和手势播放保持原有路径。

## 验证

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s camera -p test_voice_queries.py -v
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python camera/test_voice_parser.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python camera/osc_cmd.py --test
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python camera/test_controller.py
```
