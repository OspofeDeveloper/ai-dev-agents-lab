"""Tests para scripts/sdd-next-id.py (ROADMAP 11.2b).

Asignador determinista del siguiente ID secuencial (B-00X, F-NNN, ...).
Foco: el max+1 correcto, padding, archivo inexistente, multi-archivo, y la
DESAMBIGUACION de prefijos (un prefijo no debe matchear como sufijo de otro
token: F no es RF ni F-C; R no es CR).
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


class NextIdTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def next(self, prefix, *files, width=None):
        args = [prefix, *[str(f) for f in files]]
        if width is not None:
            args += ["--width", str(width)]
        r = run_script("sdd-next-id.py", *args)
        return r

    def test_empty_or_missing_file_starts_at_001(self):
        r = self.next("B", self.dir / "nope.md")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(r.stdout.strip(), "B-001")

    def test_max_plus_one_with_gaps(self):
        f = write(self.dir / "bugs.md", "### B-001\n### B-002\n### B-005\n")
        self.assertEqual(self.next("B", f).stdout.strip(), "B-006")

    def test_padding_width(self):
        f = write(self.dir / "x.md", "TC-009\n")
        self.assertEqual(self.next("TC", f).stdout.strip(), "TC-010")
        self.assertEqual(self.next("TC", f, width=4).stdout.strip(), "TC-0010")

    def test_multi_file_scan(self):
        a = write(self.dir / "a.md", "### B-003\n")
        b = write(self.dir / "b.md", "### B-010\n")
        self.assertEqual(self.next("B", a, b).stdout.strip(), "B-011")

    # --- desambiguacion de prefijos ---
    def test_F_ignores_RF_and_FC(self):
        f = write(self.dir / "features.md", "RF-001 RF-002\nF-001\nF-C-003\nF-C-001\n")
        # F solo ve F-001 -> siguiente F-002 (ni RF-002 ni F-C-003 cuentan)
        self.assertEqual(self.next("F", f).stdout.strip(), "F-002")

    def test_FC_is_independent_sequence(self):
        f = write(self.dir / "features.md", "F-001\nF-C-003\nF-C-001\n")
        self.assertEqual(self.next("F-C", f).stdout.strip(), "F-C-004")

    def test_R_ignores_CR(self):
        f = write(self.dir / "changes.md", "CR-009\n")
        self.assertEqual(self.next("R", f).stdout.strip(), "R-001")

    def test_prefix_at_line_start(self):
        # IDs como heading markdown
        f = write(self.dir / "x.md", "## B-007: titulo\n")
        self.assertEqual(self.next("B", f).stdout.strip(), "B-008")

    # --- errores de uso ---
    def test_missing_file_arg_exit_1(self):
        r = run_script("sdd-next-id.py", "B")
        self.assertEqual(r.returncode, 1)

    def test_bad_width_exit_1(self):
        f = write(self.dir / "x.md", "")
        r = self.next("B", f, width=0)
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
