---
name: kb-product-change-governance
description: Reglas de gobernanza para cambios de producto en el ecosistema SDD. Define cuándo un cambio debe modificar el PRD, cómo clasificarlo, qué trazabilidad mínima exige y cómo determinar qué artefactos derivados quedan afectados. Úsalo cuando el usuario quiera cambiar alcance, mover una capacidad entre MVP y fase futura, ajustar prioridades de roadmap, o decidir si basta con responder un gap o hay que abrir un change request.
argument-hint: "[change_request | tema_a_consultar]"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Product Change Governance para SDD

Define cómo evoluciona el producto una vez que ya existen artefactos SDD derivados. Su objetivo es evitar dos fallos frecuentes:

- tratar un cambio de scope como si fuera solo una respuesta a un gap
- modificar specs, planes o tasks sin actualizar antes la verdad de negocio

## Regla 1: El PRD sigue siendo la fuente de verdad de negocio

El PRD puede estabilizarse temporalmente durante una ejecución del pipeline, pero no se convierte en un fósil. Si el producto cambia, el PRD debe reflejarlo.

- El `_analysis.md` sirve para preguntas abiertas y preparación de specs.
- Los `*_spec.md` describen comportamiento funcional derivado.
- El PRD es el lugar donde vive la decisión de negocio vigente.

## Regla 2: Clasificar el tipo de cambio antes de tocar nada

Todo cambio debe clasificarse antes de decidir el workflow.

- `CLARIFICATION`: aclara una ambigüedad sin cambiar alcance ni prioridad comprometida.
- `BEHAVIOR_CHANGE`: cambia una regla funcional o comportamiento esperado.
- `SCOPE_CHANGE`: mueve algo entre dentro/fuera de alcance, MVP/fase futura, o añade/elimina capacidad.
- `PRIORITY_CHANGE`: no cambia la funcionalidad, pero sí su orden o fase de entrega.
- `DEPRECATION`: una capacidad deja de ser vigente.

Si un cambio entra en dos categorías, prima la de mayor impacto:
`SCOPE_CHANGE` > `BEHAVIOR_CHANGE` > `CLARIFICATION`.

## Regla 3: Cuándo basta con `_analysis.md`

Una respuesta puede quedarse en `_analysis.md` solo si cumple todas:

- no contradice el PRD vigente
- no mueve alcance entre MVP y fase futura
- no invalida exclusiones explícitas
- no cambia el roadmap comprometido

Si falla cualquiera, no es solo un gap: es un change request.

## Regla 4: Cuándo hay que modificar el PRD

Debe modificarse el PRD cuando el cambio:

- altera la sección "Dentro del alcance" o "Fuera del alcance"
- cambia prioridades o fases comprometidas
- modifica reglas de negocio transversales
- redefine quién puede hacer qué
- haría que una frase actual del PRD fuese falsa o engañosa

## Regla 4.1: Prueba de expansión de capacidad

Una respuesta a un gap deja de ser simple aclaración y pasa a requerir evaluación como change request cuando introduce alguna de estas expansiones:

- un modelo persistente nuevo no comprometido explícitamente en el PRD
- un catálogo reutilizable donde antes solo había una referencia implícita o texto libre
- una nueva operación de usuario o flujo de gestión no descrito en el alcance vigente
- una nueva granularidad funcional de una capacidad existente
- una nueva superficie funcional necesaria para soportar la respuesta
- un nuevo modelo owner de feature o una entidad antes implícita que pasa a tener gestión explícita

Ejemplos típicos:

- el PRD habla de "otras personas" y la respuesta introduce un **catálogo persistente de contactos**
- el PRD habla de presupuesto por categoría y la respuesta introduce **presupuesto por subcategoría**
- el PRD permite editar una transacción y la respuesta añade un **flujo inline de edición coordinada** sobre entidades vinculadas
- el PRD menciona una referencia implícita y la respuesta crea un **modelo owner nuevo** con CRUD o lifecycle propio

La pregunta operativa no es "¿contradice una frase literal?" sino:

- ¿esta respuesta añade capacidad gestionable nueva?
- ¿obliga a redefinir el alcance funcional comprometido?

Si la respuesta es sí, clasifícalo al menos como `BEHAVIOR_CHANGE`; si además amplía alcance o superficie funcional, `SCOPE_CHANGE`.

## Regla 5: Trazabilidad mínima de un cambio

Todo cambio aprobado debe dejar:

- identificador único de cambio (`CR-XXX`)
- fecha
- decisión aprobada
- tipo de cambio
- motivo
- secciones del PRD afectadas
- artefactos derivados posiblemente afectados

Los artefactos mínimos recomendados son:

- `product-changelog.md` como índice global del PRD
- `changes/CR-XXX/change-request.md` como informe del cambio y su impacto
- `changes/CR-XXX/decision.md` como registro estable de la decisión aprobada

La intención es separar responsabilidades:

- `product-changelog.md` resume el historial del producto
- `change-request.md` explica el diff funcional y el impacto sobre derivados
- `decision.md` conserva la decisión aprobada como referencia auditable

## Regla 6: Editar el PRD no basta

Después de un cambio aprobado no se asume que todo queda en sync.

Hay que evaluar impacto sobre:

- `*_analysis.md`
- `*_discovery.md`
- `*_features.md`
- `features/*_spec.md`
- `*_plan.md`
- `*_tasks.md`

El PRD se actualiza primero. La resincronización de derivados va después.

## Regla 7: Heurística operativa

Usa esta secuencia:

1. ¿Cambia el producto que se prometió?  
   Si sí, modifica PRD.
1.1. ¿La respuesta añade una capacidad, entidad o flujo que el PRD no comprometía explícitamente?
   Si sí, trátalo como change request aunque no contradiga una frase literal.
2. ¿Afecta a una o varias features ya derivadas?  
   Si sí, genera análisis de impacto.
3. ¿Es una aclaración menor que no cambia alcance?  
   Si sí, puede resolverse en `_analysis.md` y spec.

## Regla 8: Workflows correctos

- Cambio de producto: `wf-prd-change`
- Medir impacto PRD → derivados: `wf-prd-sync-impact`
- Resincronizar specs desde PRD: `wf-spec-sync-from-prd`
- Completar HUs incompletas por gaps ya detectados: `wf-spec-gap-resolve`
- Cambio funcional incremental sobre un spec ya consolidado: `wf-spec-delta`
