---
name: wf-spec-features-first
description: Orquestador completo del flujo features-first. Ejecuta discover para identificar features del PRD y luego lanza fast-track en paralelo para cada feature identificada (o solo para un subset si se pasa `--features`). Ejecuta conflict check y readiness al final. Activa en frases como "genera specs por feature del PRD", "flujo features-first completo", "specs en paralelo del PRD", "genera todas las features del PRD", "genera specs de la fase 1", "genera specs de estas features", "features-first completo".
argument-hint: "<prd_archivo.md> [--features F-001,F-002,...] [--skip-conflict] [--skip-readiness]"
effort: high
model: claude-opus-4-6
allowed-tools: [Read, Write, Bash, Agent]
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
- **Flags opcionales**:
  - `--features F-001,F-002,...`: lista separada por comas de Feature IDs a procesar en esta ejecución. Si se omite, se procesan **todas** las features del discovery. Si se incluye, requiere que el `_discovery.md` exista previamente (los IDs solo se conocen tras un discover).
  - `--skip-conflict`: omitir detección de conflictos al final
  - `--skip-readiness`: omitir evaluación de readiness al final

Si no hay argumento, informa al usuario:
> "Uso: `/wf-spec-features-first <prd_archivo.md> [--features F-001,F-002,...] [--skip-conflict] [--skip-readiness]`"
> "Ejemplo (todo el PRD): `/wf-spec-features-first docs/requisitos.md`"
> "Ejemplo (iteración/fase): `/wf-spec-features-first docs/requisitos.md --features F-001,F-002,F-005`"

---

## Paso 2: Verificar el archivo

Verifica que el archivo PRD existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y detén.

---

## Paso 2.5: Análisis de gaps (obligatorio)

1. Busca si existe un `*_analysis.md` para este PRD en el mismo directorio (convención: `<basename>_analysis.md`)
2. **Si existe** → usarlo como contexto. Continuar al Paso 3 pasando el path del analysis.
3. **Si NO existe** → invocar `/wf-spec-analyze <prd.md>`. Tras la ejecución, **DETENERSE** e informar al usuario:
   > "Se ha generado el análisis de gaps en `<path>_analysis.md`. Edita el archivo, responde las preguntas marcadas como _(pendiente)_ (las `[CRÍTICO]` son obligatorias para specs completos) y vuelve a ejecutar `/wf-spec-features-first <prd.md>`."

**Importante:** Este paso **nunca bloquea por gaps sin responder**. Si el analysis existe pero tiene gaps `[CRÍTICO]` con `_(pendiente)_`, se pasa igualmente a discover y fast-track. Los fast-track generarán las HUs afectadas como `[INCOMPLETO]`, que es lo que bloquea `/wf-prepare-plan` (no la generación de specs).

Si el `_analysis.md` o el contexto del proyecto indican que el PRD ha cambiado después de generar specs previos, informa de que puede ser necesario ejecutar `wf-prd-sync-impact` o `wf-spec-sync-from-prd` antes de mezclar nuevas pasadas con artefactos desactualizados.

---

## Paso 3: Ejecutar discover (o reutilizarlo)

**Caso A — `--features` está presente**:
El `_discovery.md` **debe existir previamente** (los IDs `F-XXX` solo tienen sentido contra un discovery existente). Busca `<basename>_discovery.md` en el mismo directorio del PRD.
- Si existe → continúa al Paso 4 reutilizándolo.
- Si NO existe → **detente** e informa al usuario:
  > "Has indicado `--features <IDs>`, pero no existe `<path>_discovery.md`. Las features se identifican en el discovery — ejecuta primero `/wf-spec-discover <prd.md>`, revisa el mapa generado y vuelve a ejecutar con los IDs que correspondan."

**Caso B — `--features` no está presente**:
Si hay `_analysis.md` disponible (del Paso 2.5):
- Invoca `/wf-spec-discover <prd.md> --analysis <analysis.md>`

Si no hay analysis:
- Invoca `/wf-spec-discover <prd.md>`

Espera a que termine. Lee el resultado para obtener:
- Path del `_discovery.md` generado
- Si el discover se detuvo esperando confirmación del usuario (shared models ambiguos) → **detén y transmite el mensaje al usuario**: "El discover detectó shared models con ownership ambiguo. Revisa `<path>_discovery.md`, confirma los owners y vuelve a ejecutar `/wf-spec-features-first <prd.md>`."

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

### 4b — Detectar specs preexistentes

Antes de lanzar fast-track, comprueba para cada feature del subset si ya existe `features/<nombre>/<nombre>_spec.md`:
- Si existe → **no la relances** (sería sobrescribir trabajo previo). Anótala como "ya generada previamente" y excluye de la lista de fast-track de este paso.
- Si no existe → se incluye en el lanzamiento paralelo del Paso 5.

Informa al usuario:
> "Discovery: [N_total] features totales. Esta iteración procesa [N_subset] feature(s): [lista de IDs]. Generando specs en paralelo para [N_a_generar] (las que ya existían se preservan; [N_pendientes] quedarán como PENDIENTE_GENERACIÓN)..."

---

## Paso 5: Lanzar fast-track en paralelo (solo features a generar)

Lanza fast-track únicamente para las features del **subset** que NO tienen spec preexistente (lista calculada en el Paso 4b). Las features que ya tenían spec se preservan tal cual; las que están fuera del subset no se tocan.

Para cada feature F-00X a generar, lanza un subagente con el `Agent` tool usando `subagent_type: sdd-spec-writer`:

```
Agent(
  subagent_type: "sdd-spec-writer",
  prompt: "Ejecuta el skill /wf-spec-fast-track con los siguientes argumentos: <prd.md> --scope-from <discovery.md> --feature F-00X [--analysis <analysis.md> si disponible]"
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

## Paso 6: Consolidar `_features.md` (incremental)

Las escrituras paralelas de `_features.md` por los fast-tracks pueden colisionar. **Regenera `_features.md` de forma consolidada y respetando lo que ya estaba:**

1. Si existe `_features.md` previo, léelo para preservar:
   - Estado de iteraciones anteriores (qué features ya estaban marcadas LISTA, BLOQUEADA_POR_GAPS, PENDIENTE_GENERACIÓN, etc.)
   - Entradas previas del Historial de cambios
2. Lee el `_discovery.md` para obtener el universo completo de features (todas las F-XXX), shared models y mapping RF→Feature.
3. Lee todos los specs de feature presentes en `features/*/` (incluye tanto los recién generados en esta iteración como los preexistentes de iteraciones previas).
4. Construye el `_features.md` unificado con **TODAS las features del discovery**, no solo el subset de esta iteración. Para cada una:
   - Si tiene spec en `features/<nombre>/<nombre>_spec.md` → indexarla con su metadata (descripción, actor, journeys, CAs, modelos extraídos del spec). Estado provisional `LISTA` o `BLOQUEADA_POR_GAPS` según haya HUs `[INCOMPLETO]` (el Paso 8 lo refinará).
   - Si NO tiene spec todavía → indexarla con la metadata mínima del discovery (nombre, actor, scope RFs) y estado `PENDIENTE_GENERACIÓN`. Indica explícitamente: `> Esta feature está identificada en el discovery pero aún no se ha generado spec. Ejecuta /wf-spec-features-first <prd.md> --features <F-XXX> cuando quieras procesarla.`
5. Reconcilia la tabla de shared models entre discovery y specs generados.
6. Mantiene la trazabilidad RF → HU → Feature consolidada (los RFs cuya feature aún esté PENDIENTE_GENERACIÓN se anotan como "HUs no generadas todavía").
7. Añade una entrada al Historial de cambios reflejando esta iteración:
   - Si `--features` se usó: `[YYYY-MM-DD] | features-first (subset) | Iteración sobre [F-001, F-002, ...] — N nuevas + M preservadas`
   - Si no: `[YYYY-MM-DD] | features-first (full) | Generación completa de las N features del discovery`
8. Escribe el `_features.md` en el mismo directorio que el PRD.

---

## Paso 7: Conflict check (si no `--skip-conflict`)

El conflict check opera sobre **todas las features con spec presente en `features/`**, no solo las recién generadas. Esto incluye specs preexistentes de iteraciones anteriores: si la iteración actual introduce un spec que choca con uno previo, debe detectarse.

Si hay 2 o más specs presentes en total:

Para cada spec recién generado en esta iteración, invoca `/wf-spec-conflict <feature_spec.md> --features-dir <features_dir>`. (Los specs preexistentes no se re-chequean entre sí — solo contra los nuevos.)

- Si detecta conflictos → escribe `_conflict_report.md` en el directorio del PRD
- Si no detecta conflictos → registra como "sin conflictos"

Si en esta iteración no se generó ningún spec nuevo (todas las features del subset ya tenían spec previo), salta el conflict check con nota: "Sin specs nuevos en esta iteración — conflict check omitido".

---

## Paso 8: Readiness check (si no `--skip-readiness`)

Invoca `/wf-spec-readiness <features_dir>/`.

- Genera `_readiness_report.md` en el directorio del PRD
- Actualiza `_features.md` con el estado por feature (incluyendo `PENDIENTE_GENERACIÓN` para las que aún no se han procesado en ninguna iteración)

---

## Paso 9: Informar al usuario

Presenta un resumen del flujo, diferenciando lo que se procesó en esta iteración de lo que ya estaba o queda pendiente.

**Resumen de ejecución:**

Indica el modo: "Iteración sobre subset `[F-001, F-002, ...]`" o "Generación completa".

| Feature | Origen | Spec | Gaps críticos | Estado |
|---------|--------|------|---------------|--------|
| F-001: [nombre] | Esta iteración | ✓ / ✗ | [N] | [LISTA / BLOQUEADA_POR_GAPS] |
| F-002: [nombre] | Iteración previa | ✓ | [N] | [LISTA / BLOQUEADA_POR_GAPS] |
| F-003: [nombre] | — | — | — | PENDIENTE_GENERACIÓN |

**Artefactos:**
- Discovery: `<path>_discovery.md`
- Features index: `<path>_features.md` (actualizado incrementalmente)
- Specs: `features/<nombre>/<nombre>_spec.md` (recién generados + preexistentes)
- Conflict report: `<path>_conflict_report.md` (si aplica)
- Readiness report: `<path>_readiness_report.md` (si aplica)

**Siguientes pasos** (según el estado):

Si hay features con gaps `[CRÍTICO]`:
> "Las siguientes features tienen gaps críticos sin resolver: [lista]. Edita los specs afectados, responde los gaps marcados como _(pendiente)_ y ejecuta `/wf-spec-gap-resolve <feature_spec.md>` por cada una."

Si se usó `_analysis.md` con gaps `[CRÍTICO]` sin responder:
> "Hay [N] gaps críticos del análisis previo que no fueron respondidos. Los specs afectados tienen HUs marcadas `[INCOMPLETO]` que bloquean `/wf-prepare-plan`. Responde los gaps en `<path>_analysis.md` y re-ejecuta."

Si hay conflictos de severidad ALTA:
> "Se detectaron conflictos entre features. Revisa `<path>_conflict_report.md` y resuelve antes de planificar."

Si hay features LISTA:
> "Las features marcadas como LISTA pueden avanzar a planificación:"
> ```
> /wf-prepare-plan generate features/<nombre>/<nombre>_spec.md
> ```

Si hay features `PENDIENTE_GENERACIÓN`:
> "Quedan [N] features identificadas en el discovery que aún no se han procesado: [lista de IDs]. Cuando quieras generarlas en una iteración futura:"
> ```
> /wf-spec-features-first <prd.md> --features F-XXX,F-YYY,...
> ```

Si todo está listo y no hay pendientes:
> "Todas las features están listas para planificar. Puedes ejecutar `/wf-prepare-plan generate` por cada una."
