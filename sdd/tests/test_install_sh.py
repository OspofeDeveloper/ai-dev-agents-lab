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
import re
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
    "sdd-skill-allow.py", "sdd-amend.py", "sdd-features-index.py", "sdd-analysis-gaps.py",
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

    def test_artifact_templates_do_not_teach_the_user_commands(self):
        # ROADMAP 11.7: las plantillas producen artefactos que LEE EL USUARIO. Un
        # `/wf-x <args>` ahi le ensena a teclear comandos y a pasar argumentos a
        # mano, saltandose la construccion que hace el hilo principal — que es
        # donde viven las validaciones. El ecosistema se conduce hablando.
        # Medido: el prd_analysis.md de un proyecto real traia un bloque entero de
        # comandos porque su output_template lo prescribia.
        # ROADMAP 11.10: la primera version de este backstop buscaba `/wf-` —el
        # ARREGLO— en vez de `wf-` —el DEFECTO—, y por ahi se colaron 19 nombres de
        # workflow sin barra a los artefactos de una corrida real. Ahora busca las
        # dos formas. Excepciones de forma, no de criterio: una linea de procedencia
        # (`Generado por: wf-x`) es ESTADO, y un comentario HTML va dirigido al
        # agente que rellena la plantilla, no al lector del artefacto.
        self.install("all")
        offenders = []
        for tpl in sorted((self.claude / "skills").rglob("*template*.md")):
            # Alcance: fase Spec (la barrida). Design/plan/tasks siguen en cola de
            # 11.10; ampliar este filtro es el criterio de cierre de cada fase.
            if not tpl.relative_to(self.claude / "skills").parts[0].startswith("wf-spec-"):
                continue
            for i, line in enumerate(tpl.read_text(encoding="utf-8").splitlines(), 1):
                if "Generado por:" in line or "Generada por:" in line:
                    continue
                if line.lstrip().startswith("<!--"):
                    continue
                if re.search(r"/wf-[a-z]|wf-[a-z]", line):
                    offenders.append(f"{tpl.relative_to(self.claude)}:{i}: {line.strip()[:90]}")
        self.assertEqual(offenders, [],
                         "plantillas de artefacto que ensenan comandos al usuario:\n"
                         + "\n".join(offenders))

    def test_retired_script_is_removed_on_reinstall(self):
        # ROADMAP 11.8: copiar sin reconciliar deja scripts zombis. El daño no es
        # que se ejecuten (su hook ya no esta registrado) sino que son DESCUBRIBLES:
        # un agente que haga `ls .sdd/scripts/` concluye que ese gate sigue vivo.
        # Medido: sdd-agent-sync.py de 0.82.x sobrevivio a la actualizacion a 0.83.0.
        self.install("all")
        zombie = self.proj / ".sdd" / "scripts" / "sdd-retirado.py"
        write(zombie, "#!/usr/bin/env python3\n# sdd-version: 0.1.0+abc1234\nprint(1)\n")
        r = self.install("all")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(zombie.exists(),
                         "install.sh no retira un script que el ecosistema ya no distribuye")

    def test_reconciliation_does_not_touch_a_script_of_the_team(self):
        # La otra mitad: el criterio de propiedad es el sello `# sdd-version:`.
        # Un script propio del equipo no lo lleva y NO se toca. Conservador por
        # diseno: ante la duda no se borra.
        self.install("all")
        mine = self.proj / ".sdd" / "scripts" / "mi-script-del-equipo.py"
        write(mine, "#!/usr/bin/env python3\nprint('nuestro')\n")
        r = self.install("all")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(mine.exists(),
                        "install.sh borro un script propio del proyecto (sin sello)")
        self.assertIn("nuestro", mine.read_text(encoding="utf-8"))

    def test_reconciliation_keeps_the_distributed_ones(self):
        # Guarda anti-regresion: la reconciliacion no puede llevarse por delante
        # lo que si se distribuye. Dos installs seguidos dejan el set completo.
        self.install("all")
        r = self.install("all")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for s in ENFORCEMENT_SCRIPTS:
            self.assertTrue((self.proj / ".sdd" / "scripts" / s).exists(),
                            f"la reconciliacion se llevo {s}")

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

    def test_gap_conventions_declares_answer_remit(self):
        # D-042: quién escribe las respuestas de los [P-XXX] es una tabla cerrada
        # en kb-gap-conventions (SSoT del sistema de gaps), no una zona a improvisar.
        self.install("all")
        kb = (self.skill_dir("kb-gap-conventions") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("sdd-analysis-gaps.py", kb,
                      "kb-gap-conventions no nombra el mecanismo de aplicación (D-042)")
        self.assertIn("--answer", kb, "falta la vía sancionada para el dictado (D-042)")
        self.assertIn("--check", kb, "falta la detección determinista de gaps abiertos (D-042)")
        for token in ("Read", "Edit", "Write"):
            self.assertIn(token, kb,
                          f"kb-gap-conventions no prohíbe `{token}` del analysis en main (D-042)")
        # El script tiene que estar instalado, o el SKILL apunta a algo que no existe.
        self.assertTrue((self.proj / ".sdd" / "scripts" / "sdd-analysis-gaps.py").exists(),
                        "sdd-analysis-gaps.py no se instala en .sdd/scripts/")

    def test_auditor_skills_do_not_declare_a_tool_their_agent_forbids(self):
        # D-051: `sdd-spec-auditor` tiene `disallowedTools: Write, Edit`. Una skill
        # que lo declara como `agent:` y a la vez pone `Write` en allowed-tools deja
        # un contrato que se contradice, y el modelo lo resuelve como quiera: medido,
        # dos auditores escribieron su informe con `cat >` y un tercero le pasó la
        # escritura al hilo principal.
        self.install("all")
        for name in ("wf-spec-conflict", "wf-spec-readiness", "wf-prd-sync-impact"):
            skill = (self.skill_dir(name) / "SKILL.md").read_text(encoding="utf-8")
            fm = skill.split("---")[1]
            self.assertIn("agent: sdd-spec-auditor", fm, f"{name} cambió de agente")
            self.assertNotIn("Write", fm,
                             f"{name} declara `Write` y su agente lo tiene prohibido (D-051)")
            self.assertIn("cat >", skill,
                          f"{name} no dice por qué vía se escribe el informe (D-051)")

    def test_auditor_agent_states_read_only_is_a_norm_not_a_cage(self):
        # D-051: quitar Write/Edit NO hace read-only a un agente que conserva Bash.
        # El invariante "no modifico lo que audito" tiene que estar escrito, porque
        # ninguna lista de tools lo sostiene.
        self.install("all")
        agent = (self.proj / ".claude" / "agents" / "sdd-spec-auditor.md").read_text(
            encoding="utf-8")
        self.assertIn("Bash", agent, "el agente no reconoce que conserva Bash (D-051)")
        self.assertIn("norma", agent.lower(),
                      "falta la norma que sustituye al candado inexistente (D-051)")

    def test_spec_expert_carries_the_artifact_form_norm(self):
        """D-055: la norma de forma tiene que llegarle a quien ESCRIBE DESDE CERO.

        Una regla de `.claude/rules/` se carga al tocar un path que matchea sus
        globs; un generador toca ese path por primera vez en el `Write` final, con
        el contenido ya compuesto. `kb-spec-expert` la cargan los tres agentes de
        Spec por su `skills:` y entra antes de cualquier tool call — es el unico
        portador fiable. Medido en la pasada 10 de CU-3.a.
        """
        self.install("all")
        kb = (self.skill_dir("kb-spec-expert") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("lo lee una persona", kb,
                      "kb-spec-expert no porta la norma de forma de los artefactos (D-055)")
        self.assertIn("Generado por:", kb,
                      "falta la frontera: la procedencia canonica es estado y se queda")
        # Los tres agentes de Spec tienen que cargarla, o la norma no viaja.
        for agent in ("sdd-spec-writer", "sdd-spec-explorer", "sdd-spec-auditor"):
            body = (self.claude / "agents" / f"{agent}.md").read_text(encoding="utf-8")
            self.assertIn("kb-spec-expert", body,
                          f"{agent} no carga kb-spec-expert: la norma de D-055 no le llega")

    def test_antifabrication_reaches_every_spec_writer(self):
        """D-063: la obligacion de marcar rige cada escritura, no solo la generacion.

        Un invariante mantenido por un workflow no es un invariante del
        artefacto (D-039, que lo aprendio en el PRD). Sobre un spec escriben
        cuatro; `gap-resolve` y `amend` no sabian que la regla existia.
        La SSoT viaja en `kb-gap-conventions`, que entra en la linea 1 del
        contexto de los agentes de Spec por su `skills:` (D-055).
        """
        self.install("all")
        kb = (self.skill_dir("kb-gap-conventions") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("cada escritura", kb,
                      "kb-gap-conventions no porta la norma de D-063")
        for writer in ("wf-spec-fast-track", "wf-spec-delta",
                       "wf-spec-gap-resolve", "wf-spec-amend"):
            self.assertIn(writer, kb,
                          f"la tabla de escritores del spec no nombra a {writer} (D-063)")
        # El agente que ejecuta esas skills tiene que cargar la KB, o no llega.
        writer_agent = (self.claude / "agents" / "sdd-spec-writer.md").read_text(encoding="utf-8")
        self.assertIn("kb-gap-conventions", writer_agent,
                      "sdd-spec-writer no carga kb-gap-conventions: la norma no le llega")
        # gap-resolve completa texto que nadie dicto -> necesita la marca.
        gr = (self.skill_dir("wf-spec-gap-resolve") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Asunciones Aplicadas", gr,
                      "wf-spec-gap-resolve no obliga a anotar lo que completa (D-063)")
        self.assertIn("D-063", gr)
        # amend NO usa marca: su mecanismo es el gate + la confirmacion humana.
        am = (self.skill_dir("wf-spec-amend") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("D-063", am,
                      "wf-spec-amend no declara como sostiene la anti-fabricacion")

    def test_sealing_gates_enumeration_names_all_four(self):
        """D-065: una enumeracion que gobierna conducta no se mantiene sola.

        Regla 10 decia "los tres gates" porque se escribio antes de D-061. Cuando
        el spec gano sello, nadie volvio a esta lista: el spec fue el unico
        artefacto que llegaba a VALIDADO sin que constara nadie. Este backstop
        existe para que la proxima fase que gane un gate no repita el silencio.
        """
        self.install("all")
        kb = (self.skill_dir("kb-traceability-rules") / "SKILL.md").read_text(encoding="utf-8")
        for gate in ("wf-prd-review", "wf-spec-validate", "wf-plan-validate", "wf-qa-verify"):
            self.assertIn(gate, kb,
                          f"Regla 10 no nombra el gate de sellado {gate} (ver D-065)")
        self.assertNotIn("Los tres gates", kb,
                         "Regla 10 vuelve a enumerar tres gates de sellado (ver D-065)")

    def test_spec_amend_holds_its_two_human_gates_from_main(self):
        """D-068: los dos gates de amend SON su razon de existir.

        Clasificar aclaracion-vs-cambio y confirmar el texto final palabra por
        palabra: ninguno es presentable desde un fork. Mientras lo fue, la parte
        que da valor a la skill no era ejecutable.
        """
        self.install("all")
        body = (self.skill_dir("wf-spec-amend") / "SKILL.md").read_text(encoding="utf-8")
        fm = body.split("---")[1]
        self.assertNotIn("context: fork", fm,
                         "wf-spec-amend vuelve a ser fork: sus gates no serian presentables")
        self.assertIn("AskUserQuestion", fm,
                      "wf-spec-amend no declara la tool con la que sostiene sus gates")
        self.assertIn("run_in_background: false", body,
                      "wf-spec-amend delega sin pedir sincronia (D-043)")
        self.assertIn("sdd-amend.py", body,
                      "la ref E-00X debe seguir viniendo del script (autor != marcador)")

    def test_retired_agent_is_not_installed(self):
        """D-069: sdd-spec-planner se retiro; su trabajo lo hace el carril eager.

        Backstop contra la reaparicion por copia de una plantilla vieja.
        """
        self.install("all")
        self.assertFalse((self.claude / "agents" / "sdd-spec-planner.md").exists(),
                         "sdd-spec-planner vuelve a instalarse (retirado en D-069)")

    def test_rootmap_does_not_duplicate_argument_hints(self):
        """D-069: la columna de argumentos duplicaba el frontmatter y derivaba.

        install.sh siembra este CLAUDE.md como raiz del proyecto cuando se
        instalan >=2 fases, asi que sus argumentos stale llegaban al contexto
        del orquestador. Precedente: D-023.
        """
        self.install("all")
        md = (self.claude / "CLAUDE.md").read_text(encoding="utf-8")
        hdr = "| Intención del usuario | Skill |"
        self.assertIn(hdr, md, "el rootmap recupera la columna de argumentos (ver D-069)")
        # Solo la TABLA: la prosa que explica el pipeline sí puede nombrar un flag
        # al describir un gate; lo que no debe volver es la columna que duplicaba
        # el `argument-hint` de cada skill.
        tabla = md[md.index(hdr):md.index("\n## ", md.index(hdr))]
        self.assertNotIn("--allow", tabla,
                         "el rootmap vuelve a listar flags: eso lo dice el argument-hint")
        self.assertNotIn("<prd.md>", tabla,
                         "el rootmap vuelve a listar argumentos posicionales")

    def test_spec_validate_holds_its_gate_from_the_main_thread(self):
        """D-065: el gate de sellado del spec captura quien aprueba, luego es main.

        Era el unico de los cuatro que corria en fork, y por eso el unico que no
        registraba a nadie. Estampa por script, no desde main (D-060).
        """
        self.install("all")
        head = (self.skill_dir("wf-spec-validate") / "SKILL.md").read_text(encoding="utf-8")
        fm = head.split("---")[1]
        self.assertNotIn("context: fork", fm,
                         "wf-spec-validate vuelve a ser fork: no podria capturar la identidad")
        self.assertIn("AskUserQuestion", fm,
                      "wf-spec-validate no declara la tool con la que sostiene su gate")
        self.assertIn("--approved-by", head,
                      "wf-spec-validate no estampa la atribucion por script (D-065)")
        self.assertIn("run_in_background: false", head,
                      "wf-spec-validate delega la auditoria sin pedir sincronia (D-043)")

    def test_spec_header_contract_is_declared_where_it_is_written(self):
        """D-066: `Feature ID` y `Origen de alcance` los lee otro programa.

        La plantilla de caracterizacion no los declaraba y `parse_spec` devuelve
        None sin `Feature ID`: el spec se caia del indice ENTERO, en silencio.
        """
        self.install("all")
        kb = (self.skill_dir("kb-spec-characterization") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Feature ID", kb,
                      "la cabecera de caracterizacion no declara `Feature ID` (D-066)")
        self.assertIn("Origen de alcance", kb,
                      "la cabecera de caracterizacion no declara `Origen de alcance` (D-066)")

    def test_prd_create_carries_both_halves_of_the_norm(self):
        """D-066: era la unica workflow-en-main sin la mitad de escritura."""
        self.install("all")
        skill = (self.skill_dir("wf-prd-create") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("No leas el fichero en el hilo principal", skill)
        self.assertIn("tampoco lo escribes tú", skill,
                      "wf-prd-create pierde la mitad de escritura de la norma (D-066)")

    def test_spec_overwrite_gate_is_risk_weighted(self):
        """D-062: regenerar un spec se pondera por su estado, como el PRD (D-024).

        Tres ramas, la linea objetiva es `Estado: VALIDADO` (D-061). El defecto
        que se arregla NO era el "seguro?" plano: features-first excluia en
        silencio cualquier spec preexistente, convirtiendo un "regenera F-003"
        en un no-op reportado como exito ("ya generada").
        """
        self.install("all")
        ff = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("SELLADO", ff,
                      "features-first pierde la rama de spec sellado (ver D-062)")
        self.assertIn("DRAFT", ff,
                      "features-first pierde la rama de draft (ver D-062)")
        self.assertIn("VALIDADO", ff,
                      "features-first pierde la deteccion de sello por `Estado:` (ver D-061/D-062)")
        self.assertNotIn("no relances (preservar trabajo previo)", ff,
                         "features-first vuelve a saltarse en silencio los specs preexistentes (D-062)")

    def test_spec_generators_stop_instead_of_faking_a_gate(self):
        """D-062: un gate escrito en un fork no es un gate — para y reporta.

        `wf-spec-fast-track` y `wf-spec-from-code` son `context: fork` sin
        `AskUserQuestion`: su instruccion anterior ("pregunta al usuario si desea
        regenerarlo") no era ejecutable, misma clase de defecto que D-045. El
        override lo arma el usuario en el gate de quien si puede preguntar (D-026).
        """
        self.install("all")
        ft = (self.skill_dir("wf-spec-fast-track") / "SKILL.md").read_text(encoding="utf-8")
        fc = (self.skill_dir("wf-spec-from-code") / "SKILL.md").read_text(encoding="utf-8")
        for name, body in (("wf-spec-fast-track", ft), ("wf-spec-from-code", fc)):
            self.assertIn("STOP_SPEC_SELLADO", body,
                          f"{name} no para ante un spec sellado (ver D-062)")
            self.assertIn("--allow-overwrite-sealed-spec", body,
                          f"{name} pierde el override nominal del gate (ver D-026/D-062)")
            head = body.split("---")[1] if body.startswith("---") else body[:800]
            self.assertIn("context: fork", head,
                          f"{name} dejo de ser fork: revisa si el gate debe volver a el (D-062)")
            self.assertNotIn("AskUserQuestion", head,
                             f"{name} declara AskUserQuestion en frontmatter siendo fork (ver D-045)")
        # Las instrucciones inejecutables originales, completas, no vuelven.
        self.assertNotIn(
            "Si existe \u2192 pregunta al usuario si desea regenerarlo", ft,
            "wf-spec-fast-track recupera el gate inejecutable (ver D-062)")
        self.assertNotIn(
            "Si ya existe \u2192 pregunta antes de regenerar", fc,
            "wf-spec-from-code recupera el gate inejecutable (ver D-062)")
        # Y el override tiene que ser invocable: declarado en el argument-hint.
        self.assertIn("[--allow-overwrite-sealed-spec]", ft,
                      "wf-spec-fast-track no declara el flag en su argument-hint")

    def test_spec_generators_stop_on_a_retired_feature(self):
        """D-080: `Estado:` tiene TRES valores y el sondeo los partia en dos.

        D-078 cerro la baja para los flujos que MODIFICAN un spec, con un gate
        determinista que resuelve el spec desde los argumentos. Los que lo
        REGENERAN no reciben el spec como argumento —reciben el PRD o un path de
        codigo—, asi que el invariante vive en el cuerpo de la skill. Un
        `RETIRADO` leido como "no es VALIDADO" cae en la rama del borrador: la
        que se reescribe sin preguntar, resucitando la feature sin CR ni gate.

        Y este STOP_* no lo cierra ningun flag: recuperar la feature es una
        decision de producto, no un permiso de escritura.
        """
        self.install("all")
        ft = (self.skill_dir("wf-spec-fast-track") / "SKILL.md").read_text(encoding="utf-8")
        fc = (self.skill_dir("wf-spec-from-code") / "SKILL.md").read_text(encoding="utf-8")
        ff = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        for name, body in (("wf-spec-fast-track", ft), ("wf-spec-from-code", fc)):
            self.assertIn("STOP_SPEC_RETIRADO", body,
                          f"{name} no para ante una feature dada de baja (ver D-080)")
            self.assertIn("Ningún flag lo cierra", body,
                          f"{name} deja entender que un override reabre una baja (ver D-078/D-080)")
        # El orquestador no puede parar: clasifica y excluye, nombrandolas.
        self.assertIn("RETIRADA", ff,
                      "features-first no clasifica las features dadas de baja (ver D-080)")
        # Los tres leen el campo entero, no solo VALIDADO.
        for name, body in (("wf-spec-fast-track", ft), ("wf-spec-from-code", fc),
                           ("wf-spec-features-first", ff)):
            self.assertIn("BORRADOR|VALIDADO|RETIRADO", body,
                          f"{name} vuelve al sondeo binario del `Estado:` (ver D-080)")

    def test_gap_id_ranges_are_dealt_by_the_orchestrator(self):
        """D-056: en un fan-out los IDs los reparte quien lanza, no el escritor.

        Cuatro escritores en paralelo piden todos el mismo "siguiente ID libre":
        sus specs aun no existen en disco. Medido en la pasada 11 de CU-3.a, dos
        specs hermanos reclamaron el mismo [P-009] para gaps distintos.
        """
        self.install("all")
        ff = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        ft = (self.skill_dir("wf-spec-fast-track") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("--gap-id-start", ff,
                      "features-first no reparte rangos de ID en el fan-out (D-056)")
        self.assertIn("sdd-next-id.py", ff,
                      "features-first no pide el primer ID libre del linaje (D-056)")
        self.assertIn("--gap-id-start", ft,
                      "fast-track no acepta el rango que le asigna el orquestador (D-056)")
        # El reparto tiene que ocurrir ANTES de emitir las llamadas Agent.
        self.assertLess(ff.index("--gap-id-start"), ff.index("CRÍTICO: emite TODOS"),
                        "el reparto de IDs va despues del fan-out: llega tarde (D-056)")

    def test_incomplete_marker_names_the_gap_home(self):
        """D-056: el marcador [INCOMPLETO] manda al fichero donde vive el gap.

        La plantilla hardcodeaba `_analysis.md`; un spec salio mandando al usuario
        a un fichero donde su [P-009] no existia — el callejon de D-054 por la via
        del texto.
        """
        self.install("all")
        kb = (self.skill_dir("kb-gap-conventions") / "SKILL.md").read_text(encoding="utf-8")
        marker = kb[kb.index("## Marcador de HU incompleta"):]
        # Acotado al bloque de plantilla: la prosa de alrededor puede citar la
        # forma vieja como ejemplo de lo que NO se escribe, y eso es legitimo.
        tpl = marker[marker.index("```markdown"):]
        tpl = tpl[:tpl.index("```", 3)]
        self.assertNotIn("_analysis.md", tpl,
                         "la plantilla del marcador sigue hardcodeando el analysis (D-056)")
        self.assertIn("Items Pendientes", marker,
                      "la plantilla no contempla el gap que vive en el propio spec (D-056)")
        # Y la seccion no dicta comandos al usuario (ROADMAP 11.10).
        self.assertNotIn("/wf-", marker,
                         "la seccion del marcador enseña un slash-command (11.10)")

    def test_informative_gap_review_is_reachable(self):
        """D-057: el paso de informativos no puede ser codigo muerto.

        Al anadirlo, el final del paso anterior seguia diciendo "sigue por el
        punto 8 o 9", que lo salta entero. Un paso nuevo vale lo que valgan los
        saltos que lo alcanzan: se verifica que 6b y la rama sin criticos
        enrutan a 6c, y que 6c enruta a 8/9.
        """
        self.install("all")
        ff = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("6c.", ff, "no existe el paso de repaso de informativos (D-057)")
        self.assertIn("sigue por el punto 6c", ff,
                      "el flujo de criticos salta el paso de informativos (D-057)")
        self.assertIn("pasa igualmente por el punto 6c", ff,
                      "la rama sin criticos salta el paso de informativos (D-057)")
        i6c = ff.index("6c.")
        self.assertIn("punto 8", ff[i6c:], "6c no enruta a la evaluacion de gobernanza")
        # El script tiene que dar la asuncion, o main la redactaria el.
        gaps = (self.proj / ".sdd" / "scripts" / "sdd-analysis-gaps.py").read_text(encoding="utf-8")
        self.assertIn('"asuncion"', gaps,
                      "sdd-analysis-gaps.py no emite la asuncion por defecto (D-057)")

    def test_pending_items_template_covers_every_case(self):
        """D-058: la plantilla no puede dejar casos sin cubrir.

        Solo traia la cabecera del caso CRITICO. Dos escritores se encontraron
        con "solo informativos" y improvisaron; uno de ellos cambio tambien la
        forma del bloque y el script dejo de ver sus gaps.
        """
        self.install("all")
        tpl = (self.skill_dir("wf-spec-fast-track") / "references"
               / "spec_header_templates.md").read_text(encoding="utf-8")
        sec = tpl[tpl.index("## Sección opcional: Items Pendientes"):]
        sec = sec[:sec.index("## Sección opcional: Asunciones Aplicadas")]
        self.assertIn("informativos", sec.lower(),
                      "la plantilla no cubre el caso solo-informativos (D-058)")
        self.assertIn("### [P-002][INFORMATIVO]", sec,
                      "la plantilla no da el bloque de un informativo (D-058)")
        self.assertIn("Asunción por defecto", sec,
                      "el bloque informativo no lleva su asuncion (D-057)")
        self.assertIn("CONTRATO", sec.upper(),
                      "la plantilla no dice que la forma del bloque la parsea un script (D-058)")
        kb = (self.skill_dir("kb-gap-conventions") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("contrato, no estilo", kb,
                      "la SSoT no declara la forma del bloque como contrato (D-058)")

    def test_pending_items_template_answers_in_place(self):
        """D-057: la plantilla de Items Pendientes no manda al analysis.

        Tercera aparicion del mismo defecto y la peor: es la plantilla de la
        seccion que existe PARA alojar los gaps locales del spec, y decia
        "responde los gaps en el _analysis.md". Se contradecia a si misma.
        """
        self.install("all")
        tpl = (self.skill_dir("wf-spec-fast-track") / "references"
               / "spec_header_templates.md").read_text(encoding="utf-8")
        sec = tpl[tpl.index("## Sección opcional: Items Pendientes"):]
        sec = sec[:sec.index("## Sección opcional: Asunciones Aplicadas")]
        self.assertNotIn("responde los gaps en el `_analysis.md`", sec,
                         "la plantilla de Items Pendientes manda al analysis (D-057)")
        self.assertIn("en esta misma sección", sec,
                      "la plantilla no dice donde se responde el gap local (D-057)")
        self.assertIn("no\nse reproduce", sec.replace("**", ""),
                      "la plantilla no prohibe reproducir el gap heredado (D-057)")

    def test_eager_rule_forbids_the_orchestrator_writing_artifacts(self):
        """D-060: la norma tiene que estar donde main SIEMPRE la lleva.

        Estaba citada en dos sitios como [[D-031]] y D-031 no dice eso: trata
        solo de la lectura cualitativa. La regla eager no la contenia, y ese
        hueco es lo que dejo sitio a D-059.
        """
        self.install("all")
        rule = (self.claude / "rules" / "sdd-orchestration.md").read_text(encoding="utf-8")
        self.assertIn("tampoco redacta artefactos", rule,
                      "la regla eager no prohibe que main escriba artefactos (D-060)")
        self.assertIn("generador determinista", rule,
                      "falta la frontera: invocar un generador si es suyo (D-060)")
        # La regla es eager: sin frontmatter `paths:`, o main no la lleva siempre.
        self.assertFalse(rule.lstrip().startswith("---\npaths:"),
                         "sdd-orchestration.md dejo de ser eager: main no la cargaria")

    def test_orchestrator_does_not_write_the_conflict_report(self):
        """D-059: el informe de conflictos lo escribe cada auditor, no el orquestador.

        El Paso 7 terminaba con "Escribe `_conflict_report.md` si hay conflictos"
        en un parrafo dirigido a main: un imperativo sin sujeto lo ejecuta quien
        lee. Medido en la pasada 13 — main escribio un consolidado y al transcribir
        cuatro informes ajenos adjudico un conflicto al auditor equivocado.
        """
        self.install("all")
        ff = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        paso7 = ff[ff.index("## Paso 7"):ff.index("## Paso 8")]
        self.assertNotIn("Escribe `_conflict_report.md`", paso7,
                         "el Paso 7 vuelve a pedirle a main que escriba el informe (D-059)")
        self.assertIn("lo escribe cada auditor", paso7,
                      "el Paso 7 no dice quien escribe el informe (D-059)")
        self.assertIn("no consolides", paso7.lower(),
                      "el Paso 7 no prohibe consolidar los informes (D-059)")

    def test_analyze_rescues_answers_before_overwriting(self):
        # D-051: regenerar el analysis lo sobrescribe. Las respuestas son decisiones
        # de negocio de una persona, no material regenerable: el export tiene que
        # correr ANTES de escribir, o no hay nada que devolver.
        self.install("all")
        skill = (self.skill_dir("wf-spec-analyze") / "SKILL.md").read_text(encoding="utf-8")
        exp = skill.find("--export-answers")
        imp = skill.find("--import-answers")
        self.assertNotEqual(exp, -1, "wf-spec-analyze no rescata las respuestas (D-051)")
        self.assertNotEqual(imp, -1, "wf-spec-analyze no las devuelve (D-051)")
        self.assertLess(exp, imp, "el export tiene que ir antes del import (D-051)")
        self.assertIn("no es reproducible", skill,
                      "falta por qué el emparejamiento no puede ser solo por ID (D-051)")

        # 11.10: la prosa del gap la lee una persona. Los IDs son contrato y se
        # quedan (`CA-\d{3,4}`, `HU-\d+` los parsean seal/features-index); las
        # siglas sueltas y el vocabulario de formato van en claro. Sin esto, el
        # que presenta el gap acaba traduciendo — y su contrato es verbatim.
        self.assertIn("el ID es contrato", skill,
                      "wf-spec-analyze no declara la frontera ID/jerga en la prosa del gap")
        self.assertIn("Afecta", skill,
                      "falta el borde: `Afecta` lista IDs y no se desjergoniza")

    def test_features_first_checks_gaps_before_deciding(self):
        # D-042 + lección de D-037: el conteo de [CRÍTICO] abiertos gobierna dos ramas
        # duras (detenerse / --allow-open-critical-gaps). Si el script corre DESPUÉS de
        # decidir, la decisión sigue siendo la lectura del fork y el check es decorativo.
        self.install("all")
        skill = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        # Acotar al Paso 2.5: `--allow-open-critical-gaps` tambien aparece en el
        # argument-hint del frontmatter, que no es la rama que gobierna.
        start = skill.find("## Paso 2.5")
        self.assertNotEqual(start, -1, "falta el Paso 2.5 (gate de gaps)")
        end = skill.find("## Paso 3", start)
        gate = skill[start:end if end != -1 else len(skill)]
        check_at = gate.find("sdd-analysis-gaps.py")
        branch_at = gate.find("--allow-open-critical-gaps")
        self.assertNotEqual(check_at, -1, "wf-spec-features-first no consulta el script (D-042)")
        self.assertNotEqual(branch_at, -1, "falta la rama --allow-open-critical-gaps")
        self.assertLess(check_at, branch_at,
                        "el --check debe correr ANTES de la rama que gobierna (D-042): "
                        "si no, la decisión vuelve a ser la lectura del informe")
        self.assertIn("VACUOUS", gate,
                      "no advierte del veredicto VACUOUS del check (D-042)")

    def test_installed_agents_declare_no_memory(self):
        # D-041: ningun agente instalado declara `memory:`. El estado del proyecto
        # vive en sus artefactos; la memoria de agente sobrevive fuera de ellos y
        # ningun gate, script ni check la ve ni la invalida.
        self.install("all")
        agents = sorted((self.claude / "agents").glob("*.md"))
        self.assertTrue(agents, "no se instalo ningun agente")
        for agent in agents:
            fm = agent.read_text(encoding="utf-8").split("---")[1]
            for line in fm.splitlines():
                self.assertFalse(line.startswith("memory:"),
                                 f"{agent.name} declara `{line.strip()}` (ver D-041)")

    def test_installed_wf_delegate_synchronously(self):
        # D-043: toda wf- instalada que prescriba delegar por la tool `Agent` pasa
        # `run_in_background: false`. Los subagentes corren en background por
        # defecto (Claude Code >= v2.1.198): sin el flag el orquestador no recibe
        # el resultado y acaba sondeando el disco (busy-wait medido en CU-3.a).
        self.install("all")
        offenders = []
        for skill in sorted(self.claude.glob("skills/wf-*/SKILL.md")):
            body = skill.read_text(encoding="utf-8")
            delegates = ("Agent(" in body or "tool `Agent`" in body
                         or "`Agent` tool" in body)
            if delegates and "run_in_background: false" not in body:
                offenders.append(skill.parent.name)
        self.assertEqual(offenders, [],
                         f"delegan por `Agent` sin `run_in_background: false` (D-043): "
                         f"{offenders}")

    def test_features_first_delegates_by_agent_not_bare_slash(self):
        # D-043: los cinco puntos de delegacion de features-first usan el MISMO
        # mecanismo, nombrado. Dejar "invoca /wf-spec-analyze" al lado de un
        # Agent(...) explicito es el hueco que el fork rellenó con `Skill` y un
        # busy-wait de `Monitor` + `ls`.
        self.install("all")
        skill = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        for sub, agent in (("wf-spec-analyze", "sdd-spec-explorer"),
                           ("wf-spec-discover", "sdd-spec-explorer"),
                           ("wf-spec-fast-track", "sdd-spec-writer"),
                           ("wf-spec-conflict", "sdd-spec-auditor"),
                           ("wf-spec-readiness", "sdd-spec-auditor")):
            at = skill.find(sub)
            self.assertNotEqual(at, -1, f"features-first ya no delega en {sub}")
            # El subagent_type correcto aparece en el entorno del punto de delegacion.
            near = skill[max(0, at - 700):at + 700]
            self.assertIn(agent, near,
                          f"la delegacion de {sub} no nombra `subagent_type: {agent}` (D-043)")
        for bare in ("invoca `/wf-spec-analyze", "Invoca `/wf-spec-discover",
                     "Invoca `/wf-spec-readiness", "invoca `/wf-spec-conflict"):
            self.assertNotIn(bare, skill,
                             f"queda una delegacion sin tool nombrada: «{bare}» (D-043)")

    def test_features_first_delegates_execute_not_redispatch(self):
        # D-044: el prompt del delegado le pide ejecutar la skill EL MISMO. Decirle
        # "Ejecuta el skill /wf-X" le hace usar el Skill tool, que forkea otro
        # subagente (un clon suyo) y reintroduce la asincronia un nivel mas abajo.
        self.install("all")
        skill = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("Ejecuta el skill /wf-", skill,
                         "el prompt del delegado le hace re-despachar con `Skill` (D-044)")
        for sub in ("wf-spec-analyze", "wf-spec-discover", "wf-spec-fast-track",
                    "wf-spec-conflict", "wf-spec-readiness"):
            self.assertIn(f".claude/skills/{sub}/SKILL.md", skill,
                          f"la delegacion de {sub} no le dice qué SKILL.md leer (D-044)")
        self.assertGreaterEqual(skill.count("NO uses el `Skill` tool")
                                + skill.count("NO uses el Skill tool"), 5,
                                "faltan prohibiciones del `Skill` tool en los 5 prompts (D-044)")

    def test_features_first_orchestrates_from_main_thread(self):
        # D-045: features-first delega Y sostiene cuatro gates. Un fork no puede
        # preguntar (AskUserQuestion no existe en un subagente) ni conseguir el
        # primer plano para sus delegados, asi que acababa relanzandose entero
        # desde main y deduciendo del disco resultados que no habia recibido.
        self.install("all")
        text = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        fm = text.split("---", 2)[1]
        self.assertNotIn("context: fork", fm,
                         "features-first orquesta: no puede ser `context: fork` (D-045)")
        self.assertIn("AskUserQuestion", fm,
                      "features-first sostiene sus gates: necesita `AskUserQuestion` (D-045)")
        for tool in ("Read", "Write"):
            self.assertNotIn(tool, fm.split("allowed-tools:")[1].split("\n")[0],
                             f"main no lee ni escribe artefactos: fuera `{tool}` "
                             f"de allowed-tools (D-030/D-045)")

    def test_features_first_gates_do_not_relaunch(self):
        # D-045: los gates se presentan en el momento y el flujo continua en el
        # mismo turno. "Vuelve a ejecutar añadiendo --allow-*" repetia los pasos
        # ya hechos (parseo, readiness, check de gaps) y perdia el contexto.
        self.install("all")
        skill = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        for relaunch in ("re-ejecuta añadiendo", "re-ejecutar añadiendo",
                         "vuelve a ejecutar `/wf-spec-features-first"):
            self.assertNotIn(relaunch, skill,
                             f"queda el patron de relanzado: «{relaunch}» (D-045)")
        self.assertGreaterEqual(skill.count("presenta el gate"), 3,
                                "los gates de features-first ya no se presentan (D-045)")

    def test_features_first_defines_what_waiting_means(self):
        # D-045: "espera el resultado" sin criterio no es verificable — el fork
        # podia creer honestamente que habia esperado porque el fichero estaba.
        # D-047: el criterio es QUIEN TRAE el informe, no en que turno llega, y
        # nombra las DOS vias legitimas. Escrito con una sola, la conducta
        # correcta lo incumplia 10 de 10 (CU-3.a pasada 4).
        self.install("all")
        skill = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Qué es haber esperado", skill,
                      "falta el criterio autocomprobable de espera (D-045)")
        self.assertIn("tool_result", skill,
                      "el criterio de espera no nombra la via (a) (D-047)")
        self.assertIn("notificación de fin", skill,
                      "el criterio de espera no nombra la via (b) (D-047)")
        self.assertIn("no reconstruyas", skill,
                      "falta la salida sancionada: parar en vez de reconstruir (D-045)")
        # D-045: el cuerpo viaja al contexto del agente; nombrar la tool prohibida
        # se la enseña. Medido: los dos forks hicieron `ToolSearch select:Monitor`.
        self.assertNotIn("Monitor", skill,
                         "la prohibicion nombra la tool y se la enseña al agente (D-045)")

    def test_features_first_fanout_barrier_is_explained(self):
        # D-047: el fan-out del Paso 5 es una BARRERA — el Paso 6 lee del disco lo
        # que escribieron todos. Las dos piezas se sostienen juntas: N llamadas en
        # UN mensaje + el flag. Separadas, una tapa la rotura de la otra: medido en
        # la pasada 4, tres writers en tres mensajes, inocuo solo porque el flag no
        # viajaba. El dia que el flag funcione, eso serializa el fan-out.
        self.install("all")
        skill = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("en un único mensaje", skill,
                      "falta el requisito de fan-out en un solo mensaje (D-047)")
        self.assertIn("barrera", skill,
                      "el fan-out no explica por que el flag es obligatorio aqui (D-047)")
        self.assertIn("serializa", skill,
                      "no dice que mensajes separados serializan el fan-out (D-047)")

    def test_features_first_checks_the_index_covers_the_universe(self):
        # D-046: con artifacts.prd != artifacts.spec el discovery vive con el PRD.
        # Medido: el indice registro 3 features de 9 y las 6 PENDIENTE_GENERACIÓN
        # desaparecieron, mientras main narraba las 9 correctamente.
        self.install("all")
        skill = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("--discovery", skill,
                      "el Paso 6 no ofrece la salida para el discovery externo (D-046)")
        self.assertIn("PENDIENTE_GENERACIÓN", skill)
        self.assertIn("a mano", skill,
                      "no prohibe parchear a mano un artefacto generado (D-046)")

    def test_fork_mode_is_off_in_settings(self):
        # D-050: con fork mode activo —el default interactivo— el harness lanza
        # los subagentes en background y NO evalua peticiones de primer plano:
        # ni `run_in_background: false` de la llamada ni `background:` del
        # frontmatter del agente. Medido: 0/10 con el flag prescrito, y un
        # `background: false` en el agente que tampoco forzo nada. Apagarlo es lo
        # unico que devuelve el control, y es declarativo — no depende de que el
        # modelo teclee nada.
        self.install("all")
        settings = json.loads(
            (self.claude / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(settings.get("env", {}).get("CLAUDE_CODE_FORK_SUBAGENT"), "0",
                         "el proyecto no apaga fork mode (D-050)")

    def test_agent_sync_hook_is_gone(self):
        # D-050 retira el gate. Backstop anti-resurreccion: ni el script ni el
        # matcher deben reaparecer.
        self.install("all")
        self.assertFalse((self.proj / ".sdd" / "scripts" / "sdd-agent-sync.py").exists(),
                         "el hook retirado se sigue instalando (D-050)")
        settings = json.loads(
            (self.claude / "settings.json").read_text(encoding="utf-8"))
        matchers = {e["matcher"] for e in settings["hooks"]["PreToolUse"]}
        self.assertNotIn("Agent", matchers)
        self.assertIn("Skill", matchers, "se perdio el gate de skills")

    def test_features_first_draws_the_bash_boundary(self):
        # D-048 (cierra O-8): "no hagas Read del artefacto" se cumplia al pie de
        # la letra con `cat`. La frontera va sobre el EFECTO, no sobre la tool.
        self.install("all")
        skill = (self.skill_dir("wf-spec-features-first") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("_features.md", skill)
        for criterio in ("determinista", "delimitada", "metadatos"):
            self.assertIn(criterio, skill,
                          f"la frontera de extraccion no nombra «{criterio}» (D-048)")

    def test_readiness_reads_conflict_reports_from_both_places(self):
        # D-046: el fan-out del Paso 7 escribe un informe JUNTO A CADA SPEC; el
        # readiness los buscaba solo en la raiz y se declaraba "sin analisis de
        # conflictos" con N informes en disco — advertencia no bloqueante, o sea
        # fallo silencioso.
        self.install("all")
        skill = (self.skill_dir("wf-spec-readiness") / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("*/spec/*_conflict_report.md", skill,
                      "el readiness no busca los informes por feature (D-046)")
        # D-047: un SIN_CONFLICTOS no refuta un hallazgo; nunca cerrar por mayoria.
        self.assertIn("no refuta un hallazgo", skill,
                      "falta la regla de arbitraje entre auditores (D-047)")

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
        # D-075: el modo sin gate se retira. Su unico consumidor era la cascada,
        # que era un fork; desde que corre en main, el gate se presenta de verdad.
        # Un modo que nadie alcanza no es una capacidad, es una promesa.
        self.assertNotIn("--defer-decisions", head,
                         "el flag se retiro del contrato de entrada al salir la cascada del fork (D-075)")
        self.assertIn("No hay modo sin gate", skill,
                      "la retirada del modo sin gate tiene que quedar escrita, no solo borrada (D-075)")
        self.assertIn("el Paso 5 no tiene excepciones", skill,
                      "sin el flag, el gate tiene que quedar declarado sin escapatoria (D-075)")

    def test_prd_change_cascade_runs_in_main_and_delegates(self):
        # D-075: la cascada sale del fork. Era la unica skill del ecosistema que
        # declaraba `Skill` en allowed-tools, encadenaba seis workflows desde un
        # subagente y declaraba cuatro "checkpoints humanos" que ningun fork puede
        # presentar. D-040 ya lo dejo escrito como candidato: "sacar tambien la
        # cascada del fork heredaria el gate de verdad".
        self.install("all")
        skill = (self.skill_dir("wf-prd-change-cascade") / "SKILL.md").read_text(encoding="utf-8")
        head = skill.split("---")[1]
        self.assertNotIn("context: fork", head,
                         "la cascada no puede seguir siendo un fork: sus gates no se presentan (D-075)")
        self.assertIn("AskUserQuestion", head,
                      "la cascada necesita AskUserQuestion para sostener sus gates (D-075)")
        self.assertIn("Agent", head,
                      "la cascada delega los workers por la tool Agent (D-043/D-075)")
        # El flag puede nombrarse al explicar por que ya no se usa; lo que no puede
        # es seguir viajando en la invocacion.
        self.assertNotIn("--new-reqs <cambio.md> --defer-decisions", skill,
                         "sin fork no hay nada que aplazar: el gate de wf-prd-change se presenta (D-075)")
        # El informe consolidado desaparece: cada artefacto tiene su autor (D-060).
        self.assertNotIn("Escribe `<basename>_cascade_report.md", skill,
                         "el orquestador no redacta el informe de sus delegados (D-060/D-075)")
        # Y los specs resincronizados salen en BORRADOR: callarlo deja al usuario
        # con un readiness que los bloquea sin explicar por que (D-061).
        self.assertIn("BORRADOR", skill,
                      "la cascada debe avisar de que el apply reabre la validacion (D-061/D-075)")

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

    def test_routing_rule_carries_the_spec_fork_gate_paragraph(self):
        # D-075 (residuo): Design tenia escrito desde D-072 que sus gates no se dictan
        # desde un fork, y Spec no — pese a emitir siete veredictos STOP_* desde forks.
        # La cadena "STOP_" no aparecia en NINGUNA regla eager: la convencion que usan
        # 10 skills de 5 fases no estaba nombrada en nada que el hilo principal cargue.
        self.install("all")
        routing = (self.claude / "rules" / "sdd-routing.md").read_text(encoding="utf-8")
        spec_section = routing.split("## Fase Spec")[1].split("## Fase Design")[0]
        self.assertIn("STOP_", spec_section,
                      "la seccion Spec debe nombrar el veredicto STOP_* (D-064/D-072)")
        self.assertIn("presentarlo es cosa tuya", spec_section,
                      "tiene que decir QUIEN presenta el bloqueo, no solo que el worker para")
        # Y los dos STOP_* que ningun --allow-* cierra: esperan confirmacion, no permiso.
        self.assertIn("no se cierran con ningún flag", spec_section)

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

    def test_spec_rule_covers_analysis_and_discovery(self):
        """11.10 causa A: `_analysis.md` y `_discovery.md` son artefactos de Spec.

        Viven en el directorio del PRD, asi que con solo el glob de prd quien los
        escribe (sdd-spec-explorer) cargaba la guia de PRD y NO la de Spec — que es
        donde vive la norma de no enseñar comandos en los artefactos. Medido en la
        pasada 9 de CU-3.a: 3 de 3 ejecuciones sin la regla de Spec cargada.
        """
        r = self.install("spec")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rule = self._spec_rule()
        for g in ('"**/*_analysis.md"', '"**/*_discovery.md"'):
            self.assertIn(g, rule,
                          f"la regla de Spec no cubre {g}: quien escribe ese artefacto "
                          f"no carga la guia de fase (11.10 causa A)")

    def test_noncanonical_dir_keeps_artifact_globs(self):
        """El override de directorio no debe arrastrarse los globs por nombre."""
        self.install("spec", "--artifacts-spec=specs")
        rule = self._spec_rule()
        self.assertIn('"**/*_analysis.md"', rule)
        self.assertIn('"**/*_discovery.md"', rule)

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


class KbSpecExpertContentTest(unittest.TestCase):
    """Backstop de contenido del kb-spec-expert (D-076): el umbral del veredicto de
    la fase Spec, espejo del que D-035 fijo para el PRD. Como alli, parte del insumo
    es cualitativo y no hay script que lo mecanice: se fijan las cadenas clave."""

    KB = SDD_ROOT / "pipeline" / "spec" / "skills" / "kb-spec-expert"
    WF = SDD_ROOT / "pipeline" / "spec" / "skills" / "wf-spec-validate"

    def _skill(self):
        return (self.KB / "SKILL.md").read_text(encoding="utf-8")

    def test_threshold_is_defined_and_closed(self):
        # D-076: "hallazgo bloqueante" gobierna el sello, asi que no puede quedar a
        # juicio de cada pasada. Los tres tipos que degradan estan enumerados.
        s = self._skill()
        self.assertIn("El umbral del veredicto", s)
        self.assertIn("Es bloqueante, y solo esto", s)

    def test_threshold_names_what_does_not_degrade(self):
        # La mitad que de verdad falta cuando el umbral no esta escrito: lo que se
        # reporta SIN bajar el veredicto. Sin esta lista, el juicio se va a estricto.
        s = self._skill()
        self.assertIn("No degrada el veredicto", s)
        self.assertIn("materia de Plan", s)

    def test_threshold_defers_the_mechanical_half_to_the_script(self):
        # Ortogonalidad con sdd-seal.py --check: incompletos, criticos, inferidos y
        # asunciones sin rastro los dictamina el script, no la lectura del auditor.
        s = self._skill()
        self.assertIn("sdd-seal.py spec --check", s)
        self.assertIn("necesario y no suficiente", s)

    def test_validate_restates_the_threshold(self):
        # Restatement en el workflow que sella: el prompt del auditor lleva el umbral
        # y el paso del sello remite a la SSoT en vez de re-definirlo.
        s = (self.WF / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("no lo decides aquí", s)
        self.assertIn("kb-spec-expert", s)
        tpl = (self.WF / "references" / "output_template.md").read_text(encoding="utf-8")
        self.assertIn("Hallazgos BLOQUEANTES", tpl)
        self.assertIn("Notas NO bloqueantes", tpl)


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
