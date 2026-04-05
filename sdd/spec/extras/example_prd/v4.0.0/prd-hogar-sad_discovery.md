# Feature Discovery: CUIDEO — Aplicaciones Móviles Hogar & SAD
> PRD origen: prd-hogar-sad.md | Fecha: 2026-04-05
> Generado por: wf-spec-discover

---

## Requisitos Funcionales identificados

> Los IDs de RF son los definidos explícitamente en el PRD. El PRD numera los requisitos como RF-1, RF-2... con sub-RFs numerados (RF-1.0, RF-1.1...). Se respetan los IDs originales.

| RF | Título | Sección PRD | Aplica a |
|----|--------|-------------|----------|
| RF-1 | Autenticación y Onboarding | §RF-1 | Ambos |
| RF-1.0 | Pantalla de Splash | §RF-1.0 | Ambos |
| RF-1.1 | Pantallas de Bienvenida (Onboarding) | §RF-1.1 | Ambos |
| RF-1.2 | Registro de Usuario | §RF-1.2 | Hogar (alta directa) / SAD (activación por email) |
| RF-1.3 | Inicio de Sesión | §RF-1.3 | Ambos |
| RF-1.4 | Recuperación de Acceso | §RF-1.4 | Ambos |
| RF-1.5 | Gestión del Token de Sesión | §RF-1.5 | Ambos |
| RF-1.6 | Cierre de Sesión | §RF-1.6 | Ambos |
| RF-1.7 | Pantalla Sin Permisos / Acceso Revocado | §RF-1.7 | SAD |
| RF-2 | Panel Principal | §RF-2 | Ambos |
| RF-2.1 | Accesos Directos del Panel (Home) | §RF-2.1 | Ambos |
| RF-2.2 | Tablón de Anuncios / Comunicados | §RF-2.2 | Ambos |
| RF-2.3 | Mensajes del Sistema | §RF-2.3 | Ambos |
| RF-3 | Mis Servicios (Gestión de Servicios) | §RF-3 | SAD |
| RF-3.1 | Listado de Servicios | §RF-3.1 | SAD |
| RF-3.2 | Detalle del Servicio | §RF-3.2 | SAD |
| RF-3.3 | Notas de Servicio | §RF-3.3 | SAD |
| RF-3.4 | Llamadas de Servicio (Llamamientos) | §RF-3.4 | SAD |
| RF-3.5 | Historial de Servicios | §RF-3.5 | SAD |
| RF-3.7 | Nuevo Servicio Asignado (Contratos Indefinidos) | §RF-3.7 | SAD |
| RF-4 | Control Horario (Seguimiento de Tiempo) | §RF-4 | SAD |
| RF-4.1 | Fichar Entrada/Salida | §RF-4.1 | SAD |
| RF-4.2 | Historial de Seguimiento de Tiempo | §RF-4.2 | SAD |
| RF-5 | Incidencias | §RF-5 | SAD |
| RF-5.1 | Reportar Incidencia | §RF-5.1 | SAD |
| RF-5.2 | Historial de Incidencias | §RF-5.2 | SAD |
| RF-6 | Ofertas (Ofertas de Trabajo) | §RF-6 | Hogar |
| RF-6.1 | Navegar Ofertas | §RF-6.1 | Hogar |
| RF-6.2 | Solicitar Oferta | §RF-6.2 | Hogar |
| RF-6.3 | Mis Solicitudes | §RF-6.3 | Hogar |
| RF-7 | Mi Disponibilidad (Gestión de Disponibilidad) | §RF-7 | Ambos |
| RF-7.1 | Calendario de Disponibilidad | §RF-7.1 | Ambos |
| RF-8 | Mis Ausencias (Gestión de Ausencias) | §RF-8 | SAD |
| RF-8.1 | Solicitar Ausencia | §RF-8.1 | SAD |
| RF-8.2 | Historial de Ausencias | §RF-8.2 | SAD |
| RF-9 | Perfil (Gestión de Perfil) | §RF-9 | Ambos |
| RF-9.1 | Ver y Editar Perfil | §RF-9.1 | Ambos |
| RF-9.2 | Foto de Perfil | §RF-9.2 | Ambos |
| RF-9.3 | Documentos | §RF-9.3 | Ambos |
| RF-9.4 | Firma Digital | §RF-9.4 | Ambos |
| RF-9.5 | Estado del Contrato | §RF-9.5 | SAD |
| RF-10 | Comunicación | §RF-10 | Ambos |
| RF-10.1 | Inicio de Nueva Conversación | §RF-10.1 | Ambos |
| RF-10.2 | Listado de Conversaciones | §RF-10.2 | Ambos |
| RF-10.3 | Hilo de Conversación | §RF-10.3 | Ambos |
| RF-11 | Notificaciones Push | §RF-11 | Ambos |
| RF-11.1 | Entrega de Notificaciones Push | §RF-11.1 | Ambos |
| RF-11.2 | Notificaciones Automáticas del Sistema | §RF-11.2 | Ambos |
| RF-12 | Publicación de la Aplicación | §RF-12 | Ambos (infra) |
| RF-12.1 | Aplicaciones de Marca Separadas | §RF-12.1 | Ambos (infra) |
| RF-12.2 | Presentación en el App Store | §RF-12.2 | Ambos (infra) |

> Nota: RF-3.6 (Seguimiento PIA) aparece en el PRD como eliminado (`~~RF-3.6~~`) y no se incluye en el discovery.

---

## Features identificadas

### F-001: auth-and-onboarding
- **Descripción**: Gestión completa del ciclo de acceso a la app: splash, registro, login, recuperación de contraseña, sesión y cierre de sesión, incluyendo el flujo de onboarding inicial y el estado de acceso revocado.
- **Actor principal**: Trabajadora (Hogar o SAD)
- **Objetivo del actor**: Acceder a la aplicación de forma segura y conocer sus funcionalidades principales en el primer uso
- **Journeys anticipados**:
  - Journey 1 (Hogar): registro con email + contraseña → onboarding → home
  - Journey 2 (SAD): activación de cuenta por email → establecer contraseña → login → onboarding → home
  - Journey 3 (Ambos): login con sesión activa → saltar login → home (inicio automático)
  - Journey 4 (Ambos): token caducado/revocado → redirigir a login
  - Journey 5 (SAD): cuenta revocada → pantalla de acceso denegado
  - Journey 6 (Ambos): olvidé contraseña → email de recuperación → restablecimiento
- **CAs derivables**:
  - Splash muestra logo durante 2-3s y redirige según estado de sesión
  - Registro Hogar valida email + contraseña con requisitos mínimos
  - Activación SAD requiere enlace de email para establecer contraseña
  - Login mantiene sesión sin re-autenticar si el token Sanctum es válido
  - Token caducado o respuesta 401 redirige al login sin reintentar
  - Onboarding se muestra solo en el primer uso y solicita permiso de push tras primer login
  - Cierre de sesión borra tokens y redirige al login
  - Acceso revocado (SAD) muestra pantalla informativa sin acceso a la app
- **Scope (RFs)**: RF-1.0, RF-1.1, RF-1.2, RF-1.3, RF-1.4, RF-1.5, RF-1.6, RF-1.7
- **Scope (secciones PRD)**: §RF-1 completo, §Alcance (pantalla splash, registro/autenticación, sesión)
- **Modelos propios**: AuthToken, Session, OnboardingState
- **Modelos compartidos (owner)**: Worker ← esta feature crea la entidad Worker al registrarse
- **Modelos compartidos (ref)**: DeviceRegistration (owner: F-009: push-notifications)

---

### F-002: home-dashboard
- **Descripción**: Panel principal de la app con accesos directos, anuncios, mensajes del sistema y visualización priorizada de entidades relevantes según el perfil (servicios activos, llamamientos pendientes, documentos por firmar).
- **Actor principal**: Trabajadora (Hogar o SAD)
- **Objetivo del actor**: Acceder rápidamente a la información y acciones más relevantes del día
- **Journeys anticipados**:
  - Journey 1 (Ambos): abrir app → ver home con accesos directos, anuncios recientes y badges de pendientes
  - Journey 2 (SAD): ver llamamiento pendiente en home → navegar al detalle del llamamiento
  - Journey 3 (SAD): ver servicios activos/próximos en home → navegar al detalle del servicio
  - Journey 4 (Ambos): ver y leer un comunicado del tablón → marcarlo como leído
  - Journey 5 (Ambos): recibir y leer un mensaje del sistema → borrarlo
- **CAs derivables**:
  - Home SAD muestra servicio activo + siguiente servicio con enlace "Ver más servicios"
  - Llamamiento pendiente visible con cuenta atrás; CTA navega al detalle (nunca acepta/rechaza desde home)
  - Badge visible para documentación pendiente de firma
  - Tablón diferencia contenidos fijos de comunicaciones variables; marcar como leído al abrir
  - Mensajes del sistema con dos niveles de criticidad (alta/normal); opción de borrar
  - Dashboard cargado con una sola llamada a la API (/workers/dashboard)
  - Pull-to-refresh actualiza datos del home
- **Scope (RFs)**: RF-2.1, RF-2.2, RF-2.3
- **Scope (secciones PRD)**: §RF-2 completo, §Alcance (panel principal, tablón de anuncios, mensajes sistema)
- **Modelos propios**: Announcement, SystemMessage
- **Modelos compartidos (ref)**: Worker (owner: F-001), Service (owner: F-003), ServiceCall (owner: F-003), Document (owner: F-008)

---

### F-003: service-management
- **Descripción**: Gestión completa de los servicios asignados a trabajadoras SAD: listado con estados, detalle del servicio, notas, gestión de llamamientos con firma digital y notificación de nuevo servicio asignado.
- **Actor principal**: Trabajadora SAD (Felizvita)
- **Objetivo del actor**: Conocer sus servicios asignados, gestionar la comunicación del servicio y responder a llamamientos
- **Journeys anticipados**:
  - Journey 1: ver listado de servicios → abrir detalle → ver plan de cuidados y tareas
  - Journey 2: recibir llamamiento → abrir detalle → firmar digitalmente para aceptar o rechazar con motivo
  - Journey 3: añadir nota a un servicio con adjunto → nota visible para coordinación inmediatamente
  - Journey 4 (indefinidos): recibir notificación de nuevo servicio asignado → abrir detalle → registrar "visto"
  - Journey 5: ver historial completo de llamamientos con resultados
- **CAs derivables**:
  - Servicios agrupados por estado: Activos, Próximos, Completados
  - Detalle muestra dirección como texto clickable que abre Maps (sin mapa embebido)
  - Visibilidad de campos del cliente controlable desde backoffice (RGPD)
  - Llamamiento: aceptar/rechazar solo desde detalle; navegación bloqueada hasta decisión; ambas acciones requieren firma digital
  - Llamamiento expira tras tiempo límite configurable; estados: pendiente, aceptado, rechazado, caducado, desactivado
  - Notas CRUD con adjuntos (categorías: Evolución, Tareas, Incidencias, Otras); borrado suave
  - Nuevo servicio asignado (indefinidos): notificación push + acknowledge + opción de generar incidencia
  - Historial de servicios completados con total de horas por servicio y filtro por fecha
- **Scope (RFs)**: RF-3.1, RF-3.2, RF-3.3, RF-3.4, RF-3.5, RF-3.7
- **Scope (secciones PRD)**: §RF-3 completo (excepto RF-3.6 eliminado)
- **Modelos propios**: ServiceCall, ServiceNote, ServiceHistory
- **Modelos compartidos (owner)**: Service ← esta feature define la entidad central Service con su CRUD completo
- **Modelos compartidos (ref)**: Worker (owner: F-001), Signature (owner: F-008), Incident (owner: F-005)

---

### F-004: time-tracking
- **Descripción**: Control horario de las trabajadoras SAD: fichar entrada y salida en servicios con geolocalización, estados dinámicos del botón de fichaje y visualización del historial de registros.
- **Actor principal**: Trabajadora SAD (Felizvita)
- **Objetivo del actor**: Registrar el inicio y fin de cada servicio de forma precisa y verificada por ubicación
- **Journeys anticipados**:
  - Journey 1: recibir notificación de apertura de ventana de fichaje → fichar entrada desde home/tab/detalle de servicio
  - Journey 2: finalizar servicio → fichar salida con confirmación → ver resumen de tiempo trabajado
  - Journey 3: ver historial de fichajes de un mes concreto filtrado por servicio
  - Journey 4: no poder fichar (problema de ubicación) → reportar incidencia de fichaje desde la pantalla de fichaje
- **CAs derivables**:
  - Botón de fichaje activo 30 minutos antes del inicio; estados: "Disponible en X min", "Fichar entrada", "Fichada · en servicio", "Fichar salida", "Servicio finalizado"
  - Geolocalización capturada en entrada y salida; advertencia si precisión < 50m pero sin bloqueo
  - No se permite fichaje manual desde la app; correcciones solo desde backoffice
  - Warning visible (no bloqueante) si no se ficha salida tras finalizar el servicio
  - Historial agrupado por servicio y por días; muestra fecha, hora entrada, hora salida, duración
  - No se muestran horas extra ni diferencias respecto a horas contratadas
- **Scope (RFs)**: RF-4.1, RF-4.2
- **Scope (secciones PRD)**: §RF-4 completo, §Alcance (seguimiento de tiempo)
- **Modelos propios**: TimeEntry, TimeTrackingStatus
- **Modelos compartidos (ref)**: Service (owner: F-003), Worker (owner: F-001), Incident (owner: F-005)

---

### F-005: incident-reporting
- **Descripción**: Reporte y seguimiento de incidencias del servicio o del usuario atendido por trabajadoras SAD, con categorización por tipo, adjuntos y seguimiento de estado.
- **Actor principal**: Trabajadora SAD (Felizvita)
- **Objetivo del actor**: Comunicar a coordinación incidencias ocurridas durante la prestación del servicio
- **Journeys anticipados**:
  - Journey 1: detectar incidencia durante un servicio → reportar desde detalle de servicio o módulo de incidencias → adjuntar fotos
  - Journey 2: ver historial de incidencias propias → filtrar por estado → consultar respuesta de coordinación
  - Journey 3 (fichaje): no poder asistir al servicio → reportar incidencia de tipo "No asistencia" desde pantalla de fichaje
- **CAs derivables**:
  - Tipos de incidencia predefinidos: Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros
  - Descripción obligatoria (mínimo 20 caracteres); fotos opcionales (máx. 5); documentos opcionales (máx. 3)
  - Compresión automática de imágenes; tamaño estimado antes de enviar
  - Incidencia inmediatamente visible para coordinadoras tras envío
  - Historial con estados: Reportada, En revisión, Resuelta, Cerrada; filtros por estado, fechas y búsqueda
  - Ver comentarios/respuestas de coordinación en el detalle de la incidencia
- **Scope (RFs)**: RF-5.1, RF-5.2
- **Scope (secciones PRD)**: §RF-5 completo, §Alcance (reporte de incidencias)
- **Modelos propios**: Incident, IncidentAttachment
- **Modelos compartidos (ref)**: Service (owner: F-003), Worker (owner: F-001)

---

### F-006: job-offers
- **Descripción**: Navegación, filtrado, solicitud y seguimiento de ofertas de trabajo para trabajadoras del perfil Hogar (CUIDEO).
- **Actor principal**: Trabajadora Hogar (CUIDEO)
- **Objetivo del actor**: Encontrar y solicitar ofertas de trabajo que se ajusten a su disponibilidad y zona
- **Journeys anticipados**:
  - Journey 1: navegar ofertas con filtros → abrir detalle → aplicar a oferta con confirmación
  - Journey 2: ver mis solicitudes → consultar estado → retirar solicitud pendiente
  - Journey 3: recibir notificación de cambio de estado en solicitud → ver detalle
- **CAs derivables**:
  - Listado de ofertas con tarjetas: título, ubicación, horario, tarifa; filtros por zona, horario, fecha; ordenación por recientes/ubicación/tarifa
  - Insignia "Nuevo" para ofertas publicadas en últimas 48h; estado vacío si no hay coincidencias
  - Aplicar a oferta muestra diálogo de confirmación; previene solicitudes duplicadas
  - Solicitudes con estados: Pendiente, En revisión, Aceptada, Rechazada, Oferta cerrada
  - Retirar solicitud pendiente; notificación push en cambio de estado
  - Al aplicar, si perfil incompleto → advertencia con acceso directo a completar campos obligatorios
- **Scope (RFs)**: RF-6.1, RF-6.2, RF-6.3
- **Scope (secciones PRD)**: §RF-6 completo, §Alcance (solo perfil Hogar: ofertas)
- **Modelos propios**: JobOffer, JobApplication
- **Modelos compartidos (ref)**: Worker (owner: F-001)

---

### F-007: availability-management
- **Descripción**: Declaración y gestión de disponibilidad horaria semanal para ambos perfiles mediante un calendario con slots de disponibilidad/no disponibilidad y franjas rápidas predefinidas.
- **Actor principal**: Trabajadora (Hogar o SAD)
- **Objetivo del actor**: Declarar su disponibilidad horaria para que el sistema pueda asignarle servicios
- **Journeys anticipados**:
  - Journey 1: abrir calendario semanal → seleccionar día → usar franja rápida (Mañana/Tarde/Noche/Interna/Finde) → slot creado automáticamente
  - Journey 2: seleccionar día → crear slot personalizado con hora inicio/fin y tipo (disponible/no disponible)
  - Journey 3: tocar slot existente → editarlo o eliminarlo
  - Journey 4: ver horas trabajadas vs horas de contrato en la cabecera
- **CAs derivables**:
  - Vista semanal con bloques de color diferenciados por tipo: Disponible, No disponible, Activa (solo lectura)
  - Franjas rápidas predefinidas: Mañana, Tarde, Noche, Interna, Finde (sin Madrugada)
  - Slot personalizado con time picker y tipo; se permiten solapamientos entre tipos distintos; no se permiten solapamientos entre slots del mismo tipo
  - Slots "Activa" (de planificación) son de solo lectura y se muestran solapados sobre franjas disponibles
  - Cambios guardados de forma inmediata al confirmar cada slot (sin botón "guardar todo")
  - Notificación de recordatorio si la disponibilidad no se actualiza en 30 días
- **Scope (RFs)**: RF-7.1
- **Scope (secciones PRD)**: §RF-7 completo, §Alcance (gestión de disponibilidad)
- **Modelos propios**: AvailabilitySlot, UnavailabilitySlot
- **Modelos compartidos (ref)**: Worker (owner: F-001)

---

### F-008: profile-management
- **Descripción**: Visualización y edición del perfil personal y profesional, gestión de documentos personales y laborales, firma digital y estado del contrato.
- **Actor principal**: Trabajadora (Hogar o SAD)
- **Objetivo del actor**: Mantener su perfil actualizado, gestionar su documentación y firmar documentos laborales
- **Journeys anticipados**:
  - Journey 1: ver perfil → editar dirección de domicilio → guardar
  - Journey 2: subir foto de perfil desde galería/cámara → recortar → confirmar subida
  - Journey 3: acceder a documentos → ver documentación laboral (nómina) → descargar PDF
  - Journey 4: recibir aviso de documento pendiente de firma → abrir documento → firmar digitalmente → confirmar
  - Journey 5: subir documento personal (DNI/NIE) → seleccionar tipo → adjuntar archivo → confirmar
  - Journey 6 (SAD): ver estado del contrato con tipo, fecha inicio y enlace al PDF
  - Journey 7 (Hogar): intentar aplicar a oferta con perfil incompleto → ver advertencia con campos obligatorios
- **CAs derivables**:
  - Perfil organizado en secciones: Personal, Profesional, Educación, Idiomas, Contrato (SAD)
  - Datos core de solo lectura; dirección de domicilio editable; campos editables con botón de edición por sección
  - Indicador de porcentaje de completitud del perfil visible en home (Hogar) y en perfil
  - Documentación personal: subir y reemplazar (no eliminar); laborales: solo consultar, descargar y firmar
  - Firma digital: lienzo táctil para dibujar firma; guardar como PNG; reutilizable en futuras firmas
  - DNI/NIE con fecha de vencimiento y flujo de propuesta de cambio con documento justificativo
- **Scope (RFs)**: RF-9.1, RF-9.2, RF-9.3, RF-9.4, RF-9.5
- **Scope (secciones PRD)**: §RF-9 completo, §Alcance (perfil, documentos, firma digital)
- **Modelos propios**: Document, Signature, ContractInfo
- **Modelos compartidos (owner)**: Worker (perfil) ← actualización de datos del perfil; comparte ownership con F-001 (creación)
- **Modelos compartidos (ref)**: Worker (owner: F-001)

---

### F-009: push-notifications
- **Descripción**: Registro del dispositivo para push, recepción de notificaciones con deeplinks y visualización del historial de notificaciones recibidas.
- **Actor principal**: Trabajadora (Hogar o SAD)
- **Objetivo del actor**: Recibir alertas relevantes del sistema en tiempo real y acceder directamente a la sección correspondiente
- **Journeys anticipados**:
  - Journey 1: primer login → solicitud de permiso de notificaciones → registro de token FCM
  - Journey 2: recibir notificación en segundo plano → tocar → abrir app en pantalla específica (deeplink)
  - Journey 3: consultar historial de notificaciones recibidas → marcar todas como leídas
  - Journey 4: actualización automática del token FCM al renovarse
- **CAs derivables**:
  - Permiso de notificaciones solicitado después del primer login y antes del onboarding
  - Token FCM registrado en backend; actualizado cuando cambia; dispositivo dado de baja al cerrar sesión
  - Notificaciones en primer plano mostradas como alerta in-app; en segundo plano/apagada como notificación del sistema
  - Deeplinks a: mensaje, conversación cerrada, llamamiento, cambio de estado de solicitud, cambio de estado de ausencia, apertura de fichaje, servicio próximo, documento caducando, incidencia actualizada, nuevo comunicado
  - Recordatorios automáticos del sistema (sin acción desde la app): disponibilidad no actualizada en 30 días, caducidad de documento, recordatorio de servicio, recordatorio de fichaje
- **Scope (RFs)**: RF-11.1, RF-11.2
- **Scope (secciones PRD)**: §RF-11 completo, §Alcance (notificaciones push)
- **Modelos propios**: DeviceRegistration, NotificationRecord
- **Modelos compartidos (ref)**: Worker (owner: F-001)

---

### F-010: absence-management
- **Descripción**: Solicitud y seguimiento del historial de ausencias (vacaciones, bajas, permisos) con adjuntos justificativos y visualización de saldos por tipo para trabajadoras SAD.
- **Actor principal**: Trabajadora SAD (Felizvita)
- **Objetivo del actor**: Solicitar permisos y ausencias y hacer seguimiento de su estado y saldo disponible
- **Journeys anticipados**:
  - Journey 1: solicitar vacaciones → seleccionar tipo, rango de fechas → adjuntar certificado (si aplica) → enviar para aprobación
  - Journey 2: ver historial de ausencias → filtrar por tipo/estado/año → consultar comentarios de coordinación
  - Journey 3: cancelar solicitud de ausencia pendiente
  - Journey 4: recibir notificación de cambio de estado de la ausencia → ver detalle
- **CAs derivables**:
  - Tipos de ausencia: Vacaciones, Permiso personal, Baja médica, Baja voluntaria, Asuntos propios, Otros
  - Advertencia si las fechas solicitadas entran en conflicto con servicios asignados
  - Saldo de vacaciones disponible visible antes de enviar; contadores por tipo (asignado, utilizado, pendiente, disponible)
  - Historial con estados: Pendiente, Aprobada, Rechazada, Cancelada; filtros por estado, tipo y año
  - Certificado médico obligatorio para baja médica de más de 3 días
  - Opción de medio día para fechas de inicio/fin; cómputo por días naturales (pendiente confirmar con legal)
- **Scope (RFs)**: RF-8.1, RF-8.2
- **Scope (secciones PRD)**: §RF-8 completo, §Alcance (solicitudes de ausencia, saldo vacaciones)
- **Modelos propios**: AbsenceRequest, VacationBalance
- **Modelos compartidos (ref)**: Worker (owner: F-001), Service (owner: F-003)

---

### F-011: communication
- **Descripción**: Chat de la trabajadora con el equipo de Coordinación/back-office, con selección de asunto predefinido para enrutado interno, soporte de contexto de servicio/oferta y gestión del historial de conversaciones.
- **Actor principal**: Trabajadora (Hogar o SAD)
- **Objetivo del actor**: Comunicarse con coordinación de forma directa y ordenada para gestionar consultas y situaciones del trabajo
- **Journeys anticipados**:
  - Journey 1: iniciar nueva conversación → seleccionar asunto → escribir primer mensaje → enviar (con contexto de servicio u oferta opcional)
  - Journey 2: ver listado de conversaciones → abrir hilo → leer mensajes → responder (si conversación abierta)
  - Journey 3: abrir conversación cerrada → leer historial en modo lectura
  - Journey 4: buscar conversación → borrar conversación
  - Journey 5: recibir mensaje nuevo → notificación push → deeplink al hilo
- **CAs derivables**:
  - Asuntos predefinidos al crear conversación: Vacaciones/Ausencia, Nómina/Facturación, Sobre un servicio, Documentación, Consulta general, Otros
  - Conversaciones abiertas permiten escribir; cerradas muestran "Conversación cerrada" y modo solo lectura
  - Mensajes en tiempo real via Firebase Realtime Database; paginación al cargar mensajes anteriores
  - Estado de entrega/lectura para mensajes enviados; desplazamiento automático al último mensaje
  - Contexto enlazable al mensaje (servicio u oferta relacionada)
  - Buscar y borrar conversaciones con confirmación
- **Scope (RFs)**: RF-10.1, RF-10.2, RF-10.3
- **Scope (secciones PRD)**: §RF-10 completo, §Alcance (chat con coordinación)
- **Modelos propios**: Conversation, Message
- **Modelos compartidos (ref)**: Worker (owner: F-001), Service (owner: F-003), JobOffer (owner: F-006)

---

### F-012: app-publishing
- **Descripción**: Configuración, compilación y publicación de las dos aplicaciones de marca (CUIDEO Hogar y Felizvita SAD) en App Store y Google Play desde el codebase KMM compartido.
- **Actor principal**: Equipo de desarrollo/DevOps (actor técnico)
- **Objetivo del actor**: Publicar y mantener ambas apps en las tiendas oficiales con sus respectivos branding, bundle IDs y cumplimiento normativo
- **Journeys anticipados**:
  - Journey 1 (técnico): configurar flavors/targets de build → compilar app CUIDEO (azul) y Felizvita (verde) desde mismo codebase
  - Journey 2 (técnico): preparar metadatos de store → enviar para revisión en App Store Connect y Google Play Console
  - Journey 3 (técnico): preparar documentación de cumplimiento RGPD para las stores
- **CAs derivables**:
  - CUIDEO: bundle ID es.cuideo.hogar, color azul, solo funcionalidades Hogar; soporta iOS 16+ y Android 8+
  - Felizvita: bundle ID es.cuideo.felizvita, color verde, solo funcionalidades SAD; mismos requisitos de SO
  - Metadatos completos en ambas stores: descripción, capturas, política de privacidad, URL de soporte
  - Cumplimiento RGPD: documentación de datos, justificación de permisos de ubicación, declaraciones de SDKs de terceros (Firebase)
- **Scope (RFs)**: RF-12.1, RF-12.2
- **Scope (secciones PRD)**: §RF-12 completo, §Alcance (lanzamiento MVP iOS y Android)
- **Modelos propios**: (sin modelos de dominio — feature de infraestructura/release)
- **Modelos compartidos (ref)**: (sin dependencias de dominio)

---

## Tabla de shared models

| Modelo | Feature Owner | Features que lo referencian | Criterio de asignación |
|--------|---------------|-----------------------------|------------------------|
| Worker | F-001: auth-and-onboarding | F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-009, F-010, F-011 | Creación explícita: F-001 crea la entidad Worker al registrar/activar la cuenta |
| Service | F-003: service-management | F-002, F-004, F-005, F-010, F-011 | CRUD completo: F-003 gestiona el ciclo de vida completo de los servicios |
| Document | F-008: profile-management | F-002 (badge documentos pendientes) | CRUD completo: F-008 gestiona subida, reemplazo, firma y visualización de documentos |
| Signature | F-008: profile-management | F-003 (llamamientos con firma) | Creación explícita: F-008 crea y almacena la firma digital del perfil |
| JobOffer | F-006: job-offers | F-011 (enlace contexto conversación) | Creación explícita y CRUD: F-006 define el modelo y sus operaciones |
| Conversation | F-011: communication | F-002 (badge mensajes no leídos) | CRUD completo: F-011 gestiona el ciclo de vida de las conversaciones |
| DeviceRegistration | F-009: push-notifications | F-001 (registro post-login) | Creación explícita: F-009 gestiona el registro del dispositivo para push |

---

## Trazabilidad RF → Feature

| RF | Título RF | Feature asignada |
|----|-----------|------------------|
| RF-1.0 | Pantalla de Splash | F-001: auth-and-onboarding |
| RF-1.1 | Pantallas de Bienvenida (Onboarding) | F-001: auth-and-onboarding |
| RF-1.2 | Registro de Usuario | F-001: auth-and-onboarding |
| RF-1.3 | Inicio de Sesión | F-001: auth-and-onboarding |
| RF-1.4 | Recuperación de Acceso | F-001: auth-and-onboarding |
| RF-1.5 | Gestión del Token de Sesión | F-001: auth-and-onboarding |
| RF-1.6 | Cierre de Sesión | F-001: auth-and-onboarding |
| RF-1.7 | Pantalla Sin Permisos / Acceso Revocado | F-001: auth-and-onboarding |
| RF-2.1 | Accesos Directos del Panel (Home) | F-002: home-dashboard |
| RF-2.2 | Tablón de Anuncios / Comunicados | F-002: home-dashboard |
| RF-2.3 | Mensajes del Sistema | F-002: home-dashboard |
| RF-3.1 | Listado de Servicios | F-003: service-management |
| RF-3.2 | Detalle del Servicio | F-003: service-management |
| RF-3.3 | Notas de Servicio | F-003: service-management |
| RF-3.4 | Llamadas de Servicio (Llamamientos) | F-003: service-management |
| RF-3.5 | Historial de Servicios | F-003: service-management |
| RF-3.7 | Nuevo Servicio Asignado (Contratos Indefinidos) | F-003: service-management |
| RF-4.1 | Fichar Entrada/Salida | F-004: time-tracking |
| RF-4.2 | Historial de Seguimiento de Tiempo | F-004: time-tracking |
| RF-5.1 | Reportar Incidencia | F-005: incident-reporting |
| RF-5.2 | Historial de Incidencias | F-005: incident-reporting |
| RF-6.1 | Navegar Ofertas | F-006: job-offers |
| RF-6.2 | Solicitar Oferta | F-006: job-offers |
| RF-6.3 | Mis Solicitudes | F-006: job-offers |
| RF-7.1 | Calendario de Disponibilidad | F-007: availability-management |
| RF-8.1 | Solicitar Ausencia | F-010: absence-management |
| RF-8.2 | Historial de Ausencias | F-010: absence-management |
| RF-9.1 | Ver y Editar Perfil | F-008: profile-management |
| RF-9.2 | Foto de Perfil | F-008: profile-management |
| RF-9.3 | Documentos | F-008: profile-management |
| RF-9.4 | Firma Digital | F-008: profile-management |
| RF-9.5 | Estado del Contrato | F-008: profile-management |
| RF-10.1 | Inicio de Nueva Conversación | F-011: communication |
| RF-10.2 | Listado de Conversaciones | F-011: communication |
| RF-10.3 | Hilo de Conversación | F-011: communication |
| RF-11.1 | Entrega de Notificaciones Push | F-009: push-notifications |
| RF-11.2 | Notificaciones Automáticas del Sistema | F-009: push-notifications |
| RF-12.1 | Aplicaciones de Marca Separadas | F-012: app-publishing |
| RF-12.2 | Presentación en el App Store | F-012: app-publishing |

---

## Decisiones de merge

No se realizaron merges. Todas las candidatas identificadas cumplen los 3 criterios de validación.

> Nota sobre F-012 (app-publishing): Esta feature no tiene un actor usuaria final — su actor es el equipo técnico. Se decidió mantenerla como feature separada en lugar de fusionarla con otra porque sus CAs son verificables y diferenciados (configuración de builds, metadatos de stores, cumplimiento RGPD), y su scope en el PRD (§RF-12 completo) es explícito. Sin embargo, es la única feature sin modelos de dominio y puede ser tratada como "feature de infraestructura/release" al planificar los specs.

---

## Siguiente paso

Para generar el spec de cada feature individualmente:
```
/wf-spec-fast-track prd-hogar-sad.md --scope-from prd-hogar-sad_discovery.md --feature F-001
```

Para generar todos los specs en paralelo (flujo automático):
```
/wf-spec-features-first prd-hogar-sad.md
```

Para el flujo completo spec-first (spec monolítico):
```
/wf-spec-analyze prd-hogar-sad.md
```
