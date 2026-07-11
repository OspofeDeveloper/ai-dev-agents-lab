# PRD Lab — Guía de la fase PRD

Guía de la etapa de **PRD** dentro del pipeline SDD: creación, estructuración y revisión de Product Requirements Documents antes de entrar en Spec.

> **Audiencia.** El **hilo principal (orquestador)** enruta la petición del usuario al workflow o agente correcto — el enrutado efectivo lo hacen las `description` de los skills (eager) y la regla eager `sdd-routing.md`. Un **subagente especialista** (p. ej. `prd-expert`) también carga esta guía al tocar artefactos de PRD: para él es **contexto de fase**, no una instrucción de rol — su contrato de trabajo es su propio system prompt + sus `kb-*`.

> **Precondiciones, desambiguación y fronteras de esta fase** (crear vs revisar, frontera create → review / gate de asunciones, cuándo un gap de Spec es cambio de producto) viven en la regla **eager** `sdd-routing.md`, para que el hilo principal las tenga al orientar sin tocar ficheros.

## Skills de conocimiento PRD

Las `kb-*` viven en el frontmatter `skills: [...]` de los agentes de la fase; el harness las inyecta en el contexto del subagente. El hilo principal no las consulta ni necesita su inventario: vive en `sdd/meta/skill-registry.md` (mapa humano: el `README.md` de la fase).
