"""Tests para sdd-design-resolve.py — resolución base ⊕ override per-view (D-011 12.6).

Cierra la deuda de test de 12.2 (12.9b): "target con override → vista nativa;
target sin override → base intacta". Black-box por subproceso sobre fixtures en
tmpdir, como el resto de la suite.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402

SCRIPT = "sdd-design-resolve.py"

# Base agnóstica: preámbulo + convención + 2 vistas.
BASE_VIEWS = """# Views: Login
> Spec origen: ../spec/login_spec.md
> Feature ID: F-001

## Convencion documental

Cada vista es la fuente canonica de su pantalla.

## Vista 1: Login

- **Tipo:** screen
- Campo email + password agnostico.

## Vista 2: Home

- **Tipo:** screen
- Lista de cuentas.
"""

# Override mobile-android: solo diverge la vista Login (componentes Material).
OVERRIDE_ANDROID = """# Views: Login (override mobile-android)

## Vista 1: Login

- **Tipo:** screen
- Material TextField + boton Material.
"""


def resolve(base, override=None, merged=False):
    args = ["resolve", "--base", str(base)]
    if override is not None:
        args += ["--override", str(override)]
    if merged:
        args.append("--merged")
    r = run_script(SCRIPT, *args)
    assert r.returncode == 0, r.stderr
    return r.stdout if merged else json.loads(r.stdout)


class DesignResolveTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.base = write(self.root / "login_views.md", BASE_VIEWS)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_override_arg_all_inherited(self):
        # target sin override → base intacta
        m = resolve(self.base)
        self.assertFalse(m["has_override"])
        self.assertEqual(m["overridden"], [])
        self.assertEqual(m["override_only"], [])
        self.assertTrue(all(s["source"] == "base" for s in m["sections"]))
        # las 2 vistas + la convención
        headings = [s["heading"] for s in m["sections"]]
        self.assertIn("Vista 1: Login", headings)
        self.assertIn("Vista 2: Home", headings)
        self.assertIn("Convencion documental", headings)

    def test_missing_override_file_is_treated_as_no_override(self):
        # un path de override inexistente = no override (no revienta)
        m = resolve(self.base, override=self.root / "targets/mobile-android/login_views.md")
        self.assertFalse(m["has_override"])
        self.assertTrue(all(s["source"] == "base" for s in m["sections"]))

    def test_override_one_view_wins_others_inherit(self):
        # target con override → la vista overrideada es nativa; el resto, base
        ov = write(self.root / "targets/mobile-android/login_views.md", OVERRIDE_ANDROID)
        m = resolve(self.base, override=ov)
        self.assertTrue(m["has_override"])
        self.assertEqual(m["overridden"], ["Vista 1: Login"])
        self.assertIn("Vista 2: Home", m["inherited"])
        self.assertIn("Convencion documental", m["inherited"])
        self.assertEqual(m["override_only"], [])
        src = {s["heading"]: s["source"] for s in m["sections"]}
        self.assertEqual(src["Vista 1: Login"], "override")
        self.assertEqual(src["Vista 2: Home"], "base")

    def test_match_by_name_ignores_ordinal(self):
        # base "Vista 2: Perfil" + override "Vista 1: Perfil" → mismo nombre, overridea
        base = write(self.root / "x_views.md",
                     "# Views: X\n\n## Vista 1: Home\n\n- base home\n\n## Vista 2: Perfil\n\n- base perfil\n")
        ov = write(self.root / "targets/mobile-ios/x_views.md",
                   "# Views: X ios\n\n## Vista 1: Perfil\n\n- HIG perfil\n")
        m = resolve(base, override=ov)
        self.assertEqual(m["overridden"], ["Vista 1: Perfil"])  # gana el heading del override
        self.assertEqual(m["override_only"], [])                # NO se cuenta como nueva
        self.assertIn("Vista 1: Home", m["inherited"])

    def test_override_only_section_is_added(self):
        ov = write(self.root / "targets/desktop/login_views.md",
                   "# Views: Login desktop\n\n## Vista 9: Panel lateral\n\n- solo desktop\n")
        m = resolve(self.base, override=ov)
        self.assertEqual(m["override_only"], ["Vista 9: Panel lateral"])
        self.assertEqual(m["overridden"], [])  # Login/Home no divergen aquí
        self.assertIn("Vista 1: Login", m["inherited"])

    def test_merged_output_takes_override_content_and_base_preamble(self):
        ov = write(self.root / "targets/mobile-android/login_views.md", OVERRIDE_ANDROID)
        out = resolve(self.base, override=ov, merged=True)
        # preámbulo de la base
        self.assertIn("> Spec origen: ../spec/login_spec.md", out)
        # Login viene del override (Material), no de la base
        self.assertIn("Material TextField", out)
        self.assertNotIn("Campo email + password agnostico", out)
        # Home se hereda intacta de la base
        self.assertIn("Lista de cuentas", out)
        # la convención se hereda
        self.assertIn("fuente canonica", out)

    def test_merged_without_override_equals_base_sections(self):
        out = resolve(self.base, merged=True)
        self.assertIn("Campo email + password agnostico", out)
        self.assertIn("Lista de cuentas", out)

    def test_missing_base_errors(self):
        r = run_script(SCRIPT, "resolve", "--base", str(self.root / "nope.md"))
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
