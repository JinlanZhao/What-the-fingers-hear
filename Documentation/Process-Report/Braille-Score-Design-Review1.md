# Braille Score — Design Review and Proposed Solutions

**Date:** September 30, 2026  
**Source:** Wizard of Oz demonstration and a conversation with a blind friend  
**Status:** Proposed design changes; implementation and validation are pending.

## 1. Repeated Gesture Activation

**Observation:** The same gesture can trigger a command twice.

**Proposed solutions:**

- Try a different gesture for playback control.
- Alternatively, add two small buttons on the paper: **PLAY** and **STOP**.

**Open decision:** Whether to retain gesture control or use buttons. The button sensing method has not been selected.

## 2. Gesture Clarity

**Observation:** The current gestures are not sufficiently clear.

**Next step:** Compare alternative gestures and the PLAY / STOP button option for clarity and reliable activation.

## 3. Measure Awareness

**Observation:** Users need to know which measure they have selected and which measure the audio is currently playing.

| Feedback type | When | Information |
|---|---|---|
| Automatic announcement | When preparing to play | The measure currently selected by the reading finger |
| On-demand query | During audio playback | The measure the audio has reached |

The selected measure and the playback measure must be treated as separate states.

## 4. Instrument Availability in the Current Measure

**Observation:** Users need feedback when the requested measure contains no instrument sound.

**Proposed behavior:**

- If there is sound, play the requested audio.
- If there is no sound, provide the spoken message:

> No instrument in this measure.

**Open detail:** Define whether this check concerns the full mix or only the selected instrument(s), particularly when the selected stem is silent but other instruments are active.

## 5. Instrument List and Part Counts

**Observation:** Users do not know which instruments are available or how many separately selectable parts exist, such as Flute 1 and Flute 2.

**Proposed solution:** Provide Voice Instructions explaining the available instruments, their part counts, and the names used to select them.

## 6. Registration Frame Tolerance and Recovery

**Observation:** A user may move the Braille score outside the registration frame and need help recognizing and correcting its position.

**Proposed solutions:**

- Use a larger registration frame.
- Add tape along all four edges to create a tactile distinction between the page area and its boundaries.
- Provide a beep when the score moves outside the valid area.

**Intended outcome:** The user can locate the boundaries by touch and reposition the score independently.

**Pending validation:** Check whether the larger frame and tactile boundaries support reliable recovery, and whether the system can detect displacement of the paper itself.

## 7. User Interface

**Open question:** What interface will users operate in the final application?

The final user interface remains undecided.

## 8. Operating System

**Open question:** Will the final application run on iPhone, Mac, or Windows?

The target operating system remains undecided. The role of the iPhone as a camera versus a standalone application device also needs to be specified.
