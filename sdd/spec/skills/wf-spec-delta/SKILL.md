---
name: wf-spec-delta
description: Evoluciona un Spec de feature existente. Modo 'analyze' genera un informe delta con HUs y CAs añadidos, modificados y eliminados; modo 'apply' integra los cambios validados en el spec; modo 'resolve' completa HUs marcadas [INCOMPLETO] a partir de gaps respondidos en el analysis original. Activa en frases como "quiero añadir funcionalidad al spec", "actualiza el spec con estos requisitos nuevos", "evoluciona el spec con este cambio", "genera el delta del spec", "completar gaps", "resolver incompletos".
argument-hint: "analyze <spec.md> --new-reqs <desc.md> | apply <spec.md> <delta.md> | resolve <spec.md> [--analysis <analysis.md>]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-writer
---

# Workflow: DELTA

Tu objetivo es gestionar la evolución controlada de un Spec SDD existente. Usa `kb-spec-expert` para asegurarte de que los cambios propuestos y el spec resultante mantienen la pureza funcional y los 8 elementos SDD.

**Regla de oro:** El delta nunca reescribe la historia del spec — solo la extiende. Los cambios deben ser mínimos y quirúrgicos. Si el documento de nuevos requisitos describe en realidad un cambio de scope masivo, indícalo explícitamente al finalizar y sugiere volver a partir de un PRD completo.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (`analyze`, `apply` o `resolve`)
- En modo `analyze`:
  - **Path del spec existente**: el argumento después del modo, hasta `--new-reqs`
  - **Path de nuevos requisitos**: el argumento después de `--new-reqs`
- En modo `apply`:
  - **Path del spec existente**: el segundo argumento
  - **Path del delta analysis**: el tercer argumento
- En modo `resolve`:
  - **Path del spec existente**: el argumento después del modo
  - **Path del analysis** (opcional): el argumento después de `--analysis`. Si se omite, se auto-descubre (ver Paso 2).

Si no hay argumento o el modo no es válido, informa al usuario:
> "Uso:"
> - "`/wf-spec-delta analyze <feature_spec.md> --new-reqs <description.md>`"
> - "`/wf-spec-delta apply <feature_spec.md> <feature_delta_analysis.md>`"
> - "`/wf-spec-delta resolve <feature_spec.md> [--analysis <path_analysis.md>]`"

Ejemplos:
- `analyze features/auth/auth_spec.md --new-reqs new_requirements.md`
- `apply features/auth/auth_spec.md features/auth/auth_delta_analysis.md`
- `resolve features/auth/auth_spec.md`
- `resolve features/auth/auth_spec.md --analysis ../../prd-app_analysis.md`

---

## Paso 2: Verificar archivos

**Modo `analyze`:**
1. Verifica que el spec existe y termina en `_spec.md`. Si no → informa: "El primer argumento debe ser un spec SDD (`_spec.md`). Para generar un spec nuevo, usa `/wf-spec-analyze`."
2. Verifica que el archivo de nuevos requisitos existe. Si no → informa con la ruta exacta y detén.

**Modo `apply`:**
1. Verifica que el spec existe y termina en `_spec.md`.
2. Verifica que el delta analysis existe y termina en `_delta_analysis.md`. Si no → informa: "El segundo argumento debe ser un delta analysis generado por `/wf-spec-delta analyze`."
3. Lee el delta analysis y comprueba si hay items `[CRÍTICO]_(pendiente)_` sin respuesta. Si los hay → informa al usuario: "Hay X gaps **críticos** sin responder. Las HUs afectadas se marcarán como `[INCOMPLETO]`." **Continúa.**

**Modo `resolve`:**
1. Verifica que el spec existe y termina en `_spec.md`. Si no → informa: "El primer argumento debe ser un spec SDD (`_spec.md`)."
2. Si se proporcionó `--analysis`: verifica que el archivo existe y termina en `_analysis.md`.
3. Si no se proporcionó `--analysis`: auto-descubrir buscando `*_analysis.md` en el directorio dos niveles arriba del spec (convención: si el spec está en `features/<nombre>/<nombre>_spec.md`, buscar en el directorio que contiene la carpeta `features/`). Si no se encuentra ningún `_analysis.md` → informa: "No se encontró un `_analysis.md` en el directorio del proyecto. Usa `--analysis <path>` para indicar la ruta." y detén.
4. Lee el spec y extrae todos los marcadores `[INCOMPLETO]` con sus IDs de gap `[P-XXX]`.
5. Si no hay marcadores `[INCOMPLETO]` → informa: "Este feature spec no tiene HUs incompletas. No hay gaps que resolver." y detén.

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

Lee el documento de nuevos requisitos e identifica, consultando `kb-spec-expert` para verificar pureza funcional:

- **HUs AÑADIDAS**: funcionalidades que no existen en el spec actual. Una nueva HU es: mismo actor (o actor nuevo) con objetivo funcional no cubierto por ninguna HU existente.
- **HUs MODIFICADAS**: funcionalidades existentes cuyo comportamiento, actor o valor cambia. Cita la HU original.
- **HUs ELIMINADAS**: funcionalidades del spec actual que los nuevos requisitos explícitamente eliminan o reemplazan. Cita la HU a eliminar.
- **CAs AFECTADOS**: para cada HU añadida/modificada, identifica los CAs nuevos o los cambios a CAs existentes (GIVEN/WHEN/THEN).
- **Reglas de comportamiento**: nuevas reglas, modificaciones a reglas existentes, reglas que quedan obsoletas.
- **Impacto en Fuera de Alcance**: si los nuevos requisitos mueven algo de fuera a dentro del alcance, o viceversa.

### Paso 6A: Aplicar la Prueba de Pureza

Consulta `kb-spec-expert` para verificar que cada cambio propuesto está libre de contaminación técnica. Si un nuevo requisito contiene tech (frameworks, APIs, patrones de implementación), propón la reescritura funcional equivalente.

### Paso 7A: Detectar gaps funcionales en los nuevos requisitos

Aplica la misma lógica que el modo ANALYZE estándar sobre los nuevos requisitos en el contexto del spec existente. Consulta `kb-gap-conventions` para el formato de IDs `[D-XXX]` (prefijo D = Delta), las definiciones de severidad y el marcador `_(pendiente)_`.

### Paso 8A: Formato del informe delta

Usa `references/delta_analysis_template.md` para estructurar el informe.

---

## Submodo APPLY

### Paso 4B: Segunda verificación de gaps críticos

Si hay `[CRÍTICO]_(pendiente)_` en el delta analysis → informa al usuario qué HUs se marcarán `[INCOMPLETO]` y **continúa**. (Coherente con el Paso 2.)

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

### Paso 5B.5: Resolver marcadores `[INCOMPLETO]`

Si el delta analysis resuelve gaps que originaron marcadores `[INCOMPLETO]` en el spec:

1. Integrar la respuesta del gap en la HU afectada (completar la información que faltaba)
2. Generar/completar los CAs que no pudieron generarse previamente por falta de información
3. Eliminar el marcador `> ⚠ [INCOMPLETO] — ...` de la HU
4. Eliminar el gap correspondiente de la sección `## Items Pendientes` del spec (si existe)
5. Registrar en el Changelog: "Completada HU-XXX (gap [P-XXX] resuelto)"

Si tras la integración ya no quedan HUs `[INCOMPLETO]` en el spec, el feature está listo para `/wf-prepare-plan`.

---

## Submodo RESOLVE

### Paso 4R: Extraer gaps objetivo del spec

Parsea el spec y extrae de cada marcador `[INCOMPLETO]` los IDs de gap referenciados (ej: `[P-001]`, `[P-007]`). Construye una lista de gaps objetivo: `{ gap_id, HUs_afectadas[] }`.

### Paso 5R: Localizar respuestas en el analysis

Lee el `_analysis.md` y para cada gap objetivo:
1. Busca la sección del gap por su ID (ej: `### [P-001][CRÍTICO] ...`)
2. Lee el campo `**Respuesta**`
3. Clasifica:
   - Si contiene `_(pendiente)_` → **sin resolver**
   - Si contiene texto + `_(resuelto — aplicado en <nombre_spec> ...)_` donde `<nombre_spec>` coincide con el spec actual → **ya aplicado en este spec** (omitir, no re-aplicar)
   - Si contiene texto + `_(resuelto — aplicado en ...)_` donde el spec actual NO aparece en la lista → **resuelto, pendiente de aplicar en este spec** (capturar solo el texto de la respuesta, sin el marcador de resolución)
   - Si contiene cualquier otro texto (sin marcador de pendiente ni de resolución) → **resuelto** (capturar la respuesta íntegra)

### Paso 5R.2: Verificar estado de resolución

- Si **todos** los gaps objetivo están sin resolver → informa: "Ninguno de los gaps referenciados tiene respuesta en el analysis. Responde los gaps pendientes en `<path_analysis.md>` antes de ejecutar resolve." y **detén**.
- Si **algunos** gaps están sin resolver → informa: "X de Y gaps tienen respuesta. Se integrarán los resueltos. Los gaps sin responder siguen siendo: [lista de IDs sin resolver]." **Continúa** con los resueltos.
- Si **todos** están resueltos → **continúa**.

### Paso 5R.3: Integrar respuestas

Para cada gap resuelto, aplica la misma lógica que el Paso 5B.5:

1. Integrar la respuesta del gap en la HU afectada (completar la información que faltaba)
2. Generar/completar los CAs que no pudieron generarse previamente por falta de información
3. Eliminar el marcador `> ⚠ [INCOMPLETO] — ...` de la HU
4. Eliminar el gap correspondiente de la sección `## Items Pendientes` del spec (si existe)

Reglas de integración (idénticas a Paso 5B):
- **No interpretar**: la respuesta del cliente va tal cual
- **No ampliar**: si la respuesta cubre el gap, no expandirla
- **No inferir**: no añadir información que el cliente no proporcionó

### Paso 5R.4: Marcar gaps como resueltos en el analysis

Para cada gap integrado, actualizar el campo `**Respuesta**` en el `_analysis.md` añadiendo el marcador de resolución al final:

```
- **Respuesta**: [respuesta original del cliente] _(resuelto — aplicado en <nombre_spec> v<X.Y>)_
```

Ejemplo:
```
- **Respuesta**: El bloqueo muestra un mensaje con el tiempo restante y el campo queda deshabilitado. Es por cuenta, no por dispositivo. _(resuelto — aplicado en authentication_spec v1.1)_
```

Esto permite:
- Saber que el gap ya fue procesado (evitar re-aplicar)
- Trazar en qué spec y versión se integró
- Conservar la respuesta original como registro de la decisión

**Nota**: si el mismo `[P-XXX]` es referenciado por múltiples feature specs, cada resolve añade su propia marca. Ejemplo: `_(resuelto — aplicado en authentication_spec v1.1, home-dashboard_spec v1.1)_`.

Al leer un gap en el Paso 5R, si el campo `**Respuesta**` contiene texto seguido de `_(resuelto — aplicado en ...)_`, el gap se considera **resuelto con respuesta disponible**. Extraer solo el texto de la respuesta (sin el marcador de resolución) para la integración.

Tras la integración y marcado, fluir a los Pasos 6B, 6B.5, 7B, 8B, N-0.5 y N (compartidos con el submodo APPLY).

---

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

En modo `resolve`, el Changelog registra las HUs completadas:

```markdown
### v[X.Y] — [YYYY-MM-DD]
- **Completadas**: HU-XXX "[título]" (gap [P-XXX] resuelto)
- **CAs nuevos**: CA-XXX a CA-YYY (generados tras resolver gaps)
```

Si se aplicaron asunciones de gaps `[INFORMATIVO]`, añadir antes del Changelog:

```markdown
## Asunciones Aplicadas (v[X.Y])

- **[D-XXX]**: [descripción de la asunción aplicada por defecto]
```

### Paso 6B.5: Actualizar trazabilidad en `_features.md` (si existe)

Busca `_features.md` en el directorio base del proyecto:
- Si el spec está en `features/<nombre>/`: busca dos niveles arriba (ej: `features/auth/auth_spec.md` → busca en el directorio que contiene la carpeta `features/`)
- Si el spec es monolítico: busca en el mismo directorio

**Si existe el archivo y contiene la sección `## Trazabilidad RF → HU → Feature`:**

Para cada tipo de cambio aplicado en este delta:

- **HUs AÑADIDAS**: añade una fila nueva por cada HU con:
  - RF inferido del delta analysis (busca el RF de origen mencionado en el delta o en el documento de nuevos requisitos)
  - HU con su nuevo ID y título
  - Feature: nombre del feature spec actual
  - Estado: `activo`
- **HUs MODIFICADAS**: actualiza el Título HU en la fila correspondiente; el ID y el RF no cambian
- **HUs ELIMINADAS**: cambia el Estado de la fila a `eliminado vX.Y` (usando la nueva versión del spec); **NO eliminar la fila** — se conserva para auditoría

Actualiza la tabla `## Cobertura por RF` con las HUs y features modificadas.

Añade una fila al `## Historial de cambios` con la nueva versión del spec, la fecha de hoy, tipo "delta apply" y una descripción breve del conjunto de cambios.

**Si no existe el archivo o no tiene sección de trazabilidad:** omite este paso silenciosamente — no bloquea ni avisa.

---

### Paso 7B: Aplicar la Prueba de Pureza al spec resultante

Consulta `kb-spec-expert` y verifica que el spec final no tiene contaminación técnica. Si la hay, señálala en el output.

### Paso 8B: Auto-verificar el checklist

Revisa que el spec resultante sigue teniendo los 8 elementos SDD. Si alguno ha quedado incompleto, márcalo como `[ ]` en el checklist del spec.

---

## Paso N-1: Escribir el resultado

- **Modo `analyze`**: mismo directorio que el spec + nombre base + `_delta_analysis.md`
  - Ejemplo: `features/auth/auth_spec.md` → `features/auth/auth_delta_analysis.md`
- **Modo `apply`**: sobreescribe el spec existente con la versión actualizada
- **Modo `resolve`**: sobreescribe el spec existente con la versión actualizada (igual que `apply`)

---

## Paso N-0.5: Verificación de conflictos tras apply (no bloqueante)

Solo en modo `apply`. Busca si existe un `_features.md` en el proyecto (dos niveles arriba si el spec está en `features/<nombre>/`, o en el mismo directorio):

- **Si existe `_features.md`**: lee todos los specs `*_spec.md` de las features declaradas. Ejecuta el workflow `wf-spec-conflict` con el spec recién actualizado + todos los otros specs. Si detecta conflictos → escribe el informe en `<nombre>_conflict_report.md` en el mismo directorio que el spec.
- **Si no existe `_features.md`**: omitir este paso.

Este paso es **informativo y no bloquea** el flujo.

---

## Paso N: Informar al usuario

**Tras analyze:**
- Path del delta analysis generado
- Resumen de impacto: cuántas HUs añadidas/modificadas/eliminadas, cuántos CAs afectados
- Cuántos gaps `[CRÍTICO]` pendientes y cuántos `[INFORMATIVO]`
- Siguiente paso: "Revisa `<path>_delta_analysis.md`, responde los gaps `[CRÍTICO]` marcados como _(pendiente)_ y luego ejecuta `/wf-spec-delta apply <spec.md> <delta_analysis.md>`"

**Tras apply:**
- Path del spec actualizado
- Nueva versión del spec (ej: v1.0 → v1.1)
- Resumen de cambios integrados: HUs y CAs añadidos/modificados/eliminados
- Estado de la trazabilidad: si se actualizó `_features.md`, indicar: "✓ Trazabilidad actualizada en `_features.md`."
- Resultado de la verificación de conflictos:
  - Sin conflictos o sin `_features.md`: omitir o indicar brevemente
  - Con conflictos: "⚠ Se detectaron conflictos. Revisa `<path>_conflict_report.md` antes de continuar con `/wf-prepare-plan`."
- Siguiente paso: "Puedes validar la integridad del spec actualizado con `/wf-spec-validate <path>_spec.md`"

**Tras resolve:**
- Path del spec actualizado
- Nueva versión del spec (ej: v1.0 → v1.1)
- Lista de gaps resueltos y HUs completadas (ej: "Completada HU-003 (gap [P-001] resuelto)")
- CAs generados/completados con los gaps resueltos
- Si quedan HUs `[INCOMPLETO]` (por gaps que seguían sin respuesta): listarlas con sus gaps pendientes
- Si no quedan `[INCOMPLETO]`: "✓ Feature listo para `/wf-prepare-plan`."
- Estado de la trazabilidad: si se actualizó, indicar "✓ Trazabilidad actualizada."
- Siguiente paso: "Puedes validar la integridad del spec actualizado con `/wf-spec-validate <path>_spec.md`"
