---
name: wf-prd-sync-impact
description: Analiza el impacto de un PRD actualizado sobre los artefactos SDD ya generados. Compara la versión vigente del PRD con analysis, discovery, features, specs, plan y tasks, y produce un informe de sincronización con estado por artefacto y siguientes pasos recomendados. Activa en frases como "qué impacto tiene este cambio de PRD", "qué specs han quedado stale", "analiza sync PRD → specs", "qué artefactos hay que revisar tras cambiar el PRD".
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

Para cada artefacto, asigna uno de estos estados:

- `in_sync`
- `needs_review`
- `stale`
- `unknown`

Justifica el estado con una línea concreta.

Reglas:

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
