---
name: kb-traceability-rules
description: Reglas de trazabilidad entre PRD, discovery, specs, plan y tasks en el ecosistema SDD. Define metadata mínima, estados de sincronización y criterios para detectar deriva entre artefactos derivados y la versión actual del PRD.
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Traceability Rules para SDD

Estas reglas definen cómo saber si un artefacto derivado sigue alineado con la verdad de negocio actual.

## Regla 1: Todo derivado debe declarar de qué versión nace

Los artefactos derivados deberían incluir metadata equivalente a:

```yaml
derived_from_prd: prd/PRD.md
derived_from_prd_version: "1.2"
derived_from_prd_hash: sha256:21f2f49dcdaeaa23
derived_from_change: "CR-007"
status_sync: in_sync
```

No es obligatorio reescribir retrospectivamente todos los artefactos existentes, pero los workflows nuevos deben empezar a producir o actualizar esta trazabilidad.

### Campo verificable: `derived_from_prd_hash`

Los campos anteriores son **declarativos** (los escribe el workflow y pueden mentir si el PRD se edita fuera de `wf-prd-change`). `derived_from_prd_hash` es la parte **verificable**: el sha256 del contenido del PRD en el momento de generar/sincronizar el spec.

- **Único escritor**: `sdd-sync-check.py seal` (separación autor/verificador, mismo principio que el sellador de planes). Ningún agente lo rellena ni edita a mano.
- **Consumidores**: `sdd-gate-check.py` (deniega `wf-prepare-plan`/`wf-design-*` si el PRD actual ya no coincide), `sdd-seal.py` (un plan no se sella contra un spec con deriva) y `wf-prd-sync-impact`/`wf-spec-sync-from-prd` (pre-pass `check-all`).
- **Semántica de deriva**: un mismatch significa que el PRD cambió, no que ESTE spec esté necesariamente afectado — por eso la marca automática es `needs_review` (no `stale`); el análisis de impacto decide por feature (Regla 4).
- **Ausencia de sello** (`N/A` o campo inexistente, specs legacy): no bloquea — aplica la Regla 3.

## Regla 2: Estados de sincronización permitidos

- `in_sync`: el artefacto fue generado o revisado contra la versión vigente del PRD
- `needs_review`: hay un cambio upstream que podría afectarle
- `stale`: se sabe que el artefacto quedó desactualizado
- `unknown`: no hay metadata suficiente para concluirlo

## Regla 3: La falta de metadata no implica sincronía

Si un artefacto no declara su versión de origen y existe evidencia de cambios posteriores del PRD, el estado conservador es `unknown` o `needs_review`, nunca `in_sync` por defecto.

## Regla 4: Criterios para considerar un spec afectado

Un feature spec debe revisarse si el cambio del PRD:

- toca su scope funcional
- modifica una regla transversal que sus HUs usan
- añade o quita restricciones de actor
- mueve una exclusión a MVP o la saca del MVP
- altera shared models que el spec referencia

## Regla 5: Criterios para considerar un plan afectado

Un plan debe revisarse si cambia el spec del que deriva o si el PRD añade restricciones funcionales que puedan alterar:

- ownership de módulos
- contratos inter-feature
- shared models
- flujos y casos de uso relevantes

## Regla 6: Criterios para considerar tasks afectadas

Una task queda afectada si:

- su plan padre cambia
- el CA del que deriva cambia
- su Definition of Done deja de cubrir el comportamiento vigente

## Regla 7: Sync incremental por defecto

No todo cambio exige regeneración total.

- si afecta a una feature concreta, prioriza delta o sync de esa feature
- si afecta shared models o reglas transversales, evalúa múltiples features
- si afecta discovery/ownership, reevalúa `_discovery.md` y `_features.md`

## Regla 8: Bloqueos recomendados

Debe bloquearse el avance a Plan cuando:

- el spec tiene HUs `[INCOMPLETO]`
- el spec está `stale`
- el spec está `needs_review` por un `SCOPE_CHANGE` o `BEHAVIOR_CHANGE` sin aplicar

Las tasks deberían bloquearse si el plan está `stale`.

## Regla 9: Enmienda de CA y stale puntual (back-edge tasks→spec)

Cuando una **aclaración** de un CA (la intención no cambia; solo se precisa texto ambiguo — `wf-spec-amend`) se aplica con el plan de la feature ya generado, la deriva resultante es **puntual, no global**: no degrada `status_sync` ni el `Estado:` del plan. Se registra como anotación en el header del plan:

```
> **Enmienda pendiente:** CA-003 (E-002, 2026-06-07)
```

- **Único escritor**: `sdd-amend.py` (`mark`/`clear`) — mismo principio autor≠marcador que el sellador. La numeración `E-00X` también la asigna el script (escaneando plan + changelog del spec), nunca la prosa.
- **Consumidores**: `sdd-gate-check.py` (deniega `wf-task-run --task` sobre tasks cuyo `Spec CA` referencia un CA enmendado, y `wf-prepare-tasks` sobre planes con enmiendas abiertas) y `sdd-task-state.py` (`next` salta las tasks retenidas; `set EN_CURSO` las rechaza salvo `--force`). El resto de tasks de la feature sigue ejecutable — esa es la diferencia con `stale`/`needs_review`, que son por artefacto completo.
- **Cierre**: revisión scoped de las secciones del plan que referencian el CA (`wf-spec-amend` Paso 8 → `clear`), o re-validación completa (`wf-plan-validate` → `sdd-seal.py --seal` absorbe las anotaciones).
- **Trazabilidad en el spec**: la enmienda queda en el changelog (`E-00X: aclaración CA-XXX desde T-00X`) con versión menor.
- Si el cambio NO es una aclaración (el comportamiento esperado cambia), este mecanismo no aplica: es `wf-spec-delta` y rigen las Reglas 5, 6 y 8.

## Regla 10: Atribución de aprobación humana en los gates de sellado (`Aprobado por`)

Los tres gates donde el pipeline sella el avance de fase —`wf-prd-review` (PRD), `wf-plan-validate` (Plan), `wf-qa-verify` (QA)— registran **quién aprobó el gate** en el header del artefacto. Esto da trazabilidad de autoría en proyectos multi-desarrollador. Esta regla es la SSoT del convenio; las KBs de fase (`kb-prd-expert`, `kb-plan-expert`, `kb-qa-expert`) la referencian, no la redefinen.

```
Aprobado por: <nombre> [(<rol>)] (<YYYY-MM-DD>)
```

- **Qué es**: registro del checkpoint humano del gate — **quién** aprobó. El valor prioritario es la **identidad de la persona** (nombre); el rol es **opcional** y complementario (`Oscar Pozo (Product Owner) (2026-06-09)`). Un rol pelado (`PM`) no identifica a nadie en un equipo con varios: por eso el nombre es lo que da la trazabilidad de autoría que persigue esta regla ([[D-027]]).
- **Dato humano, no verificable**: a diferencia del `derived_from_prd_hash` (Regla 1) o del `Estado:` del plan, `Aprobado por` **no es mecánicamente verificable** — ningún script lo escribe ni lo valida. Es el mismo tipo de anotación de header que escribe el orquestador que la `Aprobada por` per-TD de la deuda técnica del plan (`kb-plan-expert`), distinta del sello operativo.
- **Único escritor**: el **orquestador/workflow del gate**, en el momento de aprobar, con la fecha real de su contexto. `sdd-seal.py` y los gates **no lo tocan** (no es verificable). Esto invierte el reparto autor≠sellador de las Reglas 1 y 9: aquí no hay verificador mecánico porque no hay nada mecánico que verificar.
- **Captura de la identidad**: el workflow la pregunta con `AskUserQuestion` **precargando el nombre con `git config user.name`** como default (misma filosofía que capturar el SHA en `sdd-release.py`: no teclear lo que git ya sabe), con el **rol por fase como opcional**. El usuario confirma el nombre, lo cambia o añade rol; si git no da nombre, cae al rol por defecto. **No autoaprobar**: si el usuario no responde, no se escribe la línea.
- **Solo cuando el gate PASA**: se escribe únicamente con resultado positivo del gate. Si el gate no pasa, la línea **no** se escribe.

| Gate | Workflow | Default rol | Se escribe cuando | NO se escribe cuando |
|---|---|---|---|---|
| PRD | `wf-prd-review` | `PM` / `Product Owner` | veredicto `LISTO` | `LISTO_CON_AJUSTES`, `NO_LISTO` |
| Plan | `wf-plan-validate` | `Tech Lead` | `sdd-seal.py --seal` exit 0 (plan `VALIDADO`) | exit 2 (`BORRADOR`) |
| QA | `wf-qa-verify` | `QA` | veredicto `APTO` o `APTO_CON_RESERVAS` | `NO_APTO` |

En re-aprobación (p. ej. re-validación de un plan), se **sobrescribe** con el nuevo rol/fecha. En las plantillas de header el campo nace ausente o como placeholder; no se inventa valor hasta la aprobación.

## Regla 11: Coordenada de release (último eslabón hacia producción)

La trazabilidad funcional encadena `CA → TC → task → commit (T-00X) → veredicto QA`. El **release** cierra la cadena hacia producción: registra **en qué punto verificable se entregó la feature** — el commit SHA y, opcionalmente, un tag. Sin esto, "Cerrada" (QA APTO) es un estado interno que no llega a producción.

```
## R-001 — <YYYY-MM-DD>
- Commit/SHA: <sha completo> (<corto>)
- Tag: <tag o —>
- Veredicto QA: APTO | APTO_CON_RESERVAS
```

- **Dato mecánico (el SHA) + dato declarativo (el tag)**: el SHA lo da `git rev-parse`, no el agente — no puede mentir ni derivar (mismo principio que `derived_from_prd_hash`). El tag lo elige el humano y es opcional; el SHA siempre ancla.
- **Gate de cierre**: una feature no se releasa si su QA no pasó. El stamp se **rechaza** si no hay `_qa_report.md` o el veredicto es `NO_APTO`; `APTO` y `APTO_CON_RESERVAS` se permiten y el veredicto real queda grabado (releasar con reservas se documenta, no se oculta).
- **Único escritor**: `sdd-release.py` (`stamp`), invocado por `wf-release`. El coordinador de release vive en `<feature>_release.md`, junto al `_qa_report.md`. Re-releases (hotfix tras bug) se acumulan como `R-001`, `R-002`… — la feature puede entregarse más de una vez.
- **Consumidor**: `sdd-project-status.py` lee el release y lo muestra en la fila de la feature cerrada; una feature `APTO` sin release aparece como cierre pendiente de release (`/wf-release`).
- **Granularidad por feature**: cada feature se releasa por su cuenta (continuous delivery). El agregado "qué se entregó" lo da `wf-project-status`, no un ledger separado.
- El **tagging/versionado de release** es competencia exclusiva de esta regla y `wf-release`; `kb-delivery-discipline` (empaquetado de commits/PRs) lo excluye y apunta aquí.

## Regla 12: Los IDs de CA y HU son inmutables — tombstone, nunca renumeración

Esta regla es la **SSoT** de la estabilidad de identificadores en la cadena de trazabilidad. Los IDs de CA (`CA-XXX`) y de HU **nunca se reutilizan ni se renumeran**. Son la coordenada estable a la que apuntan las tasks (`Spec CA`, Reglas 6 y 9), los casos de prueba (`TC → CA`), los gates de sellado y los commits (`T-00X [CA-XXX]`, Regla 11). Renumerar para "cerrar huecos" desplaza esos IDs y corrompe silenciosamente toda referencia downstream: una task o un TC pasan a apuntar a un CA distinto del que verificaban.

- **Eliminación = tombstone, no borrado con compactación**: un CA o HU eliminado se marca conservando su número y dejando el hueco en la secuencia:

  ```
  CA-003 [ELIMINADO en v1.4: <razón>]
  ```

  El siguiente CA nuevo toma el **siguiente número libre nunca usado**, no el hueco del tombstone. La secuencia puede tener huecos; eso es correcto y esperado.
- **Consistente con CR-XXX y E-00X**: los cambios de producto (`CR-XXX`, gobernanza de PRD) y las enmiendas (`E-00X`, Regla 9) ya se tratan así — numeración monótona, sin reutilización. Los CA y HU siguen el mismo principio: el identificador es permanente una vez asignado.
- **Renumeración de cara a una nueva feature (decompose)**: cuando una feature spec **nace** renumerando sus CAs desde `CA-001` a partir de un spec monolítico (decomposición inicial, antes de que existan tasks/TCs que apunten a ella), eso **no** viola esta regla: no hay referencias downstream que romper porque la feature aún no las tiene. La inmutabilidad rige desde que el spec entra en el pipeline (existen derivados que lo referencian), no durante su construcción inicial.
- **Único momento en que un CA cambia de texto sin cambiar de ID**: la aclaración quirúrgica de `wf-spec-amend` (Regla 9) sustituye el texto del CA preservando su número. Eso es lo correcto; renumerar sería lo prohibido.
