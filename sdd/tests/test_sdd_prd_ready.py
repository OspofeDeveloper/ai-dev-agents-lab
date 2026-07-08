"""Black-box tests para scripts/sdd-prd-ready.py.

Gate de readiness PRD→spec (DECISIONS D-020): un PRD está READY cuando no tiene
`[ASUNCIÓN]` inline abiertas, cumple el 1:1 (marcas == entradas `[ASN-XXX]`) y
está sellado (`Aprobado por:` con valor real). Verifica:
  - READY (exit 0) sobre PRD limpio y sellado.
  - OPEN_ASSUMPTIONS (exit 2) con marcas inline sin confirmar.
  - UNSEALED (exit 2) sin marcas pero sin sello.
  - ASSUMPTION_MISMATCH (exit 2) cuando inline != entradas (huérfanas).
  - Falsa-positiva de PROSA: menciones del token en callouts `>` o dentro de
    `## Asunciones del PRD` NO se cuentan (regresión de CU-2.b).
  - Forma verbosa `[ASUNCIÓN: …]` cuenta como marca.
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

SEALED = "> **Aprobado por:** PM (2026-07-08)"
PENDING = "> **Aprobado por:** [pendiente de review — lo escribe wf-prd-review]"


def prd(header_seal, body):
    return f"---\ntype: product-requirements\nproduct: X\n---\n\n# PRD: X\n{header_seal}\n\n{body}\n"


class PrdReadyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, content, *flags):
        p = write(self.dir / "prd.md", content)
        return run_script("sdd-prd-ready.py", p, *flags)

    def test_ready(self):
        r = self._run(prd(SEALED, "## Alcance\n- El usuario puede A."))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("READY", r.stdout)

    def test_open_assumptions(self):
        body = (
            "## Alcance\n- El usuario puede A [ASUNCIÓN].\n\n"
            "## Asunciones del PRD\n"
            '- [ ] **[ASN-001]** — "El usuario puede A."\n'
        )
        r = self._run(prd(PENDING, body))
        self.assertEqual(r.returncode, 2)
        self.assertIn("OPEN_ASSUMPTIONS", r.stdout)

    def test_unsealed(self):
        r = self._run(prd(PENDING, "## Alcance\n- El usuario puede A."))
        self.assertEqual(r.returncode, 2)
        self.assertIn("UNSEALED", r.stdout)

    def test_mismatch_orphan_inline(self):
        body = (
            "## Alcance\n- El usuario puede A [ASUNCIÓN].\n- El usuario puede B [ASUNCIÓN].\n\n"
            "## Asunciones del PRD\n"
            '- [ ] **[ASN-001]** — "El usuario puede A."\n'
        )
        r = self._run(prd(PENDING, body))
        self.assertEqual(r.returncode, 2)
        self.assertIn("ASSUMPTION_MISMATCH", r.stdout)

    def test_prose_mention_not_counted(self):
        # El token aparece SOLO en prosa: un callout `>` de origen y la nota de la
        # sección. Ninguna es marca real → PRD limpio y sellado → READY.
        body = (
            "> ⚠ **Origen.** Casi todo lo que excede lo dicho va marcado como [ASUNCIÓN].\n\n"
            "## Alcance\n- El usuario puede A.\n\n"
            "## Asunciones del PRD\n"
            "> ⚠ Estas afirmaciones NO provienen del material fuente [ASUNCIÓN].\n"
        )
        r = self._run(prd(SEALED, body), "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data["verdict"], "READY")
        self.assertEqual(data["inline_marks"], 0)

    def test_verbose_form_counts(self):
        body = (
            "## Alcance\n- El usuario puede A [ASUNCIÓN: se infiere el detalle].\n\n"
            "## Asunciones del PRD\n"
            '- [ ] **[ASN-001]** — "El usuario puede A."\n'
        )
        r = self._run(prd(PENDING, body), "--json")
        self.assertEqual(r.returncode, 2)
        data = json.loads(r.stdout)
        self.assertEqual(data["inline_marks"], 1)
        self.assertEqual(data["asn_entries"], 1)
        self.assertEqual(data["verdict"], "OPEN_ASSUMPTIONS")

    def test_json_shape(self):
        r = self._run(prd(SEALED, "## Alcance\n- A."), "--json")
        data = json.loads(r.stdout)
        for key in ("verdict", "inline_marks", "asn_entries", "one_to_one", "sealed", "path"):
            self.assertIn(key, data)

    def test_bad_args(self):
        self.assertEqual(run_script("sdd-prd-ready.py").returncode, 1)
        self.assertEqual(run_script("sdd-prd-ready.py", "a.md", "b.md").returncode, 1)


if __name__ == "__main__":
    unittest.main()
