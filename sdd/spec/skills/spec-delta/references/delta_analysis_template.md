# Delta Analysis: [Nombre del feature spec]

> **Generado por**: sdd-analyst (modo delta/analyze)
> **Fecha**: [YYYY-MM-DD]
> **Spec existente**: [path/feature_spec.md] (v[X.Y])
> **Nuevos requisitos**: [path/description.md]

---

## Estado general

> **[SIN_CAMBIOS | CAMBIOS_MENORES | CAMBIOS_SIGNIFICATIVOS | CAMBIO_DE_SCOPE]**
>
> Resumen en 1-2 frases del impacto. Si el resultado es CAMBIO_DE_SCOPE, indicar que se recomienda volver a partir de un PRD completo en lugar de aplicar un delta.

---

## Resumen de impacto

| Tipo | Añadidos | Modificados | Eliminados |
|------|:--------:|:-----------:|:----------:|
| Historias de Usuario | 0 | 0 | 0 |
| Criterios de Aceptación | 0 | 0 | 0 |
| Journeys | 0 | 0 | 0 |
| Reglas de comportamiento | 0 | 0 | 0 |

---

## HUs AÑADIDAS

<!-- Si no hay HUs nuevas: "Ninguna." -->

### [HU-NEW-001] [Título de la nueva HU]
- **Como** [actor] / **quiero** [acción] / **para que** [valor]
- **Justificación**: [qué parte del documento de nuevos requisitos origina esta HU]
- **CAs propuestos**: CA-NEW-001 a CA-NEW-00X (ver sección CAs AÑADIDOS)

---

## HUs MODIFICADAS

<!-- Si no hay HUs modificadas: "Ninguna." -->

### [HU-MOD-001] Afecta a: HU-[XXX] — [Título original]
- **Cambio**: [descripción del cambio funcional]
- **Texto actual en el spec**:
  > "[cita de la HU tal como está en el spec]"
- **Texto propuesto**:
  > "Como [actor] / quiero [nuevo texto] / para que [nuevo valor]"
- **Justificación**: [qué parte de los nuevos requisitos motiva este cambio]
- **CAs afectados**: [lista de CAs que cambian con esta modificación, si los hay]

---

## HUs ELIMINADAS

<!-- Si no hay HUs a eliminar: "Ninguna." -->

### [HU-DEL-001] HU-[XXX] — [Título]
- **Justificación**: [por qué esta HU queda obsoleta según los nuevos requisitos]
- **CAs que se eliminan con esta HU**: CA-[XXX], CA-[YYY] (ver sección CAs ELIMINADOS)

---

## CAs AÑADIDOS

<!-- Si no hay CAs nuevos: "Ninguno." -->

### [CA-NEW-001] [Título] ← HU-[XXX]
```
GIVEN [precondición clara]
WHEN [acción específica del usuario o del sistema]
THEN [resultado observable y verificable]
```

---

## CAs MODIFICADOS

<!-- Si no hay CAs modificados: "Ninguno." -->

### [CA-MOD-001] Afecta a: CA-[XXX] — [Título original] ← HU-[XXX]
- **GIVEN/WHEN/THEN actual**:
  ```
  GIVEN [precondición actual]
  WHEN [acción actual]
  THEN [resultado actual]
  ```
- **GIVEN/WHEN/THEN propuesto**:
  ```
  GIVEN [precondición nueva]
  WHEN [acción nueva]
  THEN [resultado nuevo]
  ```
- **Justificación**: [qué cambia y por qué]

---

## CAs ELIMINADOS

<!-- Si no hay CAs a eliminar: "Ninguno." -->

### [CA-DEL-001] CA-[XXX] — [Título] ← HU-[XXX]
- **Justificación**: [por qué este CA queda obsoleto]

---

## Reglas de comportamiento afectadas

<!-- Si no hay reglas afectadas: "Ninguna." -->

- **[NUEVA]** [Descripción de la nueva regla funcional]
- **[MODIFICADA]** "[Regla actual]" → "[Regla propuesta]"
- **[ELIMINADA]** "[Regla que ya no aplica]" — [justificación]

---

## Puntos pendientes de validación

> - `[CRÍTICO]`: **debe responderse** antes de ejecutar `/prepare-delta apply`.
> - `[INFORMATIVO]`: si no se responde, se aplicará la "Asunción por defecto" indicada.

<!-- Si no hay puntos pendientes: eliminar esta sección y añadir "Sin gaps detectados." -->

### [D-001][CRÍTICO] [Título del gap]
- **Contexto**: [en qué parte de los nuevos requisitos aparece la ambigüedad]
- **Problema**: [por qué este gap impide definir el cambio de forma verificable]
- **Pregunta**: [pregunta concreta y específica, sin opciones inventadas]
- **Respuesta**: _(pendiente)_

### [D-002][INFORMATIVO] [Título del gap]
- **Contexto**: [dónde aparece la ambigüedad]
- **Pregunta**: [pregunta concreta]
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: [lo que se aplicará si no se responde antes de ejecutar apply]

---

## Próximos pasos

1. Revisar los cambios propuestos en las secciones anteriores
2. Responder los gaps `[CRÍTICO]` marcados como _(pendiente)_ — son **obligatorios** para continuar
3. Responder los gaps `[INFORMATIVO]` si tienes la información — si no, se aplicará la asunción por defecto
4. Una vez completados los `[CRÍTICO]`, ejecutar:
   ```
   /prepare-delta apply [path/feature_spec.md] [path/feature_delta_analysis.md]
   ```
