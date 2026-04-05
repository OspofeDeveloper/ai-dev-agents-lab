# availability-management

> **Feature ID**: F-007
> **Spec**: availability-management_spec.md
> **Actor principal**: Trabajadora (Hogar o SAD)
> **Spec monolítico origen**: N/A (features-first via discover)

## Descripción

Declaración y gestión de disponibilidad horaria semanal para ambos perfiles mediante un calendario con slots de disponibilidad/no disponibilidad y franjas rápidas predefinidas.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | AvailabilitySlot | Esta feature crea y gestiona las franjas de disponibilidad declaradas por la trabajadora |
| Owner | UnavailabilitySlot | Esta feature crea y gestiona las franjas de no disponibilidad declaradas por la trabajadora |
| Referencia | Worker | Owner: F-001 — auth-and-onboarding (entidad de la trabajadora autenticada) |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | availability-management_spec.md | ✓ |
| Plan | availability-management_plan.md | — |
| Tasks | availability-management_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) — la trabajadora debe estar autenticada para acceder al módulo de disponibilidad
- **Bloquea**: Ninguna (F-009 push-notifications referencia el trigger de recordatorio, pero no está bloqueada por esta feature)
