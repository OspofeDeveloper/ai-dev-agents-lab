# Control Horario (Time Tracking)

> **Feature ID**: F-004
> **Spec**: time-tracking_spec.md
> **Actor principal**: Trabajadora SAD (Felizvita)
> **Spec monolítico origen**: N/A (features-first via discover)

## Descripción

Control horario de las trabajadoras SAD: fichar entrada y salida en servicios con geolocalización, estados dinámicos del botón de fichaje y visualización del historial de registros.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | TimeEntry | Esta feature crea y gestiona los registros de fichaje (entrada, salida, duración, coordenadas) |
| Owner | TimeTrackingStatus | Esta feature gestiona el estado dinámico del botón de fichaje por servicio |
| Referencia | Service | Owner: F-003 — service-management |
| Referencia | Worker | Owner: F-001 — auth-and-onboarding |
| Referencia | Incident | Owner: F-005 — incident-reporting |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | time-tracking_spec.md | ✓ |
| Plan | time-tracking_plan.md | — |
| Tasks | time-tracking_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) — la trabajadora debe estar autenticada; F-003 (service-management) — los servicios asignados deben estar disponibles para fichar
- **Bloquea**: Ninguna (F-005 incident-reporting referencia Incident que es modelo propio; F-002 home-dashboard muestra acceso directo al fichaje pero no depende funcionalmente de esta feature para operar)
