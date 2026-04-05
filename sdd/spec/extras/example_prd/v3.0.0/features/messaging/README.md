# Comunicacion

> **Feature ID**: F-010
> **Spec**: messaging_spec.md
> **Actor principal**: Trabajadora (Hogar o SAD)
> **Spec monolitico origen**: prd-hogar-sad_spec.md

## Descripcion

Permite a las trabajadoras iniciar conversaciones con coordinacion seleccionando un asunto, enviar y recibir mensajes en tiempo real, y gestionar su listado de conversaciones.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Conversacion | Esta feature crea y gestiona el modelo de conversacion |
| Owner | Mensaje | Esta feature crea y gestiona los mensajes dentro de conversaciones |
| Referencia | Usuario/Sesion | Owner: F-001 — authentication |
| Referencia | Servicio | Owner: F-003 — services |
| Referencia | Oferta | Owner: F-008 — job-offers |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | messaging_spec.md | ✓ |
| Plan | messaging_plan.md | — |
| Tasks | messaging_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication) — necesita sesion autenticada
- **Bloquea**: Ninguna
