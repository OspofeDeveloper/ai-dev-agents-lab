# availability

> **Feature ID**: F-007
> **Spec**: availability_spec.md
> **Actor principal**: Trabajadora Hogar o SAD
> **Spec monolítico origen**: prd-hogar-sad_spec.md

## Descripción

Gestión de disponibilidad semanal — creación, edición y eliminación de slots de disponibilidad y no disponibilidad; los slots Activa son de solo lectura generados por planificación.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | SlotDisponibilidad | Esta feature es la única que lo crea y gestiona |
| Referencia | Servicio | Owner: F-003 — services-management (slots Activa generados desde servicios planificados) |
| Referencia | Ausencia | Owner: F-008 — absences (la solicitud de ausencia puede estar relacionada con conflictos de disponibilidad) |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | availability_spec.md | ✓ |
| Plan | availability_plan.md | — |
| Tasks | availability_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication), F-003 (services-management — los slots Activa provienen de servicios planificados)
- **Bloquea**: Ninguna
