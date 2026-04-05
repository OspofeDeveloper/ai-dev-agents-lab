---
name: wf-spec-discover
description: Analiza un PRD e identifica features candidatas por cohesión funcional. Genera un _discovery.md con el mapa de features, scope por feature y shared models. No genera specs — solo el roadmap para ejecutar wf-spec-fast-track por feature. Activa en frases como "identifica features del PRD", "descubre las features", "qué features tiene este PRD", "mapa de features", "features-first", "qué features hay en este documento".
argument-hint: "<prd_archivo.md> [--analysis <analysis.md>]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-analyst
---

# Workflow: DISCOVER

Tu objetivo es leer un PRD y producir un mapa de features candidatas con su scope, sin generar ningún spec. Usa `kb-decompose-expert` para las reglas de identificación de features y shared models.

**Regla de oro:** No generas specs, no generas HUs, no generas CAs completos. Solo identificas features, validas que cumplen los 3 criterios, asignas shared models y mapeas qué parte del PRD corresponde a cada feature.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del PRD**: el primer argumento
- **Flag opcional**: `--analysis <path>` — path a un `_analysis.md` generado previamente por `/wf-spec-analyze`

Si no hay argumento, informa al usuario:
> "Uso: `/wf-spec-discover <prd_archivo.md> [--analysis <analysis.md>]`"
> "Ejemplo: `/wf-spec-discover docs/requisitos.md --analysis docs/requisitos_analysis.md`"

---

## Paso 2: Verificar el archivo

Verifica que el archivo existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y detén.

Si el nombre termina en `_spec.md` → informa:
> "Este archivo parece un Spec ya procesado. `/wf-spec-discover` opera sobre PRDs o documentos de requisitos, no sobre specs."

---

## Paso 3: Leer el contenido

Lee el archivo PRD en su totalidad.

**Si se proporcionó `--analysis`**: lee también el `_analysis.md`. Extrae los gaps respondidos (donde el campo "Respuesta" no es `_(pendiente)_`). Las respuestas del cliente se usan como contexto adicional para:
- **Paso 5**: identificar features con mayor precisión (las respuestas pueden clarificar scopes ambiguos)
- **Paso 7**: asignar shared models (las respuestas pueden aclarar ownership)

Los gaps sin responder (`_(pendiente)_`) se ignoran en discover — no bloquean la identificación de features.

---

## Paso 4: Identificar Requisitos Funcionales (RFs)

Escanea el PRD para extraer los requisitos funcionales:

- **Si el PRD tiene RFs numerados explícitamente** (ej: "RF-4 Control Horario"): usa esos IDs y títulos directamente.
- **Si el PRD tiene secciones funcionales sin numeración** (ej: "## Control Horario"): crea IDs RF-001, RF-002... basándose en los títulos de sección y marca en el output: `> Los IDs de RF son inferidos de las secciones funcionales del PRD — el documento original no los numera explícitamente.`
- **Si el PRD no tiene estructura clara**: agrupa el contenido por tema funcional, crea IDs RF sintéticos y añade la misma nota.

Registra para cada RF: ID, título y sección/párrafo del PRD donde aparece.

---

## Paso 5: Identificar features candidatas

Consulta `kb-decompose-expert` y aplica el algoritmo de identificación por cohesión funcional:

1. **Identifica todos los actores distintos** mencionados en el PRD
2. **Para cada actor, identifica sus objetivos principales**
3. **Agrupa por objetivo**: un objetivo principal = una feature candidata
4. **Nombra cada candidata** en kebab-case descriptivo (ej: `appointment-management`, `time-tracking`)

**Nota:** Aquí trabajas con un PRD crudo, no con un spec validado. No existen HUs ni CAs formales aún. Debes razonar sobre:
- **Journeys anticipados**: qué recorridos de usuario se pueden prever a partir del PRD
- **CAs derivables**: qué criterios de aceptación verificables se podrían generar razonablemente

---

## Paso 6: Validar cada feature candidata

Para cada candidata, verifica los 3 criterios de `kb-decompose-expert`:

1. **Journeys independientes**: tiene al menos un journey anticipado que no depende de un journey de otra feature
2. **CAs derivables (mínimo 3)**: se pueden anticipar al menos 3 criterios de aceptación verificables a partir del contenido del PRD para esta feature
3. **Actor claro**: el actor principal y su objetivo están bien definidos

**Si una candidata no cumple los tres criterios:**
- Fusiona con la feature candidata funcionalmente más cercana
- Documenta la decisión de merge: candidata original, destino, y razón

---

## Paso 7: Shared models + ownership

Identifica modelos de dominio que aparecen en más de una feature candidata.

Para cada shared model, asigna ownership aplicando las reglas de `kb-decompose-expert` (en este orden):
1. **Creación explícita**: la feature cuyo scope del PRD describe la creación de la entidad
2. **Gestión completa**: la feature con operaciones CRUD completas
3. **Mayor cobertura**: la feature con más RFs que referencian la entidad
4. **Proximidad semántica**: la feature cuyo nombre es más cercano al modelo

### Ownership checkpoint

Si algún modelo tiene ownership ambiguo (empate tras aplicar los 4 criterios):
- Presenta la tabla al usuario con los modelos ambiguos y los candidatos
- Explica qué criterio aplicaste y por qué hay empate
- **Espera respuesta del usuario** antes de continuar

Si todos los modelos tienen owner claro → continúa directamente.

---

## Paso 8: Mapear scope PRD → Feature

Para cada feature validada, determina con precisión qué contenido del PRD le corresponde:

- **Scope (RFs)**: lista de IDs de RF que pertenecen a esta feature
- **Scope (secciones PRD)**: títulos de sección o párrafos del PRD que contienen la información relevante

Este mapeo es crítico: será usado por `wf-spec-fast-track` en modo scoped para filtrar el PRD y generar el spec de cada feature.

**Regla**: cada RF debe estar asignado a exactamente una feature. Si un RF abarca funcionalidad de dos features, descompón el RF en sub-RFs más específicos.

---

## Paso 9: Generar `_discovery.md`

Consulta [references/discovery_template.md](references/discovery_template.md) para la estructura exacta del artefacto.

Determina el path de salida: mismo directorio que el archivo de entrada + nombre base + `_discovery.md`.
- Ejemplo: `docs/requisitos.md` → `docs/requisitos_discovery.md`

Escribe el artefacto generado en ese path.

---

## Paso 10: Informar al usuario

Tras escribir el archivo, informa:
- Path del archivo generado
- Número de features identificadas
- Tabla resumen:

| Feature | Actor principal | RFs cubiertos | Shared models |
|---------|----------------|---------------|---------------|

- Si hubo merges: lista de candidatas fusionadas y razón
- Si hay shared models con ownership ambiguo pendiente de confirmación: listarlos
- Si se usó `--analysis`: "Se utilizó el análisis previo (`<path>`) como contexto adicional para la identificación de features."

**Siguiente paso** (mostrar siempre):

> Para generar todos los specs en paralelo:
> ```
> /wf-spec-features-first <prd.md>
> ```
>
> Para generar el spec de una feature individual:
> ```
> /wf-spec-fast-track <prd.md> --scope-from <path>_discovery.md --feature F-001
> ```
