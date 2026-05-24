---
name: wf-prepare-plan
description: Orquestador SDD para transformar Specs validados en Planes técnicos KMM. Úsalo cuando tengas un _spec.md sin items pendientes y quieras generar el plan técnico de implementación. Activa en frases como "genera el plan desde el spec", "crea el plan técnico", "transforma el spec en plan", "planifica la implementación de", "prepara el plan para". No activa para analizar o generar Specs (usa wf-spec-analyze) ni para crear Tasks (usa wf-prepare-tasks).
argument-hint: "generate <spec.md>"
effort: high
allowed-tools: [Read, Write, Agent]
disable-model-invocation: true
context: fork
agent: plan-architect
---

# prepare-plan — Orquestador del Flujo SDD (Etapa 3)

Tu rol es de **orquestador puro**: parseas argumentos, verificas que el Spec está listo, delegas la arquitectura al agente `plan-architect`, y escribes el output resultante. No realizas el diseño técnico directamente — eso lo hace el agente especializado.

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
   - Si hay `[CRÍTICO]_(pendiente)_` (en sección Items Pendientes del spec) → lista cuáles y **detén la ejecución**:
     > "❌ El Spec tiene X items [CRÍTICO] sin resolver. Responde los gaps críticos antes de generar el Plan."
   - Si el spec declara `status_sync: stale` o `status_sync: needs_review` → **detén la ejecución**:
     > "❌ El Spec no está sincronizado con la versión vigente del PRD. Ejecuta `wf-prd-sync-impact` o `wf-spec-sync-from-prd` antes de generar el Plan."
   - Si hay `[INFORMATIVO]_(pendiente)_` pero no `[INCOMPLETO]` ni `[CRÍTICO]` → advierte pero **continúa**:
     > "⚠ El Spec tiene X items [INFORMATIVO] sin responder. Se usarán los valores por defecto. Puedes responderlos después si quieres más precisión."
4. Verifica que el archivo parece un Spec validado (contiene "Criterios de Aceptación" e "Historias de Usuario"). Si parece un PRD sin procesar → informa:
   > "Este archivo no parece un Spec procesado. Primero ejecuta `/wf-spec-analyze <archivo.md>`"

---

## Paso 3: Leer el contenido

Lee el `_spec.md` en su totalidad.

Busca si existe un `_features.md` en el proyecto. Para encontrarlo:
- Si el spec está en `features/<nombre>/`, busca `../../*_features.md` (dos niveles arriba)
- Si el spec está en el directorio raíz, busca `*_features.md` en ese mismo directorio

Si existe el `_features.md`, léelo completo. Lo usarás en el paso siguiente.

Si el spec está dentro de `features/<nombre>/` pero **no se encuentra `_features.md`**, advierte al usuario:
> "⚠ No se encontró `_features.md`. Si este proyecto tiene múltiples features que comparten modelos de dominio, los shared models no se considerarán en el Plan y podrían redefinirse en cada feature. Para gestionar shared models correctamente, usa `/wf-spec-features-first` o `/wf-spec-discover` para identificar features y shared models. Continuando sin shared models."

---

## Paso 4: Delegar al agente plan-architect

Construye el prompt para el agente:

**Si NO existe `_features.md`** (proyecto sin descomposición multi-feature):
```
Path del spec: <path_completo>
Contenido del Spec:
---
<contenido_completo_del_spec>
---
INSTRUCCIÓN: Propaga al header del Plan cualquier metadata de trazabilidad presente en el Spec (`derived_from_prd`, `derived_from_prd_version`, `derived_from_change`, `status_sync`). Si falta, usa `unknown`.
```

**Si SÍ existe `_features.md`** (proyecto multi-feature):
```
Path del spec: <path_completo>
Contenido del Spec:
---
<contenido_completo_del_spec>
---

Shared models del proyecto (NO redefinir — solo referenciar):
---
<sección "Tabla de shared models" del _features.md>
---
INSTRUCCIÓN: Si algún modelo de la tabla anterior aparece en el Spec de esta feature,
NO lo redefinas en el Plan. Declara que lo usa esta feature y apunta a su feature owner.
Si esta feature ES la owner del modelo, defínelo completamente en el Domain Layer.
INSTRUCCIÓN: Propaga al header del Plan cualquier metadata de trazabilidad presente en el Spec (`derived_from_prd`, `derived_from_prd_version`, `derived_from_change`, `status_sync`). Si falta, usa `unknown`.
```

Invoca el agente `plan-architect` con el prompt construido.

Espera a que el agente complete su ejecución y recibe su output.

---

## Paso 5: Manejar TECH_GAPs

Si el agente devuelve TECH_GAPs en su output:
- Informa al usuario los gaps detectados con su descripción
- No escribas ningún archivo de salida
- Siguiente paso sugerido:
  > "Responde los TECH_GAPs añadiendo los detalles que faltan al Spec y vuelve a ejecutar `/wf-prepare-plan generate <spec.md>`"

Si no hay TECH_GAPs → continúa al paso 6.

---

## Paso 6: Escribir el resultado

Determina el path de salida:
- Mismo directorio + nombre base + `_plan.md`
- Ejemplo: `docs/login_spec.md` → `docs/login_plan.md`

Escribe el output del agente en ese archivo.

---

## Paso 7: Informar al usuario

- Path del Plan generado
- Resumen: módulos creados, número de UseCases, número de CAs cubiertos
- Si hay observaciones o puntos a revisar: cuáles
- Siguiente paso: "Revisa `<path>_plan.md` y si todo es correcto ejecuta `/wf-prepare-tasks generate <path>_plan.md`"
