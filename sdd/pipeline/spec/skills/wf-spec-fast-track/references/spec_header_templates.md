# Plantillas de cabecera para _spec.md

## Modo directo (`--capability`)

```markdown
# Spec: [Nombre de la Capability]
> Versión: 1.0 | Fecha: [YYYY-MM-DD]
> Estado: BORRADOR
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

> **`Estado:` lo escribes una sola vez, en BORRADOR, y nunca lo tocas después ([[D-061]]).**
> Un spec recién generado **no está validado**: nadie lo ha auditado todavía. La promoción a
> `VALIDADO` la escribe **`sdd-seal.py spec … --seal`** tras la validación del spec, y solo si las
> condiciones mecánicas pasan — mismo reparto autor/verificador que en el plan. **Nunca escribas
> `VALIDADO` a mano**: es la evidencia que mira el gate al pasar a planificación.

## Modo scoped (`--scope-from` + `--feature`)

```markdown
# Spec: [Nombre de la Capability]
> Versión: 1.0 | Fecha: [YYYY-MM-DD]
> Estado: BORRADOR
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

> **La forma del bloque es CONTRATO, no estilo.** Cada gap va con encabezado
> `### [P-XXX][SEVERIDAD] Título` y sus campos como bullets `- **Campo**: valor`. Lo parsea
> `sdd-analysis-gaps.py`, que es quien lo lista, lo checkea y escribe la respuesta con `--answer`.
> **Medido (pasada 12 de CU-3.a):** un spec escribió sus gaps como lista de viñetas
> (`- **[P-011][INFORMATIVO]** …`) y el script dejó de verlos: `--check` devolvió `VACUOUS` y
> `--answer` falló con exit 2. Falla ruidosamente —la guarda no dice *"0 abiertos"* sobre lo que
> no ha parseado— pero con un `[CRÍTICO]` ese gap sería inalcanzable desde la vía sancionada.

**Cabecera según lo que haya.** Elige una de las tres:

```markdown
## Items Pendientes

> ⚠️ Este spec tiene gaps **críticos** sin resolver. Las HUs afectadas están marcadas `[INCOMPLETO]` y **el paso a planificación queda bloqueado** hasta que se resuelvan.
> Para resolverlos: responde los gaps **en esta misma sección** —sustituyendo `- **Respuesta**: _(pendiente)_` en el bloque de cada uno, o dictándomelos— y pide que **se completen las historias incompletas** de este spec.
```

```markdown
## Items Pendientes

> Este spec tiene gaps **informativos** cuya asunción por defecto ya está aplicada en los criterios de aceptación (ver `## Asunciones Aplicadas`). **No bloquean** el paso a planificación; quedan anotados por trazabilidad.
> Si quieres decidir alguno de otra forma: responde el gap **en esta misma sección** —sustituyendo `- **Respuesta**: _(pendiente)_`, o dictándomelo— y pide que se actualice el spec.
```

```markdown
## Items Pendientes

> Este spec tiene gaps **críticos e informativos**. Los críticos marcan sus HUs como `[INCOMPLETO]` y **bloquean** el paso a planificación; los informativos ya tienen su asunción aplicada y no bloquean.
> En los dos casos se responden **en esta misma sección**, sustituyendo `- **Respuesta**: _(pendiente)_` en el bloque de cada uno, o dictándomelos.
```

Y los bloques, siempre con esta forma (los campos que no apliquen se omiten; un `[INFORMATIVO]`
lleva además `Asunción por defecto`, y un `[CRÍTICO]` lleva `Afecta`):

```markdown
### [P-001][CRÍTICO] [Título del gap]
- **Contexto**: [dónde aparece la ambigüedad al escribir este spec]
- **Afecta**: [HU-001, HU-003]
- **Pregunta para el cliente**: [pregunta concreta]
- **Respuesta**: _(pendiente)_

### [P-002][INFORMATIVO] [Título del gap]
- **Contexto**: [dónde aparece la ambigüedad al escribir este spec]
- **Pregunta para el cliente**: [pregunta concreta]
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: [la opción más conservadora, ya aplicada en los CAs]
```

**Si no hay ningún gap propio, la sección no se escribe.** No hace falta un `Items Pendientes`
vacío ni una nota diciendo que no hay nada pendiente.

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
