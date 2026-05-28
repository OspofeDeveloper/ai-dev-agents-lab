---
name: wf-plan-validate
description: Workflow SDD que audita un _plan.md existente contra su Spec, el handoff de Design y las reglas de `kb-plan-expert`. No rediseña el contenido arquitectónico del archivo; solo audita su validez operativa y actualiza el estado (`BORRADOR` o `VALIDADO`). Activa en frases como "valida el plan", "revisa el _plan.md", "audita si el plan está listo para tasks", "comprueba que el plan cubre todos los CAs". No activa para generar el plan ni para crear tasks.
argument-hint: "<plan.md>"
effort: high
allowed-tools: [Read, Write, Agent]
context: fork
agent: plan-auditor
---

# plan-validate — Orquestador del Flujo SDD (Etapa Plan)

Tu rol es de **orquestador puro**: verificas que el `_plan.md` existe, reúnes sus artefactos de contexto, delegas la auditoría al agente `plan-auditor`, y presentas el resultado. No regeneras el contenido arquitectónico del plan. Sí actualizas su estado operativo a `VALIDADO` o `BORRADOR`.

## Paso 1: Parsear argumentos

El argumento esperado es un único path a `<archivo_plan.md>`.

Si falta o no parece un archivo válido, informa:
> "Uso: `/wf-plan-validate <archivo_plan.md>`"

## Paso 2: Verificar el Plan

1. Verifica que el archivo existe.
2. Léelo completo.
3. Verifica que parece un Plan técnico (contiene `Checklist de Trazabilidad` y `Estado:`). Si no:
   > "Este archivo no parece un Plan técnico SDD. Primero ejecuta `/wf-prepare-plan generate <spec.md>`"
4. Revisa las líneas resumen del footer del Plan:
   - `**DESIGN_GAPs:** ...`
   - `**TECH_GAPs:** ...`
   - `**TRACE_GAPs:** ...`
   - `**PLAN_GAPs:** ...`
   Considera que hay gaps abiertos **solo si** alguna de esas líneas tiene contenido distinto de `ninguno`.
   La mera presencia del nombre del gap en la plantilla no cuenta como gap abierto.
5. Si alguna de esas líneas indica gaps abiertos:
   - actualiza el header del archivo a `Estado: BORRADOR` si no lo está ya
   - informa:
     > "❌ El Plan contiene gaps abiertos. Resuélvelos antes de validarlo."
   - detén la ejecución

## Paso 3: Resolver artefactos de contexto

1. A partir del header `Spec origen`, resuelve y lee el `_spec.md`.
2. Si falta `Spec origen`, la ruta no es usable o el archivo no puede leerse, **detén la ejecución**:
   > "❌ No se puede validar el Plan sin su `Spec origen` resoluble. Corrige el header del `_plan.md` o regenera el Plan desde el Spec antes de reintentar."
3. Si el spec leído no parece un Spec SDD válido, **detén la ejecución**:
   > "❌ El `Spec origen` del Plan no parece un Spec SDD válido. Corrige la referencia o regenera el Plan antes de validarlo."
4. Si el plan contiene sección `Handoff desde Design`:
   - resuelve y lee `DESIGN.md`
   - resuelve y lee `<feature>_flows.md`
   - resuelve y lee `<feature>_views.md`
5. Si falta alguno de los artefactos de design referenciados, continúa igualmente pero marca esa ausencia en el prompt como hallazgo esperado.
5. Si existe `_features.md` relacionado con la feature, léelo para auditar shared models.

## Paso 4: Delegar al agente plan-auditor

Invoca al agente con este prompt:

```text
Modo: validate-plan
Path del plan: <path_plan>
Contenido del Plan:
---
<contenido_plan>
---
Contenido del Spec:
---
<contenido_spec>
---
Contenido de DESIGN.md:
---
<contenido_design_o_unknown>
---
Contenido de <feature>_flows.md:
---
<contenido_flows_o_unknown>
---
Contenido de <feature>_views.md:
---
<contenido_views_o_unknown>
---
Shared models del proyecto:
---
<contenido_features_o_unknown>
---
INSTRUCCIÓN: audita cobertura de CAs, completitud de secciones, coherencia con design, shared models, estado del plan y ausencia de gaps abiertos.
INSTRUCCIÓN: usa solo esta taxonomía de gaps: `DESIGN_GAP`, `TECH_GAP`, `TRACE_GAP`, `PLAN_GAP`.
INSTRUCCIÓN: si el plan está listo para Tasks, devuelve `OK` y un resumen corto.
INSTRUCCIÓN: si no está listo, devuelve un reporte con hallazgos y severidad, y además un bloque final normalizado con estas cuatro líneas exactas para persistir en el `_plan.md`:
`**DESIGN_GAPs:** ...`
`**TECH_GAPs:** ...`
`**TRACE_GAPs:** ...`
`**PLAN_GAPs:** ...`
Usa `ninguno` cuando una categoría no tenga gaps.
```

## Paso 5: Sellar el estado operativo

Si el agente devuelve `OK`:
- actualiza el header del `_plan.md` reemplazando `Estado: BORRADOR` por `Estado: VALIDADO`
- actualiza las líneas resumen del footer a:
  - `**DESIGN_GAPs:** ninguno`
  - `**TECH_GAPs:** ninguno`
  - `**TRACE_GAPs:** ninguno`
  - `**PLAN_GAPs:** ninguno`
- informa que el Plan está listo para Tasks
- siguiente paso:
  > "Ejecuta `/wf-prepare-tasks generate <plan.md>`"

Si el agente devuelve hallazgos:
- actualiza el header del `_plan.md` a `Estado: BORRADOR`
- sustituye en el footer las cuatro líneas resumen por el bloque normalizado devuelto por el agente
- muéstralos tal cual
- indica que el plan sigue en `BORRADOR`
- no sugieras pasar a Tasks hasta resolverlos
