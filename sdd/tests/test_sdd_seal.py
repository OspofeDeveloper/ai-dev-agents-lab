"""Black-box tests para scripts/sdd-seal.py.

Cubre: sellado de un plan sellable, rechazo de planes no sellables (CA sin
cubrir, [INFERIDO]/[CRITICO]/[INCOMPLETO] en el spec), idempotencia del sellado,
deteccion de tamper (editar el plan tras sellar invalida la re-verificacion),
--unseal, y deuda tecnica (TD) aprobada vs pendiente.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


SPEC_CLEAN = """\
# Spec: Login

> Feature ID: F-001

### HU-1: como usuario quiero entrar

### CA-001: login OK ← HU-1
Dado credenciales validas, entra.

### CA-002: login KO ← HU-1
Dado credenciales invalidas, error.
"""


def plan_text(spec_rel="login_spec.md", estado="BORRADOR",
              cas=("CA-001", "CA-002"), include_gaps=True, extra=""):
    """Construye un plan SDD parametrizable."""
    refs = "\n".join(f"- Implementa {ca}." for ca in cas)
    gaps = ""
    if include_gaps:
        gaps = (
            "\n**DESIGN_GAPs:** ninguno\n"
            "**TECH_GAPs:** ninguno\n"
            "**TRACE_GAPs:** ninguno\n"
            "**PLAN_GAPs:** ninguno\n"
        )
    return (
        f"# Plan: Login\n\n"
        f"> Spec origen: `{spec_rel}`\n"
        f"**Estado:** {estado}\n\n"
        f"## Arquitectura\n\n{refs}\n\n"
        f"{extra}"
        f"## Checklist de Trazabilidad\n\n"
        f"Todos los CAs cubiertos.\n"
        f"{gaps}"
    )


class SealableTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.spec = write(self.dir / "login_spec.md", SPEC_CLEAN)
        self.plan = write(self.dir / "login_plan.md", plan_text())

    def tearDown(self):
        self.tmp.cleanup()

    def test_check_passes_for_sealable_plan(self):
        r = run_script("sdd-seal.py", "plan", self.plan, "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("sellable", r.stdout)
        # --check no debe escribir: el estado sigue BORRADOR
        self.assertIn("BORRADOR", self.plan.read_text(encoding="utf-8"))

    def test_seal_writes_validado(self):
        r = run_script("sdd-seal.py", "plan", self.plan, "--seal")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("VALIDADO", self.plan.read_text(encoding="utf-8"))

    def test_seal_is_idempotent(self):
        run_script("sdd-seal.py", "plan", self.plan, "--seal")
        first = self.plan.read_text(encoding="utf-8")
        r = run_script("sdd-seal.py", "plan", self.plan, "--seal")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(first, self.plan.read_text(encoding="utf-8"),
                         "re-sellar un plan ya VALIDADO debe ser byte-identico")

    def test_unseal_downgrades_from_validado(self):
        """"Siempre" no: desde RETIRADO se deniega (ver RetireTest, D-078)."""
        run_script("sdd-seal.py", "plan", self.plan, "--seal")
        r = run_script("sdd-seal.py", "plan", self.plan, "--unseal")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("BORRADOR", self.plan.read_text(encoding="utf-8"))

    def test_tamper_detection_after_seal(self):
        """Editar el spec tras sellar (introducir [INFERIDO]) -> --check falla (2)."""
        run_script("sdd-seal.py", "plan", self.plan, "--seal")
        # Tamper: degradamos el spec origen tras el sello.
        self.spec.write_text(SPEC_CLEAN + "\n### CA-003: extra [INFERIDO] ← HU-1\n",
                             encoding="utf-8")
        r = run_script("sdd-seal.py", "plan", self.plan, "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("INFERIDO", r.stdout)

    def test_tamper_uncovered_ca_after_seal(self):
        """Anadir un CA nuevo al spec que el plan no cubre -> --check falla."""
        run_script("sdd-seal.py", "plan", self.plan, "--seal")
        self.spec.write_text(SPEC_CLEAN + "\n### CA-009: nuevo ← HU-1\nNo cubierto.\n",
                             encoding="utf-8")
        r = run_script("sdd-seal.py", "plan", self.plan, "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("CA-009", r.stdout)


class NonSealableTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _spec(self, content):
        return write(self.dir / "login_spec.md", content)

    def test_uncovered_ca_rejected(self):
        self._spec(SPEC_CLEAN)
        # El plan solo cubre CA-001
        write(self.dir / "login_plan.md", plan_text(cas=("CA-001",)))
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("CA-002", r.stdout)

    def test_spec_with_inferido_rejected(self):
        self._spec(SPEC_CLEAN + "\n### CA-003: x [INFERIDO] ← HU-1\n")
        write(self.dir / "login_plan.md", plan_text(cas=("CA-001", "CA-002", "CA-003")))
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("INFERIDO", r.stdout)

    def test_spec_with_critico_rejected(self):
        self._spec(SPEC_CLEAN + "\n[CRÍTICO] falta info\n")
        write(self.dir / "login_plan.md", plan_text())
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("CRÍTICO", r.stdout)

    def test_plan_with_incompleto_rejected(self):
        self._spec(SPEC_CLEAN)
        write(self.dir / "login_plan.md", plan_text(extra="[INCOMPLETO] falta diseno\n\n"))
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("INCOMPLETO", r.stdout)

    def test_open_gap_rejected(self):
        self._spec(SPEC_CLEAN)
        plan = plan_text(include_gaps=False) + (
            "\n**DESIGN_GAPs:** ninguno\n"
            "**TECH_GAPs:** falta definir cache\n"
            "**TRACE_GAPs:** ninguno\n"
            "**PLAN_GAPs:** ninguno\n"
        )
        write(self.dir / "login_plan.md", plan)
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("TECH_GAPs", r.stdout)

    def test_unresolvable_spec_origin_rejected(self):
        write(self.dir / "login_plan.md", plan_text(spec_rel="no_existe_spec.md"))
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_pending_td_blocks(self):
        self._spec(SPEC_CLEAN)
        td = (
            "### TD-001: cache diferida\n"
            "- **Decisión:** no cachear ahora\n"
            "- **A pesar de:** la latencia\n"
            "- **Riesgo asumido:** lentitud en picos\n"
            "- **Queda pendiente:** anadir cache\n"
            "- **Componentes afectados:** API\n"
            "- **Aprobada por:** PENDIENTE\n\n"
        )
        write(self.dir / "login_plan.md", plan_text(extra=td))
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("TD-001", r.stdout)

    def test_approved_td_does_not_block(self):
        self._spec(SPEC_CLEAN)
        td = (
            "### TD-001: cache diferida\n"
            "- **Decisión:** no cachear ahora\n"
            "- **A pesar de:** la latencia\n"
            "- **Riesgo asumido:** lentitud en picos\n"
            "- **Queda pendiente:** anadir cache\n"
            "- **Componentes afectados:** API\n"
            "- **Aprobada por:** Oscar (PM)\n\n"
        )
        write(self.dir / "login_plan.md", plan_text(extra=td))
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class UsageTest(unittest.TestCase):
    def test_bad_args_exit_1(self):
        r = run_script("sdd-seal.py", "plan", "x.md", "--nope")
        self.assertEqual(r.returncode, 1)



class SealSpecTest(unittest.TestCase):
    """D-061: el spec gana estado operativo, con el mismo reparto que el plan."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def spec(self, extra="", estado="BORRADOR", header=True):
        cab = ("> Feature ID: F-001\n> Origen de alcance: Documento fuente\n" if header else "")
        body = (f"# Spec: x\n\n> Estado: {estado}\n{cab}> status_sync: unknown\n\n"
                "## Historias\n\n### HU-001: Algo\n\n"
                "## Criterios\n\n### CA-001: Se cumple ← HU-001\n" + extra)
        p = self.dir / "f_spec.md"
        p.write_text(body, encoding="utf-8")
        return p

    def run_seal(self, path, mode):
        return run_script("sdd-seal.py", "spec", str(path), mode)

    def run_seal_approved(self, path, valor):
        return run_script("sdd-seal.py", "spec", str(path), "--seal",
                          "--approved-by", valor)

    def test_clean_spec_is_sealable(self):
        p = self.spec()
        r = self.run_seal(p, "--seal")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Estado: VALIDADO", p.read_text(encoding="utf-8"))

    def test_answered_critical_does_not_block(self):
        """El bloque de un critico respondido se conserva (D-054) y no bloquea."""
        p = self.spec("\n## Items Pendientes\n\n### [P-011][CRÍTICO] Resuelto\n"
                      "- **Respuesta**: el usuario dijo que si.\n")
        self.assertEqual(self.run_seal(p, "--seal").returncode, 0)

    def test_open_critical_blocks_and_downgrades(self):
        p = self.spec("\n## Items Pendientes\n\n### [P-011][CRÍTICO] Abierto\n"
                      "- **Respuesta**: _(pendiente)_\n", estado="VALIDADO")
        r = self.run_seal(p, "--seal")
        self.assertEqual(r.returncode, 2)
        self.assertIn("P-011", r.stdout)
        self.assertIn("Estado: BORRADOR", p.read_text(encoding="utf-8"))

    # --- D-066: la cabecera declara lo que los derivados leen ---

    def test_header_fields_missing_blocks(self):
        """Sin `Feature ID` / `Origen de alcance` el spec no se sella.

        Su ausencia no rompe nada de forma visible: `sdd-features-index.py` no
        los emite y la feature sale incompleta —o no sale— de un indice con
        apariencia de correcto. Es el modo de fallo que D-046 declaro inaceptable.
        """
        p = self.spec(header=False)
        r = self.run_seal(p, "--seal")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("Feature ID", r.stdout)
        self.assertIn("Origen de alcance", r.stdout)

    def test_header_fields_present_is_sealable(self):
        """El delta: mismo spec con la cabecera completa, sellable."""
        self.assertEqual(self.run_seal(self.spec(), "--seal").returncode, 0)

    def test_header_fields_accept_the_bold_form(self):
        """La cabecera de caracterizacion los escribe en negrita; tambien valen."""
        p = self.dir / "f_spec.md"
        p.write_text("# Spec: x\n\n> **Estado:** BORRADOR\n> **Feature ID:** F-C-001\n"
                     "> **Origen de alcance:** characterization\n\n"
                     "## H\n\n### HU-001: a\n\n### CA-001: b \u2190 HU-001\n",
                     encoding="utf-8")
        r = self.run_seal(p, "--seal")
        self.assertEqual(r.returncode, 0, r.stdout)

    # --- D-065: quien valido el spec consta, y lo estampa el script ---

    def test_seal_stamps_human_approval(self):
        """Regla 10: el gate de sellado registra QUIEN aprobo.

        Lo escribe el script, no el hilo principal — mismo reparto que el PRD
        (`sdd-prd-apply.py --seal "<valor>"`), asi main no escribe contenido en
        el artefacto (D-060).
        """
        p = self.spec()
        r = self.run_seal_approved(p, "Ana Ruiz (QA) (2026-09-09)")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = p.read_text(encoding="utf-8")
        self.assertIn("Estado: VALIDADO", text)
        self.assertIn("Aprobado por: Ana Ruiz (QA) (2026-09-09)", text)

    def test_approval_line_clones_the_estado_format(self):
        """La linea nueva calca el formato de `Estado:`, no lo reconstruye."""
        for raw in ("> Estado: BORRADOR", "- Estado: BORRADOR",
                    "**Estado:** BORRADOR", "**Estado: BORRADOR**"):
            p = self.dir / "f_spec.md"
            p.write_text("# Spec: x\n\n" + raw + "\n> Feature ID: F-001\n"
                         "> Origen de alcance: Documento fuente\n"
                         "> status_sync: unknown\n\n"
                         "## H\n\n### HU-001: a\n\n### CA-001: b \u2190 HU-001\n",
                         encoding="utf-8")
            self.run_seal_approved(p, "Ana (2026-09-09)")
            lines = p.read_text(encoding="utf-8").splitlines()
            i = next(n for n, l in enumerate(lines) if "Estado" in l)
            estado, aprobado = lines[i], lines[i + 1]
            self.assertIn("Aprobado por", aprobado, f"no se estampo junto a {raw!r}")
            # Mismo adorno: lo que rodea a la etiqueta es identico.
            self.assertEqual(estado.split("Estado")[0], aprobado.split("Aprobado por")[0],
                             f"el prefijo no se hereda con {raw!r}")
            self.assertEqual(estado.endswith("**"), aprobado.endswith("**"),
                             f"el sufijo no se hereda con {raw!r}")

    def test_reseal_overwrites_the_approval_instead_of_duplicating(self):
        p = self.spec()
        self.run_seal_approved(p, "Ana (2026-09-09)")
        self.run_seal_approved(p, "Luis (2026-09-10)")
        text = p.read_text(encoding="utf-8")
        self.assertEqual(text.count("Aprobado por"), 1, "se duplico la linea de aprobacion")
        self.assertIn("Luis (2026-09-10)", text)

    def test_seal_without_approval_leaves_the_line_untouched(self):
        """Sellar sin el dato humano no lo inventa ni lo borra."""
        p = self.spec()
        self.run_seal_approved(p, "Ana (2026-09-09)")
        run_script("sdd-seal.py", "spec", str(p), "--seal")
        self.assertIn("Aprobado por: Ana (2026-09-09)", p.read_text(encoding="utf-8"))

    def test_approval_needs_a_successful_seal(self):
        """Un spec que no pasa las condiciones no tiene aprobacion que registrar."""
        p = self.spec("\n> \u26a0 [INCOMPLETO] \u2014 pendiente.\n")
        r = self.run_seal_approved(p, "Ana (2026-09-09)")
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Aprobado por", p.read_text(encoding="utf-8"))

    def test_approved_by_only_with_seal(self):
        r = run_script("sdd-seal.py", "spec", str(self.spec()), "--check",
                       "--approved-by", "Ana")
        self.assertEqual(r.returncode, 1, "deberia rechazarse: solo aplica con --seal")

    # --- D-063: toda asuncion aplicada en nombre del usuario deja rastro ---

    INFO_GAP = ("\n## Items Pendientes\n\n### [P-020][INFORMATIVO] Formato de la fecha\n"
                "- **Contexto**: no se dice como se muestra\n"
                "- **Respuesta**: _(pendiente)_\n"
                "- **Asunción por defecto**: formato local corto.\n")

    def test_applied_assumption_without_record_blocks(self):
        """Un [INFORMATIVO] sin responder YA decidio en nombre del usuario.

        Su asuncion por defecto entra en los CAs como si alguien la hubiera
        elegido; sellar sin que eso sea visible es declarar validada una
        decision de producto que nadie vio.
        """
        p = self.spec(self.INFO_GAP)
        r = self.run_seal(p, "--seal")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("P-020", r.stdout)
        self.assertIn("Estado: BORRADOR", p.read_text(encoding="utf-8"))

    def test_applied_assumption_with_record_is_sealable(self):
        """Mismo spec + la entrada que lo cita: sellable.

        El delta importa: sin este caso la condicion podria estar bloqueando
        por otro motivo y pareceria que funciona (leccion de D-037).
        """
        p = self.spec(self.INFO_GAP + "\n## Asunciones Aplicadas\n\n"
                      "- **[A-001]** (sobre [P-020], que nace en este spec): formato local corto.\n")
        r = self.run_seal(p, "--seal")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("Estado: VALIDADO", p.read_text(encoding="utf-8"))

    def test_answered_informative_needs_no_record(self):
        """Si alguien lo decidio de verdad, no hay asuncion que documentar."""
        p = self.spec("\n## Items Pendientes\n\n### [P-021][INFORMATIVO] Decidido\n"
                      "- **Respuesta**: se muestra en formato ISO.\n"
                      "- **Asunción por defecto**: formato local corto.\n")
        self.assertEqual(self.run_seal(p, "--seal").returncode, 0)

    def test_record_for_another_gap_does_not_count(self):
        """La entrada tiene que citar EL gap, no valer como coartada generica."""
        p = self.spec(self.INFO_GAP + "\n## Asunciones Aplicadas\n\n"
                      "- **[A-001]** (sobre [P-099], que vive en `prd/prd_analysis.md`): otra cosa.\n")
        r = self.run_seal(p, "--seal")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("P-020", r.stdout)

    def test_unparseable_assumption_section_is_denied_not_assumed(self):
        """Guarda de vacuidad (D-037): no des por documentado lo que no parseas.

        Modo de fallo real (pasada 12 de CU-3.a): un spec escribio sus bloques
        como vinetas y el script dejo de verlos. Si la seccion esta pero no se
        le reconoce ninguna entrada, se deniega — no se asume que este bien.
        """
        p = self.spec(self.INFO_GAP + "\n## Asunciones Aplicadas\n\n"
                      "Se asumio el formato local corto para P-020.\n")
        r = self.run_seal(p, "--seal")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("no se ha sabido", r.stdout)

    def test_versioned_assumption_section_counts(self):
        """wf-spec-delta escribe `## Asunciones Aplicadas (v1.1)` — tambien vale."""
        p = self.spec(self.INFO_GAP + "\n## Asunciones Aplicadas (v1.1)\n\n"
                      "- **[A-003]** (sobre [P-020]): formato local corto.\n")
        self.assertEqual(self.run_seal(p, "--seal").returncode, 0)

    def test_spec_without_informative_gaps_is_unaffected(self):
        """Sin gaps informativos la condicion no aplica: nada que documentar."""
        p = self.spec()
        self.assertEqual(self.run_seal(p, "--seal").returncode, 0)

    def test_incompleto_blocks(self):
        p = self.spec("\n> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-011].\n")
        self.assertEqual(self.run_seal(p, "--seal").returncode, 2)

    def test_ca_without_parent_hu_blocks(self):
        p = self.spec("\n### CA-002: Huerfano\n")
        r = self.run_seal(p, "--seal")
        self.assertEqual(r.returncode, 2)
        self.assertIn("CA-002", r.stdout)

    def test_unseal_allowed_from_validado(self):
        """"Siempre" no: desde RETIRADO se deniega (ver RetireTest, D-078)."""
        p = self.spec(estado="VALIDADO")
        self.assertEqual(self.run_seal(p, "--unseal").returncode, 0)
        self.assertIn("Estado: BORRADOR", p.read_text(encoding="utf-8"))

    def test_check_does_not_write(self):
        p = self.spec()
        before = p.read_text(encoding="utf-8")
        self.assertEqual(self.run_seal(p, "--check").returncode, 0)
        self.assertEqual(p.read_text(encoding="utf-8"), before)

class RetireTest(unittest.TestCase):
    """Retirada de una feature (D-074): `Estado: RETIRADO` y sus transiciones."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.spec = write(self.dir / "login_spec.md",
                          "# Spec: Login\n> Estado: BORRADOR\n> Feature ID: F-001\n"
                          "> Origen de alcance: PRD\n\n### HU-1: hu\n\n"
                          "### CA-001: ca ← HU-1\nDado a, cuando b, entonces c.\n")

    def tearDown(self):
        self.tmp.cleanup()

    def _retire(self, *extra):
        return run_script("sdd-seal.py", "spec", self.spec, "--retire", *extra)

    def test_retire_writes_state_and_trace(self):
        r = self._retire("--change", "CR-007", "--reason", "ya no se cobra")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = self.spec.read_text(encoding="utf-8")
        self.assertIn("Estado: RETIRADO", text)
        self.assertRegex(text, r"Retirada: CR-007 — ya no se cobra \(\d{4}-\d{2}-\d{2}\)")

    def test_retire_requires_the_change_that_decides_it(self):
        r = self._retire()
        self.assertEqual(r.returncode, 1)
        self.assertIn("--change", r.stderr)
        self.assertIn("Estado: BORRADOR", self.spec.read_text(encoding="utf-8"),
                      "sin traza no se escribe nada")

    def test_retire_rejects_a_malformed_change_id(self):
        r = self._retire("--change", "el-cambio-ese")
        self.assertEqual(r.returncode, 1)
        self.assertIn("CR-XXX", r.stderr)

    def test_retire_is_idempotent(self):
        self._retire("--change", "CR-007")
        before = self.spec.read_text(encoding="utf-8")
        r = self._retire("--change", "CR-009")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(self.spec.read_text(encoding="utf-8"), before,
                         "una feature ya retirada no se vuelve a estampar")

    def test_a_retired_spec_is_not_sealable(self):
        self._retire("--change", "CR-007")
        r = run_script("sdd-seal.py", "spec", self.spec, "--check")
        self.assertEqual(r.returncode, 2)
        self.assertIn("RETIRADO", r.stdout)

    def test_a_failed_seal_does_not_undo_a_retirement(self):
        """El downgrade automatico del sellado fallido resucitaria la feature."""
        self._retire("--change", "CR-007")
        run_script("sdd-seal.py", "spec", self.spec, "--seal")
        self.assertIn("Estado: RETIRADO", self.spec.read_text(encoding="utf-8"))

    def test_unseal_does_not_undo_a_retirement(self):
        """D-078: `--unseal` es la coletilla de todo flujo que evoluciona un spec
        (delta, amend, gap-resolve, sync-from-prd). Si moviera RETIRADO a BORRADOR,
        un delta sobre una feature dada de baja la reactivaria en silencio: gates
        reabiertos, indice devolviendola a viva, y la traza `Retirada:` intacta
        contradiciendo al estado."""
        self._retire("--change", "CR-007", "--reason", "motivo")
        before = self.spec.read_text(encoding="utf-8")
        r = run_script("sdd-seal.py", "spec", self.spec, "--unseal")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("RETIRADO", r.stderr)
        self.assertEqual(self.spec.read_text(encoding="utf-8"), before,
                         "no se toca nada: se sale de RETIRADO solo por --unretire")

    def test_unretire_clears_state_and_trace(self):
        self._retire("--change", "CR-007", "--reason", "motivo")
        r = run_script("sdd-seal.py", "spec", self.spec, "--unretire")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = self.spec.read_text(encoding="utf-8")
        self.assertIn("Estado: BORRADOR", text, "nunca salta directo a VALIDADO")
        self.assertNotIn("Retirada:", text, "la traza se va con el estado")

    def test_retire_only_applies_to_a_spec(self):
        r = run_script("sdd-seal.py", "plan", self.spec, "--retire", "--change", "CR-007")
        self.assertEqual(r.returncode, 1)

    def test_a_plan_whose_spec_is_retired_is_not_sealable(self):
        self._retire("--change", "CR-007")
        plan = write(self.dir / "login_plan.md",
                     plan_text(spec_rel="login_spec.md"))
        r = run_script("sdd-seal.py", "plan", plan, "--check")
        self.assertEqual(r.returncode, 2)
        self.assertIn("RETIRADO", r.stdout)


class TombstoneTest(unittest.TestCase):
    """Regla 12: un CA con tombstone no es un CA vigente, y no puede bloquear sellos."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    TOMB = "\n### CA-003 [ELIMINADO en v1.4: la capacidad se retiro]\n"

    def test_spec_with_a_tombstoned_ca_is_sealable(self):
        spec = write(self.dir / "login_spec.md",
                     "# Spec: Login\n> Estado: BORRADOR\n> Feature ID: F-001\n"
                     "> Origen de alcance: PRD\n\n### HU-001: hu\n\n"
                     "### CA-001: ca ← HU-001\nDado a, cuando b, entonces c.\n" + self.TOMB)
        r = run_script("sdd-seal.py", "spec", spec, "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_plan_need_not_cover_a_tombstoned_ca(self):
        write(self.dir / "login_spec.md", SPEC_CLEAN + self.TOMB)
        plan = write(self.dir / "login_plan.md", plan_text())
        r = run_script("sdd-seal.py", "plan", plan, "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
