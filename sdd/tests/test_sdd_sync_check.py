"""Black-box tests para scripts/sdd-sync-check.py.

Detector determinista de deriva PRD→spec (ROADMAP 1.3): sella un hash del PRD
origen en el header del spec (`derived_from_prd_hash`) y lo recomputa después.
Verifica:
  - seal escribe el hash (sha256:prefijo) y es idempotente (IN_SYNC).
  - check IN_SYNC (exit 0) cuando el PRD no cambió; DERIVA (exit 2) cuando sí.
  - --mark degrada status_sync a needs_review solo si había deriva.
  - SIN_SELLO (spec sin hash), NO_APLICA (derived_from_prd: N/A),
    PRD_NO_RESUELVE (path declarado ilegible — no bloquea).
  - check-all escanea un árbol y agrega exit codes.
  - Args inválidos (exit 1).
Planted-vs-clean: el caso "limpio" sella y verifica sin tocar el PRD; el
"planted" muta el PRD tras sellar.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


PRD = """\
# PRD: MiProducto

## RF-1: Login
El usuario puede autenticarse.
"""


def spec_text(prd_rel="prd.md", with_hash=False, status_sync="in_sync"):
    hash_line = "\n> derived_from_prd_hash: pending" if not with_hash else ""
    return (
        "# Spec: Login\n\n"
        f"> Feature ID: F-001\n"
        f"> derived_from_prd: `{prd_rel}`\n"
        f"> derived_from_prd_version: 1\n"
        f"> status_sync: {status_sync}"
        f"{hash_line}\n\n"
        "### HU-1: como usuario quiero entrar\n"
        "### CA-001: login OK ← HU-1\n"
    )


class SealTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.prd = write(self.dir / "prd.md", PRD)
        self.spec = write(self.dir / "login_spec.md", spec_text())

    def tearDown(self):
        self.tmp.cleanup()

    def test_seal_writes_hash(self):
        r = run_script("sdd-sync-check.py", "seal", self.spec)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("sha256:", self.spec.read_text(encoding="utf-8"))

    def test_seal_idempotent(self):
        run_script("sdd-sync-check.py", "seal", self.spec)
        first = self.spec.read_text(encoding="utf-8")
        r = run_script("sdd-sync-check.py", "seal", self.spec)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("IN_SYNC", r.stdout)
        self.assertEqual(first, self.spec.read_text(encoding="utf-8"))

    def test_no_aplica_when_na(self):
        write(self.spec, spec_text(prd_rel="N/A"))
        r = run_script("sdd-sync-check.py", "seal", self.spec)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("NO_APLICA", r.stdout)

    def test_seal_unresolvable_prd_exit_1(self):
        write(self.spec, spec_text(prd_rel="no_existe.md"))
        r = run_script("sdd-sync-check.py", "seal", self.spec)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)


class CheckCleanTest(unittest.TestCase):
    """Camino limpio: sellado y verificado sin tocar el PRD -> IN_SYNC."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.prd = write(self.dir / "prd.md", PRD)
        self.spec = write(self.dir / "login_spec.md", spec_text())
        run_script("sdd-sync-check.py", "seal", self.spec)

    def tearDown(self):
        self.tmp.cleanup()

    def test_check_in_sync_exit_0(self):
        r = run_script("sdd-sync-check.py", "check", self.spec)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("IN_SYNC", r.stdout)

    def test_check_does_not_write_without_mark(self):
        # Aún en sync: check no debe mutar el spec.
        before = self.spec.read_text(encoding="utf-8")
        run_script("sdd-sync-check.py", "check", self.spec)
        self.assertEqual(before, self.spec.read_text(encoding="utf-8"))


class CheckPlantedTest(unittest.TestCase):
    """Camino planted: mutar el PRD tras sellar -> DERIVA."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.prd = write(self.dir / "prd.md", PRD)
        self.spec = write(self.dir / "login_spec.md", spec_text())
        run_script("sdd-sync-check.py", "seal", self.spec)

    def tearDown(self):
        self.tmp.cleanup()

    def test_check_deriva_exit_2(self):
        self.prd.write_text(PRD + "\n## RF-2: SSO añadido\n", encoding="utf-8")
        r = run_script("sdd-sync-check.py", "check", self.spec)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("DERIVA", r.stdout)

    def test_mark_downgrades_status_sync(self):
        self.prd.write_text(PRD + "\n## RF-2: SSO añadido\n", encoding="utf-8")
        r = run_script("sdd-sync-check.py", "check", self.spec, "--mark")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("needs_review", self.spec.read_text(encoding="utf-8"))

    def test_no_drift_no_mark_change(self):
        # Sin deriva, --mark no debe degradar nada.
        r = run_script("sdd-sync-check.py", "check", self.spec, "--mark")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("in_sync", self.spec.read_text(encoding="utf-8"))
        self.assertNotIn("needs_review", self.spec.read_text(encoding="utf-8"))


class CheckEdgeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.prd = write(self.dir / "prd.md", PRD)

    def tearDown(self):
        self.tmp.cleanup()

    def test_sin_sello_exit_0(self):
        # Spec sin hash sellado: SIN_SELLO, conservador (no bloquea).
        spec = write(self.dir / "login_spec.md", spec_text())
        r = run_script("sdd-sync-check.py", "check", spec)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("SIN_SELLO", r.stdout)

    def test_no_aplica_exit_0(self):
        spec = write(self.dir / "login_spec.md", spec_text(prd_rel="N/A"))
        r = run_script("sdd-sync-check.py", "check", spec)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("NO_APLICA", r.stdout)

    def test_prd_no_resuelve_exit_0(self):
        # Sellamos, luego borramos el PRD: el sello existe pero el path no resuelve.
        spec = write(self.dir / "login_spec.md", spec_text())
        run_script("sdd-sync-check.py", "seal", spec)
        self.prd.unlink()
        r = run_script("sdd-sync-check.py", "check", spec)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PRD_NO_RESUELVE", r.stdout)


class CheckAllTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.prd = write(self.dir / "prd.md", PRD)

    def tearDown(self):
        self.tmp.cleanup()

    def test_check_all_clean_exit_0(self):
        s1 = write(self.dir / "features" / "a" / "a_spec.md", spec_text(prd_rel="../../prd.md"))
        run_script("sdd-sync-check.py", "seal", s1)
        r = run_script("sdd-sync-check.py", "check-all", self.dir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("sin deriva", r.stdout)

    def test_check_all_with_drift_exit_2(self):
        s1 = write(self.dir / "features" / "a" / "a_spec.md", spec_text(prd_rel="../../prd.md"))
        run_script("sdd-sync-check.py", "seal", s1)
        self.prd.write_text(PRD + "\nmutado\n", encoding="utf-8")
        r = run_script("sdd-sync-check.py", "check-all", self.dir)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("DERIVA", r.stdout)

    def test_check_all_no_specs_exit_0(self):
        r = run_script("sdd-sync-check.py", "check-all", self.dir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class UsageTest(unittest.TestCase):
    def test_no_command_exit_1(self):
        r = run_script("sdd-sync-check.py")
        self.assertEqual(r.returncode, 1)

    def test_bad_command_exit_1(self):
        r = run_script("sdd-sync-check.py", "nope", "x.md")
        self.assertEqual(r.returncode, 1)

    def test_check_all_not_a_dir_exit_1(self):
        r = run_script("sdd-sync-check.py", "check-all", "/no/existe/dir")
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
