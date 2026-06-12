"""Black-box tests para scripts/sdd-release.py.

Cubre el último eslabón de trazabilidad (ROADMAP 2.7): vincular el cierre de una
feature a un commit SHA / tag. Verifica:
  - Gate determinista: solo QA APTO / APTO_CON_RESERVAS pasa; NO_APTO o sin
    _qa_report.md son rechazados (exit 2).
  - SHA mecánico: en un repo git temporal, el SHA capturado es el del HEAD real
    (no tecleado); fuera de repo git y sin --sha, rechaza.
  - Generación del _release.md con la coordenada (SHA, tag, veredicto, nota).
  - --tag / --note; manejo de re-releases acumulados (R-001, R-002…).
  - Layout subcarpeta (tasks/) y plano legacy.
  - Args/estado inválidos (exit 1) y modo check.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


SPEC = """\
# Spec: Login

> Feature ID: F-001

### HU-1: como usuario quiero entrar
### CA-001: login OK ← HU-1
"""


def qa_report(verdict="APTO"):
    return (
        "# QA Report: Login\n\n"
        f"> Veredicto: {verdict}\n\n"
        "## Cobertura\n\nTodos los CAs cubiertos.\n"
    )


def init_git_repo(repo: Path) -> str:
    """Inicializa un repo git con un commit y devuelve el SHA completo del HEAD."""
    def g(*a):
        subprocess.run(["git", "-C", str(repo), *a], capture_output=True,
                       text=True, check=True)
    g("init")
    g("config", "user.email", "t@t.test")
    g("config", "user.name", "Tester")
    g("config", "commit.gpgsign", "false")
    write(repo / "f.txt", "x")
    g("add", "-A")
    g("commit", "-m", "init")
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True).stdout.strip()
    return sha


class SubdirLayoutTest(unittest.TestCase):
    """Layout con subcarpeta tasks/ dentro de un repo git real."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.head_sha = init_git_repo(self.repo)
        self.fdir = self.repo / "features" / "login"
        write(self.fdir / "spec" / "login_spec.md", SPEC)
        write(self.fdir / "tasks" / "login_qa_report.md", qa_report("APTO"))
        # Re-añade y commitea para que el árbol esté limpio y HEAD vigente.
        subprocess.run(["git", "-C", str(self.repo), "add", "-A"],
                       capture_output=True, text=True, check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "commit.gpgsign", "false"],
                       capture_output=True, text=True, check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-m", "feature"],
                       capture_output=True, text=True, check=True)
        self.head_sha = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True).stdout.strip()
        self.release = self.fdir / "tasks" / "login_release.md"

    def tearDown(self):
        self.tmp.cleanup()

    def test_stamp_captures_real_head_sha(self):
        r = run_script("sdd-release.py", "stamp", self.fdir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(self.release.exists(), "debe generar _release.md")
        text = self.release.read_text(encoding="utf-8")
        # El SHA grabado es el del HEAD real, no inventado.
        self.assertIn(self.head_sha, text)
        self.assertIn(self.head_sha[:9], text)
        self.assertIn("F-001", text)
        self.assertIn("APTO", text)
        self.assertIn("R-001", text)

    def test_stamp_with_tag_and_note(self):
        r = run_script("sdd-release.py", "stamp", self.fdir,
                       "--tag", "v1.0.0", "--note", "primer release")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = self.release.read_text(encoding="utf-8")
        self.assertIn("`v1.0.0`", text)
        self.assertIn("primer release", text)

    def test_no_tag_renders_dash(self):
        run_script("sdd-release.py", "stamp", self.fdir)
        text = self.release.read_text(encoding="utf-8")
        self.assertIn("**Tag:** —", text)

    def test_re_release_accumulates(self):
        run_script("sdd-release.py", "stamp", self.fdir, "--note", "uno")
        r = run_script("sdd-release.py", "stamp", self.fdir, "--note", "dos")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = self.release.read_text(encoding="utf-8")
        self.assertIn("R-001", text)
        self.assertIn("R-002", text)
        self.assertIn("uno", text)
        self.assertIn("dos", text)

    def test_check_reports_released(self):
        run_script("sdd-release.py", "stamp", self.fdir)
        r = run_script("sdd-release.py", "check", self.fdir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("RELEASED", r.stdout)
        self.assertIn("R-001", r.stdout)

    def test_apto_con_reservas_passes_and_records_verdict(self):
        write(self.fdir / "tasks" / "login_qa_report.md",
              qa_report("APTO_CON_RESERVAS"))
        r = run_script("sdd-release.py", "stamp", self.fdir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("APTO_CON_RESERVAS",
                      self.release.read_text(encoding="utf-8"))


class GateTest(unittest.TestCase):
    """Gate determinista de cierre: sin QA APTO no hay release."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        init_git_repo(self.repo)
        self.fdir = self.repo / "features" / "login"
        write(self.fdir / "spec" / "login_spec.md", SPEC)

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_qa_report_rejected(self):
        r = run_script("sdd-release.py", "stamp", self.fdir)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("RECHAZADO", r.stderr)
        self.assertIn("_qa_report.md", r.stderr)

    def test_no_apto_rejected(self):
        write(self.fdir / "tasks" / "login_qa_report.md", qa_report("NO_APTO"))
        r = run_script("sdd-release.py", "stamp", self.fdir)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("NO_APTO", r.stderr)
        # No debe haberse escrito ningún release.
        self.assertFalse((self.fdir / "tasks" / "login_release.md").exists())


class GitSourceTest(unittest.TestCase):
    """Captura del SHA: --sha explícito vs ausencia de repo git."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.fdir = self.root / "features" / "login"
        write(self.fdir / "spec" / "login_spec.md", SPEC)
        write(self.fdir / "tasks" / "login_qa_report.md", qa_report("APTO"))
        self.release = self.fdir / "tasks" / "login_release.md"

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_git_and_no_sha_rejected(self):
        # self.root NO es un repo git.
        r = run_script("sdd-release.py", "stamp", self.fdir)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("repo git", r.stderr)
        self.assertFalse(self.release.exists())

    def test_explicit_sha_used_when_no_repo(self):
        r = run_script("sdd-release.py", "stamp", self.fdir,
                       "--sha", "deadbeefcafef00d", "--date", "2026-01-15")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = self.release.read_text(encoding="utf-8")
        self.assertIn("deadbeefcafef00d", text)
        self.assertIn("2026-01-15", text)


class FlatLayoutTest(unittest.TestCase):
    """Layout plano legacy: artefactos directamente en features/<n>/."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.fdir = self.root / "features" / "login"
        write(self.fdir / "login_spec.md", SPEC)
        write(self.fdir / "login_qa_report.md", qa_report("APTO"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_flat_layout_release_beside_qa(self):
        r = run_script("sdd-release.py", "stamp", self.fdir,
                       "--sha", "abc123def456")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rel = self.fdir / "login_release.md"
        self.assertTrue(rel.exists(), "release junto al qa_report en layout plano")
        self.assertIn("abc123def456", rel.read_text(encoding="utf-8"))


class UsageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_bad_mode_exit_1(self):
        r = run_script("sdd-release.py", "nope", self.root)
        self.assertEqual(r.returncode, 1)

    def test_no_args_exit_1(self):
        r = run_script("sdd-release.py")
        self.assertEqual(r.returncode, 1)

    def test_missing_feature_dir_exit_1(self):
        r = run_script("sdd-release.py", "stamp", self.root / "no_existe")
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
