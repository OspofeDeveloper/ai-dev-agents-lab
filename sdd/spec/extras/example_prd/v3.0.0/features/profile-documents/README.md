# Perfil y Documentos

> **Feature ID**: F-011
> **Spec**: profile-documents_spec.md
> **Actor principal**: Trabajadora (Hogar o SAD)
> **Spec monolitico origen**: prd-hogar-sad_spec.md

## Descripcion

Gestiona el perfil personal y profesional de la trabajadora, la foto de perfil, la gestion de documentos personales y laborales, la firma digital y el estado del contrato (SAD).

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Perfil | Esta feature define y gestiona el modelo de perfil de la trabajadora |
| Owner | Documento | Esta feature gestiona documentos personales y laborales |
| Owner | FirmaDigital | Esta feature crea y gestiona la firma digital de la trabajadora |
| Referencia | Usuario/Sesion | Owner: F-001 — authentication |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | profile-documents_spec.md | ✓ |
| Plan | profile-documents_plan.md | — |
| Tasks | profile-documents_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication) — necesita sesion autenticada
- **Bloquea**: F-004 (callouts) — usa firma digital; F-008 (job-offers) — verifica completitud del perfil
