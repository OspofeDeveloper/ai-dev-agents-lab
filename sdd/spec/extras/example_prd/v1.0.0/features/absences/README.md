# absences

> **Feature ID**: F-008
> **Spec**: absences_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolítico origen**: prd-hogar-sad_spec.md

## Descripción

Gestión de ausencias SAD — solicitud de vacaciones y permisos con adjuntos, historial con filtros y contadores de saldo por tipo de ausencia.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Ausencia | Esta feature la solicita y gestiona; availability y notifications la referencian |
| Owner | SolicitudAusencia | Esta feature es la única que la crea y gestiona |
| Referencia | Servicio | Owner: F-003 — services-management (conflicto de fechas con servicios asignados) |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | absences_spec.md | ✓ |
| Plan | absences_plan.md | — |
| Tasks | absences_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication), F-003 (services-management — la solicitud de ausencia advierte sobre conflictos con servicios asignados)
- **Bloquea**: F-011 (notifications referencia Ausencia para notificaciones de estado)
