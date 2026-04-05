# Gestion de Servicios

> **Feature ID**: F-003
> **Spec**: gestion-servicios_spec.md
> **Actor principal**: Trabajadora SAD
> **PRD origen**: prd-hogar-sad.md

## Descripcion

Listado, detalle, notas, llamamientos, historial de servicios y recepcion de nuevos servicios asignados para trabajadoras SAD.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Servicio | Esta feature gestiona la consulta y detalle de servicios |
| Owner | Llamamiento | Esta feature gestiona el ciclo de vida de los llamamientos |
| Owner | NotaServicio | Esta feature crea y gestiona las notas de servicio |
| Referencia | Usuario | Owner: F-001 — Autenticacion y Onboarding |
| Referencia | FirmaDigital | Owner: F-009 — Perfil |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | gestion-servicios_spec.md | Done |
| Plan | gestion-servicios_plan.md | — |
| Tasks | gestion-servicios_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (Autenticacion), F-009 (Perfil — firma digital para llamamientos)
- **Bloquea**: F-004 (Control Horario — fichaje desde detalle), F-005 (Incidencias — reporte desde detalle)
