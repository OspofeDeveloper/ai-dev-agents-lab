---
name: prepare-spec
description: Orquestador SDD para transformar documentos de requisitos en Specs válidos. Úsalo cuando tengas un .md con requisitos, un PRD informal, o notas de reunión y quieras convertirlo en un Spec SDD limpio. Dos modos: 'analyze' genera un informe de gaps y preguntas para el cliente; 'finalize' genera el .spec final tras la validación humana. Activa en frases como "prepara el spec de", "analiza este documento para el spec", "convierte este .md en spec", "¿qué le falta a este doc para ser spec?", "genera el spec final", "transforma este documento en spec".
argument-hint: "analyze <archivo.md> | finalize <archivo.md>"
effort: high
allowed-tools: [Read, Write, Agent]
disable-model-invocation: true
---

# prepare-spec — Orquestador del Flujo SDD

Tu rol es de **orquestador puro**: parseas argumentos, verificas archivos, delegas el trabajo analítico al agente `sdd-analyst`, y escribes el output resultante. No realizas el análisis ni la generación del spec directamente — eso lo hace el agente especializado.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (`analyze` o `finalize`)
- **Path del archivo**: el resto del argumento

Si no hay argumento o el modo no es válido, informa al usuario:
> "Uso: `/prepare-spec analyze <archivo.md>` o `/prepare-spec finalize <archivo.md>`"

Ejemplos:
- `analyze docs/login.md` → modo=analyze, archivo=docs/login.md
- `finalize src/specs/notificaciones.md` → modo=finalize, archivo=src/specs/notificaciones.md

---

## Paso 2: Verificar archivos

Verifica que el archivo principal existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y detén.

En modo `finalize`, verifica también que existe `<nombre_base>_analysis.md` en el mismo directorio. Si no existe → informa: "Primero ejecuta `/prepare-spec analyze <archivo.md>` para generar el análisis."

---

## Paso 3: Leer el contenido

Lee el archivo principal en su totalidad.

En modo `finalize`, lee también el `_analysis.md` completo.

En modo `finalize`, comprueba si hay items con `_(pendiente)_` sin respuesta. Si los hay, lista cuáles y detén: "Completa las respuestas pendientes en `_analysis.md` antes de continuar."

---

## Paso 4: Delegar al agente sdd-analyst

Invoca el agente `sdd-analyst` pasándole como prompt el siguiente bloque (con los valores reales sustituidos):

**Para modo `analyze`:**
```
Modo: analyze
Path del archivo: <path_completo>
Contenido del documento:
---
<contenido_completo_del_archivo>
---
```

**Para modo `finalize`:**
```
Modo: finalize
Path del archivo original: <path_completo>
Contenido del documento original:
---
<contenido_del_archivo_original>
---
Contenido del análisis completado:
---
<contenido_completo_del_analysis.md>
---
```

Espera a que el agente complete su ejecución y recibe su output estructurado.

---

## Paso 5: Escribir el resultado

Determina el path de salida:
- Modo `analyze`: mismo directorio + nombre base + `_analysis.md` (ej: `docs/login.md` → `docs/login_analysis.md`)
- Modo `finalize`: mismo directorio + nombre base + `_spec.md` (ej: `docs/login.md` → `docs/login_spec.md`)

Escribe el output del agente en ese archivo.

---

## Paso 6: Informar al usuario

**Tras analyze:**
- Path del archivo generado
- Resumen: cuántos elementos de completitud faltan, cuántas contaminaciones, cuántos `[P-XXX]` pendientes
- Siguiente paso: "Edita `<path>_analysis.md`, responde las preguntas marcadas como _(pendiente)_ y luego ejecuta `/prepare-spec finalize <archivo.md>`"

**Tras finalize:**
- Path del spec generado
- Estado de los 6 elementos SDD
- Si hay items `[PENDIENTE]` restantes: cuántos y cuáles
- Sugerencia: "Valida el resultado con `/spec-expert revisar <path>_spec.md`"
