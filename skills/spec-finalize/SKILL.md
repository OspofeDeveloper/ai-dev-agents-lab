---
name: spec-finalize
description: Workflow interno para el modo FINALIZE del agente sdd-analyst. Define cómo construir el Spec SDD final a partir de un documento validado por el cliente. Cargado como contexto por sdd-analyst — no invocar directamente.
allowed-tools: [Read]
disable-model-invocation: true
---

# Workflow: FINALIZE

Tu objetivo es construir el Spec SDD final usando la información ya validada por el humano. Usa `spec-expert` como guía estructural para asegurarte de que el Spec resultante cumple los 8 elementos y pasa la Prueba de Pureza.

---

## Qué debes hacer

1. **Extraer las respuestas** de los items `[P-XXX]` del análisis
2. Si quedan `_(pendiente)_` sin respuesta → lista cuáles y detén la ejecución
3. **Integrar respuestas exactamente como las escribió el cliente** — sin interpretar ni ampliar
4. **Construir el Spec** con los 8 elementos en orden (ver template)
5. **Aplicar la Prueba de Pureza** sobre lo que tú mismo escribas antes de producir el output
6. **Asignar cada CA a su HU padre**: cada CA debe incluir `← HU-XXX` referenciando la historia que cubre
7. **Auto-marcar el Checklist**: marca `[x]` los items que puedes verificar directamente del spec que generaste; deja `[ ]` solo los que requieren validación humana posterior

---

## Reglas de integración

- **No inventar**: si el cliente no respondió algo, no lo inferir; marcarlo como `[PENDIENTE]`
- **No interpretar**: el texto del cliente va tal cual, sin parafrasear
- **No añadir**: si la respuesta del cliente cubre exactamente el gap, no expandirla con suposiciones adicionales

---

## Formato de output

Consulta `references/output_template.md` para la estructura exacta del Spec SDD final.
