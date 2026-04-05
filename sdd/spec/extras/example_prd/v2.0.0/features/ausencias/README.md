# Ausencias

> **Feature ID**: F-008
> **Spec**: ausencias_spec.md
> **Actor principal**: Trabajadora SAD
> **PRD origen**: prd-hogar-sad.md

## Descripcion

Solicitud de ausencias (vacaciones, bajas, permisos), historial y consulta de saldo de vacaciones para trabajadoras SAD.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Ausencia | Esta feature crea y gestiona las solicitudes de ausencia |
| Referencia | Usuario | Owner: F-001 — Autenticacion y Onboarding |
| Referencia | Servicio | Owner: F-003 — Gestion de Servicios (advertencia de conflicto con servicios) |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | ausencias_spec.md | Done |
| Plan | ausencias_plan.md | — |
| Tasks | ausencias_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (Autenticacion)
- **Bloquea**: Ninguna
