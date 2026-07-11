# Plan Lab — Guía de la fase Plan

Este directorio define un paquete focalizado en la etapa de **Plan** dentro del pipeline SDD: traducción de un `*_spec.md` validado y su handoff de Design a un `_plan.md` técnico (especializado por el overlay de stack si existe; genérico si el stack es agnóstico), seguido de una validación formal antes de pasar a Tasks.

> **Audiencia.** El **hilo principal (orquestador)** enruta la petición del usuario al workflow o agente correcto — el enrutado efectivo lo hacen las `description` de los skills (eager) y la regla eager `sdd-routing.md`. Un **subagente especialista** (p. ej. `plan-architect`) también carga esta guía al tocar artefactos de Plan: para él es **contexto de fase**, no una instrucción de rol — su contrato de trabajo es su propio system prompt + sus `kb-*`.

> **Precondiciones, desambiguación y fronteras de esta fase** (spec validado + handoff de Design como entrada, gate BORRADOR → VALIDADO antes de Tasks, gaps del handoff) viven en la regla **eager** `sdd-routing.md`, para que el hilo principal las tenga al orientar sin tocar ficheros.

## Camino canónico

```
spec validado
  -> wf-design-system / wf-design-feature-prototype   (si la feature tiene UI)
  -> wf-prepare-plan                                  (genera _plan.md en BORRADOR)
  -> wf-plan-validate                                 (gate formal)
  -> wf-prepare-tasks                                 (solo con plan VALIDADO)
```

## Skills de conocimiento Plan

Las `kb-*` viven en el frontmatter `skills: [...]` de los agentes de la fase; el harness las inyecta en el contexto del subagente. El hilo principal no las consulta ni necesita su inventario: vive en `sdd/meta/skill-registry.md` (mapa humano: el `README.md` de la fase). El overlay de stack (`wf-<stack>-init`) sustituye y amplía las KBs genéricas por variantes especializadas con el mismo mecanismo — en modo agnóstico no está presente.
