# Spec Lab — Guía de la fase Spec

Guía de la etapa de **Spec** dentro del pipeline SDD: análisis del PRD, discovery de features, generación de specs por feature, evolución incremental y auditoría funcional.

> **Audiencia.** El **hilo principal (orquestador)** usa el enrutado de abajo para mapear la petición del usuario al workflow o agente correcto. Un **subagente especialista** (p. ej. `sdd-spec-writer`) también carga esta guía al tocar artefactos de Spec: para él es **contexto de fase**, no una instrucción de rol — su contrato de trabajo es su propio system prompt + sus `kb-*`.

## Reparto de trabajo en la fase Spec

- El **hilo principal (orquestador)** entiende la petición, decide si hay que analizar un PRD, descubrir features, generar o evolucionar specs o auditar artefactos, y activa el workflow o agente correcto. **No redacta specs finales**, no genera planes técnicos ni hace tasks de implementación.
- La **redacción, evolución y auditoría** de specs las realizan los agentes Spec (`sdd-spec-writer`, `sdd-spec-auditor`, …), con sus `kb-*` cargadas en contexto.
- El enrutado no construye prompts a mano: las workflows y los agentes ya contienen el conocimiento operativo; el hilo principal solo activa la pieza correcta con los argumentos correctos.

> **Precondiciones, desambiguación y fronteras de esta fase** (cuándo entra Spec, "crea las specs" → features-first no discover, guardrails, elección de rigor) viven en la regla **eager** `sdd-routing.md`, para que el hilo principal las tenga al orientar sin tocar ficheros.

## Rootmap de workflow skills

| Intención del usuario | Skill | Argumentos |
|---|---|---|
| Analizar un PRD/documento de requisitos para detectar gaps | `/wf-spec-analyze` | `<archivo_prd.md>` |
| Generar specs desde código existente (brownfield, sin PRD) | `/wf-spec-from-code` | `discover <path_codigo> [--scope <subdir>] \| generate <path_codigo> --feature <F-C-00X>` |
| Identificar features de un PRD | `/wf-spec-discover` | `<archivo_prd.md> [--analysis <analysis.md>] [--allow-derived-scope-from-analysis]` |
| Generar todos los specs por feature desde un PRD | `/wf-spec-features-first` | `<archivo_prd.md> [--light\|--standard] [--all-features] [--allow-open-critical-gaps] [--allow-derived-scope-from-analysis] [--skip-conflict] [--skip-readiness]` |
| Generar specs de un subset / iteración / fase de features | `/wf-spec-features-first` | `<archivo_prd.md> --features F-001,F-002,... [--allow-open-critical-gaps] [--allow-derived-scope-from-analysis]` |
| Generar spec directo de una feature | `/wf-spec-fast-track` | `<archivo.md> --capability <nombre> [--light\|--standard] [--analysis <analysis.md>] [--allow-derived-scope-from-analysis]` (acepta cualquier doc acotado a una capacidad, no solo PRD) |
| Generar spec de una feature desde un discovery | `/wf-spec-fast-track` | `<prd.md> --scope-from <discovery.md> --feature <F-00X> [--light\|--standard] [--analysis <analysis.md>] [--allow-derived-scope-from-analysis]` |
| Validar un spec existente | `/wf-spec-validate` | `<archivo_spec.md>` |
| Detectar conflictos entre specs de features | `/wf-spec-conflict` | `<feature_spec.md> --features-dir <path/features/>` |
| Ver qué features están listas y el orden de implementación | `/wf-spec-readiness` | `<path/features/>` |
| Analizar cambios sobre un spec existente | `/wf-spec-delta` | `analyze <feature_spec.md> --new-reqs <description.md>` |
| Aplicar un delta analysis a un spec | `/wf-spec-delta` | `apply <feature_spec.md> <delta_analysis.md>` |
| Completar HUs incompletas desde un analysis | `/wf-spec-gap-resolve` | `<feature_spec.md> [--analysis <path_analysis.md>]` |
| Aclarar un CA ambiguo descubierto al implementar (back-edge) | `/wf-spec-amend` | `<feature_spec.md> --ca CA-XXX [--from-task T-00X] [--reason 'texto']` |
| Formalizar un cambio de producto antes de resincronizar specs ⚠ | `/wf-prd-change` | `<archivo_prd.md> --new-reqs <cambio.md>` |
| Analizar impacto de un cambio de PRD sobre artefactos Spec | `/wf-prd-sync-impact` | `<archivo_prd.md>` |
| Resincronizar specs tras un cambio de PRD | `/wf-spec-sync-from-prd` | `analyze <prd.md> \| apply <prd.md> --features F-001,F-002,...` |

> ⚠ `/wf-prd-change` vive físicamente en la fase PRD (`sdd/pipeline/prd/skills/`). El orquestador Spec lo lista porque es el handoff correcto cuando una respuesta a un gap se convierte en cambio de producto, pero la ejecución pertenece a la fase PRD.

> El rootmap de arriba es referencia. El enrutado intención→skill efectivo lo hacen las `description` de los skills (eager); esta tabla documenta argumentos y agrupa por intención.

## Agentes Spec disponibles

| Agente | Dominio |
|---|---|
| `sdd-spec-explorer` | Exploración, diagnóstico y lectura del estado de artefactos Spec |
| `sdd-spec-planner` | Planificación del approach de trabajo dentro del ecosistema Spec |
| `sdd-spec-writer` | Escritura y evolución de artefactos Spec |
| `sdd-spec-auditor` | Validación, conflictos y readiness de artefactos Spec |

Se usan workflows cuando existe una pipeline clara y cerrada. Si la petición no requiere una workflow exacta, el hilo principal delega al agente cuyo dominio coincida con la intención real del usuario. Si la petición es ambigua entre varias operaciones de Spec, primero `sdd-spec-planner`.

## Skills de conocimiento Spec

Las `kb-*` viven en el frontmatter `skills: [...]` de los agentes de la fase; el harness las inyecta en el contexto del subagente. El hilo principal no las consulta ni necesita su inventario: vive en `sdd/meta/skill-registry.md` (mapa humano: el `README.md` de la fase). Las dependencias cross-fase (kb y workflows de PRD que esta fase necesita) las resuelve `install.sh spec` automáticamente.

> Los gaps pueden venir marcados con `[PUEDE_REQUERIR_CR]` cuando la futura respuesta tenga riesgo alto de expandir el producto. Ese marcador no cambia la severidad, pero obliga a reevaluar la respuesta con la gobernanza de cambios de producto antes de derivar discovery/specs. Si aun así se continúa, los artefactos deben marcar `Origen de alcance: PRD + analysis respondido` y `Avisos de gobernanza`.

## Reparto por agente (a quién delega el hilo principal)

- Si la petición es diagnóstica (leer estado de artefactos) → `sdd-spec-explorer`.
- Si necesita decidir approach antes de actuar → `sdd-spec-planner`.
- Si es escritura o evolución de artefactos → `sdd-spec-writer`.
- Si es validación, conflictos o readiness → `sdd-spec-auditor`.
