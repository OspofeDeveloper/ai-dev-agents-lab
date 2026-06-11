"""Black-box tests para scripts/sdd-task-state.py.

Cubre: init (anade Estado + tabla Progreso), transiciones validas/invalidas,
elegibilidad de `next` con dependencias, bloqueo de HECHA por deps no HECHAS,
persistencia entre invocaciones, idempotencia, y exit codes.

Estados reales del script: PENDIENTE / EN_CURSO / HECHA / BLOQUEADA.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


TASKS = """\
# Tasks: Login

## T-001: crear modelo
- **Dependencies:** ninguna
- **Spec CA:** CA-001

## T-002: endpoint
- **Dependencies:** T-001
- **Spec CA:** CA-002

## T-003: ui
- **Dependencies:** T-002
- **Spec CA:** CA-003
"""


class TaskStateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.tasks = write(self.dir / "login_tasks.md", TASKS)

    def tearDown(self):
        self.tmp.cleanup()

    def _init(self):
        return run_script("sdd-task-state.py", "init", self.tasks)

    def _set(self, tid, state, *extra):
        return run_script("sdd-task-state.py", "set", self.tasks, tid, state, *extra)

    def test_init_adds_states_and_progreso(self):
        r = self._init()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = self.tasks.read_text(encoding="utf-8")
        # Cada una de las 3 tasks recibe su linea de Estado: PENDIENTE.
        self.assertEqual(text.count("- **Estado:** PENDIENTE"), 3)
        self.assertIn("## Progreso", text)
        self.assertIn("0/3 HECHA", text)
        self.assertIn("3 pendientes", text)

    def test_init_is_idempotent(self):
        self._init()
        first = self.tasks.read_text(encoding="utf-8")
        self._init()
        self.assertEqual(first, self.tasks.read_text(encoding="utf-8"),
                         "re-init no debe cambiar bytes")

    def test_next_returns_first_eligible(self):
        self._init()
        r = run_script("sdd-task-state.py", "next", self.tasks)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "T-001")

    def test_next_uninitialized_exits_2(self):
        r = run_script("sdd-task-state.py", "next", self.tasks)
        self.assertEqual(r.returncode, 2)
        self.assertIn("SIN_INICIALIZAR", r.stderr)

    def test_valid_transition_pendiente_to_en_curso(self):
        self._init()
        r = self._set("T-001", "EN_CURSO")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("EN_CURSO", self.tasks.read_text(encoding="utf-8"))

    def test_invalid_transition_pendiente_to_hecha(self):
        self._init()
        r = self._set("T-001", "HECHA")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("TRANSICION INVALIDA", r.stderr)

    def test_hecha_blocked_by_unsatisfied_deps(self):
        self._init()
        self._set("T-002", "EN_CURSO")
        # T-002 depende de T-001 que sigue PENDIENTE -> no puede pasar a HECHA
        r = self._set("T-002", "HECHA")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("DEPENDENCIAS NO HECHAS", r.stderr)

    def test_hecha_allowed_when_deps_done(self):
        self._init()
        self._set("T-001", "EN_CURSO")
        r = self._set("T-001", "HECHA")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # ahora T-002 es elegible
        n = run_script("sdd-task-state.py", "next", self.tasks)
        self.assertEqual(n.stdout.strip(), "T-002")

    def test_full_flow_pendiente_en_curso_hecha_persists(self):
        self._init()
        self.assertEqual(self._set("T-001", "EN_CURSO").returncode, 0)
        self.assertEqual(self._set("T-001", "HECHA").returncode, 0)
        # persistencia: una nueva invocacion check ve T-001 HECHA
        c = run_script("sdd-task-state.py", "check", self.tasks)
        self.assertIn("T-001: HECHA", c.stdout)
        self.assertIn("1/3 HECHA", c.stdout)

    def test_bloqueada_requires_motivo(self):
        self._init()
        r = self._set("T-001", "BLOQUEADA")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("motivo", r.stderr.lower())
        r2 = self._set("T-001", "BLOQUEADA", "--motivo", "falta API externa")
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)

    def test_hecha_reopen_only_with_force(self):
        self._init()
        self._set("T-001", "EN_CURSO")
        self._set("T-001", "HECHA")
        r = self._set("T-001", "PENDIENTE")
        self.assertEqual(r.returncode, 2)
        r2 = self._set("T-001", "PENDIENTE", "--force")
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)

    def test_set_same_state_noop(self):
        self._init()
        r = self._set("T-001", "PENDIENTE")
        self.assertEqual(r.returncode, 0)
        self.assertIn("sin cambios", r.stdout)

    def test_completo_when_all_done(self):
        self._init()
        for tid in ("T-001", "T-002", "T-003"):
            self._set(tid, "EN_CURSO")
            self._set(tid, "HECHA")
        r = run_script("sdd-task-state.py", "next", self.tasks)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "COMPLETO")

    def test_unknown_task_id_exit_1(self):
        self._init()
        r = self._set("T-999", "EN_CURSO")
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
