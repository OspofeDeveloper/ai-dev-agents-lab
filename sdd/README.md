# ai-dev-agents-lab

Repositorio de skills, agentes y conocimiento para automatizar el flujo **Spec-Driven Development (SDD)** sobre proyectos **Kotlin Multiplatform Mobile (KMM)** con Clean Architecture.

> 📖 **Documentación completa:** el sitio MkDocs en `sdd/docs/` (visión funcional y técnica, guías por perfil, tutorial y referencia). Servir local: `cd sdd && NO_MKDOCS_2_WARNING=1 mkdocs serve`. Publicado en GitHub Pages vía CI.

---

## Qué es esto

Un ecosistema de agentes Claude Code que cubre el pipeline completo desde un PRD informal hasta tareas de implementación accionables por feature, listas para ser delegadas a agentes KMM especializados.

```
PRD / Notas       Spec limpio       Specs por        Design           Plan técnico      Tasks
informales  ──►   monolítico  ──►   feature    ──►   validado   ──►  por feature ──►  por feature
                  (_spec.md)       (features/         (DESIGN.md,      (_plan.md)       (_tasks.md)
                                    <x>_spec.md)      views, prompt)
                                                           │
                                                     validación formal
                                                           │
                                                           kmm-feature-logic-implementer
                                                           kmm-feature-ui-implementer
                                                           kmm-platform-integrator
                                                           kmm-network-auth-implementer
```

---

## El pipeline SDD en seis etapas

### Etapa 0 — PRD

Revisa y limpia el documento de entrada antes de convertirlo en Spec. Aquí se valida que el PRD describe negocio, actores, alcance y exclusiones sin contaminarse con decisiones técnicas.

Un PRD válido para este ecosistema:
- describe un producto completo, no un fragmento arbitrario
- explicita actores
- declara alcance dentro y fuera
- puede organizarse por actores, por RFs o por secciones funcionales
- no mezcla implementación técnica

`wf-prd-create` ayuda a redactar el documento inicial. El preflight recomendado es `wf-prd-review`. El paso obligatorio del pipeline sigue siendo `wf-spec-analyze`.

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
- `features/<nombre>/spec/<nombre>_spec.md` — un Spec SDD completo y autocontenido por feature

### Etapa 3 — Design

Transforma cada spec de feature en un contrato visual reusable por herramientas como Stitch. Aqui no entra implementacion tecnica, sino identidad visual, flujos de interfaz, inventario de vistas y prompt estructurado para prototipado.

Un Design valido produce:
- `DESIGN.md` a nivel producto
- `<feature>_flows.md` para secuencias y transiciones
- `<feature>_views.md` como SSoT de pantallas, componentes y estados visuales
- `<feature>_ui_prompt.md` como ensamblaje para Stitch

La fase `design` no redefine requisitos funcionales. Si una decision cambia HUs, journeys o CAs, vuelve a `spec`.

### Etapa 4 — Plan

Transforma cada spec de feature y su handoff de Design en un plan técnico KMM. Aquí entra la tecnología: stack, módulos, capas, contratos, ownership y decisiones de expect/actual.

Un Plan válido debe tener:
- Stack tech explícito (KMM, Compose, Ktor, etc.)
- Mapa de módulos (`:feature:X`, `:core:Y`)
- Diseño capa por capa: domain → data → presentation
- Contratos de API y DTOs
- Dependencias entre componentes
- Decisiones de expect/actual (Android/iOS)
- Materialización técnica del handoff de Design y accesibilidad si aplica

Un Plan **no debe tener**: código implementado, requisitos funcionales del usuario, estimaciones de tiempo.

El `_plan.md` sale primero en estado `BORRADOR` y debe pasar una validación formal antes de generar Tasks.

Los shared models declarados en `_features.md` no se redefinen: la feature owner los define completos; el resto los referencia.

### Etapa 5 — Tasks

Transforma el Plan de cada feature en tareas independientes y accionables, ordenadas por dependencias, cada una asignada a un **owner agent KMM**. Una task = un chunk implementable, con un dominio de ejecución y un responsable claro.

Ejemplo de task:
```
## T-001: Domain Layer — LoginUseCase
- Spec CA: CA-003
- Plan ref: §3.2 Domain Module
- Layer: domain | Module: :feature:auth
- Execution domain: feature
- Owner agent: kmm-feature-logic-implementer
- Dependencies: ninguna
- Definition of done: UseCase + Repository interface + Model creados
```

---

## Arquitectura del ecosistema: 6 etapas × 3 capas

Cada etapa sigue el mismo patrón arquitectónico de 3 capas:

```
              LAYER 3              LAYER 2              LAYER 1
           (Conocimiento)       (Agente Worker)      (Workflow)

ETAPA 0    kb-prd-expert  ──►   prd-expert         ──◄──  wf-prd-create
PRD        Reglas PRD            Redacta / revisa PRD      wf-prd-review

ETAPA 1    kb-spec-expert ──►   sdd-spec-explorer  ──◄──  wf-spec-analyze
SPECIFY    kb-decompose-         Diagnóstico               wf-spec-discover
           expert                                         wf-prd-sync-impact
           kb-product-
           change-governance
           kb-traceability-
           rules

           kb-spec-expert ──►   sdd-spec-writer    ──◄──  wf-spec-fast-track
           kb-gap-              Escritura / delta         wf-spec-delta
           conventions          / sync                    wf-spec-gap-resolve
           kb-traceability-                                wf-spec-sync-from-prd
           rules

           kb-spec-expert ──►   sdd-spec-auditor   ──◄──  wf-spec-validate
           kb-conflict-         Auditoría                 wf-spec-conflict
           expert                                         wf-spec-readiness

           sdd-spec-planner     Planifica approach

           wf-spec-features-first
           Orquesta discover + fast-track en paralelo

ETAPA 3    kb-design-expert ─►   design-architect ─◄── wf-design-system
DESIGN     Reglas design         Spec -> DESIGN.md     wf-design-feature-prototype
                                  y prototipo

ETAPA 4    kb-plan-expert ──►   plan-architect ──◄── wf-prepare-plan
PLAN       Reglas Plan           Spec + Design →      /wf-prepare-plan
           + KMM arch            Plan técnico          <spec.md>
                                                     wf-plan-validate
                                                     <plan.md>

ETAPA 5    kb-tasks-expert ──►  task-generator ──◄── wf-prepare-tasks
TASKS      Reglas Tasks          Plan → Tasks         /wf-prepare-tasks
           + sizing KMM          ordenados             <plan.md>
```

**Capa 1 — Skill Workflow (`wf-`)**: punto de entrada para el usuario. Parsea argumentos, verifica archivos, delega al agente. Contiene las instrucciones del workflow que el agente ejecuta.

**Capa 2 — Agente Worker**: subagente con su propio contexto. Tiene `memory: project` para acumular aprendizaje del proyecto. Tiene `permissionMode: acceptEdits` para escribir artefactos sin interrupciones. Usa los knowledge bases de Capa 3 inyectados vía `skills: [...]`.

**Capa 3 — Skill de Knowledge (`kb-`)**: solo conocimiento y reglas. No realiza acciones, define estándares. Se inyecta en el agente para que cada decisión esté basada en criterios explícitos.

> **Nota**: la arquitectura actual separa exploración, planificación, escritura y auditoría en agentes distintos. No existe ya un worker monolítico para Spec.

---

## Estructura de archivos

```
~/.claude/
├── agents/
│   ├── prd-expert.md           ✅ Worker: PRD authoring + review
│   ├── sdd-spec-explorer.md    ✅ Worker: diagnóstico Spec
│   ├── sdd-spec-planner.md     ✅ Worker: planning Spec
│   ├── sdd-spec-writer.md      ✅ Worker: escritura Spec
│   ├── sdd-spec-auditor.md     ✅ Worker: auditoría Spec
│   ├── design-architect.md     ✅ Worker: Design / Stitch
│   ├── plan-architect.md       ✅ Worker: Plan (model: opus)
│   └── task-generator.md       ✅ Worker: Tasks
│
└── skills/
    ├── kb-prd-expert/           ✅ Knowledge: PRD rules
    │   ├── SKILL.md
    │   └── references/
    │       ├── prd_structure_guide.md
    │       ├── prd_error_patterns.md
    │       └── prd_prohibited_items.md
    │
    ├── kb-product-change-governance/ ✅ Knowledge: product change governance
    │   └── SKILL.md
    │
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
    ├── kb-traceability-rules/   ✅ Knowledge: sync status and derivation rules
    │   └── SKILL.md
    │
    ├── kb-plan-expert/          ✅ Knowledge: Plan rules
    │   ├── SKILL.md
    │   └── references/
    │       ├── kmm_architecture.md
    │       └── plan_structure.md
    │
    ├── kb-design-expert/        ✅ Knowledge: Design rules
    │   ├── SKILL.md
    │   └── references/
    │       ├── design_md_template.md
    │       ├── feature_flows_template.md
    │       ├── feature_views_template.md
    │       └── feature_ui_prompt_template.md
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
    ├── wf-prd-create/           ✅ Workflow: Create PRD
    │   └── SKILL.md
    │
    ├── wf-prd-review/           ✅ Workflow: PRD preflight
    │   └── SKILL.md
    │
    ├── wf-prd-change/           ✅ Workflow: Product change management on PRD
    │   └── SKILL.md
    │
    ├── wf-design-system/        ✅ Workflow: Product design system
    │   ├── SKILL.md
    │   └── references/output_notes.md
    │
    ├── wf-design-feature-prototype/ ✅ Workflow: Feature prototype for Stitch
    │   ├── SKILL.md
    │   └── references/output_bundle_template.md
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
    ├── wf-spec-gap-resolve/     ✅ Workflow: Complete incomplete HUs from analysis
    │   └── SKILL.md
    │
    ├── wf-prd-sync-impact/      ✅ Workflow: Analyze PRD change impact downstream
    │   └── SKILL.md
    │
    ├── wf-spec-sync-from-prd/   ✅ Workflow: Resync feature specs after PRD changes
    │   └── SKILL.md
    │
    ├── wf-prepare-plan/         ✅ Workflow: Spec + Design → Plan
    │   └── SKILL.md
    │
    ├── wf-plan-validate/        ✅ Workflow: Audit Plan before Tasks
    │   └── SKILL.md
    │
    └── wf-prepare-tasks/        ✅ Workflow: Plan → Tasks
        └── SKILL.md
```

---

## Estructura de artefactos en tu proyecto

```
project-root/
├── prd.md                              # PRD original
├── prd_analysis.md                     # /wf-spec-analyze (recomendado)
├── prd_discovery.md                    # /wf-spec-discover — mapa de features
├── prd_features.md                     # /wf-spec-features-first — índice de features y shared models
├── DESIGN.md                           # /wf-design-system — sistema visual de producto
│
└── features/
    ├── authentication/
    │   ├── README.md                       # /wf-spec-fast-track
    │   ├── spec/
    │   │   └── authentication_spec.md      # /wf-spec-fast-track
    │   ├── design/
    │   │   ├── authentication_flows.md     # /wf-design-feature-prototype
    │   │   ├── authentication_views.md     # /wf-design-feature-prototype
    │   │   └── authentication_ui_prompt.md # /wf-design-feature-prototype
    │   ├── plan/
    │   │   └── authentication_plan.md      # /wf-prepare-plan
    │   └── tasks/
    │       └── authentication_tasks.md     # /wf-prepare-tasks
    └── <una carpeta por feature>/
```

> Features creadas con el layout plano legacy (todos los artefactos directamente en `features/<nombre>/`) siguen siendo válidas: los workflows leen ambos layouts y no los mezclan dentro de una misma feature.

---

## Workflow completo

```bash
# ── Etapa 1: Specify ──────────────────────────────────────────────────────────
/wf-spec-analyze prd.md
# → prd_analysis.md con:
#     · mapa de elementos del Spec a generar desde el PRD (informativo)
#     · pureza del PRD (única condición que justifica modificarlo)
#     · gaps [CRÍTICO] e [INFORMATIVO] de negocio
# Veredicto: LISTO_PARA_SPECS | LISTO_PARA_SPECS_CON_PREGUNTAS | REQUIERE_LIMPIEZA_PRD

# [HUMANO] Si quedan gaps [CRÍTICO], decidir:
#   a) responderlos en prd_analysis.md
#   b) seguir igualmente aceptando HUs [INCOMPLETO]

# Opción A — Generar specs de TODO el PRD en una sola pasada:
/wf-spec-features-first prd.md
# Si hay gaps [CRÍTICO] pendientes, re-ejecutar con:
# /wf-spec-features-first prd.md --allow-open-critical-gaps
# Si las respuestas del analysis expanden el producto pero se decide continuar
# igualmente dejando trazabilidad de gobernanza:
# /wf-spec-features-first prd.md --allow-derived-scope-from-analysis
# Si el discovery detecta más de 5 features, el workflow pedirá iterar por subset
# salvo override explícito con `--all-features`.
# → prd_discovery.md (mapa de features + scope RF→Feature)
# → prd_features.md (índice de features + tabla de shared models)
# → features/<nombre>/spec/<nombre>_spec.md (un spec por feature, en paralelo)

# Opción B — Iterativo por fases / subset (delivery por fases):
/wf-spec-discover prd.md --analysis prd_analysis.md
# → prd_discovery.md con el mapa F-001..F-N

# [HUMANO] Elegir qué Feature IDs entran en la iteración actual

/wf-spec-features-first prd.md --features F-001,F-002,F-003
# → Genera specs solo para las features indicadas
# → prd_features.md marca el resto como PENDIENTE_GENERACIÓN
# → las generadas quedan como LISTA, BLOQUEADA o REQUIERE_CAMBIO_PRD
# Más tarde:  /wf-spec-features-first prd.md --features F-004,F-005

# [HUMANO] Revisar prd_features.md: ajustar scope si es necesario
#          Confirmar qué feature es owner de cada shared model


# ── Etapa 3: Design por producto y por feature ───────────────────────────────
# Generar o actualizar primero el sistema visual compartido
/wf-design-system generate features/authentication/authentication_spec.md
# → DESIGN.md

# Derivar artefactos de prototipado por feature
/wf-design-feature-prototype generate features/authentication/authentication_spec.md
# → features/authentication/authentication_flows.md
# → features/authentication/authentication_views.md
# → features/authentication/authentication_ui_prompt.md

# [HUMANO] Validar con cliente las vistas generadas en Stitch antes de pasar a plan


# ── Etapas 4 y 5: Por cada feature ───────────────────────────────────────────
# Empezar por las features owner de shared models

/wf-prepare-plan generate features/authentication/authentication_spec.md
# → features/authentication/authentication_plan.md

/wf-plan-validate features/authentication/authentication_plan.md
# → OK / hallazgos del plan

/wf-prepare-tasks generate features/authentication/authentication_plan.md
# → features/authentication/authentication_tasks.md

# Repetir para el resto de features (pueden procesarse en paralelo)
/wf-prepare-plan generate features/services/services_spec.md
/wf-plan-validate features/services/services_plan.md
/wf-prepare-tasks generate features/services/services_plan.md
# ...


# ── Implementación con agentes KMM ───────────────────────────────────────────
# Por cada feature, delegar las tasks en orden al owner agent indicado:
# T-000  -> kmm-platform-integrator
# T-001… -> kmm-feature-logic-implementer (Layer domain/data) | kmm-feature-ui-implementer (Layer presentation)
# T-00X  -> kmm-network-auth-implementer (si hay infraestructura transversal)
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

El ecosistema SDD alimenta directamente a los agentes KMM de implementación:

```
SDD ECOSYSTEM                              KMM ECOSYSTEM
─────────────                              ─────────────

/wf-spec-analyze + /wf-spec-features-first → features/<x>_spec.md
/wf-prepare-plan   → features/<x>_plan.md
/wf-plan-validate  → gate formal del plan
/wf-prepare-tasks  → features/<x>_tasks.md ──► kmm-feature-logic-implementer
                                             kmm-feature-ui-implementer
                                             kmm-platform-integrator
                                             kmm-network-auth-implementer
```

El `task-generator` conoce los dominios de implementación KMM y asigna cada task a un `owner agent`. Después de `/wf-prepare-tasks`, el trabajo del orquestador es delegar las tasks en orden al agente correcto, no ejecutar una skill por capa.

---

## Propiedades de escalabilidad

**Evolución independiente**: cada knowledge base (Capa 3) evoluciona sola. Actualizar `kmm_architecture.md` en `kb-plan-expert` no afecta a `kb-spec-expert`, `kb-decompose-expert` ni `kb-tasks-expert`.

**Modelo por complejidad**:
- `plan-architect` → `claude-opus-4-8` (decisiones arquitectónicas complejas)
- `task-generator` → `claude-sonnet-4-6` (formateo estructurado)
- agentes Spec → modelo por defecto, con responsabilidad separada por tipo de trabajo

**Memoria acumulativa**: cada agente worker tiene `memory: project`. Con el tiempo, los agentes de Spec y el `plan-architect` recuerdan decisiones previas y mantienen consistencia entre artefactos.

**Checkpoints humanos**: el pipeline nunca es fully-automatic. El humano valida artefactos estructurados en cuatro puntos clave:
1. Tras `wf-spec-analyze` → responder gaps de negocio _(pendiente)_ en el `_analysis.md` o, si cambió el producto comprometido, abrir `wf-prd-change`
2. Tras `wf-spec-discover` (modo iterativo) → elegir qué Feature IDs entran en la próxima iteración
3. Tras `wf-spec-features-first` → validar partición y ownership de shared models
4. Tras cada `wf-prepare-plan` → validar el plan y revisar arquitectura antes de generar tasks

**Trazabilidad completa**: cada task apunta a un CA del spec de feature. Cada CA del spec de feature es rastreable al spec monolítico origen. Los artefactos derivados deben poder declarar además contra qué versión del PRD fueron generados y si siguen `in_sync`.

---

## Instalación

Este repositorio es la fuente de verdad. La instalación tiene dos niveles: un **bootstrap global** por máquina y una **instalación por proyecto**.

### Bootstrap global (una vez por máquina)

```bash
git clone <repo-url>
cd ai-dev-agents-lab
bash sdd/setup.sh
```

Registra el hook de sesión (`~/.claude/hooks/sdd-session-check.sh`), el bloque de protocolo SDD en `~/.claude/CLAUDE.md`, las skills globales (`wf-project-init`, `wf-sdd-update`) y apunta `~/.sdd-home` a este checkout. Tras un `git pull`: `bash sdd/setup.sh --update`.

### Instalación por proyecto

Abre Claude Code en el proyecto: el hook ofrece el wizard (Modo SDD / Modo libre) y `wf-project-init` hace la entrevista e instala las fases elegidas en el `.claude/` **del proyecto** (no en el global). Vía manual: `bash <SDD_HOME>/install.sh <fase1,fase2,...>` desde la raíz del proyecto. Para actualizar un proyecto a la versión vigente del ecosistema: `/wf-sdd-update` (respeta overlays de stack y no re-entrevista).

Si te importa el rendimiento del agente, instala solo las fases que necesites. Las fases están diseñadas para trabajar con precondiciones duras y no necesitan cargar el ecosistema completo a la vez.

---

## Onboarding y política de git

### Qué se commitea en un proyecto SDD

| Path | ¿Git? | Por qué |
|---|---|---|
| `.claude/` (skills, agents, rules, settings.json) | ✅ | El proyecto funciona para cualquier dev y en CI sin tener el ecosistema instalado |
| `.claude/settings.local.json` | ❌ nunca | Permisos personales de sesión con paths absolutos (`wf-project-init` lo añade a `.gitignore`) |
| `.sdd/` (project-init.json, scripts/, sdd-version.json) | ✅ | Estado del proyecto + scripts de enforcement (gates, sellador) ejecutables en CI |
| Artefactos (PRD, `features/`, design) | ✅ | Son el producto del pipeline |

### Dev nuevo en un proyecto ya inicializado

1. Clona el proyecto → **funciona ya**: skills, agentes, rules, hooks de gates y scripts de enforcement viajan commiteados.
2. (Recomendado) Clona también este ecosistema y ejecuta `bash sdd/setup.sh`: habilita el protocolo de sesión, `/wf-sdd-update` y el init de proyectos nuevos.

### Varios devs en paralelo: una feature por rama

- **Una feature = una rama.** Cada feature vive aislada en `features/<nombre>/` (spec, design, plan, tasks): devs en features distintas no colisionan.
- **`_features.md` es un índice generado**, no se edita a mano: lo regenera `python3 .sdd/scripts/sdd-features-index.py <raíz_spec>` desde el discovery + los specs en disco + el readiness report. Un conflicto de merge sobre él es ruido — se regenera tras el merge (la verdad vive repartida por feature, no en el hub). Mismo principio que el registry generado.
- El registro de inits de stack es el log append-only `.sdd/stack-runs.jsonl` (no un array en `project-init.json`): ramas distintas se combinan sin pisarse.

### CI / runners headless

- Los gates PreToolUse y el sellador funcionan en CI sin el ecosistema al lado: viven commiteados en `.sdd/scripts/` con su sello de versión.
- El protocolo de sesión se suprime con `SDD_NON_INTERACTIVE=1` (o automáticamente con `CI=true`). El opt-out commiteable por repo es `.claude/sdd-mode.json`.
- `sdd-features-index.py --check <raíz_spec>` falla (exit 2) si `_features.md` está desactualizado respecto a sus fuentes: útil como check de CI para detectar índices a mano sin regenerar.

---

## Estado de implementación

| Componente | Tipo | Etapa | Estado |
|---|---|---|---|
| `kb-prd-expert` | Knowledge (kb) | PRD | ✅ Implementado |
| `kb-spec-expert` | Knowledge (kb) | Specify | ✅ Implementado |
| `kb-decompose-expert` | Knowledge (kb) | Decompose | ✅ Implementado |
| `kb-conflict-expert` | Knowledge (kb) | Conflict | ✅ Implementado |
| `kb-gap-conventions` | Knowledge (kb) | Transversal | ✅ Implementado |
| `kb-plan-expert` | Knowledge (kb) | Plan | ✅ Implementado |
| `kb-tasks-expert` | Knowledge (kb) | Tasks | ✅ Implementado |
| `prd-expert` | Agente Worker | PRD | ✅ Implementado |
| `sdd-spec-explorer` | Agente Worker | Specify | ✅ Implementado |
| `sdd-spec-planner` | Agente Worker | Specify | ✅ Implementado |
| `sdd-spec-writer` | Agente Worker | Specify | ✅ Implementado |
| `sdd-spec-auditor` | Agente Worker | Specify | ✅ Implementado |
| `plan-architect` | Agente Worker | Plan | ✅ Implementado |
| `task-generator` | Agente Worker | Tasks | ✅ Implementado |
| `wf-prd-create` | Workflow (wf) | PRD | ✅ Implementado |
| `wf-prd-review` | Workflow (wf) | PRD | ✅ Implementado |
| `wf-spec-analyze` | Workflow (wf) | Specify | ✅ Implementado |
| `wf-spec-validate` | Workflow (wf) | Specify | ✅ Implementado |
| `wf-spec-discover` | Workflow (wf) | Specify | ✅ Implementado |
| `wf-spec-features-first` | Workflow (wf) | Specify | ✅ Implementado |
| `wf-spec-fast-track` | Workflow (wf) | Specify | ✅ Implementado |
| `wf-spec-conflict` | Workflow (wf) | Conflict | ✅ Implementado |
| `wf-plan-validate` | Workflow (wf) | Plan | ✅ Implementado |
| `wf-spec-delta` | Workflow (wf) | Delta | ✅ Implementado |
| `wf-prepare-plan` | Workflow (wf) | Plan | ✅ Implementado |
| `wf-prepare-tasks` | Workflow (wf) | Tasks | ✅ Implementado |
