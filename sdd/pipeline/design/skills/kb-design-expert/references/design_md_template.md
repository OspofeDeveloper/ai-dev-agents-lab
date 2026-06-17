# Template de DESIGN.md

```md
---
version: 0.1.0
name: <Nombre del producto>
description: <Resumen breve del tono visual y contexto del producto>
origin: generated                  # generated | generated-provisional | extracted (kb-design-system-contract Regla 10)
direction_confidence: confirmed    # confirmed | provisional (solo en origin generated-*; provisional → marcar campos de direccion con [INFERIDO])
visual_personality:
  style_family: productive-minimal
  secondary_family: none
  density: medium
  depth: low
  typography_mode: utilitarian
  color_energy: low
  motion_level: low
  adjectives:
    - <adjetivo_1>: <implicacion concreta en UI>
    - <adjetivo_2>: <implicacion concreta en UI>
  anti_patterns:
    - <evitar_1>
    - <evitar_2>
colors:
  light:
    background: "#F7F7F5"
    surface: "#FFFFFF"
    surface-elevated: "#FFFFFF"
    on-background: "#0E0E10"
    on-surface: "#0E0E10"
    on-surface-muted: "#5C5C68"
    primary: "#0E0E10"
    on-primary: "#FFFFFF"
    accent: "#0F766E"
    on-accent: "#FFFFFF"
    border: "#E5E5E5"
    border-strong: "#C8C8CC"
    success: "#15803D"
    on-success: "#FFFFFF"
    warning: "#B45309"
    on-warning: "#FFFFFF"
    error: "#B91C1C"
    on-error: "#FFFFFF"
    info: "#1D4ED8"
    on-info: "#FFFFFF"
  dark:
    background: "#0E0E10"
    surface: "#1A1A1D"
    surface-elevated: "#252529"
    on-background: "#F7F7F5"
    on-surface: "#F7F7F5"
    on-surface-muted: "#9A9AA4"
    primary: "#FFFFFF"
    on-primary: "#0E0E10"
    accent: "#2DD4BF"
    on-accent: "#0E0E10"
    border: "#2C2C32"
    border-strong: "#3F3F46"
    success: "#22C55E"
    on-success: "#0E0E10"
    warning: "#F59E0B"
    on-warning: "#0E0E10"
    error: "#EF4444"
    on-error: "#FFFFFF"
    info: "#3B82F6"
    on-info: "#FFFFFF"
color_mode_policy:
  default: system
  user_toggle: true
  high_contrast: optional
typography:
  display:
    fontFamily: <Familia display>
    fontSize: 3rem
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: -0.02em
  h1:
    fontFamily: <Familia principal>
    fontSize: 2rem
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: -0.015em
  h2:
    fontFamily: <Familia principal>
    fontSize: 1.5rem
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: -0.01em
  h3:
    fontFamily: <Familia principal>
    fontSize: 1.25rem
    fontWeight: 600
    lineHeight: 1.25
  body:
    fontFamily: <Familia secundaria>
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: <Familia secundaria>
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: <Familia secundaria>
    fontSize: 0.8125rem
    fontWeight: 500
    lineHeight: 1.3
  caption:
    fontFamily: <Familia secundaria>
    fontSize: 0.75rem
    fontWeight: 400
    lineHeight: 1.35
  code:
    fontFamily: <Familia monoespaciada>
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.45
    fontFeature: "tnum"
rounded:
  sm: 8px
  md: 16px
  lg: 24px
  pill: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
elevation:
  level-0: none
  level-1: "0 1px 2px rgba(14, 14, 16, 0.06)"
  level-2: "0 4px 12px rgba(14, 14, 16, 0.08)"
  level-3: "0 12px 32px rgba(14, 14, 16, 0.12)"
iconography:
  library: lucide
  style: outline
  stroke_width: 1.5
  stroke_linecap: round
  stroke_linejoin: round
  grid: 24
  sizes:
    inline-xs: 12
    inline-sm: 16
    base: 20
    prominent: 28
    hero: 48
  semantic_colors:
    success: "{colors.light.success}"
    error: "{colors.light.error}"
    warning: "{colors.light.warning}"
    info: "{colors.light.info}"
motion:
  level: low
  reduced_motion_policy: "respect_system; sustituye transitions por cross-fade de fast y desactiva expression."
  durations:
    instant: 0
    fast: 120
    base: 220
    medium: 320
    slow: 500
  easing:
    feedback: "cubic-bezier(0.0, 0.0, 0.2, 1)"
    transition: "cubic-bezier(0.4, 0.0, 0.2, 1)"
    attention: "cubic-bezier(0.34, 1.56, 0.64, 1)"
    enter: "cubic-bezier(0.0, 0.0, 0.2, 1)"
    exit: "cubic-bezier(0.4, 0.0, 1.0, 1)"
  style: functional
accessibility:
  wcag_target: AA
  target_platforms: [mobile]   # superficies que cubre el producto: mobile | desktop | web (copiado del DESIGN_BRIEF.md). SSoT a nivel sistema.
  contrast_policy: "WCAG AA: 4.5:1 texto normal, 3:1 texto grande / UI components / focus indicators"
  min_touch_target: "44pt iOS / 48dp Android"
  min_target_pointer: "24px"   # tamano minimo de target para puntero fino (solo si target_platforms incluye web/desktop — kb-a11y-web-expert Regla 2)
  min_touch_spacing: "8dp"
  dynamic_type: true
  reduce_motion: respect_system
voice:
  formality: neutral
  expertise: mixto
  warmth: neutro
  playfulness: serio
  case_style: sentence
  emoji_policy: vetados
components:
  button-primary:
    default:
      backgroundColor: "{colors.light.primary}"
      textColor: "{colors.light.on-primary}"
      rounded: "{rounded.md}"
      padding: "12px 20px"
      typography: "{typography.label}"
    hover:
      backgroundColor: "{colors.light.primary}"
      textColor: "{colors.light.on-primary}"
      opacity: "0.92"
    focus-visible:
      backgroundColor: "{colors.light.primary}"
      textColor: "{colors.light.on-primary}"
      outlineColor: "{colors.light.accent}"
      outlineWidth: "2px"
      outlineOffset: "2px"
    active:
      backgroundColor: "{colors.light.primary}"
      opacity: "0.88"
      transform: "scale(0.98)"
    disabled:
      backgroundColor: "{colors.light.border}"
      textColor: "{colors.light.on-surface-muted}"
      opacity: "0.6"
    loading:
      backgroundColor: "{colors.light.primary}"
      textColor: "{colors.light.on-primary}"
      cursor: "wait"
  input-text:
    default:
      backgroundColor: "{colors.light.surface}"
      borderColor: "{colors.light.border}"
      textColor: "{colors.light.on-surface}"
      rounded: "{rounded.sm}"
      padding: "12px 14px"
    focus:
      backgroundColor: "{colors.light.surface}"
      borderColor: "{colors.light.accent}"
      outlineColor: "{colors.light.accent}"
      outlineWidth: "2px"
    filled:
      backgroundColor: "{colors.light.surface}"
      borderColor: "{colors.light.border-strong}"
    invalid:
      backgroundColor: "{colors.light.surface}"
      borderColor: "{colors.light.error}"
      textColor: "{colors.light.on-surface}"
    disabled:
      backgroundColor: "{colors.light.background}"
      borderColor: "{colors.light.border}"
      textColor: "{colors.light.on-surface-muted}"
      opacity: "0.6"
    read-only:
      backgroundColor: "{colors.light.background}"
      borderColor: "{colors.light.border}"
      textColor: "{colors.light.on-surface}"
  card-default:
    default:
      backgroundColor: "{colors.light.surface}"
      borderColor: "{colors.light.border}"
      rounded: "{rounded.md}"
      padding: "{spacing.lg}"
      elevation: "{elevation.level-1}"
    hover:
      backgroundColor: "{colors.light.surface}"
      elevation: "{elevation.level-2}"
    selected:
      backgroundColor: "{colors.light.surface}"
      borderColor: "{colors.light.accent}"
      borderWidth: "2px"
---

## Overview

Describe el caracter general del producto, la sensacion que debe transmitir y 2-4 principios de marca en prose o bullets cortos.

## Visual Personality

Define el caracter visual del producto con un perfil estructurado y adjetivos concretos. Usa el bloque `visual_personality` del frontmatter como guia.

- **Familia de estilo**: explica por que `style_family` encaja con el producto, el actor y la tarea dominante.
- **Perfil operativo**: resume como se traducen `density`, `depth`, `typography_mode`, `color_energy` y `motion_level` en decisiones visibles de interfaz.

- **<adjetivo>**: implicacion concreta — ej. "veloz → transiciones < 200ms, sin animaciones decorativas que retrasen feedback"
- **<adjetivo>**: implicacion concreta

Anti-patrones — lo que este sistema visual explicitamente NO es:
- **<evitar>**: comportamiento concreto que hay que evitar y por que

## Colors

Explica como usar la paleta, donde reservar el color acento y que colores evitar. Documenta el uso de cada token semantico (background, surface, primary, accent, success, error, etc.).

## Color Modes

Politica de modos de color (Regla 9 de `kb-design-system-contract`):

- **Modos soportados**: light + dark obligatorios; high-contrast opcional segun `accessibility_target`.
- **Seleccion del modo**: <system | manual | fija>. Si admite toggle, donde vive el control.
- **Reglas para dark mode**: surface base con valor cercano a `#0E0E10` (no `#000` plano), elevation con superficies mas claras (no sombras), accent ligeramente desaturado o iluminado para preservar contraste.
- **High-contrast (si aplica)**: bordes mas marcados, sin transparencias, contraste minimo 7:1.
- **Imagenes y media**: como se adaptan al modo (filtros, alternativas, tratamiento de fotografias).

## Typography

Explica jerarquia visual, contraste entre titulares y cuerpo, y tono editorial o utilitario. Cada rol de la type scale (`display`, `h1`-`h3`, `body`, `body-sm`, `label`, `caption`, `code`) tiene uso esperado documentado.

- **Familia(s)**: que fuentes y por que (display, body, mono si aplica).
- **Jerarquia**: como se eligen los roles en cada vista (ej. `display` solo en empty states y onboarding; `h1` una vez por pantalla).
- **Numerica tabular**: si el producto muestra datos numericos, declarar uso de `fontFeature: "tnum"` en `body`/`code`.

## Layout

Define densidad, espaciado, ritmos verticales, anchuras habituales y grid si aplica (solo si `target_platforms` incluye Web o tablet — ver `kb-design-layout`).

## Elevation & Depth

Explica como la app transmite jerarquia y profundidad visual:

- Si se usan sombras, definir niveles semanticos (`level-0` plano, `level-1` cards, `level-2` dialogs, `level-3` sheets).
- Si se usa elevation via color de superficie (fondos con distintos valores en dark mode), describirlo aqui.
- Si el producto es flat-design, indicarlo explicitamente y definir como se separa contenido sin sombras.

## Shapes

Explica el caracter de bordes, radios y geometria general de la identidad. Define cuando usar `rounded.sm`, `rounded.md`, `rounded.lg` y `rounded.pill`.

## Components

Cada componente declara todos los estados aplicables (Regla 7 de `kb-design-system-contract`). En el frontmatter, cada estado tiene sus decisiones visuales. En esta seccion, explica como se sienten los componentes clave: button, input, card, list-item, modal, toast, navigation. Incluye el tratamiento de estados recurrentes:

- **Interactivos**: default, hover (web/desktop), focus-visible, active, disabled, loading, selected.
- **Inputs**: default, focus, filled, valid, invalid, disabled, read-only.
- **Contenedores**: default, hover, selected, expanded/collapsed si aplica.

Si un estado no aplica a un componente, documentarlo con `# N/A: <razon>` en lugar de omitirlo silenciosamente.

## Iconography

Sistema de iconografia del producto segun `kb-design-iconography-expert`:

- **Libreria base**: <Lucide | Phosphor | Material Symbols | SF Symbols | Tabler | custom>. Una sola libreria; mezclar produce inconsistencia.
- **Style + stroke**: outline | filled, stroke width unico (`1.5` o `2`), linecap y linejoin consistentes.
- **Grid**: tamano del lienzo base (24, 20 o 16).
- **Tamanos por rol**: `inline-xs`, `inline-sm`, `base`, `prominent`, `hero` y cuando usar cada uno.
- **Roles semanticos**: action / navigation / status / decoration / metadata. Un icono no cumple dos roles en la misma vista.
- **Iconos custom**: si los hay, declarar el icon set roadmap (que existe, que falta).

## Accessibility

Politica de accesibilidad mobile del producto. Las reglas normativas viven en `kb-a11y-expert`; esta seccion materializa las decisiones concretas para este producto.

- **Target de conformidad**: <AA | AAA> (WCAG 2.2 mapeada a mobile).
- **Contraste**: confirma que cada par foreground/background en `colors.light` y `colors.dark` cumple el ratio (4.5:1 texto normal, 3:1 texto grande / UI / focus). El calculo real de ratios lo verifica `wf-design-a11y-audit`.
- **Touch targets**: tamano minimo declarado en `accessibility.min_touch_target`. Como se garantiza en componentes densos.
- **Dynamic type**: estrategia para soportar font scaling hasta 200% sin perdida de contenido (line-heights relativos, reflow, truncado controlado).
- **Reduce motion**: comportamiento cuando el sistema activa la preferencia, alineado con `motion.reduced_motion_policy`.
- **Focus visible**: descripcion del indicador de foco (color, grosor, offset) y como respeta el ratio 3:1.
- **Screen readers**: politica general de labels (que componentes requieren label explicito, que iconos son decorativos).
- **Imagenes**: tratamiento por defecto de imagenes informativas vs decorativas.

## Motion & Micro-interactions

Catalogo operativo segun `kb-design-motion-expert`:

- **Roles activos**: feedback, transition, attention, expression, orientation — segun `motion.level` declarado.
- **Duraciones**: escala fija del frontmatter (`fast`, `base`, `medium`, `slow`). Cuando usar cada una.
- **Easing**: curvas por rol del frontmatter. No mezclar entre roles.
- **Politica de reduced-motion**: alineada con `motion.reduced_motion_policy`.
- **Micro-interacciones por componente clave**:
  - **Button**: press scale 0.98 + opacity 0.88 durante `fast`.
  - **Input**: focus ring fade-in `base` ease-out.
  - **Modal/Sheet**: enter `medium` ease-out, exit `base` ease-in.
  - **Toast**: enter `base` ease-out, auto-dismiss tras tiempo declarado.
  - **Skeleton**: shimmer cycle linear 1200ms.
- **Lo que NO se anima**: enumerar elementos que cambian sin transicion para no retrasar respuesta percibida.

## Reference Apps

Apps reales del mercado que sirven de norte visual. Para cada referencia indicar el aspecto concreto a tomar, no solo el nombre.

- **<App 1>**: <aspecto concreto — ej. "sistema de cards de saldo, tipografia numerica tabulada, densidad de informacion en lista de transacciones">
- **<App 2>**: <aspecto concreto>
- **<App 3>**: <aspecto concreto>

## Voice & Microcopy

Sistema de voz del producto segun `kb-design-voice`. Debe alinear tono de interfaz, glosario y patrones de microcopy con el `clarity_vs_brand` del brief.

- **Ejes de voz**:
  - `formality`: por que el producto usa un tono mas formal, neutral o cercano.
  - `expertise`: cuanto dominio tecnico puede asumir en labels, errores y ayudas.
  - `warmth`: cuanto expresa empatia explicita en momentos de friccion.
  - `playfulness`: cuanto espacio hay para humor o sorpresa sin estorbar la tarea.
- **Ejemplos canonicos**:
  - Error de red: "<copy ejemplo>"
  - Empty state: "<copy ejemplo>"
  - Confirmacion destructiva: "<copy ejemplo>"
  - Exito: "<copy ejemplo>"
- **Glosario**:
  - **<termino 1>**: <uso canonico>
  - **<termino 2>**: <uso canonico>
  - **<termino 3>**: <uso canonico>
  - **<termino 4>**: <uso canonico>
  - **<termino 5>**: <uso canonico>
- **Politica editorial**:
  - Case style: `sentence` o `title`
  - Puntuacion: cuando se usa punto final en body y errores
  - Emojis: `permitidos | restringidos | vetados`
  - Abreviaturas: cuales se toleran y cuales no
- **Lo que NO decimos**:
  - "<anti-patron de copy 1>"
  - "<anti-patron de copy 2>"

## Do's and Don'ts

- Haz:
  - Regla positiva 1
  - Regla positiva 2
- Evita:
  - Regla negativa 1
  - Regla negativa 2

## Changelog

Registro de cambios al sistema visual (Regla 2 de `kb-design-governance`):

- `[2026-MM-DD]` `[feature: F-001]` <descripcion del cambio>
```
