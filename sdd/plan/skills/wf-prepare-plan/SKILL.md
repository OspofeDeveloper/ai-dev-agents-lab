---
name: wf-prepare-plan
description: "Transforma Specs validados y el handoff de Design en Planes tecnicos KMM. Usalo cuando tengas un _spec.md sin items pendientes y una feature lista a nivel visual para generar el plan tecnico de implementacion."
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

---

## Paso 3: Leer el Spec y shared models

Lee el `_spec.md` en su totalidad.

Busca si existe un `_features.md` en el proyecto:
- si el spec está en `features/<nombre>/`, busca `../../*_features.md`
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
   - dos niveles arriba si el spec está en `features/<nombre>/`
   - en el mismo directorio en otros casos
2. Resuelve `<feature>_flows.md` y `<feature>_views.md` en el mismo directorio del spec.
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

Construye el prompt para el agente.

Base mínima:
```text
Modo: generate-plan
Path del spec: <path_completo>
Contenido del Spec:
---
<contenido_completo_del_spec>
---
```

Si existe `_features.md`, añade:
```text
Shared models del proyecto (NO redefinir — solo referenciar):
---
<sección relevante o contenido completo de _features.md>
---
INSTRUCCIÓN: Si algún modelo de la tabla anterior aparece en el Spec de esta feature, no lo redefinas en el Plan salvo que esta feature sea la owner.
```

Si la feature requiere handoff de Design, añade:
```text
La feature requiere handoff de Design.
Contenido de DESIGN.md:
---
<contenido_design>
---
Contenido de <feature>_flows.md:
---
<contenido_flows>
---
Contenido de <feature>_views.md:
---
<contenido_views>
---
INSTRUCCIÓN: trata estos artefactos como fuentes normativas para UI, navegación y accesibilidad. Si detectas contradicciones o falta información crítica, devuelve `DESIGN_GAPs` y no produzcas el Plan.
```

Si la feature no requiere handoff de Design, añade:
```text
La feature no tiene superficie UI visible. No se adjunta handoff de Design.
```

Añade siempre:
```text
INSTRUCCIÓN: Propaga al header del Plan cualquier metadata de trazabilidad presente en el Spec (`derived_from_prd`, `derived_from_prd_version`, `derived_from_change`, `status_sync`). Si falta, usa `unknown`.
INSTRUCCIÓN: El Plan generado debe salir con `Estado: BORRADOR`.
```

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
- mismo directorio + nombre base + `_plan.md`
- ejemplo: `docs/login_spec.md` → `docs/login_plan.md`

Escribe el output del agente en ese archivo.

---

## Paso 8: Informar al usuario

- Path del Plan generado
- Resumen: módulos creados, número de UseCases, número de CAs cubiertos
- Estado del Plan: `BORRADOR`
- Si hay observaciones o puntos a revisar: cuáles
- Siguiente paso:
  > "Valida `<path>_plan.md` con `/wf-plan-validate <path>_plan.md` antes de generar tasks."
