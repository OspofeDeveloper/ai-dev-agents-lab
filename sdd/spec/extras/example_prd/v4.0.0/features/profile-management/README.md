# Profile Management

> **Feature ID**: F-008
> **Spec**: profile-management_spec.md
> **Actor principal**: Trabajadora (Hogar o SAD)
> **Spec monolítico origen**: N/A (features-first via discover)

## Descripción

Visualización y edición del perfil personal y profesional, gestión de documentos personales y laborales, firma digital reutilizable y consulta del estado del contrato (solo SAD).

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Document | Esta feature gestiona el ciclo de vida de los documentos de la trabajadora (personales y laborales): subida, consulta, descarga y firma |
| Owner | Signature | Esta feature captura, almacena y gestiona la firma digital de la trabajadora |
| Owner | ContractInfo | Esta feature muestra la información del contrato de trabajadoras SAD (solo lectura, gestionada por backoffice) |
| Referencia | Worker | Owner: F-001 — auth-and-onboarding (creación); F-008 actualiza los datos del perfil |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | profile-management_spec.md | ✓ ⚠ INCOMPLETO ([P-001]) |
| Plan | profile-management_plan.md | — |
| Tasks | profile-management_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) — la identidad de la trabajadora (Worker) es creada en el registro; F-008 la lee y actualiza
- **Bloquea**: F-002 (home-dashboard) — el indicador de completitud del perfil y el badge de documentos pendientes son consumidos por el home; F-006 (job-offers) — el flujo de perfil incompleto al aplicar a oferta depende de los datos de este spec
