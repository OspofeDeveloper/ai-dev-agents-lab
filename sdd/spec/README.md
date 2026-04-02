# SDD Spec — Etapas 1 y 2: Specify y Decompose

Este directorio contiene todos los agentes y skills que transforman un documento de requisitos en Specs SDD válidos y autocontenidos por feature. Cubre las dos primeras etapas del pipeline Spec Driven Development: **Specify** (del PRD al Spec monolítico) y **Decompose** (del Spec monolítico a Specs por feature).

---

## Casos de uso

### 1. Proyecto nuevo (Greenfield) — flujo completo

Tienes un PRD o documento de requisitos y quieres convertirlo en Specs SDD.

```
/wf-spec-analyze prd.md
  → genera prd_analysis.md con gaps [CRÍTICO] e [INFORMATIVO]

[edita prd_analysis.md, responde los gaps [CRÍTICO]]

/wf-spec-finalize prd.md
  → genera prd_spec.md (spec monolítico con 8 elementos SDD)

/wf-spec-decompose prd_spec.md
  → genera prd_features.md (índice de features)
  → genera features/<nombre>/<nombre>_spec.md por cada feature
  → genera features/<nombre>/README.md por cada feature
  → ejecuta verificación de conflictos automáticamente
```

**Cuándo usarlo**: cuando tienes un PRD que cubre todo el sistema o un conjunto amplio de funcionalidades.

---

### 2. Feature única sin spec previo (Fast-Track)

Quieres documentar solo una capacidad concreta sin pasar por el spec monolítico. Útil para añadir features a proyectos maduros o arrancar documentando una sola área.

```
/wf-spec-fast-track notifications.md --capability push-notifications
  → genera features/push-notifications/push-notifications_spec.md directamente
```

**Cuándo usarlo**: cuando el documento de entrada ya describe una sola capacidad acotada y no necesitas documentar el sistema completo. El spec resultante puede tener `## Items Pendientes` si hay gaps críticos, y `## Asunciones Aplicadas` si se resolvieron gaps informativos con asunciones razonables.

---

### 3. Evolución incremental de un spec existente (Delta)

El software ya existe, hay un `_spec.md` en producción y quieres añadir o modificar una funcionalidad sin regenerar todo.

```
/wf-spec-delta analyze features/auth/auth_spec.md --new-reqs new_auth_requirements.md
  → genera features/auth/auth_delta_analysis.md con HUs/CAs añadidos, modificados, eliminados

[revisa el delta, responde gaps [CRÍTICO]]

/wf-spec-delta apply features/auth/auth_spec.md features/auth/auth_delta_analysis.md
  → actualiza auth_spec.md (versión 1.0 → 1.1) con sección Changelog
```

**Cuándo usarlo**: cuando el spec ya existe y el cambio es incremental (nueva HU, modificación de un comportamiento, eliminación de una funcionalidad deprecada). El delta es quirúrgico: no toca lo que no cambia.

---

### 4. Validar un spec tras edición manual

Editas manualmente un `_spec.md` y quieres verificar que no introdujiste contaminación técnica ni rompiste la estructura SDD.

```
/wf-spec-validate features/auth/auth_spec.md
  → imprime informe APROBADO / REQUIERE_REVISIÓN (no genera archivo)
```

**Cuándo usarlo**: después de cualquier edición manual a un spec. También útil como gate antes de ejecutar `/wf-prepare-plan`.

---

### 5. Detectar conflictos entre specs de features

Quieres verificar que los specs de las diferentes features del proyecto son coherentes entre sí: sin HUs duplicadas, CAs contradictorios ni scope overlap.

```
/wf-spec-conflict features/auth/auth_spec.md --features-dir features/
  → genera features/auth/auth_conflict_report.md si hay conflictos
```

**Cuándo usarlo**: después de modificar un spec existente o añadir una nueva feature con fast-track o delta, para verificar que el cambio no choca con el resto del sistema. También se ejecuta automáticamente al final de `/wf-spec-decompose` (modo no bloqueante).

---

### 6. Consulta directa sobre qué es un Spec SDD

Preguntas conceptuales o revisión de un spec a mano, sin pasar por el flujo orquestado.

```
/kb-spec-expert features/auth/auth_spec.md
/kb-spec-expert ¿qué lleva un spec?
/kb-spec-expert ¿esto es un spec o un plan?
```

**Cuándo usarlo**: para aprender, revisar o depurar specs directamente en conversación, sin invocar el pipeline completo.

---

## Arquitectura de 3 capas

Todos los componentes de este directorio siguen el mismo patrón arquitectónico. Entender las 3 capas es clave para extender el sistema sin romper su coherencia.

```
┌─────────────────────────────────────────────────────────────┐
│  CAPA 1 — Workflows (wf-) invocables por el usuario         │
│  wf-spec-analyze │ wf-spec-finalize │ wf-spec-validate     │
│  wf-spec-fast-track │ wf-spec-decompose │ wf-spec-conflict │
│  wf-spec-delta                                              │
│                                                             │
│  Rol: parsear args → verificar archivos → ejecutar workflow │
│  → delegar al agente → escribir resultado                   │
└────────────────────────────┬────────────────────────────────┘
                             │ invoca Agent()
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA 2 — Agente Worker                                     │
│                    sdd-analyst                              │
│                                                             │
│  Rol: análisis real, generación de contenido, decisiones    │
│  Router por modo: analyze, finalize, validate, decompose,   │
│                   delta, fast-track, conflict               │
│  memory: project  │  permissionMode: acceptEdits            │
└────────────────────────────┬────────────────────────────────┘
                             │ carga como contexto
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA 3 — Knowledge Bases (kb-) — solo contexto             │
│                                                             │
│  kb-spec-expert │ kb-decompose-expert │ kb-conflict-expert  │
│  kb-gap-conventions                                         │
│                                                             │
│  Rol: reglas, templates, criterios de validación            │
│  No se invocan directamente. Solo se cargan como contexto.  │
│  disable-model-invocation: true  │  context: fork           │
└─────────────────────────────────────────────────────────────┘
```

### Por qué esta separación

**Capa 1 (Workflows `wf-`)** son los puntos de entrada del usuario. Cada workflow contiene las instrucciones paso a paso de ejecución, parsea argumentos, verifica precondiciones, delega al agente `sdd-analyst` y escribe el resultado.

**Capa 2 (sdd-analyst)** es el único componente que razona. Al ser un subagente, su contexto está aislado del contexto principal — consume tokens solo cuando es necesario y no contamina la conversación con el usuario con el detalle técnico del análisis. Tiene `memory: project` para que sus decisiones sean coherentes a lo largo de múltiples ejecuciones en el mismo proyecto.

**Capa 3 (Knowledge `kb-`)** son archivos de texto puro que se inyectan en el contexto del agente. Al declararlos en el frontmatter `skills: [...]` del agente, Claude Code los carga automáticamente cuando invoca el agente. Tienen `context: fork` para que no interfieran con el contexto principal.

---

## Mapa completo de componentes

### Skills workflow (Capa 1) — invocables por el usuario

| Skill | Comando | Produce |
|-------|---------|---------|
| `wf-spec-analyze` | `/wf-spec-analyze` | `_analysis.md` |
| `wf-spec-finalize` | `/wf-spec-finalize` | `_spec.md` |
| `wf-spec-validate` | `/wf-spec-validate` | Informe inline (sin archivo) |
| `wf-spec-fast-track` | `/wf-spec-fast-track` | `features/<x>/<x>_spec.md` directamente |
| `wf-spec-decompose` | `/wf-spec-decompose` | `_features.md`, `features/<x>/<x>_spec.md`, `features/<x>/README.md` |
| `wf-spec-conflict` | `/wf-spec-conflict` | `_conflict_report.md` |
| `wf-spec-delta` | `/wf-spec-delta` | `_delta_analysis.md` (analyze) o spec actualizado (apply) |

### Agente worker (Capa 2)

| Agente | Modos soportados | Invocado desde |
|--------|-----------------|----------------|
| `sdd-analyst` | `analyze`, `finalize`, `validate`, `decompose`, `delta`, `fast-track`, `conflict` | Todos los `wf-spec-*` |

### Knowledge bases (Capa 3)

| Skill | Tipo | Usado en modos |
|-------|------|----------------|
| `kb-spec-expert` | Conocimiento SDD (8 elementos, Prueba de Pureza, Testabilidad) | Todos |
| `kb-decompose-expert` | Partición de features, shared models, ownership | `decompose`, `fast-track` |
| `kb-conflict-expert` | 5 reglas de detección de conflictos entre specs | `conflict` |
| `kb-gap-conventions` | SSoT de convenciones de gaps | Todos los modos que generen o verifiquen gaps |

---

## Routing interno del agente sdd-analyst

Cuando un workflow invoca `sdd-analyst`, le pasa un prompt estructurado con `Modo: <modo>` como primera línea. El agente lee el modo y usa los knowledge bases correspondientes:

```
Modo: analyze    → kb-spec-expert + kb-gap-conventions
Modo: finalize   → kb-spec-expert + kb-gap-conventions
Modo: validate   → kb-spec-expert
Modo: decompose  → kb-spec-expert + kb-decompose-expert
Modo: delta      → kb-spec-expert + kb-gap-conventions
Modo: fast-track → kb-spec-expert + kb-decompose-expert + kb-gap-conventions
Modo: conflict   → kb-spec-expert + kb-conflict-expert
```

Los knowledge bases son las reglas que el agente consulta durante la ejecución (la Prueba de Pureza, los criterios de feature válida, las reglas de detección de conflictos).

---

## Artefactos producidos

```
proyecto/
├── prd.md                                    ← Input — no se modifica
├── prd_analysis.md                           ← /wf-spec-analyze
├── prd_spec.md                               ← /wf-spec-finalize
├── prd_features.md                           ← /wf-spec-decompose
├── _conflict_report.md                       ← /wf-spec-decompose (automático) o /wf-spec-conflict
└── features/
    └── <nombre-feature>/
        ├── README.md                         ← /wf-spec-decompose o /wf-spec-fast-track
        ├── <nombre>_spec.md                  ← /wf-spec-decompose o /wf-spec-fast-track
        ├── <nombre>_delta_analysis.md        ← /wf-spec-delta analyze
        ├── <nombre>_conflict_report.md       ← /wf-spec-conflict
        ├── <nombre>_plan.md                  ← /wf-prepare-plan (etapa siguiente)
        └── <nombre>_tasks.md                 ← /wf-prepare-tasks (etapa siguiente)
```

---

## Checkpoints humanos

El pipeline nunca es completamente automático. Estos son los momentos donde el humano debe intervenir:

| Momento | Qué hacer | Bloquea si no se hace |
|---------|-----------|-----------------------|
| Tras `analyze` | Responder gaps `[CRÍTICO]_(pendiente)_` en `_analysis.md` | Sí — `finalize` no avanza |
| Tras `analyze` | Responder gaps `[INFORMATIVO]_(pendiente)_` (opcional) | No — se aplican asunciones por defecto |
| Tras `delta analyze` | Responder gaps `[CRÍTICO]_(pendiente)_` en `_delta_analysis.md` | Sí — `delta apply` no avanza |
| Tras `decompose` | Revisar `_features.md` y validar la partición de features | No — pero afecta la calidad del plan |
| Tras `decompose` | Revisar `_conflict_report.md` si hay conflictos `ALTA` | No — pero pueden propagarse problemas al plan |

---

## Estructura de directorios

```
sdd/spec/
├── README.md                                  ← este archivo
├── agents/
│   └── sdd-analyst.md                        ← L2 worker (router por modo)
├── shared/
│   └── templates/                            ← Source of truth para templates compartidos
│       ├── feature_spec_template.md
│       └── feature_readme_template.md
└── skills/
    ├── kb-spec-expert/                       ← Knowledge: 8 elementos SDD, Pureza, Testabilidad
    │   ├── SKILL.md
    │   └── references/
    │       ├── prohibited_items.md
    │       └── error_patterns.md
    ├── kb-decompose-expert/                  ← Knowledge: reglas de partición y shared models
    │   └── SKILL.md
    ├── kb-conflict-expert/                   ← Knowledge: 5 reglas de detección de conflictos
    │   └── SKILL.md
    ├── kb-gap-conventions/                   ← Knowledge: SSoT de IDs, severidades y pendientes
    │   └── SKILL.md
    ├── wf-spec-analyze/                      ← Workflow: PRD → _analysis.md
    │   ├── SKILL.md
    │   └── output_template.md
    ├── wf-spec-finalize/                     ← Workflow: PRD + analysis → _spec.md
    │   ├── SKILL.md
    │   └── references/output_template.md
    ├── wf-spec-validate/                     ← Workflow: _spec.md → informe inline
    │   ├── SKILL.md
    │   └── references/output_template.md
    ├── wf-spec-fast-track/                   ← Workflow: PRD → feature spec directo
    │   ├── SKILL.md
    │   └── references/
    │       ├── feature_spec_template.md
    │       └── feature_readme_template.md
    ├── wf-spec-decompose/                    ← Workflow: _spec.md → features/*/_spec.md
    │   ├── SKILL.md
    │   └── references/
    │       ├── features_template.md
    │       ├── feature_spec_template.md
    │       └── feature_readme_template.md
    ├── wf-spec-conflict/                     ← Workflow: detectar conflictos entre specs
    │   ├── SKILL.md
    │   └── references/conflict_report_template.md
    └── wf-spec-delta/                        ← Workflow: evolución incremental de spec
        ├── SKILL.md
        └── references/delta_analysis_template.md
```

---

## Cómo extender el sistema

Para añadir un nuevo modo al pipeline:

1. **Crea el workflow** en `skills/wf-spec-<nombre>/SKILL.md` con `agent: sdd-analyst`. Aquí van las instrucciones paso a paso de qué debe hacer el agente.
2. **Crea el knowledge base** (si el modo necesita reglas propias transversales a varios workflows) en `skills/kb-<nombre>-expert/SKILL.md` con `context: fork` y `disable-model-invocation: true`.
3. **Registra el nuevo knowledge en `sdd-analyst.md`**: añádelo al frontmatter `skills: [...]` y a la tabla de routing.
4. **Registra en CLAUDE.md**: añade la entrada en el rootmap de workflow skills.

**Regla de diseño**: los workflows (`wf-`) son el punto de entrada del usuario y contienen las instrucciones de ejecución. Los knowledge (`kb-`) nunca se invocan directamente — solo se cargan como contexto del agente. Solo el agente worker (L2) razona y genera contenido.
