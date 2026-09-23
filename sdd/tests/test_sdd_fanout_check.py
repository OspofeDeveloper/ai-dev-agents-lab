"""Black-box tests para scripts/sdd-fanout-check.py ([[D-092]]).

El probe mide el contrato de fan-out ([[D-047]], [[D-084]]): las N llamadas `Agent`
de una tanda salen en UN mensaje. Lo que hace difícil el probe no es detectar el
fallo, es **no reportar como fallo** las tres cosas que se le parecen:

- dos delegaciones **secuenciales por contrato** al mismo agente (analyze → discover);
- un **relanzado tras decisión humana** (un `STOP_*` presentado, una tanda cortada);
- las N llamadas de un fan-out bueno, que el transcript parte en **N filas** con el
  mismo `message.id` y hay que volver a juntar.

Los fixtures reproducen la forma real del `.jsonl` de sesión, incluidas esas tres.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402


def agent_row(mid, ts, subagent, skill, feature):
    """Una FILA de asistente con UNA llamada Agent (así lo parte el transcript)."""
    return {
        "type": "assistant",
        "timestamp": ts,
        "message": {
            "id": mid,
            "content": [{
                "type": "tool_use",
                "name": "Agent",
                "input": {
                    "subagent_type": subagent,
                    "prompt": (f"Lee `.claude/skills/{skill}/SKILL.md` y ejecuta sus "
                               f"pasos TÚ MISMO sobre: --feature {feature}"),
                },
            }],
        },
    }


def tool_result_row(ts="2026-09-18T08:56:00.000Z"):
    return {"type": "user", "timestamp": ts,
            "message": {"content": [{"type": "tool_result", "content": "listo"}]}}


def human_row(text, ts="2026-09-18T09:00:00.000Z"):
    return {"type": "user", "timestamp": ts, "message": {"content": text}}


class FanoutCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _session(self, rows, name="s.jsonl"):
        return write(self.dir / name,
                     "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")

    def _run(self, path, *flags):
        return run_script("sdd-fanout-check.py", path, *flags)

    def test_tanda_en_un_unico_mensaje_es_ok(self):
        """Tres filas, un solo `message.id`: es UNA emisión de tamaño 3."""
        p = self._session([
            agent_row("msg-1", "2026-09-18T09:33:52Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-001"),
            agent_row("msg-1", "2026-09-18T09:33:56Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-005"),
            agent_row("msg-1", "2026-09-18T09:33:59Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-008"),
            tool_result_row(),
        ])
        r = self._run(p)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OK", r.stdout)
        self.assertIn("3×", r.stdout)

    def test_la_llamada_de_prueba_es_hallazgo(self):
        """`1 + 1`: la forma que se midió el 2026-09-18 con el contrato delante."""
        p = self._session([
            agent_row("msg-1", "2026-09-18T08:54:34Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-003"),
            tool_result_row(),
            agent_row("msg-2", "2026-09-18T08:58:47Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-004"),
        ])
        r = self._run(p)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("FANOUT_SERIALIZADO", r.stdout)
        self.assertIn("1 + 1", r.stdout)
        self.assertIn("253s", r.stdout, "el hueco es el coste real de la serialización")

    def test_la_forma_1_mas_n_menos_1_tambien(self):
        p = self._session([
            agent_row("msg-1", "2026-09-15T07:00:00Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-001"),
            tool_result_row(),
            agent_row("msg-2", "2026-09-15T07:06:00Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-002"),
            agent_row("msg-2", "2026-09-15T07:06:02Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-003"),
            agent_row("msg-2", "2026-09-15T07:06:04Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-004"),
        ])
        r = self._run(p)
        self.assertEqual(r.returncode, 2)
        self.assertIn("1 + 3", r.stdout)
        self.assertIn("4×", r.stdout)

    def test_dos_delegaciones_secuenciales_al_mismo_agente_no_son_un_fanout(self):
        """analyze → discover: mismo `sdd-spec-explorer`, dos encargos distintos.

        Sin mirar QUÉ skill ejecuta cada uno, el probe reportaría aquí un `1 + 1`
        que es el flujo correcto del contrato.
        """
        p = self._session([
            agent_row("msg-1", "2026-09-18T08:10:00Z", "sdd-spec-explorer",
                      "wf-spec-analyze", "-"),
            tool_result_row(),
            agent_row("msg-2", "2026-09-18T08:20:00Z", "sdd-spec-explorer",
                      "wf-spec-discover", "-"),
        ])
        r = self._run(p)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_relanzar_tras_un_turno_humano_no_es_hallazgo(self):
        """Una tanda cortada y relanzada después de que la persona decida."""
        p = self._session([
            agent_row("msg-1", "2026-09-18T09:40:41Z", "sdd-spec-auditor",
                      "wf-spec-conflict", "F-001"),
            tool_result_row(),
            human_row("Continua"),
            agent_row("msg-2", "2026-09-18T11:10:49Z", "sdd-spec-auditor",
                      "wf-spec-conflict", "F-001"),
        ])
        r = self._run(p)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_una_delegacion_suelta_no_es_una_tanda(self):
        """Un solo delegado no es un fan-out: ni hallazgo ni tanda limpia que contar."""
        p = self._session([
            agent_row("msg-1", "2026-09-18T08:10:00Z", "sdd-spec-auditor",
                      "wf-spec-readiness", "-"),
            tool_result_row(),
        ])
        r = self._run(p)
        self.assertEqual(r.returncode, 0)
        self.assertIn("0 tanda(s)", r.stdout)

    def test_json_lleva_veredicto_y_hallazgos(self):
        p = self._session([
            agent_row("msg-1", "2026-09-18T08:54:34Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-003"),
            tool_result_row(),
            agent_row("msg-2", "2026-09-18T08:58:47Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-004"),
        ])
        r = self._run(p, "--json")
        self.assertEqual(r.returncode, 2)
        data = json.loads(r.stdout)
        self.assertEqual(data["verdict"], "FANOUT_SERIALIZADO")
        self.assertEqual(len(data["findings"]), 1)
        self.assertEqual(data["findings"][0]["forma"], "1 + 1")
        self.assertEqual(data["findings"][0]["skill"], "wf-spec-fast-track")

    def test_un_directorio_resuelve_a_la_sesion_mas_reciente(self):
        self._session([agent_row("msg-1", "2026-09-18T08:10:00Z", "sdd-spec-writer",
                                 "wf-spec-fast-track", "F-001")], name="vieja.jsonl")
        import os
        import time
        nueva = self._session([
            agent_row("msg-9", "2026-09-18T08:54:34Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-003"),
            tool_result_row(),
            agent_row("msg-10", "2026-09-18T08:58:47Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-004"),
        ], name="nueva.jsonl")
        os.utime(nueva, (time.time() + 10, time.time() + 10))
        r = self._run(self.dir)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("nueva.jsonl", r.stdout)

    def test_transcript_inexistente_es_error_de_uso(self):
        r = self._run(self.dir / "no-existe.jsonl")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no hay transcript", r.stderr)

    def test_una_linea_truncada_no_tumba_el_probe(self):
        """El `.jsonl` de una sesión viva puede acabar a medias."""
        p = self.dir / "roto.jsonl"
        rows = [
            agent_row("msg-1", "2026-09-18T08:54:34Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-003"),
            tool_result_row(),
            agent_row("msg-2", "2026-09-18T08:58:47Z", "sdd-spec-writer",
                      "wf-spec-fast-track", "F-004"),
        ]
        text = "\n".join(json.dumps(r) for r in rows) + '\n{"type":"assist'
        write(p, text)
        r = self._run(p)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("1 + 1", r.stdout)


if __name__ == "__main__":
    unittest.main()
