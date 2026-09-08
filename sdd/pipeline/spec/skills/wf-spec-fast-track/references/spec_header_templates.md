# Plantillas de cabecera para _spec.md

## Modo directo (`--capability`)

```markdown
# Spec: [Nombre de la Capability]
> Versión: 1.0 | Fecha: [YYYY-MM-DD]
> Generado via: fast-track desde [path/del/documento.md]
> Feature ID: F-001
> Spec monolítico origen: N/A (fast-track directo)
> Source requirements: [path/del/documento.md]
> derived_from_prd: N/A
> derived_from_prd_version: N/A
> derived_from_prd_hash: N/A
> derived_from_change: N/A
> status_sync: unknown
> Origen de alcance: [Documento fuente | Documento fuente + analysis respondido]
> Avisos de gobernanza: [ninguno | alcance derivado desde P-00X, P-00Y]
```

## Modo scoped (`--scope-from` + `--feature`)

```markdown
# Spec: [Nombre de la Capability]
> Versión: 1.0 | Fecha: [YYYY-MM-DD]
> Generado via: fast-track desde [path/del/prd.md] (scope: F-00X via [discovery.md])
> Feature ID: F-00X
> Spec monolítico origen: N/A (features-first via discover)
> Source requirements: [path/del/prd.md]
> derived_from_prd: [path/del/prd.md]
> derived_from_prd_version: [versión del PRD o unknown]
> derived_from_prd_hash: [N/A — lo escribe `sdd-sync-check.py seal` en el Paso 10, nunca a mano]
> derived_from_change: [CR-XXX | N/A]
> status_sync: in_sync
> Origen de alcance: [PRD | PRD + analysis respondido]
> Avisos de gobernanza: [ninguno | alcance derivado desde P-00X, P-00Y]
```

## Sección opcional: Decisiones derivadas del analysis

Añadir después del header si se usó `--allow-derived-scope-from-analysis`:

```markdown
## Decisiones derivadas del analysis

- **[P-00X]**: [respuesta resumida] → [impacto funcional derivado]
```

## Sección opcional: Items Pendientes

Añadir al final del spec (antes del Changelog si existiera) si hay gaps —`[CRÍTICO]` o
`[INFORMATIVO]`— que **nacen al escribir este spec**.

**Solo los que nacen aquí** ([[D-057]]). Un gap del `_analysis.md` que afecta a esta feature **no
se reproduce** en esta sección: ya tiene su bloque respondible allí, y un segundo significa dos
sitios donde contestar y ninguno que mande. Si aplicaste su asunción, se referencia en
`## Asunciones Aplicadas` citando su ID y **su fichero**, sin campo `Respuesta`.

```markdown
## Items Pendientes

> ⚠️ Este spec tiene gaps **críticos** sin resolver. Las HUs afectadas están marcadas `[INCOMPLETO]` y **el paso a planificación queda bloqueado** hasta que se resuelvan.
> Para resolverlos: responde los gaps **en esta misma sección** —sustituyendo `- **Respuesta**: _(pendiente)_` en el bloque de cada uno, o dictándomelos— y pide que **se completen las historias incompletas** de este spec.

### [P-001][CRÍTICO] [Título del gap]
- **Contexto**: [dónde aparece la ambigüedad al escribir este spec]
- **Afecta**: [HU-001, HU-003]
- **Pregunta**: [pregunta concreta]
- **Respuesta**: _(pendiente)_
```

## Sección opcional: Asunciones Aplicadas

Añadir si hay asunciones `[INFORMATIVO]` aplicadas:

```markdown
## Asunciones Aplicadas

- **[A-001]** (sobre [P-00X], que nace en este spec): [descripción de la asunción aplicada y su justificación]
- **[A-002]** (sobre [P-00Y], que vive en `prd/prd_analysis.md` y sigue sin responder): [asunción aplicada]. Si se responde allí y la respuesta cambia esto, pide que se actualice este spec.
```

La segunda forma es la de un gap **heredado del análisis** ([[D-057]]): se cita con su ID y **su
fichero**, y aquí es donde se deja constancia — nunca reproduciéndolo en `Items Pendientes`, que
crearía un segundo sitio donde contestarlo.
