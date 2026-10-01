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
        self.assertIn("se planifican juntas", r.stdout)
        nota = next(l for l in r.stdout.splitlines() if "se planifican juntas" in l)
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

    def test_resumen_trae_el_total_y_el_aviso_del_grupo(self):
        data = self._tres_en_ciclo([("Movimiento", "F-001", "F-002, F-003"),
                                    ("Cuenta", "F-002", "F-001"),
                                    ("Objetivo", "F-003", "F-002")])
        self.assertTrue(data["resumen"].startswith("Quedan 1 pendiente; 1 impide planificar."))
        self.assertIn("se planifican juntas", data["resumen"])

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


if __name__ == "__main__":
    unittest.main()
