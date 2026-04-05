# Incidencias

> **Feature ID**: F-006
> **Spec**: incidents_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolitico origen**: prd-hogar-sad_spec.md

## Descripcion

Permite a las trabajadoras SAD reportar incidencias del servicio o del cliente con descripcion y adjuntos, y consultar el historial de incidencias con estado y respuestas de coordinacion.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Incidencia | Esta feature crea y gestiona el modelo de incidencia |
| Referencia | Servicio | Owner: F-003 — services |
| Referencia | Usuario/Sesion | Owner: F-001 — authentication |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | incidents_spec.md | ✓ |
| Plan | incidents_plan.md | — |
| Tasks | incidents_tasks.md | — |

## Dependencias

- **Requiere**: F-003 (services) — referencia el modelo Servicio
- **Bloquea**: Ninguna
