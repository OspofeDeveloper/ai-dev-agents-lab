# Checklist de anatomia y estados por componente

Cada componente declarado en `DESIGN.md > Components` o referenciado en `*_views.md` debe cubrir estos estados y partes obligatorias. Usado por `wf-design-validate` (Regla 16 de `kb-design-expert`) para detectar omisiones.

Estado declarado sin decisiones visuales concretas = estado vacio (no cuenta). Estado omitido sin `# N/A: <razon>` = `[ALTO]` en validacion.

---

## Componentes interactivos

### button-primary / button-secondary / button-tertiary / button-destructive

**Estados obligatorios:**
- `default`
- `hover` (si target_platforms incluye Web/desktop)
- `focus-visible`
- `active` (pressed)
- `disabled`
- `loading` (si la accion es async)
- `selected` (solo si aplica a toggle buttons)

**Partes obligatorias:**
- label (texto del CTA)
- icono opcional (left o right, no centrado en texto)
- estado de espera visible (spinner, label cambiada)

### link

**Estados obligatorios:**
- `default`
- `hover` (Web/desktop)
- `focus-visible`
- `active`
- `visited` (opcional, solo si el producto usa convencion visited)
- `disabled`

### tab / segmented-control

**Estados obligatorios:**
- `default` (no seleccionado)
- `selected`
- `hover` (Web/desktop)
- `focus-visible`
- `disabled`

### toggle / switch

**Estados obligatorios:**
- `off`
- `on`
- `focus-visible`
- `disabled`
- `loading` (si el cambio es async)

### checkbox / radio

**Estados obligatorios:**
- `unchecked` (default)
- `checked`
- `indeterminate` (solo checkbox, si aplica)
- `focus-visible`
- `disabled`

### chip / tag

**Estados obligatorios:**
- `default`
- `selected` (si aplica)
- `removable` (con X) si aplica
- `disabled`

**Partes:**
- label
- icono opcional
- accion remove opcional

---

## Inputs

### input-text / input-email / input-password / input-number / input-search

**Estados obligatorios:**
- `default`
- `focus`
- `filled` (con valor)
- `valid` (opcional, si validacion success aporta)
- `invalid`
- `disabled`
- `read-only`
- `loading` (si valida async)

**Partes obligatorias:**
- label encima
- field
- helper text (opcional, debajo)
- error message (sustituye helper en estado invalid)
- icono opcional (prefix o suffix)
- character counter (si aplica)
- visibility toggle (solo password)
- clear button (solo search con valor)

### textarea

**Estados obligatorios:**
- Mismos que input-text.
- `auto-grow` declarado si aplica.

### select / dropdown

**Estados obligatorios:**
- `default`
- `focus`
- `expanded` (lista abierta)
- `selected` (con valor)
- `disabled`
- `loading` (si carga options async)

### date-picker

**Estados obligatorios:**
- `default`
- `focus`
- `expanded` (calendario abierto)
- `selected` (con fecha o rango)
- `disabled`

### file-upload

**Estados obligatorios:**
- `default` (drop zone vacia)
- `hover` (Web, durante drag-over)
- `uploading` (con progreso por archivo)
- `success` (archivo subido)
- `error` (por archivo, no global)
- `disabled`

**Partes:**
- drop zone con copy claro
- lista de archivos con preview/icono + nombre + tamano + accion quitar
- progress bar por archivo

---

## Contenedores

### card

**Estados obligatorios:**
- `default`
- `hover` (si interactiva, Web/desktop)
- `focus-visible` (si interactiva)
- `selected` (si aplica)
- `loading` (skeleton si carga datos)

**Partes opcionales:**
- header (titulo + accion opcional)
- body (contenido principal)
- footer (acciones)
- media (imagen o ilustracion)

### list-item

**Estados obligatorios:**
- `default`
- `hover` (Web/desktop)
- `focus-visible`
- `pressed`
- `selected` (si aplica)
- `disabled`
- `expanded` (si tiene contenido disclosable)

**Partes:**
- leading (avatar, icono, checkbox opcional)
- content (primary + secondary text)
- trailing (icono, action, metadata)
- disclosure indicator (si navega)

### accordion / disclosure

**Estados obligatorios:**
- `collapsed`
- `expanded`
- `focus-visible` en el toggle
- `disabled`

### modal / dialog / sheet / drawer

**Estados obligatorios:**
- `entering`
- `open`
- `exiting`
- `dismissable` declarado (gesture, X, tap-outside, esc)

**Partes:**
- header (titulo + close opcional)
- body
- footer (acciones primarias y secundarias)
- backdrop / scrim

---

## Feedback y status

### toast / snackbar

**Estados obligatorios:**
- `entering`
- `visible`
- `exiting`
- `interactive` (con accion) vs `informational`
- variantes por severidad: info, success, warning, error

**Partes:**
- icono semantico
- mensaje
- accion opcional
- close opcional
- duracion declarada

### badge / pill

**Estados obligatorios:**
- `default`
- variantes por semantica: neutral, info, success, warning, error
- size variants si aplica

### progress-bar / spinner

**Estados obligatorios:**
- `determinate` (con porcentaje) vs `indeterminate`
- `default` vs `success` vs `error` (si refleja resultado)
- `loading` con label opcional

### empty-state

**Estados obligatorios:**
- variante con accion (CTA)
- variante sin accion (informativa)

**Partes:**
- icono o ilustracion (hero size)
- titulo
- cuerpo opcional
- CTA opcional

### skeleton

**Estados:**
- shimmer cycle declarado (Regla 7 de `kb-design-motion-expert`)
- formas que aproximan el contenido real (no rectangulos genericos)

---

## Navegacion

### bottom-navigation (mobile)

**Estados obligatorios:**
- por destino: `default`, `active`, `focus-visible`
- badge opcional sobre destino

**Partes:**
- 3-5 destinos
- icono + label (o solo icono si la app es muy minimal)

### top-navigation / app-bar

**Estados obligatorios:**
- `default`
- `scrolled` (con o sin elevation)
- variantes: con back, con title, con actions

**Partes:**
- leading action (back, menu)
- title
- trailing actions
- subtitle opcional

### side-navigation / drawer (web/tablet)

**Estados obligatorios:**
- por item: `default`, `hover`, `active`, `focus-visible`
- collapsed vs expanded (si soporta)

### breadcrumbs

**Estados obligatorios:**
- por segmento: `default`, `hover`, `active` (ultimo), `truncated` (si la ruta es larga)

---

## Reglas transversales

1. Si un componente declara solo `default` y no tiene marcado `# N/A` para el resto, se reporta como `[ALTO]`.
2. Cada estado declarado debe especificar al menos un cambio visual (color, opacity, border, elevation, transform). Estado sin cambios = vacio.
3. Componentes interactivos sin `focus-visible` declarado son `[CRITICO]` por a11y.
4. Componentes async sin `loading` declarado son `[ALTO]`.
5. Inputs sin `invalid` declarado son `[ALTO]`.
6. Modales sin `dismissable` declarado son `[CRITICO]` por a11y (no se sabe como cerrar con teclado).
