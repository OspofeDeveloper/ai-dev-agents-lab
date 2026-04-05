# Features Index: Aplicaciones Móviles CUIDEO - Hogar & SAD
> Spec origen: prd-hogar-sad_spec.md | Fecha: 2026-04-02

---

## Features identificadas

### F-001: authentication
- **Descripción**: Gestión de acceso a la app — splash, onboarding, login, registro, activación, recuperación de contraseña y cierre de sesión
- **Actor principal**: Trabajadora Hogar o SAD
- **Estado**: BLOQUEADA_POR_GAPS
- **Journeys propios**: Journey 1 (Primera apertura y onboarding), Journey 2 (Login con sesión persistente), Journey 3 (Activación de cuenta SAD)
- **CAs propios**: CA-001 a CA-017 + CA-098 + CA-102 + CA-103 (en el spec de feature: CA-001 a CA-017)
- **Modelos propios**: Sesión, Credenciales
- **Modelos compartidos (owner)**: Trabajadora ← esta feature la autentica e inicializa
- **Modelos compartidos (ref)**: Ninguno
- **Ruta spec**: features/authentication/authentication_spec.md

---

### F-002: home-dashboard
- **Descripción**: Panel principal adaptado al perfil de la trabajadora — accesos rápidos, widgets de estado, avisos y comunicados del tablón
- **Actor principal**: Trabajadora Hogar o SAD
- **Estado**: BLOQUEADA_POR_GAPS
- **Journeys propios**: (fragmento de Journey 1 — destino final), navegación home SAD y Hogar
- **CAs propios**: CA-018 a CA-030 + CA-031 a CA-033 (en el spec de feature: CA-001 a CA-020)
- **Modelos propios**: Comunicado, MensajeSistema
- **Modelos compartidos (owner)**: Ninguno
- **Modelos compartidos (ref)**: Trabajadora (owner: F-001), Servicio (owner: F-003), Llamamiento (owner: F-003), Documento (owner: F-009), Notificación (owner: F-011)
- **Ruta spec**: features/home-dashboard/home-dashboard_spec.md

---

### F-003: services-management
- **Descripción**: Gestión completa de servicios SAD — listado, detalle, notas, llamamientos y recepción de nuevas asignaciones
- **Actor principal**: Trabajadora SAD
- **Estado**: BLOQUEADA_POR_GAPS
- **Journeys propios**: Journey 5 (Responder a un llamamiento)
- **CAs propios**: CA-034 a CA-052 (en el spec de feature: CA-001 a CA-019)
- **Modelos propios**: Servicio, Llamamiento, NotaServicio
- **Modelos compartidos (owner)**: Servicio ← esta feature lo crea y gestiona; Llamamiento ← esta feature lo gestiona
- **Modelos compartidos (ref)**: Trabajadora (owner: F-001), Fichaje (owner: F-004), Incidencia (owner: F-005)
- **Ruta spec**: features/services-management/services-management_spec.md

---

### F-004: time-tracking
- **Descripción**: Control horario SAD — fichaje de entrada/salida con geolocalización e historial de fichajes
- **Actor principal**: Trabajadora SAD
- **Estado**: ESPERANDO_DEPENDENCIAS
- **Journeys propios**: Journey 4 (Fichar entrada y salida en un servicio)
- **CAs propios**: CA-053 a CA-061 (en el spec de feature: CA-001 a CA-009)
- **Modelos propios**: Fichaje
- **Modelos compartidos (owner)**: Fichaje ← esta feature lo registra y gestiona
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Incidencia (owner: F-005)
- **Ruta spec**: features/time-tracking/time-tracking_spec.md

---

### F-005: incidents
- **Descripción**: Reporte y seguimiento de incidencias SAD — formulario de reporte e historial con filtros
- **Actor principal**: Trabajadora SAD
- **Estado**: ESPERANDO_DEPENDENCIAS
- **Journeys propios**: (flujo de reporte de incidencia desde detalle de servicio o pantalla de fichaje)
- **CAs propios**: CA-062 a CA-064 (en el spec de feature: CA-001 a CA-003)
- **Modelos propios**: Incidencia
- **Modelos compartidos (owner)**: Incidencia ← esta feature la crea y gestiona
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Fichaje (owner: F-004)
- **Ruta spec**: features/incidents/incidents_spec.md

---

### F-006: job-offers
- **Descripción**: Navegación y solicitud de ofertas de trabajo para el perfil Hogar — listado, filtros, solicitud y seguimiento de candidaturas
- **Actor principal**: Trabajadora Hogar
- **Estado**: ESPERANDO_DEPENDENCIAS
- **Journeys propios**: Journey 7 (Solicitar una oferta de trabajo)
- **CAs propios**: CA-065 a CA-070 (en el spec de feature: CA-001 a CA-006)
- **Modelos propios**: Oferta, SolicitudOferta
- **Modelos compartidos (owner)**: Oferta ← esta feature la navega y gestiona
- **Modelos compartidos (ref)**: Trabajadora (owner: F-001), Perfil (owner: F-009)
- **Ruta spec**: features/job-offers/job-offers_spec.md

---

### F-007: availability
- **Descripción**: Gestión de disponibilidad semanal — creación, edición y eliminación de slots de disponibilidad y no disponibilidad
- **Actor principal**: Trabajadora Hogar o SAD
- **Estado**: ESPERANDO_DEPENDENCIAS
- **Journeys propios**: (flujo de declaración de disponibilidad semanal)
- **CAs propios**: CA-071 a CA-076 (en el spec de feature: CA-001 a CA-006)
- **Modelos propios**: SlotDisponibilidad
- **Modelos compartidos (owner)**: SlotDisponibilidad ← esta feature lo crea y gestiona
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Ausencia (owner: F-008)
- **Ruta spec**: features/availability/availability_spec.md

---

### F-008: absences
- **Descripción**: Gestión de ausencias SAD — solicitud, historial y contadores de vacaciones
- **Actor principal**: Trabajadora SAD
- **Estado**: BLOQUEADA_POR_GAPS
- **Journeys propios**: Journey 6 (Solicitar una ausencia)
- **CAs propios**: CA-077 a CA-080 (en el spec de feature: CA-001 a CA-004)
- **Modelos propios**: Ausencia, SolicitudAusencia
- **Modelos compartidos (owner)**: Ausencia ← esta feature la solicita y gestiona
- **Modelos compartidos (ref)**: Servicio (owner: F-003)
- **Ruta spec**: features/absences/absences_spec.md

---

### F-009: profile
- **Descripción**: Gestión del perfil completo de la trabajadora — datos personales, foto, documentos y estado de contrato
- **Actor principal**: Trabajadora Hogar o SAD
- **Estado**: BLOQUEADA_POR_GAPS
- **Journeys propios**: (flujo de edición de perfil, subida de documentos, firma digital)
- **CAs propios**: CA-081 a CA-092 (en el spec de feature: CA-001 a CA-012)
- **Modelos propios**: Perfil, Documento, FirmaDigital
- **Modelos compartidos (owner)**: Perfil ← esta feature lo gestiona; Documento ← esta feature lo organiza y gestiona; FirmaDigital ← esta feature la captura y almacena
- **Modelos compartidos (ref)**: Trabajadora (owner: F-001)
- **Ruta spec**: features/profile/profile_spec.md

---

### F-010: communication
- **Descripción**: Comunicación con coordinación mediante chat — crear conversaciones, mensajes en tiempo real e historial
- **Actor principal**: Trabajadora Hogar o SAD
- **Estado**: ESPERANDO_DEPENDENCIAS
- **Journeys propios**: Journey 8 (Iniciar una conversación con coordinación)
- **CAs propios**: CA-093 a CA-097 (en el spec de feature: CA-001 a CA-005)
- **Modelos propios**: Conversacion, Mensaje
- **Modelos compartidos (owner)**: Conversacion ← esta feature la crea y gestiona; Mensaje ← esta feature los envía y recibe
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Oferta (owner: F-006)
- **Ruta spec**: features/communication/communication_spec.md

---

### F-011: notifications
- **Descripción**: Notificaciones push y historial de notificaciones recibidas — solicitud de permisos, recepción e historial
- **Actor principal**: Trabajadora Hogar o SAD
- **Estado**: BLOQUEADA_POR_CONFLICTOS
- **Journeys propios**: (solicitud de permisos en onboarding, recepción push)
- **CAs propios**: CA-099 a CA-101 + CA-104 + CA-105 (en el spec de feature: CA-001 a CA-005)
- **Modelos propios**: Notificacion, TokenDispositivo
- **Modelos compartidos (owner)**: Notificacion ← esta feature la gestiona y muestra; TokenDispositivo ← esta feature lo registra
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Llamamiento (owner: F-003), Ausencia (owner: F-008), Documento (owner: F-009), Conversacion (owner: F-010)
- **Ruta spec**: features/notifications/notifications_spec.md

---

## Resumen de estado

> Última actualización: 2026-04-04 | Fuente: `prd-hogar-sad_readiness_report.md`

| Feature | Estado | Bloqueantes |
|---------|--------|-------------|
| F-001: authentication | BLOQUEADA_POR_GAPS | P-001, P-007; CF-002 |
| F-002: home-dashboard | BLOQUEADA_POR_GAPS | P-002 |
| F-003: services-management | BLOQUEADA_POR_GAPS | P-003, P-004, P-008; CF-003 |
| F-004: time-tracking | ESPERANDO_DEPENDENCIAS | F-001, F-003 |
| F-005: incidents | ESPERANDO_DEPENDENCIAS | F-001, F-003 |
| F-006: job-offers | ESPERANDO_DEPENDENCIAS | F-001, F-009 |
| F-007: availability | ESPERANDO_DEPENDENCIAS | F-001, F-003 |
| F-008: absences | BLOQUEADA_POR_GAPS | P-005 |
| F-009: profile | BLOQUEADA_POR_GAPS | P-006; CF-003 |
| F-010: communication | ESPERANDO_DEPENDENCIAS | F-001, F-003, F-006 |
| F-011: notifications | BLOQUEADA_POR_CONFLICTOS | CF-002 |

---

## Tabla de shared models

| Modelo | Feature Owner | Features que lo referencian |
|--------|---------------|-----------------------------|
| Trabajadora | F-001: authentication | F-002, F-006, F-009 |
| Sesión / Credenciales | F-001: authentication | F-002 (verificación de estado) |
| Servicio | F-003: services-management | F-002, F-004, F-005, F-007, F-008, F-010, F-011 |
| Llamamiento | F-003: services-management | F-002, F-011 |
| NotaServicio | F-003: services-management | (ninguna — uso exclusivo) |
| Fichaje | F-004: time-tracking | F-003, F-005 |
| Incidencia | F-005: incidents | F-003, F-004 |
| Oferta | F-006: job-offers | F-010 |
| SolicitudOferta | F-006: job-offers | (ninguna — uso exclusivo) |
| SlotDisponibilidad | F-007: availability | (ninguna — uso exclusivo) |
| Ausencia | F-008: absences | F-007, F-011 |
| Perfil | F-009: profile | F-006 (completitud) |
| Documento | F-009: profile | F-002 (badge), F-011 |
| FirmaDigital | F-009: profile | F-003 (llamamientos) |
| Conversacion / Mensaje | F-010: communication | F-011 |
| Notificacion | F-011: notifications | F-002 (badges), todos los emisores |
| TokenDispositivo | F-011: notifications | F-001 (registro en onboarding) |
| Comunicado | F-002: home-dashboard | (ninguna — uso exclusivo) |
| MensajeSistema | F-002: home-dashboard | (ninguna — uso exclusivo) |

---

## Trazabilidad RF → HU → Feature

| RF | Título RF | HU | Título HU | Feature | Estado |
|----|-----------|-----|-----------|---------|--------|
| RF-001 | Autenticación y Onboarding | HU-001 | Ver la pantalla de splash al abrir la app | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-002 | Completar el onboarding inicial | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-003 | Iniciar sesión en la app | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-004 | Activar mi cuenta (SAD) | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-005 | Registrarme en la app (Hogar) | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-029 | Cerrar sesión | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-032 | Ver pantalla de acceso revocado (SAD) | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-035 | Recuperar el acceso a mi cuenta | authentication | activo |
| RF-002 | Panel Principal | HU-006 | Navegar por el panel principal (perfil SAD) | home-dashboard | activo |
| RF-002 | Panel Principal | HU-007 | Navegar por el panel principal (perfil Hogar) | home-dashboard | activo |
| RF-002 | Panel Principal | HU-008 | Leer comunicados del tablón de anuncios | home-dashboard | activo |
| RF-002 | Panel Principal | HU-009 | Ver mensajes del sistema | home-dashboard | activo |
| RF-003 | Mis Servicios (Gestión de Servicios) | HU-010 | Ver el detalle de un servicio (SAD) | services-management | activo |
| RF-003 | Mis Servicios (Gestión de Servicios) | HU-011 | Consultar mis servicios asignados (SAD) | services-management | activo |
| RF-003 | Mis Servicios (Gestión de Servicios) | HU-012 | Responder a un llamamiento (SAD) | services-management | activo |
| RF-003 | Mis Servicios (Gestión de Servicios) | HU-013 | Gestionar notas de un servicio (SAD) | services-management | activo |
| RF-003 | Mis Servicios (Gestión de Servicios) | HU-014 | Recibir y confirmar un nuevo servicio asignado (SAD — contrato indefinido) | services-management | activo |
| RF-004 | Control Horario (Seguimiento de Tiempo) | HU-018 | Fichar entrada y salida en un servicio (SAD) | time-tracking | activo |
| RF-004 | Control Horario (Seguimiento de Tiempo) | HU-033 | Consultar historial de fichajes (SAD) | time-tracking | activo |
| RF-005 | Incidencias | HU-021 | Reportar una incidencia (SAD) | incidents | activo |
| RF-005 | Incidencias | HU-034 | Consultar historial de incidencias (SAD) | incidents | activo |
| RF-006 | Ofertas (Ofertas de Trabajo) | HU-015 | Navegar y filtrar ofertas de trabajo (Hogar) | job-offers | activo |
| RF-006 | Ofertas (Ofertas de Trabajo) | HU-016 | Solicitar una oferta de trabajo (Hogar) | job-offers | activo |
| RF-006 | Ofertas (Ofertas de Trabajo) | HU-017 | Consultar mis solicitudes de oferta (Hogar) | job-offers | activo |
| RF-007 | Mi Disponibilidad (Gestión de Disponibilidad) | HU-026 | Gestionar mi disponibilidad semanal | availability | activo |
| RF-008 | Mis Ausencias (Gestión de Ausencias) | HU-019 | Consultar historial de ausencias y saldo de vacaciones (SAD) | absences | activo |
| RF-008 | Mis Ausencias (Gestión de Ausencias) | HU-020 | Solicitar una ausencia (SAD) | absences | activo |
| RF-009 | Perfil (Gestión de Perfil) | HU-022 | Ver y editar mi perfil | profile | activo |
| RF-009 | Perfil (Gestión de Perfil) | HU-023 | Gestionar mi foto de perfil | profile | activo |
| RF-009 | Perfil (Gestión de Perfil) | HU-024 | Gestionar mis documentos (subir y firmar) | profile | activo |
| RF-009 | Perfil (Gestión de Perfil) | HU-025 | Ver el estado de mi contrato (SAD) | profile | activo |
| RF-010 | Comunicación | HU-027 | Comunicarme con coordinación mediante chat | communication | activo |
| RF-010 | Comunicación | HU-028 | Ver mi historial de conversaciones | communication | activo |
| RF-011 | Notificaciones (Notificaciones Push) | HU-030 | Recibir notificaciones push | notifications | activo |
| RF-011 | Notificaciones (Notificaciones Push) | HU-031 | Consultar el historial de notificaciones | notifications | activo |

> Los IDs de RF son inferidos de las secciones funcionales del PRD — el documento original los numera como RF-1 a RF-12 pero el RF-12 (Publicación de la Aplicación) es de alcance técnico/operativo y no genera HUs funcionales en el Spec. RF-3.4 (Historial de Servicios) se incluyó parcialmente en el alcance de HU-011 y HU-012; el historial completo de servicios completados (RF-3.5 del PRD) quedó fuera de alcance según la sección "Fuera de Alcance" del Spec.

---

## Cobertura por RF

| RF | Título RF | HUs asignadas | Features involucradas |
|----|-----------|---------------|-----------------------|
| RF-001 | Autenticación y Onboarding | HU-001, HU-002, HU-003, HU-004, HU-005, HU-029, HU-032, HU-035 | authentication |
| RF-002 | Panel Principal | HU-006, HU-007, HU-008, HU-009 | home-dashboard |
| RF-003 | Mis Servicios (Gestión de Servicios) | HU-010, HU-011, HU-012, HU-013, HU-014 | services-management |
| RF-004 | Control Horario (Seguimiento de Tiempo) | HU-018, HU-033 | time-tracking |
| RF-005 | Incidencias | HU-021, HU-034 | incidents |
| RF-006 | Ofertas (Ofertas de Trabajo) | HU-015, HU-016, HU-017 | job-offers |
| RF-007 | Mi Disponibilidad (Gestión de Disponibilidad) | HU-026 | availability |
| RF-008 | Mis Ausencias (Gestión de Ausencias) | HU-019, HU-020 | absences |
| RF-009 | Perfil (Gestión de Perfil) | HU-022, HU-023, HU-024, HU-025 | profile |
| RF-010 | Comunicación | HU-027, HU-028 | communication |
| RF-011 | Notificaciones (Notificaciones Push) | HU-030, HU-031 | notifications |

---

## Historial de cambios

| Versión | Fecha | Tipo | Descripción |
|---------|-------|------|-------------|
| 1.0 | 2026-04-02 | decompose | Features asignadas desde wf-spec-decompose |
| 1.1 | 2026-04-04 | readiness | Estado actualizado desde wf-spec-readiness |
