---
name: wf-prd-change
description: "Gestiona cambios de producto sobre un PRD existente: clasifica el cambio (aclaracion vs change request), actualiza el PRD si corresponde y deja trazabilidad con matriz de impacto sobre specs, plan y tasks."
when_to_use: "Activa en frases como 'cambia el alcance del PRD', 'esto pasa de fase 2 a MVP', 'actualiza el PRD con esta decision', 'gestiona este cambio de producto', 'abre un change request sobre el PRD'."
argument-hint: "<prd.md> --new-reqs <cambio.md>"
effort: high
allowed-tools: [Read, Write, Bash]
context: fork
agent: prd-expert
user-invocable: true
---

# Workflow: PRD-CHANGE

Tu objetivo es gestionar cambios de producto una vez que el PRD ya existe y el pipeline puede haber generado artefactos derivados.

Usa `kb-prd-expert` para preservar pureza de negocio y `kb-product-change-governance` para decidir si el cambio requiere actualizar el PRD o basta con registrarlo como aclaración.

**Regla de oro:** si el cambio altera el producto comprometido, el PRD se actualiza primero y la trazabilidad se registra antes de hablar de specs.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:

- path del `PRD.md`
- `--new-reqs <archivo.md>` obligatorio: documento con el cambio propuesto

Si faltan argumentos:
> "Uso: `/wf-prd-change <prd.md> --new-reqs <cambio.md>`"

## Paso 2: Verificar archivos

Comprueba que existen el PRD y el documento de cambio.

Si no existe alguno, informa y detén.

## Paso 3: Leer contexto

Lee:

- PRD completo
- documento de cambio
- `product-changelog.md` si existe en el mismo directorio
- `*_analysis.md`, `*_discovery.md`, `*_features.md` si existen

## Paso 4: Clasificar el cambio

Siguiendo `kb-product-change-governance`, clasifica el cambio como:

- `CLARIFICATION`
- `BEHAVIOR_CHANGE`
- `SCOPE_CHANGE`
- `PRIORITY_CHANGE`
- `DEPRECATION`

Indica también:

- severidad: `BAJA | MEDIA | ALTA`
- si exige editar el PRD: `sí/no`
- por qué

Si es solo `CLARIFICATION` y no contradice el PRD:

- no reescribas el PRD
- genera igualmente el artefacto de cambio
- recomienda `wf-spec-gap-resolve` o `wf-spec-delta` según corresponda

## Paso 5: Proponer y aplicar el cambio en el PRD

Si el cambio exige editar el PRD:

1. actualiza versión y fecha del PRD
2. reescribe únicamente las secciones afectadas
3. conserva el resto intacto
4. si una exclusión de fase futura pasa a MVP, elimina o corrige esa exclusión
5. **reabre el sello ([[D-028]]).** Si el PRD estaba sellado (`Aprobado por:` relleno, `status: approved`), el cambio de contenido invalida esa aprobación —atestiguaba un contenido que ya no existe—. Baja `status:` a `in-review` y **resetea la línea `Aprobado por:` al placeholder pendiente**, para que el sello nunca certifique contenido no revisado. Indica al usuario que **re-apruebe con `wf-prd-review`** (que re-verifica asunciones vía `sdd-prd-ready.py` y re-captura la identidad del aprobador, [[D-027]]). No re-selles tú aquí: el sello se establece **solo** por el gate de review, para que "sellado" siga significando "un humano aprobó *este* contenido".

Nunca metas detalles técnicos.

## Paso 6: Registrar trazabilidad

Escribe o actualiza:

- `product-changelog.md`
- `changes/CR-XXX/change-request.md`
- `changes/CR-XXX/decision.md`

Usa `product-changelog.md` como índice global. Toda la documentación detallada del cambio debe quedar agrupada dentro de `changes/CR-XXX/`.

La entrada mínima debe incluir:

- ID del cambio
- fecha
- tipo
- resumen de la decisión
- secciones del PRD tocadas
- artefactos potencialmente afectados

## Paso 7: Generar impacto inicial

Genera `changes/CR-XXX/change-request.md` con:

- clasificación del cambio
- diff funcional resumido
- impacto preliminar sobre:
  - analysis
  - discovery
  - features index
  - specs
  - plan
  - tasks
- siguiente workflow recomendado

Genera también `changes/CR-XXX/decision.md` con la decisión aprobada, el motivo, las secciones del PRD tocadas y el resumen de artefactos afectados.

## Paso 8: Informar siguiente paso

- Si solo fue aclaración:
  > "El cambio no altera el producto comprometido. No fue necesario reescribir el PRD. Continúa con `wf-spec-gap-resolve` o `wf-spec-delta` según el artefacto afectado."

- Si hubo cambio de producto:
  > "El PRD se actualizó y se registró el cambio. Ejecuta `wf-prd-sync-impact <prd.md>` para medir qué artefactos derivados han quedado desincronizados."
