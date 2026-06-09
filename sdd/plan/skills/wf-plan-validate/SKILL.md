---
name: wf-plan-validate
description: "Audita un _plan.md existente contra su Spec, el handoff de Design y las reglas de kb-plan-expert. No rediseña el contenido arquitectonico del archivo; solo audita su validez operativa y actualiza el estado (BORRADOR o VALIDADO)."
when_to_use: "Activa en frases como 'valida el plan', 'revisa el _plan.md', 'audita si el plan está listo para tasks', 'comprueba que el plan cubre todos los CAs'. No activa para generar el plan ni para crear tasks."
argument-hint: "<plan.md>"
effort: high
allowed-tools: [Read, Write, Bash, Agent, AskUserQuestion]
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

## Paso 4b: Aprobación humana de la deuda técnica (si la hay)

Si el plan contiene una sección `## Deuda técnica asumida`, cada entrada `### TD-00X` es un **checkpoint humano obligatorio** antes del sellado (el sellador rechaza cualquier TD con `Aprobada por: PENDIENTE`).

1. Revisa primero el veredicto del auditor sobre la deuda (Check 5): si degradó alguna TD a `TECH_GAP` (era un gap funcional disfrazado), trátala como gap — no la presentes para aprobar.
2. Para cada TD que el auditor consideró deuda legítima y siga en `Aprobada por: PENDIENTE`, preséntala al usuario (Decisión, A pesar de, Riesgo asumido, Queda pendiente) y pide decisión explícita con `AskUserQuestion`:
   - **Aprobar** → sustituye `PENDIENTE` por `<usuario/rol> (<YYYY-MM-DD>)` en esa entrada (esto sí lo escribe el orquestador: es el registro del checkpoint humano, no el sello del plan).
   - **Rechazar** → la decisión no se asume: el plan no es válido tal cual. Informa de que debe regenerarse resolviendo esa incertidumbre (responder en el spec si era ambigüedad funcional, o tomar otra decisión técnica) y **detén** sin sellar.
3. No autoapruebes ninguna TD por el usuario. Si no hay respuesta, la deuda queda `PENDIENTE` y el sellado fallará en el Paso 5 — que es el comportamiento correcto.

## Paso 5: Sellar el estado operativo (sellador determinista)

El estado del plan **solo** lo escribe el script `.sdd/scripts/sdd-seal.py` (separación autor/sellador: el veredicto del agente es necesario pero no suficiente). Nunca edites la línea `Estado:` a mano. (Las aprobaciones de deuda del Paso 4b sí las escribe el orquestador: son el registro del checkpoint, distinto del sello operativo del plan — el sellador las verifica, no las produce.)

Si el agente devuelve `OK`:
- actualiza las líneas resumen del footer a:
  - `**DESIGN_GAPs:** ninguno`
  - `**TECH_GAPs:** ninguno`
  - `**TRACE_GAPs:** ninguno`
  - `**PLAN_GAPs:** ninguno`
- ejecuta el sellador:
  ```bash
  python3 .sdd/scripts/sdd-seal.py plan <path_plan> --seal
  ```
- **exit 0** → el plan queda `VALIDADO`. Registra la **atribución de aprobación humana** del gate (`kb-traceability-rules` Regla 10): captura el rol con `AskUserQuestion` (default `Tech Lead`, permitiendo confirmar o dar nombre) y escribe en el header del plan, cerca de `Estado:`/`Spec origen`, la línea `Aprobado por: <rol> (<fecha real de tu contexto>)`. Esto lo escribe el **orquestador**, igual que las aprobaciones de deuda del Paso 4b: es el registro del checkpoint humano, **no** el sello operativo (el `Estado:` lo escribe `sdd-seal.py`, que no toca ni verifica esta línea). En re-validación, sobrescribe la línea previa. **No autoapruebes**: si no hay respuesta, no escribas la línea. Luego informa que está listo para Tasks:
  > "Ejecuta `/wf-prepare-tasks generate <plan.md>`"
- **exit 2** → el veredicto del agente no superó la verificación mecánica (el script muestra qué condición falló: CA sin cubrir, gap abierto, spec con `[CRÍTICO]`, `status_sync` no fiable...). El plan queda en `BORRADOR`. Muestra los checks `✗` al usuario y trata cada uno como hallazgo a resolver. No sugieras pasar a Tasks.
- **script no encontrado** → NO selles manualmente. Informa:
  > "⚠ Falta `.sdd/scripts/sdd-seal.py`. Re-ejecuta la instalación del ecosistema (`install.sh`) para reponer los scripts de enforcement."

Si el agente devuelve hallazgos:
- sustituye en el footer las cuatro líneas resumen por el bloque normalizado devuelto por el agente
- ejecuta `python3 .sdd/scripts/sdd-seal.py plan <path_plan> --unseal` (downgrade a `BORRADOR`; si el script falta, en este caso sí puedes escribir `Estado: BORRADOR` a mano — degradar siempre es seguro)
- muestra los hallazgos tal cual
- indica que el plan sigue en `BORRADOR`
- no sugieras pasar a Tasks hasta resolverlos
