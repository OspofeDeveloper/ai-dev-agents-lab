---
name: wf-design-feedback
description: "Captura feedback no estructurado de stakeholders (cliente, PM, dev, QA) y lo triajea en categorias accionables: cambio de brief, delta visual, ajuste de feature o fuera de scope. Preserva la trazabilidad del sistema ante el ida-y-vuelta con stakeholders."
when_to_use: "Activa en frases como 'incorpora este feedback del cliente', 'tengo comentarios del PM sobre el design', 'el cliente dice que no le gusta el color de los botones', 'procesa este feedback de stitch'."
argument-hint: "capture <feedback.md|input> [--source <cliente|pm|dev|qa|stitch|otro>] [--feature <feature_spec.md>] | triage <feedback_capture.md>"
effort: medium
allowed-tools: [Read, Write, Agent]
context: fork
agent: design-architect
---

# design-feedback — Captura y triage de feedback

Tu rol es transformar feedback no estructurado en acciones concretas del sistema de design, sin perder la traza del comentario original.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Modo**: `capture` o `triage`.
- En modo `capture`:
  - **Path o texto inline** del feedback: primer argumento.
  - **`--source`** opcional: `cliente`, `pm`, `dev`, `qa`, `stitch`, `otro`.
  - **`--feature`** opcional: spec relacionado si el feedback es feature-especifico.
- En modo `triage`:
  - **Path del archivo de captura**: primer argumento.

Si no hay argumento, informa:
> "Uso:"
> - "`/wf-design-feedback capture <feedback.md|texto> [--source ...] [--feature ...]`"
> - "`/wf-design-feedback triage <feedback_capture.md>`"

## Paso 2: Modo `capture`

### 2.1 Leer el feedback

- Si el primer argumento es un path existente, leerlo.
- Si es texto inline, tomarlo tal cual (el usuario lo pega en la invocacion).

### 2.2 Determinar output path

- Si hay `--feature`, escribir en el mismo directorio del spec: `<basename>_design_feedback.md`.
- Si no, escribir en `<dir_producto>/design_feedback_<fecha>.md`.

### 2.3 Estructurar la captura

Escribir el archivo con esta estructura:

```markdown
---
source: <cliente|pm|dev|qa|stitch|otro>
captured_at: <fecha ISO>
feature: <path_spec o N/A>
status: pending_triage
---

# Design Feedback — <fuente>

## Feedback original

> <texto literal del feedback, sin reformular>

## Contexto

- **Fuente**: <quien lo dijo>
- **Sobre que**: <feature, vista, sistema completo, otro>
- **Estado del sistema cuando se recibio**: <DESIGN.md version si se sabe, branch si aplica>

## Triage pendiente

Ejecutar `/wf-design-feedback triage <este_archivo>` para clasificar y proponer acciones.
```

### 2.4 Informar al usuario

- path del archivo de captura
- siguiente paso:
  > "Ejecuta `/wf-design-feedback triage <path>` para clasificar este feedback."

## Paso 3: Modo `triage`

### 3.1 Verificar archivo

1. Verificar que existe.
2. Verificar que tiene frontmatter con `status: pending_triage`. Si no, deten:
   > "Este archivo no parece una captura pendiente de triage. Genera una con `/wf-design-feedback capture`."

### 3.2 Leer DESIGN.md y brief

- Localizar `DESIGN.md` y `DESIGN_BRIEF.md` del producto.
- Leerlos completos para contextualizar el triage.

### 3.3 Delegar al agente para razonamiento

Invocar al agente `design-architect` con este prompt:

```text
Modo: design-feedback-triage
Captura de feedback:
---
<contenido_captura>
---
DESIGN_BRIEF.md:
---
<contenido_brief>
---
DESIGN.md:
---
<contenido_design>
---

INSTRUCCION: clasifica este feedback en una o varias de las siguientes categorias y propon accion concreta para cada una. No reescribas archivos; solo clasifica.

Categorias:

1. **brief_change**: el feedback exige cambiar variables del brief (style_family, clarity_vs_brand, autonomy_policy, voice_tone, etc.). Accion: `/wf-design-intake` para actualizar el brief.

2. **design_delta**: el feedback toca tokens, componentes o secciones del DESIGN.md sin cambiar el brief. Accion: `/wf-design-delta analyze` con los cambios propuestos.

3. **feature_view_change**: el feedback toca una vista o flow concreto sin afectar al sistema. Accion: regenerar `_views.md` o `_flows.md` de la feature.

4. **microcopy_change**: el feedback es sobre tono o texto puntual. Accion: actualizar microcopy en el `_views.md` afectado consultando `kb-design-voice`.

5. **a11y_concern**: el feedback senala un problema de accesibilidad. Accion: `/wf-design-a11y-audit` para verificar y `/wf-design-delta` si requiere correccion.

6. **functional_change**: el feedback en realidad es un cambio funcional, no de design. Accion: remitir a fase Spec (`/wf-spec-delta` o `/wf-prd-change`).

7. **out_of_scope**: el feedback no es accionable, es opinion sin direccion clara o pide algo fuera del producto. Accion: documentar y descartar con justificacion.

Cada hallazgo del feedback puede caer en una o varias categorias. Devuelve un triage estructurado.
```

### 3.4 Escribir el triage

Sobrescribir el archivo de captura usando la plantilla de `${CLAUDE_SKILL_DIR}/references/triage_output_template.md`.

### 3.5 Informar al usuario

- path del triage actualizado
- resumen: X items clasificados, Y categorias distintas afectadas
- siguiente paso:
  - si hay `brief_change`: `/wf-design-intake` (modo guided o hybrid).
  - si hay `design_delta`: `/wf-design-delta analyze` con los cambios listados.
  - si hay `functional_change`: remitir a fase Spec antes de tocar design.
  - si todos los items son `out_of_scope`: documentar al cliente que no se actuara y por que.

## Regla operativa

- Esta workflow no escribe el DESIGN.md ni el brief. Solo captura, clasifica y propone.
- Mantener el feedback original literal es importante: si despues hay conflicto sobre que pidio el cliente, la fuente esta.
- El triage no es definitivo: el usuario puede reclasificar manualmente editando el archivo antes de ejecutar el siguiente workflow.
