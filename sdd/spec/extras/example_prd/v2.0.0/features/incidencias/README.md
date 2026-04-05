# Incidencias

> **Feature ID**: F-005
> **Spec**: incidencias_spec.md
> **Actor principal**: Trabajadora SAD
> **PRD origen**: prd-hogar-sad.md

## Descripcion

Reporte de incidencias del servicio o del usuario con descripcion, adjuntos y seguimiento del estado.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Incidencia | Esta feature crea y gestiona las incidencias |
| Referencia | Servicio | Owner: F-003 — Gestion de Servicios |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | incidencias_spec.md | Done |
| Plan | incidencias_plan.md | — |
| Tasks | incidencias_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (Autenticacion), F-003 (Gestion de Servicios — servicio asociado)
- **Bloquea**: Ninguna
