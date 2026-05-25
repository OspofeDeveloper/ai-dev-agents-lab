# SDD Meta-Orquestador

Este directorio contiene la SSoT transversal para diseñar y evolucionar el ecosistema `sdd/`.

## Cuándo consultar este contexto

Consulta `kb-sdd-skill-architecture` cuando haya que:

- crear una nueva `kb-*`
- crear una nueva `wf-*`
- crear o refactorizar un agente
- decidir si una regla vive en `CLAUDE.md`, en una `kb-*`, en una `wf-*` o en un agente
- revisar si una documentación de fase está duplicando reglas globales

## Regla de reparto

- Las reglas transversales de arquitectura de skills y agentes viven en `kb-sdd-skill-architecture`.
- Los `CLAUDE.md` de fase viven para routing, handoffs y entrypoints operativos.
- Los `README.md` de fase viven para mapa humano de la fase, artefactos y ejemplos de uso.

Si una regla aplica a varias fases de `sdd/`, no debe definirse otra vez en `prd/`, `spec/` o `design/`. Se delega a `kb-sdd-skill-architecture`.
