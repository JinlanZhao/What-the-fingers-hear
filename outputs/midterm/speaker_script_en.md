# Musical Score Correction with M2BERT

Jinlan Zhao · MTEC-345 Midterm Presentation

Timing: 12 minutes, including live operation, playback, and a brief question.
Read the paragraphs aloud. Bracketed text is a presentation cue.
The five sections follow Part C of the course assignment.

## 1. Introduction — 2 minutes

[Show the title, your name, and a score excerpt with one highlighted note.]

Hi, I'm Jinlan Zhao. My project is Musical Score Correction with M2BERT. I use machine learning to predict the pitch, duration, or accidental of a selected note from the music around it.

I started with a practical problem: when printed music is converted into a digital score, recognition errors can change what we hear. A wrong pitch changes a melody. A wrong duration changes its timing. A missing sharp or flat changes the harmony.

I want to make those errors easier to correct for musicians working with digitized scores.

This also connects to my larger project, What the Fingers Hear, which connects Braille music with audio playback. That project depends on accurate digital music. I want to improve the score before it becomes playback or Braille notation.

What interests me is that musicians use context when they read. If I hear a questionable note, I listen to the phrase around it. I wanted to explore how a model could use that same surrounding information.

For this midterm, I built a workflow that takes a MusicXML file, predicts a replacement for a selected note attribute, and exports the edited score and MIDI. I'll show how I represent the music, how I trained the model, and what I learned from the results.

## 2. Technical Approach — 3 minutes

[Show the diagram: MusicXML + target note + task → note encoding → M2BERT → prediction → edited MusicXML + MIDI. Show the context branch beside the pitch head.]

I start with a MusicXML file and choose a note and a task: pitch, duration, or accidental correction. My parser turns the score into a sequence of notes. I hide the target attribute, pass the sequence through the model, and write the prediction back into the score.

I represent each note with four attributes: whether it starts a new bar, its position within the bar, its pitch, and its duration. This is called a compound token.

For example, a quarter-note C4 at the start of a bar becomes four numerical IDs. Each attribute gets its own learned vector. I combine those vectors into a 768-dimensional representation for the model.

I use M2BERT, a pretrained music model with a 12-layer ModernBERT encoder. It reads context on both sides of the target note. I chose it because its music pretraining gave me a stronger starting point than training a small Transformer from scratch.

The output depends on the task: 52 pitch classes, 28 duration classes, or five accidental classes. Pitch means the note letter and octave; accidentals have their own model.

[Show the dataset split and selected subset.]

I use OLiMPiC's synthetic dataset, which contains 17,945 score excerpts across training, validation, and test splits. For pitch and duration, I use 9,998 training excerpts—about two-thirds of the training split—and 499 validation excerpts. Training and validation contain different scores. I select one target note per excerpt. For accidentals, I use 15,012 training examples.

I first fine-tuned the last two encoder layers and the output heads. Then I froze the joint model and trained a small pitch context branch using key signature, time signature, voice, and staff. Its scores are added to the original pitch scores.

That was my main trade-off: keep the learned backbone stable and adapt a smaller component. The context branch has about 227,000 trainable parameters. I trained it with Adam, a batch size of 64, and a learning rate of 0.0005. Its best checkpoint came at epoch two.

## 3. Live Demonstration — 4 minutes

[Before presenting: load the model; open the pitch and duration demo inputs, their saved outputs, and the accidental result. Prepare a short screen recording of the same sequence as the video backup. Keep the existing MusicXML, MIDI, and prediction JSON files available as an additional fallback.]

[0:00–0:25 — Show the input score and target locator.]

I'll start with this MusicXML file. I use the part, measure, and note index to select the target. Here, the selected note is C4, and I choose pitch correction.

[0:25–1:15 — Run the pitch inference interface. Show the prediction and corrected score. Play the same short passage before and after correction.]

I run the model, and it predicts E4. The original reference score also has E4. Here are the ranked candidates, and here is the exported score with the change applied. I'll play the two versions so you can hear the difference.

[Allow time for playback.]

[1:15–2:10 — Open the duration input, run duration correction, and compare the output with the reference.]

For the second example, I change the task to duration. The selected note lasts three quarter-note beats. The model predicts half a beat, which is an eighth note and matches the reference. I export that change to MusicXML and MIDI as well.

This was also a useful debugging lesson. My duration labels already used quarter-note units. Removing an extra conversion fixed the exported timing.

[Allow time to inspect the notation and play the passage.]

[2:10–2:45 — Open the saved accidental inference result and its corrected MusicXML.]

This example shows accidental correction. The input has a flat, and the model predicts a sharp. I can inspect the five candidate scores and open the edited score and MIDI.

[2:45–3:40 — Show pitch validation example 57 and its saved candidate list. Compare the reference D4 with the predicted E4.]

I also want to show a pitch error. In this excerpt, the reference is D4, while the model chooses E4. D4 appears third in its candidate list. That example helped me distinguish finding a useful candidate from ranking it first. It is also why I keep the candidate list visible alongside the prediction.

[3:40–4:00 — Show the output files.]

Each correction produces an edited MusicXML file, a MIDI file, and a prediction record. I can inspect the notation, listen to the result, and trace which model produced it.

[If switching to backup video: “I'll show the recorded run of the same workflow.”]

## 4. Results and Learning — 2 minutes

[Show the results table, a training curve, and the D4/E4 example.]

I compared the models on the same 499 validation examples for pitch and duration.

My best Transformer trained from scratch reached 16.6 percent pitch accuracy. With M2BERT and the context branch, I reached 64.9 percent: 324 correct predictions out of 499. The correct pitch appears in the top five candidates about 88 percent of the time.

The joint model reached 87.8 percent duration accuracy. The accidental model reached 87.7 percent on its separate set of 1,437 validation examples.

In the demo, I can hear the pitch change and see the corrected rhythm in the notation. Duration was the strongest task by top-one accuracy; pitch still produces competing candidates, like the D4 and E4 example.

Three experiments shaped my decisions. Music pretraining gave me the largest improvement. Adding explicit context improved pitch accuracy further. Expanding the training examples and unfreezing more of the backbone reduced pitch accuracy, even while training loss kept falling. I kept the earlier model.

I also learned to look beyond overall accuracy. Natural notes dominate the accidental data. After adding examples of double-flats and double-sharps, accuracy fell slightly, but macro F1 rose from 0.512 to 0.542. That metric gives each class equal weight, so it helped me compare performance across common and rare labels.

## 5. Reflection and Next Steps — 1 minute

[Show three next steps: unify the interface; evaluate OMR-produced scores; connect to score preparation.]

My biggest insight is that representation and training strategy shaped the results more than simply increasing model size.

For the final project, I want to bring the adopted models into one correction interface, evaluate scores produced by OMR software, and connect the output to the score-preparation workflow for What the Fingers Hear.

The question I want to explore next is how to present the candidates so a musician can review a correction quickly.

Thank you. I'll take a quick question.

[Reserve the remaining time for one brief question.]

---

## Slide and rehearsal reference — not spoken

| Item | Value |
|---|---:|
| Full dataset: train / validation / test | 15,014 / 1,438 / 1,493 excerpts |
| Pitch and duration training subset | 9,998 / 15,014 = 66.6% |
| Pitch and duration validation subset | 499 / 1,438 = 34.7% |
| Best custom Transformer pitch top-1 | 83 / 499 = 16.63% |
| Adopted context v3 pitch top-1 | 324 / 499 = 64.93% |
| Adopted context v3 pitch top-5 | 439 / 499 = 87.98% |
| Adopted joint duration top-1 | 438 / 499 = 87.78% |
| Adopted accidental v2 accuracy | 1,260 / 1,437 = 87.68% |
| Adopted accidental v2 macro F1, five classes | 0.542 |

The accidental task uses a separate validation set; its accuracy has a different denominator. All reported accuracy figures above are validation results.

The joint model shares its backbone between pitch and duration. Accidental correction uses a separately fine-tuned checkpoint. Context v3 adds a residual branch to the frozen joint pitch model.

### Demo sources

- Pitch input and saved output: `ml/demo/inference_demo/pitch_test_input.musicxml` and `pitch_output/`.
- Duration input and saved output: `ml/demo/inference_demo/dur_test_input.musicxml` and `dur_output/`.
- Accidental input and saved output: `ml/demo/inference_demo/acc_test_+1.musicxml` and `acc_output_+1/`.
- Failure example: validation index 57 in `ml/data/runs/m2bert_ctx_pitch_v3_20261102_184759/pitch_dev_predictions.json`; reference D4, prediction E4, reference ranked third.
- Saved notation and MIDI for that failure: `ml/demo/unified_joint/pitch_57_samples_5187781_p3-s3/`.

The main notebook currently contains the older joint pitch/duration inference interface. Its demo demonstrates that checkpoint's behavior. Saved pitch and accidental demo outputs also include later experimental checkpoints. Label each demonstrated checkpoint separately from the best-model validation metrics.

### Preparation actions

- Make a slide with the architecture diagram described in Section 2, including the user's note/task selection and the output files.
- Put the metric table and a training/validation curve on the results slides.
- Load and rehearse the exact pitch and duration inference cells before class.
- Prepare the backup screen recording; the repository already contains saved input/output examples.
- Rehearse with playback and a timer; keep the five section boundaries at 2:00, 5:00, 9:00, 11:00, and 12:00.

### Likely questions — optional answers

**How much of the dataset did you use?**

For pitch and duration, I used 9,998 of the 15,014 training excerpts, about 66.6 percent. Accidentals use nearly the full training split.

**How many layers did you train?**

The encoder has 12 layers. During joint fine-tuning, I trained the last two layers and the output heads. For my best pitch refinement, I froze that model and trained only the context branch.

**How does the model represent a note?**

I encode four attributes: bar boundary, position, pitch, and duration. Their embeddings are combined into a 768-dimensional vector, which the Transformer updates using the surrounding notes.

**How does it choose which note to correct?**

I select the part, measure, note index, and correction task in the interface. The model predicts the selected attribute at that location.

**Why did you keep the accidental model with slightly lower accuracy?**

I wanted to balance the five classes. Its macro F1 increased from 0.512 to 0.542 after adding rare-class examples, while accuracy moved from 88.3 to 87.7 percent.

**What hardware did you use?**

I ran the experiments locally using PyTorch's MPS backend on my Mac. The model has roughly 61 million parameters. Caching the frozen backbone's outputs let me train the context branch in about a second, after loading the cache.
