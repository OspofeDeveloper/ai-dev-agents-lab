# Features Index: CUIDEO - Hogar & SAD
> PRD origen: prd-hogar-sad.md | Fecha: 2026-04-03

---

## Features identificadas

### F-001: autenticacion-onboarding
- **Descripcion**: Registro, inicio de sesion, onboarding, recuperacion de acceso, gestion de sesion y pantalla de acceso revocado
- **Actor principal**: Trabajadora (Hogar y SAD)
- **Journeys propios**: Primer acceso Hogar, Primer acceso SAD, Login habitual, Recuperacion de contrasena, Cierre de sesion, Acceso revocado
- **CAs propios**: CA-001 a CA-028
- **Modelos propios**: Usuario, Sesion
- **Modelos compartidos (owner)**: Usuario <- esta feature lo define
- **Modelos compartidos (ref)**: —
- **Ruta spec**: features/autenticacion-onboarding/autenticacion-onboarding_spec.md

### F-002: panel-principal
- **Descripcion**: Pantalla principal con accesos directos, tablon de anuncios y mensajes del sistema
- **Actor principal**: Trabajadora (Hogar y SAD)
- **Journeys propios**: Consultar Home y navegar, Consultar comunicado, Consultar mensaje del sistema
- **CAs propios**: CA-001 a CA-024
- **Modelos propios**: Anuncio, MensajeSistema
- **Modelos compartidos (owner)**: Anuncio <- esta feature lo define
- **Modelos compartidos (ref)**: Usuario (owner: F-001)
- **Ruta spec**: features/panel-principal/panel-principal_spec.md

### F-003: gestion-servicios
- **Descripcion**: Listado, detalle, notas, llamamientos, historial y recepcion de nuevos servicios asignados
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Consultar servicios, Detalle de servicio, Gestionar notas, Responder a llamamiento, Consultar historial, Recibir nuevo servicio asignado
- **CAs propios**: CA-001 a CA-037
- **Modelos propios**: Servicio, Llamamiento, NotaServicio
- **Modelos compartidos (owner)**: Servicio <- esta feature lo define
- **Modelos compartidos (ref)**: Usuario (owner: F-001), FirmaDigital (owner: F-009)
- **Ruta spec**: features/gestion-servicios/gestion-servicios_spec.md

### F-004: control-horario
- **Descripcion**: Fichaje de entrada/salida con geolocalizacion y consulta de historial de fichajes
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Fichar entrada, Fichar salida, Consultar historial de fichajes
- **CAs propios**: CA-001 a CA-021
- **Modelos propios**: RegistroFichaje
- **Modelos compartidos (owner)**: —
- **Modelos compartidos (ref)**: Servicio (owner: F-003)
- **Ruta spec**: features/control-horario/control-horario_spec.md

### F-005: incidencias
- **Descripcion**: Reporte de incidencias del servicio con descripcion, adjuntos y seguimiento del estado
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Reportar incidencia, Consultar historial de incidencias
- **CAs propios**: CA-001 a CA-017
- **Modelos propios**: Incidencia
- **Modelos compartidos (owner)**: —
- **Modelos compartidos (ref)**: Servicio (owner: F-003)
- **Ruta spec**: features/incidencias/incidencias_spec.md

### F-006: ofertas-trabajo
- **Descripcion**: Navegacion, filtros, solicitud de ofertas y seguimiento de candidaturas
- **Actor principal**: Trabajadora Hogar
- **Journeys propios**: Buscar y aplicar a oferta, Seguimiento de solicitudes
- **CAs propios**: CA-001 a CA-025
- **Modelos propios**: Oferta, Solicitud
- **Modelos compartidos (owner)**: Oferta <- esta feature lo define
- **Modelos compartidos (ref)**: Usuario (owner: F-001)
- **Ruta spec**: features/ofertas-trabajo/ofertas-trabajo_spec.md

### F-007: disponibilidad
- **Descripcion**: Calendario semanal de disponibilidad con franjas rapidas, slots personalizados y horas asignadas
- **Actor principal**: Trabajadora (Hogar y SAD)
- **Journeys propios**: Gestionar disponibilidad semanal
- **CAs propios**: CA-001 a CA-013
- **Modelos propios**: SlotDisponibilidad
- **Modelos compartidos (owner)**: —
- **Modelos compartidos (ref)**: Usuario (owner: F-001)
- **Ruta spec**: features/disponibilidad/disponibilidad_spec.md

### F-008: ausencias
- **Descripcion**: Solicitud de ausencias, historial y consulta de saldo de vacaciones
- **Actor principal**: Trabajadora SAD
- **Journeys propios**: Solicitar ausencia, Consultar historial y saldo
- **CAs propios**: CA-001 a CA-018
- **Modelos propios**: Ausencia
- **Modelos compartidos (owner)**: —
- **Modelos compartidos (ref)**: Usuario (owner: F-001), Servicio (owner: F-003)
- **Ruta spec**: features/ausencias/ausencias_spec.md

### F-009: perfil
- **Descripcion**: Visualizacion y edicion de perfil, foto, documentos, firma digital y estado del contrato
- **Actor principal**: Trabajadora (Hogar y SAD)
- **Journeys propios**: Consultar y editar perfil, Subir foto, Gestionar documentos, Capturar firma digital, Consultar contrato
- **CAs propios**: CA-001 a CA-035
- **Modelos propios**: Perfil, Documento, FirmaDigital
- **Modelos compartidos (owner)**: FirmaDigital <- esta feature lo define
- **Modelos compartidos (ref)**: Usuario (owner: F-001)
- **Ruta spec**: features/perfil/perfil_spec.md

### F-010: comunicacion
- **Descripcion**: Chat con coordinacion por asuntos predefinidos con enrutado transparente
- **Actor principal**: Trabajadora (Hogar y SAD)
- **Journeys propios**: Iniciar conversacion, Consultar conversaciones, Intercambiar mensajes
- **CAs propios**: CA-001 a CA-024
- **Modelos propios**: Conversacion, Mensaje
- **Modelos compartidos (owner)**: —
- **Modelos compartidos (ref)**: Usuario (owner: F-001)
- **Ruta spec**: features/comunicacion/comunicacion_spec.md

### F-011: notificaciones
- **Descripcion**: Recepcion de notificaciones push con deeplinks y recordatorios automaticos
- **Actor principal**: Trabajadora (Hogar y SAD)
- **Journeys propios**: Recibir y actuar sobre notificacion, Recibir recordatorio automatico
- **CAs propios**: CA-001 a CA-011
- **Modelos propios**: Notificacion
- **Modelos compartidos (owner)**: —
- **Modelos compartidos (ref)**: Usuario (owner: F-001)
- **Ruta spec**: features/notificaciones/notificaciones_spec.md

---

## Tabla de shared models

| Modelo | Feature Owner | Features que lo referencian |
|--------|---------------|-----------------------------|
| Usuario | F-001: autenticacion-onboarding | F-002, F-003, F-006, F-007, F-008, F-009, F-010, F-011 |
| Servicio | F-003: gestion-servicios | F-004, F-005, F-008 |
| FirmaDigital | F-009: perfil | F-003 |
| Oferta | F-006: ofertas-trabajo | F-010 (enlazar contexto) |
| Anuncio | F-002: panel-principal | F-011 (deeplink a comunicado) |
