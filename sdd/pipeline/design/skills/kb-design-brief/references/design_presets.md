# Presets de producto

Cada preset declara variables minimas del brief Y un set de starters (tokens, type scale, componentes base) que `wf-design-system` usa como punto de partida en lugar de DESIGN.md en blanco. Los starters concretos viven en `references/preset_starter_kits.md` y `references/preset_components.md` de `kb-design-expert` para no inflar este archivo.

## `none`

- sin defaults cerrados
- sin starter kit
- decidir campo a campo segun spec, PRD y criterio del intake
- usar solo cuando ningun preset encaje y el equipo tenga capacidad para cerrar el sistema desde cero

## `b2b-operational`

**Brief defaults:**
- `style_family`: `productive-minimal`
- `secondary_family`: `none`
- `density`: `medium`
- `depth`: `low`
- `typography_mode`: `utilitarian`
- `color_energy`: `low`
- `motion_level`: `low`
- `clarity_vs_brand`: `clarity-first`
- `reference_apps_policy`: `preferred`
- `voice_tone`: `neutral + tecnico + neutro + serio`
- `iconography_library`: `lucide` outline stroke 1.5
- `accessibility_target`: `AA`

**Starter kit referenciado**: `preset_starter_kits.md > b2b-operational`

Incluye:
- paleta light + dark (grises neutros + acento azul-petroleo)
- type scale Inter (display, h1, h2, h3, body, body-sm, label, caption, code)
- 6 componentes base con estados completos (button-primary, button-secondary, input-text, card-default, list-item, modal)
- motion catalog `motion_level: low` (durations + easing)
- iconografia Lucide outline 1.5
- accessibility AA

## `consumer-lifestyle`

**Brief defaults:**
- `style_family`: `expressive-modern`
- `secondary_family`: `none`
- `density`: `medium`
- `depth`: `low`
- `typography_mode`: `brand-forward`
- `color_energy`: `medium`
- `motion_level`: `medium`
- `clarity_vs_brand`: `balanced`
- `reference_apps_policy`: `required`
- `voice_tone`: `cercano + accesible + calido + medido`
- `iconography_library`: `phosphor` duo-tone o fill
- `accessibility_target`: `AA`

**Starter kit**: `preset_starter_kits.md > consumer-lifestyle`

Incluye:
- paleta light + dark con acento vibrante
- type scale brand-forward (display Geist + body Inter)
- 6 componentes base con estados, micro-interacciones medium (spring sutil en CTA)
- motion catalog `motion_level: medium` con expression permitido en milestones
- iconografia Phosphor fill

## `fintech-trust`

**Brief defaults:**
- `style_family`: `productive-minimal`
- `secondary_family`: `depth-material`
- `density`: `medium`
- `depth`: `low`
- `typography_mode`: `utilitarian`
- `color_energy`: `low`
- `motion_level`: `low`
- `clarity_vs_brand`: `clarity-first`
- `reference_apps_policy`: `required`
- `voice_tone`: `neutral + tecnico/mixto + neutro + serio`
- `iconography_library`: `lucide` outline stroke 1.5
- `accessibility_target`: `AA` (recomendado `AAA` si producto regulado)
- `typography_tabular`: `true` (fontFeature `"tnum"` en body y code para legibilidad numerica)

**Starter kit**: `preset_starter_kits.md > fintech-trust`

Incluye:
- paleta light + dark sobria (neutros + acento verde o azul de confianza)
- type scale con tabular nums en body y code
- componentes financieros base (button-primary, input-currency, input-text, card-balance, transaction-list-item, modal-confirm, status-badge)
- motion catalog `motion_level: low` (sin expression)
- accessibility AA con notas para AAA en contraste critico

## `health-calm`

**Brief defaults:**
- `style_family`: `calm-minimal`
- `secondary_family`: `none`
- `density`: `low`
- `depth`: `flat`
- `typography_mode`: `neutral-humanist`
- `color_energy`: `low`
- `motion_level`: `low`
- `clarity_vs_brand`: `balanced`
- `reference_apps_policy`: `preferred`
- `voice_tone`: `cercano + accesible + humano + medido`
- `iconography_library`: `phosphor` outline ligero (stroke 1.5)
- `accessibility_target`: `AAA` recomendado por contexto sensible

**Starter kit**: `preset_starter_kits.md > health-calm`

Incluye:
- paleta light + dark calida (off-white, beige claro, verde salvia o azul sereno)
- type scale neutral-humanist con line-height generoso (1.55-1.65 en body)
- 6 componentes base con motion bajo, sin attention agresiva
- iconografia Phosphor outline 1.5
- voice: empatica, sin culpa, errores con tono cuidadoso

## `content-editorial`

**Brief defaults:**
- `style_family`: `editorial-premium`
- `secondary_family`: `none`
- `density`: `low`
- `depth`: `flat`
- `typography_mode`: `editorial`
- `color_energy`: `low` o `medium`
- `motion_level`: `low`
- `clarity_vs_brand`: `brand-forward`
- `reference_apps_policy`: `required`
- `voice_tone`: `neutral + mixto + humano + medido`
- `iconography_library`: `tabler` outline fino (stroke 1) o iconografia custom
- `accessibility_target`: `AA`

**Starter kit**: `preset_starter_kits.md > content-editorial`

Incluye:
- paleta light + dark con paper-tone y acento minimo
- type scale serif (display + h1-h2 serif, body sans)
- componentes con espaciado generoso, sin sombras
- motion catalog `motion_level: low` con duraciones medium para hero transitions

---

## Reglas de uso de presets

1. El preset acelera, no decide. Cualquier variable del brief puede sobreescribirse despues con justificacion.
2. Si el spec/PRD contradice un valor del preset, manda el producto real (Regla 6 de `kb-design-brief`).
3. Cuando `wf-design-system` corre con un preset, debe **partir del starter kit**, no generar DESIGN.md en blanco.
4. El starter kit es un punto de partida al 70%. Las decisiones especificas del producto (Reference Apps, adjetivos de personalidad, valores finales de paleta) las cierra el agente desde spec + brief + research.
5. Si el usuario quiere anadir un preset nuevo: editar este archivo + `preset_starter_kits.md` + `preset_components.md`. Documentar en `sdd/pipeline/design/README.md > Como extender el sistema`.
