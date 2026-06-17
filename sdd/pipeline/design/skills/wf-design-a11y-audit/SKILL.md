---
name: wf-design-a11y-audit
description: Audita la accesibilidad de un DESIGN.md (y opcionalmente un *_views.md) frente a kb-a11y-expert y los deltas web de kb-a11y-web-expert. Verifica contraste, targets por plataforma, focus order, screen reader labels, motion y forms; en web añade teclado, hover/focus content y reflow. Produce reporte con severidad.
when_to_use: "Activa en frases como 'valida la accesibilidad', 'audit a11y del DESIGN.md', 'comprueba contraste WCAG'. Complementa a wf-design-validate (auditoría general); no activa para regenerar el DESIGN.md (usa wf-design-delta)."
argument-hint: "<DESIGN.md> [--views <feature_views.md>] [--brief <DESIGN_BRIEF.md>] [--target AA|AAA] [--lenient]"
effort: medium
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: design-system-architect
user-invocable: true
---

# design-a11y-audit — Auditoria ejecutiva de accesibilidad

Tu rol es verificar, no opinar. Las reglas de a11y platform-neutral son SSoT de `kb-a11y-expert`; los deltas web/desktop (puntero fino, teclado primario) son SSoT de `kb-a11y-web-expert`. Aqui se aplican a un DESIGN.md y a views concretos, ramificando por las plataformas objetivo del producto.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del DESIGN.md**: primer argumento posicional.
- **Path de un `*_views.md`** opcional via `--views`.
- **Path del brief** opcional via `--brief`.
- **Target WCAG** opcional via `--target` (`AA` o `AAA`). Si no se pasa, hereda del frontmatter `accessibility.wcag_target` del DESIGN.md o del brief.
- **Flag `--lenient`** opcional: relaja el comportamiento por defecto; solo los hallazgos `[CRITICO]` bloquean. Por defecto la auditoria es **estricta** (cualquier `[CRITICO]` o `[ALTO]` cuenta como fallo). Misma semantica que `wf-design-validate`.

Si falta path, informa:
> "Uso: `/wf-design-a11y-audit <DESIGN.md> [--views <feature_views.md>] [--brief <DESIGN_BRIEF.md>] [--target AA|AAA] [--lenient]`"

## Paso 2: Verificar el DESIGN.md

1. Verifica que el archivo existe y tiene frontmatter valido.
2. Lee el archivo completo.

## Paso 2b: Resolver DESIGN_BRIEF.md

1. Si se pasa `--brief`, lee ese archivo.
2. Si no se pasa, intenta resolver `DESIGN_BRIEF.md` en el mismo directorio del DESIGN.md.
3. Si existe, usalo como fuente auxiliar para `target`, notas especiales y severidad esperada.
4. Si no existe, continua sin brief.

## Paso 2c: Determinar el target efectivo

Usa esta prioridad:
1. `--target`
2. `accessibility.wcag_target` del DESIGN.md
3. `accessibility_target` del `DESIGN_BRIEF.md` si existe
4. `AA` por defecto

## Paso 2d: Resolver las plataformas objetivo

Determina `target_platforms` (qué punteros sirve el producto) con esta prioridad:
1. `accessibility.target_platforms` del DESIGN.md
2. `target_platforms` del `DESIGN_BRIEF.md` si existe
3. Si ninguno lo declara, asume **táctil** (compatibilidad con el comportamiento histórico mobile-first) y anota un `[MEDIO]` recomendando declarar `target_platforms` explícitamente.

Clasifica:
- **Táctil** (`mobile`, `touch`, o coarse pointer): activa el criterio de target táctil del Paso 4a.
- **Web/desktop** (`web`, `desktop`, o fine pointer): activa el criterio de puntero fino del Paso 4b y los checks web del Paso 7b. Carga `kb-a11y-web-expert` en contexto.
- Un producto puede declarar **ambos**: se ejecutan los dos criterios de target (4a y 4b) y los checks web; ningún target relaja al otro (ver `kb-a11y-web-expert` Regla 1).

## Paso 3: Verificar contraste de colores

(Platform-neutral: `kb-a11y-expert` Regla 2. Idéntico para táctil y web.)

Para cada modo (`light`, `dark`, `high-contrast` si existe) y para cada par foreground/background:

- Calcular ratio de contraste (algoritmo WCAG 2.x luminancia relativa).
- Validar:
  - Texto normal: `4.5:1` para AA, `7:1` para AAA.
  - Texto grande (≥18pt o ≥14pt bold): `3:1` para AA, `4.5:1` para AAA.
  - UI components y focus indicators: `3:1` minimo.

Pares a auditar como minimo:
- `on-background` / `background`
- `on-surface` / `surface`
- `on-surface-muted` / `surface`
- `on-primary` / `primary`
- `on-accent` / `accent`
- `on-success` / `success`
- `on-error` / `error`
- `on-warning` / `warning`
- `on-info` / `info`
- `border` / `background` (UI component contrast)
- `border` / `surface`

Si un par no alcanza el ratio, marcar:
```
[CRITICO] Par <on-X> / <X> en modo <light|dark>: ratio actual <X.X:1>, requerido <Y.Y:1>.
```

## Paso 4: Verificar targets de interacción (ramifica por plataforma)

Ejecuta el sub-paso que corresponda según el Paso 2d. Si el producto declara ambos, ejecuta los dos.

### Paso 4a: Targets táctiles (plataforma táctil — `kb-a11y-expert` Regla 3)

Para cada componente declarado:
- Si tiene `size`, `width`, `height` o `padding`, calcular el touch target efectivo.
- Verificar `>= 44pt iOS` y `>= 48dp Android` segun `accessibility.min_touch_target`.
- Spacing minimo entre targets `>= 8dp` segun `min_touch_spacing`.

Componentes pequenos (chips, icon-only buttons) tienen mayor riesgo. Marcar:
```
[ALTO] Componente <X> tiene touch target <YxZ>, menor que minimo tactil <44pt/48dp>.
```

### Paso 4b: Targets de puntero fino (web/desktop — `kb-a11y-web-expert` Regla 2)

Para cada componente declarado servido a web/desktop:
- Verificar `>= 24x24 CSS px` (WCAG 2.5.8 AA) segun `accessibility.min_target_pointer`. Si el `target` efectivo es `AAA`, el mínimo es 44×44 px (2.5.5).
- Si un target queda por debajo, comprobar si invoca una excepción válida de 2.5.8 (espaciado equivalente, inline en texto, control nativo del user agent, esencial). Si la excepción está documentada en `*_views.md`, no es hallazgo.

Marcar:
```
[ALTO] Componente <X> tiene target <YxZ> px, menor que el minimo de puntero fino <24x24 px> y sin excepcion 2.5.8 documentada.
```

## Paso 5: Verificar motion handling

- Frontmatter debe declarar `motion.reduced_motion_policy`.
- La politica debe ser explicita (no `"si"` o `"respect_system"` sin mas).
- Si declara `motion_level: medium` o superior, debe describir como se reduce el motion en `prefers-reduced-motion`.

## Paso 6: Verificar declaraciones de a11y en DESIGN.md

Seccion `## Accessibility` debe documentar:
- target WCAG (declarado)
- politica de contraste
- touch targets
- dynamic type
- reduce motion
- focus visible
- screen readers
- imagenes informativas vs decorativas

Si una declaracion falta, marca `[MEDIO]`.

## Paso 7: Si `--views` se pasa, verificar la vista

Para cada vista del `*_views.md`:
- Verifica `### Notas de accesibilidad` o equivalente.
- Verifica focus order declarado si la vista tiene mas de 5 elementos interactivos o modal con focus trap.
- Verifica labels de iconos no decorativos.
- Verifica anuncios live para estados que cambian (errores inline, badges dinamicos, contadores).
- Si la vista tiene form, verifica que cada campo tiene label asociado y errores son anunciados.

Reportar omisiones con severidad:
- Labels ausentes en iconos interactivos: `[CRITICO]`.
- Focus order no declarado en modal con focus trap: `[ALTO]`.
- Live region ausente en error inline: `[ALTO]`.
- Form sin labels asociados: `[CRITICO]`.

## Paso 7b: Checks web/desktop (solo si `target_platforms` incluye web/desktop)

Aplica `kb-a11y-web-expert`. Sobre el DESIGN.md y, si se pasó `--views`, sobre cada vista:

- **Operabilidad por teclado (Regla 5)**: cada vista con controles interactivos declara que son operables por teclado y sin trampas de foco (más allá del focus trap intencional de un modal). Ausencia de declaración en vista con controles complejos → `[ALTO]`.
- **Hover/focus content (Regla 3)**: cada tooltip/popover/menú revelado por hover o focus declara dismissable + hoverable + persistent. Contenido revelado sin las tres propiedades → `[ALTO]`.
- **Reflow / resize / text spacing (Regla 4)**: el DESIGN.md declara `accessibility.reflow` y tipografía en unidades relativas; vistas con layout fijo que se rompe a 320px o altura fija que recorta texto → `[ALTO]`.
- **Focus visible / order / not-obscured (Regla 6)**: indicador de foco visible con contraste 3:1; foco no obstruido por headers sticky; orden de foco lógico al abrir/cerrar modales. Indicador de foco eliminado sin reemplazo → `[CRITICO]`; foco obstruido por header sticky → `[ALTO]`.
- **Estructura semántica (Regla 7)**: el DESIGN.md o las vistas declaran landmarks, skip-link, page title y `lang`. Ausencia de landmarks/skip-link en un producto web → `[MEDIO]`.

## Paso 8: Delegar al agente (opcional, para razonamiento avanzado)

Si los pasos 3-7b producen hallazgos que requieren razonamiento contextual (ej. evaluar si un focus order tiene sentido en una vista compleja, o si un reflow degrada operabilidad), delegar al agente `design-system-architect` cargando `kb-a11y-expert` y, cuando el target sea web/desktop, también `kb-a11y-web-expert`.

## Paso 9: Producir reporte

Escribe siempre el reporte en `<dir_design>/a11y_audit_<fecha>.md` y muestra el mismo contenido al usuario, siguiendo la estructura de `${CLAUDE_SKILL_DIR}/references/a11y_report_template.md`.

Reglas de `Estado` del reporte (mismas que `wf-design-validate`):
- Por defecto (estricto): `FAIL` si hay al menos un `[CRITICO]` o `[ALTO]`; `PASS_WITH_GAPS` si solo hay `[MEDIO]`/`[BAJO]`; `PASS` sin hallazgos.
- Con `--lenient`: `FAIL` solo si hay `[CRITICO]`; cualquier otro hallazgo → `PASS_WITH_GAPS`.

## Paso 10: Informar al usuario

- ruta del reporte
- path del brief usado (o `N/A`)
- siguiente paso recomendado:
  - corregir tokens de color con bajo contraste antes de ejecutar `wf-design-export`.
  - si los criticos son numerosos, considerar `wf-design-delta analyze` para canalizar las correcciones.

Esta workflow no escribe el DESIGN.md ni el views. Solo audita.
