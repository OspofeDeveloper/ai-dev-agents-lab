# Plantilla de salida — Paso 9: Informar al usuario

## Resumen de ejecución

Indica el modo: "Iteración sobre subset `[F-001, F-002, ...]`" o "Generación completa".

| Feature | Origen | Spec | Gaps críticos | Estado |
|---------|--------|------|---------------|--------|
| F-001: [nombre] | Esta iteración | ✓ / ✗ | [N] | [LISTA / BLOQUEADA / REQUIERE_CAMBIO_PRD] |
| F-002: [nombre] | Iteración previa | ✓ | [N] | [LISTA / BLOQUEADA / REQUIERE_CAMBIO_PRD] |
| F-003: [nombre] | — | — | — | PENDIENTE_GENERACIÓN |
| F-004: [nombre] | Iteración previa | ✓ | — | RETIRADA |

## Artefactos

- Discovery: `<path>_discovery.md`
- Features index: `<path>_features.md` (actualizado incrementalmente)
- Specs: `features/<nombre>/spec/<nombre>_spec.md` (recién generados + preexistentes; features planas legacy: sin subcarpeta)
- Conflict report: `<path>_conflict_report.md` (si aplica)
- Readiness report: `<path>_readiness_report.md` (si aplica)

## Siguientes pasos (bloques condicionales)

> **Estos mensajes los lee el usuario, así que van en lenguaje natural.** No le des nombres de
> workflow ni comandos con flags: el ecosistema se conduce **hablando**, y quien construye los
> argumentos —con sus validaciones— eres tú, no él. Un comando surfaceado invita a teclearlo a
> mano y a saltarse esa construcción.

**Si hay features con gaps `[CRÍTICO]`:**
> "Las siguientes features tienen gaps críticos sin resolver: [lista]. Responde los gaps
> marcados como _(pendiente)_ en `<path>_analysis.md` y pídeme que **complete las historias
> incompletas** de esas features."

**Si se usó `_analysis.md` con gaps `[CRÍTICO]` sin responder:**
> "Hay [N] gaps críticos del análisis previo que no fueron respondidos. Los specs afectados
> tienen HUs marcadas `[INCOMPLETO]`, y eso **bloquea el paso a planificación**. Responde los
> gaps en `<path>_analysis.md` y dímelo para retomarlo."

**Si hay conflictos de severidad ALTA:**
> "Se detectaron conflictos entre features. Revisa `<path>_conflict_report.md` y resuélvelos
> antes de planificar."

**Si hay features LISTA:**
> "Las features marcadas como LISTA pueden avanzar a planificación: [lista]. Dime cuál quieres
> planificar —o si prefieres empezar por todas— y me encargo."

**Si hay features `PENDIENTE_GENERACIÓN`:**
> "Quedan [N] features identificadas en el discovery que aún no se han procesado: [lista de
> IDs]. Cuando quieras generarlas, dímelo indicando cuáles."

**Si todo está listo y no hay pendientes:**
> "Todas las features están listas para planificar. Dime por cuál empezamos."
