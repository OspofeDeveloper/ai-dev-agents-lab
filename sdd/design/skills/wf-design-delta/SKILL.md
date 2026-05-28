---
name: wf-design-delta
description: Evoluciona un DESIGN.md existente. Modo 'analyze' produce un informe delta con tokens, componentes y secciones a anadir, modificar o eliminar; modo 'apply' integra los cambios validados preservando lo previo. Activa en frases como "actualiza el DESIGN.md con estos cambios visuales", "cambia el style_family del sistema", "anade tokens para esta feature", "evoluciona el sistema visual". No activa para regenerar DESIGN.md desde cero (eso es `wf-design-system`).
argument-hint: "analyze <DESIGN.md> --new-reqs <cambios.md> [--brief <DESIGN_BRIEF.md>] | apply <DESIGN.md> <delta_analysis.md>"
effort: high
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: design-architect
---

# design-delta — Evolucion controlada del sistema visual

Tu rol es gestionar cambios incrementales sobre `DESIGN.md` sin reescribir lo previo. Aplica la **Regla 15** de `kb-design-expert` (politica de evolucion).

**Regla de oro:** el delta nunca reescribe la historia del sistema visual. Extiende cuando se puede, muta solo cuando es necesario y siempre deja traza en `## Changelog`. Si el cambio supone reabrir `style_family` o `clarity_vs_brand`, es realmente una mutacion de brief — remite primero a actualizar `DESIGN_BRIEF.md` con `wf-design-intake`.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: `analyze` o `apply`.
- En modo `analyze`:
  - **Path del DESIGN.md existente**: argumento tras el modo.
  - **Path de nuevos requisitos**: tras `--new-reqs`.
  - **Path del brief** opcional mediante `--brief`.
- En modo `apply`:
  - **Path del DESIGN.md existente**: segundo argumento.
  - **Path del delta analysis**: tercer argumento.

Si no hay argumento o el modo no es valido, informa:
> "Uso:"
> - "`/wf-design-delta analyze <DESIGN.md> --new-reqs <cambios.md> [--brief <DESIGN_BRIEF.md>]`"
> - "`/wf-design-delta apply <DESIGN.md> <design_delta_analysis.md>`"

## Paso 2: Verificar archivos

**Modo `analyze`:**
1. Verifica que `DESIGN.md` existe.
2. Verifica que el archivo de cambios existe.
3. Si se paso `--brief`, leelo; si no, intenta resolver `DESIGN_BRIEF.md` en el mismo directorio.

**Modo `apply`:**
1. Verifica que `DESIGN.md` existe.
2. Verifica que el delta analysis existe y termina en `_delta_analysis.md`. Si no:
   > "El segundo argumento debe ser un delta analysis generado por `/wf-design-delta analyze`."
3. Si el delta analysis tiene items `[CRITICO]_(pendiente)_` sin responder, deten y pide al usuario resolverlos antes de aplicar.

## Paso 3: Leer contenido

Lee todos los archivos relevantes (DESIGN.md, brief si existe, requisitos o delta analysis).

## Paso 4: Delegar al agente design-architect

### Modo `analyze`

Invoca al agente con este prompt:

```text
Modo: design-delta-analyze
Path DESIGN.md: <path>
Contenido DESIGN.md actual:
---
<contenido_design>
---
DESIGN_BRIEF.md (si existe):
---
<contenido_brief_o_N/A>
---
Nuevos requisitos visuales:
---
<contenido_nuevos_reqs>
---

INSTRUCCION: produce un `<basename>_delta_analysis.md` con la siguiente estructura.

Aplica las reglas de kb-design-expert que tienes en contexto:
- Regla 15: distinguir entre extender (anadir) y mutar (cambiar valores existentes).
- Una mutacion sobre `style_family`, `clarity_vs_brand`, `autonomy_policy` exige actualizar el brief primero; en ese caso marca `[BRIEF_CHANGE_REQUIRED]` y no propongas el cambio aqui.
- Anti-patrones de kb-design-style-taxonomy Regla 7 no pueden introducirse.

Estructura del analisis:

```
# DESIGN Delta Analysis

## Resumen
<una linea>

## Extensiones propuestas (anadir sin tocar lo existente)

### Tokens nuevos
- <token>: <valor> — <justificacion> — [origen: <feature/brief/spec>]

### Componentes nuevos
- <componente>: <descripcion breve> — <justificacion>

### Secciones nuevas
- <seccion>: <razon>

## Mutaciones propuestas (cambian valores existentes)

> Cada mutacion debe estar justificada y tener impacto evaluado.

### M-001: <descripcion corta>
- Antes: <valor actual>
- Despues: <valor propuesto>
- Justificacion: <por que>
- Impacto: <componentes / features afectados>
- Severidad: [BAJA | MEDIA | ALTA | CRITICA]
- Estado: [confirmado | _(pendiente)_]

## Items a eliminar (raros, requieren justificacion fuerte)

- <item>: <razon> — Severidad: [ALTA | CRITICA]_(pendiente)_

## Conflictos detectados con brief
- <descripcion o `ninguno`>

## Cambios bloqueantes (requieren actualizar el brief primero)
- [BRIEF_CHANGE_REQUIRED] <descripcion>

## Plan de aplicacion
1. <paso>
2. <paso>
```

No escribas el DESIGN.md. Devuelve solo el analisis estructurado.
```

Escribe el output del agente en `<basename>_delta_analysis.md` junto al `DESIGN.md`.

### Modo `apply`

Invoca al agente con este prompt:

```text
Modo: design-delta-apply
Path DESIGN.md: <path>
Contenido DESIGN.md actual:
---
<contenido_design>
---
Delta analysis aprobado:
---
<contenido_delta_analysis>
---

INSTRUCCION: produce el `DESIGN.md` actualizado aplicando el delta.

Reglas:
- Preserva todos los tokens, componentes y secciones existentes que no aparezcan en mutaciones ni eliminaciones.
- Aplica primero extensiones, luego mutaciones, luego eliminaciones.
- Cada cambio aplicado debe anadir una entrada en la seccion `## Changelog` con formato `[<fecha>] [feature: <id o N/A>] <descripcion>`. Si la seccion no existe, creala al final.
- No introduzcas decisiones nuevas no listadas en el analysis.
- Si encuentras ambiguedad, marca `DESIGN_GAP` y no apliques ese item concreto.
- El archivo resultante debe seguir cumpliendo Reglas 6, 11, 12, 13, 14 de kb-design-expert.

Devuelve el `DESIGN.md` completo, no solo el diff.
```

## Paso 5: Manejar DESIGN_GAPs

Si el agente devuelve gaps:
- en modo `analyze`: incluirlos en el delta_analysis con severidad y marcar `_(pendiente)_`.
- en modo `apply`: no escribir el archivo; informar al usuario y sugerir resolverlos en el analysis primero.

## Paso 6: Escribir y validar el resultado

**Modo `analyze`:**
- Escribe `<basename>_delta_analysis.md` en el directorio del DESIGN.md.

**Modo `apply`:**
- Escribe el DESIGN.md actualizado (sobrescribiendo el anterior solo si todas las mutaciones estan confirmadas).
- Ejecuta el linter:
  ```bash
  npx @google/design.md lint <path_design>
  ```
- Reporta el resultado del linter al usuario.

## Paso 7: Informar al usuario

**Modo `analyze`:**
- path del delta analysis
- numero de extensiones, mutaciones, eliminaciones y BRIEF_CHANGE_REQUIRED
- siguiente paso: revisar el analysis, resolver `_(pendiente)_` y ejecutar `apply`

**Modo `apply`:**
- path del DESIGN.md actualizado
- resumen del Changelog anadido
- resultado del linter
- siguiente paso recomendado:
  - si hay features ya prototipadas, considerar regenerar sus `*_views.md` con `/wf-design-feature-prototype`
  - si los cambios afectan al brief, recordar actualizarlo con `wf-design-intake`
