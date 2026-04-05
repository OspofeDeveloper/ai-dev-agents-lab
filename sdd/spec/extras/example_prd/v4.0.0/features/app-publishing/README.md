# App Publishing

> **Feature ID**: F-012
> **Spec**: app-publishing_spec.md
> **Actor principal**: Equipo de desarrollo / DevOps
> **Spec monolítico origen**: N/A (features-first via discover)

## Descripción

Configuración, compilación y publicación de las dos aplicaciones de marca (CUIDEO Hogar y Felizvita SAD) en App Store y Google Play desde el codebase compartido, incluyendo metadatos de tiendas y cumplimiento normativo RGPD.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| — | — | Esta feature no define ni referencia modelos de dominio. Es una feature de infraestructura/release. |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | app-publishing_spec.md | ✓ |
| Plan | app-publishing_plan.md | — |
| Tasks | app-publishing_tasks.md | — |

## Dependencias

- **Requiere**: Todas las features funcionales deben estar implementadas antes de la compilación de los binarios de distribución (F-001 a F-011). En particular: F-001 (auth-and-onboarding) para los flujos de autenticación incluidos en capturas de tienda.
- **Bloquea**: Ninguna (es la última fase del pipeline de entrega MVP).
