# Autenticacion y Onboarding

> **Feature ID**: F-001
> **Spec**: authentication_spec.md
> **Actor principal**: Trabajadora (Hogar o SAD)
> **Spec monolitico origen**: prd-hogar-sad_spec.md

## Descripcion

Gestiona el registro, activacion, inicio de sesion, sesion persistente, recuperacion de acceso, cierre de sesion y onboarding de las trabajadoras en ambas apps (CUIDEO y Felizvita).

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Usuario/Sesion | Esta feature crea y gestiona las cuentas de usuario y sus sesiones |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | authentication_spec.md | ✓ |
| Plan | authentication_plan.md | — |
| Tasks | authentication_tasks.md | — |

## Dependencias

- **Requiere**: Ninguna
- **Bloquea**: F-002 (home-dashboard), F-012 (notifications) — dependen de la sesion autenticada
