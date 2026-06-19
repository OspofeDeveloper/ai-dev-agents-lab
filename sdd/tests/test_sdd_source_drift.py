"""Tests para sdd-source-drift.py — drift de fuentes externas pineadas (D-011 12.5).

Verifica la detección cross-repo: pin vs HEAD del checkout de specs/design, y la
lista de artefactos relevantes cambiados. Usa repos git temporales reales (patrón
de test_sdd_release.py). Black-box por subproceso.
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

SCRIPT = "sdd-source-drift.py"


def _g(repo, *a):
    subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True)


def _short(repo):
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def init_repo(repo: Path) -> str:
    repo.mkdir(parents=True, exist_ok=True)
    _g(repo, "init")
    _g(repo, "config", "user.email", "t@t")
    _g(repo, "config", "user.name", "t")
    _g(repo, "config", "commit.gpgsign", "false")
    (repo / "DESIGN.md").write_text("base", encoding="utf-8")
    _g(repo, "add", "-A")
    _g(repo, "commit", "-m", "init")
    return _short(repo)


def commit_file(repo: Path, rel: str, content: str, msg: str) -> str:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    _g(repo, "add", "-A")
    _g(repo, "commit", "-m", msg)
    return _short(repo)


def check(root):
    r = run_script(SCRIPT, "check", "--root", str(root))
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


class SourceDriftTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        # repo de diseño como subdirectorio del consumer (path relativo "design_repo")
        self.design = self.root / "design_repo"
        self.pin = init_repo(self.design)

    def tearDown(self):
        self.tmp.cleanup()

    def _init_json(self, **extra):
        obj = {"dispatcher": "wf-project-init", "topology": "consumer"}
        obj.update(extra)
        write(self.root / ".sdd/project-init.json", json.dumps(obj))

    def test_no_drift_when_pin_is_head(self):
        self._init_json(design_source="design_repo", design_source_pin=self.pin)
        d = check(self.root)
        self.assertFalse(d["any_drift"])
        s = d["sources"][0]
        self.assertEqual(s["kind"], "design")
        self.assertTrue(s["git_ok"])
        self.assertFalse(s["drifted"])
        self.assertEqual(s["changed"], [])

    def test_drift_lists_changed_design_artifacts(self):
        self._init_json(design_source="design_repo", design_source_pin=self.pin)
        commit_file(self.design, "features/login/design/login_views.md", "v", "add views")
        d = check(self.root)
        self.assertTrue(d["any_drift"])
        s = d["sources"][0]
        self.assertTrue(s["drifted"])
        self.assertIn("features/login/design/login_views.md", s["changed"])

    def test_drift_ignores_irrelevant_files(self):
        self._init_json(design_source="design_repo", design_source_pin=self.pin)
        commit_file(self.design, "README.md", "x", "docs")
        d = check(self.root)
        s = d["sources"][0]
        self.assertTrue(s["drifted"])      # el HEAD avanzó
        self.assertEqual(s["changed"], [])  # pero ningún artefacto relevante

    def test_unknown_pin_is_not_git_ok(self):
        self._init_json(design_source="design_repo", design_source_pin="unknown")
        d = check(self.root)
        s = d["sources"][0]
        self.assertFalse(s["git_ok"])
        self.assertFalse(s["drifted"])

    def test_non_git_source_is_not_git_ok(self):
        (self.root / "plain").mkdir()
        self._init_json(design_source="plain", design_source_pin="abc1234")
        d = check(self.root)
        s = d["sources"][0]
        self.assertFalse(s["git_ok"])
        self.assertFalse(s["drifted"])

    def test_no_external_sources_is_empty(self):
        self._init_json(artifacts={"spec": "spec"})  # standalone-like, sin fuentes externas
        d = check(self.root)
        self.assertEqual(d["sources"], [])
        self.assertFalse(d["any_drift"])

    def test_both_specs_and_design_sources(self):
        specs = self.root / "specs_repo"
        specs_pin = init_repo(specs)
        self._init_json(
            artifacts_source="specs_repo", artifacts_source_pin=specs_pin,
            design_source="design_repo", design_source_pin=self.pin,
        )
        # specs avanza con un spec nuevo; design no
        commit_file(specs, "features/login/spec/login_spec.md", "s", "add spec")
        d = check(self.root)
        self.assertTrue(d["any_drift"])
        by_kind = {s["kind"]: s for s in d["sources"]}
        self.assertTrue(by_kind["specs"]["drifted"])
        self.assertIn("features/login/spec/login_spec.md", by_kind["specs"]["changed"])
        self.assertFalse(by_kind["design"]["drifted"])

    def test_no_init_json_is_empty(self):
        d = check(self.root)
        self.assertEqual(d["sources"], [])
        self.assertFalse(d["any_drift"])


if __name__ == "__main__":
    unittest.main()
