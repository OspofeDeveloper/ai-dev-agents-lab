"""Tests para scripts/sdd-scaffold.py (ROADMAP 11.4d).

El scaffold genera el esqueleto canonico de kb-*/wf-*/agente con frontmatter
correcto POR CONSTRUCCION. Invariante central: lo que produce pasa el linter
estructural (sdd-structural-lint.py) sin retoques (0 blocking).
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script  # noqa: E402


class ScaffoldBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def scaffold(self, *args):
        return run_script("sdd-scaffold.py", *args, "--root", self.root)

    def read(self, rel):
        return (self.root / rel).read_text(encoding="utf-8")


class KbScaffoldTest(ScaffoldBase):
    def test_kb_layout_and_frontmatter(self):
        r = self.scaffold("kb", "foo-bar", "--phase", "spec")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        fm = self.read("pipeline/spec/skills/kb-foo-bar/SKILL.md")
        self.assertIn("name: kb-foo-bar", fm)
        self.assertIn("user-invocable: false", fm)
        self.assertIn("allowed-tools: [Read]", fm)
        # una kb NUNCA lleva estos campos
        self.assertNotIn("when_to_use", fm)
        self.assertNotIn("argument-hint", fm)
        self.assertNotIn("context: fork", fm)

    def test_kb_prefix_not_doubled(self):
        # pasar 'kb-foo' no debe producir kb-kb-foo
        self.scaffold("kb", "kb-foo", "--phase", "plan")
        self.assertTrue((self.root / "pipeline/plan/skills/kb-foo/SKILL.md").exists())
        self.assertFalse((self.root / "pipeline/plan/skills/kb-kb-foo").exists())

    def test_global_phase_goes_to_meta(self):
        self.scaffold("kb", "sdd-thing", "--phase", "global")
        self.assertTrue((self.root / "meta/skills/kb-sdd-thing/SKILL.md").exists())


class WfScaffoldTest(ScaffoldBase):
    def test_wf_frontmatter(self):
        r = self.scaffold("wf", "do-stuff", "--phase", "tasks")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        fm = self.read("pipeline/tasks/skills/wf-do-stuff/SKILL.md")
        self.assertIn("name: wf-do-stuff", fm)
        self.assertIn("when_to_use:", fm)
        self.assertIn("argument-hint:", fm)
        self.assertIn("context: fork", fm)
        self.assertIn("user-invocable: true", fm)
        self.assertIn("allowed-tools: [Read, Write]", fm)

    def test_wf_with_agent_adds_agent_and_tool(self):
        self.scaffold("wf", "gen-plan", "--phase", "plan", "--agent", "plan-architect")
        fm = self.read("pipeline/plan/skills/wf-gen-plan/SKILL.md")
        self.assertIn("agent: plan-architect", fm)
        self.assertIn("Agent", fm)  # allowed-tools incluye Agent

    def test_tech_stack_phase(self):
        self.scaffold("wf", "kmm-thing", "--phase", "tech/kmm")
        self.assertTrue((self.root / "tech/kmm/skills/wf-kmm-thing/SKILL.md").exists())


class AgentScaffoldTest(ScaffoldBase):
    def test_agent_layout_and_color(self):
        r = self.scaffold("agent", "tasks-helper", "--phase", "tasks",
                          "--skills", "kb-a,kb-b")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        fm = self.read("pipeline/tasks/agents/tasks-helper.md")
        self.assertIn("name: tasks-helper", fm)
        self.assertIn("skills: [kb-a, kb-b]", fm)
        self.assertIn("color: cyan", fm)       # tasks -> cyan
        self.assertIn("model: claude-opus-4-8", fm)
        self.assertIn("effort: high", fm)       # default (no read-only)

    def test_agent_read_only_swaps_effort_for_disallowed(self):
        self.scaffold("agent", "plan-auditor2", "--phase", "plan",
                      "--skills", "kb-a", "--read-only")
        fm = self.read("pipeline/plan/agents/plan-auditor2.md")
        self.assertIn("disallowedTools: Write, Edit", fm)
        self.assertNotIn("effort: high", fm)
        self.assertIn("color: orange", fm)      # plan -> orange

    def test_agent_scaffold_declares_no_memory(self):
        # D-041: el scaffold es el propagador real del frontmatter de agente.
        # Si vuelve a emitir `memory:`, vuelve a todo agente que se cree.
        self.scaffold("agent", "mem-helper", "--phase", "spec", "--skills", "kb-a")
        fm = self.read("pipeline/spec/agents/mem-helper.md")
        self.assertNotIn("memory:", fm)

    def test_agent_tech_phase_is_red(self):
        self.scaffold("agent", "kmm-thing", "--phase", "tech/kmm", "--skills", "kb-a")
        fm = self.read("tech/kmm/agents/kmm-thing.md")
        self.assertIn("color: red", fm)

    def test_agent_requires_skills(self):
        r = self.scaffold("agent", "no-skills", "--phase", "spec")
        self.assertEqual(r.returncode, 2)
        self.assertIn("skills", r.stderr.lower())


class GuardsTest(ScaffoldBase):
    def test_duplicate_refused(self):
        self.scaffold("kb", "dup", "--phase", "spec")
        r = self.scaffold("kb", "dup", "--phase", "spec")
        self.assertEqual(r.returncode, 2)
        self.assertIn("ya existe", r.stderr)

    def test_force_overwrites(self):
        self.scaffold("kb", "dup", "--phase", "spec")
        r = self.scaffold("kb", "dup", "--phase", "spec", "--force")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_bad_phase_exit_2(self):
        r = self.scaffold("kb", "x", "--phase", "frontend")
        self.assertEqual(r.returncode, 2)
        self.assertIn("fase no reconocida", r.stderr)

    def test_dry_run_does_not_write(self):
        r = self.scaffold("kb", "ghost", "--phase", "spec", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("name: kb-ghost", r.stdout)
        self.assertFalse((self.root / "pipeline/spec/skills/kb-ghost").exists())


class LintCleanInvariantTest(ScaffoldBase):
    """El esqueleto generado debe pasar el linter estructural sin blocking."""

    def test_scaffolded_pieces_pass_structural_lint(self):
        self.scaffold("kb", "clean-kb", "--phase", "spec")
        self.scaffold("wf", "clean-wf", "--phase", "plan", "--agent", "plan-architect")
        self.scaffold("agent", "clean-agent", "--phase", "tasks", "--skills", "kb-x")
        r = run_script("sdd-structural-lint.py", "--root", self.root, "--check")
        self.assertEqual(r.returncode, 0,
                         f"el scaffold debe producir 0 blocking:\n{r.stdout}")


if __name__ == "__main__":
    unittest.main()
