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
| Análisis de documento origen (modos `analyze`, `finalize`, `fast-track`) | `[P-XXX]` | `[P-001]`, `[P-042]` |
| Análisis de cambios incrementales (modo `delta`) | `[D-XXX]` | `[D-001]`, `[D-003]` |

**Numeración**: secuencial desde `001`, sin saltos, reiniciando en cada artefacto nuevo.

---

## Severidades

### `[CRÍTICO]`

Bloquea la generación del artefacto de la siguiente fase. Aplica cuando el gap impide:
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
- **Pregunta para el cliente**: [pregunta concreta y específica — sin inventar opciones]
- **Respuesta**: _(pendiente)_

### [P-002][INFORMATIVO] Título descriptivo del gap
- **Contexto**: [dónde se detectó el gap en el documento]
- **Pregunta para el cliente**: [pregunta concreta y específica]
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: [qué se aplicará si el cliente no responde]
```

---

## Reglas de bloqueo para orquestadores

Los orquestadores verifican la presencia de marcadores pendientes antes de avanzar al siguiente paso del pipeline:

| Condición en el artefacto | Acción del orquestador |
|---------------------------|------------------------|
| Hay `[CRÍTICO]_(pendiente)_` | **Bloquear**: listar los gaps sin respuesta y detener la ejecución |
| Solo hay `[INFORMATIVO]_(pendiente)_` | **Continuar**: informar al usuario que se aplicarán las asunciones por defecto |
| No hay `_(pendiente)_` | **Continuar** normalmente |

**Patrón de verificación**: buscar la cadena literal `_(pendiente)_` en el archivo. Es un bloqueo si aparece en la misma sección que un `[CRÍTICO]`.

---

## Convenciones para "Asunción por defecto"

- Debe ser la opción **más conservadora** (la que minimiza las asunciones funcionales)
- Debe ser **específica**: no "se comportará de forma estándar" sino "se mostrará un mensaje de error genérico y el usuario permanecerá en la pantalla actual"
- Se documenta en el spec generado en la sección `## Asunciones Aplicadas`
- En modo `delta`, se documenta en la sección `## Asunciones Aplicadas (vX.Y)` del spec actualizado
