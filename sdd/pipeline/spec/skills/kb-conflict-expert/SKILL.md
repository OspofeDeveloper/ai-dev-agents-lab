---
name: kb-conflict-expert
description: Experto en detección de conflictos entre Specs SDD de features. Reglas para identificar HUs duplicadas, CAs contradictorios, scope overlaps y shared models inconsistentes entre specs del mismo proyecto.
effort: low
allowed-tools: [Read]
user-invocable: false
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

### La causa de un conflicto de modelo compartido ([[D-111]])

Cada regla de un modelo compartido tiene un dueño: la feature dueña publica su **contrato** (ciclo
de vida, qué puede hacer el actor, invariantes y el catálogo de **orígenes externos**), y las
demás lo citan o le hacen una **petición**. Cuando dos specs chocan sobre un modelo compartido, di
**por qué** —es lo que decide dónde se corrige—, con una de estas causas:

| Causa | Qué pasa | Dónde se corrige |
|---|---|---|
| **Duplica** | el consumidor reescribe una regla del contrato del dueño, y no coinciden | el consumidor: cita el contrato en vez de reescribirlo |
| **Supone** | el consumidor da por hecha una regla que el dueño no dice | el dueño: decide la regla en su contrato |
| **Efecto no catalogado** | una operación del consumidor crea o cambia el modelo y el catálogo de orígenes del dueño no la recoge | el dueño: añade la fila y decide qué se puede hacer con lo que crea |
| **Sin dueño** | cada spec deja la regla a la otra y nadie la tiene | el dueño del modelo, siempre |
| **Decisión** | los dos specs dicen lo que les toca y el choque es de producto | según la decisión, pero una regla del modelo se escribe solo en su dueño |

**Contradicción o hueco: la severidad ([[D-112]]).** Solo **Duplica** (que no coincide) y
**Decisión** son una **contradicción** —dos specs dicen cosas incompatibles—, y solo esas son
**ALTA**. **Supone**, **Efecto no catalogado** y **Sin dueño** son un **hueco**: falta una regla
que alguien tiene que decidir, pero ningún spec dice lo contrario de otro. Un hueco es **MEDIA**: no
bloquea a las features que no lo resuelven, y la lista lo ofrece como decisión de su bloque. Medido
en la pasada 1 de `CU-3.ab`: la mayoría de los *"conflictos graves"* eran huecos —el contrato de
cuentas no decía si el saldo puede quedar negativo; objetivos no repetía una regla de cuentas que le
bastaba con citar— y cada uno frenó como si dos specs se contradijeran.

Escríbela en el informe (campo **Causa** del conflicto). Y en la **Decisión de producto**, el
*Cambia:* de una opción que fija una regla del modelo nombra **al dueño**: si una opción obliga a
cambiar también al consumidor, es porque el consumidor tenía la regla duplicada — y eso se
corrige citando, no volviendo a escribirla.

**Una opción describe un solo comportamiento.** No la expliques comparándola con dos cosas que se
comportan distinto (*"igual que una aportación directa o una transferencia"*, cuando una deja un
movimiento y la otra dos): quien la elige no sabe cuál de las dos ha elegido, y el que la aplica
tampoco. Medido en la pasada 4 de la tanda de continuación: esa opción partió el cambio en dos
lecturas, y cada spec se quedó con una.

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
| Shared models inconsistentes — contradicción | ALTA | Modelo de dominio corrupto |
| Shared models inconsistentes — hueco (falta la regla, nadie la contradice) | MEDIA | Decisión pendiente del dueño; no corrompe nada todavía |
| Scope overlap | MEDIA | Duplicación de trabajo, boundaries difusos |
| Fuera de alcance contradictorio | MEDIA | Gap funcional no cubierto por ninguna feature |

---

## Cómo se citan estas reglas en un informe ([[D-091]])

El informe de conflictos lo lee una persona de producto que decide qué feature manda en cada
choque. Cuando justifiques un veredicto **cita la regla por lo que dice, no por dónde vive**:

| En vez de | Escribe |
|---|---|
| *"Regla 4 de `kb-conflict-expert`"* | *"el mismo modelo con comportamientos distintos en dos CAs de features diferentes"* |
| *"la tabla de severidad de `kb-conflict-expert` da ALTA por defecto"* | *"un shared model inconsistente corrompe el modelo de dominio, y eso es ALTA por defecto"* |

No es una regla de estilo: por [[D-042]] ese texto se le lee **verbatim** a quien decide, y el
nombre de una kb no le dice nada — es un detalle de cómo está construido el sistema que se lo
cuenta. La regla enunciada sostiene el veredicto ella sola; el nombre solo sostiene la
procedencia, y para eso ya está `Generado por:`. Medido tres veces en la pasada de `CU-3.d` del
2026-09-18 (probe V1), las tres con esta forma exacta.

---

## Qué NO es un conflicto

- Dos features que referencian el mismo shared model correctamente (con owner declarado) — eso es el comportamiento esperado de los shared models.
- Un consumidor que **cita** el contrato del dueño (*"según el contrato de Movimiento"*) o que tiene una **petición al dueño** registrada: es la vía correcta. Una petición sin atender no es un conflicto que arbitrar —la lista de pendientes ya la trae como trabajo sobre el dueño—. Tampoco lo es una línea **Estado** dentro de una petición (*"pendiente de que F-001 las integre"*): es de antes de [[D-112]] y no cuenta; si el dueño cita la petición en su fila, está atendida.
- CAs que describen el mismo escenario pero para **actores distintos** con capacidades distintas — son CAs distintos válidos.
- Features que mencionan la misma entidad de dominio con propósitos distintos (ej: Feature A *crea* usuarios, Feature B *lista* usuarios — no es conflicto, es colaboración correcta).
