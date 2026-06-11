"""Black-box tests para scripts/sdd-seal.py.

Cubre: sellado de un plan sellable, rechazo de planes no sellables (CA sin
cubrir, [INFERIDO]/[CRITICO]/[INCOMPLETO] en el spec), idempotencia del sellado,
deteccion de tamper (editar el plan tras sellar invalida la re-verificacion),
--unseal, y deuda tecnica (TD) aprobada vs pendiente.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


SPEC_CLEAN = """\
# Spec: Login

> Feature ID: F-001

### HU-1: como usuario quiero entrar

### CA-001: login OK ← HU-1
Dado credenciales validas, entra.

### CA-002: login KO ← HU-1
Dado credenciales invalidas, error.
"""


def plan_text(spec_rel="login_spec.md", estado="BORRADOR",
              cas=("CA-001", "CA-002"), include_gaps=True, extra=""):
    """Construye un plan SDD parametrizable."""
    refs = "\n".join(f"- Implementa {ca}." for ca in cas)
    gaps = ""
    if include_gaps:
        gaps = (
            "\n**DESIGN_GAPs:** ninguno\n"
            "**TECH_GAPs:** ninguno\n"
            "**TRACE_GAPs:** ninguno\n"
            "**PLAN_GAPs:** ninguno\n"
        )
    return (
        f"# Plan: Login\n\n"
        f"> Spec origen: `{spec_rel}`\n"
        f"**Estado:** {estado}\n\n"
        f"## Arquitectura\n\n{refs}\n\n"
        f"{extra}"
        f"## Checklist de Trazabilidad\n\n"
        f"Todos los CAs cubiertos.\n"
        f"{gaps}"
    )


class SealableTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.spec = write(self.dir / "login_spec.md", SPEC_CLEAN)
        self.plan = write(self.dir / "login_plan.md", plan_text())

    def tearDown(self):
        self.tmp.cleanup()

    def test_check_passes_for_sealable_plan(self):
        r = run_script("sdd-seal.py", "plan", self.plan, "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("sellable", r.stdout)
        # --check no debe escribir: el estado sigue BORRADOR
        self.assertIn("BORRADOR", self.plan.read_text(encoding="utf-8"))

    def test_seal_writes_validado(self):
        r = run_script("sdd-seal.py", "plan", self.plan, "--seal")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("VALIDADO", self.plan.read_text(encoding="utf-8"))

    def test_seal_is_idempotent(self):
        run_script("sdd-seal.py", "plan", self.plan, "--seal")
        first = self.plan.read_text(encoding="utf-8")
        r = run_script("sdd-seal.py", "plan", self.plan, "--seal")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(first, self.plan.read_text(encoding="utf-8"),
                         "re-sellar un plan ya VALIDADO debe ser byte-identico")

    def test_unseal_always_downgrades(self):
        run_script("sdd-seal.py", "plan", self.plan, "--seal")
        r = run_script("sdd-seal.py", "plan", self.plan, "--unseal")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("BORRADOR", self.plan.read_text(encoding="utf-8"))

    def test_tamper_detection_after_seal(self):
        """Editar el spec tras sellar (introducir [INFERIDO]) -> --check falla (2)."""
        run_script("sdd-seal.py", "plan", self.plan, "--seal")
        # Tamper: degradamos el spec origen tras el sello.
        self.spec.write_text(SPEC_CLEAN + "\n### CA-003: extra [INFERIDO] ← HU-1\n",
                             encoding="utf-8")
        r = run_script("sdd-seal.py", "plan", self.plan, "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("INFERIDO", r.stdout)

    def test_tamper_uncovered_ca_after_seal(self):
        """Anadir un CA nuevo al spec que el plan no cubre -> --check falla."""
        run_script("sdd-seal.py", "plan", self.plan, "--seal")
        self.spec.write_text(SPEC_CLEAN + "\n### CA-009: nuevo ← HU-1\nNo cubierto.\n",
                             encoding="utf-8")
        r = run_script("sdd-seal.py", "plan", self.plan, "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("CA-009", r.stdout)


class NonSealableTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _spec(self, content):
        return write(self.dir / "login_spec.md", content)

    def test_uncovered_ca_rejected(self):
        self._spec(SPEC_CLEAN)
        # El plan solo cubre CA-001
        write(self.dir / "login_plan.md", plan_text(cas=("CA-001",)))
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("CA-002", r.stdout)

    def test_spec_with_inferido_rejected(self):
        self._spec(SPEC_CLEAN + "\n### CA-003: x [INFERIDO] ← HU-1\n")
        write(self.dir / "login_plan.md", plan_text(cas=("CA-001", "CA-002", "CA-003")))
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("INFERIDO", r.stdout)

    def test_spec_with_critico_rejected(self):
        self._spec(SPEC_CLEAN + "\n[CRÍTICO] falta info\n")
        write(self.dir / "login_plan.md", plan_text())
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("CRÍTICO", r.stdout)

    def test_plan_with_incompleto_rejected(self):
        self._spec(SPEC_CLEAN)
        write(self.dir / "login_plan.md", plan_text(extra="[INCOMPLETO] falta diseno\n\n"))
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("INCOMPLETO", r.stdout)

    def test_open_gap_rejected(self):
        self._spec(SPEC_CLEAN)
        plan = plan_text(include_gaps=False) + (
            "\n**DESIGN_GAPs:** ninguno\n"
            "**TECH_GAPs:** falta definir cache\n"
            "**TRACE_GAPs:** ninguno\n"
            "**PLAN_GAPs:** ninguno\n"
        )
        write(self.dir / "login_plan.md", plan)
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("TECH_GAPs", r.stdout)

    def test_unresolvable_spec_origin_rejected(self):
        write(self.dir / "login_plan.md", plan_text(spec_rel="no_existe_spec.md"))
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_pending_td_blocks(self):
        self._spec(SPEC_CLEAN)
        td = (
            "### TD-001: cache diferida\n"
            "- **Decisión:** no cachear ahora\n"
            "- **A pesar de:** la latencia\n"
            "- **Riesgo asumido:** lentitud en picos\n"
            "- **Queda pendiente:** anadir cache\n"
            "- **Componentes afectados:** API\n"
            "- **Aprobada por:** PENDIENTE\n\n"
        )
        write(self.dir / "login_plan.md", plan_text(extra=td))
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("TD-001", r.stdout)

    def test_approved_td_does_not_block(self):
        self._spec(SPEC_CLEAN)
        td = (
            "### TD-001: cache diferida\n"
            "- **Decisión:** no cachear ahora\n"
            "- **A pesar de:** la latencia\n"
            "- **Riesgo asumido:** lentitud en picos\n"
            "- **Queda pendiente:** anadir cache\n"
            "- **Componentes afectados:** API\n"
            "- **Aprobada por:** Oscar (PM)\n\n"
        )
        write(self.dir / "login_plan.md", plan_text(extra=td))
        r = run_script("sdd-seal.py", "plan", self.dir / "login_plan.md", "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class UsageTest(unittest.TestCase):
    def test_bad_args_exit_1(self):
        r = run_script("sdd-seal.py", "plan", "x.md", "--nope")
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
