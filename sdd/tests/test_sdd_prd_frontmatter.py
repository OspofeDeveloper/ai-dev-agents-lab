"""Black-box tests para scripts/sdd-prd-frontmatter.py.

Validador determinista del frontmatter obligatorio del PRD (kb-prd-expert Regla 3:
type, product, version, created, status). Cierra el desliz intermitente del
`prd-expert` que omite campos —sobre todo `status`— (CU-2.i). Verifica:
  - COMPLETO (exit 0) sobre frontmatter con los 5 campos.
  - INCOMPLETO (exit 2) cuando falta un campo mecánico y no se pasa --fix.
  - --fix repone los campos mecánicos (type/version/created/status) → exit 0.
  - --fix NO inventa `product` (contenido): exit 2 aunque reponga los mecánicos.
  - Sin bloque de frontmatter → exit 2, no fabrica el bloque.
  - --today fija el valor de `created` al reponerlo.
  - --json emite la estructura esperada.
  - Args inválidos (exit 1).
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402

COMPLETE = (
    "---\n"
    "type: product-requirements\n"
    "product: App X\n"
    "version: 1.0\n"
    "created: 2026-07-13\n"
    "status: draft\n"
    "---\n\n# PRD: App X\n"
)
NO_STATUS = (
    "---\n"
    "type: product-requirements\n"
    "product: App X\n"
    "version: 1.0\n"
    "created: 2026-07-13\n"
    "---\n\n# PRD: App X\n"
)
NO_STATUS_NO_PRODUCT = (
    "---\n"
    "type: product-requirements\n"
    "version: 1.0\n"
    "created: 2026-07-13\n"
    "---\n\n# PRD: X\n"
)
NO_FRONTMATTER = "# PRD sin frontmatter\n\nContenido.\n"


class FrontmatterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _prd(self, content):
        p = self.dir / "prd.md"
        write(p, content)
        return p

    def _run(self, content, *flags):
        return run_script("sdd-prd-frontmatter.py", self._prd(content), *flags)

    def test_complete_is_ok(self):
        r = self._run(COMPLETE)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_missing_status_without_fix_fails(self):
        r = self._run(NO_STATUS)
        self.assertEqual(r.returncode, 2)
        self.assertIn("status", (r.stdout + r.stderr))

    def test_fix_repones_status(self):
        p = self._prd(NO_STATUS)
        r = run_script("sdd-prd-frontmatter.py", p, "--fix", "--today", "2026-07-13")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = p.read_text(encoding="utf-8")
        self.assertIn("status: draft", text)
        # sigue completo al re-validar
        self.assertEqual(run_script("sdd-prd-frontmatter.py", p).returncode, 0)

    def test_fix_no_inventa_product(self):
        p = self._prd(NO_STATUS_NO_PRODUCT)
        r = run_script("sdd-prd-frontmatter.py", p, "--fix", "--today", "2026-07-13")
        self.assertEqual(r.returncode, 2)  # product no auto-completable
        text = p.read_text(encoding="utf-8")
        self.assertIn("status: draft", text)     # mecánico repuesto
        self.assertNotIn("product:", text)       # contenido NO inventado

    def test_no_frontmatter_no_se_fabrica(self):
        p = self._prd(NO_FRONTMATTER)
        r = run_script("sdd-prd-frontmatter.py", p, "--fix")
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("status: draft", p.read_text(encoding="utf-8"))

    def test_today_fija_created(self):
        content = (
            "---\ntype: product-requirements\nproduct: App X\n"
            "version: 1.0\nstatus: draft\n---\n\n# PRD: App X\n"
        )
        p = self._prd(content)
        run_script("sdd-prd-frontmatter.py", p, "--fix", "--today", "2020-01-02")
        self.assertIn("created: 2020-01-02", p.read_text(encoding="utf-8"))

    def test_json_shape(self):
        r = self._run(NO_STATUS, "--json")
        data = json.loads(r.stdout)
        self.assertTrue(data["has_frontmatter"])
        self.assertEqual(data["missing"], ["status"])
        self.assertEqual(data["missing_autofixable"], ["status"])
        self.assertEqual(data["missing_content"], [])
        self.assertFalse(data["complete"])

    def test_fix_on_complete_adds_nothing(self):
        p = self._prd(COMPLETE)
        r = run_script("sdd-prd-frontmatter.py", p, "--fix", "--json")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout)["fixed"], [])

    def test_invalid_args(self):
        self.assertEqual(run_script("sdd-prd-frontmatter.py").returncode, 1)
        self.assertEqual(
            run_script("sdd-prd-frontmatter.py", "a.md", "b.md").returncode, 1
        )


if __name__ == "__main__":
    unittest.main()
