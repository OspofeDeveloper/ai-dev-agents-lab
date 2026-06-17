# CU-2 — Crear y dejar listo un PRD

**Objetivo:** verificar que el sistema redacta un PRD de negocio sin inventar (marca
`[ASUNCIÓN]` lo que no traza a la fuente) y que la revisión no lo da por `LISTO`
mientras queden asunciones sin confirmar ni se autoaprueba.
**Proyecto a usar:** un producto real del que tengas notas o un brief informal
(cualquier dominio). Idealmente material con afirmaciones no triviales o lagunas, para
que el PRD tenga que marcar `[ASUNCIÓN]`.
**Cobertura automática:** ninguna directa — la calidad del PRD y el respeto del gate
de asunciones son juicio del agente `prd-expert`, así que estos escenarios son
**manuales**. El conteo de asunciones (`grep "[ASUNCIÓN]"`) sí es determinista.

> [!IMPORTANT]
> **La regla que gobierna toda la fase — anti-fabricación (Regla 12 de
> `kb-prd-expert`):** toda afirmación de negocio traza al material fuente, o se
> marca `[ASUNCIÓN]` (inline) + `[ASN-XXX]` en `## Asunciones del PRD`. Un PRD con
> asunciones sin confirmar **no llega a `LISTO`**.

---

## 🧪 Qué se prueba aquí (por componente)

CU-2 es un **objetivo de usuario** (crear y dejar listo un PRD), no una sola skill: sus
escenarios ejercitan **dos componentes**. Marca cada escenario al ejecutarlo. El estado de
cobertura autoritativo (ejes happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) —
esta vista es la **transpuesta** para leer/ejecutar el CU.

### `wf-prd-create` — redactar el PRD (`prd-expert`) (4)
- [ ] CU-2.a — Crear el PRD desde notas
- [ ] CU-2.b — Crear el PRD sin notas (brief oral)
- [ ] CU-2.c — Apuntar a un directorio o fuente inexistente
- [ ] CU-2.d — Regenerar un PRD que ya existe

### `wf-prd-review` — revisar el PRD y sellar (`prd-expert`) (4)
- [ ] CU-2.e — Revisar el PRD: gate de asunciones (lo más crítico)
- [ ] CU-2.f — Veredicto LISTO y sello de aprobación
- [ ] CU-2.g — Pasar algo que no es un PRD
- [ ] CU-2.h — La revisión no reescribe a su cosecha

> **Capa determinista** (no es un escenario manual): el conteo de asunciones
> (`grep "[ASUNCIÓN]"`, Paso 5.5 de `wf-prd-review`) es el único check automático de la fase.

---

## CU-2.a — Crear el PRD desde notas

**Precondición:** existe un fichero de notas/brief válido (tus notas reales del producto).
**Mecanismo:** skill `wf-prd-create` → subagente **`prd-expert`** (`context: fork`,
carga `kb-prd-expert`). Output: `prd.md` (en `--output`, o `artifacts.prd` de
`project-init.json`, o `<dir>/prd.md`).

1. Le pides que te cree el PRD a partir de esas notas ("créame el PRD desde este brief").
   → **Esperado:** `prd-expert` redacta `prd.md` con las secciones mínimas (Resumen,
     Actores, Alcance dentro/fuera, Reglas transversales); lo que no traza a la fuente
     va marcado `[ASUNCIÓN]`; te reporta el **path** del PRD y el **nº de asunciones**.

**Resultado:** PASS si redacta el PRD trazado a la fuente, marca lo no dicho y reporta
path + nº de asunciones · FALLO si inventa actores/alcance sin marcarlos, o mete
tecnología.
**Desviación → reportar:** issue citando `CU-2.a`.

## CU-2.b — Crear el PRD sin notas (brief oral)

**Precondición:** no le pasas ninguna fuente (`--source`).
**Mecanismo:** skill `wf-prd-create` → `prd-expert`.

1. Le pides el PRD sin darle ningún documento de partida.
   → **Esperado:** el workflow **pide un brief mínimo** de forma interactiva (no
     continúa sin input) y marca `[ASUNCIÓN]` de forma **agresiva** (casi todo lo no
     dicho).

**Resultado:** PASS si pide brief y marca asunciones agresivamente · FALLO si rellena
el PRD con invención silenciosa.
**Desviación → reportar:** issue citando `CU-2.b`.

## CU-2.c — Apuntar a un directorio o fuente inexistente

**Precondición:** el directorio destino o el `--source` no existen.
**Mecanismo:** skill `wf-prd-create` (checkpoint de precondición).

1. Le pides crear el PRD apuntando a una ruta que no existe.
   → **Esperado:** informa la ruta exacta y **se detiene**; no crea el directorio ni
     trabaja a ciegas.

**Resultado:** PASS si se detiene informando la ruta · FALLO si continúa o crea rutas
a ciegas.
**Desviación → reportar:** issue citando `CU-2.c`.

## CU-2.d — Regenerar un PRD que ya existe

**Precondición:** ya hay un `prd.md` en el destino.
**Mecanismo:** skill `wf-prd-create` (confirmación antes de sobrescribir).

1. Le pides crear el PRD de nuevo en el mismo sitio.
   → **Esperado:** **pregunta** antes de regenerar; no sobrescribe sin tu confirmación.

**Resultado:** PASS si pregunta antes de pisar · FALLO si sobrescribe sin confirmación.
**Desviación → reportar:** issue citando `CU-2.d`.

---

## CU-2.e — Revisar el PRD: gate de asunciones (lo más crítico)

**Precondición:** el `prd.md` contiene marcas `[ASUNCIÓN]` / `[ASN-XXX]`.
**Mecanismo:** skill `wf-prd-review` → `prd-expert`; `allowed-tools` incluye
`AskUserQuestion`. Check determinista `grep "[ASUNCIÓN]"` (Paso 5.5).

1. Le pides que revise el PRD.
   → **Esperado:** detecta las asunciones por grep y te presenta **cada** `[ASN-XXX]`
     con `AskUserQuestion` (confirmar / rechazar / editar); edita el PRD **solo** según
     tu decisión.
2. Dejas alguna asunción sin confirmar.
   → **Esperado:** el veredicto **no puede ser `LISTO`** mientras quede una abierta.

**Resultado:** PASS si presenta cada asunción y no marca `LISTO` con alguna abierta ·
FALLO si marca `LISTO` con asunciones abiertas, o las confirma él solo.
**Desviación → reportar:** issue citando `CU-2.e`.

## CU-2.f — Veredicto LISTO y sello de aprobación

**Precondición:** PRD limpio, sin asunciones pendientes.
**Mecanismo:** skill `wf-prd-review` → `prd-expert` (Paso 6, sello `Aprobado por:`).

1. Le pides revisar el PRD ya limpio.
   → **Esperado:** te pide el rol aprobador con `AskUserQuestion` (default PM/PO).
2. Respondes con un rol.
   → **Esperado:** escribe `Aprobado por: <rol> (<fecha>)` en el PRD.
3. **No** respondes.
   → **Esperado:** **no autoaprueba** (no escribe la línea).

**Resultado:** PASS si solo sella con respuesta humana · FALLO si estampa
`Aprobado por:` sin que respondas.
**Desviación → reportar:** issue citando `CU-2.f`.

## CU-2.g — Pasar algo que no es un PRD

**Precondición:** le pasas un `_spec.md` / `_plan.md` / `_tasks.md`.
**Mecanismo:** skill `wf-prd-review` (checkpoint de tipo de artefacto).

1. Le pides revisar como PRD un artefacto de otra fase.
   → **Esperado:** informa que no es un PRD y **se detiene**.

**Resultado:** PASS si lo rechaza · FALLO si intenta revisarlo como PRD.
**Desviación → reportar:** issue citando `CU-2.g`.

## CU-2.h — La revisión no reescribe a su cosecha

**Precondición:** PRD con problemas de estructura o contaminación técnica.
**Mecanismo:** skill `wf-prd-review` → `prd-expert` (diagnostica, no edita salvo 5.5 y 6).

1. Le pides revisar un PRD con secciones mal planteadas o con tecnología metida.
   → **Esperado:** **diagnostica** (cita el fragmento, la regla del catálogo y una
     reescritura propuesta) pero **no edita** el PRD por su cuenta; las únicas
     ediciones permitidas son la confirmación de asunciones (5.5) y el sello (6).

**Resultado:** PASS si solo diagnostica · FALLO si reescribe secciones sin que se lo
pidas.
**Desviación → reportar:** issue citando `CU-2.h`.
