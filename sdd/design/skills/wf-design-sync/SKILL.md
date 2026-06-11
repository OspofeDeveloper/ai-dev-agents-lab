---
name: wf-design-sync
description: "Analiza el impacto de un cambio en el DESIGN.md, brief o spec sobre los artefactos de diseño derivados (flows, views, ui_prompt, exports de tokens): marca cuáles quedaron stale, con estado por artefacto y siguientes pasos. Réplica de wf-prd-sync-impact en Design."
when_to_use: "Activa en frases como 'qué artefactos de diseño quedaron desactualizados', 'qué views hay que regenerar tras cambiar el DESIGN.md', 'analiza el impacto del cambio visual', 'qué prototipos están stale', 'sincroniza el diseño tras el cambio de spec'. No activa para evolucionar el DESIGN.md (usa wf-design-delta) ni para auditarlo sin derivados (usa wf-design-validate)."
argument-hint: "<DESIGN.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: design-architect
user-invocable: true
---

# Workflow: DESIGN-SYNC-IMPACT

Tu objetivo es determinar qué artefactos de diseño derivados deben revisarse tras un cambio en el sistema visual (`DESIGN.md`), en el brief (`DESIGN_BRIEF.md`) o en un `_spec.md` del que cuelgan prototipos. Hoy esa deriva es silenciosa: `wf-design-delta` solo dice "considera regenerar" y nadie comprueba qué quedó stale.

Usa `kb-design-governance` (política de evolución, Regla 2) y `kb-design-expert` con criterio **conservador**: si no puedes demostrar que un artefacto sigue alineado con sus fuentes, no lo marques `in_sync`.

> Alcance: este workflow hace **análisis de impacto** (lectura + razonamiento conservador), no detección por hash. El sellado determinista de la deriva diseño (hash de `DESIGN.md`/spec en el header de cada artefacto, à la `sdd-sync-check.py` de la fase spec) es endurecimiento futuro — anotado como candidato en ROADMAP 11.2. Hasta entonces, el criterio conservador es la red.

## Paso 1: Parsear argumentos

Extrae el path del `DESIGN.md`.

Si falta:
> "Uso: `/wf-design-sync <DESIGN.md>`"

## Paso 2: Resolver el DESIGN.md y descubrir artefactos derivados

Verifica que el `DESIGN.md` existe (si no, detén e informa). La **raíz de diseño** es el directorio que lo contiene (típicamente el que contiene `features/`, o `artifacts.design` si `.sdd/project-init.json` lo declara).

Desde esa raíz, descubre:

- `DESIGN_BRIEF.md` (brief de producto, si existe)
- Por feature (subcarpeta `features/<n>/design/` o, en layout plano legacy, la raíz de la feature):
  - `<n>_flows.md`
  - `<n>_views.md`
  - `<n>_ui_prompt.md`
- `<n>_spec.md` de cada feature (subcarpeta `spec/` o raíz legacy) — fuente funcional de sus prototipos
- Exports de tokens si existen (salidas de `wf-design-export`: `css`, `style-dictionary`, `compose`, `swiftui`, `tailwind` bajo el `--output-dir` usado)
- `<n>_design_discovery.md` / moodboard si existen (insumos pre-DESIGN)

## Paso 3: Leer el contexto mínimo necesario

Lee: `DESIGN.md` completo, `DESIGN_BRIEF.md` si existe, y por feature los headers de `_flows`/`_views`/`_ui_prompt` + el header del `_spec.md`. Lee el contenido completo de cualquier artefacto cuya sincronía no puedas decidir solo por header.

## Paso 4: Evaluar estado por artefacto (grafo de dependencias)

El grafo de derivación de la fase Design:

```
DESIGN_BRIEF.md ─► DESIGN.md ─► (por feature) _views.md, _ui_prompt.md
                      │         exports de tokens (css/compose/...)
   _spec.md (feature) ─────────► _flows.md, _views.md, _ui_prompt.md
```

Propagación de deriva (criterio conservador — ante la duda, `needs_review`):

- **Si cambió `DESIGN_BRIEF.md`** (policy de autonomía, `clarity_vs_brand`, `accessibility_target`, dirección visual): `DESIGN.md` → `needs_review`; transitivamente todos los artefactos de feature → `needs_review`.
- **Si cambió `DESIGN.md`** (tokens, componentes, estilo): `_views.md` y `_ui_prompt.md` de TODAS las features que lo consumieron → `needs_review`; exports de tokens → `stale` (deben re-exportarse); `_flows.md` suele quedar `in_sync` (secuencias, no dependen de tokens) salvo que el cambio afecte navegación o estados visuales que el flow describa.
- **Si cambió un `<n>_spec.md`** (HUs/CAs/journeys de esa feature): `_flows.md`, `_views.md` y `_ui_prompt.md` de ESA feature → `needs_review` (la superficie funcional pudo cambiar); el `DESIGN.md` solo si el cambio introduce un tipo de superficie/componente que el sistema no cubre (entonces `needs_review`), si no `in_sync`.
- Si un artefacto **contradice** su fuente actual (p. ej. un view referencia un token que el `DESIGN.md` ya no define) → `stale`.
- Si no hay header ni evidencia suficiente para decidir → `unknown`.

Estados posibles por artefacto: `in_sync` · `needs_review` · `stale` · `unknown`. Justifica cada uno con una línea concreta (qué fuente cambió y por qué afecta).

## Paso 5: Generar la matriz de impacto

Produce `<basename>_design_sync_report.md` (junto al `DESIGN.md`) con tablas separadas para:

- `DESIGN.md` y `DESIGN_BRIEF.md` (nivel producto)
- artefactos de feature (`_flows`/`_views`/`_ui_prompt`) por feature
- exports de tokens

Cada fila: artefacto · fuente(s) de la que deriva · estado sync · motivo · acción recomendada.

## Paso 6: Recomendar acciones

Mapea cada estado a su siguiente paso:

- `in_sync` → sin acción
- `needs_review` / `stale` en **`DESIGN.md`** → `wf-design-delta analyze <DESIGN.md> --new-reqs <cambios.md>` (evolución incremental) o regeneración con `wf-design-system`
- `needs_review` / `stale` en **artefactos de feature** → `wf-design-feature-prototype generate <feature_spec.md>` (regenera flows/views/ui_prompt desde el spec + DESIGN.md vigentes)
- `stale` en **exports de tokens** → `wf-design-export <DESIGN.md> --platforms ...` (re-exporta)
- `unknown` → revisión manual; si procede, `wf-design-validate <DESIGN.md>`

No regeneres tú los artefactos: este workflow solo diagnostica y recomienda (read-only sobre los artefactos derivados; solo escribe su propio `_design_sync_report.md`).
