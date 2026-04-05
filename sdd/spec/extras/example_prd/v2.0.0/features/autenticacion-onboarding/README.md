# Autenticacion y Onboarding

> **Feature ID**: F-001
> **Spec**: autenticacion-onboarding_spec.md
> **Actor principal**: Trabajadora (Hogar y SAD)
> **PRD origen**: prd-hogar-sad.md

## Descripcion

Registro, inicio de sesion, onboarding, recuperacion de acceso, gestion de sesion y pantalla de acceso revocado para ambos perfiles de usuaria.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Usuario | Esta feature crea y gestiona la sesion del usuario |
| Owner | Sesion | Esta feature gestiona el ciclo de vida de la sesion |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | autenticacion-onboarding_spec.md | Done |
| Plan | autenticacion-onboarding_plan.md | — |
| Tasks | autenticacion-onboarding_tasks.md | — |

## Dependencias

- **Requiere**: Ninguna
- **Bloquea**: F-002 (Panel Principal), F-011 (Notificaciones) — requieren sesion activa
