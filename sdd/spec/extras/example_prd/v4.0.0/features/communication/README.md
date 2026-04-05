# Communication

> **Feature ID**: F-011
> **Spec**: communication_spec.md
> **Actor principal**: Trabajadora (Hogar o SAD)
> **Spec monolítico origen**: N/A (features-first via discover)

## Descripción

Chat bidireccional entre la trabajadora y el equipo de Coordinación, con selección de asunto predefinido para enrutado interno, soporte de contexto de servicio/oferta, gestión del historial de conversaciones y consulta de hilos cerrados en modo solo lectura.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Conversation | Esta feature crea y gestiona el ciclo de vida de las conversaciones |
| Owner | Message | Esta feature gestiona el envío, recepción y estado de los mensajes |
| Referencia | Worker | Owner: F-001 (auth-and-onboarding) — identidad de la trabajadora |
| Referencia | Service | Owner: F-003 (service-management) — enlace de contexto opcional en conversaciones |
| Referencia | JobOffer | Owner: F-006 (job-offers) — enlace de contexto opcional en conversaciones |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | communication_spec.md | ✓ |
| Plan | communication_plan.md | — |
| Tasks | communication_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) — la trabajadora debe estar autenticada para acceder al chat; F-003 (service-management) si se usa contexto de servicio; F-006 (job-offers) si se usa contexto de oferta; F-009 (push-notifications) para recibir notificaciones de mensajes nuevos y conversaciones cerradas
- **Bloquea**: F-002 (home-dashboard) — el badge de mensajes no leídos en el home depende del modelo Conversation definido en esta feature
