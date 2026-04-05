# Readiness Report: Aplicaciones Moviles CUIDEO - Hogar & SAD

> **Generado por**: sdd-analyst (modo readiness)
> **Fecha**: 2026-04-04
> **Features analizadas**: 11
> **Conflict report**: Si — `prd-hogar-sad_conflict_report.md`
> **Fuente**: `prd-hogar-sad_features.md`

---

## Estado general

> **NINGUNA_LISTA**
>
> 0 de 11 features listas para `/wf-prepare-plan`. 6 features tienen gaps pendientes ([INCOMPLETO]), 4 features estan involucradas en conflictos de severidad ALTA, y las 5 features restantes sin bloqueos propios estan esperando la resolucion de dependencias bloqueadas. Ademas, se detectaron 2 ciclos de dependencia circular (F-003/F-004 y F-003/F-005).

---

## Matriz de readiness

| Feature | Estado | HUs [INCOMPLETO] | Conflictos ALTA | Dependencias pendientes |
|---------|--------|:-----------------:|:---------------:|------------------------|
| F-001: authentication | BLOQUEADA_POR_GAPS, BLOQUEADA_POR_CONFLICTOS | 2 (HU-003, HU-004) | 1 (CF-002) | — |
| F-002: home-dashboard | BLOQUEADA_POR_GAPS | 1 (HU-006) | 0 | F-001 (bloqueada) |
| F-003: services-management | BLOQUEADA_POR_GAPS, BLOQUEADA_POR_CONFLICTOS | 2 (HU-010, HU-012) | 1 (CF-003) | F-004, F-005 (ciclo) |
| F-004: time-tracking | ESPERANDO_DEPENDENCIAS | 0 | 0 | F-001 (bloqueada), F-003 (bloqueada, ciclo) |
| F-005: incidents | ESPERANDO_DEPENDENCIAS | 0 | 0 | F-001 (bloqueada), F-003 (bloqueada, ciclo) |
| F-006: job-offers | ESPERANDO_DEPENDENCIAS | 0 | 0 | F-001 (bloqueada), F-009 (bloqueada) |
| F-007: availability | ESPERANDO_DEPENDENCIAS | 0 | 0 | F-001 (bloqueada), F-003 (bloqueada) |
| F-008: absences | BLOQUEADA_POR_GAPS | 1 (HU-019) | 0 | F-001 (bloqueada), F-003 (bloqueada) |
| F-009: profile | BLOQUEADA_POR_GAPS, BLOQUEADA_POR_CONFLICTOS | 2 (HU-022, HU-025) | 1 (CF-003) | F-001 (bloqueada) |
| F-010: communication | ESPERANDO_DEPENDENCIAS | 0 | 0 | F-001 (bloqueada), F-003 (bloqueada), F-006 (bloqueada) |
| F-011: notifications | BLOQUEADA_POR_CONFLICTOS | 0 | 1 (CF-002) | F-001 (bloqueada), F-003 (bloqueada), F-008 (bloqueada), F-009 (bloqueada), F-010 (bloqueada) |

---

## Fases de implementacion

> Orden recomendado basado en el grafo de dependencias. Dentro de cada fase, las features pueden planificarse e implementarse en paralelo. Las features del ciclo de dependencia circular (F-003, F-004, F-005) se agrupan en una fase conjunta.

### Fase 1 (sin dependencias)

| Feature | Estado | Accion requerida |
|---------|--------|------------------|
| F-001: authentication | BLOQUEADA_POR_GAPS, BLOQUEADA_POR_CONFLICTOS | Resolver gaps [P-001] y [P-007]; resolver conflicto CF-002 con F-011 |

### Fase 2 (depende de Fase 1)

| Feature | Depende de | Estado | Accion requerida |
|---------|------------|--------|------------------|
| F-002: home-dashboard | F-001 | BLOQUEADA_POR_GAPS | Resolver gap [P-002] |
| F-009: profile | F-001 | BLOQUEADA_POR_GAPS, BLOQUEADA_POR_CONFLICTOS | Resolver gap [P-006]; resolver conflicto CF-003 con F-003 |
| F-003: services-management | F-001, F-004, F-005 (ciclo) | BLOQUEADA_POR_GAPS, BLOQUEADA_POR_CONFLICTOS | Resolver gaps [P-003], [P-004], [P-008]; resolver conflicto CF-003 con F-009; resolver ciclo con F-004/F-005 |
| F-004: time-tracking | F-001, F-003 (ciclo) | ESPERANDO_DEPENDENCIAS | Resolver ciclo con F-003; esperar desbloqueo de F-001 y F-003 |
| F-005: incidents | F-001, F-003 (ciclo) | ESPERANDO_DEPENDENCIAS | Resolver ciclo con F-003; esperar desbloqueo de F-001 y F-003 |

### Fase 3 (depende de Fases 1 y 2)

| Feature | Depende de | Estado | Accion requerida |
|---------|------------|--------|------------------|
| F-006: job-offers | F-001, F-009 | ESPERANDO_DEPENDENCIAS | Esperar desbloqueo de F-001 y F-009 |
| F-007: availability | F-001, F-003 | ESPERANDO_DEPENDENCIAS | Esperar desbloqueo de F-001 y F-003 |
| F-008: absences | F-001, F-003 | BLOQUEADA_POR_GAPS | Resolver gap [P-005]; esperar desbloqueo de F-001 y F-003 |

### Fase 4 (depende de Fases 1, 2 y 3)

| Feature | Depende de | Estado | Accion requerida |
|---------|------------|--------|------------------|
| F-010: communication | F-001, F-003, F-006 | ESPERANDO_DEPENDENCIAS | Esperar desbloqueo de F-001, F-003 y F-006 |

### Fase 5 (depende de Fases 1, 2, 3 y 4)

| Feature | Depende de | Estado | Accion requerida |
|---------|------------|--------|------------------|
| F-011: notifications | F-001, F-003, F-008, F-009, F-010 | BLOQUEADA_POR_CONFLICTOS | Resolver conflicto CF-002 con F-001; esperar desbloqueo de todas las dependencias |

---

## Inventario de gaps bloqueantes

> Los siguientes gaps criticos impiden que las HUs afectadas se completen. Hasta que se resuelvan, las features no pueden pasar a `/wf-prepare-plan`.

| Gap | Severidad | HUs afectadas | Features afectadas | Accion |
|-----|-----------|---------------|-------------------|--------|
| [P-001] | CRITICO | HU-003 | F-001: authentication | Responder y ejecutar `/wf-spec-delta` sobre `features/authentication/authentication_spec.md` |
| [P-002] | CRITICO | HU-006 | F-002: home-dashboard | Responder y ejecutar `/wf-spec-delta` sobre `features/home-dashboard/home-dashboard_spec.md` |
| [P-003] | CRITICO | HU-010 | F-003: services-management | Responder y ejecutar `/wf-spec-delta` sobre `features/services-management/services-management_spec.md` |
| [P-004] | CRITICO | HU-012 | F-003: services-management | Responder y ejecutar `/wf-spec-delta` sobre `features/services-management/services-management_spec.md` |
| [P-005] | CRITICO | HU-019 | F-008: absences | Responder y ejecutar `/wf-spec-delta` sobre `features/absences/absences_spec.md` |
| [P-006] | CRITICO | HU-022, HU-025 | F-009: profile | Responder y ejecutar `/wf-spec-delta` sobre `features/profile/profile_spec.md` |
| [P-007] | CRITICO | HU-004 | F-001: authentication | Responder y ejecutar `/wf-spec-delta` sobre `features/authentication/authentication_spec.md` |
| [P-008] | CRITICO | HU-012 | F-003: services-management | Responder y ejecutar `/wf-spec-delta` sobre `features/services-management/services-management_spec.md` |

---

## Conflictos ALTA no resueltos

> Los siguientes conflictos de severidad ALTA deben resolverse antes de planificar las features afectadas.

| ID | Tipo | Features afectadas | Descripcion breve | Referencia |
|----|------|-------------------|-------------------|------------|
| CF-002 | CA duplicado | F-001: authentication, F-011: notifications | El CA de solicitud de permiso de notificaciones push esta duplicado en ambas features con divergencia (token de dispositivo solo en F-011) | `prd-hogar-sad_conflict_report.md` |
| CF-003 | Shared model inconsistente | F-009: profile, F-003: services-management | El modelo FirmaDigital tiene comportamientos contradictorios: firma persistente en profile vs. captura nueva en cada llamamiento en services-management | `prd-hogar-sad_conflict_report.md` |

---

## Dependencias circulares

> Se detectaron dependencias circulares que impiden determinar el orden de implementacion para las features involucradas.

| Ciclo | Features involucradas | Causa probable |
|-------|----------------------|----------------|
| 1 | F-003 (services-management) <-> F-004 (time-tracking) | F-003 referencia Fichaje (owner: F-004) para acceso desde detalle de servicio; F-004 referencia Servicio (owner: F-003) porque el fichaje se asocia a un servicio |
| 2 | F-003 (services-management) <-> F-005 (incidents) | F-003 referencia Incidencia (owner: F-005) para acceso desde detalle de servicio; F-005 referencia Servicio (owner: F-003) porque la incidencia se asocia a un servicio |

> **Nota**: Estos ciclos son comunes en modulos con navegacion cruzada (un servicio enlaza a sus fichajes/incidencias y viceversa). La resolucion tipica es definir un modulo como "nucleo" (F-003 services-management en este caso) y tratar la navegacion inversa como integracion opcional, no como dependencia dura.

---

## Proximos pasos

1. **Prioriza resolver los gaps `[CRITICO]`** — afectan a 6 features (F-001, F-002, F-003, F-008, F-009 directamente; el resto indirectamente por dependencias):
   - Responde los gaps [P-001] a [P-008] en el `_analysis.md`
   - Ejecuta `/wf-spec-delta analyze <feature_spec.md> --new-reqs <respuestas>` para cada feature afectada
2. **Resuelve los conflictos ALTA** — afectan a 4 features (F-001, F-003, F-009, F-011):
   - **CF-002**: Decide en que spec vive el CA canonico de solicitud de permisos de notificaciones (recomendado: F-011 notifications)
   - **CF-003**: Consulta con cliente/legal si la firma digital es persistente o de un solo uso; actualiza profile_spec.md y services-management_spec.md
3. **Resuelve los ciclos de dependencia** entre F-003, F-004 y F-005:
   - Evalua si las navegaciones cruzadas son dependencias duras o integraciones opcionales
   - Ajusta los READMEs para reflejar la decision
4. **Re-ejecuta `/wf-spec-readiness project/features/`** despues de cada correccion para verificar el progreso
