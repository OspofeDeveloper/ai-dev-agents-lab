"""Tests para scripts/sdd-meta-lint-hook.py (ROADMAP 11.4c).

Hook PostToolUse advisory: al editar un */SKILL.md o */agents/*.md del
ecosistema, si la pieza tiene findings BLOCKING del linter los inyecta como
additionalContext; si esta limpia (o no es pieza, o no es edicion), silencio.
Siempre exit 0.

Se aisla apuntando el hook a un arbol-fixture con SDD_META_LINT_ROOT (el linter
hermano es el real). Entrada por stdin (JSON del hook).
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script  # noqa: E402

CLEAN_KB = """---
name: kb-clean
description: "Una kb limpia de prueba."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# kb-clean

Cuerpo limpio.
"""

# name != directorio -> NAME-MISMATCH (blocking)
BROKEN_KB = """---
name: kb-OTRO-NOMBRE
description: "x"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# kb-broken
"""


class HookBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, rel, content):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def run_hook(self, tool_name, file_path):
        payload = json.dumps({"tool_name": tool_name,
                              "tool_input": {"file_path": str(file_path)}})
        return run_script("sdd-meta-lint-hook.py", stdin=payload,
                          env={"SDD_META_LINT_ROOT": str(self.root)})

    def assertSilent(self, r):
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(r.stdout.strip(), "", f"esperaba silencio: {r.stdout!r}")

    def assertContext(self, r):
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = json.loads(r.stdout)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PostToolUse")
        return out["hookSpecificOutput"]["additionalContext"]


class FeedbackTest(HookBase):
    def test_clean_skill_edit_is_silent(self):
        p = self._write("spec/skills/kb-clean/SKILL.md", CLEAN_KB)
        self.assertSilent(self.run_hook("Write", p))

    def test_broken_skill_edit_surfaces_finding(self):
        p = self._write("spec/skills/kb-broken/SKILL.md", BROKEN_KB)
        ctx = self.assertContext(self.run_hook("Edit", p))
        self.assertIn("kb-broken", ctx)
        self.assertIn("NAME-MISMATCH", ctx)

    def test_only_findings_of_edited_file(self):
        # dos piezas rotas; al editar una, el feedback es solo de esa
        self._write("spec/skills/kb-broken/SKILL.md", BROKEN_KB)
        other = self._write("plan/skills/kb-otra/SKILL.md",
                            BROKEN_KB.replace("kb-OTRO-NOMBRE", "kb-MAL2"))
        ctx = self.assertContext(self.run_hook("Edit", other))
        self.assertIn("kb-otra", ctx)
        self.assertNotIn("kb-broken", ctx)


class ScopeTest(HookBase):
    def test_non_skill_file_silent(self):
        p = self._write("README.md", "# readme\n")
        self.assertSilent(self.run_hook("Write", p))

    def test_non_edit_tool_silent(self):
        p = self._write("spec/skills/kb-broken/SKILL.md", BROKEN_KB)
        self.assertSilent(self.run_hook("Bash", p))

    def test_file_outside_root_silent(self):
        outside = Path(self.tmp.name).parent / "nope-SKILL.md"
        self.assertSilent(self.run_hook("Write", outside))

    def test_agent_file_broken_surfaces(self):
        # agente con name != basename -> NAME-MISMATCH
        agent = """---
name: otro-nombre
description: "x"
skills: [kb-a]
memory: project
permissionMode: acceptEdits
model: claude-opus-4-8
color: cyan
---

# agente
"""
        p = self._write("tasks/agents/my-agent.md", agent)
        ctx = self.assertContext(self.run_hook("Edit", p))
        self.assertIn("NAME-MISMATCH", ctx)

    def test_bad_stdin_silent(self):
        r = run_script("sdd-meta-lint-hook.py", stdin="not-json",
                       env={"SDD_META_LINT_ROOT": str(self.root)})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_missing_file_path_silent(self):
        payload = json.dumps({"tool_name": "Write", "tool_input": {}})
        r = run_script("sdd-meta-lint-hook.py", stdin=payload,
                       env={"SDD_META_LINT_ROOT": str(self.root)})
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
