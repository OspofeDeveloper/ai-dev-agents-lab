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
    "sdd-prd-ready.py", "sdd-prd-frontmatter.py", "sdd-prd-deps.py",
    "sdd-prd-apply.py",
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

    # Las 5 fases con framing dual-audience (D-018 piloto PRD + roll-out D-022
    # completo: spec, prd, design, plan, tasks).
    DUAL_AUDIENCE_PHASES = ("prd", "spec", "design", "plan", "tasks")

    def test_phase_rules_are_dual_audience(self):
        # Las reglas de fase se heredan en los subagentes escritores (Claude Code
        # inyecta project rules en subagentes, sin opt-out). Su contenido no puede
        # afirmar un rol de orquestador exclusivo, o contradice al agente que sí
        # redacta el artefacto. Ver DECISIONS D-018 / D-022.
        self.install("all")
        for p in self.DUAL_AUDIENCE_PHASES:
            rule = (self.claude / "rules" / f"sdd-{p}.md").read_text(encoding="utf-8")
            self.assertNotIn("Instrucciones para el Orquestador", rule,
                             f"sdd-{p}.md conserva título de orquestador")
            self.assertNotIn("Eres el **orquestador**", rule,
                             f"sdd-{p}.md conserva rol en 2a persona")
            self.assertIn("Audiencia.", rule, f"sdd-{p}.md sin nota de Audiencia")

    def test_phase_rules_have_no_rootmap_table(self):
        # D-023: el rootmap plano de skills se eliminó del cuerpo lazy (era
        # redundante con las `description` de los skills (eager) + sdd-routing.md,
        # y empíricamente no load-bearing — D-022). Backstop anti-regresión: la
        # tabla no debe reaparecer en ninguna fase. El enrutado NO depende de ella.
        self.install("all")
        for p in self.DUAL_AUDIENCE_PHASES:
            rule = (self.claude / "rules" / f"sdd-{p}.md").read_text(encoding="utf-8")
            self.assertNotIn("## Rootmap de workflow skills", rule,
                             f"sdd-{p}.md reintroduce la tabla rootmap (ver D-023)")

    def test_prd_create_overwrite_gate_is_risk_weighted(self):
        # D-024: el gate de sobreescritura de wf-prd-create es ponderado por
        # riesgo, no un "¿seguro?" plano. Debe distinguir PRD sellado (siempre
        # confirma, avisa del descarte) de draft (regenera sin nagging si la
        # orden es explícita). Backstop: las 3 ramas siguen en el skill instalado.
        self.install("all")
        skill = (self.skill_dir("wf-prd-create") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("EXISTE_SELLADO", skill,
                      "wf-prd-create pierde la rama de PRD sellado (ver D-024)")
        self.assertIn("EXISTE_DRAFT", skill,
                      "wf-prd-create pierde la rama de draft (ver D-024)")
        self.assertIn("Aprobado por:", skill,
                      "wf-prd-create pierde la detección de sello (ver D-024)")

    def test_prd_create_honors_explicit_output_path(self):
        # D-025: la ruta de salida explícita es autoritativa; si diverge del
        # layout del proyecto, wf-prd-create pregunta (AskUserQuestion), nunca
        # redirige en silencio al default. Backstop: el gate de divergencia
        # (Paso 4a) sigue en el skill instalado.
        self.install("all")
        skill = (self.skill_dir("wf-prd-create") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("autoritativa", skill,
                      "wf-prd-create pierde que la ruta explícita es autoritativa (ver D-025)")
        self.assertIn("diverge", skill,
                      "wf-prd-create pierde el gate de divergencia de ruta (ver D-025)")
        self.assertIn("D-025", skill,
                      "wf-prd-create pierde la referencia a D-025")

    def test_routing_rule_has_spec_precondition(self):
        # La readiness/precondición de spec ya NO vive en la regla de fase lazy
        # (sdd-spec.md): se relocalizó al carril eager (sdd-routing.md, y la frontera
        # mecánica en sdd-orchestration.md). Ver DECISIONS D-022.
        self.install("all")
        spec_rule = (self.claude / "rules" / "sdd-spec.md").read_text(encoding="utf-8")
        self.assertNotIn("en estado revisable", spec_rule,
                         "la precondición de spec debe haberse movido a sdd-routing.md")
        routing = (self.claude / "rules" / "sdd-routing.md").read_text(encoding="utf-8")
        self.assertIn("revisable", routing)
        # la frontera mecánica (sdd-prd-ready.py) vive en la regla de orquestación
        self.assertIn("sdd-prd-ready.py", self._orch_rule())

    def _orch_rule(self):
        return (self.claude / "rules" / "sdd-orchestration.md").read_text(encoding="utf-8")

    def test_orchestration_rule_is_eager(self):
        # La disciplina transversal va en una regla SIN `paths:`, que Claude Code
        # carga eager (al arrancar), a diferencia de las reglas de fase lazy. Ese
        # carril es el que cubre el momento "orientar antes de tocar ficheros".
        # Ver DECISIONS D-021.
        self.install("all")
        rule = self._orch_rule()
        # frontmatter presente pero SIN paths: (la ausencia de paths: = eager)
        self.assertTrue(rule.startswith("---\n"),
                        "la regla de orquestacion debe tener frontmatter")
        header = rule.split("---", 2)[1]
        # ninguna linea del frontmatter puede ser la clave `paths:` (eso lo haria lazy)
        self.assertFalse(
            any(ln.strip().startswith("paths:") for ln in header.splitlines()),
            "la regla eager NO debe declarar la clave paths: (o seria lazy)")
        # senales de disciplina transversal
        self.assertIn("topología", rule)
        self.assertIn("readiness", rule.lower())
        self.assertIn("Orden del pipeline", rule)

    def test_orchestration_rule_is_dual_audience(self):
        # Al ser eager, la heredan tambien los subagentes escritores (sin opt-out,
        # ver D-018). No puede afirmar un rol de orquestador exclusivo en 2a persona.
        self.install("all")
        rule = self._orch_rule()
        self.assertNotIn("Eres el orquestador", rule)
        self.assertNotIn("No redactas", rule)
        self.assertIn("Audiencia.", rule)

    def test_orchestration_rule_has_communication_discipline(self):
        # El orquestador no surfacea nombres de skill (wf-*) ni slash-commands al
        # usuario; narra en lenguaje natural. Handoff agnostico a comandos (D-019).
        self.install("all")
        rule = self._orch_rule()
        self.assertIn("Comunicación con el usuario", rule)
        self.assertIn("lenguaje natural", rule)
        self.assertIn("agnóstico a comandos", rule)

    def test_orchestration_rule_forbids_auto_arming_overrides(self):
        # El orquestador nunca auto-arma un flag --allow-* de override: lo arma el
        # usuario. Ante una precondicion bloqueante invoca sin el flag, deja que el
        # gate se detenga y devuelva el bloqueo, y presenta la eleccion con
        # AskUserQuestion; solo re-invoca con --allow-* si el usuario fuerza (D-026).
        self.install("all")
        rule = self._orch_rule()
        self.assertIn("--allow-", rule)
        self.assertIn("arma el usuario", rule)
        self.assertIn("AskUserQuestion", rule)
        self.assertIn("D-026", rule)

    def test_orchestration_rule_delegates_qualitative_read(self):
        # D-031: al orientar sobre readiness, el orquestador cita el veredicto
        # mecanico y enruta; NO hace Read del artefacto completo ni emite su propio
        # diagnostico cualitativo en el hilo principal (eso es del experto en su skill).
        self.install("all")
        rule = self._orch_rule()
        self.assertIn("lectura cualitativa", rule)
        self.assertIn("D-031", rule)

    def test_prd_review_edit_assumption_is_inline_free_text(self):
        # El gate de asunciones permite editar en el momento: el usuario escribe el
        # texto nuevo en el campo libre en vez de elegir "Editar" y diferirlo (Q1).
        self.install("all")
        skill = (self.skill_dir("wf-prd-review") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("campo libre", skill,
                      "wf-prd-review pierde la edicion inline por texto libre (Q1)")

    def test_seal_gates_prefill_approver_from_git(self):
        # D-027: los 3 gates de sellado registran la identidad del aprobador,
        # precargando el nombre con `git config user.name` (rol opcional).
        self.install("all")
        for skill_name in ("wf-prd-review", "wf-plan-validate", "wf-qa-verify"):
            skill = (self.skill_dir(skill_name) / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("git config user.name", skill,
                          f"{skill_name} no precarga el aprobador de git (ver D-027)")

    def test_prd_review_gate_waits_for_diagnosis(self):
        # Q1: el gate de asunciones (Paso 5.5) espera el diagnostico del prd-expert
        # (Paso 4) y no se paraleliza — el gate usa los flags de gobernanza.
        self.install("all")
        skill = (self.skill_dir("wf-prd-review") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("no lo paralelices", skill.lower(),
                      "wf-prd-review pierde que el gate espera al diagnostico (Q1)")

    def test_prd_change_reopens_seal(self):
        # D-028: un cambio de PRD reabre el sello (status in-review + Aprobado por
        # a pendiente); el sello solo lo re-establece wf-prd-review.
        self.install("all")
        skill = (self.skill_dir("wf-prd-change") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("reabre el sello", skill.lower(),
                      "wf-prd-change pierde la reapertura del sello (ver D-028)")
        self.assertIn("in-review", skill)
        self.assertIn("--reopen", skill,
                      "wf-prd-change no reabre el sello por script determinista (D-032)")

    def test_prd_change_marks_its_inferences(self):
        # D-039: la anti-fabricacion (Regla 12) rige cada escritura sobre el PRD, no
        # solo la creacion. wf-prd-change marca [ASUNCION] lo que no traza a la
        # peticion; en conformance CU-7.b pasada 2 escribio una capacidad inferida y
        # estrecho una exclusion existente sin marca alguna -> el PRD quedaba 0=0 y el
        # review lo declaraba LISTO sobre contenido fabricado.
        self.install("all")
        skill = (self.skill_dir("wf-prd-change") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("[ASUNCIÓN]", skill,
                      "wf-prd-change no obliga a marcar sus inferencias (D-039)")
        self.assertIn("[ASN-XXX]", skill,
                      "wf-prd-change no exige la entrada de la seccion de asunciones (D-039)")
        # La escapatoria concreta observada: estrechar una exclusion se siente como
        # higiene y no lo es. Debe estar nombrada, no solo implicada por la regla general.
        self.assertIn("Estrechar o reinterpretar una exclusión", skill,
                      "wf-prd-change debe nombrar el estrechamiento de exclusiones (D-039)")
        # La otra escapatoria: diferir a Spec una decision de alcance.
        self.assertIn("materia de Spec", skill,
                      "wf-prd-change debe atajar el 'esto es materia de Spec' (D-039)")
        # No puede resolverlas: corre en fork, asi que no puede preguntar. Redactado
        # SIN nombrar la tool: sdd-structural-lint marca FORK-ASKUSER-CONFLICT
        # (blocking) en cuanto un skill `context: fork` menciona ese token, aunque sea
        # para negarlo. Si esto se reescribe, mantener la formulacion negativa sin token.
        self.assertIn("no puedes presentar preguntas al usuario", skill,
                      "wf-prd-change debe declarar que no puede resolver las asunciones (D-039)")
        self.assertIn("OPEN_ASSUMPTIONS", skill,
                      "wf-prd-change debe remitir el estado abierto al gate del review (D-039)")

    def test_prd_change_runs_in_main_with_gate(self):
        # D-040: wf-prd-change deja de ser `context: fork` y se re-arquitectura al
        # modelo de wf-prd-review (main orquesta y sostiene el gate, el prd-expert
        # analiza y escribe). Un fork no puede preguntar, asi que la clasificacion y
        # las bifurcaciones de alcance se decidian sin humano.
        self.install("all")
        skill = (self.skill_dir("wf-prd-change") / "SKILL.md").read_text(encoding="utf-8")
        head = skill.split("---")[1]
        self.assertNotIn("context: fork", head,
                         "wf-prd-change no puede seguir siendo un fork: no podria preguntar (D-040)")
        self.assertIn("AskUserQuestion", head,
                      "wf-prd-change necesita AskUserQuestion para su gate (D-040)")
        self.assertIn("Agent", head,
                      "wf-prd-change delega el analisis y la escritura via Agent (D-040)")
        # Simetria con wf-prd-review: main no lee ni escribe el artefacto.
        self.assertNotIn("Read", head.split("allowed-tools:")[1].split("\n")[0],
                         "main no debe declarar Read: la lectura es del prd-expert (D-031/D-038)")
        self.assertNotIn("Write", head.split("allowed-tools:")[1].split("\n")[0],
                         "main no debe declarar Write: la escritura es del prd-expert (D-038)")
        self.assertIn("Siempre, sin excepción por trivialidad", skill,
                      "el gate no puede saltar segun el criterio del agente (D-040)")
        self.assertIn("--defer-decisions", skill,
                      "wf-prd-change pierde el modo sin gate para la cascada (D-040)")
        self.assertIn("la ambigüedad se marca", skill,
                      "el modo sin gate pierde su invariante: marcar en vez de decidir (D-040)")

    def test_prd_change_cascade_defers_decisions(self):
        # D-040: la cascada es un fork y no puede heredar el gate de wf-prd-change,
        # asi que la invoca con --defer-decisions. Su "checkpoint humano (1) aprobar el
        # cambio de producto" nunca fue un checkpoint: era un fork invocando a un fork.
        self.install("all")
        skill = (self.skill_dir("wf-prd-change-cascade") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("--defer-decisions", skill,
                      "la cascada debe invocar wf-prd-change con --defer-decisions (D-040)")
        self.assertIn("decisión aplazada", skill,
                      "la cascada debe dejar de llamar checkpoint humano al paso 3 (D-040)")
        self.assertIn("wf-prd-review", skill,
                      "la cascada debe remitir la decision aplazada al gate del review (D-040)")

    def test_prd_review_uses_dependency_graph(self):
        # D-029/Q2a: el gate de asunciones carga el grafo determinista de
        # dependencias (sdd-prd-deps.py) y corre el backstop --check pre-sello.
        self.install("all")
        skill = (self.skill_dir("wf-prd-review") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("sdd-prd-deps.py", skill,
                      "wf-prd-review no usa el grafo de dependencias (ver D-029)")
        self.assertIn("--check", skill,
                      "wf-prd-review pierde el backstop pre-sello de huérfanas (D-029)")

    def test_prd_review_backstop_runs_before_apply(self):
        # D-037: el backstop de dependencias LEE las entradas [ASN-XXX]; si corre
        # después de sdd-prd-apply.py la sección ya no existe y el check es un no-op
        # que se lee como garantía (fallo real en CU-2.j). El orden es normativo.
        self.install("all")
        skill = (self.skill_dir("wf-prd-review") / "SKILL.md").read_text(encoding="utf-8")
        check_at = skill.find("--check --rejected")
        apply_at = skill.find("sdd-prd-apply.py \"<path>\" --confirm")
        self.assertNotEqual(check_at, -1, "falta el backstop --check --rejected (D-029)")
        self.assertNotEqual(apply_at, -1, "falta la aplicación por sdd-prd-apply.py (D-030)")
        self.assertLess(check_at, apply_at,
                        "el backstop de dependencias debe ir ANTES del apply (D-037): "
                        "después, la sección de asunciones ya no existe y el check es vacuo")
        self.assertIn("--keep", skill,
                      "wf-prd-review pierde el tercer desenlace --keep del backstop (D-037)")
        self.assertIn("VACUOUS", skill,
                      "wf-prd-review no advierte del check vacuo por orden invertido (D-037)")

    def test_prd_review_declares_editing_remit(self):
        # D-038: el ámbito de edición del review es cerrado y explícito (tres runs de
        # conformance resolvieron la misma edición de tres formas distintas), el hilo
        # principal no escribe el artefacto aunque tenga la tool, y la clasificación de
        # gobernanza la decide el prd-expert (no se enruta a wf-prd-change contra él).
        self.install("all")
        skill = (self.skill_dir("wf-prd-review") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Qué ediciones son de este review", skill,
                      "wf-prd-review pierde la tabla de ámbito de edición (D-038)")
        self.assertIn("nunca escribe el artefacto", skill,
                      "wf-prd-review pierde la regla de que main no escribe (D-038)")
        self.assertIn("no es enforcement duro", skill,
                      "wf-prd-review debe advertir que allowed-tools no es enforcement (D-038)")
        self.assertIn("prd-expert", skill,
                      "wf-prd-review pierde la delegación al prd-expert (D-038)")
        self.assertIn("wf-prd-change", skill,
                      "wf-prd-review pierde la frontera con wf-prd-change (D-038)")

    def test_prd_review_applies_edits_via_script(self):
        # D-030/Q3: las ediciones del review (asunciones + sello) se aplican con
        # sdd-prd-apply.py, y el hilo principal NO tiene Read/Write sobre el PRD
        # (imposible cargar el documento entero en contexto).
        self.install("all")
        skill = (self.skill_dir("wf-prd-review") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("sdd-prd-apply.py", skill,
                      "wf-prd-review no aplica las ediciones por script (ver D-030)")
        self.assertIn("--seal", skill,
                      "wf-prd-review pierde el sellado por script (D-030)")
        fm = skill.split("---", 2)[1]
        at = [ln for ln in fm.splitlines() if ln.startswith("allowed-tools:")][0]
        self.assertNotIn("Read", at,
                         "wf-prd-review no debe declarar Read: main no carga el PRD (D-030)")
        self.assertNotIn("Write", at,
                         "wf-prd-review no debe declarar Write: edita por script (D-030)")

    def test_orchestration_rule_readiness_line_is_topology_gated(self):
        # La linea de la frontera PRD->Spec solo aparece si se instalan ambas
        # fases; en una topologia sin ese par no se cuela (D-021).
        self.install("prd,spec")
        self.assertIn("sdd-prd-ready.py", self._orch_rule())
        # instalacion limpia (otro tmpdir) con una fase sin el par prd+spec
        with tempfile.TemporaryDirectory() as other:
            r = run_bash(INSTALL, "plan", cwd=Path(other))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            rule = (Path(other) / ".claude" / "rules" / "sdd-orchestration.md").read_text(encoding="utf-8")
            self.assertNotIn("sdd-prd-ready.py", rule)

    def test_routing_rule_is_eager_and_dual_audience(self):
        # sdd-routing.md: desambiguación/fronteras de fase, carga eager (sin paths:),
        # dual-audience (la heredan los subagentes). Ver DECISIONS D-022.
        self.install("spec")
        routing_path = self.claude / "rules" / "sdd-routing.md"
        self.assertTrue(routing_path.exists(), "falta rules/sdd-routing.md con spec instalado")
        routing = routing_path.read_text(encoding="utf-8")
        self.assertTrue(routing.startswith("---\n"), "sdd-routing.md sin frontmatter")
        header = routing.split("---", 2)[1]
        self.assertFalse(any(ln.strip().startswith("paths:") for ln in header.splitlines()),
                         "sdd-routing.md NO debe declarar paths: (o seria lazy)")
        # desambiguación que las descriptions no cubren
        self.assertIn("features-first", routing)
        self.assertIn("rigor", routing.lower())
        # dual-audience
        self.assertNotIn("Eres el **orquestador**", routing)
        self.assertIn("Audiencia.", routing)

    def test_routing_rule_is_scoped(self):
        # Topology-gating por fase: la desambiguación de una fase solo aparece si
        # esa fase está instalada; no se filtra la de otras. Ver D-022. (Sustituye
        # al antiguo topology_gated: cerrado el roll-out, las 5 fases aportan
        # routing.md, así que la "ausencia total" ya no es alcanzable por install;
        # el invariante que queda es el scoping.)
        self.install("plan")
        routing = (self.claude / "rules" / "sdd-routing.md").read_text(encoding="utf-8")
        self.assertIn("BORRADOR", routing)              # marcador de plan presente
        self.assertNotIn("style_family", routing)       # design NO instalado → no se cuela
        self.assertNotIn("create → review", routing)    # prd NO instalado → no se cuela

    def test_routing_rule_has_prd_border(self):
        # La fase prd aporta su desambiguación eager (frontera create → review /
        # gate de asunciones) a sdd-routing.md. Ver DECISIONS D-022 (roll-out).
        self.install("prd")
        routing_path = self.claude / "rules" / "sdd-routing.md"
        self.assertTrue(routing_path.exists(), "falta rules/sdd-routing.md con prd instalado")
        routing = routing_path.read_text(encoding="utf-8")
        self.assertIn("create → review", routing)
        self.assertIn("wf-prd-review", routing)
        # dual-audience también en la contribución de prd
        self.assertIn("Audiencia.", routing)

    def test_routing_rule_has_design_border(self):
        # La fase design aporta su desambiguación eager (precondición spec+brief,
        # trampas intake/delta/branch/variant) a sdd-routing.md. Ver D-022 (roll-out).
        self.install("design")
        routing_path = self.claude / "rules" / "sdd-routing.md"
        self.assertTrue(routing_path.exists(), "falta rules/sdd-routing.md con design instalado")
        routing = routing_path.read_text(encoding="utf-8")
        # desambiguaciones críticas que las descriptions no cubren
        self.assertIn("style_family", routing)
        self.assertIn("wf-design-intake", routing)
        self.assertIn("Audiencia.", routing)

    def test_routing_rule_has_plan_border(self):
        # La fase plan aporta su desambiguación eager (gate BORRADOR → VALIDADO,
        # precondición spec+handoff Design) a sdd-routing.md. Ver D-022 (roll-out).
        self.install("plan")
        routing = (self.claude / "rules" / "sdd-routing.md").read_text(encoding="utf-8")
        self.assertIn("BORRADOR", routing)
        self.assertIn("VALIDADO", routing)
        self.assertIn("Audiencia.", routing)

    def test_routing_rule_has_tasks_border(self):
        # La fase tasks aporta su desambiguación eager (precondición plan VALIDADO,
        # las 3 vías task-run/bug/amend) a sdd-routing.md. Ver D-022 (roll-out).
        self.install("tasks")
        routing = (self.claude / "rules" / "sdd-routing.md").read_text(encoding="utf-8")
        self.assertIn("wf-task-run", routing)
        self.assertIn("wf-spec-amend", routing)   # back-edge desde ejecución
        self.assertIn("Audiencia.", routing)

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


class KbPrdExpertContentTest(unittest.TestCase):
    """Backstop de contenido del kb-prd-expert (D-033/D-034): afila el juicio del
    prd-expert; no hay script que lo mecanice, así que fijamos las cadenas clave."""

    KB = SDD_ROOT / "pipeline" / "prd" / "skills" / "kb-prd-expert"

    def _skill(self):
        return (self.KB / "SKILL.md").read_text(encoding="utf-8")

    def _prohibited(self):
        return (self.KB / "references" / "prd_prohibited_items.md").read_text(encoding="utf-8")

    def test_regla12_names_dressed_restatement(self):
        # D-033: la Regla 12 distingue reenunciado desnudo vs vestido y da el ejemplo canónico
        s = self._skill()
        self.assertIn("Reenunciado vestido", s)
        self.assertIn("multi-divisa fuera de alcance", s)
        # y aclara que Depende de: no es para reenunciados
        self.assertIn("no es para reenunciados", s.lower())

    def test_prohibited_lists_presentation_format(self):
        # D-034: el catálogo cita el formato de presentación como contaminación dura
        p = self._prohibited()
        self.assertIn("Formato de presentación de una capacidad", p)
        self.assertIn("en un calendario", p)
        # y el frame de "tabla = dura, no matiz opcional"
        self.assertIn("contaminación dura", p)

    def test_prohibited_temporal_does_not_launder_format(self):
        # D-036: la nota ataja el escape "la dimensión temporal es negocio" para bajar la severidad
        p = self._prohibited()
        self.assertIn("dimensión temporal no lava el formato", p)
        self.assertIn("próximas semanas", p)

    def test_regla14_defines_verdict_threshold(self):
        # D-035: la Regla 14 define el umbral del veredicto (solo lo bloqueante degrada)
        s = self._skill()
        self.assertIn("Regla 14", s)
        self.assertIn("Umbral del veredicto", s)
        self.assertIn("solo lo **bloqueante** degrada", s)
        # y nombra explícitamente lo que NO degrada LISTO
        self.assertIn("Qué NO degrada", s)
        self.assertIn("materia de Spec", s)


if __name__ == "__main__":
    unittest.main()
