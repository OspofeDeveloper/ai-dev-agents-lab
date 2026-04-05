# Comunicacion

> **Feature ID**: F-010
> **Spec**: comunicacion_spec.md
> **Actor principal**: Trabajadora (Hogar y SAD)
> **PRD origen**: prd-hogar-sad.md

## Descripcion

Chat con coordinacion organizado por asuntos predefinidos, con enrutado interno transparente y soporte de conversaciones abiertas/cerradas.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Conversacion | Esta feature crea y gestiona las conversaciones |
| Owner | Mensaje | Esta feature crea y gestiona los mensajes del chat |
| Referencia | Usuario | Owner: F-001 — Autenticacion y Onboarding |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | comunicacion_spec.md | Done |
| Plan | comunicacion_plan.md | — |
| Tasks | comunicacion_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (Autenticacion)
- **Bloquea**: Ninguna
