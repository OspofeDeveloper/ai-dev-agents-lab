# auth-and-onboarding

> **Feature ID**: F-001
> **Spec**: auth-and-onboarding_spec.md
> **Actor principal**: Trabajadora (Hogar o SAD)
> **Spec monolítico origen**: N/A (fast-track desde prd-hogar-sad.md via discover)

## Descripción

Gestión completa del ciclo de acceso a la app: splash, registro (Hogar), activación por email (SAD), inicio de sesión, recuperación de contraseña, sesión persistente, onboarding inicial y pantalla de acceso revocado (SAD).

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | AuthToken | Token de sesión activa de la trabajadora |
| Owner | Session | Estado de la sesión local (activa / caducada / revocada) |
| Owner | OnboardingState | Registro local del estado de completación del onboarding |
| Owner | Worker | Esta feature crea la entidad Worker al registrarse (Hogar) o al activar cuenta (SAD) |
| Referencia | DeviceRegistration | Owner: F-009 (push-notifications) — registro del dispositivo para notificaciones |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | auth-and-onboarding_spec.md | ✓ |
| Plan | auth-and-onboarding_plan.md | — |
| Tasks | auth-and-onboarding_tasks.md | — |

## Dependencias

- **Requiere**: Ninguna (es la feature base del pipeline de acceso)
- **Bloquea**: Todas las demás features (todas requieren una sesión activa de Trabajadora establecida por esta feature)
