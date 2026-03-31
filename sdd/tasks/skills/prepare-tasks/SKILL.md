---
name: prepare-tasks
description: Orquestador SDD para transformar Planes técnicos KMM en Tasks de implementación. Úsalo cuando tengas un _plan.md validado y quieras generar el listado de tasks para ejecutar con las skills KMM. Activa en frases como "genera las tasks del plan", "trocéa el plan en tasks", "crea el listado de implementación", "prepara las tasks para", "¿qué tasks tengo que hacer?". No activa para generar Specs (usa prepare-spec) ni para generar Planes (usa prepare-plan).
argument-hint: "generate <plan.md>"
effort: high
allowed-tools: [Read, Write, Agent]
disable-model-invocation: true
context: fork
agent: task-generator
---

# prepare-tasks — Orquestador del Flujo SDD (Etapa 3)

Tu rol es de **orquestador puro**: parseas argumentos, verificas que el Plan está listo, delegas la descomposición al agente `task-generator`, y escribes el output resultante. No realizas la descomposición directamente — eso lo hace el agente especializado.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (solo `generate` está soportado)
- **Path del archivo**: el resto del argumento

Si no hay argumento o el modo no es válido, informa al usuario:
> "Uso: `/prepare-tasks generate <archivo_plan.md>`"

Ejemplo:
- `generate docs/login_plan.md` → modo=generate, archivo=docs/login_plan.md

---

## Paso 2: Verificar el Plan

1. Verifica que el archivo existe.
2. Lee el archivo completo.
3. Comprueba que no contiene `[TECH_GAP]` sin resolver. Si los hay → lista cuáles y detén:
   > "El Plan tiene X TECH_GAPs sin resolver. Actualiza el Spec y regenera el Plan antes de crear Tasks."
4. Verifica que el archivo parece un Plan técnico (contiene "Domain Layer" o "Checklist de Trazabilidad"). Si no → informa:
   > "Este archivo no parece un Plan técnico. Primero ejecuta `/prepare-plan generate <spec.md>`"

---

## Paso 3: Leer el contenido

Lee el `_plan.md` en su totalidad.

---

## Paso 4: Delegar al agente task-generator

Invoca el agente `task-generator` con el siguiente prompt:

```
Path del plan: <path_completo>
Contenido del Plan:
---
<contenido_completo_del_plan>
---
```

Espera a que el agente complete su ejecución y recibe su output.

---

## Paso 5: Escribir el resultado

Determina el path de salida:
- Mismo directorio + nombre base + `_tasks.md`
- Ejemplo: `docs/login_plan.md` → `docs/login_tasks.md`

Escribe el output del agente en ese archivo.

---

## Paso 6: Informar al usuario

- Path del archivo de tasks generado
- Resumen: total de tasks, desglose por fase (scaffold/domain/data/presentation/tests)
- Orden recomendado de ejecución
- Siguiente paso: "Ejecuta las tasks en orden empezando por T-000 con `/kmm-scaffold`"
