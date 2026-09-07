# Spec Lab — Guía de la fase Spec

Guía de la etapa de **Spec** dentro del pipeline SDD: análisis del PRD, discovery de features, generación de specs por feature, evolución incremental y auditoría funcional.

> **Audiencia.** El **hilo principal (orquestador)** enruta la petición del usuario al workflow o agente correcto — el enrutado efectivo lo hacen las `description` de los skills (eager) y la regla eager `sdd-routing.md`. Un **subagente especialista** (p. ej. `sdd-spec-writer`) también carga esta guía al tocar artefactos de Spec: para él es **contexto de fase**, no una instrucción de rol — su contrato de trabajo es su propio system prompt + sus `kb-*`. **Con una excepción:** la sección siguiente —«Lo que escribes en un artefacto lo lee una persona»— describe la **forma obligatoria** de los artefactos de esta fase, así que vincula a todo el que escriba uno. Medido (pasada 9 de CU-3.a): los auditores tenían esta guía cargada y aun así nombraron workflows en sus informes, así que la norma vive **además** en la instrucción de rol de cada skill que redacta recomendaciones.

> **Precondiciones, desambiguación y fronteras de esta fase** (cuándo entra Spec, "crea las specs" → features-first no discover, guardrails, elección de rigor) viven en la regla **eager** `sdd-routing.md`, para que el hilo principal las tenga al orientar sin tocar ficheros.

## Lo que escribes en un artefacto lo lee una persona

Los artefactos de esta fase —`_analysis.md`, `_discovery.md`, `_spec.md`, `_conflict_report.md`, `_readiness_report.md`, `_features.md`— **los lee el usuario**, no solo el pipeline. Ahí dentro rige la misma frontera que en el chat (SSoT: `sdd-orchestration.md`, "Comunicación con el usuario"):

- **Estado y procedencia se quedan como están**: marcadores (`[CRÍTICO]`, `[INCOMPLETO]`, `[INFERIDO]`), veredictos (`LISTO_PARA_SPECS`, `PENDIENTE_GENERACIÓN`), IDs (`P-XXX`, `F-00X`, `CF-001`) y cabeceras de procedencia (`Generado por: wf-spec-discover`) son **contrato**: los parsean los scripts y los gates.
- **Las recomendaciones y los siguientes pasos van en lenguaje natural**: *"formalizar el cambio en el PRD antes de seguir"*, *"pedir que se aclare el CA-004"*. **No** se nombra el workflow que lo hace —ni `wf-spec-delta`, ni `/wf-spec-amend`, ni con barra ni sin ella—: el usuario no invoca comandos, te lo pide hablando, y surfacearlos le enseña a teclear argumentos a mano saltándose las validaciones.

Medido (pasada 8 de CU-3.a): **19 nombres de workflow** se colaron en un `_readiness_report.md`, dos `_conflict_report.md` y el `_features.md` de una corrida real. No los ponía ninguna plantilla — los ponía el agente, de su propio vocabulario.

## Skills de conocimiento Spec

Las `kb-*` viven en el frontmatter `skills: [...]` de los agentes de la fase; el harness las inyecta en el contexto del subagente. El hilo principal no las consulta ni necesita su inventario: vive en `sdd/meta/skill-registry.md` (mapa humano: el `README.md` de la fase). Las dependencias cross-fase (kb y workflows de PRD que esta fase necesita) las resuelve `install.sh spec` automáticamente.

> Los gaps pueden venir marcados con `[PUEDE_REQUERIR_CR]` cuando la futura respuesta tenga riesgo alto de expandir el producto. Ese marcador no cambia la severidad, pero obliga a reevaluar la respuesta con la gobernanza de cambios de producto antes de derivar discovery/specs. Si aun así se continúa, los artefactos deben marcar `Origen de alcance: PRD + analysis respondido` y `Avisos de gobernanza`.
