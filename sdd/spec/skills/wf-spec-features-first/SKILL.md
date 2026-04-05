---
name: wf-spec-features-first
description: Orquestador completo del flujo features-first. Ejecuta discover para identificar features del PRD y luego lanza fast-track en paralelo para cada feature identificada. Ejecuta conflict check y readiness al final. Activa en frases como "genera specs por feature del PRD", "flujo features-first completo", "specs en paralelo del PRD", "genera todas las features del PRD", "features-first completo".
argument-hint: "<prd_archivo.md> [--skip-conflict] [--skip-readiness]"
effort: high
model: claude-opus-4-6
allowed-tools: [Read, Write, Bash, Agent]
---

# Workflow: FEATURES-FIRST (Orquestador)

Tu objetivo es ejecutar el flujo features-first completo: identificar features de un PRD y generar un spec por cada una en paralelo. Este skill **no delega a `sdd-analyst`** — orquesta otros workflow skills.

**Regla de oro:** Eres un orquestador. No analizas contenido, no generas specs, no tomas decisiones funcionales. Invocas skills en el orden correcto y consolidas resultados.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del PRD**: el primer argumento
- **Flags opcionales**:
  - `--skip-conflict`: omitir detección de conflictos al final
  - `--skip-readiness`: omitir evaluación de readiness al final

Si no hay argumento, informa al usuario:
> "Uso: `/wf-spec-features-first <prd_archivo.md>`"
> "Ejemplo: `/wf-spec-features-first docs/requisitos.md`"
> "Flags opcionales: `--skip-conflict`, `--skip-readiness`"

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

---

## Paso 3: Ejecutar discover

Si hay `_analysis.md` disponible (del Paso 2.5):
- Invoca `/wf-spec-discover <prd.md> --analysis <analysis.md>`

Si no hay analysis:
- Invoca `/wf-spec-discover <prd.md>`

Espera a que termine. Lee el resultado para obtener:
- Path del `_discovery.md` generado
- Si el discover se detuvo esperando confirmación del usuario (shared models ambiguos) → **detén y transmite el mensaje al usuario**: "El discover detectó shared models con ownership ambiguo. Revisa `<path>_discovery.md`, confirma los owners y vuelve a ejecutar `/wf-spec-features-first <prd.md>`."

---

## Paso 4: Leer discovery y extraer features

Lee el `_discovery.md` generado.

Parsea la lista de features identificadas:
- Extrae cada Feature ID (F-001, F-002, ...)
- Extrae el nombre kebab-case de cada feature
- Cuenta el total de features

Informa al usuario del progreso:
> "Discovery completado: [N] features identificadas. Generando specs en paralelo..."

---

## Paso 5: Lanzar fast-track en paralelo

Para cada feature F-00X del discovery, lanza un subagente con el `Agent` tool usando `subagent_type: sdd-analyst`:

```
Agent(
  subagent_type: "sdd-analyst",
  prompt: "Ejecuta el skill /wf-spec-fast-track con los siguientes argumentos: <prd.md> --scope-from <discovery.md> --feature F-00X [--analysis <analysis.md> si disponible]"
)
```

**CRÍTICO: emite TODOS los `Agent` tool calls en un único mensaje** — no esperes entre ellos. Cada subagente es completamente independiente. Si hay 6 features, tu respuesta debe contener 6 llamadas al `Agent` tool simultáneas, todas con `subagent_type: sdd-analyst`.

No uses el `Skill` tool para esto — no soporta ejecución paralela.

Espera a que **todas** terminen. Para cada una, registra:
- Feature ID y nombre
- Si se completó con éxito o falló
- Path del spec generado
- Número de gaps `[CRÍTICO]` encontrados (si los hay)
- Número de asunciones aplicadas

---

## Paso 6: Consolidar `_features.md`

Las escrituras paralelas de `_features.md` por los fast-tracks pueden colisionar. **Regenera `_features.md` de forma consolidada:**

1. Lee todos los specs de feature generados en `features/*/`
2. Lee el `_discovery.md` para los shared models y el mapping RF→Feature
3. Genera un `_features.md` unificado con:
   - Todas las features indexadas con su metadata (descripción, actor, journeys, CAs, modelos)
   - Tabla de shared models completa (reconciliada entre discovery y specs generados)
   - Trazabilidad RF → HU → Feature consolidada (mapeando los RFs del discovery a las HUs de cada spec)
   - Historial de cambios con entrada: `[fecha] | features-first | Features generadas desde wf-spec-features-first`
4. Escribe el `_features.md` en el mismo directorio que el PRD

---

## Paso 7: Conflict check (si no `--skip-conflict`)

Si se generaron **2 o más features con specs válidos**:

Para cada spec de feature generado, invoca `/wf-spec-conflict <feature_spec.md> --features-dir <features_dir>`.

- Si detecta conflictos → escribe `_conflict_report.md` en el directorio del PRD
- Si no detecta conflictos → registra como "sin conflictos"

---

## Paso 8: Readiness check (si no `--skip-readiness`)

Invoca `/wf-spec-readiness <features_dir>/`.

- Genera `_readiness_report.md` en el directorio del PRD
- Actualiza `_features.md` con el estado por feature

---

## Paso 9: Informar al usuario

Presenta un resumen completo del flujo:

**Resumen de ejecución:**

| Feature | Spec | Gaps críticos | Estado |
|---------|------|---------------|--------|
| F-001: [nombre] | ✓ / ✗ | [N] | [LISTA / BLOQUEADA_POR_GAPS] |

**Artefactos generados:**
- Discovery: `<path>_discovery.md`
- Features index: `<path>_features.md`
- Specs: `features/<nombre>/<nombre>_spec.md` (listar todos)
- Conflict report: `<path>_conflict_report.md` (si aplica)
- Readiness report: `<path>_readiness_report.md` (si aplica)

**Siguientes pasos** (según el estado):

Si hay features con gaps `[CRÍTICO]`:
> "Las siguientes features tienen gaps críticos sin resolver: [lista]. Edita los specs afectados, responde los gaps marcados como _(pendiente)_ y ejecuta `/wf-spec-delta resolve <feature_spec.md>` por cada una."

Si se usó `_analysis.md` con gaps `[CRÍTICO]` sin responder:
> "Hay [N] gaps críticos del análisis previo que no fueron respondidos. Los specs afectados tienen HUs marcadas `[INCOMPLETO]` que bloquean `/wf-prepare-plan`. Responde los gaps en `<path>_analysis.md` y re-ejecuta."

Si hay conflictos de severidad ALTA:
> "Se detectaron conflictos entre features. Revisa `<path>_conflict_report.md` y resuelve antes de planificar."

Si hay features LISTA:
> "Las features marcadas como LISTA pueden avanzar a planificación:"
> ```
> /wf-prepare-plan generate features/<nombre>/<nombre>_spec.md
> ```

Si todo está listo:
> "Todas las features están listas para planificar. Puedes ejecutar `/wf-prepare-plan generate` por cada una."
