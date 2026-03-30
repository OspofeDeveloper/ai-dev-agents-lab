# SDD Spec — Etapas 1 y 2: Specify y Decompose

Este directorio contiene todos los agentes y skills que transforman un documento de requisitos en Specs SDD válidos y autocontenidos por feature. Cubre las dos primeras etapas del pipeline Spec Driven Development: **Specify** (del PRD al Spec monolítico) y **Decompose** (del Spec monolítico a Specs por feature).

---

## Casos de uso

### 1. Proyecto nuevo (Greenfield) — flujo completo

Tienes un PRD o documento de requisitos y quieres convertirlo en Specs SDD.

```
/prepare-spec analyze prd.md
  → genera prd_analysis.md con gaps [CRÍTICO] e [INFORMATIVO]

[edita prd_analysis.md, responde los gaps [CRÍTICO]]

/prepare-spec finalize prd.md
  → genera prd_spec.md (spec monolítico con 8 elementos SDD)

/decompose-spec prd_spec.md
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
/prepare-spec fast-track notifications.md --capability push-notifications
  → genera features/push-notifications/push-notifications_spec.md directamente
```

**Cuándo usarlo**: cuando el documento de entrada ya describe una sola capacidad acotada y no necesitas documentar el sistema completo. El spec resultante puede tener `## Items Pendientes` si hay gaps críticos, y `## Asunciones Aplicadas` si se resolvieron gaps informativos con asunciones razonables.

---

### 3. Evolución incremental de un spec existente (Delta)

El software ya existe, hay un `_spec.md` en producción y quieres añadir o modificar una funcionalidad sin regenerar todo.

```
/prepare-delta analyze features/auth/auth_spec.md --new-reqs new_auth_requirements.md
  → genera features/auth/auth_delta_analysis.md con HUs/CAs añadidos, modificados, eliminados

[revisa el delta, responde gaps [CRÍTICO]]

/prepare-delta apply features/auth/auth_spec.md features/auth/auth_delta_analysis.md
  → actualiza auth_spec.md (versión 1.0 → 1.1) con sección Changelog
```

**Cuándo usarlo**: cuando el spec ya existe y el cambio es incremental (nueva HU, modificación de un comportamiento, eliminación de una funcionalidad deprecada). El delta es quirúrgico: no toca lo que no cambia.

---

### 4. Validar un spec tras edición manual

Editas manualmente un `_spec.md` y quieres verificar que no introdujiste contaminación técnica ni rompiste la estructura SDD.

```
/prepare-spec validate features/auth/auth_spec.md
  → imprime informe APROBADO / REQUIERE_REVISIÓN (no genera archivo)
```

**Cuándo usarlo**: después de cualquier edición manual a un spec. También útil como gate antes de ejecutar `/prepare-plan`.

---

### 5. Detectar conflictos entre specs de features

Quieres verificar que los specs de las diferentes features del proyecto son coherentes entre sí: sin HUs duplicadas, CAs contradictorios ni scope overlap.

```
/check-conflicts features/auth/auth_spec.md --features-dir features/
  → genera features/auth/auth_conflict_report.md si hay conflictos
```

**Cuándo usarlo**: después de modificar un spec existente o añadir una nueva feature con fast-track o delta, para verificar que el cambio no choca con el resto del sistema. También se ejecuta automáticamente al final de `/decompose-spec` (modo no bloqueante).

---

### 6. Consulta directa sobre qué es un Spec SDD

Preguntas conceptuales o revisión de un spec a mano, sin pasar por el flujo orquestado.

```
/spec-expert features/auth/auth_spec.md
/spec-expert ¿qué lleva un spec?
/spec-expert ¿esto es un spec o un plan?
```

**Cuándo usarlo**: para aprender, revisar o depurar specs directamente en conversación, sin invocar el pipeline completo.

---

## Arquitectura de 3 capas

Todos los componentes de este directorio siguen el mismo patrón arquitectónico. Entender las 3 capas es clave para extender el sistema sin romper su coherencia.

```
┌─────────────────────────────────────────────────────────────┐
│  CAPA 1 — Orquestadores (skills invocables por el usuario)  │
│  prepare-spec  │  decompose-spec  │  prepare-delta  │  check-conflicts │
│                                                             │
│  Rol: parsear args → verificar archivos → delegar → escribir│
│  No razonan. No analizan. Solo coordinan.                   │
│  disable-model-invocation: true                             │
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
│  CAPA 3 — Knowledge Bases y Workflows (solo contexto)       │
│                                                             │
│  Knowledge:   spec-expert  │  decompose-expert  │  conflict-expert │
│  Workflows:   spec-analyze │  spec-finalize  │  spec-validate      │
│               spec-decompose │  spec-delta  │  spec-fast-track     │
│               spec-conflict                                 │
│                                                             │
│  Rol: reglas, templates, instrucciones de ejecución         │
│  No se invocan directamente. Solo se cargan como contexto.  │
│  disable-model-invocation: true  │  context: fork (knowledge)│
└─────────────────────────────────────────────────────────────┘
```

### Por qué esta separación

**Capa 1 (Orquestadores)** corren en el contexto principal de la conversación porque necesitan invocar `Agent()`. Al usar `disable-model-invocation: true`, no consumen tokens en razonamiento — son código procedural expresado en lenguaje natural. Si falla la verificación de un archivo, el error llega al usuario sin coste.

**Capa 2 (sdd-analyst)** es el único componente que razona. Al ser un subagente, su contexto está aislado del contexto principal — consume tokens solo cuando es necesario y no contamina la conversación con el usuario con el detalle técnico del análisis. Tiene `memory: project` para que sus decisiones sean coherentes a lo largo de múltiples ejecuciones en el mismo proyecto.

**Capa 3 (Knowledge + Workflows)** son archivos de texto puro que se inyectan en el contexto del agente. Al declararlos en el frontmatter `skills: [...]` del agente, Claude Code los carga automáticamente cuando invoca el agente. Los knowledge bases tienen `context: fork` para que no interfieran con el contexto principal.

---

## Mapa completo de componentes

### Skills invocables (Capa 1)

| Skill | Comando | Modos | Produce |
|-------|---------|-------|---------|
| `prepare-spec` | `/prepare-spec` | `analyze`, `finalize`, `validate`, `fast-track` | `_analysis.md`, `_spec.md`, informe inline, `features/<x>/<x>_spec.md` |
| `decompose-spec` | `/decompose-spec` | — | `_features.md`, `features/<x>/<x>_spec.md`, `features/<x>/README.md` |
| `prepare-delta` | `/prepare-delta` | `analyze`, `apply` | `_delta_analysis.md`, spec actualizado con versión incrementada |
| `check-conflicts` | `/check-conflicts` | — | `_conflict_report.md` |

### Agente worker (Capa 2)

| Agente | Modos soportados | Invocado desde |
|--------|-----------------|----------------|
| `sdd-analyst` | `analyze`, `finalize`, `validate`, `decompose`, `delta`, `fast-track`, `conflict` | `prepare-spec`, `decompose-spec`, `prepare-delta`, `check-conflicts` |

### Knowledge bases (Capa 3)

| Skill | Tipo | Usado en modos |
|-------|------|----------------|
| `spec-expert` | Conocimiento SDD (8 elementos, Prueba de Pureza, Testabilidad) | Todos |
| `decompose-expert` | Partición de features, shared models, ownership | `decompose`, `fast-track` |
| `conflict-expert` | 5 reglas de detección de conflictos entre specs | `conflict` |

### Workflows (Capa 3)

| Skill | Tipo | Modo que implementa |
|-------|------|---------------------|
| `spec-analyze` | Workflow | `analyze` |
| `spec-finalize` | Workflow | `finalize` |
| `spec-validate` | Workflow | `validate` |
| `spec-decompose` | Workflow | `decompose` |
| `spec-delta` | Workflow | `delta` (submodos: `analyze`, `apply`) |
| `spec-fast-track` | Workflow | `fast-track` |
| `spec-conflict` | Workflow | `conflict` |

---

## Routing interno del agente sdd-analyst

Cuando un orquestador invoca `sdd-analyst`, le pasa un prompt estructurado con `Modo: <modo>` como primera línea. El agente lee el modo y carga el workflow y los knowledge bases correspondientes:

```
Modo: analyze    → spec-analyze    + spec-expert
Modo: finalize   → spec-finalize   + spec-expert
Modo: validate   → spec-validate   + spec-expert
Modo: decompose  → spec-decompose  + spec-expert + decompose-expert
Modo: delta      → spec-delta      + spec-expert
Modo: fast-track → spec-fast-track + spec-expert + decompose-expert
Modo: conflict   → spec-conflict   + spec-expert + conflict-expert
```

Los workflows contienen las instrucciones paso a paso de qué hacer. Los knowledge bases son las reglas que el agente consulta durante la ejecución del workflow (la Prueba de Pureza, los criterios de feature válida, las reglas de detección de conflictos).

---

## Artefactos producidos

```
proyecto/
├── prd.md                                    ← Input — no se modifica
├── prd_analysis.md                           ← /prepare-spec analyze
├── prd_spec.md                               ← /prepare-spec finalize
├── prd_features.md                           ← /decompose-spec
├── _conflict_report.md                       ← /decompose-spec (automático) o /check-conflicts
└── features/
    └── <nombre-feature>/
        ├── README.md                         ← /decompose-spec o /prepare-spec fast-track
        ├── <nombre>_spec.md                  ← /decompose-spec o /prepare-spec fast-track
        ├── <nombre>_delta_analysis.md        ← /prepare-delta analyze
        ├── <nombre>_conflict_report.md       ← /check-conflicts
        ├── <nombre>_plan.md                  ← /prepare-plan (etapa siguiente)
        └── <nombre>_tasks.md                 ← /prepare-tasks (etapa siguiente)
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
└── skills/
    ├── prepare-spec/SKILL.md                 ← L1: /prepare-spec
    ├── decompose-spec/SKILL.md               ← L1: /decompose-spec
    ├── prepare-delta/SKILL.md                ← L1: /prepare-delta
    ├── check-conflicts/SKILL.md              ← L1: /check-conflicts
    ├── spec-expert/                          ← L3 knowledge
    │   ├── SKILL.md
    │   └── references/
    │       ├── prohibited_items.md
    │       └── error_patterns.md
    ├── decompose-expert/SKILL.md             ← L3 knowledge
    ├── conflict-expert/SKILL.md              ← L3 knowledge
    ├── spec-analyze/                         ← L3 workflow
    │   ├── SKILL.md
    │   └── references/output_template.md
    ├── spec-finalize/                        ← L3 workflow
    │   ├── SKILL.md
    │   └── references/output_template.md
    ├── spec-validate/                        ← L3 workflow (solo lectura, no produce archivos)
    │   ├── SKILL.md
    │   └── references/output_template.md
    ├── spec-decompose/                       ← L3 workflow
    │   ├── SKILL.md
    │   └── references/
    │       ├── features_template.md
    │       ├── feature_spec_template.md
    │       └── feature_readme_template.md
    ├── spec-delta/                           ← L3 workflow
    │   ├── SKILL.md
    │   └── references/delta_analysis_template.md
    ├── spec-fast-track/SKILL.md              ← L3 workflow
    └── spec-conflict/                        ← L3 workflow
        ├── SKILL.md
        └── references/conflict_report_template.md
```

---

## Cómo extender el sistema

Para añadir un nuevo modo al pipeline:

1. **Crea el workflow L3** en `skills/spec-<nombre>/SKILL.md` con `disable-model-invocation: true`. Aquí van las instrucciones paso a paso de qué debe hacer el agente.
2. **Crea el knowledge base L3** (si el modo necesita reglas propias) en `skills/<nombre>-expert/SKILL.md` con `context: fork`.
3. **Registra el nuevo skill en `sdd-analyst.md`**: añádelo al frontmatter `skills: [...]` y a la tabla de routing.
4. **Crea el orquestador L1** si el usuario necesita invocarlo directamente: `skills/<nombre>/SKILL.md` con `disable-model-invocation: true` y `allowed-tools: [Read, Write, Agent]`. Si el modo es una extensión natural de un orquestador existente (como `fast-track` en `prepare-spec`), modifica ese orquestador en lugar de crear uno nuevo.

**Regla de diseño**: los orquestadores (L1) nunca razonan. Los workflows (L3) nunca escriben archivos. Solo el agente worker (L2) hace ambas cosas — y solo lo hace a través de los workflows que tiene disponibles.
