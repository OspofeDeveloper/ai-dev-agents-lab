# job-offers

> **Feature ID**: F-006
> **Spec**: job-offers_spec.md
> **Actor principal**: Trabajadora Hogar
> **Spec monolítico origen**: prd-hogar-sad_spec.md

## Descripción

Navegación y solicitud de ofertas de trabajo para el perfil Hogar — listado con filtros, solicitud con confirmación, prevención de duplicados y seguimiento de candidaturas.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Oferta | Esta feature la navega y gestiona; communication la referencia para enlazar contexto |
| Owner | SolicitudOferta | Esta feature es la única que la crea y gestiona |
| Referencia | Trabajadora | Owner: F-001 — authentication |
| Referencia | Perfil | Owner: F-009 — profile (completitud al aplicar a una oferta) |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | job-offers_spec.md | ✓ |
| Plan | job-offers_plan.md | — |
| Tasks | job-offers_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication), F-009 (profile — la completitud del perfil condiciona si se puede aplicar a una oferta)
- **Bloquea**: F-010 (communication referencia Oferta para enlazar contexto en conversaciones)
