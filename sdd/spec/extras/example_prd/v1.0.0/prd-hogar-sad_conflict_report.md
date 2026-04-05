# Conflict Report: Aplicaciones Móviles CUIDEO - Hogar & SAD

> **Generado por**: sdd-analyst (modo conflict)
> **Fecha**: 2026-04-02
> **Specs analizados**: 11 features
> **Features**: F-001 authentication, F-002 home-dashboard, F-003 services-management, F-004 time-tracking, F-005 incidents, F-006 job-offers, F-007 availability, F-008 absences, F-009 profile, F-010 communication, F-011 notifications

---

## Estado general

> **CONFLICTOS_DETECTADOS**
>
> Se detectaron 4 conflictos en el análisis de los 11 specs: 2 de severidad ALTA y 2 de severidad MEDIA. Los conflictos de severidad ALTA deben resolverse antes de iniciar `/wf-prepare-plan` en las features afectadas.

---

## Resumen de conflictos

| ID | Tipo | Severidad | Features involucradas |
|----|------|:---------:|-----------------------|
| CF-001 | Scope overlap | MEDIA | F-001 authentication, F-002 home-dashboard |
| CF-002 | CA duplicado | ALTA | F-001 authentication, F-011 notifications |
| CF-003 | Shared model inconsistente | ALTA | F-009 profile, F-003 services-management |
| CF-004 | Fuera de alcance contradictorio | MEDIA | F-004 time-tracking, F-007 availability |

---

## Detalle de conflictos

### [CF-001] Scope overlap — Severidad: MEDIA

**Features involucradas**: `F-001 authentication`, `F-002 home-dashboard`

**Descripción**: El Journey 1 de home-dashboard reproduce textualmente los pasos 1 a 8 del Journey 1 de authentication (splash, login, permisos de notificaciones push, onboarding, permisos de ubicación). Estos pasos son el objetivo principal de F-001; home-dashboard los reutiliza en su propio Journey en lugar de referenciar authentication como dependencia de entrada.

**En `F-001 authentication`** (Journey 1, pasos 1–8):
> "1. La trabajadora abre la app por primera vez. 2. La app muestra la pantalla de splash con el logo de la marca durante 2-3 segundos. 3. No hay sesión activa; la app redirige al login. 4. La trabajadora inicia sesión [...] 5. Tras el login exitoso, la app solicita permiso de notificaciones push. 6. La app muestra las pantallas de onboarding (3-5 pantallas con los highlights principales). 7. La app solicita permiso de ubicación con explicación del uso para fichaje. 8. El onboarding finaliza y la trabajadora llega a la pantalla principal (home)."

**En `F-002 home-dashboard`** (Journey 1, pasos 1–8):
> "1. La trabajadora abre la app por primera vez. 2. La app muestra la pantalla de splash con el logo de la marca durante 2-3 segundos. 3. No hay sesión activa; la app redirige al login. 4. La trabajadora inicia sesión [...] 5. Tras el login exitoso, la app solicita permiso de notificaciones push. 6. La app muestra las pantallas de onboarding (3-5 pantallas con los highlights principales). 7. La app solicita permiso de ubicación con explicación del uso para fichaje. 8. El onboarding finaliza y la trabajadora llega a la pantalla principal (home)."

**Por qué es un conflicto**: Home-dashboard toma prestado el flujo completo de otra feature (authentication) en lugar de referenciarla como dependencia. Si el flujo de onboarding cambia en F-001 (por ejemplo, el orden de solicitud de permisos o los pasos del onboarding), habría dos definiciones del mismo flujo que se desincronizarían. La feature propietaria de ese scope es F-001.

**Sugerencia de resolución**: El Journey 1 de home-dashboard debería reducirse a describir únicamente el destino: "La trabajadora llega a la home como resultado del flujo de autenticación y onboarding (ver F-001 Journey 1)." Los pasos de splash, login y onboarding deben eliminarse del spec de home-dashboard y quedar exclusivamente en authentication.

---

### [CF-002] CA duplicado — Severidad: ALTA

**Features involucradas**: `F-001 authentication`, `F-011 notifications`

**Descripción**: El CA-004 de authentication y el CA-001 de notifications describen exactamente el mismo comportamiento — solicitud de permiso de notificaciones push antes del onboarding — con el mismo GIVEN, el mismo WHEN y el mismo THEN. Tener el mismo CA en dos specs distintos genera dos CAs independientes que un implementador podría interpretar como requisitos separados o que podrían evolucionar de forma inconsistente.

**En `F-001 authentication`** (CA-004):
> "GIVEN la trabajadora acaba de hacer login por primera vez / WHEN se inicia el flujo de onboarding / THEN la app solicita permiso de notificaciones push antes de mostrar las pantallas de onboarding."

**En `F-011 notifications`** (CA-001):
> "GIVEN la trabajadora acaba de hacer login por primera vez / WHEN se inicia el flujo de onboarding / THEN la app solicita permiso de notificaciones push antes de mostrar las pantallas de onboarding; el token del dispositivo queda vinculado al usuario concreto."

**Por qué es un conflicto**: Es un CA duplicado: mismo actor, mismo estado previo, misma acción, mismo resultado esperado. Adicionalmente, la versión de notifications añade "el token del dispositivo queda vinculado al usuario concreto" — un detalle de implementación que no está en authentication, lo que introduce una divergencia entre las dos definiciones del mismo comportamiento.

**Sugerencia de resolución**: El CA canónico de la solicitud de permiso de notificaciones pertenece a F-011 (notifications), dado que el comportamiento de vinculación del token y la gestión del permiso es responsabilidad de esa feature. En authentication CA-004, sustituir el CA completo por una referencia: "Véase F-011 CA-001 — la solicitud de permiso de notificaciones push ocurre en este punto del flujo." Alternativamente, mantener el CA solo en notifications y referenciarlo desde authentication.

---

### [CF-003] Shared model inconsistente — Severidad: ALTA

**Features involucradas**: `F-009 profile`, `F-003 services-management`

**Descripción**: El modelo `FirmaDigital` está declarado con owner en F-009 (profile) y referenciado por F-003 (services-management). Sin embargo, ambas features describen comportamientos incompatibles del modelo: profile indica que la firma se almacena en el perfil y queda disponible para firmas futuras (firma persistente), mientras que services-management describe la captura de firma en cada llamamiento sin ninguna referencia a la firma almacenada (firma de un solo uso por acción).

**En `F-009 profile`** (CA-010):
> "GIVEN la trabajadora accede al lienzo de firma digital / WHEN dibuja su firma con el dedo o stylus / THEN puede borrar/reiniciar la firma, previsualizar antes de guardar, y guardar la firma; **la firma queda almacenada en el perfil y disponible para futuras firmas de documentos**."

**En `F-003 services-management`** (CA-014 y CA-015):
> "GIVEN la trabajadora SAD está en el detalle de un llamamiento pendiente y pulsa aceptar / WHEN se muestra el diálogo de aceptación / THEN **la trabajadora debe firmar digitalmente con el dedo** para confirmar la aceptación."
> "GIVEN la trabajadora SAD está en el detalle de un llamamiento pendiente y pulsa rechazar / WHEN se muestra el diálogo de rechazo / THEN **la trabajadora debe seleccionar un motivo [...] y firmar digitalmente con el dedo**."

**Por qué es un conflicto**: Si la firma se almacena en el perfil y está disponible para usos futuros (F-009), el flujo de llamamientos debería permitir usarla sin re-capturarla. Si cada llamamiento requiere una captura nueva (F-003), entonces la función de almacenamiento de F-009 carece de utilidad práctica en este contexto. No puede ser cierto simultáneamente que la firma sea persistente Y que siempre se requiera captura nueva. El modelo de dominio de FirmaDigital tiene comportamientos contradictorios en ambos specs.

**Sugerencia de resolución**: Aclarar con el cliente el modelo de negocio: (a) si la firma se captura de nueva en cada acto jurídico (llamamientos, documentos) por razones legales, entonces el CA-010 de profile debe eliminar el concepto de "almacenamiento para uso futuro"; o (b) si la firma almacenada puede reutilizarse en los llamamientos, entonces services-management CA-014/CA-015 deben describir que se presenta la firma almacenada para confirmación (no una captura con el dedo desde cero). La decisión tiene implicaciones legales y debe involucrar a legal/backoffice.

---

### [CF-004] Fuera de alcance contradictorio — Severidad: MEDIA

**Features involucradas**: `F-004 time-tracking`, `F-007 availability`

**Descripción**: Time-tracking declara explícitamente en su sección "Fuera de Alcance" que no incluye "Conteo de horas extra o diferencias respecto a horas contratadas en el historial." Sin embargo, availability CA-001 incluye como parte del estado de la pantalla de disponibilidad un indicador de "horas trabajadas vs. horas de contrato" en la cabecera, que es precisamente la comparación entre horas trabajadas y horas contratadas que time-tracking excluye.

**En `F-004 time-tracking`** (Fuera de Alcance):
> "Conteo de horas extra o diferencias respecto a horas contratadas en el historial."

**En `F-007 availability`** (CA-001):
> "GIVEN la trabajadora (Hogar o SAD) accede a 'Mi Disponibilidad' / WHEN la pantalla se carga / THEN se muestra una vista semanal (Lun–Dom) [...]. **En la cabecera se muestran las horas trabajadas vs. horas de contrato de forma prominente.**"

**Por qué es un conflicto**: Time-tracking excluye explícitamente la comparación horas trabajadas/contratadas, pero availability la incluye como elemento visible de su propia pantalla. Ambas features operan sobre la misma dimensión conceptual (tiempo trabajado vs. tiempo comprometido contractualmente). Si nadie es responsable de calcular esa comparativa, el dato que availability necesita mostrar no tiene feature propietaria que lo provea.

**Sugerencia de resolución**: Determinar cuál feature es la propietaria del cómputo "horas trabajadas vs. horas de contrato": (a) si availability es quien lo muestra, debería ser también responsable del cómputo o declarar explícitamente que lo consume del modelo de Fichaje (F-004) sin que time-tracking lo compute; o (b) si ese dato corresponde a time-tracking, entonces time-tracking debe eliminar esta exclusión de su Fuera de Alcance y añadir el CA correspondiente. En cualquier caso, ambas features deben acordar el origen del dato.

---

## Inventario de comparaciones realizadas

> Esta sección garantiza trazabilidad de qué se comparó contra qué.

| Check | Features comparadas | Conflictos encontrados |
|-------|---------------------|:---------------------:|
| HUs duplicadas | Todos los pares (55 combinaciones, 25 HUs totales) | 0 |
| CAs contradictorios / duplicados | Todos los pares — foco en mismo GIVEN+WHEN | 1 (CF-002) |
| Scope overlap | Todos los pares — Journeys y objetivos funcionales | 1 (CF-001) |
| Shared models inconsistentes | Todos los specs vs. tabla shared models del `_features.md` | 1 (CF-003) |
| Fuera de alcance contradictorio | Todas las secciones Fuera de Alcance vs. HUs/CAs del resto | 1 (CF-004) |

---

## Próximos pasos

1. Revisar cada conflicto de severidad **ALTA** — deben resolverse antes de iniciar `/wf-prepare-plan` en las features afectadas:
   - **CF-002**: Decidir en qué spec vive el CA canónico de solicitud de permisos de notificaciones. Editar authentication_spec.md o notifications_spec.md para eliminar la duplicidad.
   - **CF-003**: Consultar con cliente/legal si la firma digital es persistente (reutilizable) o de un solo uso por acto. Actualizar profile_spec.md y services-management_spec.md para que el modelo FirmaDigital tenga un único comportamiento coherente.
2. Los conflictos de severidad **MEDIA** pueden documentarse como decisiones de diseño y resolverse en la fase de implementación:
   - **CF-001**: Limpiar el Journey 1 de home-dashboard para que referencie authentication en lugar de duplicar sus pasos.
   - **CF-004**: Acordar quién provee el dato "horas trabajadas vs. horas de contrato" y actualizar los specs de time-tracking y/o availability.
3. Para cada conflicto resuelto: editar los specs afectados y re-ejecutar `/wf-spec-conflict features/authentication/authentication_spec.md --features-dir features/` para verificar que se eliminó.
