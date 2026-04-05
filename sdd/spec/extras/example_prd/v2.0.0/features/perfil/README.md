# Perfil

> **Feature ID**: F-009
> **Spec**: perfil_spec.md
> **Actor principal**: Trabajadora (Hogar y SAD)
> **PRD origen**: prd-hogar-sad.md

## Descripcion

Visualizacion y edicion de perfil, foto, gestion de documentos (personales y laborales), firma digital y estado del contrato.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Perfil | Esta feature gestiona los datos de perfil de la trabajadora |
| Owner | Documento | Esta feature gestiona la visualizacion y subida de documentos |
| Owner | FirmaDigital | Esta feature captura y almacena la firma digital |
| Referencia | Usuario | Owner: F-001 — Autenticacion y Onboarding |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | perfil_spec.md | Done |
| Plan | perfil_plan.md | — |
| Tasks | perfil_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (Autenticacion)
- **Bloquea**: F-003 (Gestion de Servicios — firma digital para llamamientos), F-006 (Ofertas — datos de perfil en solicitud)
