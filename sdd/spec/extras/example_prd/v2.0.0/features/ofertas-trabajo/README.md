# Ofertas de Trabajo

> **Feature ID**: F-006
> **Spec**: ofertas-trabajo_spec.md
> **Actor principal**: Trabajadora Hogar
> **PRD origen**: prd-hogar-sad.md

## Descripcion

Navegacion, filtros, solicitud de ofertas de trabajo y seguimiento de candidaturas para trabajadoras Hogar.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Oferta | Esta feature gestiona la consulta y detalle de ofertas |
| Owner | Solicitud | Esta feature crea y gestiona las solicitudes de la trabajadora |
| Referencia | Usuario | Owner: F-001 — Autenticacion y Onboarding |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | ofertas-trabajo_spec.md | Done |
| Plan | ofertas-trabajo_plan.md | — |
| Tasks | ofertas-trabajo_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (Autenticacion), F-009 (Perfil — datos del perfil incluidos en la solicitud)
- **Bloquea**: Ninguna
