"""Black-box tests para scripts/sdd-gate-check.py.

El gate es un hook PreToolUse: lee el JSON del hook por stdin, SIEMPRE sale 0,
y senala la denegacion emitiendo un JSON con permissionDecision: deny en stdout.
Permitir = stdout vacio. Esta suite verifica:
  - precondicion OK -> permite (stdout vacio)
  - precondicion fallida -> deniega (JSON deny con motivo accionable)
  - fail-open documentado: stdin ilegible / skill sin gate / path no resoluble -> permite
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


def hook_payload(skill, args):
    return json.dumps({
        "tool_name": "Skill",
        "tool_input": {"skill": skill, "args": args},
    })


def is_deny(stdout):
    if not stdout.strip():
        return None
    data = json.loads(stdout)
    return data["hookSpecificOutput"]["permissionDecision"]


SPEC_OK = """\
# Spec: Login
> Feature ID: F-001
### CA-001: ok ← HU-1
"""


class GateSpecFiableTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, skill, spec_content):
        spec = write(self.dir / "login_spec.md", spec_content)
        r = run_script("sdd-gate-check.py",
                       stdin=hook_payload(skill, str(spec)))
        return r

    def test_clean_spec_allowed(self):
        r = self._run("wf-prepare-plan", SPEC_OK)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "", "spec limpio -> permitir (stdout vacio)")

    def test_spec_with_incompleto_denied(self):
        r = self._run("wf-prepare-plan", SPEC_OK + "\n[INCOMPLETO] falta HU\n")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(is_deny(r.stdout), "deny")
        self.assertIn("INCOMPLETO", r.stdout)

    def test_spec_with_critico_denied(self):
        r = self._run("wf-prepare-plan", SPEC_OK + "\n[CRÍTICO] gap\n")
        self.assertEqual(is_deny(r.stdout), "deny")

    def test_answered_critical_block_does_not_block(self):
        """D-061: un critico YA RESPONDIDO no puede bloquear el plan para siempre.

        Desde D-054 el spec conserva el bloque por trazabilidad; contar la palabra
        [CRITICO] en crudo dejaba la feature inplanificable tras responderla.
        """
        spec = (SPEC_OK + "\n## Items Pendientes\n\n"
                "### [P-011][CRÍTICO] Ya respondido\n"
                "- **Contexto**: x\n"
                "- **Respuesta**: el usuario decidio que si.\n")
        r = self._run("wf-prepare-plan", spec)
        self.assertEqual(r.stdout.strip(), "", "un critico respondido no debe denegar")

    def test_open_critical_block_denied_with_its_id(self):
        spec = (SPEC_OK + "\n## Items Pendientes\n\n"
                "### [P-011][CRÍTICO] Sin responder\n"
                "- **Respuesta**: _(pendiente)_\n")
        r = self._run("wf-prepare-plan", spec)
        self.assertEqual(is_deny(r.stdout), "deny")
        self.assertIn("P-011", r.stdout)

    def test_spec_in_borrador_denied(self):
        """D-061: cada fase consume artefactos sellados de la anterior."""
        r = self._run("wf-prepare-plan", "> Estado: BORRADOR\n" + SPEC_OK)
        self.assertEqual(is_deny(r.stdout), "deny")
        self.assertIn("BORRADOR", r.stdout)

    def test_spec_validado_allowed(self):
        r = self._run("wf-prepare-plan", "> Estado: VALIDADO\n" + SPEC_OK)
        self.assertEqual(r.stdout.strip(), "")

    def test_spec_without_estado_line_allowed(self):
        """Legacy: un spec sin la linea Estado no se bloquea (politica conservadora)."""
        r = self._run("wf-prepare-plan", SPEC_OK)
        self.assertEqual(r.stdout.strip(), "")

    def test_spec_with_inferido_denied(self):
        r = self._run("wf-prepare-plan", SPEC_OK + "\n[INFERIDO] sin confirmar\n")
        self.assertEqual(is_deny(r.stdout), "deny")
        self.assertIn("INFERIDO", r.stdout)

    def test_status_sync_stale_denied(self):
        r = self._run("wf-prepare-plan", "---\nstatus_sync: stale\n---\n" + SPEC_OK)
        self.assertEqual(is_deny(r.stdout), "deny")

    def test_status_sync_unknown_allowed(self):
        # unknown es legitimo en specs sin PRD (fast-track) -> permitir
        r = self._run("wf-prepare-plan", "---\nstatus_sync: unknown\n---\n" + SPEC_OK)
        self.assertEqual(r.stdout.strip(), "")

    def test_gate_applies_to_design_and_qa(self):
        for skill in ("wf-design-system", "wf-design-feature-prototype", "wf-qa-plan"):
            r = self._run(skill, SPEC_OK + "\n[CRÍTICO] gap\n")
            self.assertEqual(is_deny(r.stdout), "deny", f"{skill} deberia denegar")

    def test_missing_spec_file_denied(self):
        # path resoluble pero archivo inexistente -> evidencia positiva -> deny
        r = run_script("sdd-gate-check.py",
                       stdin=hook_payload("wf-prepare-plan",
                                          str(self.dir / "no_existe_spec.md")))
        self.assertEqual(is_deny(r.stdout), "deny")


class GatePlanValidadoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _plan(self, estado="VALIDADO", extra=""):
        return write(self.dir / "x_plan.md",
                     f"# Plan\n**Estado:** {estado}\n\n{extra}")

    def test_validado_plan_allowed(self):
        plan = self._plan("VALIDADO")
        r = run_script("sdd-gate-check.py",
                       stdin=hook_payload("wf-prepare-tasks", str(plan)))
        self.assertEqual(r.stdout.strip(), "")

    def test_borrador_plan_denied(self):
        plan = self._plan("BORRADOR")
        r = run_script("sdd-gate-check.py",
                       stdin=hook_payload("wf-prepare-tasks", str(plan)))
        self.assertEqual(is_deny(r.stdout), "deny")
        self.assertIn("BORRADOR", r.stdout)

    def test_amend_pending_denied(self):
        plan = self._plan("VALIDADO", extra="**Enmienda pendiente:** CA-001 (E-001)\n")
        r = run_script("sdd-gate-check.py",
                       stdin=hook_payload("wf-prepare-tasks", str(plan)))
        self.assertEqual(is_deny(r.stdout), "deny")
        self.assertIn("E-001", r.stdout)


class FailOpenTest(unittest.TestCase):
    def test_unreadable_stdin_allows(self):
        r = run_script("sdd-gate-check.py", stdin="not json at all {{{")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_non_skill_tool_allows(self):
        payload = json.dumps({"tool_name": "Bash", "tool_input": {}})
        r = run_script("sdd-gate-check.py", stdin=payload)
        self.assertEqual(r.stdout.strip(), "")

    def test_skill_without_gate_allows(self):
        r = run_script("sdd-gate-check.py",
                       stdin=hook_payload("wf-spec-analyze", "algo.md"))
        self.assertEqual(r.stdout.strip(), "")

    def test_unresolvable_path_allows(self):
        # gate con skill conocido pero sin token *_spec.md en args -> conservador -> permite
        r = run_script("sdd-gate-check.py",
                       stdin=hook_payload("wf-prepare-plan", "--help"))
        self.assertEqual(r.stdout.strip(), "")


class RetiredFeatureTest(unittest.TestCase):
    """Una feature dada de baja se deniega en los tres frentes (D-074).

    Asimetria deliberada con `Enmienda pendiente`, que retiene SOLO las tasks del
    CA enmendado: la baja cancela la feature entera, asi que no queda subconjunto
    que tenga sentido ejecutar.
    """

    SPEC_RETIRADO = ("# Spec: Pagos\n> Estado: RETIRADO\n"
                     "> Retirada: CR-007 — ya no se cobra\n> Feature ID: F-002\n"
                     "### CA-001: ok ← HU-1\n")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.spec = write(self.dir / "pagos_spec.md", self.SPEC_RETIRADO)
        self.plan = write(self.dir / "pagos_plan.md",
                          "# Plan: Pagos\n> Estado: VALIDADO\n"
                          "> Spec origen: pagos_spec.md\n## Checklist de Trazabilidad\n- CA-001\n")
        self.tasks = write(self.dir / "pagos_tasks.md",
                           "# Tasks: Pagos\n> Plan origen: pagos_plan.md\n"
                           "## T-001: hacer\n- **Spec CA**: CA-001\n")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, skill, path):
        return run_script("sdd-gate-check.py", stdin=hook_payload(skill, str(path)))

    def test_prepare_plan_denied(self):
        r = self._run("wf-prepare-plan", self.spec)
        self.assertEqual(is_deny(r.stdout), "deny")
        self.assertIn("RETIRADO", r.stdout)

    def test_qa_plan_denied(self):
        self.assertEqual(is_deny(self._run("wf-qa-plan", self.spec).stdout), "deny")

    def test_prepare_tasks_denied_via_spec_origen(self):
        r = self._run("wf-prepare-tasks", self.plan)
        self.assertEqual(is_deny(r.stdout), "deny")
        self.assertIn("RETIRADO", r.stdout)

    def test_task_run_denied_for_the_whole_feature(self):
        r = self._run("wf-task-run", self.tasks)
        self.assertEqual(is_deny(r.stdout), "deny")
        self.assertIn("RETIRADO", r.stdout)

    def test_retirement_is_reported_before_open_gaps(self):
        """Decirle que responda criticos de una feature cancelada le manda a trabajar
        en lo que ya no existe."""
        write(self.spec, self.SPEC_RETIRADO + "\n### [P-001][CRÍTICO] gap\n"
              "- **Respuesta**: _(pendiente)_\n")
        r = self._run("wf-prepare-plan", self.spec)
        self.assertIn("RETIRADO", r.stdout)
        self.assertNotIn("sin responder", r.stdout)

    def test_a_live_feature_still_passes(self):
        """Guarda de vacuidad: el gate no deniega por existir, deniega por la baja."""
        vivo = write(self.dir / "login_spec.md",
                     "# Spec: Login\n> Estado: VALIDADO\n> Feature ID: F-001\n"
                     "### CA-001: ok ← HU-1\n")
        self.assertEqual(self._run("wf-prepare-plan", vivo).stdout.strip(), "")

    def test_unresolvable_spec_origen_stays_conservative(self):
        """Politica del hook: sin evidencia positiva de violacion, se permite."""
        plan = write(self.dir / "otro_plan.md",
                     "# Plan: Otro\n> Estado: VALIDADO\n"
                     "> Spec origen: no_existe_spec.md\n")
        self.assertEqual(self._run("wf-prepare-tasks", plan).stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
