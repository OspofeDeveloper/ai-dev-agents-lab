# ai-dev-agents-lab

Repositorio de skills, agentes y conocimiento para automatizar el flujo **Spec-Driven Development (SDD)** sobre proyectos **Kotlin Multiplatform Mobile (KMM)** con Clean Architecture.

---

## Qué es esto

Un ecosistema de agentes Claude Code que cubre el pipeline completo desde un PRD informal hasta tareas de implementación accionables por feature, organizadas por capa KMM y listas para ser ejecutadas con skills especializadas.

```
PRD / Notas       Mapa funcional    Análisis de       Specs por        Plan técnico      Tasks
informales  ──►   del proyecto ──►  gaps por    ──►   feature    ──►   por feature ──►  por feature
                  (_project_map.md) feature           (features/         (_plan.md)       (_tasks.md)
                                    (_analysis.md)     <x>_spec.md)
                                                                                              │
                                                                                     /kmm-domain
                                                                                     /kmm-data
                                                                                     /kmm-presentation
                                                                                     /kmm-tests
                                                                                     ...
```

---

## El pipeline SDD en cuatro etapas

### Etapa 1 — Specify (map-flow)

Transforma un documento de requisitos informal en specs funcionales puros por feature: sin tecnología, sin implementación, solo "qué" y "por qué".

El flujo tiene tres pasos con dos checkpoints humanos:

1. `/wf-spec-map` genera un mapa funcional del proyecto desde el PRD
2. **[HUMANO]** valida el mapa: scope, features, shared models
3. `/wf-spec-map-analyze` analiza cada feature del mapa y produce un análisis de gaps
4. **[HUMANO]** responde los gaps de cada feature
5. `/wf-spec-map-generate` genera un spec completo por feature

**Prueba de Pureza del Spec:**
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

### Etapa 2 — Plan

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

### Etapa 3 — Tasks

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

## Arquitectura del ecosistema: 3 etapas × 3 capas

Cada etapa sigue el mismo patrón arquitectónico de 3 capas:

```
              LAYER 3              LAYER 2              LAYER 1
           (Conocimiento)       (Agente Worker)      (Orquestador)

ETAPA 1    kb-spec-expert   ──►    sdd-analyst   ──◄──  wf-spec-map
SPECIFY    kb-gap-conventions      Genera mapa,         wf-spec-map-analyze
           kb-decompose-expert     analiza gaps,        wf-spec-map-generate
           kb-conflict-expert      genera specs          /wf-spec-validate
                                                         /wf-spec-conflict

ETAPA 2    plan-expert   ──►    plan-architect ──◄── prepare-plan
PLAN       Reglas Plan           Spec → Plan          /prepare-plan
           + KMM arch            técnico               generate <spec.md>

ETAPA 3    tasks-expert  ──►    task-generator ──◄── prepare-tasks
TASKS      Reglas Tasks          Plan → Tasks         /prepare-tasks
           + sizing KMM          ordenados             generate <plan.md>
```

**Capa 1 — Skill Orquestador**: punto de entrada para el usuario. Parsea argumentos, verifica archivos, delega al agente. No tiene `context: fork` — corre en el contexto principal para poder invocar agentes.

**Capa 2 — Agente Worker**: subagente con su propio contexto. Tiene `memory: project` para acumular aprendizaje del proyecto. Tiene `permissionMode: acceptEdits` para escribir artefactos sin interrupciones. Usa los knowledge bases de Capa 3 inyectados vía `skills: [...]`.

**Capa 3 — Skill de Referencia**: solo conocimiento y reglas. No realiza acciones, define estándares. Se inyecta en el agente para que cada decisión esté basada en criterios explícitos.

> **Nota**: `sdd-analyst` es el worker compartido de la etapa Specify. Opera en distintos modos (`map`, `analyze`, `generate`, `validate`, `conflict`) según lo que le pase el orquestador.

---

## Estructura de archivos

```
~/.claude/
├── agents/
│   ├── sdd-analyst.md          ✅ Worker: Specify (map, analyze, generate, validate, conflict)
│   ├── plan-architect.md       ✅ Worker: Plan (model: opus)
│   └── task-generator.md       ✅ Worker: Tasks
│
└── skills/
    ├── kb-spec-expert/             ✅ Layer 3: Spec rules
    │   ├── SKILL.md
    │   └── references/
    │       ├── prohibited_items.md
    │       └── error_patterns.md
    │
    ├── kb-gap-conventions/         ✅ Layer 3: Gap analysis conventions
    │   └── SKILL.md
    │
    ├── kb-decompose-expert/        ✅ Layer 3: Feature partition rules
    │   └── SKILL.md
    │
    ├── kb-conflict-expert/         ✅ Layer 3: Conflict detection rules
    │   └── SKILL.md
    │
    ├── wf-spec-map/                ✅ Layer 1: Map orchestrator
    │   └── SKILL.md
    │
    ├── wf-spec-map-analyze/        ✅ Layer 1: Gap analysis orchestrator
    │   └── SKILL.md
    │
    ├── wf-spec-map-generate/       ✅ Layer 1: Spec generation orchestrator
    │   └── SKILL.md
    │
    ├── wf-spec-validate/           ✅ Layer 1: Spec validation orchestrator
    │   └── SKILL.md
    │
    ├── wf-spec-conflict/           ✅ Layer 1: Conflict detection orchestrator
    │   └── SKILL.md
    │
    ├── plan-expert/                ✅ Layer 3: Plan rules
    │   ├── SKILL.md
    │   └── references/
    │       ├── kmm_architecture.md
    │       └── plan_structure.md
    │
    ├── prepare-plan/               ✅ Layer 1: Plan orchestrator
    │   └── SKILL.md
    │
    ├── tasks-expert/               ✅ Layer 3: Tasks rules
    │   └── SKILL.md
    │
    └── prepare-tasks/              ✅ Layer 1: Tasks orchestrator
        └── SKILL.md
```

---

## Estructura de artefactos en tu proyecto

```
project-root/
├── prd.md                              # PRD original (no se modifica)
├── prd_project_map.md                  # /wf-spec-map — mapa funcional del proyecto
├── prd_features.md                     # /wf-spec-map-generate — índice de features y shared models
│
└── features/
    ├── authentication/
    │   ├── _analysis.md                # /wf-spec-map-analyze — gaps de la feature
    │   ├── authentication_spec.md      # /wf-spec-map-generate
    │   ├── authentication_plan.md      # /prepare-plan
    │   └── authentication_tasks.md     # /prepare-tasks
    ├── services/
    │   ├── _analysis.md
    │   ├── services_spec.md
    │   ├── services_plan.md
    │   └── services_tasks.md
    └── <una carpeta por feature>/
```

---

## Workflow completo

```bash
# ── Etapa 1: Specify (map-flow) ───────────────────────────────────────────────

/wf-spec-map prd.md
# → prd_project_map.md (mapa funcional: features, scope, shared models)

# [HUMANO] Revisar prd_project_map.md: validar features, ajustar scope si es necesario

/wf-spec-map-analyze prd_project_map.md
# → features/<nombre>/_analysis.md (gaps, preguntas, ambigüedades por feature)

# [HUMANO] Editar cada _analysis.md: responder los gaps de cada feature

/wf-spec-map-generate prd_project_map.md
# → prd_features.md (índice de features + tabla de shared models)
# → features/<nombre>/<nombre>_spec.md (un spec SDD completo por feature)


# ── Etapas 2 y 3: Por cada feature ───────────────────────────────────────────
# Empezar por las features owner de shared models

/prepare-plan generate features/authentication/authentication_spec.md
# → features/authentication/authentication_plan.md

/prepare-tasks generate features/authentication/authentication_plan.md
# → features/authentication/authentication_tasks.md

# Repetir para el resto de features (pueden procesarse en paralelo)
/prepare-plan generate features/services/services_spec.md
/prepare-tasks generate features/services/services_plan.md
# ...


# ── Validación y conflictos (opcional, en cualquier momento) ──────────────────
/wf-spec-validate features/authentication/authentication_spec.md
# → auditoría del spec: elementos faltantes, contaminación técnica

/wf-spec-conflict features/authentication/authentication_spec.md --features-dir features/
# → detección de conflictos entre specs de features


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
1. `/wf-spec-map` detecta qué modelos aparecen en más de una feature y los incluye en el mapa con su feature owner
2. `/wf-spec-map-generate` genera `prd_features.md` con la tabla de shared models y produce specs que solo referencian los modelos de otras features sin redefinirlos
3. `/prepare-plan` lee la tabla de shared models e inyecta la información al `plan-architect`
4. El `plan-architect` define el modelo completo solo en el Plan de la feature owner; en los demás planes solo lo referencia

**Ejemplo en `prd_features.md`:**
```markdown
## Tabla de shared models

| Modelo | Feature Owner         | Features que lo referencian      |
|--------|-----------------------|----------------------------------|
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

/wf-spec-map         →  prd_project_map.md
/wf-spec-map-analyze →  features/<x>/_analysis.md
/wf-spec-map-generate → features/<x>/<x>_spec.md
/prepare-plan        →  features/<x>/<x>_plan.md
/prepare-tasks       →  features/<x>/<x>_tasks.md ──► /kmm-scaffold
                                                       /kmm-domain
                                                       /kmm-data
                                                       /kmm-presentation
                                                       /kmm-expect-actual
                                                       /kmm-tests
                                                       /kmm-audit
```

El `task-generator` conoce los nombres de las skills KMM y asigna cada task a la skill correcta. Después de `/prepare-tasks`, el trabajo es ejecutar tasks en orden.

---

## Propiedades de escalabilidad

**Evolución independiente**: cada knowledge base (Capa 3) evoluciona sola. Actualizar `kmm_architecture.md` en `plan-expert` no afecta a `kb-spec-expert`, `kb-decompose-expert` ni `tasks-expert`.

**Modelo por complejidad**:
- `plan-architect` → `claude-opus-4-6` (decisiones arquitectónicas complejas)
- `task-generator` → `claude-sonnet-4-6` (formateo estructurado)
- `sdd-analyst` → modelo por defecto (análisis funcional)

**Memoria acumulativa**: cada agente worker tiene `memory: project`. Con el tiempo, el `plan-architect` recuerda decisiones de features anteriores y mantiene consistencia arquitectónica entre ellas.

**Checkpoints humanos**: el pipeline nunca es fully-automatic. El humano valida artefactos estructurados en tres puntos clave:
1. Tras `/wf-spec-map` → validar mapa funcional y scope de features
2. Tras `/wf-spec-map-analyze` → responder gaps de cada feature
3. Tras cada `/prepare-plan` → revisar arquitectura antes de generar tasks

**Trazabilidad completa**: cada task apunta a un CA del spec de feature. Cada CA del spec de feature es rastreable al análisis de gaps y al mapa funcional origen.

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
| `kb-spec-expert` | Skill Layer 3 | Specify | ✅ Implementado |
| `kb-gap-conventions` | Skill Layer 3 | Specify | ✅ Implementado |
| `kb-decompose-expert` | Skill Layer 3 | Specify | ✅ Implementado |
| `kb-conflict-expert` | Skill Layer 3 | Specify | ✅ Implementado |
| `sdd-analyst` | Agente Layer 2 | Specify | ✅ Implementado |
| `wf-spec-map` | Skill Layer 1 | Specify | ✅ Implementado |
| `wf-spec-map-analyze` | Skill Layer 1 | Specify | ✅ Implementado |
| `wf-spec-map-generate` | Skill Layer 1 | Specify | ✅ Implementado |
| `wf-spec-validate` | Skill Layer 1 | Specify | ✅ Implementado |
| `wf-spec-conflict` | Skill Layer 1 | Specify | ✅ Implementado |
| `plan-expert` | Skill Layer 3 | Plan | ✅ Implementado |
| `plan-architect` | Agente Layer 2 | Plan | ✅ Implementado |
| `prepare-plan` | Skill Layer 1 | Plan | ✅ Implementado |
| `tasks-expert` | Skill Layer 3 | Tasks | ✅ Implementado |
| `task-generator` | Agente Layer 2 | Tasks | ✅ Implementado |
| `prepare-tasks` | Skill Layer 1 | Tasks | ✅ Implementado |
| `sdd` | Skill master (opcional) | — | 🔲 Pendiente |
