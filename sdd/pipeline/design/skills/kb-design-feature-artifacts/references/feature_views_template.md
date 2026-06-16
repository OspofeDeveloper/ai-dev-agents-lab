# Template de `<feature>_views.md`

```md
# Views: <Nombre de la feature>
> Spec origen: <path>
> Feature ID: <F-XXX>

## Convencion documental

Este archivo es la fuente canonica de cada pantalla de la feature. Define componentes obligatorios, estados visuales, acciones y notas de layout. Las secuencias de usuario viven en `<feature>_flows.md`. Los tokens visuales y componentes base viven en `DESIGN.md`.

Reglas de contenido:
- Cada campo normativo contiene la decision tomada, no el razonamiento que la justifica. Si necesitas preservar el razonamiento de una eleccion, usa un bloque `> Nota:` al final de la vista.
- Las condiciones de visibilidad o comportamiento condicional de elementos UI se incluyen solo si tienen trazabilidad explicita al spec (journey, HU o CA que las exija).
- Los elementos pertenecientes a otra feature (entidades o estructuras definidas en otro spec) se marcan con `[Dependencia: F-XXX]`; no se define su estructura interna.

## Vista 1: <Nombre de la vista>

- **Tipo:** screen | dialog | sheet | tab | state
- **Objetivo:** <para que existe>
- **Origen spec:** HU-XXX, Journey X, CA-XXX
- **Actor:** <actor>
- **Accion primaria:** <CTA principal>
- **Acciones secundarias:** <si aplica>

### Componentes obligatorios

- Componente 1 — referencia a `DESIGN.md > Components > <nombre>`, con estados aplicables explicitos (default, focus, disabled, loading, etc. — ver Regla 7 de `kb-design-system-contract`).
- Componente 2
- Componente 3

### Estados de vista (Regla 4 de kb-design-feature-artifacts)

Por cada estado declarado, especificar: que se muestra, microcopy esperada y accion principal si aplica. Si un estado no aplica, marcar `# N/A: <razon>`.

- **Default**: <que componentes aparecen con contenido normal>
- **Loading**: <skeleton si dura > 1s; spinner inline si menor; que zonas se cubren>
- **Empty**: <copy orientativo + accion principal "crear primer item" o equivalente — no dejar vacio silencioso>
- **Error**: <que paso + por que si se sabe + como recuperarse; CTA "reintentar" cuando aplique>
- **Partial** (si aplica): <datos parciales o stale, como se senala al usuario>
- **Success** (si aplica): <confirmacion visual + duracion + transicion al estado siguiente>

### Microcopy minimo (Regla 5 de kb-design-feature-artifacts)

Documentar la microcopy clave de la vista: label de accion primaria, copy de empty state, copy de error tipico, label de loading si tiene texto. Las reglas de tono viven en `kb-design-voice`.

- **Accion primaria**: "<copy>"
- **Empty state**: "<copy>"
- **Error tipico**: "<copy>"

### Notas de layout

- Jerarquia
- Responsive
- Restricciones de plataforma si aplica

### Notas de accesibilidad

Solo si la vista introduce decisiones a11y especificas (focus order no trivial, labels custom, anuncios live, etc.). Las reglas generales viven en `DESIGN.md > Accessibility` y en `kb-a11y-expert`.

- **Focus order**: orden de navegacion para teclado externo / Switch Control / Switch Access. Indicar solo si difiere del orden de lectura por defecto o si la vista contiene modales con foco atrapado.
- **Labels de componentes interactivos**: label semantico para VoiceOver/TalkBack de cada control. Iconos decorativos puros se marcan `accessibilityHidden`.
- **Hints / traits**: para acciones no obvias (ej. swipe para descartar) o cuando el rol semantico necesita override.
- **Anuncios dinamicos**: estados que requieren `liveRegion` (polite | assertive). Ejemplo: error inline de formulario, badge que aparece, contador que cambia.
- **Forms**: labels asociados, mensajes de error persistentes y orden logico de focus.
- **Multimedia**: caption o transcripcion si la vista incluye video/audio con contenido informativo.
- **Touch targets atipicos**: si la vista tiene controles densos, declarar como se garantiza el tamano minimo.
```
