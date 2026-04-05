# Absence Management

> **Feature ID**: F-010
> **Spec**: absence-management_spec.md
> **Actor principal**: Trabajadora SAD (Felizvita)
> **Spec monolítico origen**: N/A (features-first via discover)

## Descripción

Solicitud y seguimiento del historial de ausencias (vacaciones, bajas, permisos) con adjuntos justificativos y visualización de saldos por tipo para trabajadoras SAD.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | AbsenceRequest | Esta feature crea y gestiona el ciclo de vida completo de las solicitudes de ausencia |
| Owner | VacationBalance | Esta feature gestiona la visualización de saldos de ausencias por tipo |
| Referencia | Worker | Owner: F-001 — auth-and-onboarding |
| Referencia | Service | Owner: F-003 — service-management (para detección de conflictos con servicios asignados) |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | absence-management_spec.md | ✓ |
| Plan | absence-management_plan.md | — |
| Tasks | absence-management_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding — entidad Worker), F-003 (service-management — entidad Service para conflictos), F-009 (push-notifications — notificaciones de cambio de estado)
- **Bloquea**: Ninguna

## Estado

> ⚠ Spec con 2 gaps CRÍTICOS pendientes ([P-001], [P-002]). `/wf-prepare-plan` bloqueado hasta resolución.
