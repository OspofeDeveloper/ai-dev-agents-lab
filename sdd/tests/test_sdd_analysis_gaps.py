"""Black-box tests para scripts/sdd-analysis-gaps.py.

El script da la parte VERIFICABLE del gate de gaps del `_analysis.md` (DECISIONS
D-042): antes, "¿quedan `[CRÍTICO]` sin responder?" lo decidía un agente leyendo
prosa, y de esa lectura cuelgan dos ramas duras de `wf-spec-features-first`.
Verifica:
  - --check: críticos abiertos → CRITICAL_OPEN exit 2, con sus IDs.
  - --check: informativos abiertos NO bloquean (CRITICAL_ANSWERED exit 0).
  - --check: documento sin bloques de gap → VACUOUS exit 2 (guarda de D-037: no
    puede responder "0 abiertos" sobre algo que no ha sabido parsear).
  - --answer: sustituye SOLO la línea Respuesta del gap indicado.
  - --answer sobre gap ya respondido → exit 2 sin tocar el fichero (salvo --force).
  - --answer con ID inexistente → exit 2 listando los IDs válidos.
  - tolerancia a campos extra en el bloque (los informes reales añaden `Problema`).
  - IDs `[D-XXX]` de los delta analysis, no solo `[P-XXX]`.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402

HEAD = (
    "# Análisis SDD: Producto X\n\n"
    "## Puntos pendientes de validación con cliente\n\n"
    "> Las respuestas se escriben en este archivo.\n\n"
    "---\n\n"
)


def gap(gid, severity, answer="_(pendiente)_", extra_flags="", with_problema=False):
    """Bloque de gap en el formato SSoT de kb-gap-conventions."""
    block = f"### [{gid}][{severity}]{extra_flags} Título de {gid}\n\n"
    block += "- **Contexto**: dónde se detectó.\n"
    if with_problema:
        # Campo EXTRA que los informes reales añaden y la plantilla no contempla.
        block += "- **Problema**: por qué bloquea.\n"
    if severity == "CRÍTICO":
        block += "- **Afecta**: HU-001\n"
    block += "- **Pregunta para el cliente**: ¿pregunta concreta?\n"
    block += f"- **Respuesta**: {answer}\n"
    if severity == "INFORMATIVO":
        block += "- **Asunción por defecto**: se aplicará Y.\n"
    return block + "\n---\n\n"


class AnalysisGapsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, *blocks, name="prd_analysis.md"):
        path = self.root / name
        write(path, HEAD + "".join(blocks))
        return path

    def check(self, path, *flags):
        return run_script("sdd-analysis-gaps.py", path, "--check", *flags)

    def check_json(self, path):
        r = self.check(path, "--json")
        return r, json.loads(r.stdout)

    # === --check =========================================================
    def test_critical_open_is_blocking_and_lists_ids(self):
        path = self.make(gap("P-001", "CRÍTICO"),
                         gap("P-002", "CRÍTICO", answer="Sí, se puede."),
                         gap("P-003", "CRÍTICO"))
        r, data = self.check_json(path)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertEqual(data["verdict"], "CRITICAL_OPEN")
        self.assertEqual(data["critical_total"], 3)
        self.assertEqual(data["critical_open"], 2)
        self.assertEqual(data["critical_open_ids"], ["P-001", "P-003"])

    def test_informative_open_does_not_block(self):
        # [INFORMATIVO] nunca bloquea: aplica su asunción por defecto.
        path = self.make(gap("P-001", "CRÍTICO", answer="Respondido."),
                         gap("P-002", "INFORMATIVO"))
        r, data = self.check_json(path)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(data["verdict"], "CRITICAL_ANSWERED")
        self.assertEqual(data["informative_open"], 1)
        self.assertEqual(data["informative_open_ids"], ["P-002"])

    def test_vacuous_when_no_gap_blocks(self):
        # Guarda de D-037: sin bloques parseados NO se responde "0 abiertos".
        path = self.root / "prd.md"
        write(path, "# PRD\n\n## Alcance\n\n- El usuario puede registrar un gasto.\n")
        r, data = self.check_json(path)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertEqual(data["verdict"], "VACUOUS")

    def test_check_tolerates_extra_fields_and_flags(self):
        path = self.make(gap("P-001", "CRÍTICO", extra_flags="[PUEDE_REQUERIR_CR]",
                             with_problema=True))
        r, data = self.check_json(path)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(data["critical_open_ids"], ["P-001"])
        self.assertIn("PUEDE_REQUERIR_CR", data["gaps"][0]["flags"])

    def test_check_accepts_delta_analysis_ids(self):
        path = self.make(gap("D-001", "CRÍTICO"), name="feature_delta_analysis.md")
        r, data = self.check_json(path)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(data["critical_open_ids"], ["D-001"])

    # === --answer ========================================================
    def test_answer_replaces_only_that_line(self):
        path = self.make(gap("P-001", "CRÍTICO"), gap("P-002", "CRÍTICO"))
        before = path.read_text(encoding="utf-8")
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-001",
                       "No, solo ingresos y gastos.", "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        after = path.read_text(encoding="utf-8")
        changed = [(a, b) for a, b in zip(before.splitlines(), after.splitlines()) if a != b]
        self.assertEqual(len(changed), 1, f"cambió más de una línea: {changed}")
        self.assertIn("- **Respuesta**: No, solo ingresos y gastos.", after)
        data = json.loads(r.stdout)
        self.assertEqual(data["critical_open_ids"], ["P-002"])
        self.assertFalse(data["overwritten"])

    def test_answer_normalizes_whitespace_to_one_line(self):
        path = self.make(gap("P-001", "CRÍTICO"))
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-001",
                       "primera línea\nsegunda   línea")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("- **Respuesta**: primera línea segunda línea",
                      path.read_text(encoding="utf-8"))

    def test_answer_refuses_to_overwrite_without_force(self):
        path = self.make(gap("P-001", "CRÍTICO", answer="Respuesta humana previa."))
        before = path.read_text(encoding="utf-8")
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-001", "otra cosa")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--force", r.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), before, "escribió pese al fallo")

    def test_answer_overwrites_with_force(self):
        path = self.make(gap("P-001", "CRÍTICO", answer="Respuesta humana previa."))
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-001", "corregida",
                       "--force", "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(json.loads(r.stdout)["overwritten"])
        self.assertIn("- **Respuesta**: corregida", path.read_text(encoding="utf-8"))

    def test_answer_unknown_id_lists_valid_ones(self):
        path = self.make(gap("P-001", "CRÍTICO"), gap("P-002", "INFORMATIVO"))
        before = path.read_text(encoding="utf-8")
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-099", "x")
        self.assertEqual(r.returncode, 2)
        self.assertIn("P-001", r.stderr)
        self.assertIn("P-002", r.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_answer_on_document_without_gaps_fails(self):
        path = self.root / "prd.md"
        write(path, "# PRD\n\nSin gaps.\n")
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-001", "x")
        self.assertEqual(r.returncode, 2)

    def test_answer_empty_is_usage_error(self):
        path = self.make(gap("P-001", "CRÍTICO"))
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-001", "   ")
        self.assertEqual(r.returncode, 1)

    # === CLI =============================================================
    def test_check_and_answer_are_exclusive(self):
        path = self.make(gap("P-001", "CRÍTICO"))
        r = run_script("sdd-analysis-gaps.py", path, "--check", "--answer", "P-001", "x")
        self.assertEqual(r.returncode, 1)

    def test_no_mode_is_usage_error(self):
        path = self.make(gap("P-001", "CRÍTICO"))
        r = run_script("sdd-analysis-gaps.py", path)
        self.assertEqual(r.returncode, 1)

    def test_missing_file_is_io_error(self):
        r = run_script("sdd-analysis-gaps.py", self.root / "no-existe.md", "--check")
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
