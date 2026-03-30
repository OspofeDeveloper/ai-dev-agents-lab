---
name: spec-analyze
description: Workflow interno para el modo ANALYZE del agente sdd-analyst. Define cómo auditar un documento de requisitos y producir un informe de gaps. Cargado como contexto por sdd-analyst — no invocar directamente.
allowed-tools: [Read]
disable-model-invocation: true
---

# Workflow: ANALYZE

Tu objetivo es producir un informe honesto del estado del documento. Usa `spec-expert` para aplicar los 3 checks y detectar todo lo que impediría que este documento se convierta en un Spec válido.

**Regla de oro:** Nunca rellenas huecos funcionales. Si algo no está definido o es ambiguo, lo marcas con `_(pendiente)_` en el campo "Respuesta" del gap (consulta `gap-conventions` para el formato exacto) y formulas una pregunta concreta. El cliente decide, tú detectas.

---

## Qué debes identificar

### Check 1 — Completitud
Verifica la presencia de los 8 elementos obligatorios (consulta `spec-expert` para su definición):
- Actores
- Historias de Usuario (Como/quiero/para que)
- Recorridos de Usuario
- Resultados y Éxito
- Instrucciones Inambiguas (incluyendo tabla de destinos de navegación si hay flujos de navegación)
- Criterios de Aceptación (GIVEN/WHEN/THEN)
- Checklist de Validación
- Fuera de Alcance

### Check 2 — Pureza
Consulta `prohibited_items.md` y `error_patterns.md` del skill `spec-expert` antes de emitir tu veredicto. Para cada frase problemática:
- Cita el fragmento exacto
- Explica por qué es técnico
- Propón la reescritura funcional

### Check 3 — Testabilidad
Cada CA debe ser verificable objetivamente e independientemente, tener GIVEN/WHEN/THEN completo, y referenciar su HU padre. Los que no cumplan estos criterios deben aparecer con su reformulación sugerida.

---

## Gaps funcionales → preguntas [P-XXX]

Si encuentras información funcional ausente o ambigua (no técnica), formúlala como pregunta para el cliente. Cada gap debe ser:
- Concreto (no "¿qué más falta?")
- Sin opciones inventadas (el cliente decide)

Consulta `gap-conventions` para el formato de IDs `[P-XXX]`, las definiciones de severidad `[CRÍTICO]` / `[INFORMATIVO]`, el marcador `_(pendiente)_` y el formato exacto de cada gap en el informe.

### Clasificación de severidad (obligatoria)

Consulta `gap-conventions` para las definiciones completas. Resumen:

- **`[CRÍTICO]`**: bloquea la siguiente fase (el gap impide un CA verificable, un Journey sin estado de éxito, o una regla con interpretaciones incompatibles)
- **`[INFORMATIVO]`**: continúa con asunción por defecto (edge cases asumibles, preferencias menores). **Siempre incluye una "Asunción por defecto"** con lo que se aplicará si el cliente no responde.

---

## Formato de output

Consulta `references/output_template.md` para la estructura exacta del informe.
