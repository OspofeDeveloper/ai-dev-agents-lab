# Incident Reporting

> **Feature ID**: F-005
> **Spec**: incident-reporting_spec.md
> **Actor principal**: Trabajadora SAD (Felizvita)
> **Spec monolítico origen**: N/A (features-first via discover)

## Descripción

Reporte y seguimiento de incidencias del servicio o del usuario atendido por trabajadoras SAD, con categorización por tipo, adjuntos y seguimiento de estado con respuestas de coordinación.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Incident | Esta feature define y gestiona el ciclo de vida de las incidencias |
| Owner | IncidentAttachment | Esta feature gestiona los adjuntos (fotos y documentos) vinculados a una incidencia |
| Referencia | Service | Owner: F-003: service-management — servicio al que se vincula la incidencia |
| Referencia | Worker | Owner: F-001: auth-and-onboarding — trabajadora que reporta la incidencia |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | incident-reporting_spec.md | ✓ |
| Plan | incident-reporting_plan.md | — |
| Tasks | incident-reporting_tasks.md | — |

## Dependencias

- **Requiere**: F-001: auth-and-onboarding (autenticación de la trabajadora), F-003: service-management (referencia al servicio relacionado), F-004: time-tracking (punto de entrada desde pantalla de fichaje)
- **Bloquea**: Ninguna
