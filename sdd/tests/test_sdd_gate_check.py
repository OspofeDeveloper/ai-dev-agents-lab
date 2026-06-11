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


if __name__ == "__main__":
    unittest.main()
