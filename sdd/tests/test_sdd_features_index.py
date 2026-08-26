"""Black-box tests para scripts/sdd-features-index.py.

Cubre los escenarios verificados en ROADMAP 5.4: genera _features.md desde
fuentes fixture, idempotencia byte-identica, --check exit 2 si desactualizado /
0 si en sync, --stdout no escribe, layout subcarpeta y plano legacy, estado
PENDIENTE_GENERACIÓN (feature en discovery sin carpeta), BLOQUEADA (marcador),
LISTA (limpio), y readiness autoritativo sobre el marcador-based.

Cubre además el cruce de frontera de topología (D-046): en `authoring`
(`artifacts.prd` != `artifacts.spec`) el discovery vive con el PRD, no en la
raíz spec — el índice debe encontrarlo por `.sdd/project-init.json` o por
`--discovery`, y declararlo en voz alta cuando no lo encuentra.
"""
from __future__ import annotations

import json
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

    # ── Cruce de frontera de topología (D-046) ────────────────────────────

    def _authoring(self):
        """Topología `authoring`: discovery en prd/, specs e índice en spec/."""
        write(self.dir / ".sdd" / "project-init.json",
              json.dumps({"topology": "authoring",
                          "artifacts": {"prd": "prd", "spec": "spec"}}))
        write(self.dir / "prd" / "prd_discovery.md", DISCOVERY)
        write(self.dir / "spec" / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        return self.dir / "spec"

    def test_authoring_finds_discovery_via_project_init(self):
        spec_root = self._authoring()
        r = run_script("sdd-features-index.py", spec_root)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = (spec_root / "spec_features.md").read_text(encoding="utf-8")
        # Sin el cruce de frontera, F-002 (en discovery, sin spec) desaparecía.
        self.assertIn("### F-002: Perfil", text)
        self.assertIn("PENDIENTE_GENERACIÓN", text)
        self.assertIn("discovery=sí", text)
        # El nombre de proyecto sale del discovery, no del nombre del directorio.
        self.assertIn("# Features Index: MiProducto", text)

    def test_external_discovery_does_not_rename_the_index(self):
        # El índice conserva el nombre derivado de SU raíz (spec_features.md),
        # no el del basename del PRD (prd_features.md): vive en otra raíz.
        spec_root = self._authoring()
        run_script("sdd-features-index.py", spec_root)
        self.assertTrue((spec_root / "spec_features.md").exists())
        self.assertFalse((spec_root / "prd_features.md").exists())
        self.assertIn("> Discovery: `../prd/prd_discovery.md`",
                      (spec_root / "spec_features.md").read_text(encoding="utf-8"))

    def test_explicit_discovery_flag_wins(self):
        write(self.dir / "otra" / "x_discovery.md", DISCOVERY)
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        r = self._run("--discovery", str(self.dir / "otra" / "x_discovery.md"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = (self.dir / f"{self.dir.name}_features.md").read_text(encoding="utf-8")
        self.assertIn("### F-002: Perfil", text)

    def test_explicit_discovery_missing_exit_1(self):
        r = self._run("--discovery", str(self.dir / "no_existe.md"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("--discovery no existe", r.stderr)

    def test_local_discovery_beats_project_init(self):
        # Si <dir> tiene su propio discovery, no se cruza la frontera.
        spec_root = self._authoring()
        write(spec_root / "local_discovery.md",
              DISCOVERY.replace("# Feature Discovery: MiProducto",
                                "# Feature Discovery: Local"))
        run_script("sdd-features-index.py", spec_root)
        text = (spec_root / "local_features.md").read_text(encoding="utf-8")
        self.assertIn("# Features Index: Local", text)

    def test_missing_discovery_is_declared_not_silent(self):
        # La política conservadora se mantiene, pero deja de ser silenciosa:
        # el aviso viaja en el artefacto Y por stderr.
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = (self.dir / f"{self.dir.name}_features.md").read_text(encoding="utf-8")
        self.assertIn("SIN DISCOVERY", text)
        self.assertIn("sin discovery", r.stderr)

    def test_no_warning_when_no_specs_either(self):
        # Raíz vacía: no hay nada que el índice pueda estar ocultando.
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = (self.dir / f"{self.dir.name}_features.md").read_text(encoding="utf-8")
        self.assertNotIn("SIN DISCOVERY", text)

    def test_authoring_index_is_idempotent(self):
        spec_root = self._authoring()
        run_script("sdd-features-index.py", spec_root)
        first = (spec_root / "spec_features.md").read_text(encoding="utf-8")
        run_script("sdd-features-index.py", spec_root)
        self.assertEqual(first,
                         (spec_root / "spec_features.md").read_text(encoding="utf-8"))
        r = run_script("sdd-features-index.py", spec_root, "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_broken_project_init_does_not_crash(self):
        write(self.dir / ".sdd" / "project-init.json", "{ no es json")
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
