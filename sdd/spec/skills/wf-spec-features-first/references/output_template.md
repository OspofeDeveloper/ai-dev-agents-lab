# Plantilla de salida — Paso 9: Informar al usuario

## Resumen de ejecución

Indica el modo: "Iteración sobre subset `[F-001, F-002, ...]`" o "Generación completa".

| Feature | Origen | Spec | Gaps críticos | Estado |
|---------|--------|------|---------------|--------|
| F-001: [nombre] | Esta iteración | ✓ / ✗ | [N] | [LISTA / BLOQUEADA / REQUIERE_CAMBIO_PRD] |
| F-002: [nombre] | Iteración previa | ✓ | [N] | [LISTA / BLOQUEADA / REQUIERE_CAMBIO_PRD] |
| F-003: [nombre] | — | — | — | PENDIENTE_GENERACIÓN |

## Artefactos

- Discovery: `<path>_discovery.md`
- Features index: `<path>_features.md` (actualizado incrementalmente)
- Specs: `features/<nombre>/spec/<nombre>_spec.md` (recién generados + preexistentes; features planas legacy: sin subcarpeta)
- Conflict report: `<path>_conflict_report.md` (si aplica)
- Readiness report: `<path>_readiness_report.md` (si aplica)

## Siguientes pasos (bloques condicionales)

**Si hay features con gaps `[CRÍTICO]`:**
> "Las siguientes features tienen gaps críticos sin resolver: [lista]. Edita los specs afectados, responde los gaps marcados como _(pendiente)_ y ejecuta `/wf-spec-gap-resolve <feature_spec.md>` por cada una."

**Si se usó `_analysis.md` con gaps `[CRÍTICO]` sin responder:**
> "Hay [N] gaps críticos del análisis previo que no fueron respondidos. Los specs afectados tienen HUs marcadas `[INCOMPLETO]` que bloquean `/wf-prepare-plan`. Responde los gaps en `<path>_analysis.md` y re-ejecuta."

**Si hay conflictos de severidad ALTA:**
> "Se detectaron conflictos entre features. Revisa `<path>_conflict_report.md` y resuelve antes de planificar."

**Si hay features LISTA:**
> "Las features marcadas como LISTA pueden avanzar a planificación:"
> ```
> /wf-prepare-plan generate features/<nombre>/spec/<nombre>_spec.md
> ```

**Si hay features `PENDIENTE_GENERACIÓN`:**
> "Quedan [N] features identificadas en el discovery que aún no se han procesado: [lista de IDs]. Para generarlas en una iteración futura:"
> ```
> /wf-spec-features-first <prd.md> --features F-XXX,F-YYY,...
> ```

**Si todo está listo y no hay pendientes:**
> "Todas las features están listas para planificar. Puedes ejecutar `/wf-prepare-plan generate` por cada una."
