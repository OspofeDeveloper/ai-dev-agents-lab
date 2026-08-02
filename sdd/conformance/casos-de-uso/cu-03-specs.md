# CU-3 — Generar las specs de un PRD

**Objetivo:** verificar que el camino PRD → specs por feature respeta el analyze
obligatorio, para en los gaps críticos, descubre features (no las inventa el PRD),
permite trabajar por subset, genera specs en paralelo y deja la trazabilidad e índice
correctos.
**Proyecto a usar:** el mismo producto real de CU-2, con su PRD ya `LISTO`. Idealmente
con alguna decisión de negocio sin cerrar, para que el analyze produzca al menos un gap
`[CRÍTICO]`.
**Cobertura automática:** parcial — los índices y marcadores deterministas
(`sdd-features-index.py`, `sdd-gap-conventions`) tienen tests, pero la calidad del
análisis, el discovery y los specs es juicio de los agentes → **manual**.

> [!IMPORTANT]
> **El analyze es obligatorio y las features no están en el PRD.** Ningún `F-XXX`
> existe hasta correr el discovery. Para una petición general ("crea las specs"), el
> entrypoint es `wf-spec-features-first <prd.md>`, **no** `wf-spec-discover`.

---

## 🧪 Qué se prueba aquí (por componente)

CU-3 es un **objetivo de usuario** (generar las specs de un PRD), no una sola skill: sus
escenarios ejercitan **ocho componentes** de la fase Spec. Marca cada escenario al ejecutarlo.
El estado de cobertura autoritativo (ejes happy/edge/harness/args) vive en
[`ROADMAP.md`](../ROADMAP.md) — esta vista es la **transpuesta** para leer/ejecutar el CU.

### `wf-spec-analyze` — analyze obligatorio y pureza (`sdd-spec-explorer`) (2)
- [ ] CU-3.a — El analyze es obligatorio y para en gaps críticos
- [ ] CU-3.k — Analyze: contaminación técnica detiene y las preguntas de riesgo van neutras

### `wf-spec-discover` — mapa de features y ownership (`sdd-spec-explorer`) (2)
- [ ] CU-3.c — Discovery: mapa de features y elección de subset
- [ ] CU-3.i — Discovery: ownership ambiguo de shared model para en checkpoint humano

### `wf-spec-features-first` — orquestador del flujo features-first (2)
- [ ] CU-3.d — Generación por feature (features-first) en paralelo
- [ ] CU-3.l — Features-first: `--features` con IDs inexistentes en el discovery

### `wf-spec-fast-track` — spec directo de una feature (`sdd-spec-writer`) (2)
- [ ] CU-3.e — Spec directo de una feature (fast-track)
- [ ] CU-3.j — Fast-track: documento multi-feature, pares de flags y feature ID inexistente

### `sdd-spec-auditor` — validate / conflict / readiness (read-only) (4)
- [ ] CU-3.f — Validar, conflictos y readiness
- [ ] CU-3.m — Validate en modo ligero: proporcionalidad sin relajar invariantes
- [ ] CU-3.n — Conflict: precondición de specs insuficientes
- [ ] CU-3.o — Readiness: sin índice, ciclos de dependencia y scope derivado

### `wf-spec-gap-resolve` — completar incompletos y confirmar inferidos (`sdd-spec-writer`) (2)
- [ ] CU-3.g — Completar HUs incompletas (gap-resolve)
- [ ] CU-3.q — Gap-resolve: confirmación de `[INFERIDO]` (tres vías)

### `wf-spec-delta` — evolución incremental del spec (`sdd-spec-writer`) (1)
- [ ] CU-3.h — Evolucionar un spec con requisitos nuevos (delta)

### orquestador de la fase Spec — guardrail de cambio de producto y oferta de rigor (3)
- [ ] CU-3.b — Expansión de alcance desde las respuestas del analysis
- [ ] CU-3.p — Delta / gap-resolve: un cambio de producto encubierto detiene y remite a wf-prd-change
- [ ] CU-3.r — El rigor (standard/ligero) se elige al crear el spec, no en el init (D-006)

> **Capa determinista** (no son escenarios manuales): los índices y marcadores
> (`sdd-features-index.py`, `sdd-gap-conventions`) están cubiertos por unittests; la calidad
> del análisis, el discovery y los specs es juicio de los agentes y queda en esta vista manual.

---

## CU-3.a — El analyze es obligatorio y para en gaps críticos

**Precondición:** PRD `LISTO`, sin `_analysis.md` todavía.
**Mecanismo:** skill `wf-spec-analyze` → subagente **`sdd-spec-explorer`**. Output:
`<basename>_analysis.md`.

1. Le pides empezar a generar las specs del PRD.
   → **Esperado:** como no hay `_analysis.md`, ejecuta primero el analyze (o
     `wf-spec-features-first` lo lanza y **se detiene**), produce `_analysis.md` con
     gaps `[P-XXX]` y severidad, y te pide revisarlo antes de continuar.
2. El analysis deja gaps `[CRÍTICO]` abiertos y pides seguir igualmente.
   → **Esperado:** el orquestador pide decisión explícita: responder los críticos
     primero, o continuar con `--allow-open-critical-gaps`. No avanza en silencio.
     El conteo de críticos abiertos sale de `sdd-analysis-gaps.py --check`
     ([[D-042]]), **no** de la lectura del informe — y ese check corre **antes** de la
     rama que gobierna.
   → **FALLO:** decidir la rama citando una lectura propia del `_analysis.md`; o
     tratar un veredicto `VACUOUS` (documento no parseado) como "sin gaps críticos".
3. **El mensaje de cierre te dice qué responder, sin que abras el fichero** ([[D-042]]).
   → **Esperado:** path exacto del `_analysis.md`, los IDs `[CRÍTICO]` **cada uno con su
     pregunta en una línea**, y qué se sustituye (`- **Respuesta**: _(pendiente)_`).
   → **FALLO:** un "responde las preguntas marcadas como `_(pendiente)_`" genérico que
     te obliga a bucear entre todos los gaps para saber cuáles bloquean.
4. **Quién escribe las respuestas** ([[D-042]]). Dicta una respuesta en la conversación
   en vez de editar el fichero.
   → **Esperado:** el hilo principal la aplica con
     `sdd-analysis-gaps.py --answer P-XXX "texto"` por `Bash`, y el fichero cambia
     **solo** en esa línea.
   → **FALLO (tres formas):** que main haga `Read`/`Edit`/`Write` del `_analysis.md`;
     que **rehúse** ayudar remitiéndote al editor cuando existe vía sancionada; o —el
     grave— que **complete o reinterprete** una respuesta que no diste.
   → **Ojo al verificar:** que el frontmatter no declare `Write` **no lo impide**
     (`allowed-tools` no es enforcement, [[D-038]]). Hay que mirar los logs.

5. **Cómo delega el orquestador** ([[D-043]]) — se lee en los logs de
   `wf-spec-features-first`, no hay que provocarlo.
   → **Esperado:** invoca el analyze con la tool `Agent`, `subagent_type:
     sdd-spec-explorer` y **`run_in_background: false`**, y **espera su retorno**. Un
     solo reporte final.
   → **FALLO (cuatro señales, cualquiera basta):** `Monitor` sobre el artefacto que el
     delegado va a escribir; `ls`/`find` repetido sobre el directorio de artefactos
     esperando a que aparezca; un segundo agente relanzado sobre el mismo trabajo; o
     el reporte final **emitido dos veces** (delata que el stream asíncrono cerró
     después). Sondear el disco no es esperar: es un race de doble escritura.
   → **FALLO adicional (Regla de oro):** que el orquestador haga `cat`/`Read` del PRD o
     del `_analysis.md` — lo que necesita sale del script o del reporte del delegado.

**Resultado:** PASS si genera el analysis, para en los críticos por veredicto de script,
te dice cuáles son sin abrir el fichero, ni escribe ni inventa las respuestas, y delega
en síncrono sin sondear el disco · FALLO si salta el analyze, avanza con críticos sin
override explícito, decide por lectura propia, toca el informe a mano, o se queda en
busy-wait.
**Desviación → reportar:** issue citando `CU-3.a`.

> **Pasada 1 (2026-08-02, v0.76.0) — PASS en el paso 1; origen de [[D-042]].** El analyze
> corrió primero y el flujo **se detuvo** con `spec/features/` intacto; pureza `APROBADO`
> con la línea borderline de L95 reconocida como patrón válido (no sobre-disparó
> `REQUIERE_LIMPIEZA_PRD`); 5 `[CRÍTICO]` + 6 `[INFORMATIVO]`, con P-001 y P-009 marcados
> `[PUEDE_REQUERIR_CR]` y redactados en **neutro**. El paso 2 **no se ejercitó**: el
> orquestador se adelantó ofreciendo él mismo la bifurcación antes de que el usuario
> empujara — conducta correcta y más fuerte que la pedida, pero el probe no llegó a correrse.
>
> **El hallazgo:** main ofreció *"me los dictas y **yo los anoto** en el análisis"*, una vía
> que **el contrato no contemplaba** — los tres sitios que hablan del tema (SKILL de analyze,
> Paso 2.5 de features-first y la cabecera del propio artefacto) dicen siempre que escribe el
> usuario. Vacío de la misma forma que cerró [[D-038]] en la fase PRD. Al investigarlo apareció
> el defecto mayor: la detección de "¿quedan `[CRÍTICO]` sin responder?" era **juicio de agente
> sobre prosa** gobernando dos ramas duras. Ambos cerrados en [[D-042]]; los pasos 2, 3 y 4 de
> arriba son nuevos y **no tienen aún ninguna pasada**.
>
> **El segundo hallazgo — busy-wait ([[D-043]]).** El log de `wf-spec-features-first` es literal:
> `Skill(wf-spec-analyze)` → `Monitor(wait for prd_analysis.md)` → `cat …/prd.md` (el orquestador
> cargándose el PRD entero) → `ls -la prd/` → *"I'll wait for the analysis skill to finish"* →
> `ls -la prd/` otra vez → reporte final **duplicado**. Causa: el Paso 5 prescribía la tool exacta
> y los otros cuatro puntos de delegación decían solo *"invoca `/wf-spec-analyze`"*; el fork
> rellenó el hueco con `Skill` (que ni estaba en su `allowed-tools` — tercera confirmación de
> [[D-038]]) y sin handle síncrono se puso a sondear. Al contarlo: **7 skills delegaban por
> `Agent` y solo `wf-prd-create` pasaba `run_in_background: false`**. Cerrado en [[D-043]] con
> barrido de las 7 + regla blocking `AGENT-DISPATCH-UNSYNCED`. El paso 5 de arriba es nuevo y
> **no tiene aún ninguna pasada**: el linter garantiza que el flag está escrito, no que el
> orquestador lo teclee.

## CU-3.b — Expansión de alcance desde las respuestas del analysis

**Precondición:** al responder el `_analysis.md` introduces capacidad nueva (entidad
persistente, catálogo reutilizable, owner o flujo no comprometidos en el PRD).
**Mecanismo:** guardrail del orquestador + `wf-spec-features-first`.

1. Respondes el analysis ampliando el alcance y pides continuar a specs.
   → **Esperado:** **no** continúa a discovery/specs; te remite a `wf-prd-change`
     primero, salvo override explícito `--allow-derived-scope-from-analysis` (que marca
     los derivados con `Origen de alcance: PRD + analysis respondido` y
     `Avisos de gobernanza`).

**Resultado:** PASS si frena la expansión encubierta · FALLO si genera specs con
alcance derivado sin override ni avisos.
**Desviación → reportar:** issue citando `CU-3.b`.

## CU-3.c — Discovery: mapa de features y elección de subset

**Precondición:** `_analysis.md` revisado.
**Mecanismo:** skill `wf-spec-discover` → **`sdd-spec-explorer`**. Output:
`<basename>_discovery.md` (mapa + scope RF→Feature + shared models) y `_features.md`.

1. Le pides trabajar "la fase 1" / "solo estas features".
   → **Esperado:** como los `F-XXX` no existen aún, ejecuta el discovery, te **presenta
     el mapa** (Feature ID, nombre, actor, RFs cubiertos) y **te pregunta qué IDs**
     incluir en esta iteración (no elige por ti).
2. El discovery identifica >5 features y no pediste subset.
   → **Esperado:** recomienda iterar con `--features …`; solo usa `--all-features` como
     override explícito.

**Resultado:** PASS si descubre, presenta el mapa y pregunta el subset · FALLO si
inventa features sin discovery, o procesa todas sin avisar con >5.
**Desviación → reportar:** issue citando `CU-3.c`.

## CU-3.d — Generación por feature (features-first) en paralelo

**Precondición:** discovery hecho y subset elegido (o todas).
**Mecanismo:** skill `wf-spec-features-first` (orquestador, `allowed-tools` incluye
`Agent`) → internamente `wf-spec-discover` + `wf-spec-fast-track` (agente
**`sdd-spec-writer`**) por feature, en paralelo.

1. Confirmas los IDs y le pides generar sus specs.
   → **Esperado:** genera `features/<nombre>/spec/<nombre>_spec.md` por feature (CAs en
     `GIVEN/WHEN/THEN`) y actualiza `_features.md` (índice + trazabilidad RF→HU→Feature
     + estado). Las features **no incluidas** quedan `PENDIENTE_GENERACIÓN` y se pueden
     generar en pasadas posteriores sin perder lo anterior.

**Resultado:** PASS si genera los specs del subset y marca el resto pendiente · FALLO
si pierde features previas, o genera fuera del subset pedido.
**Desviación → reportar:** issue citando `CU-3.d`.

## CU-3.e — Spec directo de una feature (fast-track)

**Precondición:** una capacidad concreta, con o sin discovery.
**Mecanismo:** skill `wf-spec-fast-track` → **`sdd-spec-writer`**.

1. Le pides el spec de una sola capacidad ("hazme el spec de login").
   → **Esperado:** genera el spec de esa feature (`--capability <nombre>` o
     `--scope-from <discovery> --feature F-00X`), respetando `--light`/`--standard`
     (el modo ligero mantiene los invariantes, solo ajusta proporción). Si **no** pasas
     flag, la elección del rigor la **ofrece el orquestador** al crear el spec (CU-3.r),
     no el init.

**Resultado:** PASS si genera un spec válido de la feature · FALLO si relaja
invariantes en `--light`, o mete tecnología.
**Desviación → reportar:** issue citando `CU-3.e`.

## CU-3.f — Validar, conflictos y readiness

**Precondición:** uno o más specs de feature generados.
**Mecanismo:** `wf-spec-validate` / `wf-spec-conflict` / `wf-spec-readiness` →
subagente **`sdd-spec-auditor`**.

1. Le pides validar un spec.
   → **Esperado:** lo audita contra el contrato de Spec y reporta OK o los items a
     corregir, sin reescribirlo a su cosecha.
2. Le pides detectar conflictos entre features.
   → **Esperado:** con `--features-dir` reporta HUs duplicadas, CAs contradictorios,
     solapes de scope y shared models inconsistentes; no redefine specs.
3. Le pides saber qué está listo / en qué orden implementar.
   → **Esperado:** produce `_readiness_report.md` con estado por feature y orden de
     implementación.

**Resultado:** PASS si audita/repora sin modificar los specs · FALLO si edita specs al
validar, o silencia un conflicto real.
**Desviación → reportar:** issue citando `CU-3.f`.

## CU-3.g — Completar HUs incompletas (gap-resolve)

**Precondición:** un spec con HUs `[INCOMPLETO]` y respuestas ya escritas en el
`_analysis.md`.
**Mecanismo:** skill `wf-spec-gap-resolve` → **`sdd-spec-writer`**.

1. Le pides completar las HUs incompletas del spec.
   → **Esperado:** rellena las HUs `[INCOMPLETO]` **usando las respuestas del
     analysis** (no inventa); si una respuesta falta, no fabrica el contenido.

**Resultado:** PASS si completa solo con material respondido · FALLO si inventa el
contenido de una HU sin respuesta.
**Desviación → reportar:** issue citando `CU-3.g`.

## CU-3.h — Evolucionar un spec con requisitos nuevos (delta)

**Precondición:** un spec de feature ya generado al que llegan requisitos nuevos
(post-spec, sin cambio de PRD).
**Mecanismo:** skill `wf-spec-delta` → subagente **`sdd-spec-writer`**. Modo `analyze`
produce `<feature>_delta_analysis.md`; modo `apply` integra preservando lo previo.

1. Le pides analizar un cambio sobre el spec ("añade estos requisitos al spec de auth").
   → **Esperado:** `analyze` genera `<feature>_delta_analysis.md` con las HUs/CAs a
     **añadir, modificar y eliminar**, sin tocar el spec todavía.
2. Le pides aplicar ese delta.
   → **Esperado:** `apply` verifica que el segundo argumento termina en
     `_delta_analysis.md` (si no, se detiene pidiéndolo) e **integra los cambios
     preservando** el resto del spec; no regenera desde cero.

**Resultado:** PASS si analyze diagnostica y apply integra preservando lo previo · FALLO
si apply pisa el spec entero, o aplica sin un delta analysis válido.
**Desviación → reportar:** issue citando `CU-3.h`.

## CU-3.i — Discovery: ownership ambiguo de shared model para en checkpoint humano

**Precondición:** un PRD donde un modelo de dominio aparece en varias features y queda en
**empate** tras los 4 criterios de ownership de `kb-decompose-expert`.
**Mecanismo:** skill `wf-spec-discover` → `sdd-spec-explorer` (Paso 7, ownership checkpoint).

1. Le pides descubrir las features de ese PRD.
   → **Esperado:** al llegar al shared model ambiguo, **presenta la tabla** (modelo,
     candidatos, criterio aplicado y por qué hay empate) y **espera tu decisión** antes de
     continuar; no asigna owner por su cuenta.
2. Respondes el owner.
   → **Esperado:** continúa el discovery asignando ese owner; los modelos con owner claro no se preguntan.

**Resultado:** PASS si para a preguntar solo en el empate real y respeta tu decisión ·
FALLO si asigna ownership ambiguo en silencio, o pregunta por modelos ya resueltos.
**Desviación → reportar:** issue citando `CU-3.i`.

## CU-3.j — Fast-track: documento multi-feature, pares de flags y feature ID inexistente

**Precondición:** según el sub-escenario: (1) un documento que describe **varias** features
sin `--scope-from`; (2) `--scope-from` sin `--feature` (o viceversa); (3) un `--feature`
que no existe en el `_discovery.md`.
**Mecanismo:** skill `wf-spec-fast-track` → `sdd-spec-writer` (Scope Check Paso 4; validación de args Paso 1; resolución de feature Paso 3).

1. Le pides el fast-track de un documento que en realidad describe varias capacidades, sin acotar.
   → **Esperado:** no genera un spec contaminado de multi-feature: **remite** a `/wf-spec-discover` + `/wf-spec-features-first`.
2. Pides el modo scoped pero solo aportas uno de los dos flags acoplados.
   → **Esperado:** error "`--scope-from` y `--feature` deben usarse juntos"; no asume el que falta.
3. Pides el fast-track de un `F-00X` que no está en el discovery.
   → **Esperado:** se detiene listando las features disponibles; no inventa el scope.

**Resultado:** PASS si redirige el multi-feature, exige los flags acoplados y rechaza el
ID inexistente · FALLO si genera un spec multi-feature, asume un flag ausente, o procesa un feature ID que no existe.
**Desviación → reportar:** issue citando `CU-3.j`.

## CU-3.k — Analyze: contaminación técnica detiene y las preguntas de riesgo van neutras

**Precondición:** un PRD con contaminación técnica (stack, endpoints, esquemas) y/o un gap
funcional cuya respuesta podría expandir el producto.
**Mecanismo:** skill `wf-spec-analyze` → `sdd-spec-explorer` (Check 2 pureza; Paso 5 framing de gaps).

1. Le pides analizar un PRD con tecnología metida.
   → **Esperado:** Check 2 detecta la contaminación, el veredicto es `REQUIERE_LIMPIEZA_PRD`
     y te remite a limpiar el PRD (o `wf-prd-review`/`prd-expert`) **antes** de continuar a specs; no genera specs sobre un PRD sucio.
2. El analysis formula un gap cuya respuesta podría introducir capacidad nueva.
   → **Esperado:** marca el gap `[PUEDE_REQUERIR_CR]` y redacta la pregunta **neutra** (no
     ofrece como opción "normal" una solución expansiva tipo "¿catálogo persistente o texto libre?").

**Resultado:** PASS si detiene por contaminación y formula neutro los gaps de riesgo · FALLO
si genera specs con un PRD contaminado, o empuja hacia una respuesta expansiva.
**Desviación → reportar:** issue citando `CU-3.k`.

## CU-3.l — Features-first: `--features` con IDs inexistentes en el discovery

**Precondición:** existe `_discovery.md`; pides un subset con al menos un ID que **no** está en él.
**Mecanismo:** skill `wf-spec-features-first` (Paso 4a — validación del subset contra el discovery).

1. Le pides generar las features de un subset que incluye un ID inventado (p. ej. `F-099`).
   → **Esperado:** **se detiene** indicando qué IDs no aparecen en el discovery y listando los
     IDs válidos; no genera nada del subset hasta que corrijas.

**Resultado:** PASS si valida el subset contra el discovery y para con el ID inválido · FALLO
si ignora el ID inexistente, o genera solo los válidos sin avisar del inválido.
**Desviación → reportar:** issue citando `CU-3.l`.

## CU-3.m — Validate en modo ligero: proporcionalidad sin relajar invariantes

**Precondición:** un spec con header `Modo: ligero`, con el núcleo de 4 presente, una sección
no-núcleo omitida **con** `N/A — modo ligero` y otra omitida **sin** esa marca.
**Mecanismo:** skill `wf-spec-validate` → `sdd-spec-auditor` (Paso 4, detección de modo).
**Read-only** (`allowed-tools: [Read, Bash]`, sin Write).

1. Le pides validar el spec ligero.
   → **Esperado:** no marca como hallazgo las secciones núcleo legítimamente omitidas con
     `N/A — modo ligero`, pero **sí** reporta como hallazgo la sección omitida **sin** la
     marca; no reescribe el spec (no tiene Write).
2. El spec ligero tiene un CA sin GIVEN/WHEN/THEN completo.
   → **Esperado:** el Check 3 lo reporta — la testabilidad es **idéntica** en ambos modos;
     el modo ligero ajusta proporción, no relaja invariantes.

**Resultado:** PASS si respeta el núcleo de 4, exige la marca `N/A` y mantiene los invariantes ·
FALLO si marca como error una omisión legítima, deja pasar una sección sin marca, o tolera un CA no testable en ligero.
**Desviación → reportar:** issue citando `CU-3.m`.

## CU-3.n — Conflict: precondición de specs insuficientes

**Precondición:** un directorio de features con 0 o 1 spec.
**Mecanismo:** skill `wf-spec-conflict` → `sdd-spec-auditor` (Paso 2).

1. Le pides detectar conflictos con un solo spec.
   → **Esperado:** informa que **se necesitan al menos 2 specs** y no fabrica un conflicto.
2. Le pides conflictos en un directorio sin specs.
   → **Esperado:** informa que no encontró specs y remite a generarlos (`wf-spec-features-first` / `wf-spec-fast-track`).

**Resultado:** PASS si exige ≥2 specs y guía cuando faltan · FALLO si reporta conflictos con
<2 specs, o falla sin explicar qué falta.
**Desviación → reportar:** issue citando `CU-3.n`.

## CU-3.o — Readiness: sin índice, ciclos de dependencia y scope derivado

**Precondición:** según el sub-escenario: (1) directorio de features sin `_features.md`;
(2) features con dependencias en ciclo; (3) una feature con alcance derivado del analysis no
consolidado en el PRD.
**Mecanismo:** skill `wf-spec-readiness` → `sdd-spec-auditor` (Pasos 2, 5, 6). Solo lee y sintetiza.

1. Le pides el readiness sin que exista `_features.md`.
   → **Esperado:** **se detiene** indicando ejecutar `wf-spec-features-first`/`wf-spec-fast-track` primero; no inventa el índice.
2. Hay un ciclo de dependencias entre features.
   → **Esperado:** **reporta el ciclo** y excluye esas features del orden de implementación,
     pero **no aborta** el resto del informe.
3. Una feature declara alcance derivado del analysis sin consolidar en PRD.
   → **Esperado:** la clasifica `REQUIERE_CAMBIO_PRD`, **no** `LISTA`.

**Resultado:** PASS si para sin índice, reporta el ciclo sin abortar y marca el scope derivado ·
FALLO si fabrica el índice, aborta todo el informe por un ciclo, o marca `LISTA` una feature con scope sin consolidar.
**Desviación → reportar:** issue citando `CU-3.o`.

## CU-3.p — Delta / gap-resolve: un cambio de producto encubierto detiene y remite a wf-prd-change

**Precondición:** un spec ya generado; le pasas un "requisito nuevo" (delta) o una "respuesta de
gap" (gap-resolve) que en realidad mueve alcance, exclusión o regla de negocio del PRD.
**Mecanismo:** skill `wf-spec-delta` (Paso 7A) / `wf-spec-gap-resolve` (Paso 4) → `sdd-spec-writer`.

1. Pides añadir al spec un "requisito" que en realidad cambia el alcance del producto (`delta analyze`).
   → **Esperado:** detecta que no es un delta de spec sino un cambio de producto; **detiene** y
     remite a `wf-prd-change` antes de seguir.
2. Pides completar un `[INCOMPLETO]` con una "respuesta" que contradice el PRD o mueve algo MVP↔fase futura (`gap-resolve`).
   → **Esperado:** **detiene** y remite a `wf-prd-change`; no integra el cambio como si fuera un gap normal.

**Resultado:** PASS si ambas vías frenan el cambio de producto encubierto y remiten a `wf-prd-change` ·
FALLO si integran la expansión/contradicción como delta o gap normal.
**Desviación → reportar:** issue citando `CU-3.p`.

## CU-3.q — Gap-resolve: confirmación de `[INFERIDO]` (tres vías)

**Precondición:** un spec de caracterización con CAs `[INFERIDO]` sin confirmar.
**Mecanismo:** skill `wf-spec-gap-resolve` → `sdd-spec-writer` (Paso 3, caso `[INFERIDO]`). La fuente
de confirmación es **el usuario**, no un `_analysis.md`.

1. Pides confirmar los `[INFERIDO]` y respondes **"Confirmado"**.
   → **Esperado:** elimina el marcador y actualiza `Evidencia:` a `confirmado por <usuario> el <fecha>`
     (mantiene la evidencia parcial original); no lo resuelve desde un `_analysis.md`.
2. Respondes **"Incorrecto"** con el comportamiento real.
   → **Esperado:** corrige el CA con ese comportamiento (o lo elimina si la capacidad no existe).
3. Respondes **"No lo sé"**.
   → **Esperado:** el marcador `[INFERIDO]` **se queda** y ese CA **sigue bloqueando** `wf-prepare-plan`.

**Resultado:** PASS si las tres respuestas se tratan distinto y "No lo sé" mantiene el bloqueo · FALLO
si confirma un `[INFERIDO]` desde el analysis, o lo da por resuelto sin confirmación humana.
**Desviación → reportar:** issue citando `CU-3.q`.

## CU-3.r — El rigor (standard/ligero) se elige al crear el spec, no en el init (D-006)

**Precondición:** proyecto SDD ya inicializado con `pipeline_mode: standard` (el default; el init
ya no pregunta el rigor — ver `cu-01-inicializar.md` CU-1.n). Le pides crear el spec de una feature.
**Mecanismo:** orquestador de la fase Spec (`pipeline/spec/CLAUDE.md` → instalado como
`.claude/rules/sdd-spec.md`, sección "Elección del rigor del pipeline"). Como `wf-spec-fast-track` y
`wf-spec-features-first` son `context: fork` y **no** pueden usar `AskUserQuestion` ([[D-002]]), la
oferta ocurre en el **hilo principal** antes de delegar.

1. Pides el spec de una feature **sin** especificar el modo.
   → **Esperado:** antes de invocar la workflow, el orquestador **ofrece** Standard (recomendado) /
     Ligero con `AskUserQuestion` y pasa el flag elegido. No asume ligero por su cuenta ni genera sin ofrecer.
2. Pides el spec pasando explícitamente `--light` (o `--standard`).
   → **Esperado:** **no** pregunta — respeta el flag.
3. El proyecto tiene `pipeline_mode: light` fijado a mano (override de proyecto) y no pasas flag.
   → **Esperado:** usa `light` sin preguntar (el equipo ya fijó el default de proyecto).
4. Pides generar un lote con `wf-spec-features-first` sin flag.
   → **Esperado:** pregunta el modo **una sola vez** para toda la pasada, nunca feature a feature.
5. Pides `--light` sobre una feature que **toca shared models, introduce entidades nuevas o expande alcance**.
   → **Esperado:** el rigor ligero **se prohíbe solo**: la workflow lo fuerza a `standard` pese al flag (regla en `kb-spec-expert`), porque en ese perfil de feature se relaja ceremonia pero **no** rigor. No genera un spec ligero sobre una feature con shared models / entidades nuevas / alcance expandido. (Es el guardrail de la última línea de `pipeline/spec/routing.md`.)

**Resultado:** PASS si ofrece la elección al crear (no en el init), respeta el flag explícito y el
override de proyecto, pregunta una sola vez por lote, y **fuerza standard cuando la feature toca shared
models / entidades / alcance pese a `--light`** · FALLO si genera ligeros sin ofrecer la elección,
re-pregunta pese a un flag explícito, pregunta feature a feature en un lote, o **deja pasar un spec ligero
sobre una feature que expande alcance / toca shared models**.
**Desviación → reportar:** issue citando `CU-3.r`.
