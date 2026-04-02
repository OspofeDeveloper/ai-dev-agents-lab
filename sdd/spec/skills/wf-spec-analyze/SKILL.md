---
name: wf-spec-analyze
description: Analiza un documento de requisitos y produce un informe de gaps (completitud, pureza y testabilidad). Genera un `_analysis.md` con preguntas para el cliente. Activa en frases como "analiza este documento para el spec", "¿qué le falta a este doc para ser spec?", "genera el análisis de gaps", "prepara el análisis del spec", "analiza este PRD".
argument-hint: "<archivo.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-analyst
---

# Workflow: ANALYZE

Tu objetivo es producir un informe honesto del estado del documento. Usa `kb-spec-expert` para aplicar los 3 checks y detectar todo lo que impediría que este documento se convierta en un Spec válido.

**Regla de oro:** Nunca rellenas huecos funcionales. Si algo no está definido o es ambiguo, lo marcas con `_(pendiente)_` en el campo "Respuesta" del gap (consulta `kb-gap-conventions` para el formato exacto) y formulas una pregunta concreta. El cliente decide, tú detectas.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS` el path del archivo a analizar.

Si no hay argumento, informa al usuario:
> "Uso: `/wf-spec-analyze <archivo.md>`"
> "Ejemplo: `/wf-spec-analyze docs/requisitos.md`"

---

## Paso 2: Verificar el archivo

Verifica que el archivo existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y detén.

---

## Paso 3: Leer el contenido

Lee el archivo en su totalidad.

---

## Paso 4: Identificar gaps y problemas

### Check 1 — Completitud
Verifica la presencia de los 8 elementos obligatorios (consulta `kb-spec-expert` para su definición):
- Actores
- Historias de Usuario (Como/quiero/para que)
- Recorridos de Usuario
- Resultados y Éxito
- Instrucciones Inambiguas (incluyendo tabla de destinos de navegación si hay flujos de navegación)
- Criterios de Aceptación (GIVEN/WHEN/THEN)
- Checklist de Validación
- Fuera de Alcance

### Check 2 — Pureza
Consulta `prohibited_items.md` y `error_patterns.md` del skill `kb-spec-expert` antes de emitir tu veredicto. Para cada frase problemática:
- Cita el fragmento exacto
- Explica por qué es técnico
- Propón la reescritura funcional

### Check 3 — Testabilidad
Cada CA debe ser verificable objetivamente e independientemente, tener GIVEN/WHEN/THEN completo, y referenciar su HU padre. Los que no cumplan estos criterios deben aparecer con su reformulación sugerida.

---

## Paso 5: Formular gaps funcionales → preguntas [P-XXX]

Si encuentras información funcional ausente o ambigua (no técnica), formúlala como pregunta para el cliente. Cada gap debe ser:
- Concreto (no "¿qué más falta?")
- Sin opciones inventadas (el cliente decide)

Consulta `kb-gap-conventions` para el formato de IDs `[P-XXX]`, las definiciones de severidad `[CRÍTICO]` / `[INFORMATIVO]`, el marcador `_(pendiente)_` y el formato exacto de cada gap en el informe.

### Campo "Afecta" (obligatorio en CRÍTICO)

Para cada gap `[CRÍTICO]`, determina qué HUs del documento no pueden completarse sin la respuesta a este gap. Lista sus IDs en el campo `- **Afecta**: [HU-001, HU-003]`. Si las HUs aún no tienen IDs asignados (porque el documento es un PRD sin HUs formales), describe las funcionalidades afectadas en texto libre (ej: `- **Afecta**: funcionalidad de login, recuperación de contraseña`).

### Clasificación de severidad (obligatoria)

Consulta `kb-gap-conventions` para las definiciones completas. Resumen:

- **`[CRÍTICO]`**: las HUs indicadas en "Afecta" quedarán marcadas `[INCOMPLETO]` en el spec si no se responde. Se generarán con la información disponible pero no podrán avanzar a plan/tasks.
- **`[INFORMATIVO]`**: continúa con asunción por defecto (edge cases asumibles, preferencias menores). **Siempre incluye una "Asunción por defecto"** con lo que se aplicará si el cliente no responde.

---

## Paso 6: Formato del informe

Consulta [output_template.md](output_template.md) para la estructura exacta del informe.

---

## Paso 7: Escribir el resultado

Determina el path de salida: mismo directorio que el archivo de entrada + nombre base + `_analysis.md`.
- Ejemplo: `docs/requisitos.md` → `docs/requisitos_analysis.md`

Escribe el informe generado en ese path.

---

## Paso 8: Informar al usuario

Tras escribir el archivo, informa:
- Path del archivo generado
- Resumen: cuántos elementos de completitud faltan, cuántas contaminaciones detectadas, cuántos `[P-XXX]` pendientes (desglosados: CRÍTICOS e INFORMATIVOS)
- Siguiente paso: "Edita `<path>_analysis.md`, responde las preguntas marcadas como _(pendiente)_ y luego ejecuta `/wf-spec-finalize <archivo.md>`"
