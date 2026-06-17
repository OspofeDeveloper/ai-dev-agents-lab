---
name: kb-design-system-contract
description: Contrato normativo y SSoT del DESIGN.md como artefacto de producto SDD: formato Google design.md, frontmatter YAML obligatorio (visual_personality, color light/dark, type scale, iconography, motion, voice, reference apps, procedencia origin/direction_confidence), secciones canonicas en orden estable, quoting en components y estados aplicables por componente.
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Design System Contract

Esta KB es la SSoT del contrato de `DESIGN.md`: que es como artefacto, que formato sigue, que campos del frontmatter son obligatorios, en que orden van las secciones y que estados debe declarar cada componente.

Las reglas de proceso de los artefactos de feature (trazabilidad a journeys/CAs, descomposicion en `*_flows.md` / `*_views.md` / `*_ui_prompt.md`) viven en `kb-design-feature-artifacts`. La consumibilidad por plan y la evolucion (delta vs regeneracion) viven en `kb-design-governance`. Las reglas de a11y aplicadas al producto viven en `kb-a11y-expert`. Esta KB se limita al contrato del artefacto.

## Regla 1: DESIGN.md es un artefacto de producto, no de feature

Por defecto, `DESIGN.md` vive a nivel de producto y se comparte entre todas las features del producto.

Incluye:
- tokens visuales reutilizables
- principios de jerarquia y composicion
- patrones base de componentes
- tono de interfaz y voice/copy UI
- reglas de estados comunes

No incluyas:
- journeys concretos de una feature
- navegacion detallada pantalla a pantalla
- copy especifico de una HU concreta

Las excepciones deben ser explicitas: una feature puede anadir notas locales, pero no puede crear una segunda fuente normativa del sistema visual.

`DESIGN_GAP` es el marcador canonico de esta KB para todo hueco del contrato que falta cerrar (campo obligatorio sin definir, equivalente de color ausente, Reference App no inferible). Su SSoT vive aqui; las reglas R4, R6 y R9 lo usan y el resto de la fase lo hereda.

## Regla 2: Formato Google design.md con orden estable de secciones

`DESIGN.md` sigue la especificacion oficial `@google/design.md`:
- **Frontmatter YAML**: tokens con tipos estrictos
- **Cuerpo markdown**: rationale y guidance en prose

Los tokens son los valores normativos. El markdown explica intencion, tono y reglas de aplicacion.

**Secciones canonicas** — deben aparecer en este orden exacto entre si:
- `## Overview`
- `## Colors`
- `## Typography`
- `## Layout`
- `## Elevation & Depth`
- `## Shapes`
- `## Components`
- `## Do's and Don'ts`

**Secciones custom** — el linter las preserva sin error; incluirlas en estas posiciones recomendadas:
- `## Visual Personality` → despues de `## Overview`, antes de `## Colors`
- `## Color Modes` → despues de `## Colors`, antes de `## Typography`
- `## Accessibility` → despues de `## Components`, antes de `## Motion & Micro-interactions`
- `## Motion & Micro-interactions` → despues de `## Accessibility`, antes de `## Reference Apps`
- `## Reference Apps` → despues de `## Motion`, antes de `## Voice & Microcopy`
- `## Voice & Microcopy` → despues de `## Reference Apps`, antes de `## Do's and Don'ts`
- `## Changelog` → al final del documento

**Token types validos:**
- `colors`: hex `"#RRGGBB"` en sRGB
- `typography`: objeto con `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`. Para cifras tabuladas usar `fontFeature: "tnum"` — **nunca `fontVariantNumeric`** (no es campo valido del schema)
- `spacing` / `rounded`: strings con unidad (`"8px"`, `"1rem"`, `"0.875rem"`)
- `components`: propiedades estandar reconocidas por el linter: `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. Otras (`minHeight`, `borderColor`, `placeholderColor`, etc.) son toleradas pero generan warnings. Referencias con `{categoria.nombre}`.
- `visual_personality` / `motion` / `accessibility`: objetos libres — el linter los preserva sin validarlos. Pueden usar enteros, booleans y strings sin restriccion.

**Quoting obligatorio dentro de `components:`** — todos los valores dentro de `components:` deben ser **strings entrecomillados**, incluidos numericos como `fontWeight` o dimensiones. Un valor bare integer (ej. `fontWeight: 600`) hace crashear el linter con `raw.match is not a function`, porque internamente llama `.match()` a cada valor buscando referencias `{tokens.x}`. Correcto: `fontWeight: "600"`, `padding: "16px 24px"`, `minHeight: "48dp"`. Esta restriccion **solo aplica a `components:`**; los bloques top-level (`typography`, `accessibility`, etc.) pueden usar enteros/booleans bare sin problema.

Validar el resultado con `npx @google/design.md lint DESIGN.md`: cubre orden de secciones canonicas, referencias rotas, presencia de al menos un color primario y contraste WCAG AA en pares de color.

> Los criterios normativos de accesibilidad (contraste, touch targets, dynamic type, motion, focus, labels, anuncios live) viven en `kb-a11y-expert`. La seccion `## Accessibility` del `DESIGN.md` materializa esos criterios para el producto; no los redefine aqui.

**`accessibility.target_platforms` (SSoT de superficie a nivel sistema).** El bloque `accessibility` del frontmatter declara `target_platforms`: la lista de superficies que cubre el producto (`mobile`, `desktop`, `web`), copiada del `DESIGN_BRIEF.md`. Es **obligatorio en cuanto el brief declara más de una superficie o incluye web/desktop** (de lo contrario, default `[mobile]`). Razón: el `DESIGN.md` es el contrato compartido entre superficies — un producto multi-superficie (app móvil + desktop + web) tiene UN `DESIGN.md` con `target_platforms: [mobile, desktop, web]`, y los artefactos por feature (`flows`/`views`/`ui_prompt`) derivan de él por superficie (ver `kb-design-feature-artifacts`). Cuando incluye web/desktop, declarar también `min_target_pointer` (puntero fino, `kb-a11y-web-expert` Regla 2). No se forkea el `DESIGN.md` por superficie: lo que diverge son los artefactos de feature, no el sistema.

## Regla 3: Visual Personality es obligatorio y estructurado

`DESIGN.md` debe incluir la seccion `## Visual Personality` y su bloque `visual_personality:` en el frontmatter YAML. Sin esta seccion, el agente y el generador de UI (Stitch u otro) no tienen un norte de caracter visual y el output es generico.

La eleccion de estilo se rige por `kb-design-style-taxonomy`. No uses etiquetas vagas como unica decision normativa.

**En el frontmatter:**
```yaml
visual_personality:
  style_family: productive-minimal
  secondary_family: depth-material
  density: medium
  depth: low
  typography_mode: utilitarian
  color_energy: low
  motion_level: low
  adjectives:
    - adjetivo_1: implicacion concreta en UI
    - adjetivo_2: implicacion concreta en UI
  anti_patterns:
    - evitar_1
    - evitar_2
```

Campos:
- `style_family`: familia principal cerrada, elegida segun `kb-design-style-taxonomy`
- `secondary_family`: opcional, solo si ayuda a matizar sin mezclar direcciones incompatibles
- `density`, `depth`, `typography_mode`, `color_energy`, `motion_level`: usar exclusivamente los valores validos y reglas de `kb-design-style-taxonomy`
- `adjectives`: 5-7 adjetivos con implicacion concreta
- `anti_patterns`: 2-4 resultados visuales a evitar

**En la seccion markdown:**
- 5-7 adjetivos de marca con su implicacion concreta en decisiones de UI (no basta listar el adjetivo sin la implicacion)
- 2-4 anti-patrones: lo que este sistema visual explicitamente NO es, con el comportamiento concreto a evitar
- explicacion breve de por que la `style_family` elegida encaja con el producto, actor y tarea dominante

**Como derivar los adjetivos:**
- Del PRD: nombre del producto, vision, audiencia objetivo y diferenciadores
- Del spec: contexto de uso (frecuencia, urgencia, tipo de datos), tipo de tarea del actor

Si no hay PRD disponible, derivar desde el spec: un spec de finanzas personales con foco en velocidad operativa y legibilidad numerica conduce a una familia `productive-minimal` con `typography_mode: utilitarian`. Un spec de fitness con gamificacion suele conducir a `expressive-modern` con `color_energy: high` y `motion_level: medium`.

## Regla 4: Reference Apps obligatorias

`DESIGN.md` debe incluir la seccion `## Reference Apps` con 3-5 apps reales del mercado en la misma categoria de producto.

**Formato de cada referencia:**
- Nombre de la app
- Aspecto concreto a tomar (no solo el nombre): densidad, paleta, tipografia, componentes, micro-interacciones
- Por que es relevante para este producto concreto

Las referencias se obtienen via web research en el `wf-design-system` antes de delegar al agente. Si no hay research disponible, marcar la seccion con `[DESIGN_GAP: investigar apps de referencia en la categoria <nombre_categoria>]` en lugar de inventar referencias.

Un DESIGN.md sin Reference Apps obliga al generador de UI a generar el estilo sin norte → resultado amateur. Una referencia concreta ("tomar de Revolut la densidad de informacion en listas y la tipografia numerica prominente") guia al generador hacia decisiones profesionales.

## Regla 5: Familia de estilo antes que tokens

Antes de elegir colores, tipografia, radios o componentes, decide la familia visual base siguiendo `kb-design-style-taxonomy`.

Orden correcto:
1. contexto de producto y actor
2. `style_family` y perfil estructurado de `visual_personality`
3. apps de referencia
4. tokens y componentes

Si el documento salta directamente a tokens sin haber fijado `style_family`, la direccion visual queda infraespecificada y tendera a lo generico.

## Regla 6: DESIGN.md materializa el brief, no lo reabre

Cuando exista `DESIGN_BRIEF.md`, `DESIGN.md` debe materializar sus decisiones cerradas. No reabras variables ya fijadas en el brief salvo contradiccion clara con spec o PRD.

La jerarquia de fuentes y el listado de variables gobernadas por el brief son SSoT de `kb-design-brief` Regla 10. Cuando aqui se diga "el brief manda", se entiende segun esa regla.

Implicacion practica para el agente:
- Si `DESIGN.md` propuesto contradice el brief, el agente lo corrige antes de escribir.
- Si la contradiccion procede del spec o el PRD, el agente la senala como `DESIGN_GAP` en lugar de decidir unilateralmente.

## Regla 7: Componentes deben declarar todos los estados aplicables

Cualquier componente interactivo declarado en `DESIGN.md` o referenciado en `*_views.md` debe enumerar todos los estados que aplican a su tipologia. Esta es la causa mas comun de regresiones visuales en dev.

Estados base por tipo:

- **Interactivos (button, link, tab, toggle, checkbox, radio, switch)**: `default`, `hover` (solo si target_platforms incluye Web/desktop), `focus-visible`, `active` (pressed), `disabled`, `loading` (si aplica accion async), `selected` (si aplica multi-estado).
- **Inputs (text-input, textarea, select, date-picker, file-picker)**: `default`, `focus`, `filled`, `valid`, `invalid`, `disabled`, `read-only`. Adicionales: `loading` si valida async.
- **Contenedores con estado (card, list-item, accordion)**: `default`, `hover` (si interactivo), `selected`, `disabled`, `loading`, `expanded`/`collapsed` (si aplica).
- **Indicadores (badge, tag, chip)**: `default`, `selected`, `removable` (si aplica), `disabled`.
- **Vistas grandes (page, sheet, modal, drawer)**: `entering`, `default`, `exiting`. Para pantallas con datos, los estados de vista (loading/empty/error/success) viven en `*_views.md` y se rigen por `kb-design-feature-artifacts` Regla 4.

Reglas comunes:

1. Si un estado aplica al componente segun esta tabla y no se declara, `wf-design-validate` lo marca como `[ALTO]`.
2. Cada estado declarado debe tener decisiones visuales concretas (color, opacity, border, motion). Estado sin decision es decoracion vacia.
3. La omision intencional de un estado (`disabled` no aplica porque el boton siempre esta activo en esa vista) debe documentarse con `# N/A: <razon>`.

→ Checklist detallado por componente: `${CLAUDE_SKILL_DIR}/references/component_anatomy_checklist.md` (SSoT unica del checklist; lo cargan esta KB y `wf-design-validate`).

Anti-patron: declarar solo `default` y dejar que dev "improvise" los demas. El producto saldra inconsistente.

## Regla 8: Type scale completa y obligatoria

`DESIGN.md` debe declarar una type scale completa en el frontmatter YAML, no solo `font-family`. Sin scale, cada feature inventa sus tamanos.

Roles minimos obligatorios:

- `display`: tamano hero (40-72px segun densidad), uso en empty states, landing, milestones.
- `h1`/`h2`/`h3`: jerarquia de pantalla. Como minimo dos niveles, idealmente tres.
- `body`: texto base de lectura (14-17px segun densidad).
- `body-sm`: secundario (12-14px).
- `label`: etiquetas de campo, botones, tags (11-13px, normalmente medium weight).
- `caption`: metadata, helper text (10-12px).
- `code` (si aplica): tipografia monoespaciada para contenido tecnico.

Cada rol declara:

- `size` (px o rem)
- `line-height` (numero o px)
- `font-weight` (numerico: 400, 500, 600, 700)
- `letter-spacing` (px, normalmente negativo en displays grandes y positivo en labels)
- `text-transform` si aplica (uppercase en labels operativos, none en el resto)

`typography_mode` del brief sugiere la familia de fuentes y el peso base:

- `utilitarian`: family Inter/IBM Plex/SF Pro, weight base 400, labels en 500.
- `neutral-humanist`: family Inter/Geist/SF Pro, contrastes de peso suaves.
- `brand-forward`: dos fuentes (display custom + body neutral), pesos contrastados.
- `editorial`: serif para display y h1-h2, sans para body.

Anti-patron: declarar solo "tipografia Inter 16px" y permitir que cada vista invente jerarquia. El producto pierde jerarquia visual.

## Regla 9: Color modes light y dark obligatorios

`DESIGN.md` debe declarar al menos modo `light` y modo `dark`. El modo `high-contrast` es opcional pero recomendado si `accessibility_target: AAA`.

Estructura de tokens de color en el frontmatter:

```yaml
colors:
  light:
    background: <token o valor>
    surface: <token o valor>
    surface-elevated: <token o valor>
    on-background: <texto sobre background>
    on-surface: <texto sobre surface>
    primary: <token o valor>
    on-primary: <texto sobre primary>
    border: <token o valor>
    success: <token o valor>
    warning: <token o valor>
    error: <token o valor>
    info: <token o valor>
  dark:
    background: <...>
    surface: <...>
    # ... mismas claves que light
```

Reglas:

1. Cada token de color en `light` tiene su equivalente en `dark`. Faltar uno es `DESIGN_GAP`.
2. Cada par foreground/background (ej. `on-primary` sobre `primary`) cumple el ratio de contraste del `accessibility_target` del brief. Esto lo verifica `wf-design-a11y-audit`.
3. Modo `dark` no es invertir colores literalmente: redefine surface, on-surface y elevation para preservar legibilidad. Usar superficies cercanas a negro puro (#0E0E10) en lugar de #000 plano.
4. La politica de seleccion de modo (automatica via system, manual via toggle, fija) se documenta en `## Color Modes` del markdown.

Anti-patron: declarar solo `light` y dejar dark mode como "lo hara el dev". Resultado: dark mode roto en produccion.

## Regla 10: Procedencia y confianza de direccion en el frontmatter

El frontmatter del `DESIGN.md` declara **de donde viene** y **cuanto se puede confiar en su direccion visual**. Dos campos de procedencia, ambos opcionales en lectura pero con semantica fija:

```yaml
origin: generated            # generated | generated-provisional | extracted
direction_confidence: confirmed   # confirmed | provisional   (solo relevante cuando origin es generated-*)
```

**`origin` — tres valores cerrados:**

| Valor | Significado | Quien lo escribe |
|---|---|---|
| `generated` | Direccion visual derivada de fuente humana fiable (brief cerrado con confirmacion, o direccion confirmada explicitamente). Es el valor por defecto de un `DESIGN.md` sano generado desde el pipeline | `wf-design-system` cuando la direccion esta anclada o el usuario la confirma |
| `generated-provisional` | Direccion visual inferida **sin** fuente humana fiable (`--no-brief`, brief en modo `auto`/`ai-default`, o research de Reference Apps pobre/ausente) y aun **no confirmada** por un humano | `wf-design-system` cuando la direccion queda no anclada y no se confirma |
| `extracted` | `DESIGN.md` derivado por ingenieria inversa de una UI en produccion. Sus campos de procedencia adicionales (`evidence_base`, `evidence_coverage`) y su metodologia viven en `kb-design-characterization` | `wf-design-extract` / modo `design-extract` |

La **ausencia** del campo `origin` se interpreta como `generated` (compatibilidad con `DESIGN.md` previos al campo). Los tres valores son mutuamente excluyentes: un mismo `DESIGN.md` no puede ser a la vez `generated-provisional` y `extracted`.

**`direction_confidence` — dos valores cerrados:**

- `provisional`: la direccion visual (`style_family`, paleta primaria/accent, `motion_level`) se infirio sin evidencia humana fiable. Acompaña a `origin: generated-provisional`.
- `confirmed`: la direccion fue confirmada por un humano (en el origen, vía `wf-design-system`, o al validar, vía `wf-design-validate`). Acompaña a `origin: generated`.

Cuando `direction_confidence: provisional`, los campos de direccion inferidos sin evidencia se marcan con el marcador **`[INFERIDO]`** ya definido para la fase (SSoT en `kb-design-characterization`) — **NO se inventa un marcador nuevo**. Igual que en caracterizacion, **`[INFERIDO]` aqui NO bloquea ningun gate del pipeline**: la fase Design no tiene gate ni sellador mecanico (`sdd-gate-check.py` / `sdd-seal.py` operan solo sobre specs y planes). El sello es informativo; el enforcement real es la **confirmacion humana** descrita en el ciclo de vida.

**El ciclo de vida `provisional → confirmed`** (que lo dispara, quien lo pone, quien lo limpia, su traza en `## Changelog`) **no vive aqui**: es la dimension temporal/operativa del artefacto y su SSoT es `kb-design-governance` Regla 5. Esta KB solo fija los **valores validos** del frontmatter; la gobernanza fija su transicion.

> Coherencia con `kb-design-characterization`: esa KB documenta el header `origin: extracted` (+ `evidence_base`, `evidence_coverage`) del camino brownfield. Los tres valores de `origin` conviven limpio: `extracted` es ortogonal a la dimension de confianza de direccion (`direction_confidence` no aplica a un `extracted`, cuya confianza se expresa con `evidence_coverage`).

## KB Load Status

Esta KB no declara dependencias `skills:`; no aplica el protocolo de verificacion.
