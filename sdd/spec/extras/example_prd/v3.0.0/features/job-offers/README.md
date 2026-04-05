# Ofertas de Trabajo

> **Feature ID**: F-008
> **Spec**: job-offers_spec.md
> **Actor principal**: Trabajadora Hogar
> **Spec monolitico origen**: prd-hogar-sad_spec.md

## Descripcion

Permite a las trabajadoras Hogar navegar ofertas de trabajo disponibles con filtros, ver detalle, solicitar ofertas y hacer seguimiento del estado de sus solicitudes.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Oferta | Esta feature define el modelo de oferta de trabajo |
| Owner | Solicitud | Esta feature crea y gestiona las solicitudes de oferta |
| Referencia | Usuario/Sesion | Owner: F-001 — authentication |
| Referencia | Perfil | Owner: F-011 — profile-documents |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | job-offers_spec.md | ✓ |
| Plan | job-offers_plan.md | — |
| Tasks | job-offers_tasks.md | — |

## Dependencias

- **Requiere**: F-011 (profile-documents) — verifica completitud del perfil antes de aplicar
- **Bloquea**: Ninguna
