"""Black-box tests para scripts/sdd-features-index.py.

Cubre los escenarios verificados en ROADMAP 5.4: genera _features.md desde
fuentes fixture, idempotencia byte-identica, --check exit 2 si desactualizado /
0 si en sync, --stdout no escribe, layout subcarpeta y plano legacy, estado
PENDIENTE_GENERACIÓN (feature en discovery sin carpeta), BLOQUEADA (marcador),
LISTA (limpio), y readiness autoritativo sobre el marcador-based.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


DISCOVERY = """\
# Feature Discovery: MiProducto

> PRD origen: prd.md

## Features identificadas

### F-001: Login
- **Descripción**: autenticacion de usuarios
- **Actor principal**: usuario
- **Scope (RFs)**: RF-1

### F-002: Perfil
- **Descripción**: gestion de perfil
- **Actor principal**: usuario
- **Scope (RFs)**: RF-2

## Trazabilidad RF → Feature

| RF | Título | Feature |
|---|---|---|
| RF-1 | Login | F-001 |
| RF-2 | Perfil | F-002 |
"""


def spec(fid, title, marker=""):
    return (
        f"# Spec: {title}\n\n"
        f"> Feature ID: {fid}\n\n"
        f"### HU-1: hu\n\n"
        f"### CA-001: ca ← HU-1\n"
        f"{marker}"
    )


class FeaturesIndexTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *flags):
        return run_script("sdd-features-index.py", self.dir, *flags)

    def test_generates_features_md(self):
        write(self.dir / "prj_discovery.md", DISCOVERY)
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = self.dir / "prj_features.md"
        self.assertTrue(out.exists())
        text = out.read_text(encoding="utf-8")
        self.assertIn("### F-001: Login", text)
        self.assertIn("### F-002: Perfil", text)
        # F-001 tiene spec -> LISTA; F-002 no -> PENDIENTE_GENERACIÓN
        self.assertIn("PENDIENTE_GENERACIÓN", text)

    def test_idempotent_byte_identical(self):
        write(self.dir / "prj_discovery.md", DISCOVERY)
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        self._run()
        first = (self.dir / "prj_features.md").read_text(encoding="utf-8")
        self._run()
        self.assertEqual(first, (self.dir / "prj_features.md").read_text(encoding="utf-8"),
                         "regenerar sin cambios debe dar bytes identicos")

    def test_check_in_sync_exit_0(self):
        write(self.dir / "prj_discovery.md", DISCOVERY)
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        self._run()
        r = self._run("--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("EN_SYNC", r.stdout)

    def test_check_stale_exit_2(self):
        write(self.dir / "prj_discovery.md", DISCOVERY)
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        self._run()
        # Cambiar la descripcion de F-001 dentro de la seccion parseada ->
        # el archivo en disco queda stale respecto a la regeneracion.
        write(self.dir / "prj_discovery.md",
              DISCOVERY.replace("autenticacion de usuarios",
                                "autenticacion y SSO de usuarios"))
        r = self._run("--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("DESACTUALIZADO", r.stderr)

    def test_stdout_does_not_write(self):
        write(self.dir / "prj_discovery.md", DISCOVERY)
        r = self._run("--stdout")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("### F-001", r.stdout)
        self.assertFalse((self.dir / "prj_features.md").exists(),
                         "--stdout no debe escribir el archivo")

    def test_marker_yields_bloqueada(self):
        write(self.dir / "prj_discovery.md", DISCOVERY)
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login", marker="\n[INCOMPLETO] falta HU\n"))
        self._run()
        text = (self.dir / "prj_features.md").read_text(encoding="utf-8")
        self.assertIn("BLOQUEADA", text)

    def test_legacy_flat_layout(self):
        write(self.dir / "prj_discovery.md", DISCOVERY)
        # layout plano: spec directamente en features/<nombre>/
        write(self.dir / "features" / "login" / "login_spec.md",
              spec("F-001", "Login"))
        self._run()
        text = (self.dir / "prj_features.md").read_text(encoding="utf-8")
        self.assertIn("features/login/login_spec.md", text)

    def test_readiness_overrides_marker_based(self):
        write(self.dir / "prj_discovery.md", DISCOVERY)
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        # readiness declara F-001 BLOQUEADA aunque su spec este limpio
        write(self.dir / "prj_readiness_report.md",
              "# Readiness\n\n## Matriz de readiness\n\n"
              "| Feature | Estado | Bloqueantes |\n"
              "|---|---|---|\n"
              "| F-001: Login | BLOQUEADA | conflicto ALTA con F-002 |\n")
        self._run()
        text = (self.dir / "prj_features.md").read_text(encoding="utf-8")
        self.assertIn("conflicto ALTA con F-002", text)

    def test_no_discovery_uses_specs_only(self):
        # fast-track standalone: sin discovery, solo specs presentes
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = list(self.dir.glob("*_features.md"))
        self.assertEqual(len(out), 1)
        self.assertIn("F-001", out[0].read_text(encoding="utf-8"))

    def test_not_a_directory_exit_1(self):
        r = run_script("sdd-features-index.py", self.dir / "no_existe")
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
