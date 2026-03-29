---
name: prepare-plan
description: Orquestador SDD para transformar Specs validados en Planes técnicos KMM. Úsalo cuando tengas un _spec.md sin items pendientes y quieras generar el plan técnico de implementación. Activa en frases como "genera el plan desde el spec", "crea el plan técnico", "transforma el spec en plan", "planifica la implementación de", "prepara el plan para". No activa para analizar o generar Specs (usa prepare-spec) ni para crear Tasks (usa prepare-tasks).
argument-hint: "generate <spec.md>"
effort: high
allowed-tools: [Read, Write, Agent]
disable-model-invocation: true
---

# prepare-plan — Orquestador del Flujo SDD (Etapa 2)

Tu rol es de **orquestador puro**: parseas argumentos, verificas que el Spec está listo, delegas la arquitectura al agente `plan-architect`, y escribes el output resultante. No realizas el diseño técnico directamente — eso lo hace el agente especializado.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (solo `generate` está soportado)
- **Path del archivo**: el resto del argumento

Si no hay argumento o el modo no es válido, informa al usuario:
> "Uso: `/prepare-plan generate <archivo_spec.md>`"

Ejemplo:
- `generate docs/login_spec.md` → modo=generate, archivo=docs/login_spec.md

---

## Paso 2: Verificar el Spec

1. Verifica que el archivo existe.
2. Lee el archivo completo.
3. Comprueba que no contiene items `_(pendiente)_` sin responder. Si los hay → lista cuáles y detén:
   > "El Spec tiene X items pendientes. Completa el análisis antes de generar el Plan."
4. Verifica que el archivo parece un Spec validado (contiene "Criterios de Aceptación" o "Historias de Usuario"). Si parece un PRD sin procesar → informa:
   > "Este archivo no parece un Spec procesado. Primero ejecuta `/prepare-spec analyze <archivo.md>`"

---

## Paso 3: Leer el contenido

Lee el `_spec.md` en su totalidad.

---

## Paso 4: Delegar al agente plan-architect

Invoca el agente `plan-architect` pasándole como prompt:

```
Path del spec: <path_completo>
Contenido del Spec:
---
<contenido_completo_del_spec>
---
```

Espera a que el agente complete su ejecución y recibe su output.

---

## Paso 5: Manejar TECH_GAPs

Si el agente devuelve TECH_GAPs en su output:
- Informa al usuario los gaps detectados con su descripción
- No escribas ningún archivo de salida
- Siguiente paso sugerido:
  > "Responde los TECH_GAPs añadiendo los detalles que faltan al Spec y vuelve a ejecutar `/prepare-plan generate <spec.md>`"

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
- Siguiente paso: "Revisa `<path>_plan.md` y si todo es correcto ejecuta `/prepare-tasks generate <path>_plan.md`"
