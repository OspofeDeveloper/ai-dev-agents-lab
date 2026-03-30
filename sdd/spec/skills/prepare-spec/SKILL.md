---
name: prepare-spec
description: Orquestador SDD para transformar documentos de requisitos en Specs válidos. Tres modos — 'analyze' genera un informe de gaps y preguntas para el cliente; 'finalize' genera el .spec final tras la validación humana; 'validate' audita un _spec.md existente sin generar archivos. Activa en frases como "prepara el spec de", "analiza este documento para el spec", "convierte este .md en spec", "¿qué le falta a este doc para ser spec?", "genera el spec final", "transforma este documento en spec", "valida el spec", "comprueba si el spec sigue siendo válido".
argument-hint: "analyze <archivo.md> | finalize <archivo.md> | validate <archivo_spec.md>"
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
> "Uso: `/prepare-spec analyze <archivo.md>` | `/prepare-spec finalize <archivo.md>` | `/prepare-spec validate <archivo_spec.md>`"

Ejemplos:
- `analyze docs/login.md` → modo=analyze, archivo=docs/login.md
- `finalize src/specs/notificaciones.md` → modo=finalize, archivo=src/specs/notificaciones.md
- `validate src/specs/notificaciones_spec.md` → modo=validate, archivo=src/specs/notificaciones_spec.md

---

## Paso 2: Verificar archivos

Verifica que el archivo principal existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y detén.

En modo `finalize`, verifica también que existe `<nombre_base>_analysis.md` en el mismo directorio. Si no existe → informa: "Primero ejecuta `/prepare-spec analyze <archivo.md>` para generar el análisis."

En modo `validate`, verifica que el archivo termina en `_spec.md`. Si no → informa: "El modo validate espera un spec generado (`_spec.md`). Para analizar un PRD usa `/prepare-spec analyze`."

---

## Paso 3: Leer el contenido

Lee el archivo principal en su totalidad.

En modo `finalize`, lee también el `_analysis.md` completo.

En modo `finalize`, comprueba si hay items con `_(pendiente)_` sin respuesta. Si los hay, lista cuáles y detén: "Completa las respuestas pendientes en `_analysis.md` antes de continuar."

En modo `validate`, lee el `_spec.md` en su totalidad.

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

**Para modo `validate`:**
```
Modo: validate
Path del archivo: <path_completo>
Contenido del spec:
---
<contenido_completo_del_spec>
---
```

Espera a que el agente complete su ejecución y recibe su output estructurado.

---

## Paso 5: Escribir el resultado (o imprimir para validate)

Determina el path de salida:
- Modo `analyze`: mismo directorio + nombre base + `_analysis.md` (ej: `docs/login.md` → `docs/login_analysis.md`)
- Modo `finalize`: mismo directorio + nombre base + `_spec.md` (ej: `docs/login.md` → `docs/login_spec.md`)
- Modo `validate`: **no escribir ningún archivo** — imprimir directamente el informe del agente al usuario.

Para `analyze` y `finalize`, escribe el output del agente en el archivo correspondiente.

---

## Paso 6: Informar al usuario

**Tras analyze:**
- Path del archivo generado
- Resumen: cuántos elementos de completitud faltan, cuántas contaminaciones, cuántos `[P-XXX]` pendientes
- Siguiente paso: "Edita `<path>_analysis.md`, responde las preguntas marcadas como _(pendiente)_ y luego ejecuta `/prepare-spec finalize <archivo.md>`"

**Tras finalize:**
- Path del spec generado
- Estado de los 8 elementos SDD (incluye Actores y Fuera de Alcance)
- Si hay items `[PENDIENTE]` restantes: cuántos y cuáles
- Siguiente paso: "Si editas el spec manualmente, puedes re-validarlo con `/prepare-spec validate <path>_spec.md`"

**Tras validate:**
- Imprime el informe directamente (no genera ningún archivo)
- Si el resultado es REQUIERE_REVISIÓN: indica los problemas encontrados y sugiere corregirlos manualmente antes de pasar a la fase siguiente
