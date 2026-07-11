# Spec Lab — Guía de la fase Spec

Guía de la etapa de **Spec** dentro del pipeline SDD: análisis del PRD, discovery de features, generación de specs por feature, evolución incremental y auditoría funcional.

> **Audiencia.** El **hilo principal (orquestador)** enruta la petición del usuario al workflow o agente correcto — el enrutado efectivo lo hacen las `description` de los skills (eager) y la regla eager `sdd-routing.md`. Un **subagente especialista** (p. ej. `sdd-spec-writer`) también carga esta guía al tocar artefactos de Spec: para él es **contexto de fase**, no una instrucción de rol — su contrato de trabajo es su propio system prompt + sus `kb-*`.

> **Precondiciones, desambiguación y fronteras de esta fase** (cuándo entra Spec, "crea las specs" → features-first no discover, guardrails, elección de rigor) viven en la regla **eager** `sdd-routing.md`, para que el hilo principal las tenga al orientar sin tocar ficheros.

## Skills de conocimiento Spec

Las `kb-*` viven en el frontmatter `skills: [...]` de los agentes de la fase; el harness las inyecta en el contexto del subagente. El hilo principal no las consulta ni necesita su inventario: vive en `sdd/meta/skill-registry.md` (mapa humano: el `README.md` de la fase). Las dependencias cross-fase (kb y workflows de PRD que esta fase necesita) las resuelve `install.sh spec` automáticamente.

> Los gaps pueden venir marcados con `[PUEDE_REQUERIR_CR]` cuando la futura respuesta tenga riesgo alto de expandir el producto. Ese marcador no cambia la severidad, pero obliga a reevaluar la respuesta con la gobernanza de cambios de producto antes de derivar discovery/specs. Si aun así se continúa, los artefactos deben marcar `Origen de alcance: PRD + analysis respondido` y `Avisos de gobernanza`.
