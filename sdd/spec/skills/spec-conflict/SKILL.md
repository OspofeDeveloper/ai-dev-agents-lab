---
name: spec-conflict
description: Workflow interno para el modo CONFLICT del agente sdd-analyst. Define cómo comparar un conjunto de Specs SDD para detectar conflictos entre features del mismo proyecto. Cargado como contexto por sdd-analyst — no invocar directamente.
allowed-tools: [Read]
disable-model-invocation: true
---

# Workflow: CONFLICT

Tu objetivo es detectar inconsistencias entre los Specs SDD de un mismo proyecto que podrían derivar en comportamiento indefinido, implementación duplicada o gaps funcionales no cubiertos. Usa `conflict-expert` para las 5 reglas de detección y `spec-expert` como referencia estructural.

**Regla de oro:** El informe es informativo, no bloqueante. Tu rol es detectar y describir — la decisión de cómo resolver cada conflicto la toma el humano.

---

## Qué debes hacer

### 1. Inventariar todos los specs recibidos

El orquestador te pasará el contenido de todos los specs a comparar. Para cada spec, extrae internamente (no en el output):
- Feature ID y nombre
- Lista de actores
- Lista de HUs con sus IDs, actores y objetivos funcionales
- Lista de CAs con sus IDs, GIVEN/WHEN/THEN y HU padre
- Lista de Journeys con sus pasos principales
- Modelos de dominio mencionados (tanto propios como referenciados como shared)
- Sección Fuera de Alcance

### 2. Aplicar las 5 reglas de conflict-expert

Aplica cada regla consultando `conflict-expert` y busca conflictos entre cada par de specs:

1. **HUs duplicadas**: compara actores + verbos + objetivos entre todos los pares de features
2. **CAs contradictorios**: compara GIVEN+WHEN entre todos los CAs del proyecto; busca THENs incompatibles
3. **Scope overlap**: analiza si los Journeys de una feature incluyen funcionalidad que es el objetivo de otra
4. **Shared models inconsistentes**: inventaría todos los modelos mencionados y cruza sus definiciones/comportamientos
5. **Fuera de alcance contradictorio**: cruza las secciones "Fuera de Alcance" de cada feature con las HUs de las demás

### 3. Clasificar cada conflicto detectado

Por cada conflicto:
- Asigna el ID: `[CF-001]`, `[CF-002]`, etc.
- Asigna la severidad según `conflict-expert`: ALTA o MEDIA
- Describe qué features están involucradas
- Cita las secciones exactas en conflicto
- Sugiere una posible resolución (sin imponer — es una sugerencia)

### 4. Producir el output

Usa `references/conflict_report_template.md` para estructurar el informe.

Si no se detecta ningún conflicto → devuelve un informe breve con estado "SIN_CONFLICTOS" y el inventario de comparaciones realizadas.
