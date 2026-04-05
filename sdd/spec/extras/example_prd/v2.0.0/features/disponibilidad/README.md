# Disponibilidad

> **Feature ID**: F-007
> **Spec**: disponibilidad_spec.md
> **Actor principal**: Trabajadora (Hogar y SAD)
> **PRD origen**: prd-hogar-sad.md

## Descripcion

Calendario semanal de disponibilidad con franjas rapidas, slots personalizados y visualizacion de horas asignadas.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | SlotDisponibilidad | Esta feature crea y gestiona los slots de disponibilidad |
| Referencia | Usuario | Owner: F-001 — Autenticacion y Onboarding |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | disponibilidad_spec.md | Done |
| Plan | disponibilidad_plan.md | — |
| Tasks | disponibilidad_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (Autenticacion)
- **Bloquea**: Ninguna
