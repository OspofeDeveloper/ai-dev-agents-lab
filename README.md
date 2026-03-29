# ai-dev-agents-lab

Repositorio de skills, agentes y conocimiento para automatizar el flujo **Spec-Driven Development (SDD)** sobre proyectos **Kotlin Multiplatform Mobile (KMM)** con Clean Architecture.

---

## Qué es esto

Un ecosistema de agentes Claude Code que cubre el pipeline completo desde un PRD informal hasta tareas de implementación accionables, organizadas por capa KMM y listas para ser ejecutadas con skills especializadas.

```
PRD / Notas          Spec válido         Plan técnico        Tasks
informales    ──►    (_spec.md)   ──►    (_plan.md)   ──►   (_tasks.md)
                                                                  │
                                                         /kmm-domain
                                                         /kmm-data
                                                         /kmm-presentation
                                                         /kmm-tests
                                                         ...
```

---

## El pipeline SDD en tres etapas

### Etapa 1 — Specify

Transforma un documento de requisitos informal en un Spec funcional puro: sin tecnología, sin implementación, solo "qué" y "por qué".

**Prueba de Pureza:**
> "¿Cambiaría esta frase si pasáramos de KMM a web, o de Kotlin a Python?"
> - **SÍ** → es un detalle técnico → pertenece al Plan
> - **NO** → es funcional → puede estar en el Spec

Un Spec válido contiene exactamente 6 elementos obligatorios:
1. Recorridos de Usuario (User Journeys)
2. Resultados y Éxito
3. Instrucciones Inambiguas
4. Criterios de Aceptación (GIVEN/WHEN/THEN)
5. Checklists de Validación
6. Historias de Usuario

### Etapa 2 — Plan

Transforma un Spec validado en un plan técnico KMM. Aquí es donde entra la tecnología: stack, módulos, capas, contratos de API, decisiones de expect/actual.

Un Plan válido debe tener:
- Stack tech explícito (KMM, Compose, Ktor, etc.)
- Mapa de módulos (`:feature:X`, `:core:Y`)
- Diseño capa por capa: domain → data → presentation
- Contratos de API y DTOs
- Dependencias entre componentes
- Decisiones de expect/actual (Android/iOS)

Un Plan **no debe tener**: código implementado, requisitos funcionales del usuario, estimaciones de tiempo.

### Etapa 3 — Tasks

Transforma el Plan en tareas independientes y accionables, ordenadas por dependencias, cada una asignada a una skill KMM. Una task = un chunk implementable, una capa, un componente.

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

ETAPA 1    spec-expert   ──►    sdd-analyst   ──◄──  prepare-spec
SPECIFY    Reglas SDD            Analiza/             /prepare-spec
                                 Finaliza Specs        analyze|finalize

ETAPA 2    plan-expert   ──►    plan-architect ──◄── prepare-plan
PLAN       Reglas Plan           Spec → Plan          /prepare-plan
           + KMM arch            técnico               <spec.md>

ETAPA 3    tasks-expert  ──►    task-generator ──◄── prepare-tasks
TASKS      Reglas Tasks          Plan → Tasks         /prepare-tasks
           + sizing KMM          ordenados             <plan.md>
```

**Capa 1 — Skill Orquestador**: punto de entrada para el usuario (`/prepare-*`). Parsea argumentos, verifica archivos, delega al agente. No tiene `context: fork` — corre en el contexto principal para poder invocar agentes.

**Capa 2 — Agente Worker**: subagente con su propio contexto. Tiene `memory: project` para acumular aprendizaje del proyecto. Tiene `permissionMode: acceptEdits` para escribir artefactos sin interrupciones. Usa el knowledge base de Capa 3 inyectado vía `skills: [...]`.

**Capa 3 — Skill de Referencia**: solo conocimiento y reglas. No realiza acciones, define estándares. Se inyecta en el agente para que cada decisión de análisis esté basada en criterios explícitos.

---

## Estructura de archivos

```
~/.claude/
├── agents/
│   ├── sdd-analyst.md          ✅ Spec worker
│   ├── plan-architect.md       🔲 Plan worker (model: opus)
│   └── task-generator.md       🔲 Tasks worker
│
└── skills/
    ├── spec-expert/             ✅ Layer 3: Spec rules
    │   ├── SKILL.md
    │   └── references/
    │       ├── prohibited_items.md
    │       └── error_patterns.md
    │
    ├── plan-expert/             🔲 Layer 3: Plan rules
    │   ├── SKILL.md
    │   └── references/
    │       ├── kmm_architecture.md   ← KMM-specific
    │       ├── plan_structure.md
    │       └── plan_patterns.md
    │
    ├── tasks-expert/            🔲 Layer 3: Tasks rules
    │   ├── SKILL.md
    │   └── references/
    │       ├── task_sizing.md
    │       └── kmm_task_templates.md
    │
    ├── prepare-spec/            ✅ Layer 1: Spec orchestrator
    │   ├── SKILL.md
    │   └── references/
    │       └── analysis_template.md
    │
    ├── prepare-plan/            🔲 Layer 1: Plan orchestrator
    ├── prepare-tasks/           🔲 Layer 1: Tasks orchestrator
    └── sdd/                     🔲 Master pipeline (opcional)
```

---

## Puente SDD → KMM

El ecosistema SDD no reemplaza las skills KMM, las alimenta. Los Tasks generados en Etapa 3 están formateados para ser consumidos directamente por las skills de implementación:

```
SDD ECOSYSTEM                          KMM ECOSYSTEM
─────────────                          ─────────────

/prepare-spec  →  _spec.md
/prepare-plan  →  _plan.md
/prepare-tasks →  _tasks.md  ────►  /kmm-scaffold
                                    /kmm-domain
                                    /kmm-data
                                    /kmm-presentation
                                    /kmm-expect-actual
                                    /kmm-tests
                                    /kmm-audit
```

El `task-generator` conoce los nombres de las skills KMM y asigna cada task a la skill correcta. Después de `/prepare-tasks`, el trabajo es ejecutar tasks en orden.

---

## Workflow completo

```bash
# Etapa 1: Specify
/prepare-spec analyze prd.md        # → prd_analysis.md (gaps + preguntas)
# [editar prd_analysis.md, responder preguntas]
/prepare-spec finalize prd.md       # → prd_spec.md

# Etapa 2: Plan
/prepare-plan prd_spec.md           # → prd_plan.md (plan técnico KMM)
# [revisar y validar el plan]

# Etapa 3: Tasks
/prepare-tasks prd_plan.md          # → prd_tasks.md (tasks ordenadas por /kmm-*)
# [revisar dependencias y orden]

# Implementación con KMM skills
/kmm-scaffold  (T-000)
/kmm-domain    (T-001, T-002)
/kmm-data      (T-003, T-004)
/kmm-presentation (T-005)
/kmm-tests     (T-006)
```

---

## Propiedades de escalabilidad

**Evolución independiente**: cada knowledge base (Capa 3) evoluciona sola. Actualizar `kmm_architecture.md` en `plan-expert` no toca `spec-expert` ni `tasks-expert`.

**Modelo por complejidad**:
- `plan-architect` → `claude-opus-4-6` (decisiones arquitectónicas complejas)
- `task-generator` → `claude-sonnet-4-6` (formateo estructurado)
- `sdd-analyst` → modelo por defecto

**Memoria acumulativa**: cada agente worker tiene `memory: project`. Con el tiempo, el `plan-architect` recuerda decisiones de arquitectura de features anteriores y es consistente.

**Checkpoints humanos**: el pipeline nunca es fully-automatic. El humano valida artefactos estructurados entre cada etapa, no escribe código.

**Artefactos trazables**:
```
features/auth/
├── auth_spec.md        ← v1.0, VALIDATED
├── auth_plan.md        ← v1.0, VALIDATED
├── auth_tasks.md       ← v1.0, IN_PROGRESS
└── auth_analysis.md    ← borrador de análisis
```

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

| Componente | Tipo | Estado |
|---|---|---|
| `spec-expert` | Skill Layer 3 | ✅ Implementado |
| `sdd-analyst` | Agente Layer 2 | ✅ Implementado |
| `prepare-spec` | Skill Layer 1 | ✅ Implementado |
| `plan-expert` | Skill Layer 3 | ✅ Implementado |
| `plan-architect` | Agente Layer 2 | ✅ Implementado |
| `prepare-plan` | Skill Layer 1 | ✅ Implementado |
| `tasks-expert` | Skill Layer 3 | ✅ Implementado |
| `task-generator` | Agente Layer 2 | ✅ Implementado |
| `prepare-tasks` | Skill Layer 1 | ✅ Implementado |
| `sdd` | Skill master (opcional) | 🔲 Pendiente |
