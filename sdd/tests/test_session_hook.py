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
    """Las 5 ramas de CU-1.f a nivel de DECISION del hook (que directiva emite
    ante cada estado) + la dimension commit del drift.

    Las ramas 2 ('Ahora no' escribe .sdd/version-denied) y 5 ('Actualizar
    ahora' -> wf-sdd-update) son conducta del agente y no se unit-testean; lo
    que SI es determinista es su CONTRATO: la directiva del gate contiene el
    ECO_ID exacto a persistir y nombra tanto AskUserQuestion como wf-sdd-update.

    ECO_ID = '<version>+<commit corto>', igual que en el E2E real: por eso los
    casos que dependen del ECO_ID usan _eco_git() (eco es un repo git con un
    commit), no _eco() (sin commit, ECO_ID = solo la version)."""

    def _eco(self, version):
        """eco NO-git: ECO_COMMIT vacio -> ECO_ID = solo la version."""
        eco = self.base / "eco"
        write(eco / "VERSION", version + "\n")
        write(self.home / ".sdd-home", str(eco))
        return eco

    def _eco_git(self, version):
        """eco como repo git con un commit: ECO_ID = '<version>+<commit>',
        como en produccion. Devuelve (eco, eco_id)."""
        eco = self.base / "eco"
        write(eco / "VERSION", version + "\n")
        subprocess.run([GIT, "-C", str(eco), "init", "-q"],
                       check=True, capture_output=True)
        subprocess.run([GIT, "-C", str(eco), "add", "-A"],
                       check=True, capture_output=True)
        subprocess.run([GIT, "-C", str(eco),
                        "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-q", "-m", "eco"],
                       check=True, capture_output=True)
        short = subprocess.run([GIT, "-C", str(eco), "rev-parse", "--short", "HEAD"],
                               check=True, capture_output=True, text=True).stdout.strip()
        write(self.home / ".sdd-home", str(eco))
        return eco, f"{version}+{short}"

    def _denied(self, value):
        # memoria local por-dev: el agente escribe el ECO_ID (<version>+<commit>).
        write(self.proj / ".sdd" / "version-denied", value + "\n")

    # --- Escenario 1: version no decidida -> gate --------------------------
    def test_1_undecided_emits_gate(self):
        # drift sin .sdd/version-denied -> gate (version-drift-undecided)
        self._eco("0.30.0")
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.29.0")
        out = self.run_hook()
        self.assertDirective(out, "version-drift-undecided")
        self.assertIn("0.29.0", out)
        self.assertIn("0.30.0", out)

    # --- Escenarios 1+5: el gate nombra AskUserQuestion y wf-sdd-update -----
    def test_15_gate_contract_names_askuserquestion_and_update(self):
        self._eco("0.30.0")
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.29.0")
        out = self.run_hook()
        self.assertIn("AskUserQuestion", out)   # rama 1: gate, nunca texto libre
        self.assertIn("wf-sdd-update", out)     # rama 5: Actualizar ahora

    # --- Escenario 2: el gate dicta el ECO_ID EXACTO a persistir -----------
    def test_2_gate_dictates_exact_eco_id_to_persist(self):
        # con eco git, ECO_ID = version+commit: la directiva debe nombrar el
        # fichero y contener la cadena exacta que el agente escribira alli.
        _, eco_id = self._eco_git("0.30.0")
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.29.0")
        out = self.run_hook()
        self.assertDirective(out, "version-drift-undecided")
        self.assertIn("version-denied", out)
        self.assertIn(eco_id, out)

    # --- Escenario 3: version actual ya declinada -> aviso blando, sin gate -
    def test_3_declined_current_is_soft_no_gate(self):
        _, eco_id = self._eco_git("0.30.0")
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.29.0")
        self._denied(eco_id)  # declina el ECO_ID completo (version+commit)
        out = self.run_hook()
        self.assertDirective(out, "version-drift")
        self.assertNotIn("version-drift-undecided", out)
        self.assertNotIn("AskUserQuestion", out)

    # --- Escenario 4a: el ecosistema avanza de VERSION -> re-gate ----------
    def test_4a_newer_version_re_gates(self):
        _, eco_id = self._eco_git("0.31.0")
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.29.0")
        self._denied("0.30.0+deadbee")  # declino una version anterior
        self.assertDirective(self.run_hook(), "version-drift-undecided")

    # --- Escenario 4b: misma VERSION, distinto COMMIT declinado -> re-gate --
    def test_4b_same_version_new_commit_re_gates(self):
        _, eco_id = self._eco_git("0.30.0")
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.29.0")
        self._denied("0.30.0+0000000")  # DENIED != ECO_ID (otro commit) -> gate
        self.assertDirective(self.run_hook(), "version-drift-undecided")

    # --- Dimension commit: misma version, distinto commit del sello -> drift
    def test_commit_only_drift_emits_gate(self):
        _, eco_id = self._eco_git("0.30.0")
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.30.0", commit="0000000")  # ver igual, commit no
        self.assertDirective(self.run_hook(), "version-drift-undecided")

    # --- Sin drift ---------------------------------------------------------
    def test_no_drift_when_versions_match(self):
        self._eco("0.29.0")
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.29.0")
        # commit del ecosistema vacio (eco no es repo git) -> no compara commit
        self.assertSilent(self.run_hook())

    def test_no_drift_when_version_and_commit_match(self):
        eco, _ = self._eco_git("0.29.0")
        short = subprocess.run([GIT, "-C", str(eco), "rev-parse", "--short", "HEAD"],
                               check=True, capture_output=True, text=True).stdout.strip()
        _init_json(self.proj, ["spec"], complete=True)
        _version_json(self.proj, "0.29.0", commit=short)
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
