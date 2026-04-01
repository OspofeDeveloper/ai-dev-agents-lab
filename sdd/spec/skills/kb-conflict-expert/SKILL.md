---
name: kb-conflict-expert
description: Experto en detección de conflictos entre Specs SDD de features. Contiene las reglas para identificar HUs duplicadas, CAs contradictorios, scope overlaps y shared models inconsistentes. Úsalo cuando necesites verificar que un spec nuevo o modificado no entra en conflicto con specs existentes en el mismo proyecto.
allowed-tools: [Read]
disable-model-invocation: true
context: fork
---

# Conflict Expert — Reglas de Detección de Conflictos entre Specs SDD

Estas reglas aplican cuando se compara un conjunto de Specs SDD (`_spec.md`) que pertenecen al mismo proyecto para detectar inconsistencias que podrían indicar solapamiento de scope, requisitos contradictorios o modelos mal definidos.

---

## Regla 1: HUs duplicadas

**Definición**: Dos HUs en features distintas describen la misma acción para el mismo actor.

**Criterio de detección**: Coincidencia de los tres componentes:
- Mismo actor (o rol equivalente — ej: "trabajadora" y "cuidadora" en el mismo sistema son el mismo actor)
- Mismo verbo de acción principal (registrar, consultar, editar, confirmar, etc.)
- Mismo objetivo funcional (para qué sirve la acción)

**Cómo reportar**: Cita ambas HUs con sus IDs, features de origen y la coincidencia exacta detectada.

**No es duplicado si**: Los dos verbos son distintos aunque el objetivo sea similar (ej: "visualizar" vs. "exportar" un informe), o el actor tiene capacidades estructuralmente diferentes en cada feature.

---

## Regla 2: CAs contradictorios

**Definición**: Dos CAs en features distintas que, dado el mismo GIVEN y el mismo WHEN, describen THENs incompatibles o mutuamente excluyentes.

**Criterio de detección**:
- GIVEN equivalente (misma precondición del sistema o del usuario)
- WHEN equivalente (misma acción desencadenante)
- THEN incompatible (resultados que no pueden ser verdaderos simultáneamente — ej: "el sistema muestra un error" vs. "el sistema confirma la operación" para la misma acción en el mismo estado)

**Cómo reportar**: Cita los dos CAs completos con sus IDs y features de origen. Explica por qué los THENs son incompatibles.

**No es contradicción si**: Los GIVEN son distintos (precondiciones diferentes producen resultados diferentes es comportamiento normal).

---

## Regla 3: Scope overlap

**Definición**: Una feature incluye Journeys o funcionalidad que, por cohesión funcional, pertenecen a otra feature ya definida.

**Criterio de detección** (consulta también `kb-decompose-expert`):
- Un Journey en la feature A incluye pasos que son el objetivo principal de otra feature B
- Una feature "toma prestado" un flujo completo de otra en lugar de referenciarla como dependencia

**Cómo reportar**: Describe el solapamiento con citas de los Journeys afectados. Sugiere qué feature debería ser la propietaria de ese scope.

**No es overlap si**: El Journey de A *termina* en el punto de entrada a B (es una dependencia, no un solapamiento).

---

## Regla 4: Shared models inconsistentes

**Definición**: Un modelo de dominio aparece en dos o más features con atributos, comportamientos o semántica incompatibles, o aparece en una feature nueva sin estar declarado en el `_features.md`.

**Criterio de detección**:
- Mismo nombre de modelo → atributos definidos de forma diferente en dos features
- Mismo nombre de modelo → comportamientos distintos en dos CAs de features diferentes (ej: el modelo puede estar en estado X en una feature pero ese estado no existe en la otra)
- Modelo referenciado en un spec pero no declarado como "shared" en `_features.md`

**Cómo reportar**: Cita el modelo, las features que lo referencian y la inconsistencia específica detectada.

---

## Regla 5: Fuera de alcance contradictorio

**Definición**: Una feature declara algo como fuera de su alcance que otra feature asume incluido en su propio alcance.

**Criterio de detección**:
- La sección "Fuera de Alcance" de la feature A menciona explícitamente algo que la feature B incluye en sus HUs o Journeys
- Una feature asume que otra gestiona algo, pero esa "otra feature" lo tiene explícitamente en su "Fuera de Alcance"

**Cómo reportar**: Cita la declaración de fuera de alcance y la HU/Journey que la contradice. Indica cuál de las dos debería tener razón.

---

## Severidad de los conflictos

| Tipo | Severidad | Impacto |
|------|-----------|---------|
| CAs contradictorios | ALTA | Comportamiento indefinido en producción |
| HUs duplicadas | ALTA | Implementación doble, inconsistencia de datos |
| Shared models inconsistentes | ALTA | Modelo de dominio corrupto |
| Scope overlap | MEDIA | Duplicación de trabajo, boundaries difusos |
| Fuera de alcance contradictorio | MEDIA | Gap funcional no cubierto por ninguna feature |

---

## Qué NO es un conflicto

- Dos features que referencian el mismo shared model correctamente (con owner declarado) — eso es el comportamiento esperado de los shared models.
- CAs que describen el mismo escenario pero para **actores distintos** con capacidades distintas — son CAs distintos válidos.
- Features que mencionan la misma entidad de dominio con propósitos distintos (ej: Feature A *crea* usuarios, Feature B *lista* usuarios — no es conflicto, es colaboración correcta).
