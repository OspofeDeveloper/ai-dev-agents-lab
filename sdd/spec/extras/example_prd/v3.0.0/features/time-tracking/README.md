# Control Horario

> **Feature ID**: F-005
> **Spec**: time-tracking_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolitico origen**: prd-hogar-sad_spec.md

## Descripcion

Permite a las trabajadoras SAD fichar entrada y salida de un servicio con captura de geolocalizacion y consultar el historial de seguimiento de tiempo agrupado por servicio.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | RegistroFichaje | Esta feature crea y gestiona los registros de fichaje |
| Referencia | Servicio | Owner: F-003 — services |
| Referencia | Usuario/Sesion | Owner: F-001 — authentication |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | time-tracking_spec.md | ✓ |
| Plan | time-tracking_plan.md | — |
| Tasks | time-tracking_tasks.md | — |

## Dependencias

- **Requiere**: F-003 (services) — referencia el modelo Servicio
- **Bloquea**: Ninguna
