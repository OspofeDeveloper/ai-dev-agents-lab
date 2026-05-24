---
name: kb-traceability-rules
description: Reglas de trazabilidad entre PRD, discovery, specs, plan y tasks en el ecosistema SDD. Define metadata mínima, estados de sincronización y criterios para detectar deriva entre artefactos. Úsalo cuando haya que decidir si un spec o plan está alineado con la versión actual del PRD o cuando se diseñen workflows de sync y change management.
argument-hint: "[artefacto | tema_a_consultar]"
effort: medium
allowed-tools: [Read]
disable-model-invocation: true
context: fork
---

# Traceability Rules para SDD

Estas reglas definen cómo saber si un artefacto derivado sigue alineado con la verdad de negocio actual.

## Regla 1: Todo derivado debe declarar de qué versión nace

Los artefactos derivados deberían incluir metadata equivalente a:

```yaml
derived_from_prd: prd/PRD.md
derived_from_prd_version: "1.2"
derived_from_change: "CR-007"
status_sync: in_sync
```

No es obligatorio reescribir retrospectivamente todos los artefactos existentes, pero los workflows nuevos deben empezar a producir o actualizar esta trazabilidad.

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
