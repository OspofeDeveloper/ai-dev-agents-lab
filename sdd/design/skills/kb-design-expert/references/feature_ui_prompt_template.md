# Template de `<feature>_ui_prompt.md`

```md
# Prompt Stitch — <Nombre de la feature>

Genera las vistas de la feature `<nombre-feature>` para una app `<mobile | web | both>`.

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
