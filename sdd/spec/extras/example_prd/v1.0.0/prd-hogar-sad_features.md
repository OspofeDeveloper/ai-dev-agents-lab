# Features Index: Aplicaciones Móviles CUIDEO - Hogar & SAD
> Spec origen: prd-hogar-sad_spec.md | Fecha: 2026-04-02

---

## Features identificadas

### F-001: authentication
- **Descripción**: Gestión de acceso a la app — splash, onboarding, login, registro, activación, recuperación de contraseña y cierre de sesión
- **Actor principal**: Trabajadora Hogar o SAD
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
- **Journeys propios**: (solicitud de permisos en onboarding, recepción push)
- **CAs propios**: CA-099 a CA-101 + CA-104 + CA-105 (en el spec de feature: CA-001 a CA-005)
- **Modelos propios**: Notificacion, TokenDispositivo
- **Modelos compartidos (owner)**: Notificacion ← esta feature la gestiona y muestra; TokenDispositivo ← esta feature lo registra
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Llamamiento (owner: F-003), Ausencia (owner: F-008), Documento (owner: F-009), Conversacion (owner: F-010)
- **Ruta spec**: features/notifications/notifications_spec.md

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
