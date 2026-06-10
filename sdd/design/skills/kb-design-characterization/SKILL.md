---
name: kb-design-characterization
description: "Reglas para extraer un DESIGN.md desde una UI ya en produccion (CSS/tokens/componentes/capturas): evidencia obligatoria por token/decision visual, jerarquia de evidencia, marcador [INFERIDO], documentar inconsistencias reales sin promediarlas, header origin: extracted. No es el contrato del DESIGN.md (ver kb-design-system-contract) ni el marco de la fase design (ver kb-design-expert)."
effort: medium
allowed-tools: [Read]
user-invocable: false
---

# Design Characterization (ingenieria inversa de UI existente)

Un `DESIGN.md` **extraido** describe **como se ve hoy la UI en produccion, verificado contra el codigo/CSS/capturas** — no como deberia verse ni la intencion de marca. Es la entrada alternativa a la fase `design` cuando no se va a rediseñar: la UI existente es la unica fuente de verdad disponible.

Esta KB es el espejo en la fase `design` de `kb-spec-characterization` (specs de caracterizacion brownfield). Cubre **solo la metodologia de extraccion**. No redefine:

- el **contrato** del `DESIGN.md` (frontmatter YAML, secciones canonicas, type scale, color modes, quoting, estados de componente) → `kb-design-system-contract`. El DESIGN.md extraido conforma a ese contrato; esta KB solo añade los campos de procedencia.
- el **marco** de la fase (separacion producto/feature, orden del pipeline) → `kb-design-expert`. De ahi se hereda el marcador `DESIGN_GAP`.
- la **gobernanza** (versionado semver, extender vs mutar) → `kb-design-governance`.

## Regla de oro

**Un token o decision visual sin evidencia no se inventa.** Cada token, color, valor tipografico, radio, spacing, componente o estado del `DESIGN.md` extraido traza a un puntero verificable en la UI real, o se marca `[INFERIDO]` / `DESIGN_GAP`. Si no puedes señalar donde la UI produce ese valor, no lo escribas como decision firme.

## Jerarquia de evidencia (de mas a menos fuerte)

1. **Fichero de design tokens / CSS custom properties declaradas** — `Evidencia: <archivo> (--color-primary: #2F6BFF)`. La fuente de verdad de los autores del producto; maxima fuerza.
2. **Regla CSS/SCSS leida con ruta exacta** — `Evidencia: <archivo:linea-linea>` (`.btn-primary { background: #2F6BFF }`).
3. **Valor declarado en el codigo de un componente** — `Evidencia: <archivo:linea>` (React/Vue/Compose/SwiftUI/etc.: un `style={{ borderRadius: 8 }}`, un `RoundedCornerShape(8.dp)`).
4. **Observacion medida/muestreada de captura de pantalla** — `Evidencia: captura <nombre> (color picker / medicion de spacing)`. Confianza menor: depende de render, zoom y antialiasing.
5. **`[INFERIDO]`** — valor deducido (escala tipografica derivada de dos tamaños observados, un estado `disabled` no encontrado en el codigo, dark mode ausente que se propone) pero **no observado directamente**.

No bajes el liston: con menos acceso, MAS lecturas con ruta exacta o mediciones, no menos.

## Marcador `[INFERIDO]` para Design

A nivel de token, estado, componente o seccion no observable en la UI real. Formato:

```markdown
# [INFERIDO] type scale display=40px — derivado de body=16px y h1=24px observados; no hay un rol "display" usado en el CSS actual.
```

o, en una decision de seccion completa:

```markdown
## Motion & Micro-interactions
[INFERIDO] No se observaron transiciones declaradas en el CSS. Valores propuestos por convencion; confirmar con el equipo.
```

**Diferencia critica con spec — `[INFERIDO]` aqui NO bloquea ningun gate del pipeline.** Los gates y selladores deterministas (`sdd-gate-check.py`, `sdd-seal.py`) operan sobre **specs y planes**, no sobre `DESIGN.md`: la fase Design no tiene gate mecanico de sellado. Por tanto un `[INFERIDO]` en un `DESIGN.md` extraido:

- se **reporta** al usuario en el informe de `wf-design-extract`,
- es lo que `wf-design-validate` debe **señalar** al auditar el contrato,
- pero **no detiene** `wf-prepare-plan` ni ningun workflow aguas abajo.

No sobre-afirmes un enforcement mecanico que no existe. La señal es informativa: el `[INFERIDO]` es una invitacion a aportar contexto humano, no un bloqueo.

Para huecos donde falta evidencia y se necesita aporte humano que la herramienta no puede deducir, usa **`DESIGN_GAP`** (marcador ya existente de la fase, SSoT en `kb-design-expert`): p. ej. Reference Apps no inferibles de la UI, o un `visual_personality` que el CSS no permite caracterizar.

## Header obligatorio del DESIGN.md extraido

El `DESIGN.md` extraido conforma al frontmatter del contrato (`kb-design-system-contract`) y **añade** estos campos de procedencia — no inventa un formato nuevo:

```yaml
origin: extracted
evidence_base: <commit SHA corto> (<fecha>)
evidence_coverage: <descripcion del nivel de acceso>   # ej. "design tokens + CSS" | "solo CSS suelto" | "solo capturas — sin acceso al codigo"
```

`evidence_base` ancla el `DESIGN.md` en el tiempo: los valores eran verdad en ese commit. Si la UI avanza, el `DESIGN.md` puede estar desactualizado — eso es deriva, no error.

La seccion `## Changelog` del `DESIGN.md` **arranca** con la entrada de extraccion:

```markdown
## Changelog
- v1.0.0 — extraido de la UI en produccion (commit <SHA>, <fecha>). Cobertura: <evidence_coverage>. <N> tokens con evidencia directa, <M> [INFERIDO].
```

## Lo que NUNCA hace una extraccion

| Prohibido | Por que |
|---|---|
| Inventar `visual_personality` / adjetivos / `style_family` sin evidencia | El caracter visual debe inferirse del CSS real (paleta, densidad, radios, tipografia). Si no es inferible, va `[INFERIDO]` o `DESIGN_GAP` — nunca un adjetivo de marca elegido por gusto |
| "Limpiar" inconsistencias reales convirtiendolas en un sistema falsamente coherente | Si la UI usa 5 azules distintos, se **documentan los 5** con su evidencia y una nota `[INCONSISTENTE]` (o equivalente); NO se promedian a uno. Caracterizar es documentar lo que HAY. Unificar es rediseñar — decision posterior via `wf-design-delta` |
| Inventar dark mode si no existe en la UI | El contrato pide light+dark, pero un dark mode ausente se marca `[INFERIDO]` / `DESIGN_GAP`, no se fabrica una paleta oscura plausible |
| Inventar Reference Apps | No son observables en la propia UI → `DESIGN_GAP` (mismo criterio que `kb-design-system-contract` Regla 4 cuando no hay research) |
| Inventar estados de componente no observados | Un `hover`/`focus`/`disabled` que el CSS no define va `[INFERIDO]`, no un valor "estandar" |

## Inconsistencias reales: documentar, no promediar

La UI heredada casi siempre es inconsistente. La extraccion lo **refleja con honestidad**:

```markdown
## Colors
[INCONSISTENTE] La UI usa varios azules para "primary":
- `#2F6BFF` — `tokens.css:12` (--color-primary), usado en botones
- `#1E5FE0` — `header.css:44`, usado en el nav
- `#3B82F6` — `card.tsx:88`, hardcoded
Documentado tal cual. Unificar a un primary unico es rediseño → wf-design-delta.
```

El `DESIGN.md` extraido es un **espejo fiel**, no una version idealizada. Promediar destruye informacion que el equipo necesita para decidir el rediseño.

## Degradacion por nivel de acceso

| Acceso disponible | Evidencia maxima | Como se declara |
|---|---|---|
| Fichero de design tokens / CSS custom properties | Nivel 1 | `evidence_coverage: design tokens declarados` |
| Solo CSS/SCSS suelto (sin tokens centralizados) | Nivel 2 (leido con ruta) | `evidence_coverage: CSS suelto — valores leidos con archivo:linea` |
| Solo capturas (sin acceso al codigo) | Nivel 4 (medido/muestreado) | `evidence_coverage: solo capturas — sin acceso al codigo; confianza reducida` |

Con menor acceso, la confianza global baja y **se declara en el header**. No se finge nivel 1 cuando solo hay capturas.

## Relacion con el resto del pipeline

- El `DESIGN.md` extraido fluye como cualquier `DESIGN.md`: auditable con `wf-design-validate`, evolucionable con `wf-design-delta`, exportable con `wf-design-export`.
- **Caso tipico de 3.4 (proyecto que NO se va a rediseñar)**: el `DESIGN.md` extraido es el **contrato a respetar**, no un punto de partida a reemplazar. El equipo de codigo y futuras features se alinean con lo que la UI ya es.
- **"Se ve asi hoy pero quiero cambiarlo"** = `wf-design-delta` sobre el `DESIGN.md` extraido — el delta separa limpio lo que la UI hace de lo que se quiere cambiar (mismo principio que `wf-spec-delta` sobre un spec de caracterizacion).
- Si el cambio toca `style_family` o variables del brief, no hay brief que tocar (la extraccion no genera `DESIGN_BRIEF.md`): el rediseño profundo arranca con `wf-design-intake` para fijar la nueva direccion antes de mutar el `DESIGN.md`.
