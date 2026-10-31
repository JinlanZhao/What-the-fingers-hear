# What the Fingers Hear — Speaker Script

Key points to emphasize appear in **bold**.

## 01. What the Fingers Hear

I'm Jinlan Zhao, studying Electronic Production and Design at Berklee. **What the Fingers Hear connects a physical Braille music score with audio playback.** A reader selects a measure by touch and uses a command to hear it. Since the last report, I have added voice-selected instruments, physical controls and spoken clarification. Today I'll show the prototype, the IRB and study plan, and the next interactions for blind and low-vision musicians.

## 02. Since the last report

The score, page map, camera tracking and Max playback form the foundation. **The new work connects voice-selected instruments, RECORD / PLAY / STOP buttons, and spoken clarification.** The system asks which instrument part the reader means and speaks selected error prompts. I have drafted the research protocol and am completing CITI training.

## 03. Physical controls

I added physical buttons after repeated or unclear gesture activation in the earlier demo. **Hold RECORD to speak, then release it to submit. PLAY starts the Full Mix from the selected measure. STOP stops playback and cancels recording or a pending request.** A Teensy 4.0 handles the three buttons with debounced events. The input-method study will compare buttons and gestures on equivalent Play and Stop tasks.

## 04. Current system

OpenCV and ArUco establish page coordinates. MediaPipe tracks the fingertip, and the page map converts its position into a measure. **Starting RECORD freezes that measure for the request.** Local Whisper transcribes speech, local Qwen2.5:7b parses the command, and Python validates it before sending OSC to Max/MSP. Max handles playback and synchronization. Direct PLAY and gestures send transport commands directly. The prototype runs on my Mac and uses macOS speech output.

## 05. Voice-selected playback

**Voice requests now select one instrument, multiple instruments, or an explicit measure range.** “Play violin one” uses the measure captured when RECORD begins. “Play flute one and cello from measure eight to twelve” specifies the parts and range. Max plays selected stems on a shared signal-rate playhead to keep them aligned. Full Mix uses a separate stereo player. The prepared piece contains sixteen measures with a registered page map.

## 06. Parser revisions

The regex parser handled fixed phrases but struggled with natural wording and corrections. A rules-only language-model prompt produced missing fields and incorrect clarification. **The current prompt uses ordered decision steps and 34 examples. Python handles self-corrections and exclusions.** The parser runs locally through Ollama with Qwen2.5:7b after API rate limits interrupted development. The deterministic parser remains the error fallback.

## 07. Spoken clarification

At measure two, I say “Play flute.” The system asks “Flute one, flute two, or both?” I hold RECORD again and answer “Flute one.” **The conversation keeps the original measure even if my finger moves.** STOP clears the pending question. Spoken feedback currently covers clarification and selected errors. Successful playback requests also print a confirmation in the terminal.

## 08. Recorded demonstration

This recording shows the prepared Braille score, physical controls, voice requests and Max playback working together. **Listen for the requested instrument changes and watch the button interaction.**

[Play the embedded video. Continue on the next slide.]

## 09. Development results

**The October 12 report records 31 transcript-based parser cases passing.** Hardware tests connected the buttons, voice requests and camera anchor. Two fixes are next: Whisper sometimes transcribes “full mix” as “four mix,” and terminal feedback can name an earlier instrument after Python corrects the playback selection. I will also measure task success, measure-selection accuracy and end-to-end response time.

## 10. IRB progress

**I am completing the CITI training course and preparing the IRB application.** The protocol drafted on October 14 covers three studies. I am preparing the consent materials, task scripts and data-collection plan for submission. Recruitment and participant data collection will begin after written IRB approval. **Because IRB review takes time, I will use that period to develop interactions that help musicians explore the ensemble and return to their reading.**

## 11. Three planned studies

**Study 1 examines usability through touch and voice tasks**, including success, errors and recovery. **Study 2 compares buttons and gestures** for equivalent Play and Stop tasks, including unintended activation, interruption, physical effort and preference. **Study 3 examines interaction rules and customization**, including understanding, settings use and perceived effort. Studies 2 and 3 compare conditions within participants and counterbalance their order. I will collect task logs and participant feedback.

## 12. Development during IRB review

**My first development priorities are returning to a saved position, explaining silence and instrument entry, and comparing parts within one range.** Together, they form one scenario: read my part, ask which instruments are active here, listen to another part, compare combinations, then return to my original reading position. These interactions build directly on the existing page map, voice commands and multistem playback.

## 13. Returning to the reading position

Imagine a violin reader at measure five who wants to hear the cello. “Remember here” saves the piece, part, page and measure, together with the playback range and selected parts. After exploring, “Go back” restores that state. **Restoring playback and helping a finger find the paper position are separate tasks.** I will begin with spoken page and measure cues, then explore optional audio navigation. The Page Map shows measure 1 across pages 2–3 and measure 16 across pages 17–18, so the bookmark also needs to preserve the relevant page continuation.

## 14. Silence and instrument entry

**Silence needs an explanation.** A part may be resting, a command may have failed, or the system may have lost the reading position. Each state needs distinct feedback and an action. In this proposed example: “Flute one rests here. Its next entry is measure eight. Would you like the two measures before it enters?” **Rest and entry information will come from MusicXML.** Command status and tracking status will explain system errors. Readers can ask which instruments play at the current measure, then listen to the lead-in or choose another part.

## 15. Comparing parts in the same passage

The system already supports multiple stems. **I want to keep the same range while the reader changes the listening combination.** “Play my part,” “Add cello,” “Play the Full Mix,” then “Restore the previous combination.” The reader can compare shared rhythms, musical responses and how the surrounding ensemble changes their melody. Saving the range and previous combination reduces repeated instrument and measure descriptions. This supports the project's use of a full orchestral score.

## 16. Further interaction directions

Three further directions extend this workflow. **Practice:** lock the selection, pick up the instrument, hear a model, wait a user-set interval and repeat, with count-in and immediate Stop. The selection stays available when hands leave the page. Amber Sound Touch describes teaching through short demonstrations and repeated playing. **Annotations:** bind the original voice recording to the piece, part and measure, including teacher or conductor advice. Readers choose query, arrival or pre-practice review. **Independent setup:** announce page and tracking status, give an actionable recovery cue, and allow a spoken measure number. Clearly distinguish the current location from the last valid location. Voice, earcons and optional haptics can be compared.

Practice reference: [Amber Sound Touch, “Memorising music”](https://soundtouch.ambertrust.org/services/instrumental-and-vocal-tuition/strategies/memorising-music/).

## 17. Next steps

**Research preparation and interaction development will move forward together.** I will complete CITI training and prepare the application and consent materials while prototyping the three priority interactions. Across development, I will repeat measure-selection and page-placement trials, measure response time, and add consistent task scripts and event logging. After approval, I plan to conduct all three studies and use task outcomes, recovery behavior and reader feedback to guide revisions.

## 18. Questions for discussion

**What cues would help a reader return to the saved position on paper?** I am especially interested in page and measure feedback for a measure that continues across pages. **Which information would most help ensemble listening: active instruments, rest and entry information, or saved part combinations?** For the input-method study, I will keep tasks, practice and feedback comparable between buttons and gestures. Thank you.
