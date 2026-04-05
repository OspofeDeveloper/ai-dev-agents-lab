# Gestion de Servicios

> **Feature ID**: F-003
> **Spec**: service-management_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolitico origen**: N/A (features-first via discover)

## Descripcion

Gestionar los servicios asignados a la trabajadora SAD: listado, detalle con informacion del cliente y ubicacion, notas de servicio, historial de servicios completados y recepcion de nuevos servicios asignados (contratos indefinidos).

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Servicio | Esta feature define y gestiona la entidad servicio con listado, detalle, historial y asignacion |
| Owner | Cliente | La informacion del cliente se muestra y gestiona como parte del detalle de servicio |
| Referencia | Usuaria | Owner: F-001 -- auth-and-onboarding |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | service-management_spec.md | :warning: (2 gaps criticos) |
| Plan | service-management_plan.md | -- |
| Tasks | service-management_tasks.md | -- |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) -- modelo Usuaria
- **Bloquea**: F-002 (dashboard-and-announcements), F-004 (service-calls), F-005 (time-tracking), F-006 (incident-reporting), F-008 (absence-management), F-009 (availability-management), F-011 (communication), F-012 (push-notifications) -- modelo Servicio
