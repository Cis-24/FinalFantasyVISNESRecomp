"""Tests for export_ca65_authority against a tiny synthetic ca65 build."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import export_ca65_authority as ex

# C0:0000  lda #$12 (A9 12)   rep #$30 stops prefix; ldx #$1234 (A2 34 12); rts (60);
# C0:0006  .word $0102 (table after rts -> data); C0:0008 nop (EA); C0:0009 .byte $2C
# (data directly after fall-through nop -> unknown); C0:000A lda #$00 (A9 00)
ROM = bytes.fromhex("A912A2341260" "0201" "EA" "2C" "A900")
SRC = """.proc Start
        lda #$12
        ldx #$1234
        rts
.endproc
Tbl:    .word $0102
Nop:    nop
        .byte $2C
        lda #$00
"""
DBG = "\n".join([
    "version\tmajor=2,minor=0",
    'file\tid=0,name="src/t.asm",size=1,mtime=0x0,mod=0',
    'mod\tid=0,name="t.o",file=0',
    'seg\tid=0,name="CODE",start=0x000000,size=0x0000,addrsize=absolute,type=rw',
    'seg\tid=1,name="test_code",start=0xC00000,size=0x000B,addrsize=absolute,type=ro,oname="x.sfc",ooffs=0',
    "span\tid=0,seg=1,start=0,size=2",
    "span\tid=1,seg=1,start=2,size=3",
    "span\tid=2,seg=1,start=5,size=1",
    "span\tid=3,seg=1,start=6,size=2,type=2",
    "span\tid=4,seg=1,start=8,size=1",
    "span\tid=5,seg=1,start=9,size=1,type=1",
    "span\tid=6,seg=1,start=10,size=2",
    "line\tid=0,file=0,line=2,span=0",
    "line\tid=1,file=0,line=3,span=1",
    "line\tid=2,file=0,line=4,span=2",
    "line\tid=3,file=0,line=6,span=3",
    "line\tid=4,file=0,line=7,span=4",
    "line\tid=5,file=0,line=8,span=5",
    "line\tid=6,file=0,line=9,span=6",
    'scope\tid=0,name="",mod=0',
    'scope\tid=1,name="Start",mod=0,type=scope,parent=0,size=6,span=2+1+0',
    'sym\tid=0,name="Start",addrsize=absolute,scope=0,val=0xC00000,seg=1,type=lab',
    'sym\tid=1,name="@0006",addrsize=absolute,scope=0,val=0xC00006,seg=1,type=lab',
]) + "\n"


class ExportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "src").mkdir()
        (self.tmp / "src/t.asm").write_text(SRC)
        (self.tmp / "t.dbg").write_text(DBG)
        (self.tmp / "t.sfc").write_bytes(ROM)

    def run_export(self, assembled=None):
        out = self.tmp / "out"
        asm = self.tmp / "t.sfc"
        if assembled is not None:
            asm = self.tmp / "other.sfc"
            asm.write_bytes(assembled)
        return ex.export(self.tmp / "t.dbg", self.tmp, self.tmp / "t.sfc", asm, out / "a.json",
                         out / "s.toml", out / "r.txt")

    def test_classification(self):
        auth, rep = self.run_export()
        self.assertEqual([i["pc24"] for i in auth["instructions"]], ["0xC00000", "0xC00002", "0xC00005", "0xC00008", "0xC0000A"])
        self.assertEqual(auth["instructions"][1]["bytes"], "a23412")
        self.assertEqual(auth["data_regions"], [dict(start_pc24="0xC00006", end_pc24="0xC00008")])
        self.assertEqual([u[0] for u in rep["unknown"]], [0xC00009])      # BIT-skip trick stays unknown
        self.assertEqual(rep["conflicts"], [])

    def test_entries_need_both_widths(self):
        auth, _ = self.run_export()
        self.assertEqual(auth["entries"], [dict(pc24="0xC00000", m=1, x=0)])

    def test_symbols_and_label_check(self):
        self.run_export()
        toml = (self.tmp / "out/s.toml").read_text()
        self.assertIn('name = "Start"', toml)
        self.assertIn('addr = "0000"', toml)
        self.assertIn("mismatches 0", (self.tmp / "out/r.txt").read_text())

    def test_image_mismatch_refused(self):
        with self.assertRaises(SystemExit):
            self.run_export(assembled=ROM[:-1] + b"\x01")

    def test_length_conflict_reported(self):
        (self.tmp / "t.dbg").write_text(DBG.replace("span\tid=0,seg=1,start=0,size=2", "span\tid=0,seg=1,start=0,size=4"))
        _, rep = self.run_export()
        self.assertTrue(any("length 4" in c for c in rep["conflicts"]))

    def test_opcode_table(self):
        for op, n in {0xA9: "M", 0xA2: "X", 0x22: "4", 0x60: "1", 0xD0: "2", 0x82: "3", 0xBF: "4"}.items():
            self.assertEqual(ex.OPLEN[op], n)
        self.assertTrue(ex.instruction_size_ok(0xA9, 3) and not ex.instruction_size_ok(0xA9, 4))


if __name__ == "__main__":
    unittest.main()
