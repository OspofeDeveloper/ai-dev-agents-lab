# Service Management (Gestión de Servicios SAD)

> **Feature ID**: F-003
> **Spec**: service-management_spec.md
> **Actor principal**: Trabajadora SAD (Felizvita)
> **Spec monolítico origen**: N/A (features-first via discover)

## Descripción

Gestión completa de los servicios asignados a trabajadoras SAD: listado con estados, detalle del servicio con plan de cuidados, notas de servicio con adjuntos, gestión de llamamientos con firma digital obligatoria y notificación de nuevo servicio asignado para contratos indefinidos.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Service | Esta feature define la entidad central Service con su CRUD completo y ciclo de vida |
| Owner | ServiceCall | Esta feature define el modelo de llamamiento y sus estados (pendiente, aceptado, rechazado, caducado, desactivado) |
| Owner | ServiceNote | Esta feature define el modelo de nota de servicio con categorías y adjuntos |
| Owner | ServiceHistory | Esta feature define el modelo de historial de servicios completados |
| Referencia | Worker | Owner: F-001 (auth-and-onboarding) — entidad de la trabajadora autenticada |
| Referencia | Signature | Owner: F-008 (profile-management) — firma digital reutilizada en aceptación/rechazo de llamamientos |
| Referencia | Incident | Owner: F-005 (incident-reporting) — incidencia generada desde detalle de servicio o nuevo servicio asignado |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | service-management_spec.md | ✓ |
| Plan | service-management_plan.md | — |
| Tasks | service-management_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) — la trabajadora debe estar autenticada; F-008 (profile-management) — la firma digital debe estar disponible para llamamientos
- **Bloquea**: F-002 (home-dashboard) — el home SAD muestra servicios activos y llamamientos pendientes de esta feature; F-004 (time-tracking) — el fichaje está vinculado a servicios; F-005 (incident-reporting) — las incidencias pueden iniciarse desde el detalle del servicio; F-010 (absence-management) — las ausencias pueden entrar en conflicto con servicios asignados; F-011 (communication) — las conversaciones pueden tener contexto de servicio
