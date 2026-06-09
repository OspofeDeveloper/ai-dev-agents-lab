---
name: wf-qa-verify
description: "Verifica la cobertura real de CAs de una feature tras implementar: localiza y ejecuta los tests que ejercitan cada TC del qa_plan, registra evidencia, escribe los estados por TC (CUBIERTO/PARCIAL/SIN_COBERTURA/MANUAL_PENDIENTE/DIVERGENTE) y produce <feature>_qa_report.md con veredicto APTO/APTO_CON_RESERVAS/NO_APTO. Delega a qa-engineer."
when_to_use: "Activa con frases como 'verifica la cobertura de la feature', 'qa verify', 'están cubiertos los CAs', 'audita los tests contra el spec', 'pasa QA la feature'. No activa para derivar casos de prueba (usa wf-qa-plan), ni para arreglar un test que falla contra un CA (usa wf-bug)."
argument-hint: "<feature_qa_plan.md>"
effort: high
allowed-tools: [Read, Write, Bash, Agent, AskUserQuestion]
context: fork
agent: qa-engineer
user-invocable: true
---

# Workflow: QA-VERIFY

Tu objetivo es auditar con evidencia ejecutada si la implementación de una feature cubre los CAs que su spec promete, TC a TC, y producir el `_qa_report.md` con veredicto. Los criterios de cobertura, estados y veredictos son los de `kb-qa-expert` — en particular su regla de oro: **cobertura sin evidencia ejecutada no existe**.

---

## Paso 1: Parsear argumentos y localizar artefactos

Extrae el path del `_qa_plan.md`. Si falta:
> "Uso: `/wf-qa-verify <feature_qa_plan.md>` — si aún no existe el QA plan, genera primero con `/wf-qa-plan generate <feature_spec.md>`"

Desde el qa_plan, resuelve el `Spec origen` del header (relativo al qa_plan). Si no resuelve, detente: la trazabilidad CA→TC es el objeto de este workflow, sin spec no hay verificación.

---

## Paso 2: Estado de implementación

Localiza el `_tasks.md` de la feature (mismo directorio que el qa_plan, o raíz de la feature en layout plano). Si existe y su tabla `## Progreso` no está COMPLETO, informa al usuario y pregunta si desea continuar con una **verificación parcial** (el report lo marcará). Si no existe `_tasks.md`, continúa — el QA verify también sirve para auditar features implementadas fuera del pipeline.

---

## Paso 3: Verificar cada TC automatizable

Para cada TC con `Automatizable: sí`, delega en `qa-engineer`:

1. **Localizar el test real** que lo ejercita: búsqueda por referencia (`TC-XXX`/`CA-XXX` en nombres o comentarios), por nombre del comportamiento, o por el módulo afectado. Anota el archivo y test concretos.
2. **Ejecutarlo**: con los comandos de `<stack>_project_state.md` si existe; si no, detecta el runner por archivos del repo (`gradlew`, `package.json`, `Makefile`, `pyproject.toml`...). Registra comando + resumen real de la salida.
3. **Asignar estado** según `kb-qa-expert`:
   - verde y ejercita el THEN completo → `CUBIERTO`
   - existe pero no cubre el THEN completo → `PARCIAL` (qué falta, concreto)
   - no existe test → `SIN_COBERTURA`
   - **ejecuta y FALLA → `DIVERGENTE`**: el código viola el CA. No toques código ni test, no "ajustes" el TC: la acción es `/wf-bug` citando el CA.

Si no hay forma razonable de ejecutar nada, decláralo literalmente ("verificación ejecutable: no disponible — \<motivo\>"): los TCs afectados quedan en `PENDIENTE` y el report lo refleja — nunca como cubiertos.

---

## Paso 4: Verificar los TC manuales

Presenta al usuario la checklist de TCs `Automatizable: no` (GIVEN/WHEN/THEN de cada uno) y pídele el resultado de los que haya ejecutado:
- confirmado → `CUBIERTO` (la confirmación queda registrada como evidencia: "confirmado por <usuario> YYYY-MM-DD")
- comportamiento incorrecto → `DIVERGENTE` (→ `/wf-bug`)
- sin ejecutar → `MANUAL_PENDIENTE`

No marques nunca un TC manual como CUBIERTO sin confirmación explícita del humano en esta sesión.

---

## Paso 5: Escribir estados y report

1. **Actualiza el campo `Estado` de cada TC** en el `_qa_plan.md` (este workflow es el único escritor de ese campo).
2. **Escribe el report** junto al qa_plan: `<nombre>_qa_report.md`, con el formato de `kb-qa-expert`: header de trazabilidad (qa_plan, spec, fecha, commit verificado), tabla resumen por CA (estado del CA = el peor de sus TCs), detalle de hallazgos (solo TCs no CUBIERTOS), acciones recomendadas y **veredicto**:
   - `APTO` — todos los CAs CUBIERTOS
   - `APTO_CON_RESERVAS` — hay PARCIAL/MANUAL_PENDIENTE, sin SIN_COBERTURA ni DIVERGENTE
   - `NO_APTO` — algún CA SIN_COBERTURA o DIVERGENTE
   Si la verificación fue parcial (Paso 2) o sin ejecución disponible (Paso 3), el header lo declara.

3. **Si el veredicto es `APTO` o `APTO_CON_RESERVAS`**, registra la **atribución de aprobación humana** del gate (`kb-traceability-rules` Regla 10): captura el rol con `AskUserQuestion` (default `QA`, permitiendo confirmar o dar nombre) y escribe en el header del `_qa_report.md` la línea `Aprobado por: <rol> (<fecha real de tu contexto>)`. **No autoapruebes**: si no hay respuesta, no escribas la línea. Si el veredicto es `NO_APTO`, **no** la escribas.

Si el report ya existe de una verificación anterior, sobreescríbelo (el qa_plan conserva el estado vigente; el report es la foto de esta verificación).

---

## Paso 6: Informar al usuario

- Veredicto y resumen por CA (X/N cubiertos).
- Hallazgos accionables: cada `DIVERGENTE` con su comando de `/wf-bug` sugerido; cada `SIN_COBERTURA`/`PARCIAL` con su owner de test recomendado; `MANUAL_PENDIENTE` listados.
- Si el veredicto es `APTO`: la feature cierra su ciclo QA — el siguiente paso natural es `/wf-spec-readiness` para el estado global del producto.
