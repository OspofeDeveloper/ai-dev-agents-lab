# Notificaciones

> **Feature ID**: F-011
> **Spec**: notificaciones_spec.md
> **Actor principal**: Trabajadora (Hogar y SAD)
> **PRD origen**: prd-hogar-sad.md

## Descripcion

Recepcion de notificaciones push con deeplinks y recordatorios automaticos del sistema para eventos importantes.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Notificacion | Esta feature gestiona la entrega y navegacion de notificaciones |
| Referencia | Usuario | Owner: F-001 — Autenticacion y Onboarding |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | notificaciones_spec.md | Done |
| Plan | notificaciones_plan.md | — |
| Tasks | notificaciones_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (Autenticacion — vinculacion de token FCM post-login)
- **Bloquea**: Ninguna
