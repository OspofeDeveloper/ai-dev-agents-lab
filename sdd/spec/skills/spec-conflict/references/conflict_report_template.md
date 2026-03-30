# Conflict Report: [Nombre del proyecto]

> **Generado por**: sdd-analyst (modo conflict)
> **Fecha**: [YYYY-MM-DD]
> **Specs analizados**: [N] features
> **Features**: [lista de feature IDs y nombres]

---

## Estado general

> **[SIN_CONFLICTOS | CONFLICTOS_DETECTADOS]**
>
> Resumen en 1-2 frases. Si hay conflictos, indicar cuántos son de severidad ALTA y cuántos MEDIA.

---

## Resumen de conflictos

<!-- Si SIN_CONFLICTOS: "No se detectaron conflictos entre los [N] specs analizados." -->

| ID | Tipo | Severidad | Features involucradas |
|----|------|:---------:|-----------------------|
| CF-001 | HU duplicada | ALTA | feature-a, feature-b |
| CF-002 | CA contradictorio | ALTA | feature-b, feature-c |
| CF-003 | Scope overlap | MEDIA | feature-a, feature-c |

---

## Detalle de conflictos

<!-- Repetir este bloque por cada conflicto detectado -->

### [CF-001] [Tipo de conflicto] — Severidad: [ALTA | MEDIA]

**Features involucradas**: `[feature-a]`, `[feature-b]`

**Descripción**: [explicación del conflicto en lenguaje natural]

**En `[feature-a]`**:
> "[cita exacta de la HU, CA, Journey o regla en conflicto — con su ID]"

**En `[feature-b]`**:
> "[cita exacta de la sección en conflicto — con su ID]"

**Por qué es un conflicto**: [explicación específica de la incompatibilidad]

**Sugerencia de resolución**: [recomendación concreta — ej: "Considerar que HU-003 de feature-a es la definición canónica y eliminar la HU-007 de feature-b", o "Clarificar con el cliente qué feature es la responsable de X"]

---

## Inventario de comparaciones realizadas

> Esta sección garantiza trazabilidad de qué se comparó contra qué.

| Check | Features comparadas | Conflictos encontrados |
|-------|---------------------|:---------------------:|
| HUs duplicadas | Todos los pares | N |
| CAs contradictorios | Todos los pares | N |
| Scope overlap | Todos los pares | N |
| Shared models inconsistentes | Todos los specs | N |
| Fuera de alcance contradictorio | Todos los pares | N |

---

## Próximos pasos

<!-- Si SIN_CONFLICTOS -->
> Los specs están listos para continuar con `/prepare-plan`.

<!-- Si CONFLICTOS_DETECTADOS -->
1. Revisar cada conflicto de severidad **ALTA** — deben resolverse antes de iniciar `/prepare-plan` en las features afectadas
2. Los conflictos de severidad **MEDIA** pueden documentarse como decisiones de diseño y resolverse en la fase de implementación
3. Para cada conflicto resuelto: editar los specs afectados y re-ejecutar `/check-conflicts` para verificar que se eliminó
