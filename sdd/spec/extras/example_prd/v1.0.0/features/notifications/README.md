# notifications

> **Feature ID**: F-011
> **Spec**: notifications_spec.md
> **Actor principal**: Trabajadora Hogar o SAD
> **Spec monolítico origen**: prd-hogar-sad_spec.md

## Descripción

Notificaciones push y historial de notificaciones — solicitud de permisos en onboarding, recepción en todos los estados de la app, deeplinks y recordatorios automáticos del sistema.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Notificacion | Esta feature la gestiona y muestra; home-dashboard la referencia para badges |
| Owner | TokenDispositivo | Esta feature lo registra al vincular el dispositivo con el usuario en el onboarding |
| Referencia | Servicio | Owner: F-003 — services-management (deeplinks a servicios, recordatorio de servicio próximo) |
| Referencia | Llamamiento | Owner: F-003 — services-management (deeplinks a llamamiento, notificación de nuevo llamamiento) |
| Referencia | Ausencia | Owner: F-008 — absences (notificación de cambio de estado de ausencia) |
| Referencia | Documento | Owner: F-009 — profile (aviso de caducidad de documento) |
| Referencia | Conversacion | Owner: F-010 — communication (deeplinks a conversación en notificación de mensaje nuevo) |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | notifications_spec.md | ✓ |
| Plan | notifications_plan.md | — |
| Tasks | notifications_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication — el token se vincula al usuario autenticado), F-003 (services-management), F-008 (absences), F-009 (profile), F-010 (communication)
- **Bloquea**: Ninguna
