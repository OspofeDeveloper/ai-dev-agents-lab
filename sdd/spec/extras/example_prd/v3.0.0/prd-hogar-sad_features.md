# Features Index: Aplicaciones Moviles CUIDEO - Hogar & SAD

> Spec origen: prd-hogar-sad_spec.md | Fecha: 2026-04-05

---

## Features identificadas

### F-001: authentication
- **Descripcion**: Gestiona el registro, activacion, inicio de sesion, sesion persistente, recuperacion de acceso, cierre de sesion y onboarding de las trabajadoras
- **Actor principal**: Trabajadora (Hogar o SAD)
- **Journeys propios**: Journey 1 (Registro y primer acceso Hogar), Journey 2 (Activacion y primer acceso SAD), Journey 3 (Inicio de sesion habitual), Journey 4 (Recuperacion de acceso)
- **CAs propios**: CA-001 a CA-016 en el spec de esta feature
- **Modelos propios**: —
- **Modelos compartidos (owner)**: Usuario/Sesion
- **Modelos compartidos (ref)**: —
- **Ruta spec**: features/authentication/authentication_spec.md
- **Estado**: pendiente-readiness

### F-002: home-dashboard
- **Descripcion**: Presenta el panel principal con accesos directos diferenciados por perfil, el tablon de comunicados, los mensajes del sistema y la diferenciacion de marca
- **Actor principal**: Trabajadora (Hogar o SAD)
- **Journeys propios**: — (punto de llegada/partida de otros journeys; flujos secundarios de comunicados y mensajes)
- **CAs propios**: CA-001 a CA-016 en el spec de esta feature
- **Modelos propios**: Comunicado, MensajeSistema
- **Modelos compartidos (owner)**: —
- **Modelos compartidos (ref)**: Usuario/Sesion (owner: F-001), Servicio (owner: F-003), Llamamiento (owner: F-004)
- **Ruta spec**: features/home-dashboard/home-dashboard_spec.md
- **Estado**: pendiente-readiness

### F-003: services
- **Descripcion**: Permite consultar servicios asignados, ver detalle, registrar notas de servicio con adjuntos y consultar historial de servicios
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Journey 5 (Consultar servicios y ver detalle)
- **CAs propios**: CA-001 a CA-014 en el spec de esta feature
- **Modelos propios**: —
- **Modelos compartidos (owner)**: Servicio, NotaServicio
- **Modelos compartidos (ref)**: Usuario/Sesion (owner: F-001)
- **Ruta spec**: features/services/services_spec.md
- **Estado**: pendiente-readiness

### F-004: callouts
- **Descripcion**: Gestiona la recepcion, visualizacion, aceptacion y rechazo de llamamientos con firma digital obligatoria y gestion de caducidad
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Journey 7 (Responder a un llamamiento)
- **CAs propios**: CA-001 a CA-003 en el spec de esta feature
- **Modelos propios**: —
- **Modelos compartidos (owner)**: Llamamiento
- **Modelos compartidos (ref)**: Servicio (owner: F-003), FirmaDigital (owner: F-011), Usuario/Sesion (owner: F-001)
- **Ruta spec**: features/callouts/callouts_spec.md
- **Estado**: pendiente-readiness

### F-005: time-tracking
- **Descripcion**: Permite fichar entrada y salida de un servicio con geolocalizacion y consultar historial de seguimiento de tiempo
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Journey 6 (Fichar entrada y salida de servicio)
- **CAs propios**: CA-001 a CA-008 en el spec de esta feature
- **Modelos propios**: —
- **Modelos compartidos (owner)**: RegistroFichaje
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Usuario/Sesion (owner: F-001)
- **Ruta spec**: features/time-tracking/time-tracking_spec.md
- **Estado**: pendiente-readiness

### F-006: incidents
- **Descripcion**: Permite reportar incidencias del servicio con descripcion y adjuntos, y consultar historial de incidencias con estado y respuestas
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Journey 8 (Reportar incidencia), Journey 14 (Consultar historial de incidencias)
- **CAs propios**: CA-001 a CA-003 en el spec de esta feature
- **Modelos propios**: —
- **Modelos compartidos (owner)**: Incidencia
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Usuario/Sesion (owner: F-001)
- **Ruta spec**: features/incidents/incidents_spec.md
- **Estado**: pendiente-readiness

### F-007: absences
- **Descripcion**: Permite solicitar ausencias con tipo, fechas, justificacion y documentacion, y consultar historial de ausencias con saldo de vacaciones
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Journey 9 (Solicitar ausencia), Journey 15 (Consultar historial de ausencias)
- **CAs propios**: CA-001 a CA-005 en el spec de esta feature
- **Modelos propios**: —
- **Modelos compartidos (owner)**: Ausencia
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Usuario/Sesion (owner: F-001)
- **Ruta spec**: features/absences/absences_spec.md
- **Estado**: pendiente-readiness

### F-008: job-offers
- **Descripcion**: Permite navegar ofertas de trabajo con filtros, solicitar ofertas y hacer seguimiento de solicitudes
- **Actor principal**: Trabajadora Hogar
- **Journeys propios**: Journey 10 (Navegar y solicitar oferta)
- **CAs propios**: CA-001 a CA-006 en el spec de esta feature
- **Modelos propios**: —
- **Modelos compartidos (owner)**: Oferta, Solicitud
- **Modelos compartidos (ref)**: Usuario/Sesion (owner: F-001), Perfil (owner: F-011)
- **Ruta spec**: features/job-offers/job-offers_spec.md
- **Estado**: pendiente-readiness

### F-009: availability
- **Descripcion**: Permite gestionar disponibilidad semanal mediante calendario con franjas horarias predefinidas y personalizadas
- **Actor principal**: Trabajadora (Hogar o SAD)
- **Journeys propios**: Journey 11 (Gestionar disponibilidad)
- **CAs propios**: CA-001 a CA-006 en el spec de esta feature
- **Modelos propios**: —
- **Modelos compartidos (owner)**: SlotDisponibilidad
- **Modelos compartidos (ref)**: Usuario/Sesion (owner: F-001)
- **Ruta spec**: features/availability/availability_spec.md
- **Estado**: pendiente-readiness

### F-010: messaging
- **Descripcion**: Permite iniciar conversaciones con coordinacion, enviar y recibir mensajes en tiempo real y gestionar listado de conversaciones
- **Actor principal**: Trabajadora (Hogar o SAD)
- **Journeys propios**: Journey 12 (Comunicarse con coordinacion)
- **CAs propios**: CA-001 a CA-005 en el spec de esta feature
- **Modelos propios**: —
- **Modelos compartidos (owner)**: Conversacion, Mensaje
- **Modelos compartidos (ref)**: Usuario/Sesion (owner: F-001), Servicio (owner: F-003), Oferta (owner: F-008)
- **Ruta spec**: features/messaging/messaging_spec.md
- **Estado**: pendiente-readiness

### F-011: profile-documents
- **Descripcion**: Gestiona perfil personal y profesional, foto de perfil, documentos personales y laborales, firma digital y estado del contrato
- **Actor principal**: Trabajadora (Hogar o SAD)
- **Journeys propios**: Journey 13 (Gestionar documentos)
- **CAs propios**: CA-001 a CA-009 en el spec de esta feature
- **Modelos propios**: —
- **Modelos compartidos (owner)**: Perfil, Documento, FirmaDigital
- **Modelos compartidos (ref)**: Usuario/Sesion (owner: F-001)
- **Ruta spec**: features/profile-documents/profile-documents_spec.md
- **Estado**: pendiente-readiness

### F-012: notifications
- **Descripcion**: Gestiona registro de dispositivo para push, notificaciones automaticas, deeplinks de navegacion e historial de notificaciones
- **Actor principal**: Trabajadora (Hogar o SAD)
- **Journeys propios**: — (transversal; flujos de registro, recepcion y consulta de historial)
- **CAs propios**: CA-001 a CA-003 en el spec de esta feature
- **Modelos propios**: —
- **Modelos compartidos (owner)**: RegistroDispositivo, Notificacion
- **Modelos compartidos (ref)**: Usuario/Sesion (owner: F-001)
- **Ruta spec**: features/notifications/notifications_spec.md
- **Estado**: pendiente-readiness

---

## Resumen de estado

| Feature | Estado | Bloqueantes |
|---------|--------|-------------|
<!-- Se completa tras ejecutar /wf-spec-readiness -->

---

## Tabla de shared models

| Modelo | Feature Owner | Features que lo referencian |
|--------|---------------|-----------------------------|
| Usuario/Sesion | F-001: authentication | F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-009, F-010, F-011, F-012 |
| Servicio | F-003: services | F-002, F-004, F-005, F-006, F-007, F-010 |
| NotaServicio | F-003: services | — |
| Llamamiento | F-004: callouts | F-002 |
| RegistroFichaje | F-005: time-tracking | — |
| Incidencia | F-006: incidents | — |
| Ausencia | F-007: absences | — |
| Oferta | F-008: job-offers | F-010 |
| Solicitud | F-008: job-offers | — |
| SlotDisponibilidad | F-009: availability | — |
| Conversacion | F-010: messaging | — |
| Mensaje | F-010: messaging | — |
| Perfil | F-011: profile-documents | F-008 |
| Documento | F-011: profile-documents | — |
| FirmaDigital | F-011: profile-documents | F-004 |
| RegistroDispositivo | F-012: notifications | — |
| Notificacion | F-012: notifications | — |

---

## Trazabilidad RF → HU → Feature

| RF | Titulo RF | HU | Titulo HU | Feature | Estado |
|----|-----------|-----|-----------|---------|--------|
| RF-1 | Autenticacion y Onboarding | HU-001 | Pantalla de splash | authentication | activo |
| RF-1 | Autenticacion y Onboarding | HU-002 | Registro de cuenta (Hogar) | authentication | activo |
| RF-1 | Autenticacion y Onboarding | HU-003 | Pantallas de bienvenida (onboarding) | authentication | activo |
| RF-1 | Autenticacion y Onboarding | HU-004 | Activacion de cuenta (SAD) | authentication | activo |
| RF-1 | Autenticacion y Onboarding | HU-005 | Inicio de sesion | authentication | activo |
| RF-1 | Autenticacion y Onboarding | HU-006 | Sesion persistente | authentication | activo |
| RF-1 | Autenticacion y Onboarding | HU-007 | Recuperacion de acceso | authentication | activo |
| RF-1 | Autenticacion y Onboarding | HU-008 | Cierre de sesion | authentication | activo |
| RF-1 | Autenticacion y Onboarding | HU-009 | Pantalla de acceso revocado (SAD) | authentication | activo |
| RF-2 | Panel Principal | HU-010 | Panel principal con accesos directos | home-dashboard | activo |
| RF-2 | Panel Principal | HU-011 | Tablon de anuncios y comunicados | home-dashboard | activo |
| RF-2 | Panel Principal | HU-012 | Mensajes del sistema | home-dashboard | activo |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-013 | Listado de servicios (SAD) | services | activo |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-014 | Detalle del servicio (SAD) | services | activo |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-015 | Notas de servicio (SAD) | services | activo |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-016 | Detalle del llamamiento (SAD) | callouts | activo |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-017 | Aceptar o rechazar llamamiento (SAD) | callouts | activo |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-018 | Listado de llamamientos (SAD) | callouts | activo |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-019 | Nuevo servicio asignado - contratos indefinidos (SAD) | services | activo |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-030 | Historial de servicios (SAD) | services | activo |
| RF-4 | Control Horario (Seguimiento de Tiempo) | HU-022 | Fichar entrada y salida (SAD) | time-tracking | activo |
| RF-4 | Control Horario (Seguimiento de Tiempo) | HU-023 | Historial de seguimiento de tiempo (SAD) | time-tracking | activo |
| RF-5 | Incidencias | HU-024 | Reportar incidencia (SAD) | incidents | activo |
| RF-5 | Incidencias | HU-025 | Historial de incidencias (SAD) | incidents | activo |
| RF-6 | Ofertas (Ofertas de Trabajo) | HU-028 | Navegar ofertas de trabajo (Hogar) | job-offers | activo |
| RF-6 | Ofertas (Ofertas de Trabajo) | HU-037 | Solicitar oferta de trabajo (Hogar) | job-offers | activo |
| RF-6 | Ofertas (Ofertas de Trabajo) | HU-038 | Mis solicitudes (Hogar) | job-offers | activo |
| RF-6 | Ofertas (Ofertas de Trabajo) | HU-044 | Completar perfil antes de aplicar (Hogar) | job-offers | activo |
| RF-7 | Mi Disponibilidad (Gestion de Disponibilidad) | HU-029 | Calendario de disponibilidad | availability | activo |
| RF-8 | Mis Ausencias (Gestion de Ausencias) | HU-026 | Solicitar ausencia (SAD) | absences | activo |
| RF-8 | Mis Ausencias (Gestion de Ausencias) | HU-027 | Historial de ausencias (SAD) | absences | activo |
| RF-9 | Perfil (Gestion de Perfil) | HU-032 | Ver y editar perfil | profile-documents | activo |
| RF-9 | Perfil (Gestion de Perfil) | HU-033 | Estado del contrato (SAD) | profile-documents | activo |
| RF-9 | Perfil (Gestion de Perfil) | HU-034 | Foto de perfil | profile-documents | activo |
| RF-9 | Perfil (Gestion de Perfil) | HU-035 | Gestion de documentos | profile-documents | activo |
| RF-9 | Perfil (Gestion de Perfil) | HU-036 | Firma digital | profile-documents | activo |
| RF-10 | Comunicacion | HU-039 | Iniciar conversacion con coordinacion | messaging | activo |
| RF-10 | Comunicacion | HU-040 | Listado de conversaciones | messaging | activo |
| RF-10 | Comunicacion | HU-041 | Hilo de conversacion | messaging | activo |
| RF-11 | Notificaciones (Notificaciones Push) | HU-020 | Deeplinks de notificaciones push | notifications | activo |
| RF-11 | Notificaciones (Notificaciones Push) | HU-021 | Notificaciones automaticas del sistema | notifications | activo |
| RF-11 | Notificaciones (Notificaciones Push) | HU-031 | Registrar dispositivo para notificaciones push | notifications | activo |
| RF-11 | Notificaciones (Notificaciones Push) | HU-042 | Historial de notificaciones | notifications | activo |
| RF-12 | Publicacion de la Aplicacion | HU-043 | Aplicaciones de marca diferenciada | home-dashboard | activo |

---

## Cobertura por RF

| RF | Titulo RF | HUs asignadas | Features involucradas |
|----|-----------|---------------|-----------------------|
| RF-1 | Autenticacion y Onboarding | HU-001, HU-002, HU-003, HU-004, HU-005, HU-006, HU-007, HU-008, HU-009 | authentication |
| RF-2 | Panel Principal | HU-010, HU-011, HU-012 | home-dashboard |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-013, HU-014, HU-015, HU-016, HU-017, HU-018, HU-019, HU-030 | services, callouts |
| RF-4 | Control Horario (Seguimiento de Tiempo) | HU-022, HU-023 | time-tracking |
| RF-5 | Incidencias | HU-024, HU-025 | incidents |
| RF-6 | Ofertas (Ofertas de Trabajo) | HU-028, HU-037, HU-038, HU-044 | job-offers |
| RF-7 | Mi Disponibilidad (Gestion de Disponibilidad) | HU-029 | availability |
| RF-8 | Mis Ausencias (Gestion de Ausencias) | HU-026, HU-027 | absences |
| RF-9 | Perfil (Gestion de Perfil) | HU-032, HU-033, HU-034, HU-035, HU-036 | profile-documents |
| RF-10 | Comunicacion | HU-039, HU-040, HU-041 | messaging |
| RF-11 | Notificaciones (Notificaciones Push) | HU-020, HU-021, HU-031, HU-042 | notifications |
| RF-12 | Publicacion de la Aplicacion | HU-043 | home-dashboard |

---

## Historial de cambios

| Version | Fecha | Tipo | Descripcion |
|---------|-------|------|-------------|
| 1.0 | 2026-04-05 | decompose | Features asignadas desde wf-spec-decompose |
