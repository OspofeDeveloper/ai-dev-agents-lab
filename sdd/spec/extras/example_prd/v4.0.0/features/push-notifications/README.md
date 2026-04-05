# Push Notifications

> **Feature ID**: F-009
> **Spec**: push-notifications_spec.md
> **Actor principal**: Trabajadora (Hogar o SAD)
> **Spec monolítico origen**: N/A (features-first via discover)

## Descripción

Registro del dispositivo para notificaciones push, recepción de alertas con deeplink a la sección relevante, historial de notificaciones y recordatorios automáticos del sistema enviados por el backend.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | DeviceRegistration | Esta feature crea y gestiona el registro del dispositivo para push; ciclo de vida vinculado a la sesión |
| Owner | NotificationRecord | Esta feature almacena el historial de notificaciones recibidas por la trabajadora |
| Referencia | Worker | Owner: F-001 auth-and-onboarding — entidad de la trabajadora autenticada |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | push-notifications_spec.md | ✓ |
| Plan | push-notifications_plan.md | — |
| Tasks | push-notifications_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) — el registro del dispositivo ocurre tras el primer login; la baja ocurre al cerrar sesión
- **Bloquea**: F-001 (auth-and-onboarding) referencia DeviceRegistration; todas las features que generan eventos push (F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-010, F-011) dependen de esta feature para la entrega de notificaciones
