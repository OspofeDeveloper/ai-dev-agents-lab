# SDD Plan — Gate técnico entre Design y Tasks

Este directorio contiene la fase `plan` del pipeline SDD. Su responsabilidad es transformar un `*_spec.md` validado y, cuando aplique, su handoff de Design en un `_plan.md` técnico KMM que cierre arquitectura, ownership, contratos y decisiones de plataforma antes de generar Tasks.

## Propósito de la fase

`plan` responde al **cómo técnico**:

- qué módulos se crean o modifican
- qué componentes existen por CA
- qué ownership tiene cada pieza entre `feature`, `core`, `app` y plataforma
- qué dependencias entre capas y módulos son válidas
- qué puntos requieren `expect/actual`
- cómo se materializa la accesibilidad y navegación definidas en Design

No responde todavía al orden exacto de implementación ni al troceado en tareas. Eso pertenece a `tasks`.

## Artefactos de entrada

- `features/<feature>/spec/<feature>_spec.md`
- `DESIGN.md` cuando la regla canónica de `kb-plan-expert` determine que `Design` es obligatorio
- `features/<feature>/design/<feature>_flows.md` cuando aplique esa misma regla
- `features/<feature>/design/<feature>_views.md` cuando aplique esa misma regla
- `*_features.md` si el proyecto usa shared models

(Features con layout plano legacy: los mismos artefactos directamente en `features/<feature>/`.)

## Artefactos de salida

- `features/<feature>/plan/<feature>_plan.md` (layout plano legacy: junto al spec)

Estado esperado del plan:
- `BORRADOR` tras `wf-prepare-plan`
- apto para Tasks solo después de `wf-plan-validate`

La SSoT de reglas de fase, obligatoriedad de `Design` y taxonomía de gaps vive en `skills/kb-plan-expert/SKILL.md`.

## Workflows

### `/wf-prepare-plan generate <feature_spec.md>`

Genera un `_plan.md` nuevo en estado `BORRADOR`.

Bloquea si:
- el Spec no está listo
- falta el handoff de Design requerido
- hay `DESIGN_GAP`, `TECH_GAP`, `TRACE_GAP` o `PLAN_GAP`

### `/wf-plan-validate <feature_plan.md>`

Audita un `_plan.md` existente contra:
- el Spec
- el handoff de Design
- los shared models
- las reglas de `kb-plan-expert`

Su objetivo es decidir si el Plan está listo para pasar a Tasks y sellar su estado operativo:
- `VALIDADO` si pasa
- `BORRADOR` si falla

## Dependencias cross-fase

Los agentes de esta fase cargan skills de otras fases del pipeline SDD:

| Skill | Fase origen | Uso en Plan |
|---|---|---|
| `kb-spec-expert` | `sdd/pipeline/spec/skills/` | Entender qué es un Spec SDD válido y extraer sus CAs |
| `kb-a11y-expert` | `sdd/pipeline/design/skills/` | Materializar las decisiones de accesibilidad del DESIGN.md como decisiones técnicas |

Estas dependencias siguen la Regla 9 de `kb-sdd-skill-architecture`: la SSoT vive en la fase que la define; `plan` la consume sin duplicar.

---

## Criterios de calidad

Un Plan sano:
- cubre todos los CAs del Spec
- no redefine shared models ajenos
- no introduce decisiones visuales nuevas
- materializa accesibilidad y navegación como decisiones técnicas
- no deja gaps abiertos
- puede entregarse a implementación sin nuevas decisiones arquitectónicas

## Siguiente fase

Solo cuando el `_plan.md` esté validado:

```text
/wf-prepare-tasks generate <feature_plan.md>
```
