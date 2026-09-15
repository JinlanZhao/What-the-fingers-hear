# Touch-Anchored, Multimodal Playback for Braille Sheet Music

*A feasibility prototype proposal*

Jinlan Zhao · Berklee College of Music

## 1. Project Concept and Definition

This project is an audio navigation and playback system for blind musicians who read embossed braille music. It allows a musician to touch a location on a physical braille score and hear the music from that location through either an immediate hand gesture or a spoken request for selected instrumental stems. The same hand movement already used to read the score therefore also becomes the input for selecting a playback position.

The score itself remains a normal, removable embossed page and contains no embedded electronics. An infrared-sensitive camera mounted above the page tracks a small active infrared marker worn on the upper surface of the reading finger and observes a separate command-hand gesture area. The marker does not cover the fingertip or interfere with contact between the fingerpad and the braille dots. A fixed frame and visual registration markers define the page coordinate system. Because the camera follows the active marker rather than attempting to recognize the braille symbols, temporary occlusion of the score by the hand does not prevent position tracking.

Touch selects the position, while an explicit gesture or voice request starts an action. Touch alone never starts audio. For direct point-and-play, a simple gesture from the command hand immediately plays all stems from the current stable touched measure, without waiting for speech recognition. For custom stem playback, the beginning of speech freezes the stable finger position immediately before voice onset; the spoken request then specifies one or more instruments and, optionally, the number of measures. The form of the command selects the interaction path, so the user does not need to enter a separate mode.

The prototype is prepared for one selected piece. Its digital score, embossed braille score, page layout, instrumental audio stems, and measure boundaries are aligned in advance. It is therefore a pre-registered interactive score, not a real-time braille optical recognition system and not a general score-following system for arbitrary pages.

The initial scope is a reliable solo-user prototype that demonstrates:

- touch-based selection of a measure on a physical braille score;
- low-latency, gesture-triggered playback from the selected measure;
- voice-defined playback of one or more selected instrumental stems;
- multitrack playback controls such as play, stop, solo, mute, and playback of a specified number of measures;
- personalized recognition of continuous reading, intentional rereading, navigation, and possible struggle from recent finger movement;
- context-aware audio assistance that can be offered without allowing touch or an ML prediction to trigger playback automatically; playback still requires an explicit gesture or validated voice request.

## 2. Prior / Related Work

Research has shown that camera-based tracking can capture finger movement during tactile reading. Breidegard developed a system using two cameras and a microphone to register finger movement and reading-aloud behavior during braille and tactile-picture reading [1]. Aranyanak and Reilly later demonstrated a Wii Remote-based system for tracking braille readers on both refreshable braille displays and embossed paper [2]. These systems establish that a camera can track reading motion without modifying every braille cell or measure.

Braille reading is not a uniform left-to-right movement. Reading speed, hand use, reversals, pauses, and repeated exploration vary across readers and across passages. Ulusoy and Sipahi evaluated an adaptive algorithm based on braille-like finger movement and found that accommodating reversal behavior can improve interaction [3]. TouchScope also reviews multiple approaches to finger tracking and emphasizes the variability introduced by active hand movement in tactile tasks [4]. These variations make it difficult to infer difficulty through fixed rules such as “a two-second pause means struggle.” They instead motivate a personalized temporal model that interprets a sequence of movements relative to each reader’s own normal reading behavior.

The proposed active IR marker is conceptually closest to marker-based camera tracking: the camera follows a deliberately identifiable point on the reading finger instead of trying to infer the relevant finger from an unmarked hand image. This preserves the key advantage previously sought through page-embedded IR receivers, namely identifying one designated reading finger, while eliminating the need for dozens of phototransistors, multiplexers, and wires beneath the tactile page.

The score-preparation workflow draws on existing digital-to-braille music transcription. Goto et al. demonstrated transcription from MusicXML into braille music notation [5], and the GOODFEEL suite provides a commercial workflow for producing braille music from digital notation [6]. In this project, a common symbolic source is used to produce both the braille page and the rendered audio stems, keeping measure identities consistent across tactile and audio representations.

Music synchronization and score-following work, including Dixon’s online time-warping approach [7] and the chroma-onset synchronization method of Ewert, Müller, and Grosche [8], is relevant when aligning an independent expressive recording to a symbolic score. However, the first prototype does not require automatic score following. It uses stems rendered from the same symbolic score as the braille transcription, so measure boundaries can be exported directly. Automatic audio-score alignment remains an optional extension for supporting commercial or live recordings.

The contribution of this project is the complete interaction design: a removable physical braille page, an active marker that identifies the intended reading finger, camera-to-page registration, a personalized temporal model of tactile reading behavior, explicit and user-controlled assistance, dual low-latency gesture and voice-customization paths, a voice-onset position snapshot, and programmable multitrack playback in Max/MSP. The central ML contribution is not finger localization. It is the attempt to recognize when the reader’s normal tactile reading flow has changed, identify the local passage associated with that change, and offer relevant audio assistance without interrupting ordinary reading or starting playback without consent.

## 3. System Architecture

The system contains three preparation stages and eleven runtime layers.

### Offline preparation

| Stage | Input | Output |
|---|---|---|
| Score preparation | MusicXML or another symbolic score representation | Embossable braille score, MIDI, tempo map, and synchronized instrumental stems |
| Page registration | Physical page layout | A two-dimensional map of page regions to measure identifiers |
| Music alignment | Measure boundaries and rendered stems | A bar-to-time table containing the start and end of every playable measure |

### Runtime system

| Layer | Input | Output | Purpose |
|---|---|---|---|
| 1. Page registration | Frame markers in the camera image | Page coordinate system | Corrects camera angle, translation, and perspective |
| 2. IR marker detection | Camera frames | Marker coordinates and visibility | Tracks only the marked reading finger |
| 3. Contact-point estimation | Marker position, orientation, and user calibration | Estimated fingertip contact point | Corrects the offset between the marker and fingerpad |
| 4. Geometric measure lookup | Estimated contact point and page map | Current measure region and boundary distance | Converts page position into a measure without requiring ML |
| 5. Reading-behavior inference | Recent finger trajectory and personalized baseline | Reading state, local difficulty region, and confidence | Distinguishes continuous reading, rereading, navigation, and possible struggle |
| 6. Assistance policy | Reading state, confidence, prompt history, and user settings | Optional offer of audio assistance | Prevents low-confidence or repetitive interruptions |
| 7. Gesture-triggered direct playback | Command-hand gesture and current stable measure | Validated all-stem playback action | Provides low-latency point-and-play without speech recognition |
| 8. Voice-onset anchoring | Rolling position buffer and voice activity detection | Frozen measure for the current command | Uses the stable position immediately before speech begins |
| 9. Speech and intent processing | Spoken stem request and current score metadata | Schema-validated track list and duration | Converts speech into custom multistem playback |
| 10. Max/MSP playback | Validated action and bar-to-time table | Multitrack audio output | Seeks, plays, stops, solos, mutes, and preserves reverb tails |
| 11. Interaction logging | Reading-state output, prompts, gestures, voice commands, and corrections | Labeled trials and evaluation records | Supports evaluation and bounded personalization |

Python runs the sensing, registration, ML, gesture, and voice-control pipeline. It sends only validated actions to Max/MSP over OSC. Typical messages are:

```text
/play_all 18 4
/play_stems 18 4 fl1 vln1 vc
```

The first command immediately plays all stems from Bar 18 through Bar 21. The second plays only flute 1, violin 1, and cello over the same range. Separating sensing from playback allows the camera system and Max patch to be tested independently.

## 4. Hardware

### Physical score and registration frame

The musician reads a standard embossed braille music page. The page is inserted into a rigid, repeatable frame so that it cannot drift during reading. Four visual fiducial markers are placed on the frame rather than on the tactile reading area. These markers allow the camera image to be transformed into stable page coordinates through homography [9]. The page can be removed or replaced without modifying the braille surface.

### Overhead IR-sensitive camera

One fixed overhead camera views the complete page, its registration frame, and a defined command-hand gesture area. The camera must either omit the normal IR-cut filter or provide sufficient sensitivity at the marker wavelength. Resolution, field of view, exposure control, and mounting height must be selected so that the finger marker remains separable across the entire page while the command hand remains visible enough for gesture recognition.

The camera does not perform braille OCR. It detects the frame markers and the active IR marker, while a hand-tracking model recognizes a small set of explicit gestures in the command area; all musical content is supplied through the pre-registered page map.

### Wearable active IR marker

The marker is mounted on the nail or upper surface of the distal finger segment, with the light directed toward the overhead camera. The fingertip and fingerpad remain uncovered.

The first prototype uses one IR LED to test visibility, comfort, and position accuracy. If finger rotation creates excessive marker-to-contact error, the developed version uses two spatially separated IR points. Their orientation provides an estimate of finger direction and allows the system to project from the marker toward the fingertip. The two points may use different brightness levels or temporal patterns so their order can be distinguished.

The marker is self-powered by a small battery and does not require a cable to the computer. It must be lightweight, must not catch on the page, and must be removable so that different mounting positions can be evaluated.

### Computer, microphone, and audio output

A laptop receives the camera stream, runs Python and Max/MSP, and connects to a microphone for custom stem requests. Headphones are preferred during early testing because they make transport and track-selection errors easier to detect without adding room noise to speech recognition.

## 5. Software

### Python, OpenCV, and MediaPipe

Python coordinates camera capture, marker detection, page registration, calibration, position buffering, reading-behavior inference, gesture recognition, speech processing, and OSC communication. OpenCV detects the frame markers, estimates the homography between camera and page coordinates, isolates the active IR point or points, and performs the geometric page-to-measure lookup. MediaPipe provides command-hand landmarks, handedness, and gesture recognition within a defined control area [12].

The system stores three score-specific files:

- `page_map.json`: measure identifiers and their two-dimensional page regions;
- `bar_times.json`: measure identifiers, start times, and end times;
- `tracks.json`: allowed track names and their corresponding Max/MSP channels.

### Gesture processing

Gesture recognition is restricted to the command hand and a defined control area so that ordinary braille-reading motion is not interpreted as a command. A direct-play gesture is accepted only after sufficient temporal stability and confidence, followed by one-shot triggering and a cooldown period. On acceptance, Python snapshots the current stable touched measure and sends an all-stem playback action directly to Max/MSP, bypassing speech recognition. Max resets all stem gains before playback so that a previous solo or mute state cannot carry into point-and-play.

The minimum prototype uses one visually distinct playback gesture rather than relying on timing-sensitive single-tap versus double-tap classification. Additional gestures for stop, pause, or confirmation are added only after their false-trigger rate has been measured.

### Voice processing

A voice activity detector identifies the beginning of speech. Because onset detection is necessarily delayed, Python maintains a rolling buffer of recent finger positions. Once speech begins, the system retrieves approximately 200–500 ms of position data immediately before onset and calculates a stable anchor from that window.

Whisper or another ASR system converts speech into text [10]. Voice is used when the musician wants custom playback of one or more named stems and, optionally, a specified number of measures; a small amount of processing latency is acceptable in this path. A prompted general-purpose language model maps the transcription into a small structured command schema. It is given only the permitted actions, measure vocabulary, and available track names. The output is validated before transmission. Unsupported, incomplete, or ambiguous commands cause the system to ask the reader to repeat or clarify.

A deterministic command parser will be implemented first as a baseline. The LLM parser is retained only if it provides a measurable improvement for natural phrasing and likely ASR errors without increasing unsafe command execution.

### Max/MSP playback engine

Max/MSP loads 29 synchronized stereo stems into reusable `stem_player` abstractions and receives OSC messages from Python. A shared signal-rate playhead drives every `play~` instance so that all stems seek and stop together. A separate stereo `sfplay~ 2` object handles full-piece playback. A `coll` or `dict` object stores the bar-to-time table, and short gain ramps are applied at transport boundaries to avoid clicks. Each stem sends dry audio and a separate signal to a shared reverb return so that bounded local playback can stop cleanly while the reverb tail continues.

Max/MSP provides:

- play from the selected measure;
- play a requested number of measures;
- stop, pause, and resume;
- solo or mute a named instrumental stem;
- reset all track states;
- reset to all stems before direct point-and-play;
- report the current playback state to Python.

The first Max prototype accepts manually entered measure numbers and track selections before it is connected to the camera, gesture, and voice layers.

## 6. Machine Learning

The central learned component interprets tactile reading behavior over time. Its purpose is to recognize when a reader is progressing continuously, deliberately rereading, navigating or repositioning, or showing a sustained pattern that may indicate difficulty with a local passage. It also estimates the measure or short measure range around which that behavior is concentrated.

This separates two technical problems. OpenCV, calibration, and the registered page map answer **where the finger is**. The ML model asks **what the recent movement pattern may mean for this particular reader**. A touched measure is therefore determined geometrically; ML is not added merely to replace a coordinate lookup that can already be solved deterministically.

The research question is whether a personalized temporal model can detect when and where audio assistance may be useful early enough to help, while maintaining a sufficiently low false-prompt rate that normal tactile reading is not interrupted.

### Input features

The model analyzes a short rolling window of normalized finger positions. Candidate features include:

- calibrated contact coordinates and the sequence of visited measures;
- velocity, acceleration, movement direction, and continuity of forward progress;
- dwell duration and local position variance;
- frequency, distance, and timing of backward movements;
- repeated visits to the same measure or small measure range;
- spatial coverage within a local passage;
- line transitions and large repositioning movements;
- each reader’s calibrated baseline speed, dwell pattern, and reversal frequency.

The musical tempo is not used as a strong prior for reading speed. Tactile reading, especially while learning unfamiliar material, does not necessarily proceed at performance tempo.

### Behavioral states and model structure

The first prototype uses four observable behavioral states:

- **Continuous reading:** relatively stable progress through the score;
- **Intentional rereading:** a purposeful return to earlier material followed by continued progress;
- **Navigation or repositioning:** a line change, broad search, or rapid movement to another area of the page;
- **Possible struggle:** sustained dwell, repeated reversals, reduced progress, or repeated exploration concentrated around a local passage.

These labels describe observable movement patterns rather than claiming direct access to the reader’s mental state. In particular, “possible struggle” remains a hypothesis that the user can accept or reject.

A rule-based temporal detector provides the baseline. It uses fixed thresholds for dwell, reversals, and repeated visits. A lightweight temporal classifier is then trained on window-level or trial-level features. Candidate models include a Random Forest or gradient-boosted classifier over sliding-window features and a Hidden Markov Model if state-transition structure proves useful. A compact model is preferred over a deep neural network because the first prototype will have limited participant-specific data and must support interpretable errors and real-time inference.

The model returns a probability distribution over behavioral states, a local measure or measure range, and confidence. A single pause or reversal is never enough to trigger assistance. “Possible struggle” must remain stable across successive windows and exceed a confidence threshold before it reaches the assistance policy.

### Assistance policy

The model never starts playback. When persistent, high-confidence possible struggle is detected, the system may ask a short question such as, “Would you like to hear Bars 18 through 20?” The musician may accept, reject, or ignore the offer. An optional user setting disables proactive offers entirely, preserving fully explicit gesture- or voice-initiated control.

The policy includes a cooldown period and suppresses repeated prompts for the same passage. Navigation, ordinary pauses, low-confidence predictions, and intentional rereading do not produce an unsolicited prompt. Explicit gesture and voice commands remain available at any time, regardless of the inferred state.

### Training and personalization

Data collection begins with examples of each participant’s normal reading, rereading, and navigation patterns. During structured trials, participants read selected passages and identify moments when they want assistance. The finger trajectory immediately preceding a genuine request for help provides candidate positive examples, while participant confirmation or rejection of system prompts provides additional labels. Brief retrospective annotation may be used to distinguish deliberate rereading from experienced difficulty.

Training and test data are separated by complete reading trials or passages rather than by adjacent video frames, which would otherwise create temporal leakage and misleadingly high accuracy. The first evaluation emphasizes within-user personalization. A generic model may be used only as an initialization and is compared with the personalized model.

User responses to assistance prompts are logged as explicit feedback. Model updates are bounded and occur only between sessions in the first prototype. The learned model is retained only if it improves over the rule-based temporal baseline without producing an unacceptable false-prompt rate.

### Evaluation measures

Evaluation reports:

- macro-averaged F1 across the four behavioral states;
- precision and recall for possible struggle;
- false assistance prompts per minute of ordinary reading;
- detection latency relative to the participant’s request for help;
- accuracy of the estimated difficulty measure or measure range;
- prompt acceptance, rejection, and ignore rates;
- improvement of the personalized model over the rule-based baseline;
- performance across passages, reading speeds, hand angles, and sessions.

MediaPipe Gesture Recognizer, Whisper, and the optional LLM intent parser are pretrained ML components, but the research contribution is the personalized temporal inference of tactile reading behavior and the design of uncertainty-aware assistance around that inference.

## 7. Interaction

### Session setup

The musician inserts the prepared braille page into the frame and puts the IR marker on the preferred reading finger. The system confirms that the page markers, finger marker, and command-hand gesture area are visible. A short calibration asks the reader to touch several known positions. Spoken and nonvisual feedback guides this process; visual alignment is never required from the user.

### Normal use

The musician reads the physical score normally. The marked reading finger supplies the playback position, while the other hand supplies an explicit command when needed. The system provides two interaction paths without requiring a separate mode switch.

For **direct point-and-play**, the reader touches the desired measure and makes one simple playback gesture with the command hand. The system snapshots the current stable measure, resets every stem gain to its default active state, and immediately begins all-stem playback from that location. This path does not use ASR or an LLM and is optimized for low latency. A separate, unambiguous gesture may provide immediate stop after it has been validated against false triggers.

For **custom stem playback**, the reader keeps the marked finger on the desired measure and speaks a request such as:

- “Play flute one, violin one, and cello.”
- “Play flute and cello for four bars.”
- “Play the strings for two bars.”

At voice onset, the system freezes the stable pre-onset position. Movement after that moment does not change the command’s starting measure. The parser validates the requested stem list and duration; Max then resets all stem gains, activates only the requested tracks, and begins bounded playback. The additional recognition latency is acceptable because this path replaces a slower manual search for several instruments.

In parallel, the temporal model monitors whether recent movement resembles continuous reading, intentional rereading, navigation, or possible struggle. These behavioral states are more directly observable than a broad “learning mode” or “performance mode,” which cannot be inferred reliably from finger motion alone.

If proactive assistance is enabled and possible struggle remains persistent and high-confidence, the system may ask whether the musician wants to hear the local passage. The prompt does not start playback. The musician must accept it through a designated gesture or voice response, or issue a separate playback command. The user can disable proactive prompts and use the system entirely through explicit commands.

### Uncertainty and correction

If marker visibility is lost or the contact point lies near a measure boundary, the system asks for confirmation before playback, for example, “Bar 18?” The reader may confirm through a designated gesture or correct it verbally. A direct spoken measure number is treated as an explicit override for the current command and is logged separately from camera-derived positions.

During ordinary reading, the system remains silent unless proactive assistance has been enabled and the persistent-struggle criteria are met. Direct point-and-play uses a brief nonverbal acknowledgement so that audio can begin without a spoken delay. The system otherwise speaks only when confirming a custom stem request, asking for clarification, or disclosing low confidence.

## 8. Music - Bar Alignment

The prototype uses a single symbolic score as the source of truth. The same MusicXML or MIDI-derived project produces:

1. the braille music transcription;
2. the printed measure identifiers used in the page map;
3. the tempo and meter map;
4. synchronized instrumental audio stems;
5. the start and end time of each measure.

This avoids unnecessary audio-score alignment errors. The bar-to-time table uses the following form:

```json
[
  {"bar": 1, "start_ms": 0, "end_ms": 3240},
  {"bar": 2, "start_ms": 3240, "end_ms": 6810},
  {"bar": 3, "start_ms": 6810, "end_ms": 10020}
]
```

All stems begin at the same zero point, use the same sample rate, and have equal duration. When Max receives a measure and optional length, it looks up the start of the first measure and the end of the final requested measure, then seeks all stems together.

The page map is registered separately. Each measure is represented by a two-dimensional region covering its actual horizontal extent, rather than by a single sensor point. Regions may have different widths. If a measure continues across a line or page break, its regions are represented explicitly.

For the first prototype, the selected piece should avoid ambiguous repeat structures, multiple endings, and page turns. If repeats are present, the playback order must be linearized and each occurrence must receive an unambiguous identifier. Supporting an independent expressive recording would require a separate offline alignment stage, such as DTW or chroma-onset synchronization [7, 8], and is outside the minimum prototype.

## 9. Material List

The following costs are preliminary estimates and must be checked against the exact camera and fabrication method selected.

| Item | Quantity | Role | Estimated cost | Notes |
|---|---:|---|---:|---|
| IR-sensitive USB camera | 1 | Overhead page, marker, and command-hand tracking | $30–$80 | Must be tested at the selected IR wavelength |
| Camera stand or rigid overhead mount | 1 | Maintains a fixed view of the page | $15–$35 | Existing stand may be reused |
| 850 nm or 940 nm IR LEDs | 2–4 | Active finger marker and spares | $3–$8 | Final wavelength chosen after camera test |
| Battery holder, small battery, switch, resistors, wire | 1 set | Powers the marker | $5–$12 | No computer cable required |
| Lightweight finger/nail mount | 1–3 prototypes | Holds the marker without covering the fingerpad | $5–$20 | 3D printed, silicone, or modified clip |
| Optional IR-pass filter | 1 | Reduces visible-light interference | $8–$25 | Added only if ambient-light testing requires it |
| Registration frame and fiducial markers | 1 | Fixes the page and defines page coordinates | $5–$20 | Foam board, acrylic, or laser-cut material |
| Embossed braille score | 1 prototype piece | Physical reading surface | Varies | Requires an embosser or external transcription service |
| Laptop | 1 | Runs Python, ML, ASR, and Max/MSP | Already owned | — |
| Microphone | 1 | Captures custom stem requests | Already owned | Built-in microphone may be sufficient |
| Headphones or speakers | 1 | Audio output | Already owned | — |
| Max/MSP | 1 license | Multitrack playback engine | Already owned / institutional access | Confirm available license |
| MediaPipe | 1 software package | Command-hand gesture recognition | Free | Runs in the Python sensing layer |
| GOODFEEL/Lime or another braille transcription workflow | 1 | Produces the embossed score | Access dependent | Confirm through disability/accessibility services |

Estimated new hardware cost: approximately **$55–$175**, excluding the laptop, software licenses, and braille embossing service. The lower end assumes an existing camera mount and a simple one-LED marker.

## 10. Prototype Step

### Step 1 — Playback and alignment without sensing

Prepare one short piece, export synchronized stems, create a manual bar-to-time table, and build a Max/MSP patch that accepts typed measure commands. Confirm shared-playhead synchronization across all stems, full-piece playback, bounded playback, stop, solo, mute, gain reset, and reverb-tail behavior before adding camera input.

### Step 2 — Camera and page-coordinate test

Mount a standard or IR-sensitive camera over a printed page mock-up. Place four fiducial markers on the frame and verify that OpenCV can maintain stable page coordinates when the camera or frame is slightly repositioned. Confirm that the same camera view also includes a comfortable command-hand gesture area.

### Step 3 — One-marker optical go/no-go test

Build a one-LED finger marker and test it on real embossed cardstock under natural reading movement. Measure detection rate across the full page, multiple finger angles, different speeds, and realistic room lighting. Do not proceed to the full system unless the marker remains visible without changing the reader’s tactile technique.

### Step 4 — Contact-point calibration

Collect trials in which the marker wearer touches known locations. Measure the error between marker location and actual fingertip contact. If a single marker cannot keep this error comfortably below typical measure-region width, prototype the two-point orientation marker.

### Step 5 — Page-to-measure map

Create region polygons for every measure on one page and implement the deterministic coordinate-to-measure baseline. Test centers, boundaries, line changes, deliberate reversals, and contact near adjacent measures.

### Step 6 — Direct gesture-triggered playback

Add MediaPipe command-hand recognition in the defined control area. Implement temporal stability, confidence, one-shot triggering, and cooldown. Connect the direct gesture to a validated `/play_all` action that snapshots the current stable measure, resets all track gains, and starts playback without ASR. Measure gesture-to-audio latency and false triggers during normal reading movement.

### Step 7 — Voice-onset anchoring and custom stem commands

Connect Python to Max/MSP by OSC using typed multistem commands first. Add the rolling position buffer and voice activity detection, confirming that the selected measure comes from the stable interval before speech and is not changed by movement during or after the request. Add Whisper only after transport is stable. Implement a deterministic parser for one or more track names and an optional duration before testing an LLM parser with schema validation.

### Step 8 — ML reading-behavior inference

Collect trial-level examples of continuous reading, intentional rereading, navigation, and participant-identified difficulty. Implement the rule-based temporal baseline, train the personalized classifier, and compare them on held-out passages. Add persistence, confidence, and cooldown requirements so that isolated pauses or reversals do not create assistance prompts.

### Step 9 — Full integration

Integrate camera tracking, geometric measure lookup, command-hand gestures, reading-behavior inference, assistance prompts, custom-stem voice recognition, structured commands, and Max/MSP playback for one complete page and one piece. Log position, inferred state, confidence, difficulty region, prompt response, recognized gesture or voice command, selected measure, playback result, and latency.

### Step 10 — Formative accessibility evaluation

After engineering safety and reliability checks, conduct a small formative evaluation with blind braille-music readers if recruitment and required research approval are available. Evaluate marker comfort, preservation of natural reading technique, command-hand comfort, gesture latency and false triggers, custom-stem voice-command usefulness, behavioral-state recognition, appropriateness of assistance timing, clarity of feedback, and failure recovery. Sighted simulation may be used for debugging but cannot substitute for this evaluation.

## 11. Goals

1. Build a working solo-user prototype that connects a physical braille music page to measure-specific audio playback.
2. Preserve an ordinary embossed reading surface with no embedded sensors, wiring, or required tactile search targets.
3. Track one designated reading finger and a separate command-hand gesture area with a single overhead IR-sensitive camera and a lightweight active marker that leaves the reading fingerpad unobstructed.
4. Convert a touched page region into a measure identifier through calibrated page geometry and disclose boundary uncertainty before executing a potentially incorrect selection.
5. Support low-latency gesture-triggered all-stem playback and voice-defined playback of one or more selected stems over an optional bounded range.
6. Implement synchronized multitrack playback in Max/MSP using a validated bar-to-time table.
7. Train a personalized temporal model to distinguish continuous reading, intentional rereading, navigation, and possible struggle, and localize the passage associated with possible difficulty.
8. Demonstrate that any retained ML model improves over a rule-based temporal baseline while maintaining a low false-prompt rate during ordinary reading.
9. Measure behavioral-state accuracy, possible-struggle precision and recall, difficulty-region accuracy, prompt acceptance, gesture-to-audio latency, custom voice-command latency, and robustness across realistic reading motions and lighting conditions.
10. Produce a modular architecture in which the physical score, page map, music alignment, gesture layer, behavioral model, assistance policy, voice layer, and playback engine can be tested separately.
11. Establish whether the system can be expanded from a one-page feasibility prototype to longer works, multiple pages, and a broader group of blind musicians.

## 12. References

[1] Breidegard, B. (2007). Computer-based automatic finger- and speech-tracking system. *Behavior Research Methods, 39*, 824–834. https://doi.org/10.3758/BF03192975

[2] Aranyanak, I., & Reilly, R. G. (2013). A system for tracking braille readers using a Wii Remote and a refreshable braille display. *Behavior Research Methods, 45*, 216–228. https://doi.org/10.3758/s13428-012-0235-8

[3] Ulusoy, M., & Sipahi, R. (2016). Experimental evaluation of a braille-reading-inspired finger motion adaptive algorithm. *PLOS ONE, 11*(2), e0148356. https://doi.org/10.1371/journal.pone.0148356

[4] Baciero, A., Perea, M., Duñabeitia, J. A., & Gómez, P. (2023). TouchScope: A passive-haptic device to investigate tactile perception using a refreshable braille display. *Journal of Cognition, 6*(1). https://doi.org/10.5334/joc.271

[5] Goto, D., Gotoh, T., Minamikawa-Tachino, R., & Tamura, N. (2007). A transcription system from MusicXML format to braille music notation. *EURASIP Journal on Advances in Signal Processing, 2007*, 042498. https://doi.org/10.1155/2007/42498

[6] Dancing Dots. GOODFEEL Braille Music Translator. https://shop.dancingdots.com/products/goodfeel-braille-music-translator

[7] Dixon, S. (2005). An on-line time warping algorithm for tracking musical performances. *Proceedings of the 19th International Joint Conference on Artificial Intelligence*. https://www.ijcai.org/Proceedings/05/Papers/post-0005.pdf

[8] Ewert, S., Müller, M., & Grosche, P. (2009). High resolution audio synchronization using chroma onset features. *Proceedings of the IEEE International Conference on Acoustics, Speech and Signal Processing*, 1869–1872. https://doi.org/10.1109/ICASSP.2009.4959972

[9] OpenCV. Basic concepts of the homography explained with code. https://docs.opencv.org/4.x/d9/dab/tutorial_homography.html

[10] Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2023). Robust speech recognition via large-scale weak supervision. *Proceedings of the 40th International Conference on Machine Learning, 202*, 28492–28518. https://proceedings.mlr.press/v202/radford23a.html

[11] Cycling ’74. `play~` reference. https://docs.cycling74.com/reference/play~

[12] Google AI Edge. Gesture recognition task guide. https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer
