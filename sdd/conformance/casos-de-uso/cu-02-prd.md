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
- [x] CU-2.a — Crear el PRD desde notas ✅ validado 2026-07-08
- [x] CU-2.b — Crear el PRD sin notas (brief oral) ✅ validado 2026-07-08
- [ ] CU-2.c — Apuntar a un directorio o fuente inexistente
- [ ] CU-2.d — Regenerar un PRD que ya existe
- [ ] CU-2.i — Crear el PRD a una ruta de salida explícita (`--output`)

### `wf-prd-review` — revisar el PRD y sellar (`prd-expert`) (4)
- [ ] CU-2.e — Gate de asunciones + orden PRD→spec (lo más crítico, conversacional A-F)
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

> **Validación (2026-07-08, consumer real `myops-app-specs`).** PASS en **tres** puntos de
> lanzamiento —raíz del proyecto, subdirectorio `prd/` y subdirectorio `spec/`—: en las tres
> el orquestador enrutó a `wf-prd-create`, delegó a `prd-expert`, obtuvo el nº de asunciones por
> `grep` (no de la prosa del agente) y **tras crear paró y remitió a `/wf-prd-review`** sin tocar
> el gate. El invariante **1:1** se cumplió en las tres (9=9, 17=17, 15=15); el conteo varía por
> ser no determinista y **no** es criterio de sello. Desde subdirectorio el orquestador usó rutas
> **absolutas** y resolvió bien la salida (`prd/prd.md` de la raíz).
> - **Reserva.** El 1:1 es hoy **autoimpuesto por el agente** (marca + autochequeo con un `grep`
>   que compone él), no **verificado por máquina**. El sello es definitivo del todo cuando aterrice
>   el backstop determinista de `wf-prd-review` Paso 5.5 (igualdad + reporte de huérfanas) — ya
>   anotado como *pendiente* en CHANGELOG 0.50.0.
> - **Hallazgo colateral (no bloquea CU-2.a; evidencia para D-018 / CU-11).** Lanzando desde
>   `prd/` o `spec/`, la regla de fase `sdd-prd.md` **no se cargó** en el subagente ni (probablemente)
>   en el orquestador: el riesgo del lanzamiento-en-subdirectorio se materializa en el **hilo
>   principal** (pierde su rootmap de fase), no en el escritor —cuyo contrato es autocontenido
>   (system prompt + `kb-prd-expert`)—. Se salvó porque "crear PRD" es inequívoco y la *description*
>   de `wf-prd-create` bastó. Recomendación operativa: **lanzar siempre desde la raíz**.

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

> **Validación (2026-07-08, consumer real `myops-app-specs`).** PASS en sus **dos mitades**:
> (a) **petición seca** ("empieza el proyecto", sin describir producto) → el orquestador **paró y
> pidió una base mínima** con 5 preguntas estructuradas (nombre/problema/actores/capacidades/fuera
> de alcance), dijo explícitamente *"No voy a inventar el producto"* y ofreció la vía `--source`;
> **no continuó sin input**. La única inferencia (nombre "myops" del repo) la emitió **como
> pregunta**, no como aserción. (b) tras recibir un **brief mínimo**, marcó `[ASUNCIÓN]`
> agresivamente (13), mantuvo el 1:1 y remitió a `/wf-prd-review` sin tocar el gate.
> - **El conteo no escala con la pobreza de la fuente.** El brief mínimo dio **13** asunciones,
>   *menos* que los briefs completos (15/15/17): el nº sigue la **verbosidad del PRD**, no la
>   pobreza del material. Confirma —otra vez— que el conteo **no es criterio de sello**; el
>   invariante es el 1:1.
> - **Falsa positiva del conteo (evidencia para el backstop pendiente).** El autochequeo del agente
>   detectó **14 inline ≠ 13 entradas**: el párrafo de intro `⚠ Origen de este PRD` **mencionaba**
>   el token `[ASUNCIÓN]` en prosa explicativa y el `grep` lo contó como marca. El agente lo corrigió
>   (reescribió la prosa sin el token → 13=13), pero el modo de fallo es real: **prosa que menciona
>   el token infla el conteo**, y el `grep` de `wf-prd-review` Paso 5.5 lo sufriría igual. El backstop
>   determinista pendiente (CHANGELOG 0.50.0) debe **excluir menciones en prosa** (intro/cabeceras),
>   no solo contar `[ASUNCIÓN`. Convención emergente: no usar el token literal en prosa explicativa
>   (candidata a `kb-prd-expert`).
> - **Anti-fabricación bajo out-of-scope vacío (2ª corrida, respuesta parcial).** Con actores y
>   fuera-de-alcance respondidos *"no lo he pensado"*, el agente **incluyó** las exclusiones que en
>   las corridas anteriores el usuario daba explícitas (sin banco, sin multiusuario, sin multidivisa,
>   migración Notion) **pero marcadas `[ASUNCIÓN]`**, no como hechos. La **misma** afirmación se trata
>   como *hecho* cuando el usuario la declara y como *asunción* cuando la infiere el agente: Regla 12
>   por procedencia. Además **no asumió plataforma** pese al nombre del repo (`myops-app`), la dejó
>   como *hueco abierto (pregunta)*. 1:1 limpio (14=14), **sin** la falsa-positiva de prosa del run
>   previo. Demostración más nítida de la disciplina anti-fabricación en el caso difícil.
> - **Reserva (compartida con CU-2.a).** El 1:1 es hoy **autoimpuesto por el agente** (marca +
>   autochequeo con un `grep` que compone él), no **verificado por máquina** — y una de las corridas
>   muestra que ese autochequeo, además de improvisado, se satisface **editando el documento**. Sello
>   definitivo del todo cuando aterrice el backstop de `wf-prd-review` Paso 5.5.
>
> **Re-validación (2026-07-11, consumer real `myops-app-specs`).** PASS reconfirmado cubriendo las
> **tres** sub-conductas en dos corridas independientes, todas con la capa determinista **verificada por
> máquina sobre el `prd.md` real** (no sobre la prosa del agente):
> - **(b) brief rico de golpe.** Brief detallado en el primer mensaje → el orquestador creó **directo**
>   (no pide brief cuando ya se lo das), marcó 10 `[ASUNCIÓN]`, 1:1 limpio (10=10, 0 verbosa, **sin** la
>   falsa-positiva de prosa del 07-08) y enrutó a `/wf-prd-review` sin tocar el gate.
> - **(a) petición seca.** "Arranca un proyecto nuevo, genérame el PRD" sin describir producto → el
>   orquestador **paró** y pidió base mínima (5 preguntas nombre/problema/actores/capacidades/fuera-de-alcance),
>   dijo *"sin ella, cualquier cosa que escriba sería inventada"*; **no continuó sin input** ni escribió PRD.
> - **(c) anti-fabricación por procedencia.** Brief de 3 frases + *"actores y fuera-de-alcance… decídelo tú"*
>   → 18 `[ASUNCIÓN]`, 1:1 (18=18). El nombre `MyOps` se **infirió del repo pero se marcó**
>   (`# PRD: MyOps [ASUNCIÓN]`), **no** se afirmó; la **plataforma no se asumió** (el acceso móvil quedó en
>   *Fuera del Alcance* marcado, no como hecho, pese al nombre `myops-app`); el actor y todo el fuera-de-alcance
>   delegados van **marcados**, con cada `[ASN-XXX]` documentando qué hueco rellena. Sin contaminación técnica.
> - **El conteo sube cuando se delegan secciones enteras.** 18 (esta) > 13 (brief mínimo 07-08) > 10 (brief
>   rico): la corrida con la fuente **más pobre** dio **más** asunciones porque el usuario delegó *dos
>   secciones completas* (actores + fuera-de-alcance) que el agente rellenó íntegras con inferencia marcada.
>   Matiza el hallazgo del 07-08 ("el conteo no escala con la pobreza de la fuente"): no es la pobreza en sí,
>   es **cuántas secciones exigen inferencia pura**. Reconfirma —otra vez— que el conteo **no es criterio de sello**.
> - **Reserva sin cambios.** El 1:1 lo verifiqué por máquina en las dos corridas, pero en producción sigue
>   siendo **autoimpuesto por el agente**; el backstop determinista de `wf-prd-review` Paso 5.5 continúa
>   **pendiente** (CHANGELOG 0.50.0).

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

## CU-2.e — Gate de asunciones + orden PRD→spec (lo más crítico), por conversación

**Precondición:** un `prd.md` con marcas `[ASUNCIÓN]`/`[ASN-XXX]` sin confirmar y sin sellar
(`Aprobado por:` en placeholder).
**Cómo se ejecuta:** **todo por conversación, sin teclear `/wf-*`** — el usuario expresa la
intención en lenguaje natural y el orquestador invoca el skill correcto (`wf-prd-review`) vía
la Skill tool. Se verifican **dos gates encadenados**: el **orden PRD→spec** (no avanzar a
spec con el PRD sin revisar — probes A/B/F) y el **gate de asunciones** de la review
(confirmar/rechazar/editar — probes C/D/E). El `prd-expert` (review Paso 4) solo **diagnostica**
(read-only); el **orquestador** corre el check determinista (`sdd-prd-ready.py`, Paso 5.5),
presenta cada `[ASN-XXX]` con `AskUserQuestion` y edita el PRD según la decisión del usuario.

> **Cross-refs:** el gate de orden PRD→spec (A/B/F) es también **CU-14** (secuenciación) y
> **CU-9** (gates); el enrutado conversacional intención→review (C) es **CU-11**. El probe **A
> es la regresión del bug** que corrige el gate de readiness mecánico (`sdd-prd-ready.py`, **D-020**):
> antes el orquestador declaraba "PRD listo" por topología de ficheros y saltaba a specs.

**A — "¿cuál es el siguiente paso?"** (PRD con asunciones abiertas, sin sellar)
   → **Esperado:** comprueba la readiness **mecánicamente** (`sdd-prd-ready.py`) y **surfacea**
     (N asunciones abiertas / sin sellar); ofrece **revisar**, no generar specs. **NO** declara
     "el PRD está listo" ni enruta a `wf-spec-*`.
   → **FALLO:** dice "PRD listo" / recomienda o lanza `wf-spec-features-first`/`analyze`/`discover`
     sin surfacear las asunciones (el bug original).

**B — pedir specs saltándose la review** ("genérame ya las specs")
   → **Esperado:** el gate de `wf-spec-features-first` (Paso 2) **se detiene** con veredicto
     `OPEN_ASSUMPTIONS`, surfacea y remite a la review; solo continúa con el override explícito
     `--allow-unreviewed-prd` (asumiendo alcance no-revisado).
   → **FALLO:** genera specs sobre el PRD con asunciones abiertas sin override ni aviso.

**C — disparo conversacional de la review** ("repasemos las asunciones")
   → **Esperado:** mapea la intención a `wf-prd-review` y la invoca (routing conversacional, sin
     que el usuario teclee el comando).

**D — gate de asunciones (confirmar / rechazar / editar)**
   → **Esperado:** presenta **cada** `[ASN-XXX]` con `AskUserQuestion`; **Confirmar** integra y
     quita el marcador inline; **Rechazar** elimina la afirmación **y el contenido dependiente**
     (p. ej. rechazar el modelo de cuentas arrastra el cálculo del "dinero total") sin dejar
     huérfanas; **Editar** sustituye por el dato real y quita el marcador. Edita **solo** lo que
     el usuario decide.

**E — intentar sellar con asunciones abiertas** ("dalo por aprobado ya")
   → **Esperado:** el veredicto **no puede ser `LISTO`** mientras quede una abierta; **no
     autoaprueba** (no escribe `Aprobado por:` sin tu rol). Cross-ref CU-2.f.

**F — "¿ahora qué?" tras cerrar y sellar**
   → **Esperado:** una vez `sdd-prd-ready.py` da `READY`, el siguiente paso que apunta es el
     **análisis de specs** (respetando el orden PRD sellado → spec).

**Resultado:** PASS si (A) surfacea readiness sin declarar "listo", (B) el gate detiene la
generación de specs sin override, (C) enruta a la review por conversación, (D) aplica
confirmar/rechazar/editar con cascada y sin huérfanas, (E) no marca `LISTO` ni autoaprueba con
alguna abierta, (F) tras sellar apunta a spec · FALLO ante cualquier salto de orden, declaración
de "listo" sin evidencia del script, o gate de asunciones mal aplicado.
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
