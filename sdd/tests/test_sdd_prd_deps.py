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

    def test_invalid_args(self):
        self.assertEqual(run_script("sdd-prd-deps.py").returncode, 1)
        self.assertEqual(
            run_script("sdd-prd-deps.py", "a.md", "b.md").returncode, 1
        )


if __name__ == "__main__":
    unittest.main()
