# HCI Gesture Interaction Research for Blind Braille-Music Users

## Purpose

This document summarizes research relevant to designing nonvisual playback gestures for the Braille Score prototype. The goal is to define a small gesture set that blind users can learn without visual demonstration, perform reliably, and use without interfering with Braille reading.

## Research Findings

### Blind and sighted users may use gestures differently

Kane, Wobbrock, and Ladner compared touchscreen gestures created and performed by blind and sighted participants. The groups differed in gesture preferences and performance characteristics. This supports designing and testing gestures with blind users instead of adopting a gesture vocabulary based only on sighted designers' assumptions.

**Project implication:** The initial gesture set should remain provisional until it is evaluated with blind users.

### Choice-based elicitation can support unfamiliar commands

Dim et al. studied mid-air TV gestures with blind participants. In the first study, some participants had difficulty inventing gestures for unfamiliar commands. A second, choice-based elicitation study presented candidate gestures for participants to compare and select. The authors found that these choices helped participants identify suitable gestures.

**Project implication:** Testing should present a small number of verbally explainable candidates for each command while still allowing participants to suggest alternatives.

### Recognition must tolerate variation

Khanna et al. compared free-space gesture trajectories produced by blind and sighted users. Blind participants showed greater inter-user variation, lower velocity, longer pauses, and more jerk or jitter in their movements.

**Project implication:** Recognition should not depend on exact movement speed, a rigid trajectory, or a very short timing window. Static poses with a forgiving hold threshold are appropriate candidates for the first prototype.

### Playback controls need immediate nonvisual feedback

Lee and Ashok's YouTilt system explored motion gestures for online-video control by blind users and used vibration to confirm accepted input.

**Project implication:** Every accepted gesture should produce immediate nonvisual confirmation. The first prototype can use short earcons; haptic feedback can be considered later.

## Design Principles for This Prototype

- Keep the first gesture vocabulary small.
- Use gestures only for immediate transport actions such as `PLAY` and `STOP`.
- Keep instrument selection and playback duration in the voice-control layer.
- Let the **reading hand** provide score position only.
- Recognize commands only from the other hand inside a defined **command zone**.
- Use poses that can be taught through verbal or tactile instruction.
- Avoid gestures that require a precise camera-facing orientation or trajectory.
- Require a brief stable hold before activation.
- Use one-shot triggering and a cooldown to prevent repeated commands.
- Give immediate nonvisual confirmation after a command is accepted.

## Initial Gesture Candidates

These are engineering candidates for the first prototype, not validated final gestures.

| Command | Candidate gesture | Rationale |
|---|---|---|
| `PLAY` | Thumbs-up, held briefly | Proprioceptively distinct and substantially different from an open palm in hand-landmark space |
| `STOP` | Open palm, held briefly | Easy to describe verbally and less likely than a fist to resemble a relaxed resting hand |

`PAUSE / RESUME`, navigation, stem selection, and other commands should not be added until testing shows that they are necessary.

## Proposed Interaction Flow

```text
Reading finger identifies a score region
→ command hand enters the command zone
→ candidate pose is detected
→ pose remains stable for approximately 0.5 seconds
→ command is accepted once
→ short rising or falling earcon confirms acceptance
→ playback action is executed
→ brief cooldown prevents retriggering
```

Suggested feedback mapping:

- `PLAY`: short rising earcon
- `STOP`: short falling earcon

The earcons should be brief and spectrally unobtrusive so they do not mask the musical playback.

## Proposed HCI Evaluation

Use a choice-based elicitation and validation session with blind participants:

1. Explain each candidate gesture verbally or through guided tactile instruction.
2. Ask participants to perform each gesture several times without visual correction.
3. Compare candidate gestures for the same command.
4. Invite participants to modify the candidates or propose alternatives.
5. Test the selected gestures during an actual Braille-reading and playback task.

Evaluate:

- ease of learning without visual demonstration;
- recognition accuracy;
- false-trigger rate during normal Braille reading;
- command execution time;
- physical comfort and fatigue;
- memorability after a delay;
- subjective preference;
- clarity of the nonvisual confirmation.

## Implementation Notes

MediaPipe can provide hand landmarks, while simple Python rules can classify the two initial static poses. Gesture recognition should run only when a hand is inside the command zone. Suggested initial thresholds are:

- stable hold: approximately `400–600 ms`;
- one accepted command per hold;
- re-arm only after the hand leaves the command zone or returns to a neutral state;
- a short cooldown after activation.

These values are starting points and must be adjusted through testing with blind users.

## Key Research Papers

### Kane, Wobbrock, and Ladner, 2011

Kane, S. K., Wobbrock, J. O., & Ladner, R. E. (2011). **Usable Gestures for Blind People: Understanding Preference and Performance.** *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI '11)*, 413–422. [https://doi.org/10.1145/1978942.1979001](https://doi.org/10.1145/1978942.1979001)

**Relevance:** Compares gesture preferences and execution between blind and sighted users. The study concerns touchscreen gestures, so its findings inform user-centered gesture design but do not directly validate mid-air poses.

### Dim et al., 2016

Dim, N. K., Silpasuwanchai, C., Sarcar, S., & Ren, X. (2016). **Designing Mid-Air TV Gestures for Blind People Using User- and Choice-Based Elicitation Approaches.** *Proceedings of the 2016 ACM Conference on Designing Interactive Systems (DIS '16)*, 204–214. [https://doi.org/10.1145/2901790.2901834](https://doi.org/10.1145/2901790.2901834)

**Relevance:** Directly studies mid-air gesture design with blind participants and supports combining user elicitation with a choice-based method.

### Khanna et al., 2024

Khanna, P., Ramakrishnan, I. V., Jain, S., Bi, X., & Balasubramanian, A. (2024). **Hand Gesture Recognition for Blind Users by Tracking 3D Gesture Trajectory.** *Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI '24)*. [https://doi.org/10.1145/3613904.3642602](https://doi.org/10.1145/3613904.3642602)

**Relevance:** Identifies differences and greater variation in free-space gestures produced by blind users. Its system tracks gesture trajectories using a smartwatch, so the recognition method is not directly equivalent to camera-based static-pose recognition.

### Lee and Ashok, 2021

Lee, H.-N., & Ashok, V. (2021). **Towards Enhancing Blind Users' Interaction Experience with Online Videos via Motion Gestures.** *Proceedings of the 32nd ACM Conference on Hypertext and Social Media (HT '21)*. [https://doi.org/10.1145/3465336.3475116](https://doi.org/10.1145/3465336.3475116)

**Relevance:** Applies motion gestures to media playback and demonstrates the value of immediate nonvisual confirmation. Because YouTilt uses device motion and vibration, its findings support the interaction principle rather than directly validating the proposed camera-based gestures.

## Current Design Decision

For the first prototype:

```text
Reading hand → score position only
Command hand → PLAY / STOP gestures in a separate command zone
Voice input → stem selection and playback duration
Machine learning → reading-behavior and struggle inference, not direct playback activation
```

The gesture vocabulary should remain limited to `PLAY` and `STOP` until blind-user testing provides evidence for additional commands.
