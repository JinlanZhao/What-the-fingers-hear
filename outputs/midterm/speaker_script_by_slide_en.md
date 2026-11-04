# Context-Aware Correction of OMR Errors for Braille Music

Jinlan Zhao · MTEC-345 Midterm Presentation

English speaking script, organized by the 11 guideline slides.
Timing includes demonstration, playback, and one brief question.
Bracketed directions are cues, not spoken text.

## Slide 1 — Project Title | 0:00–0:15

Hi, I'm Jinlan Zhao. My project is Context-Aware Correction of OMR Errors for Braille Music. I use musical context to correct note attributes and prepare cleaner scores for playback and Braille transcription.

## Slide 2 — Why this Project? | 0:15–2:00

I started this project because I want to make printed music easier to turn into usable Braille scores.

A common workflow starts with a printed score or PDF. Optical Music Recognition, or OMR, converts it into a digital format like MusicXML. That file can then support MIDI playback and Braille transcription.

The problem is that recognition errors travel through this workflow. If OMR reads a wrong pitch or misses a sharp, that mistake becomes part of the digital score. The playback changes, and the same incorrect musical information can enter the Braille version.

This connects directly to What the Fingers Hear, my larger project connecting a physical Braille score with audio playback. I want the tactile score and the audio to come from accurate musical information.

For this midterm, I focused on the correction step. I give the model a symbolic score and a known error location, and it predicts the replacement using surrounding notes.

My final-project goal is to connect OMR, error detection, and correction, then compare the resulting Braille scores. I want to see how fixing the digital score improves what reaches the musician.

## Slide 3 — Related Work | 2:00–2:45

I built my proposal around three existing projects.

First, de Reuse and Fujinaga's OMR Spellchecker uses musical context to flag suspicious symbols. It helps locate errors; my model supplies a replacement at the selected location.

Second, Mayer and colleagues' OLiMPiC project provides aligned score data and Linearized MusicXML. I use its clean scores to create controlled replacement errors with known answers.

Third, Audiveris converts score images into MusicXML. I plan to use its output for the final project's real OMR examples.

Together, they give me three parts of the workflow: score recognition, reference data, and error detection. My contribution is the correction step between detection and Braille transcription.

## Slide 4 — System Architecture | 2:45–3:30

[Follow the arrows on the architecture diagram.]

My current system starts with MusicXML, a target note, and a correction task. I parse the notes, encode their attributes, and hide the attribute I want to predict.

M2BERT reads the sequence and produces ranked candidates. I apply the selected prediction and export MusicXML, MIDI, and a prediction record.

Pitch and duration share a backbone with separate output heads. Pitch also has a context branch. Accidentals use a separately fine-tuned model.

I run this locally on my Mac with PyTorch and MPS acceleration. I use Transformers for the model, lxml for score editing, and mido for MIDI output.

## Slide 5 — Technical Approach | 3:30–5:00

I represent each note with four attributes: bar boundary, position within the bar, pitch, and duration. Each attribute gets an embedding, and I combine them into a 768-dimensional vector.

The backbone has 12 Transformer encoder layers. It uses notes before and after the target to predict the hidden attribute. The output has 52 pitch classes, 28 duration classes, or five accidental classes.

I use the synthetic OLiMPiC dataset. For pitch and duration, I selected 9,998 training excerpts, about 66.6 percent of the training split, and 499 validation excerpts. Each excerpt contains multiple notes, with one target selected for each task. Training and validation come from different scores. The accidental task uses 15,012 training examples.

I began with a small Transformer trained from scratch, then adapted pretrained M2BERT. I fine-tuned its last two layers and the task heads.

For my best pitch model, I froze the joint model and trained a small context branch using key signature, time signature, voice, and staff. That branch adjusts the original pitch scores. Freezing the backbone also let me cache its outputs and train this smaller component quickly.

## Slide 6 — Demo! | 5:00–9:00

[0:00–0:25 within this slide: open the pitch input and highlight the selected note.]

I'll start with this MusicXML file. I select the part, measure, and note index, then choose pitch correction. Here, the input note is C4.

[0:25–1:15: run pitch inference, show the corrected score, and play the same short passage before and after correction.]

The model predicts E4, which matches the reference score. Here are the candidates and the edited notation. I'll play the two versions so you can hear the change.

[Pause for playback.]

[1:15–2:10: open the duration input, run inference, inspect the output, and play it.]

Next, I choose duration correction. This note lasts three quarter-note beats. The model predicts half a beat, an eighth note, which matches the reference. I can see the new note length in the score and hear it in the MIDI output.

[Pause for playback.]

[2:10–2:45: open the saved accidental result and corrected notation.]

This saved example shows accidental correction. The input has a flat, and the model predicts a sharp. The output includes the five candidate scores and the edited score.

[2:45–3:40: show validation example 57 and the saved context-v3 candidate list.]

Here's an interesting pitch error. The reference is D4, but the model chooses E4. D4 appears third in the candidate list. This example helped me separate two questions: does the model find the right candidate, and does it put that candidate first?

[3:40–4:00: show the output directory.]

Each example produces MusicXML, MIDI, and a prediction record. I can inspect the notation, listen to the edit, and trace the model used.

[Video fallback line: “I'll show the recorded run of the same workflow.”]

## Slide 7 — Results: Quantitative | 9:00–9:45

My best Transformer trained from scratch reached 16.6 percent pitch accuracy. With M2BERT and the context branch, I reached 64.9 percent—324 correct predictions out of 499. The correct pitch appears in the top five about 88 percent of the time.

The joint model reached 87.8 percent duration accuracy. The accidental model reached 87.7 percent on its separate set of 1,437 validation examples.

Music pretraining gave me the largest improvement. The context branch improved pitch further. Adding more training examples and unfreezing the backbone reduced accuracy, so I kept the earlier checkpoint.

## Slide 8 — Results: Qualitative | 9:45–10:15

In these examples, I can hear the corrected pitch and see the eighth note restored in the score. Comparing the edited file with the reference makes each change easy to inspect.

The D4-to-E4 error shows a different outcome: the correct answer is among the candidates, but the first choice changes the intended pitch. That's why I display both the prediction and its alternatives.

## Slide 9 — Challenges and Solutions | 10:15–10:40

I solved three practical problems. Low pitch accuracy led me to pretrained M2BERT. A duration export bug led me to use quarter-note units consistently. For rare accidentals, I added 400 examples of double-flats and double-sharps. Macro F1 rose from 0.512 to 0.542, while overall accuracy fell slightly. That taught me to track both metrics.

## Slide 10 — Accomplishments | 10:40–11:00

I completed the midterm workflow: create correction examples, train and compare models, apply predictions, and export musical output. I also expanded from pitch correction to duration and accidentals.

My main lesson was to improve representation and training strategy before increasing model size. Next comes detector integration and Braille evaluation.

## Slide 11 — Future Work | 11:00–12:00

[Show the final-project pipeline: Score image → Audiveris → error detector → correction → MusicXML → MIDI / Braille.]

For the final project, I'll process score images with Audiveris and connect an existing error detector to my correction model.

Then I'll translate three versions through the same Braille workflow: the reference score, raw OMR output, and corrected output. I'll compare which errors carry into Braille, which corrections fix them, and where new errors appear.

I'll evaluate detection, correction, and the resulting Braille notation. That connects my model results to the original goal: more reliable score preparation for Braille music.

Thank you. I'll take a quick question.

[Reserve the remaining time for one brief question.]

---

## Source and production notes — not spoken

### Original project direction

- Course proposal: `/Users/zhaojinlan/Documents/GitHub/MTEC-345-001_Assignments/Jinlan Zhao/MidtermProject/Proposal/README.md`.
- Course status report: `/Users/zhaojinlan/Documents/GitHub/MTEC-345-001_Assignments/Jinlan Zhao/MidtermProject/StatusReport/README.md`.
- Current experiment results: `ml/correction_all_experiments.md` and the retained run predictions/configurations.

The proposal's final goal is OMR → detection → correction → MusicXML/MIDI → Braille, with downstream comparison of reference, raw OMR, and corrected scores. The revised motivation and final slide follow that goal.

### Slide references

- Slide 3, OMR Spellchecker: de Reuse & Fujinaga (2022), https://zenodo.org/records/7316782.
- Slide 3, OLiMPiC / LMX: Mayer et al. (2024), https://arxiv.org/abs/2403.13763.
- Slide 3, Audiveris MusicXML export: https://audiveris.github.io/audiveris/_pages/tutorials/quick/export/.
- Slide 5, M2BERT: Wang & Su (2025), *Improving BERT for Symbolic Music Understanding Using Token Denoising and Pianoroll Prediction*, https://arxiv.org/abs/2507.04776; official implementation https://github.com/york135/M2BERT.

### Slide changes to match this script

- Slide 1: restore the proposal title, *Context-Aware Correction of OMR Errors for Braille Music*. M2BERT can appear as a subtitle.
- Slide 2: show the path from OMR errors to playback and Braille, with the correction stage highlighted.
- Slide 3: use the proposal's three references: Spellchecker, OLiMPiC, and Audiveris. Cite M2BERT on Slide 5.
- Slide 10: list completed midterm work and final-project tasks under separate labels.
- Slide 11: show the full detect-and-correct pipeline and the three-way Braille comparison.

### Demonstration preparation

- Use `ml/demo/inference_demo/pitch_test_input.musicxml` and `dur_test_input.musicxml` for the pitch/duration interface.
- Use the saved accidental result at `ml/demo/inference_demo/acc_output_+1/`.
- Use validation index 57 from `ml/data/runs/m2bert_ctx_pitch_v3_20261102_184759/pitch_dev_predictions.json` for the candidate comparison; reference D4 is third among E4, C4, D4.
- Label demo checkpoints individually. The existing main notebook's pitch/duration interface uses the joint checkpoint; Slide 7 reports the best adopted model for each task.
- Record the demonstrated sequence before class for the video backup. Keep saved input/output files open.
- Rehearse at approximately 120–130 words per minute, with extra pauses on the motivation and architecture slides. The four-minute demo includes inspection, file switching, and playback.
