# profile

> **Feature ID**: F-009
> **Spec**: profile_spec.md
> **Actor principal**: Trabajadora Hogar o SAD
> **Spec monolítico origen**: prd-hogar-sad_spec.md

## Descripción

Gestión del perfil completo de la trabajadora — datos personales y profesionales, foto de perfil, documentación personal y laboral con firma digital, estado del contrato y completitud.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Perfil | Esta feature lo gestiona; job-offers lo referencia para completitud al aplicar |
| Owner | Documento | Esta feature lo organiza y gestiona; home-dashboard lo referencia para badge |
| Owner | FirmaDigital | Esta feature la captura y almacena; services-management la usa en llamamientos |
| Referencia | Trabajadora | Owner: F-001 — authentication |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | profile_spec.md | ✓ |
| Plan | profile_plan.md | — |
| Tasks | profile_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication)
- **Bloquea**: F-002 (home-dashboard referencia Documento para badge), F-006 (job-offers referencia Perfil para completitud), F-011 (notifications referencia Documento para recordatorio de vencimiento)
