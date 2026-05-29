---
name: kb-design-iconography-expert
description: Base de conocimiento para el sistema de iconografia del producto. Define la libreria base, el stroke/fill rule, el grid de icono, los tamanos por rol y la semantica. Evita iconos inconsistentes que hacen que el producto se vea amateur.
argument-hint: "(cargada automaticamente por agentes y workflows de design)"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Design Iconography Expert

Eres la fuente de verdad para el sistema de iconografia. No redefines reglas visuales generales: especificas como el producto resuelve sus iconos.

## Regla 1: Una sola libreria base por producto

El `DESIGN.md` debe declarar una unica libreria de iconos como SSoT. Mezclar dos librerias (Lucide + Material, por ejemplo) produce inconsistencia visual inmediata.

Librerias recomendadas por familia visual:

- `productive-minimal`: Lucide o Phosphor (stroke style, neutral).
- `calm-minimal`: Phosphor (stroke ligero) o iconos custom de stroke 1.5.
- `expressive-modern`: Phosphor o Solar (duo-tone permitido), o iconos custom.
- `editorial-premium`: iconos custom o Tabler (estetica editorial fina).
- `depth-material`: Material Symbols (filled o rounded segun nivel de depth).
- `custom` (familia): iconos custom requeridos.

Plataformas nativas: SF Symbols en iOS y Material Symbols en Android pueden coexistir con la libreria base siempre que el `DESIGN.md` lo declare explicitamente.

## Regla 2: Stroke width y fill rule consistentes

Si la libreria es `stroke-based` (Lucide, Phosphor outline, Tabler):

- Stroke width unico para todo el producto: `1.5` o `2` (no mezclar).
- Stroke linecap consistente: `round` por defecto en mobile.
- Stroke linejoin consistente: `round`.

Si la libreria es `fill-based` (Phosphor fill, Solar, Material filled):

- Fill rule consistente (`nonzero` o `evenodd`).
- No mezclar fill con outline en la misma vista salvo que la distincion sea semantica (activo vs inactivo en una bottom nav).

Cualquier icono custom debe respetar el stroke/fill rule del sistema.

## Regla 3: Grid de icono unificado

Todos los iconos del producto se disenan sobre el mismo grid base:

- `24x24` por defecto (estandar Material/Lucide).
- `20x20` si la densidad del producto es `high` o si el producto es desktop-first.
- `16x16` solo para tamanos inline o badges, nunca como tamano base.

El grid se declara en el `DESIGN.md` y los iconos custom deben respetarlo.

## Regla 4: Tamanos por rol

Los iconos no se escalan libremente. Cada rol tiene su tamano:

- `inline-xs`: 12-14px — dentro de etiquetas, badges.
- `inline-sm`: 16px — dentro de botones secundarios, listas densas.
- `base`: 20-24px — accion principal, navegacion, items de lista estandar.
- `prominent`: 28-32px — bottom tabs activos, accion principal destacada.
- `hero`: 40-64px — empty states, onboarding, illustration-like.

Familias `calm-minimal` y `editorial-premium` tienden a usar tamanos `base` mas grandes (24px) y `hero` mas presentes.
Familias `productive-minimal` priorizan `inline-sm` y `base` 20px para maximizar densidad.

## Regla 5: Roles semanticos por icono

Cada icono usado debe tener rol semantico claro y consistente:

- `action`: ejecuta una accion (edit, delete, share, save).
- `navigation`: indica un destino (home, search, profile, settings).
- `status`: comunica estado (success, error, warning, info, pending).
- `decoration`: refuerza identidad sin accion (hero icon en empty state).
- `metadata`: aporta informacion contextual (calendar, clock, location).

Un mismo icono no puede tener dos roles en la misma vista. Ej: el icono `check` solo para `status: success`, no para `action: confirm` (para `confirm` usa `arrow-right` o el texto del boton).

## Regla 6: Iconos de status con color, no solo con forma

Los iconos de status (`success`, `error`, `warning`, `info`) deben:

- usar color del token semantico correspondiente (`color.success`, `color.error`, etc.)
- no depender solo del color para comunicar — el contenido o un label refuerza el significado (a11y)
- mantener la misma forma a lo largo del producto (no usar dos checks distintos para "completado" en pantallas distintas)

## Regla 7: Anti-patrones de iconografia

No introducir:

- Iconos de tres librerias distintas en la misma vista.
- Stroke 1, 1.5 y 2 mezclados.
- Iconos con perspectiva 3D en un producto flat.
- Emoji como sustituto de iconos en navegacion o acciones principales.
- Iconos que requieren label aclaratoria siempre (si el icono no se entiende solo en su rol esperado, no es el icono adecuado).
- Iconos que cambian de estilo entre pantallas (`profile` outline en una vista, filled en otra) sin razon semantica.

## Regla 8: Como se documenta iconografia en DESIGN.md

Frontmatter YAML:

```yaml
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
    success: color.success
    error: color.error
    warning: color.warning
    info: color.info
```

Seccion markdown `## Iconography`:

- libreria elegida y por que encaja con la familia visual
- politica de plataformas nativas (SF Symbols / Material Symbols opcional)
- catalogo de iconos clave por rol semantico
- cuando hacer iconos custom y cuando no
- ejemplos textuales: que icono usar en login (`log-in`), en delete (`trash-2`), en error (`alert-circle`)

## Regla 9: Custom icons solo cuando justificado

Hacer iconos custom es caro de mantener. Solo cuando:

- la libreria base no tiene un concepto especifico del dominio (industria muy nicho).
- la libreria base contradice la familia visual de forma clara.
- la marca requiere iconografia diferenciada como elemento de identidad.

Si se decide custom, declarar en `DESIGN.md` un "icon set roadmap": que iconos custom existen y cuales faltan por hacer.
