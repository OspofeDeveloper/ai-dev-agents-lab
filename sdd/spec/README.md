# SDD Spec — Etapa 1: Specify

Este directorio contiene todos los agentes y skills que transforman un documento de requisitos en Specs SDD válidos y autocontenidos por feature.

---

## Flujo

```
PRD (sucio)
    ↓ /wf-spec-map                        → prd_project_map.md
    ↓ [usuario valida el mapa]            ← checkpoint estratégico
    ↓ /wf-spec-map-analyze                → features/<X>/_analysis.md (por feature)
    ↓ [usuario responde gaps por feature] ← checkpoint táctico
    ↓ /wf-spec-map-generate
    ↓
_features.md + features/<nombre>/<nombre>_spec.md
    ↓ /prepare-plan generate (por feature)
features/<nombre>/<nombre>_plan.md
    ↓ /prepare-tasks generate (por feature)
features/<nombre>/<nombre>_tasks.md
```

---

## Casos de uso

### 1. Proyecto nuevo — flujo completo

```
/wf-spec-map prd.md
  → genera prd_project_map.md (features, interacciones, scope, flags de riesgo)

[edita prd_project_map.md — valida que las features son las correctas]

/wf-spec-map-analyze prd.md
  → genera features/<nombre>/_analysis.md por cada feature del mapa

[para cada feature, edita su _analysis.md y responde los gaps [CRÍTICO]]

/wf-spec-map-generate prd.md
  → genera features/<nombre>/<nombre>_spec.md por cada feature
  → genera features/<nombre>/README.md por cada feature
  → genera prd_features.md (índice de features + shared models)
```

---

### 2. Validar un spec tras edición manual

```
/wf-spec-validate features/auth/auth_spec.md
  → imprime informe APROBADO / REQUIERE_REVISIÓN (no genera archivo)
```

Útil como gate antes de ejecutar `/prepare-plan`.

---

### 3. Detectar conflictos entre specs de features

```
/wf-spec-conflict features/auth/auth_spec.md --features-dir features/
  → genera features/auth/auth_conflict_report.md si hay conflictos
```

Se ejecuta automáticamente al final de `/wf-spec-map-generate` (no bloqueante). Usa este skill directamente si modificas un spec manualmente.

---

## Arquitectura de skills

```
┌──────────────────────────────────────────────────────────┐
│  WORKFLOW SKILLS (invocables directamente)               │
│                                                          │
│  wf-spec-map  │  wf-spec-map-analyze  │  wf-spec-map-generate  │
│  wf-spec-validate  │  wf-spec-conflict                   │
│                                                          │
│  context: fork  │  agent: sdd-analyst                   │
└──────────────────────────┬───────────────────────────────┘
                           │ delega en
                           ▼
┌──────────────────────────────────────────────────────────┐
│  sdd-analyst (agente worker)                             │
│  memory: project  │  permissionMode: acceptEdits         │
└──────────────────────────┬───────────────────────────────┘
                           │ carga como contexto
                           ▼
┌──────────────────────────────────────────────────────────┐
│  KNOWLEDGE SKILLS (solo contexto)                        │
│                                                          │
│  kb-spec-expert  │  kb-decompose-expert                  │
│  kb-conflict-expert  │  kb-gap-conventions               │
│                                                          │
│  disable-model-invocation: true                          │
└──────────────────────────────────────────────────────────┘
```

---

## Mapa de componentes

### Workflow skills

| Skill | Produce | Descripción |
|-------|---------|-------------|
| `wf-spec-map` | `_project_map.md` | Extrae features, interacciones y scope del PRD |
| `wf-spec-map-analyze` | `features/<x>/_analysis.md` (por feature) | Analiza cada feature individualmente con el mapa como contexto |
| `wf-spec-map-generate` | `features/<x>/<x>_spec.md` + `_features.md` | Genera specs por feature directamente |
| `wf-spec-validate` | informe inline | Audita un spec existente (no genera archivo) |
| `wf-spec-conflict` | `_conflict_report.md` | Detecta conflictos entre specs de features |

### Knowledge skills

| Skill | Qué contiene | Usado en |
|-------|--------------|----------|
| `kb-spec-expert` | 8 elementos SDD, Prueba de Pureza, Testabilidad | `wf-spec-map-analyze`, `wf-spec-map-generate`, `wf-spec-validate`, `wf-spec-conflict` |
| `kb-decompose-expert` | Features válidas, shared models, ownership | `wf-spec-map`, `wf-spec-map-generate` |
| `kb-conflict-expert` | 5 reglas de detección de conflictos | `wf-spec-conflict` (y verificación automática en `wf-spec-map-generate`) |
| `kb-gap-conventions` | IDs `[P-XXX]`, severidades, marcador pendiente | `wf-spec-map-analyze`, `wf-spec-map-generate` |

---

## Routing del agente sdd-analyst

```
wf-spec-map          → kb-decompose-expert
wf-spec-map-analyze  → kb-spec-expert + kb-gap-conventions
wf-spec-map-generate → kb-spec-expert + kb-gap-conventions + kb-decompose-expert
wf-spec-validate     → kb-spec-expert
wf-spec-conflict     → kb-conflict-expert + kb-spec-expert
```

---

## Artefactos producidos

```
proyecto/
├── prd.md                              ← Input — no se modifica
├── prd_project_map.md                  ← /wf-spec-map
├── prd_features.md                     ← /wf-spec-map-generate
├── _conflict_report.md                 ← /wf-spec-map-generate (automático) o /wf-spec-conflict
└── features/
    └── <nombre-feature>/
        ├── _analysis.md                ← /wf-spec-map-analyze
        ├── README.md                   ← /wf-spec-map-generate
        ├── <nombre>_spec.md            ← /wf-spec-map-generate
        ├── <nombre>_conflict_report.md ← /wf-spec-conflict
        ├── <nombre>_plan.md            ← /prepare-plan (etapa siguiente)
        └── <nombre>_tasks.md           ← /prepare-tasks (etapa siguiente)
```

---

## Checkpoints humanos

| Momento | Qué hacer | Bloquea si no se hace |
|---------|-----------|-----------------------|
| Tras `wf-spec-map` | Revisar `_project_map.md` — features, interacciones, scope | Sí — `wf-spec-map-analyze` usa el mapa como verdad |
| Tras `wf-spec-map-analyze` | Responder gaps `[CRÍTICO]_(pendiente)_` en cada `_analysis.md` | Sí — `wf-spec-map-generate` no avanza si hay pendientes |
| Tras `wf-spec-map-analyze` | Responder gaps `[INFORMATIVO]_(pendiente)_` (opcional) | No — se aplican asunciones por defecto |
| Tras cualquier edición manual | Ejecutar `wf-spec-validate` sobre el spec editado | No — pero puede introducir contaminación o romper la estructura |

---

## Estructura de directorios

```
sdd/spec/
├── README.md
├── agents/
│   └── sdd-analyst.md                     ← agente worker
├── shared/
│   └── templates/
│       ├── project_map_template.md        ← template para wf-spec-map
│       ├── feature_analysis_template.md   ← template para wf-spec-map-analyze
│       ├── feature_spec_template.md       ← template para wf-spec-map-generate
│       └── feature_readme_template.md     ← template para wf-spec-map-generate
└── skills/
    ├── wf-spec-map/SKILL.md
    ├── wf-spec-map-analyze/SKILL.md
    ├── wf-spec-map-generate/SKILL.md
    ├── wf-spec-validate/SKILL.md
    ├── wf-spec-conflict/SKILL.md
    ├── kb-spec-expert/SKILL.md
    │   └── references/
    │       ├── prohibited_items.md
    │       └── error_patterns.md
    ├── kb-gap-conventions/SKILL.md
    ├── kb-decompose-expert/SKILL.md
    └── kb-conflict-expert/SKILL.md
```

---

## Cómo extender el sistema

Para añadir un nuevo workflow:

1. **Crea el workflow skill** en `skills/wf-<nombre>/SKILL.md` con `context: fork` y `agent: sdd-analyst`.
2. **Crea el knowledge skill** si el workflow necesita reglas propias reutilizables: `skills/kb-<nombre>/SKILL.md` con `disable-model-invocation: true`.
3. **Actualiza `sdd-analyst.md`**: añade el nuevo knowledge a la tabla de routing.
4. **Añade la entrada al rootmap** en `sdd/CLAUDE.md`.
