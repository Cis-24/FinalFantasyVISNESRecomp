"""Tests for miss_report.py: the skipped dispatches it reads from a run's stderr log."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import miss_report as mr


class SkippedDispatchTest(unittest.TestCase):
    def test_dispatch_oob_line(self):
        # The line snesrecomp patch 0015 prints in every build; the wound handler case of r05.
        lines = ["[dispatch-oob] first hit site=$C243AC value=$004600 frame=12408 "
                 "(target missing from the generated dispatch; ...)\n"]
        self.assertEqual(mr.skipped_dispatches(lines), [("dispatch-oob", 0xC243AC, 0x4600, 12408)])

    def test_unresolved_abandon_line_has_no_value(self):
        lines = ["[unresolved-abandon] first hit site=$C0FFEE frame=7 entry_s=$15F0 hrv=2 "
                 "(handler side effects SKIPPED -- authorize this dispatch)\n"]
        self.assertEqual(mr.skipped_dispatches(lines), [("unresolved-abandon", 0xC0FFEE, None, 7)])

    def test_other_lines_are_ignored(self):
        lines = ["exit: script quit after 13903 frames\n",
                 "  [dispatch-oob] first hit site=$C243AC value=$004600 frame=1\n",
                 "[dispatch-oob] later hit site=$C243AC value=$004600 frame=1\n"]
        self.assertEqual(mr.skipped_dispatches(lines), [])


if __name__ == "__main__":
    unittest.main()
