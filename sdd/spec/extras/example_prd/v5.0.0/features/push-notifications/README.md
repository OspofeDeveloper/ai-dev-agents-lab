# Push Notifications

> **Feature ID**: F-012
> **Spec**: push-notifications_spec.md
> **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
> **Spec monolitico origen**: N/A (features-first via discover)

## Descripcion

Gestionar el registro del dispositivo para notificaciones push, recibir notificaciones con navegacion a pantalla especifica y consultar el historial de notificaciones. Incluye recordatorios automaticos del sistema para acciones pendientes y proximos vencimientos.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Notificacion | Esta feature gestiona la entidad de notificacion (recepcion, historial, marcar como leida) |
| Owner | PreferenciaNotificacion | Esta feature define las preferencias de notificacion (reservado para mejora futura) |
| Referencia | Usuaria | Owner: F-001 -- auth-and-onboarding |
| Referencia | Servicio | Owner: F-003 -- service-management |
| Referencia | Llamamiento | Owner: F-004 -- service-calls |
| Referencia | Ausencia | Owner: F-008 -- absence-management |
| Referencia | Documento | Owner: F-010 -- profile-and-documents |
| Referencia | Conversacion | Owner: F-011 -- communication |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | push-notifications_spec.md | Pendiente (1 gap critico) |
| Plan | push-notifications_plan.md | -- |
| Tasks | push-notifications_tasks.md | -- |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) para la entidad Usuaria y el flujo de primer login donde se solicita el permiso
- **Bloquea**: Ninguna
