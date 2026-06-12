"""Black-box tests para scripts/sdd-skill-allow.py.

Hook PermissionRequest (matcher: Skill). Lee el JSON del hook por stdin y emite
`allow` SOLO si la skill invocada es una `wf-*`; en cualquier otro caso no emite
nada (stdout vacio -> el harness pregunta al usuario). Siempre sale 0.

Contrato verificado leyendo el script:
  - tool_name != "Skill"           -> no decide (stdout vacio)
  - skill wf-* (kebab-case)         -> allow
  - skill kb-* / otra              -> no decide
  - forma cualificada plugin:skill -> se queda con el ultimo segmento
  - stdin ilegible                 -> no decide (return 0)
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script  # noqa: E402


def skill_payload(skill):
    return json.dumps({"tool_name": "Skill", "tool_input": {"skill": skill}})


def decision(stdout):
    """Devuelve el behavior de la decision, o None si stdout esta vacio."""
    if not stdout.strip():
        return None
    data = json.loads(stdout)
    return data["hookSpecificOutput"]["decision"]["behavior"]


class SkillAllowTest(unittest.TestCase):
    def _run(self, payload):
        return run_script("sdd-skill-allow.py", stdin=payload)

    def test_wf_skill_allowed(self):
        r = self._run(skill_payload("wf-prepare-plan"))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(decision(r.stdout), "allow")
        # Forma del payload de salida
        data = json.loads(r.stdout)
        self.assertEqual(
            data["hookSpecificOutput"]["hookEventName"], "PermissionRequest"
        )

    def test_various_wf_skills_allowed(self):
        for skill in ("wf-spec-analyze", "wf-design-system", "wf-qa-verify",
                      "wf-prd-create", "wf-task-run"):
            r = self._run(skill_payload(skill))
            self.assertEqual(decision(r.stdout), "allow", f"{skill} deberia permitir")
            self.assertEqual(r.returncode, 0)

    def test_kb_skill_not_decided(self):
        # kb-* no son invocables por el usuario -> el hook no decide
        r = self._run(skill_payload("kb-plan-expert"))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")
        self.assertIsNone(decision(r.stdout))

    def test_unknown_skill_not_decided(self):
        r = self._run(skill_payload("alguna-skill-ajena"))
        self.assertEqual(r.stdout.strip(), "")

    def test_skill_without_wf_prefix_not_decided(self):
        # nombre que contiene wf pero no es prefijo -> fullmatch falla
        r = self._run(skill_payload("my-wf-thing"))
        self.assertEqual(r.stdout.strip(), "")

    def test_qualified_plugin_skill_uses_last_segment(self):
        # plugin:wf-foo -> se queda con wf-foo -> allow
        r = self._run(skill_payload("plugin:wf-prepare-tasks"))
        self.assertEqual(decision(r.stdout), "allow")

    def test_qualified_plugin_non_wf_not_decided(self):
        r = self._run(skill_payload("plugin:kb-spec-expert"))
        self.assertEqual(r.stdout.strip(), "")

    def test_non_skill_tool_not_decided(self):
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})
        r = self._run(payload)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_unreadable_stdin_returns_0_and_silent(self):
        r = self._run("no es json {{{")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_empty_skill_not_decided(self):
        r = self._run(skill_payload(""))
        self.assertEqual(r.stdout.strip(), "")

    def test_missing_tool_input_not_decided(self):
        payload = json.dumps({"tool_name": "Skill"})
        r = self._run(payload)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
