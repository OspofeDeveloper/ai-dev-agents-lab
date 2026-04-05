# Llamamientos de Servicio

> **Feature ID**: F-004
> **Spec**: service-calls_spec.md
> **Actor principal**: Trabajadora SAD (contrato fijo discontinuo)
> **Spec monolitico origen**: N/A (features-first via discover)

## Descripcion

Gestionar el ciclo completo de llamamientos: recibir ofertas de turnos, evaluarlas con toda la informacion relevante, y aceptar o rechazar con firma digital obligatoria dentro de un plazo limitado configurado desde backoffice.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Llamamiento | Esta feature define y gestiona el ciclo de vida completo del llamamiento (recibir, aceptar, rechazar, caducar) |
| Referencia | Servicio | Owner: F-003 — service-management |
| Referencia | Usuaria | Owner: F-001 — auth-and-onboarding |
| Referencia | FirmaDigital | Owner: F-010 — profile-and-documents |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | service-calls_spec.md | ✓ (2 gaps criticos pendientes) |
| Plan | service-calls_plan.md | — |
| Tasks | service-calls_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) para identidad de la usuaria, F-010 (profile-and-documents) para firma digital reutilizable
- **Bloquea**: Ninguna directamente (F-002 y F-012 referencian Llamamiento pero no dependen de esta feature para generarse)
