# Panel Principal y Contenidos

> **Feature ID**: F-002
> **Spec**: home-dashboard_spec.md
> **Actor principal**: Trabajadora (Hogar o SAD)
> **Spec monolitico origen**: prd-hogar-sad_spec.md

## Descripcion

Presenta el panel principal con accesos directos diferenciados por perfil (Hogar/SAD), el tablon de comunicados, los mensajes del sistema y la diferenciacion de marca entre CUIDEO y Felizvita.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Referencia | Usuario/Sesion | Owner: F-001 — authentication |
| Referencia | Servicio | Owner: F-003 — services |
| Referencia | Llamamiento | Owner: F-004 — callouts |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | home-dashboard_spec.md | ✓ |
| Plan | home-dashboard_plan.md | — |
| Tasks | home-dashboard_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (authentication) — necesita sesion autenticada para mostrar el panel
- **Bloquea**: Ninguna
