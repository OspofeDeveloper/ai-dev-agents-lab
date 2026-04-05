# F-002: home-dashboard

> Feature del proyecto: Aplicaciones Móviles CUIDEO - Hogar & SAD
> Actor principal: Trabajadora (Hogar o SAD)
> Spec monolítico origen: N/A (features-first via discover)

## Descripción

Panel principal de la app con accesos directos, anuncios, mensajes del sistema y visualización priorizada de entidades relevantes según el perfil (servicios activos, llamamientos pendientes, documentos por firmar).

## Artefactos

| Artefacto | Estado | Ruta |
|-----------|--------|------|
| Spec | ✓ | features/home-dashboard/home-dashboard_spec.md |
| Plan | — | features/home-dashboard/home-dashboard_plan.md |
| Tasks | — | features/home-dashboard/home-dashboard_tasks.md |

## Scope (RFs cubiertos)

- RF-2.1: Accesos Directos del Panel (Home)
- RF-2.2: Tablón de Anuncios / Comunicados
- RF-2.3: Mensajes del Sistema

## Modelos propios

- Announcement
- SystemMessage

## Modelos compartidos (referencias)

| Modelo | Feature Owner |
|--------|--------------|
| Worker | F-001: auth-and-onboarding |
| Service | F-003: service-management |
| ServiceCall | F-003: service-management |
| Document | F-008: profile-management |

## Estado del pipeline

- [x] Spec generado (v1.0 — 2026-04-05)
- [ ] Conflictos verificados
- [ ] Plan generado
- [ ] Tasks generadas
