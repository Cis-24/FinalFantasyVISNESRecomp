"""Tests for the comparison helpers: HDMAEN collapsing (compare_ppuw) and rect masks (compare_dumps)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import compare_dumps as cd
import compare_ppuw as cp


class CollapseTest(unittest.TestCase):
    def test_repeated_hdmaen_counts_once(self):
        ws = [(0x420C, 0x00), (0x2100, 0x0F), (0x420C, 0x00), (0x420C, 0x00), (0x420C, 0x00), (0x420C, 0xFE)]
        out, n = cp.collapse_hdmaen(ws)
        self.assertEqual(out, [(0x420C, 0x00), (0x2100, 0x0F), (0x420C, 0x00), (0x420C, 0xFE)])
        self.assertEqual(n, 2)

    def test_other_registers_and_values_stay(self):
        # Scroll registers are double-write latches: two equal writes are two halves, never collapsed.
        ws = [(0x210D, 0x30), (0x210D, 0x30), (0x420C, 0x00), (0x420C, 0x80)]
        out, n = cp.collapse_hdmaen(ws)
        self.assertEqual(out, ws)
        self.assertEqual(n, 0)


class RectMaskTest(unittest.TestCase):
    MASKS = [
        {"file": "fb", "rect": [10, 2, 12, 3], "tags": ["a"], "reason": "x"},
        {"file": "fb", "start": 5, "end": 6, "reason": "y"},
        {"file": "wram", "start": 0x10, "end": 0x11, "tags": ["a"], "reason": "z"},
    ]

    def test_rect_expands_per_row(self):
        r = cd.mask_ranges(self.MASKS, "fb", "a")
        self.assertIn((2 * 256 + 10, 2 * 256 + 12), r)
        self.assertIn((3 * 256 + 10, 3 * 256 + 12), r)
        self.assertIn((5, 6), r)
        self.assertEqual(len(r), 3)

    def test_tags_filter(self):
        self.assertEqual(cd.mask_ranges(self.MASKS, "fb", "b"), [(5, 6)])
        self.assertEqual(cd.mask_ranges(self.MASKS, "wram", "a"), [(0x10, 0x11)])


if __name__ == "__main__":
    unittest.main()
