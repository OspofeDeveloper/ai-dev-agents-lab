# Feature Discovery: Aplicaciones Moviles CUIDEO - Hogar & SAD
> PRD origen: prd-hogar-sad.md | Fecha: 2026-04-05
> Generado por: wf-spec-discover
> Analysis utilizado: prd-hogar-sad_analysis.md

---

## Requisitos Funcionales identificados

| RF | Titulo | Seccion PRD |
|----|--------|-------------|
| RF-1.0 | Pantalla de Splash | RF-1: Autenticacion y Onboarding |
| RF-1.1 | Pantallas de Bienvenida | RF-1: Autenticacion y Onboarding |
| RF-1.2 | Registro de Usuario | RF-1: Autenticacion y Onboarding |
| RF-1.3 | Inicio de Sesion | RF-1: Autenticacion y Onboarding |
| RF-1.4 | Recuperacion de Acceso | RF-1: Autenticacion y Onboarding |
| RF-1.5 | Gestion del Token de Sesion | RF-1: Autenticacion y Onboarding |
| RF-1.6 | Cierre de Sesion | RF-1: Autenticacion y Onboarding |
| RF-1.7 | Pantalla Sin Permisos / Acceso Revocado | RF-1: Autenticacion y Onboarding |
| RF-2.1 | Accesos Directos del Panel | RF-2: Panel Principal |
| RF-2.2 | Tablon de Anuncios / Comunicados | RF-2: Panel Principal |
| RF-2.3 | Mensajes del Sistema | RF-2: Panel Principal |
| RF-3.1 | Listado de Servicios | RF-3: Mis Servicios |
| RF-3.2 | Detalle del Servicio | RF-3: Mis Servicios |
| RF-3.3 | Notas de Servicio | RF-3: Mis Servicios |
| RF-3.4 | Llamadas de Servicio (Llamamientos) | RF-3: Mis Servicios |
| RF-3.5 | Historial de Servicios | RF-3: Mis Servicios |
| RF-3.7 | Nuevo Servicio Asignado (Contratos Indefinidos) | RF-3: Mis Servicios |
| RF-4.1 | Fichar Entrada/Salida | RF-4: Control Horario |
| RF-4.2 | Historial de Seguimiento de Tiempo | RF-4: Control Horario |
| RF-5.1 | Reportar Incidencia | RF-5: Incidencias |
| RF-5.2 | Historial de Incidencias | RF-5: Incidencias |
| RF-6.1 | Navegar Ofertas | RF-6: Ofertas |
| RF-6.2 | Solicitar Oferta | RF-6: Ofertas |
| RF-6.3 | Mis solicitudes | RF-6: Ofertas |
| RF-7.1 | Calendario de Disponibilidad | RF-7: Mi Disponibilidad |
| RF-8.1 | Solicitar Ausencia | RF-8: Mis Ausencias |
| RF-8.2 | Historial de Ausencias | RF-8: Mis Ausencias |
| RF-9.1 | Ver y Editar Perfil | RF-9: Perfil |
| RF-9.2 | Foto de Perfil | RF-9: Perfil |
| RF-9.3 | Documentos | RF-9: Perfil |
| RF-9.4 | Firma Digital | RF-9: Perfil |
| RF-9.5 | Estado del Contrato | RF-9: Perfil |
| RF-10.1 | Inicio de Nueva Conversacion | RF-10: Comunicacion |
| RF-10.2 | Listado de Conversaciones | RF-10: Comunicacion |
| RF-10.3 | Hilo de Conversacion | RF-10: Comunicacion |
| RF-11.1 | Entrega de Notificaciones Push | RF-11: Notificaciones |
| RF-11.2 | Notificaciones Automaticas del Sistema | RF-11: Notificaciones |

> **Nota:** RF-3.6 (Seguimiento PIA) esta eliminado en el PRD original. RF-12 (Publicacion de la Aplicacion) se excluye del discovery por ser funcionalidad de despliegue/implementacion, no funcionalidad de usuario (confirmado por contaminacion [C-016] en el analysis).

---

## Features identificadas

### F-001: auth-and-onboarding
- **Descripcion**: Gestionar el ciclo de vida completo de autenticacion de la trabajadora: registro, inicio de sesion, recuperacion de acceso, onboarding, gestion de sesion y cierre de sesion
- **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
- **Objetivo del actor**: Acceder de forma segura a la aplicacion y completar el proceso de bienvenida inicial
- **Journeys anticipados**:
  1. Registro de nueva cuenta (solo Hogar: email + contrasena)
  2. Activacion de cuenta SAD (enlace de email desde backoffice, luego login con credenciales)
  3. Inicio de sesion con email y contrasena
  4. Recuperacion de acceso (olvido de contrasena)
  5. Onboarding post-login (pantallas de bienvenida + solicitud de permisos)
  6. Cierre de sesion
  7. Acceso revocado (cuenta suspendida/dada de baja, solo SAD)
- **CAs derivables**:
  1. La trabajadora Hogar completa el registro con email y contrasena y accede a la app
  2. La trabajadora inicia sesion y es redirigida al home correcto segun su perfil
  3. La trabajadora recupera el acceso a su cuenta estableciendo nueva contrasena
  4. La sesion se mantiene activa durante 30 dias sin requerir nuevo login
  5. El onboarding se muestra solo una vez tras el primer login
  6. Una cuenta revocada muestra la pantalla de acceso denegado sin permitir navegacion
  7. El cierre de sesion borra datos locales y redirige a la pantalla de login
- **Scope (RFs)**: RF-1.0, RF-1.1, RF-1.2, RF-1.3, RF-1.4, RF-1.5, RF-1.6, RF-1.7
- **Scope (secciones PRD)**: RF-1: Autenticacion y Onboarding (completa)
- **Modelos propios**: Sesion, CredencialesUsuaria
- **Modelos compartidos (owner)**: Usuaria (esta feature crea y autentica la entidad usuaria)
- **Modelos compartidos (ref)**: --

### F-002: dashboard-and-announcements
- **Descripcion**: Proporcionar la pantalla principal con accesos directos contextuales segun perfil, el tablon de anuncios/comunicados de la empresa y los mensajes del sistema
- **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
- **Objetivo del actor**: Acceder rapidamente a las funcionalidades principales y mantenerse informada de comunicaciones y avisos de la empresa
- **Journeys anticipados**:
  1. Acceder al home y ver accesos directos adaptados al perfil (Hogar vs SAD)
  2. Consultar el tablon de anuncios, leer un comunicado y marcarlo como leido
  3. Ver mensajes del sistema con diferenciacion de criticidad, leer y borrar mensajes
  4. Ver badges de acciones pendientes (mensajes no leidos, documentos por firmar)
- **CAs derivables**:
  1. La home SAD muestra servicio activo + fichaje como accion principal y adapta el contenido segun estado
  2. La home Hogar muestra accesos directos a Ofertas, Disponibilidad, Perfil, Comunicacion
  3. Los anuncios fijados por backoffice aparecen en la parte superior del tablon
  4. Los mensajes del sistema se muestran diferenciados por criticidad (alta primero, normal debajo)
  5. Tocar un comunicado lo abre en detalle y lo marca como leido automaticamente
  6. Los accesos directos muestran badges con contadores de acciones pendientes
- **Scope (RFs)**: RF-2.1, RF-2.2, RF-2.3
- **Scope (secciones PRD)**: RF-2: Panel Principal (completa)
- **Modelos propios**: Anuncio, MensajeSistema
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Usuaria (owner: F-001), Servicio (owner: F-003), Llamamiento (owner: F-004)

### F-003: service-management
- **Descripcion**: Gestionar los servicios asignados a la trabajadora SAD: listado, detalle con informacion del cliente y ubicacion, notas de servicio, historial de servicios completados y recepcion de nuevos servicios asignados (contratos indefinidos)
- **Actor principal**: Trabajadora SAD
- **Objetivo del actor**: Consultar y gestionar toda la informacion de sus servicios asignados de forma centralizada
- **Journeys anticipados**:
  1. Consultar el listado de servicios agrupados por estado (activos, proximos, completados)
  2. Ver el detalle completo de un servicio (cliente, ubicacion, plan de cuidados, tareas)
  3. Anadir una nota de servicio con adjuntos y consultarla posteriormente
  4. Consultar el historial de servicios completados con horas trabajadas
  5. Recibir notificacion de nuevo servicio asignado (indefinidos), confirmar recepcion y generar incidencia si no puede atenderlo
- **CAs derivables**:
  1. Los servicios se listan agrupados por estado: Activos, Proximos, Completados
  2. El detalle del servicio muestra direccion clickable que abre la app de Maps del dispositivo
  3. La trabajadora anade una nota con adjuntos categorizada (Evolucion, Tareas, Incidencias, Otras)
  4. La trabajadora SAD con contrato indefinido confirma recepcion de un nuevo servicio asignado
  5. La visibilidad de campos del cliente es controlable desde backoffice
  6. El historial muestra total de horas trabajadas por servicio con filtros por fecha
- **Scope (RFs)**: RF-3.1, RF-3.2, RF-3.3, RF-3.5, RF-3.7
- **Scope (secciones PRD)**: RF-3: Mis Servicios (excepto RF-3.4 Llamamientos)
- **Modelos propios**: NotaServicio
- **Modelos compartidos (owner)**: Servicio (esta feature define y gestiona la entidad servicio con CRUD completo), Cliente (la informacion del cliente se muestra y gestiona como parte del servicio)
- **Modelos compartidos (ref)**: Usuaria (owner: F-001)

### F-004: service-calls
- **Descripcion**: Gestionar el ciclo completo de llamamientos: recibir ofertas de turnos, evaluarlas, y aceptar o rechazar con firma digital obligatoria dentro de un plazo limitado
- **Actor principal**: Trabajadora SAD (contrato fijo discontinuo)
- **Objetivo del actor**: Responder a los llamamientos de turnos disponibles de forma informada y dentro del plazo establecido
- **Journeys anticipados**:
  1. Recibir notificacion de llamamiento, acceder al detalle desde home
  2. Evaluar el llamamiento (informacion del servicio, ubicacion, urgencia, cuenta atras)
  3. Aceptar el llamamiento con firma digital
  4. Rechazar el llamamiento con motivo obligatorio y firma digital
  5. Ver llamamiento caducado o desactivado (aceptado por otra trabajadora)
- **CAs derivables**:
  1. El llamamiento pendiente se muestra con urgencia y cuenta atras en la home
  2. Una vez dentro del detalle del llamamiento, la navegacion queda bloqueada hasta que la trabajadora acepte o rechace
  3. La aceptacion requiere firma digital con copy legal claro e inequivoco
  4. El rechazo requiere seleccion obligatoria de motivo y firma digital
  5. Los llamamientos caducan automaticamente tras el tiempo limite configurado desde backoffice
  6. El historial completo de llamamientos (con resultado final) se muestra en la seccion de historial de servicios
- **Scope (RFs)**: RF-3.4
- **Scope (secciones PRD)**: RF-3.4: Llamadas de Servicio (Llamamientos)
- **Modelos propios**: --
- **Modelos compartidos (owner)**: Llamamiento (esta feature define y gestiona el ciclo de vida completo del llamamiento)
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Usuaria (owner: F-001), FirmaDigital (owner: F-010)

### F-005: time-tracking
- **Descripcion**: Registrar la entrada y salida de la trabajadora SAD en cada servicio con captura de geolocalizacion, y consultar el historial de fichajes
- **Actor principal**: Trabajadora SAD
- **Objetivo del actor**: Fichar entrada y salida de cada servicio de forma fiable y consultar su historial de tiempo trabajado
- **Journeys anticipados**:
  1. Fichar entrada en un servicio activo (desde home, detalle del servicio o tab de fichaje) con captura GPS
  2. Fichar salida al finalizar el servicio con confirmacion y captura GPS
  3. Consultar el historial de fichajes agrupado por servicio y por dias
  4. Reportar incidencia de fichaje o solicitar ausencia desde la pantalla de fichaje
- **CAs derivables**:
  1. El fichaje captura coordenadas GPS y muestra advertencia si la precision es baja sin bloquear la accion
  2. El boton de fichaje de entrada se activa 30 minutos antes del inicio del servicio
  3. El boton de fichaje muestra estados dinamicos segun la hora (Disponible en X min, Fichar entrada, Fichada, Fichar salida, Servicio finalizado)
  4. Un warning visible recuerda fichar la salida si la trabajadora no lo ha hecho tras finalizar el servicio
  5. El historial muestra fecha, hora de entrada, hora de salida y duracion de cada registro
  6. No se muestran conteos de horas extra ni diferencias respecto a horas contratadas
- **Scope (RFs)**: RF-4.1, RF-4.2
- **Scope (secciones PRD)**: RF-4: Control Horario (completa)
- **Modelos propios**: RegistroFichaje
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Usuaria (owner: F-001)

### F-006: incident-reporting
- **Descripcion**: Reportar incidencias del servicio o del usuario atendido y consultar su historial con respuestas de coordinacion
- **Actor principal**: Trabajadora SAD
- **Objetivo del actor**: Comunicar incidencias relevantes del servicio a coordinacion y hacer seguimiento de su resolucion
- **Journeys anticipados**:
  1. Reportar una nueva incidencia seleccionando tipo, servicio, descripcion y adjuntos
  2. Consultar el historial de incidencias con filtros por estado y fecha
  3. Ver el detalle de una incidencia con comentarios/respuestas de coordinadoras
- **CAs derivables**:
  1. La trabajadora selecciona tipo de incidencia de lista predefinida (Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros)
  2. La descripcion es obligatoria con minimo 20 caracteres
  3. Se pueden adjuntar hasta 5 fotos y 3 documentos con compresion automatica de imagenes
  4. Las incidencias se listan en orden cronologico inverso con estados (Reportada, En revision, Resuelta, Cerrada)
  5. La trabajadora puede ver comentarios y respuestas de coordinadoras en el detalle
- **Scope (RFs)**: RF-5.1, RF-5.2
- **Scope (secciones PRD)**: RF-5: Incidencias (completa)
- **Modelos propios**: Incidencia, ComentarioIncidencia
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Usuaria (owner: F-001)

### F-007: job-offers
- **Descripcion**: Navegar las ofertas de trabajo disponibles, solicitar las que interesen y gestionar el seguimiento de las solicitudes presentadas
- **Actor principal**: Trabajadora Hogar
- **Objetivo del actor**: Encontrar oportunidades de trabajo adecuadas, aplicar a ellas y seguir el estado de sus solicitudes
- **Journeys anticipados**:
  1. Navegar las ofertas disponibles con filtros por zona, horario y fecha
  2. Ver el detalle completo de una oferta y solicitar con un toque
  3. Consultar el listado de solicitudes presentadas con su estado
  4. Retirar una solicitud pendiente
- **CAs derivables**:
  1. Las ofertas se listan en formato tarjeta con titulo, ubicacion, horario y tarifa
  2. Se pueden filtrar por codigo postal/zona, horario, rango de fecha y ordenar por recientes, cercania o tarifa
  3. La solicitud se envia con un solo toque e incluye automaticamente los datos del perfil
  4. Se previenen solicitudes duplicadas a la misma oferta
  5. Las solicitudes muestran estados: Pendiente, En revision, Aceptada, Rechazada, Oferta cerrada
  6. La trabajadora recibe notificacion push en cambio de estado de la solicitud
- **Scope (RFs)**: RF-6.1, RF-6.2, RF-6.3
- **Scope (secciones PRD)**: RF-6: Ofertas (completa)
- **Modelos propios**: Oferta, Solicitud
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Usuaria (owner: F-001)

### F-008: absence-management
- **Descripcion**: Solicitar ausencias (vacaciones, baja medica, permisos) con documentacion justificativa y consultar el historial con saldos de vacaciones
- **Actor principal**: Trabajadora SAD
- **Objetivo del actor**: Gestionar sus solicitudes de ausencia y conocer su saldo de vacaciones disponible
- **Journeys anticipados**:
  1. Solicitar una ausencia seleccionando tipo, fechas, motivo y adjuntando certificado si aplica
  2. Consultar el historial de ausencias con filtros por estado, tipo y ano
  3. Ver los contadores de vacaciones (asignacion anual, dias utilizados, pendientes de aprobacion, disponibles)
  4. Cancelar una solicitud de ausencia pendiente
- **CAs derivables**:
  1. La trabajadora selecciona tipo de ausencia (Vacaciones, Permiso personal, Baja medica, Baja voluntaria, Asuntos propios, Otros)
  2. Se muestra el saldo de vacaciones disponible antes de enviar la solicitud
  3. Se advierte si las fechas solicitadas entran en conflicto con servicios asignados
  4. Adjuntar certificado medico es obligatorio para baja medica superior a 3 dias
  5. Las ausencias muestran estados: Pendiente, Aprobada, Rechazada, Cancelada
- **Scope (RFs)**: RF-8.1, RF-8.2
- **Scope (secciones PRD)**: RF-8: Mis Ausencias (completa)
- **Modelos propios**: Ausencia, SaldoVacaciones
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Servicio (owner: F-003), Usuaria (owner: F-001)

### F-009: availability-management
- **Descripcion**: Gestionar la disponibilidad semanal de la trabajadora mediante un calendario con franjas rapidas predefinidas y slots personalizados, visualizando horas contratadas vs trabajadas
- **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
- **Objetivo del actor**: Declarar su disponibilidad horaria semanal para que el sistema pueda asignar servicios adecuadamente
- **Journeys anticipados**:
  1. Visualizar el calendario semanal con slots de disponibilidad, no disponibilidad y activos
  2. Crear un slot de disponibilidad usando una franja rapida predefinida (Manana, Tarde, Noche, Interna, Finde)
  3. Crear un slot personalizado con hora de inicio/fin y tipo (Disponible / No disponible)
  4. Editar o eliminar un slot existente de tipo Disponible o No disponible
  5. Consultar las horas contratadas vs trabajadas en la cabecera
- **CAs derivables**:
  1. La cabecera muestra horas trabajadas vs horas de contrato en formato prominente
  2. Los slots se muestran como bloques horarios con color diferenciado segun tipo (Disponible, No disponible, Activa)
  3. Se permiten solapamientos entre slots de distinto tipo pero no entre slots del mismo tipo
  4. Los slots de tipo Activa (servicios asignados por planificacion) son de solo lectura
  5. Los cambios se guardan de forma inmediata al confirmar cada slot
  6. Se muestra recordatorio si la disponibilidad no se actualiza en 30 dias
- **Scope (RFs)**: RF-7.1
- **Scope (secciones PRD)**: RF-7: Mi Disponibilidad (completa)
- **Modelos propios**: SlotDisponibilidad, FranjaRapida
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Usuaria (owner: F-001), Servicio (owner: F-003)

### F-010: profile-and-documents
- **Descripcion**: Gestionar la informacion personal y profesional de la trabajadora, subir y consultar documentos (personales y laborales), capturar firma digital y visualizar el estado del contrato
- **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
- **Objetivo del actor**: Mantener su perfil actualizado, gestionar su documentacion y firmar documentos cuando se requiera
- **Journeys anticipados**:
  1. Ver y editar la informacion del perfil por secciones (personal, profesional, idiomas)
  2. Subir o actualizar la foto de perfil
  3. Consultar documentos personales y laborales organizados en categorias dinamicas
  4. Subir o reemplazar un documento personal (DNI/NIE, certificados)
  5. Firmar un documento laboral usando la firma digital
  6. Capturar y guardar la firma digital para reutilizarla en futuras firmas
  7. Consultar el estado del contrato (solo SAD)
  8. (Solo Hogar) Completar perfil para poder aplicar a ofertas
- **CAs derivables**:
  1. Los datos core (nombre, apellidos, DNI/NIE) son de solo lectura; la direccion de domicilio es editable
  2. Se muestra un indicador de porcentaje de completitud del perfil
  3. Los documentos se organizan en dos categorias: personal (subir/reemplazar) y laboral (solo consultar/firmar)
  4. La trabajadora captura su firma digital con el dedo y puede reutilizarla
  5. Se reciben avisos de caducidad para DNI/certificados
  6. (Solo Hogar) Al aplicar a una oferta con perfil incompleto, se bloquea con indicacion de campos pendientes
- **Scope (RFs)**: RF-9.1, RF-9.2, RF-9.3, RF-9.4, RF-9.5
- **Scope (secciones PRD)**: RF-9: Perfil (completa)
- **Modelos propios**: PerfilTrabajadora, Documento, Contrato
- **Modelos compartidos (owner)**: FirmaDigital (esta feature define la captura y almacenamiento de la firma)
- **Modelos compartidos (ref)**: Usuaria (owner: F-001)

### F-011: communication
- **Descripcion**: Comunicarse con coordinacion mediante un sistema de chat con asuntos predefinidos, consultar el historial de conversaciones y recibir mensajes en tiempo real
- **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
- **Objetivo del actor**: Comunicarse de forma fluida con coordinacion para resolver dudas, gestionar incidencias administrativas o consultar sobre servicios
- **Journeys anticipados**:
  1. Iniciar una nueva conversacion seleccionando un asunto predefinido y escribiendo el primer mensaje
  2. Consultar el listado de conversaciones con indicadores de no leido y estado (abierta/cerrada)
  3. Enviar y recibir mensajes en tiempo real dentro de un hilo de conversacion
  4. Consultar una conversacion cerrada en modo historico (solo lectura)
  5. Buscar y borrar conversaciones
- **CAs derivables**:
  1. Al crear conversacion se selecciona asunto predefinido (Vacaciones/Ausencia, Nomina/Facturacion, Sobre un servicio, Documentacion, Consulta general, Otros)
  2. Los mensajes nuevos aparecen automaticamente sin refrescar la pantalla
  3. Las conversaciones cerradas por backoffice se muestran en modo historico sin campo de entrada de texto
  4. Se muestra estado de entrega/lectura para mensajes enviados
  5. Se puede enlazar contexto (servicio u oferta) al crear la conversacion
- **Scope (RFs)**: RF-10.1, RF-10.2, RF-10.3
- **Scope (secciones PRD)**: RF-10: Comunicacion (completa)
- **Modelos propios**: Conversacion, Mensaje
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Usuaria (owner: F-001), Servicio (owner: F-003), Oferta (owner: F-007)

### F-012: push-notifications
- **Descripcion**: Gestionar el registro del dispositivo para notificaciones push, recibir notificaciones con navegacion a pantalla especifica (deeplink) y consultar el historial de notificaciones
- **Actor principal**: Trabajadora (ambos perfiles: Hogar y SAD)
- **Objetivo del actor**: Recibir avisos oportunos de eventos importantes y acceder rapidamente a la informacion relevante desde la notificacion
- **Journeys anticipados**:
  1. Conceder permiso de notificaciones push tras el primer login
  2. Recibir una notificacion push (en primer plano, segundo plano o app cerrada) y tocarla para navegar a la pantalla relevante
  3. Consultar el historial de notificaciones y marcarlas como leidas
  4. Recibir notificaciones automaticas del sistema (recordatorios de disponibilidad, caducidad de documentos, servicio proximo, fichaje pendiente)
- **CAs derivables**:
  1. El permiso de notificaciones se solicita despues del primer login y antes del onboarding
  2. Tocar una notificacion abre la pantalla especifica via deeplink
  3. Las notificaciones se reciben correctamente con la app en primer plano (alerta in-app), segundo plano y cerrada
  4. El historial de notificaciones se puede consultar y marcar todas como leidas
  5. Se envian recordatorios automaticos: disponibilidad no actualizada en 30 dias, caducidad de documento en 30 dias, servicio programado manana, fichaje no realizado tras inicio del servicio
- **Scope (RFs)**: RF-11.1, RF-11.2
- **Scope (secciones PRD)**: RF-11: Notificaciones (completa)
- **Modelos propios**: Notificacion, PreferenciaNotificacion
- **Modelos compartidos (owner)**: --
- **Modelos compartidos (ref)**: Usuaria (owner: F-001), Servicio (owner: F-003), Llamamiento (owner: F-004), Ausencia (owner: F-008), Documento (owner: F-010), Conversacion (owner: F-011)

---

## Tabla de shared models

| Modelo | Feature Owner | Features que lo referencian | Criterio de asignacion |
|--------|---------------|-----------------------------|------------------------|
| Usuaria | F-001: auth-and-onboarding | F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-009, F-010, F-011, F-012 | Creacion explicita: F-001 registra y autentica la entidad usuaria |
| Servicio | F-003: service-management | F-002, F-004, F-005, F-006, F-008, F-009, F-011, F-012 | Gestion completa: F-003 contiene listado, detalle, notas, historial y asignacion de servicios (CRUD funcional) |
| Llamamiento | F-004: service-calls | F-002, F-003, F-012 | Creacion explicita: F-004 define el ciclo de vida completo del llamamiento (recibir, aceptar, rechazar, caducar) |
| FirmaDigital | F-010: profile-and-documents | F-004 | Creacion explicita: F-010 contiene la captura, almacenamiento y reutilizacion de la firma (RF-9.4) |
| Oferta | F-007: job-offers | F-011 | Creacion explicita: F-007 define la navegacion, detalle y solicitud de ofertas |
| Ausencia | F-008: absence-management | F-012 | Creacion explicita: F-008 define la solicitud y gestion de ausencias |
| Documento | F-010: profile-and-documents | F-012 | Gestion completa: F-010 gestiona subida, reemplazo, consulta y firma de documentos |
| Conversacion | F-011: communication | F-012 | Creacion explicita: F-011 crea y gestiona conversaciones |
| Cliente | F-003: service-management | -- | Proximidad semantica: la informacion del cliente aparece exclusivamente como parte del detalle de servicio |

---

## Trazabilidad RF -> Feature

| RF | Titulo RF | Feature asignada |
|----|-----------|------------------|
| RF-1.0 | Pantalla de Splash | F-001: auth-and-onboarding |
| RF-1.1 | Pantallas de Bienvenida | F-001: auth-and-onboarding |
| RF-1.2 | Registro de Usuario | F-001: auth-and-onboarding |
| RF-1.3 | Inicio de Sesion | F-001: auth-and-onboarding |
| RF-1.4 | Recuperacion de Acceso | F-001: auth-and-onboarding |
| RF-1.5 | Gestion del Token de Sesion | F-001: auth-and-onboarding |
| RF-1.6 | Cierre de Sesion | F-001: auth-and-onboarding |
| RF-1.7 | Pantalla Sin Permisos / Acceso Revocado | F-001: auth-and-onboarding |
| RF-2.1 | Accesos Directos del Panel | F-002: dashboard-and-announcements |
| RF-2.2 | Tablon de Anuncios / Comunicados | F-002: dashboard-and-announcements |
| RF-2.3 | Mensajes del Sistema | F-002: dashboard-and-announcements |
| RF-3.1 | Listado de Servicios | F-003: service-management |
| RF-3.2 | Detalle del Servicio | F-003: service-management |
| RF-3.3 | Notas de Servicio | F-003: service-management |
| RF-3.4 | Llamadas de Servicio (Llamamientos) | F-004: service-calls |
| RF-3.5 | Historial de Servicios | F-003: service-management |
| RF-3.7 | Nuevo Servicio Asignado (Contratos Indefinidos) | F-003: service-management |
| RF-4.1 | Fichar Entrada/Salida | F-005: time-tracking |
| RF-4.2 | Historial de Seguimiento de Tiempo | F-005: time-tracking |
| RF-5.1 | Reportar Incidencia | F-006: incident-reporting |
| RF-5.2 | Historial de Incidencias | F-006: incident-reporting |
| RF-6.1 | Navegar Ofertas | F-007: job-offers |
| RF-6.2 | Solicitar Oferta | F-007: job-offers |
| RF-6.3 | Mis solicitudes | F-007: job-offers |
| RF-7.1 | Calendario de Disponibilidad | F-009: availability-management |
| RF-8.1 | Solicitar Ausencia | F-008: absence-management |
| RF-8.2 | Historial de Ausencias | F-008: absence-management |
| RF-9.1 | Ver y Editar Perfil | F-010: profile-and-documents |
| RF-9.2 | Foto de Perfil | F-010: profile-and-documents |
| RF-9.3 | Documentos | F-010: profile-and-documents |
| RF-9.4 | Firma Digital | F-010: profile-and-documents |
| RF-9.5 | Estado del Contrato | F-010: profile-and-documents |
| RF-10.1 | Inicio de Nueva Conversacion | F-011: communication |
| RF-10.2 | Listado de Conversaciones | F-011: communication |
| RF-10.3 | Hilo de Conversacion | F-011: communication |
| RF-11.1 | Entrega de Notificaciones Push | F-012: push-notifications |
| RF-11.2 | Notificaciones Automaticas del Sistema | F-012: push-notifications |

---

## Decisiones de merge

No se realizaron merges. Todas las features candidatas cumplen los 3 criterios de validacion (journeys independientes, minimo 3 CAs derivables, actor claro).

**Notas de diseno relevantes:**

- **RF-3.4 (Llamamientos) separado de RF-3 (Servicios)**: Aunque el PRD agrupa los llamamientos dentro de "Mis Servicios", se separan en una feature independiente (F-004: service-calls) porque tienen un actor mas especifico (trabajadora con contrato fijo discontinuo), journeys completamente independientes (aceptar/rechazar con firma digital, cuenta atras, bloqueo de navegacion) y reglas de negocio propias (caducidad, competencia multi-trabajadora). El historial de llamamientos (RF-3.5 CA5) se referencia desde F-003 pero la entidad Llamamiento es owned por F-004.

- **RF-3.5 (Historial de Servicios) en F-003**: El historial de servicios incluye servicios completados Y el historial de llamamientos. El RF-3.5 se asigna a F-003 porque su journey principal es consultar servicios completados. Los llamamientos que aparecen en el historial referencian la entidad Llamamiento de F-004.

- **RF-12 (Publicacion de la Aplicacion) excluido**: Es funcionalidad de despliegue/implementacion, no funcionalidad de usuario. Pertenece al Plan, no al Spec (confirmado por contaminacion [C-016] en el analysis).

---

## Siguiente paso

Para generar el spec de cada feature individualmente:
```
/wf-spec-fast-track prd-hogar-sad.md --scope-from prd-hogar-sad_discovery.md --feature F-001
```

Para generar todos los specs en paralelo (flujo automatico):
```
/wf-spec-features-first prd-hogar-sad.md
```
