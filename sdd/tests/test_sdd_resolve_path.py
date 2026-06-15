"""Tests para sdd-resolve-path.py (ROADMAP 11.2a).

El resolutor de rutas absorbe la frase canónica de layout recitada en ~20
skills. Cubre los tres modos (write / find / rel-from) contra los ejemplos
canónicos de la prosa que reemplaza, ambos layouts (subcarpeta de fase y plano
legacy), el caso fuera-de-feature, el repo consumidor y los errores de uso.

Black-box por subproceso (`run_script`); `find` usa fixtures reales en tmpdir.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402

SCRIPT = "sdd-resolve-path.py"


def out(*args, cwd=None):
    r = run_script(SCRIPT, *args, cwd=cwd)
    return r


class WriteFeatureKindsTest(unittest.TestCase):
    """write <kind> respeta el layout del input y replica el nombre de feature."""

    def w(self, kind, inp, *extra):
        r = out("write", kind, inp, *extra)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def test_subfolder_layout_plan_from_spec(self):
        self.assertEqual(
            self.w("plan", "features/login/spec/login_spec.md"),
            "features/login/plan/login_plan.md",
        )

    def test_flat_legacy_layout_plan_from_spec(self):
        self.assertEqual(
            self.w("plan", "features/login/login_spec.md"),
            "features/login/login_plan.md",
        )

    def test_outside_feature_same_dir(self):
        self.assertEqual(
            self.w("plan", "docs/login_spec.md"),
            "docs/login_plan.md",
        )

    def test_tasks_from_plan_subfolder(self):
        self.assertEqual(
            self.w("tasks", "features/login/plan/login_plan.md"),
            "features/login/tasks/login_tasks.md",
        )

    def test_design_family_lands_in_design_subfolder(self):
        for kind, suf in (("flows", "_flows.md"), ("views", "_views.md"),
                          ("ui-prompt", "_ui_prompt.md"),
                          ("design-discovery", "_design_discovery.md")):
            self.assertEqual(
                self.w(kind, "features/login/spec/login_spec.md"),
                f"features/login/design/login{suf}",
            )

    def test_qa_family_lands_in_tasks_subfolder(self):
        # el sufijo largo (_qa_plan.md) no se confunde con _plan.md
        for kind, suf in (("qa-plan", "_qa_plan.md"), ("qa-report", "_qa_report.md"),
                          ("release", "_release.md"), ("bugs", "_bugs.md")):
            self.assertEqual(
                self.w(kind, "features/login/spec/login_spec.md"),
                f"features/login/tasks/login{suf}",
            )

    def test_feature_name_drives_basename_not_input_filename(self):
        # el nombre del artefacto sale de la carpeta de feature, no del fichero
        self.assertEqual(
            self.w("plan", "features/checkout/spec/whatever_spec.md"),
            "features/checkout/plan/checkout_plan.md",
        )

    def test_consumer_local_root_redirects_local_artifact(self):
        # el spec vive en el SSoT; el plan va al repo local en subcarpeta de fase
        self.assertEqual(
            self.w("plan", "../product-ssot/spec/features/login/spec/login_spec.md",
                   "--local-root", "."),
            "features/login/plan/login_plan.md",
        )

    def test_write_rejects_product_kind(self):
        r = out("write", "discovery", "features/x/spec/x_spec.md")
        self.assertEqual(r.returncode, 1)
        self.assertIn("producto", r.stderr.lower())


class RelFromTest(unittest.TestCase):
    """rel-from emite el header de trazabilidad relativo (Spec origen / Plan origen)."""

    def rf(self, anchor, target):
        r = out("rel-from", anchor, target)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def test_subfolder_spec_origen(self):
        self.assertEqual(
            self.rf("features/login/plan/login_plan.md",
                    "features/login/spec/login_spec.md"),
            "../spec/login_spec.md",
        )

    def test_flat_legacy_same_dir(self):
        self.assertEqual(
            self.rf("features/login/login_plan.md", "features/login/login_spec.md"),
            "login_spec.md",
        )

    def test_outside_feature_same_dir(self):
        self.assertEqual(
            self.rf("docs/login_plan.md", "docs/login_spec.md"),
            "login_spec.md",
        )

    def test_consumer_deep_relative(self):
        rel = self.rf(
            "features/login/plan/login_plan.md",
            "../product-ssot/spec/features/login/spec/login_spec.md",
        )
        # debe subir tres niveles desde plan/ hasta la raíz local y salir al sibling
        self.assertEqual(rel, "../../../../product-ssot/spec/features/login/spec/login_spec.md")


class FindTest(unittest.TestCase):
    """find localiza un artefacto existente en ambos layouts; vacío + exit 3 si no."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def find(self, kind, inp):
        return out("find", kind, inp, cwd=self.root)

    def test_find_subfolder_layout(self):
        write(self.root / "features/login/spec/login_spec.md", "# spec")
        write(self.root / "features/login/plan/login_plan.md", "# plan")
        r = self.find("plan", "features/login/spec/login_spec.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "features/login/plan/login_plan.md")

    def test_find_flat_legacy_layout(self):
        write(self.root / "features/login/login_spec.md", "# spec")
        write(self.root / "features/login/login_plan.md", "# plan")
        r = self.find("plan", "features/login/login_spec.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "features/login/login_plan.md")

    def test_find_prefers_subfolder_when_both_exist(self):
        write(self.root / "features/login/spec/login_spec.md", "# spec")
        write(self.root / "features/login/plan/login_plan.md", "# subfolder")
        write(self.root / "features/login/login_plan.md", "# flat")
        r = self.find("plan", "features/login/spec/login_spec.md")
        self.assertEqual(r.stdout.strip(), "features/login/plan/login_plan.md")

    def test_find_missing_returns_exit_3_empty(self):
        write(self.root / "features/login/spec/login_spec.md", "# spec")
        r = self.find("plan", "features/login/spec/login_spec.md")
        self.assertEqual(r.returncode, 3)
        self.assertEqual(r.stdout.strip(), "")

    def test_find_product_fixed_name_design(self):
        write(self.root / "features/login/spec/login_spec.md", "# spec")
        write(self.root / "DESIGN.md", "# design")
        r = self.find("design-doc", "features/login/spec/login_spec.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "DESIGN.md")

    def test_find_product_glob_features_index(self):
        write(self.root / "features/login/spec/login_spec.md", "# spec")
        write(self.root / "myprd_features.md", "# index")
        r = self.find("features-index", "features/login/spec/login_spec.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "myprd_features.md")

    def test_find_product_missing_exit_3(self):
        write(self.root / "features/login/spec/login_spec.md", "# spec")
        r = self.find("design-doc", "features/login/spec/login_spec.md")
        self.assertEqual(r.returncode, 3)


class UsageTest(unittest.TestCase):
    def test_no_args_exits_1(self):
        r = out()
        self.assertEqual(r.returncode, 1)

    def test_unknown_kind_find_exits_1(self):
        r = out("find", "bogus", "features/x/spec/x_spec.md")
        self.assertEqual(r.returncode, 1)

    def test_kinds_lists_both_groups(self):
        r = out("kinds")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("plan", r.stdout)
        self.assertIn("design-doc", r.stdout)


if __name__ == "__main__":
    unittest.main()
