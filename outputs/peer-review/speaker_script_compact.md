# What the Fingers Hear — Speaker Script

Key points to emphasize appear in **bold**.

## 01. What the Fingers Hear

I'm Jinlan Zhao. **What the Fingers Hear connects a physical Braille music score with audio playback.** Readers select a measure by touch and request the parts they want to hear. Today I'll show the new controls and voice interaction, the research plan, and the next features for musicians.

## 02. Controls

**Hold RECORD to speak and release it to submit. PLAY starts the Full Mix from the selected measure. STOP stops playback and cancels recording or a pending request.** I added these controls after repeated or unclear gesture activation in the earlier demo. A Teensy 4.0 handles the buttons with debounced events. The study will compare buttons and gestures on equivalent tasks.

## 03. System

OpenCV and ArUco establish page coordinates. MediaPipe tracks the fingertip, and the page map identifies the measure. **Starting RECORD freezes that measure for the request.** Local Whisper transcribes speech, Qwen2.5:7b interprets it, and Python validates the command before sending OSC to Max/MSP. Max handles playback and synchronization. Direct PLAY and gestures send transport commands directly.

## 04. Voice

**Voice requests select a single instrument, several instruments, or a measure range.** “Play violin one” uses the captured measure. “Play flute one and cello from measure eight to twelve” sets both parts and range. If I say “Play flute,” the system asks “Flute one, flute two, or both?” **The answer keeps the original measure, even if my finger moves.** Selected stems share a signal-rate playhead, while Full Mix uses a stereo player. The prepared piece contains sixteen measures.

## 05. Development

The regex parser struggled with natural wording. **The current parser uses ordered decision steps and 34 examples, with Python handling corrections and exclusions.** Local Ollama inference replaced the API after rate limits interrupted development. Regex remains the fallback. **The October 12 report records 31 transcript-based parser cases passing.** The next fixes address “full mix” becoming “four mix” in transcription and terminal messages that disagree with corrected tracks.

## 06. Demo

**Listen for changes in the requested instruments and watch the physical controls.** This recording shows the score, camera selection, voice commands and Max playback together.

[Play the embedded video.]

## 07. Research

**I am completing CITI training and preparing the IRB application**, including the protocol and consent materials. I plan three studies: **usability** through touch and voice tasks, **buttons versus gestures** on equivalent transport tasks, and **interaction rules and customization**. I will collect success, errors, recovery behavior and participant feedback. Studies 2 and 3 compare conditions within participants, with counterbalanced order and comparable practice and feedback. Recruitment and data collection will follow written approval. **While IRB review takes time, I will develop the next interactions.**

## 08. Return

A violin reader at measure five wants to hear cello. **“Remember here” saves the reading location and playback state. “Go back” restores them after exploration.** Restoring playback and helping a finger find the paper position are separate tasks. I will begin with spoken page and measure cues, then explore optional audio navigation. Measures 1 and 16 continue across pages, so the bookmark must preserve the relevant page continuation.

## 09. Silence

**A rest, a failed request and an unknown position each need different feedback.** For example: “Flute one rests here. Its next entry is measure eight. Would you like the two measures before it enters?” **MusicXML supplies rests, active instruments and the next entry.** Command and tracking status explain system errors. This lets a reader ask which instruments play here, hear the lead-in or choose another part.

## 10. Ensemble

**Keep the same range while changing the listening combination:** “Play my part,” “Add cello,” “Play the Full Mix,” and “Restore the previous combination.” This reduces repeated descriptions of instruments and measures. Readers can focus on shared rhythms, musical responses and how the ensemble changes their melody. The full scenario is to read my part, explore other instruments, compare combinations and return to my reading position.

## 11. Next Steps

**The first priorities are return, silence and entry feedback, and part comparison.** Later, a practice loop can lock the selection while the reader picks up an instrument, then alternate a model with a user-set practice interval, count-in and Stop. Amber Sound Touch describes short demonstrations and repeated playing. Voice annotations can preserve teacher advice by piece, part and measure, with reader-chosen review timing. Setup feedback can explain tracking status and give recovery cues or accept a spoken measure. **Current location and last valid location need distinct feedback.** I will also measure tracking accuracy and response time and log recovery.

Practice reference: [Amber Sound Touch, “Memorising music”](https://soundtouch.ambertrust.org/services/instrumental-and-vocal-tuition/strategies/memorising-music/).

## 12. Discussion

**What page and measure cues would help readers return to a saved place on paper?** And **which feedback would most help ensemble listening:** available instruments, rest and entry information, or saved part combinations? These are the questions I want to explore next. Thank you.
