"""Black-box tests para scripts/sdd-prd-apply.py.

Aplica deterministamente las decisiones de review de un PRD (Q3, DECISIONS D-030).
Ligadura inline↔entrada por TEXTO exacto + SOLAPAMIENTO de contenido (marcador
anónimo; ni orden ni texto exacto garantizados por la creación). Verifica:
  - confirm quita el marcador inline + elimina la entrada (1:1 preservado).
  - edit sustituye la afirmación inline + quita marcador + elimina la entrada.
  - reject borra la línea inline + elimina la entrada.
  - al vaciarse `## Asunciones del PRD`, se elimina la sección entera.
  - --seal escribe/sobrescribe la línea `Aprobado por:`.
  - precondición 1:1 rota → exit 2; desalineación (guarda) → exit 2.
  - ASN inexistente → exit 2; args inválidos / combinaciones ilegales → exit 1.
  - integración: aplicar todo + sellar deja el PRD READY para sdd-prd-ready.py.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402

FRONT = (
    "---\ntype: product-requirements\nproduct: X\nversion: 1.0\n"
    "created: 2026-07-15\nstatus: draft\n---\n\n"
    "# PRD: X\n"
    "> **Aprobado por:** [pendiente de review — lo escribe wf-prd-review]\n\n"
)

# Tres asunciones; el cuerpo y las entradas van EN EL MISMO ORDEN (contrato posicional).
BODY = (
    "## Alcance\n\n"
    "### Movimientos\n"
    "- El usuario puede registrar un gasto.\n"
    "- El usuario puede editar o eliminar un movimiento ya registrado. [ASUNCIÓN]\n\n"
    "### Cuentas\n"
    "- El usuario puede registrar y mantener sus cuentas y tarjetas. [ASUNCIÓN]\n"
    "- El usuario puede consultar el saldo de cada cuenta por separado. [ASUNCIÓN]\n\n"
)
SECTION = (
    "---\n\n"
    "## Asunciones del PRD\n\n"
    "> ⚠ Estas afirmaciones NO provienen del material fuente.\n\n"
    "- [ ] **[ASN-001]** — El usuario puede editar o eliminar un movimiento ya registrado. · *Hueco: …*\n"
    "- [ ] **[ASN-002]** — El usuario puede registrar y mantener sus cuentas y tarjetas. · *Hueco: …*\n"
    "- [ ] **[ASN-003]** — El usuario puede consultar el saldo de cada cuenta por separado. · *Hueco: …* · **Depende de:** ASN-002\n"
)
PRD = FRONT + BODY + SECTION


class PrdApplyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, content=PRD):
        return write(self.dir / "prd.md", content)

    def _apply(self, p, *flags):
        return run_script("sdd-prd-apply.py", p, *flags)

    def _read(self, p):
        return Path(p).read_text(encoding="utf-8")

    # --- confirm ---------------------------------------------------------
    def test_confirm_strips_marker_and_removes_entry(self):
        p = self._write()
        r = self._apply(p, "--confirm", "ASN-001")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = self._read(p)
        # la afirmación sobrevive sin marcador inline
        self.assertIn("editar o eliminar un movimiento ya registrado.", out)
        self.assertNotIn("editar o eliminar un movimiento ya registrado. [ASUNCIÓN]", out)
        # la entrada desaparece de la sección
        self.assertNotIn("[ASN-001]", out)
        # quedan 2 marcas inline y 2 entradas (1:1 preservado)
        self.assertEqual(out.count("[ASUNCIÓN]"), 2)
        self.assertEqual(out.count("[ASN-00"), 2)

    # --- edit ------------------------------------------------------------
    def test_edit_replaces_assertion(self):
        p = self._write()
        r = self._apply(p, "--edit", "ASN-001=El usuario puede eliminar un movimiento, no editarlo.")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = self._read(p)
        self.assertIn("- El usuario puede eliminar un movimiento, no editarlo.", out)
        self.assertNotIn("editar o eliminar un movimiento ya registrado. [ASUNCIÓN]", out)
        self.assertNotIn("[ASN-001]", out)

    # --- reject ----------------------------------------------------------
    def test_reject_deletes_body_line_and_entry(self):
        p = self._write()
        r = self._apply(p, "--reject", "ASN-002")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = self._read(p)
        self.assertNotIn("registrar y mantener sus cuentas", out)
        self.assertNotIn("[ASN-002]", out)
        self.assertEqual(out.count("[ASUNCIÓN]"), 2)

    # --- posicional: la N-ésima marca ↔ la N-ésima entrada ---------------
    def test_mapping_targets_right_line(self):
        p = self._write()
        # ASN-003 (saldo por cuenta) debe tocar su propia marca, no otra
        r = self._apply(p, "--reject", "ASN-003")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = self._read(p)
        self.assertNotIn("consultar el saldo de cada cuenta", out)
        # las otras dos afirmaciones inline siguen intactas
        self.assertIn("editar o eliminar un movimiento ya registrado. [ASUNCIÓN]", out)
        self.assertIn("registrar y mantener sus cuentas y tarjetas. [ASUNCIÓN]", out)

    # --- orden divergente cuerpo≠sección: gana el texto, no la posición ---
    def test_text_match_beats_positional_on_divergent_order(self):
        # Regresión de una PRD real: el cuerpo lista la exclusión ANTES que la
        # regla transversal, pero las entradas numeran la regla ANTES que la
        # exclusión → el mapeo posicional emparejaría al revés. El match por texto
        # (las entradas citan la afirmación, aquí entre comillas) debe corregirlo.
        divergent = (
            FRONT
            + "## Alcance\n\n"
            + "- El usuario puede registrar un gasto.\n"
            + "- El usuario puede editar un movimiento. [ASUNCIÓN]\n\n"
            + "### Fuera del Alcance\n"
            + "- La conversión multidivisa queda fuera del alcance. [ASUNCIÓN]\n\n"
            + "### Reglas transversales\n"
            + "- La aplicación opera con una única moneda. [ASUNCIÓN]\n\n"
            + "---\n\n## Asunciones del PRD\n\n"
            + '- [ ] **[ASN-001]** — "El usuario puede editar un movimiento." · *Hueco: …*\n'
            + '- [ ] **[ASN-002]** — "La aplicación opera con una única moneda." · *Hueco: …*\n'
            + '- [ ] **[ASN-003]** — "La conversión multidivisa queda fuera del alcance." · *Hueco: …* · **Depende de:** ASN-002\n'
        )
        p = write(self.dir / "prd.md", divergent)
        # Rechazar ASN-002 (la regla de moneda, 2ª entrada) debe borrar la línea de
        # moneda, NO la de multidivisa (que es la 2ª marca en orden de documento).
        r = self._apply(p, "--reject", "ASN-002")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = self._read(p)
        self.assertNotIn("una única moneda", out)
        self.assertIn("multidivisa queda fuera del alcance. [ASUNCIÓN]", out)

    # --- combinación + vaciado de sección --------------------------------
    def test_resolving_all_removes_section(self):
        p = self._write()
        r = self._apply(
            p, "--confirm", "ASN-001",
            "--edit", "ASN-002=El usuario da de alta sus cuentas.",
            "--reject", "ASN-003",
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = self._read(p)
        self.assertNotIn("## Asunciones del PRD", out)
        self.assertNotIn("[ASUNCIÓN]", out)
        self.assertNotIn("[ASN-00", out)
        # no queda un `---` colgante al final
        self.assertFalse(out.rstrip().endswith("---"))

    def test_json_output_shape(self):
        p = self._write()
        r = self._apply(p, "--reject", "ASN-001,ASN-002,ASN-003", "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data["rejected"], ["ASN-001", "ASN-002", "ASN-003"])
        self.assertTrue(data["section_removed"])

    # --- seal ------------------------------------------------------------
    def test_seal_writes_value(self):
        p = self._write()
        r = self._apply(p, "--seal", "Oscar Pozo (Product Owner) (2026-07-21)")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = self._read(p)
        self.assertIn("**Aprobado por:** Oscar Pozo (Product Owner) (2026-07-21)", out)
        self.assertNotIn("[pendiente", out)

    def test_seal_overwrites_previous(self):
        p = self._write()
        self._apply(p, "--seal", "Alguien (2026-01-01)")
        r = self._apply(p, "--seal", "Otro (2026-02-02)")
        self.assertEqual(r.returncode, 0)
        out = self._read(p)
        self.assertIn("Otro (2026-02-02)", out)
        self.assertNotIn("Alguien", out)
        self.assertEqual(out.count("Aprobado por:"), 1)

    def test_seal_missing_line_fails(self):
        p = write(self.dir / "prd.md", "# PRD sin sello\n\n## Alcance\n- A.\n")
        r = self._apply(p, "--seal", "X (2026-01-01)")
        self.assertEqual(r.returncode, 2)

    # --- guardas y errores ----------------------------------------------
    def test_one_to_one_broken_fails(self):
        # 3 marcas inline pero 2 entradas → 1:1 roto.
        broken = FRONT + BODY + (
            "## Asunciones del PRD\n\n"
            "- [ ] **[ASN-001]** — A. · *Hueco: …*\n"
            "- [ ] **[ASN-002]** — B. · *Hueco: …*\n"
        )
        p = write(self.dir / "prd.md", broken)
        r = self._apply(p, "--confirm", "ASN-001")
        self.assertEqual(r.returncode, 2)
        self.assertIn("1:1", r.stdout + r.stderr)

    def test_misalignment_guard_fails(self):
        # Reordeno el cuerpo para que la 1ª marca no comparta contenido con ASN-001.
        body = (
            "## Alcance\n\n"
            "- Texto totalmente distinto sobre colores. [ASUNCIÓN]\n"
            "- El usuario puede registrar y mantener sus cuentas y tarjetas. [ASUNCIÓN]\n"
            "- El usuario puede consultar el saldo de cada cuenta por separado. [ASUNCIÓN]\n\n"
        )
        p = write(self.dir / "prd.md", FRONT + body + SECTION)
        r = self._apply(p, "--confirm", "ASN-001")
        self.assertEqual(r.returncode, 2)
        self.assertIn("desalineación", (r.stdout + r.stderr).lower())

    def test_unknown_asn_fails(self):
        p = self._write()
        r = self._apply(p, "--reject", "ASN-099")
        self.assertEqual(r.returncode, 2)
        self.assertIn("ASN-099", r.stdout + r.stderr)

    def test_ambiguous_decision_fails(self):
        p = self._write()
        r = self._apply(p, "--confirm", "ASN-001", "--reject", "ASN-001")
        self.assertEqual(r.returncode, 1)

    def test_seal_and_decisions_are_exclusive(self):
        p = self._write()
        r = self._apply(p, "--confirm", "ASN-001", "--seal", "X (2026-01-01)")
        self.assertEqual(r.returncode, 1)

    def test_no_action_fails(self):
        p = self._write()
        self.assertEqual(self._apply(p).returncode, 1)

    def test_edit_needs_equals(self):
        p = self._write()
        r = self._apply(p, "--edit", "ASN-001")
        self.assertEqual(r.returncode, 1)

    def test_invalid_args(self):
        self.assertEqual(run_script("sdd-prd-apply.py").returncode, 1)
        self.assertEqual(run_script("sdd-prd-apply.py", "a.md", "b.md").returncode, 1)

    # --- integración con sdd-prd-ready.py --------------------------------
    def test_resolve_then_seal_is_ready(self):
        p = self._write()
        r1 = self._apply(
            p, "--confirm", "ASN-001,ASN-002", "--reject", "ASN-003",
        )
        self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
        r2 = self._apply(p, "--seal", "Oscar Pozo (Product Owner) (2026-07-21)")
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        ready = run_script("sdd-prd-ready.py", p, "--json")
        data = json.loads(ready.stdout)
        self.assertEqual(data["verdict"], "READY", ready.stdout)
        self.assertEqual(data["inline_marks"], 0)
        self.assertEqual(data["asn_entries"], 0)
        self.assertTrue(data["sealed"])


if __name__ == "__main__":
    unittest.main()
