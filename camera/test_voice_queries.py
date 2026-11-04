"""Query/rest-feedback regressions; no microphone, TTS, model or Max required.

Run: .venv/bin/python -m unittest discover -s camera -p test_voice_queries.py -v
"""

import threading
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

import voice_queries
from voice_mvp import Controller, SAMPLE_RATE
from voice_queries import answer_query, rest_feedback


def stems(start, end, *tracks):
    return {"cmd": "play_stems", "start": start, "end": end, "tracks": list(tracks)}


class QueryTests(unittest.TestCase):
    def test_measure_questions(self):
        for text in ["Which measure am I pointing to?", "What measure am I on?",
                     "What's my current measure?", "Where am I?",
                     "Can you tell me the current measure?"]:
            with self.subTest(text=text):
                self.assertEqual(answer_query(text, 7), "Your selected measure is 7.")

    def test_no_selected_measure(self):
        self.assertIn("No measure is selected", answer_query("Where am I?", None))

    def test_inventory_comes_from_score_parts(self):
        for text in ["What instruments are available?", "Which instruments can I play?",
                     "List the instruments", "What instruments can I choose?",
                     "Can you tell me what instruments are available?"]:
            with self.subTest(text=text):
                answer = answer_query(text, None)
                self.assertIn("Flute 1, Flute 2", answer)
                self.assertIn("Horn 4", answer)
                self.assertIn("Cello", answer)
                self.assertIn("Double Bass", answer)
                self.assertNotIn("effect", answer)

    def test_commands_and_transport_questions_are_not_intercepted(self):
        for text in ["play flute one", "play measures five through eight",
                     "play full mix", "stop", "both", "play both for me",
                     "Which measure is playing?", "What instruments are playing?"]:
            with self.subTest(text=text):
                self.assertIsNone(answer_query(text, 7))

    def test_missing_inventory_is_not_invented(self):
        with patch.object(voice_queries, "TRACKS_PATH") as path:
            path.read_text.side_effect = FileNotFoundError
            self.assertIn("can't read", answer_query("What instruments are available?", 7))


class RestFeedbackTests(unittest.TestCase):
    def test_rests_at_start(self):
        self.assertEqual(rest_feedback(stems(1, 2, "fl1")),
                         "Flute 1: no notes in measure 1.")

    def test_rest_at_start_is_reported_even_if_part_enters_later(self):
        self.assertEqual(rest_feedback(stems(1, 16, "fl1")),
                         "Flute 1: no notes in measure 1.")

    def test_single_measure(self):
        self.assertEqual(rest_feedback(stems(4, 4, "fh4")), "Horn 4: no notes in measure 4.")

    def test_multi_part_reports_only_resting_part(self):
        self.assertEqual(rest_feedback(stems(1, 16, "fl1", "vc")),
                         "Flute 1: no notes in measure 1.")

    def test_sounding_and_unpitched_parts(self):
        self.assertIsNone(rest_feedback(stems(1, 16, "vc", "sn", "bd")))

    def test_effects_have_no_score_activity_claim(self):
        self.assertIsNone(rest_feedback(stems(1, 2, "room")))

    def test_full_mix_and_stop_are_untouched(self):
        self.assertIsNone(rest_feedback({"cmd": "play_all", "start": 1, "end": 2}))
        self.assertIsNone(rest_feedback({"cmd": "stop"}))

    def test_missing_score_is_unknown_activity(self):
        with patch.object(voice_queries.ET, "parse", side_effect=FileNotFoundError):
            self.assertEqual(rest_feedback(stems(1, 2, "fl1")),
                             "I can't determine the instrument activity right now.")

    def test_missing_part_or_measure_does_not_assert_silence(self):
        for xml in ['<score-partwise/>',
                    '<score-partwise><part id="P1"><measure number="2">'
                    '<note><rest/></note></measure></part></score-partwise>']:
            with self.subTest(xml=xml):
                tree = voice_queries.ET.ElementTree(voice_queries.ET.fromstring(xml))
                with patch.object(voice_queries.ET, "parse", return_value=tree):
                    self.assertIsNone(rest_feedback(stems(1, 2, "fl1")))


class ControllerQueryTests(unittest.TestCase):
    def setUp(self):
        self.ctrl = Controller(7, MagicMock(), MagicMock())
        self.ctrl._state = Controller.PROCESSING
        self.ctrl._last_start = 4
        self.audio = np.zeros(SAMPLE_RATE, dtype=np.float32)

    def run_request(self, text, anchor=7, query_anchor=7):
        with patch("voice_mvp._record_until", return_value=self.audio), \
             patch("voice_mvp._transcribe", return_value=text):
            self.ctrl._run_recording(threading.Event(), anchor, 0, 4, query_anchor)

    def test_queries_speak_without_parse_playback_or_history_changes(self):
        pending = {"anchor": 3, "question": "Flute one, flute two, or both?"}
        self.ctrl._pending = pending
        with patch("voice_mvp._llm_parse") as parse, \
             patch("voice_mvp._dispatch") as dispatch, \
             patch("voice_mvp._speak") as speak:
            self.run_request("Which measure am I pointing to?")
        speak.assert_called_once_with("Your selected measure is 7.")
        parse.assert_not_called()
        dispatch.assert_not_called()
        self.ctrl._client.send_message.assert_not_called()
        self.assertEqual(self.ctrl._last_start, 4)
        self.assertEqual(self.ctrl._pending, pending)
        self.assertEqual(self.ctrl._state, Controller.IDLE)

    def test_query_uses_current_selection_without_changing_pending_anchor(self):
        pending = {"anchor": 3, "question": "Flute one, flute two, or both?"}
        self.ctrl._pending = pending
        with patch("voice_mvp._speak") as speak:
            self.run_request("Which measure am I pointing to?", anchor=3, query_anchor=9)
        speak.assert_called_once_with("Your selected measure is 9.")
        self.assertEqual(self.ctrl._pending, pending)

    def test_absent_current_selection_does_not_reuse_pending_anchor(self):
        self.ctrl._pending = {"anchor": 3, "question": "Flute one, flute two, or both?"}
        with patch("voice_mvp._speak") as speak:
            self.run_request("Where am I?", anchor=3, query_anchor=None)
        self.assertIn("No measure is selected", speak.call_args.args[0])

    def test_notice_precedes_unchanged_playback(self):
        command = stems(1, 16, "fl1", "vc")
        events = []
        with patch("voice_mvp._llm_parse", return_value=(command, None)), \
             patch("voice_mvp._speak", side_effect=lambda text: events.append(text)), \
             patch("voice_mvp._dispatch", side_effect=lambda cmd, client: events.append(cmd)):
            self.run_request("play flute one and cello", anchor=1)
        self.assertEqual(events, ["Flute 1: no notes in measure 1.", command])
        self.assertEqual(self.ctrl._last_start, 1)

    def test_sounding_command_has_no_new_tts(self):
        command = stems(3, 8, "fl1")
        with patch("voice_mvp._llm_parse", return_value=(command, "Playing flute one.")), \
             patch("voice_mvp._speak") as speak, patch("voice_mvp._dispatch") as dispatch:
            self.run_request("play flute one measures three through eight")
        speak.assert_not_called()
        dispatch.assert_called_once_with(command, self.ctrl._client)

    def test_stop_during_notice_cancels_dispatch(self):
        with patch("voice_mvp._llm_parse", return_value=(stems(1, 2, "fl1"), None)), \
             patch("voice_mvp._speak", side_effect=lambda text: self.ctrl.on_stop()), \
             patch("voice_mvp._dispatch") as dispatch:
            self.run_request("play flute one measures one through two")
        dispatch.assert_not_called()
        self.assertEqual(self.ctrl._last_start, 4)

    def test_stop_during_query_does_not_send_playback(self):
        with patch("voice_mvp._speak", side_effect=lambda text: self.ctrl.on_stop()), \
             patch("voice_mvp._dispatch") as dispatch:
            self.run_request("What instruments can I choose?")
        dispatch.assert_not_called()
        self.assertEqual(self.ctrl._state, Controller.IDLE)


if __name__ == "__main__":
    unittest.main()
