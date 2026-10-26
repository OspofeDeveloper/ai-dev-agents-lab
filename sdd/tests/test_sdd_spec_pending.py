"""Black-box tests para `sdd-project-status.py --spec-pending` (D-102).

La lista de pendientes de la fase Spec es la que el hilo principal ofrece al cerrar
cada flujo. Tiene que salir SOLO de ficheros y en un orden fijo, porque lo que no
sale de ficheros se degrada en la segunda tanda (D-097/D-099). Cubre cada tipo de
pendiente, el orden, el readiness desactualizado, la aceptación del alcance
derivado, la respuesta reabierta y la lista vacía. Incluye también las dos piezas
que la alimentan: la condición 9 de `sdd-seal.py spec` y la marca `Reabierto:` de
`sdd-analysis-gaps.py`.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402

ANALYSIS = """\
# Análisis

### [P-001][CRÍTICO] Saldar una deuda
- **Contexto**: x
- **Respuesta**: {p1}

### [P-002][INFORMATIVO] Editar un movimiento
- **Contexto**: x
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: se puede editar todo
"""


def index(features, shared=()):
    """features: [(fid, name, ruta|None, estado, avisos)]; shared: [(modelo, owner, refs)]"""
    out = ["# Features Index: Prj",
           "> Discovery: `../prd/prj_discovery.md` (fuera de esta raíz de artefactos)", "",
           "## Features", ""]
    for fid, name, ruta, estado, avisos in features:
        out += [f"### {fid}: {name}",
                f"- **Ruta spec**: {ruta or '(pendiente de generación)'}",
                f"- **Estado**: {estado}",
                f"- **Origen de alcance**: {'PRD + analysis respondido' if avisos != 'ninguno' else 'PRD'}",
                f"- **Avisos de gobernanza**: {avisos}", ""]
    if shared:
        out += ["## Tabla de shared models", "",
                "| Modelo | Feature Owner | Features que lo referencian |", "|---|---|---|"]
        out += [f"| {m} | {o}: x | {refs} |" for m, o, refs in shared] + [""]
    return "\n".join(out) + "\n"


def spec(fid, estado="BORRADOR", avisos="ninguno", extra_header="", body=""):
    return (f"# Spec: {fid}\n\n> Feature ID: {fid}\n> Estado: {estado}\n"
            f"> Origen de alcance: {'PRD' if avisos == 'ninguno' else 'PRD + analysis respondido'}\n"
            f"> Avisos de gobernanza: {avisos}\n{extra_header}\n"
            f"### HU-001: hu\n\n### CA-001: ca ← HU-001\n{body}")


def readme(fid, requiere="Ninguna"):
    return (f"# {fid}\n\n> **Feature ID**: {fid}\n\n## Dependencias\n\n"
            f"- **Requiere**: {requiere}\n- **Bloquea**: Ninguna\n")


class Bank:
    def __init__(self, root: Path):
        self.root = root
        self.spec = root / "spec"
        self.prd = root / "prd"

    def feature(self, fid, name, estado="BORRADOR", avisos="ninguno", requiere="Ninguna",
                extra_header="", body=""):
        write(self.spec / "features" / name / "spec" / f"{name}_spec.md",
              spec(fid, estado, avisos, extra_header, body))
        write(self.spec / "features" / name / "README.md", readme(fid, requiere))

    def index(self, features, shared=()):
        write(self.spec / "spec_features.md", index(features, shared))

    def analysis(self, p1="_(pendiente)_"):
        write(self.prd / "prj_analysis.md", ANALYSIS.format(p1=p1))

    def readiness(self, matrix_rows="", alta_rows="", media_rows=None):
        text = ["# Readiness Report: Prj", "", "## Matriz de readiness", "",
                "| Feature | Estado | HUs [INCOMPLETO] | Conflictos ALTA | Bloqueantes |",
                "|---|---|:-:|:-:|---|", matrix_rows, "", "---", "",
                "## Conflictos ALTA no resueltos", "",
                "| ID | Tipo | Features afectadas | Descripcion breve | Referencia |",
                "|----|------|-------------------|-------------------|------------|",
                alta_rows, "", "---", ""]
        if media_rows is not None:
            text += ["## Conflictos MEDIA abiertos", "",
                     "| ID | Tipo | Features afectadas | Descripcion breve | Referencia |",
                     "|----|------|-------------------|-------------------|------------|",
                     media_rows, "", "---", ""]
        write(self.spec / "spec_readiness_report.md", "\n".join(text) + "\n")

    def pending(self):
        r = run_script("sdd-project-status.py", self.spec, "--spec-pending", "--json")
        assert r.returncode == 0, r.stdout + r.stderr
        return json.loads(r.stdout)


def tipos(data):
    return [i["tipo"] for i in data["items"]]


class SpecPendingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.b = Bank(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def _base(self, readiness=True, **kw):
        b = self.b
        b.feature("F-001", "movimientos", requiere="F-002")
        b.feature("F-002", "cuentas", requiere="F-001")
        b.index([("F-001", "movimientos", "features/movimientos/spec/movimientos_spec.md",
                  "BLOQUEADA", "ninguno"),
                 ("F-002", "cuentas", "features/cuentas/spec/cuentas_spec.md", "BLOQUEADA",
                  "ninguno"),
                 ("F-003", "deudas", None, "PENDIENTE_GENERACIÓN", "alcance derivado desde P-001")])
        b.analysis(kw.get("p1", "_(pendiente)_"))
        if readiness:
            time.sleep(0.01)
            b.readiness(
                "| F-001: movimientos | BLOQUEADA | 0 | 1 | conflicto |\n"
                "| F-002: cuentas | BLOQUEADA | 0 | 1 | conflicto |",
                "| CF-F001-01 | HU duplicada | F-001, F-002 | misma operación | x |",
                kw.get("media"))

    def test_orden_completo(self):
        self._base(media="| CF-F002-01 | Scope overlap | F-001, F-002 | vista | x |")
        data = self.b.pending()
        self.assertEqual(tipos(data), ["gap_critico", "conflicto_alta", "ciclo", "validar",
                                       "conflicto_media", "generar"])
        self.assertEqual([i["orden"] for i in data["items"]], list(range(1, 7)))
        self.assertTrue(data["readiness_vigente"])

    def test_conflicto_ofrece_las_dos_features(self):
        self._base()
        alta = next(i for i in self.b.pending()["items"] if i["tipo"] == "conflicto_alta")
        self.assertEqual(alta["opciones"], ["F-001", "F-002"])
        self.assertTrue(alta["bloquea_plan"])

    def test_ciclo_desde_los_readmes(self):
        self._base()
        ciclo = next(i for i in self.b.pending()["items"] if i["tipo"] == "ciclo")
        self.assertEqual(ciclo["features"], ["F-001", "F-002"])

    def test_ciclo_sin_respaldo_nombra_la_dependencia_y_no_inventa_flechas(self):
        """Sin tabla de shared models, ninguna arista está respaldada: bloquea y las nombra."""
        self._base()
        ciclo = next(i for i in self.b.pending()["items"] if i["tipo"] == "ciclo")
        self.assertTrue(ciclo["bloquea_plan"])
        self.assertEqual(sorted(ciclo["opciones"]), ["F-001 → F-002", "F-002 → F-001"])
        self.assertIn("Dependencia circular entre", ciclo["que"])

    def _tres_en_ciclo(self, shared):
        """F-001 → F-002 → F-003 → F-001; ninguna arista F-002 → F-003 inventada."""
        b = self.b
        b.feature("F-001", "movimientos", requiere="F-002")
        b.feature("F-002", "cuentas", requiere="F-001, F-003")
        b.feature("F-003", "objetivos", requiere="F-001")
        rows = [(f, n, f"features/{n}/spec/{n}_spec.md", "BLOQUEADA", "ninguno")
                for f, n in (("F-001", "movimientos"), ("F-002", "cuentas"),
                             ("F-003", "objetivos"))]
        b.index(rows, shared)
        b.analysis("respondida")
        time.sleep(0.01)
        b.readiness("", "", "")
        return b.pending()

    def test_ciclo_respaldado_por_modelos_es_un_grupo_y_no_bloquea(self):
        data = self._tres_en_ciclo([("Movimiento", "F-001", "F-002, F-003"),
                                    ("Cuenta", "F-002", "F-001"),
                                    ("Objetivo", "F-003", "F-002")])
        self.assertNotIn("ciclo", tipos(data))
        self.assertEqual([g["features"] for g in data["grupos"]], [["F-001", "F-002", "F-003"]])
        validar = next(i for i in data["items"] if i["tipo"] == "validar")
        self.assertEqual(validar["features"], ["F-001", "F-002", "F-003"])
        r = run_script("sdd-project-status.py", self.b.spec, "--spec-pending")
        self.assertIn("usan datos unas de otras", r.stdout)
        nota = next(l for l in r.stdout.splitlines() if "usan datos unas de otras" in l)
        self.assertNotIn("→", nota)

    def test_ciclo_con_una_arista_suelta_bloquea_solo_por_esa(self):
        data = self._tres_en_ciclo([("Movimiento", "F-001", "F-002, F-003"),
                                    ("Cuenta", "F-002", "F-001")])
        ciclo = next(i for i in data["items"] if i["tipo"] == "ciclo")
        self.assertEqual(ciclo["opciones"], ["F-002 → F-003"])
        self.assertEqual(data["grupos"], [])

    def test_validar_separa_los_que_esperan_a_un_pendiente_anterior(self):
        self._base()
        self.b.feature("F-004", "categorias")
        idx = self.b.spec / "spec_features.md"
        idx.write_text(idx.read_text() + "### F-004: categorias\n"
                       "- **Ruta spec**: features/categorias/spec/categorias_spec.md\n"
                       "- **Estado**: BLOQUEADA\n- **Avisos de gobernanza**: ninguno\n")
        os.utime(self.b.spec / "spec_readiness_report.md")
        validar = next(i for i in self.b.pending()["items"] if i["tipo"] == "validar")
        self.assertEqual(validar["features"], ["F-004"])
        self.assertEqual([e["feature"] for e in validar["en_espera"]], ["F-001", "F-002"])
        self.assertIn("conflicto CF-F001-01", validar["en_espera"][0]["motivo"])

    def test_el_mismo_hallazgo_visto_desde_el_otro_lado_sale_una_vez(self):
        self._base(readiness=False)
        time.sleep(0.01)
        self.b.readiness(alta_rows="| CF-F001-01 | Modelo | F-001, F-002 | El saldo cambia | x |\n"
                                   "| CF-F002-01 | Modelo | F-001, F-002 | Mismo hallazgo que "
                                   "CF-F001-01, visto desde el otro lado | x |")
        altas = [i["conflicto"] for i in self.b.pending()["items"] if i["tipo"] == "conflicto_alta"]
        self.assertEqual(altas, ["CF-F001-01"])

    def test_resumen_trae_el_total_y_el_aviso_del_grupo(self):
        data = self._tres_en_ciclo([("Movimiento", "F-001", "F-002, F-003"),
                                    ("Cuenta", "F-002", "F-001"),
                                    ("Objetivo", "F-003", "F-002")])
        self.assertTrue(data["resumen"].startswith("Para poder planificar falta: "))
        self.assertIn("no frena a ninguna", data["resumen"])

    def test_resumen_dice_que_es_cada_pendiente_y_aparte_lo_que_no_bloquea(self):
        """Un total suelto ("Quedan 6 pendientes") se lee como specs: se dice por tipo (D-110)."""
        self._base()
        self.b.feature("F-004", "categorias")
        idx = self.b.spec / "spec_features.md"
        idx.write_text(idx.read_text() + "### F-009: pagos\n- **Estado**: PENDIENTE\n")
        data = self.b.pending()
        self.assertNotIn("Quedan", data["resumen"])
        self.assertIn("validar ", data["resumen"])
        self.assertIn("Además, sin bloquear: 2 features sin spec.", data["resumen"])

    def test_informe_de_conflictos_anterior_a_su_spec_pide_rehacerlos(self):
        """Un spec corregido tras su informe: primero sus conflictos, luego el readiness (D-104)."""
        self._base()
        rep = self.b.spec / "features" / "cuentas" / "spec" / "cuentas_conflict_report.md"
        write(rep, "## Resumen de conflictos\n")
        past = time.time() - 120
        os.utime(rep, (past, past))
        os.utime(self.b.spec / "spec_readiness_report.md", (past + 10, past + 10))
        ready = self.b.pending()["items"][0]
        self.assertEqual(ready["tipo"], "readiness")
        self.assertEqual(ready["conflictos"], ["F-002"])
        self.assertIn("conflictos de F-002", ready["accion"])

    def _reabrir(self, spec_body="", header=""):
        b = self.b
        b.feature("F-001", "deudas-y-reembolsos", extra_header=header, body=spec_body)
        b.index([("F-001", "deudas-y-reembolsos",
                  "features/deudas-y-reembolsos/spec/deudas-y-reembolsos_spec.md",
                  "BLOQUEADA", "ninguno")])
        write(b.prd / "prj_analysis.md",
              "# Análisis\n\n### [P-002][CRÍTICO] Saldar una deuda\n"
              "- **Afecta**: deudas y reembolsos entre amigos\n"
              "- **Respuesta**: entra en la cuenta que diga el usuario\n")
        past = time.time() - 3600
        os.utime(b.spec / "features" / "deudas-y-reembolsos" / "spec" /
                 "deudas-y-reembolsos_spec.md", (past, past))
        r = run_script("sdd-analysis-gaps.py", b.prd / "prj_analysis.md",
                       "--answer", "P-002", "entra en la cuenta del gasto", "--force")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return [i for i in b.pending()["items"] if i["tipo"] == "reabierto"]

    def test_reabrir_alcanza_un_spec_que_aplica_la_respuesta_sin_citarla(self):
        """El caso de F-005: la respuesta aplicada sin `[P-002]`; lo encuentra por `Afecta`."""
        reab = self._reabrir()
        self.assertEqual(reab[0]["features"], ["F-001"])

    def test_reabrir_usa_la_cabecera_de_respuestas_aplicadas(self):
        b = self.b
        b.feature("F-009", "otra", extra_header="> Respuestas del análisis aplicadas: P-002\n")
        reab = self._reabrir()
        idx = b.spec / "spec_features.md"
        idx.write_text(idx.read_text() + "### F-009: otra\n"
                       "- **Ruta spec**: features/otra/spec/otra_spec.md\n"
                       "- **Estado**: BLOQUEADA\n- **Avisos de gobernanza**: ninguno\n")
        past = time.time() - 3600
        os.utime(b.spec / "features" / "otra" / "spec" / "otra_spec.md", (past, past))
        reab = [i for i in b.pending()["items"] if i["tipo"] == "reabierto"]
        self.assertEqual(reab[0]["features"], ["F-001", "F-009"])

    def test_preguntas_criticas_traen_el_mapa_para_elegir_como_tratarlas(self):
        """Varias preguntas críticas: ID, feature, título y fichero de cada una (D-106)."""
        self._base()
        self.b.feature("F-002", "cuentas", requiere="F-001",
                       body="\n## Items Pendientes\n\n### [P-021][CRÍTICO] Saldo negativo\n"
                            "- **Respuesta**: _(pendiente)_\n")
        os.utime(self.b.spec / "spec_readiness_report.md")
        mapa = self.b.pending()["preguntas_criticas"]
        self.assertEqual([(q["gap"], q["features"]) for q in mapa],
                         [("P-001", []), ("P-021", ["F-002"])])
        self.assertEqual(mapa[1]["titulo"], "Saldo negativo")
        self.assertTrue(mapa[1]["fichero"].endswith("cuentas_spec.md"))
        self.assertTrue(mapa[0]["fichero"].endswith("prj_analysis.md"))

    def test_conflicto_trae_la_decision_de_producto_del_informe(self):
        """El conflicto se presenta como decisión de producto, del informe (D-109)."""
        self._base()
        write(self.b.spec / "features" / "movimientos" / "spec" / "movimientos_conflict_report.md",
              "## Detalle de conflictos\n\n### [CF-F001-01] HU duplicada — Severidad: ALTA\n\n"
              "**Decisión de producto**:\n"
              "- **Qué hay que decidir**: qué pasa al borrar un gasto con deuda\n"
              "- **Ejemplo**: el Usuario paga 30 € por Ana y luego ve que eran 25 €\n"
              "- **Opción 1 — Gasto bloqueado**: el Usuario no puede borrarlo mientras exista la deuda. "
              "*Cambia:* F-001 (movimientos)\n"
              "- **Opción 2 — Se propaga**: borrar el gasto anula la deuda. *Cambia:* F-001 (movimientos), "
              "F-002 (cuentas)\n\n## Inventario\n")
        os.utime(self.b.spec / "spec_readiness_report.md")
        alta = next(i for i in self.b.pending()["items"] if i["tipo"] == "conflicto_alta")
        d = alta["decision"]
        self.assertEqual(d["que_decidir"], "qué pasa al borrar un gasto con deuda")
        self.assertIn("30 €", d["ejemplo"])
        self.assertEqual([(o["titulo"], o["cambia"]) for o in d["opciones"]],
                         [("Gasto bloqueado", ["F-001"]), ("Se propaga", ["F-001", "F-002"])])
        self.assertIn("mientras exista la deuda", d["opciones"][0]["efecto"])

    def test_conflicto_sin_decision_en_el_informe_la_deja_vacia(self):
        self._base()
        alta = next(i for i in self.b.pending()["items"] if i["tipo"] == "conflicto_alta")
        self.assertIsNone(alta["decision"])
        self.assertEqual(alta["opciones"], ["F-001", "F-002"])

    def test_media_descartada_por_el_readiness_no_aparece(self):
        """Con la tabla MEDIA en el readiness, un MEDIA de un informe suelto no sale."""
        self._base(media="")
        write(self.b.spec / "features" / "cuentas" / "spec" / "cuentas_conflict_report.md",
              "## Resumen de conflictos\n\n| ID | Tipo | Severidad | Features |\n|---|---|---|---|\n"
              "| CF-F002-09 | Scope overlap | MEDIA | F-001, F-002 |\n")
        os.utime(self.b.spec / "spec_readiness_report.md")  # readiness más nuevo que el informe
        self.assertNotIn("conflicto_media", tipos(self.b.pending()))

    def test_sin_tabla_media_cae_a_los_informes_y_lo_dice(self):
        self._base(media=None)
        rep = self.b.spec / "features" / "cuentas" / "spec" / "cuentas_conflict_report.md"
        write(rep, "## Resumen de conflictos\n\n| ID | Tipo | Severidad | Features |\n|---|---|---|---|\n"
                   "| CF-F002-09 | Scope overlap | MEDIA | F-001, F-002 |\n")
        past = time.time() - 60
        os.utime(rep, (past, past))
        media = next(i for i in self.b.pending()["items"] if i["tipo"] == "conflicto_media")
        self.assertIn("sin arbitrar", media["que"])

    def test_sin_readiness_lo_primero_es_rehacerlo(self):
        self._base(readiness=False)
        data = self.b.pending()
        self.assertEqual(data["items"][0]["tipo"], "readiness")
        self.assertFalse(data["readiness_vigente"])

    def test_spec_tocado_despues_del_readiness_lo_desactualiza(self):
        self._base()
        time.sleep(0.01)
        sp = self.b.spec / "features" / "cuentas" / "spec" / "cuentas_spec.md"
        sp.write_text(sp.read_text() + "\n<!-- delta -->\n")
        data = self.b.pending()
        self.assertEqual(data["items"][0]["tipo"], "readiness")
        self.assertIn("F-002", data["items"][0]["que"])

    def test_sellar_no_desactualiza_el_readiness(self):
        """Validar cambia el spec, pero no su contenido: no debe pedir rehacer el readiness."""
        self._base()
        time.sleep(0.01)
        sp = self.b.spec / "features" / "cuentas" / "spec" / "cuentas_spec.md"
        sp.write_text(sp.read_text().replace("Estado: BORRADOR", "Estado: VALIDADO"))
        self.assertNotIn("readiness", tipos(self.b.pending()))

    def test_alcance_derivado_bloquea_hasta_aceptarlo(self):
        self._base(p1="respondida")
        self.b.feature("F-001", "movimientos", avisos="alcance derivado desde P-001",
                       requiere="F-002")
        os.utime(self.b.spec / "spec_readiness_report.md")
        data = self.b.pending()
        self.assertIn("alcance_derivado", tipos(data))
        validar = next(i for i in data["items"] if i["tipo"] == "validar")
        self.assertEqual(validar["derivadas"], ["F-001"])
        self.b.feature("F-001", "movimientos", avisos="alcance derivado desde P-001",
                       requiere="F-002",
                       extra_header="> Alcance derivado aceptado: Ana (2026-09-28)\n")
        os.utime(self.b.spec / "spec_readiness_report.md")
        self.assertNotIn("alcance_derivado", tipos(self.b.pending()))

    def test_respuesta_reabierta_senala_los_specs_que_la_citan(self):
        self._base(p1="primera")
        self.b.feature("F-001", "movimientos", requiere="F-002", body="Ver [P-001].\n")
        past = time.time() - 3600
        os.utime(self.b.spec / "features" / "movimientos" / "spec" / "movimientos_spec.md",
                 (past, past))
        r = run_script("sdd-analysis-gaps.py", self.b.prd / "prj_analysis.md",
                       "--answer", "P-001", "segunda", "--force")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("- **Reabierto**:", (self.b.prd / "prj_analysis.md").read_text())
        reab = next(i for i in self.b.pending()["items"] if i["tipo"] == "reabierto")
        self.assertEqual(reab["features"], ["F-001"])

    def test_misma_respuesta_con_force_no_reabre(self):
        self._base(p1="igual")
        r = run_script("sdd-analysis-gaps.py", self.b.prd / "prj_analysis.md",
                       "--answer", "P-001", "igual", "--force")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("Reabierto", (self.b.prd / "prj_analysis.md").read_text())

    def test_todo_resuelto_lista_vacia(self):
        b = self.b
        b.feature("F-001", "movimientos", estado="VALIDADO")
        b.index([("F-001", "movimientos", "features/movimientos/spec/movimientos_spec.md",
                  "LISTA", "ninguno")])
        b.analysis("respondida")
        time.sleep(0.01)
        b.readiness("| F-001: movimientos | LISTA | 0 | 0 | — |", "", "")
        data = b.pending()
        self.assertEqual(data["total"], 0)
        r = run_script("sdd-project-status.py", b.spec, "--spec-pending")
        self.assertIn("Nada pendiente", r.stdout)

    def test_salida_humana_sin_nombres_de_skill(self):
        self._base()
        r = run_script("sdd-project-status.py", self.b.spec, "--spec-pending")
        self.assertEqual(r.returncode, 0)
        self.assertNotRegex(r.stdout, r"\b(wf|kb)-[a-z]")


class SealMencionTest(unittest.TestCase):
    """Una marca entre comillas de código es una mención, no una marca (D-104)."""

    def test_la_plantilla_que_explica_incompleto_no_bloquea_el_sello(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x_spec.md"
            write(p, spec("F-001", body="\n## Items Pendientes\n\n> Los críticos marcan sus HUs "
                                         "como `[INCOMPLETO]` y bloquean.\n"))
            r = run_script("sdd-seal.py", "spec", p, "--check")
            self.assertEqual(r.returncode, 0, r.stdout)

    def test_la_marca_real_sigue_bloqueando(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x_spec.md"
            write(p, spec("F-001", body="\n> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001].\n"))
            r = run_script("sdd-seal.py", "spec", p, "--check")
            self.assertEqual(r.returncode, 2, r.stdout)


class SealReportTest(unittest.TestCase):
    """`sdd-seal.py spec --report`: la tabla del lote, impresa por el script (D-107)."""

    def test_una_fila_por_spec_con_aprobador_o_motivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok = Path(tmp) / "bien_spec.md"
            write(ok, spec("F-002", estado="VALIDADO",
                           extra_header="> Aprobado por: Ana (PO) (2026-10-01)\n"))
            ko = Path(tmp) / "mal_spec.md"
            write(ko, spec("F-001", body="\n> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001].\n"))
            r = run_script("sdd-seal.py", "spec", "--report", ok, ko)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("| F-002: bien | ✓ Ana (PO) (2026-10-01) | — |", r.stdout)
            self.assertRegex(r.stdout, r"\| F-001: mal \| ✗ \| falla: Sin HUs \[INCOMPLETO\]")


class SealDerivedScopeTest(unittest.TestCase):
    """Condición 9 de `sdd-seal.py spec` (D-102)."""

    def _spec(self, d, avisos, header=""):
        p = d / "x_spec.md"
        write(p, spec("F-001", avisos=avisos, extra_header=header))
        return p

    def test_derivado_sin_aceptar_no_sella(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._spec(Path(tmp), "alcance derivado desde P-001")
            r = run_script("sdd-seal.py", "spec", p, "--check")
            self.assertEqual(r.returncode, 2)
            self.assertIn("Alcance derivado", r.stdout)

    def test_aceptado_con_nombre_sella_y_deja_constancia(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._spec(Path(tmp), "alcance derivado desde P-001")
            r = run_script("sdd-seal.py", "spec", p, "--seal", "--approved-by", "Ana (2026-09-28)",
                           "--accept-derived-scope", "Ana (2026-09-28)")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            text = p.read_text()
            self.assertIn("Estado: VALIDADO", text)
            self.assertIn("Alcance derivado aceptado: Ana (2026-09-28)", text)
            self.assertIn("Avisos de gobernanza: alcance derivado desde P-001", text)

    def test_aceptar_sin_aprobador_es_error_de_uso(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._spec(Path(tmp), "alcance derivado desde P-001")
            r = run_script("sdd-seal.py", "spec", p, "--seal", "--accept-derived-scope", "Ana")
            self.assertNotEqual(r.returncode, 0)
            self.assertNotIn("VALIDADO", p.read_text())

    def test_sin_aviso_no_cambia_nada(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._spec(Path(tmp), "ninguno")
            r = run_script("sdd-seal.py", "spec", p, "--check")
            self.assertEqual(r.returncode, 0, r.stdout)



INFORME_BLOQUES = """## Detalle de conflictos

### [CF-F001-01] Modelo — Severidad: ALTA

**Decisión de producto**:
- **Qué hay que decidir**: qué pasa con el saldo al reservar
- **Afecta también a**: F-004 (presupuesto), que suma los gastos
- **Opción 1 — Por movimiento**: reservar crea un gasto. *Cambia:* F-001 (movimientos), F-002 (cuentas)
- **Opción 2 — Excepción**: no crea gasto. *Cambia:* F-001 (movimientos)

### [CF-F001-02] CA contradictorio — Severidad: ALTA

**Decisión de producto**:
- **Qué hay que decidir**: si una transferencia cuenta para el límite global
- **Opción 1 — No cuenta**: mover dinero propio no es gastar. *Cambia:* F-004 (presupuesto)
- **Opción 2 — Cuenta**: reduce el margen. *Cambia:* F-004 (presupuesto)

## Inventario
"""


class MapaPorBloquesTest(unittest.TestCase):
    """Qué se puede planificar ya y qué bloques faltan (D-112)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.b = Bank(Path(self.tmp.name))
        b = self.b
        b.feature("F-001", "movimientos")
        b.feature("F-002", "cuentas")
        b.feature("F-003", "categorias", estado="VALIDADO")
        b.feature("F-004", "presupuesto")
        b.feature("F-005", "resumen")
        b.index([(f, n, f"features/{n}/spec/{n}_spec.md", "BLOQUEADA", "ninguno")
                 for f, n in (("F-001", "movimientos"), ("F-002", "cuentas"),
                              ("F-003", "categorias"), ("F-004", "presupuesto"),
                              ("F-005", "resumen"))])
        b.analysis("respondida")
        write(b.spec / "features" / "movimientos" / "spec" / "movimientos_conflict_report.md",
              INFORME_BLOQUES)
        time.sleep(0.01)
        b.readiness(alta_rows="| CF-F001-01 | Modelo | F-001, F-002 | saldo | x |\n"
                              "| CF-F001-02 | CA | F-001, F-004 | límite global | x |")

    def tearDown(self):
        self.tmp.cleanup()

    def test_una_feature_sin_nada_pendiente_se_puede_planificar_aunque_otras_tengan_conflictos(self):
        data = self.b.pending()
        self.assertEqual(data["por_feature"]["F-003"]["estado_plan"], "planificable")
        self.assertIn("Ya puedes planificar: categorias (F-003).", data["mapa"])

    def test_sin_sellar_queda_lista_en_cuanto_se_valide(self):
        data = self.b.pending()
        self.assertEqual(data["por_feature"]["F-005"]["estado_plan"], "lista_para_validar")
        self.assertIn("en cuanto las valides (no les falta ninguna decisión): resumen (F-005).",
                      data["mapa"])

    def test_el_bloque_lo_forman_las_features_que_la_decision_cambia_no_las_que_nombra(self):
        """CF-F001-02 nombra a movimientos, pero solo cambia presupuesto: bloque aparte."""
        bloques = {b["bloque"]: b["features"] for b in self.b.pending()["bloques"]}
        self.assertEqual(sorted(bloques.values()), [["F-001", "F-002"], ["F-004"]])

    def test_afecta_tambien_a_crea_espera_entre_bloques_sin_fusionarlos(self):
        data = self.b.pending()
        pres = next(b for b in data["bloques"] if b["features"] == ["F-004"])
        mov = next(b for b in data["bloques"] if b["features"] == ["F-001", "F-002"])
        self.assertEqual(pres["depende_de"], [mov["bloque"]])
        self.assertEqual(mov["depende_de"], [])
        self.assertIn("Además espera a 1 decisión del bloque " + mov["bloque"], data["mapa"])
        self.assertIn("Solo depende de sí mismo.", data["mapa"])

    def test_sin_afecta_tambien_a_no_hay_espera(self):
        rep = self.b.spec / "features" / "movimientos" / "spec" / "movimientos_conflict_report.md"
        rep.write_text(INFORME_BLOQUES.replace(
            "- **Afecta también a**: F-004 (presupuesto), que suma los gastos\n", ""))
        os.utime(self.b.spec / "spec_readiness_report.md")
        data = self.b.pending()
        self.assertTrue(all(b["depende_de"] == [] for b in data["bloques"]))

    def test_el_mapa_no_nombra_skills(self):
        data = self.b.pending()
        texto = data["cierre"]["pregunta"] + "".join(
            o["label"] + o["description"] + o.get("preview", "") for o in data["cierre"]["opciones"])
        self.assertNotRegex(texto, r"\b(wf|kb)-[a-z]")
        self.assertNotIn("conflicto_alta", texto)
        self.assertIn("1. Si una transferencia cuenta para el límite global\n"
                      "   Afecta a: presupuesto (F-004)\n   Opciones: No cuenta · Cuenta", texto)

    def test_el_cierre_trae_la_pregunta_y_como_mucho_cuatro_opciones(self):
        """Lo que no cabe se dice en la pregunta; la última opción es siempre dejarlo."""
        op = self.b.pending()["cierre"]["opciones"]
        self.assertLessEqual(len(op), 4)
        self.assertEqual(op[-1]["label"], "Lo dejo para luego")
        self.assertTrue(op[0]["label"].endswith("(Recomendado)"))
        self.assertTrue(all(o.get("preview") for o in op if o["accion"].startswith("bloque:")))

    def test_lo_que_no_frena_tambien_sale_en_el_mapa(self):
        """El mapa es qué falta para cerrarlo todo: también los menores y lo que no tiene spec."""
        self.b.readiness(alta_rows="| CF-F001-01 | Modelo | F-001, F-002 | saldo | x |",
                         media_rows="| CF-F004-01 | Hueco | F-004 | no dice si una devolución "
                                    "resta del gasto | x |")
        data = self.b.pending()
        self.assertIn("Sin frenar nada, queda 1 decisión menor", data["mapa"])
        menores = next(o for o in data["cierre"]["opciones"] if o["accion"] == "menores")
        self.assertIn("No dice si una devolución resta del gasto", menores["preview"])
        self.assertNotIn("(media) entre", menores["preview"])


class PreguntaAlcanceTest(unittest.TestCase):
    """El aviso de gobernanza, contado como pregunta a quien decide (v0.126.1)."""

    def test_saca_lo_que_se_acepta_y_de_donde_salio(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "sdd_project_status", Path(__file__).resolve().parent.parent / "scripts"
            / "sdd-project-status.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        texto = mod._pregunta_alcance(
            "alcance derivado desde P-002; alcance derivado (deshacer un cobro ya registrado "
            "sobre una deuda, decisión de producto sobre el conflicto CF-F001-02) decidido por "
            "el usuario")
        self.assertTrue(texto.startswith("¿Das por bueno «deshacer un cobro ya registrado "
                                         "sobre una deuda»? No está en el PRD"))
        self.assertIn("(CF-F001-02, P-002)", texto)



INFORME_TRASLADO = """## Detalle de conflictos

### [CF-F002-01] Shared models inconsistentes — Severidad: MEDIA

**Causa**: Sin trasladar — cuentas ya fija en su contrato que reservar exige saldo.

**Traslado**:
- **Qué**: reservar dinero para un objetivo exige saldo suficiente en la cuenta
- **Decidido en**: F-002 (cuentas)
- **Falta en**: F-003 (objetivos)

### [CF-F001-03] Hueco — Severidad: MEDIA

**Decisión de producto**:
- **Qué hay que decidir**: si el saldo puede quedar negativo al registrar un gasto
- **Opción 1 — Nunca negativo**: se deniega. *Cambia:* F-002 (cuentas)
- **Opción 2 — Puede quedar negativo**: se avisa. *Cambia:* F-002 (cuentas)

## Inventario
"""


class LoYaDecididoYSugerenciasTest(unittest.TestCase):
    """D-113 y v0.126.2: lo ya decidido no se pregunta; las sugerencias se ven."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        b = self.b = Bank(Path(self.tmp.name))
        b.feature("F-001", "movimientos", estado="VALIDADO")
        b.feature("F-002", "cuentas", estado="VALIDADO",
                  extra_header="> Sugerencias de la validación: promete avisar sin datos y no "
                               "hay criterio que lo pruebe → añadir ese criterio\n")
        b.feature("F-003", "objetivos", estado="VALIDADO")
        b.index([(f, n, f"features/{n}/spec/{n}_spec.md", "LISTA", "ninguno")
                 for f, n in (("F-001", "movimientos"), ("F-002", "cuentas"),
                              ("F-003", "objetivos"))])
        b.analysis("respondida")
        write(b.spec / "features" / "cuentas" / "spec" / "cuentas_conflict_report.md",
              INFORME_TRASLADO)
        time.sleep(0.01)
        b.readiness(media_rows="| `CF-F002-01` | Sin trasladar | F-002, F-003 | x | x |\n"
                               "| `CF-F001-03` (= `CF-F005-09`) | Hueco | F-001, F-002 | "
                               "invariante técnica | x |")

    def tearDown(self):
        self.tmp.cleanup()

    def test_sin_trasladar_no_es_una_decision(self):
        data = self.b.pending()
        tr = next(i for i in data["items"] if i["tipo"] == "trasladar")
        self.assertEqual(tr["features"], ["F-003"])
        self.assertNotIn("CF-F002-01", [i.get("conflicto") for i in data["items"]
                                       if i["tipo"] == "conflicto_media"])
        op = next(o for o in data["cierre"]["opciones"] if o["accion"] == "trasladar")
        self.assertIn("reservar dinero para un objetivo exige saldo suficiente", op["preview"])
        self.assertIn("Ya decidido, falta copiarlo", data["mapa"])

    def test_el_id_con_alias_del_readiness_encuentra_su_decision(self):
        """`CF-F001-03` (= `CF-F005-09`) se quedaba sin decisión de producto (CU-3.ac)."""
        menor = next(i for i in self.b.pending()["items"] if i["tipo"] == "conflicto_media")
        self.assertEqual(menor["decision"]["que_decidir"],
                         "si el saldo puede quedar negativo al registrar un gasto")

    def test_la_sugerencia_de_la_validacion_sale_en_el_mapa_y_se_ofrece(self):
        data = self.b.pending()
        self.assertIn("La validación dejó 1 sugerencia en cuentas", data["mapa"])
        labels = [o["label"] for o in data["cierre"]["opciones"]]
        self.assertTrue(any(l.startswith("Aplicar sugerencias (1)") for l in labels), labels)

    def test_el_resultado_del_lote_encabeza_el_cierre(self):
        r = run_script("sdd-project-status.py", self.b.spec, "--spec-pending", "--json",
                       "--lote", self.b.spec / "features" / "cuentas" / "spec" / "cuentas_spec.md")
        pregunta = json.loads(r.stdout)["cierre"]["pregunta"]
        self.assertTrue(pregunta.startswith("Validadas (1): cuentas (F-002)."), pregunta[:120])
        self.assertIn("- cuentas (F-002): promete avisar sin datos", pregunta)



class PieDelBloqueTest(unittest.TestCase):
    def test_un_bloque_que_solo_acepta_alcance_no_promete_cambios(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Bank(Path(tmp))
            b.feature("F-001", "deudas", avisos="alcance derivado desde P-002")
            b.feature("F-002", "cuentas")
            b.index([("F-001", "deudas", "features/deudas/spec/deudas_spec.md", "BLOQUEADA",
                      "alcance derivado desde P-002"),
                     ("F-002", "cuentas", "features/cuentas/spec/cuentas_spec.md", "BLOQUEADA",
                      "ninguno")])
            b.analysis("respondida")
            time.sleep(0.01)
            b.readiness()
            bloque = b.pending()["bloques"][0]
            self.assertIn("no hace falta cambiar ningún spec", bloque["preview"])
            self.assertNotIn("una revisión de", bloque["preview"])



class SugerenciasDelSelladorTest(unittest.TestCase):
    def _spec(self, tmp):
        p = Path(tmp) / "x_spec.md"
        write(p, spec("F-001"))
        return p

    def test_suggest_queda_en_la_cabecera_y_se_va_al_desellar(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._spec(tmp)
            r = run_script("sdd-seal.py", "spec", p, "--seal", "--approved-by", "Ana (2026-10-26)",
                           "--suggest", "falta un CA → añadirlo", "--suggest", "otra")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("> Sugerencias de la validación: falta un CA → añadirlo · otra",
                          p.read_text())
            r = run_script("sdd-seal.py", "spec", "--report", "--lineas", p)
            self.assertIn("Validadas (1): x (F-001). Aprobó: Ana (2026-10-26).", r.stdout)
            self.assertIn("- x (F-001): otra", r.stdout)
            run_script("sdd-seal.py", "spec", p, "--unseal")
            self.assertNotIn("Sugerencias de la validación", p.read_text())

    def test_volver_a_sellar_sin_sugerencias_las_quita(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = self._spec(tmp)
            run_script("sdd-seal.py", "spec", p, "--seal", "--approved-by", "Ana", "--suggest", "a")
            run_script("sdd-seal.py", "spec", p, "--seal", "--approved-by", "Ana")
            self.assertNotIn("Sugerencias de la validación", p.read_text())

    def test_sellar_pone_al_dia_el_indice(self):
        """v0.126.2: el índice seguía «pendiente de validación» tras sellar."""
        with tempfile.TemporaryDirectory() as tmp:
            b = Bank(Path(tmp))
            b.feature("F-001", "cuentas")
            b.index([("F-001", "cuentas", "features/cuentas/spec/cuentas_spec.md", "BLOQUEADA",
                      "ninguno")])
            sp = b.spec / "features" / "cuentas" / "spec" / "cuentas_spec.md"
            r = run_script("sdd-seal.py", "spec", sp, "--seal", "--approved-by", "Ana")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("Índice de features actualizado", r.stdout)
            self.assertIn("LISTA", (b.spec / "spec_features.md").read_text())


class MotivoDelRechazoTest(unittest.TestCase):
    """v0.127.1: por qué no se selló queda en el spec; el cierre y el mapa lo leen."""

    def _bank(self, tmp, header):
        b = Bank(Path(tmp))
        b.feature("F-001", "objetivos", extra_header="> Versión: 1.2\n" + header)
        b.feature("F-002", "cuentas", estado="VALIDADO")
        b.index([("F-001", "objetivos", "features/objetivos/spec/objetivos_spec.md", "LISTA",
                  "ninguno"),
                 ("F-002", "cuentas", "features/cuentas/spec/cuentas_spec.md", "LISTA",
                  "ninguno")])
        b.analysis("respondida")
        time.sleep(0.01)
        b.readiness()
        return b

    def test_blocked_queda_en_la_cabecera_con_su_version_y_se_va_al_sellar(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x_spec.md"
            write(p, spec("F-001", extra_header="> Versión: 1.2\n"))
            r = run_script("sdd-seal.py", "spec", p, "--unseal", "--blocked",
                           "repite una regla de los movimientos — citarla")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("> La validación pide corregir: (v1.2) repite una regla de los "
                          "movimientos — citarla", p.read_text())
            r = run_script("sdd-seal.py", "spec", "--report", "--lineas", p)
            self.assertIn("no se validó — la validación pide corregir: repite una regla", r.stdout)
            self.assertNotIn("o no se aprobó", r.stdout)
            run_script("sdd-seal.py", "spec", p, "--unseal")
            self.assertIn("La validación pide corregir", p.read_text(),
                          "aplicar un cambio no demuestra que se corrigió")
            run_script("sdd-seal.py", "spec", p, "--seal", "--approved-by", "Ana")
            self.assertNotIn("La validación pide corregir", p.read_text())

    def test_not_approved_lo_dice_y_sustituye_al_hallazgo_anterior(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x_spec.md"
            write(p, spec("F-001"))
            run_script("sdd-seal.py", "spec", p, "--unseal", "--blocked", "a")
            r = run_script("sdd-seal.py", "spec", p, "--unseal", "--not-approved")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            text = p.read_text()
            self.assertNotIn("La validación pide corregir", text)
            self.assertIn("> Sin aprobar: se dejó en borrador al validar", text)
            r = run_script("sdd-seal.py", "spec", "--report", p)
            self.assertIn("pasa la auditoría, pero no se aprobó", r.stdout)

    def test_blocked_solo_con_unseal(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x_spec.md"
            write(p, spec("F-001"))
            r = run_script("sdd-seal.py", "spec", p, "--seal", "--blocked", "a")
            self.assertEqual(r.returncode, 1)

    def test_el_mapa_la_da_por_corregir_y_no_por_lista(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = self._bank(tmp, "> La validación pide corregir: (v1.2) repite una regla — citarla\n")
            data = b.pending()
            self.assertEqual(data["por_feature"]["F-001"]["estado_plan"], "pendiente_corregir")
            self.assertNotIn("en cuanto las valides", data["mapa"])
            self.assertIn("Falta corregir lo que vio la validación en objetivos (F-001)",
                          data["mapa"])
            op = next(o for o in data["cierre"]["opciones"] if o["accion"] == "corregir")
            self.assertIn("objetivos (F-001): repite una regla — citarla", op["preview"])
            self.assertNotIn("validar", [o["accion"] for o in data["cierre"]["opciones"]])

    def test_con_la_version_cambiada_vuelve_a_lista_para_validar(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = self._bank(tmp, "> La validación pide corregir: (v1.1) repite una regla\n")
            data = b.pending()
            self.assertEqual(data["por_feature"]["F-001"]["estado_plan"], "lista_para_validar")
            r = run_script("sdd-seal.py", "spec", "--report", "--lineas",
                           b.spec / "features" / "objetivos" / "spec" / "objetivos_spec.md")
            self.assertIn("se corrigió lo que pidió la validación anterior", r.stdout)


class RehacerLaMedicionTest(unittest.TestCase):
    def test_la_opcion_dice_que_cambio_y_que_va_a_pasar(self):
        """v0.127.1: salía sin vista previa, y el aviso parecía contradecir al «ya puedes»."""
        with tempfile.TemporaryDirectory() as tmp:
            b = Bank(Path(tmp))
            b.feature("F-001", "categorias", estado="VALIDADO")
            b.feature("F-002", "objetivos")
            b.index([("F-001", "categorias", "features/categorias/spec/categorias_spec.md",
                      "LISTA", "ninguno"),
                     ("F-002", "objetivos", "features/objetivos/spec/objetivos_spec.md",
                      "LISTA", "ninguno")])
            b.analysis("respondida")
            b.readiness()
            time.sleep(0.02)
            b.feature("F-002", "objetivos", body="\ncambiado\n")
            data = b.pending()
            op = next(o for o in data["cierre"]["opciones"] if o["accion"] == "readiness")
            self.assertIn("Han cambiado después de la última medición: objetivos (F-002).",
                          op["preview"])
            self.assertIn("Lo ya validado se puede planificar igual", data["mapa"])
            self.assertNotIn("puede cambiar lo que sigue", data["mapa"])


INFORME_FUERA_DEL_DUENO = """## Detalle de conflictos

### [CF-F004-01] Shared models inconsistentes — Severidad: MEDIA

**Causa**: Decidido fuera del dueño — el usuario respondió D-006 en movimientos.

**Traslado**:
- **Qué**: el dinero que reservas para un objetivo no cuenta para tu límite global
- **Decidido en**: F-001 (movimientos), respuesta a D-006
- **Falta en**: F-004 (presupuesto)

## Inventario
"""


class DecididoFueraDelDuenoTest(unittest.TestCase):
    def test_se_aplica_como_traslado_y_no_se_pregunta(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Bank(Path(tmp))
            b.feature("F-001", "movimientos", estado="VALIDADO")
            b.feature("F-004", "presupuesto", estado="VALIDADO")
            b.index([("F-001", "movimientos", "features/movimientos/spec/movimientos_spec.md",
                      "LISTA", "ninguno"),
                     ("F-004", "presupuesto", "features/presupuesto/spec/presupuesto_spec.md",
                      "LISTA", "ninguno")])
            b.analysis("respondida")
            write(b.spec / "features" / "presupuesto" / "spec" / "presupuesto_conflict_report.md",
                  INFORME_FUERA_DEL_DUENO)
            time.sleep(0.01)
            b.readiness(media_rows="| `CF-F004-01` | Decidido fuera del dueño | F-001, F-004 | x | x |")
            data = b.pending()
            tr = next(i for i in data["items"] if i["tipo"] == "trasladar")
            self.assertEqual(tr["traslado"]["falta_en"], ["F-004"])
            self.assertEqual(tr["traslado"]["decidido_en"], ["F-001"])
            self.assertNotIn("conflicto_media", tipos(data))

    def test_lo_que_falta_copiar_no_se_ofrece_para_validar(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Bank(Path(tmp))
            b.feature("F-001", "movimientos", estado="BORRADOR")
            b.feature("F-004", "presupuesto", estado="BORRADOR")
            b.index([("F-001", "movimientos", "features/movimientos/spec/movimientos_spec.md",
                      "LISTA", "ninguno"),
                     ("F-004", "presupuesto", "features/presupuesto/spec/presupuesto_spec.md",
                      "LISTA", "ninguno")])
            b.analysis("respondida")
            write(b.spec / "features" / "presupuesto" / "spec" / "presupuesto_conflict_report.md",
                  INFORME_FUERA_DEL_DUENO)
            time.sleep(0.01)
            b.readiness(media_rows="| `CF-F004-01` | Decidido fuera del dueño | F-001, F-004 | x | x |")
            data = b.pending()
            val = next(i for i in data["items"] if i["tipo"] == "validar")
            self.assertEqual(val["features"], ["F-001"])
            self.assertEqual(val["en_espera"][0]["feature"], "F-004")
            self.assertEqual(data["por_feature"]["F-004"]["estado_plan"], "pendiente_copiar")
            self.assertIn("Validar las listas (1)",
                          " ".join(o["label"] for o in data["cierre"]["opciones"]))


if __name__ == "__main__":
    unittest.main()
