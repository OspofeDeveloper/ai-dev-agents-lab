# Template de DESIGN.md

```md
---
version: alpha
name: <Nombre del producto>
description: <Resumen breve del tono visual y contexto del producto>
visual_personality:
  adjectives:
    - <adjetivo_1>: <implicacion concreta en UI>
    - <adjetivo_2>: <implicacion concreta en UI>
  anti_adjectives:
    - <evitar_1>
    - <evitar_2>
colors:
  primary: "#000000"
  secondary: "#666666"
  accent: "#0F766E"
  surface: "#FFFFFF"
  background: "#F7F7F5"
  success: "#15803D"
  warning: "#B45309"
  danger: "#B91C1C"
typography:
  h1:
    fontFamily: <Familia principal>
    fontSize: 2.5rem
    fontWeight: 700
    lineHeight: 1.1
  h2:
    fontFamily: <Familia principal>
    fontSize: 1.75rem
    fontWeight: 600
    lineHeight: 1.2
  body:
    fontFamily: <Familia secundaria>
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: <Familia secundaria>
    fontSize: 0.875rem
    fontWeight: 500
    lineHeight: 1.3
rounded:
  sm: 8px
  md: 16px
  lg: 24px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
motion:
  speed: fast | balanced | slow
  easing: ease-out | ease-in-out | spring
  style: functional | expressive | playful
accessibility:
  wcag_target: AA
  contrast_policy: "WCAG AA: 4.5:1 texto normal, 3:1 texto grande / UI components / focus indicators"
  min_touch_target: "44pt iOS / 48dp Android"
  min_touch_spacing: "8dp"
  dynamic_type: true
  reduce_motion: respect_system
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
  input-default:
    backgroundColor: "{colors.surface}"
    borderColor: "{colors.secondary}"
    rounded: "{rounded.sm}"
  card-default:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
---

## Overview

Describe el caracter general del producto, la sensacion que debe transmitir y 2-4 principios de marca en prose o bullets cortos.

## Visual Personality

Define el caracter visual del producto con adjetivos concretos y sus implicaciones en decisiones de UI. Usa el listado del frontmatter como guia.

- **<adjetivo>**: implicacion concreta — ej. "veloz → transiciones < 200ms, sin animaciones decorativas que retrasen feedback"
- **<adjetivo>**: implicacion concreta

Anti-adjetivos — lo que este sistema visual explicitamente NO es:
- **<evitar>**: comportamiento concreto que hay que evitar y por que

## Colors

Explica como usar la paleta, donde reservar el color acento y que colores evitar.

## Typography

Explica jerarquia visual, contraste entre titulares y cuerpo, y tono editorial o utilitario.

## Layout

Define densidad, espaciado, ritmos verticales y anchuras habituales.

## Elevation & Depth

Explica como la app transmite jerarquia y profundidad visual:

- Si se usan sombras, definir niveles semanticos (ej: nivel 1 para cards, nivel 2 para dialogs, nivel 3 para sheets que cubren pantalla).
- Si se usa elevation via color de superficie (fondos con distintos valores de gris), describirlo aqui.
- Si el producto es flat-design, indicarlo explicitamente y definir como se separa contenido sin sombras.

## Shapes

Explica el caracter de bordes, radios y geometria general de la identidad.

## Components

Explica como deben sentirse formularios, listas, cards, tabs, dialogs y acciones destructivas. Incluye el tratamiento comun de estados recurrentes (loading, empty, error, success) cuando afecta a componentes.

## Accessibility

Politica de accesibilidad mobile del producto. Las reglas normativas viven en `kb-a11y-expert`; esta seccion materializa las decisiones concretas para este producto.

- **Target de conformidad**: <AA | AAA> (WCAG 2.2 mapeada a mobile).
- **Contraste**: confirma que la paleta de `colors` y los `components` cumplen 4.5:1 (texto normal) y 3:1 (texto grande / UI no decorativa) en todos los estados (default, focus, disabled, error).
- **Touch targets**: tamano minimo declarado en `accessibility.min_touch_target`. Indica como se garantiza en componentes densos (ej. zona tactil ampliada en iconos pequenos, spacing en chips).
- **Dynamic type**: estrategia para soportar font scaling hasta 200% sin perdida de contenido (line-heights relativos, reflow, truncado controlado).
- **Reduce motion**: comportamiento cuando el sistema activa la preferencia. Animaciones decorativas se deshabilitan; animaciones funcionales tienen variante reducida.
- **Focus visible**: descripcion del indicador de foco (color, grosor, offset) y como respeta el ratio 3:1.
- **Screen readers**: politica general de labels (que componentes requieren label explicito, que iconos son decorativos).
- **Imagenes**: tratamiento por defecto de imagenes informativas vs decorativas.

## Motion & Micro-interactions

Define el comportamiento animado del sistema visual:

- **Velocidad base**: duracion tipica de transiciones (ej: 150ms feedback, 300ms navegacion entre pantallas).
- **Easing**: curva de animacion y cuando aplicarla (ej: ease-out para entradas, ease-in para salidas).
- **Elementos con feedback animado**: botones, inputs, listas, dialogs — que tipo de feedback recibe cada uno.
- **Estilo general**: functional (animaciones utilitarias) | expressive (refuerzan personalidad de marca) | playful (gamifican la experiencia).
- **Lo que NO se anima**: elementos que cambian sin transicion para no retrasar la percepcion de respuesta.

## Reference Apps

Apps reales del mercado que sirven de norte visual. Para cada referencia indicar el aspecto concreto a tomar, no solo el nombre.

- **<App 1>**: <aspecto concreto — ej. "sistema de cards de saldo, tipografia numerica tabulada, densidad de informacion en lista de transacciones">
- **<App 2>**: <aspecto concreto>
- **<App 3>**: <aspecto concreto>

## Do's and Don'ts

- Haz:
  - Regla positiva 1
  - Regla positiva 2
- Evita:
  - Regla negativa 1
  - Regla negativa 2
```
