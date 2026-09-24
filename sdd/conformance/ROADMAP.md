# ROADMAP de cobertura — batería de conformance vs. skills del ecosistema

Este documento es el **checklist de auditoría** de la batería de conformance (`casos-de-uso/cu-*.md`)
contra las **51 workflow skills `wf-*`** del core del ecosistema. La batería está organizada por
*journey* (CU), no por skill; aquí invertimos la vista: **una fila por `wf-*`**, en orden de pipeline,
para garantizar que ningún skill se queda sin casos en los cuatro ejes de prueba.

## Alcance

- **Solo `wf-*` del core** (51 skills). Agentes, scripts (`sdd-*.py`) y `kb-*` se anotan como cobertura
  *derivada* en la columna Mecanismo cuando un `wf-*` los ejercita; no tienen fila propia.
- **Overlay KMM diferido** a un track aparte (8 `wf-kmm-*` + kb anidadas). CU-12 ya lo cubre parcialmente.

## Leyenda

- **Ejes:** `✅` cubierto · `🟡` parcial · `❌` hueco · `—` no aplica.
  - **Happy** — invocación canónica con precondiciones satisfechas → artefacto correcto + sello.
  - **Edge** — args parciales/ausentes, layout legacy, subset, idempotencia, re-ejecución, monorepo.
  - **Harness** — invocar saltándose una precondición o gate → debe **bloquear** (`[SDD-GATE]`, veredicto no-`LISTO`, parada por gap crítico).
  - **Args OK** — un escenario verifica que el orquestador traduce el lenguaje natural a los **args correctos** del skill (y que **no** inyecta overrides peligrosos sin petición explícita).
- **Estado:** `PENDIENTE` (sin revisar) · `REVISADO` (cruzado, sin huecos) · `CON-HUECOS` (faltan escenarios) · `COMPLETADO` (huecos rellenados).

## Progreso

**Revisadas: 48 / 51** · Completadas: 48 · Revisadas sin huecos: 0 · Con huecos: 0 · **Pendientes: 3**

> ⚠ **El contador decía `48 / 49` y las skills del core son 51** (descubierto al recontar en
> [[D-075]]). Las dos que faltaban no eran cualesquiera: **`wf-conformance-author` y
> `wf-conformance-status`**, las que escriben y leen esta misma matriz. Entran como `PENDIENTE`
> en la fase meta en vez de seguir fuera del censo — el instrumento tampoco se mide solo por
> defecto. La cabecera, el Alcance y el Progreso dicen ahora el mismo número.

> ⏱ **`wf-spec-retire` nace sin medir** ([[D-074]], 2026-09-14). Los escenarios están escritos
> (CU-7.o/p/q, y desde [[D-078]] también CU-7.s y CU-9.o) pero no ejercitados: la fila es
> `PENDIENTE` y no se marca de otra forma hasta que haya pasada. Además, **CU-7 no puede medir el
> bloqueo aguas abajo**: su proyecto arranca sin plan ni tasks, así que la denegación de generar y
> ejecutar tareas necesita el proyecto de CU-6.

> 🔴 **`CU-3.d` estrena pasada propia y sale FALLO — y tres de los cuatro hallazgos son del
> instrumento** (2026-09-21, v0.116.0, [[D-089]]/[[D-090]]/[[D-091]]/[[D-092]]). Dos tandas por
> subset sobre el consumer de siempre. **Puntos 1 y 4 en verde** —el 4 es la primera medición
> conductual limpia de [[D-087]]: `--skip-index` en los 5 encargos y cero regeneraciones por parte
> de los escritores—; **puntos 2 y 3 en rojo**. El 2 por una causa **determinista y reproducible
> fuera de la corrida**: el índice heredaba el `PENDIENTE_GENERACIÓN` del readiness de la tanda
> anterior y salía con `Ruta spec` a un fichero que existe. El 3 por la forma `1 + 1` **con N=2**,
> donde el desvío no tiene forma visible.
>
> Lo que deja en el banco: **V4** (`sdd-fanout-check.py`), que convierte el contrato de fan-out en
> una medición mecánica sobre el transcript y que, al validarlo contra el histórico, **encontró una
> ocurrencia de 2026-09-15 que nadie había registrado**; el **probe V1 arreglado** —su glob lo
> abortaba entero en zsh, así que llevaba una pasada sin medir nada—; y dos puntos de CU-3.d más
> afilados (qué mirar en el índice al iterar por subsets, y que medir el fan-out con una tanda de
> 3+ **no lo mide donde se rompe**). **La pasada no cuenta para ninguna serie**: es un FALLO, y
> además el árbol cambia con sus arreglos.

> ✅ **Y la serie de `CU-3.d` abre 1/3 el mismo día** (2026-09-21, ancla **v0.116.0**). Segunda
> corrida con los arreglos dentro, misma prosa y mismo reparto **2 + 3**: los cuatro puntos en
> verde. Lo que la hace valer más que un verde: **la condición de [[D-089]] volvió a darse** —el
> aviso de matriz estancada saltó a la primera, con las mismas tres features— así que el defecto
> era **estructural del flujo por subsets**, no un accidente. [[D-090]] en campo sin una sola
> colisión de IDs y con el readiness clasificando vigencias solo. **V1 = 0.**
>
> La pasada dejó además un hallazgo propio ([[D-093]]: el veredicto del informe no llevaba su
> alcance), arreglado en la misma versión. **No reinicia la serie**: toca prosa del informe de
> conflictos y los siguientes pasos del readiness —lo que miden CU-3.f/o y V1—, no ninguno de los
> cuatro puntos de CU-3.d, que siguen congelados desde el ancla. La regla de la campaña es
> **congelar el punto que el escenario mide**, no el árbol entero. El arreglo sale como
> **v0.116.1** para que el ancla no nombre dos árboles: 1/3 corrió sobre 0.116.0, y 2/3 y 3/3
> correrán sobre 0.116.1+, con los cuatro puntos byte-idénticos entre ambas.

> 🔁 **Y la serie se pierde a propósito dos días después** ([[D-094]], v0.117.0). Los agentes Opus
> pasan a `claude-opus-5-5` y el orquestador de las sesiones con ellos. Los agentes que ejecuta
> CU-3.d son `sonnet-5` y no cambian, pero su **punto 3** —el fan-out en un único mensaje— lo
> emite el **hilo principal**: juicio al otro lado de una frontera de modelo. **`CU-3.d` vuelve a
> 0/3**; la 1/3 queda como histórica. Con una pasada se pierde una pasada; sellando sobre `opus-5`
> se habría perdido un sello. Los sellos conductuales previos (CU-3.a, CU-2, CU-1, CU-13.a) pasan
> a `SELLADO (5) — pendiente HUMO (5.5)`.

> ✅ **Y la serie nueva abre 1/3 el mismo día** (ancla **v0.117.0+71d38cd**, orquestador
> `opus-5-5`). Los cuatro puntos en verde, [[D-093]] funcionando a la primera y la condición de
> [[D-089]] reproducida por tercera vez con las mismas tres features. Dos hallazgos fuera de los
> cuatro puntos → [[D-095]] (v0.117.1): una portada de conflictos que el arbitraje desmiente sin
> que nada lo señale, y el script del índice anunciando el nombre sin la ruta. **No reinician la
> serie.** Y [[D-090]]/[[D-093]] ganan por fin comprobación explícita en `CU-3.f` (puntos 2 y 4) y
> `CU-3.o` (punto 6).

> ✅ **2/3 al día siguiente** (v0.117.1+8f348f0). Cuatro puntos en verde por segunda vez seguida y
> [[D-095]] funcionando en campo. Un hallazgo fuera de los cuatro puntos → [[D-096]] (v0.117.2):
> los auditores del fan-out no sabían qué pares les tocan —dos de tres dieron por limpio un par
> ajeno con un ALTA confirmado— y el readiness desmintió la portada de uno que nunca habló de ese
> par. **No reinicia la serie.**

> ⏱ **Cuatro escenarios nacen sin pasada del barrido de enlazado lateral de Spec**
> ([[D-078]]/[[D-079]], 2026-09-14): **CU-9.o** (evolucionar una feature dada de baja se deniega, y
> el estado sobrevive incluso sin hook), **CU-7.s** (la reactivación es la única vuelta atrás y no
> restaura sellos), **CU-4.e** (el sistema caracterizado adquiere un PRD: adopción, no
> regeneración) y **CU-3.s** (el informe consolidado de conflictos se escribe donde el readiness lo
> busca). Ninguno salió de una corrida: salieron de **revisión estática**, así que la Regla 9 punto
> 5 (*"congela la frase que falló"*) no aplica — la frase hay que inventarla, y eso es parte de lo
> que estos cuatro tienen que aportar para ser ejecutables. La **capa determinista** de CU-9.o y
> CU-7.s sí está cubierta por CI (`test_sdd_seal.py`, `test_sdd_gate_check.py`); lo que falta es la
> conductual.

> ⏱ **Cinco escenarios más nacen sin pasada del tercer barrido de enlazado de Spec**
> ([[D-080]]/[[D-081]]/[[D-082]], 2026-09-15), esta vez sobre **quién regenera** y sobre las
> **costuras del orquestador**: **CU-3.t** (regenerar el spec de una feature dada de baja para en
> las dos vías, directa y en lote), **CU-4.f** (su gemelo brownfield, con el código todavía en
> producción), **CU-3.u** (la decisión del gate de alcance viaja al fan-out, y un `STOP_*` de un
> delegado se presenta en vez de enterrarse), **CU-3.v** (un discovery que ya existe se reutiliza,
> no se regenera) y **CU-3.w** (la salida de un conflicto es una vía que desella, y las retiradas
> no compiten). Como los cuatro de la tanda anterior, salieron de **revisión estática**. La capa
> determinista de CU-3.t **sí** está en CI desde hoy (`SPEC-RETIRED-BLIND` en
> `test_sdd_structural_lint.py`, 6 tests); lo que falta es la conductual.

> ✅ **Primera pasada del ancla nueva, y confirma una predicción del banco** (pasada 14 de
> CU-3.a, v0.114.1, [[D-084]]). **FALLO**, así que no cuenta para la serie — pero el fallo es el
> que el probe 5 llevaba escrito desde [[D-050]]: el fan-out en `1 + (N-1)` (una llamada de
> prueba y el resto después) serializa la tanda ahora que el flag surte efecto. Contrato
> reforzado en los tres emisores + backstop `FANOUT-PILOT-UNGUARDED`. Se llevó por delante un
> segundo hallazgo mudo: la instrucción de la plantilla pegada al valor de
> `derived_from_prd_hash`. **Lo demás de la pasada quedó medido y limpio** (12/12 delegaciones
> síncronas, gobernanza entera en su rama negativa, V1 = 0, arbitraje de divergencias de libro).

> ⏱ **El barrido que faltaba: [[D-073]] llegó al árbol sin llegar al banco** (v0.114.1,
> 2026-09-15). `wf-spec-delta` se movió al hilo principal con **tres gates** en 0.107.0, la única
> versión de la tanda 0.107→0.114 **sin** bullet `⚠ Conformance` — así que **CU-3.h** y **CU-3.p**
> siguieron describiendo un fork de dos pasos. Reescritos los dos (CU-3.p arrastraba además un
> ancla fantasma —«Paso 7A»— y un **FALLO falso**: penalizaba una salida sancionada del gate),
> corregido **CU-3.m** (declaraba unos `allowed-tools` que no son los de la skill y mandaba
> verificar la no-reescritura *por la lista de tools*, que es justo lo que [[D-051]] dice que no
> la garantiza) y añadido **CU-3.f punto 5**, que mide el **sello** de `wf-spec-validate` — la
> mitad del workflow que ningún escenario tocaba desde [[D-065]]. Los cuatro salieron de revisión
> estática: **sin pasada**.
>
> ⏱ **Y el recuento de CU-3.a se re-ancla a v0.113.0.** Su nota decía *"las tres arrancan de cero
> sobre 0.106.0 o posterior"*, pero CU-3.a mide **orquestación**, y [[D-080]]/[[D-081]] cambiaron
> el fan-out de `wf-spec-features-first` (cuarta clase `RETIRADA` en el subset; la decisión del
> gate viajando en el prompt; rama para el `STOP_*` de un delegado). Tres pasadas a caballo de ese
> cambio no son *sobre el mismo árbol*.

> ⏱ **Los seis escenarios del cascade quedan sin pasada bajo la arquitectura nueva**
> ([[D-075]], 2026-09-14). CU-7.f–k están reescritos —los checkpoints se **preguntan**, no se
> reportan— y CU-7.r nace hoy. La cobertura está completa; la **evidencia conductual, no**: lo
> medido antes lo fue sobre un fork que no podía presentar ninguna de esas paradas.

> **Auditoría completa.** Todas las fases del core revisadas: bootstrap (2) · prd (4) · spec (13) ·
> design (14) · plan (2) · tasks (7) · meta (6). Las skills meta entran en la batería vía
> [`cu-17-meta.md`](casos-de-uso/cu-17-meta.md) + routing en `CU-13.h`.
>
> **Track diferido pendiente:** overlay KMM (8 `wf-kmm-*` + kb anidadas) — auditarlo aparte si se decide
> ampliar el alcance. CU-12 lo cubre parcialmente.

> Eje **Args OK** transversal: el contrato de paso de args lo cubren CU-11.b (construcción
> de flags/modos/paths), CU-11.f (overrides peligrosos no auto-inyectados), CU-11.g (input
> oral vs argumento de fichero) y CU-11.h (selección/multivalor). Aplican a todas las fases.

---

## Fase bootstrap (2)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-project-init | `--topology <a\|c\|s\|design>` `--surfaces <…>` `--design-targets <…>` `--prd` `--design` `--stack` `--name` `--sdd-path` `--force` | orquestador en hilo principal (`AskUserQuestion`, sin fork); `sdd-init-detect.py` (detect/verify/target-platforms); `install.sh --no-claude-md`; hook SessionStart; `sdd-version.json` | CU-1.b/d/e/h/i/j/k/l/m/n/o/p/q/r/t/u · CU-10.d | ✅ | ✅ | ✅ | ✅ | COMPLETADO | Flags y enum inválido cubiertos por CU-1.p (incl. `--topology design` + `--design-targets`, D-011); topología `design` y consumer con repo de diseño en CU-1.q / CU-1.i caso 4; guard de doble SSoT de diseño (D-012, CU-1.i caso 5); aviso advisory de SSoT productor sin git (CU-1.r, `is_git_repo`); regla **eager** `sdd-orchestration.md` (D-021, disciplina de orquestación transversal, generada sin `paths:` por `install_orchestration_rule`) — instalación en CU-1.t, carga y aplicación al orientar en CU-14.j; regla **eager** `sdd-routing.md` (D-022, desambiguación por-fase topology-gated, `install_routing_rule`) — instalación on-disk en CU-1.u (backstop `test_routing_rule_*`), enrutado por descriptions + desambiguación eager en CU-11.a sub-caso 1; entrevista interactiva validada a mano (los escenarios hook-only a/c/f/g son cobertura del hook de sesión, sin fila propia) |
| wf-sdd-update | `--force` | `install.sh --prune` + overlay; `CHANGELOG.md`; `sdd-version.json` | CU-1.f · CU-10.a/b/i/j/k | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |

---

## Fase prd (4)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-prd-create | `<dir_proyecto>` `[--source <notas.md>]` `[--output <prd.md>]` | prd-expert; grep `[ASUNCIÓN]`; Regla 12 | CU-2.a/b/c/d/i · CU-13.a · CU-11.b/g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | `--output` a ruta custom cubierto por **CU-2.i** (gate [[D-025]], sellada 2026-07-15); `--source`/oral por CU-11.b/g |
| wf-prd-review | `<prd.md>` | prd-expert (delegación **síncrona**, `run_in_background: false`, [[D-043]]); `sdd-prd-ready.py` (1:1 + veredicto), `sdd-prd-deps.py` (grafo + backstop `--check`), `sdd-prd-apply.py` (`--confirm/--edit/--reject/--seal/--reopen`), `sdd-prd-frontmatter.py` | CU-2.e/f/g/h/j · CU-13.a | ✅ | ✅ | ✅ | — | COMPLETADO | Arg único posicional. Bloque cerrado 2026-07-30: gate de asunciones y no-autoaprobación (2.e/2.f), enrutado por tipo de artefacto (2.g), no-reescritura byte-idéntica (2.h) y cascada determinista de dependencias (2.j: orden del backstop, 3 desenlaces, consecuencia en el momento, ámbito de edición) |
| wf-prd-change | `<prd.md> --new-reqs <cambio.md\|texto>` | **hilo principal** + gate (`AskUserQuestion`); prd-expert (analiza read-only, escribe por delegación; **síncrona**, [[D-043]]); kb-product-change-governance; `sdd-prd-apply.py --reopen`; `changes/CR-XXX/` | CU-7.a/b/c/**n** · CU-13.a · CU-11.g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | Re-arquitecturada por [[D-040]]: gate obligatorio de clasificación + bifurcaciones (**CU-7.n**, nueva). El modo `--defer-decisions` **se retira** en [[D-075]] —su único consumidor era la cascada, que ya no es un fork—, y **CU-7.n sub-caso G cambia de premisa**: mide que el gate llega igual cuando quien invoca es el cascade. `--new-reqs` admite texto inline → **CU-11.g obsoleto** en su ejemplo canónico de "exige fichero". Precondición de fichero inexistente sin caso propio (patrón ya en CU-2.c) |
| wf-prd-change-cascade | `<prd.md> [--new-reqs] [--features F-…] [--review-before-apply] [--skip-design] [--dry-run]` | **hilo principal** ([[D-075]]): sostiene sus gates con `AskUserQuestion`, invoca `wf-prd-change` con el `Skill` tool (corre en main, su gate se presenta dentro) y delega los workers por `Agent` con `run_in_background: false` — `sdd-spec-auditor` (sync-impact, conflict ×N en un mensaje, readiness), `sdd-spec-writer` (spec-sync analyze/apply), `design-system-architect` (design-sync). **Sin artefacto propio**: el resumen se presenta ([[D-060]]). Backstop determinista: `FORK-SKILL-DISPATCH` de `sdd-structural-lint.py` | CU-7.f/g/h/i/j/k/**r** · CU-13.a · CU-11.f | ✅ | ✅ | ✅ | ✅ | COMPLETADO | Hueco que destapó [[D-075]]: **nadie medía que el orquestador no redacta el informe de sus delegados** ni que no surfacea comandos — rellenado con **CU-7.r**. Los seis escenarios previos **cambian de forma**: sus checkpoints pasan de reportarse a preguntarse |

---

## Fase spec (14)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-spec-analyze | `<archivo.md> [--allow-overwrite-analysis]` | sdd-spec-explorer; kb-spec-expert; kb-gap-conventions; `sdd-analysis-gaps.py` (`--check`); **para** con `STOP_ARTEFACTO_EXISTE` si ya hay `_analysis.md` — el gate lo presenta quien invoca ([[D-064]]) | CU-3.a/k · CU-13.b · CU-11.f | ✅ | ✅ | ✅ | ✅ | COMPLETADO | El 🟡 anterior (*regenerar con confirm en el Paso 7*) medía una conducta **retirada** por [[D-064]]: el fork ya no confirma, para y devuelve el bloqueo. Lo que queda por ejercitar es `--allow-overwrite-analysis` armado por el usuario |
| wf-spec-discover | `<prd.md> [--analysis <analysis.md>] [--allow-derived-scope-from-analysis] [--allow-overwrite-discovery]` | sdd-spec-explorer; kb-decompose-expert; **para** con `STOP_OWNERSHIP_AMBIGUO` (shared model sin dueño) y con `STOP_ARTEFACTO_EXISTE` si ya hay `_discovery.md` — regenerarlo renumera los `F-00X` que los specs ya citan ([[D-081]]) | CU-3.c/i/v · CU-13.b | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | `--allow-derived...` cubierto vía CU-11.f; inferencia de RFs sin caso (mecánico) · **la reutilización la mide CU-3.v** ([[D-081]]): el bloqueo por artefacto existente solo nombraba el camino de regenerar, y la salida buena vivía en la otra rama del workflow que lo invoca |
| wf-spec-features-first | `<prd.md> [--light\|--standard] [--features F-…\|--all-features] [--allow-open-critical-gaps] [--allow-derived-scope-from-analysis] [--skip-conflict] [--skip-readiness]` | orquestador **en el hilo principal** (sin `context: fork`, [[D-045]]): sostiene sus 4 gates con `AskUserQuestion` sin relanzarse, y delega 5 veces por `Agent` recibiendo el informe **entregado** — `tool_result` o notificación de fin, nunca deducido ([[D-043]]/[[D-047]]), con el flag obligatorio en el fan-out por ser barrera y honrado de verdad desde que el proyecto apaga fork mode ([[D-050]]: 5/5 en la pasada 6, contra 0/10 antes); el delegado ejecuta la sub-skill, no la re-despacha ([[D-044]]); `sdd-features-index.py` (cruza `artifacts.prd`↔`artifacts.spec`, [[D-046]]); `sdd-analysis-gaps.py --check` (gate de gaps, [[D-042]]); clasifica el subset en cuatro clases —`NO_EXISTE` / `RETIRADA` / `SELLADO` / `DRAFT`— y **transporta** al fan-out el `--allow-derived-scope-from-analysis` que el usuario armó ([[D-080]]/[[D-081]]) y el `--skip-index` que deja el índice con un solo autor ([[D-087]]) | CU-3.a/b/c/d/l/r/t/u/v · CU-13.b/g · CU-11.f | ✅ | ✅ | ✅ | ✅ | COMPLETADO | **`CU-3.d` FALLO en su primera pasada propia** (2026-09-21): el fan-out volvió a salir `1 + (N-1)` **con N=2** ([[D-092]]) —donde el desvío no tiene forma visible— y el índice del Paso 6 heredó el `PENDIENTE_GENERACIÓN` del readiness de la tanda anterior ([[D-089]]). El Paso 7 gana además dos notas: los informes de tandas previas **no se relanzan** (el readiness los marca ESTANCADO por su `Conjunto comparado`) y la colisión de IDs **ya no existe** ([[D-090]]) — las dos cosas se improvisaron a mano en esa pasada · **`CU-3.a` SELLADO 3/3** (pasadas 16-18, ancla v0.115.1, 2026-09-18): primer escenario de la campaña que cierra serie. Congelar el Paso 5 fue la condición, no acertar tres veces · **La llamada de prueba, [[D-084]]** (pasada 14): el contrato del fan-out decía *"todas en un único mensaje"* y no cubría el desvío que de verdad ocurre — lanzar **una** para ver si va y el resto después, que cumple la letra y serializa la tanda igual. Backstop `FANOUT-PILOT-UNGUARDED` · **Tres costuras de la delegación, [[D-081]]**: la decisión del gate de alcance no bajaba al prompt de los escritores —que reevalúan con `--analysis` y paraban con `STOP_REQUIERE_PRD_CHANGE` por lo ya contestado—, el Caso B del discovery no miraba si el artefacto existía, y un `STOP_*` de un delegado no tenía rama (se reportaba como "falló"). Miden CU-3.u y CU-3.v |
| wf-spec-fast-track | `<archivo.md> --capability <n> \| --scope-from <discovery.md> --feature <F-00X> [--light\|--standard] [--analysis] [--gap-id-start <P-XXX>] [--allow-derived-scope-from-analysis] [--allow-overwrite-sealed-spec] [--skip-index]` | sdd-spec-writer; `sdd-next-id.py`/`sdd-sync-check.py seal`; lee el `Estado:` **entero** y **para** con `STOP_SPEC_SELLADO` (cierra `--allow-overwrite-sealed-spec`) o con `STOP_SPEC_RETIRADO` (**no lo cierra ningún flag**, [[D-080]]) | CU-3.e/j/r/t · CU-13.b | ✅ | ✅ | ✅ | ✅ | COMPLETADO | **CU-3.e punto 2 ([[D-077]])**: la frontera fast-track → validate no estaba medida. Es donde el spec **nace** en `BORRADOR` ([[D-061]]) y el gate que exige el sello está dos fases más allá; `wf-spec-delta` y `wf-spec-gap-resolve` ya cerraban diciéndolo. Espejo de CU-2.a punto 2 (frontera create → review del PRD) · **CU-3.t ([[D-080]])**: el sondeo de estado era binario (`VALIDADO` sí o no), así que un spec `RETIRADO` caía en la rama del borrador y se reescribía — resucitando la feature sin `CR` ni gate. Backstop `SPEC-RETIRED-BLIND` |
| wf-spec-from-code | `discover <path> [--scope] [--allow-overwrite-code-discovery] \| discover <path> --capabilities 'F-C-00X=confirmada\|descartada: <motivo>\|corregida: <texto>' \| generate <path> --feature <F-C-00X> [--allow-overwrite-sealed-spec] \| generate <path> --capability <n> --scope <subdir> [--allow-overwrite-sealed-spec]` | sdd-spec-writer; kb-spec-characterization; `discover` **para** con `STOP_CODE_DISCOVERY_SIN_VALIDAR` y `generate` con `STOP_SPEC_SELLADO` si el spec está `VALIDADO` ([[D-062]]/[[D-071]]) y con `STOP_SPEC_RETIRADO` si la capacidad se dio de baja ([[D-080]]); el mapa que ya existe se protege con `STOP_ARTEFACTO_EXISTE` y la validación humana vuelve por `--capabilities`, con `STOP_CAPACIDAD_DESCARTADA` si se pide caracterizar lo descartado ([[D-083]]) | CU-4.a/b/c/d/e/f/g/h · CU-13.b/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | modo directo `--capability --scope` (sin discovery) sin caso propio · **la salida de la onramp la cubre ahora CU-4.e** ([[D-079]]): qué pasa cuando el sistema caracterizado adquiere un PRD. La entrada estaba completa y el hueco estaba en el único sitio donde no se mira — cuando el proyecto **deja de ser** el caso que justificó la entrada · **CU-4.f ([[D-080]])**: el gemelo de CU-3.t en brownfield, donde es más fácil de provocar — el código sigue en producción, así que *"documenta esto otra vez"* es la petición natural sobre una capacidad ya retirada · **CU-4.g y CU-4.h ([[D-083]])**: el `_code_discovery.md` era el único artefacto con trabajo humano dentro sin gate de sobreescritura, y su gate humano no declaraba **canal de vuelta** — lo que [[D-081]] y [[D-082]] cerraron para sus gemelos greenfield el mismo día |
| wf-spec-validate | `<archivo_spec.md>` | **hilo principal** ([[D-065]]): delega la auditoría a sdd-spec-auditor por `Agent` (síncrona), presenta el informe, **captura quién aprueba** y sella con `sdd-seal.py spec --seal --approved-by` (autor≠verificador: el veredicto del agente no sella) | CU-3.f/m · CU-9.o · CU-13.b/g | ✅ | ✅ | ✅ | — | COMPLETADO | **El sello no lo medía nadie hasta v0.114.1.** La fila cita CU-3.f/m desde [[D-065]], pero los dos escenarios medían solo la **auditoría** y el umbral: que main **capture quién aprueba** y estampe `Estado: VALIDADO` + `Aprobado por:` con `sdd-seal.py --seal --approved-by` no aparecía en ninguno — justo la mitad que protege la regeneración (`--allow-overwrite-sealed-spec`) y alimenta a `gate_spec_fiable`. Lo mide ahora **CU-3.f punto 5** ⏱ sin pasada. · Umbral del veredicto cerrado en [[D-076]] (espejo de [[D-035]]): «hallazgo bloqueante» gobernaba el sello y no estaba definido en ninguna kb — ahora vive en `kb-spec-expert` (Paso 4 de «Cómo validar un Spec») con backstop en `test_install_sh.py::KbSpecExpertContentTest`, y **CU-3.f punto 1 / CU-3.m punto 3** lo miden. · **la no-reescritura NO está garantizada por la lista de tools** ([[D-051]]): el auditor conserva `Bash` y un `cat >` escribe igual. Es una **norma** escrita en el agente — verificarla exige mirar si tocó el spec, no confiar en el frontmatter |
| wf-spec-conflict | `<feature_spec.md> --features-dir <path/features/>` | sdd-spec-auditor; kb-conflict-expert; excluye del conjunto los specs `RETIRADO` diciéndolo ([[D-080]]); numera los hallazgos con el `F-00X` del spec auditado delante (`CF-F001-01`) y declara en cabecera el `Conjunto comparado` ([[D-090]]) | CU-3.f/n/s/w · CU-13.b | ✅ | ✅ | ✅ | ✅ | COMPLETADO | **Dos costuras del fan-out de auditores, [[D-090]]** (pasada de `CU-3.d`, 2026-09-18): tres auditores paralelos numerando en local produjeron **tres `CF-002` distintos**, y los informes de la tanda anterior —calculados contra 2 specs— se leyeron junto a los de una de 5 sin que nada lo dijera. Prefijo de feature en el ID (sin reparto: el auditor ya sabe qué spec audita) y `Conjunto comparado` en la cabecera · **Modo directorio cubierto por CU-3.s** ([[D-078]], misma tanda): el hueco *"`.` sobre directorio sin caso propio"* escondía uno real — el consolidado se escribía **dentro** de `features/` y `wf-spec-readiness`, su único lector, lo busca en el **padre**; ninguna de sus dos rutas alcanzaba la raíz de `features/`. Invisible porque la advertencia de ausencia no bloquea · **el informe no bloquea nada aguas abajo ([[D-077]])**: `gate_spec_fiable` no lee los `_conflict_report.md` y no debe hacerlo —la severidad la asigna un juicio y los auditores se contradicen por diseño ([[D-047]])—; `wf-prepare-plan` **avisa y continúa** (CU-6.a punto 2, CU-3.o punto 5) · **la salida del hallazgo no existía ([[D-082]])**: `kb-conflict-expert` define detección y severidad y termina sin decir qué se hace, y el cierre de la skill mandaba a *"editar los specs afectados"* — una edición a mano **conserva el sello**, así que el gate la deja pasar. Lo mide CU-3.w |
| wf-spec-readiness | `<path/features/>` | sdd-spec-auditor; kb-gap-conventions; `sdd-features-index.py`; lee los `_conflict_report.md` **de la raíz y de cada feature**, en ambos layouts ([[D-046]]), comprueba su **vigencia** por el `Conjunto comparado` y marca ESTANCADO el que no cubra los specs actuales ([[D-090]]), y **arbitra** las divergencias entre auditores sin cerrarlas por mayoría ([[D-047]]) | CU-3.f/o/s · CU-13.b/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | **Alcance del veredicto acotado en [[D-077]]**: `LISTA` no miraba el sello del spec mientras `gate_spec_fiable` sí lo exige ([[D-061]]), y `BLOQUEADA` por conflicto `ALTA` no lo lee ningún gate. Los dos límites los miden **CU-3.o puntos 4 y 5**; el gemelo desde el gate es **CU-9.n** |
| wf-spec-delta | `analyze <spec.md> --new-reqs <desc.md> \| apply <spec.md> <delta_analysis.md> [--allow-open-critical-gaps]` | **hilo principal** ([[D-073]]): sostiene **tres gates** —delta vs cambio de producto, cuál de las lecturas si el requisito es ambiguo, y aplicar o no con críticos abiertos— y delega análisis e integración a sdd-spec-writer; kb-spec-expert; `sdd-analysis-gaps.py --check` (el recuento sale del script); `sdd-seal.py --unseal`; `sdd-features-index.py` | CU-3.h/p · CU-9.o · CU-13.b/g · CU-15.d | ✅ | ✅ | ✅ | ✅ | COMPLETADO | **CU-3.h y CU-3.p reescritos** (v0.114.1): [[D-073]] llegó al árbol en 0.107.0 **sin barrido de conformance** —la única versión de la tanda 0.107→0.114 sin su bullet `⚠ Conformance`—, así que el catálogo siguió midiendo un fork con dos pasos y cero gates. CU-3.h mide ahora los **tres**: `POSIBLE_CAMBIO_DE_PRODUCTO` con sus **dos salidas sancionadas**, el `AMBIGUO` presentado una-opción-por-lectura con *"no lo decido ahora"* dejando gap `[D-XXX]`, y el de críticos abiertos con el recuento saliendo del script. CU-3.p corrige además un **ancla fantasma** (citaba un «Paso 7A» que no existe; el gate es el 4A) y un **FALLO falso**: daba por desviación *"tratarlo como delta"*, que es una salida legítima del gate ⏱ **sin pasada en su forma nueva** |
| wf-spec-gap-resolve | `<feature_spec.md> [--analysis <analysis.md>] [--inferred 'CA-XXX=confirmado\|incorrecto: <texto>\|no-lo-se']` | sdd-spec-writer; kb-spec-characterization; `sdd-analysis-gaps.py --check`; los `[INFERIDO]` **paran** con `STOP_INFERIDO_SIN_CONFIRMAR`, las tres vías las presenta quien invoca ([[D-068]]) y las decisiones vuelven por `--inferred` ([[D-082]]) | CU-3.g/p/q · CU-4.c · CU-9.o · CU-13.b/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | CU-3.q mide **dos turnos** desde [[D-068]]: parada + material verbatim, y después las decisiones aplicadas tal cual — con **puntos 5 y 6 nuevos** ([[D-082]]): el segundo turno no tenía **canal**. El Paso 1 parseaba `<spec>` y `--analysis`, y *"si vienen decididos"* dependía de que el texto libre se pareciera lo suficiente |
| wf-spec-retire | `<feature_spec.md> --change CR-XXX [--reason 'texto']` \| `reactivate <feature_spec.md>` | **hilo principal** ([[D-074]]): exige la traza del `CR-XXX`, delega el diagnóstico de impacto a sdd-spec-auditor (shared models huérfanos, dependencias, artefactos ya generados) y sostiene **un gate sin override** — no hay `--allow-*` porque puede preguntar; `sdd-seal.py --retire` es el único escritor de la baja, `--unseal` degrada el plan, `sdd-features-index.py` deriva `RETIRADA`; el bloqueo lo aplica `sdd-gate-check.py` en los tres frentes | CU-7.o/p/q/s · CU-9.o · CU-13.b/g | ❌ | ❌ | ❌ | 🟡 | PENDIENTE | nace sin pasada; el bloqueo aguas abajo necesita el proyecto de CU-6, no el de CU-7. **El modo `reactivate` ya tiene escenario**: `CU-7.s` mide que devuelve a `BORRADOR` sin restaurar ningún sello —ni el del spec ni el del plan—, que retira la traza `Retirada:`, que conserva el `F-00X` y que avisa de que el PRD sigue sin contemplar la capacidad. **Y que es la única puerta de vuelta** ([[D-078]]): el `--unseal` de los flujos de evolución era una segunda, no sancionada. **Enrutado añadido en [[D-075]]** (residuo de [[D-071]]): [[D-074]] llegó a `routing.md` y a CU-7, pero no a la matriz — ni fila en CU-13.b ni la trampa de tres vías (*retirar vs posponer vs borrar una HU*) en CU-13.g, que es la desambiguación que `routing.md` declara crítica |
| wf-spec-amend | `<feature_spec.md> --ca CA-XXX [--from-task T-00X] [--reason 'texto']` | **hilo principal** ([[D-068]]): sostiene sus **dos gates** con `AskUserQuestion` —clasificar aclaración-vs-cambio de comportamiento, y confirmar el texto final palabra por palabra— y delega el análisis y la edición quirúrgica a sdd-spec-writer; `sdd-amend.py` es el único que asigna `E-00X` y marca el plan | CU-8.d/e · CU-9.o · CU-13.b/g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | los dos gates son **su razón de existir**: una pasada que no los vea presentados es FALLO, no matiz |
| wf-spec-sync-from-prd | `analyze <prd.md> \| apply <prd.md> --features F-001,F-002,...` | sdd-spec-writer; `sdd-sync-check.py seal`; el `apply` ejecuta el **contrato de integración** del delta —no invoca el workflow, que desde [[D-073]] vive en main ([[D-070]])— con `--unseal`, versión menor, changelog e índice ([[D-067]]); cuarta acción `retire`, que **se salta y reporta**: un fork no da de baja nada ([[D-074]]) | CU-7.l/m/q · CU-13.b · CU-15.a | ✅ | ✅ | ✅ | ✅ | COMPLETADO | **CU-7.l corregida en [[D-077]]** (recalibración, Regla 9 punto 4): su FALLO afirmaba que *"el readiness lo bloqueará"* y el readiness **no lo bloquea** —da `LISTA` un spec recién desellado—. Quien deniega es `gate_spec_fiable` una fase más tarde, así que el aviso de la reapertura es lo único que protege al usuario en ese tramo |
| wf-prd-sync-impact | `<prd.md>` | sdd-spec-auditor (`[Read, Bash]`: escribe su informe por redirección, **nunca lo delega a main** — [[D-051]]); `sdd-sync-check.py`; `derived_from_prd_hash` | CU-7.d/e · CU-13.b · CU-15.a | ✅ | ✅ | ✅ | — | COMPLETADO | informe **efímero** (cabecera `Vigente para: PRD v<X.Y>`); ofrece no volcarlo si el derivado se regenera acto seguido |

---

## Fase design (14)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-design-intake | `generate <feature_spec.md> [--prd] [--output] [--mode guided\|hybrid\|auto] [--preset <name>] [--learn]` | design-system-architect; kb-design-brief/-style-decision-tree; `sdd-init-detect.py target-platforms` (D-011) | CU-5.a/m · CU-13.c | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | `--learn`/`--preset` vía CU-11.b; `target_platforms` (familias) desde `design_targets` (D-011, CU-5.a.3) |
| wf-design-discover | `<feature_spec.md> [--prd] [--brief] [--output] [--mode interactive\|auto]` | orquestador (sin agente); WebSearch/WebFetch | CU-5.g · CU-13.c | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | modo `auto` (sin validación) vía variante de arg |
| wf-design-moodboard | `<feature_spec.md> [--prd] [--output] [--mode interactive\|auto]` | design-system-architect; kb-design-style-taxonomy/-decision-tree | CU-5.f · CU-13.c/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | alimenta intake, no cierra brief |
| wf-design-system | `generate <feature_spec.md> [--prd] [--brief] [--design-file] [--no-brief]` | design-system-architect; kb-design-system-contract (incl. Regla 11 `## Platform Components`, D-011); `sdd-init-detect.py target-platforms` (gate Paso 3b); linter `@google/design.md` | CU-5.b/k/l · CU-13.c/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | autoría de `## Platform Components` con design targets divergentes (D-011, CU-5.b casos 2-3); gate determinista `requires_platform_components` (Paso 3b → `NATIVE_PLATFORMS`), `PlatformComponentsGateTest` |
| wf-design-validate | `<DESIGN.md> [--brief] [--views] [--lenient] [--pedagogical]` | design-system-architect; linter `@google/design.md`; kb-design-governance R5; kb-design-system-contract R11 + `sdd-init-detect.py target-platforms` (gate Paso 4b, D-011) | CU-5.e/o · CU-13.c/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | promoción provisional→confirmed = única escritura (gated); gate `DESIGN_GAP` por `## Platform Components` ausente con targets divergentes (D-011, CU-5.e caso 6, check 19 del checklist) |
| wf-design-delta | `analyze <DESIGN.md> --new-reqs <cambios.md> [--brief] \| apply <DESIGN.md> <delta.md>` | design-system-architect; kb-design-expert R15 | CU-5.e/p · CU-13.c/g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-design-sync | `<DESIGN.md>` | design-system-architect; kb-design-governance R2 (read-only); `sdd-source-drift.py` (D-011, cross-repo) | CU-5.e/r/x · CU-13.c | ✅ | ✅ | ✅ | — | COMPLETADO | arg único posicional; deriva intra-repo por razonamiento (hash futuro, ROADMAP 11.2); drift cross-repo determinista por pin git (D-011, CU-5.x) |
| wf-design-feature-prototype | `generate <feature_spec.md> [--design-file] [--brief] [--no-brief]` | design-feature-architect; kb-design-feature-artifacts/-conflict-expert; `sdd-resolve-path.py`; `sdd-design-resolve.py` (D-011) | CU-5.c/k/n/w · CU-13.c | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | base⊕override per-view por design target (D-011, CU-5.w); resolución `sdd-design-resolve.py` |
| wf-design-extract | `discover <path_ui> [--scope] \| generate <path_ui> [--from <extraction.md>] [--scope] [--design-file]` | design-system-architect; kb-design-characterization; linter `@google/design.md` | CU-5.d · CU-13.c/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | gate discover→generate cubierto vía CU-5.d |
| wf-design-branch | `create <branch> \| list \| compare <a> <b> \| merge <branch> --into <target> \| discard <branch>` | design-system-architect; kb-design-governance R22 | CU-5.h/s · CU-13.c/g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-design-variant | `create <feature_spec.md> --variants A,B [--hypothesis] \| compare <feature_variants.md>` | design-feature-architect | CU-5.i/t · CU-13.c/g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-design-export | `<DESIGN.md> --platforms <css,style-dictionary,compose,swiftui,tailwind> [--output-dir] [--dry-run]` | sin agente (traduce fielmente); idempotente | CU-5.e/u · CU-13.c · CU-11.h | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-design-a11y-audit | `<DESIGN.md> [--views] [--brief] [--target AA\|AAA] [--lenient]` | design-system-architect; kb-a11y-expert/-web-expert | CU-5.e/q · CU-13.c | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | escribe `a11y_audit_<fecha>.md`; ramifica por plataforma |
| wf-design-feedback | `capture <feedback.md\|texto> [--source] [--feature] \| triage <feedback_capture.md>` | design-feature-architect (7 categorías de triage) | CU-5.j/v · CU-13.c · CU-11.g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |

---

## Fase plan (2)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-prepare-plan | `generate <spec.md>` | plan-architect; kb-plan-expert; `gate_spec_fiable`; `sdd-resolve-path.py`; `sdd-source-drift.py` (drift + `design_ssot`) + `sdd-design-resolve.py` (D-011/D-012, consumer) | CU-6.a/h/k · CU-9.e/f/g/h/i/n · CU-13.d | ✅ | ✅ | ✅ | — | COMPLETADO | **CU-9.n ([[D-077]])**: el sello del spec era la única de las siete razones de denegación de `gate_spec_fiable` sin escenario — su gemelo para el plan (CU-9.c) existía desde el principio. Y **CU-6.a punto 2**: un conflicto `ALTA` abierto se **advierte, no bloquea** (ningún gate lee los `_conflict_report.md`). arg único `generate <spec>`; stack KMM solapa con CU-12; consumer con `design_source` resuelve el handoff del repo de diseño en solo lectura + drift cross-repo (D-011, CU-6.k.5); aviso de doble SSoT de diseño (D-012, CU-6.k.6) |
| wf-plan-validate | `<plan.md>` | plan-auditor; `sdd-seal.py` (autor≠sellador) | CU-6.b/i/l · CU-13.d | ✅ | ✅ | ✅ | — | COMPLETADO | gate de plan validado que consume tasks: CU-9.a–d |

---

## Fase tasks (7)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-prepare-tasks | `generate <plan.md>` | task-generator; kb-tasks-expert; gate plan validado | CU-6.c/n · CU-9.a/b/c/d · CU-13.d | ✅ | ✅ | ✅ | — | COMPLETADO | resolución de stack = espejo de CU-6.k |
| wf-task-run | `<feature_tasks.md> [--task T-00X \| --next \| --all] [--no-commit]` | Owner agent (delegación **síncrona**, `run_in_background: false`, [[D-043]], ahora exigida por el hook `sdd-agent-sync.py`, [[D-048]]: se valida el DoD y se commitea sobre su reporte); `sdd-task-state.py`; `sdd-gate-check.py`; commit | CU-6.d/j/m/n · CU-9.j/k/n · CU-15.f · CU-13.d | ✅ | ✅ | ✅ | ✅ | COMPLETADO | sigue `context: fork` delegando (`FORK-ORCHESTRATOR` warning): bloque aparte pendiente, [[D-045]] |
| wf-qa-plan | `generate <feature_spec.md>` | qa-engineer; kb-qa-expert; `gate_spec_fiable` | CU-6.e/o · CU-9.e–i · CU-14.f · CU-13.d | ✅ | ✅ | ✅ | — | COMPLETADO | — |
| wf-qa-verify | `<feature_qa_plan.md>` | qa-engineer; evidencia ejecutada; único escritor de `Estado` TC | CU-6.f/o · CU-14.f · CU-13.d | ✅ | ✅ | ✅ | — | COMPLETADO | — |
| wf-release | `<feature_dir\|tasks_path> [--tag <tag>] [--no-tag] [--note <texto>]` | `sdd-release.py` (sin agente); gate QA APTO; git SHA | CU-6.g · CU-14.g · CU-13.d · CU-11.f | ✅ | ✅ | ✅ | ✅ | COMPLETADO | `APTO_CON_RESERVAS` se graba con reservas; re-releases R-00X |
| wf-bug | `<descripcion.md\|texto> [--feature <nombre>]` | Owner (triaje contra CA; fix por delegación **síncrona**, [[D-043]]); `sdd-next-id.py` | CU-8.a/b/c/f · CU-13.d/g · CU-11.g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-project-status | `[<raíz_artefactos_spec>] [--output <path>]` | `sdd-project-status.py` (sin agente, read-only) | CU-10.f · CU-13.d/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | agrega lo sellado; no razona ni edita |

---

## Fase meta (8)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-skill-create | `<kb\|wf> <nombre> --phase <fase\|global> [--description] [--agent] [--effort] [--force]` | sdd-author; `sdd-scaffold.py`; `sdd-structural-lint.py` (gate) | CU-17.a · CU-13.h | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-agent-create | `<nombre> --phase <fase\|global> --skills <kb…> [--description] [--model] [--effort high] [--read-only]` | sdd-author; `sdd-scaffold.py`; `sdd-structural-lint.py` | CU-17.b · CU-13.h | ✅ | ✅ | ✅ | ✅ | COMPLETADO | no regenera registry (solo indexa skills) |
| wf-stack-create | `<stack> [--type <app\|web\|backend>] [--detect '<cond>'] [--with-agents] [--description]` | sdd-author; kb-sdd-stack-overlay-contract; `sdd-structural-lint.py` | CU-17.c · CU-13.h | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-sdd-audit | `<structural\|content\|full> [--phase <fase\|global>]` | sdd-auditor; `sdd-structural-lint.py`; kb-sdd-audit-structural/-content | CU-17.d · CU-13.h | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-sdd-refactor | `<path-skill-o-agente> [--reason <motivo>]` | sdd-author; `sdd-structural-lint.py` (siempre) | CU-17.e · CU-13.h | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-sdd-status | `[--phase <fase\|global>] [--output <path>]` | sin agente (mecánico); `generate-skill-registry.py` | CU-17.f · CU-13.h/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | read-mostly; SIN CONSUMIDOR / SIN REGISTRAR |
| wf-conformance-author | `<skill-name\|phase> [--cu <cu-NN>]` | sdd-conformance; kb-sdd-conformance (Reglas 1-9); escribe escenarios en `cu-NN-*.md` y actualiza esta matriz | — | ❌ | ❌ | ❌ | ❌ | PENDIENTE | **Sin cruzar contra el catálogo.** Aparecida al cuadrar el contador ([[D-075]]): es la skill que **escribe** esta matriz y no tenía fila en ella |
| wf-conformance-status | `[--phase <fase>]` | sin agente (read-only); `sdd-conformance-coverage.py`; lee esta matriz | — | ❌ | ❌ | ❌ | ❌ | PENDIENTE | **Sin cruzar contra el catálogo.** Ídem: lee esta matriz y no figuraba en ella |

---

## Track diferido — overlay KMM

8 `wf-kmm-*` (init, network-setup, auth-setup-keycloak, database-setup, datastore-setup, environments,
testing-setup, stack-setup-ktor-keycloak-koin) + kb anidadas. **Fuera de esta tanda.** CU-12 cubre
parcialmente el init y el scaffolding del overlay.
