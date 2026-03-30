---
name: spec-fast-track
description: Workflow interno para el modo FAST-TRACK del agente sdd-analyst. Define cómo generar un Spec de feature directamente desde un documento de requisitos acotado a una sola capacidad, sin pasar por el spec monolítico ni por el flujo analyze/finalize/decompose. Cargado como contexto por sdd-analyst — no invocar directamente.
allowed-tools: [Read]
disable-model-invocation: true
---

# Workflow: FAST-TRACK

Tu objetivo es generar un Spec de feature SDD completo y válido directamente desde un documento de requisitos enfocado en una sola capacidad. Usa `spec-expert` para garantizar pureza y los 8 elementos, y `decompose-expert` para verificar que el scope es el de una sola feature válida.

**Cuándo usar fast-track vs. flujo estándar:**
- Fast-track es para documentar **una sola capacidad** en un proyecto donde el resto ya está documentado (o no se quiere documentar todavía).
- Si el documento describe múltiples capacidades independientes → informar que debe usar el flujo estándar (`/prepare-spec analyze` → `finalize` → `/decompose-spec`).

---

## Qué debes hacer

### 1. Scope Check

Verifica que el documento describe una única capability SDD válida. Consulta `decompose-expert` para los criterios:
- Actor principal identificable
- Journeys funcionalmente independientes de otras features potenciales
- Al menos 3 CAs verificables asumibles (incluso si el documento no los tiene todos explícitos, deben ser derivables con asunciones razonables)

Si el documento claramente describe **múltiples features independientes** → devuelve:
> "Este documento describe [N] capacidades distintas: [lista]. Para documentar todas, usa `/prepare-spec analyze <archivo.md>` seguido de `/decompose-spec`. Para una sola, extrae solo esa capacidad en un documento separado y vuelve a ejecutar fast-track."

Si el scope es ambiguo pero asumible → aplícalo con una asunción [INFORMATIVO] documentada.

### 2. Análisis compacto (inline)

Aplica los 3 checks del modo ANALYZE pero enfocados en la capability indicada:

**Check 1 — Completitud**: verifica los 8 elementos. Identifica cuáles están presentes, cuáles son derivables con asunciones razonables y cuáles requieren respuesta del cliente.

**Check 2 — Pureza**: consulta `spec-expert/references/prohibited_items.md`. Propón reescrituras funcionales para cualquier contaminación técnica encontrada.

**Check 3 — Testabilidad**: verifica que los CAs son verificables con GIVEN/WHEN/THEN completo.

### 3. Gap handling inline

No genera un `_analysis.md` separado. Consulta `gap-conventions` para el formato de IDs `[P-XXX]`, severidades y marcador `_(pendiente)_`. Los gaps se gestionan directamente en el spec:

- **`[CRÍTICO]`**: incluir en una sección `## Items Pendientes` al final del spec generado (ver formato abajo). La presencia de items `[CRÍTICO]` en el spec **bloquea** la ejecución de `/prepare-plan`.
- **`[INFORMATIVO]`**: aplicar la asunción más conservadora y documentar en `## Asunciones Aplicadas` al final del spec.

### 4. Generar el Spec de feature

Produce un `_spec.md` completo con los 8 elementos SDD siguiendo la estructura de `references/feature_spec_template.md`.

**Header específico del fast-track:**
```markdown
# Spec: [Nombre de la Capability]
> Versión: 1.0 | Fecha: [YYYY-MM-DD]
> Generado via: fast-track desde [path/del/documento.md]
> Feature ID: F-001
> Spec monolítico origen: N/A (fast-track directo)
```

**Si hay items `[CRÍTICO]` pendientes**, añadir al final del spec (antes del Changelog si existiera):
```markdown
## Items Pendientes

> ⚠️ Este spec tiene gaps **críticos** sin resolver. `/prepare-plan` quedará bloqueado hasta que se resuelvan.
> Para resolverlos: edita este spec respondiendo los gaps, luego ejecuta `/prepare-spec validate <path>_spec.md`.

### [P-001][CRÍTICO] [Título del gap]
- **Pregunta**: [pregunta concreta]
- **Respuesta**: [CRÍTICO]_(pendiente)_
```

**Si hay asunciones aplicadas**, añadir:
```markdown
## Asunciones Aplicadas

- **[A-001]**: [descripción de la asunción aplicada y su justificación]
```

### 5. Validar el spec generado

Antes de devolver el output, aplica la Prueba de Pureza al spec completo. Consulta `spec-expert`. Si hay contaminación técnica introducida durante la generación, corrígela antes de devolver el output.

### 6. Generar artefactos de índice

**README de la feature**: Genera el contenido completo de `features/<capability>/README.md` siguiendo `references/feature_readme_template.md`. Usa los datos del spec recién generado:
- Feature ID: F-001 si `_features.md` no existe, o el siguiente ID disponible si existe
- Actor principal: extraído del spec
- Spec monolítico origen: `N/A (fast-track directo)`
- Artefactos: Spec ✓, Plan —, Tasks —

**Índice de features (`_features.md`)**: Busca si existe algún `*_features.md` en el directorio padre de la carpeta `features/` (es decir, en el mismo directorio que el archivo de input):
- **Si existe**: léelo y añade la nueva feature como entrada `F-00X` (con el siguiente ID disponible). Actualiza la tabla de shared models si la feature declara alguno.
- **Si no existe**: genera un `_features.md` nuevo usando el formato de `decompose-expert`, con esta feature como primera entrada `F-001`, sin spec monolítico origen y sin tabla de shared models si no hay ninguno.

Devuelve en tu output, además del spec, los siguientes bloques claramente delimitados:
```
--- README ---
<contenido completo del README.md>
--- /README ---

--- FEATURES_INDEX ---
<contenido completo del _features.md actualizado o nuevo>
--- /FEATURES_INDEX ---

--- FEATURES_INDEX_PATH ---
<path absoluto donde debe escribirse el _features.md>
--- /FEATURES_INDEX_PATH ---
```
