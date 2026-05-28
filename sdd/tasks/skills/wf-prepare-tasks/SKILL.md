---
name: wf-prepare-tasks
description: Orquestador SDD para transformar Planes técnicos KMM validados en Tasks de implementación. Úsalo cuando tengas un _plan.md validado y quieras generar el listado de tasks para delegar a agentes KMM especializados. Activa en frases como "genera las tasks del plan", "trocéa el plan en tasks", "crea el listado de implementación", "prepara las tasks para", "¿qué tasks tengo que hacer?". No activa para generar Specs (usa wf-spec-analyze), ni para generar Planes (usa wf-prepare-plan), ni para validar Planes (usa wf-plan-validate).
argument-hint: "generate <plan.md>"
effort: high
allowed-tools: [Read, Write, Agent]
disable-model-invocation: true
context: fork
agent: task-generator
---

# prepare-tasks — Orquestador del Flujo SDD (Etapa Tasks)

Tu rol es de **orquestador puro**: parseas argumentos, verificas que el Plan está listo, delegas la descomposición al agente `task-generator`, y escribes el output resultante. No realizas la descomposición directamente.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (solo `generate` está soportado)
- **Path del archivo**: el resto del argumento

Si no hay argumento o el modo no es válido, informa al usuario:
> "Uso: `/wf-prepare-tasks generate <archivo_plan.md>`"

Ejemplo:
- `generate docs/login_plan.md` → modo=generate, archivo=docs/login_plan.md

---

## Paso 2: Verificar el Plan

1. Verifica que el archivo existe.
2. Lee el archivo completo.
3. Revisa las líneas resumen del footer del Plan:
   - `**DESIGN_GAPs:** ...`
   - `**TECH_GAPs:** ...`
   - `**TRACE_GAPs:** ...`
   - `**PLAN_GAPs:** ...`
   Considera que hay gaps sin resolver **solo si** alguna de esas líneas tiene contenido distinto de `ninguno`.
   La mera presencia del nombre del gap en la plantilla no cuenta como gap abierto.
4. Si alguna de esas líneas indica gaps abiertos → lista cuáles y detén:
   > "❌ El Plan tiene gaps sin resolver. Actualiza Design o Spec, regenera el Plan y vuelve a validarlo antes de crear Tasks."
5. Si el plan declara `status_sync: stale` o `status_sync: needs_review` → detén:
   > "❌ El Plan no está sincronizado con la versión vigente del PRD. Resincroniza primero el Spec/Plan antes de crear Tasks."
6. Si el header no contiene `Estado:` o el estado no es `VALIDADO` → detén:
   > "❌ El Plan no está validado. Ejecuta `/wf-plan-validate <plan.md>` y corrige los hallazgos antes de generar Tasks."
7. Verifica que el archivo parece un Plan técnico (contiene `Domain Layer` o `Checklist de Trazabilidad`). Si no → informa:
   > "Este archivo no parece un Plan técnico. Primero ejecuta `/wf-prepare-plan generate <spec.md>`"

---

## Paso 3: Leer el contenido

Lee el `_plan.md` en su totalidad.

---

## Paso 4: Delegar al agente task-generator

Invoca al agente `task-generator` con el siguiente prompt:

```text
Path del plan: <path_completo>
Contenido del Plan:
---
<contenido_completo_del_plan>
---
INSTRUCCIÓN: El Plan ya viene validado. Si declara metadata de trazabilidad (`Spec origen`, `PRD origen`, `PRD version`, `Change ref`, `Status sync`), propágala al header del `_tasks.md`. Si falta, usa `unknown` o `N/A` de forma explícita.
```

Espera a que el agente complete su ejecución y recibe su output.

---

## Paso 5: Escribir el resultado

Determina el path de salida:
- mismo directorio + nombre base + `_tasks.md`
- ejemplo: `docs/login_plan.md` → `docs/login_tasks.md`

Escribe el output del agente en ese archivo.

---

## Paso 6: Informar al usuario

- Path del archivo de tasks generado
- Resumen: total de tasks y desglose por owner agent o dominio de ejecución
- Orden recomendado de ejecución
- Siguiente paso:
  > "Delega las tasks en orden empezando por T-000 al owner agent indicado"
