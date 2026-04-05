# Gestion de Ausencias

> **Feature ID**: F-008
> **Spec**: absence-management_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolitico origen**: N/A (features-first via discover)

## Descripcion

Solicitar ausencias (vacaciones, baja medica, permisos) con documentacion justificativa y consultar el historial con saldos de vacaciones.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Ausencia | Esta feature crea y gestiona las solicitudes de ausencia |
| Owner | SaldoVacaciones | Esta feature gestiona los contadores de vacaciones |
| Referencia | Servicio | Owner: F-003 — service-management |
| Referencia | Usuaria | Owner: F-001 — auth-and-onboarding |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | absence-management_spec.md | Generado (con 1 gap critico pendiente) |
| Plan | absence-management_plan.md | -- |
| Tasks | absence-management_tasks.md | -- |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) para la identidad de la trabajadora; F-003 (service-management) para la deteccion de conflictos con servicios asignados
- **Bloquea**: F-012 (push-notifications) referencia Ausencia para notificaciones automaticas de ausencia proxima
