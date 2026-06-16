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

**Regla de oro:** Eres un orquestador. No analizas contenido, no generas specs, no tomas decisiones funcionales. Invocas skills en el orden correcto y consolidas resultados.

**Sobre el flujo iterativo por subset:** las "fases" o "iteraciones" no se definen en el PRD ni en el discovery — son una decisión humana de delivery sobre qué features procesar en cada pasada. El usuario decide el subset **después** de ver el discovery; cada ejecución con `--features` actualiza `_features.md` de forma incremental, sin borrar las features ya generadas en pasadas anteriores ni las pendientes para futuras.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del PRD**: el primer argumento
- **Flags opcionales**: `--features F-001,...` (IDs a procesar, requiere discovery previo); `--light`/`--standard` (modo del pipeline — se propaga a cada fast-track; sin flag rige `pipeline_mode` de `.sdd/project-init.json`); `--allow-open-critical-gaps` (genera con gaps críticos abiertos → HUs `[INCOMPLETO]`); `--allow-derived-scope-from-analysis` (continúa aunque el analysis expanda el PRD); `--all-features` (full-run override para PRDs grandes); `--skip-conflict`/`--skip-readiness` (omitir checks finales).

Si no hay argumento, informa el uso con todos los flags opcionales y ejemplos de los modos principales: completo sin flags, subset con `--features`, con `--allow-open-critical-gaps`, con `--allow-derived-scope-from-analysis`.

---

## Paso 2: Verificar el archivo

Verifica que el archivo PRD existe; si no → informa con ruta exacta y detén.

---

## Paso 2.5: Análisis de gaps (obligatorio)

1. Busca si existe un `*_analysis.md` para este PRD (convención: `<basename>_analysis.md`). Búscalo en el directorio de artefactos prd (`artifacts.prd` de `.sdd/project-init.json`, si está declarado) y en el mismo directorio del PRD.
2. **Si NO existe** → invocar `/wf-spec-analyze <prd.md>`. Tras la ejecución, **DETENERSE** e informar al usuario:
   > "Se ha generado el análisis de gaps en `<path>_analysis.md`. Edita el archivo, responde las preguntas marcadas como _(pendiente)_ (las `[CRÍTICO]` son obligatorias para specs completos) y vuelve a ejecutar `/wf-spec-features-first <prd.md>`."
3. **Si existe** → léelo y determina: veredicto (`LISTO_PARA_SPECS`, `LISTO_PARA_SPECS_CON_PREGUNTAS`, `REQUIERE_LIMPIEZA_PRD`), gaps `[CRÍTICO]` pendientes, presencia de `[PUEDE_REQUERIR_CR]`, y si hay respuestas resueltas que introducen expansión funcional no comprometida.
4. Si el veredicto es `REQUIERE_LIMPIEZA_PRD` → **DETENERSE** e informar al usuario:
   > "El análisis previo marca `REQUIERE_LIMPIEZA_PRD`. Corrige la contaminación técnica del PRD antes de continuar y vuelve a ejecutar el flujo."
5. Si hay gaps `[CRÍTICO]` pendientes y **no** se ha pasado `--allow-open-critical-gaps` → **DETENERSE** e informar al usuario:
   > "El análisis previo sigue teniendo [N] gap(s) `[CRÍTICO]` pendiente(s). Decide una de estas dos vías antes de generar specs: (a) responderlos en `<path>_analysis.md` y re-ejecutar; (b) re-ejecutar añadiendo `--allow-open-critical-gaps` para aceptar HUs `[INCOMPLETO]`."
6. Si hay gaps `[CRÍTICO]` pendientes y **sí** se ha pasado `--allow-open-critical-gaps` → continuar al Paso 3 dejando constancia explícita de que las HUs afectadas podrán salir `[INCOMPLETO]`.
7. Si no hay gaps `[CRÍTICO]` pendientes, inspecciona las respuestas ya resueltas. Si alguna introduce señales de cambio de producto según `kb-product-change-governance`:
   - si **NO** se ha pasado `--allow-derived-scope-from-analysis` → **DETENERSE** e informar al usuario:
     > "Las respuestas del análisis parecen introducir cambio de producto (por ejemplo: nueva entidad persistente, catálogo reutilizable, nueva granularidad funcional o flujo adicional no comprometido en el PRD). Formaliza primero el cambio con `wf-prd-change <prd.md> --new-reqs <cambio.md>` o re-ejecuta añadiendo `--allow-derived-scope-from-analysis` si quieres continuar dejando el scope marcado como derivado."
   - si **SÍ** se ha pasado `--allow-derived-scope-from-analysis` → continuar dejando constancia explícita de que el discovery, `_features.md` y los specs deberán marcar ese alcance como **scope derivado** y no como PRD puro.
8. Si no hay gaps `[CRÍTICO]` pendientes y no se detectan señales de cambio → continuar al Paso 3 usando el `_analysis.md` como contexto.

**Importante:** `[INFORMATIVO]` nunca bloquea; `[CRÍTICO]` abiertos requieren `--allow-open-critical-gaps`. Para señales de expansión consulta `kb-product-change-governance`. Si el PRD cambió después de generar specs previos, puede ser necesario `wf-prd-sync-impact` antes de mezclar pasadas.

---

## Paso 3: Ejecutar discover (o reutilizarlo)

**Caso A — `--features` está presente**:
El `_discovery.md` **debe existir previamente** (los IDs `F-XXX` solo tienen sentido contra un discovery existente). Busca `<basename>_discovery.md` en el directorio de artefactos prd (`artifacts.prd` de `.sdd/project-init.json`, si está declarado) y en el mismo directorio del PRD.
- Si existe → continúa al Paso 4 reutilizándolo.
- Si NO existe → **detente** e informa al usuario:
  > "Has indicado `--features <IDs>`, pero no existe `<path>_discovery.md`. Las features se identifican en el discovery — ejecuta primero `/wf-spec-discover <prd.md>`, revisa el mapa generado y vuelve a ejecutar con los IDs que correspondan."

**Caso B — `--features` no está presente**:
Invoca `/wf-spec-discover <prd.md> [--analysis <analysis.md>] [--allow-derived-scope-from-analysis si aplica]`. Espera que termine y obtén el path del `_discovery.md`. Si el discover se detuvo por shared models ambiguos → transmite el mensaje al usuario y espera resolución.

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
  prompt: "Ejecuta el skill /wf-spec-fast-track con los siguientes argumentos: <prd.md> --scope-from <discovery.md> --feature F-00X [--light|--standard si se pasó o si project-init declara pipeline_mode] [--analysis <analysis.md> si disponible]"
)
```

**CRÍTICO: emite TODOS los `Agent` tool calls en un único mensaje** — no esperes entre ellos. Cada subagente es completamente independiente. Si hay 6 features a generar, tu respuesta debe contener 6 llamadas al `Agent` tool simultáneas, todas con `subagent_type: sdd-spec-writer`.

No uses el `Skill` tool para esto — no soporta ejecución paralela.

Espera a que **todas** terminen. Para cada una, registra:
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

Opera sobre **todas las features con spec en `features/`**, incluyendo preexistentes de iteraciones anteriores. Con ≥2 specs: por cada spec recién generado invoca `/wf-spec-conflict <spec.md> --features-dir <features_dir>` (solo los nuevos se chequean contra todos). Escribe `_conflict_report.md` si hay conflictos. Sin specs nuevos → omitir.

---

## Paso 8: Readiness check (si no `--skip-readiness`)

Invoca `/wf-spec-readiness <features_dir>/`. Genera `_readiness_report.md` en el directorio raíz de artefactos spec (junto a `_features.md`) y actualiza `_features.md` con el estado de cada feature (incluyendo `PENDIENTE_GENERACIÓN` para las no procesadas aún).

---

## Paso 9: Informar al usuario

Presenta el resumen siguiendo la plantilla de `${CLAUDE_SKILL_DIR}/references/output_template.md`. Diferencia features procesadas en esta iteración vs preexistentes de iteraciones anteriores vs pendientes de futura generación. Incluye los bloques condicionales de siguientes pasos (gaps críticos, conflictos, features listas, features PENDIENTE_GENERACIÓN).
