# Gestion de Ausencias

> **Feature ID**: F-007
> **Spec**: absences_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolitico origen**: prd-hogar-sad_spec.md

## Descripcion

Permite a las trabajadoras SAD solicitar ausencias indicando tipo, fechas, justificacion y documentacion requerida, y consultar el historial de ausencias con saldo de vacaciones.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Ausencia | Esta feature crea y gestiona el modelo de ausencia |
| Referencia | Servicio | Owner: F-003 — services |
| Referencia | Usuario/Sesion | Owner: F-001 — authentication |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | absences_spec.md | ✓ |
| Plan | absences_plan.md | — |
| Tasks | absences_tasks.md | — |

## Dependencias

- **Requiere**: F-003 (services) — la advertencia de conflicto de fechas referencia servicios asignados
- **Bloquea**: Ninguna
