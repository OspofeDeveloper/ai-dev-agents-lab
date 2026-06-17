"""Tests para sdd-init-detect.py (hardening de wf-project-init).

El script absorbe la lógica determinista que el skill recitaba en bash: find-up
del raíz del proyecto (monorepo), estado previo, carpetas candidatas, detección
de stack (Paso 4) y la verificación post-install (Paso 9). Black-box por
subproceso (`run_script`) sobre fixtures en tmpdir.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402

SCRIPT = "sdd-init-detect.py"


def detect(root):
    r = run_script(SCRIPT, "detect", "--root", str(root))
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def verify(root, phases):
    r = run_script(SCRIPT, "verify", "--phases", phases, "--root", str(root))
    return r.returncode, json.loads(r.stdout)


def repair_plan(root):
    r = run_script(SCRIPT, "repair-plan", "--root", str(root))
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


class DetectStateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_virgin_project(self):
        d = detect(self.root)
        self.assertFalse(d["init_found"])
        self.assertFalse(d["mode_found"])
        self.assertIsNone(d["mode"])
        self.assertEqual(d["installed_phases"], [])
        self.assertEqual(d["artifact_candidates"], {})
        self.assertIsNone(d["detected_stack"])
        self.assertIsNone(d["sdd_root"])
        self.assertFalse(d["sdd_root_is_ancestor"])

    def test_prior_mode_free(self):
        write(self.root / ".claude/sdd-mode.json", '{"mode": "free"}')
        d = detect(self.root)
        self.assertTrue(d["mode_found"])
        self.assertEqual(d["mode"], "free")
        # marcador en el propio cwd: sdd_root es el cwd, no un ancestro
        self.assertEqual(Path(d["sdd_root"]), self.root.resolve())
        self.assertFalse(d["sdd_root_is_ancestor"])

    def test_installed_phases_detected(self):
        write(self.root / ".claude/rules/sdd-spec.md", "x")
        write(self.root / ".claude/rules/sdd-plan.md", "x")
        d = detect(self.root)
        self.assertIn("spec", d["installed_phases"])
        self.assertIn("plan", d["installed_phases"])
        self.assertNotIn("design", d["installed_phases"])

    def test_legacy_layout_phase_detected(self):
        # layout plano legacy: <fase>/.claude/CLAUDE.md
        write(self.root / "spec/.claude/CLAUDE.md", "x")
        self.assertIn("spec", detect(self.root)["installed_phases"])

    def test_artifact_candidates(self):
        write(self.root / "specs/.keep", "")
        write(self.root / "docs/prd/.keep", "")
        d = detect(self.root)
        self.assertEqual(d["artifact_candidates"].get("spec"), ["specs"])
        self.assertEqual(d["artifact_candidates"].get("prd"), ["docs/prd"])
        self.assertNotIn("design", d["artifact_candidates"])


class DetectStackTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_kmm(self):
        write(self.root / "gradle/libs.versions.toml", "")
        write(self.root / "iosApp/.keep", "")
        d = detect(self.root)
        self.assertEqual(d["detected_stack"], "kmm")
        self.assertEqual(d["detected_type"], "app")
        self.assertEqual(d["app_framework"], "compose_multiplatform")

    def test_next_web(self):
        write(self.root / "package.json", '{"dependencies": {"next": "14"}}')
        d = detect(self.root)
        self.assertEqual(d["detected_stack"], "next")
        self.assertEqual(d["detected_type"], "web")
        self.assertIsNone(d["app_framework"])

    def test_fastapi_backend_requirements_ci(self):
        write(self.root / "requirements.txt", "FastAPI==0.110\n")
        d = detect(self.root)
        self.assertEqual(d["detected_stack"], "fastapi")
        self.assertEqual(d["detected_type"], "backend")

    def test_android_not_kmm(self):
        write(self.root / "app/build.gradle.kts", "")
        d = detect(self.root)
        self.assertEqual(d["detected_stack"], "android")
        self.assertEqual(d["app_framework"], "android")

    def test_no_stack(self):
        write(self.root / "main.cpp", "int main(){}")
        self.assertIsNone(detect(self.root)["detected_stack"])


class FindUpMonorepoTest(unittest.TestCase):
    """find-up con techo en el git toplevel (Paso 3.0)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init"], cwd=self.root, capture_output=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_marker_in_ancestor_found(self):
        write(self.root / ".sdd/project-init.json", '{"dispatcher": "wf-project-init"}')
        sub = self.root / "packages" / "app"
        sub.mkdir(parents=True)
        d = detect(sub)
        self.assertEqual(Path(d["sdd_root"]), self.root.resolve())
        self.assertTrue(d["sdd_root_is_ancestor"])

    def test_no_marker_no_root(self):
        sub = self.root / "packages" / "app"
        sub.mkdir(parents=True)
        d = detect(sub)
        self.assertIsNone(d["sdd_root"])


class VerifyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _install_standalone(self, phases=("spec", "plan", "tasks")):
        for f in phases:
            write(self.root / f".claude/rules/sdd-{f}.md", "x")
        write(self.root / ".claude/CLAUDE.md", "x")
        write(self.root / ".sdd/project-init.json", json.dumps({
            "dispatcher": "wf-project-init",
            "topology": "standalone",
            "artifacts": {"spec": "spec"},
        }))
        for s in ("sdd-gate-check.py", "sdd-seal.py", "sdd-task-state.py",
                  "sdd-sync-check.py", "sdd-skill-allow.py"):
            write(self.root / ".sdd/scripts" / s, "x")
        write(self.root / ".sdd/sdd-version.json", "{}")
        write(self.root / ".gitignore", ".claude/settings.local.json\n")

    def _install_minimal_state(self, extra):
        """Instala el mínimo para verify y escribe project-init.json con `extra`."""
        for f in ("spec", "plan", "tasks"):
            write(self.root / f".claude/rules/sdd-{f}.md", "x")
        write(self.root / ".claude/CLAUDE.md", "x")
        write(self.root / ".sdd/project-init.json", json.dumps(extra))
        for s in ("sdd-gate-check.py", "sdd-seal.py", "sdd-task-state.py",
                  "sdd-sync-check.py", "sdd-skill-allow.py"):
            write(self.root / ".sdd/scripts" / s, "x")
        write(self.root / ".sdd/sdd-version.json", "{}")
        write(self.root / ".gitignore", ".claude/settings.local.json\n")

    def test_well_installed_passes(self):
        self._install_standalone()
        code, checks = verify(self.root, "spec,plan,tasks")
        self.assertEqual(code, 0, [c for c in checks if not c["ok"]])
        self.assertTrue(all(c["ok"] for c in checks))

    def test_missing_phase_rule_fails(self):
        self._install_standalone(phases=("spec", "plan"))  # falta tasks
        code, checks = verify(self.root, "spec,plan,tasks")
        self.assertEqual(code, 2)
        self.assertFalse(next(c for c in checks if c["check"] == "fase-tasks")["ok"])

    def test_consumer_artifacts_source_ok(self):
        # consumer: solo plan+tasks, sin "artifacts" sino "artifacts_source"
        for f in ("plan", "tasks"):
            write(self.root / f".claude/rules/sdd-{f}.md", "x")
        write(self.root / ".claude/CLAUDE.md", "x")
        write(self.root / ".sdd/project-init.json", json.dumps({
            "dispatcher": "wf-project-init",
            "topology": "consumer",
            "artifacts_source": "../myshop-specs",
        }))
        for s in ("sdd-gate-check.py", "sdd-seal.py", "sdd-task-state.py",
                  "sdd-sync-check.py", "sdd-skill-allow.py"):
            write(self.root / ".sdd/scripts" / s, "x")
        write(self.root / ".sdd/sdd-version.json", "{}")
        write(self.root / ".gitignore", ".claude/settings.local.json\n")
        code, checks = verify(self.root, "plan,tasks")
        self.assertEqual(code, 0, [c for c in checks if not c["ok"]])
        self.assertTrue(next(c for c in checks if c["check"] == "artifacts-map")["ok"])

    def test_authoring_no_plan_tasks_passes(self):
        # authoring: prd+spec+design, sin plan/tasks, con "artifacts"
        for f in ("prd", "spec", "design"):
            write(self.root / f".claude/rules/sdd-{f}.md", "x")
        write(self.root / ".claude/CLAUDE.md", "x")
        write(self.root / ".sdd/project-init.json", json.dumps({
            "dispatcher": "wf-project-init",
            "topology": "authoring",
            "surfaces": [],
            "design_role": "system",
            "artifacts": {"prd": "prd", "spec": "spec", "design": "design"},
        }))
        for s in ("sdd-gate-check.py", "sdd-seal.py", "sdd-task-state.py",
                  "sdd-sync-check.py", "sdd-skill-allow.py"):
            write(self.root / ".sdd/scripts" / s, "x")
        write(self.root / ".sdd/sdd-version.json", "{}")
        write(self.root / ".gitignore", ".claude/settings.local.json\n")
        code, checks = verify(self.root, "prd,spec,design")
        self.assertEqual(code, 0, [c for c in checks if not c["ok"]])
        self.assertTrue(next(c for c in checks if c["check"] == "topology")["ok"])

    def test_legacy_schema_fails(self):
        # esquema viejo (profiles/profile/type) ya no es válido → check topology FALLA
        for legacy in ({"profiles": ["product"]}, {"profile": "product"}, {"type": "app"}):
            obj = {"dispatcher": "wf-project-init", "artifacts": {"spec": "spec"}}
            obj.update(legacy)
            self._install_minimal_state(obj)
            code, checks = verify(self.root, "spec,plan,tasks")
            self.assertEqual(code, 2, f"legacy {legacy} debería fallar")
            self.assertFalse(next(c for c in checks if c["check"] == "topology")["ok"])

    def test_missing_topology_fails(self):
        self._install_minimal_state({
            "dispatcher": "wf-project-init",
            "artifacts": {"spec": "spec"},
        })
        code, checks = verify(self.root, "spec,plan,tasks")
        self.assertEqual(code, 2)
        self.assertFalse(next(c for c in checks if c["check"] == "topology")["ok"])

    def test_missing_gitignore_line_fails(self):
        self._install_standalone()
        write(self.root / ".gitignore", "node_modules\n")  # sin la línea SDD
        code, checks = verify(self.root, "spec,plan,tasks")
        self.assertEqual(code, 2)
        self.assertFalse(next(c for c in checks if c["check"] == "gitignore")["ok"])


class RepairPlanTest(unittest.TestCase):
    """Plan determinista de reparación (extend) — la lógica que el agente
    improvisaba en prosa al reparar un init a medias. `phases` es el contrato:
    lo declarado-pero-no-instalado se repara, y el `design_role` se deriva de la
    topología sin preguntar."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _state(self, *, phases, installed, design_role, topology="authoring", **extra):
        for f in installed:
            write(self.root / f".claude/rules/sdd-{f}.md", "x")
        obj = {
            "dispatcher": "wf-project-init",
            "topology": topology,
            "phases": list(phases),
            "design_role": design_role,
        }
        obj.update(extra)
        write(self.root / ".sdd/project-init.json", json.dumps(obj))

    def test_authoring_design_declared_missing_derives_system(self):
        # El caso real de CU-1.e: prd+spec instalados, design declarado con role null.
        self._state(phases=["prd", "spec", "design"], installed=["prd", "spec"],
                    design_role=None, topology="authoring")
        p = repair_plan(self.root)
        self.assertEqual(p["missing_phases"], ["design"])
        self.assertEqual(p["expected_design_role"], "system")
        self.assertFalse(p["design_role_consistent"])  # null ≠ system
        self.assertTrue(p["needs_repair"])

    def test_consumer_design_derives_feature(self):
        self._state(phases=["plan", "tasks", "design"], installed=["plan", "tasks"],
                    design_role=None, topology="consumer")
        p = repair_plan(self.root)
        self.assertEqual(p["missing_phases"], ["design"])
        self.assertEqual(p["expected_design_role"], "feature")
        self.assertTrue(p["needs_repair"])

    def test_standalone_design_derives_full(self):
        self._state(phases=["spec", "design", "plan", "tasks"],
                    installed=["spec", "plan", "tasks"],
                    design_role=None, topology="standalone")
        p = repair_plan(self.root)
        self.assertEqual(p["missing_phases"], ["design"])
        self.assertEqual(p["expected_design_role"], "full")

    def test_declared_phases_in_canonical_order(self):
        # El JSON puede declararlas desordenadas; el plan las normaliza.
        self._state(phases=["design", "spec", "prd"], installed=["spec"],
                    design_role="system", topology="authoring")
        p = repair_plan(self.root)
        self.assertEqual(p["declared_phases"], ["prd", "spec", "design"])
        self.assertEqual(p["missing_phases"], ["prd", "design"])

    def test_no_design_declared_role_is_null(self):
        self._state(phases=["spec", "plan", "tasks"],
                    installed=["spec", "plan", "tasks"],
                    design_role=None, topology="standalone")
        p = repair_plan(self.root)
        self.assertFalse(p["design_declared"])
        self.assertIsNone(p["expected_design_role"])
        self.assertTrue(p["design_role_consistent"])  # null == null

    def test_fully_consistent_needs_no_repair(self):
        self._state(phases=["prd", "spec", "design"],
                    installed=["prd", "spec", "design"],
                    design_role="system", topology="authoring")
        p = repair_plan(self.root)
        self.assertEqual(p["missing_phases"], [])
        self.assertTrue(p["design_role_consistent"])
        self.assertFalse(p["needs_repair"])

    def test_role_mismatch_alone_needs_repair(self):
        # Todo instalado pero design_role incoherente con la topología → reparar.
        self._state(phases=["prd", "spec", "design"],
                    installed=["prd", "spec", "design"],
                    design_role="feature", topology="authoring")  # debería ser system
        p = repair_plan(self.root)
        self.assertEqual(p["missing_phases"], [])
        self.assertEqual(p["expected_design_role"], "system")
        self.assertFalse(p["design_role_consistent"])
        self.assertTrue(p["needs_repair"])

    def test_no_init_json_is_not_repairable(self):
        p = repair_plan(self.root)
        self.assertFalse(p["init_found"])
        self.assertFalse(p["init_readable"])
        self.assertFalse(p["needs_repair"])

    def test_malformed_init_json_is_not_repairable(self):
        write(self.root / ".sdd/project-init.json", "{ not json")
        p = repair_plan(self.root)
        self.assertTrue(p["init_found"])
        self.assertFalse(p["init_readable"])
        self.assertFalse(p["needs_repair"])


if __name__ == "__main__":
    unittest.main()
