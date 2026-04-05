# communication

> **Feature ID**: F-010
> **Spec**: communication_spec.md
> **Actor principal**: Trabajadora Hogar o SAD
> **Spec monolítico origen**: prd-hogar-sad_spec.md

## Descripción

Comunicación con coordinación mediante chat — crear conversaciones con asunto predefinido, mensajes en tiempo real, historial con conversaciones cerradas y borrado.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Conversacion | Esta feature la crea y gestiona; notifications la referencia para deeplinks |
| Owner | Mensaje | Esta feature los envía y recibe en tiempo real |
| Referencia | Servicio | Owner: F-003 — services-management (enlazar contexto de servicio en conversación) |
| Referencia | Oferta | Owner: F-006 — job-offers (enlazar contexto de oferta en conversación) |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | communication_spec.md | ✓ |
| Plan | communication_plan.md | — |
| Tasks | communication_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication), F-003 (services-management — enlazar servicio como contexto), F-006 (job-offers — enlazar oferta como contexto)
- **Bloquea**: F-011 (notifications referencia Conversacion para deeplinks de mensajes nuevos)
