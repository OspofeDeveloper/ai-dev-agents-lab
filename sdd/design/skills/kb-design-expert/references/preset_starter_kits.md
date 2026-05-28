# Preset starter kits — DESIGN.md base al 70% por preset

Cuando `wf-design-system` corre con un preset declarado en el brief, debe partir del starter kit correspondiente como base de `DESIGN.md`, no de un archivo en blanco. El agente despues precisa adjetivos, Reference Apps y rationale especificos del producto desde spec + brief + research.

Los snippets de componentes con sus estados viven en `preset_components.md`.

---

## `b2b-operational`

### Frontmatter base

```yaml
version: 0.1.0
visual_personality:
  style_family: productive-minimal
  secondary_family: none
  density: medium
  depth: low
  typography_mode: utilitarian
  color_energy: low
  motion_level: low
  adjectives:
    - <a personalizar>
  anti_patterns:
    - generic-saas
    - playful-when-trust-is-required
    - decorative-gradients-without-meaning
    - flat-without-hierarchy
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
typography:
  display:
    fontFamily: Inter
    fontSize: 2.5rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: -0.02em
  h1:
    fontFamily: Inter
    fontSize: 1.75rem
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: -0.015em
  h2:
    fontFamily: Inter
    fontSize: 1.375rem
    fontWeight: 600
    lineHeight: 1.25
  h3:
    fontFamily: Inter
    fontSize: 1.125rem
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: Inter
    fontSize: 0.9375rem
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: Inter
    fontSize: 0.8125rem
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: 500
    lineHeight: 1.3
    textTransform: none
  caption:
    fontFamily: Inter
    fontSize: 0.6875rem
    fontWeight: 400
    lineHeight: 1.35
  code:
    fontFamily: "JetBrains Mono"
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.45
    fontFeature: "tnum"
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  2xl: 32px
rounded:
  sm: 6px
  md: 8px
  lg: 12px
  pill: 9999px
elevation:
  level-0: none
  level-1: "0 1px 2px rgba(14, 14, 16, 0.06)"
  level-2: "0 4px 12px rgba(14, 14, 16, 0.08)"
  level-3: "0 12px 32px rgba(14, 14, 16, 0.12)"
motion:
  level: low
  reduced_motion_policy: "respect_system; sustituye transitions por cross-fade fast"
  durations:
    instant: 0
    fast: 120
    base: 200
    medium: 280
  easing:
    feedback: "cubic-bezier(0.0, 0.0, 0.2, 1)"
    transition: "cubic-bezier(0.4, 0.0, 0.2, 1)"
    enter: "cubic-bezier(0.0, 0.0, 0.2, 1)"
    exit: "cubic-bezier(0.4, 0.0, 1.0, 1)"
  style: functional
iconography:
  library: lucide
  style: outline
  stroke_width: 1.5
  stroke_linecap: round
  stroke_linejoin: round
  grid: 20
  sizes:
    inline-xs: 12
    inline-sm: 14
    base: 18
    prominent: 24
    hero: 40
accessibility:
  wcag_target: AA
  contrast_policy: "WCAG AA: 4.5:1 texto normal, 3:1 UI / focus"
  min_touch_target: "44pt iOS / 48dp Android"
  min_touch_spacing: "8dp"
  dynamic_type: true
  reduce_motion: respect_system
voice:
  formality: neutral
  expertise: tecnico
  warmth: neutro
  playfulness: serio
  case_style: sentence
  emoji_policy: vetados
```

**Componentes incluidos**: `button-primary`, `button-secondary`, `input-text`, `card-default`, `list-item`, `modal` (ver `preset_components.md`).

---

## `consumer-lifestyle`

### Frontmatter base

```yaml
version: 0.1.0
visual_personality:
  style_family: expressive-modern
  secondary_family: none
  density: medium
  depth: low
  typography_mode: brand-forward
  color_energy: medium
  motion_level: medium
  adjectives:
    - <a personalizar>
  anti_patterns:
    - premium-but-illegible
    - flat-without-hierarchy
    - dribbblified-overdesigned
colors:
  light:
    background: "#FAFAF9"
    surface: "#FFFFFF"
    surface-elevated: "#FFFFFF"
    on-background: "#171717"
    on-surface: "#171717"
    on-surface-muted: "#737373"
    primary: "#171717"
    on-primary: "#FAFAF9"
    accent: "#F97316"
    on-accent: "#FFFFFF"
    border: "#E7E5E4"
    border-strong: "#A8A29E"
    success: "#16A34A"
    on-success: "#FFFFFF"
    warning: "#EAB308"
    on-warning: "#171717"
    error: "#DC2626"
    on-error: "#FFFFFF"
    info: "#2563EB"
    on-info: "#FFFFFF"
  dark:
    background: "#0C0A09"
    surface: "#1C1917"
    surface-elevated: "#292524"
    on-background: "#FAFAF9"
    on-surface: "#FAFAF9"
    on-surface-muted: "#A8A29E"
    primary: "#FAFAF9"
    on-primary: "#0C0A09"
    accent: "#FB923C"
    on-accent: "#0C0A09"
    border: "#292524"
    border-strong: "#44403C"
    success: "#22C55E"
    on-success: "#0C0A09"
    warning: "#FACC15"
    on-warning: "#0C0A09"
    error: "#EF4444"
    on-error: "#FFFFFF"
    info: "#3B82F6"
    on-info: "#FFFFFF"
typography:
  display:
    fontFamily: Geist
    fontSize: 3rem
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: -0.025em
  h1:
    fontFamily: Geist
    fontSize: 2rem
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: -0.02em
  h2:
    fontFamily: Geist
    fontSize: 1.5rem
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: -0.01em
  h3:
    fontFamily: Geist
    fontSize: 1.25rem
    fontWeight: 600
    lineHeight: 1.25
  body:
    fontFamily: Inter
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.55
  body-sm:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: Inter
    fontSize: 0.8125rem
    fontWeight: 600
    lineHeight: 1.3
  caption:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: 400
    lineHeight: 1.4
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
rounded:
  sm: 8px
  md: 14px
  lg: 20px
  pill: 9999px
motion:
  level: medium
  reduced_motion_policy: "respect_system; deshabilita expression y sustituye transitions por cross-fade base"
  durations:
    instant: 0
    fast: 140
    base: 240
    medium: 320
    slow: 480
  easing:
    feedback: "cubic-bezier(0.0, 0.0, 0.2, 1)"
    transition: "cubic-bezier(0.4, 0.0, 0.2, 1)"
    attention: "cubic-bezier(0.34, 1.56, 0.64, 1)"
    enter: "cubic-bezier(0.0, 0.0, 0.2, 1)"
    exit: "cubic-bezier(0.4, 0.0, 1.0, 1)"
  style: expressive
iconography:
  library: phosphor
  style: fill
  stroke_width: 0
  grid: 24
  sizes:
    inline-xs: 14
    inline-sm: 18
    base: 22
    prominent: 28
    hero: 56
voice:
  formality: cercano
  expertise: accesible
  warmth: calido
  playfulness: medido
  case_style: sentence
  emoji_policy: permitidos
```

**Componentes incluidos**: `button-primary`, `button-secondary`, `input-text`, `card-feature`, `list-item-rich`, `modal`, `bottom-sheet`.

---

## `fintech-trust`

Base similar a `b2b-operational` con ajustes:
- accent verde `#15803D` o azul `#1E40AF` segun marca
- `body` y `code` con `fontFeature: "tnum"` obligatorio
- componente extra `input-currency` con prefijo de simbolo y formato visual
- componente extra `status-badge` con variantes success/warning/error/pending para estados financieros
- accessibility con notas para AAA en contraste de cifras criticas

**Componentes incluidos**: `button-primary`, `button-destructive`, `input-text`, `input-currency`, `card-balance`, `transaction-list-item`, `status-badge`, `modal-confirm`.

---

## `health-calm`

### Frontmatter base

```yaml
version: 0.1.0
visual_personality:
  style_family: calm-minimal
  secondary_family: none
  density: low
  depth: flat
  typography_mode: neutral-humanist
  color_energy: low
  motion_level: low
  adjectives:
    - <a personalizar>
  anti_patterns:
    - dribbblified-overdesigned
    - brand-saturated-at-cost-of-clarity
    - aggressive-color-states
    - density-when-calm-is-required
colors:
  light:
    background: "#FAF8F5"
    surface: "#FFFFFF"
    surface-elevated: "#FFFFFF"
    on-background: "#2D2A26"
    on-surface: "#2D2A26"
    on-surface-muted: "#7D7773"
    primary: "#3F6F5B"
    on-primary: "#FFFFFF"
    accent: "#3F6F5B"
    on-accent: "#FFFFFF"
    border: "#EDE9E3"
    border-strong: "#D1CCC4"
    success: "#3F6F5B"
    on-success: "#FFFFFF"
    warning: "#A66A39"
    on-warning: "#FFFFFF"
    error: "#8B3A3A"
    on-error: "#FFFFFF"
    info: "#3A6B8B"
    on-info: "#FFFFFF"
  dark:
    background: "#1A1816"
    surface: "#262320"
    surface-elevated: "#322E2A"
    on-background: "#F0EBE4"
    on-surface: "#F0EBE4"
    on-surface-muted: "#A8A29A"
    primary: "#7FA690"
    on-primary: "#1A1816"
    accent: "#7FA690"
    on-accent: "#1A1816"
    border: "#3A352F"
    border-strong: "#52473F"
    success: "#7FA690"
    on-success: "#1A1816"
    warning: "#D9A06B"
    on-warning: "#1A1816"
    error: "#C46868"
    on-error: "#FFFFFF"
    info: "#7DA1BD"
    on-info: "#1A1816"
typography:
  display:
    fontFamily: "Geist"
    fontSize: 2.5rem
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: -0.015em
  h1:
    fontFamily: "Geist"
    fontSize: 1.875rem
    fontWeight: 600
    lineHeight: 1.25
  h2:
    fontFamily: "Geist"
    fontSize: 1.5rem
    fontWeight: 500
    lineHeight: 1.3
  body:
    fontFamily: "Geist"
    fontSize: 1.0625rem
    fontWeight: 400
    lineHeight: 1.65
  body-sm:
    fontFamily: "Geist"
    fontSize: 0.9375rem
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Geist"
    fontSize: 0.875rem
    fontWeight: 500
    lineHeight: 1.35
  caption:
    fontFamily: "Geist"
    fontSize: 0.8125rem
    fontWeight: 400
    lineHeight: 1.4
spacing:
  xs: 4px
  sm: 12px
  md: 20px
  lg: 28px
  xl: 40px
  2xl: 56px
rounded:
  sm: 12px
  md: 18px
  lg: 24px
  pill: 9999px
motion:
  level: low
  reduced_motion_policy: "respect_system; transitions ya base lentas, sin expression"
  durations:
    instant: 0
    fast: 140
    base: 260
    medium: 360
  easing:
    feedback: "cubic-bezier(0.0, 0.0, 0.2, 1)"
    transition: "cubic-bezier(0.4, 0.0, 0.2, 1)"
    enter: "cubic-bezier(0.0, 0.0, 0.2, 1)"
    exit: "cubic-bezier(0.4, 0.0, 1.0, 1)"
  style: functional
iconography:
  library: phosphor
  style: outline
  stroke_width: 1.5
  grid: 24
  sizes:
    inline-xs: 14
    inline-sm: 18
    base: 22
    prominent: 28
    hero: 56
voice:
  formality: cercano
  expertise: accesible
  warmth: humano
  playfulness: medido
  case_style: sentence
  emoji_policy: restringidos
```

**Componentes incluidos**: `button-primary`, `button-secondary`, `input-text`, `card-default`, `list-item`, `modal`.

---

## `content-editorial`

Base con tipografia serif para display/h1-h2 + sans para body:

```yaml
typography:
  display:
    fontFamily: "Source Serif Pro"
    fontSize: 3.5rem
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.02em
  h1:
    fontFamily: "Source Serif Pro"
    fontSize: 2.25rem
    fontWeight: 600
    lineHeight: 1.2
  h2:
    fontFamily: "Source Serif Pro"
    fontSize: 1.625rem
    fontWeight: 500
    lineHeight: 1.3
  body:
    fontFamily: "Inter"
    fontSize: 1.0625rem
    fontWeight: 400
    lineHeight: 1.65
```

Paleta paper-tone + acento minimo, motion `low` con duraciones medium en hero transitions, iconografia Tabler outline stroke 1.

**Componentes incluidos**: `button-primary`, `button-text`, `card-article`, `list-item-article`, `hero-banner`, `modal`.

---

## Como usa `wf-design-system` los starter kits

1. `wf-design-system` lee el brief. Si tiene `product_preset` declarado, carga el starter kit correspondiente desde este archivo.
2. El agente parte del frontmatter base del starter kit y solo modifica:
   - `adjectives` (siempre se personalizan al producto)
   - colores `accent` y `primary` si el research o PRD aportan paleta concreta
   - `iconography.library` si la familia visual del producto lo requiere
   - `Reference Apps` (siempre se rellena con research del producto)
   - `Visual Personality` rationale en markdown
   - `## Color Modes`, `## Iconography`, `## Motion & Micro-interactions` con rationale del producto
3. Los starter kits **no se modifican por feature**. Son SSoT de arranque del producto.
4. Si tras 3-4 features el equipo necesita ajustar el starter kit base (ej. anadir un componente), se canaliza via `wf-design-delta`, no se edita este archivo en una pasada.
