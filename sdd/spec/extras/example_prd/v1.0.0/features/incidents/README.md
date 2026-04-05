# incidents

> **Feature ID**: F-005
> **Spec**: incidents_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolítico origen**: prd-hogar-sad_spec.md

## Descripción

Reporte y seguimiento de incidencias SAD — formulario de reporte con adjuntos e historial con filtros y comentarios de coordinación.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Incidencia | Esta feature la crea y gestiona; services-management y time-tracking la referencian para acceso rápido |
| Referencia | Servicio | Owner: F-003 — services-management (la incidencia se asocia a un servicio) |
| Referencia | Fichaje | Owner: F-004 — time-tracking (incidencias de tipo fichaje/no asistencia) |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | incidents_spec.md | ✓ |
| Plan | incidents_plan.md | — |
| Tasks | incidents_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication), F-003 (services-management — la incidencia referencia un servicio)
- **Bloquea**: F-003 (services-management referencia Incidencia para acceso desde detalle de servicio), F-004 (time-tracking referencia Incidencia para acceso desde pantalla de fichaje)
