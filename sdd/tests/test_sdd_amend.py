"""Black-box tests para scripts/sdd-amend.py.

Marcador determinista de enmiendas de CA sobre planes SDD. Separa el AUTOR del
que MARCA: la anotacion `Enmienda pendiente` del plan SOLO la escribe/limpia
este script. (La retencion selectiva de tasks que referencian el CA la aplican
los CONSUMIDORES de la anotacion — sdd-gate-check.py y sdd-task-state.py — no
este script; aqui se verifica que el contrato de la anotacion es solido.)

Contrato verificado leyendo el script:
  mark   inserta `> **Enmienda pendiente:** CA-XXX (E-NNN, fecha)` tras `Estado:`
  clear  elimina la(s) linea(s) por --ca / --ref / --all
  list   lista sin escribir
  next-ref  imprime el siguiente E-NNN libre escaneando los archivos dados
Exit: 0 OK; 1 error de uso/IO; 2 plan sin `Estado:` reconocible o nada que limpiar.
"""
from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


def plan_text(estado="VALIDADO", spec_rel="login_spec.md", extra=""):
    return (
        f"# Plan: Login\n\n"
        f"> Spec origen: `{spec_rel}`\n"
        f"**Estado:** {estado}\n\n"
        f"## Arquitectura\n\n- Implementa CA-001, CA-002, CA-003.\n\n"
        f"{extra}"
    )


AMEND_LINE_RE = re.compile(
    r"^>\s*\*\*Enmienda pendiente:\*\*\s*(CA-\d+)\s*\((E-\d+),\s*([\d-]+)\)\s*$",
    re.MULTILINE,
)


class AmendMarkTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.plan = write(self.dir / "login_plan.md", plan_text())

    def tearDown(self):
        self.tmp.cleanup()

    def _mark(self, ca, *extra):
        return run_script("sdd-amend.py", "mark", self.plan, "--ca", ca, *extra)

    def test_mark_writes_amend_line_after_estado(self):
        r = self._mark("CA-003")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = self.plan.read_text(encoding="utf-8")
        m = AMEND_LINE_RE.search(text)
        self.assertIsNotNone(m, f"no se escribio la linea de enmienda:\n{text}")
        self.assertEqual(m.group(1), "CA-003")
        # Aparece tras la linea de Estado (header), antes de Arquitectura
        self.assertLess(text.index("Enmienda pendiente"), text.index("## Arquitectura"))
        self.assertGreater(text.index("Enmienda pendiente"), text.index("**Estado:**"))

    def test_mark_format_is_canonical(self):
        r = self._mark("CA-003")
        self.assertEqual(r.returncode, 0)
        text = self.plan.read_text(encoding="utf-8")
        m = AMEND_LINE_RE.search(text)
        # ref autoasignada E-001 (no hay refs previas), fecha ISO
        self.assertEqual(m.group(2), "E-001")
        self.assertRegex(m.group(3), r"^\d{4}-\d{2}-\d{2}$")
        self.assertIn("REF: E-001", r.stdout)

    def test_mark_explicit_ref(self):
        r = self._mark("CA-002", "--ref", "E-007")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = self.plan.read_text(encoding="utf-8")
        self.assertIn("E-007", text)

    def test_mark_invalid_ref_format_exit_1(self):
        r = self._mark("CA-002", "--ref", "X-9")
        self.assertEqual(r.returncode, 1)
        self.assertIn("--ref invalido", r.stderr)

    def test_mark_ref_autoincrements_over_existing(self):
        # Primera enmienda -> E-001
        self._mark("CA-001")
        # Segunda (otro CA) -> E-002 (escanea el plan y ve E-001)
        r = self._mark("CA-002")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("REF: E-002", r.stdout)

    def test_mark_idempotent_same_ca(self):
        self._mark("CA-003")
        first = self.plan.read_text(encoding="utf-8")
        r = self._mark("CA-003")
        self.assertEqual(r.returncode, 0)
        self.assertIn("YA_MARCADA", r.stdout)
        self.assertEqual(first, self.plan.read_text(encoding="utf-8"),
                         "re-mark del mismo CA no debe cambiar bytes")

    def test_mark_ref_from_spec_origen_changelog(self):
        # El changelog de enmiendas aplicadas vive en el spec origen.
        write(self.dir / "login_spec.md",
              "# Spec: Login\n> Feature ID: F-001\n"
              "Enmienda aplicada E-005 sobre CA-001.\n")
        r = self._mark("CA-002")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # Siguiente libre tras E-005 -> E-006
        self.assertIn("REF: E-006", r.stdout)

    def test_mark_invalid_ca_exit_1(self):
        r = self._mark("CA-XYZ")
        self.assertEqual(r.returncode, 1)
        self.assertIn("--ca CA-XXX", r.stderr)

    def test_mark_no_estado_line_exit_2(self):
        bad = write(self.dir / "no_es_plan.md", "# Algo\n\nsin estado reconocible\n")
        r = run_script("sdd-amend.py", "mark", bad, "--ca", "CA-001")
        self.assertEqual(r.returncode, 2)
        self.assertIn("no parece un plan", r.stderr)


class AmendClearListTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.plan = write(self.dir / "login_plan.md", plan_text())

    def tearDown(self):
        self.tmp.cleanup()

    def _mark(self, ca, *extra):
        return run_script("sdd-amend.py", "mark", self.plan, "--ca", ca, *extra)

    def test_clear_by_ca(self):
        self._mark("CA-001")
        self._mark("CA-002")
        r = run_script("sdd-amend.py", "clear", self.plan, "--ca", "CA-001")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = self.plan.read_text(encoding="utf-8")
        self.assertNotIn("CA-001 (", text)
        self.assertIn("CA-002 (", text)

    def test_clear_by_ref(self):
        self._mark("CA-001", "--ref", "E-010")
        r = run_script("sdd-amend.py", "clear", self.plan, "--ref", "E-010")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("Enmienda pendiente", self.plan.read_text(encoding="utf-8"))

    def test_clear_all(self):
        self._mark("CA-001")
        self._mark("CA-002")
        r = run_script("sdd-amend.py", "clear", self.plan, "--all")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("Enmienda pendiente", self.plan.read_text(encoding="utf-8"))

    def test_clear_nonexistent_exit_2(self):
        self._mark("CA-001")
        r = run_script("sdd-amend.py", "clear", self.plan, "--ca", "CA-999")
        self.assertEqual(r.returncode, 2)
        self.assertIn("NADA_QUE_LIMPIAR", r.stderr)

    def test_clear_all_on_empty_is_noop_exit_0(self):
        r = run_script("sdd-amend.py", "clear", self.plan, "--all")
        self.assertEqual(r.returncode, 0)
        self.assertIn("nada que limpiar", r.stdout.lower())

    def test_clear_requires_target(self):
        r = run_script("sdd-amend.py", "clear", self.plan)
        self.assertEqual(r.returncode, 1)
        self.assertIn("clear exige", r.stderr)

    def test_list_does_not_write(self):
        self._mark("CA-001")
        before = self.plan.read_text(encoding="utf-8")
        r = run_script("sdd-amend.py", "list", self.plan)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("CA-001", r.stdout)
        self.assertIn("1 enmienda", r.stdout)
        self.assertEqual(before, self.plan.read_text(encoding="utf-8"),
                         "list no debe escribir")

    def test_list_empty(self):
        r = run_script("sdd-amend.py", "list", self.plan)
        self.assertEqual(r.returncode, 0)
        self.assertIn("0 enmienda", r.stdout)

    def test_mark_then_clear_roundtrip_idempotent(self):
        before = self.plan.read_text(encoding="utf-8")
        self._mark("CA-001")
        run_script("sdd-amend.py", "clear", self.plan, "--ca", "CA-001")
        self.assertEqual(before, self.plan.read_text(encoding="utf-8"),
                         "mark + clear del mismo CA debe restaurar los bytes")


class AmendNextRefAndUsageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_next_ref_empty_is_e001(self):
        f = write(self.dir / "a.md", "sin refs aqui\n")
        r = run_script("sdd-amend.py", "next-ref", f)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "E-001")

    def test_next_ref_scans_multiple_files(self):
        a = write(self.dir / "a.md", "menciona E-003\n")
        b = write(self.dir / "b.md", "menciona E-009 y E-002\n")
        r = run_script("sdd-amend.py", "next-ref", a, b)
        self.assertEqual(r.stdout.strip(), "E-010")

    def test_unknown_command_exit_1(self):
        f = write(self.dir / "p.md", plan_text())
        r = run_script("sdd-amend.py", "frobnicate", f)
        self.assertEqual(r.returncode, 1)
        self.assertIn("comando desconocido", r.stderr)

    def test_missing_args_exit_1(self):
        r = run_script("sdd-amend.py")
        self.assertEqual(r.returncode, 1)

    def test_missing_file_io_exit_1(self):
        r = run_script("sdd-amend.py", "list", str(self.dir / "no_existe.md"))
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
