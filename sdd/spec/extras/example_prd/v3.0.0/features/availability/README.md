# Gestion de Disponibilidad

> **Feature ID**: F-009
> **Spec**: availability_spec.md
> **Actor principal**: Trabajadora (Hogar o SAD)
> **Spec monolitico origen**: prd-hogar-sad_spec.md

## Descripcion

Permite a las trabajadoras (Hogar y SAD) gestionar su disponibilidad semanal mediante un calendario con franjas horarias predefinidas y personalizadas.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | SlotDisponibilidad | Esta feature crea y gestiona los slots de disponibilidad |
| Referencia | Usuario/Sesion | Owner: F-001 — authentication |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | availability_spec.md | ✓ |
| Plan | availability_plan.md | — |
| Tasks | availability_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication) — necesita sesion autenticada
- **Bloquea**: Ninguna
