---
name: wf-prd-sync-impact
description: "Analiza el impacto de un PRD actualizado sobre los artefactos SDD ya generados (analysis, discovery, features, specs, plan, tasks) y produce un informe de sincronizacion con estado por artefacto y siguientes pasos."
when_to_use: "Activa en frases como 'que impacto tiene este cambio de PRD', 'que specs han quedado stale', 'analiza sync PRD → specs', 'que artefactos hay que revisar tras cambiar el PRD'."
argument-hint: "<prd.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-auditor
---

# Workflow: PRD-SYNC-IMPACT

Tu objetivo es determinar qué artefactos derivados deben revisarse tras un cambio en el PRD.

Usa `kb-product-change-governance` y `kb-traceability-rules` para aplicar criterios conservadores: si no puedes demostrar que un artefacto sigue alineado, no lo marques `in_sync`.

## Paso 1: Parsear argumentos

Extrae el path del PRD.

Si falta:
> "Uso: `/wf-prd-sync-impact <prd.md>`"

## Paso 2: Descubrir artefactos relacionados

En el directorio del PRD, busca si existen:

- `*_analysis.md`
- `*_discovery.md`
- `*_features.md`
- `features/*/*_spec.md`
- `features/*/*_plan.md`
- `features/*/*_tasks.md`
- `product-changelog.md`
- `changes/CR-XXX/change-request.md`
- `changes/CR-XXX/decision.md`

## Paso 3: Leer el contexto mínimo necesario

Lee:

- PRD actual
- changelog del producto si existe
- artefactos del cambio más recientes en `changes/CR-XXX/` si existen
- índice `_features.md` si existe
- headers y metadata de specs, plans y tasks
- contenido completo de los artefactos cuya sincronía no pueda decidirse solo por metadata

Si existe carpeta `changes/`, úsala como fuente prioritaria para entender el alcance exacto del último cambio aprobado. `product-changelog.md` sirve como índice; `change-request.md` y `decision.md` contienen el detalle operativo.

## Paso 4: Evaluar estado por artefacto

**Pre-pass determinista sobre los specs**: ejecuta desde la raíz del proyecto (si el script existe):

```
python3 .sdd/scripts/sdd-sync-check.py check-all <directorio_de_features> --mark
```

El resultado es evidencia mecánica, no opinión: `DERIVA` = el PRD cambió desde el sellado del spec (su `status_sync` queda en `needs_review`); `IN_SYNC` = verificado por hash contra el PRD actual; `SIN_SELLO`/`PRD_NO_RESUELVE` = sin evidencia (aplica el criterio conservador de `kb-traceability-rules`, Regla 3). Nunca marques `in_sync` un spec que el script reporta `DERIVA`.

Para cada artefacto, asigna uno de estos estados:

- `in_sync`
- `needs_review`
- `stale`
- `unknown`

Justifica el estado con una línea concreta.

Reglas:

- si el script reporta `DERIVA` para un spec, al menos `needs_review` (evidencia por hash)
- si el PRD cambió en una sección que afecta claramente al artefacto, al menos `needs_review`
- si el artefacto contradice el PRD actual, `stale`
- si no hay metadata ni evidencia suficiente, `unknown`

## Paso 5: Generar matriz de impacto

Produce un informe `<basename>_sync_report.md` con tablas separadas para:

- analysis/discovery/features index
- specs por feature
- plans por feature
- tasks por feature

Cada fila debe incluir:

- artefacto
- versión base conocida
- estado sync
- motivo
- acción recomendada

## Paso 6: Recomendar acciones

Mapea cada estado a un siguiente paso:

- `in_sync` → sin acción
- `needs_review` → `wf-spec-sync-from-prd analyze`
- `stale` → `wf-spec-sync-from-prd apply` o regeneración explícita
- `unknown` → revisión manual o análisis de sync
