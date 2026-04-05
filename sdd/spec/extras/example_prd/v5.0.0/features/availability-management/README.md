# Availability Management

> **Feature ID**: F-009
> **Spec**: availability-management_spec.md
> **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
> **Spec monolitico origen**: N/A (features-first via discover)

## Descripcion

Gestionar la disponibilidad semanal de la trabajadora mediante un calendario con franjas rapidas predefinidas y slots personalizados, visualizando horas contratadas vs trabajadas.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Referencia | Usuaria | Owner: F-001 -- auth-and-onboarding |
| Referencia | Servicio | Owner: F-003 -- service-management |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | availability-management_spec.md | Done |
| Plan | availability-management_plan.md | -- |
| Tasks | availability-management_tasks.md | -- |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) para la entidad Usuaria; F-003 (service-management) para la entidad Servicio y slots de tipo Activa
- **Bloquea**: Ninguna
