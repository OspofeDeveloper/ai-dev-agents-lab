---
name: wf-spec-fast-track
description: Genera el Spec de una feature directamente desde un documento de requisitos acotado a una sola capacidad. Soporta modo scoped con --scope-from para filtrar un PRD completo a una feature del discovery. Acepta --analysis para usar gaps pre-resueltos de un analisis previo. Activa en frases como "genera el spec directo de esta feature", "fast-track del spec", "crea el spec de esta capability directamente", "genera spec sin análisis previo".
argument-hint: "<archivo.md> --capability <nombre-kebab> [--analysis <analysis.md>] | <prd.md> --scope-from <discovery.md> --feature <F-00X> [--analysis <analysis.md>]"
effort: high
allowed-tools: [Read, Write, Bash]
agent: sdd-spec-writer
---

# Workflow: FAST-TRACK

Tu objetivo es generar un Spec de feature SDD completo y válido directamente desde un documento de requisitos enfocado en una sola capacidad. Usa `kb-spec-expert` para garantizar pureza y los 8 elementos, y `kb-decompose-expert` para verificar que el scope es el de una sola feature válida.

**Dos modos de operación:**
- **Modo directo** (`--capability`): el documento de entrada está acotado a una sola capacidad. Es el modo original.
- **Modo scoped** (`--scope-from` + `--feature`): el documento de entrada es un PRD completo, pero se filtra a una sola feature usando el scope definido en un `_discovery.md` previo generado por `/wf-spec-discover`.

**Cuándo usar fast-track vs. flujo estándar:**
- Fast-track es para documentar **una sola capacidad** en un proyecto donde el resto ya está documentado (o no se quiere documentar todavía).
- En modo scoped, fast-track opera sobre un PRD completo pero restringido al scope de una feature del discovery.
- Si el documento describe múltiples capacidades independientes y no hay `--scope-from` → informar que debe usar el flujo estándar o `/wf-spec-discover` primero.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del archivo**: el primer argumento
- **Modo directo**: si hay `--capability` → extraer el nombre de la capability
- **Modo scoped**: si hay `--scope-from` y `--feature` → extraer el path del `_discovery.md` y el Feature ID (ej: `F-001`)
- **Flag opcional**: `--analysis <path>` → path a un `_analysis.md` con gaps pre-resueltos

**Validación de argumentos:**
- Si hay `--scope-from` sin `--feature` (o viceversa) → informa: "Los flags `--scope-from` y `--feature` deben usarse juntos."
- Si no hay ni `--capability` ni `--scope-from` → informa:
> "Uso modo directo: `/wf-spec-fast-track <archivo.md> --capability <nombre-kebab-case>`"
> "Uso modo scoped: `/wf-spec-fast-track <prd.md> --scope-from <discovery.md> --feature <F-00X>`"

---

## Paso 2: Verificar el archivo

Verifica que el archivo existe:
```
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
```

Si no existe → informa al usuario con la ruta exacta y detén.

---

## Paso 3: Leer el contenido

Lee el archivo de entrada en su totalidad.

**Si modo scoped:** lee también el `_discovery.md` indicado en `--scope-from`. Extrae del discovery:
- El bloque de la feature indicada por `--feature` (ej: `F-001`)
- El **nombre kebab-case** de la feature → se usa como `capability` para el resto del flujo
- La lista de **Scope (RFs)** → los IDs de RF que pertenecen a esta feature
- La lista de **Scope (secciones PRD)** → las secciones del PRD relevantes
- Los **shared models** declarados para esta feature (owner y ref)

Si el Feature ID no existe en el discovery → informa:
> "El feature `<F-00X>` no existe en `<discovery.md>`. Features disponibles: [lista]."

---

## Paso 4: Scope Check

### Modo directo (--capability)

Verifica que el documento describe una única capability SDD válida. Consulta `kb-decompose-expert` para los criterios:
- Actor principal identificable
- Journeys funcionalmente independientes de otras features potenciales
- Al menos 3 CAs verificables asumibles (incluso si el documento no los tiene todos explícitos, deben ser derivables con asunciones razonables)

Si el documento claramente describe **múltiples features independientes** → devuelve:
> "Este documento describe [N] capacidades distintas: [lista]. Para documentar todas, usa `/wf-spec-discover <archivo.md>` para identificar features y luego `/wf-spec-features-first <archivo.md>` para generar los specs. Para una sola, extrae solo esa capacidad en un documento separado y vuelve a ejecutar fast-track."

Si el scope es ambiguo pero asumible → aplícalo con una asunción [INFORMATIVO] documentada.

### Modo scoped (--scope-from + --feature)

**No aplica el check de multi-feature.** El scope ya fue definido por `/wf-spec-discover` y validado por el usuario. En su lugar:

1. Filtra mentalmente el PRD a solo los RFs y secciones listados en el scope de la feature
2. Lee el PRD completo para entender el contexto general, pero **solo genera HUs/CAs para los RFs del scope de esta feature**
3. Verifica que el scope filtrado contiene suficiente información para generar un spec válido (actor identificable, journeys derivables, mínimo 3 CAs)
4. Si la información es insuficiente → informa: "El scope del feature `<F-00X>` en el PRD no contiene suficiente información funcional para generar un spec válido. Revisa el `_discovery.md` y ajusta el scope."

---

## Paso 5: Análisis compacto (inline)

**Si se proporcionó `--analysis`**: lee el `_analysis.md` primero. Extrae todos los gaps respondidos (donde "Respuesta" no es `_(pendiente)_`). Durante los checks siguientes, antes de crear un gap nuevo:
1. Busca en el analysis si la misma pregunta o contexto ya fue respondido
2. Si fue respondido → usa la respuesta del cliente directamente, no crees gap ni marques `[INCOMPLETO]`
3. Si no fue respondido (sigue como `_(pendiente)_`) → procede como si no hubiera analysis (crea gap `[CRÍTICO]` y marca HU como `[INCOMPLETO]`)
4. Si el inline analysis detecta un gap que no existe en el analysis previo → créalo normalmente

Aplica los 3 checks del modo ANALYZE pero enfocados en la capability indicada:

**Check 1 — Completitud**: verifica los 8 elementos. Identifica cuáles están presentes, cuáles son derivables con asunciones razonables y cuáles requieren respuesta del cliente.

**Check 2 — Pureza**: consulta `prohibited_items.md` del skill `kb-spec-expert`. Propón reescrituras funcionales para cualquier contaminación técnica encontrada.

**Check 3 — Testabilidad**: verifica que los CAs son verificables con GIVEN/WHEN/THEN completo.

---

## Paso 6: Gap handling inline

No genera un `_analysis.md` separado. Consulta `kb-gap-conventions` para el formato de IDs `[P-XXX]`, severidades, marcador `_(pendiente)_` y campo `Afecta`. Los gaps se gestionan directamente en el spec:

- **`[CRÍTICO]`**: determina qué HUs afecta (campo `Afecta`). Las HUs afectadas se marcan `[INCOMPLETO]` en el spec (se generan con la información disponible). La presencia de HUs `[INCOMPLETO]` en el spec **bloquea** la ejecución de `/wf-prepare-plan`. Los gaps se documentan en una sección `## Items Pendientes` al final del spec (ver formato abajo).
- **`[INFORMATIVO]`**: aplicar la asunción más conservadora y documentar en `## Asunciones Aplicadas` al final del spec.

---

## Paso 7: Generar el Spec de feature

Produce un `_spec.md` completo con los 8 elementos SDD siguiendo la estructura de `references/feature_spec_template.md`.

**Header específico del fast-track (modo directo):**
```markdown
# Spec: [Nombre de la Capability]
> Versión: 1.0 | Fecha: [YYYY-MM-DD]
> Generado via: fast-track desde [path/del/documento.md]
> Feature ID: F-001
> Spec monolítico origen: N/A (fast-track directo)
> Source requirements: [path/del/documento.md]
> derived_from_prd: N/A
> derived_from_prd_version: N/A
> derived_from_change: N/A
> status_sync: unknown
```

**Header específico del fast-track (modo scoped):**
```markdown
# Spec: [Nombre de la Capability]
> Versión: 1.0 | Fecha: [YYYY-MM-DD]
> Generado via: fast-track desde [path/del/prd.md] (scope: F-00X via [discovery.md])
> Feature ID: F-00X
> Spec monolítico origen: N/A (features-first via discover)
> Source requirements: [path/del/prd.md]
> derived_from_prd: [path/del/prd.md]
> derived_from_prd_version: [versión del PRD o unknown]
> derived_from_change: [CR-XXX | N/A]
> status_sync: in_sync
```

**Si hay items `[CRÍTICO]` pendientes**, añadir al final del spec (antes del Changelog si existiera):
```markdown
## Items Pendientes

> ⚠️ Este spec tiene gaps **críticos** sin resolver. Las HUs afectadas están marcadas `[INCOMPLETO]` y `/wf-prepare-plan` quedará bloqueado hasta que se resuelvan.
> Para resolverlos: responde los gaps en el `_analysis.md` y ejecuta `/wf-spec-gap-resolve <path>_spec.md`.

### [P-001][CRÍTICO] [Título del gap]
- **Afecta**: [HU-001, HU-003]
- **Pregunta**: [pregunta concreta]
- **Respuesta**: _(pendiente)_
```

**Si hay asunciones aplicadas**, añadir:
```markdown
## Asunciones Aplicadas

- **[A-001]**: [descripción de la asunción aplicada y su justificación]
```

---

## Paso 8: Validar el spec generado

Antes de escribir el output, aplica la Prueba de Pureza al spec completo. Consulta `kb-spec-expert`. Si hay contaminación técnica introducida durante la generación, corrígela antes de continuar.

---

## Paso 9: Generar artefactos de índice

**README de la feature**: Genera el contenido completo de `features/<capability>/README.md` siguiendo `references/feature_readme_template.md`. Usa los datos del spec recién generado:
- Feature ID: F-001 si `_features.md` no existe, o el siguiente ID disponible si existe
- Actor principal: extraído del spec
- Spec monolítico origen: `N/A (fast-track directo)`
- Artefactos: Spec ✓, Plan —, Tasks —

**Índice de features (`_features.md`)**: Busca si existe algún `*_features.md` en el directorio del archivo de input:
- **Si existe**: léelo y añade la nueva feature como entrada `F-00X` (con el siguiente ID disponible). Actualiza la tabla de shared models si la feature declara alguno.
- **Si no existe**: genera un `_features.md` nuevo con esta feature como primera entrada `F-001`, sin spec monolítico origen y sin tabla de shared models si no hay ninguno.

**Trazabilidad RF→HU (solo modo scoped):** Si se usó `--scope-from`, el discovery contiene el mapping RF→Feature. Al actualizar `_features.md`, añade o actualiza la sección `## Trazabilidad RF → HU → Feature` con las filas correspondientes a esta feature: para cada RF del scope, mapea las HUs generadas en este spec. Si la sección ya existía (de una ejecución previa de fast-track para otra feature), añade las filas nuevas sin eliminar las existentes.

---

## Paso 10: Escribir los artefactos

Escribe los 3 artefactos (crea directorios si no existen), todos relativos al directorio del archivo de entrada:

1. **Spec**: `features/<capability>/<capability>_spec.md`
2. **README**: `features/<capability>/README.md`
3. **Features index**: `<nombre_base>_features.md` en el directorio del archivo de entrada (o actualiza el existente)

---

## Paso 11: Informar al usuario

Tras escribir los artefactos, informa:
- Path del spec generado
- Path del README generado
- Path del `_features.md` creado o actualizado (indicar si era nuevo o actualización)
- Si hay items `[CRÍTICO]` pendientes en el spec: listarlos y advertir que bloquean `/wf-prepare-plan`
- Si se aplicaron asunciones: mencionar cuántas y dónde están documentadas en el spec
- Siguiente paso: "Revisa el spec generado. Si está listo, continúa con `/wf-prepare-plan generate <path>_spec.md`"
