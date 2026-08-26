---
name: wf-spec-features-first
description: "Orquestador del flujo features-first: ejecuta discover sobre el PRD y lanza fast-track en paralelo por feature (todas o un subset con --features), con guardrails de gaps criticos y alcance, y cierra con conflict check y readiness."
when_to_use: "Activa en frases como 'genera specs por feature del PRD', 'flujo features-first completo', 'specs en paralelo del PRD', 'genera todas las features del PRD', 'genera specs de la fase 1', 'genera specs de estas features', 'features-first completo'."
argument-hint: "<prd_archivo.md> [--features F-001,F-002,...] [--light|--standard] [--allow-open-critical-gaps] [--allow-derived-scope-from-analysis] [--all-features] [--skip-conflict] [--skip-readiness]"
effort: high
allowed-tools: [Bash, Agent, AskUserQuestion]
user-invocable: true
---

# Workflow: FEATURES-FIRST (Orquestador)

Este workflow pertenece a la fase Spec y **requiere un PRD o documento de requisitos previo** como entrada. Si el usuario todavía no tiene ese artefacto, remítelo a la fase PRD antes de continuar.

Tu objetivo es ejecutar el flujo features-first: identificar features de un PRD y generar un spec por cada una en paralelo. Puede operar sobre **todo el PRD** o sobre un **subset de features** (iteración / fase) cuando se proporciona `--features`. Este skill **no realiza el análisis ni la escritura por sí mismo** — orquesta otros workflow skills.

Este workflow corre en el **hilo principal** (igual que `wf-prd-create`, `wf-prd-review` y `wf-prd-change`, y **no** en `context: fork`) por dos razones ([[D-045]]): sostiene **cuatro gates** que requieren `AskUserQuestion` —readiness del PRD, gaps críticos, expansión de alcance y coste de PRD grande—, una tool que no existe dentro de un subagente; y la delegación síncrona que necesita para consumir el resultado del paso siguiente **solo se obtiene desde el hilo principal** (con fork mode activo —el default interactivo— un subagente no puede pedir el primer plano para sus propios delegados).

**Regla de oro:** Eres un orquestador. No analizas contenido, no generas specs, no tomas decisiones funcionales. Invocas skills en el orden correcto y consolidas resultados. **No hagas `Read` ni `cat` del PRD, del `_analysis.md` ni de ningún spec**: lo que necesitas saber sale del script determinista o del reporte de quien delegaste ([[D-031]]/[[D-042]]). Esto vale **aunque las tools estén disponibles** — `allowed-tools` es declarativo, no una jaula ([[D-038]]), así que la restricción se sostiene por norma.

> **Cómo delegas — un solo mecanismo, y el resultado se recibe, no se deduce ([[D-043]], corregida
> por [[D-045]]).** Los cinco puntos de delegación de este workflow (analyze, discover, fast-track,
> conflict, readiness) se invocan **siempre** con la tool `Agent`, pasando el `subagent_type` que se
> indica en cada paso y **`run_in_background: false`**, y **no** con el `Skill` tool (no paraleliza
> y no devuelve un handle síncrono).
>
> **Qué es haber esperado.** Has esperado cuando **el texto del informe del delegado está en tu
> contexto como resultado de tu propia llamada `Agent`**. Ninguna otra cosa cuenta: que el fichero
> exista, que su tamaño deje de cambiar, que un script te dé un veredicto sobre él, o que lo leas
> de cualquier buzón intermedio del entorno. Todo eso es deducir, y deducir no es esperar.
>
> **Si no tienes el informe, para.** No continúes y **no reconstruyas**: di que la delegación no
> devolvió resultado y detente. En particular, **nunca presentes como dicho por el delegado un dato
> que has obtenido tú por tu cuenta** — un path, un veredicto o un recuento sacados del disco
> suben con la misma apariencia de verdad que los del informe, y ahí es donde el error deja de
> notarse.
>
> **No afirmes limitaciones del entorno que no has comprobado.** Si una tool rechaza un parámetro,
> la evidencia es su error de validación; sin ese error, no se afirma. Justificar un atajo con una
> limitación supuesta convierte una decisión tuya en un hecho del harness.
>
> **El delegado ejecuta la skill, no la re-despacha ([[D-044]]).** El prompt le dice que **lea el
> `SKILL.md` y ejecute sus pasos él mismo**, y le **prohíbe** usar el `Skill` tool. El motivo es
> estructural: las sub-skills llevan `context: fork`, así que invocarlas con `Skill` **forkea otro
> subagente** — y como su `agent:` es el mismo que acabas de lanzar, ese fork es un **clon** del
> delegado. Medido en CU-3.a pasada 2: el envoltorio intermedio costó **~210 KB por delegación**
> (casi tanto como el que hacía el trabajo, porque recibe su reporte entero y lo re-emite), y ese
> salto extra vuelve a ser **asíncrono**. En el fan-out del Paso 5 esto se multiplica por feature.

> **Cómo presentas un gate ([[D-045]]).** Los cuatro gates de este workflow (Pasos 2, 2.5, 2.5 de
> alcance y 4a.1) se presentan **en el momento, con `AskUserQuestion`**, y el flujo **continúa en el
> mismo turno** con lo que el usuario elija. No le digas "vuelve a ejecutar añadiendo `--allow-…`":
> re-invocar el workflow entero repite los pasos ya hechos (parseo, readiness, check de gaps) y
> pierde el contexto de la parada.
>
> Lo que **no** cambia ([[D-026]]): **tú nunca armas un `--allow-*` por tu cuenta** ni lo infieres de
> una petición impaciente. Son escotillas de seguridad, y quien las abre es el usuario **eligiendo
> explícitamente** en el gate. Los flags siguen siendo válidos si vienen **de entrada** en
> `$ARGUMENTS`: en ese caso el gate correspondiente ya está decidido y no se presenta — deja
> constancia y sigue.
>
> Antes de la pregunta, da en el texto los datos que hacen falta para decidir (paths, veredicto,
> IDs, recuentos), sacados del script o del reporte del delegado. La pregunta no sustituye a la
> información: la acompaña.

**Sobre el flujo iterativo por subset:** las "fases" o "iteraciones" no se definen en el PRD ni en el discovery — son una decisión humana de delivery sobre qué features procesar en cada pasada. El usuario decide el subset **después** de ver el discovery; cada ejecución con `--features` actualiza `_features.md` de forma incremental, sin borrar las features ya generadas en pasadas anteriores ni las pendientes para futuras.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del PRD**: el primer argumento
- **Flags opcionales**: `--features F-001,...` (IDs a procesar, requiere discovery previo); `--light`/`--standard` (modo del pipeline — se propaga a cada fast-track; sin flag rige `pipeline_mode` de `.sdd/project-init.json`); `--allow-open-critical-gaps` (genera con gaps críticos abiertos → HUs `[INCOMPLETO]`); `--allow-derived-scope-from-analysis` (continúa aunque el analysis expanda el PRD); `--allow-unreviewed-prd` (continúa aunque el PRD tenga `[ASUNCIÓN]` sin confirmar / sin sellar → alcance no-revisado); `--all-features` (full-run override para PRDs grandes); `--skip-conflict`/`--skip-readiness` (omitir checks finales).

Si no hay argumento, informa el uso con todos los flags opcionales y ejemplos de los modos principales: completo sin flags, subset con `--features`, con `--allow-open-critical-gaps`, con `--allow-derived-scope-from-analysis`.

---

## Paso 2: Verificar el archivo y la readiness del PRD

Verifica que el archivo PRD existe; si no → informa con ruta exacta y detén.

**Gate de readiness PRD→spec ([[D-020]]).** Un PRD con `[ASUNCIÓN]` sin confirmar hornearía inferencias no validadas en los specs. Compruébalo mecánicamente (no a ojo ni por topología):
```
!python3 .sdd/scripts/sdd-prd-ready.py "<prd.md>"
```
- Veredicto `READY` → continúa.
- `OPEN_ASSUMPTIONS` o `ASSUMPTION_MISMATCH`, y **no** se pasó `--allow-unreviewed-prd` → **presenta el gate**: informa del veredicto y del detalle que dio el script, y pregunta con `AskUserQuestion`:
  - *Revisar el PRD primero* (recomendada) — el flujo se detiene aquí; el usuario cierra las asunciones con `/wf-prd-review <prd.md>` y vuelve cuando esté sellado.
  - *Continuar sobre un PRD no-revisado* — equivale a `--allow-unreviewed-prd`: sigues al Paso 2.5 dejando constancia explícita de que los derivados se generan sobre alcance **no-revisado**.
- `UNSEALED` → **advisory**: avisa ("el PRD no está sellado; recomendable cerrar la aprobación con `/wf-prd-review`") y continúa.
- Con `--allow-unreviewed-prd` de entrada sobre un veredicto bloqueante → no presentes el gate; continúa dejando constancia explícita de que los derivados se generan sobre un PRD **no-revisado**.
- Si falta el script (`.sdd/scripts/sdd-prd-ready.py` no existe) → avisa (reinstala el ecosistema con `install.sh`) y continúa (conservador: no bloquees por falta de tooling).

---

## Paso 2.5: Análisis de gaps (obligatorio)

1. Busca si existe un `*_analysis.md` para este PRD (convención: `<basename>_analysis.md`). Búscalo en el directorio de artefactos prd (`artifacts.prd` de `.sdd/project-init.json`, si está declarado) y en el mismo directorio del PRD.
2. **Si NO existe** → genera el análisis delegando con la tool `Agent` ([[D-043]]), y **espera su resultado**:
   ```
   Agent(
     subagent_type: "sdd-spec-explorer",
     run_in_background: false,
     prompt: "Lee `.claude/skills/wf-spec-analyze/SKILL.md` y ejecuta sus pasos TÚ MISMO sobre estos argumentos: <prd.md>. NO uses el `Skill` tool: ya eres el agente al que esa skill delega (`agent: sdd-spec-explorer`), así que invocarla te forkearía en un clon tuyo. Dentro de ese SKILL.md, `${CLAUDE_SKILL_DIR}` es `.claude/skills/wf-spec-analyze/`. Al terminar, informa del path exacto del `_analysis.md` generado, su veredicto y el nº de gaps por severidad."
   )
   ```
   El path del `_analysis.md` lo tomas **del informe del delegado**, no buscándolo en el disco. Marca este análisis como **recién generado**: el usuario aún no lo ha visto, así que el gate del punto 6 se presenta igualmente aunque el script no reporte críticos abiertos (con la opción de revisarlo antes de generar specs).
3. **Estado mecánico de los gaps — antes de decidir nada** ([[D-042]]):
   ```
   !python3 .sdd/scripts/sdd-analysis-gaps.py "<path>_analysis.md" --check --json
   ```
   Da `verdict` (`CRITICAL_OPEN` / `CRITICAL_ANSWERED` / `VACUOUS`), `critical_open` y `critical_open_ids`. **Este conteo no se hace leyendo el informe**: contar marcadores `_(pendiente)_` no es juicio, y de él cuelgan las dos ramas duras de los puntos 5 y 6. Si el veredicto es `VACUOUS`, el documento no se ha podido parsear — **detente** y dilo, no lo trates como "sin gaps".
4. **Si existe** → léelo para lo que **sí** es juicio: veredicto del análisis (`LISTO_PARA_SPECS`, `LISTO_PARA_SPECS_CON_PREGUNTAS`, `REQUIERE_LIMPIEZA_PRD`), presencia de `[PUEDE_REQUERIR_CR]`, y si las respuestas ya escritas introducen expansión funcional no comprometida.
5. Si el veredicto del análisis es `REQUIERE_LIMPIEZA_PRD` → **DETENERSE** e informar al usuario:
   > "El análisis previo marca `REQUIERE_LIMPIEZA_PRD`. Corrige la contaminación técnica del PRD antes de continuar y vuelve a ejecutar el flujo."
6. Si el script dio `CRITICAL_OPEN` y **no** se pasó `--allow-open-critical-gaps` de entrada, o si el análisis está **recién generado** (punto 2) → **presenta el gate**.

   El texto que acompaña a la pregunta **no puede ser genérico**: quien tiene que responder no debería bucear en el informe para saber qué le toca. Con los IDs que devolvió el script (punto 3), da el **path exacto**, la lista de `[P-XXX]` `[CRÍTICO]` **cada uno con su pregunta en una línea**, y qué se sustituye (`- **Respuesta**: _(pendiente)_`). Las preguntas salen del informe del delegado o de `--list`; no abras el fichero para redactarlas.

   Y después pregunta con `AskUserQuestion`:
   - *Responderlos primero* (recomendada) — el flujo se detiene aquí. El usuario los escribe en el `_analysis.md`, o **te los dicta y los aplicas tú con el script** (punto siguiente). Cuando estén cerrados, se retoma.
   - *Continuar aceptando el riesgo* — equivale a `--allow-open-critical-gaps`: sigues al Paso 3 dejando constancia explícita de que las HUs afectadas podrán salir `[INCOMPLETO]` y quedarán bloqueadas para plan/tasks hasta completarse con `/wf-spec-gap-resolve`.
   - *Responder solo algunas* — el usuario cierra las que tenga claras ahora; el resto quedan abiertas y se vuelve a evaluar el gate.

   Si el análisis estaba recién generado pero el script **no** reporta críticos abiertos, el gate se reduce a dos vías: *revisar el análisis antes de generar* o *continuar ya*.
7. Si el script dio `CRITICAL_OPEN` y `--allow-open-critical-gaps` vino **de entrada** en `$ARGUMENTS` → no presentes el gate; continúa al Paso 3 dejando constancia explícita de que las HUs afectadas podrán salir `[INCOMPLETO]`.
8. Si el script dio `CRITICAL_ANSWERED`, inspecciona las respuestas ya resueltas. Si alguna introduce señales de cambio de producto según `kb-product-change-governance`:
   - si **NO** vino `--allow-derived-scope-from-analysis` de entrada → **presenta el gate**. Di qué respuesta concreta introduce qué señal (nueva entidad persistente, catálogo reutilizable, nueva granularidad funcional o flujo adicional no comprometido en el PRD) y pregunta con `AskUserQuestion`:
     - *Formalizar el cambio en el PRD* (recomendada) — el flujo se detiene; el cambio se abre con `wf-prd-change <prd.md> --new-reqs <cambio.md>` y los derivados se generan después, sobre PRD limpio.
     - *Continuar con alcance derivado* — equivale a `--allow-derived-scope-from-analysis`: sigues dejando constancia de que el discovery, `_features.md` y los specs marcarán ese alcance como **scope derivado** y no como PRD puro.
   - si `--allow-derived-scope-from-analysis` vino **de entrada** → no presentes el gate; continúa dejando constancia explícita de que el discovery, `_features.md` y los specs deberán marcar ese alcance como **scope derivado** y no como PRD puro.
9. Si el script dio `CRITICAL_ANSWERED` y no se detectan señales de cambio → continuar al Paso 3 usando el `_analysis.md` como contexto.

**Importante:** `[INFORMATIVO]` nunca bloquea (el script los reporta aparte: cada uno aplicará su asunción por defecto); `[CRÍTICO]` abiertos requieren `--allow-open-critical-gaps`. Para señales de expansión consulta `kb-product-change-governance`. Si el PRD cambió después de generar specs previos, puede ser necesario `wf-prd-sync-impact` antes de mezclar pasadas.

> **Las respuestas de los gaps no las escribes tú** ([[D-042]]; tabla de ámbito en `kb-gap-conventions`). Las escribe el usuario en el `_analysis.md`; si te las dicta, las aplicas con `sdd-analysis-gaps.py --answer P-XXX "texto"`. Nunca edites el informe a mano ni completes una respuesta que el usuario no ha dado.

---

## Paso 3: Ejecutar discover (o reutilizarlo)

**Caso A — `--features` está presente**:
El `_discovery.md` **debe existir previamente** (los IDs `F-XXX` solo tienen sentido contra un discovery existente). Busca `<basename>_discovery.md` en el directorio de artefactos prd (`artifacts.prd` de `.sdd/project-init.json`, si está declarado) y en el mismo directorio del PRD.
- Si existe → continúa al Paso 4 reutilizándolo.
- Si NO existe → **detente** e informa al usuario:
  > "Has indicado `--features <IDs>`, pero no existe `<path>_discovery.md`. Las features se identifican en el discovery — ejecuta primero `/wf-spec-discover <prd.md>`, revisa el mapa generado y vuelve a ejecutar con los IDs que correspondan."

**Caso B — `--features` no está presente**:
Delega el discovery con la tool `Agent` ([[D-043]]):
```
Agent(
  subagent_type: "sdd-spec-explorer",
  run_in_background: false,
  prompt: "Lee `.claude/skills/wf-spec-discover/SKILL.md` y ejecuta sus pasos TÚ MISMO sobre estos argumentos: <prd.md> [--analysis <analysis.md>] [--allow-derived-scope-from-analysis si aplica]. NO uses el `Skill` tool: ya eres el agente al que esa skill delega (`agent: sdd-spec-explorer`), así que invocarla te forkearía en un clon tuyo. Dentro de ese SKILL.md, `${CLAUDE_SKILL_DIR}` es `.claude/skills/wf-spec-discover/`. Al terminar, informa del path exacto del `_discovery.md`, la lista de features (ID + nombre + actor), los shared models y si te detuviste por ambigüedad."
)
```
Espera su resultado (el de la tool, no el del disco) y obtén de él el path del `_discovery.md`. Si el discover se detuvo por shared models ambiguos → transmite el mensaje al usuario y espera resolución.

---

## Paso 4: Determinar el subset a procesar

Necesitas la lista de features (ID + nombre kebab-case) y su total `N_total`. **No hagas `Read` del `_discovery.md`** (Regla de oro):
- **Discovery recién generado (Caso B)** → la lista viene en el **informe del delegado**, que la reporta explícitamente.
- **Discovery reutilizado (Caso A)** → extráela con una consulta **acotada** por `Bash`, no cargando el documento:
  ```
  !grep -nE "^### F-[0-9]{3}:" "<path>_discovery.md"
  ```
  Una extracción determinista y delimitada no es "leer el artefacto": lo que la Regla de oro prohíbe es traerte el contenido para opinar sobre él.

### 4a — Determinar el subset

- **Si NO hay `--features`**: el subset a procesar = todas las features del discovery.
- **Si hay `--features F-001,F-002,...`**:
  1. Valida que **todos** los IDs solicitados existen en el discovery.
  2. Si alguno no existe → **detén** con mensaje claro: "Los siguientes IDs no aparecen en `<path>_discovery.md`: [lista]. IDs válidos: [lista del discovery]."
  3. El subset = solo las features cuyos IDs aparecen en `--features`.
- **Features NO incluidas en el subset** (caso `--features`): se registrarán en `_features.md` con estado `PENDIENTE_GENERACIÓN` y no se les lanza fast-track en esta ejecución.

### 4a.1 — Guardrail de coste para PRDs grandes

Si no hay `--features` y el discovery contiene >5 features, y **no** vino `--all-features` de entrada → **presenta el gate**. Muestra el mapa de features (ID, nombre, actor, RFs) tal como te lo reportó el delegado, di cuántas son, y pregunta con `AskUserQuestion` qué alcance quiere en esta pasada:
- *Un subset de features* — el usuario nombra los IDs; equivale a `--features F-001,...`. Las no incluidas quedan `PENDIENTE_GENERACIÓN` y se generan en pasadas posteriores sin perder lo anterior. **No elijas tú el subset**: puedes agrupar por dependencia o por gaps abiertos para ayudar a decidir, pero la selección es del usuario.
- *Todas de una pasada* — equivale a `--all-features`.

Si hay gaps `[CRÍTICO]` abiertos, dilo aquí también: indica qué features quedarían con HUs `[INCOMPLETO]`, porque cambia la decisión de alcance. Con `--all-features` o `--features` **de entrada** → no presentes el gate; continúa.

### 4b — Detectar specs preexistentes

Para cada feature del subset: si ya existe su spec — `features/<nombre>/spec/<nombre>_spec.md` (subcarpetas) o `features/<nombre>/<nombre>_spec.md` (plano legacy) — → no relances (preservar trabajo previo), excluye del fast-track y anota como "ya generada". Informa al usuario: N_total totales, N_subset a procesar, N_a_generar nuevas, N_pendientes futuras.

---

## Paso 5: Lanzar fast-track en paralelo (solo features a generar)

Lanza fast-track únicamente para las features del **subset** que NO tienen spec preexistente (lista calculada en el Paso 4b). Las features que ya tenían spec se preservan tal cual; las que están fuera del subset no se tocan.

Para cada feature F-00X a generar, lanza un subagente con el `Agent` tool usando `subagent_type: sdd-spec-writer`:

```
Agent(
  subagent_type: "sdd-spec-writer",
  run_in_background: false,
  prompt: "Lee `.claude/skills/wf-spec-fast-track/SKILL.md` y ejecuta sus pasos TÚ MISMO sobre estos argumentos: <prd.md> --scope-from <discovery.md> --feature F-00X [--light|--standard si se pasó o si project-init declara pipeline_mode] [--analysis <analysis.md> si disponible]. NO uses el `Skill` tool: esa skill es `context: fork` y invocarla te forkearía otro subagente en cascada. Dentro de ese SKILL.md, `${CLAUDE_SKILL_DIR}` es `.claude/skills/wf-spec-fast-track/`. Al terminar, informa del path del spec generado, nº de gaps `[CRÍTICO]` y nº de asunciones aplicadas."
)
```

**CRÍTICO: emite TODOS los `Agent` tool calls en un único mensaje** — no esperes entre ellos. Cada subagente es completamente independiente. Si hay 6 features a generar, tu respuesta debe contener 6 llamadas al `Agent` tool simultáneas, todas con `subagent_type: sdd-spec-writer`.

`run_in_background: false` **no** rompe el paralelismo ([[D-043]]): las N llamadas emitidas en un único mensaje siguen corriendo a la vez; el flag solo garantiza que el mensaje no vuelve hasta que **todas** han terminado — que es justo lo que el Paso 6 asume al regenerar el índice leyendo los specs del disco.

No uses el `Skill` tool para esto — no soporta ejecución paralela.

Espera a que **todas** terminen según el criterio de arriba: tienes el informe de cada delegado como resultado de tu llamada. Que los ficheros hayan aparecido en `features/` no te dice que los fast-tracks terminaran, ni con qué resultado. Para cada una, registra **de su informe**:
- Feature ID y nombre
- Si se completó con éxito o falló
- Path del spec generado
- Número de gaps `[CRÍTICO]` encontrados (si los hay)
- Número de asunciones aplicadas

Si el subset está vacío tras filtrar specs preexistentes (todas las features pedidas ya tenían spec), salta al Paso 6 con el conjunto vacío de "recién generadas".

---

## Paso 6: Regenerar `_features.md` (pasada autoritativa)

`_features.md` es un artefacto **generado**, no editado a mano: lo produce el regenerador determinista `sdd-features-index.py` escaneando el discovery (universo de features + shared models + RF→Feature) + todos los specs presentes (estado real por marcadores, HUs/CAs) + el readiness report si existe (veredicto). Esto elimina de raíz la colisión de escrituras paralelas de los fast-tracks **y** los conflictos de merge entre devs sobre el hub monolítico (un conflicto en `_features.md` pasa a ser ruido: se regenera tras el merge).

Tras esperar a que terminen todos los fast-tracks, ejecuta la pasada autoritativa **una sola vez** desde la raíz del proyecto (el directorio que contiene `.sdd/`):

```
python3 .sdd/scripts/sdd-features-index.py <raíz_spec>
```

`<raíz_spec>` es el directorio raíz de artefactos spec donde viven `features/` y `_features.md` (regla de layout: `artifacts.spec` de `.sdd/project-init.json` si está declarado; si no, el directorio del PRD de entrada). El resultado cubre TODAS las features del discovery: las del subset recién generadas quedan con su estado real, las preexistentes se reflejan tal cual desde sus specs en disco, y las que aún no tienen spec aparecen como `PENDIENTE_GENERACIÓN` — sin que tú tengas que preservar estado a mano. Si el script no existe:
> "⚠ Falta `.sdd/scripts/sdd-features-index.py`. Re-ejecuta la instalación del ecosistema (`install.sh`) para reponer los scripts de enforcement. El índice `_features.md` no se ha regenerado."

---

## Paso 7: Conflict check (si no `--skip-conflict`)

Opera sobre **todas las features con spec en `features/`**, incluyendo preexistentes de iteraciones anteriores. Con ≥2 specs: por cada spec recién generado delega con la tool `Agent` ([[D-043]]), `subagent_type: "sdd-spec-auditor"` y `run_in_background: false`, con el prompt `"Lee .claude/skills/wf-spec-conflict/SKILL.md y ejecuta sus pasos TÚ MISMO sobre: <spec.md> --features-dir <features_dir>. NO uses el Skill tool ([[D-044]]): ya eres su agente y te forkearía en un clon."` (solo los nuevos se chequean contra todos; puedes emitir las N llamadas en un único mensaje). Escribe `_conflict_report.md` si hay conflictos. Sin specs nuevos → omitir.

---

## Paso 8: Readiness check (si no `--skip-readiness`)

Delega con la tool `Agent` ([[D-043]]), `subagent_type: "sdd-spec-auditor"` y `run_in_background: false`, con el prompt `"Lee .claude/skills/wf-spec-readiness/SKILL.md y ejecuta sus pasos TÚ MISMO sobre: <features_dir>/. NO uses el Skill tool ([[D-044]]): ya eres su agente y te forkearía en un clon."`. Genera `_readiness_report.md` en el directorio raíz de artefactos spec (junto a `_features.md`) y actualiza `_features.md` con el estado de cada feature (incluyendo `PENDIENTE_GENERACIÓN` para las no procesadas aún).

---

## Paso 9: Informar al usuario

Presenta el resumen siguiendo la plantilla de `${CLAUDE_SKILL_DIR}/references/output_template.md` (consúltala por `Bash`; es material **del skill**, no un artefacto del proyecto — la Regla de oro habla de PRD, analysis y specs). Diferencia features procesadas en esta iteración vs preexistentes de iteraciones anteriores vs pendientes de futura generación. Incluye los bloques condicionales de siguientes pasos (gaps críticos, conflictos, features listas, features PENDIENTE_GENERACIÓN).
