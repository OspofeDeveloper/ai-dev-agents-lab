---
name: kb-traceability-rules
description: Reglas de trazabilidad entre PRD, discovery, specs, plan y tasks en el ecosistema SDD. Define metadata mínima, estados de sincronización y criterios para detectar deriva entre artefactos. Úsalo cuando haya que decidir si un spec o plan está alineado con la versión actual del PRD o cuando se diseñen workflows de sync y change management.
argument-hint: "[artefacto | tema_a_consultar]"
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
