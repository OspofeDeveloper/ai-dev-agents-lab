---
name: wf-design-validate
description: "Audita un DESIGN.md ya existente contra el contrato visual (kb-design-expert, kb-design-style-taxonomy, kb-design-brief) y el linter oficial de Google design.md. No regenera el archivo, solo reporta DESIGN_GAP o OK."
when_to_use: "Activa en frases como 'valida el DESIGN.md', 'revisa que el sistema visual esta bien', 'audita el design despues de editarlo', 'comprueba que el DESIGN.md cumple el brief'. No activa para generar o modificar el archivo."
argument-hint: "<DESIGN.md> [--brief <DESIGN_BRIEF.md>] [--views <feature_views.md>] [--lenient] [--pedagogical]"
effort: medium
allowed-tools: [Read, Bash]
context: fork
agent: design-architect
---

# design-validate — Orquestador del Flujo SDD (Etapa Design)

Tu rol es de **auditor puro**: leer un `DESIGN.md` existente, contrastar contra brief y kbs, ejecutar el linter de Google y devolver una lista de hallazgos. No escribes el archivo.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del DESIGN.md**: primer argumento posicional.
- **Path del brief** opcional mediante `--brief`.
- **Path de un `*_views.md`** opcional mediante `--views`: si se pasa, valida tambien microcopy y estados de vista (Reglas 19-20 de `kb-design-expert`).
- **Flag `--lenient`** opcional: relaja el comportamiento por defecto. Hallazgos no-criticos no bloquean. Por defecto la validacion es **estricta** (cualquier `[CRITICO]` o `[ALTO]` cuenta como fallo).
- **Flag `--pedagogical`** opcional: cada hallazgo lleva explicacion extendida, referencia a la regla concreta y enlace al ejemplo o checklist relevante. Pensado para diseñadores junior.

Si no hay path o no se reconoce el comando, informa:
> "Uso: `/wf-design-validate <DESIGN.md> [--brief <DESIGN_BRIEF.md>] [--views <feature_views.md>] [--lenient] [--pedagogical]`"

## Paso 2: Verificar el DESIGN.md

1. Verifica que el archivo existe.
2. Lee el archivo completo (frontmatter YAML + markdown).
3. Si no parece un `DESIGN.md` (sin frontmatter o sin secciones canonicas), informa:
   > "Este archivo no parece un `DESIGN.md` SDD. Genera uno con `/wf-design-system` o indica un path valido."

## Paso 3: Resolver DESIGN_BRIEF.md

1. Si se paso `--brief <path>`, leelo.
2. Si no, busca `DESIGN_BRIEF.md` en el mismo directorio del DESIGN.md.
3. Si existe, leelo y usalo para contrastar.
4. Si no existe, registra `BRIEF_GAP: sin brief disponible para contrastar coherencia` y continua. La auditoria sigue valida; solo se acota a estructura.

## Paso 4: Ejecutar el linter de Google design.md

Ejecuta:
```bash
npx @google/design.md lint <path_design>
```

Captura el resultado:
- **Sin errores** → registrar `linter: OK`.
- **Con errores** → guardar la lista completa de errores.
- **npx no disponible** → registrar `linter: SKIPPED` con explicacion.

## Paso 5: Delegar auditoría al agente design-architect

Lee el checklist completo de validación:
`${CLAUDE_SKILL_DIR}/references/validation-checklist.md`

Invoca al agente cargando `kb-design-expert`, `kb-design-style-taxonomy`, `kb-design-brief` y `kb-a11y-expert` con este prompt:

```text
Modo: design-validate
Path del DESIGN.md: <path_design>
Contenido del DESIGN.md:
---
<contenido_completo_design>
---
DESIGN_BRIEF.md (si existe):
---
<contenido_brief_o_N/A>
---
*_views.md (si se pasó --views):
---
<contenido_views_o_N/A>
---
Resultado del linter:
---
<resultado_linter>
---
Flag --lenient: <true|false>
Flag --pedagogical: <true|false>

Checklist de validación:
---
<contenido_completo_de_validation-checklist.md>
---

INSTRUCCION: audita el DESIGN.md sin reescribirlo. Usa el checklist anterior como guía exhaustiva. Devuelve hallazgos con severidad siguiendo el formato de salida del checklist.
No reescribas el archivo. No propongas patches. Solo reporta.
```

## Paso 6: Informar al usuario

Muestra el reporte tal como lo devuelva el agente. Anade:

- path del DESIGN.md auditado
- path del brief usado (o `N/A`)
- siguiente paso recomendado:
  - si `PASS` → continuar con `/wf-design-feature-prototype`
  - si `PASS_WITH_GAPS` → considerar `/wf-design-delta analyze` para resolverlos
  - si `FAIL` → corregir manualmente o regenerar con `/wf-design-system`

No escribas ningun archivo en este workflow.
