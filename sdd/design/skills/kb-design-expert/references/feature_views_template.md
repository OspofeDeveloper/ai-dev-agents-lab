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

- Componente 1
- Componente 2
- Componente 3

### Estados a generar

- Default
- Loading
- Empty
- Error
- Success

### Notas de layout

- Jerarquia
- Responsive
- Restricciones de plataforma si aplica
```
