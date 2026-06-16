# Component Anatomy Checklist

Checklist operativo para validar que cada componente declarado en `DESIGN.md` o referenciado en `*_views.md` tiene todos sus estados aplicables con decisiones visuales concretas.

`wf-design-validate` usa esta tabla para emitir hallazgos `[ALTO]` cuando un estado obligatorio falta o está declarado sin valores.

---

## Reglas transversales

1. **Estado sin decision visual** = decoración vacía → `[ALTO]` en validate.
2. **Omisión intencional** debe documentarse con `# N/A: <razón>` en el token del componente.
3. **`hover`** solo aplica si `target_platforms` incluye `web` o `desktop`. En mobile-only, omitirlo es correcto (no requiere `# N/A`).
4. Cada estado debe definir al mínimo: `backgroundColor` o `textColor` o `border` según qué cambia visualmente.
5. Componente interactivo sin `focus-visible` (o `focus`) declarado = `[CRITICO]` por a11y.
6. Componente con acción async sin `loading` declarado = `[ALTO]`.
7. Input sin `invalid` declarado = `[ALTO]`.
8. Modal/dialog/sheet/drawer sin `dismissable` declarado (cómo se cierra: gesto, X, tap-outside, `esc`) = `[CRITICO]` por a11y.

---

## Interactivos

Aplica a: `button`, `link`, `tab`, `toggle`, `checkbox`, `radio`, `switch`, `icon-button`, `fab`.

| Estado | Obligatorio | Propiedades mínimas a declarar |
|---|---|---|
| `default` | Siempre | `backgroundColor`, `textColor`, `border` (si aplica), `typography` |
| `hover` | Solo web/desktop | `backgroundColor` o `border` diferenciado del `default` |
| `focus-visible` | Siempre | `outline` o `border` con contraste ≥ 3:1 contra el fondo adyacente |
| `active` (pressed) | Siempre | `backgroundColor` o `scale`/`opacity` diferenciado |
| `disabled` | Siempre (o `# N/A`) | `opacity` reducida (≥ 0.38) o colores semánticos desaturados |
| `loading` | Si la acción es async | Indicador visible (spinner, shimmer); el texto del botón puede ocultarse o cambiar |
| `selected` | Si admite multi-estado o estado persistente | `backgroundColor` o `border` diferenciado + `textColor` si cambia |

**Notas:**
- `toggle` y `switch` requieren además `checked` / `unchecked` (o `on` / `off`) como subestados de `default`, y `loading` si el cambio es async.
- `checkbox` y `radio` requieren `checked`, `unchecked`, e `indeterminate` (si aplica multi-select).
- `tab` activo usa `selected`; tab inactivo es `default`.
- `link` añade `visited` (opcional, solo si el producto usa la convención visited).
- Parte obligatoria de los `button`: label (texto del CTA), icono opcional (left o right, no centrado en el texto) y estado de espera visible (spinner o label cambiada) cuando hay `loading`.

---

## Inputs

Aplica a: `text-input`, `textarea`, `select`, `date-picker`, `time-picker`, `file-picker`, `search-bar`, `pin-input`.

| Estado | Obligatorio | Propiedades mínimas a declarar |
|---|---|---|
| `default` | Siempre | `backgroundColor`, `border`, `placeholderColor`, `typography` |
| `focus` | Siempre | `border` con color de acento o mayor grosor; outline accesible |
| `filled` | Siempre | `textColor` del valor introducido; puede diferir del placeholder |
| `valid` | Siempre | Indicador positivo (icon, border verde); no solo ausencia de error |
| `invalid` | Siempre | `border` o indicador semántico de error; helper text color |
| `disabled` | Siempre (o `# N/A`) | `opacity` o colores desaturados; cursor `not-allowed` en web |
| `read-only` | Si el campo puede ser read-only | Diferenciado de `disabled`: legible pero no editable |
| `loading` | Si valida async | Spinner inline o borde animado mientras valida |

**Notas:**
- `select` y `date-picker` requieren también el estado `open`/`expanded` (dropdown/popover/calendario visible).
- `text-input`/`search-bar`: partes obligatorias según el tipo — label encima, field, helper text opcional, error message (sustituye al helper en `invalid`), icono prefix/suffix opcional, character counter (si aplica), visibility toggle (solo password), clear button (solo search con valor).
- `textarea` hereda los estados de `text-input` y declara `auto-grow` si aplica.
- `file-picker`/`file-upload`: estados `default` (drop zone vacía), `hover` (Web, durante drag-over), `uploading` (progreso por archivo, no global), `success` (archivo subido) y `error` (por archivo, no global). Partes obligatorias: drop zone con copy claro, lista de archivos con preview/icono + nombre + tamaño + acción quitar, y progress bar por archivo.

---

## Contenedores con estado

Aplica a: `card`, `list-item`, `accordion`, `expandable-section`, `collapsible`.

| Estado | Obligatorio | Propiedades mínimas a declarar |
|---|---|---|
| `default` | Siempre | `backgroundColor`, `border` o `shadow` si aplica elevation |
| `hover` | Solo si el contenedor es interactivo y web/desktop | `backgroundColor` o `shadow` diferenciado |
| `selected` | Si admite selección | `border` de acento o `backgroundColor` diferenciado |
| `disabled` | Si el contenedor puede desactivarse | `opacity` reducida; contenido interno no interactivo |
| `loading` | Si carga datos internos | Shimmer sobre el área de contenido |
| `expanded` | Si es accordion/collapsible | Icono rotado, área de contenido visible, height animada |
| `collapsed` | Si es accordion/collapsible | Icono en posición cerrada, área de contenido oculta |

**Nota:** Para pantallas con datos (`empty`, `error`, `success`), los estados de vista viven en `*_views.md`, no en el componente de `DESIGN.md`.

---

## Indicadores

Aplica a: `badge`, `tag`, `chip`, `status-dot`, `avatar`.

| Estado | Obligatorio | Propiedades mínimas a declarar |
|---|---|---|
| `default` | Siempre | `backgroundColor`, `textColor`, `rounded`, tamaño |
| `selected` | Si el indicador es interactivo | `backgroundColor` diferenciado |
| `removable` | Si tiene acción de eliminar | Icono de cierre visible; estado `hover` del icono si web |
| `disabled` | Si puede desactivarse | `opacity` reducida |

**Nota:** `badge` de notificación (numérico) debe declarar también `zero` (ocultar cuando count = 0) vs `nonzero` (visible). Documentar con `# N/A` si count nunca es 0.

---

## Vistas grandes

Aplica a: `modal`, `sheet` (bottom/side), `drawer`, `page`, `dialog`.

| Estado | Obligatorio | Propiedades mínimas a declarar |
|---|---|---|
| `entering` | Siempre | Animación de entrada (slide, fade, scale) y duración |
| `default` | Siempre | `backgroundColor`, `rounded` (si aplica), `shadow` o overlay |
| `exiting` | Siempre | Animación de salida (opuesto a entering o diferente) |

**Notas:**
- Los estados de datos de la pantalla (`loading`, `empty`, `error`, `success`) pertenecen a `*_views.md`, no aquí.
- `modal`/`dialog`/`sheet`/`drawer` deben declarar `dismissable`: cómo se cierra (gesto, X, tap-outside, `esc`). Omitirlo es `[CRITICO]` por a11y (regla transversal 8). Partes habituales: header (título + close opcional), body, footer (acciones primaria/secundaria) y backdrop/scrim.

---

## Navegación

Aplica a: `bottom-nav`, `top-app-bar`, `tab-bar`, `side-nav`, `breadcrumb`.

| Estado | Obligatorio | Propiedades mínimas a declarar |
|---|---|---|
| `default` | Siempre | `backgroundColor`, `textColor`, altura, iconografía |
| `active-item` | Siempre | Color de acento en el ítem activo; diferenciado del resto |
| `scrolled` (si aplica) | Solo si cambia al hacer scroll | `shadow` o `backgroundColor` diferenciado |

**Notas:**
- `bottom-nav` (mobile): 3-5 destinos con icono + label (o solo icono si la app es muy minimal); badge opcional por destino.
- `top-app-bar`: variantes con back / con title / con actions; partes leading action (back, menu), title, trailing actions, subtitle opcional.
- `side-nav` (web/tablet): por ítem `default`, `hover`, `active`, `focus-visible`; soporta `collapsed` vs `expanded` si aplica.
- `breadcrumb`: por segmento `default`, `hover`, `active` (último) y `truncated` (si la ruta es larga).

---

## Feedback y status

Aplica a: `toast`, `snackbar`, `progress-bar`, `spinner`, `empty-state`, `skeleton`, `badge` (de estado).

| Componente | Estados / variantes obligatorias | Partes mínimas |
|---|---|---|
| `toast` / `snackbar` | `entering`, `visible`, `exiting`; variantes por severidad (info, success, warning, error); `interactive` (con acción) vs `informational` | icono semántico, mensaje, acción opcional, close opcional, duración declarada |
| `progress-bar` / `spinner` | `determinate` (con porcentaje) vs `indeterminate`; `default` vs `success` vs `error` si refleja resultado | label opcional |
| `empty-state` | variante con acción (CTA) y variante sin acción (informativa) | icono o ilustración (hero size), título, cuerpo opcional, CTA opcional |
| `skeleton` | shimmer cycle declarado (ver Regla 7 de `kb-design-motion-expert`) | formas que aproximan el contenido real, no rectángulos genéricos |
| `badge` / `pill` (estado) | `default` + variantes por semántica (neutral, info, success, warning, error); size variants si aplica | — |

**Nota:** los estados de datos a nivel de pantalla (`loading`/`empty`/`error`/`success` de una vista) viven en `*_views.md`; aquí se trata el componente reutilizable de feedback, no la vista.

---

## Formato esperado en DESIGN.md

```yaml
components:
  button-primary:
    backgroundColor: "{colors.light.primary}"
    textColor: "{colors.light.on-primary}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
    states:
      hover:
        backgroundColor: "{colors.light.primary-hover}"
      focus-visible:
        outline: "2px solid {colors.light.primary}"
        outlineOffset: "2px"
      active:
        opacity: "0.88"
      disabled:
        opacity: "0.38"
      loading:
        opacity: "0.72"
```

Todos los valores dentro de `components:` deben ser strings entrecomillados (ver Regla 2 de esta KB).
