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

Aplica los 3 checks definidos en `spec-expert`:

- **Check 1 — Completitud**: los 8 elementos SDD están presentes (consulta `spec-expert` para sus definiciones)
- **Check 2 — Pureza**: consulta `spec-expert/references/prohibited_items.md` y `error_patterns.md`; cita cualquier frase que viole la Prueba de Pureza
- **Check 3 — Testabilidad**: cada CA tiene GIVEN/WHEN/THEN completo, es verificable objetivamente, y referencia su HU padre (`← HU-XXX`)

---

## Formato de output

Consulta `references/output_template.md` para la estructura exacta del informe de validación.
