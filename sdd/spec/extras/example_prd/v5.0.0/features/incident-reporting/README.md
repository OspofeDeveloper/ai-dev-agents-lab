# Reporte y Seguimiento de Incidencias

> **Feature ID**: F-006
> **Spec**: incident-reporting_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolitico origen**: N/A (features-first via discover)

## Descripcion

Reportar incidencias del servicio o del usuario atendido y consultar su historial con respuestas de coordinacion.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Propio | Incidencia | Entidad principal: reporte con tipo, descripcion, adjuntos y estado |
| Propio | ComentarioIncidencia | Respuestas de coordinacion asociadas a una incidencia |
| Referencia | Servicio | Owner: F-003 — service-management |
| Referencia | Usuaria | Owner: F-001 — auth-and-onboarding |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | incident-reporting_spec.md | Done |
| Plan | incident-reporting_plan.md | -- |
| Tasks | incident-reporting_tasks.md | -- |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) para la identidad de la trabajadora; F-003 (service-management) para la vinculacion de servicios
- **Bloquea**: Ninguna
