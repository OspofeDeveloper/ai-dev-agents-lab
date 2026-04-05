# Autenticacion y Onboarding

> **Feature ID**: F-001
> **Spec**: auth-and-onboarding_spec.md
> **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
> **Spec monolitico origen**: N/A (features-first via discover)

## Descripcion

Gestionar el ciclo de vida completo de autenticacion de la trabajadora: registro, inicio de sesion, recuperacion de acceso, onboarding, gestion de sesion y cierre de sesion.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Usuaria | Esta feature crea y autentica la entidad usuaria |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | auth-and-onboarding_spec.md | Pendiente (1 gap critico) |
| Plan | auth-and-onboarding_plan.md | -- |
| Tasks | auth-and-onboarding_tasks.md | -- |

## Dependencias

- **Requiere**: Ninguna
- **Bloquea**: F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-009, F-010, F-011, F-012 (todas referencian el modelo Usuaria)
