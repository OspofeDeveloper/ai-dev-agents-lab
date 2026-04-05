# Project Hub: CUIDEO — Aplicaciones Móviles Hogar & SAD
> PRD origen: prd-hogar-sad.md
> Generado via: wf-spec-fast-track (features-first)
> Última actualización: 2026-04-05 (actualizado con F-008: profile-management)

---

## Índice de Features

| Feature ID | Nombre | Actor principal | Spec | Plan | Tasks | Estado |
|------------|--------|-----------------|------|------|-------|--------|
| F-001 | [auth-and-onboarding](features/auth-and-onboarding/README.md) | Trabajadora (Hogar/SAD) | ✓ | — | — | Spec listo |
| F-002 | [home-dashboard](features/home-dashboard/home-dashboard_spec.md) | Trabajadora (Hogar o SAD) | ✓ | — | — | Spec listo |
| F-003 | [service-management](features/service-management/README.md) | Trabajadora SAD (Felizvita) | [✓](features/service-management/service-management_spec.md) | — | — | ⚠ INCOMPLETO ([P-001]) |
| F-004 | [time-tracking](features/time-tracking/time-tracking_spec.md) | Trabajadora SAD (Felizvita) | ✓ | — | — | Spec listo |
| F-005 | [incident-reporting](features/incident-reporting/incident-reporting_spec.md) | Trabajadora SAD (Felizvita) | ✓ | — | — | Spec listo |
| F-006 | [job-offers](features/job-offers/job-offers_spec.md) | Trabajadora Hogar (CUIDEO) | ✓ | — | — | Spec listo |
| F-007 | [availability-management](features/availability-management/availability-management_spec.md) | Trabajadora (Hogar o SAD) | ✓ | — | — | Spec listo |
| F-008 | [profile-management](features/profile-management/profile-management_spec.md) | Trabajadora (Hogar o SAD) | ✓ | — | — | ⚠ INCOMPLETO ([P-001]) |
| F-009 | [push-notifications](features/push-notifications/push-notifications_spec.md) | Trabajadora (Hogar o SAD) | ✓ | — | — | Spec listo |
| F-010 | [absence-management](features/absence-management/absence-management_spec.md) | Trabajadora SAD (Felizvita) | ✓ | — | — | ⚠ INCOMPLETO ([P-001], [P-002]) |
| F-011 | [communication](features/communication/communication_spec.md) | Trabajadora (Hogar o SAD) | ✓ | — | — | Spec listo |
| F-012 | [app-publishing](features/app-publishing/app-publishing_spec.md) | Equipo de desarrollo / DevOps | ✓ | — | — | Spec listo |

---

## Shared Models

| Modelo | Feature Owner | Features que lo referencian | Criterio de asignación |
|--------|---------------|-----------------------------|------------------------|
| Worker | F-001: auth-and-onboarding | F-002, F-004, F-005, F-006, F-007, F-008, F-009, F-010, F-011 | Creación al registrarse (Hogar) o activar cuenta (SAD): F-001 define la entidad base Worker; la actualización de perfil es responsabilidad compartida con F-008 |
| AuthToken | F-001: auth-and-onboarding | — | Creación explícita: F-001 gestiona el token de sesión activa de la trabajadora |
| Session | F-001: auth-and-onboarding | — | Creación explícita: F-001 gestiona el estado de sesión local (activa, caducada, revocada) |
| OnboardingState | F-001: auth-and-onboarding | — | Creación explícita: F-001 almacena el estado de completación del onboarding en el dispositivo |
| Document | F-008: profile-management | F-002 (badge documentos pendientes de firma en home) | Creación y CRUD: F-008 gestiona el ciclo de vida de los documentos personales y laborales de la trabajadora |
| Signature | F-008: profile-management | F-003 (firma digital en llamamientos) | Creación explícita: F-008 captura, almacena y gestiona la firma digital de la trabajadora |
| ContractInfo | F-008: profile-management | — | Creación explícita: F-008 muestra la información del contrato SAD (solo lectura desde backoffice) |
| Service | F-003: service-management | F-002, F-004, F-005, F-010, F-011 | CRUD completo: F-003 gestiona el ciclo de vida completo de los servicios asignados |
| ServiceCall | F-003: service-management | — | Creación explícita: F-003 define el modelo de llamamiento y sus estados (pendiente, aceptado, rechazado, caducado, desactivado) |
| ServiceNote | F-003: service-management | — | CRUD completo: F-003 gestiona las notas de servicio con categorías y adjuntos |
| ServiceHistory | F-003: service-management | — | Creación explícita: F-003 define el historial de servicios completados |
| TimeEntry | F-004: time-tracking | — | Owner: F-004 crea y gestiona los registros de fichaje (entrada, salida, duración, coordenadas) |
| TimeTrackingStatus | F-004: time-tracking | — | Owner: F-004 gestiona el estado dinámico del botón de fichaje por servicio |
| Incident | F-005: incident-reporting | F-003 (reportar desde detalle de servicio), F-004 (referencia desde pantalla de fichaje) | Creación y CRUD completo: F-005 define el ciclo de vida de las incidencias |
| IncidentAttachment | F-005: incident-reporting | — | Creación explícita: F-005 gestiona los adjuntos de las incidencias |
| DeviceRegistration | F-009: push-notifications | F-001 (registro post-login) | Creación explícita: F-009 gestiona el registro del dispositivo para push |
| NotificationRecord | F-009: push-notifications | — | Creación explícita: F-009 almacena el historial de notificaciones recibidas |
| AbsenceRequest | F-010: absence-management | — | Creación y CRUD completo: F-010 define el ciclo de vida de las solicitudes de ausencia |
| VacationBalance | F-010: absence-management | — | Creación explícita: F-010 gestiona los saldos de ausencias por tipo |
| JobOffer | F-006: job-offers | F-011 (enlace contexto conversación) | Creación explícita y CRUD: F-006 define el modelo y sus operaciones |
| JobApplication | F-006: job-offers | — | Creación explícita y CRUD: F-006 define el modelo de solicitud con sus estados (Pendiente, En revisión, Aceptada, Rechazada, Oferta cerrada) |
| AvailabilitySlot | F-007: availability-management | — | Creación y CRUD: F-007 gestiona las franjas de disponibilidad declaradas por la trabajadora |
| UnavailabilitySlot | F-007: availability-management | — | Creación y CRUD: F-007 gestiona las franjas de no disponibilidad declaradas por la trabajadora |
| Conversation | F-011: communication | F-002 (badge mensajes no leídos) | CRUD completo: F-011 gestiona el ciclo de vida de las conversaciones |
| Message | F-011: communication | — | Creación explícita: F-011 gestiona el envío, recepción y estado de los mensajes |

---

## Trazabilidad RF → HU → Feature

| RF | Título RF | Feature | HUs |
|----|-----------|---------|-----|
| RF-1.0 | Pantalla de Splash | F-001: auth-and-onboarding | HU-001 |
| RF-1.1 | Pantallas de Bienvenida (Onboarding) | F-001: auth-and-onboarding | HU-002 |
| RF-1.2 | Registro de Usuario | F-001: auth-and-onboarding | HU-003, HU-004 |
| RF-1.3 | Inicio de Sesión | F-001: auth-and-onboarding | HU-005, HU-006 |
| RF-1.4 | Recuperación de Acceso | F-001: auth-and-onboarding | HU-007 |
| RF-1.5 | Gestión del Token de Sesión | F-001: auth-and-onboarding | HU-008 |
| RF-1.6 | Cierre de Sesión | F-001: auth-and-onboarding | HU-009 |
| RF-1.7 | Pantalla Sin Permisos / Acceso Revocado | F-001: auth-and-onboarding | HU-010 |
| RF-2.1 | Accesos Directos del Panel (Home) | F-002: home-dashboard | HU-001, HU-002, HU-003 |
| RF-2.2 | Tablón de Anuncios / Comunicados | F-002: home-dashboard | HU-004 |
| RF-2.3 | Mensajes del Sistema | F-002: home-dashboard | HU-005 |
| RF-3.1 | Listado de Servicios | F-003: service-management | HU-001 |
| RF-3.2 | Detalle del Servicio | F-003: service-management | HU-002 |
| RF-3.3 | Notas de Servicio | F-003: service-management | HU-003 |
| RF-3.4 | Llamadas de Servicio (Llamamientos) | F-003: service-management | HU-004 |
| RF-3.5 | Historial de Servicios | F-003: service-management | HU-005 |
| RF-3.7 | Nuevo Servicio Asignado (Contratos Indefinidos) | F-003: service-management | HU-006 |
| RF-4.1 | Fichar Entrada/Salida | F-004: time-tracking | HU-001, HU-002, HU-003, HU-004, HU-005 |
| RF-4.2 | Historial de Seguimiento de Tiempo | F-004: time-tracking | HU-006 |
| RF-5.1 | Reportar Incidencia | F-005: incident-reporting | HU-001, HU-002, HU-004 |
| RF-5.2 | Historial de Incidencias | F-005: incident-reporting | HU-003 |
| RF-6.1 | Navegar Ofertas | F-006: job-offers | HU-001 |
| RF-6.2 | Solicitar Oferta | F-006: job-offers | HU-002 |
| RF-6.3 | Mis Solicitudes | F-006: job-offers | HU-003 |
| RF-7.1 | Calendario de Disponibilidad | F-007: availability-management | HU-001, HU-002, HU-003, HU-004, HU-005, HU-006, HU-007 |
| RF-9.1 | Ver y Editar Perfil | F-008: profile-management | HU-001, HU-002, HU-004, HU-008 |
| RF-9.2 | Foto de Perfil | F-008: profile-management | HU-003 |
| RF-9.3 | Documentos | F-008: profile-management | HU-005, HU-006 |
| RF-9.4 | Firma Digital | F-008: profile-management | HU-007 |
| RF-9.5 | Estado del Contrato | F-008: profile-management | HU-009 |
| RF-10.1 | Inicio de Nueva Conversación | F-011: communication | HU-001, HU-002 |
| RF-10.2 | Listado de Conversaciones | F-011: communication | HU-003, HU-004 |
| RF-10.3 | Hilo de Conversación | F-011: communication | HU-005, HU-006, HU-007 |
| RF-11.1 | Entrega de Notificaciones Push | F-009: push-notifications | HU-001, HU-002, HU-003, HU-004 |
| RF-11.2 | Notificaciones Automáticas del Sistema | F-009: push-notifications | HU-005 |
| RF-12.1 | Aplicaciones de Marca Separadas | F-012: app-publishing | HU-001, HU-004 |
| RF-12.2 | Presentación en el App Store | F-012: app-publishing | HU-002, HU-003, HU-004 |
| RF-8.1 | Solicitar Ausencia | F-010: absence-management | HU-001, HU-002, HU-003 |
| RF-8.2 | Historial de Ausencias | F-010: absence-management | HU-004, HU-005, HU-006 |
