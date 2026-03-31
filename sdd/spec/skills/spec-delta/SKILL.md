---
name: spec-delta
description: Evoluciona un Spec de feature existente con requisitos nuevos. Modo 'analyze' genera un informe delta con HUs y CAs añadidos, modificados y eliminados; modo 'apply' integra los cambios validados en el spec, incrementando la versión y añadiendo Changelog. Activa en frases como "quiero añadir funcionalidad al spec", "actualiza el spec con estos requisitos nuevos", "evoluciona el spec con este cambio", "genera el delta del spec".
argument-hint: "analyze <feature_spec.md> --new-reqs <description.md> | apply <feature_spec.md> <delta_analysis.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-analyst
---

# Workflow: DELTA

Tu objetivo es gestionar la evolución controlada de un Spec SDD existente. Usa `spec-expert` para asegurarte de que los cambios propuestos y el spec resultante mantienen la pureza funcional y los 8 elementos SDD.

**Regla de oro:** El delta nunca reescribe la historia del spec — solo la extiende. Los cambios deben ser mínimos y quirúrgicos. Si el documento de nuevos requisitos describe en realidad un cambio de scope masivo, indícalo explícitamente al finalizar y sugiere volver a partir de un PRD completo.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (`analyze` o `apply`)
- En modo `analyze`:
  - **Path del spec existente**: el argumento después del modo, hasta `--new-reqs`
  - **Path de nuevos requisitos**: el argumento después de `--new-reqs`
- En modo `apply`:
  - **Path del spec existente**: el segundo argumento
  - **Path del delta analysis**: el tercer argumento

Si no hay argumento o el modo no es válido, informa al usuario:
> "Uso:"
> - "`/spec-delta analyze <feature_spec.md> --new-reqs <description.md>`"
> - "`/spec-delta apply <feature_spec.md> <feature_delta_analysis.md>`"

Ejemplos:
- `analyze features/auth/auth_spec.md --new-reqs new_requirements.md`
- `apply features/auth/auth_spec.md features/auth/auth_delta_analysis.md`

---

## Paso 2: Verificar archivos

**Modo `analyze`:**
1. Verifica que el spec existe y termina en `_spec.md`. Si no → informa: "El primer argumento debe ser un spec SDD (`_spec.md`). Para generar un spec nuevo, usa `/spec-analyze`."
2. Verifica que el archivo de nuevos requisitos existe. Si no → informa con la ruta exacta y detén.

**Modo `apply`:**
1. Verifica que el spec existe y termina en `_spec.md`.
2. Verifica que el delta analysis existe y termina en `_delta_analysis.md`. Si no → informa: "El segundo argumento debe ser un delta analysis generado por `/spec-delta analyze`."
3. Lee el delta analysis y comprueba si hay items `[CRÍTICO]_(pendiente)_` sin respuesta. Si los hay → lista cuáles y detén: "Hay gaps **críticos** sin responder en el delta analysis. Son obligatorios antes de aplicar los cambios."

---

## Paso 3: Leer el contenido

Lee ambos archivos en su totalidad.

---

## Submodo ANALYZE

### Paso 4A: Inventariar el spec existente

Extrae y lista internamente (no en el output):
- Todos los actores con sus capacidades
- Todas las HUs con sus IDs y títulos
- Todos los CAs con sus IDs, HU padre y GIVEN/WHEN/THEN
- Todos los Journeys con sus IDs
- Todas las Instrucciones Inambiguas (reglas de comportamiento)
- La sección Fuera de Alcance

### Paso 5A: Analizar los nuevos requisitos

Lee el documento de nuevos requisitos e identifica, consultando `spec-expert` para verificar pureza funcional:

- **HUs AÑADIDAS**: funcionalidades que no existen en el spec actual. Una nueva HU es: mismo actor (o actor nuevo) con objetivo funcional no cubierto por ninguna HU existente.
- **HUs MODIFICADAS**: funcionalidades existentes cuyo comportamiento, actor o valor cambia. Cita la HU original.
- **HUs ELIMINADAS**: funcionalidades del spec actual que los nuevos requisitos explícitamente eliminan o reemplazan. Cita la HU a eliminar.
- **CAs AFECTADOS**: para cada HU añadida/modificada, identifica los CAs nuevos o los cambios a CAs existentes (GIVEN/WHEN/THEN).
- **Reglas de comportamiento**: nuevas reglas, modificaciones a reglas existentes, reglas que quedan obsoletas.
- **Impacto en Fuera de Alcance**: si los nuevos requisitos mueven algo de fuera a dentro del alcance, o viceversa.

### Paso 6A: Aplicar la Prueba de Pureza

Consulta `spec-expert` para verificar que cada cambio propuesto está libre de contaminación técnica. Si un nuevo requisito contiene tech (frameworks, APIs, patrones de implementación), propón la reescritura funcional equivalente.

### Paso 7A: Detectar gaps funcionales en los nuevos requisitos

Aplica la misma lógica que el modo ANALYZE estándar sobre los nuevos requisitos en el contexto del spec existente. Consulta `gap-conventions` para el formato de IDs `[D-XXX]` (prefijo D = Delta), las definiciones de severidad y el marcador `_(pendiente)_`.

### Paso 8A: Formato del informe delta

Usa `references/delta_analysis_template.md` para estructurar el informe.

---

## Submodo APPLY

### Paso 4B: Segunda verificación de gaps críticos

Si hay `[CRÍTICO]_(pendiente)_` en el delta analysis → lista cuáles y detén. (El Paso 2 ya lo comprueba — esta es una segunda línea de defensa.)

### Paso 5B: Integrar los cambios

Reglas de integración:
- **No interpretar**: el texto aprobado va tal cual
- **No ampliar**: si la respuesta cubre el gap, no expandirla
- **No inferir**: si algo quedó sin responder pero era [INFORMATIVO], usa solo la Asunción por defecto

Para cada tipo de cambio:

- **HUs AÑADIDAS**: insertar después de la última HU existente con numeración consecutiva (ej: si el spec llega hasta HU-006, la primera nueva es HU-007)
- **HUs MODIFICADAS**: reemplazar solo el texto de la HU afectada; mantener el ID original
- **HUs ELIMINADAS**: eliminar la HU y todos sus CAs asociados; renumerar para mantener secuencia sin huecos
- **CAs NUEVOS**: insertar al final de los CAs de su HU padre con numeración consecutiva. Incluir `← HU-XXX`
- **CAs MODIFICADOS**: reemplazar solo el GIVEN/WHEN/THEN del CA afectado; mantener el ID
- **CAs ELIMINADOS**: eliminar y renumerar los CAs restantes para eliminar huecos
- **Journeys**: actualizar añadiendo/modificando/eliminando pasos según los cambios de HUs
- **Instrucciones Inambiguas**: añadir/modificar/eliminar reglas según el delta
- **Fuera de Alcance**: actualizar si el delta lo especifica

### Paso 6B: Actualizar versionado y Changelog

Incrementar la versión en el header del spec (1.0 → 1.1, 1.2 → 1.3, 2.0 → 2.1).

Añadir o actualizar la sección Changelog al final del spec (orden cronológico inverso):

```markdown
## Changelog

### v[X.Y] — [YYYY-MM-DD]
- **Añadidas**: HU-XXX "[título]"
- **Modificadas**: HU-XXX "[título original]" — [descripción breve del cambio]
- **Eliminadas**: HU-XXX "[título]" (y sus CAs asociados)
- **CAs nuevos**: CA-XXX a CA-YYY
- **CAs modificados**: CA-XXX "[título]"
- **CAs eliminados**: CA-XXX "[título]"
- **Reglas**: [nueva/modificada/eliminada] "[descripción breve]"
```

Si se aplicaron asunciones de gaps `[INFORMATIVO]`, añadir antes del Changelog:

```markdown
## Asunciones Aplicadas (v[X.Y])

- **[D-XXX]**: [descripción de la asunción aplicada por defecto]
```

### Paso 7B: Aplicar la Prueba de Pureza al spec resultante

Consulta `spec-expert` y verifica que el spec final no tiene contaminación técnica. Si la hay, señálala en el output.

### Paso 8B: Auto-verificar el checklist

Revisa que el spec resultante sigue teniendo los 8 elementos SDD. Si alguno ha quedado incompleto, márcalo como `[ ]` en el checklist del spec.

---

## Paso N-1: Escribir el resultado

- **Modo `analyze`**: mismo directorio que el spec + nombre base + `_delta_analysis.md`
  - Ejemplo: `features/auth/auth_spec.md` → `features/auth/auth_delta_analysis.md`
- **Modo `apply`**: sobreescribe el spec existente con la versión actualizada

---

## Paso N-0.5: Verificación de conflictos tras apply (no bloqueante)

Solo en modo `apply`. Busca si existe un `_features.md` en el proyecto (dos niveles arriba si el spec está en `features/<nombre>/`, o en el mismo directorio):

- **Si existe `_features.md`**: lee todos los specs `*_spec.md` de las features declaradas. Ejecuta el workflow `spec-conflict` con el spec recién actualizado + todos los otros specs. Si detecta conflictos → escribe el informe en `<nombre>_conflict_report.md` en el mismo directorio que el spec.
- **Si no existe `_features.md`**: omitir este paso.

Este paso es **informativo y no bloquea** el flujo.

---

## Paso N: Informar al usuario

**Tras analyze:**
- Path del delta analysis generado
- Resumen de impacto: cuántas HUs añadidas/modificadas/eliminadas, cuántos CAs afectados
- Cuántos gaps `[CRÍTICO]` pendientes y cuántos `[INFORMATIVO]`
- Siguiente paso: "Revisa `<path>_delta_analysis.md`, responde los gaps `[CRÍTICO]` marcados como _(pendiente)_ y luego ejecuta `/spec-delta apply <spec.md> <delta_analysis.md>`"

**Tras apply:**
- Path del spec actualizado
- Nueva versión del spec (ej: v1.0 → v1.1)
- Resumen de cambios integrados: HUs y CAs añadidos/modificados/eliminados
- Resultado de la verificación de conflictos:
  - Sin conflictos o sin `_features.md`: omitir o indicar brevemente
  - Con conflictos: "⚠ Se detectaron conflictos. Revisa `<path>_conflict_report.md` antes de continuar con `/prepare-plan`."
- Siguiente paso: "Puedes validar la integridad del spec actualizado con `/spec-validate <path>_spec.md`"
