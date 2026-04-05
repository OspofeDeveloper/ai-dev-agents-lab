# Communication

> **Feature ID**: F-011
> **Spec**: communication_spec.md
> **Actor principal**: Trabajadora (Hogar y SAD)
> **Spec monolitico origen**: N/A (features-first via discover)

## Descripcion

Comunicarse con coordinacion mediante un sistema de chat con asuntos predefinidos, consultar el historial de conversaciones y recibir mensajes en tiempo real.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Referencia | Usuaria | Owner: F-001 — auth-and-onboarding |
| Referencia | Servicio | Owner: F-003 — service-management |
| Referencia | Oferta | Owner: F-007 — job-offers |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | communication_spec.md | ✓ |
| Plan | communication_plan.md | — |
| Tasks | communication_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) para la entidad Usuaria, F-003 (service-management) para enlazar servicios como contexto, F-007 (job-offers) para enlazar ofertas como contexto
- **Bloquea**: F-012 (push-notifications) referencia Conversacion como shared model
