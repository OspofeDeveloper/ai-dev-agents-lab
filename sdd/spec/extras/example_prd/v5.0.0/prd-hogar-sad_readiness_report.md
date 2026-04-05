# Readiness Report: Aplicaciones Moviles CUIDEO - Hogar & SAD

> **Generado por**: sdd-analyst (modo readiness)
> **Fecha**: 2026-04-05
> **Features analizadas**: 12
> **Conflict report**: Si — features/auth-and-onboarding/auth-and-onboarding_conflict_report.md
> **Fuente**: prd-hogar-sad_features.md

---

## Estado general

> **NINGUNA_LISTA**
>
> 0 de 12 features listas para `/wf-prepare-plan`. Las 12 features estan bloqueadas: 7 por gaps criticos pendientes, 2 por conflictos ALTA no resueltos sin gaps propios, y 3 esperando dependencias bloqueadas. Todos los bloqueos se originan en gaps criticos sin respuesta y 2 conflictos de severidad ALTA.

---

## Matriz de readiness

| Feature | Estado | HUs [INCOMPLETO] | Conflictos ALTA | Dependencias pendientes |
|---------|--------|:-----------------:|:---------------:|------------------------|
| F-001: auth-and-onboarding | BLOQUEADA_POR_GAPS | 1 (HU-001) | 1 (CF-001) | — |
| F-002: dashboard-and-announcements | BLOQUEADA_POR_GAPS | 1 (HU-004) | 0 | F-001, F-003, F-004 |
| F-003: service-management | BLOQUEADA_POR_GAPS | 2 (HU-002, HU-003) | 0 | F-001 |
| F-004: service-calls | BLOQUEADA_POR_GAPS | 3 (HU-003, HU-004, HU-006) | 0 | F-001, F-003, F-010 |
| F-005: time-tracking | BLOQUEADA_POR_CONFLICTOS | 0 | 1 (CF-002) | F-001, F-003 |
| F-006: incident-reporting | BLOQUEADA_POR_CONFLICTOS | 0 | 1 (CF-002) | F-001, F-003 |
| F-007: job-offers | ESPERANDO_DEPENDENCIAS | 0 | 0 | F-001, F-010 |
| F-008: absence-management | BLOQUEADA_POR_GAPS | 1 (HU-003) | 0 | F-001, F-003 |
| F-009: availability-management | ESPERANDO_DEPENDENCIAS | 0 | 0 | F-001, F-003 |
| F-010: profile-and-documents | BLOQUEADA_POR_GAPS | 2 (HU-005, HU-006) | 0 | F-001 |
| F-011: communication | ESPERANDO_DEPENDENCIAS | 0 | 0 | F-001, F-003, F-007 |
| F-012: push-notifications | BLOQUEADA_POR_GAPS | 1 (HU-003) | 1 (CF-001) | F-001, F-003, F-004, F-008, F-010, F-011 |

---

## Fases de implementacion

> Orden recomendado basado en el grafo de dependencias. Dentro de cada fase, las features pueden planificarse e implementarse en paralelo.

### Fase 1 (sin dependencias)

| Feature | Estado | Accion requerida |
|---------|--------|------------------|
| F-001: auth-and-onboarding | BLOQUEADA_POR_GAPS + CONFLICTOS | Resolver gap [P-001] (campos formulario registro Hogar) y conflicto CF-001 (duplicacion solicitud permiso push con F-012) |

### Fase 2 (depende de Fase 1)

| Feature | Depende de | Estado | Accion requerida |
|---------|------------|--------|------------------|
| F-003: service-management | F-001 | BLOQUEADA_POR_GAPS | Resolver gaps [P-008] (RGPD datos salud) y [P-010] (edicion notas) |
| F-010: profile-and-documents | F-001 | BLOQUEADA_POR_GAPS | Resolver gap [P-001] (discrepancia tipo contrato PRD vs Swagger) |

### Fase 3 (depende de Fases 1-2)

| Feature | Depende de | Estado | Accion requerida |
|---------|------------|--------|------------------|
| F-004: service-calls | F-001, F-003, F-010 | BLOQUEADA_POR_GAPS | Resolver gaps [P-001] (caducidad llamamientos) y [P-002] (copy legal) |
| F-005: time-tracking | F-001, F-003 | BLOQUEADA_POR_CONFLICTOS | Resolver conflicto CF-002 (HU duplicada reporte incidencia fichaje con F-006) |
| F-006: incident-reporting | F-001, F-003 | BLOQUEADA_POR_CONFLICTOS | Resolver conflicto CF-002 (HU duplicada reporte incidencia fichaje con F-005) |
| F-007: job-offers | F-001, F-010 | ESPERANDO_DEPENDENCIAS | Sin bloqueos propios; espera a F-001 y F-010 |
| F-008: absence-management | F-001, F-003 | BLOQUEADA_POR_GAPS | Resolver gap [P-001] (computo vacaciones dias naturales/laborables) |
| F-009: availability-management | F-001, F-003 | ESPERANDO_DEPENDENCIAS | Sin bloqueos propios; espera a F-001 y F-003 |

### Fase 4 (depende de Fases 1-3)

| Feature | Depende de | Estado | Accion requerida |
|---------|------------|--------|------------------|
| F-002: dashboard-and-announcements | F-001, F-003, F-004 | BLOQUEADA_POR_GAPS | Resolver gap [P-001] (criterios criticidad mensajes sistema) |
| F-011: communication | F-001, F-003, F-007 | ESPERANDO_DEPENDENCIAS | Sin bloqueos propios; espera a F-001, F-003 y F-007 |

### Fase 5 (depende de Fases 1-4)

| Feature | Depende de | Estado | Accion requerida |
|---------|------------|--------|------------------|
| F-012: push-notifications | F-001, F-003, F-004, F-008, F-010, F-011 | BLOQUEADA_POR_GAPS + CONFLICTOS | Resolver gap [P-001] (destinos deeplinks por tipo) y conflicto CF-001 (duplicacion solicitud permiso push con F-001) |

---

## Inventario de gaps bloqueantes

> Los siguientes gaps criticos impiden que las HUs afectadas se completen. Hasta que se resuelvan, las features no pueden pasar a `/wf-prepare-plan`.

| Gap | Severidad | HUs afectadas | Feature afectada | Accion |
|-----|-----------|---------------|-----------------|--------|
| [P-001] | CRITICO | HU-001 | F-001: auth-and-onboarding | Responder y ejecutar `/wf-spec-delta resolve features/auth-and-onboarding/auth-and-onboarding_spec.md` |
| [P-001] | CRITICO | HU-004 | F-002: dashboard-and-announcements | Responder y ejecutar `/wf-spec-delta resolve features/dashboard-and-announcements/dashboard-and-announcements_spec.md` |
| [P-008] | CRITICO | HU-002 | F-003: service-management | Responder y ejecutar `/wf-spec-delta resolve features/service-management/service-management_spec.md` |
| [P-010] | CRITICO | HU-003 | F-003: service-management | Responder y ejecutar `/wf-spec-delta resolve features/service-management/service-management_spec.md` |
| [P-001] | CRITICO | HU-006 | F-004: service-calls | Responder y ejecutar `/wf-spec-delta resolve features/service-calls/service-calls_spec.md` |
| [P-002] | CRITICO | HU-003, HU-004 | F-004: service-calls | Responder y ejecutar `/wf-spec-delta resolve features/service-calls/service-calls_spec.md` |
| [P-001] | CRITICO | HU-003 | F-008: absence-management | Responder y ejecutar `/wf-spec-delta resolve features/absence-management/absence-management_spec.md` |
| [P-001] | CRITICO | HU-005, HU-006 | F-010: profile-and-documents | Responder y ejecutar `/wf-spec-delta resolve features/profile-and-documents/profile-and-documents_spec.md` |
| [P-001] | CRITICO | HU-003 | F-012: push-notifications | Responder y ejecutar `/wf-spec-delta resolve features/push-notifications/push-notifications_spec.md` |

> **Nota**: Los IDs de gap [P-XXX] son locales a cada spec. Gaps con el mismo ID en features distintas son gaps diferentes.

---

## Conflictos ALTA no resueltos

> Los siguientes conflictos de severidad ALTA deben resolverse antes de planificar las features afectadas.

| ID | Tipo | Features afectadas | Descripcion breve | Referencia |
|----|------|-------------------|-------------------|------------|
| CF-001 | Shared model inconsistente | F-001 (auth-and-onboarding), F-012 (push-notifications) | Duplicacion de definicion del flujo de solicitud de permiso de notificaciones push post-login. Ambas features definen HUs/CAs para el mismo comportamiento. | `features/auth-and-onboarding/auth-and-onboarding_conflict_report.md` |
| CF-002 | HU duplicada | F-005 (time-tracking), F-006 (incident-reporting) | HU-004 de F-005 duplica la funcionalidad de reporte de incidencia de fichaje que es propiedad de F-006. CA-019 de F-005 ya redirige a F-006 pero mantiene una HU formal independiente. | `features/auth-and-onboarding/auth-and-onboarding_conflict_report.md` |

---

## Proximos pasos

1. **Priorizar resolver los gaps `[CRITICO]`** — afectan a 7 features (F-001, F-002, F-003, F-004, F-008, F-010, F-012). Resolviendo los gaps de F-001, F-003 y F-010 (Fase 1 y 2) se desbloquean transitivamente las features de fases posteriores que solo estan en ESPERANDO_DEPENDENCIAS.
2. **Resolver los conflictos ALTA** — CF-001 afecta a F-001 y F-012; CF-002 afecta a F-005 y F-006. Editar los specs segun las sugerencias del conflict report y re-ejecutar `/wf-spec-conflict`.
3. **Orden de resolucion recomendado** (maximo impacto):
   - Primero: gaps de F-001 (desbloquea cascada hacia las 11 features restantes)
   - Segundo: gaps de F-003 y F-010 (desbloquea Fase 3)
   - Tercero: conflictos CF-001 y CF-002 (desbloquea F-005, F-006, F-012)
   - Cuarto: gaps restantes de F-002, F-004, F-008, F-012
4. Re-ejecutar `/wf-spec-readiness features/` despues de cada correccion para verificar el progreso
