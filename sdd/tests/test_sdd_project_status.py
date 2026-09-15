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


class RetiradaTest(unittest.TestCase):
    """Una feature dada de baja (D-074): visible, sin accion y fuera del foco."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        write(self.dir / "prj_features.md",
              "# Features Index: MiProducto\n\n## Resumen de estado\n\n"
              "| Feature | Estado | Bloqueantes |\n|---|---|---|\n"
              "| F-001: Login | LISTA | — |\n"
              "| F-002: Pagos | RETIRADA | CR-007 — ya no se cobra |\n")
        write(self.dir / "features" / "Login" / "spec" / "login_spec.md", spec("F-001", "Login"))
        f = self.dir / "features" / "Pagos"
        write(f / "spec" / "pagos_spec.md",
              spec("F-002", "Pagos").replace("> Feature ID: F-002",
                                             "> Estado: RETIRADO\n> Feature ID: F-002"))
        # Artefactos downstream que la cascada de fases pintaria como "en marcha".
        write(f / "plan" / "pagos_plan.md", "# Plan: Pagos\n> Estado: VALIDADO\n")
        write(f / "tasks" / "pagos_tasks.md", "# Tasks: Pagos\n## T-001: hacer\n")

    def tearDown(self):
        self.tmp.cleanup()

    def _out(self):
        r = run_script("sdd-project-status.py", self.dir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def test_retired_feature_is_listed_not_dropped(self):
        out = self._out()
        self.assertIn("F-002: Pagos", out,
                      "un estado no reconocido la haria desaparecer del informe")
        self.assertIn("RETIRADA", out)

    def test_retirement_beats_the_phase_cascade(self):
        """Tiene plan y tasks en disco: sin la rama de baja se pintaria como fase Tasks."""
        fila = [l for l in self._out().splitlines() if "F-002: Pagos" in l][0]
        self.assertIn("| Retirada |", fila)
        self.assertNotIn("Tasks", fila)

    def test_retired_feature_asks_for_nothing(self):
        fila = [l for l in self._out().splitlines() if "F-002: Pagos" in l][0]
        self.assertTrue(fila.rstrip().endswith("| — |"),
                        f"una feature de baja no tiene siguiente accion: {fila}")

    def test_retired_feature_is_out_of_the_focus_list(self):
        out = self._out()
        foco = out.split("## Siguiente foco", 1)[1]
        self.assertNotIn("F-002", foco)
        self.assertIn("F-001", foco, "las vivas siguen en el foco")


class SinValidarTest(unittest.TestCase):
    """El sello del spec tambien decide aqui (D-077).

    `gate_spec_fiable` deniega el plan de un spec en BORRADOR (D-061), asi que
    anunciar "LISTA → /wf-prepare-plan" manda al usuario contra el gate.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _build(self, estado_spec=None, estado_idx="LISTA", marker=""):
        write(self.dir / "prj_features.md",
              "# Features Index: MiProducto\n\n## Resumen de estado\n\n"
              "| Feature | Estado | Bloqueantes |\n|---|---|---|\n"
              f"| F-001: Login | {estado_idx} | — |\n")
        text = spec("F-001", "Login") + marker
        if estado_spec is not None:
            text = text.replace("> Feature ID: F-001",
                                f"> Estado: {estado_spec}\n> Feature ID: F-001")
        write(self.dir / "features" / "login" / "spec" / "login_spec.md", text)

    def _fila(self):
        r = run_script("sdd-project-status.py", self.dir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        filas = [l for l in r.stdout.splitlines()
                 if l.startswith("| F-001:") and "|" in l[8:]]
        self.assertTrue(filas, f"sin fila para F-001 en:\n{r.stdout}")
        return filas[0]

    def test_borrador_no_se_anuncia_como_lista(self):
        self._build(estado_spec="BORRADOR")
        fila = self._fila()
        self.assertIn("BLOQUEADA", fila)
        self.assertIn("pendiente de validación", fila)
        self.assertNotIn("/wf-prepare-plan", fila,
                         "anunciar el plan sobre un spec sin sellar manda contra el gate")

    def test_la_accion_es_validar_no_responder_gaps(self):
        """Sin gaps que responder, mandar a resolverlos es un callejon sin salida."""
        self._build(estado_spec="BORRADOR")
        self.assertIn("/wf-spec-validate", self._fila())

    def test_validado_sigue_anunciando_el_plan(self):
        self._build(estado_spec="VALIDADO")
        fila = self._fila()
        self.assertIn("LISTA", fila)
        self.assertIn("/wf-prepare-plan", fila)

    def test_spec_legacy_sin_estado_no_cambia(self):
        """Politica conservadora: solo bloquea lo que se afirma."""
        self._build(estado_spec=None)
        self.assertIn("/wf-prepare-plan", self._fila())

    def test_marcadores_mandan_sobre_el_sello(self):
        """Con gaps abiertos la accion sigue siendo resolverlos: validar lo rechazaria."""
        self._build(estado_spec="BORRADOR", estado_idx="BLOQUEADA",
                    marker="\n[INCOMPLETO] falta decidir\n")
        fila = self._fila()
        self.assertIn("BLOQUEADA", fila)
        self.assertIn("gap", fila)


class SinValidarMotivoBackstopTest(unittest.TestCase):
    """Los dos scripts escriben la MISMA cadena de motivo (D-077, precedente D-069).

    `sdd-features-index.py` la escribe en `_features.md`; `sdd-project-status.py`
    la busca ahi para elegir la accion. Si divergen, el estado se sigue pintando
    bien y la accion vuelve en silencio a "responder gaps" — el callejon sin salida
    que este motivo existe para evitar.
    """

    def _const(self, script):
        import re
        text = (Path(__file__).resolve().parent.parent / "scripts" / script
                ).read_text(encoding="utf-8")
        m = re.search(r'^SIN_VALIDAR_MOTIVO\s*=\s*"(?P<v>[^"]+)"', text, re.MULTILINE)
        assert m, f"no se encuentra SIN_VALIDAR_MOTIVO en {script}"
        return m.group("v")

    def test_las_dos_copias_coinciden(self):
        self.assertEqual(self._const("sdd-features-index.py"),
                         self._const("sdd-project-status.py"))


if __name__ == "__main__":
    unittest.main()
