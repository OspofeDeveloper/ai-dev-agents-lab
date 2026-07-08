# CU-2 — Crear y dejar listo un PRD

**Objetivo:** verificar que el sistema redacta un PRD de negocio sin inventar (marca
`[ASUNCIÓN]` lo que no traza a la fuente) y que la revisión no lo da por `LISTO`
mientras queden asunciones sin confirmar ni se autoaprueba.
**Proyecto a usar:** un producto real del que tengas notas o un brief informal
(cualquier dominio). Idealmente material con afirmaciones no triviales o lagunas, para
que el PRD tenga que marcar `[ASUNCIÓN]`.
**Cobertura automática:** ninguna directa — la calidad del PRD y el respeto del gate
de asunciones son juicio del agente `prd-expert`, así que estos escenarios son
**manuales**. El conteo de asunciones (`grep "[ASUNCIÓN"`, sin exigir el `]` de cierre para
tolerar también la forma verbosa `[ASUNCIÓN: …]`) sí es determinista.

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

### `wf-prd-create` — redactar el PRD (`prd-expert`) (5)
- [ ] CU-2.a — Crear el PRD desde notas
- [ ] CU-2.b — Crear el PRD sin notas (brief oral)
- [ ] CU-2.c — Apuntar a un directorio o fuente inexistente
- [ ] CU-2.d — Regenerar un PRD que ya existe
- [ ] CU-2.i — Crear el PRD a una ruta de salida explícita (`--output`)

### `wf-prd-review` — revisar el PRD y sellar (`prd-expert`) (4)
- [ ] CU-2.e — Revisar el PRD: gate de asunciones (lo más crítico)
- [ ] CU-2.f — Veredicto LISTO y sello de aprobación
- [ ] CU-2.g — Pasar algo que no es un PRD
- [ ] CU-2.h — La revisión no reescribe a su cosecha

> **Capa determinista** (no es un escenario manual): el conteo de asunciones
> (`grep "[ASUNCIÓN"`, Paso 5.5 de `wf-prd-review`) es el único check automático de la fase.

---

## CU-2.a — Crear el PRD desde notas

**Precondición:** existe un fichero de notas/brief válido (tus notas reales del producto).
**Mecanismo:** skill `wf-prd-create` en el **hilo principal** (gates `AskUserQuestion`: brief
si no hay `--source`, confirmación de sobreescritura); delega la redacción al agente
**`prd-expert`** (carga `kb-prd-expert`) vía la tool `Agent`, en **una sola invocación
síncrona** (espera el resultado; no relanza ni sondea el filesystem → sin race de doble
escritura). Output: `prd.md` (en `--output`, o `artifacts.prd` de `project-init.json`, o
`<dir>/prd.md`).

1. Le pides que te cree el PRD a partir de esas notas ("créame el PRD desde este brief").
   → **Esperado:** `prd-expert` redacta `prd.md` con las secciones mínimas (Resumen,
     Actores, Alcance dentro/fuera, Reglas transversales); lo que no traza a la fuente
     va marcado con la bandera inline **`[ASUNCIÓN]`** (token literal, la explicación va en
     `## Asunciones del PRD`) + su `[ASN-XXX]`; te reporta el **path** del PRD y el **nº de
     asunciones**.

> **Comprobación de formato (capa determinista):** `grep -c "\[ASUNCIÓN" prd.md` debe igualar
> el nº de marcas inline. El gate de `wf-prd-review` tolera la forma verbosa `[ASUNCIÓN: …]`,
> pero el contrato (`kb-prd-expert` Regla 12) pide la bandera escueta `[ASUNCIÓN]`: la verbosa
> duplica la sección y es señal de deriva del agente, aunque ya no rompe el conteo.

> **Correspondencia 1:1 (capa determinista):** el nº de marcas inline `[ASUNCIÓN]` debe **igualar**
> el nº de entradas `[ASN-XXX]` de `## Asunciones del PRD` (`kb-prd-expert` Regla 12, "Correspondencia 1:1"):
> `[ $(grep -c "\[ASUNCIÓN" prd.md) -eq $(grep -oE "\[ASN-[0-9]+\]" prd.md | sort -u | wc -l) ]`. Una
> marca de más = **huérfana** (el review itera sobre `[ASN-XXX]` y no la limpiará → marcador muerto en un
> PRD sellado; es justo lo que CU-2.e vigila al rechazar). Derivas observadas: agrupar varias exclusiones
> de `## Fuera del Alcance` bajo un solo `[ASN-XXX]`, o reafirmar en `## Reglas de Negocio Transversales`
> una asunción ya catalogada. `inline > entradas` es FALLO de formato.

> **Frontmatter y conteo (capa determinista):** el PRD debe abrir con el frontmatter YAML
> obligatorio (`type`, `product`, `version`, `created`, `status`) + el placeholder
> `> **Aprobado por:** [pendiente…]` (guía de estructura de `kb-prd-expert`). Y el **nº de
> asunciones que reporta el orquestador** sale del `grep`, **no** de la prosa del agente (que
> puede contar mal sobre su propio texto — verificado: dijo 11, grep=10).

2. Tras crear, observa qué hace el orquestador a continuación (frontera create→review).
   → **Esperado:** **para y recomienda `/wf-prd-review`**. **NO** confirma/rechaza/edita las
     asunciones, **no** monta una entrevista (`AskUserQuestion` por cada `[ASN-XXX]`), **no**
     integra decisiones ni sube versión ni sella `Aprobado por:`. Ese gate es exclusivo de
     `wf-prd-review` (Pasos 5.5/6); aquí solo se crea y se enruta.

**Resultado:** PASS si redacta el PRD trazado a la fuente, marca lo no dicho con la bandera
detectable por el gate, reporta path + nº de asunciones, y **tras crear para y enruta a
`/wf-prd-review`** · FALLO si inventa actores/alcance sin marcarlos, mete tecnología, o
**improvisa el gate de asunciones** (entrevista/integración/sello) en vez de enrutar a review.
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

## CU-2.i — Crear el PRD a una ruta de salida explícita (`--output`)

**Precondición:** pides el PRD indicando un destino concreto distinto del layout por defecto
(ni `artifacts.prd` ni `<dir>/prd.md`).
**Mecanismo:** skill `wf-prd-create` (Paso 5: la rama `--output` tiene prioridad sobre
`artifacts.prd` y sobre el default `<dir>/prd.md`).

1. Le pides crear el PRD con una ruta de salida explícita.
   → **Esperado:** escribe el PRD **exactamente en esa ruta** y reporta ese path; no usa
     `artifacts.prd` ni `<dir>/prd.md`.

**Resultado:** PASS si respeta la ruta dada · FALLO si la ignora y cae al layout por defecto.
**Desviación → reportar:** issue citando `CU-2.i`.

---

## CU-2.e — Revisar el PRD: gate de asunciones (lo más crítico)

**Precondición:** el `prd.md` contiene marcas `[ASUNCIÓN]` / `[ASN-XXX]`.
**Mecanismo:** skill `wf-prd-review` en el **hilo principal** (no es `context: fork`).
El `prd-expert` (Paso 4) solo **diagnostica y lista** las asunciones (read-only); el
**orquestador** corre el check determinista `grep "[ASUNCIÓN"` (Paso 5.5), presenta cada
`[ASN-XXX]` con `AskUserQuestion` y edita el PRD según tu decisión. `allowed-tools` incluye
`AskUserQuestion`.

1. Le pides que revise el PRD.
   → **Esperado:** detecta las asunciones por grep y te presenta **cada** `[ASN-XXX]`
     con `AskUserQuestion` (confirmar / rechazar / editar); edita el PRD **solo** según
     tu decisión.
2. Dejas alguna asunción sin confirmar.
   → **Esperado:** el veredicto **no puede ser `LISTO`** mientras quede una abierta.
3. Sobre una asunción, eliges **Rechazar**.
   → **Esperado:** elimina del PRD esa afirmación **y el contenido que dependía de ella**,
     y quita su entrada de `## Asunciones del PRD`; no la deja huérfana.
4. Sobre otra, eliges **Editar** y das el dato real.
   → **Esperado:** sustituye la afirmación por tu texto confirmado y quita el marcador inline.
5. Cuando una sección queda sin asunciones, elimina su entrada; si no queda ninguna, elimina
   la sección `## Asunciones del PRD` entera.

**Resultado:** PASS si presenta cada asunción, aplica fielmente confirmar/rechazar/editar
(rechazar borra también el contenido dependiente) y no marca `LISTO` con alguna abierta ·
FALLO si marca `LISTO` con asunciones abiertas, las confirma él solo, o al rechazar deja
contenido huérfano.
**Desviación → reportar:** issue citando `CU-2.e`.

## CU-2.f — Veredicto LISTO y sello de aprobación

**Precondición:** PRD limpio, sin asunciones pendientes.
**Mecanismo:** skill `wf-prd-review`, Paso 6 — el **orquestador** (hilo principal) captura
el rol aprobador con `AskUserQuestion` y estampa el sello `Aprobado por:`. El `prd-expert`
**no interviene** en el sello.

1. Le pides revisar el PRD ya limpio.
   → **Esperado:** te pide el rol aprobador con `AskUserQuestion` (default PM/PO).
2. Respondes con un rol.
   → **Esperado:** escribe `Aprobado por: <rol> (<fecha>)` en el PRD.
3. **No** respondes.
   → **Esperado:** **no autoaprueba** (no escribe la línea).
4. Re-ejecutas la revisión sobre el PRD ya sellado y respondes con un rol.
   → **Esperado:** **sobrescribe** la línea `Aprobado por:` previa (no añade una segunda);
     no acumula sellos duplicados.

**Resultado:** PASS si solo sella con respuesta humana y la re-revisión sobrescribe el sello ·
FALLO si estampa `Aprobado por:` sin que respondas, o si acumula sellos duplicados.
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
**Mecanismo:** skill `wf-prd-review`. El `prd-expert` **solo diagnostica** (read-only): cita
el fragmento, la regla del catálogo y propone reescritura, pero **nunca edita** el PRD. Las
dos únicas ediciones —asunciones (5.5) y sello (6)— las hace el **orquestador**, no el agente.

1. Le pides revisar un PRD con secciones mal planteadas o con tecnología metida.
   → **Esperado:** el `prd-expert` **diagnostica** (cita el fragmento, la regla del catálogo
     y una reescritura propuesta) pero **no edita** el PRD por su cuenta. Las únicas ediciones
     de todo el review son las del orquestador en 5.5/6, ajenas a arreglar contaminación: este
     escenario verifica que la contaminación se **diagnostica**, no se reescribe sola.

**Resultado:** PASS si solo diagnostica · FALLO si reescribe secciones sin que se lo
pidas.
**Desviación → reportar:** issue citando `CU-2.h`.
