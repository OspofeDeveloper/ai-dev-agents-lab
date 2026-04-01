---
name: wf-spec-map-analyze
description: Analiza cada feature de un `_project_map.md` validado individualmente. Para cada feature, genera `features/<X>/_analysis.md` con gaps de completitud, pureza y testabilidad — usando el mapa como contexto del sistema completo para detectar también contaminación cross-feature. Activa en frases como "analiza las features del mapa", "genera los análisis de features", "analiza el PRD por features", "detecta gaps por feature".
argument-hint: "<prd.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-analyst
---

# Workflow: SPEC-MAP-ANALYZE

Tu objetivo es analizar cada feature del mapa de forma individual, usando el project map como contexto del sistema completo. Cada análisis cubre únicamente el scope de su feature — no el PRD entero.

Este workflow analiza el PRD feature por feature (una por una), lo que permite checkpoints humanos más pequeños y contextualizados en lugar de revisar el documento entero de golpe.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS` el path del PRD.

Si no hay argumento, informa al usuario:
> "Uso: `/wf-spec-map-analyze <prd.md>`"
> "Ejemplo: `/wf-spec-map-analyze docs/requisitos.md`"

---

## Paso 2: Verificar precondiciones

1. Verifica que el PRD existe.
2. Construye el path del project map: mismo directorio + nombre base + `_project_map.md`.
3. Verifica que el project map existe. Si no → informa:
   > "No se encontró el project map. Genera el mapa primero con `/wf-spec-map <prd.md>`"
4. Lee el project map completo.
5. Extrae la lista de features. Si alguna feature está marcada como `[EXCLUIDA]` → omitirla del análisis.
6. Si el project map está vacío o no tiene features → informa que el mapa debe tener al menos una feature antes de continuar.

---

## Paso 3: Leer el PRD

Lee el PRD en su totalidad. Será el documento fuente del que se extrae la información para cada feature.

---

## Paso 4: Analizar cada feature

Para cada feature del mapa (en orden de ID), ejecuta los siguientes pasos:

### 4a. Extraer información relevante al scope de esta feature

Del PRD, identifica las secciones, párrafos y reglas que corresponden a esta feature según lo que declara el mapa. Ten en cuenta las interacciones del mapa para saber qué información pertenece a qué feature cuando el PRD mezcle varias.

### 4b. Aplicar Check 1 — Completitud

Verifica si hay información suficiente en el PRD para construir los 8 elementos SDD de esta feature (consulta `kb-spec-expert`):
- Actores (filtrado al scope de esta feature)
- Historias de Usuario
- Recorridos de Usuario
- Resultados y Éxito
- Instrucciones Inambiguas
- Criterios de Aceptación (GIVEN/WHEN/THEN)
- Checklist de Validación
- Fuera de Alcance

### 4c. Aplicar Check 2 — Pureza

Detecta contaminación técnica en las secciones del PRD que corresponden a esta feature. Consulta `kb-spec-expert` (referencias `prohibited_items.md` y `error_patterns.md`). Para cada fragmento problemático:
- Cita el fragmento exacto
- Explica por qué es técnico (Prueba de Pureza: ¿cambiaría si pasáramos a otra plataforma?)
- Propón la reescritura funcional

### 4d. Aplicar Check 3 — Testabilidad

Verifica que los comportamientos descritos para esta feature son convertibles en CAs con GIVEN/WHEN/THEN completo y verificables objetivamente. Los que no cumplan aparecen con su reformulación sugerida.

### 4e. Detectar contaminación cross-feature

Identifica secciones del PRD que el mapa asigna a **otra** feature pero que aparecen mezcladas con la información de la feature actual. Documéntalas para que el programador sepa qué ignorar al responder los gaps de esta feature.

### 4f. Formular gaps → [P-XXX]

Para cada información funcional ausente o ambigua, formula un gap. Consulta `kb-gap-conventions` para el formato de IDs `[P-XXX]`, las definiciones de severidad y el marcador `_(pendiente)_`.

Regla de oro: nunca rellenas huecos funcionales. Si algo no está definido, marcas el gap y preguntas. No inventas.

### 4g. Generar el `_analysis.md` de la feature

Produce el análisis siguiendo la estructura de `references/feature_analysis_template.md`.

Determina el path de salida: `<directorio_del_prd>/features/<nombre-feature>/_analysis.md`

Crea el directorio si no existe.

---

## Paso 5: Escribir los artefactos

Escribe un `_analysis.md` por cada feature procesada.

---

## Paso 6: Informar al usuario

Tras escribir todos los análisis, informa:
- Número de features analizadas
- Tabla resumen: Feature | CRÍTICOS pendientes | INFORMATIVOS pendientes | Estado
- Si alguna feature tiene 0 CRÍTICOS: menciona que está lista para generar
- Siguiente paso:
  > "Edita cada `features/<X>/_analysis.md` y responde los gaps `[CRÍTICO]_(pendiente)_` de cada feature. Los gaps `[INFORMATIVO]` son opcionales — si no los respondes se aplicarán las asunciones por defecto. Cuando todos los `[CRÍTICO]` estén respondidos, ejecuta:"
  > ```
  > /wf-spec-map-generate <prd.md>
  > ```
