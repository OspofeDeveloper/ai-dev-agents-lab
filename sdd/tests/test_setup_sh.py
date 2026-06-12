"""Tests de integracion para setup.sh (bootstrap global, ROADMAP 11.3b).

setup.sh instala en ~/.claude del usuario; aqui se aisla con un HOME falso
(tmpdir) para no tocar la maquina. NO se ejercita --dev (crearia symlinks en
el .claude/ del repo real). Invariantes:
- install fresco: hook copiado, ~/.sdd-home, hook registrado en settings.json,
  bloque SDD-BOOTSTRAP en CLAUDE.md, skills wf-project-init + wf-sdd-update.
- idempotencia: re-run no duplica el hook ni el bloque.
- preserva settings.json y CLAUDE.md ajenos del usuario.
- --uninstall revierte la huella preservando lo ajeno.
- argumento desconocido -> exit 1; --help -> exit 0.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import SDD_ROOT, run_bash, write  # noqa: E402

SETUP = SDD_ROOT / "setup.sh"
BLOCK_START = "<!-- >>> SDD-BOOTSTRAP >>>"


class SetupBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.claude = self.home / ".claude"

    def tearDown(self):
        self.tmp.cleanup()

    def setup(self, *args):
        return run_bash(SETUP, *args, env={"HOME": str(self.home)})

    def _settings(self):
        return json.loads((self.claude / "settings.json").read_text(encoding="utf-8"))

    def _hook_registered(self):
        ss = self._settings().get("hooks", {}).get("SessionStart", [])
        return any(h.get("command", "").endswith("sdd-session-check.sh")
                   for m in ss for h in m.get("hooks", []))


class FreshInstallTest(SetupBase):
    def test_fresh_install_lays_out_bootstrap(self):
        r = self.setup()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # hook copiado
        self.assertTrue((self.claude / "hooks" / "sdd-session-check.sh").exists())
        # ~/.sdd-home apunta al repo
        sdd_home = (self.home / ".sdd-home").read_text(encoding="utf-8").strip()
        self.assertEqual(sdd_home, str(SDD_ROOT))
        # skills globales
        self.assertTrue((self.claude / "skills" / "wf-project-init" / "SKILL.md").exists())
        self.assertTrue((self.claude / "skills" / "wf-sdd-update" / "SKILL.md").exists())
        # hook registrado y bloque presente
        self.assertTrue(self._hook_registered())
        md = (self.claude / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn(BLOCK_START, md)


class IdempotencyTest(SetupBase):
    def test_rerun_does_not_duplicate(self):
        self.setup()
        r = self.setup()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ya registrado", r.stdout)
        # un solo hook SDD en SessionStart
        ss = self._settings()["hooks"]["SessionStart"]
        sdd_hooks = [h for m in ss for h in m.get("hooks", [])
                     if h.get("command", "").endswith("sdd-session-check.sh")]
        self.assertEqual(len(sdd_hooks), 1, "el hook no debe duplicarse")
        # un solo bloque SDD-BOOTSTRAP
        md = (self.claude / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(md.count(BLOCK_START), 1, "el bloque no debe duplicarse")


class PreservesForeignConfigTest(SetupBase):
    def test_preserves_foreign_settings_and_claude_md(self):
        foreign_settings = {
            "model": "opus",
            "permissions": {"allow": ["Bash(npm:*)"]},
            "hooks": {
                "SessionStart": [
                    {"hooks": [{"type": "command", "command": "mi-hook-propio.sh"}]}
                ]
            },
        }
        write(self.claude / "settings.json", json.dumps(foreign_settings, indent=2))
        write(self.claude / "CLAUDE.md", "# Notas propias\nmis reglas\n")

        r = self.setup()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        s = self._settings()
        # config propia intacta
        self.assertEqual(s["model"], "opus")
        self.assertEqual(s["permissions"], {"allow": ["Bash(npm:*)"]})
        # hook propio del usuario preservado + hook SDD anadido
        cmds = [h.get("command", "") for m in s["hooks"]["SessionStart"]
                for h in m.get("hooks", [])]
        self.assertIn("mi-hook-propio.sh", cmds)
        self.assertTrue(any(c.endswith("sdd-session-check.sh") for c in cmds))
        # CLAUDE.md propio preservado + bloque anadido
        md = (self.claude / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("mis reglas", md)
        self.assertIn(BLOCK_START, md)


class UninstallTest(SetupBase):
    def test_uninstall_reverts_preserving_foreign(self):
        # config ajena + install + uninstall
        write(self.claude / "settings.json", json.dumps({
            "permissions": {"allow": ["Bash(npm:*)"]},
            "hooks": {"SessionStart": [
                {"hooks": [{"type": "command", "command": "mi-hook-propio.sh"}]}
            ]},
        }, indent=2))
        write(self.claude / "CLAUDE.md", "# Notas propias\nmis reglas\n")
        self.setup()
        self.assertTrue((self.claude / "hooks" / "sdd-session-check.sh").exists())

        r = self.setup("--uninstall")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # huella SDD retirada
        self.assertFalse((self.claude / "hooks" / "sdd-session-check.sh").exists())
        self.assertFalse((self.claude / "skills" / "wf-project-init").exists())
        self.assertFalse((self.home / ".sdd-home").exists())
        # lo ajeno preservado
        s = self._settings()
        self.assertEqual(s["permissions"], {"allow": ["Bash(npm:*)"]})
        cmds = [h.get("command", "") for m in s.get("hooks", {}).get("SessionStart", [])
                for h in m.get("hooks", [])]
        self.assertIn("mi-hook-propio.sh", cmds)
        self.assertFalse(any(c.endswith("sdd-session-check.sh") for c in cmds))
        md = (self.claude / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("mis reglas", md)
        self.assertNotIn(BLOCK_START, md)

    def test_uninstall_is_idempotent(self):
        self.setup()
        self.setup("--uninstall")
        r = self.setup("--uninstall")  # segunda vez: ausente != error
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class ArgParsingTest(SetupBase):
    def test_unknown_arg_exits_1(self):
        r = self.setup("--bogus")
        self.assertEqual(r.returncode, 1)
        self.assertIn("desconocido", r.stdout + r.stderr)

    def test_help_exits_0(self):
        r = self.setup("--help")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Uso", r.stdout)


if __name__ == "__main__":
    unittest.main()
