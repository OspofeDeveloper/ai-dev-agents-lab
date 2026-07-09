# PRD Lab — Guía de la fase PRD

Guía de la etapa de **PRD** dentro del pipeline SDD: creación, estructuración y revisión de Product Requirements Documents antes de entrar en Spec.

> **Audiencia.** El **hilo principal (orquestador)** usa el enrutado de abajo para mapear la petición del usuario al workflow o agente correcto. Un **subagente especialista** (p. ej. `prd-expert`) también carga esta guía al tocar artefactos de PRD: para él es **contexto de fase**, no una instrucción de rol — su contrato de trabajo es su propio system prompt + sus `kb-*`.

## Reparto de trabajo en la fase PRD

- El **hilo principal (orquestador)** entiende la petición, decide si hay que crear un PRD desde cero, revisar uno existente o resolver una duda conceptual sobre PRDs, y activa el workflow o agente correcto. **No redacta el documento final**, no hace análisis funcional de Spec y no toma decisiones técnicas de implementación.
- La **redacción, reorganización y revisión guiada** del PRD la realiza el agente **`prd-expert`**, con `kb-prd-expert` cargada en su contexto.
- El enrutado no construye prompts a mano: las workflows y `prd-expert` ya contienen el conocimiento operativo necesario; el hilo principal solo activa la pieza correcta con los argumentos correctos.

> **Precondiciones, desambiguación y fronteras de esta fase** (crear vs revisar, frontera create → review / gate de asunciones, cuándo un gap de Spec es cambio de producto) viven en la regla **eager** `sdd-routing.md`, para que el hilo principal las tenga al orientar sin tocar ficheros.

## Rootmap de workflow skills

| Intención del usuario | Skill | Argumentos |
|---|---|---|
| Crear un PRD desde notas, brief o idea inicial | `/wf-prd-create` | `<directorio_proyecto> [--source <notas.md>] [--output <prd.md>]` |
| Revisar si un PRD está limpio y bien planteado | `/wf-prd-review` | `<archivo_prd.md>` |
| Gestionar un cambio de producto sobre un PRD ya existente | `/wf-prd-change` | `<archivo_prd.md> --new-reqs <cambio.md>` |
| Propagar un cambio de PRD por todo el pipeline en un solo comando (cascade) | `/wf-prd-change-cascade` | `<archivo_prd.md> [--new-reqs <cambio.md>] [--features F-001,...] [--review-before-apply] [--skip-design] [--dry-run]` |

> El rootmap de arriba es referencia. El enrutado intención→skill efectivo lo hacen las `description` de los skills (eager); esta tabla documenta argumentos y agrupa por intención.

## Agentes PRD disponibles

La unidad primaria de trabajo en esta etapa es el **agente especializado en PRD**.

| Agente | Dominio |
|---|---|
| `prd-expert` | Redacción, reorganización y revisión guiada de PRDs orientados a negocio y compatibles con el pipeline SDD |

Se usan workflows cuando existe una pipeline clara y cerrada. Si la petición no requiere una workflow concreta pero sí ayuda experta para redactar o limpiar un PRD, el hilo principal delega a `prd-expert`.

## Skills de conocimiento PRD

Las `kb-*` viven en el frontmatter `skills: [...]` de los agentes de la fase; el harness las inyecta en el contexto del subagente. El hilo principal no las consulta ni necesita su inventario: vive en `sdd/meta/skill-registry.md` (mapa humano: el `README.md` de la fase).

## Reparto por agente (a quién delega el hilo principal)

- Si la petición es de **redacción, reorganización o revisión guiada** de un PRD, o una **duda conceptual** sobre qué debe contener → `prd-expert` (ya carga `kb-prd-expert`).
- Si encaja en una `wf-*` cerrada y adecuada, se usa esa workflow; los subagentes trabajan con sus `kb-*` ya cargadas y el hilo principal no replica ese conocimiento.
