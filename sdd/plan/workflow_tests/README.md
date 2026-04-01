# Workflow Tests — SDD Plan Phase

Guía de validación manual de cada workflow de la etapa Plan del sistema SDD. Cada archivo describe:
- **Prompt de activación**: lo que debes escribir para disparar el workflow
- **Flujo esperado**: pasos que debe seguir el agente, a nivel de capas (qué invoca, qué skill usa, qué produce)

Usa esta guía para verificar que el comportamiento real del agente coincide con el diseño.

---

## Workflows cubiertos

| # | Archivo | Workflow | Trigger |
|---|---------|----------|---------|
| 01 | [prepare-plan.md](01_prepare-plan.md) | `prepare-plan` | Traducir spec de feature a plan técnico |
| 02 | [prepare-tasks.md](02_prepare-tasks.md) | `prepare-tasks` | Trocear plan en tasks implementables |

---

## Flujo de referencia

```
features/<X>/<X>_spec.md
 └─► /prepare-plan generate              → features/<X>/<X>_plan.md
 └─► /prepare-tasks generate             → features/<X>/<X>_tasks.md
```

---

## Cómo validar un workflow

Para cada test, compara el comportamiento observado contra los pasos definidos en el archivo correspondiente. Los puntos clave a revisar:

1. **El workflow skill parsea args y delega en el agente correcto** — no improvisa
2. **El agente carga los knowledge skills correctos** — plan-expert, tasks-expert, etc.
3. **El workflow guía los pasos** — el agente sigue el SKILL.md, no improvisa
4. **Los artefactos de salida tienen el nombre y ubicación correctos**
5. **Los bloqueos por TECH_GAPs se respetan** — no se bypassean
