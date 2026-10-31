"""Black-box tests para `sdd-model-contracts.py` y lo que cuelga de él (D-111).

Cada regla de un modelo compartido tiene un dueño: el spec dueño publica el contrato
del modelo con su catálogo de orígenes, y los consumidores lo citan o le hacen una
petición. El script es el lint de esas fronteras; la condición 10 de `sdd-seal.py
spec` y el tipo `peticion` de `sdd-project-status.py --spec-pending` lo consumen.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import run_script, write  # noqa: E402
from test_sdd_spec_pending import Bank  # noqa: E402

CONTRATO = """
## Contrato de modelos compartidos
### Movimiento
- **Qué puede hacer el Usuario**: crear, editar y eliminar los que registra a mano.
#### Orígenes externos
| Origen | Operación | Qué crea o cambia | ¿Se puede tocar desde el histórico? | Si se toca |
|---|---|---|---|---|
{filas}
"""

CONSUMO = """
## Modelos de otras features
| Modelo | Dueña | Qué hace esta feature con él | Regla que aplica |
|---|---|---|---|
{filas}
{peticiones}
"""

PETICION = """### Peticiones al dueño
### [R-001] A F-001 (Movimiento): el gasto de una deuda viva no se edita
- **Por qué**: la deuda cuenta con ese gasto.

"""

GASTO_DEUDA = "| Movimiento | F-001 | crea un gasto al registrar una deuda | Orígenes externos de F-001 |"
LECTURA = "| Movimiento | F-001 | lectura: suma los gastos del mes | Contrato de F-001 |"


class ContractsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.b = Bank(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def _banco(self, origenes="", consumo_f2="", consumo_f3="", refs="F-002", contrato=True):
        b = self.b
        b.feature("F-001", "movimientos",
                  body=CONTRATO.format(filas=origenes) if contrato else
                  CONSUMO.format(filas="", peticiones=""))
        b.feature("F-002", "deudas", body=consumo_f2)
        b.feature("F-003", "presupuesto", body=consumo_f3)
        b.index([(f, n, f"features/{n}/spec/{n}_spec.md", "BLOQUEADA", "ninguno")
                 for f, n in (("F-001", "movimientos"), ("F-002", "deudas"),
                              ("F-003", "presupuesto"))],
                shared=[("Movimiento", "F-001", refs)])

    def contracts(self):
        r = run_script("sdd-model-contracts.py", self.b.spec, "--json")
        self.assertIn(r.returncode, (0, 2), r.stderr)
        return json.loads(r.stdout), r.returncode

    def seal(self, name):
        return run_script("sdd-seal.py", "spec",
                          self.b.spec / "features" / name / "spec" / f"{name}_spec.md", "--check")

    def test_consumidor_que_crea_sin_fila_en_el_catalogo_del_dueño_bloquea_al_dueño(self):
        self._banco(consumo_f2=CONSUMO.format(filas=GASTO_DEUDA, peticiones=""))
        data, rc = self.contracts()
        self.assertEqual(rc, 2)
        self.assertEqual([(c["owner"], c["consumidor"]) for c in data["catalogo"]],
                         [("F-001", "F-002")])
        r = self.seal("movimientos")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("no lo recoge", r.stdout)
        self.assertEqual(self.seal("deudas").returncode, 0, self.seal("deudas").stdout)

    def test_catalogo_con_la_fila_del_consumidor_pasa(self):
        self._banco(origenes="| F-002 (deudas) | Registrar deuda | gasto vinculado | no | — |",
                    consumo_f2=CONSUMO.format(filas=GASTO_DEUDA, peticiones=""))
        data, rc = self.contracts()
        self.assertEqual(rc, 0, data)
        self.assertEqual(self.seal("movimientos").returncode, 0)

    def test_la_lectura_no_necesita_fila_en_el_catalogo(self):
        self._banco(consumo_f2=CONSUMO.format(filas=LECTURA, peticiones=""))
        data, rc = self.contracts()
        self.assertEqual((rc, data["catalogo"]), (0, []))

    def test_lectura_en_medio_de_la_celda_tampoco_necesita_fila(self):
        fila = "| Movimiento | F-001 | asocia un gasto a su resumen; lectura de su importe | Contrato |"
        self._banco(consumo_f2=CONSUMO.format(filas=fila, peticiones=""))
        data, rc = self.contracts()
        self.assertEqual((rc, data["catalogo"]), (0, []))

    def test_lectura_y_escritura_en_la_misma_celda_escribe(self):
        # v0.128.0: «lectura: … · escritura: …» salía como solo lectura (CU-3.ac (3)).
        fila = ("| Movimiento | F-001 | lectura: muestra las aportaciones · escritura: reservar "
                "crea el movimiento | Contrato |")
        self._banco(consumo_f2=CONSUMO.format(filas=fila, peticiones=""))
        data, rc = self.contracts()
        self.assertEqual(rc, 2)
        self.assertEqual([u["escribe"] for u in data["uso"] if u["feature"] == "F-002"], [True])

    def test_el_indice_declara_un_uso_que_el_spec_no_tiene(self):
        # v0.128.4: F-003 figura como referencia de Movimiento y su spec no lo usa.
        self._banco(consumo_f2=CONSUMO.format(filas=LECTURA, peticiones=""),
                    consumo_f3=CONSUMO.format(filas="", peticiones=""), refs="F-002, F-003")
        data, rc = self.contracts()
        self.assertEqual([(x["feature"], x["modelo"]) for x in data["referencias_sin_uso"]],
                         [("F-003", "Movimiento")])
        self.assertEqual(rc, 0)          # es un aviso: no bloquea

    def test_vecinas_son_las_que_comparten_un_modelo(self):
        self._banco(consumo_f2=CONSUMO.format(filas=LECTURA, peticiones=""), refs="F-002")
        r = run_script("sdd-model-contracts.py", self.b.spec, "--vecinas", "F-002", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        v = json.loads(r.stdout)
        self.assertEqual(v["vecinas"], ["F-001"])
        self.assertEqual(v["por_modelo"]["F-001"], ["Movimiento"])
        r = run_script("sdd-model-contracts.py", self.b.spec, "--vecinas", "F-003", "--json")
        self.assertEqual(json.loads(r.stdout)["vecinas"], [])

    def test_lee_al_principio_o_no_cambia_tambien_es_lectura(self):
        for fila in ("| Movimiento | F-001 | Lee el histórico para el resumen | Contrato |",
                     "| Movimiento | F-001 | elige la cuenta del gasto. No cambia su saldo | Contrato |"):
            self._banco(consumo_f2=CONSUMO.format(filas=fila, peticiones=""))
            data, rc = self.contracts()
            self.assertEqual((rc, data["catalogo"]), (0, []), fila)

    def test_la_columna_uso_manda_sobre_como_esta_redactada_la_celda(self):
        """«Lee…» en la celda pero `escritura` en Uso: cuenta como escritura (D-112)."""
        tabla = ("| Modelo | Dueña | Uso | Qué hace esta feature con él | Regla que aplica |\n"
                 "|---|---|---|---|---|\n"
                 "| Movimiento | F-001 | escritura | Lee y luego crea un gasto | Contrato |\n")
        self._banco(consumo_f2="\n## Modelos de otras features\n" + tabla)
        data, rc = self.contracts()
        self.assertEqual([c["consumidor"] for c in data["catalogo"]], ["F-002"])
        self._banco(consumo_f2="\n## Modelos de otras features\n"
                    + tabla.replace("| escritura |", "| lectura |").replace("Lee y luego crea",
                                                                          "Crea"))
        data, rc = self.contracts()
        self.assertEqual(data["catalogo"], [])

    def test_lo_que_el_spec_declara_usar_respalda_la_dependencia_del_ciclo(self):
        """El índice olvida que F-003 lee Movimiento: aviso, pero no un ciclo que bloquea."""
        self._banco(origenes="| F-002 (deudas) | Registrar deuda | gasto | no | — |",
                    consumo_f2=CONSUMO.format(filas=GASTO_DEUDA, peticiones=""),
                    consumo_f3=CONSUMO.format(filas=LECTURA, peticiones=""))
        for fid, name, req in (("F-001", "movimientos", "F-003"), ("F-003", "presupuesto", "F-001")):
            readme = self.b.spec / "features" / name / "README.md"
            readme.write_text(readme.read_text().replace("- **Requiere**: Ninguna",
                                                         f"- **Requiere**: {req}"))
        b = self.b
        idx = b.spec / "spec_features.md"
        idx.write_text(idx.read_text().replace(
            "| Movimiento | F-001: x | F-002 |",
            "| Movimiento | F-001: x | F-002 |\n| Presupuesto | F-003: x | F-001 |"))
        pend = self.b.pending()
        self.assertNotIn("ciclo", [i["tipo"] for i in pend["items"]])
        self.assertEqual([d["feature"] for d in pend["dependencias_no_declaradas"]], ["F-003"])

    def test_peticion_pendiente_bloquea_al_consumidor_y_sale_en_la_lista(self):
        self._banco(origenes="| F-002 (deudas) | Registrar deuda | gasto vinculado | sí | — |",
                    consumo_f2=CONSUMO.format(filas=GASTO_DEUDA,
                                              peticiones=PETICION.format(estado="pendiente")))
        data, rc = self.contracts()
        self.assertEqual([p["id"] for p in data["peticiones"]], ["R-001"])
        r = self.seal("deudas")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("R-001 sin atender", r.stdout)
        pend = self.b.pending()
        pet = [i for i in pend["items"] if i["tipo"] == "peticion"]
        self.assertEqual(len(pet), 1)
        self.assertEqual(pet[0]["owner"], "F-001")
        self.assertEqual(pet[0]["via"], "wf-spec-delta sobre el dueño")
        self.assertIn("completar 1 contrato de un modelo compartido", pend["resumen"])

    def test_peticion_citada_en_el_catalogo_del_dueño_queda_atendida(self):
        self._banco(origenes="| F-002 (deudas) · R-001 | Registrar deuda | gasto vinculado | no | — |",
                    consumo_f2=CONSUMO.format(filas=GASTO_DEUDA,
                                              peticiones=PETICION.format(estado="pendiente")))
        data, rc = self.contracts()
        self.assertEqual((rc, data["peticiones"]), (0, []))
        self.assertEqual(self.seal("deudas").returncode, 0)

    def test_peticion_citada_en_otra_columna_de_la_fila_tambien_queda_atendida(self):
        self._banco(origenes="| F-002 (deudas) | Registrar deuda | gasto vinculado (F-002 · R-001) | no | — |",
                    consumo_f2=CONSUMO.format(filas=GASTO_DEUDA,
                                              peticiones=PETICION.format(estado="pendiente")))
        data, rc = self.contracts()
        self.assertEqual((rc, data["peticiones"]), (0, []))

    def test_el_R_001_de_otra_consumidora_no_atiende_esta_peticion(self):
        self._banco(origenes="| F-002 (deudas) | Registrar deuda | gasto | no | — |\n"
                             "| F-003 (presupuesto) · R-001 | Otra cosa | x | no | — |",
                    consumo_f2=CONSUMO.format(filas=GASTO_DEUDA,
                                              peticiones=PETICION.format(estado="pendiente")))
        data, rc = self.contracts()
        self.assertEqual([p["id"] for p in data["peticiones"]], ["R-001"])

    def test_dependencia_que_el_indice_no_declara_es_un_aviso(self):
        self._banco(consumo_f3=CONSUMO.format(filas=LECTURA.replace("suma", "cuenta"),
                                              peticiones=""))
        data, rc = self.contracts()
        self.assertEqual(rc, 0)
        self.assertEqual([d["feature"] for d in data["no_declaradas"]], ["F-003"])
        r = run_script("sdd-project-status.py", self.b.spec, "--spec-pending")
        self.assertIn("Aviso (no es un pendiente): F-003 (presupuesto) usa Movimiento", r.stdout)

    def test_dueña_en_formato_nuevo_sin_contrato_de_su_modelo(self):
        self._banco(contrato=False, consumo_f2=CONSUMO.format(filas=LECTURA, peticiones=""))
        data, rc = self.contracts()
        self.assertEqual(rc, 2)
        self.assertEqual([p["owner"] for p in data["sin_contrato"]], ["F-001"])
        self.assertEqual(self.seal("movimientos").returncode, 2)

    def test_specs_anteriores_a_los_contratos_quedan_exentos(self):
        self._banco(contrato=False)
        write(self.b.spec / "features" / "movimientos" / "spec" / "movimientos_spec.md",
              (self.b.spec / "features" / "movimientos" / "spec" / "movimientos_spec.md")
              .read_text().split("## Modelos de otras features")[0])
        data, rc = self.contracts()
        self.assertEqual(rc, 0)
        self.assertEqual(data["anteriores_a_d111"], ["F-001", "F-002", "F-003"])
        r = self.seal("movimientos")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn("Contratos", r.stdout)

    def test_peticion_respondida_que_la_consumidora_aun_da_por_pendiente_se_corrige(self):
        # v0.128.5: cuentas salía lista para validar con «pendiente: F-006 aún sin spec».
        fila = GASTO_DEUDA.replace("Orígenes externos de F-001",
                                   "Contrato de F-001 (pendiente: F-001 aún sin spec, ver R-001)")
        self._banco(origenes="| F-002 (deudas) · R-001 | Registrar deuda | gasto vinculado | no | — |",
                    consumo_f2=CONSUMO.format(filas=fila,
                                              peticiones=PETICION.format(estado="pendiente")))
        data, rc = self.contracts()
        self.assertEqual((rc, data["peticiones"]), (0, []))
        self.assertEqual([(d["consumidor"], d["id"]) for d in data["peticiones_desfasadas"]],
                         [("F-002", "R-001")])
        self.assertEqual(self.seal("deudas").returncode, 0)   # no cambia lo que se sella
        pend = json.loads(run_script("sdd-project-status.py", self.b.spec, "--spec-pending",
                                     "--json").stdout)
        corr = [i for i in pend["items"] if i["tipo"] == "corregir"]
        self.assertEqual([i["features"] for i in corr], [["F-002"]])
        self.assertNotEqual(pend["por_feature"]["F-002"]["estado_plan"], "lista_para_validar")
        self.assertNotIn("F-002", next((i["features"] for i in pend["items"]
                                        if i["tipo"] == "validar"), []))

    def test_pendiente_de_aceptar_es_dominio_no_espera(self):
        fila = GASTO_DEUDA.replace("Orígenes externos de F-001",
                                   "un pago pendiente de aceptar lo fija F-001 (ver R-001)")
        self._banco(origenes="| F-002 (deudas) · R-001 | Registrar deuda | gasto vinculado | no | — |",
                    consumo_f2=CONSUMO.format(filas=fila,
                                              peticiones=PETICION.format(estado="pendiente")))
        data, _ = self.contracts()
        self.assertEqual(data["peticiones_desfasadas"], [])

    def test_peticion_a_una_feature_sin_spec_espera_a_generarla_no_es_un_bloque(self):
        # v0.128.5: cuentas salía como bloque «solo depende de sí mismo» y recomendado, y su
        # única decisión era una pregunta de pagos previstos, sin spec todavía.
        b = self.b
        b.feature("F-002", "deudas", body=CONSUMO.format(
            filas=GASTO_DEUDA, peticiones=PETICION.format(estado="pendiente")))
        b.index([("F-001", "movimientos", None, "PENDIENTE_GENERACIÓN", "ninguno"),
                 ("F-002", "deudas", "features/deudas/spec/deudas_spec.md", "BLOQUEADA",
                  "ninguno")], shared=[("Movimiento", "F-001", "F-002")])
        b.readiness()
        pend = json.loads(run_script("sdd-project-status.py", b.spec, "--spec-pending",
                                     "--json").stdout)
        self.assertIn("espera_generar", [i["tipo"] for i in pend["items"]])
        self.assertNotIn("peticion", [i["tipo"] for i in pend["items"]])
        self.assertEqual(pend["bloques"], [])
        self.assertEqual(pend["por_feature"]["F-002"]["estado_plan"], "espera_a_otro")
        self.assertIn("espera a que se genere movimientos (F-001), que tiene que responder su "
                      "petición", pend["mapa"])
        self.assertIn("Generar movimientos (F-001) desbloquea deudas (F-002)", pend["mapa"])
        self.assertTrue(pend["cierre"]["opciones"][0]["label"].startswith("Generar movimientos"))


class UnsealDropsApprovalTest(unittest.TestCase):
    def test_unseal_retira_el_aprobado_por(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x_spec.md"
            write(p, "# Spec\n\n> Feature ID: F-001\n> Estado: VALIDADO\n"
                     "> Aprobado por: Ana (PO) (2026-10-21)\n> Origen de alcance: PRD\n\n"
                     "### HU-001: hu\n\n### CA-001: ca ← HU-001\n")
            r = run_script("sdd-seal.py", "spec", p, "--unseal")
            self.assertEqual(r.returncode, 0, r.stderr)
            text = p.read_text()
            self.assertIn("Estado: BORRADOR", text)
            self.assertNotIn("Aprobado por", text)


if __name__ == "__main__":
    unittest.main()
