---
name: wf-design-a11y-audit
description: Audita un DESIGN.md y opcionalmente un *_views.md frente a las reglas de kb-a11y-expert. Verifica contraste real de pares foreground/background, touch targets, focus order declarado, screen reader labels, motion handling y forms accesibles. Produce un reporte con severidad. Complementa a wf-design-validate.
when_to_use: "Activa en frases como 'valida la accesibilidad', 'audit a11y del DESIGN.md', 'comprueba contraste WCAG'."
argument-hint: "<DESIGN.md> [--views <feature_views.md>] [--brief <DESIGN_BRIEF.md>] [--target AA|AAA] [--strict]"
effort: medium
allowed-tools: [Read, Write, Bash, Agent]
context: fork
agent: design-architect
---

# design-a11y-audit — Auditoria ejecutiva de accesibilidad

Tu rol es verificar, no opinar. Las reglas de a11y son SSoT de `kb-a11y-expert`. Aqui se aplican a un DESIGN.md y a views concretos.

## Paso 1: Parsear argumentos

Extrae de `$ARGUMENTS`:
- **Path del DESIGN.md**: primer argumento posicional.
- **Path de un `*_views.md`** opcional via `--views`.
- **Path del brief** opcional via `--brief`.
- **Target WCAG** opcional via `--target` (`AA` o `AAA`). Si no se pasa, hereda del frontmatter `accessibility.wcag_target` del DESIGN.md o del brief.
- **`--strict`**: cualquier hallazgo cuenta como fallo bloqueante.

Si falta path, informa:
> "Uso: `/wf-design-a11y-audit <DESIGN.md> [--views <feature_views.md>] [--brief <DESIGN_BRIEF.md>] [--target AA|AAA] [--strict]`"

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

## Paso 3: Verificar contraste de colores

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

## Paso 4: Verificar touch targets

Para cada componente declarado:
- Si tiene `size`, `width`, `height` o `padding`, calcular el touch target efectivo.
- Verificar `>= 44pt iOS` y `>= 48dp Android` segun `accessibility.min_touch_target`.
- Spacing minimo entre targets `>= 8dp` segun `min_touch_spacing`.

Componentes pequenos (chips, icon-only buttons) tienen mayor riesgo. Marcar:
```
[ALTO] Componente <X> tiene touch target <YxZ>, menor que minimo <44pt/48dp>.
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

## Paso 8: Delegar al agente (opcional, para razonamiento avanzado)

Si los pasos 3-7 producen hallazgos que requieren razonamiento contextual (ej. evaluar si un focus order tiene sentido en una vista compleja), delegar al agente `design-architect` cargando `kb-a11y-expert`.

## Paso 9: Producir reporte

Escribe siempre el reporte en `<dir_design>/a11y_audit_<fecha>.md` y muestra el mismo contenido al usuario:

```
=== A11Y AUDIT REPORT ===
Path: <design_path>
Views: <views_path o N/A>
Target: <AA|AAA>
Fecha: <ISO>

== Contraste ==
[CRITICO] light: on-surface-muted/surface = 3.2:1 (requerido 4.5:1)
[CRITICO] dark:  on-warning/warning = 2.8:1 (requerido 4.5:1)

== Touch targets ==
[ALTO] chip-removable: 32x32 (minimo 44pt)

== Motion ==
OK

== Declaraciones ==
[MEDIO] Falta documentar politica de dynamic type en seccion Accessibility

== Vistas (si aplica) ==
[ALTO] login_views.md > Vista 'login': focus order no declarado en modal

== Total ==
2 criticos, 2 altos, 1 medio.
Estado: FAIL
```

## Paso 10: Informar al usuario

- ruta del reporte
- path del brief usado (o `N/A`)
- siguiente paso recomendado:
  - corregir tokens de color con bajo contraste antes de ejecutar `wf-design-export`.
  - si los criticos son numerosos, considerar `wf-design-delta analyze` para canalizar las correcciones.

Esta workflow no escribe el DESIGN.md ni el views. Solo audita.
