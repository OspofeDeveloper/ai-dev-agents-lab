"""Tests de integracion para install.sh (ROADMAP 11.3b).

Instala el ecosistema en proyectos sinteticos (tmpdir) y comprueba los
invariantes que han mordido en sesiones reales:
- instalacion por fase (solo las piezas de la fase + sus dependencias cross-fase)
- scripts de enforcement en .sdd/scripts/ con sello de version
- reglas de fase con frontmatter `paths:`
- --prune reconcilia huerfanos de un install anterior con mas fases
- sin --prune, los huerfanos quedan con aviso
- idempotencia del merge de settings.json
- SDD_PROJECT_ROOT redirige scripts/.sdd a la raiz real
- fase desconocida -> exit 1

Black-box: corre `bash install.sh ...` con cwd = proyecto-fixture.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import SDD_ROOT, run_bash, run_script, write  # noqa: E402

INSTALL = SDD_ROOT / "install.sh"

# Scripts de enforcement que install.sh distribuye a .sdd/scripts/
ENFORCEMENT_SCRIPTS = [
    "sdd-seal.py", "sdd-gate-check.py", "sdd-task-state.py", "sdd-sync-check.py",
    "sdd-skill-allow.py", "sdd-amend.py", "sdd-features-index.py",
    "sdd-project-status.py", "sdd-kb-check.py", "sdd-release.py", "sdd-next-id.py",
    "sdd-resolve-path.py", "sdd-design-resolve.py", "sdd-source-drift.py",
]


class InstallBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def install(self, *args, env=None):
        r = run_bash(INSTALL, *args, cwd=self.proj, env=env)
        return r

    # atajos de rutas instaladas
    @property
    def claude(self):
        return self.proj / ".claude"

    def skill_dir(self, name):
        return self.claude / "skills" / name

    def agent_file(self, name):
        return self.claude / "agents" / name


class InstallAllTest(InstallBase):
    def test_install_all_lays_out_everything(self):
        r = self.install("all")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # agentes de varias fases
        for a in ("prd-expert.md", "sdd-spec-writer.md",
                  "design-system-architect.md", "design-feature-architect.md",
                  "plan-architect.md", "plan-auditor.md", "task-generator.md",
                  "qa-engineer.md"):
            self.assertTrue(self.agent_file(a).exists(), f"falta agents/{a}")
        # skills representativas de cada fase
        for s in ("kb-prd-expert", "kb-spec-expert", "kb-design-expert",
                  "kb-plan-expert", "kb-tasks-expert"):
            self.assertTrue(self.skill_dir(s).exists(), f"falta skills/{s}")
        # reglas de fase con carga perezosa
        for p in ("prd", "spec", "design", "plan", "tasks"):
            self.assertTrue((self.claude / "rules" / f"sdd-{p}.md").exists(),
                            f"falta rules/sdd-{p}.md")
        # CLAUDE.md raiz (pipeline completo)
        self.assertTrue((self.claude / "CLAUDE.md").exists())
        # settings.json
        self.assertTrue((self.claude / "settings.json").exists())

    def test_enforcement_scripts_stamped(self):
        r = self.install("all")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        scripts_dir = self.proj / ".sdd" / "scripts"
        for s in ENFORCEMENT_SCRIPTS:
            p = scripts_dir / s
            self.assertTrue(p.exists(), f"falta .sdd/scripts/{s}")
            second = p.read_text(encoding="utf-8").splitlines()[1]
            self.assertTrue(second.startswith("# sdd-version:"),
                            f"{s} sin sello de version en la linea 2: {second!r}")
        # sello de instalacion del proyecto
        ver = self.proj / ".sdd" / "sdd-version.json"
        self.assertTrue(ver.exists())
        meta = json.loads(ver.read_text(encoding="utf-8"))
        self.assertEqual(meta["installed_by"], "install.sh")
        self.assertIn("version", meta)

    def test_phase_rules_have_paths_frontmatter(self):
        self.install("all")
        spec_rule = (self.claude / "rules" / "sdd-spec.md").read_text(encoding="utf-8")
        self.assertTrue(spec_rule.startswith("---\npaths:"),
                        "la regla de fase debe empezar con frontmatter paths:")
        self.assertIn('"**/*_spec.md"', spec_rule)

    def test_default_arg_is_all(self):
        # sin argumento equivale a 'all'
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(self.skill_dir("kb-plan-expert").exists())


class ArtifactsGlobTest(InstallBase):
    """--artifacts-<fase>=<dir> reescribe el glob de directorio de la regla (CU-1.m, (B))."""

    def _spec_rule(self):
        return (self.claude / "rules" / "sdd-spec.md").read_text(encoding="utf-8")

    def test_noncanonical_dir_rewrites_directory_glob(self):
        r = self.install("spec", "--artifacts-spec=specs")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rule = self._spec_rule()
        self.assertIn('"specs/**"', rule)          # glob de directorio reescrito
        self.assertNotIn('"spec/**"', rule)         # el canónico ya no está
        # los globs por nombre de artefacto no se tocan
        self.assertIn('"**/*_spec.md"', rule)
        self.assertIn('"**/features/*/spec/**"', rule)

    def test_trailing_slash_is_trimmed(self):
        r = self.install("spec", "--artifacts-spec=specs/")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rule = self._spec_rule()
        self.assertIn('"specs/**"', rule)
        self.assertNotIn('"specs//**"', rule)

    def test_no_flag_keeps_canonical_glob(self):
        r = self.install("spec")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('"spec/**"', self._spec_rule())

    def test_verify_accepts_the_rewritten_rule(self):
        # (A)+(B) end-to-end: install reescribe, verify (rule-globs) lo acepta.
        self.install("prd,spec,design", "--design-role=system", "--artifacts-spec=specs")
        write(self.proj / ".sdd" / "project-init.json", json.dumps({
            "dispatcher": "wf-project-init", "topology": "authoring",
            "surfaces": [], "design_role": "system",
            "artifacts": {"prd": "prd", "spec": "specs", "design": "design"},
        }))
        write(self.proj / ".claude" / "CLAUDE.md", "x")
        write(self.proj / ".gitignore", ".claude/settings.local.json\n")
        r = run_script("sdd-init-detect.py",
                       "verify", "--phases", "prd,spec,design", "--root", str(self.proj))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        checks = json.loads(r.stdout)
        self.assertTrue(next(c for c in checks if c["check"] == "rule-globs")["ok"])


class InstallByPhaseTest(InstallBase):
    def test_spec_only_installs_spec_and_prd_deps(self):
        r = self.install("spec")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # spec presente
        self.assertTrue(self.skill_dir("kb-spec-expert").exists())
        self.assertTrue(self.agent_file("sdd-spec-writer.md").exists())
        # dependencias de prd que spec necesita
        self.assertTrue(self.skill_dir("kb-prd-expert").exists())
        self.assertTrue(self.agent_file("prd-expert.md").exists())
        # plan/tasks NO instalados
        self.assertFalse(self.agent_file("plan-architect.md").exists())
        self.assertFalse(self.agent_file("task-generator.md").exists())
        self.assertFalse((self.claude / "rules" / "sdd-plan.md").exists())
        # regla de spec si
        self.assertTrue((self.claude / "rules" / "sdd-spec.md").exists())

    def test_plan_pulls_cross_phase_deps(self):
        r = self.install("plan")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # dependencias cross-fase declaradas en install.sh
        for dep in ("kb-spec-expert", "kb-a11y-expert", "kb-a11y-web-expert",
                    "kb-design-governance", "kb-plan-expert"):
            self.assertTrue(self.skill_dir(dep).exists(), f"falta dep {dep}")
        self.assertTrue(self.agent_file("plan-architect.md").exists())
        self.assertTrue(self.agent_file("plan-auditor.md").exists())

    def test_single_phase_claude_md_is_phase_doc(self):
        # con una sola fase, CLAUDE.md raiz = el de la fase, no el pipeline completo
        self.install("spec")
        root_md = (self.claude / "CLAUDE.md").read_text(encoding="utf-8")
        phase_md = (SDD_ROOT / "pipeline" / "spec" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(root_md, phase_md)

    def test_unknown_phase_exits_1(self):
        r = self.install("frontend")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no reconocida", r.stdout + r.stderr)


class PruneTest(InstallBase):
    def test_prune_removes_orphans_from_previous_install(self):
        # install completo y luego reinstalar con menos fases + --prune
        self.install("all")
        self.assertTrue(self.agent_file("task-generator.md").exists())
        self.assertTrue(self.skill_dir("kb-tasks-expert").exists())

        r = self.install("prd,spec", "--prune")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # piezas de tasks/plan/design eliminadas
        self.assertFalse(self.agent_file("task-generator.md").exists(),
                         "task-generator deberia haberse podado")
        self.assertFalse(self.skill_dir("kb-tasks-expert").exists())
        self.assertFalse((self.claude / "rules" / "sdd-tasks.md").exists())
        self.assertFalse((self.claude / "rules" / "sdd-plan.md").exists())
        # lo de prd/spec sigue
        self.assertTrue(self.skill_dir("kb-spec-expert").exists())
        self.assertTrue((self.claude / "rules" / "sdd-spec.md").exists())

    def test_without_prune_orphans_remain_with_warning(self):
        self.install("all")
        r = self.install("prd,spec")  # sin --prune
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # el huerfano sigue instalado
        self.assertTrue(self.agent_file("task-generator.md").exists())
        # y se avisa
        self.assertIn("--prune", r.stdout)
        self.assertIn("fases no seleccionadas", r.stdout)


class StaleOverlayPruneTest(InstallBase):
    """Cambiar el stack de un overlay (kmm) a uno sin overlay (ios) retira el
    overlay ajeno SIEMPRE (sin --prune): no es inerte como una fase de mas, su
    regla cargaria convenciones del stack equivocado y solo puede haber un stack.
    Regresion del bug visto probando CU-1.o B2 (correccion kmm->ios dejaba el
    overlay kmm huerfano: skills wf-kmm-*/kb-kmm-*, agentes kmm-*, sdd-kmm.md)."""

    def _init_json(self, stack):
        write(self.proj / ".sdd" / "project-init.json",
              json.dumps({"name": "s", "topology": "standalone",
                          "stack": stack, "phases": ["spec", "plan", "tasks"]}))

    def test_stack_change_prunes_foreign_overlay(self):
        self._init_json("kmm")
        self.install("spec,plan,tasks")
        # baseline: overlay kmm presente
        self.assertTrue(self.skill_dir("wf-kmm-init").exists())
        self.assertTrue(self.agent_file("kmm-tester.md").exists())
        self.assertTrue((self.claude / "rules" / "sdd-kmm.md").exists())

        # cambio de stack a ios (sin overlay) y re-install SIN --prune
        self._init_json("ios")
        r = self.install("spec,plan,tasks")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # overlay kmm retirado por completo (exclusivas: wf-/kb-kmm-/kb-cmp-, agentes kmm-*, regla)
        self.assertFalse(self.skill_dir("wf-kmm-init").exists(),
                         "wf-kmm-init deberia haberse podado")
        self.assertFalse(self.skill_dir("kb-kmm-clean-architecture").exists())
        self.assertFalse(self.skill_dir("kb-cmp-resources").exists())
        self.assertFalse(self.agent_file("kmm-tester.md").exists())
        self.assertFalse((self.claude / "rules" / "sdd-kmm.md").exists())
        # base intacto: las de basename compartido vuelven a su variante generica
        self.assertTrue(self.skill_dir("kb-plan-expert").exists())
        self.assertTrue(self.agent_file("plan-architect.md").exists())
        self.assertTrue(self.agent_file("task-generator.md").exists())
        # aviso de modo generico para un stack sin overlay
        self.assertIn("no tiene overlay especialista", r.stdout)
        self.assertIn("overlay ajeno", r.stdout)

    def test_same_stack_reinstall_keeps_overlay(self):
        # mismo stack: 6b NO debe podar el overlay del propio proyecto
        self._init_json("kmm")
        self.install("spec,plan,tasks")
        r = self.install("spec,plan,tasks")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(self.skill_dir("wf-kmm-init").exists())
        self.assertTrue(self.agent_file("kmm-tester.md").exists())
        self.assertTrue((self.claude / "rules" / "sdd-kmm.md").exists())
        self.assertNotIn("overlay ajeno", r.stdout)


class IdempotencyTest(InstallBase):
    def test_settings_merge_idempotent(self):
        self.install("all")
        settings = self.claude / "settings.json"
        first = settings.read_text(encoding="utf-8")
        r = self.install("all")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(first, settings.read_text(encoding="utf-8"),
                         "re-install no debe cambiar settings.json")

    def test_reinstall_is_clean(self):
        # dos installs completos consecutivos: sin error, sin huerfanos
        self.install("all")
        r = self.install("all")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("fases no seleccionadas", r.stdout)


class ProjectRootTest(InstallBase):
    def test_sdd_project_root_redirects_enforcement(self):
        # install.sh con cwd en un subdir pero SDD_PROJECT_ROOT a la raiz:
        # los scripts/.sdd van a la raiz, no al subdir.
        subdir = self.proj / "sub"
        subdir.mkdir()
        r = run_bash(INSTALL, "tasks", cwd=subdir,
                     env={"SDD_PROJECT_ROOT": str(self.proj)})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # .sdd en la raiz, no en el subdir
        self.assertTrue((self.proj / ".sdd" / "scripts" / "sdd-seal.py").exists())
        self.assertFalse((subdir / ".sdd").exists())
        # las skills (.claude) si van junto al cwd (no usan SDD_PROJECT_ROOT)
        self.assertTrue((subdir / ".claude" / "skills" / "kb-tasks-expert").exists())


if __name__ == "__main__":
    unittest.main()
