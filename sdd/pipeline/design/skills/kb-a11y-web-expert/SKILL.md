---
name: kb-a11y-web-expert
description: Deltas de accesibilidad web/desktop sobre el nucleo platform-neutral de kb-a11y-expert. Cubre WCAG 2.2 completo para puntero fino y teclado primario. La cargan design-system-architect, design-feature-architect y plan-architect junto a kb-a11y-expert.
effort: low
allowed-tools: [Read]
user-invocable: false
---

# A11y Web Expert — Deltas web/desktop sobre el nucleo a11y

Eres la fuente de verdad de los **deltas web/desktop** de accesibilidad para las fases `design` y `plan` del pipeline SDD. Tu trabajo es cubrir lo que diverge del mundo tactil cuando el target es web o desktop: puntero fino, teclado como modo primario y criterios WCAG que solo existen en ese contexto.

## Reparto con `kb-a11y-expert` (lee esto primero)

`kb-a11y-expert` es la SSoT del **nucleo platform-neutral**. Esta KB **no recopia** esas reglas: las referencia. Los mismos criterios WCAG aplican a mobile y a web, asi que viven en un solo sitio.

| Dominio | SSoT | Aplica a web |
|---|---|---|
| Objetivo de conformidad (WCAG 2.2 AA por defecto) | `kb-a11y-expert` Regla 1 | sin cambios |
| Contraste de color (1.4.3, 1.4.11) | `kb-a11y-expert` Regla 2 | sin cambios |
| Motion / reduce-motion (2.3.3) | `kb-a11y-expert` Regla 5 | sin cambios; el flag es `prefers-reduced-motion` (CSS) |
| Screen reader labels/hints/traits (4.1.2, 1.1.1) | `kb-a11y-expert` Regla 7 | sin cambios en el principio; el mecanismo es ARIA (ver Regla 6 aqui) |
| Anuncios dinamicos / live regions (4.1.3) | `kb-a11y-expert` Regla 8 | sin cambios en el principio; el mecanismo es `aria-live` |
| Forms y validacion accesible (1.3.1, 3.3.1, 3.3.2, 3.3.8) | `kb-a11y-expert` Regla 9 | sin cambios en el principio; orden de tab y `<label for>` se concretan en Regla 5 aqui |
| Multimedia y contenido no textual (1.1.1, 1.2.x) | `kb-a11y-expert` Regla 10 | sin cambios |
| Handoff a plan (materializar a11y en codigo) | `kb-a11y-expert` Regla 11 | aplica; las primitivas web (roles ARIA, `tabindex`, foco) las concreta Regla 7 aqui |

> Si una decision a11y es platform-neutral, su SSoT es `kb-a11y-expert`. Esta KB solo aporta el **delta web**: lo que cambia cuando el puntero es fino y el teclado es el modo primario de operacion. Si al escribir una regla aqui repites contenido de `kb-a11y-expert`, es senal de que debe ser una referencia, no una copia.

## Fuentes normativas

- W3C — WCAG 2.2 (recomendacion completa, contexto web): https://www.w3.org/TR/WCAG22/
- W3C — Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/
- WAI-ARIA Authoring Practices Guide (APG): https://www.w3.org/WAI/ARIA/apg/

A diferencia de `kb-a11y-expert` (que mapea WCAG a mobile via `wcag2mobile-22`), esta KB usa el **WCAG 2.2 completo web**, sin el mapping mobile. Cuando una regla cite un criterio WCAG, el ID (ej. `WCAG 2.5.8`) es la referencia normativa.

## Alcance y limites

Esta KB cubre los **deltas de accesibilidad web/desktop** de UI con puntero fino y teclado. NO cubre:
- el nucleo platform-neutral (es SSoT de `kb-a11y-expert`; ver tabla de reparto arriba)
- accesibilidad mobile nativa (Switch Control, VoiceOver/TalkBack como modo primario — eso es `kb-a11y-expert`)
- microcopy, tono editorial o i18n (otros dominios)
- decisiones funcionales del spec (`kb-spec-expert`)
- arquitectura tecnica general (`kb-plan-expert`)

Si una decision a11y requiere modificar comportamiento funcional del spec (ej. anadir un atajo de teclado que el spec no contempla como flujo), no se resuelve aqui: vuelve al spec.

## Regla 1: Cuando aplica el delta web (mobile vs web en un mismo producto)

El discriminador es el **tipo de puntero**, no el dispositivo:

- **Puntero grueso (`pointer: coarse`)** — touch, lapiz: aplican los targets tactiles de `kb-a11y-expert` Regla 3 (44pt iOS / 48dp Android / 44px web-mobile).
- **Puntero fino (`pointer: fine`)** — mouse, trackpad: aplican los deltas web de esta KB (Regla 2, target 24×24px) y el teclado como modo primario de operacion.

Un producto **web responsive** puede tener **ambos** a la vez: la misma vista servida a un movil (coarse) y a un desktop (fine). En ese caso no se elige uno: se cumplen los dos criterios donde cada puntero esta presente. La consulta de medios `@media (pointer: coarse)` / `(pointer: fine)` materializa la distincion en CSS.

- En `DESIGN.md`: el campo `accessibility.target_platforms` es la SSoT de superficie a nivel sistema (`kb-design-system-contract`) y es **obligatorio declararlo cuando el producto sirve web/desktop** (no basta con que esté solo en el `DESIGN_BRIEF.md`): el `DESIGN.md` es el contrato que consumen plan y los artefactos de feature. Cuando incluye web/desktop, esta KB entra en juego y debe declararse también `accessibility.min_target_pointer`.
- En `*_views.md`: una vista que se sirve a ambos punteros declara como satisface los dos criterios de target.

## Regla 2: Target size para puntero fino (WCAG 2.5.8 AA)

Para elementos operados con puntero fino, el minimo es **24×24 CSS px** (WCAG 2.5.8 Target Size Minimum, AA) — frente a los 44/48 del mundo tactil.

- El criterio AAA (2.5.5 Target Size Enhanced) es 44×44 CSS px; usarlo solo si el `accessibility.wcag_target` es `AAA`.
- Excepciones de 2.5.8 (espaciado equivalente, target inline en texto, control nativo del agente de usuario, esencial): aplican igual que en la norma; documentar cual se invoca cuando un target queda por debajo de 24px.
- El target tactil de `kb-a11y-expert` Regla 3 **no se relaja** para los punteros gruesos del mismo producto: 24px es el minimo del puntero fino, no un nuevo minimo global.

- En `DESIGN.md`: declara `accessibility.min_target_pointer: 24px` cuando el producto sirve web/desktop, junto al `min_touch_target` tactil si tambien sirve mobile.
- En `*_views.md`: controles densos servidos a desktop (toolbars, tablas con acciones por fila) declaran como garantizan los 24px o que excepcion invocan.

## Regla 3: Hover y focus content (WCAG 1.4.13)

Solo existe en web/desktop (no hay hover en touch). Cuando pasar el puntero o enfocar un elemento revela contenido adicional (tooltips, popovers, menus en hover), ese contenido debe ser:

- **Dismissable**: descartable con `Esc` sin mover el puntero ni el foco.
- **Hoverable**: el puntero puede moverse sobre el contenido revelado sin que desaparezca.
- **Persistent**: permanece visible hasta que el usuario lo descarta, mueve el foco/puntero fuera, o deja de ser valido.

- En `*_views.md`: cada vista con contenido revelado por hover/focus declara como cumple las tres propiedades. Un tooltip que desaparece al intentar leerlo o que no se puede cerrar con `Esc` es un fallo `[ALTO]`.

## Regla 4: Reflow, resize y text spacing (WCAG 1.4.10, 1.4.4, 1.4.12)

Criterios web de adaptacion de contenido. `kb-a11y-expert` Regla 4 cubre el escalado de tipografia hasta 200% en mobile; aqui su **forma web completa**:

- **Reflow (1.4.10 AA)**: el contenido debe presentarse sin scroll en dos ejes a la vez a un ancho equivalente de **320 CSS px** (y 256px de alto). Excepcion: contenido que requiere disposicion 2D (tablas, mapas, diagramas).
- **Resize text (1.4.4 AA)**: el texto escala hasta **200%** sin perdida de contenido ni funcionalidad y sin tecnologia asistida (zoom del navegador). Usa unidades relativas (`rem`/`em`), nunca `px` fijos para tamano de fuente.
- **Text spacing (1.4.12 AA)**: el contenido no se rompe ni pierde funcionalidad cuando el usuario fuerza: line-height 1.5×, espaciado de parrafo 2×, letra 0.12×, palabra 0.16× el tamano de fuente. Evita alturas de contenedor fijas que recorten texto reflowed.

- En `DESIGN.md`: los tokens de `typography` usan unidades escalables y `lineHeight` relativos (alineado con `kb-a11y-expert` Regla 4); declara `accessibility.reflow: true` y `accessibility.text_spacing: true` cuando el target es web.
- En `*_views.md`: una vista con layout que se rompe a 320px o con altura fija que recorta texto declara la decision (reflow, scroll de un solo eje, contenedor flexible) y la traza a la regla.

## Regla 5: Operabilidad por teclado (WCAG 2.1.1, 2.1.2)

En web/desktop el teclado es el **modo primario** de operacion asistida (no Switch Control). Todo debe ser operable por teclado:

- **2.1.1 Keyboard (A)**: toda funcionalidad operable con puntero debe serlo tambien por teclado, sin requerir timing especifico de pulsaciones.
- **2.1.2 No Keyboard Trap (A)**: el foco que entra en un componente debe poder salir solo con teclado. Si el componente requiere algo mas que `Tab`/`Shift+Tab` para salir, debe avisarse al usuario como salir.
- **Orden de tab logico**: el orden de tabulacion sigue el orden de lectura/visual; no se reordena artificialmente con `tabindex` positivos.
- **Atajos de un solo caracter (2.1.4 A)**: si existen, deben poder desactivarse, remaparse o limitarse a estar activos solo con foco.

- En `*_views.md`: cada vista declara en `### Notas de accesibilidad` los controles operables por teclado, los atajos relevantes y como se evita la trampa de foco en modales (ver Regla 6).
- Materializacion en plan: ver Regla 7 (primitivas: `tabindex`, manejadores de teclado, `focus()` programatico).

## Regla 6: Focus order, focus visible y focus not obscured (WCAG 2.4.3, 2.4.7, 2.4.11)

El foco de teclado es la espina dorsal de la operabilidad web. `kb-a11y-expert` Regla 6 define focus order/visible en clave mobile (Switch Control); aqui en clave **teclado primario**:

- **2.4.3 Focus Order (A)**: el orden de foco preserva significado y operabilidad. En contenido revelado dinamicamente (modales, drawers), el foco se mueve al contenedor al abrir y vuelve al disparador al cerrar.
- **2.4.7 Focus Visible (AA)**: el indicador de foco de teclado es siempre visible y cumple el contraste 3:1 de `kb-a11y-expert` Regla 2. Nunca eliminar el outline sin reemplazarlo por un indicador equivalente.
- **2.4.11 Focus Not Obscured Minimum (AA, WCAG 2.2)**: el elemento enfocado no queda totalmente oculto por contenido superpuesto (headers sticky, banners de cookies, barras flotantes). Verificar especialmente con headers fijos.
- **Trampas de foco en modales**: un modal abierto **atrapa el foco a proposito** (foco circular dentro del dialog) — esto es correcto y distinto de la trampa prohibida por 2.1.2: el foco sale del modal al cerrarlo con `Esc` o su accion de cierre. Documentar el patron de focus trap del modal en la vista.

- En `*_views.md`: cada vista con modal, drawer o header sticky declara el orden de foco al abrir/cerrar, la visibilidad del indicador y que el foco no queda obstruido.

## Regla 7: Estructura semantica web — roles, landmarks, skip-links, title y lang

Especifico de la plataforma web; no aplica a una app nativa. Materializa el principio de `kb-a11y-expert` Regla 7 (labels/traits) con las primitivas del DOM:

- **HTML semantico primero**: usar el elemento nativo correcto (`<button>`, `<a>`, `<nav>`, `<main>`, `<h1>`–`<h6>`) antes que `<div>` + ARIA. ARIA solo cuando no hay elemento nativo equivalente. Primera regla de ARIA: no usar ARIA si un elemento nativo sirve.
- **Landmarks** (WCAG 1.3.1): regiones de pagina identificadas (`<header>`/`banner`, `<nav>`/`navigation`, `<main>`/`main`, `<aside>`/`complementary`, `<footer>`/`contentinfo`) para que el lector navegue por estructura.
- **Skip links** (WCAG 2.4.1 Bypass Blocks, A): primer foco tabulable de la pagina que salta al contenido principal, saltando navegacion repetida.
- **Page title** (WCAG 2.4.2, A): cada pagina/vista con `<title>` unico y descriptivo.
- **Lang** (WCAG 3.1.1, A): el idioma de la pagina declarado en `<html lang>`; cambios de idioma inline con `lang` en el elemento.
- **Jerarquia de encabezados** (1.3.1): un solo `<h1>` por pagina, niveles sin saltos.

- En `*_views.md`: cada vista declara sus landmarks, el destino del skip-link, el `title` de la pagina y la jerarquia de encabezados.
- En el plan (extiende `kb-a11y-expert` Regla 11): primitivas web — roles ARIA, estados/propiedades ARIA (`aria-expanded`, `aria-selected`, `aria-current`), `tabindex`, gestion de foco programatica, `aria-live` para anuncios (mecanismo web de `kb-a11y-expert` Regla 8). Estas decisiones pertenecen al plan, no al spec.

## Regla 8: Herramientas de verificacion web

Para auditar a11y web (complementa el handoff a plan de `kb-a11y-expert` Regla 11):

- **Axe DevTools** (extension de navegador / `axe-core`): detecta violaciones automatizables de WCAG en el DOM.
- **Lighthouse** (Chrome DevTools): auditoria de accesibilidad con score y hallazgos.
- **Navegacion por teclado real**: recorrer la vista solo con `Tab`/`Shift+Tab`/`Enter`/`Space`/`Esc`/flechas. Ninguna herramienta automatizada sustituye esta verificacion manual: ~30-40% de los criterios WCAG no son detectables de forma automatica.
- **Lectores de pantalla de escritorio**: NVDA / JAWS (Windows), VoiceOver (macOS) — distintos de los moviles de `kb-a11y-expert`.

Las herramientas automaticas son condicion necesaria, no suficiente: un score perfecto de Lighthouse no garantiza operabilidad por teclado ni anuncios correctos.

## Regla de oro

> Si la decision a11y es platform-neutral (contraste, motion, labels, live regions, forms, multimedia), su SSoT es `kb-a11y-expert`: referenciala, no la recopies.
> Si la decision diverge porque el puntero es fino o el teclado es el modo primario (target 24px, hover/focus content, reflow, focus visible/order/not-obscured, operabilidad por teclado, roles/landmarks/skip-links), su SSoT es esta KB.
> Si afecta a comportamiento funcional o introduce un flujo/atajo nuevo, vuelve al Spec. Si afecta a estructura visual o tokens, al `DESIGN.md`. Si afecta a primitivas, librerias o APIs web, al Plan.
