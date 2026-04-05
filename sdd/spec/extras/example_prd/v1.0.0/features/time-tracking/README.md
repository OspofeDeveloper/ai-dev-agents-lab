# time-tracking

> **Feature ID**: F-004
> **Spec**: time-tracking_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolítico origen**: prd-hogar-sad_spec.md

## Descripción

Control horario SAD — fichaje de entrada y salida con geolocalización e historial de fichajes agrupado por servicio y día.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Fichaje | Esta feature registra y gestiona los fichajes de entrada y salida |
| Referencia | Servicio | Owner: F-003 — services-management (el fichaje se asocia a un servicio) |
| Referencia | Incidencia | Owner: F-005 — incidents (acceso a reporte de incidencia de fichaje) |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | time-tracking_spec.md | ✓ |
| Plan | time-tracking_plan.md | — |
| Tasks | time-tracking_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication), F-003 (services-management — el fichaje requiere un servicio asignado)
- **Bloquea**: F-003 (services-management referencia Fichaje para acceso desde detalle de servicio), F-005 (incidents referencia Fichaje para incidencias de fichaje)
