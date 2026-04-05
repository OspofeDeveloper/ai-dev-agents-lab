# Llamamientos

> **Feature ID**: F-004
> **Spec**: callouts_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolitico origen**: prd-hogar-sad_spec.md

## Descripcion

Gestiona la recepcion, visualizacion, aceptacion y rechazo de llamamientos (turnos ofrecidos) para trabajadoras SAD, incluyendo firma digital obligatoria y gestion de caducidad.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Llamamiento | Esta feature define y gestiona el modelo de llamamiento |
| Referencia | Servicio | Owner: F-003 — services |
| Referencia | FirmaDigital | Owner: F-011 — profile-documents |
| Referencia | Usuario/Sesion | Owner: F-001 — authentication |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | callouts_spec.md | ✓ |
| Plan | callouts_plan.md | — |
| Tasks | callouts_tasks.md | — |

## Dependencias

- **Requiere**: F-003 (services) — referencia el modelo Servicio; F-011 (profile-documents) — usa firma digital
- **Bloquea**: Ninguna
