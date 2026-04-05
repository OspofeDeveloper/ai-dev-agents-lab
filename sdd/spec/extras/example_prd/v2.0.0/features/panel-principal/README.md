# Panel Principal

> **Feature ID**: F-002
> **Spec**: panel-principal_spec.md
> **Actor principal**: Trabajadora (Hogar y SAD)
> **PRD origen**: prd-hogar-sad.md

## Descripcion

Pantalla principal con accesos directos personalizados por perfil, tablon de anuncios/comunicados y mensajes del sistema.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Anuncio | Esta feature gestiona la visualizacion y lectura de anuncios |
| Owner | MensajeSistema | Esta feature gestiona la visualizacion y lectura de mensajes del sistema |
| Referencia | Usuario | Owner: F-001 — Autenticacion y Onboarding |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | panel-principal_spec.md | Done |
| Plan | panel-principal_plan.md | — |
| Tasks | panel-principal_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (Autenticacion — sesion activa)
- **Bloquea**: Ninguna (es punto de navegacion hacia otras features)
