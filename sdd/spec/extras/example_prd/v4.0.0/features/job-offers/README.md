# Job Offers (Ofertas de Trabajo)

> **Feature ID**: F-006
> **Spec**: job-offers_spec.md
> **Actor principal**: Trabajadora Hogar (CUIDEO)
> **Spec monolítico origen**: N/A (features-first via discover)

## Descripción

Navegación, filtrado, solicitud y seguimiento de ofertas de trabajo para trabajadoras del perfil Hogar (CUIDEO).

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | JobOffer | Esta feature define el modelo JobOffer con su ciclo de vida completo (listado, detalle, filtros, ordenación) |
| Owner | JobApplication | Esta feature define el modelo JobApplication con sus estados (Pendiente, En revisión, Aceptada, Rechazada, Oferta cerrada) y la operación de retirada |
| Referencia | Worker | Owner: F-001: auth-and-onboarding — los datos del perfil de la trabajadora se adjuntan automáticamente a cada solicitud |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | job-offers_spec.md | ✓ |
| Plan | job-offers_plan.md | — |
| Tasks | job-offers_tasks.md | — |

## Dependencias

- **Requiere**: F-001: auth-and-onboarding (el perfil de la trabajadora debe existir para poder aplicar a ofertas); F-008: profile-management (los datos del perfil se adjuntan a la solicitud; la completitud del perfil es precondición para aplicar)
- **Bloquea**: F-011: communication (referencia JobOffer como modelo de contexto para conversaciones)
