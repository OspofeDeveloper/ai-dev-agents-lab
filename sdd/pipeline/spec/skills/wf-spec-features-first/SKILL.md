---
name: wf-spec-features-first
description: "Orquestador del flujo features-first: ejecuta discover sobre el PRD y lanza fast-track en paralelo por feature (todas o un subset con --features), con guardrails de gaps criticos y alcance, y cierra con conflict check y readiness."
when_to_use: "Activa en frases como 'genera specs por feature del PRD', 'flujo features-first completo', 'specs en paralelo del PRD', 'genera todas las features del PRD', 'genera specs de la fase 1', 'genera specs de estas features', 'features-first completo'."
argument-hint: "<prd_archivo.md> [--features F-001,F-002,...] [--light|--standard] [--allow-open-critical-gaps] [--allow-derived-scope-from-analysis] [--all-features] [--skip-conflict] [--skip-readiness]"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
context: fork
user-invocable: true
---

# Workflow: FEATURES-FIRST (Orquestador)

Este workflow pertenece a la fase Spec y **requiere un PRD o documento de requisitos previo** como entrada. Si el usuario todavía no tiene ese artefacto, remítelo a la fase PRD antes de continuar.

Tu objetivo es ejecutar el flujo features-first: identificar features de un PRD y generar un spec por cada una en paralelo. Puede operar sobre **todo el PRD** o sobre un **subset de features** (iteración / fase) cuando se proporciona `--features`. Este skill **no realiza el análisis ni la escritura por sí mismo** — orquesta otros workflow skills.

**Regla de oro:** Eres un orquestador. No analizas contenido, no generas specs, no tomas decisiones funcionales. Invocas skills en el orden correcto y consolidas resultados. **No hagas `Read`/`cat` del PRD ni del `_analysis.md`**: lo que necesitas saber sale del script determinista o del reporte de quien delegaste ([[D-031]]/[[D-042]]).

> **Cómo delegas — un solo mecanismo, síncrono, sin sondeo ([[D-043]]).** Los cinco puntos de
> delegación de este workflow (analyze, discover, fast-track, conflict, readiness) se invocan
> **siempre** con la tool `Agent`, pasando el `subagent_type` que se indica en cada paso y
> **`run_in_background: false`**. El flag es obligatorio: desde Claude Code v2.1.198 los subagentes
> corren en **background por defecto** y aquí necesitas su resultado en el acto — el paso siguiente
> lo consume. **No uses el `Skill` tool** para ninguno de los cinco (no paraleliza y su despacho no
> te devuelve un handle síncrono).
>
> Y **espera el resultado de la tool**: no averigües si un delegado terminó **sondeando el disco**
> (`ls`/`find` en bucle sobre el directorio de artefactos, `Monitor` sobre el fichero que va a
> escribir) ni relances un segundo agente "por si acaso" — eso no es esperar, es un race de doble
> escritura sobre el mismo artefacto. Si crees que no terminó, no lo compruebes: no ha terminado.

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
- `OPEN_ASSUMPTIONS` o `ASSUMPTION_MISMATCH`, y **no** se pasó `--allow-unreviewed-prd` → **DETENTE** e informa:
  > "El PRD no está listo para spec (`<veredicto>`): <detalle del script>. Revísalo con `/wf-prd-review <prd.md>` (confirma las asunciones y sella la aprobación) y vuelve a ejecutar. Si quieres continuar igualmente asumiendo alcance no-revisado, re-ejecuta añadiendo `--allow-unreviewed-prd`."
- `UNSEALED` → **advisory**: avisa ("el PRD no está sellado; recomendable cerrar la aprobación con `/wf-prd-review`") y continúa.
- Con `--allow-unreviewed-prd` sobre un veredicto bloqueante → continúa dejando constancia explícita de que los derivados se generan sobre un PRD **no-revisado**.
- Si falta el script (`.sdd/scripts/sdd-prd-ready.py` no existe) → avisa (reinstala el ecosistema con `install.sh`) y continúa (conservador: no bloquees por falta de tooling).

---

## Paso 2.5: Análisis de gaps (obligatorio)

1. Busca si existe un `*_analysis.md` para este PRD (convención: `<basename>_analysis.md`). Búscalo en el directorio de artefactos prd (`artifacts.prd` de `.sdd/project-init.json`, si está declarado) y en el mismo directorio del PRD.
2. **Si NO existe** → genera el análisis delegando con la tool `Agent` ([[D-043]]), y **espera su resultado**:
   ```
   Agent(
     subagent_type: "sdd-spec-explorer",
     run_in_background: false,
     prompt: "Ejecuta el skill /wf-spec-analyze con los siguientes argumentos: <prd.md>"
   )
   ```
   Tras la ejecución, **DETENERSE** e informar al usuario. El mensaje **no puede ser genérico**: quien tiene que responder no debería bucear en el informe para saber qué le toca. Saca los IDs críticos del script (punto 3) y da path, lista de `[P-XXX]` `[CRÍTICO]` con su pregunta en una línea, y qué se sustituye:
   > "Se ha generado el análisis de gaps en `<path>_analysis.md`. Quedan [N] gap(s) `[CRÍTICO]`: [P-XXX] — <pregunta>; … En el bloque de cada uno, sustituye `- **Respuesta**: _(pendiente)_` por tu respuesta y vuelve a ejecutar `/wf-spec-features-first <prd.md>`. Si prefieres dictármelas, las aplico yo con el script."
3. **Estado mecánico de los gaps — antes de decidir nada** ([[D-042]]):
   ```
   !python3 .sdd/scripts/sdd-analysis-gaps.py "<path>_analysis.md" --check --json
   ```
   Da `verdict` (`CRITICAL_OPEN` / `CRITICAL_ANSWERED` / `VACUOUS`), `critical_open` y `critical_open_ids`. **Este conteo no se hace leyendo el informe**: contar marcadores `_(pendiente)_` no es juicio, y de él cuelgan las dos ramas duras de los puntos 5 y 6. Si el veredicto es `VACUOUS`, el documento no se ha podido parsear — **detente** y dilo, no lo trates como "sin gaps".
4. **Si existe** → léelo para lo que **sí** es juicio: veredicto del análisis (`LISTO_PARA_SPECS`, `LISTO_PARA_SPECS_CON_PREGUNTAS`, `REQUIERE_LIMPIEZA_PRD`), presencia de `[PUEDE_REQUERIR_CR]`, y si las respuestas ya escritas introducen expansión funcional no comprometida.
5. Si el veredicto del análisis es `REQUIERE_LIMPIEZA_PRD` → **DETENERSE** e informar al usuario:
   > "El análisis previo marca `REQUIERE_LIMPIEZA_PRD`. Corrige la contaminación técnica del PRD antes de continuar y vuelve a ejecutar el flujo."
6. Si el script dio `CRITICAL_OPEN` y **no** se ha pasado `--allow-open-critical-gaps` → **DETENERSE** e informar al usuario, citando los IDs que devolvió:
   > "El análisis previo sigue teniendo [N] gap(s) `[CRÍTICO]` pendiente(s) ([IDs]). Decide una de estas dos vías antes de generar specs: (a) responderlos en `<path>_analysis.md` y re-ejecutar; (b) re-ejecutar añadiendo `--allow-open-critical-gaps` para aceptar HUs `[INCOMPLETO]`."
7. Si el script dio `CRITICAL_OPEN` y **sí** se ha pasado `--allow-open-critical-gaps` → continuar al Paso 3 dejando constancia explícita de que las HUs afectadas podrán salir `[INCOMPLETO]`.
8. Si el script dio `CRITICAL_ANSWERED`, inspecciona las respuestas ya resueltas. Si alguna introduce señales de cambio de producto según `kb-product-change-governance`:
   - si **NO** se ha pasado `--allow-derived-scope-from-analysis` → **DETENERSE** e informar al usuario:
     > "Las respuestas del análisis parecen introducir cambio de producto (por ejemplo: nueva entidad persistente, catálogo reutilizable, nueva granularidad funcional o flujo adicional no comprometido en el PRD). Formaliza primero el cambio con `wf-prd-change <prd.md> --new-reqs <cambio.md>` o re-ejecuta añadiendo `--allow-derived-scope-from-analysis` si quieres continuar dejando el scope marcado como derivado."
   - si **SÍ** se ha pasado `--allow-derived-scope-from-analysis` → continuar dejando constancia explícita de que el discovery, `_features.md` y los specs deberán marcar ese alcance como **scope derivado** y no como PRD puro.
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
  prompt: "Ejecuta el skill /wf-spec-discover con los siguientes argumentos: <prd.md> [--analysis <analysis.md>] [--allow-derived-scope-from-analysis si aplica]"
)
```
Espera su resultado (el de la tool, no el del disco) y obtén de él el path del `_discovery.md`. Si el discover se detuvo por shared models ambiguos → transmite el mensaje al usuario y espera resolución.

---

## Paso 4: Leer discovery y determinar el subset a procesar

Lee el `_discovery.md` (recién generado o reutilizado).

Parsea la lista completa de features identificadas:
- Extrae cada Feature ID (F-001, F-002, ...) con su nombre kebab-case
- Cuenta el total de features `N_total`

### 4a — Determinar el subset

- **Si NO hay `--features`**: el subset a procesar = todas las features del discovery.
- **Si hay `--features F-001,F-002,...`**:
  1. Valida que **todos** los IDs solicitados existen en el discovery.
  2. Si alguno no existe → **detén** con mensaje claro: "Los siguientes IDs no aparecen en `<path>_discovery.md`: [lista]. IDs válidos: [lista del discovery]."
  3. El subset = solo las features cuyos IDs aparecen en `--features`.
- **Features NO incluidas en el subset** (caso `--features`): se registrarán en `_features.md` con estado `PENDIENTE_GENERACIÓN` y no se les lanza fast-track en esta ejecución.

### 4a.1 — Guardrail de coste para PRDs grandes

Si no hay `--features` y el discovery contiene >5 features: sin `--all-features` → **DETENERSE** e informar al usuario de iterar por subset con `--features F-001,...`, o re-ejecutar con `--all-features`. Con `--all-features` → continuar.

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
  prompt: "Ejecuta el skill /wf-spec-fast-track con los siguientes argumentos: <prd.md> --scope-from <discovery.md> --feature F-00X [--light|--standard si se pasó o si project-init declara pipeline_mode] [--analysis <analysis.md> si disponible]"
)
```

**CRÍTICO: emite TODOS los `Agent` tool calls en un único mensaje** — no esperes entre ellos. Cada subagente es completamente independiente. Si hay 6 features a generar, tu respuesta debe contener 6 llamadas al `Agent` tool simultáneas, todas con `subagent_type: sdd-spec-writer`.

`run_in_background: false` **no** rompe el paralelismo ([[D-043]]): las N llamadas emitidas en un único mensaje siguen corriendo a la vez; el flag solo garantiza que el mensaje no vuelve hasta que **todas** han terminado — que es justo lo que el Paso 6 asume al regenerar el índice leyendo los specs del disco.

No uses el `Skill` tool para esto — no soporta ejecución paralela.

Espera a que **todas** terminen (esperando el resultado de las tools; **no** listando `features/` en bucle para ver si ya aparecieron los ficheros). Para cada una, registra:
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

Opera sobre **todas las features con spec en `features/`**, incluyendo preexistentes de iteraciones anteriores. Con ≥2 specs: por cada spec recién generado delega con la tool `Agent` ([[D-043]]), `subagent_type: "sdd-spec-auditor"` y `run_in_background: false`, con el prompt `"Ejecuta el skill /wf-spec-conflict con los siguientes argumentos: <spec.md> --features-dir <features_dir>"` (solo los nuevos se chequean contra todos; puedes emitir las N llamadas en un único mensaje). Escribe `_conflict_report.md` si hay conflictos. Sin specs nuevos → omitir.

---

## Paso 8: Readiness check (si no `--skip-readiness`)

Delega con la tool `Agent` ([[D-043]]), `subagent_type: "sdd-spec-auditor"` y `run_in_background: false`, con el prompt `"Ejecuta el skill /wf-spec-readiness con los siguientes argumentos: <features_dir>/"`. Genera `_readiness_report.md` en el directorio raíz de artefactos spec (junto a `_features.md`) y actualiza `_features.md` con el estado de cada feature (incluyendo `PENDIENTE_GENERACIÓN` para las no procesadas aún).

---

## Paso 9: Informar al usuario

Presenta el resumen siguiendo la plantilla de `${CLAUDE_SKILL_DIR}/references/output_template.md`. Diferencia features procesadas en esta iteración vs preexistentes de iteraciones anteriores vs pendientes de futura generación. Incluye los bloques condicionales de siguientes pasos (gaps críticos, conflictos, features listas, features PENDIENTE_GENERACIÓN).
