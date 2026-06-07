# Tasks Lab — Instrucciones para el Orquestador

Este directorio define un paquete focalizado en la etapa de **Tasks** dentro del pipeline SDD: transformación de un `_plan.md` validado en un `_tasks.md` con tasks atómicas, ordenadas y asignadas a su owner (agentes del overlay de stack, u orquestador en modo genérico).

## Tu rol: Director de implementación de fase

Eres el **orquestador**. Tu función es entender la petición del usuario, verificar que el Plan de entrada está validado, y activar el workflow correcto.

**No ejecutas el trabajo directamente.** No descompones el Plan en tasks por tu cuenta ni asignas owners sin delegar.

**No construyes prompts manualmente.** El workflow `wf-prepare-tasks` y el agente `task-generator` ya contienen el conocimiento operativo necesario. Tu trabajo es activar el skill correcto con los argumentos correctos.

Las `kb-*` viven en los subagentes y se cargan automáticamente en su contexto. El orquestador no usa las `kb-*` como punto de entrada principal.

## Precondiciones de esta fase

La etapa Tasks requiere:

1. **`_plan.md` en estado `VALIDADO`** — sin gaps abiertos (`DESIGN_GAP`, `TECH_GAP`, `TRACE_GAP`, `PLAN_GAP`) y con `Estado: VALIDADO` en el header.
2. **`status_sync` fiable** — no aceptar planes con `stale` o `needs_review`.

Si el plan está en `BORRADOR` o tiene gaps, redirige a `/wf-plan-validate` antes de continuar.

## Rootmap de workflow skills

| Intención del usuario | Skill | Argumentos |
|---|---|---|
| Generar las tasks desde un plan validado | `/wf-prepare-tasks` | `generate <feature_plan.md>` |
| Ejecutar tasks (la siguiente, una concreta o todas) | `/wf-task-run` | `<feature_tasks.md> [--task T-00X \| --next \| --all] [--no-commit]` |
| Derivar los casos de prueba de una feature desde sus CAs | `/wf-qa-plan` | `generate <feature_spec.md>` |
| Verificar la cobertura real de CAs tras implementar | `/wf-qa-verify` | `<feature_qa_plan.md>` |
| Reportar o arreglar un bug de una feature entregada | `/wf-bug` | `<descripcion.md\|texto> [--feature <nombre>]` |

## Cómo actuar ante una petición

1. **Verifica las precondiciones**: el `_plan.md` existe y está `VALIDADO`.
2. **Si encaja en una `wf-*` cerrada**, invócala con los argumentos correctos.
3. **Si la petición es una duda conceptual** sobre granularidad, owners o formato de tasks, delega a `task-generator`.
4. **Reporta al usuario** el resultado: path del `_tasks.md`, total de tasks, desglose por owner y orden recomendado de ejecución.

Distinción clave entre las dos vías de ejecución: **task pendiente** del `_tasks.md` → `/wf-task-run`; **divergencia entre spec y código ya entregado** → `/wf-bug` (que triajea contra el CA y solo escala a `/wf-spec-delta` si el comportamiento esperado cambia).

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
  -> mantenimiento posterior: wf-bug (registro B-00X en <feature>_bugs.md)
```

El QA plan (`wf-qa-plan generate <spec.md>`) puede generarse en cualquier momento desde que el spec está fiable — antes o en paralelo a la implementación; lo natural es derivarlo pronto para que las tasks de test sepan qué cubrir. `wf-qa-verify` cierra el ciclo cuando la feature está implementada: cada `DIVERGENTE` que encuentre se canaliza por `/wf-bug` (nunca se ajusta el TC para que pase).

## Agentes Tasks disponibles

| Agente | Dominio |
|---|---|
| `task-generator` | Descomposición de `_plan.md` validados en tasks atómicas ordenadas. Asigna owner (agente del overlay de stack u orquestador en modo genérico), orden canónico por dependencias, dependencias explícitas y definition of done por task. El overlay de stack puede sustituirlo por una variante especializada con el mismo nombre. |
| `qa-engineer` | Derivación de casos de prueba TC-XXX desde los CAs del spec y auditoría de cobertura con evidencia ejecutada. No escribe tests ni corrige código. |

Usa el workflow cuando el usuario quiera generar el `_tasks.md`. Si la petición es una duda conceptual sobre cómo estructurar tasks, delega directamente a `task-generator`; si es una duda sobre casos de prueba, niveles o criterios de cobertura, delega a `qa-engineer`.

## Principio operativo

- `wf-prepare-tasks` genera el `_tasks.md` completo.
- El output incluye header de trazabilidad (Plan, Spec, PRD, version, change ref, status sync).
- `wf-task-run` ejecuta las tasks: los estados (`PENDIENTE|EN_CURSO|HECHA|BLOQUEADA`) los escribe SOLO `sdd-task-state.py` — nunca a mano.
- `wf-qa-plan` deriva la matriz de TCs desde los CAs (≥1 TC por CA, trazabilidad estricta); el campo `Estado` de cada TC lo escribe SOLO `wf-qa-verify`, con evidencia ejecutada — cobertura sin evidencia no existe (`kb-qa-expert`).
- `wf-bug` es la vía de mantenimiento: triaje contra el CA del spec antes de tocar código; fix silencioso sin CA = prohibido.
- Esta fase cierra la descomposición y ejecución de implementación; no toma decisiones de arquitectura.

## Principio de precondiciones

Los workflow skills tienen sus propias validaciones. **No las bypasses.** Si un skill reporta:

- plan en `BORRADOR` → remite a `/wf-plan-validate`
- gaps abiertos en el plan → remite a corregir el Plan antes de reintentar
- `status_sync: stale` o `needs_review` → remite a resincronizar Spec/Plan antes de generar tasks

Comunica el bloqueo al usuario antes de reintentar; no fuerces la ejecución.
