# ai-dev-agents-lab

Repositorio de skills, agentes y conocimiento para automatizar el flujo **Spec-Driven Development (SDD)** sobre proyectos **Kotlin Multiplatform Mobile (KMM)** con Clean Architecture.

---

## Qué es esto

Un ecosistema de agentes Claude Code que cubre el pipeline completo desde un PRD informal hasta tareas de implementación accionables por feature, organizadas por capa KMM y listas para ser ejecutadas con skills especializadas.

```
PRD / Notas       Spec limpio       Specs por        Plan técnico      Tasks
informales  ──►   monolítico  ──►   feature    ──►   por feature ──►  por feature
                  (_spec.md)       (features/         (_plan.md)       (_tasks.md)
                                    <x>_spec.md)
                                                                            │
                                                                   /kmm-domain
                                                                   /kmm-data
                                                                   /kmm-presentation
                                                                   /kmm-tests
                                                                   ...
```

---

## El pipeline SDD en cuatro etapas

### Etapa 1 — Specify

Transforma un documento de requisitos informal en un Spec funcional puro: sin tecnología, sin implementación, solo "qué" y "por qué".

**Prueba de Pureza:**
> "¿Cambiaría esta frase si pasáramos de KMM a web, o de Kotlin a Python?"
> - **SÍ** → es un detalle técnico → pertenece al Plan
> - **NO** → es funcional → puede estar en el Spec

Un Spec válido contiene exactamente 8 elementos obligatorios:
0. Actores
1. Historias de Usuario
2. Recorridos de Usuario (User Journeys)
3. Resultados y Éxito
4. Instrucciones Inambiguas
5. Criterios de Aceptación (GIVEN/WHEN/THEN)
6. Checklist de Validación
7. Fuera de Alcance

El resultado es un **spec monolítico limpio** (`_spec.md`) que cubre todo el proyecto.

### Etapa 2 — Decompose

Parte el spec monolítico limpio en **un spec por feature**. Cada feature es una unidad funcional cohesiva con Journeys, CAs e Historias de Usuario propias.

Esta etapa también identifica los **shared models**: modelos de domain que son usados por más de una feature. Cada shared model tiene una feature *owner* que lo define; las demás features solo lo referencian.

El resultado es:
- `_features.md` — índice de features con scope, shared models y rutas
- `features/<nombre>/<nombre>_spec.md` — un Spec SDD completo y autocontenido por feature

### Etapa 3 — Plan

Transforma cada spec de feature en un plan técnico KMM. Aquí entra la tecnología: stack, módulos, capas, contratos de API, decisiones de expect/actual.

Un Plan válido debe tener:
- Stack tech explícito (KMM, Compose, Ktor, etc.)
- Mapa de módulos (`:feature:X`, `:core:Y`)
- Diseño capa por capa: domain → data → presentation
- Contratos de API y DTOs
- Dependencias entre componentes
- Decisiones de expect/actual (Android/iOS)

Un Plan **no debe tener**: código implementado, requisitos funcionales del usuario, estimaciones de tiempo.

Los shared models declarados en `_features.md` no se redefinen: la feature owner los define completos; el resto los referencia.

### Etapa 4 — Tasks

Transforma el Plan de cada feature en tareas independientes y accionables, ordenadas por dependencias, cada una asignada a una skill KMM. Una task = un chunk implementable, una capa, un componente.

Ejemplo de task:
```
## T-001: Domain Layer — LoginUseCase
- Spec CA: CA-003
- Plan ref: §3.2 Domain Module
- Layer: domain | Module: :feature:auth
- Skill: /kmm-domain
- Dependencies: ninguna
- Definition of done: UseCase + Repository interface + Model creados
```

---

## Arquitectura del ecosistema: 4 etapas × 3 capas

Cada etapa sigue el mismo patrón arquitectónico de 3 capas:

```
              LAYER 3              LAYER 2              LAYER 1
           (Conocimiento)       (Agente Worker)      (Workflow)

ETAPA 1    kb-spec-expert ──►   sdd-analyst   ──◄──  wf-spec-analyze
SPECIFY    Reglas SDD            Analiza/             wf-spec-discover
           kb-decompose-        Genera Specs          wf-spec-features-first
           expert               por feature           wf-spec-fast-track
           Reglas de                                  wf-spec-validate
           partición                                  wf-spec-conflict
                                                      wf-spec-delta

ETAPA 3    kb-plan-expert ──►   plan-architect ──◄── wf-prepare-plan
PLAN       Reglas Plan           Spec → Plan          /wf-prepare-plan
           + KMM arch            técnico               <spec.md>

ETAPA 4    kb-tasks-expert ──►  task-generator ──◄── wf-prepare-tasks
TASKS      Reglas Tasks          Plan → Tasks         /wf-prepare-tasks
           + sizing KMM          ordenados             <plan.md>
```

**Capa 1 — Skill Workflow (`wf-`)**: punto de entrada para el usuario. Parsea argumentos, verifica archivos, delega al agente. Contiene las instrucciones del workflow que el agente ejecuta.

**Capa 2 — Agente Worker**: subagente con su propio contexto. Tiene `memory: project` para acumular aprendizaje del proyecto. Tiene `permissionMode: acceptEdits` para escribir artefactos sin interrupciones. Usa los knowledge bases de Capa 3 inyectados vía `skills: [...]`.

**Capa 3 — Skill de Knowledge (`kb-`)**: solo conocimiento y reglas. No realiza acciones, define estándares. Se inyecta en el agente para que cada decisión esté basada en criterios explícitos.

> **Nota**: `sdd-analyst` es el worker compartido de las etapas 1 y 2. Opera en siete modos distintos (`analyze`, `finalize`, `validate`, `decompose`, `fast-track`, `delta`, `conflict`) según lo que le pase el workflow.

---

## Estructura de archivos

```
~/.claude/
├── agents/
│   ├── sdd-analyst.md          ✅ Worker: Specify + Decompose
│   ├── plan-architect.md       ✅ Worker: Plan (model: opus)
│   └── task-generator.md       ✅ Worker: Tasks
│
└── skills/
    ├── kb-spec-expert/          ✅ Knowledge: Spec rules
    │   ├── SKILL.md
    │   └── references/
    │       ├── prohibited_items.md
    │       └── error_patterns.md
    │
    ├── kb-decompose-expert/     ✅ Knowledge: Feature partition rules
    │   └── SKILL.md
    │
    ├── kb-conflict-expert/      ✅ Knowledge: Conflict detection rules
    │   └── SKILL.md
    │
    ├── kb-gap-conventions/      ✅ Knowledge: Gap format conventions
    │   └── SKILL.md
    │
    ├── kb-plan-expert/          ✅ Knowledge: Plan rules
    │   ├── SKILL.md
    │   └── references/
    │       ├── kmm_architecture.md
    │       └── plan_structure.md
    │
    ├── kb-tasks-expert/         ✅ Knowledge: Tasks rules
    │   ├── SKILL.md
    │   └── references/
    │       ├── task_sizing.md
    │       └── kmm_task_templates.md
    │
    ├── wf-spec-analyze/         ✅ Workflow: Analyze requirements
    │   ├── SKILL.md
    │   └── output_template.md
    │
    ├── wf-spec-validate/        ✅ Workflow: Audit existing spec
    │   ├── SKILL.md
    │   └── references/output_template.md
    │
    ├── wf-spec-fast-track/      ✅ Workflow: Direct feature spec
    │   ├── SKILL.md
    │   └── references/
    │       ├── feature_spec_template.md
    │       └── feature_readme_template.md
    │
    ├── wf-spec-conflict/        ✅ Workflow: Detect conflicts between specs
    │   ├── SKILL.md
    │   └── references/conflict_report_template.md
    │
    ├── wf-spec-delta/           ✅ Workflow: Evolve spec with new requirements
    │   ├── SKILL.md
    │   └── references/delta_analysis_template.md
    │
    ├── wf-prepare-plan/         ✅ Workflow: Spec → Plan
    │   └── SKILL.md
    │
    └── wf-prepare-tasks/        ✅ Workflow: Plan → Tasks
        └── SKILL.md
```

---

## Estructura de artefactos en tu proyecto

```
project-root/
├── prd.md                           # PRD original
├── prd_analysis.md                  # /wf-spec-analyze (recomendado)
├── prd_discovery.md                 # /wf-spec-discover — mapa de features
├── prd_features.md                  # /wf-spec-features-first — índice de features y shared models
│
└── features/
    ├── authentication/
    │   ├── authentication_spec.md   # /wf-spec-fast-track
    │   ├── authentication_plan.md   # /wf-prepare-plan
    │   └── authentication_tasks.md  # /wf-prepare-tasks
    ├── services/
    │   ├── services_spec.md
    │   ├── services_plan.md
    │   └── services_tasks.md
    └── <una carpeta por feature>/
```

---

## Workflow completo

```bash
# ── Etapa 1: Specify ──────────────────────────────────────────────────────────
/wf-spec-analyze prd.md
# → prd_analysis.md (gaps, contaminaciones técnicas, preguntas para el cliente)

# [HUMANO] Editar prd_analysis.md: responder cada item _(pendiente)_

/wf-spec-features-first prd.md
# → prd_discovery.md (mapa de features + scope RF→Feature)
# → prd_features.md (índice de features + tabla de shared models)
# → features/<nombre>/<nombre>_spec.md (un spec por feature, en paralelo)

# [HUMANO] Revisar prd_features.md: ajustar scope de features si es necesario
#          Confirmar qué feature es owner de cada shared model


# ── Etapas 3 y 4: Por cada feature ───────────────────────────────────────────
# Empezar por las features owner de shared models

/wf-prepare-plan generate features/authentication/authentication_spec.md
# → features/authentication/authentication_plan.md

/wf-prepare-tasks generate features/authentication/authentication_plan.md
# → features/authentication/authentication_tasks.md

# Repetir para el resto de features (pueden procesarse en paralelo)
/wf-prepare-plan generate features/services/services_spec.md
/wf-prepare-tasks generate features/services/services_plan.md
# ...


# ── Implementación con KMM skills ─────────────────────────────────────────────
# Por cada feature, ejecutar las tasks en orden:
/kmm-scaffold  (T-000)
/kmm-domain    (T-001, T-002, ...)
/kmm-data      (T-003, T-004, ...)
/kmm-presentation (T-005, ...)
/kmm-tests     (T-006, ...)
```

---

## Gestión de shared models

Los shared models evitan que el mismo concepto (ej. `User`) sea definido de forma distinta en cada feature.

**Cómo funcionan:**
1. `/wf-spec-discover` detecta qué modelos aparecen en más de una feature y los lista en `_features.md` con su feature owner
2. `/wf-prepare-plan` lee la tabla de shared models e inyecta la información al `plan-architect`
3. El `plan-architect` define el modelo completo solo en el Plan de la feature owner; en los demás planes solo lo referencia

**Ejemplo en `prd_features.md`:**
```markdown
## Tabla de shared models

| Modelo | Feature Owner       | Features que lo referencian      |
|--------|---------------------|----------------------------------|
| User   | F-001: authentication | services, time-tracking, profile |
| Zone   | F-005: availability   | services                         |
```

**Orden de implementación recomendado:** primero las features owner de shared models, para que el `Plan ref` esté disponible cuando lo necesiten las features que los referencian.

---

## Puente SDD → KMM

El ecosistema SDD alimenta directamente las skills KMM de implementación:

```
SDD ECOSYSTEM                              KMM ECOSYSTEM
─────────────                              ─────────────

/wf-spec-analyze + /wf-spec-features-first → features/<x>_spec.md
/wf-prepare-plan   → features/<x>_plan.md
/wf-prepare-tasks  → features/<x>_tasks.md ──► /kmm-scaffold
                                             /kmm-domain
                                             /kmm-data
                                             /kmm-presentation
                                             /kmm-expect-actual
                                             /kmm-tests
                                             /kmm-audit
```

El `task-generator` conoce los nombres de las skills KMM y asigna cada task a la skill correcta. Después de `/wf-prepare-tasks`, el trabajo es ejecutar tasks en orden.

---

## Propiedades de escalabilidad

**Evolución independiente**: cada knowledge base (Capa 3) evoluciona sola. Actualizar `kmm_architecture.md` en `kb-plan-expert` no afecta a `kb-spec-expert`, `kb-decompose-expert` ni `kb-tasks-expert`.

**Modelo por complejidad**:
- `plan-architect` → `claude-opus-4-6` (decisiones arquitectónicas complejas)
- `task-generator` → `claude-sonnet-4-6` (formateo estructurado)
- `sdd-analyst` → modelo por defecto (análisis funcional)

**Memoria acumulativa**: cada agente worker tiene `memory: project`. Con el tiempo, el `plan-architect` recuerda decisiones de features anteriores y mantiene consistencia arquitectónica entre ellas.

**Checkpoints humanos**: el pipeline nunca es fully-automatic. El humano valida artefactos estructurados en tres puntos clave:
1. Tras `wf-spec-analyze` → responder preguntas abiertas
2. Tras `wf-spec-features-first` → validar partición y ownership de shared models
3. Tras cada `wf-prepare-plan` → revisar arquitectura antes de generar tasks

**Trazabilidad completa**: cada task apunta a un CA del spec de feature. Cada CA del spec de feature es rastreable al spec monolítico origen.

---

## Instalación

Este repositorio es la fuente de verdad. El script `install.sh` copia todo a `~/.claude/` donde Claude Code lo carga automáticamente.

```bash
# Clonar el repo
git clone <repo-url>
cd ai-dev-agents-lab

# Instalar en ~/.claude/
chmod +x install.sh
./install.sh

# Reiniciar Claude Code para cargar los nuevos skills y agentes
```

Para actualizar tras un `git pull`:
```bash
git pull && ./install.sh
```

---

## Estado de implementación

| Componente | Tipo | Etapa | Estado |
|---|---|---|---|
| `kb-spec-expert` | Knowledge (kb) | Specify | ✅ Implementado |
| `kb-decompose-expert` | Knowledge (kb) | Decompose | ✅ Implementado |
| `kb-conflict-expert` | Knowledge (kb) | Conflict | ✅ Implementado |
| `kb-gap-conventions` | Knowledge (kb) | Transversal | ✅ Implementado |
| `kb-plan-expert` | Knowledge (kb) | Plan | ✅ Implementado |
| `kb-tasks-expert` | Knowledge (kb) | Tasks | ✅ Implementado |
| `sdd-analyst` | Agente Worker | Specify | ✅ Implementado |
| `plan-architect` | Agente Worker | Plan | ✅ Implementado |
| `task-generator` | Agente Worker | Tasks | ✅ Implementado |
| `wf-spec-analyze` | Workflow (wf) | Specify | ✅ Implementado |
| `wf-spec-validate` | Workflow (wf) | Specify | ✅ Implementado |
| `wf-spec-discover` | Workflow (wf) | Specify | ✅ Implementado |
| `wf-spec-features-first` | Workflow (wf) | Specify | ✅ Implementado |
| `wf-spec-fast-track` | Workflow (wf) | Specify | ✅ Implementado |
| `wf-spec-conflict` | Workflow (wf) | Conflict | ✅ Implementado |
| `wf-spec-delta` | Workflow (wf) | Delta | ✅ Implementado |
| `wf-prepare-plan` | Workflow (wf) | Plan | ✅ Implementado |
| `wf-prepare-tasks` | Workflow (wf) | Tasks | ✅ Implementado |
