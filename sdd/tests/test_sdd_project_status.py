"""Black-box tests para scripts/sdd-project-status.py.

Informe PM read-only (ROADMAP 2.6): escanea features/ y agrega el estado sellado
en cada artefacto. Verifica:
  - Fase alcanzada por presencia de artefactos: Spec / Plan / Tasks / QA /
    Cerrada, y PENDIENTE_GENERACIÓN (feature del índice sin carpeta).
  - Layout subcarpeta y plano legacy.
  - READ-ONLY: el árbol de artefactos es byte-idéntico antes/después (salvo el
    --output explícito).
  - --output escribe el informe; estructura de la tabla de salida.
  - Args inválidos (exit 1).
"""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


FEATURES_MD = """\
# Features Index: MiProducto

## Resumen de estado

| Feature | Estado | Bloqueantes |
|---|---|---|
| F-001: Login | LISTA | — |
| F-002: Perfil | LISTA | — |
| F-003: Pagos | LISTA | — |
| F-004: Reportes | LISTA | — |
| F-005: Ajustes | PENDIENTE_GENERACIÓN | sin spec |
"""


def spec(fid, title):
    return (
        f"# Spec: {title}\n\n"
        f"> Feature ID: {fid}\n\n"
        f"### HU-1: hu\n### CA-001: ca ← HU-1\n"
    )


def plan(estado="VALIDADO"):
    return (
        "# Plan: X\n\n"
        f"**Estado:** {estado}\n\n"
        "## Arquitectura\n\nImplementa CA-001.\n"
    )


def tasks(done, total):
    rows = "\n".join(
        f"| T-{i:03d} | {'HECHA' if i <= done else 'PENDIENTE'} | x |"
        for i in range(1, total + 1)
    )
    return (
        "# Tasks: X\n\n## Progreso\n\n"
        "| Task | Estado | Owner |\n|---|---|---|\n"
        f"{rows}\n"
    )


def qa(verdict="APTO"):
    return f"# QA Report\n\n> Veredicto: {verdict}\n\n## Cobertura\nok\n"


def tree_digest(root: Path) -> dict:
    """{ruta_relativa: sha256} de todos los ficheros bajo root (para read-only check)."""
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


class MultiFeatureTest(unittest.TestCase):
    """Árbol multi-feature cubriendo cada fase alcanzada."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        write(self.dir / "prj_features.md", FEATURES_MD)
        # F-001: solo Spec -> fase Spec
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        # F-002: Spec + Plan VALIDADO -> fase Plan
        write(self.dir / "features" / "perfil" / "spec" / "perfil_spec.md",
              spec("F-002", "Perfil"))
        write(self.dir / "features" / "perfil" / "plan" / "perfil_plan.md", plan())
        # F-003: hasta Tasks (parcial) -> fase Tasks
        write(self.dir / "features" / "pagos" / "spec" / "pagos_spec.md",
              spec("F-003", "Pagos"))
        write(self.dir / "features" / "pagos" / "plan" / "pagos_plan.md", plan())
        write(self.dir / "features" / "pagos" / "tasks" / "pagos_tasks.md",
              tasks(done=1, total=3))
        # F-004: QA APTO -> fase Cerrada (sin release)
        write(self.dir / "features" / "reportes" / "spec" / "reportes_spec.md",
              spec("F-004", "Reportes"))
        write(self.dir / "features" / "reportes" / "tasks" / "reportes_qa_report.md",
              qa("APTO"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_phases_detected(self):
        r = run_script("sdd-project-status.py", self.dir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = r.stdout
        # F-001 Spec, F-002 Plan, F-003 Tasks, F-004 Cerrada, F-005 PENDIENTE
        self.assertIn("F-001", out)
        self.assertRegex(out, r"F-001:.*\|\s*Spec\s*\|")
        self.assertRegex(out, r"F-002:.*\|\s*Plan\s*\|")
        self.assertRegex(out, r"F-003:.*\|\s*Tasks\s*\|")
        self.assertRegex(out, r"F-004:.*\|\s*Cerrada\s*\|")

    def test_pending_generation_without_folder(self):
        r = run_script("sdd-project-status.py", self.dir)
        self.assertIn("F-005", r.stdout)
        self.assertIn("PENDIENTE_GENERACIÓN", r.stdout)

    def test_tasks_progress_shown(self):
        r = run_script("sdd-project-status.py", self.dir)
        self.assertIn("1/3 HECHA", r.stdout)

    def test_report_has_table_header(self):
        r = run_script("sdd-project-status.py", self.dir)
        self.assertIn("## Por feature", r.stdout)
        self.assertIn("| Feature | Fase | Estado | Bloqueo | Siguiente acción |", r.stdout)

    def test_is_read_only(self):
        before = tree_digest(self.dir)
        r = run_script("sdd-project-status.py", self.dir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        after = tree_digest(self.dir)
        self.assertEqual(before, after,
                         "el informe NO debe escribir ni mutar ningún artefacto")

    def test_output_writes_file(self):
        out_file = self.dir / "status.md"
        before = tree_digest(self.dir)
        r = run_script("sdd-project-status.py", self.dir, "--output", out_file)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(out_file.exists())
        # Lo único nuevo en el árbol es el --output; nada más cambió.
        after = tree_digest(self.dir)
        after.pop("status.md", None)
        self.assertEqual(before, after,
                         "salvo el --output, no debe tocar el resto del árbol")


class FlatLayoutTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_flat_layout_plan_phase(self):
        # layout plano: spec y plan directamente en features/<n>/
        write(self.dir / "features" / "login" / "login_spec.md", spec("F-001", "Login"))
        write(self.dir / "features" / "login" / "login_plan.md", plan("BORRADOR"))
        r = run_script("sdd-project-status.py", self.dir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertRegex(r.stdout, r"F-001.*\|\s*Plan\s*\|")
        self.assertIn("BORRADOR", r.stdout)


class EmptyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_features_still_succeeds(self):
        r = run_script("sdd-project-status.py", self.dir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Estado del proyecto", r.stdout)


class UsageTest(unittest.TestCase):
    def test_no_args_exit_1(self):
        r = run_script("sdd-project-status.py")
        self.assertEqual(r.returncode, 1)

    def test_not_a_directory_exit_1(self):
        r = run_script("sdd-project-status.py", "/no/existe/dir")
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
