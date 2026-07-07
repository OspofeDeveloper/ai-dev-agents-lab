"""Tests de la matriz de estados del hook sdd-session-check.sh (ROADMAP 11.3c).

El hook SessionStart inyecta (o no) una directiva [SDD-PROTOCOL] segun el
estado SDD del proyecto. Siempre sale con exit 0; la senal es su stdout.

Se aisla por completo controlando el entorno:
- CLAUDE_PROJECT_DIR -> proyecto-fixture en tmpdir
- HOME -> home falso en tmpdir (de el lee .sdd-home, sdd-deny/allowlist)
- CI="" y SDD_NON_INTERACTIVE="" -> neutralizan herencia del runner real

Cobertura: los 5 estados de directiva (mode-undecided, free->silencio,
init-pending, init-incomplete, version-drift), los opt-out (CI, no-interactivo,
HOME==proyecto), la exclusion del repo del ecosistema, deny/allowlist por ruta
(5.6) y el techo git en monorepos (5.7).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import SDD_ROOT, run_bash, write  # noqa: E402

HOOK = SDD_ROOT / "bootstrap" / "sdd-session-check.sh"
GIT = shutil.which("git")


def _init_json(root, phases, complete=True):
    """Escribe .sdd/project-init.json con las fases dadas; si complete, crea
    tambien la regla de cada fase (.claude/rules/sdd-<f>.md) para que el hook
    no la considere 'no instalada'."""
    write(root / ".sdd" / "project-init.json",
          json.dumps({"phases": list(phases)}, indent=2))
    if complete:
        for f in phases:
            write(root / ".claude" / "rules" / f"sdd-{f}.md", "---\npaths: []\n---\n")


def _mode_json(root, mode):
    write(root / ".claude" / "sdd-mode.json",
          json.dumps({"mode": mode}, indent=2))


def _version_json(root, version, commit="abc1234"):
    write(root / ".sdd" / "sdd-version.json",
          json.dumps({"version": version, "commit": commit}, indent=2))


class HookBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.proj = self.base / "project"
        self.proj.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self, project=None, home=None, **env):
        e = {
            "HOME": str(home or self.home),
            "CLAUDE_PROJECT_DIR": str(project or self.proj),
            "CI": "",
            "SDD_NON_INTERACTIVE": "",
        }
        e.update({k: str(v) for k, v in env.items()})
        r = run_bash(HOOK, env=e)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def assertDirective(self, out, token):
        self.assertIn(f"[SDD-PROTOCOL] {token}", out)

    def assertSilent(self, out):
        self.assertEqual(out.strip(), "", f"esperaba silencio, hubo: {out!r}")


class BasicStatesTest(HookBase):
    def test_virgin_project_asks_wizard(self):
        self.assertDirective(self.run_hook(), "mode-undecided")

    def test_free_mode_is_silent(self):
        _mode_json(self.proj, "free")
        self.assertSilent(self.run_hook())

    def test_sdd_mode_without_init_is_pending(self):
        _mode_json(self.proj, "sdd")
        self.assertDirective(self.run_hook(), "init-pending")

    def test_initialized_complete_is_silent(self):
        _init_json(self.proj, ["spec", "plan"], complete=True)
        self.assertSilent(self.run_hook())

    def test_initialized_incomplete_warns(self):
        # declara spec y plan pero solo instala la regla de spec
        _init_json(self.proj, ["spec", "plan"], complete=False)
        write(self.proj / ".claude" / "rules" / "sdd-spec.md", "---\npaths: []\n---\n")
        out = self.run_hook()
        self.assertDirective(out, "init-incomplete")
        self.assertIn("plan", out)

    def test_init_takes_precedence_over_mode(self):
        # con init presente, el modo no se evalua (init gana)
        _init_json(self.proj, ["spec"], complete=True)
        _mode_json(self.proj, "free")
        self.assertSilent(self.run_hook())


class VersionDriftTest(HookBase):
    def _eco(self, version):
        eco = self.base / "eco"
        write(eco / "VERSION", version + "\n")
        write(self.home / ".sdd-home", str(eco))
        return eco

    def _denied(self, value):
        # memoria local por-dev; en tests ECO_ID = solo la version (commit vacio,
        # eco no es repo git), asi que se declina pasando "<version>"
        write(self.proj / ".sdd" / "version-denied", value + "\n")

    def test_undecided_version_emits_gate(self):
        # drift sin .sdd/version-denied -> gate (version-drift-undecided)
        self._eco("0.30.0")
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.29.0")
        out = self.run_hook()
        self.assertDirective(out, "version-drift-undecided")
        self.assertIn("0.29.0", out)
        self.assertIn("0.30.0", out)

    def test_declined_current_version_soft_notice(self):
        # el usuario ya declino la version actual del ecosistema -> aviso blando,
        # NO el gate
        self._eco("0.30.0")
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.29.0")
        self._denied("0.30.0")
        out = self.run_hook()
        self.assertDirective(out, "version-drift")
        self.assertNotIn("version-drift-undecided", out)

    def test_new_version_re_gates_after_denial(self):
        # se declino una version anterior; el ecosistema avanza -> el gate reaparece
        self._eco("0.31.0")
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.29.0")
        self._denied("0.30.0")
        self.assertDirective(self.run_hook(), "version-drift-undecided")

    def test_no_drift_when_versions_match(self):
        self._eco("0.29.0")
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.29.0")
        # commit del ecosistema vacio (eco no es repo git) -> no compara commit
        self.assertSilent(self.run_hook())

    def test_no_drift_without_version_stamp(self):
        # proyecto sin .sdd/sdd-version.json -> no se puede comparar -> silencio
        self._eco("0.30.0")
        _init_json(self.proj, ["spec"], complete=True)
        self.assertSilent(self.run_hook())


class SpecialistInitPendingTest(HookBase):
    """Directiva specialist-init-pending (D-014): stack con overlay cuyo init
    tecnico aun no corrio. Apunta .sdd-home al SDD_ROOT real para que el hook
    resuelva sdd-init-detect.py (degrada en silencio si no lo encuentra)."""

    def _stack_init(self, *, specialist_workflow, stack="kmm"):
        write(self.home / ".sdd-home", str(SDD_ROOT))
        obj = {"phases": ["spec", "plan", "tasks"], "stack": stack,
               "specialist_workflow": specialist_workflow}
        write(self.proj / ".sdd" / "project-init.json", json.dumps(obj, indent=2))
        for f in ("spec", "plan", "tasks"):
            write(self.proj / ".claude" / "rules" / f"sdd-{f}.md", "---\npaths: []\n---\n")

    def test_pending_emits_directive(self):
        self._stack_init(specialist_workflow="wf-kmm-init")
        out = self.run_hook()
        self.assertDirective(out, "specialist-init-pending")
        self.assertIn("wf-kmm-init", out)

    def test_silent_after_run_logged(self):
        self._stack_init(specialist_workflow="wf-kmm-init")
        write(self.proj / ".sdd" / "stack-runs.jsonl",
              json.dumps({"workflow": "wf-kmm-init", "stack": "kmm"}) + "\n")
        out = self.run_hook()
        self.assertNotIn("specialist-init-pending", out)

    def test_silent_when_no_specialist_workflow(self):
        self._stack_init(specialist_workflow=None, stack="agnostico")
        out = self.run_hook()
        self.assertNotIn("specialist-init-pending", out)


class OptOutTest(HookBase):
    def test_ci_true_suppresses(self):
        # proyecto virgen que normalmente pediria wizard, pero CI=true -> silencio
        self.assertSilent(self.run_hook(CI="true"))

    def test_non_interactive_suppresses(self):
        self.assertSilent(self.run_hook(SDD_NON_INTERACTIVE="1"))

    def test_ci_false_does_not_suppress(self):
        self.assertDirective(self.run_hook(CI="false"), "mode-undecided")

    def test_home_equals_project_is_silent(self):
        # sesion en el propio HOME no es un proyecto
        self.assertSilent(self.run_hook(project=self.home))


class SddRepoExclusionTest(HookBase):
    def test_project_under_sdd_home_is_silent(self):
        # .sdd-home apunta a un ancestro del proyecto -> sesion de desarrollo
        # del ecosistema, no proyecto consumidor -> silencio aunque sea virgen
        write(self.home / ".sdd-home", str(self.base))
        self.assertSilent(self.run_hook())

    def test_project_outside_sdd_home_acts(self):
        # .sdd-home en una rama distinta -> el proyecto si dispara wizard
        write(self.home / ".sdd-home", str(self.base / "otra-rama"))
        self.assertDirective(self.run_hook(), "mode-undecided")


class PathListsTest(HookBase):
    def test_denylist_hit_silences(self):
        write(self.home / ".claude" / "sdd-denylist", str(self.proj) + "\n")
        self.assertSilent(self.run_hook())

    def test_denylist_miss_acts(self):
        write(self.home / ".claude" / "sdd-denylist",
              str(self.base / "otro-proyecto") + "\n")
        self.assertDirective(self.run_hook(), "mode-undecided")

    def test_denylist_comments_ignored(self):
        write(self.home / ".claude" / "sdd-denylist",
              f"# {self.proj}\n\n")  # comentada -> no silencia
        self.assertDirective(self.run_hook(), "mode-undecided")

    def test_allowlist_opt_in_outside_silences(self):
        # allowlist con un prefijo que NO cubre el proyecto -> silencio (opt-in)
        write(self.home / ".claude" / "sdd-allowlist",
              str(self.base / "solo-aqui") + "\n")
        self.assertSilent(self.run_hook())

    def test_allowlist_covering_acts(self):
        write(self.home / ".claude" / "sdd-allowlist", str(self.proj) + "\n")
        self.assertDirective(self.run_hook(), "mode-undecided")


@unittest.skipIf(GIT is None, "git no disponible")
class MonorepoCeilingTest(HookBase):
    def _git_init(self, root):
        root.mkdir(parents=True, exist_ok=True)
        subprocess.run([GIT, "init", "-q", str(root)], check=True,
                       capture_output=True)

    def test_finds_marker_in_ancestor_up_to_git_root(self):
        # repo git con .sdd/ incompleto en la raiz; sesion en un subpaquete
        repo = self.base / "repo"
        self._git_init(repo)
        _init_json(repo, ["spec", "plan"], complete=False)
        write(repo / ".claude" / "rules" / "sdd-spec.md", "---\npaths: []\n---\n")
        sub = repo / "packages" / "app"
        sub.mkdir(parents=True)
        out = self.run_hook(project=sub)
        # encontro el .sdd/ del ancestro -> reporta init-incomplete (falta plan)
        self.assertDirective(out, "init-incomplete")
        self.assertIn("plan", out)

    def test_closest_ancestor_wins(self):
        # raiz init completo, subpaquete con su propio .sdd/ incompleto: gana el cercano
        repo = self.base / "repo"
        self._git_init(repo)
        _init_json(repo, ["spec"], complete=True)
        sub = repo / "packages" / "app"
        _init_json(sub, ["tasks"], complete=False)
        out = self.run_hook(project=sub)
        self.assertDirective(out, "init-incomplete")
        self.assertIn("tasks", out)

    def test_ceiling_stops_at_git_root(self):
        # marcador POR ENCIMA del git root no debe encontrarse desde el repo
        _init_json(self.base, ["spec"], complete=False)  # fuera del repo
        repo = self.base / "repo"
        self._git_init(repo)
        # repo sin marcador propio; sesion en el repo
        self.assertDirective(self.run_hook(project=repo), "mode-undecided")

    def test_no_git_no_upward_walk(self):
        # sin git, solo se mira el propio dir: marcador en el padre no se ve
        _init_json(self.base, ["spec"], complete=False)
        sub = self.base / "sub"
        sub.mkdir()
        self.assertDirective(self.run_hook(project=sub), "mode-undecided")


if __name__ == "__main__":
    unittest.main()
