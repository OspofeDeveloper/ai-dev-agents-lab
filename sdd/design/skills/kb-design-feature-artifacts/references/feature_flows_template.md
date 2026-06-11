# Template de `<feature>_flows.md`

```md
# Flows: <Nombre de la feature>
> Spec origen: <path>
> Feature ID: <F-XXX>

## Resumen funcional

Breve resumen de la feature y del actor principal.

## Convencion documental

Este archivo define secuencias, precondiciones y transiciones de navegacion. Los componentes, estados visuales y notas de layout viven en `<feature>_views.md` y `DESIGN.md`.

Si incluyes un mapa de navegacion consolidado al final del archivo, marcalo como derivado: `> Derivado de las tablas de transiciones por flujo. La fuente normativa son dichas tablas.` Si hay conflicto entre el mapa y una tabla individual, manda la tabla del flujo.

## Flujo 1: <Nombre>

- **Objetivo:** <que quiere conseguir el usuario>
- **Origen spec:** HU-XXX, Journey X, CA-XXX
- **Precondiciones:** <si aplica>

1. Pantalla origen
2. Accion del usuario
3. Respuesta del sistema
4. Pantalla destino

### Transiciones

| Desde | Trigger | Hacia | Notas |
|---|---|---|---|
| | | | |
```
