# Time Tracking (Control Horario)

> **Feature ID**: F-005
> **Spec**: time-tracking_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolitico origen**: N/A (features-first via discover)

## Descripcion

Registrar la entrada y salida de la trabajadora SAD en cada servicio con captura de geolocalizacion, y consultar el historial de fichajes agrupado por servicio y por dias.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | RegistroFichaje | Esta feature crea y gestiona los registros de fichaje de entrada y salida |
| Referencia | Servicio | Owner: F-003 — service-management |
| Referencia | Usuaria | Owner: F-001 — auth-and-onboarding |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | time-tracking_spec.md | ✓ |
| Plan | time-tracking_plan.md | — |
| Tasks | time-tracking_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) para la entidad Usuaria; F-003 (service-management) para la entidad Servicio y lista de servicios activos
- **Bloquea**: Ninguna
