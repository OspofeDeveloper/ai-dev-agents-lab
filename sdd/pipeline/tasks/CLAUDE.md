# Tasks Lab — Guía de la fase Tasks

Este directorio define un paquete focalizado en la etapa de **Tasks** dentro del pipeline SDD: transformación de un `_plan.md` validado en un `_tasks.md` con tasks atómicas, ordenadas y asignadas a su owner (agentes del overlay de stack, u orquestador en modo genérico).

> **Audiencia.** El **hilo principal (orquestador)** enruta la petición del usuario al workflow o agente correcto — el enrutado efectivo lo hacen las `description` de los skills (eager) y la regla eager `sdd-routing.md`. Un **subagente especialista** (p. ej. `task-generator`) también carga esta guía al tocar artefactos de Tasks: para él es **contexto de fase**, no una instrucción de rol — su contrato de trabajo es su propio system prompt + sus `kb-*`.

> **Precondiciones, desambiguación y fronteras de esta fase** (plan VALIDADO como entrada, las tres vías de ejecución task-run/bug/amend, integridad de estados, fronteras de QA y release) viven en la regla **eager** `sdd-routing.md`, para que el hilo principal las tenga al orientar sin tocar ficheros.

## Camino canónico

```
plan validado (_plan.md con Estado: VALIDADO)
  -> wf-prepare-tasks generate <plan.md>
  -> _tasks.md con tasks ordenadas por dominio de ejecución (Estado: PENDIENTE)
  -> wf-task-run <tasks.md>            (una task elegible por invocación; --all para lote)
       estado persistente vía .sdd/scripts/sdd-task-state.py (transiciones validadas)
       commit por task: "T-00X: <título> [CA-XXX]"
  -> ... repetir hasta COMPLETO
  -> wf-qa-verify <qa_plan.md>         (cobertura real de CAs con evidencia → _qa_report.md)
  -> wf-release <feature_dir> [--tag]  (QA APTO → registra SHA/tag en <feature>_release.md)
  -> mantenimiento posterior: wf-bug (registro B-00X en <feature>_bugs.md)
```

El `wf-release` es el último eslabón hacia producción: solo lo acepta una feature con QA `APTO`/`APTO_CON_RESERVAS` (gate en `sdd-release.py`), captura el commit SHA con git (no se teclea) y, opcionalmente, registra/crea un tag. La coordenada queda en `<feature>_release.md` y `wf-project-status` la muestra en la fila de la feature cerrada. Re-releases (hotfix tras bug) se acumulan `R-001`, `R-002`…

El QA plan (`wf-qa-plan generate <spec.md>`) puede generarse en cualquier momento desde que el spec está fiable — antes o en paralelo a la implementación; lo natural es derivarlo pronto para que las tasks de test sepan qué cubrir. `wf-qa-verify` cierra el ciclo cuando la feature está implementada.

## Skills de conocimiento Tasks

Las `kb-*` viven en el frontmatter `skills: [...]` de los agentes de la fase; el harness las inyecta en el contexto del subagente. El hilo principal no las consulta ni necesita su inventario: vive en `sdd/meta/skill-registry.md` (mapa humano: el `README.md` de la fase). El overlay de stack (`wf-<stack>-init`) puede sustituir `task-generator` por una variante especializada con el mismo mecanismo.
