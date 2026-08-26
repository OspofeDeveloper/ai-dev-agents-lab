"""Black-box tests para scripts/sdd-agent-sync.py.

El hook PreToolUse (matcher: Agent) que hace mecanica la sincronia de la
delegacion a agentes SDD (D-048). Contrato:

  - deniega si el subagent_type es del ecosistema y falta `run_in_background: false`
  - permite si el flag esta puesto a false
  - NO toca agentes que no son del ecosistema (general-purpose, Explore, propios)
  - politica conservadora: cualquier entrada rara -> permitir, exit 0
  - nunca bloquea por un error interno propio
  - `SDD_ALLOW_ASYNC_AGENTS=1` lo desactiva entero

Un hook que deniegue de mas deja el repo del usuario inoperable, asi que la
mitad de estos casos verifican que NO dispara.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script  # noqa: E402


def payload(agent, tool_name="Agent", **extra):
    tool_input = {"prompt": "haz cosas", "description": "x"}
    if agent is not None:
        tool_input["subagent_type"] = agent
    tool_input.update(extra)
    return json.dumps({"tool_name": tool_name, "tool_input": tool_input})


class AgentSyncTest(unittest.TestCase):
    def _run(self, stdin, env=None):
        return run_script("sdd-agent-sync.py", stdin=stdin, env=env)

    def _decision(self, r):
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        if not r.stdout.strip():
            return None
        return json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"]

    # ── Deniega: evidencia positiva ───────────────────────────────────────

    def test_denies_sdd_agent_without_flag(self):
        r = self._run(payload("sdd-spec-explorer"))
        self.assertEqual(self._decision(r), "deny")

    def test_denies_when_flag_is_true(self):
        r = self._run(payload("sdd-spec-writer", run_in_background=True))
        self.assertEqual(self._decision(r), "deny")

    def test_deny_reason_is_actionable(self):
        # El motivo se lo come el modelo: tiene que decirle QUE hacer, no solo
        # que ha hecho mal. Sin la salida explicita, un agente entre "prohibido"
        # y "necesito el resultado" improvisa (leccion de D-045).
        r = self._run(payload("prd-expert"))
        reason = json.loads(r.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("run_in_background: false", reason)
        self.assertIn("prd-expert", reason)
        self.assertIn("mismos", reason, "no dice que reintente la MISMA llamada")
        self.assertIn("un unico mensaje", reason, "no recuerda la barrera del fan-out")
        self.assertIn("No cambies de estrategia", reason,
                      "no cierra la puerta a improvisar otra via")

    def test_denies_every_known_sdd_agent(self):
        # Si un agente del ecosistema se queda fuera de la lista, su delegacion
        # sigue siendo asincrona en silencio — que es el bug original.
        for agent in ("sdd-spec-auditor", "sdd-spec-planner", "task-generator",
                      "plan-architect", "plan-auditor", "qa-engineer",
                      "design-system-architect", "design-feature-architect",
                      "sdd-author", "sdd-auditor", "sdd-conformance",
                      "kmm-explorer", "kmm-planner", "kmm-tester"):
            with self.subTest(agent=agent):
                self.assertEqual(self._decision(self._run(payload(agent))), "deny")

    # ── Permite: todo lo demas ────────────────────────────────────────────

    def test_allows_when_flag_is_false(self):
        r = self._run(payload("sdd-spec-explorer", run_in_background=False))
        self.assertIsNone(self._decision(r))

    def test_ignores_non_sdd_agents(self):
        # El ecosistema se instala en repos ajenos: no le toca forzarle el modo
        # de ejecucion a los agentes del usuario ni a los del harness (D-045,
        # mismo motivo por el que se descarto DISABLE_BACKGROUND_TASKS).
        for agent in ("general-purpose", "Explore", "Plan", "claude",
                      "mi-agente-propio"):
            with self.subTest(agent=agent):
                self.assertIsNone(self._decision(self._run(payload(agent))))

    def test_ignores_other_tools(self):
        r = self._run(payload("sdd-spec-explorer", tool_name="Skill"))
        self.assertIsNone(self._decision(r))

    def test_missing_subagent_type_allows(self):
        r = self._run(payload(None))
        self.assertIsNone(self._decision(r))

    def test_unreadable_stdin_allows(self):
        r = self._run("no soy json {{{")
        self.assertIsNone(self._decision(r))

    def test_empty_stdin_allows(self):
        r = self._run("")
        self.assertIsNone(self._decision(r))

    def test_malformed_tool_input_allows(self):
        r = self._run(json.dumps({"tool_name": "Agent", "tool_input": "no soy un dict"}))
        self.assertIsNone(self._decision(r))

    def test_null_tool_input_allows(self):
        r = self._run(json.dumps({"tool_name": "Agent", "tool_input": None}))
        self.assertIsNone(self._decision(r))

    def test_non_string_subagent_type_allows(self):
        r = self._run(json.dumps({"tool_name": "Agent",
                                  "tool_input": {"subagent_type": 42}}))
        self.assertIsNone(self._decision(r))

    def test_subagent_type_is_trimmed(self):
        r = self._run(payload("  sdd-spec-explorer  "))
        self.assertEqual(self._decision(r), "deny")

    # ── Escotilla ─────────────────────────────────────────────────────────

    def test_env_escape_hatch_disables_the_gate(self):
        # Un gate que no se puede apagar puede dejar un repo inoperable si el
        # harness deja de aceptar el parametro: denegaria en bucle sin salida.
        r = self._run(payload("sdd-spec-explorer"),
                      env={"SDD_ALLOW_ASYNC_AGENTS": "1"})
        self.assertIsNone(self._decision(r))

    def test_escape_hatch_only_with_exact_value(self):
        r = self._run(payload("sdd-spec-explorer"),
                      env={"SDD_ALLOW_ASYNC_AGENTS": "true"})
        self.assertEqual(self._decision(r), "deny")

    # ── Nunca revienta ────────────────────────────────────────────────────

    def test_always_exits_zero(self):
        for stdin in ("", "{}", "basura", json.dumps({"tool_name": "Agent"}),
                      payload("sdd-spec-explorer")):
            with self.subTest(stdin=stdin[:20]):
                self.assertEqual(self._run(stdin).returncode, 0)

    def test_never_writes_to_stderr(self):
        # stderr de un hook ensucia la sesion del usuario.
        for stdin in ("basura", payload("sdd-spec-explorer"), payload("general-purpose")):
            with self.subTest(stdin=stdin[:20]):
                self.assertEqual(self._run(stdin).stderr, "")


if __name__ == "__main__":
    unittest.main()
