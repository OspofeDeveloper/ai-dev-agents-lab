---
name: kb-gap-conventions
description: Convenciones SSoT para el sistema de gaps y marcadores del pipeline SDD. Define formatos de ID, severidades, marcador de pendiente y reglas de bloqueo. Consultar en todos los modos del agente que generen, formateen o verifiquen gaps.
allowed-tools: []
disable-model-invocation: true
context: fork
---

# Gap Conventions — SSoT de Gaps y Marcadores SDD

Este skill es el **Single Source of Truth** para todas las convenciones de gaps en el pipeline SDD. Consúltalo antes de generar, formatear o verificar cualquier gap en cualquier modo.

---

## Formatos de ID de gap

| Contexto | Prefijo | Ejemplo |
|----------|---------|---------|
| Análisis de documento origen (modos `analyze`, `fast-track`) | `[P-XXX]` | `[P-001]`, `[P-042]` |
| Análisis de cambios incrementales (modo `delta`) | `[D-XXX]` | `[D-001]`, `[D-003]` |

**Numeración**: secuencial desde `001`, sin saltos, reiniciando en cada artefacto nuevo.

---

## Severidades

### Marcador advisory opcional: `[PUEDE_REQUERIR_CR]`

Se puede añadir como marcador complementario a un gap cuando la propia pregunta o una futura respuesta tienen alta probabilidad de convertirse en change request de producto.

Formato:

- `[P-001][CRÍTICO][PUEDE_REQUERIR_CR]`
- `[P-002][INFORMATIVO][PUEDE_REQUERIR_CR]`

Uso:

- no cambia por sí solo la severidad del gap
- no bloquea automáticamente el pipeline
- obliga al agente y al usuario a reevaluar la respuesta con `kb-product-change-governance` antes de derivar discovery/specs si la respuesta introduce expansión de capacidad

Casos típicos:

- la respuesta puede introducir un catálogo persistente nuevo
- la respuesta puede añadir una nueva granularidad funcional
- la respuesta puede crear un flujo de usuario no comprometido en el PRD
- la respuesta puede convertir una referencia implícita en una capacidad gestionable explícita

### `[CRÍTICO]`

Marca las HUs afectadas como `[INCOMPLETO]` en el spec si no se responde. El spec se genera igualmente, pero las HUs incompletas no pueden avanzar a plan/tasks. Aplica cuando el gap impide:
- Definir un CA verificable (GIVEN/WHEN/THEN completo e inequívoco)
- Identificar el actor principal de un Journey
- Determinar el estado de éxito de un Journey
- Resolver una regla de negocio con interpretaciones funcionales incompatibles entre sí

Formato completo: `[P-001][CRÍTICO]` o `[D-001][CRÍTICO]`

### `[INFORMATIVO]`

No bloquea. Se avanza aplicando la "Asunción por defecto" declarada si el humano no responde. Aplica para:
- Edge cases con comportamiento conservador asumible
- Prioridad relativa entre opciones igualmente válidas
- Comportamiento en condiciones poco probables
- Preferencias de UX menores que no afectan la funcionalidad core

Formato completo: `[P-002][INFORMATIVO]` o `[D-002][INFORMATIVO]`

**Obligatorio**: todo gap `[INFORMATIVO]` debe incluir una "Asunción por defecto" que declare explícitamente qué se aplicará si el humano no responde.

---

## Marcador de pendiente

El marcador `_(pendiente)_` se inserta en el campo **"Respuesta"** de cada gap hasta que el humano lo reemplaza con su respuesta real.

### Formato de un gap en un informe de análisis

```markdown
### [P-001][CRÍTICO] Título descriptivo del gap
- **Contexto**: [dónde se detectó el gap en el documento]
- **Afecta**: [HU-001, HU-003 — lista de HUs que no pueden completarse sin esta respuesta]
- **Pregunta para el cliente**: [pregunta concreta y específica — sin inventar opciones]
- **Respuesta**: _(pendiente)_

### [P-002][INFORMATIVO] Título descriptivo del gap
- **Contexto**: [dónde se detectó el gap en el documento]
- **Pregunta para el cliente**: [pregunta concreta y específica]
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: [qué se aplicará si el cliente no responde]
```

> **Nota sobre `Afecta`**: El campo `Afecta` es obligatorio en gaps `[CRÍTICO]` y permite trazar qué HUs quedarán marcadas como `[INCOMPLETO]` si el gap no se responde. No aplica a gaps `[INFORMATIVO]` (estos siempre tienen asunción por defecto).

---

## Reglas de bloqueo para orquestadores

Los orquestadores verifican la presencia de marcadores pendientes antes de avanzar al siguiente paso del pipeline:

### En `wf-prepare-plan` (generar plan desde spec)

| Condición en el `_spec.md` | Acción del orquestador |
|-----------------------------|------------------------|
| Hay HUs marcadas `[INCOMPLETO]` | **Bloquear**: listar las HUs incompletas y los gaps que las bloquean |
| Hay gaps `[INFORMATIVO]` con `_(pendiente)_` pero no `[INCOMPLETO]` | **Continuar** con advertencia |
| Sin marcadores pendientes | **Continuar** normalmente |

**Patrón de verificación**: buscar la cadena literal `[INCOMPLETO]` para HUs incompletas, y `_(pendiente)_` para gaps sin responder.

---

## Convenciones para "Asunción por defecto"

- Debe ser la opción **más conservadora** (la que minimiza las asunciones funcionales)
- Debe ser **específica**: no "se comportará de forma estándar" sino "se mostrará un mensaje de error genérico y el usuario permanecerá en la pantalla actual"
- Se documenta en el spec generado en la sección `## Asunciones Aplicadas`
- En modo `delta`, se documenta en la sección `## Asunciones Aplicadas (vX.Y)` del spec actualizado

---

## Marcador de HU incompleta: `[INCOMPLETO]`

El marcador `[INCOMPLETO]` se aplica a nivel de HU en el spec generado cuando un gap `[CRÍTICO]` que la afecta (campo `Afecta`) quedó sin respuesta.

### Formato en el spec generado

Al final de cada HU afectada:
```markdown
> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001], [P-003]. Responde en el `_analysis.md` y ejecuta `/wf-spec-gap-resolve` para completar.
```

### Efecto en el pipeline

- Una HU marcada `[INCOMPLETO]` **se incluye** en el spec con toda la información disponible
- Los CAs asociados se generan parcialmente si es posible (con el GIVEN/WHEN disponible) o se omiten con referencia al gap
- `wf-prepare-plan` **bloquea** si el feature spec contiene HUs `[INCOMPLETO]`
- Para completar: responder el gap en el `_analysis.md`, luego ejecutar `/wf-spec-gap-resolve <feature_spec.md>` para integrar la respuesta y eliminar la marca
