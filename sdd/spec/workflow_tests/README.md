# Workflow Tests — SDD Spec Phase

Guía de validación manual de cada workflow de la etapa Spec del sistema SDD.

---

## Estado

Los tests de workflows spec (`wf-spec-map`, `wf-spec-map-analyze`, `wf-spec-map-generate`, `wf-spec-validate`, `wf-spec-conflict`) están pendientes de crear.

Los tests de la etapa Plan se han movido a `sdd/plan/workflow_tests/`.

---

## Flujo completo de referencia

```
PRD
 └─► /wf-spec-map               → prd_project_map.md
         [HUMANO: valida el mapa]
 └─► /wf-spec-map-analyze       → features/<X>/_analysis.md (por feature)
         [HUMANO: responde gaps CRÍTICO por feature]
 └─► /wf-spec-map-generate      → features/<X>/<X>_spec.md + _features.md
         [automático: verifica conflictos con wf-spec-conflict]
```

---

## Cómo validar un workflow

Para cada test, compara el comportamiento observado contra los pasos definidos en el archivo correspondiente. Los puntos clave a revisar:

1. **El workflow skill parsea args y delega en sdd-analyst** — no improvisa
2. **sdd-analyst carga los knowledge skills correctos** — kb-spec-expert, kb-decompose-expert, etc.
3. **El workflow guía los pasos** — el agente sigue el SKILL.md, no improvisa
4. **Los artefactos de salida tienen el nombre y ubicación correctos**
5. **Los bloqueos por gaps CRÍTICO se respetan** — no se bypassean
