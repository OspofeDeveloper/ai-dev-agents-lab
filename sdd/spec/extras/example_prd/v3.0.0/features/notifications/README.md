# Notificaciones Push

> **Feature ID**: F-012
> **Spec**: notifications_spec.md
> **Actor principal**: Trabajadora (Hogar o SAD)
> **Spec monolitico origen**: prd-hogar-sad_spec.md

## Descripcion

Gestiona el registro de dispositivos para notificaciones push, la recepcion de notificaciones automaticas del sistema, los deeplinks de navegacion desde notificaciones y el historial de notificaciones.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | RegistroDispositivo | Esta feature crea el registro de dispositivo para push |
| Owner | Notificacion | Esta feature gestiona el historial de notificaciones |
| Referencia | Usuario/Sesion | Owner: F-001 — authentication |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | notifications_spec.md | ✓ |
| Plan | notifications_plan.md | — |
| Tasks | notifications_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication) — necesita sesion autenticada para registrar dispositivo
- **Bloquea**: Ninguna
