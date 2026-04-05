# authentication

> **Feature ID**: F-001
> **Spec**: authentication_spec.md
> **Actor principal**: Trabajadora Hogar o SAD
> **Spec monolítico origen**: prd-hogar-sad_spec.md

## Descripción

Gestión de acceso a la app — splash, onboarding, login, registro, activación, recuperación de contraseña y cierre de sesión para ambos perfiles (Hogar y SAD).

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Trabajadora | Esta feature autentica e inicializa la identidad de la trabajadora |
| Owner | Sesión / Credenciales | Esta feature crea, valida y destruye la sesión de usuario |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | authentication_spec.md | ✓ |
| Plan | authentication_plan.md | — |
| Tasks | authentication_tasks.md | — |

## Dependencias

- **Requiere**: Ninguna — es la feature base del sistema
- **Bloquea**: F-002 (home-dashboard), F-003 (services-management), F-004 (time-tracking), F-005 (incidents), F-006 (job-offers), F-007 (availability), F-008 (absences), F-009 (profile), F-010 (communication), F-011 (notifications)
