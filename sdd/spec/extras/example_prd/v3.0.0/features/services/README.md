# Gestion de Servicios

> **Feature ID**: F-003
> **Spec**: services_spec.md
> **Actor principal**: Trabajadora SAD
> **Spec monolitico origen**: prd-hogar-sad_spec.md

## Descripcion

Permite a las trabajadoras SAD consultar sus servicios asignados, ver el detalle completo de cada servicio, registrar notas de evolucion con adjuntos y consultar el historial de servicios completados.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Servicio | Esta feature define y gestiona el modelo de servicio asignado |
| Owner | NotaServicio | Esta feature crea y gestiona las notas de servicio |
| Referencia | Usuario/Sesion | Owner: F-001 — authentication |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | services_spec.md | ✓ |
| Plan | services_plan.md | — |
| Tasks | services_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication) — necesita sesion autenticada
- **Bloquea**: F-004 (callouts), F-005 (time-tracking), F-006 (incidents) — referencian el modelo Servicio
