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
- **Estado**: {estado}
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
