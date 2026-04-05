# Ofertas de Trabajo

> **Feature ID**: F-007
> **Spec**: job-offers_spec.md
> **Actor principal**: Trabajadora Hogar
> **Spec monolitico origen**: N/A (features-first via discover)

## Descripcion

Navegar las ofertas de trabajo disponibles, solicitar las que interesen y gestionar el seguimiento de las solicitudes presentadas.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Oferta | Esta feature define la navegacion, filtrado y detalle de ofertas de trabajo |
| Owner | Solicitud | Esta feature define la solicitud, seguimiento y retirada de candidaturas |
| Referencia | Usuaria | Owner: F-001 — auth-and-onboarding |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | job-offers_spec.md | ✓ |
| Plan | job-offers_plan.md | -- |
| Tasks | job-offers_tasks.md | -- |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) para la entidad Usuaria; F-010 (profile-and-documents) para la validacion de completitud de perfil al solicitar oferta
- **Bloquea**: F-011 (communication) referencia Oferta como contexto enlazable al crear conversacion; F-012 (push-notifications) referencia cambios de estado de solicitud como evento de notificacion
