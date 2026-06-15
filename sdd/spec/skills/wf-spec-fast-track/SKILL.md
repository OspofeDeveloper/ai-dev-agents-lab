---
name: wf-spec-fast-track
description: "Genera el Spec de una feature directamente desde un documento de requisitos acotado a una sola capacidad. Soporta modo scoped con --scope-from para filtrar un PRD completo a una feature del discovery. Acepta --analysis para usar gaps pre-resueltos de un analisis previo."
when_to_use: "Activa en frases como 'genera el spec directo de esta feature', 'fast-track del spec', 'crea el spec de esta capability directamente', 'genera spec sin analisis previo'."
argument-hint: "<archivo.md> --capability <nombre-kebab> [--light|--standard] [--analysis <analysis.md>] [--allow-derived-scope-from-analysis] | <prd.md> --scope-from <discovery.md> --feature <F-00X> [--light|--standard] [--analysis <analysis.md>] [--allow-derived-scope-from-analysis]"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: sdd-spec-writer
user-invocable: true
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
- **Flag opcional**: `--light` / `--standard` → fuerza el modo del pipeline para esta feature.

**Resolución del modo** (en este orden): flag explícito > `pipeline_mode` de `.sdd/project-init.json` (directorio actual o ancestro) > `standard`. Las reglas exactas de qué relaja el modo ligero viven en `kb-spec-expert` ("Modo ligero — proporcionalidad declarada"); los invariantes (CAs testables, trazabilidad, marcadores, pureza, gobernanza) son idénticos en ambos modos.

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

Verifica (con `kb-decompose-expert`) que el documento describe una única capability SDD válida: actor identificable, journeys independientes, ≥3 CAs asumibles (modo ligero: ≥1 CA asumible). Si describe múltiples features independientes → remite al usuario a `/wf-spec-discover` + `/wf-spec-features-first`. Si el scope es ambiguo pero asumible → aplica con asunción `[INFORMATIVO]`.

### Modo scoped (--scope-from + --feature)

**No aplica el check de multi-feature.** El scope ya fue definido por `/wf-spec-discover` y validado por el usuario. En su lugar:

1. Filtra mentalmente el PRD a solo los RFs y secciones listados en el scope de la feature
2. Lee el PRD completo para entender el contexto general, pero **solo genera HUs/CAs para los RFs del scope de esta feature**
3. Verifica que el scope filtrado contiene suficiente información para generar un spec válido (actor identificable, journeys derivables, mínimo 3 CAs — modo ligero: mínimo 1)
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

Produce un `_spec.md` completo siguiendo la estructura de `${CLAUDE_SKILL_DIR}/references/feature_spec_template.md`:

- **Modo standard**: los 8 elementos SDD completos.
- **Modo ligero**: el núcleo de 4 (Actores, HUs, CAs, Fuera de Alcance); las demás secciones solo si aportan, y si se omiten quedan presentes con `N/A — modo ligero` explícito (regla de `kb-spec-expert` — nunca rellenar por inventar). Añade `> Modo: ligero` al header del spec.

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
- Feature ID: el siguiente F-NNN libre. **No lo cuentes a mano** (colisión con el índice de features): `!python3 .sdd/scripts/sdd-next-id.py F <ruta_al_features.md>` (emite `F-001` si `_features.md` no existe; ignora `RF-` y `F-C-`, que no son features de producto). Sin python3/script → máximo `F-NNN` del índice + 1
- Actor principal: extraído del spec
- Spec monolítico origen: `N/A (fast-track directo)`
- Artefactos: Spec ✓, Plan —, Tasks — (rutas relativas a la raíz de la feature según su layout: `spec/<nombre>_spec.md` con subcarpetas, `<nombre>_spec.md` si la feature es plana legacy)
- Origen de alcance: `PRD` o `PRD + analysis respondido`
- Avisos de gobernanza: `ninguno` o lista de gaps que derivaron alcance no consolidado

**Índice de features (`_features.md`)**: NO lo escribas a mano. `_features.md` es un artefacto **generado** por `sdd-features-index.py` (regenerador determinista) a partir del discovery + los specs presentes + el readiness report. Tú escribes el spec y el README de la feature; el índice se regenera en el Paso 10. Esto elimina la colisión de escrituras paralelas (varios fast-tracks lanzados a la vez por `wf-spec-features-first`) y los conflictos de merge entre devs sobre el hub monolítico. Los campos del índice (estado canónico, origen de alcance, trazabilidad RF→HU) los deriva el script de sus fuentes: tú solo debes asegurarte de que el header del spec los declare correctamente (`> Feature ID:`, `> Origen de alcance:`, `> Avisos de gobernanza:`).

---

## Paso 10: Escribir los artefactos

Determina el directorio raíz de los artefactos spec (regla de layout): si `.sdd/project-init.json` (en el directorio actual o un ancestro) declara `artifacts.spec`, usa ese directorio (relativo a la raíz que contiene `.sdd/`); si no, usa el directorio del archivo de entrada.

**Layout de feature**: cada feature organiza sus artefactos en subcarpetas por fase (`features/<nombre>/spec/`, `design/`, `plan/`, `tasks/`; el `README.md` vive en la raíz de la feature). Si la feature ya existe con layout plano legacy (artefactos directamente en `features/<nombre>/`), consérvalo — no mezcles layouts dentro de una misma feature.

Verifica si el spec ya existe en cualquiera de los dos layouts con el resolutor (cubre subcarpetas y plano legacy en una sola llamada):
```bash
!python3 .sdd/scripts/sdd-resolve-path.py find spec "<raíz_spec>/features/<capability>/spec/<capability>_spec.md"
```
Emite el path existente (vacío + exit 3 si no existe en ningún layout). **Fallback** a mano: busca en `<raíz_spec>/features/<capability>/spec/<capability>_spec.md` (subcarpetas) o `<raíz_spec>/features/<capability>/<capability>_spec.md` (plano legacy). Si existe → pregunta al usuario si desea regenerarlo (no → informa del path y detén; sí → reescribe en su ubicación actual). Escribe los 2 artefactos que tú compones (crea directorios si no existen), relativos a esa raíz:
1. **Spec**: `<raíz_spec>/features/<capability>/spec/<capability>_spec.md`
2. **README**: `<raíz_spec>/features/<capability>/README.md` (siempre en la raíz de la feature)

El `_features.md` NO se escribe aquí: es un índice generado, se regenera más abajo.

**Sellar la trazabilidad PRD→spec** (solo si `derived_from_prd` es un path real — modo scoped): tras escribir el spec, ejecuta desde la raíz del proyecto (el directorio que contiene `.sdd/`):

```
python3 .sdd/scripts/sdd-sync-check.py seal <path_del_spec>
```

El script calcula el hash del PRD origen y escribe `derived_from_prd_hash` en el header. NUNCA rellenes ese campo a mano (separación autor/verificador: es la evidencia con la que los gates y el sellador de planes detectan deriva del PRD). Si el script no existe:
> "⚠ Falta `.sdd/scripts/sdd-sync-check.py`. Re-ejecuta la instalación del ecosistema (`install.sh`) para reponer los scripts de enforcement. El spec queda con `derived_from_prd_hash: N/A` (sin detección de deriva)."

**Regenerar el índice de features**: tras escribir el spec, regenera `_features.md` ejecutando desde la raíz del proyecto (el directorio que contiene `.sdd/`):

```
python3 .sdd/scripts/sdd-features-index.py <raíz_spec>
```

`<raíz_spec>` es el directorio que contiene `features/` y el `_features.md` (el mismo de arriba). El script escanea el discovery + todos los specs + el readiness report (si existe) y regenera el índice de forma determinista y atómica — por eso es seguro aunque varios fast-tracks corran en paralelo. NUNCA edites `_features.md` a mano (separación autor/generador). Si el script no existe:
> "⚠ Falta `.sdd/scripts/sdd-features-index.py`. Re-ejecuta la instalación del ecosistema (`install.sh`) para reponer los scripts de enforcement. El índice `_features.md` no se ha regenerado."

---

## Paso 11: Informar al usuario

Informa: paths generados (spec, README) y `_features.md` regenerado. Si hay `[CRÍTICO]` pendientes: listarlos (bloquean `/wf-prepare-plan`). Si se aplicaron asunciones: cuántas y dónde. Siguiente paso: `/wf-prepare-plan generate <path>_spec.md`.
