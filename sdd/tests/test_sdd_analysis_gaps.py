"""Black-box tests para scripts/sdd-analysis-gaps.py.

El script da la parte VERIFICABLE del gate de gaps del `_analysis.md` (DECISIONS
D-042): antes, "¿quedan `[CRÍTICO]` sin responder?" lo decidía un agente leyendo
prosa, y de esa lectura cuelgan dos ramas duras de `wf-spec-features-first`.
Verifica:
  - --check: críticos abiertos → CRITICAL_OPEN exit 2, con sus IDs.
  - --check: informativos abiertos NO bloquean (CRITICAL_ANSWERED exit 0).
  - --check: documento sin bloques de gap → VACUOUS exit 2 (guarda de D-037: no
    puede responder "0 abiertos" sobre algo que no ha sabido parsear).
  - --answer: sustituye SOLO la línea Respuesta del gap indicado.
  - --answer sobre gap ya respondido → exit 2 sin tocar el fichero (salvo --force).
  - --answer con ID inexistente → exit 2 listando los IDs válidos.
  - tolerancia a campos extra en el bloque (los informes reales añaden `Problema`).
  - IDs `[D-XXX]` de los delta analysis, no solo `[P-XXX]`.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402

HEAD = (
    "# Análisis SDD: Producto X\n\n"
    "## Puntos pendientes de validación con cliente\n\n"
    "> Las respuestas se escriben en este archivo.\n\n"
    "---\n\n"
)


def gap(gid, severity, answer="_(pendiente)_", extra_flags="", with_problema=False):
    """Bloque de gap en el formato SSoT de kb-gap-conventions."""
    block = f"### [{gid}][{severity}]{extra_flags} Título de {gid}\n\n"
    block += "- **Contexto**: dónde se detectó.\n"
    if with_problema:
        # Campo EXTRA que los informes reales añaden y la plantilla no contempla.
        block += "- **Problema**: por qué bloquea.\n"
    if severity == "CRÍTICO":
        block += "- **Afecta**: HU-001\n"
    block += "- **Pregunta para el cliente**: ¿pregunta concreta?\n"
    block += f"- **Respuesta**: {answer}\n"
    if severity == "INFORMATIVO":
        block += "- **Asunción por defecto**: se aplicará Y.\n"
    return block + "\n---\n\n"


class AnalysisGapsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, *blocks, name="prd_analysis.md"):
        path = self.root / name
        write(path, HEAD + "".join(blocks))
        return path

    def check(self, path, *flags):
        return run_script("sdd-analysis-gaps.py", path, "--check", *flags)

    def check_json(self, path):
        r = self.check(path, "--json")
        return r, json.loads(r.stdout)

    # === --check =========================================================
    def test_critical_open_is_blocking_and_lists_ids(self):
        path = self.make(gap("P-001", "CRÍTICO"),
                         gap("P-002", "CRÍTICO", answer="Sí, se puede."),
                         gap("P-003", "CRÍTICO"))
        r, data = self.check_json(path)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertEqual(data["verdict"], "CRITICAL_OPEN")
        self.assertEqual(data["critical_total"], 3)
        self.assertEqual(data["critical_open"], 2)
        self.assertEqual(data["critical_open_ids"], ["P-001", "P-003"])

    def test_informative_open_does_not_block(self):
        # [INFORMATIVO] nunca bloquea: aplica su asunción por defecto.
        path = self.make(gap("P-001", "CRÍTICO", answer="Respondido."),
                         gap("P-002", "INFORMATIVO"))
        r, data = self.check_json(path)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(data["verdict"], "CRITICAL_ANSWERED")
        self.assertEqual(data["informative_open"], 1)
        self.assertEqual(data["informative_open_ids"], ["P-002"])

    def test_vacuous_when_no_gap_blocks(self):
        # Guarda de D-037: sin bloques parseados NO se responde "0 abiertos".
        path = self.root / "prd.md"
        write(path, "# PRD\n\n## Alcance\n\n- El usuario puede registrar un gasto.\n")
        r, data = self.check_json(path)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertEqual(data["verdict"], "VACUOUS")

    def test_check_tolerates_extra_fields_and_flags(self):
        path = self.make(gap("P-001", "CRÍTICO", extra_flags="[PUEDE_REQUERIR_CR]",
                             with_problema=True))
        r, data = self.check_json(path)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(data["critical_open_ids"], ["P-001"])
        self.assertIn("PUEDE_REQUERIR_CR", data["gaps"][0]["flags"])

    def test_check_accepts_delta_analysis_ids(self):
        path = self.make(gap("D-001", "CRÍTICO"), name="feature_delta_analysis.md")
        r, data = self.check_json(path)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(data["critical_open_ids"], ["D-001"])

    # === --answer ========================================================
    def test_answer_replaces_only_that_line(self):
        path = self.make(gap("P-001", "CRÍTICO"), gap("P-002", "CRÍTICO"))
        before = path.read_text(encoding="utf-8")
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-001",
                       "No, solo ingresos y gastos.", "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        after = path.read_text(encoding="utf-8")
        changed = [(a, b) for a, b in zip(before.splitlines(), after.splitlines()) if a != b]
        self.assertEqual(len(changed), 1, f"cambió más de una línea: {changed}")
        self.assertIn("- **Respuesta**: No, solo ingresos y gastos.", after)
        data = json.loads(r.stdout)
        self.assertEqual(data["critical_open_ids"], ["P-002"])
        self.assertFalse(data["overwritten"])

    def test_answer_normalizes_whitespace_to_one_line(self):
        path = self.make(gap("P-001", "CRÍTICO"))
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-001",
                       "primera línea\nsegunda   línea")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("- **Respuesta**: primera línea segunda línea",
                      path.read_text(encoding="utf-8"))

    def test_answer_refuses_to_overwrite_without_force(self):
        path = self.make(gap("P-001", "CRÍTICO", answer="Respuesta humana previa."))
        before = path.read_text(encoding="utf-8")
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-001", "otra cosa")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--force", r.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), before, "escribió pese al fallo")

    def test_answer_overwrites_with_force(self):
        path = self.make(gap("P-001", "CRÍTICO", answer="Respuesta humana previa."))
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-001", "corregida",
                       "--force", "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(json.loads(r.stdout)["overwritten"])
        self.assertIn("- **Respuesta**: corregida", path.read_text(encoding="utf-8"))

    def test_answer_unknown_id_lists_valid_ones(self):
        path = self.make(gap("P-001", "CRÍTICO"), gap("P-002", "INFORMATIVO"))
        before = path.read_text(encoding="utf-8")
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-099", "x")
        self.assertEqual(r.returncode, 2)
        self.assertIn("P-001", r.stderr)
        self.assertIn("P-002", r.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_answer_on_document_without_gaps_fails(self):
        path = self.root / "prd.md"
        write(path, "# PRD\n\nSin gaps.\n")
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-001", "x")
        self.assertEqual(r.returncode, 2)

    def test_answer_empty_is_usage_error(self):
        path = self.make(gap("P-001", "CRÍTICO"))
        r = run_script("sdd-analysis-gaps.py", path, "--answer", "P-001", "   ")
        self.assertEqual(r.returncode, 1)

    # === --list (D-052) ===================================================
    # El gate tiene que decir QUE se pregunta en cada gap, y en una sesion que
    # retoma el trabajo main no tiene el informe del delegado en contexto. Sin
    # esta via, la unica forma de saberlo seria abrir el artefacto.
    def test_list_emits_the_question_of_each_gap(self):
        path = self.make(gap("P-001", "CRÍTICO"),
                         gap("P-002", "INFORMATIVO", answer="Ya resuelto."))
        r = run_script("sdd-analysis-gaps.py", path, "--list", "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data["total"], 2)
        self.assertEqual([g["id"] for g in data["gaps"]], ["P-001", "P-002"])
        self.assertIn("pregunta concreta", data["gaps"][0]["question"])
        self.assertFalse(data["gaps"][0]["answered"])
        self.assertTrue(data["gaps"][1]["answered"])

    def test_list_carries_the_flags_that_drive_the_routing(self):
        # `PUEDE_REQUERIR_CR` es el disparador con el que el orquestador decide
        # si delegar la evaluacion de gobernanza, sin leer ninguna respuesta.
        path = self.make(gap("P-001", "CRÍTICO", extra_flags="[PUEDE_REQUERIR_CR]"))
        r = run_script("sdd-analysis-gaps.py", path, "--list", "--json")
        data = json.loads(r.stdout)
        self.assertIn("PUEDE_REQUERIR_CR", data["gaps"][0]["flags"])

    def test_list_does_not_leak_the_answer_text(self):
        # --list es metadatos. El texto de las respuestas se saca con
        # --export-answers, que es otra cosa y tiene otro proposito.
        path = self.make(gap("P-001", "CRÍTICO", answer="Secreto de negocio."))
        r = run_script("sdd-analysis-gaps.py", path, "--list", "--json")
        self.assertNotIn("Secreto de negocio", r.stdout)

    def test_list_emits_the_context_fields_of_each_gap(self):
        # D-053: la pregunta pelada no basta. `Contexto`, `Problema` y `Afecta` son
        # los campos que le dicen al usuario POR QUE importa y CUANTO detalle hace
        # falta; sin ellos main tendria que abrir el fichero, que la Regla de oro
        # de wf-spec-features-first le prohibe.
        path = self.make(gap("P-001", "CRÍTICO", with_problema=True))
        r = run_script("sdd-analysis-gaps.py", path, "--list", "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        g = json.loads(r.stdout)["gaps"][0]
        self.assertIn("dónde se detectó", g["contexto"])
        self.assertIn("por qué bloquea", g["problema"])
        self.assertIn("HU-001", g["afecta"])

    def test_list_field_missing_is_none_not_an_error(self):
        # Los informes reales no siempre traen `Problema` (los INFORMATIVO del
        # fichero medido no lo llevan). Ausencia != malformado.
        path = self.make(gap("P-002", "INFORMATIVO"))
        r = run_script("sdd-analysis-gaps.py", path, "--list", "--json")
        self.assertEqual(r.returncode, 0)
        g = json.loads(r.stdout)["gaps"][0]
        self.assertIsNone(g["problema"])
        self.assertIsNotNone(g["question"])

    def test_list_joins_a_field_that_continues_on_the_next_line(self):
        # Un `Contexto` largo puede seguir en la linea siguiente. Se entrega
        # entero: es texto que se le ENSENA al usuario, no un resumen.
        block = ("### [P-001][CRÍTICO] Título\n\n"
                 "- **Contexto**: primera parte\n"
                 "  y la continuación de la frase.\n"
                 "- **Pregunta para el cliente**: ¿pregunta concreta?\n"
                 "- **Respuesta**: _(pendiente)_\n\n---\n\n")
        path = self.make(block)
        r = run_script("sdd-analysis-gaps.py", path, "--list", "--json")
        g = json.loads(r.stdout)["gaps"][0]
        self.assertEqual(g["contexto"], "primera parte y la continuación de la frase.")

    def test_list_gap_filters_to_one(self):
        # D-053: los gaps se presentan de UNO EN UNO, asi que main pide uno cada
        # vez. Traer los 7 de golpe le metaria en contexto medio artefacto, que es
        # justo lo que la Regla de oro de wf-spec-features-first evita.
        path = self.make(gap("P-001", "CRÍTICO", with_problema=True),
                         gap("P-002", "CRÍTICO"),
                         gap("P-003", "INFORMATIVO"))
        r = run_script("sdd-analysis-gaps.py", path, "--list", "--gap", "P-002", "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual([g["id"] for g in data["gaps"]], ["P-002"])
        self.assertNotIn("P-001", r.stdout)

    def test_list_gap_with_unknown_id_lists_the_valid_ones(self):
        # Mismo trato que --answer con un ID inexistente: error accionable, no
        # traceback. Se cazo al estrenarlo: el GapError escapaba sin capturar.
        path = self.make(gap("P-001", "CRÍTICO"))
        r = run_script("sdd-analysis-gaps.py", path, "--list", "--gap", "P-099")
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stdout + r.stderr)
        self.assertIn("P-001", r.stderr)

    def test_list_on_document_without_gaps_is_empty_not_an_error(self):
        # A diferencia de --check, listar cero gaps no es un veredicto: no bloquea.
        path = self.root / "vacio.md"
        write(path, "# Sin bloques de gap\n")
        r = run_script("sdd-analysis-gaps.py", path, "--list", "--json")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout)["total"], 0)

    def test_list_is_exclusive_with_other_modes(self):
        path = self.make(gap("P-001", "CRÍTICO"))
        r = run_script("sdd-analysis-gaps.py", path, "--list", "--check")
        self.assertEqual(r.returncode, 1)

    # === --export-answers / --import-answers (D-051) =====================
    # Regenerar un `_analysis.md` lo SOBRESCRIBE y se lleva por delante las
    # respuestas ya dadas. El emparejamiento es por ID **y** título porque el
    # análisis no es reproducible: el mismo P-XXX puede ser otra pregunta.
    @staticmethod
    def _gap_titled(gid, title, answer="_(pendiente)_", severity="CRÍTICO"):
        return (f"### [{gid}][{severity}] {title}\n\n"
                "- **Contexto**: dónde se detectó.\n"
                f"- **Respuesta**: {answer}\n\n---\n\n")

    def _export(self, path):
        r = run_script("sdd-analysis-gaps.py", path, "--export-answers")
        return r, json.loads(r.stdout)

    def test_export_answers_only_takes_the_answered_ones(self):
        path = self.make(gap("P-001", "CRÍTICO", answer="Sí, se descuenta."),
                         gap("P-002", "CRÍTICO"),
                         gap("P-003", "INFORMATIVO", answer="Reduce el pendiente."))
        r, data = self._export(path)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(data["exported"], 2)
        self.assertEqual([a["id"] for a in data["answers"]], ["P-001", "P-003"])
        self.assertEqual(data["answers"][0]["answer"], "Sí, se descuenta.")

    def test_import_returns_the_answer_when_id_and_title_match(self):
        src = self.make(self._gap_titled("P-001", "Deuda y saldo", "Sí, se descuenta."),
                        name="viejo.md")
        dst = self.make(self._gap_titled("P-001", "Deuda y saldo"), name="nuevo.md")
        payload = self.root / "ans.json"
        write(payload, json.dumps(self._export(src)[1]))
        r = run_script("sdd-analysis-gaps.py", dst, "--import-answers", payload)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Sí, se descuenta.", dst.read_text(encoding="utf-8"))

    def test_import_refuses_when_the_same_id_is_another_question(self):
        # EL caso que justifica la regla: el ID coincide, la pregunta no.
        # Escribir aquí metería una respuesta de negocio en el gap equivocado.
        src = self.make(self._gap_titled("P-002", "Presupuesto por categoría",
                                         "Es la suma."), name="viejo.md")
        dst = self.make(self._gap_titled("P-002", "Traspaso de reserva"), name="nuevo.md")
        payload = self.root / "ans.json"
        write(payload, json.dumps(self._export(src)[1]))
        r = run_script("sdd-analysis-gaps.py", dst, "--import-answers", payload, "--json")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data["applied"], 0)
        self.assertEqual(data["needs_review"][0]["reason"], "titulo_distinto")
        self.assertIn("_(pendiente)_", dst.read_text(encoding="utf-8"))

    def test_import_reports_a_gap_that_no_longer_exists(self):
        src = self.make(self._gap_titled("P-009", "Gap que desapareció", "Respondido."),
                        name="viejo.md")
        dst = self.make(self._gap_titled("P-001", "Otro gap"), name="nuevo.md")
        payload = self.root / "ans.json"
        write(payload, json.dumps(self._export(src)[1]))
        r = run_script("sdd-analysis-gaps.py", dst, "--import-answers", payload, "--json")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertEqual(json.loads(r.stdout)["needs_review"][0]["reason"], "id_ausente")

    def test_import_does_not_silently_overwrite_an_existing_answer(self):
        src = self.make(self._gap_titled("P-001", "Deuda y saldo", "Respuesta vieja."),
                        name="viejo.md")
        dst = self.make(self._gap_titled("P-001", "Deuda y saldo", "Respuesta nueva."),
                        name="nuevo.md")
        payload = self.root / "ans.json"
        write(payload, json.dumps(self._export(src)[1]))
        r = run_script("sdd-analysis-gaps.py", dst, "--import-answers", payload, "--json")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertEqual(json.loads(r.stdout)["needs_review"][0]["reason"], "ya_respondido")
        self.assertIn("Respuesta nueva.", dst.read_text(encoding="utf-8"))

    def test_import_round_trip_is_idempotent(self):
        src = self.make(self._gap_titled("P-001", "Deuda y saldo", "Sí, se descuenta."),
                        name="viejo.md")
        dst = self.make(self._gap_titled("P-001", "Deuda y saldo"), name="nuevo.md")
        payload = self.root / "ans.json"
        write(payload, json.dumps(self._export(src)[1]))
        run_script("sdd-analysis-gaps.py", dst, "--import-answers", payload)
        first = dst.read_text(encoding="utf-8")
        # Segunda pasada: la respuesta ya está, así que sale por needs_review
        # (ya_respondido) y el documento NO cambia.
        r = run_script("sdd-analysis-gaps.py", dst, "--import-answers", payload)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(dst.read_text(encoding="utf-8"), first)

    def test_import_into_a_document_without_gaps_is_an_error(self):
        # Guarda de D-037: no se declara "0 aplicadas, todo bien" sobre algo
        # que no se ha sabido parsear.
        src = self.make(self._gap_titled("P-001", "Deuda", "Sí."), name="viejo.md")
        dst = self.root / "vacio.md"
        write(dst, "# Documento sin bloques de gap\n")
        payload = self.root / "ans.json"
        write(payload, json.dumps(self._export(src)[1]))
        r = run_script("sdd-analysis-gaps.py", dst, "--import-answers", payload)
        self.assertEqual(r.returncode, 2)
        self.assertIn("ERROR", r.stderr)

    def test_export_and_import_are_exclusive_modes(self):
        path = self.make(gap("P-001", "CRÍTICO"))
        r = run_script("sdd-analysis-gaps.py", path, "--export-answers", "--check")
        self.assertEqual(r.returncode, 1)

    # === CLI =============================================================
    def test_check_and_answer_are_exclusive(self):
        path = self.make(gap("P-001", "CRÍTICO"))
        r = run_script("sdd-analysis-gaps.py", path, "--check", "--answer", "P-001", "x")
        self.assertEqual(r.returncode, 1)

    def test_no_mode_is_usage_error(self):
        path = self.make(gap("P-001", "CRÍTICO"))
        r = run_script("sdd-analysis-gaps.py", path)
        self.assertEqual(r.returncode, 1)

    def test_missing_file_is_io_error(self):
        r = run_script("sdd-analysis-gaps.py", self.root / "no-existe.md", "--check")
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
