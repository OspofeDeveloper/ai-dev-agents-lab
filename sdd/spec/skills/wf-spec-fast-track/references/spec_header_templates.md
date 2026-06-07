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

Añadir al final del spec (antes del Changelog si existiera) si hay gaps `[CRÍTICO]` pendientes:

```markdown
## Items Pendientes

> ⚠️ Este spec tiene gaps **críticos** sin resolver. Las HUs afectadas están marcadas `[INCOMPLETO]` y `/wf-prepare-plan` quedará bloqueado hasta que se resuelvan.
> Para resolverlos: responde los gaps en el `_analysis.md` y ejecuta `/wf-spec-gap-resolve <path>_spec.md`.

### [P-001][CRÍTICO] [Título del gap]
- **Afecta**: [HU-001, HU-003]
- **Pregunta**: [pregunta concreta]
- **Respuesta**: _(pendiente)_
```

## Sección opcional: Asunciones Aplicadas

Añadir si hay asunciones `[INFORMATIVO]` aplicadas:

```markdown
## Asunciones Aplicadas

- **[A-001]**: [descripción de la asunción aplicada y su justificación]
```
