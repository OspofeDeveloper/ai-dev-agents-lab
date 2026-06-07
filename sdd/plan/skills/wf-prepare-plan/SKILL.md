---
name: wf-prepare-plan
description: "Transforma Specs validados y el handoff de Design en Planes tecnicos. Usalo cuando tengas un _spec.md sin items pendientes y una feature lista a nivel visual para generar el plan tecnico de implementacion. El plan se especializa segun el stack del proyecto (overlay tech, p. ej. KMM) o en modo generico para stacks agnosticos."
when_to_use: "Activa en frases como 'genera el plan desde el spec', 'crea el plan tecnico', 'transforma el spec en plan', 'planifica la implementacion de', 'prepara el plan para'. No activa para analizar o generar Specs (usa wf-spec-analyze), ni para validar Planes (usa wf-plan-validate), ni para crear Tasks (usa wf-prepare-tasks)."
argument-hint: "generate <spec.md>"
effort: high
allowed-tools: [Read, Write, Agent]
context: fork
agent: plan-architect
---

# prepare-plan — Orquestador del Flujo SDD (Etapa Plan)

Tu rol es de **orquestador puro**: parseas argumentos, verificas que el Spec y el handoff de Design están listos, delegas la arquitectura al agente `plan-architect`, y escribes el output resultante. No realizas el diseño técnico directamente.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (solo `generate` está soportado)
- **Path del archivo**: el resto del argumento

Si no hay argumento o el modo no es válido, informa al usuario:
> "Uso: `/wf-prepare-plan generate <archivo_spec.md>`"

Ejemplo:
- `generate docs/login_spec.md` → modo=generate, archivo=docs/login_spec.md

---

## Paso 2: Verificar el Spec

Antes de verificar el Spec, determina el contexto técnico del proyecto. Busca `.sdd/project-init.json` (en el directorio actual o en el raíz del proyecto):

- **Stack con especialista** (`specialist_workflow` no nulo, p. ej. `kmm`): exige `<stack>_project_state.md` (directorio actual o raíz). Si falta, detén:
  > "❌ El stack `<stack>` no tiene su estado técnico generado. Ejecuta `/wf-<stack>-init` antes de producir el Plan."
- **Stack agnóstico** (`"stack": "agnostico"`): modo genérico — no exijas ningún project_state. El Plan debe fundamentarse en la exploración del repositorio (estructura, lenguajes, convenciones existentes) y en `kb-plan-expert`.
- **Stack pendiente** (`"stack": null`): la entrevista técnica del proyecto no se ha hecho (init de perfil no técnico). Detén:
  > "❌ Este proyecto aún no tiene configurado su stack. Ejecuta `/wf-project-init` → 'Completar / ampliar' (perfil Desarrollo) antes de producir el Plan."
- **Sin `.sdd/project-init.json`**: si existe `kmm_project_state.md` (compatibilidad con proyectos antiguos), continúa en modo KMM. Si no, detén:
  > "❌ Este proyecto no está inicializado. Ejecuta primero `/wf-project-init` antes de producir el Plan."

1. Verifica que el archivo existe.
2. Lee el archivo completo.
3. Comprueba si contiene HUs incompletas, items pendientes o señales de desincronización:
   - Si hay HUs marcadas `[INCOMPLETO]` → lista cuáles, los gaps que las bloquean, y **detén la ejecución**:
     > "❌ El Spec tiene X HUs marcadas `[INCOMPLETO]`. No se puede generar el Plan hasta completarlas. Responde los gaps pendientes en el `_analysis.md` y ejecuta `/wf-spec-gap-resolve` para integrar las respuestas."
   - Si hay `[CRÍTICO]_(pendiente)_` → lista cuáles y **detén la ejecución**:
     > "❌ El Spec tiene X items [CRÍTICO] sin resolver. Responde los gaps críticos antes de generar el Plan."
   - Si el spec declara `status_sync: stale` o `status_sync: needs_review` → **detén la ejecución**:
     > "❌ El Spec no está sincronizado con la versión vigente del PRD. Ejecuta `wf-prd-sync-impact` o `wf-spec-sync-from-prd` antes de generar el Plan."
   - Si hay `[INFORMATIVO]_(pendiente)_` pero no `[INCOMPLETO]` ni `[CRÍTICO]` → advierte pero **continúa**:
     > "⚠ El Spec tiene X items [INFORMATIVO] sin responder. Se usarán los valores por defecto. Puedes responderlos después si quieres más precisión."
4. Verifica que el archivo parece un Spec validado (contiene "Criterios de Aceptación" e "Historias de Usuario"). Si parece un PRD sin procesar → informa:
   > "Este archivo no parece un Spec procesado. Primero ejecuta `/wf-spec-analyze <archivo.md>`"
5. **Pin del SSoT (solo repos consumidores)**: si `.sdd/project-init.json` declara `artifacts_source` y `artifacts_source_pin`, compara el pin con `git -C <artifacts_source> rev-parse --short HEAD`. Si difieren → **advierte y continúa** (no bloquea):
   > "⚠ El repo de specs (`<artifacts_source>`) está en `<HEAD>` pero este repo planificó por última vez contra `<pin>`. Revisa los cambios de specs desde entonces y actualiza `artifacts_source_pin` en `.sdd/project-init.json` cuando los hayas asumido."

---

## Paso 3: Leer el Spec y shared models

Lee el `_spec.md` en su totalidad.

Busca si existe un `_features.md` en el proyecto:
- si el spec está dentro de `features/<nombre>/` (directamente — layout plano legacy — o en su subcarpeta `spec/`), busca `*_features.md` en el directorio que contiene `features/`
- si el spec está en el directorio raíz, busca `*_features.md` en ese mismo directorio

Si existe `_features.md`, léelo completo.

Si el spec está dentro de `features/<nombre>/` pero **no se encuentra `_features.md`**, advierte al usuario:
> "⚠ No se encontró `_features.md`. Si este proyecto tiene múltiples features que comparten modelos de dominio, los shared models no se considerarán en el Plan y podrían redefinirse en cada feature. Para gestionar shared models correctamente, usa `/wf-spec-features-first` o `/wf-spec-discover` para identificar features y shared models. Continuando sin shared models."

---

## Paso 4: Resolver el handoff de Design

Aplica la **Regla canónica de `kb-plan-expert`** para decidir si `Design` es obligatorio. No inventes heurísticas adicionales fuera de esa regla.

Determina si la feature requiere handoff de Design exactamente según esa regla canónica:
- si la regla aplica → **sí requiere**
- si la regla no aplica → puede continuar sin handoff de Design

Si **sí requiere** handoff de Design:

1. Resuelve `DESIGN.md`:
   - si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.design`, búscalo en ese directorio
   - si el spec está dentro de `features/<nombre>/` (directamente o en su subcarpeta `spec/`), búscalo en el directorio que contiene `features/`
   - en el mismo directorio en otros casos
2. Resuelve `<feature>_flows.md` y `<feature>_views.md`: en la subcarpeta `design/` de la feature (`features/<nombre>/design/`); si no existe, en el mismo directorio del spec (layout plano legacy).
3. Lee los tres archivos completos.
4. Si falta alguno, **detén la ejecución**:
   > "❌ La feature requiere handoff de Design pero falta uno o más artefactos (`DESIGN.md`, `<feature>_flows.md`, `<feature>_views.md`). Ejecuta `/wf-design-system` y `/wf-design-feature-prototype` antes de generar el Plan."
5. Si `DESIGN.md` no contiene `## Accessibility`, **detén la ejecución**:
   > "❌ `DESIGN.md` no incluye la sección `## Accessibility`. Valida o corrige Design antes de generar el Plan."

Si **no requiere** handoff de Design:
- continúa
- deja trazado en el prompt del agente que se trata de una feature sin superficie UI visible

---

## Paso 5: Delegar al agente plan-architect

Construye el prompt para el agente ensamblando los bloques de `${CLAUDE_SKILL_DIR}/references/plan_prompt_templates.md`:
- Bloque base (siempre): spec completo
- Bloque shared models (si existe `_features.md`): instrucción de no redefinir owners ajenos
- Bloque handoff de Design (si la feature lo requiere): DESIGN.md + flows + views, con instrucción normativa
- Bloque sin Design (si la feature no tiene UI): nota explícita
- Bloque final (siempre): propagación de metadata de trazabilidad y estado `BORRADOR`

Invoca el agente `plan-architect` con el prompt construido.

---

## Paso 6: Manejar gaps del agente

Si el agente devuelve `DESIGN_GAPs`:
- informa al usuario los gaps detectados
- no escribas ningún archivo de salida
- siguiente paso sugerido:
  > "Corrige el handoff de Design (`DESIGN.md`, `*_flows.md`, `*_views.md`) y vuelve a ejecutar `/wf-prepare-plan generate <spec.md>`"

Si el agente devuelve `TECH_GAPs`:
- informa al usuario los gaps detectados
- no escribas ningún archivo de salida
- siguiente paso sugerido:
  > "Responde los TECH_GAPs añadiendo los detalles que faltan al Spec y vuelve a ejecutar `/wf-prepare-plan generate <spec.md>`"

Si no hay gaps → continúa.

Si el agente devuelve otros gaps normativos (`TRACE_GAPs`, `PLAN_GAPs`):
- informa al usuario los gaps detectados
- no escribas ningún archivo de salida
- siguiente paso sugerido:
  > "Corrige los gaps estructurales del Plan y vuelve a ejecutar `/wf-prepare-plan generate <spec.md>`"

---

## Paso 7: Escribir el resultado

Determina el path de salida:
- **repo consumidor** (si `.sdd/project-init.json` del directorio actual o un ancestro declara `artifacts_source`): el plan vive en ESTE repo, no junto al spec del SSoT → `<raíz_consumidor>/features/<nombre>/plan/<nombre>_plan.md` (crea los directorios; `<nombre>` = el de la carpeta de feature del spec en el SSoT)
- si el spec está en la subcarpeta `spec/` de una feature → subcarpeta hermana `plan/`: `features/<nombre>/plan/<nombre>_plan.md` (crea el directorio si no existe)
- si el spec está directamente en `features/<nombre>/` (layout plano legacy) o fuera de una feature → mismo directorio + nombre base + `_plan.md`
- ejemplos: `features/login/spec/login_spec.md` → `features/login/plan/login_plan.md`; `docs/login_spec.md` → `docs/login_plan.md`; consumidor con spec en `../product-ssot/spec/features/login/spec/login_spec.md` → `features/login/plan/login_plan.md` (local)

Antes de escribir, verifica si el archivo ya existe:
```bash
!test -f "<path_calculado>" && echo "EXISTE" || echo "NO_EXISTE"
```
Si ya existe → pregunta al usuario:
> "Ya existe `<path>`. ¿Deseas regenerarlo?"
- Si responde **no** → informa el path del artefacto existente y detén.
- Si responde **sí** → continúa.

Escribe el output del agente en ese archivo.

Antes de cerrar, verifica que el header `Spec origen` del plan resuelve como ruta relativa **desde la ubicación final del `_plan.md`** (con subcarpetas: `../spec/<nombre>_spec.md`; layout plano: `<nombre>_spec.md`; repo consumidor: la ruta relativa hasta el checkout del SSoT, p. ej. `../../../product-ssot/spec/features/login/spec/login_spec.md`). Si no resuelve, corrígelo — el sellador de `/wf-plan-validate` lo comprueba.

---

## Paso 8: Informar al usuario

- Path del Plan generado
- Resumen: módulos creados, número de UseCases, número de CAs cubiertos
- Estado del Plan: `BORRADOR`
- Si hay observaciones o puntos a revisar: cuáles
- Siguiente paso:
  > "Valida `<path>_plan.md` con `/wf-plan-validate <path>_plan.md` antes de generar tasks."
