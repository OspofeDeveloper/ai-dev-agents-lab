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
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import SDD_ROOT, run_script, write  # noqa: E402


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

    def test_pendiente_note_does_not_teach_a_command(self):
        # ROADMAP 11.10: `_features.md` lo lee una persona, y esta nota la escribe
        # el SCRIPT — no una plantilla, asi que el barrido de plantillas de 11.7 no
        # podia verla. Traia `/wf-spec-features-first <prd.md> --features F-00X`
        # literal. El ID de feature SI se queda: es como el usuario la nombra.
        write(self.dir / "prj_discovery.md", DISCOVERY)
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        self._run()
        text = (self.dir / "prj_features.md").read_text(encoding="utf-8")
        for line in text.splitlines():
            if "identificada en el discovery" not in line:
                continue
            self.assertNotIn("/wf-", line, f"la nota ensena un comando: {line}")
            self.assertNotIn("wf-spec", line, f"la nota nombra un workflow: {line}")
            self.assertIn("F-002", line, "la nota debe nombrar la feature")
            break
        else:
            self.fail("no se emitio la nota de PENDIENTE_GENERACIÓN")

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

    # === D-083: el mapa brownfield NO es un discovery ======================
    CODE_DISCOVERY = """\
# Mapa de capacidades: billing

> Evidencia base: commit abc1234
> Validación: pendiente

## Capacidades

### F-C-001: Cobro de suscripcion
- **Actor**: sistema
- **Superficie**: POST /billing/charge
"""

    def test_code_discovery_is_not_taken_as_discovery(self):
        """Adopcion (D-079): el mapa brownfield y el discovery del PRD conviven.

        `sorted()` daba el mapa por orden alfabetico (`billing_code_discovery.md`
        < `prd_discovery.md`), y el indice salia con el universo equivocado y el
        nombre equivocado.
        """
        write(self.dir / "billing_code_discovery.md", self.CODE_DISCOVERY)
        write(self.dir / "prj_discovery.md", DISCOVERY)
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.dir / "prj_features.md").exists(),
                        "el indice debe nombrarse por el discovery del PRD")
        self.assertFalse((self.dir / "billing_code_features.md").exists(),
                         "el mapa de capacidades no da nombre al indice")
        text = (self.dir / "prj_features.md").read_text(encoding="utf-8")
        self.assertIn("### F-002: Perfil", text, "el universo sale del discovery del PRD")
        self.assertNotIn("F-C-001", text)

    def test_only_code_discovery_falls_back_to_specs(self):
        """Brownfield puro: sin discovery de features, el indice sale de los specs."""
        write(self.dir / "billing_code_discovery.md", self.CODE_DISCOVERY)
        write(self.dir / "features" / "cobro" / "spec" / "cobro_spec.md",
              spec("F-C-001", "Cobro de suscripcion"))
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.dir / "billing_code_features.md").exists())
        out = next(self.dir.glob("*_features.md"))
        text = out.read_text(encoding="utf-8")
        self.assertIn("discovery=no", text,
                      "declarar `discovery=sí` sobre el mapa era declarar un discovery que no existe")
        self.assertIn("F-C-001", text)

    def test_adoption_keeps_existing_index_name_but_prd_universe(self):
        """Adopcion real: ya hay indice del brownfield cuando llega el PRD.

        El nombre de salida se hereda del indice existente —eso no cambia—; lo
        que no puede heredarse es el universo, que pasa a ser el del PRD.
        """
        write(self.dir / "billing_code_discovery.md", self.CODE_DISCOVERY)
        write(self.dir / "billing_code_features.md", "# indice viejo del brownfield\n")
        write(self.dir / "prj_discovery.md", DISCOVERY)
        write(self.dir / "features" / "login" / "spec" / "login_spec.md",
              spec("F-001", "Login"))
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.dir / "prj_features.md").exists(),
                         "no se crea un indice paralelo: se reescribe el que hay")
        text = (self.dir / "billing_code_features.md").read_text(encoding="utf-8")
        self.assertIn("### F-002: Perfil", text, "el universo sale del discovery del PRD")
        self.assertNotIn("F-C-001", text)

    def test_explicit_discovery_flag_is_respected(self):
        """El filtro es del barrido automatico: un `--discovery` explicito manda."""
        write(self.dir / "billing_code_discovery.md", self.CODE_DISCOVERY)
        write(self.dir / "features" / "cobro" / "spec" / "cobro_spec.md",
              spec("F-C-001", "Cobro de suscripcion"))
        r = self._run("--discovery", str(self.dir / "billing_code_discovery.md"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.dir / "billing_code_features.md").exists())

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


class RetiradaTest(unittest.TestCase):
    """El quinto estado (D-074): derivado del spec, y por encima del readiness."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        write(self.dir / "prj_discovery.md", DISCOVERY)

    def tearDown(self):
        self.tmp.cleanup()

    def _spec(self, extra_header="", marker=""):
        text = spec("F-001", "Login", marker).replace(
            "> Feature ID: F-001", "> Estado: RETIRADO\n> Retirada: CR-007 — ya no va\n"
                                  "> Feature ID: F-001" + extra_header)
        return write(self.dir / "features" / "login" / "spec" / "login_spec.md", text)

    def _index(self):
        r = run_script("sdd-features-index.py", self.dir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return (self.dir / "prj_features.md").read_text(encoding="utf-8")

    def test_retired_spec_yields_retirada(self):
        self._spec()
        out = self._index()
        self.assertIn("| F-001: Login | RETIRADA |", out)
        self.assertIn("CR-007", out, "la columna de bloqueantes lleva el cambio que la retira")

    def test_retirada_wins_over_the_readiness_verdict(self):
        """El readiness es autoritativo para todo... menos para resucitar una baja."""
        self._spec()
        write(self.dir / "prj_readiness_report.md",
              "## Matriz de readiness\n\n| Feature | Estado | Bloqueantes |\n"
              "|---|---|---|\n| F-001: Login | LISTA | — |\n")
        self.assertIn("| F-001: Login | RETIRADA |", self._index())

    def test_retirada_wins_over_markers(self):
        """Una feature retirada no esta BLOQUEADA: no hay nada que desbloquear."""
        self._spec(marker="\n[INCOMPLETO] falta decidir\n")
        self.assertIn("| F-001: Login | RETIRADA |", self._index())

    def test_still_idempotent_with_a_retired_feature(self):
        self._spec()
        first = self._index()
        self.assertEqual(first, self._index())


class SinValidarTest(unittest.TestCase):
    """El sello desmiente a LISTA, y solo a LISTA (D-077).

    `gate_spec_fiable` deniega el plan de un spec en BORRADOR (D-061). Un indice
    que lo diera por LISTA prometeria lo que el gate incumple una fase mas tarde.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        write(self.dir / "prj_discovery.md", DISCOVERY)

    def tearDown(self):
        self.tmp.cleanup()

    def _spec(self, estado=None, marker=""):
        text = spec("F-001", "Login", marker)
        if estado is not None:
            text = text.replace("> Feature ID: F-001",
                                f"> Estado: {estado}\n> Feature ID: F-001")
        return write(self.dir / "features" / "login" / "spec" / "login_spec.md", text)

    def _readiness(self, estado, bloqueantes="—"):
        write(self.dir / "prj_readiness_report.md",
              "## Matriz de readiness\n\n| Feature | Estado | Bloqueantes |\n"
              f"|---|---|---|\n| F-001: Login | {estado} | {bloqueantes} |\n")

    def _index(self):
        r = run_script("sdd-features-index.py", self.dir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return (self.dir / "prj_features.md").read_text(encoding="utf-8")

    def test_borrador_limpio_no_sale_lista(self):
        self._spec(estado="BORRADOR")
        out = self._index()
        self.assertIn("| F-001: Login | BLOQUEADA |", out)
        self.assertIn("pendiente de validación", out,
                      "el motivo dice que falta un paso, no que el spec este mal")

    def test_validado_limpio_sale_lista(self):
        self._spec(estado="VALIDADO")
        self.assertIn("| F-001: Login | LISTA |", self._index())

    def test_spec_legacy_sin_linea_estado_no_se_bloquea(self):
        """Politica conservadora: solo bloquea lo que se afirma (misma que status_sync)."""
        self._spec(estado=None)
        self.assertIn("| F-001: Login | LISTA |", self._index())

    def test_borrador_desmiente_un_readiness_que_dice_lista(self):
        """La cabecera del spec es mas fresca que el informe: un delta lo desella despues."""
        self._spec(estado="BORRADOR")
        self._readiness("LISTA")
        out = self._index()
        self.assertIn("| F-001: Login | BLOQUEADA |", out)
        self.assertIn("pendiente de validación", out)

    def test_borrador_respeta_los_demas_veredictos_del_readiness(self):
        """REQUIERE_CAMBIO_PRD ya no promete nada, y su motivo es mas informativo."""
        self._spec(estado="BORRADOR")
        self._readiness("REQUIERE_CAMBIO_PRD", "gobernanza: alcance derivado")
        out = self._index()
        self.assertIn("| F-001: Login | REQUIERE_CAMBIO_PRD |", out)
        self.assertIn("gobernanza: alcance derivado", out)

    def test_marcadores_ganan_al_sello_como_motivo(self):
        """Un spec con marcadores Y en borrador reporta los marcadores: es mas concreto."""
        self._spec(estado="BORRADOR", marker="\n[INCOMPLETO] falta decidir\n")
        out = self._index()
        self.assertIn("| F-001: Login | BLOQUEADA |", out)
        self.assertIn("marcadores", out)

    def test_retirada_gana_al_sello(self):
        """RETIRADO manda sobre todo (D-074), incluido el sello."""
        text = spec("F-001", "Login").replace(
            "> Feature ID: F-001",
            "> Estado: RETIRADO\n> Retirada: CR-007 — ya no va\n> Feature ID: F-001")
        write(self.dir / "features" / "login" / "spec" / "login_spec.md", text)
        self.assertIn("| F-001: Login | RETIRADA |", self._index())

    def test_sigue_siendo_idempotente(self):
        self._spec(estado="BORRADOR")
        self.assertEqual(self._index(), self._index())


class CanonStatesBackstopTest(unittest.TestCase):
    """Las copias del vocabulario de estados no divergen ([[D-069]]).

    `CANON_STATES` vive en `sdd-features-index.py`. Cuando una copia se queda
    corta el sintoma no es cosmetico: `sdd-project-status.py` filtra por su propia
    tupla y la feature con un estado que no reconoce **desaparece** del informe.
    Este test existe porque la lista se quedo corta seis veces en dos dias.
    """

    def _canon(self):
        text = (SDD_ROOT / "scripts" / "sdd-features-index.py").read_text(encoding="utf-8")
        m = re.search(r"CANON_STATES\s*=\s*\((?P<body>.*?)\)", text, re.DOTALL)
        assert m, "no se encuentra CANON_STATES"
        return set(re.findall(r'"([A-ZÓ_]+)"', m.group("body")))

    def test_project_status_knows_every_canonical_state(self):
        canon = self._canon()
        text = (SDD_ROOT / "scripts" / "sdd-project-status.py").read_text(encoding="utf-8")
        m = re.search(r'if fm and cells\[1\] in \((?P<body>.*?)\):', text, re.DOTALL)
        self.assertIsNotNone(m, "no se encuentra el filtro de estados de features_resumen()")
        copia = set(re.findall(r'"([A-ZÓ_]+)"', m.group("body")))
        self.assertEqual(canon, copia,
                         "sdd-project-status.py filtra por una copia de CANON_STATES: "
                         "un estado que le falte hace DESAPARECER la feature del informe")

    def test_the_canonical_prose_enumerates_every_state(self):
        canon = self._canon()
        kb = (SDD_ROOT / "pipeline" / "spec" / "skills" / "kb-decompose-expert"
              / "SKILL.md").read_text(encoding="utf-8")
        linea = [l for l in kb.splitlines() if l.startswith("Estados canónicos")]
        self.assertEqual(len(linea), 1, "se espera una sola linea canonica en kb-decompose-expert")
        prosa = set(re.findall(r"`([A-ZÓ_]+)`", linea[0]))
        self.assertEqual(canon, prosa,
                         "la enumeracion en prosa de kb-decompose-expert diverge de CANON_STATES")


if __name__ == "__main__":
    unittest.main()
