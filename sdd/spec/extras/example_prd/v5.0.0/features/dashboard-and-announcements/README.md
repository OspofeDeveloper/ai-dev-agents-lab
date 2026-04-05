# Dashboard and Announcements

> **Feature ID**: F-002
> **Spec**: dashboard-and-announcements_spec.md
> **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
> **Spec monolitico origen**: N/A (features-first via discover)

## Descripcion

Proporcionar la pantalla principal con accesos directos contextuales segun perfil, el tablon de anuncios/comunicados de la empresa y los mensajes del sistema.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | Anuncio | Esta feature gestiona la consulta y lectura de anuncios/comunicados |
| Owner | MensajeSistema | Esta feature gestiona la consulta, lectura y borrado de mensajes del sistema |
| Referencia | Usuaria | Owner: F-001 (auth-and-onboarding) — datos de perfil en cabecera del panel |
| Referencia | Servicio | Owner: F-003 (service-management) — informacion resumida de servicios en home SAD |
| Referencia | Llamamiento | Owner: F-004 (service-calls) — llamamiento pendiente visible en home SAD |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | dashboard-and-announcements_spec.md | Parcial (1 HU INCOMPLETO) |
| Plan | dashboard-and-announcements_plan.md | -- |
| Tasks | dashboard-and-announcements_tasks.md | -- |

## Dependencias

- **Requiere**: F-001 (auth-and-onboarding) — la trabajadora debe estar autenticada para acceder al panel
- **Bloquea**: Ninguna
