# Workflow Tests — SDD Spec Phase

Guía de validación manual de cada workflow del sistema SDD. Cada archivo describe:
- **Prompt de activación**: lo que debes escribir para disparar el workflow
- **Flujo esperado**: pasos que debe seguir el agente, a nivel de capas (qué invoca, qué skill usa, qué produce)

Usa esta guía para verificar que el comportamiento real del agente coincide con el diseño.

---

## Workflows cubiertos

| # | Archivo | Workflow | Trigger |
|---|---------|----------|---------|
| 01 | [prepare-spec-analyze.md](01_prepare-spec-analyze.md) | `prepare-spec analyze` | Primer paso de cualquier spec nuevo |
| 02 | [prepare-spec-finalize.md](02_prepare-spec-finalize.md) | `prepare-spec finalize` | Tras responder gaps del analyze |
| 03 | [prepare-spec-validate.md](03_prepare-spec-validate.md) | `prepare-spec validate` | Auditar un spec ya existente |
| 04 | [prepare-spec-fast-track.md](04_prepare-spec-fast-track.md) | `prepare-spec fast-track` | Feature única sin spec monolítico |
| 05 | [decompose-spec.md](05_decompose-spec.md) | `decompose-spec` | Tras tener el spec monolítico limpio |
| 06 | [check-conflicts.md](06_check-conflicts.md) | `check-conflicts` | Revisar conflictos entre features |
| 07 | [prepare-delta.md](07_prepare-delta.md) | `prepare-delta` | Evolución incremental de spec existente |
| 08 | [prepare-plan.md](08_prepare-plan.md) | `prepare-plan` | Traducir spec de feature a plan KMM |
| 09 | [prepare-tasks.md](09_prepare-tasks.md) | `prepare-tasks` | Trocear plan en tasks implementables |

---

## Flujo completo de referencia

```
PRD
 └─► /prepare-spec analyze      → prd_analysis.md
         [HUMANO: responde gaps CRÍTICO]
 └─► /prepare-spec finalize     → prd_spec.md
 └─► /decompose-spec            → prd_features.md + features/X/X_spec.md
         [HUMANO: valida partición]
 └─► /check-conflicts           → _conflict_report.md  (opcional pero recomendado)
 └─► /prepare-plan              → features/X/X_plan.md
 └─► /prepare-tasks             → features/X/X_tasks.md

Casos especiales:
 └─► /prepare-spec fast-track   → features/X/X_spec.md  (atajo para feature única)
 └─► /prepare-spec validate     → informe inline (sin generar archivo)
 └─► /prepare-delta             → evolución incremental de spec existente
```

---

## Cómo validar un workflow

Para cada test, compara el comportamiento observado contra los pasos definidos en el archivo correspondiente. Los puntos clave a revisar:

1. **El orquestador (L1) no hace trabajo de análisis** — solo parsea args y delega
2. **El subagente correcto es invocado** — con el modo y ficheros correctos
3. **El subagente carga el knowledge correcto** — spec-expert, decompose-expert, etc.
4. **El workflow (L3) es el que guía los pasos** — no el agente improvisando
5. **Los artefactos de salida tienen el nombre y ubicación correctos**
6. **Los bloqueos por gaps CRÍTICO se respetan** — no se bypassean
