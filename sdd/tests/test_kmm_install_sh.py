"""Tests de integracion para el overlay KMM (ROADMAP 11.3b).

Invariantes criticos del overlay (varios fueron bugs reales: 0.1, 6.6, 10.3):
- tech/kmm/install.sh instala la regla del stack en rules/sdd-kmm.md y NO
  pisa el CLAUDE.md raiz del proyecto.
- la KB transversal kb-kmm-project-state-protocol (raiz de skills/) se instala
  (precondicion dura de los agentes KMM; bug 0.1).
- el overlay sustituye por basename las piezas genericas (plan-architect.md,
  kb-plan-expert) por su variante KMM.
- install.sh, al detectar stack en .sdd/project-init.json, re-aplica el overlay
  tras instalar las fases genericas (bug 6.6: reinstalar plan/tasks degradaba
  el proyecto en silencio).

Black-box: corre los .sh con cwd = proyecto-fixture.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import SDD_ROOT, run_bash, write  # noqa: E402

INSTALL = SDD_ROOT / "install.sh"
KMM_INSTALL = SDD_ROOT / "tech" / "kmm" / "install.sh"

KMM_PLAN_ARCHITECT_SRC = SDD_ROOT / "tech" / "kmm" / "agents" / "plan-architect.md"
GENERIC_PLAN_ARCHITECT_SRC = SDD_ROOT / "pipeline" / "plan" / "agents" / "plan-architect.md"
KMM_KB_PLAN_EXPERT_SRC = SDD_ROOT / "tech" / "kmm" / "skills" / "plan" / "kb-plan-expert" / "SKILL.md"


class KmmOverlayBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    @property
    def claude(self):
        return self.proj / ".claude"

    def kmm_install(self, env=None):
        return run_bash(KMM_INSTALL, cwd=self.proj, env=env)

    def install(self, *args, env=None):
        return run_bash(INSTALL, *args, cwd=self.proj, env=env)


class KmmDoesNotClobberRootTest(KmmOverlayBase):
    def test_creates_kmm_rule(self):
        r = self.kmm_install()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rule = self.claude / "rules" / "sdd-kmm.md"
        self.assertTrue(rule.exists())
        text = rule.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\npaths:"))
        self.assertIn('"**/*.kt"', text)

    def test_does_not_create_root_claude_md(self):
        # overlay solo: NO debe aparecer un .claude/CLAUDE.md (bug 10.3)
        r = self.kmm_install()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.claude / "CLAUDE.md").exists(),
                         "el overlay no debe crear/pisar el CLAUDE.md raiz")

    def test_preserves_existing_root_claude_md(self):
        sentinel = "# Mi proyecto\nReglas propias del equipo.\n"
        write(self.claude / "CLAUDE.md", sentinel)
        r = self.kmm_install()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((self.claude / "CLAUDE.md").read_text(encoding="utf-8"),
                         sentinel, "el overlay no debe tocar el CLAUDE.md raiz existente")

    def test_installs_project_state_protocol_kb(self):
        # bug 0.1: la KB transversal vive en la raiz de skills/, no en plan/tasks
        r = self.kmm_install()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(
            (self.claude / "skills" / "kb-kmm-project-state-protocol" / "SKILL.md").exists(),
            "kb-kmm-project-state-protocol debe instalarse (precondicion de los agentes KMM)")

    def test_installs_kmm_agents(self):
        self.kmm_install()
        for a in ("kmm-explorer.md", "kmm-feature-logic-implementer.md",
                  "kmm-planner.md", "kmm-tester.md"):
            self.assertTrue((self.claude / "agents" / a).exists(), f"falta agents/{a}")


class KmmOverridesByBasenameTest(KmmOverlayBase):
    def test_overlay_replaces_generic_plan_architect(self):
        # instala generico primero, luego overlay: la variante KMM gana
        self.install("plan,tasks")
        installed = self.claude / "agents" / "plan-architect.md"
        self.assertEqual(installed.read_text(encoding="utf-8"),
                         GENERIC_PLAN_ARCHITECT_SRC.read_text(encoding="utf-8"),
                         "tras install generico debe estar la variante generica")

        r = self.kmm_install()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(installed.read_text(encoding="utf-8"),
                         KMM_PLAN_ARCHITECT_SRC.read_text(encoding="utf-8"),
                         "tras el overlay debe estar la variante KMM (override por basename)")
        # marcador de contenido KMM presente
        self.assertIn("Koin", installed.read_text(encoding="utf-8"))

    def test_overlay_replaces_generic_kb_plan_expert(self):
        self.install("plan,tasks")
        self.kmm_install()
        installed = self.claude / "skills" / "kb-plan-expert" / "SKILL.md"
        self.assertEqual(installed.read_text(encoding="utf-8"),
                         KMM_KB_PLAN_EXPERT_SRC.read_text(encoding="utf-8"),
                         "kb-plan-expert instalada debe ser la variante KMM")


class InstallReappliesOverlayTest(KmmOverlayBase):
    def _declare_kmm_stack(self):
        write(self.proj / ".sdd" / "project-init.json",
              json.dumps({"stack": "kmm", "phases": ["plan", "tasks"]}, indent=2))

    def test_install_plan_reapplies_kmm_overlay(self):
        # proyecto KMM ya montado, luego reinstalar las fases genericas:
        # install.sh debe re-aplicar el overlay (bug 6.6) y NO dejar la generica.
        self.install("plan,tasks")
        self.kmm_install()
        self._declare_kmm_stack()

        r = self.install("plan,tasks")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("re-aplicando el overlay", r.stdout)
        installed = self.claude / "agents" / "plan-architect.md"
        self.assertEqual(installed.read_text(encoding="utf-8"),
                         KMM_PLAN_ARCHITECT_SRC.read_text(encoding="utf-8"),
                         "reinstalar plan/tasks no debe degradar la variante KMM")

    def test_unknown_stack_warns_not_crashes(self):
        # stack declarado pero sin overlay en el ecosistema -> aviso, no fallo
        write(self.proj / ".sdd" / "project-init.json",
              json.dumps({"stack": "flutter", "phases": ["plan"]}, indent=2))
        r = self.install("plan")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("flutter", r.stdout)
        self.assertIn("re-aplica el overlay manualmente", r.stdout)


if __name__ == "__main__":
    unittest.main()
