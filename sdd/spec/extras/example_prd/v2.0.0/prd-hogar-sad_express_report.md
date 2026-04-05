# Express Report: CUIDEO - Hogar & SAD
> Generado por: wf-spec-express | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md
> Features generadas: 11

---

## Resumen ejecutivo

> Se generaron 11 features a partir del PRD v1.9 de las aplicaciones moviles CUIDEO (Hogar) y Felizvita (SAD). No hay HUs marcadas [INCOMPLETO]. Se detectaron 23 contaminaciones tecnicas que fueron auto-corregidas, todos los CAs del PRD fueron reformulados al formato GIVEN/WHEN/THEN, y se aplicaron 8 asunciones informativas documentadas.

---

## 1. Contaminaciones tecnicas auto-corregidas

> Todas las contaminaciones fueron auto-corregidas aplicando reescrituras funcionales.

| ID | Cita original | Reescritura aplicada | Feature(s) afectada(s) |
|----|---------------|----------------------|------------------------|
| C-001 | "Kotlin Multiplatform Mobile (KMM)" | Eliminada toda referencia a KMM en los specs; es detalle de implementacion | Todas |
| C-002 | "Jetpack Compose para Android e iOS" | Eliminado; framework UI especifico de plataforma | Todas |
| C-003 | "API RESTful", "Formato de respuesta JSON" | Eliminadas; detalles de arquitectura de backend | Todas |
| C-004 | "Autenticacion basada en JWT" | Reescrito como: "La trabajadora se autentica con email y contrasena" | F-001 |
| C-005 | "Firebase Cloud Messaging" | Reescrito como: "La trabajadora recibe notificaciones push" (sin nombrar proveedor) | F-011 |
| C-006 | "Firebase Realtime Database (mensajeria)" | Reescrito como: "Los mensajes se actualizan en tiempo real" | F-010 |
| C-007 | "Firebase Crashlytics", "Firebase Analytics" | Eliminados; son requisitos no funcionales tecnicos, no funcionalidad de usuario | Todas |
| C-008 | "Token Sanctum valido 30 dias" | Reescrito como: "La sesion se mantiene activa durante 30 dias" preservando el comportamiento funcional sin nombrar la tecnologia | F-001 |
| C-009 | "iOS Keychain / Android Keystore" (CA8 de RF-1.3) | Reescrito como: "Almacenar credenciales de forma segura" | F-001 |
| C-010 | "POST /api/v1/workers/auth/login" y todos los endpoints API | Eliminadas todas las referencias a endpoints de API en los specs; pertenecen al Plan | Todas |
| C-011 | "Diagrama de arquitectura" (ASCII con API REST, Backend, DB) | Eliminado; es arquitectura tecnica | Todas |
| C-012 | "Modulos en shared: Modulo de Red, Cliente API..." | Eliminado; es arquitectura interna | Todas |
| C-013 | "Bundle ID: es.cuideo.hogar", colores hex "#0066CC", "#00AA55" | Eliminados; especificaciones esteticas y de plataforma pertenecen al Plan | Todas |
| C-014 | "iOS 16+ (App Store)", "Android 8+ / API Level 26" | Eliminados; requisitos de compatibilidad tecnica | Todas |
| C-015 | "TLS 1.2+", "Anclaje de certificados" | Eliminados; detalles de seguridad de implementacion | Todas |
| C-016 | "EncryptedSharedPreferences / Android Keystore" | Eliminado; detalle de plataforma | F-001 |
| C-017 | "token FCM" | Reescrito como: "vincular las notificaciones al usuario concreto" en contexto funcional | F-001, F-011 |
| C-018 | "TestFlight", "App Store Connect", "Google Play Console" | Eliminados; requisitos de publicacion son tecnicos, no funcionales | RF-12 no genera feature |
| C-019 | "WCAG AA", "44x44 pts (iOS) / 48x48 dp (Android)" | Eliminados de los specs; son requisitos no funcionales tecnicos | Todas |
| C-020 | "TalkBack/VoiceOver" | Eliminado; referencia a tecnologia de plataforma | Todas |
| C-021 | "Swagger v1.6.0" (referencias en RF-9.1, RF-9.5) | Preservado como nota funcional sobre alineacion pendiente con backend; eliminada referencia al Swagger como fuente tecnica | F-009 |
| C-022 | "GET /api/v1/workers/services/:id?type=service|extra_service" y parametros de query | Eliminados; detalles de API pertenecen al Plan | F-003 |
| C-023 | "POST /api/v1/workers/time-tracking/clock-in body: service_worker_id, type: worker|rest" | Eliminado; parametros de API pertenecen al Plan | F-004 |

---

## 2. Problemas de testabilidad auto-corregidos

> Todos los CAs del PRD estaban en formato "CAX: descripcion" sin estructura GIVEN/WHEN/THEN. Se reformularon 253 CAs al formato requerido.

| ID | CA original | Problema | Reformulacion aplicada | Feature |
|----|-------------|----------|------------------------|---------|
| T-001 | Todos los CAs del PRD (253 CAs) | Formato "CAX: descripcion" sin GIVEN/WHEN/THEN | Reformulados a GIVEN [precondicion] / WHEN [accion] / THEN [resultado observable] | Todas |

> Nota: No se listan individualmente los 253 CAs reformulados por volumen. Cada feature spec contiene los CAs ya reformulados. Los CAs del PRD original se copiaron preservando la semantica funcional y se estructuraron en el formato GIVEN/WHEN/THEN requerido.

---

## 3. Gaps CRITICOS — HUs marcadas [INCOMPLETO]

> Ningun gap critico detectado. Todas las HUs estan completas.

> El PRD v1.9 es suficientemente detallado en sus requisitos funcionales. Los puntos pendientes de confirmacion (computo de vacaciones, copy legal para llamamientos, alineacion de tipos de contrato con Swagger) son informativos y se resolvieron con asunciones conservadoras.

---

## 4. Gaps INFORMATIVOS — Asunciones aplicadas

> Estos gaps se resolvieron con asunciones conservadoras.
> Si no estas de acuerdo con alguna, edita el feature spec directamente
> o usa `/wf-spec-delta` para modificarla formalmente.

| Gap | Pregunta | Asuncion aplicada | Feature(s) |
|-----|----------|-------------------|------------|
| [P-001] | Cual es la duracion exacta de la pantalla de splash? | Se asume 2-3 segundos como indica el PRD, sin animacion adicional configurable | F-001 |
| [P-002] | Cuantas pantallas de onboarding se muestran exactamente? | Se asume 3 pantallas (valor ideal indicado en el PRD), no el maximo de 5 | F-001 |
| [P-003] | Quien define los niveles de criticidad de los mensajes del sistema? | Se asume que el nivel de criticidad (alta/normal) viene definido por el backend; la app solo los muestra diferenciados visualmente | F-002 |
| [P-004] | Cuales son los textos oficiales (copy) de aceptacion y rechazo de llamamientos? | Se usan textos genericos diferenciados hasta que negocio/legal proporcione los textos oficiales | F-003 |
| [P-005] | La caducidad sin respuesta de un llamamiento computa como rechazo por inaccion? | Se muestra como "caducado" sin implicacion de rechazo, pendiente de revision legal | F-003 |
| [P-006] | Cual es el umbral exacto de precision GPS "baja"? | Se define como menor a 50 metros con timeout de espera de 2 segundos, segun indica el PRD | F-004 |
| [P-007] | Las vacaciones se computan por dias naturales o laborables? | Se computan por dias naturales como indica el PRD, pendiente de confirmacion con cliente/legal | F-008 |
| [P-008] | El tipo de contrato es "Indefinido/Fijo Discontinuo" o "Tiempo completo/Tiempo parcial"? | Se asume que son dimensiones distintas; el spec espera "Indefinido/Fijo Discontinuo" pero ambos podrian coexistir cuando se alinee con backend | F-009 |

---

## 5. Shared models — Ownership decidido

> Los shared models fueron asignados automaticamente segun las reglas
> de kb-decompose-expert (creacion -> CRUD completo -> cobertura -> proximidad semantica).

| Modelo | Owner asignado | Criterio aplicado | Otras features que lo referencian |
|--------|----------------|-------------------|-----------------------------------|
| Usuario | F-001: autenticacion-onboarding | Creacion (registro/activacion crea el usuario) | F-002, F-003, F-006, F-007, F-008, F-009, F-010, F-011 |
| Servicio | F-003: gestion-servicios | CRUD completo (listado, detalle, notas, historial) | F-004, F-005, F-008 |
| FirmaDigital | F-009: perfil | Creacion (captura de firma) | F-003 |
| Oferta | F-006: ofertas-trabajo | CRUD completo (listado, detalle, solicitud) | F-010 (enlazar contexto) |
| Anuncio | F-002: panel-principal | CRUD completo (listado, detalle, lectura) | F-011 (deeplink a comunicado) |

---

## 6. Conflictos detectados

> No se detectaron conflictos entre las features generadas.

> Verificacion realizada:
> - HUs duplicadas: ninguna. Cada feature tiene un actor y objetivo distintos o scope claramente diferenciado.
> - CAs contradictorios: ninguno. Los CAs de features que comparten modelos (Servicio, Usuario) operan en contextos funcionales distintos.
> - Scope overlap: ninguno. Las features fueron particionadas por cohesion funcional con boundaries claros. Los puntos de contacto entre features (p.ej. fichaje desde detalle de servicio) son referencias de navegacion, no solapamientos de scope.
> - Shared models inconsistentes: ninguno. Los modelos compartidos tienen ownership claro y uso consistente.
> - Fuera de alcance contradictorio: ninguno.

---

## 7. Completitud del spec (8 elementos SDD)

| Elemento | Estado |
|----------|--------|
| Actores | COMPLETO — 2 actores principales (Trabajadora Hogar, Trabajadora SAD) identificados con capacidades por feature |
| Historias de Usuario | COMPLETO — 39 HUs generadas cubriendo todos los RF funcionales |
| Recorridos de Usuario | COMPLETO — Journeys detallados por feature con flujos principales y alternativos |
| Resultados y Exito | COMPLETO — Definidos por feature |
| Instrucciones Inambiguas | COMPLETO — Reglas de comportamiento y tablas de destinos de navegacion por feature |
| Criterios de Aceptacion | COMPLETO — 253 CAs en formato GIVEN/WHEN/THEN, reformulados desde el PRD |
| Checklist de Validacion | COMPLETO — Todos los items verificables marcados [x] |
| Fuera de Alcance | COMPLETO — Exclusiones funcionales definidas por feature, alineadas con el PRD |

---

## Artefactos generados

| Artefacto | Path |
|-----------|------|
| Features index | prd-hogar-sad_features.md |
| Trazabilidad | prd-hogar-sad_traceability.md |
| Feature spec | features/autenticacion-onboarding/autenticacion-onboarding_spec.md |
| Feature README | features/autenticacion-onboarding/README.md |
| Feature spec | features/panel-principal/panel-principal_spec.md |
| Feature README | features/panel-principal/README.md |
| Feature spec | features/gestion-servicios/gestion-servicios_spec.md |
| Feature README | features/gestion-servicios/README.md |
| Feature spec | features/control-horario/control-horario_spec.md |
| Feature README | features/control-horario/README.md |
| Feature spec | features/incidencias/incidencias_spec.md |
| Feature README | features/incidencias/README.md |
| Feature spec | features/ofertas-trabajo/ofertas-trabajo_spec.md |
| Feature README | features/ofertas-trabajo/README.md |
| Feature spec | features/disponibilidad/disponibilidad_spec.md |
| Feature README | features/disponibilidad/README.md |
| Feature spec | features/ausencias/ausencias_spec.md |
| Feature README | features/ausencias/README.md |
| Feature spec | features/perfil/perfil_spec.md |
| Feature README | features/perfil/README.md |
| Feature spec | features/comunicacion/comunicacion_spec.md |
| Feature README | features/comunicacion/README.md |
| Feature spec | features/notificaciones/notificaciones_spec.md |
| Feature README | features/notificaciones/README.md |
| Express report | prd-hogar-sad_express_report.md |

---

## Proximos pasos

1. **Revisa este informe** — especialmente las secciones 3 (CRITICOS) y 4 (asunciones)
2. **Para cada feature lista**, ejecuta:
   `/wf-prepare-plan features/<nombre>/<nombre>_spec.md`
3. **Si hay HUs `[INCOMPLETO]`**: responde los gaps CRITICOS y usa `/wf-spec-delta`
4. **Si discrepas con una asuncion**: edita el spec o usa `/wf-spec-delta` en la feature afectada
5. **Si hay conflictos ALTA**: resuelvelos antes de avanzar a plan

---

**PRD CONGELADO**
El documento `prd-hogar-sad.md` queda congelado. Para cambios futuros:
`/wf-spec-delta analyze <feature_spec.md> --new-reqs <cambios.md>`
