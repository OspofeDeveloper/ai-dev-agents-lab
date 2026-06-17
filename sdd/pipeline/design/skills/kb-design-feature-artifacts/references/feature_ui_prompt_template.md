# Template de `<feature>_ui_prompt.md`

Prompt de ensamblaje **tool-agnostic**. La noción de `target_tool` / `target_platforms` y la regla de selección son SSoT de `kb-design-feature-artifacts` Regla 7 — este template solo las materializa. Elige la variante según `target_platforms` y rellena el encabezado común.

## Encabezado común (cualquier `target_tool`)

```md
# Prompt de ensamblaje de UI — <Nombre de la feature>

target_tool: <stitch | web-generic>
target_platforms: <mobile | desktop | web>   # SINGULAR: una superficie por archivo (ver Regla 7, multi-superficie)

Genera las vistas de la feature `<nombre-feature>` para `<target_platforms>` usando `<target_tool>`.
> Multi-superficie: si el producto cubre varias plataformas, hay un archivo `ui_prompt` por superficie (`<feature>_ui_prompt.mobile.md`, `<feature>_ui_prompt.web.md`), cada uno con su `target_tool` y su `target_platforms` singular. NO mezcles jergas en un mismo prompt (ver kb-design-feature-artifacts Regla 7).

## Fuentes de verdad

- Usa `DESIGN_BRIEF.md` si existe, para respetar guardrails de direccion visual, plataformas objetivo, severidad a11y y tradeoffs de claridad vs marca.
- Usa `DESIGN.md` como contrato visual del producto.
- Usa `<feature>_views.md` como contrato canonico de pantallas, componentes, acciones y estados.
- Usa `<feature>_flows.md` para respetar secuencias y transiciones de navegacion.

Si hay tension entre fuentes:
1. `DESIGN_BRIEF.md` manda sobre direccion visual global y guardrails de decision, si existe.
2. `<feature>_views.md` manda sobre la definicion de cada pantalla.
3. `<feature>_flows.md` manda sobre navegacion y orden de las acciones.
4. `DESIGN.md` manda sobre identidad visual y sistema de componentes.

## Contexto funcional

<Resumen corto derivado del spec>

## Contrato visual

Usa estrictamente el `DESIGN.md` del producto como fuente de identidad visual y el `DESIGN_BRIEF.md` como fuente de guardrails si existe. No redefinas tokens, componentes base ni reglas de formato dentro de este prompt. Si necesitas hacer referencia a un componente o token especifico, citalos por nombre y remite a `DESIGN.md`; no copies sus valores aqui.

## Vistas requeridas

1. <Vista 1>
2. <Vista 2>
3. <Vista 3>

## Reglas de comportamiento

- No inventes funcionalidades fuera del spec.
- Mantener consistencia visual entre todas las vistas.
- Respetar `clarity_vs_brand`, `target_platforms`, `accessibility_target` y guardrails del `DESIGN_BRIEF.md` cuando exista.
- Incluir estados de loading, empty y error donde aplique.
- Reflejar acciones destructivas con tratamiento visual diferenciado.
- Mantener formularios claros y jerarquia de acciones primaria/secundaria.
- No convertir este prompt en una segunda especificacion de pantallas: los detalles de cada vista ya viven en `<feature>_views.md`.
```

## Variante `target_tool: stitch` (mobile — formato histórico, no degradar)

Tras el encabezado común, el prompt para Stitch sigue tal cual: jerga y formato del prompt Stitch, destino de prototipado mobile. Pide vistas completas, estados importantes y consistencia visual en términos del generador Stitch. No introduce vocabulario web.

## Variante `target_tool: web-generic` (web/desktop — reutilizable por v0 / Lovable / bolt / código a mano)

Tras el encabezado común, añade un bloque de ensamblaje web reutilizable, sin jerga propietaria de Stitch:

```md
## Ensamblaje web

- Describe cada vista en términos de **HTML semántico y roles ARIA** (`<header>`/`banner`, `<nav>`/`navigation`, `<main>`, `<button>`, `<a>`, encabezados jerárquicos), no widgets propietarios.
- Declara los **breakpoints responsive** relevantes (móvil, tablet, desktop) y cómo reflowea el contenido (ver `kb-a11y-web-expert` Regla 4; no recopiar sus criterios).
- Cubre **todos los estados por vista**: loading, empty, error, focus, hover, disabled (además de los declarados en `<feature>_views.md`).
- La accesibilidad web (target 24px de puntero fino, hover/focus content, focus visible/order, landmarks/skip-links) la gobierna `kb-a11y-web-expert`: remite a ella por nombre, no copies sus reglas dentro del prompt.
- No asumas ninguna herramienta concreta: el prompt debe ser consumible por v0, Lovable, bolt o un desarrollador escribiendo el código a mano.
```
