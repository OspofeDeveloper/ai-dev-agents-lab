"""Black-box tests para scripts/sdd-prd-deps.py.

Grafo determinista de dependencias entre asunciones (Q2a, DECISIONS D-029). Una
entrada `[ASN-XXX]` puede declarar `Depende de: ASN-YYY` (ID pelado). Verifica:
  - grafo bien formado → exit 0; --json emite {nodes, graph, dangling_edges, cycles}.
  - arista a una asunción inexistente (dangling) → exit 2.
  - ciclo / autodependencia → exit 2.
  - sin dependencias → grafo vacío, exit 0.
  - --check --rejected: dependiente de una rechazada NO rechazado → huérfana, exit 2.
  - --check --rejected: dependiente también rechazado → consistente, exit 0.
  - --check sin --rejected → error de uso (exit 1); args inválidos (exit 1).

D-037 (backstop con dientes):
  - --keep <dependiente>: tercer desenlace (conservada conscientemente) → exit 0.
  - --keep de otra cosa NO silencia la huérfana real → sigue exit 2.
  - VACUOUS: rechazos sobre un documento sin entradas `[ASN-XXX]` (el backstop se
    corrió DESPUÉS de sdd-prd-apply.py) → exit 2, no OK. Es el fallo real de CU-2.j.
  - sin rechazos sobre documento sin entradas → NO es vacuo (exit 0).
  - --keep sin --check → error de uso (exit 1).
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


def prd(entries: str) -> str:
    return (
        "---\ntype: product-requirements\nproduct: X\n---\n\n# PRD: X\n\n"
        "## Alcance\n- El usuario puede A.\n\n"
        "## Asunciones del PRD\n" + entries + "\n"
    )


# 007 depende de 006 (arista válida)
GRAPH_OK = prd(
    "- [ ] **[ASN-006]** — Cuentas gestionables. · *Hueco: …*\n"
    "- [ ] **[ASN-007]** — Saldo por cuenta. · *Hueco: …* · **Depende de:** ASN-006\n"
)
# 007 depende de 099 (inexistente)
GRAPH_DANGLING = prd(
    "- [ ] **[ASN-007]** — Saldo por cuenta. · **Depende de:** ASN-099\n"
)
# ciclo 006<->007
GRAPH_CYCLE = prd(
    "- [ ] **[ASN-006]** — A. · **Depende de:** ASN-007\n"
    "- [ ] **[ASN-007]** — B. · **Depende de:** ASN-006\n"
)
NO_DEPS = prd(
    "- [ ] **[ASN-001]** — A. · *Hueco: …*\n"
    "- [ ] **[ASN-002]** — B. · *Hueco: …*\n"
)


class PrdDepsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, content, *flags):
        p = write(self.dir / "prd.md", content)
        return run_script("sdd-prd-deps.py", p, *flags)

    def test_graph_ok(self):
        r = self._run(GRAPH_OK)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OK", r.stdout)

    def test_json_shape(self):
        r = self._run(GRAPH_OK, "--json")
        data = json.loads(r.stdout)
        self.assertEqual(data["graph"], {"ASN-007": ["ASN-006"]})
        self.assertEqual(data["dangling_edges"], [])
        self.assertEqual(data["cycles"], [])
        self.assertIn("ASN-006", data["nodes"])

    def test_dangling_edge_fails(self):
        r = self._run(GRAPH_DANGLING)
        self.assertEqual(r.returncode, 2)
        self.assertIn("MALFORMED", r.stdout)
        self.assertIn("ASN-099", r.stdout)

    def test_cycle_fails(self):
        r = self._run(GRAPH_CYCLE)
        self.assertEqual(r.returncode, 2)
        self.assertIn("MALFORMED", r.stdout)

    def test_no_deps_is_ok(self):
        r = self._run(NO_DEPS, "--json")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout)["graph"], {})

    def test_check_orphan_fails(self):
        # rechazo 006 pero NO 007 → 007 queda huérfana.
        r = self._run(GRAPH_OK, "--check", "--rejected", "ASN-006")
        self.assertEqual(r.returncode, 2)
        self.assertIn("ASN-007", r.stdout)

    def test_check_consistent_ok(self):
        # rechazo ambas → coherente.
        r = self._run(GRAPH_OK, "--check", "--rejected", "ASN-006,ASN-007")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_check_json_orphans(self):
        r = self._run(GRAPH_OK, "--check", "--rejected", "ASN-006", "--json")
        self.assertEqual(json.loads(r.stdout)["orphans"], ["ASN-007"])

    def test_check_requires_rejected(self):
        r = self._run(GRAPH_OK, "--check")
        self.assertEqual(r.returncode, 1)

    # --- D-037: tercer desenlace (--keep) y guarda de vacuidad ---

    def test_keep_resolves_orphan(self):
        # 006 rechazada, 007 depende de ella pero el usuario la CONSERVA a
        # conciencia (la dependencia queda satisfecha de otro modo) → coherente.
        r = self._run(GRAPH_OK, "--check", "--rejected", "ASN-006", "--keep", "ASN-007")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ASN-007", r.stdout)

    def test_keep_json_reports_kept(self):
        r = self._run(
            GRAPH_OK, "--check", "--rejected", "ASN-006", "--keep", "ASN-007", "--json"
        )
        data = json.loads(r.stdout)
        self.assertEqual(data["orphans"], [])
        self.assertEqual(data["kept"], ["ASN-007"])

    def test_keep_of_unrelated_does_not_silence_orphan(self):
        # --keep debe NOMBRAR al dependiente; nombrar otra cosa no lo silencia.
        r = self._run(GRAPH_OK, "--check", "--rejected", "ASN-006", "--keep", "ASN-099")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("ASN-007", r.stdout)

    def test_check_after_apply_is_vacuous_not_ok(self):
        # Documento SIN entradas `[ASN-XXX]` (ya aplicadas y sección eliminada) pero
        # con rechazos: no hay nada que comprobar → VACUOUS, nunca OK. (CU-2.j)
        applied = (
            "---\ntype: product-requirements\nproduct: X\n---\n\n# PRD: X\n\n"
            "## Alcance\n- El usuario puede A.\n"
        )
        r = self._run(applied, "--check", "--rejected", "ASN-006")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("VACUOUS", r.stdout)

    def test_vacuous_json_flag(self):
        applied = (
            "---\ntype: product-requirements\nproduct: X\n---\n\n# PRD: X\n\n"
            "## Alcance\n- El usuario puede A.\n"
        )
        r = self._run(applied, "--check", "--rejected", "ASN-006", "--json")
        self.assertTrue(json.loads(r.stdout)["vacuous"])

    def test_no_rejections_on_empty_doc_is_not_vacuous(self):
        # Sin rechazos no hay nada que pueda quedar huérfano: no es un fallo.
        applied = (
            "---\ntype: product-requirements\nproduct: X\n---\n\n# PRD: X\n\n"
            "## Alcance\n- El usuario puede A.\n"
        )
        r = self._run(applied, "--check", "--rejected", "")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_keep_requires_check(self):
        r = self._run(GRAPH_OK, "--keep", "ASN-007")
        self.assertEqual(r.returncode, 1)

    def test_invalid_args(self):
        self.assertEqual(run_script("sdd-prd-deps.py").returncode, 1)
        self.assertEqual(
            run_script("sdd-prd-deps.py", "a.md", "b.md").returncode, 1
        )


if __name__ == "__main__":
    unittest.main()
