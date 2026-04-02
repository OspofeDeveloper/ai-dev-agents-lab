# Roadmap: /wf-init-sdd — Pipeline completo

## Estado actual

El wizard `/wf-init-sdd` cubre solo la fase **Spec** del pipeline SDD:
- Generar specs desde PRD (analyze → finalize → decompose)
- Fast-track para features individuales
- Delta para cambios incrementales
- Validación y detección de conflictos
- Detección de estado para continuar

## Opciones futuras: Plan y Tasks

Cuando se implementen, añadir estas opciones al menú del wizard:

| # | Opción | Workflow destino |
|---|---|---|
| 7 | Generar plan técnico desde un spec | `/wf-prepare-plan generate <spec.md>` |
| 8 | Generar tareas desde un plan | `/wf-prepare-tasks generate <plan.md>` |

### Flujo Opción 7 — Generar plan técnico

- Pregunta: "¿Cuál es la ruta del spec de feature?" (el `_spec.md`)
- Verifica que existe y que no tiene `_(pendiente)_`
- Invoca: `/wf-prepare-plan generate <spec>`
- Informa: "Siguiente: `/wf-prepare-tasks generate <plan>`"

### Flujo Opción 8 — Generar tareas

- Pregunta: "¿Cuál es la ruta del plan?" (el `_plan.md`)
- Verifica que existe
- Invoca: `/wf-prepare-tasks generate <plan>`

### Mejora en detección de estado (Opción 6)

Extender la lógica de detección para cubrir las 3 fases:

```
Si existe _tasks.md:
  → "Tu proyecto tiene tareas generadas. Listo para implementar."

Si existe _plan.md pero NO _tasks.md:
  → "Tienes el plan técnico. Siguiente: /wf-prepare-tasks"

Si existe features/*/_spec.md pero NO _plan.md:
  → "Tienes specs por feature. Siguiente: /wf-prepare-plan"
```

## Cuándo implementar

Cuando los workflows `wf-prepare-plan` y `wf-prepare-tasks` estén estabilizados y probados.
