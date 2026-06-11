"""Black-box tests para scripts/merge-claude-settings.py.

Cubre: dest inexistente -> copia source; merge anade matchers/hooks ausentes
sin perder settings propios del proyecto; idempotencia (re-merge no duplica);
preserva permisos/claves del equipo; eliminacion de hooks deprecated.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


SOURCE = {
    "hooks": {
        "PreToolUse": [
            {"matcher": "Skill",
             "hooks": [{"type": "command", "command": "sdd-gate-check.py"}]},
        ],
        "SessionStart": [
            {"matcher": "*",
             "hooks": [{"type": "command", "command": "sdd-session-check.sh"}]},
        ],
    },
    "permissions": {"allow": ["Bash(python3:*)"]},
}


class MergeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.src = self.dir / "source.json"
        self.src.write_text(json.dumps(SOURCE, indent=2), encoding="utf-8")
        self.dest = self.dir / "dest.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _merge(self):
        return run_script("merge-claude-settings.py", self.src, self.dest)

    def _dest(self):
        return json.loads(self.dest.read_text(encoding="utf-8"))

    def test_missing_dest_copies_source(self):
        r = self._merge()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self._dest(), SOURCE)

    def test_merge_preserves_project_keys(self):
        project = {
            "model": "opus",
            "permissions": {"allow": ["Bash(npm:*)"]},  # propia del proyecto
            "hooks": {
                "PreToolUse": [
                    {"matcher": "Edit",
                     "hooks": [{"type": "command", "command": "prettier"}]},
                ]
            },
        }
        write(self.dest, json.dumps(project, indent=2))
        r = self._merge()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = self._dest()
        # Clave propia del proyecto intacta (el valor del proyecto gana)
        self.assertEqual(out["model"], "opus")
        self.assertEqual(out["permissions"], {"allow": ["Bash(npm:*)"]})
        # El hook Edit del proyecto se preserva
        matchers = {e["matcher"] for e in out["hooks"]["PreToolUse"]}
        self.assertIn("Edit", matchers)
        # El hook Skill del source se anade
        self.assertIn("Skill", matchers)
        # El evento SessionStart del source entra completo
        self.assertIn("SessionStart", out["hooks"])

    def test_merge_is_idempotent(self):
        self._merge()
        first = self.dest.read_text(encoding="utf-8")
        r = self._merge()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ya al dia", r.stdout)
        self.assertEqual(first, self.dest.read_text(encoding="utf-8"),
                         "re-merge no debe cambiar nada")

    def test_existing_matcher_not_duplicated(self):
        # dest ya tiene el matcher Skill (con otro comando) -> no se anade otra entrada
        project = {
            "hooks": {
                "PreToolUse": [
                    {"matcher": "Skill",
                     "hooks": [{"type": "command", "command": "mi-propio.py"}]},
                ]
            }
        }
        write(self.dest, json.dumps(project, indent=2))
        self._merge()
        out = self._dest()
        skill_entries = [e for e in out["hooks"]["PreToolUse"]
                         if e["matcher"] == "Skill"]
        self.assertEqual(len(skill_entries), 1, "matcher existente no se duplica")
        # y conserva el comando del proyecto
        self.assertEqual(skill_entries[0]["hooks"][0]["command"], "mi-propio.py")

    def test_deprecated_hook_removed(self):
        deprecated = ('echo \'{"hookSpecificOutput": {"hookEventName": '
                      '"PermissionRequest", "decision": {"behavior": "allow"}}}\'')
        project = {
            "hooks": {
                "PreToolUse": [
                    {"matcher": "Skill",
                     "hooks": [{"type": "command", "command": deprecated}]},
                ]
            }
        }
        write(self.dest, json.dumps(project, indent=2))
        self._merge()
        out = self._dest()
        commands = [h["command"]
                    for e in out["hooks"]["PreToolUse"]
                    for h in e.get("hooks", [])]
        self.assertNotIn(deprecated, commands, "el hook deprecated debe eliminarse")

    def test_bad_args_exit_1(self):
        r = run_script("merge-claude-settings.py", self.src)
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
