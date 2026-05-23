---
name: wf-spec-analyze
description: Recopila las decisiones de negocio que necesitarán los Specs a partir de un PRD ya congelado. Mapea qué elementos del Spec se generarán desde el PRD, detecta contaminación técnica y formula preguntas concretas para el cliente. Genera un `_analysis.md` cuyas respuestas alimentan los Specs (el PRD no se modifica). Activa en frases como "prepara los inputs para los specs", "qué decisiones de negocio faltan para los specs", "analiza este PRD para empezar los specs", "genera el análisis previo al spec".
argument-hint: "<archivo.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-explorer
---

# Workflow: ANALYZE

Este workflow pertenece a la fase Spec y **requiere un PRD o documento de requisitos previo** como entrada. Si el usuario todavía no tiene ese artefacto, remítelo a la fase PRD antes de continuar.

Tu objetivo es **recopilar las decisiones de negocio que los Specs necesitarán** a partir de un PRD que ya está congelado. No auditas el PRD ni le buscas defectos: el PRD ya hizo su trabajo en la fase anterior y, según `kb-prd-expert`, no tiene por qué contener HUs, Journeys, CAs ni Checklist — esos elementos pertenecen al Spec y se generarán después.

Usa `kb-spec-expert` para aplicar los 3 checks. El Check 1 mapea qué elementos del Spec se generarán a partir del PRD; el Check 2 detecta contaminación técnica (única condición que sí justifica retocar el PRD); el Check 3 evalúa la testabilidad si el PRD ya tuviera CAs formales.

**Regla de oro:** Nunca rellenas huecos funcionales. Si algo no está definido o es ambiguo, lo marcas con `_(pendiente)_` en el campo "Respuesta" del gap (consulta `kb-gap-conventions` para el formato exacto) y formulas una pregunta concreta. El cliente decide, tú detectas. **El PRD no se modifica**: las respuestas se anotan en el `_analysis.md` y alimentan los Specs.

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

Si el nombre termina en `_spec.md`, `_plan.md` o `_tasks.md` → informa:
> "Este archivo parece un artefacto posterior del pipeline SDD. `/wf-spec-analyze` opera sobre PRDs o documentos de requisitos previos a Spec."

---

## Paso 3: Leer el contenido

Lee el archivo en su totalidad.

---

## Paso 4: Mapear elementos del Spec y detectar problemas reales

### Check 1 — Mapeo de elementos del Spec a generar
Para cada uno de los 8 elementos del Spec (consulta `kb-spec-expert` para su definición), determina su estado de partida en el PRD:

- Actores
- Historias de Usuario (Como/quiero/para que)
- Recorridos de Usuario
- Resultados y Éxito
- Instrucciones Inambiguas (incluyendo tabla de destinos de navegación si hay flujos de navegación)
- Criterios de Aceptación (GIVEN/WHEN/THEN)
- Checklist de Validación
- Fuera de Alcance

Para cada uno, indica si ya viene en el PRD, si se generará entero durante la fase Spec, o si está parcial y se completará en Spec. **Esto no es un score de defectos**: lo normal en un PRD es que HUs formales, Journeys paso a paso, CAs en GIVEN/WHEN/THEN y Checklist no estén — pertenecen al Spec, no al PRD (`kb-prd-expert` Regla 9). El propósito de este check es dar visibilidad de qué se va a generar después, no señalar carencias.

### Check 2 — Pureza (única vía legítima para tocar el PRD)
Consulta `prohibited_items.md` y `error_patterns.md` del skill `kb-spec-expert` antes de emitir tu veredicto. Para cada frase problemática:
- Cita el fragmento exacto
- Explica por qué es técnico
- Propón la reescritura funcional

**Importante**: ésta es la **única** condición que justifica devolver el documento a la fase PRD. Si el Check 2 está limpio, el PRD se considera correcto tal cual está y se procede con los Specs, incluso si los Checks 1 o 3 reportan elementos ausentes (es lo esperable).

### Check 3 — Testabilidad
Si el PRD ya incluye CAs formales (poco habitual en un PRD), cada uno debe ser verificable objetivamente e independientemente, tener GIVEN/WHEN/THEN completo, y referenciar su HU padre. Los que no cumplan estos criterios deben aparecer con su reformulación sugerida. Si no hay CAs en el PRD, indica `NO_APLICA` — los CAs se generarán en la fase Spec.

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
- Veredicto del Estado de preparación para Specs
- Resumen: cuántos elementos del Spec se generarán desde cero vs. ya parciales en PRD, cuántas contaminaciones técnicas detectadas (si las hay), cuántos `[P-XXX]` pendientes (desglosados: CRÍTICOS e INFORMATIVOS)
- Siguiente paso:
  - Si veredicto = `LISTO_PARA_SPECS` o `LISTO_PARA_SPECS_CON_PREGUNTAS`: "Anota las respuestas a las preguntas marcadas como _(pendiente)_ en `<path>_analysis.md` (las respuestas se escriben en este archivo, no en el PRD) y ejecuta `/wf-spec-features-first <archivo.md>` para el flujo completo, o `/wf-spec-discover <archivo.md> --analysis <path>_analysis.md` para el paso a paso."
  - Si veredicto = `REQUIERE_LIMPIEZA_PRD`: "Hay contaminación técnica en el PRD. Aplica las acciones marcadas en la sección Pureza del análisis y vuelve a ejecutar `/wf-spec-analyze <archivo.md>` antes de continuar."
