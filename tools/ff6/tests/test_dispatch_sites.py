"""Tests for the dispatch-site scanner on a tiny synthetic source tree."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dispatch_sites as ds

SRC = """.proc Run
        tax
        jmp     (near StateTbl,x)
.endproc
.proc Off
        jsr     (near CmdTbl+$10,x)
        jmp     (.loword(VecTbl),x)
.endproc
.proc Exec
@3d40:  jmp     (near PageTbl,x)
        longa
        lda     f:EvtTbl,x
        sta     $2a
        jmp     ($002a)
.endproc
"""


class ScanTest(unittest.TestCase):
    def test_scan(self):
        d = Path(tempfile.mkdtemp())
        (d / "a.asm").write_text(SRC)
        r = list(ds.scan(d))
        self.assertEqual([(x["proc"], x["kind"], x["table"], x["offset"]) for x in r],
                         [("Run", "table", "StateTbl", 0), ("Off", "table", "CmdTbl", 16),
                          ("Off", "table", "VecTbl", 0), ("Exec", "table", "PageTbl", 0),
                          ("Exec", "ptrtail", "EvtTbl", 0)])
        self.assertEqual([x["occurrence"] for x in r], [1, 1, 2, 1, 2])
        self.assertEqual(r[4]["ptr"], "$002a")


class TableInfoTest(unittest.TestCase):
    # Battle and menu both define MaxHPMPTbl. menu_common.asm is included into menu.o, so no
    # module names it as its file; the first candidate used to win (the battle table).
    DBG = dict(
        files={0: "./src/battle/battle_main.asm", 1: "./src/battle/init_attacker.asm",
               2: "./src/menu/menu_main.asm", 3: "./src/menu/menu_common.asm"},
        mods={0: dict(name="battle.o", file=0), 1: dict(name="menu.o", file=2)},
        scopes={10: dict(name="", type="", mod=0, parent=None, spans=[]),
                11: dict(name="", type="", mod=1, parent=None, spans=[])},
        syms=[dict(name="MaxHPMPTbl", val=0xC22859, scope=10, ref=[100]),
              dict(name="MaxHPMPTbl", val=0xC30D7E, scope=11, ref=[200]),
              dict(name="OnlyTbl", val=0xC30100, scope=11, ref=[])],
        line_loc={100: (1, 87), 200: (3, 2326)}, segs={}, spans={})

    def test_duplicate_label_follows_the_site_reference(self):
        self.assertEqual(ds.table_info(self.DBG, "MaxHPMPTbl", "menu/menu_common.asm", 2326)[0], 0xC30D7E)
        self.assertEqual(ds.table_info(self.DBG, "MaxHPMPTbl", "battle/init_attacker.asm", 87)[0], 0xC22859)

    def test_duplicate_label_without_reference_is_unresolved(self):
        self.assertIsNone(ds.table_info(self.DBG, "MaxHPMPTbl", "menu/menu_common.asm", 9999))

    def test_unique_label_needs_no_reference(self):
        self.assertEqual(ds.table_info(self.DBG, "OnlyTbl", "menu/menu_common.asm", 9999)[0], 0xC30100)


class PtrListTest(unittest.TestCase):
    # jmp (zTaskCodePtr): no table, the targets are the labels the source stores into the pointer.
    def test_ptrlist_keeps_unique_code_labels_in_the_site_bank(self):
        rom = bytearray(0x100)
        rom[0x10] = 0x6C                                   # jmp (abs)
        dbg = dict(files={0: "./src/menu/m.asm"}, lines={1: (0, 7, 0, [5])},
                   segs={1: dict(name="C3", start=0xC30000, size=0x100, ooffs=0)},
                   spans={5: dict(seg=1, start=0x10, size=3, typed=False)}, ram_lines=set(),
                   syms=[dict(name="A", val=0xC30020), dict(name="B", val=0xC30040),
                         dict(name="Dup", val=0xC30050), dict(name="Dup", val=0xC30058),
                         dict(name="Far", val=0xC20020), dict(name="Data", val=0xC30060)])
        rows = {0xC30020: {"kind": "code"}, 0xC30040: {"kind": "code"}, 0xC30050: {"kind": "code"},
                0xC20020: {"kind": "code"}, 0xC30060: {"kind": "data"}}
        site = dict(file="menu/m.asm", line=7, proc="Exec", occurrence=1, op="jmp", kind="ptrlist",
                    ptr="zP", targets=["A", "B", "Dup", "Far", "Data", "Gone"])
        out, n, dropped = ds.build_dispatches([site], dbg, rows, bytes(rom))
        self.assertEqual(n, 1)
        self.assertEqual(out, [dict(site_pc24="0xC30010", kind="ptrtail", targets=["0xC30020", "0xC30040"])])
        self.assertEqual(len(dropped), 4)


if __name__ == "__main__":
    unittest.main()
