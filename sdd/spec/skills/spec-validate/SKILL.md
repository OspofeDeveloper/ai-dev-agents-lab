---
name: spec-validate
description: Workflow interno para el modo VALIDATE del agente sdd-analyst. Define cómo auditar un _spec.md ya generado para detectar regresiones tras ediciones manuales. Cargado como contexto por sdd-analyst — no invocar directamente.
allowed-tools: [Read]
disable-model-invocation: true
---

# Workflow: VALIDATE

Tu objetivo es auditar un `_spec.md` ya generado para detectar regresiones de pureza, testabilidad o completitud introducidas por ediciones manuales. Usa `spec-expert` para aplicar los 3 checks.

**No produces ningún archivo nuevo.** El informe se devuelve al orquestador para que lo imprima directamente al usuario.

---

## Qué debes verificar

### Check 1 — Completitud (8 elementos)
- Actores
- Historias de Usuario
- Recorridos de Usuario
- Resultados y Éxito
- Instrucciones Inambiguas
- Criterios de Aceptación
- Checklist de Validación
- Fuera de Alcance

### Check 2 — Pureza
Consulta `spec-expert/references/prohibited_items.md` y `spec-expert/references/error_patterns.md`. Cita cualquier frase que viole la Prueba de Pureza.

### Check 3 — Testabilidad
Cada CA debe tener GIVEN/WHEN/THEN completo, ser verificable objetivamente, y referenciar su HU padre (`← HU-XXX`).

---

## Formato de output

Consulta `references/output_template.md` para la estructura exacta del informe de validación.
