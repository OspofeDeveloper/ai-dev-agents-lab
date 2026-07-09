# Plan Lab — Guía de la fase Plan

Este directorio define un paquete focalizado en la etapa de **Plan** dentro del pipeline SDD: traducción de un `*_spec.md` validado y su handoff de Design a un `_plan.md` técnico (especializado por el overlay de stack si existe; genérico si el stack es agnóstico), seguido de una validación formal antes de pasar a Tasks.

> **Audiencia.** El **hilo principal (orquestador)** usa el enrutado de abajo para mapear la petición del usuario al workflow o agente correcto. Un **subagente especialista** (p. ej. `plan-architect`) también carga esta guía al tocar artefactos de Plan: para él es **contexto de fase**, no una instrucción de rol — su contrato de trabajo es su propio system prompt + sus `kb-*`.

## Reparto de trabajo en la fase Plan

- El **hilo principal (orquestador)** entiende la petición, decide si hay que generar un plan, validarlo o resolver una duda conceptual, y activa el workflow o agente correcto. **No diseña la arquitectura**, no escribe código ni genera tasks de implementación.
- La **traducción de Spec + Design a arquitectura** la realiza `plan-architect`; la **auditoría formal** del plan, `plan-auditor`, con sus `kb-*` cargadas en contexto.
- El enrutado no construye prompts a mano: las workflows y los agentes ya contienen el conocimiento operativo; el hilo principal solo activa la pieza correcta con los argumentos correctos.

> **Precondiciones, desambiguación y fronteras de esta fase** (spec validado + handoff de Design como entrada, gate BORRADOR → VALIDADO antes de Tasks, gaps del handoff) viven en la regla **eager** `sdd-routing.md`, para que el hilo principal las tenga al orientar sin tocar ficheros.

## Rootmap de workflow skills

| Intención del usuario | Skill | Argumentos |
|---|---|---|
| Generar el plan técnico desde un spec listo | `/wf-prepare-plan` | `generate <feature_spec.md>` |
| Validar si un `_plan.md` está listo para Tasks | `/wf-plan-validate` | `<feature_plan.md>` |

> El rootmap de arriba es referencia. El enrutado intención→skill efectivo lo hacen las `description` de los skills (eager); esta tabla documenta argumentos y agrupa por intención.

## Camino canónico

```
spec validado
  -> wf-design-system / wf-design-feature-prototype   (si la feature tiene UI)
  -> wf-prepare-plan                                  (genera _plan.md en BORRADOR)
  -> wf-plan-validate                                 (gate formal)
  -> wf-prepare-tasks                                 (solo con plan VALIDADO)
```

## Agentes Plan disponibles

| Agente | Dominio |
|---|---|
| `plan-architect` | Traducción de Spec + Design a arquitectura técnica. Genera `_plan.md` en estado `BORRADOR`. |
| `plan-auditor` | Auditoría formal del `_plan.md` contra Spec, Design y `kb-plan-expert`. Certifica `VALIDADO` o devuelve hallazgos. |

> El overlay de stack (p. ej. KMM) puede sustituir `plan-architect` y `plan-auditor` por variantes especializadas con el mismo nombre, que añaden las KBs de arquitectura del stack. En modo genérico (stack agnóstico) operan fundamentando las decisiones en la exploración real del repositorio.

Se usan workflows cuando exista una pipeline clara y cerrada. Si la petición no requiere una workflow exacta pero sí ayuda experta para estructurar la fase `plan` (duda conceptual sobre qué debe contener el Plan o cómo resolver ownership técnico), el hilo principal delega a `plan-architect`.

## Skills de conocimiento Plan

Las `kb-*` viven en el frontmatter `skills: [...]` de los agentes de la fase; el harness las inyecta en el contexto del subagente. El hilo principal no las consulta ni necesita su inventario: vive en `sdd/meta/skill-registry.md` (mapa humano: el `README.md` de la fase). El overlay de stack (`wf-<stack>-init`) sustituye y amplía las KBs genéricas por variantes especializadas con el mismo mecanismo — en modo agnóstico no está presente.
