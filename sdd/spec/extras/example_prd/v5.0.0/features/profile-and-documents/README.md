# Profile and Documents

> **Feature ID**: F-010
> **Spec**: profile-and-documents_spec.md
> **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
> **Spec monolitico origen**: N/A (features-first via discover)

## Descripcion

Gestionar la informacion personal y profesional de la trabajadora, subir y consultar documentos (personales y laborales), capturar firma digital y visualizar el estado del contrato.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | FirmaDigital | Esta feature define la captura, almacenamiento y reutilizacion de la firma |
| Owner | PerfilTrabajadora | Esta feature gestiona la informacion personal y profesional |
| Owner | Documento | Esta feature gestiona subida, reemplazo, consulta y firma de documentos |
| Owner | Contrato | Esta feature muestra la informacion del contrato (solo SAD) |
| Referencia | Usuaria | Owner: F-001 — auth-and-onboarding |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | profile-and-documents_spec.md | ! (1 gap critico) |
| Plan | profile-and-documents_plan.md | -- |
| Tasks | profile-and-documents_tasks.md | -- |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) — referencia modelo Usuaria
- **Bloquea**: F-004 (service-calls) — referencia modelo FirmaDigital
