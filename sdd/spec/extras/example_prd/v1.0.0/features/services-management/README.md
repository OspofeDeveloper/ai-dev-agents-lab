# services-management

> **Feature ID**: F-003
> **Spec**: services-management_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolítico origen**: prd-hogar-sad_spec.md

## Descripción

Gestión completa de servicios SAD — listado, detalle del servicio con plan de cuidados, gestión de notas, respuesta a llamamientos con firma digital y recepción de nuevas asignaciones.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Servicio | Esta feature lo crea y gestiona; otros módulos lo referencian para fichaje, incidencias, disponibilidad, ausencias, comunicación y notificaciones |
| Owner | Llamamiento | Esta feature lo gestiona; home-dashboard y notifications lo referencian |
| Owner | NotaServicio | Esta feature es la única que lo crea y gestiona |
| Referencia | Trabajadora | Owner: F-001 — authentication |
| Referencia | Fichaje | Owner: F-004 — time-tracking (acceso directo desde detalle de servicio) |
| Referencia | Incidencia | Owner: F-005 — incidents (acceso directo desde detalle de servicio) |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | services-management_spec.md | ✓ |
| Plan | services-management_plan.md | — |
| Tasks | services-management_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication), F-004 (time-tracking — para acceso a fichaje desde detalle), F-005 (incidents — para acceso a reporte desde detalle)
- **Bloquea**: F-002 (home-dashboard usa Servicio y Llamamiento), F-007 (availability referencia Servicio), F-008 (absences referencia Servicio), F-010 (communication referencia Servicio), F-011 (notifications referencia Servicio y Llamamiento)
