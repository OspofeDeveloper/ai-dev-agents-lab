---
name: wf-spec-fast-track
description: "Genera el Spec de una feature directamente desde un documento de requisitos acotado a una sola capacidad. Soporta modo scoped con --scope-from para filtrar un PRD completo a una feature del discovery. Acepta --analysis para usar gaps pre-resueltos de un analisis previo."
when_to_use: "Activa en frases como 'genera el spec directo de esta feature', 'fast-track del spec', 'crea el spec de esta capability directamente', 'genera spec sin analisis previo'."
argument-hint: "<archivo.md> --capability <nombre-kebab> [--analysis <analysis.md>] [--allow-derived-scope-from-analysis] | <prd.md> --scope-from <discovery.md> --feature <F-00X> [--analysis <analysis.md>] [--allow-derived-scope-from-analysis]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-writer
---

# Workflow: FAST-TRACK

Tu objetivo es generar un Spec de feature SDD completo y válido directamente desde un documento de requisitos enfocado en una sola capacidad. Usa `kb-spec-expert` para garantizar pureza y los 8 elementos, y `kb-decompose-expert` para verificar que el scope es el de una sola feature válida.

**Dos modos:** directo (`--capability`): documento acotado a una sola capacidad; scoped (`--scope-from` + `--feature`): PRD completo filtrado al scope de una feature del discovery. Si el documento describe múltiples capacidades sin `--scope-from`, remitir al flujo estándar o `/wf-spec-discover`.

---

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del archivo**: el primer argumento
- **Modo directo**: si hay `--capability` → extraer el nombre de la capability
- **Modo scoped**: si hay `--scope-from` y `--feature` → extraer el path del `_discovery.md` y el Feature ID (ej: `F-001`)
- **Flag opcional**: `--analysis <path>` → path a un `_analysis.md` con gaps pre-resueltos
- **Flag opcional**: `--allow-derived-scope-from-analysis` → permite continuar aunque el analysis introduzca expansión funcional no consolidada todavía en el PRD. Sin este flag, el workflow se detiene para remitir a `wf-prd-change`.

Si hay `--scope-from` sin `--feature` (o viceversa) → error: "Los flags `--scope-from` y `--feature` deben usarse juntos." Si no hay ni `--capability` ni `--scope-from` → mostrar uso de ambos modos y detener.

---

## Paso 2: Verificar el archivo

Verifica que el archivo existe; si no → informa con ruta exacta y detén.

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

Verifica (con `kb-decompose-expert`) que el documento describe una única capability SDD válida: actor identificable, journeys independientes, ≥3 CAs asumibles. Si describe múltiples features independientes → remite al usuario a `/wf-spec-discover` + `/wf-spec-features-first`. Si el scope es ambiguo pero asumible → aplica con asunción `[INFORMATIVO]`.

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
5. Si una respuesta resuelta introduce señales de cambio de producto según `kb-product-change-governance`:
   - si **NO** se pasó `--allow-derived-scope-from-analysis` → **DETENERSE** con veredicto operativo `STOP_REQUIERE_PRD_CHANGE` e informar:
     > "La respuesta a `[P-XXX]` introduce expansión funcional no consolidada en el PRD. Formaliza primero el cambio con `wf-prd-change` o re-ejecuta con `--allow-derived-scope-from-analysis` para generar el spec dejando el alcance marcado como derivado."
   - si **SÍ** se pasó `--allow-derived-scope-from-analysis` → continuar con veredicto operativo `CONTINUAR_CON_ALCANCE_DERIVADO`. Registra internamente:
     - gaps/respuestas que originan el alcance derivado
     - si la expansión crea modelo owner nuevo, catálogo reutilizable, granularidad funcional nueva o flujo adicional
     - que el spec, el README y el `_features.md` deben marcar **Origen de alcance: PRD + analysis respondido**

**Regla adicional obligatoria:** si la respuesta respondida crea un nuevo modelo owner de feature o promociona una entidad antes implícita a capacidad gestionable explícita, no la trates como scope limpio. Sin `--allow-derived-scope-from-analysis`, detente siempre. Ejemplos típicos: `Contacto` persistente, presupuestos por subcategoría, CRUD explícito sobre una entidad antes implícita.

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

Produce un `_spec.md` completo con los 8 elementos SDD siguiendo la estructura de `${CLAUDE_SKILL_DIR}/references/feature_spec_template.md`.

Usa las plantillas de cabecera de `${CLAUDE_SKILL_DIR}/references/spec_header_templates.md`:
- **Modo directo**: cabecera con `Generado via: fast-track desde [path]`, `Feature ID: F-001`, `derived_from_prd: N/A`
- **Modo scoped**: cabecera con `Generado via: fast-track desde [prd.md] (scope: F-00X via [discovery.md])`, `status_sync: in_sync`

Añade las secciones opcionales según corresponda (plantillas en `spec_header_templates.md`):
- `## Decisiones derivadas del analysis` si se usó `--allow-derived-scope-from-analysis`
- `## Items Pendientes` si hay gaps `[CRÍTICO]` sin respuesta
- `## Asunciones Aplicadas` si hay asunciones `[INFORMATIVO]` aplicadas

---

## Paso 8: Validar el spec generado

Antes de escribir el output, aplica la Prueba de Pureza al spec completo. Consulta `kb-spec-expert`. Si hay contaminación técnica introducida durante la generación, corrígela antes de continuar.

---

## Paso 9: Generar artefactos de índice

**README de la feature**: Genera el contenido completo de `features/<capability>/README.md` siguiendo `${CLAUDE_SKILL_DIR}/references/feature_readme_template.md`. Usa los datos del spec recién generado:
- Feature ID: F-001 si `_features.md` no existe, o el siguiente ID disponible si existe
- Actor principal: extraído del spec
- Spec monolítico origen: `N/A (fast-track directo)`
- Artefactos: Spec ✓, Plan —, Tasks — (rutas relativas a la raíz de la feature según su layout: `spec/<nombre>_spec.md` con subcarpetas, `<nombre>_spec.md` si la feature es plana legacy)
- Origen de alcance: `PRD` o `PRD + analysis respondido`
- Avisos de gobernanza: `ninguno` o lista de gaps que derivaron alcance no consolidado

**Índice de features (`_features.md`)**: Sigue la guía de `${CLAUDE_SKILL_DIR}/references/artefact_index_update.md` para añadir/crear la entrada de la feature, usar estados canónicos, campos de origen de alcance y trazabilidad RF→HU en modo scoped.

---

## Paso 10: Escribir los artefactos

Determina el directorio raíz de los artefactos spec (regla de layout): si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.spec`, usa ese directorio (relativo a la raíz que contiene `.sdd/`); si no, usa el directorio del archivo de entrada.

**Layout de feature**: cada feature organiza sus artefactos en subcarpetas por fase (`features/<nombre>/spec/`, `design/`, `plan/`, `tasks/`; el `README.md` vive en la raíz de la feature). Si la feature ya existe con layout plano legacy (artefactos directamente en `features/<nombre>/`), consérvalo — no mezcles layouts dentro de una misma feature.

Verifica si el spec ya existe — en `<raíz_spec>/features/<capability>/spec/<capability>_spec.md` (subcarpetas) o `<raíz_spec>/features/<capability>/<capability>_spec.md` (plano legacy); si existe → pregunta al usuario si desea regenerarlo (no → informa del path y detén; sí → reescribe en su ubicación actual). Escribe los 3 artefactos (crea directorios si no existen), todos relativos a esa raíz:
1. **Spec**: `<raíz_spec>/features/<capability>/spec/<capability>_spec.md`
2. **README**: `<raíz_spec>/features/<capability>/README.md` (siempre en la raíz de la feature)
3. **Features index**: `<raíz_spec>/<nombre_base>_features.md` (o actualiza el existente)

---

## Paso 11: Informar al usuario

Informa: paths generados (spec, README, `_features.md` nuevo/actualizado). Si hay `[CRÍTICO]` pendientes: listarlos (bloquean `/wf-prepare-plan`). Si se aplicaron asunciones: cuántas y dónde. Siguiente paso: `/wf-prepare-plan generate <path>_spec.md`.
