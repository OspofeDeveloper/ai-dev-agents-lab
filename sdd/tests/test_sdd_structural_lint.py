"""Black-box tests para scripts/sdd-structural-lint.py.

Usa el flag --root <path> (anadido en ROADMAP 11.3 para testabilidad: default =
comportamiento de siempre, escanear el arbol del ecosistema) para apuntar el
linter a arboles-fixture aislados. Cada tipo de finding se prueba con un fixture
que planta la violacion (debe marcarla) y, donde aporta, un fixture limpio (no
debe marcarla). Ademas verifica exit codes, forma del --json, y los DOS
edge-cases criticos que NO deben regresar:
  (a) lineas `description:` de frontmatter no se marcan como CITED-RULE-MISSING,
  (b) un wf con `context: fork` + `agent:` no se marca por Agent en
      ALLOWED-TOOLS-MISMATCH.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


def lint(root, *flags):
    return run_script("sdd-structural-lint.py", "--root", root, *flags)


def types_in(root, *flags):
    """Devuelve el set de tipos de finding emitidos en --json (filtro de flags)."""
    r = run_script("sdd-structural-lint.py", "--root", root, "--json", *flags)
    return r, {f["type"] for f in json.loads(r.stdout)}


def skill_md(name, body, extra_fm=""):
    return (f"---\nname: {name}\ndescription: una skill.\n"
            f"user-invocable: {'true' if name.startswith('wf-') else 'false'}\n"
            f"{extra_fm}---\n\n# {name}\n\n{body}\n")


class StructuralLintTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    # --- KB con N reglas, para citas validas/invalidas ---------------------
    def _kb_with_rules(self, name, n):
        rules = "\n".join(f"## Regla {i}: regla {i}\nTexto." for i in range(1, n + 1))
        write(self.root / "spec" / "skills" / name / "SKILL.md",
              skill_md(name, rules))

    # === CITED-RULE-MISSING ===============================================
    def test_cited_rule_missing_flagged(self):
        self._kb_with_rules("kb-real", 3)
        write(self.root / "spec" / "skills" / "kb-otra" / "SKILL.md",
              skill_md("kb-otra", "Ver Regla 9 de kb-real para el detalle."))
        r, types = types_in(self.root)
        self.assertIn("CITED-RULE-MISSING", types, r.stdout)

    def test_cited_rule_existing_not_flagged(self):
        self._kb_with_rules("kb-real", 3)
        write(self.root / "spec" / "skills" / "kb-otra" / "SKILL.md",
              skill_md("kb-otra", "Ver Regla 2 de kb-real para el detalle."))
        _, types = types_in(self.root)
        self.assertNotIn("CITED-RULE-MISSING", types)

    # === CITED-SKILL-MISSING ==============================================
    def test_cited_skill_missing_flagged(self):
        write(self.root / "spec" / "skills" / "kb-otra" / "SKILL.md",
              skill_md("kb-otra", "Segun Regla 1 de kb-fantasma esto aplica."))
        _, types = types_in(self.root)
        self.assertIn("CITED-SKILL-MISSING", types)

    # === CITED-RULE-ON-WORKFLOW ===========================================
    def test_cited_rule_on_workflow_flagged(self):
        write(self.root / "spec" / "skills" / "kb-otra" / "SKILL.md",
              skill_md("kb-otra", "Como dice la Regla 3 de wf-algo."))
        _, types = types_in(self.root)
        self.assertIn("CITED-RULE-ON-WORKFLOW", types)

    # === ABSOLUTE-PATH ====================================================
    def test_absolute_path_flagged(self):
        write(self.root / "spec" / "skills" / "kb-otra" / "SKILL.md",
              skill_md("kb-otra", "Lee /Users/oscar/proyecto/spec.md como entrada."))
        _, types = types_in(self.root)
        self.assertIn("ABSOLUTE-PATH", types)

    def test_absolute_path_in_docs_not_flagged(self):
        # docs/ se excluye: el path absoluto es evidencia narrativa
        write(self.root / "docs" / "ROADMAP.md",
              "# Roadmap\n\nHallazgo en /Users/oscar/x.md durante la auditoria.\n")
        _, types = types_in(self.root)
        self.assertNotIn("ABSOLUTE-PATH", types)

    # === NAME-MISMATCH ====================================================
    def test_name_mismatch_flagged(self):
        # name del frontmatter != nombre del directorio
        write(self.root / "spec" / "skills" / "kb-dir" / "SKILL.md",
              skill_md("kb-otro-nombre", "Cuerpo."))
        _, types = types_in(self.root)
        self.assertIn("NAME-MISMATCH", types)

    def test_name_match_not_flagged(self):
        write(self.root / "spec" / "skills" / "kb-dir" / "SKILL.md",
              skill_md("kb-dir", "Cuerpo."))
        _, types = types_in(self.root)
        self.assertNotIn("NAME-MISMATCH", types)

    # === AGENT-MEMORY-DECLARED (D-041) ====================================
    def _agent_md(self, name, extra_fm=""):
        return (f"---\nname: {name}\ndescription: un agente.\n"
                f"skills: [kb-x]\n{extra_fm}color: green\n---\n\n# {name}\n\nCuerpo.\n")

    def test_agent_memory_declared_flagged(self):
        # Un agente que declara memory: el estado debe vivir en los artefactos.
        write(self.root / "spec" / "agents" / "mi-agente.md",
              self._agent_md("mi-agente", "memory: project\n"))
        r, types = types_in(self.root)
        self.assertIn("AGENT-MEMORY-DECLARED", types)
        self.assertIn("blocking", r.stdout)

    def test_agent_without_memory_not_flagged(self):
        write(self.root / "spec" / "agents" / "mi-agente.md",
              self._agent_md("mi-agente"))
        _, types = types_in(self.root)
        self.assertNotIn("AGENT-MEMORY-DECLARED", types)

    def test_agent_memory_in_creation_template_flagged(self):
        # La plantilla de kb-sdd-creation-guide es de donde hereda cada agente
        # nuevo: si memory: vuelve ahi, vuelve a todo el ecosistema.
        write(self.root / "meta" / "skills" / "kb-sdd-creation-guide" /
              "references" / "frontmatter-templates.md",
              "# Plantillas\n\n```yaml\n---\nname: <nombre>\nmemory: project\n---\n```\n")
        _, types = types_in(self.root)
        self.assertIn("AGENT-MEMORY-DECLARED", types)

    def test_non_agent_with_memory_not_flagged(self):
        # Solo aplica a */agents/ y a la plantilla: una skill que mencione
        # memory: en su cuerpo no es una declaracion de agente.
        write(self.root / "spec" / "skills" / "kb-mem" / "SKILL.md",
              skill_md("kb-mem", "El campo `memory:` del frontmatter de un agente."))
        _, types = types_in(self.root)
        self.assertNotIn("AGENT-MEMORY-DECLARED", types)

    # === AGENT-DISPATCH-UNSYNCED (D-043) ==================================
    def test_agent_dispatch_without_sync_flag_flagged(self):
        # Un wf que delega por la tool Agent sin run_in_background: false se
        # queda sin handle sincrono y acaba sondeando el disco.
        write(self.root / "spec" / "skills" / "wf-orq" / "SKILL.md",
              skill_md("wf-orq",
                       'Lanza el trabajo con:\n\n```\nAgent(\n'
                       '  subagent_type: "sdd-spec-writer",\n'
                       '  prompt: "Ejecuta el skill /wf-x"\n)\n```\n'))
        r, types = types_in(self.root)
        self.assertIn("AGENT-DISPATCH-UNSYNCED", types)
        self.assertIn("blocking", r.stdout)

    def test_agent_dispatch_with_sync_flag_not_flagged(self):
        write(self.root / "spec" / "skills" / "wf-orq" / "SKILL.md",
              skill_md("wf-orq",
                       'Lanza el trabajo con:\n\n```\nAgent(\n'
                       '  subagent_type: "sdd-spec-writer",\n'
                       '  run_in_background: false,\n'
                       '  prompt: "Ejecuta el skill /wf-x"\n)\n```\n'))
        _, types = types_in(self.root)
        self.assertNotIn("AGENT-DISPATCH-UNSYNCED", types)

    def test_kb_describing_agent_dispatch_not_flagged(self):
        # La regla es sobre PRESCRIPCIONES de delegacion: una kb- que DESCRIBE
        # el patron (kb-sdd-creation-guide) no delega y no debe tripear.
        write(self.root / "meta" / "skills" / "kb-guia" / "SKILL.md",
              skill_md("kb-guia",
                       "Una wf que delega invoca la tool `Agent` con su "
                       "subagent_type."))
        _, types = types_in(self.root)
        self.assertNotIn("AGENT-DISPATCH-UNSYNCED", types)

    def test_wf_without_delegation_not_flagged(self):
        write(self.root / "spec" / "skills" / "wf-simple" / "SKILL.md",
              skill_md("wf-simple", "Corre un script y reporta el veredicto."))
        _, types = types_in(self.root)
        self.assertNotIn("AGENT-DISPATCH-UNSYNCED", types)

    # === USER-FACING-COMMAND (11.10) ======================================
    def test_user_facing_command_flagged(self):
        # Un mensaje dictado al usuario NO lleva comandos: si los ve, los teclea,
        # y al teclearlos pasa argumentos a mano saltandose las validaciones que
        # hace el hilo principal al construir la invocacion.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", 'Si falta el argumento, informa:\n'
                               '> "Uso: `/wf-x <archivo.md>`"\n'))
        r, types = types_in(self.root)
        self.assertIn("USER-FACING-COMMAND", types, r.stdout)
        self.assertNotIn("blocking", r.stdout)

    def test_user_facing_command_flagged_in_option_list(self):
        # Tambien en listas de opciones dictadas (`> - "..."`).
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", '> - "`/wf-x analyze <spec.md>`"\n'))
        _, types = types_in(self.root)
        self.assertIn("USER-FACING-COMMAND", types)

    def test_natural_language_message_not_flagged(self):
        # El arreglo: la misma parada, dicha como accion y no como invocacion.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", 'Si falta el argumento, informa:\n'
                               '> "Necesito el path del documento que quieres analizar."\n'))
        _, types = types_in(self.root)
        self.assertNotIn("USER-FACING-COMMAND", types)

    def test_agent_prose_naming_a_workflow_not_flagged(self):
        # Prosa dirigida al AGENTE (sin comillas de apertura): es un puntero de
        # invocacion legitimo, no un mensaje al usuario.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "Si el PRD no esta sellado, remite a `wf-prd-review`.\n"))
        _, types = types_in(self.root)
        self.assertNotIn("USER-FACING-COMMAND", types)

    def test_agent_blockquote_with_inner_quotes_not_flagged(self):
        # Falso positivo real cazado al estrenar la regla: prosa al agente, en
        # blockquote, con comillas POR DENTRO (un argumento shell). El mensaje
        # dictado ABRE con comilla; esto no.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", '> (`!grep -nE \'^version:\' "<prd>"`). Es lo que permite a\n'
                               '> `wf-spec-discover` comprobar la version.\n'))
        _, types = types_in(self.root)
        self.assertNotIn("USER-FACING-COMMAND", types)

    def test_delegation_prompt_keeps_the_skill_path(self):
        # Un prompt de delegacion es agente->agente y DEBE nombrar el SKILL.md.
        # No lleva la forma `> "`, asi que la regla no lo toca.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", 'Agent(\n  prompt: "Lee `.claude/skills/wf-y/SKILL.md` '
                               'y ejecuta sus pasos TU MISMO."\n)\n'))
        _, types = types_in(self.root)
        self.assertNotIn("USER-FACING-COMMAND", types)

    # --- detector (b): la seccion "Informar al usuario" -------------------
    def test_user_facing_command_flagged_inline_in_report_section(self):
        # La forma que el detector de comillas NO veia, y que costo 19 nombres de
        # workflow filtrados a los artefactos de una corrida real: el paso de
        # informe dicta los siguientes pasos EN LINEA, sin comillas.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "## Paso 9: Informar al usuario\n\n"
                               "Informa: path del informe. Siguiente paso: "
                               "`/wf-prepare-plan generate <spec.md>`.\n"))
        r, types = types_in(self.root)
        self.assertIn("USER-FACING-COMMAND", types, r.stdout)
        self.assertNotIn("blocking", r.stdout)

    def test_user_facing_command_flagged_without_slash_in_report_section(self):
        # Sin barra tambien: el nombre desnudo es igual de invocable a ojos del
        # usuario. El backstop de 11.7 se escribio mirando `/wf-` —el arreglo—
        # en vez de `wf-` —el defecto—, y por ahi se colaron los 19.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "## Paso 9: Informar al usuario\n\n"
                               "Si hay conflictos, sugiere resolverlos con "
                               "`wf-spec-delta`.\n"))
        _, types = types_in(self.root)
        self.assertIn("USER-FACING-COMMAND", types)

    def test_report_section_ends_at_the_next_heading(self):
        # La seccion acaba donde acaba: un puntero de invocacion en el paso
        # SIGUIENTE es prosa al agente y no se marca. Sin este corte, la regla
        # marcaria media skill desde el primer "Informar al usuario".
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "## Paso 8: Informar al usuario\n\n"
                               "Informa el path generado.\n\n"
                               "## Paso 9: Cierre\n\n"
                               "Delega en `wf-spec-conflict` para la pasada final.\n"))
        _, types = types_in(self.root)
        self.assertNotIn("USER-FACING-COMMAND", types)

    def test_natural_language_report_section_not_flagged(self):
        # El arreglo, medido: el mismo paso, dicho como accion que el usuario
        # PIDE en vez de comando que teclea.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "## Paso 9: Informar al usuario\n\n"
                               "Informa: path del informe. Siguiente paso: pedirme "
                               "que **genere el plan tecnico** de la feature.\n"))
        _, types = types_in(self.root)
        self.assertNotIn("USER-FACING-COMMAND", types)

    def test_ordinary_section_with_workflow_pointer_not_flagged(self):
        # Un encabezado normal no activa el detector (b): fuera de la seccion de
        # informe sigue mandando la forma `> "..."` del detector (a).
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "## Paso 3: Verificar precondiciones\n\n"
                               "Si el PRD no esta sellado, remite a `wf-prd-review`.\n"))
        _, types = types_in(self.root)
        self.assertNotIn("USER-FACING-COMMAND", types)

    def test_report_section_in_a_kb_not_flagged(self):
        # La regla escanea workflows. Una `kb-*` describe el mecanismo AL AGENTE
        # que la carga; nombrar ahi un `wf-*` es legitimo.
        write(self.root / "spec" / "skills" / "kb-y" / "SKILL.md",
              skill_md("kb-y", "## Informar al usuario\n\n"
                               "El orquestador remite a `/wf-spec-gap-resolve`.\n"))
        _, types = types_in(self.root)
        self.assertNotIn("USER-FACING-COMMAND", types)

    # --- detectores (c) opciones de gate y (d) mensaje en linea ----------
    def test_askuserquestion_option_naming_a_workflow_flagged(self):
        # Las opciones de un gate SON la pantalla que ve el usuario: su titulo y
        # su descripcion se le pintan literalmente. Medido en el gate de
        # gobernanza de features-first, que nombraba el workflow con sus flags.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "Presenta el gate y pregunta con `AskUserQuestion`:\n"
                               "  - *Formalizar el cambio* (recomendada) — se abre con "
                               "`wf-prd-change <prd.md> --new-reqs <c.md>`.\n"
                               "  - *Continuar igualmente* — sigues con alcance derivado.\n"))
        r, types = types_in(self.root)
        self.assertIn("USER-FACING-COMMAND", types, r.stdout)

    def test_askuserquestion_mentioned_midsentence_not_flagged(self):
        # Falso positivo real al estrenar (c): una linea que solo MENCIONA la tool
        # a media frase es prosa al agente. El bloque se abre si la linea lo
        # INTRODUCE (acaba en `:`), no si la nombra.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "Corre en el hilo principal (igual que `wf-prd-create`) "
                               "porque sostiene gates que requieren `AskUserQuestion`.\n"))
        _, types = types_in(self.root)
        self.assertNotIn("USER-FACING-COMMAND", types)

    def test_option_block_ends_at_the_first_non_bullet(self):
        # El bloque de opciones acaba donde acaba: la prosa que sigue vuelve a ser
        # del agente.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "Pregunta con `AskUserQuestion`:\n"
                               "  - *Seguir* — continua el flujo.\n"
                               "\nDespues delega en `wf-spec-conflict` la pasada final.\n"))
        _, types = types_in(self.root)
        self.assertNotIn("USER-FACING-COMMAND", types)

    def test_inline_quoted_message_flagged(self):
        # `informa: "..."` / `avisa ("...")`: mensaje al usuario sin blockquote.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", 'Si no esta sellado → avisa ("recomendable cerrarlo '
                               'con `/wf-prd-review`") y continua.\n'))
        _, types = types_in(self.root)
        self.assertIn("USER-FACING-COMMAND", types)

    def test_inline_message_in_natural_language_not_flagged(self):
        # El arreglo: mismo aviso, sin ensenar la invocacion.
        write(self.root / "spec" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", 'Si no esta sellado → avisa ("conviene cerrar la '
                               'aprobacion; dime si lo revisamos") y continua.\n'))
        _, types = types_in(self.root)
        self.assertNotIn("USER-FACING-COMMAND", types)

    # === AGENT-TOOL-CLASH (D-051) =========================================
    def _auditor(self):
        write(self.root / "spec" / "agents" / "mi-auditor.md",
              self._agent_md("mi-auditor", "disallowedTools: Write, Edit\n"))

    def test_agent_tool_clash_flagged(self):
        # allowed-tools declara Write; el agente que ejecuta la skill lo prohibe.
        self._auditor()
        write(self.root / "spec" / "skills" / "wf-audita" / "SKILL.md",
              skill_md("wf-audita", "Escribe el informe.",
                       extra_fm=("allowed-tools: [Read, Write, Bash]\n"
                                 "context: fork\nagent: mi-auditor\n")))
        r, types = types_in(self.root)
        self.assertIn("AGENT-TOOL-CLASH", types, r.stdout)
        self.assertIn("blocking", r.stdout)

    def test_agent_tool_clash_names_the_offending_tool(self):
        # El mensaje debe decir QUE tool choca: si no, no es accionable.
        self._auditor()
        write(self.root / "spec" / "skills" / "wf-audita" / "SKILL.md",
              skill_md("wf-audita", "Escribe el informe.",
                       extra_fm=("allowed-tools: [Read, Edit, Bash]\n"
                                 "context: fork\nagent: mi-auditor\n")))
        r = run_script("sdd-structural-lint.py", "--root", self.root, "--json")
        msgs = [f["message"] for f in json.loads(r.stdout)
                if f["type"] == "AGENT-TOOL-CLASH"]
        self.assertTrue(msgs, r.stdout)
        self.assertIn("Edit", msgs[0])
        self.assertIn("mi-auditor", msgs[0])

    def test_agent_tool_clash_clean_after_removing_the_tool(self):
        # El arreglo: allowed-tools coherente con lo que el agente tiene.
        self._auditor()
        write(self.root / "spec" / "skills" / "wf-audita" / "SKILL.md",
              skill_md("wf-audita", "Escribe el informe con `cat >`.",
                       extra_fm=("allowed-tools: [Read, Bash]\n"
                                 "context: fork\nagent: mi-auditor\n")))
        _, types = types_in(self.root)
        self.assertNotIn("AGENT-TOOL-CLASH", types)

    def test_agent_tool_clash_ignores_skill_without_agent(self):
        # Sin `agent:`, la skill NO la ejecuta nadie con disallowedTools:
        # su allowed-tools es la palabra final y no hay choque posible.
        self._auditor()
        write(self.root / "spec" / "skills" / "wf-suelta" / "SKILL.md",
              skill_md("wf-suelta", "Escribe el informe.",
                       extra_fm="allowed-tools: [Read, Write, Bash]\n"))
        _, types = types_in(self.root)
        self.assertNotIn("AGENT-TOOL-CLASH", types)

    def test_agent_tool_clash_ignores_agent_without_disallowed(self):
        # Un agente sin disallowedTools no restringe nada.
        write(self.root / "spec" / "agents" / "mi-escritor.md",
              self._agent_md("mi-escritor"))
        write(self.root / "spec" / "skills" / "wf-escribe" / "SKILL.md",
              skill_md("wf-escribe", "Escribe el artefacto.",
                       extra_fm=("allowed-tools: [Read, Write, Bash]\n"
                                 "context: fork\nagent: mi-escritor\n")))
        _, types = types_in(self.root)
        self.assertNotIn("AGENT-TOOL-CLASH", types)

    # === FORK-ORCHESTRATOR (D-045) ========================================
    DELEG = ('Delega con:\n\n```\nAgent(\n'
             '  subagent_type: "sdd-spec-writer",\n'
             '  run_in_background: false,\n'
             '  prompt: "Lee el SKILL.md y ejecuta sus pasos tu mismo."\n)\n```\n')

    def test_fork_orchestrator_with_gate_is_blocking(self):
        # Fork + delegacion + escotilla --allow-*: le aplican los dos motivos
        # (no puede preguntar, no consigue el primer plano) => blocking.
        write(self.root / "spec" / "skills" / "wf-orq" / "SKILL.md",
              skill_md("wf-orq",
                       self.DELEG + "\nSin `--allow-open-critical-gaps` detente.\n",
                       extra_fm="context: fork\n"))
        r, types = types_in(self.root)
        self.assertIn("FORK-ORCHESTRATOR", types)
        self.assertIn("blocking", r.stdout)

    def test_fork_orchestrator_without_gate_is_warning(self):
        # Fork + delegacion pero sin gate: solo le aplica el motivo de sincronia.
        # Se marca (warning) sin arrastrar aqui una fase entera.
        write(self.root / "spec" / "skills" / "wf-exec" / "SKILL.md",
              skill_md("wf-exec", self.DELEG, extra_fm="context: fork\n"))
        r, types = types_in(self.root)
        self.assertIn("FORK-ORCHESTRATOR", types)
        self.assertNotIn("blocking", r.stdout)

    def test_orchestrator_in_main_thread_not_flagged(self):
        # El arreglo: misma delegacion, sin context: fork => limpio.
        write(self.root / "spec" / "skills" / "wf-orq" / "SKILL.md",
              skill_md("wf-orq",
                       self.DELEG + "\nSin `--allow-open-critical-gaps` detente.\n"))
        _, types = types_in(self.root)
        self.assertNotIn("FORK-ORCHESTRATOR", types)

    def test_fork_worker_without_delegation_not_flagged(self):
        # Un worker (fork + agent:, sin delegar) es la arquitectura correcta.
        write(self.root / "spec" / "skills" / "wf-worker" / "SKILL.md",
              skill_md("wf-worker", "Escribe el artefacto y reporta.",
                       extra_fm="context: fork\nagent: sdd-spec-writer\n"))
        _, types = types_in(self.root)
        self.assertNotIn("FORK-ORCHESTRATOR", types)

    def test_fork_over_declaring_agent_tool_not_flagged(self):
        # Declarar Agent en allowed-tools sin usarlo en el cuerpo es
        # sobre-declaracion, no orquestacion: la regla mira el CUERPO.
        write(self.root / "spec" / "skills" / "wf-decl" / "SKILL.md",
              skill_md("wf-decl", "Corre un script y reporta.",
                       extra_fm="context: fork\nallowed-tools: [Read, Bash, Agent]\n"))
        _, types = types_in(self.root)
        self.assertNotIn("FORK-ORCHESTRATOR", types)

    def test_kb_describing_fork_orchestrator_not_flagged(self):
        write(self.root / "meta" / "skills" / "kb-guia" / "SKILL.md",
              skill_md("kb-guia",
                       "Una wf con `context: fork` que use la tool `Agent` no "
                       "puede conseguir el primer plano.",
                       extra_fm="context: fork\n"))
        _, types = types_in(self.root)
        self.assertNotIn("FORK-ORCHESTRATOR", types)

    # === FORK-CONFIRM-GATE / FORK-INTERVIEW, formas de Design (D-072) =====

    def test_fork_confirm_gate_catches_the_closed_yes_no_suffix(self):
        # La forma de Design: la pregunta cerrada dictada con su sufijo.
        write(self.root / "design" / "skills" / "wf-merge" / "SKILL.md",
              skill_md("wf-merge",
                       "Si el diff es breaking, avisa:\n"
                       "> \"Esto sobrescribe el target. ¿Quieres continuar? (y/n)\"\n",
                       extra_fm="context: fork\nagent: design-system-architect\n"))
        r, types = types_in(self.root)
        self.assertIn("FORK-CONFIRM-GATE", types)
        self.assertIn("blocking", r.stdout)

    def test_fork_confirm_gate_catches_the_infinitive_forms(self):
        # "pedir confirmacion" y "pedir al usuario": la regla cazaba la forma
        # conjugada y estas se le escapaban por una letra.
        write(self.root / "design" / "skills" / "wf-pide" / "SKILL.md",
              skill_md("wf-pide",
                       "Antes de escribir, pedir confirmacion al usuario del formato.",
                       extra_fm="context: fork\nagent: design-system-architect\n"))
        _, types = types_in(self.root)
        self.assertIn("FORK-CONFIRM-GATE", types)

    def test_fork_confirm_gate_catches_asking_the_user_to_confirm(self):
        # "Detente y pide al usuario que confirme": para bien, pero le dicta la
        # pregunta y le promete una continuacion que un fork no puede tener.
        write(self.root / "design" / "skills" / "wf-inventario" / "SKILL.md",
              skill_md("wf-inventario",
                       "Detente aqui. Presenta el inventario y pide al usuario "
                       "que confirme, corrija o descarte.",
                       extra_fm="context: fork\nagent: design-system-architect\n"))
        _, types = types_in(self.root)
        self.assertIn("FORK-CONFIRM-GATE", types)

    def test_fork_interview_catches_the_open_questionnaire(self):
        # El caso medido: siete preguntas abiertas dictadas en un fork, y el
        # check reportando CERO porque su heuristica no conocia esta forma.
        write(self.root / "design" / "skills" / "wf-vibes" / "SKILL.md",
              skill_md("wf-vibes",
                       "Realiza al usuario una serie de preguntas abiertas sobre el producto.",
                       extra_fm="context: fork\nagent: design-system-architect\n"))
        _, types = types_in(self.root)
        self.assertIn("FORK-INTERVIEW", types)

    def test_fork_interview_catches_iterating_with_the_user(self):
        write(self.root / "design" / "skills" / "wf-cura" / "SKILL.md",
              skill_md("wf-cura",
                       "Presenta la lista. Iterar hasta que el usuario confirme.",
                       extra_fm="context: fork\nagent: design-system-architect\n"))
        _, types = types_in(self.root)
        self.assertIn("FORK-INTERVIEW", types)

    def test_interview_in_the_main_thread_is_not_flagged(self):
        # El arreglo: la misma entrevista, sin fork, con AskUserQuestion. Es
        # exactamente donde debe vivir.
        write(self.root / "design" / "skills" / "wf-vibes-main" / "SKILL.md",
              skill_md("wf-vibes-main",
                       "Realiza al usuario una serie de preguntas abiertas sobre el producto.",
                       extra_fm="allowed-tools: [Bash, Agent, AskUserQuestion]\n"))
        _, types = types_in(self.root)
        self.assertNotIn("FORK-INTERVIEW", types)
        self.assertNotIn("FORK-CONFIRM-GATE", types)

    def test_questions_written_into_an_artifact_are_not_an_interview(self):
        # Un fork que EJEMPLIFICA como redactar las preguntas de un artefacto no
        # esta preguntando nada: wf-spec-analyze lleva `¿…?` de muestra y es
        # correcto. Si esto casara, la regla seria inservible en Spec.
        write(self.root / "spec" / "skills" / "wf-analiza" / "SKILL.md",
              skill_md("wf-analiza",
                       "Cada gap se redacta concreto: \"¿catalogo persistente o texto libre?\".",
                       extra_fm="context: fork\nagent: sdd-spec-explorer\n"))
        _, types = types_in(self.root)
        self.assertNotIn("FORK-INTERVIEW", types)
        self.assertNotIn("FORK-CONFIRM-GATE", types)

    # === FORK-SELF-DELEGATION (D-070) =====================================

    def test_fork_ordering_delegation_to_its_own_agent_is_blocking(self):
        # El caso real: `agent: X` en el frontmatter y "Invoca el agente `X`" en
        # el cuerpo. El fork YA corre como X, asi que eso forkea un clon suyo.
        write(self.root / "spec" / "skills" / "wf-clon" / "SKILL.md",
              skill_md("wf-clon", "Invoca el agente `sdd-spec-writer` con ese prompt.",
                       extra_fm="context: fork\nagent: sdd-spec-writer\n"))
        r, types = types_in(self.root)
        self.assertIn("FORK-SELF-DELEGATION", types)
        self.assertIn("blocking", r.stdout)

    def test_fork_self_delegation_catches_the_role_statement(self):
        # La misma confusion en forma descriptiva: "delegas X al agente `Y`".
        write(self.root / "plan" / "skills" / "wf-rol" / "SKILL.md",
              skill_md("wf-rol",
                       "Tu rol es de orquestador puro: delegas la arquitectura al "
                       "agente `plan-architect`, y escribes el output.",
                       extra_fm="context: fork\nagent: plan-architect\n"))
        _, types = types_in(self.root)
        self.assertIn("FORK-SELF-DELEGATION", types)

    def test_fork_self_delegation_catches_the_unnamed_form(self):
        # "Invoca al agente con este prompt": en un fork con `agent:` no hay otro
        # agente al que referirse, asi que la forma sin nombre es la misma orden.
        write(self.root / "design" / "skills" / "wf-anon" / "SKILL.md",
              skill_md("wf-anon", "Invoca al agente con este prompt:",
                       extra_fm="context: fork\nagent: design-system-architect\n"))
        _, types = types_in(self.root)
        self.assertIn("FORK-SELF-DELEGATION", types)

    def test_fork_delegating_to_a_different_agent_not_flagged_here(self):
        # Delegar en OTRO agente es otro problema (FORK-ORCHESTRATOR), no este:
        # esta regla es especifica del clon de si mismo.
        write(self.root / "tasks" / "skills" / "wf-otro" / "SKILL.md",
              skill_md("wf-otro", "Invoca el agente `kmm-implementer` con ese prompt.",
                       extra_fm="context: fork\nagent: task-generator\n"))
        _, types = types_in(self.root)
        self.assertNotIn("FORK-SELF-DELEGATION", types)

    def test_main_thread_delegating_to_its_agent_not_flagged(self):
        # Sin `context: fork` no hay inyeccion: `agent:` no se usa y delegar por
        # la tool `Agent` es exactamente lo correcto (wf-spec-validate, D-065).
        write(self.root / "spec" / "skills" / "wf-main" / "SKILL.md",
              skill_md("wf-main", "Invoca el agente `sdd-spec-auditor` con ese prompt.",
                       extra_fm="agent: sdd-spec-auditor\n"))
        _, types = types_in(self.root)
        self.assertNotIn("FORK-SELF-DELEGATION", types)

    def test_describing_the_self_delegation_prohibition_is_not_an_order(self):
        # La NOTA que prohibe el patron no puede casar con el patron: la negacion
        # en la misma linea excluye el hallazgo (D-045 seccion 4).
        write(self.root / "spec" / "skills" / "wf-nota" / "SKILL.md",
              skill_md("wf-nota",
                       "Redactalo tu: no invoques el agente `sdd-spec-writer`, que "
                       "es el tuyo, porque forkearia un clon.",
                       extra_fm="context: fork\nagent: sdd-spec-writer\n"))
        _, types = types_in(self.root)
        self.assertNotIn("FORK-SELF-DELEGATION", types)

    def test_kb_describing_the_clone_antipattern_not_flagged(self):
        # Una kb-* que documenta el anti-patron lo describe, no lo prescribe.
        write(self.root / "meta" / "skills" / "kb-guia-clon" / "SKILL.md",
              skill_md("kb-guia-clon",
                       "Si el cuerpo dice invoca el agente `sdd-author`, forkea un clon.",
                       extra_fm="context: fork\nagent: sdd-author\n"))
        _, types = types_in(self.root)
        self.assertNotIn("FORK-SELF-DELEGATION", types)

    # === AGENT-PROMPT-REDISPATCH (D-044) ==================================
    def test_agent_prompt_redispatch_flagged(self):
        # "Ejecuta el skill /wf-X" hace que el delegado use el Skill tool, que
        # forkea otro subagente (un clon suyo si la sub-skill declara ese agent:).
        write(self.root / "spec" / "skills" / "wf-orq" / "SKILL.md",
              skill_md("wf-orq",
                       'Delega con `Agent`:\n\n```\nAgent(\n'
                       '  subagent_type: "sdd-spec-explorer",\n'
                       '  run_in_background: false,\n'
                       '  prompt: "Ejecuta el skill /wf-spec-analyze con: <prd.md>"\n)\n```\n'))
        r, types = types_in(self.root)
        self.assertIn("AGENT-PROMPT-REDISPATCH", types)
        self.assertIn("blocking", r.stdout)

    def test_agent_prompt_self_execution_not_flagged(self):
        write(self.root / "spec" / "skills" / "wf-orq" / "SKILL.md",
              skill_md("wf-orq",
                       'Delega con `Agent`:\n\n```\nAgent(\n'
                       '  subagent_type: "sdd-spec-explorer",\n'
                       '  run_in_background: false,\n'
                       '  prompt: "Lee .claude/skills/wf-spec-analyze/SKILL.md y ejecuta '
                       'sus pasos TU MISMO sobre: <prd.md>. NO uses el Skill tool."\n)\n```\n'))
        _, types = types_in(self.root)
        self.assertNotIn("AGENT-PROMPT-REDISPATCH", types)

    def test_kb_describing_redispatch_not_flagged(self):
        # La kb que PROHIBE el anti-patron tiene que poder nombrarlo.
        write(self.root / "meta" / "skills" / "kb-guia" / "SKILL.md",
              skill_md("kb-guia",
                       "Nunca escribas un prompt que diga «Ejecuta el skill /wf-X»: "
                       "el delegado re-despacha con el `Skill` tool."))
        _, types = types_in(self.root)
        self.assertNotIn("AGENT-PROMPT-REDISPATCH", types)

    # === REFERENCE-PATH-MISSING ===========================================
    def test_reference_path_missing_flagged(self):
        write(self.root / "spec" / "skills" / "kb-ref" / "SKILL.md",
              skill_md("kb-ref",
                       "Consulta ${CLAUDE_SKILL_DIR}/references/no_existe.md aqui."))
        _, types = types_in(self.root)
        self.assertIn("REFERENCE-PATH-MISSING", types)

    def test_reference_path_existing_not_flagged(self):
        write(self.root / "spec" / "skills" / "kb-ref" / "references" / "guia.md",
              "contenido")
        write(self.root / "spec" / "skills" / "kb-ref" / "SKILL.md",
              skill_md("kb-ref",
                       "Consulta ${CLAUDE_SKILL_DIR}/references/guia.md aqui."))
        _, types = types_in(self.root)
        self.assertNotIn("REFERENCE-PATH-MISSING", types)

    # === SKILL-REF-MISSING ================================================
    def test_skill_ref_missing_flagged_in_readme(self):
        write(self.root / "spec" / "README.md",
              "# Fase spec\n\nUsa `kb-inexistente` para esto.\n")
        _, types = types_in(self.root)
        self.assertIn("SKILL-REF-MISSING", types)

    def test_skill_ref_real_not_flagged(self):
        write(self.root / "spec" / "skills" / "kb-existe" / "SKILL.md",
              skill_md("kb-existe", "Cuerpo."))
        write(self.root / "spec" / "README.md",
              "# Fase spec\n\nUsa `kb-existe` para esto.\n")
        _, types = types_in(self.root)
        self.assertNotIn("SKILL-REF-MISSING", types)

    # === ALLOWED-TOOLS-MISMATCH ===========================================
    def test_allowed_tools_bash_missing_flagged(self):
        write(self.root / "plan" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "Paso 1.\n\n!git rev-parse HEAD\n",
                       extra_fm="allowed-tools: [Read, Write]\n"))
        _, types = types_in(self.root)
        self.assertIn("ALLOWED-TOOLS-MISMATCH", types)

    def test_allowed_tools_bash_present_not_flagged(self):
        write(self.root / "plan" / "skills" / "wf-x" / "SKILL.md",
              skill_md("wf-x", "Paso 1.\n\n!git rev-parse HEAD\n",
                       extra_fm="allowed-tools: [Read, Write, Bash]\n"))
        _, types = types_in(self.root)
        self.assertNotIn("ALLOWED-TOOLS-MISMATCH", types)

    # === DESCRIPTION-TOO-LONG =============================================
    def test_description_too_long_flagged(self):
        long_desc = "x" * 230
        write(self.root / "spec" / "skills" / "kb-long" / "SKILL.md",
              f"---\nname: kb-long\ndescription: {long_desc}\n"
              f"user-invocable: false\n---\n\n# kb-long\n\nCuerpo.\n")
        _, types = types_in(self.root)
        self.assertIn("DESCRIPTION-TOO-LONG", types)

    # === USER-INVOCABLE-MISSING ===========================================
    def test_user_invocable_missing_on_wf_flagged(self):
        write(self.root / "spec" / "skills" / "wf-noui" / "SKILL.md",
              "---\nname: wf-noui\ndescription: un wf.\n---\n\n# wf-noui\n\nCuerpo.\n")
        _, types = types_in(self.root)
        self.assertIn("USER-INVOCABLE-MISSING", types)

    def test_user_invocable_missing_on_kb_flagged(self):
        # kb sin `user-invocable: false`
        write(self.root / "spec" / "skills" / "kb-noui" / "SKILL.md",
              "---\nname: kb-noui\ndescription: una kb.\n---\n\n# kb-noui\n\nCuerpo.\n")
        _, types = types_in(self.root)
        self.assertIn("USER-INVOCABLE-MISSING", types)

    # === EDGE-CASE (a): description: no se marca como CITED-RULE-MISSING ===
    def test_description_provenance_not_flagged_as_cited_rule(self):
        # La linea description: cita una Regla N de una kb que no la define;
        # NO debe marcarse (provenance historica intencionada).
        self._kb_with_rules("kb-real", 2)
        write(self.root / "spec" / "skills" / "kb-prov" / "SKILL.md",
              "---\nname: kb-prov\n"
              "description: SSoT extraida de Regla 9 de kb-real (provenance).\n"
              "user-invocable: false\n---\n\n# kb-prov\n\nCuerpo limpio sin citas.\n")
        r, types = types_in(self.root)
        self.assertNotIn("CITED-RULE-MISSING", types, r.stdout)
        self.assertNotIn("CITED-SKILL-MISSING", types, r.stdout)

    # === EDGE-CASE (b): context: fork + agent: no se marca por Agent =======
    def test_fork_pattern_not_flagged_for_agent(self):
        body = "Paso 1: el agente, con sus skills en contexto, hace el trabajo.\n"
        write(self.root / "design" / "skills" / "wf-fork" / "SKILL.md",
              skill_md("wf-fork", body,
                       extra_fm="allowed-tools: [Read]\ncontext: fork\n"
                                "agent: design-architect\n"))
        r, types = types_in(self.root, "--severity", "warning")
        self.assertNotIn("ALLOWED-TOOLS-MISMATCH", types, r.stdout)

    # === FORK-CONFIRM-GATE (blocking, D-064) ==============================
    def test_fork_confirm_gate_in_prose_is_blocking(self):
        """Un fork que DICTA "pregunta al usuario" no puede presentar ese gate.

        Es el hueco por el que se colaron diez sitios reales: FORK-ASKUSER-CONFLICT
        solo mira el nombre literal de la tool y daba 0 sobre un arbol con diez
        violaciones. El detector vigilaba la cita, no la conducta.
        """
        body = "Si ya existe → pregunta al usuario:\n> \"Ya existe. ¿Deseas regenerarlo?\"\n"
        write(self.root / "spec" / "skills" / "wf-fork-ow" / "SKILL.md",
              skill_md("wf-fork-ow", body,
                       extra_fm="allowed-tools: [Read, Write, Bash]\ncontext: fork\n"
                                "agent: sdd-spec-writer\n"))
        r, types = types_in(self.root, "--severity", "blocking")
        self.assertIn("FORK-CONFIRM-GATE", types, r.stdout)

    def test_fork_confirm_gate_catches_the_bracketed_choice(self):
        """La otra forma medida: "pregunta: `[sobreescribir | cancelar]`"."""
        body = "- `!test -f x` — si existe, informa al usuario y pregunta: `[sobreescribir | cancelar]`.\n"
        write(self.root / "spec" / "skills" / "wf-fork-ow2" / "SKILL.md",
              skill_md("wf-fork-ow2", body,
                       extra_fm="allowed-tools: [Read, Bash]\ncontext: fork\n"
                                "agent: sdd-spec-auditor\n"))
        r, types = types_in(self.root, "--severity", "blocking")
        self.assertIn("FORK-CONFIRM-GATE", types, r.stdout)

    def test_fork_confirm_gate_catches_waiting_for_the_user(self):
        """D-068: ordenar ESPERAR a una persona tampoco es ejecutable en un fork.

        Forma real, en el ownership checkpoint de wf-spec-discover.
        """
        body = "- Presenta la tabla\n- **Espera respuesta del usuario** antes de continuar\n"
        write(self.root / "spec" / "skills" / "wf-fork-wait" / "SKILL.md",
              skill_md("wf-fork-wait", body,
                       extra_fm="allowed-tools: [Read, Write, Bash]\ncontext: fork\n"
                                "agent: sdd-spec-explorer\n"))
        r, types = types_in(self.root, "--severity", "blocking")
        self.assertIn("FORK-CONFIRM-GATE", types, r.stdout)

    def test_fork_confirm_gate_catches_explicit_confirmation(self):
        """Forma real, en el Paso 5 de wf-spec-amend."""
        body = "Pide confirmación explícita al usuario. Sin confirmación no hay enmienda.\n"
        write(self.root / "spec" / "skills" / "wf-fork-conf" / "SKILL.md",
              skill_md("wf-fork-conf", body,
                       extra_fm="allowed-tools: [Read, Write, Bash]\ncontext: fork\n"
                                "agent: sdd-spec-writer\n"))
        r, types = types_in(self.root, "--severity", "blocking")
        self.assertIn("FORK-CONFIRM-GATE", types, r.stdout)

    def test_describing_another_skills_gate_is_not_a_finding(self):
        """El falso positivo que aparecio al afilar la regla (D-068).

        `wf-prd-change-cascade` describe el gate de OTRA skill —"resolver las
        bifurcaciones preguntando al usuario"— justo para explicar que el no
        puede heredarlo. El dos-puntos es lo que separa la orden de la
        descripcion.
        """
        body = ("`wf-prd-change` tiene un gate: confirmar la clasificación y resolver las "
                "bifurcaciones preguntando al usuario. Tú eres un subagente y no puedes "
                "heredarlo, así que pasa `--defer-decisions`.\n")
        write(self.root / "prd" / "skills" / "wf-fork-desc" / "SKILL.md",
              skill_md("wf-fork-desc", body,
                       extra_fm="allowed-tools: [Read, Bash, Skill]\ncontext: fork\n"))
        r, types = types_in(self.root)
        self.assertNotIn("FORK-CONFIRM-GATE", types, r.stdout)

    def test_describing_the_prohibition_is_not_a_gate(self):
        """El falso positivo que habria hecho la regla inusable.

        Las notas de D-062/D-064 explican DENTRO del fork por que ahi no se
        pregunta. Marcar esa prosa obligaria a quitar la explicacion justo del
        sitio donde hace falta.
        """
        body = ("> **Por qué aquí no preguntas.** Corres en `context: fork`, y un subagente no puede\n"
                "> presentarle una elección al usuario ni una pregunta al usuario final.\n"
                "Paras y reportas `STOP_ARTEFACTO_EXISTE` a quien te lanzó.\n")
        write(self.root / "spec" / "skills" / "wf-fork-ok" / "SKILL.md",
              skill_md("wf-fork-ok", body,
                       extra_fm="allowed-tools: [Read, Write, Bash]\ncontext: fork\n"
                                "agent: sdd-spec-writer\n"))
        r, types = types_in(self.root)
        self.assertNotIn("FORK-CONFIRM-GATE", types, r.stdout)

    def test_main_thread_skill_may_hold_the_gate(self):
        """En el hilo principal el gate es correcto: la regla no debe morderlo."""
        body = "Si ya existe → pregunta al usuario con AskUserQuestion qué hacer.\n"
        write(self.root / "spec" / "skills" / "wf-main-gate" / "SKILL.md",
              skill_md("wf-main-gate", body,
                       extra_fm="allowed-tools: [Bash, Agent, AskUserQuestion]\n"))
        r, types = types_in(self.root)
        self.assertNotIn("FORK-CONFIRM-GATE", types, r.stdout)

    # === FORK-INTERVIEW (warning, D-015) ==================================
    def test_fork_interview_flagged_as_warning(self):
        # fork que entrevista EN PROSA (sin declarar AskUserQuestion) → warning
        body = "Paso 1: pregunta secuencialmente, una opcion a la vez. Esperar respuesta.\n"
        write(self.root / "design" / "skills" / "wf-fork-iv" / "SKILL.md",
              skill_md("wf-fork-iv", body,
                       extra_fm="allowed-tools: [Read, Bash]\ncontext: fork\n"
                                "agent: kmm-explorer\n"))
        r, types = types_in(self.root, "--severity", "warning")
        self.assertIn("FORK-INTERVIEW", types, r.stdout)

    def test_fork_delegation_not_flagged_as_interview(self):
        # fork que solo delega con args ("confirmar o inferir") → NO es entrevista
        body = "Paso 1: confirmar con el usuario o inferir del proyecto, y delegar al agente.\n"
        write(self.root / "design" / "skills" / "wf-fork-deleg" / "SKILL.md",
              skill_md("wf-fork-deleg", body,
                       extra_fm="allowed-tools: [Read, Bash]\ncontext: fork\n"
                                "agent: kmm-platform-integrator\n"))
        _, types = types_in(self.root)
        self.assertNotIn("FORK-INTERVIEW", types)

    def test_fork_confirmation_gate_flagged_as_warning(self):
        # fork con GATE DE CONFIRMACION en prosa (sin AskUserQuestion) → warning [[D-016]]
        body = "Paso 3: presenta el plan. Espera confirmacion del usuario antes de instalar.\n"
        write(self.root / "design" / "skills" / "wf-fork-gate" / "SKILL.md",
              skill_md("wf-fork-gate", body,
                       extra_fm="allowed-tools: [Read, Bash]\ncontext: fork\n"))
        r, types = types_in(self.root, "--severity", "warning")
        self.assertIn("FORK-INTERVIEW", types, r.stdout)

    # === Exit codes =======================================================
    def test_exit_0_when_clean(self):
        # Un arbol con una sola skill perfectamente formada -> sin findings
        write(self.root / "spec" / "skills" / "kb-clean" / "SKILL.md",
              skill_md("kb-clean", "Cuerpo limpio."))
        r = lint(self.root, "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_exit_1_when_only_warnings(self):
        write(self.root / "spec" / "skills" / "wf-noui" / "SKILL.md",
              "---\nname: wf-noui\ndescription: un wf.\n---\n\n# wf-noui\n\nCuerpo.\n")
        r = lint(self.root, "--check")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_exit_2_when_blocking(self):
        write(self.root / "spec" / "skills" / "kb-x" / "SKILL.md",
              skill_md("kb-x", "Lee /Users/oscar/x.md como entrada."))
        r = lint(self.root, "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    # === Forma del --json =================================================
    def test_json_shape(self):
        write(self.root / "spec" / "skills" / "kb-x" / "SKILL.md",
              skill_md("kb-x", "Lee /Users/oscar/x.md como entrada."))
        r = lint(self.root, "--json")
        data = json.loads(r.stdout)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        for f in data:
            self.assertEqual(set(f.keys()),
                             {"severity", "type", "file", "line", "message"})
            self.assertIn(f["severity"], ("blocking", "warning"))
            self.assertIsInstance(f["line"], int)

    def test_severity_filter_blocking_only(self):
        # arbol con un blocking (path) y un warning (kb sin user-invocable)
        write(self.root / "spec" / "skills" / "kb-x" / "SKILL.md",
              "---\nname: kb-x\ndescription: una kb.\n---\n\n"
              "# kb-x\n\nLee /Users/oscar/x.md aqui.\n")
        r = lint(self.root, "--json", "--severity", "blocking")
        data = json.loads(r.stdout)
        self.assertTrue(all(f["severity"] == "blocking" for f in data), r.stdout)
        self.assertTrue(any(f["type"] == "ABSOLUTE-PATH" for f in data))


class DefaultScanTest(unittest.TestCase):
    """El escaneo por defecto (sin --root) sigue funcionando sobre el repo real."""

    def test_default_scan_no_blocking(self):
        # El repo sano debe estar en blocking=0 (ver ROADMAP 11.4a).
        r = run_script("sdd-structural-lint.py", "--check", "--severity", "blocking")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)  # 0 blocking pero hay warnings -> exit 1
        self.assertIn("0 blocking", r.stdout)


if __name__ == "__main__":
    unittest.main()
