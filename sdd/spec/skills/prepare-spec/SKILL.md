---
name: prepare-spec
description: Orquestador SDD para transformar documentos de requisitos en Specs válidos. Cuatro modos — 'analyze' genera un informe de gaps y preguntas para el cliente; 'finalize' genera el .spec monolítico final tras la validación humana; 'validate' audita un _spec.md existente sin generar archivos; 'fast-track' genera directamente el spec de una sola capability sin pasar por el monolito. Activa en frases como "prepara el spec de", "analiza este documento para el spec", "convierte este .md en spec", "¿qué le falta a este doc para ser spec?", "genera el spec final", "transforma este documento en spec", "valida el spec", "comprueba si el spec sigue siendo válido", "genera el spec directo de esta feature", "fast-track del spec".
argument-hint: "analyze <archivo.md> | finalize <archivo.md> | validate <archivo_spec.md> | fast-track <archivo.md> --capability <nombre-kebab>"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
disable-model-invocation: true
---

# prepare-spec — Orquestador del Flujo SDD

Tu rol es de **orquestador puro**: parseas argumentos, verificas archivos, delegas el trabajo analítico al agente `sdd-analyst`, y escribes el output resultante. No realizas el análisis ni la generación del spec directamente — eso lo hace el agente especializado.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: la primera palabra (`analyze`, `finalize`, `validate` o `fast-track`)
- **Path del archivo**: el argumento después del modo
- **En modo `fast-track`**: extrae también `--capability <nombre>` del argumento. Si falta, informa: "Uso: `/prepare-spec fast-track <archivo.md> --capability <nombre-kebab-case>`"

Si no hay argumento o el modo no es válido, informa al usuario:
> "Uso: `/prepare-spec analyze <archivo.md>` | `/prepare-spec finalize <archivo.md>` | `/prepare-spec validate <archivo_spec.md>` | `/prepare-spec fast-track <archivo.md> --capability <nombre>`"

Ejemplos:
- `analyze docs/login.md` → modo=analyze, archivo=docs/login.md
- `finalize src/specs/notificaciones.md` → modo=finalize, archivo=src/specs/notificaciones.md
- `validate src/specs/notificaciones_spec.md` → modo=validate, archivo=src/specs/notificaciones_spec.md
- `fast-track docs/push-notifications.md --capability push-notifications` → modo=fast-track, archivo=docs/push-notifications.md, capability=push-notifications

---

## Paso 2: Verificar archivos

Verifica que el archivo principal existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y detén.

En modo `finalize`, verifica también que existe el archivo de análisis. Búscalo en este orden:
1. `<nombre_base>_analysis.md` en el mismo directorio (nombre canónico)
2. Si no existe, busca cualquier `*_analysis.md` en el mismo directorio y usa el más reciente
3. Si tampoco existe ninguno → informa: "No se encontró un archivo de análisis. Primero ejecuta `/prepare-spec analyze <archivo.md>` para generarlo, o especifica el path del análisis si está en otra ubicación."

En modo `validate`, verifica que el archivo termina en `_spec.md`. Si no → informa: "El modo validate espera un spec generado (`_spec.md`). Para analizar un PRD usa `/prepare-spec analyze`."

En modo `fast-track`, solo verifica que el archivo de entrada existe. No requiere `_analysis.md` previo.

---

## Paso 3: Leer el contenido

Lee el archivo principal en su totalidad.

En modo `finalize`, lee también el `_analysis.md` completo.

En modo `finalize`, comprueba la severidad de los items pendientes:
- Si hay items `[CRÍTICO]_(pendiente)_` sin respuesta → lista cuáles y detén: "Hay gaps **críticos** sin responder en `_analysis.md`. Son obligatorios para continuar."
- Si solo hay items `[INFORMATIVO]_(pendiente)_` → informa al usuario que se aplicarán las asunciones por defecto y **permite continuar** (el agente aplicará las asunciones en el spec generado).

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

**Para modo `fast-track`:**
```
Modo: fast-track
Capability: <nombre-kebab-case>
Path del archivo: <path_completo>
Contenido del documento:
---
<contenido_completo_del_archivo>
---
```

Espera a que el agente complete su ejecución y recibe su output estructurado.

---

## Paso 5: Escribir el resultado (o imprimir para validate)

Determina el path de salida:
- Modo `analyze`: mismo directorio + nombre base + `_analysis.md` (ej: `docs/login.md` → `docs/login_analysis.md`)
- Modo `finalize`: mismo directorio + nombre base + `_spec.md` (ej: `docs/login.md` → `docs/login_spec.md`)
- Modo `validate`: **no escribir ningún archivo** — imprimir directamente el informe del agente al usuario.
- Modo `fast-track`: escribe los 3 artefactos siguientes (crea directorios si no existen):
  1. **Spec**: `features/<capability>/<capability>_spec.md` relativo al directorio del archivo de entrada (ej: `docs/push.md` con `--capability push-notifications` → `docs/features/push-notifications/push-notifications_spec.md`)
  2. **README**: `features/<capability>/README.md` con el contenido del bloque `--- README ---` del output del agente
  3. **Índice de features**: escribe el `_features.md` en el path indicado por el bloque `--- FEATURES_INDEX_PATH ---` del output del agente, con el contenido del bloque `--- FEATURES_INDEX ---`

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

**Tras fast-track:**
- Path del spec generado
- Path del README generado
- Path del `_features.md` creado o actualizado (indicar si era nuevo o actualización)
- Si hay items `[CRÍTICO]` pendientes en el spec: listarlos y advertir que bloquean `/prepare-plan`
- Si se aplicaron asunciones: mencionar cuántas y dónde están documentadas en el spec
- Siguiente paso: "Revisa el spec generado. Si está listo, continúa con `/prepare-plan generate <path>_spec.md`"
