# Features Index: Aplicaciones Moviles CUIDEO - Hogar & SAD
> PRD origen: prd-hogar-sad.md | Fecha: 2026-04-05
> Generado por: wf-spec-features-first (consolidado)

## Features identificadas

### F-001: auth-and-onboarding
- **Descripcion**: Gestionar el ciclo de vida completo de autenticacion de la trabajadora: registro, inicio de sesion, recuperacion de acceso, onboarding, gestion de sesion y cierre de sesion
- **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
- **Journeys propios**: Registro Hogar, Primer acceso SAD, Inicio de sesion recurrente, Recuperacion de acceso, Onboarding post-primer-login, Cierre de sesion, Acceso revocado
- **HUs**: HU-001 a HU-007 (7) | **CAs**: CA-001 a CA-027 (27)
- **Modelos propios**: Sesion, CredencialesUsuaria
- **Modelos compartidos (owner)**: Usuaria
- **Modelos compartidos (ref)**: --
- **Ruta spec**: features/auth-and-onboarding/auth-and-onboarding_spec.md
- **Estado**: BLOQUEADA_POR_GAPS -- 1 gap critico ([P-001]: campos formulario registro Hogar) + BLOQUEADA_POR_CONFLICTOS (CF-001)

### F-002: dashboard-and-announcements
- **Descripcion**: Proporcionar la pantalla principal con accesos directos contextuales segun perfil, tablon de anuncios y mensajes del sistema
- **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
- **Journeys propios**: Acceder al panel principal, Consultar anuncios, Leer mensajes del sistema, Ver badges pendientes
- **HUs**: HU-001 a HU-005 (5) | **CAs**: 25
- **Modelos propios**: Anuncio, MensajeSistema
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Usuaria (F-001), Servicio (F-003), Llamamiento (F-004)
- **Ruta spec**: features/dashboard-and-announcements/dashboard-and-announcements_spec.md
- **Estado**: BLOQUEADA_POR_GAPS -- 1 gap critico ([P-001]: criterios de criticidad de mensajes del sistema)

### F-003: service-management
- **Descripcion**: Gestionar los servicios asignados a la trabajadora SAD: listado, detalle, notas, historial y recepcion de nuevos servicios
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Consultar listado, Ver detalle servicio, Anadir nota, Consultar historial, Recibir nuevo servicio asignado
- **HUs**: HU-001 a HU-005 (5) | **CAs**: 29
- **Modelos propios**: NotaServicio
- **Modelos compartidos (owner)**: Servicio, Cliente
- **Modelos compartidos (ref)**: Usuaria (F-001)
- **Ruta spec**: features/service-management/service-management_spec.md
- **Estado**: BLOQUEADA_POR_GAPS -- 2 gaps criticos ([P-008]: RGPD datos salud, [P-010]: edicion notas)

### F-004: service-calls
- **Descripcion**: Gestionar el ciclo completo de llamamientos: recibir, evaluar, aceptar o rechazar con firma digital dentro de plazo limitado
- **Actor principal**: Trabajadora SAD (contrato fijo discontinuo)
- **Journeys propios**: Consultar llamamientos, Evaluar llamamiento, Aceptar con firma, Rechazar con firma, Ver caducados/desactivados
- **HUs**: HU-001 a HU-007 (7) | **CAs**: 15
- **Modelos propios**: --
- **Modelos compartidos (owner)**: Llamamiento
- **Modelos compartidos (ref)**: Servicio (F-003), Usuaria (F-001), FirmaDigital (F-010)
- **Ruta spec**: features/service-calls/service-calls_spec.md
- **Estado**: BLOQUEADA_POR_GAPS -- 2 gaps criticos ([P-001]: caducidad llamamientos, [P-002]: copy legal)

### F-005: time-tracking
- **Descripcion**: Registrar entrada y salida de la trabajadora SAD con geolocalizacion y consultar historial de fichajes
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Fichar entrada, Fichar salida, Consultar historial, Reportar incidencia de fichaje
- **HUs**: HU-001 a HU-005 (5) | **CAs**: 22
- **Modelos propios**: RegistroFichaje
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Servicio (F-003), Usuaria (F-001)
- **Ruta spec**: features/time-tracking/time-tracking_spec.md
- **Estado**: BLOQUEADA_POR_CONFLICTOS -- CF-002 (HU duplicada reporte incidencia fichaje con F-006) + ESPERANDO_DEPENDENCIAS (F-001, F-003)

### F-006: incident-reporting
- **Descripcion**: Reportar incidencias del servicio y consultar historial con respuestas de coordinacion
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Reportar incidencia, Consultar historial, Ver detalle con respuestas
- **HUs**: HU-001 a HU-003 (3) | **CAs**: 19
- **Modelos propios**: Incidencia, ComentarioIncidencia
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Servicio (F-003), Usuaria (F-001)
- **Ruta spec**: features/incident-reporting/incident-reporting_spec.md
- **Estado**: BLOQUEADA_POR_CONFLICTOS -- CF-002 (HU duplicada reporte incidencia fichaje con F-005) + ESPERANDO_DEPENDENCIAS (F-001, F-003)

### F-007: job-offers
- **Descripcion**: Navegar ofertas de trabajo, solicitar las que interesen y gestionar el seguimiento de solicitudes
- **Actor principal**: Trabajadora Hogar
- **Journeys propios**: Navegar ofertas, Ver detalle y solicitar, Consultar solicitudes, Retirar solicitud
- **HUs**: HU-001 a HU-006 (6) | **CAs**: 19
- **Modelos propios**: Oferta, Solicitud
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Usuaria (F-001)
- **Ruta spec**: features/job-offers/job-offers_spec.md
- **Estado**: ESPERANDO_DEPENDENCIAS -- F-001 y F-010 bloqueadas

### F-008: absence-management
- **Descripcion**: Solicitar ausencias con documentacion justificativa y consultar historial con saldos de vacaciones
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Solicitar ausencia, Consultar historial, Ver saldo vacaciones, Cancelar solicitud
- **HUs**: HU-001 a HU-004 (4) | **CAs**: 16
- **Modelos propios**: Ausencia, SaldoVacaciones
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Servicio (F-003), Usuaria (F-001)
- **Ruta spec**: features/absence-management/absence-management_spec.md
- **Estado**: BLOQUEADA_POR_GAPS -- 1 gap critico ([P-001]: computo vacaciones dias naturales/laborables)

### F-009: availability-management
- **Descripcion**: Gestionar disponibilidad semanal con franjas rapidas y slots personalizados, visualizando horas contratadas vs trabajadas
- **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
- **Journeys propios**: Visualizar calendario, Crear slot con franja rapida, Crear slot personalizado, Editar/eliminar slot, Consultar horas
- **HUs**: HU-001 a HU-005 (5) | **CAs**: 19
- **Modelos propios**: SlotDisponibilidad, FranjaRapida
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Usuaria (F-001), Servicio (F-003)
- **Ruta spec**: features/availability-management/availability-management_spec.md
- **Estado**: ESPERANDO_DEPENDENCIAS -- F-001 y F-003 bloqueadas

### F-010: profile-and-documents
- **Descripcion**: Gestionar perfil personal/profesional, documentos, firma digital y estado del contrato
- **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
- **Journeys propios**: Editar perfil, Foto de perfil, Gestionar documentos, Firma digital, Estado contrato, Completar perfil Hogar
- **HUs**: HU-001 a HU-006 (6) | **CAs**: 38
- **Modelos propios**: PerfilTrabajadora, Documento, Contrato
- **Modelos compartidos (owner)**: FirmaDigital
- **Modelos compartidos (ref)**: Usuaria (F-001)
- **Ruta spec**: features/profile-and-documents/profile-and-documents_spec.md
- **Estado**: BLOQUEADA_POR_GAPS -- 1 gap critico ([P-001]: discrepancia tipo contrato PRD vs Swagger)

### F-011: communication
- **Descripcion**: Comunicarse con coordinacion mediante chat con asuntos predefinidos, historial de conversaciones y mensajes en tiempo real
- **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
- **Journeys propios**: Iniciar conversacion, Consultar listado, Enviar/recibir mensajes, Consultar cerradas, Buscar/gestionar
- **HUs**: HU-001 a HU-005 (5) | **CAs**: 20
- **Modelos propios**: Conversacion, Mensaje
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Usuaria (F-001), Servicio (F-003), Oferta (F-007)
- **Ruta spec**: features/communication/communication_spec.md
- **Estado**: ESPERANDO_DEPENDENCIAS -- F-001, F-003 y F-007 bloqueadas

### F-012: push-notifications
- **Descripcion**: Gestionar notificaciones push, deeplinks a pantallas especificas e historial de notificaciones
- **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
- **Journeys propios**: Conceder permiso, Recibir notificacion, Navegar desde notificacion, Consultar historial, Recordatorios automaticos
- **HUs**: HU-001 a HU-005 (5) | **CAs**: 23
- **Modelos propios**: Notificacion, PreferenciaNotificacion
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Usuaria (F-001), Servicio (F-003), Llamamiento (F-004), Ausencia (F-008), Documento (F-010), Conversacion (F-011)
- **Ruta spec**: features/push-notifications/push-notifications_spec.md
- **Estado**: BLOQUEADA_POR_GAPS -- 1 gap critico ([P-001]: destinos de navegacion/deeplinks por tipo) + BLOQUEADA_POR_CONFLICTOS (CF-001)

---

## Resumen de estado

> Ultima actualizacion: 2026-04-05 | Fuente: `prd-hogar-sad_readiness_report.md`

| Feature | Estado | Bloqueantes |
|---------|--------|-------------|
| F-001: auth-and-onboarding | BLOQUEADA_POR_GAPS | P-001, CF-001 |
| F-002: dashboard-and-announcements | BLOQUEADA_POR_GAPS | P-001 |
| F-003: service-management | BLOQUEADA_POR_GAPS | P-008, P-010 |
| F-004: service-calls | BLOQUEADA_POR_GAPS | P-001, P-002 |
| F-005: time-tracking | BLOQUEADA_POR_CONFLICTOS | CF-002 |
| F-006: incident-reporting | BLOQUEADA_POR_CONFLICTOS | CF-002 |
| F-007: job-offers | ESPERANDO_DEPENDENCIAS | F-001, F-010 |
| F-008: absence-management | BLOQUEADA_POR_GAPS | P-001 |
| F-009: availability-management | ESPERANDO_DEPENDENCIAS | F-001, F-003 |
| F-010: profile-and-documents | BLOQUEADA_POR_GAPS | P-001 |
| F-011: communication | ESPERANDO_DEPENDENCIAS | F-001, F-003, F-007 |
| F-012: push-notifications | BLOQUEADA_POR_GAPS | P-001, CF-001 |

---

## Tabla de shared models

| Modelo | Feature Owner | Features que lo referencian | Criterio de asignacion |
|--------|---------------|-----------------------------|------------------------|
| Usuaria | F-001: auth-and-onboarding | F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-009, F-010, F-011, F-012 | Creacion explicita: F-001 registra y autentica la entidad |
| Servicio | F-003: service-management | F-002, F-004, F-005, F-006, F-008, F-009, F-011, F-012 | Gestion completa: listado, detalle, notas, historial, asignacion |
| Cliente | F-003: service-management | -- | Proximidad semantica: aparece como parte del detalle de servicio |
| Llamamiento | F-004: service-calls | F-002, F-003, F-012 | Creacion explicita: ciclo de vida completo del llamamiento |
| Oferta | F-007: job-offers | F-011 | Creacion explicita: navegacion, detalle y solicitud de ofertas |
| Ausencia | F-008: absence-management | F-012 | Creacion explicita: solicitud y gestion de ausencias |
| FirmaDigital | F-010: profile-and-documents | F-004 | Creacion explicita: captura, almacenamiento y reutilizacion de la firma |
| Documento | F-010: profile-and-documents | F-012 | Gestion completa: subida, reemplazo, consulta y firma |
| Conversacion | F-011: communication | F-012 | Creacion explicita: crea y gestiona conversaciones |

---

## Trazabilidad RF -> HU -> Feature

| RF | Titulo RF | Feature | HUs generadas |
|----|-----------|---------|---------------|
| RF-1.0 | Pantalla de Splash | F-001: auth-and-onboarding | HU-005 |
| RF-1.1 | Pantallas de Bienvenida | F-001: auth-and-onboarding | HU-004 |
| RF-1.2 | Registro de Usuario | F-001: auth-and-onboarding | HU-001 [INCOMPLETO] |
| RF-1.3 | Inicio de Sesion | F-001: auth-and-onboarding | HU-002 |
| RF-1.4 | Recuperacion de Acceso | F-001: auth-and-onboarding | HU-003 |
| RF-1.5 | Gestion del Token de Sesion | F-001: auth-and-onboarding | HU-005 |
| RF-1.6 | Cierre de Sesion | F-001: auth-and-onboarding | HU-006 |
| RF-1.7 | Pantalla Sin Permisos / Acceso Revocado | F-001: auth-and-onboarding | HU-007 |
| RF-2.1 | Accesos Directos del Panel | F-002: dashboard-and-announcements | HU-001, HU-002, HU-005 |
| RF-2.2 | Tablon de Anuncios / Comunicados | F-002: dashboard-and-announcements | HU-003 |
| RF-2.3 | Mensajes del Sistema | F-002: dashboard-and-announcements | HU-004 [INCOMPLETO] |
| RF-3.1 | Listado de Servicios | F-003: service-management | HU-001 |
| RF-3.2 | Detalle del Servicio | F-003: service-management | HU-002 [INCOMPLETO] |
| RF-3.3 | Notas de Servicio | F-003: service-management | HU-003 [INCOMPLETO] |
| RF-3.4 | Llamadas de Servicio (Llamamientos) | F-004: service-calls | HU-001 a HU-007 |
| RF-3.5 | Historial de Servicios | F-003: service-management | HU-004 |
| RF-3.7 | Nuevo Servicio Asignado | F-003: service-management | HU-005 |
| RF-4.1 | Fichar Entrada/Salida | F-005: time-tracking | HU-001, HU-002 |
| RF-4.2 | Historial de Seguimiento de Tiempo | F-005: time-tracking | HU-003 |
| RF-5.1 | Reportar Incidencia | F-006: incident-reporting | HU-001 |
| RF-5.2 | Historial de Incidencias | F-006: incident-reporting | HU-002, HU-003 |
| RF-6.1 | Navegar Ofertas | F-007: job-offers | HU-001, HU-002 |
| RF-6.2 | Solicitar Oferta | F-007: job-offers | HU-003 |
| RF-6.3 | Mis solicitudes | F-007: job-offers | HU-004, HU-005 |
| RF-7.1 | Calendario de Disponibilidad | F-009: availability-management | HU-001 a HU-005 |
| RF-8.1 | Solicitar Ausencia | F-008: absence-management | HU-001 |
| RF-8.2 | Historial de Ausencias | F-008: absence-management | HU-002, HU-003, HU-004 |
| RF-9.1 | Ver y Editar Perfil | F-010: profile-and-documents | HU-001 |
| RF-9.2 | Foto de Perfil | F-010: profile-and-documents | HU-002 |
| RF-9.3 | Documentos | F-010: profile-and-documents | HU-003 |
| RF-9.4 | Firma Digital | F-010: profile-and-documents | HU-004 |
| RF-9.5 | Estado del Contrato | F-010: profile-and-documents | HU-005 [INCOMPLETO] |
| RF-10.1 | Inicio de Nueva Conversacion | F-011: communication | HU-001 |
| RF-10.2 | Listado de Conversaciones | F-011: communication | HU-002, HU-005 |
| RF-10.3 | Hilo de Conversacion | F-011: communication | HU-003, HU-004 |
| RF-11.1 | Entrega de Notificaciones Push | F-012: push-notifications | HU-001, HU-002 |
| RF-11.2 | Notificaciones Automaticas del Sistema | F-012: push-notifications | HU-003 [INCOMPLETO], HU-005 |

---

## Historial de cambios

| Fecha | Operacion | Detalle |
|-------|-----------|---------|
| 2026-04-05 | features-first | 12 features generadas desde wf-spec-features-first. 5 LISTAS, 7 con gaps criticos pendientes |
| 2026-04-05 | readiness | Estado actualizado desde wf-spec-readiness. 0 LISTAS, 7 BLOQUEADA_POR_GAPS, 2 BLOQUEADA_POR_CONFLICTOS, 3 ESPERANDO_DEPENDENCIAS |
