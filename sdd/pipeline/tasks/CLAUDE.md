# Tasks Lab — Guía de la fase Tasks

Este directorio define un paquete focalizado en la etapa de **Tasks** dentro del pipeline SDD: transformación de un `_plan.md` validado en un `_tasks.md` con tasks atómicas, ordenadas y asignadas a su owner (agentes del overlay de stack, u orquestador en modo genérico).

> **Audiencia.** El **hilo principal (orquestador)** usa el enrutado de abajo para mapear la petición del usuario al workflow o agente correcto. Un **subagente especialista** (p. ej. `task-generator`) también carga esta guía al tocar artefactos de Tasks: para él es **contexto de fase**, no una instrucción de rol — su contrato de trabajo es su propio system prompt + sus `kb-*`.

## Reparto de trabajo en la fase Tasks

- El **hilo principal (orquestador)** entiende la petición, verifica que el Plan de entrada está validado, y activa el workflow correcto. **No descompone el Plan en tasks** por su cuenta ni asigna owners sin delegar.
- La **descomposición** del plan la realiza `task-generator`; la **derivación y verificación de QA** (casos de prueba desde CAs, cobertura con evidencia), `qa-engineer`, con sus `kb-*` cargadas en contexto.
- El enrutado no construye prompts a mano: las workflows y los agentes ya contienen el conocimiento operativo; el hilo principal solo activa la pieza correcta con los argumentos correctos.

> **Precondiciones, desambiguación y fronteras de esta fase** (plan VALIDADO como entrada, las tres vías de ejecución task-run/bug/amend, integridad de estados, fronteras de QA y release) viven en la regla **eager** `sdd-routing.md`, para que el hilo principal las tenga al orientar sin tocar ficheros.

## Rootmap de workflow skills

| Intención del usuario | Skill | Argumentos |
|---|---|---|
| Generar las tasks desde un plan validado | `/wf-prepare-tasks` | `generate <feature_plan.md>` |
| Ejecutar tasks (la siguiente, una concreta o todas) | `/wf-task-run` | `<feature_tasks.md> [--task T-00X \| --next \| --all] [--no-commit]` |
| Derivar los casos de prueba de una feature desde sus CAs | `/wf-qa-plan` | `generate <feature_spec.md>` |
| Verificar la cobertura real de CAs tras implementar | `/wf-qa-verify` | `<feature_qa_plan.md>` |
| Reportar o arreglar un bug de una feature entregada | `/wf-bug` | `<descripcion.md\|texto> [--feature <nombre>]` |
| Vincular el cierre de una feature (QA APTO) a un commit SHA / tag de release | `/wf-release` | `<feature_dir\|tasks_path> [--tag <tag>] [--no-tag] [--note <texto>]` |
| Ver el estado de delivery del proyecto (qué fase y qué falta por feature) | `/wf-project-status` | `[<raíz_artefactos_spec>] [--output <path>]` |

> El rootmap de arriba es referencia. El enrutado intención→skill efectivo lo hacen las `description` de los skills (eager); esta tabla documenta argumentos y agrupa por intención.

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

## Agentes Tasks disponibles

| Agente | Dominio |
|---|---|
| `task-generator` | Descomposición de `_plan.md` validados en tasks atómicas ordenadas. Asigna owner (agente del overlay de stack u orquestador en modo genérico), orden canónico por dependencias, dependencias explícitas y definition of done por task. El overlay de stack puede sustituirlo por una variante especializada con el mismo nombre. |
| `qa-engineer` | Derivación de casos de prueba TC-XXX desde los CAs del spec y auditoría de cobertura con evidencia ejecutada. No escribe tests ni corrige código. |

Se usa el workflow cuando el usuario quiera generar el `_tasks.md`. Si la petición es una duda conceptual sobre cómo estructurar tasks, el hilo principal delega a `task-generator`; si es una duda sobre casos de prueba, niveles o criterios de cobertura, a `qa-engineer`.

## Skills de conocimiento Tasks

Las `kb-*` viven en el frontmatter `skills: [...]` de los agentes de la fase; el harness las inyecta en el contexto del subagente. El hilo principal no las consulta ni necesita su inventario: vive en `sdd/meta/skill-registry.md` (mapa humano: el `README.md` de la fase). El overlay de stack (`wf-<stack>-init`) puede sustituir `task-generator` por una variante especializada con el mismo mecanismo.
