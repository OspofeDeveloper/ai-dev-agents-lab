# home-dashboard

> **Feature ID**: F-002
> **Spec**: home-dashboard_spec.md
> **Actor principal**: Trabajadora Hogar o SAD
> **Spec monolítico origen**: prd-hogar-sad_spec.md

## Descripción

Panel principal adaptado al perfil de la trabajadora — accesos rápidos, widgets de estado, avisos, comunicados del tablón de anuncios y mensajes del sistema.

## Shared Models

| Rol | Modelo | Descripción |
|-----|--------|-------------|
| Owner | Comunicado | Esta feature muestra y gestiona los comunicados del tablón de anuncios |
| Owner | MensajeSistema | Esta feature muestra y gestiona los mensajes administrativos del sistema |
| Referencia | Trabajadora | Owner: F-001 — authentication |
| Referencia | Servicio | Owner: F-003 — services-management |
| Referencia | Llamamiento | Owner: F-003 — services-management |
| Referencia | Documento | Owner: F-009 — profile (badge pendiente firma) |
| Referencia | Notificacion | Owner: F-011 — notifications (badges y deeplinks) |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | home-dashboard_spec.md | ✓ |
| Plan | home-dashboard_plan.md | — |
| Tasks | home-dashboard_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication) — la home solo es accesible tras autenticación válida
- **Bloquea**: Ninguna
