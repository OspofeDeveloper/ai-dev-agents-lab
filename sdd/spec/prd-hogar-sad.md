---
type: product-requirements
client: Doonamis SL
product: Aplicaciones Móviles CUIDEO - Hogar & SAD
version: 1.9
created: 2026-01-28
last_updated: 2026-03-26
status: in-review
authors:
  - Ferran Falguera
---
# PRD: Aplicaciones Móviles CUIDEO - Hogar & SAD

## Resumen Ejecutivo

### Visión del Producto
Empoderar a las trabajadoras de cuidado con herramientas móviles intuitivas que simplifiquen sus operaciones diarias, mejoren la comunicación con los coordinadores y proporcionen transparencia en la gestión de servicios.

### Objetivos de Negocio
- Proporcionar una experiencia mobile-first para las trabajadoras de cuidado para gestionar servicios, disponibilidad y comunicación
- Facilitar la comunicación fluida entre trabajadoras y back-office
- Permitir el seguimiento del tiempo en tiempo real con validación de geolocalización
- Digitalizar la gestión de documentos y el reporte de incidencias
- Optimizar las solicitudes de ausencia y la gestión de disponibilidad

### Lanzamiento Objetivo
Todos los módulos incluidos en el MVP para el lanzamiento inicial tanto en iOS (App Store) como en Android (Google Play).

### Puntos Clave
- **Arquitectura de doble perfil**: Codebase única (KMM) que sirve dos aplicaciones de marca diferentes
- **Seguimiento de tiempo validado por ubicación**: Garantizar el cumplimiento del servicio con geolocalización
- **Comunicación en tiempo real**: Mensajería directa con coordinación (enrutado interno gestionado por back-office)
- **Gestión integral de servicios**: Desde ofertas de trabajo hasta servicios completados

---

## Alcance

### Dentro del Alcance - Lanzamiento MVP

#### Todos los Perfiles de Usuario (Hogar & SAD)

- Pantalla de splash
- Registro y autenticación de usuarias (email y contraseña)
- Gestión de sesiones con refresh tokens
- Panel principal con accesos directos y anuncios
- Gestión de disponibilidad por zonas (basadas en dirección de domicilio)
- Gestión de perfil (información personal, experiencia, documentos)
- Carga de documentos (PDF, DOC, DOCX, JPG, PNG)
- Captura de firma digital
- Módulo de comunicación con back-office
- Notificaciones push con deeplinks
- Mensajes del sistema de solo lectura
- Chat de comunicación con coordinación/back-office


#### Solo Perfil Hogar

- Listado de ofertas de trabajo con filtros
- Gestión de solicitudes de ofertas
- Seguimiento del estado de las solicitudes


#### Solo Perfil SAD

- Pantalla de acceso revocado
- Gestión de servicios asignados (recurrentes y puntuales)
- Detalles de servicio con integración de ubicación: un link a Google Maps
- Notas de servicio con adjuntos de archivos
- Llamadas de servicio (llamamientos) con aceptar/rechazar
- Seguimiento de tiempo (fichar entrada/salida) con geolocalización
- Historial de seguimiento de tiempo por servicio
- Reporte de incidencias con adjuntos
- Solicitudes de ausencia con seguimiento de estado
- Saldo de vacaciones por año
- Visualización del estado del contrato


### Fuera de Alcance - Posibles fases futuras

- Autenticación biométrica (Face ID, Huella digital)
- Autenticación de dos factores (2FA)
- Detección de GPS simulado
- Modo offline con sincronización
- Gestión activa de pagos/nóminas (el acceso de solo lectura a documentos de nómina está dentro del alcance como parte de Documentación laboral)
- Funciones sociales (perfiles, valoraciones)
- Eventos de analytics personalizados (solo Firebase out-of-the-box)

---

## Contexto y Problema

### Problema a Resolver
Este documento define los requisitos para dos aplicaciones móviles nativas desarrolladas con Kotlin Multiplatform Mobile (KMM) que servirán dos perfiles de usuaria diferentes dentro del ecosistema CUIDEO:

- **CUIDEO (Hogar)**: Aplicación de tema azul para trabajadoras de cuidado a domicilio con contrato **fijo discontinuo** que buscan oportunidades
- **Felizvita (SAD)**: Aplicación de tema verde para trabajadoras **contratadas** del Servicio de Asistencia Social que gestionan sus servicios

### Usuario Objetivo

#### CUIDEO (Perfil Hogar)

- **Esquema de Colores**: Azul
- **Usuarias Objetivo**: Trabajadoras del hogar única y exclusivamente (perfil Hogar)
- **Casos de Uso Principales**:
  - Navegar y aplicar a ofertas de trabajo
  - Gestionar disponibilidad por zonas
  - Comunicación con coordinadores
  - Gestión de perfil y documentos


#### Felizvita (Perfil SAD)

- **Esquema de Colores**: Verde
- **Usuarias Objetivo**: Trabajadoras del Servicio de Asistencia Social
- **Casos de Uso Principales**:
  - Gestionar servicios asignados (recurrentes y puntuales)
  - Seguimiento de tiempo con geolocalización
  - Reportar incidencias
  - Solicitar ausencias
  - Notas de servicio y documentación

---

## Arquitectura del Sistema

### Visión General de la Arquitectura

#### Stack Tecnológico

**Aplicación Móvil:**
- **Framework:** Kotlin Multiplatform Mobile (KMM)
- **Código Compartido:** Lógica de negocio, red, modelos de datos
- **Específico de Plataforma:** UI (Jetpack Compose para Android e iOS), APIs de plataforma

**Backend:**
- Desarrollado por el equipo del cliente
- API RESTful
- Formato de respuesta JSON
- Autenticación basada en JWT

### Diagrama de Arquitectura
```
┌────────────────────────────┐
│        Apps Móviles        │
│  CUIDEO (Hogar) / SAD      │
│      iOS / Android         │
└───────────────┬────────────┘
                │ HTTPS + JWT
                ▼
┌────────────────────────────┐
│         API REST           │
│     Backend del cliente    │
└───────────────┬────────────┘
                │
                ▼
┌────────────────────────────┐
│         Base de Datos      │
└────────────────────────────┘
```

### Integraciones Externas

**Servicios de Terceros:**
- Firebase Cloud Messaging (notificaciones push)
- Firebase Realtime Database (mensajería)
- Firebase Crashlytics (reporte de caídas)
- Firebase Analytics (analítica básica)

---

### Lógica de Negocio Compartida (KMM)

**Módulos en shared:**

1. **Módulo de Red**: Cliente API, gestión de solicitudes/respuestas
2. **Módulo de Autenticación**: Inicio de sesión, gestión de tokens, sesión
3. **Módulo de Perfil de Usuaria**: Datos de perfil, documentos
4. **Módulo de Servicios** (SAD): Gestión de servicios, notas, llamadas
5. **Módulo de Control Horario** (SAD): Fichar entrada/salida, geolocalización
6. **Módulo de Ofertas** (Hogar): Navegar ofertas, solicitudes
7. **Módulo de Comunicación**: Mensajería, conversaciones
8. **Módulo de Notificaciones**: Gestión de notificaciones push
9. **Módulo de Incidencias** (SAD): Reporte de incidencias
10. **Módulo de Ausencias** (SAD): Solicitudes de ausencia, saldo
11. **Módulo de Disponibilidad**: Configuración de disponibilidad
12. **Utilidades Comunes**: Formato de fechas, validación, gestión de errores

---

### Especificación de la API

#### Resumen de Endpoints API

Las especificaciones completas de los endpoints se detallan en las secciones de Requisitos Funcionales. A continuación se presenta un resumen de alto nivel.

> **Nota:** Los endpoints marcados con ✅ están definidos en el Swagger oficial (`https://newbeta.felizvita.app/api-docs/`, v1.6.0). Los marcados con 🔲 son requisitos funcionales pendientes de definir en la API por el equipo de backend.

##### Autenticación

- ✅ POST /api/v1/workers/auth/login - Autenticar con email y contraseña; retorna token Sanctum válido 30 días
- ✅ POST /api/v1/workers/auth/forgot-password - Enviar email con enlace de recuperación de contraseña
- ✅ POST /api/v1/workers/auth/reset-password - Restablecer contraseña con token de un solo uso (expira 60 min)
- ✅ GET /api/v1/workers/auth/validate-token - Verificar validez del token actual y obtener datos básicos
- ✅ POST /api/v1/workers/auth/logout - Revocar el token Sanctum del trabajador
- 🔲 POST /api/v1/workers/auth/refresh - Refrescar token de acceso usando refresh token
- 🔲 POST /api/v1/workers/auth/register - Registro de usuaria (solo Hogar, pendiente de definir)


##### Dashboard

- ✅ GET /api/v1/workers/dashboard - Vista consolidada: perfil laboral + servicios activos + anuncios recientes (una sola llamada)


##### Anuncios

- ✅ GET /api/v1/announcements - Listar anuncios paginados (máx. 50/página); filtros: type, priority, content_type
- ✅ GET /api/v1/announcements/:id - Obtener detalle con adjuntos; registra lectura automáticamente
- ✅ POST /api/v1/announcements/:id/mark-read - Marcar como leído (idempotente)


##### Mensajes del Sistema

- 🔲 GET /api/v1/messages/system - Listar mensajes del sistema
- 🔲 GET /api/v1/messages/system/:id - Obtener detalles del mensaje
- 🔲 POST /api/v1/messages/system/:id/mark-read - Marcar como leído
- 🔲 DELETE /api/v1/messages/system/:id - Borrar mensaje

##### Servicios (SAD)

- ✅ GET /api/v1/workers/services - Listar todos los servicios (activos, próximos e inactivos en arrays separados)
- ✅ GET /api/v1/workers/services/active - Solo servicios activos
- ✅ GET /api/v1/workers/services/upcoming - Solo servicios con fecha de inicio posterior a hoy
- ✅ GET /api/v1/workers/services/:id?type=service|extra_service - Detalle completo del servicio
- 🔲 GET /api/v1/workers/services/:service_worker_id/notes - Listar notas del servicio
- 🔲 POST /api/v1/workers/services/:service_worker_id/notes - Añadir nota de servicio
- 🔲 PUT /api/v1/workers/services/:service_worker_id/notes/:note_id - Editar nota
- 🔲 DELETE /api/v1/workers/services/:service_worker_id/notes/:note_id - Borrar nota (borrado suave)

##### Llamadas de Servicio (SAD)

- 🔲 GET /api/v1/service-calls - Listar llamadas de servicio
- 🔲 GET /api/v1/service-calls/:id - Obtener detalles de la llamada
- 🔲 POST /api/v1/service-calls/:id/accept - Aceptar llamada de servicio
- 🔲 POST /api/v1/service-calls/:id/reject - Rechazar llamada de servicio


##### Asignación de Servicio (SAD)

- ✅ POST /api/v1/workers/services/:service_worker_id/acknowledge - Confirmar recepción de nuevo servicio asignado (estado: pending→acknowledged)

##### Control Horario (SAD)

- ✅ POST /api/v1/workers/time-tracking/clock-in - Fichar entrada (`service_worker_id`, `type: worker|rest`)
- ✅ POST /api/v1/workers/time-tracking/clock-out - Fichar salida (`service_worker_id`, `type: worker|rest`); calcula horas trabajadas
- ✅ GET /api/v1/workers/time-tracking/current-status - Estado de fichaje de todos los servicios activos
- ✅ GET /api/v1/workers/time-tracking/current-status/:service_worker_id - Estado de fichaje de un servicio concreto
- ✅ GET /api/v1/workers/time-tracking/history?service_worker_id=X[&month=MM&year=YYYY] - Sin mes: resumen mensual; con mes: detalle diario

##### Incidencias (SAD)

- 🔲 POST /api/v1/workers/incidents - Reportar incidencia
- 🔲 GET /api/v1/workers/incidents - Listar incidencias
- 🔲 GET /api/v1/workers/incidents/:id - Obtener detalles de la incidencia

##### Ofertas (Hogar)

- 🔲 GET /api/v1/offers - Listar ofertas de trabajo con filtros
- 🔲 GET /api/v1/offers/:id - Obtener detalles de la oferta
- 🔲 POST /api/v1/offers/:id/apply - Solicitar oferta

##### Solicitudes (Hogar)

- 🔲 GET /api/v1/applications - Listar mis solicitudes
- 🔲 DELETE /api/v1/applications/:id - Retirar solicitud

##### Disponibilidad (Ambos)

- ✅ GET /api/v1/workers/availability - Horas contratadas, asignadas y fichadas esta semana + franjas disponibles/no disponibles
- ✅ POST /api/v1/workers/availability/available-slots - Crear franja de disponibilidad (`day` 1-7, `start_time` HH:MM, `end_time` HH:MM); se permiten solapamientos con franjas de no disponibilidad
- ✅ PUT /api/v1/workers/availability/available-slots/:id - Actualizar franja de disponibilidad
- ✅ DELETE /api/v1/workers/availability/available-slots/:id - Eliminar franja de disponibilidad
- ✅ POST /api/v1/workers/availability/unavailable-slots - Crear franja de no disponibilidad (`day` 1-7, `start_time` HH:MM, `end_time` HH:MM); se permiten solapamientos con franjas disponibles
- ✅ PUT /api/v1/workers/availability/unavailable-slots/:id - Actualizar franja de no disponibilidad
- ✅ DELETE /api/v1/workers/availability/unavailable-slots/:id - Eliminar franja de no disponibilidad

##### Ausencias (SAD)

- 🔲 POST /api/v1/workers/absences - Solicitar ausencia
- 🔲 GET /api/v1/workers/absences - Listar ausencias con saldo de vacaciones
- 🔲 GET /api/v1/workers/absences/:id - Obtener detalles de la ausencia
- 🔲 DELETE /api/v1/workers/absences/:id - Cancelar solicitud de ausencia

##### Perfil (Ambos)

- ✅ GET /api/v1/workers/profile - Obtener datos laborales: tipo de contrato, horas semanales, estado
- 🔲 PUT /api/v1/workers/profile/personal-info - Actualizar información personal
- 🔲 PUT /api/v1/workers/profile/professional - Actualizar información profesional
- 🔲 POST /api/v1/workers/profile/languages - Añadir idioma
- 🔲 DELETE /api/v1/workers/profile/languages/:id - Eliminar idioma
- 🔲 POST /api/v1/workers/profile/photo - Subir foto de perfil
- 🔲 DELETE /api/v1/workers/profile/photo - Borrar foto de perfil
- 🔲 GET /api/v1/workers/profile/documents - Listar documentos (personal + laboral)
- 🔲 POST /api/v1/workers/profile/documents - Subir documento (solo documentación personal)
- 🔲 PUT /api/v1/workers/profile/documents/:id - Reemplazar documento personal existente
- 🔲 POST /api/v1/workers/profile/documents/:id/sign - Firmar documento laboral
- 🔲 POST /api/v1/workers/profile/signature - Guardar firma
- 🔲 GET /api/v1/workers/profile/signature - Obtener firma
- 🔲 GET /api/v1/workers/profile/contract - Obtener información del contrato (solo SAD): tipo, fecha inicio, número empleada, enlace PDF

##### Comunicación (Ambos)

- 🔲 GET /api/v1/workers/communication/conversations - Listar conversaciones
- 🔲 GET /api/v1/workers/communication/conversations/:id/messages - Obtener mensajes de la conversación
- 🔲 POST /api/v1/workers/communication/conversations/:id/messages - Enviar mensaje
- 🔲 POST /api/v1/workers/communication/conversations/:id/mark-read - Marcar conversación como leída
- 🔲 POST /api/v1/workers/communication/conversations - Iniciar nueva conversación
- 🔲 DELETE /api/v1/workers/communication/conversations/:id - Borrar conversación

##### Notificaciones (Ambos)

- 🔲 POST /api/v1/workers/devices/register - Registrar dispositivo para push
- 🔲 PUT /api/v1/workers/devices/:device_id/fcm-token - Actualizar token FCM
- 🔲 DELETE /api/v1/workers/devices/:device_id - Dar de baja dispositivo
- 🔲 GET /api/v1/workers/notifications - Listar historial de notificaciones
- 🔲 PUT /api/v1/workers/notifications/mark-all-read - Marcar todas como leídas

---

## Requisitos Funcionales

### RF-1: Autenticación y Onboarding

**Se aplica a:** Ambos perfiles

#### RF-1.0: Pantalla de Splash

**Descripción:**
Pantalla de bienvenida con el logo de la aplicación, visible unos segundos al arrancar antes de iniciar el flujo de autenticación.

**Criterios de Aceptación:**
**CA1:** Mostrar el logo de la aplicación sobre fondo de marca al arrancar
**CA2:** Duración de 2-3 segundos antes de redirigir automáticamente
**CA3:** Redirigir al login si no hay sesión activa; al home si hay sesión válida

**Endpoints API Requeridos:** Ninguno

---

#### RF-1.1: Pantallas de Bienvenida

**Descripción:**
Pantalla de onboarding que explica las funcionalidades principales de la app. El flujo recomendado es: **login → onboarding → permisos** (así se evita mostrar el onboarding a quien no tiene acceso). El onboarding es general y cubre ambos tipos de contrato (fijo discontinuo e indefinido), ya que las trabajadoras pueden rotar entre estados.

**Criterios de Aceptación:**

**CA1:** Mostrar 3-5 pantallas de bienvenida (ideal 3, máximo 5), priorizando los highlights principales de la aplicación
**CA2:** Solicitar permiso de **ubicación** con explicación clara del uso (fichaje)
**CA3:** Solicitar permiso de **notificaciones push** — solicitarlo **después del primer login y antes del onboarding** para vincular el token FCM al usuario concreto
**CA4:** Permiso de **cámara/archivos**: solicitar **solo en el momento en que se necesite** (p. ej. al subir un documento), no durante el onboarding
**CA5:** Mostrar el onboarding solo una vez
**CA6:** Almacenar el estado de completación del onboarding localmente
**CA7:** El contenido del onboarding es general y válido para ambos tipos de contrato

**Endpoints API Requeridos:** Ninguno (solo local)

---

#### RF-1.2: Registro de Usuario

**Descripción:**
**Perfil Hogar**: Las trabajadoras se registran directamente desde la app introduciendo su email y eligiendo una contraseña. El alta queda completada al enviar el formulario de registro.

**Perfil SAD (Felizvita)**: No existe registro abierto. Las cuentas se crean desde el backoffice y se envía a la trabajadora un **email de activación** con un enlace para que establezca sus credenciales (email ya preconfigurado + nueva contraseña) en el primer acceso.

**Criterios de Aceptación:**
**CA1:** (Solo Hogar) Introducir email y contraseña para iniciar el registro; validación de formato en ambos campos
**CA2:** (Solo Hogar) La contraseña debe cumplir requisitos mínimos de seguridad (mínimo 8 caracteres, al menos una mayúscula y un número)
**CA3:** (Solo Hogar) Completar el registro e iniciar sesión directamente tras el envío del formulario
**CA4:** Mostrar mensajes de error claros para errores de validación
**CA5:** Asignar la usuaria al perfil correcto según sea (Hogar/SAD)
**CA6:** (Solo SAD) Flujo de activación de cuenta: la trabajadora recibe un email con un enlace de activación; al acceder al enlace puede establecer su contraseña y acceder a la app

**Endpoints API Requeridos:**

- `POST /api/v1/workers/auth/register` — Registro de usuaria (solo Hogar, con email y contraseña) 🔲 pendiente

---

#### RF-1.3: Inicio de Sesión

**Descripción:**
Las usuarias inician sesión con su **email y contraseña**. La sesión se **mantiene activa** tras el primer acceso para reducir fricción; el login solo se vuelve a solicitar si el token Sanctum ha expirado o sido revocado (baja, inactividad >30 días) o la usuaria ha cerrado sesión explícitamente.

**Criterios de Aceptación:**
**CA1:** Campos de entrada de email y contraseña
**CA2:** Validar formato del email antes de enviar la solicitud
**CA3:** Mostrar error claro si las credenciales son incorrectas
**CA4:** Bloqueo temporal tras N intentos fallidos (N configurable en servidor)
**CA5:** Mantener la sesión activa si no hace logout (no requerir login en cada acceso)
**CA6:** Inicio de sesión automático si el token Sanctum almacenado sigue siendo válido (verificado con `/auth/validate-token` al arrancar la app); sin mostrar pantalla de login
**CA7:** Redirigir a la pantalla principal al iniciar sesión con éxito
**CA8:** Almacenar tokens de forma segura (iOS Keychain / Android Keystore)
**CA9:** Si el token queda invalidado (trabajadora dada de baja, etc.), las credenciales no permitirán el acceso y se muestra la pantalla de acceso revocado (RF-1.7)

**Endpoints API Requeridos:**

- `POST /api/v1/workers/auth/login` — Autenticar con email y contraseña; retorna token Sanctum (body: `email`, `password`, `device_name` opcional)

---

#### RF-1.4: Recuperación de Acceso

**Descripción:**
La usuaria puede recuperar el acceso a su cuenta en caso de haber olvidado la contraseña. Desde la pantalla de login accede al flujo de recuperación, introduce su email y recibe un enlace para establecer una nueva contraseña.

**Criterios de Aceptación:**
**CA1:** Enlace "¿Olvidaste tu contraseña?" o similar en la pantalla de login que lleva a la pantalla de recuperación
**CA2:** Pantalla de recuperación con campo de entrada de email
**CA3:** Mostrar confirmación de envío del email (sin revelar si el email existe en el sistema)
**CA4:** El enlace de recuperación recibido por email permite establecer una nueva contraseña; el enlace tiene caducidad (definida por backend)
**CA5:** La nueva contraseña debe cumplir los mismos requisitos de seguridad que el registro (RF-1.2)
**CA6:** Si la cuenta está dada de baja o suspendida, el enlace no permitirá el acceso y se muestra la pantalla de acceso revocado (RF-1.7)

**Endpoints API Requeridos:**

- `POST /api/v1/workers/auth/forgot-password` — Enviar email con enlace de recuperación (respuesta genérica para no revelar si el email existe)
- `POST /api/v1/workers/auth/reset-password` — Restablecer contraseña con token de un solo uso (expira 60 min)

---

#### RF-1.5: Gestión del Token de Sesión

**Descripción:**
La API utiliza un **único token Sanctum válido 30 días** (no hay mecanismo de access token + refresh token en la versión actual). La sesión se mantiene activa mientras el token sea válido; si expira o es revocado por el backend, la usuaria debe volver a iniciar sesión.

La app verifica la validez del token llamando a `/auth/validate-token` al arrancar. Cualquier respuesta `401` de la API indica que el token ha expirado o sido revocado.

> **Nota:** El endpoint `POST /api/v1/workers/auth/refresh` (🔲 pendiente) añadirá en el futuro un mecanismo de refresh token separado. Hasta entonces, la gestión de sesión se realiza exclusivamente con el token Sanctum de 30 días.

**Criterios de Aceptación:**
**CA1:** Verificar la validez del token llamando a `/auth/validate-token` al arrancar la app
**CA2:** Detectar respuestas `401` en cualquier llamada a la API como señal de token expirado o revocado
**CA3:** Redirigir al login si el token no es válido; no reintentar la llamada
**CA4:** Si múltiples llamadas simultáneas reciben `401`, redirigir al login una sola vez
**CA5:** El token almacenado se borra localmente al hacer logout

**Endpoints API Requeridos:**

- `GET /api/v1/workers/auth/validate-token` — Verificar validez del token actual y obtener datos básicos del usuario
- `POST /api/v1/workers/auth/refresh` — Refrescar token de acceso (🔲 pendiente de implementar)

---

#### RF-1.6: Cierre de Sesión

**Descripción:**
Las usuarias pueden cerrar sesión, borrando los datos de sesión locales e invalidando tokens.

**Criterios de Aceptación:**
**CA1:** Borrar todos los tokens almacenados del almacenamiento seguro
**CA2:** Borrar datos de usuaria en caché
**CA3:** Invalidar refresh token en el backend
**CA4:** Redirigir a la pantalla de inicio de sesión
**CA5:** Mostrar diálogo de confirmación antes de cerrar sesión

**Endpoints API Requeridos:**

- `POST /api/v1/workers/auth/logout` — Revocar el token Sanctum del trabajador

---

#### RF-1.7: Pantalla Sin Permisos / Acceso Revocado

**Se aplica a:** Solo perfil SAD (Felizvita)

**Descripción:**
Cuando una trabajadora intenta acceder con credenciales válidas pero su cuenta ha sido suspendida, dada de baja o desactivada, se muestra una pantalla informativa en lugar de permitir el acceso a la app.

**Criterios de Aceptación:**
**CA1:** Detectar el estado de cuenta suspendida o revocada en la respuesta de autenticación del backend
**CA2:** Mostrar pantalla informativa con mensaje claro: "Ya no tienes permisos para acceder a esta aplicación"
**CA3:** No permitir navegar a ninguna sección de la app desde esta pantalla
**CA4:** Mostrar información de contacto o soporte para que la trabajadora pueda resolver la situación
**CA5:** No mantener sesión ni almacenar tokens en este estado

**Endpoints API Requeridos:**

Ninguno específico — el estado de cuenta revocada se detecta en la respuesta de `POST /api/v1/workers/auth/login`

---

### RF-2: Panel Principal

**Se aplica a:** Ambos perfiles

#### RF-2.1: Accesos Directos del Panel

**Descripción:**
Pantalla principal con tarjetas de acceso rápido a las secciones primarias de la aplicación según el perfil de usuaria.

**Criterios de Aceptación:**
**CA1:** Home de Hogar: Ofertas, Mi Disponibilidad, Perfil, Comunicación
**CA2:** Home de SAD: priorizar **servicio activo + fichaje** como acción principal. El contenido es configurable según estado (servicio activo, próximos servicios, llamamientos pendientes, etc.). Secciones: Mis Servicios, Fichar, Incidencias, Solicitar Ausencia, Mis Ausencias, Mi Disponibilidad, Documentación, Perfil, Comunicación. Bloque de comunicados/avisos etiquetado como **"Últimos avisos"**: muestra 2–3 items con acceso al listado completo
**CA3:** Mostrar notificaciones de badge en los accesos directos (mensajes no leídos, acciones pendientes)
**CA4:** Tocar acceso directo navega al módulo correspondiente
**CA5:** Mostrar nombre de usuaria y foto de perfil en la cabecera
**CA6:** Pull-to-refresh para actualizar datos del panel
**CA7:** (SAD) Si existe un **llamamiento pendiente** de respuesta, mostrarlo de forma muy visible en la home con indicación de urgencia y cuenta atrás de caducidad. El CTA de la home lleva al **detalle del llamamiento**; aceptar/rechazar solo es posible dentro del detalle, nunca directamente desde la home
**CA8:** (SAD) Mostrar badge/contador destacado para **documentación pendiente de firma** como elemento de alta prioridad en la home
**CA9:** (SAD) El bloque de servicios del home muestra como máximo el **servicio activo + el siguiente servicio**; si hay más, mostrar el enlace **"Ver más servicios"** en lugar del contador "+2" o similar. En el home se muestra información resumida de cada servicio; tocar una tarjeta navega al detalle completo del servicio (RF-3.2). Se prioriza la reducción de información visible en el home.

**Endpoints API Requeridos:**

- `GET /api/v1/workers/dashboard` — Vista consolidada en una llamada: perfil laboral + servicios activos + anuncios recientes

---

#### RF-2.2: Tablón de Anuncios / Comunicados

**Descripción:**
Sección de contenidos informativos de la empresa hacia las trabajadoras. Incluye dos tipos de contenido:
- **Contenidos fijos**: protocolos de actuación, calendario laboral, PRL, documentos de referencia permanente.
- **Comunicaciones variables**: recordatorios, campañas, formación, novedades.

Se envía notificación push cuando hay nuevo contenido y se muestra un badge de "hay actualización".

**Criterios de Aceptación:**
**CA1:** Listar comunicados diferenciando entre contenidos fijos (protocolo, calendario laboral, PRL, documentos de referencia permanente) y comunicaciones variables (recordatorios, campañas, novedades). El backoffice puede **fijar** contenidos importantes en la parte superior (no necesariamente separados en bloques rígidos)
**CA2:** Mostrar título, fecha y texto de previsualización de cada comunicado
**CA3:** Tocar comunicado para ver detalles completos
**CA4:** Marcar comunicado como leído automáticamente cuando se abre
**CA5:** Indicador visual para comunicados no leídos (badge en menú/tab)
**CA6:** Soporte para imágenes y adjuntos en los detalles
**CA7:** Notificación push cuando se publica un nuevo comunicado
**CA8:** Badge en el icono de la sección indicando contenido nuevo no leído

**Endpoints API Requeridos:**

- `GET /api/v1/announcements` — Listar anuncios (con soporte para fijados)
- `GET /api/v1/announcements/:id` — Obtener detalles del anuncio
- `POST /api/v1/announcements/:id/mark-read` — Marcar como leído

---

#### RF-2.3: Mensajes del Sistema

**Descripción:**
Mensajes de solo lectura de administración a las usuarias (no hay funcionalidad de respuesta).

Se diferenciarán en dos niveles de criticidad, alta se mostrarán diferentes y primero y normal se mostrarán debajo

**Criterios de Aceptación:**
**CA1:** Mostrar lista de mensajes con remitente, asunto, fecha
**CA2:** Indicador visual para mensajes no leídos
**CA3:** Tocar mensaje para ver contenido completo
**CA4:** Marcar como leído automáticamente cuando se abre
**CA5:** Los mensajes no se pueden responder (sin botón de redactar)
**CA6:** Opción de borrar mensajes
**CA7:** Soporte para visualización de adjuntos

**Endpoints API Requeridos:**

- `GET /api/v1/messages/system` — Listar mensajes del sistema (con niveles de criticidad)
- `GET /api/v1/messages/system/:id` — Obtener detalles del mensaje
- `POST /api/v1/messages/system/:id/mark-read` — Marcar como leído
- `DELETE /api/v1/messages/system/:id` — Borrar mensaje

---

### RF-3: Mis Servicios (Gestión de Servicios)

**Se aplica a:** Solo perfil SAD (Felizvita)

#### RF-3.1: Listado de Servicios

**Descripción:**
Mostrar todos los servicios asignados (recurrentes y puntuales) con estado actual.

**Criterios de Aceptación:**
**CA1:** Listar servicios agrupados por estado: Activos, Próximos, Completados
**CA2:** Mostrar información clave del servicio: nombre/código del cliente, dirección, fecha/hora, tipo
**CA3:** Distinción visual entre servicios recurrentes y puntuales
**CA4:** Tocar servicio para navegar a la vista detallada
**CA5:** Pull-to-refresh para actualizar lista
**CA6:** Estado vacío cuando no hay servicios asignados

**Endpoints API Requeridos:**

- `GET /api/v1/workers/services` — Listar todos los servicios (activos, próximos e inactivos en arrays separados)
- `GET /api/v1/workers/services/active` — Solo servicios activos
- `GET /api/v1/workers/services/upcoming` — Solo servicios con fecha de inicio posterior a hoy

---

#### RF-3.2: Detalle del Servicio

**Descripción:**
Información completa sobre un servicio específico incluyendo detalles del cliente, ubicación, plan de cuidados, tareas diarias y documentación.

**Criterios de Aceptación:**
**CA1:** Mostrar información básica del servicio (código, tipo, fechas, horario)
**CA2:** Mostrar información del cliente (nombre, dirección, edad). Información de salud: **pendiente de revisión RGPD** — consultar con legal antes de mostrar medicación u otros datos persistentes de salud en el lado de la cuidadora
**CA3:** Mostrar la **dirección como texto clickable** que abre directamente la app de Maps del dispositivo (Google Maps / Apple Maps). **No se incluye mapa embebido** en la pantalla de detalle. El objetivo es reducir la carga visual de la pantalla.
**CA4:** Mostrar plan de cuidados y **listado descriptivo de tareas** (sin checklist; derivado de la valoración/servicio, gestionado desde backend, no editable por la cuidadora)
**CA5:** Listar documentación asociada (protocolos de cuidado)
**CA6:** Acceso a notas de servicio (RF-3.3)
**CA7:** Acceso al historial de seguimiento de tiempo para este servicio
**CA8:** Mostrar de forma prominente un CTA **"Contacta con tu coordinador / empresa"** (no llamarlo "contacto de emergencia", ya que no es una emergencia real) con el teléfono de coordinación
**CA9:** Acceso directo para **fichar entrada/salida** desde el detalle del servicio (además de home y tab de fichaje)
**CA10:** Botón para **reportar incidencia** del servicio accesible desde el detalle
**CA11:** La visibilidad de determinados campos del servicio (datos del cliente) es **controlable desde backoffice** para respetar la privacidad (cada campo puede marcarse como visible o no visible para la cuidadora)

**Endpoints API Requeridos:**

- `GET /api/v1/workers/services/:id?type=service|extra_service` — Obtener detalles completos del servicio (cliente, ubicación, plan de cuidados, tareas, documentación)

---

#### RF-3.3: Notas de Servicio

**Descripción:**
Las trabajadoras pueden registrar notas sobre la evolución del servicio, tareas completadas e incidencias. Las notas pueden incluir adjuntos de archivos.

**Criterios de Aceptación:**
**CA1:** Mostrar lista cronológica de notas del servicio
**CA2:** Mostrar autora de la nota, fecha/hora, contenido y adjuntos
**CA3:** Añadir nueva nota con entrada de texto multilínea
**CA4:** Adjuntar archivos (fotos, documentos) a las notas
**CA5:** Categorizar notas: Evolución, Tareas, Incidencias, Otras
**CA6:** Borrar notas propias (borrado suave para auditoría)
**CA7:** Notas visibles para coordinadoras inmediatamente

**Endpoints API Requeridos:**

- `GET /api/v1/workers/services/:service_worker_id/notes` — Listar notas del servicio 🔲 pendiente
- `POST /api/v1/workers/services/:service_worker_id/notes` — Añadir nota con adjuntos y categoría 🔲 pendiente
- `PUT /api/v1/workers/services/:service_worker_id/notes/:note_id` — Editar nota propia 🔲 pendiente
- `DELETE /api/v1/workers/services/:service_worker_id/notes/:note_id` — Borrar nota propia (borrado suave) 🔲 pendiente

---

#### RF-3.4: Llamadas de Servicio (Llamamientos)

**Descripción:**
Las trabajadoras reciben notificaciones de llamamientos para turnos disponibles. El mismo llamamiento puede enviarse a varias trabajadoras simultáneamente; la primera en aceptar lo recibe y el resto queda desactivado (gestión desde backoffice). El tiempo límite de exposición del llamamiento es configurable desde backoffice. Tanto la **aceptación como el rechazo requieren firma digital** de la trabajadora. **El acceso a aceptar/rechazar es exclusivo desde el detalle del llamamiento** (nunca directamente desde la home); una vez en el detalle, la trabajadora no puede salir sin haber tomado una decisión.

**Criterios de Aceptación:**
**CA1:** Listar todas las llamadas de servicio recibidas con estado (pendiente, aceptada, rechazada, caducada/desactivada)
**CA2:** Mostrar información básica de la llamada: código de servicio, fecha/hora, ubicación, urgencia
**CA3:** Tocar llamada para ver detalles completos (más campos que la información básica)
**CA4:** Aceptar llamada con diálogo donde la trabajadora debe **firmar digitalmente** con el dedo; el copy de aceptación debe ser claro e inequívoco (solicitar textos oficiales a negocio/legal)
**CA5:** Rechazar llamada con selección obligatoria de motivo **y firma digital** de la trabajadora; el copy de rechazo debe ser explícito y distinguirse claramente del de aceptación
**CA6:** Motivos de rechazo: No disponible, Demasiado lejos, Motivos personales, Otros (con campo de texto)
**CA7:** Notificación push cuando se recibe nueva llamada
**CA8:** Las llamadas caducan automáticamente tras el tiempo límite configurado desde backoffice; si no hay respuesta puede computar como rechazo por inacción (pendiente de revisión legal)
**CA9:** Cuenta atrás visual para llamadas pendientes
**CA10:** Cuando un llamamiento caduca o es aceptado por otra trabajadora, mostrarlo como desactivado/no disponible en la lista
**CA11:** Una vez dentro del detalle del llamamiento, la navegación hacia atrás queda **bloqueada hasta que la trabajadora acepte o rechace** (sin botón de retroceso hasta decisión final)

**Endpoints API Requeridos:**

- `GET /api/v1/service-calls` — Listar llamadas de servicio con estado
- `GET /api/v1/service-calls/:id` — Obtener detalles completos de la llamada
- `POST /api/v1/service-calls/:id/accept` — Aceptar llamada (incluye firma digital)
- `POST /api/v1/service-calls/:id/reject` — Rechazar llamada (incluye motivo y firma digital)

---

#### RF-3.5: Historial de Servicios

**Descripción:**
Ver lista histórica de servicios completados y llamadas de servicio pasadas. Distribución de llamamientos: en la **Home** se muestran únicamente los llamamientos **pendientes de respuesta**; el **historial completo** de todos los llamamientos (con su resultado: aceptado, rechazado, caducado/desactivado) se muestra en esta sección.

**Criterios de Aceptación:**
**CA1:** Listar servicios completados con fechas y nombres de clientes
**CA2:** Mostrar total horas trabajadas por servicio
**CA3:** Filtrar por rango de fechas
**CA4:** Tocar para ver detalles de servicio archivado (solo lectura)
**CA5:** Mostrar el **historial completo de llamamientos** con su resultado final (aceptado, rechazado, caducado, desactivado)

**Endpoints API Requeridos:**

- `GET /api/v1/workers/services/history` — Historial de servicios completados
- `GET /api/v1/service-calls` — Listar llamamientos con filtro por estado (incluye historial completo)

---


#### RF-3.6: ~~Seguimiento PIA~~ *(eliminado — funcionalidad descartada)*

---

#### RF-3.7: Nuevo Servicio Asignado (Contratos Indefinidos)

**Se aplica a:** Solo perfil SAD (Felizvita) — trabajadoras con contrato indefinido

**Descripción:**
Para trabajadoras con contrato **indefinido**, la asignación de un nuevo servicio no es un llamamiento (no requiere aceptación/rechazo). Se trata de una **notificación informativa** que comunica que un nuevo servicio ha sido asignado. Se debe registrar que la trabajadora ha recibido/visto la notificación, y existe la posibilidad de generar una incidencia si la trabajadora no puede atender el servicio.

**Criterios de Aceptación:**
**CA1:** Recibir notificación push "Nuevo servicio asignado" con deeplink al detalle del servicio
**CA2:** Mostrar el nuevo servicio en home de forma visible (elemento diferenciado de los llamamientos)
**CA3:** Registrar interacción "visto/recibido" cuando la trabajadora abre el detalle del servicio
**CA4:** Desde el detalle del nuevo servicio, opción de **generar una incidencia** si la trabajadora no puede atender el servicio (no es un rechazo formal, sino una comunicación a coordinación)
**CA5:** Distinción visual y conceptual entre servicios **puntuales** (con fecha de inicio y fin definidas; pueden ser de días o semanas) y servicios **recurrentes** (sin fecha de fin; p.ej. martes y jueves de forma continuada)

**Endpoints API Requeridos:**

- `GET /api/v1/workers/services/:id?type=service|extra_service` — Obtener detalles del servicio asignado
- `POST /api/v1/workers/services/:service_worker_id/acknowledge` — Confirmar recepción del nuevo servicio (estado: pending→acknowledged)

---

### RF-4: Control Horario (Seguimiento de Tiempo)

**Se aplica a:** Solo perfil SAD (Felizvita)

#### RF-4.1: Fichar Entrada/Salida

**Descripción:**
Las trabajadoras fichan entrada cuando comienzan un servicio y fichan salida cuando terminan. La geolocalización se captura. El fichaje es accesible desde la **home**, el **detalle del servicio** y el **tab de fichaje**. **No se permite fichaje manual** desde la app de la trabajadora; las correcciones se gestionan internamente desde backoffice.

**Criterios de Aceptación:**
**CA1:** Acción de fichaje accesible desde home, detalle del servicio y tab de fichaje
**CA2:** Seleccionar servicio de la lista de servicios activos antes de fichar entrada
**CA3:** Capturar coordenadas GPS al fichar entrada/salida
**CA4:** Mostrar advertencia si la precisión de la ubicación es baja (<50m); esperar máximo 2s antes de permitir continuar
**CA5:** Permitir fichar incluso sin precisión de ubicación óptima (trazabilidad mantenida, sin bloqueo por ubicación)
**CA6:** Mostrar contador de tiempo transcurrido mientras está fichada
**CA7:** Mostrar botón "Fichar salida" cuando se ha fichado entrada
**CA8:** Diálogo de confirmación al fichar salida
**CA9:** El servidor envía una **notificación push N minutos antes del inicio del servicio** (N configurable en servidor), momento a partir del cual la trabajadora ya puede fichar. El mensaje de la notificación debe incluir el nombre de la trabajadora y el nombre del receptor del servicio (p. ej. "Buenos días [nombre], ya puedes fichar para el servicio del Sr./Sra. [nombre_receptor]")
**CA10:** No bloquear fichajes entre servicios del mismo día (mañana/tarde); gestionar inicio/fin de forma independiente por servicio
**CA11:** Opción para reportar una **incidencia de fichaje** (p. ej. no ha podido ir/fichar) directamente desde la pantalla de fichaje. También opción de **solicitar una ausencia** desde la misma pantalla para evitar confusión entre incidencia operativa y ausencia de la trabajadora
**CA12:** No se permite fichaje manual desde la app; las correcciones de fichaje se gestionan desde backoffice
**CA13:** El botón de fichaje de entrada se activa **30 minutos antes del inicio del servicio**; fuera de esa ventana aparece deshabilitado con indicación visual del tiempo restante
**CA14:** El botón de fichaje muestra **estados dinámicos según la hora**: "Disponible en X min", "Fichar entrada", "Fichada · en servicio", "Fichar salida", "Servicio finalizado"
**CA15:** Si la trabajadora no ficha la **salida** tras finalizar el servicio, mostrar un **warning visible** (banner o notificación in-app) que recuerde la acción pendiente. Este warning **no bloquea** la navegación ni el acceso al resto de la app.

**Endpoints API Requeridos:**

- `POST /api/v1/workers/time-tracking/clock-in` — Fichar entrada (body: `service_worker_id`, `type: worker|rest`); envío de coordenadas GPS 🔲 pendiente de confirmar con backend (no documentado en Swagger v1.6.0)
- `POST /api/v1/workers/time-tracking/clock-out` — Fichar salida (body: `service_worker_id`, `type: worker|rest`); envío de coordenadas GPS 🔲 pendiente de confirmar con backend; calcula horas trabajadas
- `GET /api/v1/workers/time-tracking/current-status` — Estado de fichaje de todos los servicios activos
- `GET /api/v1/workers/time-tracking/current-status/:service_worker_id` — Estado de fichaje de un servicio concreto

---

#### RF-4.2: Historial de Seguimiento de Tiempo

**Descripción:**
Muestra todos los registros de entrada y salida agrupados por servicio y la duración.

**Criterios de Aceptación:**
**CA1:** Listar todas las entradas de tiempo agrupadas por servicio y por días
**CA2:** Mostrar la fecha, la hora de entrada, la hora de salida y la duración de cada registro
**CA3:** Filtrar por rango de fechas
**CA4:** Filtrar por servicio
**CA5:** No mostrar al trabajador conteos de horas extra ni diferencias respecto a las horas contratadas; esta información queda reservada para gestión interna

**Endpoints API Requeridos:**

- `GET /api/v1/workers/time-tracking/history?service_worker_id=X[&month=MM&year=YYYY]` — Sin mes: resumen mensual; con mes: detalle diario de fichajes

---

### RF-5: Incidencias

**Se aplica a:** Solo perfil SAD (Felizvita)

#### RF-5.1: Reportar Incidencia

**Descripción:**
Las trabajadoras pueden reportar **incidencias del servicio o del usuario** (incidencias médicas, de seguridad, materiales, etc.), categorizadas por tipo con descripción y adjuntos opcionales según el tipo. Estas incidencias son principalmente del servicio/usuario atendido, no de la propia cuidadora (las ausencias de la trabajadora tienen su propio flujo en RF-8). Excepcionalmente se incluye el tipo "Incidencia de fichaje / No asistencia" para reportar problemas operativos de la propia cuidadora relacionados directamente con la prestación del servicio. La taxonomía y el copy deben dejar claro este punto.

**Criterios de Aceptación:**
**CA1:** Seleccionar tipo de incidencia de lista predefinida (Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros)
**CA2:** Seleccionar servicio relacionado (si la incidencia ocurre durante el servicio)
**CA3:** Introducir descripción de la incidencia (obligatorio, mínimo 20 caracteres)
**CA4:** Adjuntar fotos de cámara o galería (opcional, máximo 5)
**CA5:** Adjuntar documentos (opcional, máximo 3)
**CA6:** Mostrar tamaño estimado de subida antes de enviar
**CA7:** Comprimir imágenes automáticamente
**CA8:** Mostrar confirmación de envío
**CA9:** Incidencia inmediatamente visible para coordinadoras

**Endpoints API Requeridos:**

- `POST /api/v1/workers/incidents` — Reportar incidencia (con tipo, servicio, descripción y adjuntos)

---

#### RF-5.2: Historial de Incidencias

**Descripción:**
Ver todas las incidencias reportadas con su estado actual y respuestas de coordinadoras.

**Criterios de Aceptación:**
**CA1:** Listar incidencias en orden cronológico inverso
**CA2:** Mostrar número de incidencia, tipo, fecha, estado
**CA3:** Valores de estado: Reportada, En revisión, Resuelta, Cerrada
**CA4:** Tocar incidencia para ver detalles completos
**CA5:** Ver comentarios/respuestas de coordinadoras
**CA6:** Filtrar por estado
**CA7:** Filtrar por rango de fechas
**CA8:** Buscar por número de incidencia o descripción

**Endpoints API Requeridos:**

- `GET /api/v1/workers/incidents` — Listar incidencias (con filtros por estado, fechas y búsqueda)
- `GET /api/v1/workers/incidents/:id` — Obtener detalles de la incidencia (incluye comentarios de coordinadoras)

---

### RF-6: Ofertas (Ofertas de Trabajo)

**Se aplica a:** Solo perfil Hogar (CUIDEO)

#### RF-6.1: Navegar Ofertas

**Descripción:**
Las trabajadoras del hogar pueden consultar las ofertas de trabajo disponibles filtradas por ubicación, horario y requisitos.

**Criterios de Aceptación:**
**CA1:** Listar ofertas disponibles en formato de tarjeta
**CA2:** Mostrar resumen de la oferta: título del trabajo, ubicación (código postal/ciudad), horario, tarifa horaria
**CA3:** Filtrar por código postal/zona
**CA4:** Filtrar por horario (mañana, tarde, noche, madrugada, 24h)
**CA5:** Filtrar por rango de fecha de inicio
**CA6:** Ordenar por: más recientes, ubicación más cercana, tarifa más alta
**CA7:** Tocar oferta para ver detalles completos
**CA8:** Botón «Aplicar» en cada tarjeta de oferta
**CA9:** Insignia que muestra "Nuevo" para ofertas publicadas en las últimas 48h
**CA10:** Estado vacío cuando no hay ofertas coincidentes

**Endpoints API Requeridos:**

- `GET /api/v1/offers` — Listar ofertas disponibles (con filtros por zona, horario, fecha y ordenación)
- `GET /api/v1/offers/:id` — Obtener detalles completos de la oferta

---

#### RF-6.2: Solicitar Oferta

**Descripción:**
Las trabajadoras pueden solicitar ofertas de trabajo. La solicitud se envía a coordinadoras para revisión.

**Criterios de Aceptación:**
**CA1:** Botón «Aplicar» en la pantalla de detalle de la oferta
**CA2:** Muestra un diálogo de confirmación con el resumen de la oferta
**CA3:** Envía la solicitud con un solo toque
**CA4:** Mostrar mensaje de éxito después de la solicitud
**CA5:** Prevenir solicitudes duplicadas a la misma oferta
**CA6:** La solicitud incluye automáticamente los datos del perfil de la trabajadora
**CA7:** La trabajadora recibe notificación de confirmación

**Endpoints API Requeridos:**

- `POST /api/v1/offers/:id/apply` — Solicitar oferta de trabajo

---

#### RF-6.3: Mis solicitudes

**Descripción:**
Ver todas las solicitudes presentadas con su estado actual.

**Criterios de Aceptación:**
**CA1:** Listar solicitudes en orden cronológico inverso
**CA2:** Mostrar título de la oferta, ubicación, fecha de solicitud, estado
**CA3:** Valores de estado: Pendiente, En revisión, Aceptada, Rechazada, Oferta cerrada
**CA4:** Tocar solicitud para ver detalles de la oferta
**CA5:** Distinción visual para solicitudes aceptadas
**CA6:** Filtrar por estado
**CA7:** Opción de retirar solicitud pendiente
**CA8:** Recibir notificación push en cambio de estado

**Endpoints API Requeridos:**

- `GET /api/v1/applications` — Listar solicitudes (con filtro por estado)
- `DELETE /api/v1/applications/:id` — Retirar solicitud pendiente

---

### RF-7: Mi Disponibilidad (Gestión de Disponibilidad)

**Se aplica a:** Ambos perfiles

> **Contexto de rediseño (v1.8 — 19/03/2026):** El modelo anterior basado en zonas se ha redefinido para alinear la UX con la operativa real de asignación de servicios y las reglas legales. La disponibilidad es ahora una **declaración de tiempo libre dentro de una ventana operativa**, usada por el sistema para asignar servicios, no para que la trabajadora autogestione su trabajo.

#### RF-7.1: Calendario de Disponibilidad

**Descripción:**
Pantalla principal de disponibilidad. Combina visualización y edición en una única interfaz de calendario. La trabajadora puede ver su disponibilidad semanal y modificarla directamente desde la misma pantalla, sin navegar a pantallas secundarias.

La pantalla se estructura en dos áreas:

1. **Calendario semanal (área principal):** Vista de la semana (Lun–Dom) donde se visualizan y gestionan los slots de disponibilidad creados para cada día. Cada slot se muestra como un bloque horario con indicación visual de su tipo (**Disponible** / **No disponible** / **Activa**). Los slots de distintos tipos pueden solaparse visualmente en el calendario.

2. **Panel de franjas rápidas (lateral o inferior):** Conjunto de botones de aplicación rápida con las franjas predefinidas del sistema: **Mañana, Tarde, Noche, Interna, Finde**. Al pulsar una franja con un día seleccionado, se crea automáticamente un slot de disponibilidad con el rango horario correspondiente a esa franja.

Adicionalmente, la trabajadora puede crear slots personalizados indicando hora de inicio y hora de fin, y eligiendo si el slot es de tipo **Disponible** o **No disponible**.

**Tipos de entradas en el calendario:**
- **Disponible:** Franjas que la trabajadora declara como disponibles. Editables.
- **No disponible:** Franjas que la trabajadora declara como no disponibles dentro de un rango mayor de disponibilidad (p. ej. una franja corta de excepción). Editables. Pueden solaparse con franjas "Disponible".
- **Activa:** Horas que por planificación tienen un servicio asignado. Provienen del sistema de planificación y son de **solo lectura** (no editables ni eliminables desde la app). Se muestran solapadas sobre las franjas "Disponible" correspondientes.

**Criterios de Aceptación:**
**CA1:** Mostrar en la cabecera la información de **horas trabajadas vs. horas de contrato** en formato prominente: `30 / 40 h` o mensaje equivalente `"Te faltan X horas"`
**CA2:** Vista semanal tipo calendario (Lun–Dom) que muestra los slots de disponibilidad creados para cada día como bloques horarios con color diferenciado según tipo: **Disponible** (p. ej. verde), **No disponible** (p. ej. rojo/gris), **Activa** (p. ej. azul). Los slots de distintos tipos pueden solaparse visualmente
**CA3:** Al seleccionar un día en el calendario, se activa el panel de franjas rápidas y el formulario de creación de slot personalizado para ese día
**CA4:** El **panel de franjas rápidas** muestra las franjas predefinidas: **Mañana, Tarde, Noche, Interna, Finde**. La franja **Madrugada queda eliminada**. Pulsar una franja crea inmediatamente un slot de tipo "Disponible" con el rango horario de esa franja para el día seleccionado
**CA5:** El **formulario de slot personalizado** permite introducir hora de inicio y hora de fin (inputs tipo time picker) y seleccionar el tipo: **Disponible** o **No disponible**. Permite crear múltiples slots por día. Se permiten solapamientos entre slots de **distinto tipo** (p. ej. una franja amplia de disponibilidad con una excepción corta de no disponibilidad dentro). **No se permiten solapamientos entre slots del mismo tipo** en el mismo día (dos franjas "Disponible" o dos "No disponible" no pueden solaparse); la API devuelve error en este caso
**CA6:** Los slots de tipo "No disponible" bloquean la asignación de servicios en ese rango horario, aunque haya disponibilidad declarada en la misma franja. Esta lógica la gestiona el backend
**CA7:** Los slots de tipo **"Activa"** representan horas con servicio asignado por planificación. Se muestran solapados sobre las franjas "Disponible" correspondientes. Son de **solo lectura**: no se pueden editar ni eliminar desde la app
**CA8:** Tocar un slot de tipo "Disponible" o "No disponible" permite editarlo (modificar hora inicio/fin o tipo) o eliminarlo. Tocar un slot "Activa" solo muestra información (no permite edición)
**CA9:** No se implementa drag & drop; toda la interacción es mediante selección + inputs
**CA10:** La ventana operativa de cada día está basada en **12 horas desde el inicio de jornada**, respetando el descanso mínimo legal. Esta lógica la provee la API; la app puede mostrarla de forma informativa pero no la calcula
**CA11:** Los cambios se guardan de forma inmediata al confirmar cada slot (no hay botón "guardar todo")
**CA12:** Pull-to-refresh para sincronizar el estado con el servidor
**CA13:** Notificación de recordatorio si la disponibilidad no se actualiza en 30 días

**Reglas de negocio aplicables:**
Estas reglas las valida y gestiona exclusivamente el servidor. La app no las calcula ni las interpreta; si un slot no cumple alguna de ellas, la API devuelve el error correspondiente y la app lo muestra al usuario.
- Máximo 8 horas de trabajo por día
- Mínimo 12 horas de descanso entre jornadas
- La disponibilidad declarada se usa para completar las horas del contrato mediante asignación automática de servicios

**Endpoints API Requeridos:**

- `GET /api/v1/workers/availability` — Horas contratadas, asignadas y fichadas esta semana + franjas de disponibilidad, no disponibilidad y entradas activas (de planificación, solo lectura)
- `POST /api/v1/workers/availability/available-slots` — Crear franja de disponibilidad (`day` 1-7 ISO 8601, `start_time` HH:MM, `end_time` HH:MM); se permiten solapamientos con franjas de no disponibilidad
- `PUT /api/v1/workers/availability/available-slots/:id` — Actualizar franja de disponibilidad
- `DELETE /api/v1/workers/availability/available-slots/:id` — Eliminar franja de disponibilidad
- `POST /api/v1/workers/availability/unavailable-slots` — Crear franja de no disponibilidad (`day` 1-7 ISO 8601, `start_time` HH:MM, `end_time` HH:MM); se permiten solapamientos con franjas disponibles
- `PUT /api/v1/workers/availability/unavailable-slots/:id` — Actualizar franja de no disponibilidad
- `DELETE /api/v1/workers/availability/unavailable-slots/:id` — Eliminar franja de no disponibilidad

---

### RF-8: Mis Ausencias (Gestión de Ausencias)

**Se aplica a:** Solo perfil SAD (Felizvita)

#### RF-8.1: Solicitar Ausencia

**Descripción:**
Las trabajadoras del SAD pueden solicitar tiempo libre (vacaciones, baja médica, días personales) con documentación justificativa.

**Criterios de Aceptación:**
**CA1:** Seleccionar tipo de ausencia: Vacaciones, Permiso personal, Baja médica, Baja voluntaria, Asuntos propios, Otros
**CA2:** Seleccionar rango de fechas (fecha de inicio, fecha final)
**CA3:** Opciones de medio día para fechas de inicio/final
**CA4:** Introducir motivo/descripción (obligatorio para algunos tipos)
**CA5:** Adjuntar certificado médico (obligatorio para baja médica >3 días)
**CA6:** Mostrar saldo de vacaciones disponible antes de enviar
**CA7:** Advertencia si las fechas solicitadas entran en conflicto con servicios asignados
**CA8:** Enviar solicitud para aprobación
**CA9:** Recibir notificación Push de confirmación

**Endpoints API Requeridos:**

- `POST /api/v1/workers/absences` — Solicitar ausencia (con tipo, fechas, motivo y adjuntos)

---

#### RF-8.2: Historial de Ausencias

**Descripción:**
Ver todas las solicitudes de ausencia con estado y saldo de vacaciones restante.

**Criterios de Aceptación:**
**CA1:** Listar ausencias en orden cronológico inverso
**CA2:** Mostrar tipo de ausencia, fechas, recuento de días, estado
**CA3:** Valores de estado: Pendiente, Aprobada, Rechazada, Cancelada
**CA4:** Tocar ausencia para ver detalles y comentarios de coordinadora
**CA5:** Cancelar solicitudes de ausencia pendientes
**CA6:** Filtrar por estado
**CA7:** Filtrar por tipo de ausencia
**CA8:** Filtrar por año
**CA9:** Mostrar **contadores por tipo de ausencia** (p. ej. vacaciones: asignación anual total, días utilizados, días pendientes de aprobación, días disponibles; otros tipos según aplique)
**CA10:** Las vacaciones se computan por **días naturales** (pendiente de confirmar con cliente/legal)

**Endpoints API Requeridos:**

- `GET /api/v1/workers/absences` — Listar ausencias con contadores por tipo y saldo de vacaciones (filtros por estado, tipo y año)
- `GET /api/v1/workers/absences/:id` — Obtener detalles de la ausencia y comentarios de coordinadora
- `DELETE /api/v1/workers/absences/:id` — Cancelar solicitud de ausencia pendiente

---

### RF-9: Perfil (Gestión de Perfil)

**Se aplica a:** Ambos perfiles

#### RF-9.1: Ver y Editar Perfil

**Descripción:**
Las trabajadoras pueden ver su información personal y de perfil. Los **datos "core"** (nombre, apellidos, DNI/NIE, etc.) provienen del sistema y en general **no son editables** directamente desde la app; en los campos que aplique, se permitirá enviar una **"propuesta de cambio"** con documentación justificativa para que el backoffice valide el cambio.

**Criterios de Aceptación:**
**CA1:** Ver información actual del perfil organizada en secciones:
- Información Personal: Nombre, Email, Teléfono, Dirección de domicilio *(editable)*, Fecha de Nacimiento, Número de DNI/NIE
- Profesional: Años de experiencia, Especializaciones, Certificaciones
- Educación: Títulos, Cursos de formación
- Idiomas: Idioma + nivel de competencia
- Contrato (solo SAD): Tipo (Indefinido, Fijo Discontinuo), Fecha de inicio ⚠️ *El Swagger v1.6.0 devuelve `contract_type: "Tiempo completo" | "Tiempo parcial"` — pendiente alinear con backend si son el mismo campo o dos dimensiones distintas*

**CA2:** Datos core (nombre, apellidos, DNI/NIE, etc.) son de solo lectura; la **dirección de domicilio es un campo editable** (ya que afecta a la zona de disponibilidad); para los campos editables, mostrar botón de edición por sección
**CA3:** Validar campos obligatorios
**CA4:** Validación de formato de teléfono
**CA5:** Validación del formato de email
**CA6:** Validación del formato de DNI/NIE
**CA7:** Guardar cambios por sección (solo en campos editables)
**CA8:** Indicador de **porcentaje de completitud del perfil** visible en la pantalla principal del perfil
**CA9:** Los campos del perfil pueden cambiar (nota en la UI para flexibilidad)
**CA10:** Para DNI/NIE: mostrar la **fecha de vencimiento** y flujo de "proponer nueva fecha + adjuntar documento" (sin editar el dato existente directamente; el backoffice valida el cambio)
**CA11:** (Solo Hogar) Introducir un **flujo de completar perfil**: la trabajadora puede navegar libremente por la app con el perfil incompleto, pero al intentar **aplicar a una oferta**, se muestra una advertencia o bloqueo informando de los campos obligatorios pendientes, con acceso directo a completarlos
**CA12:** (Solo Hogar) El porcentaje de completitud del perfil debe ser visible desde la home para incentivar su cumplimentación antes de aplicar


**Endpoints API Requeridos:**

- `GET /api/v1/workers/profile` — Obtener perfil completo (personal, profesional, idiomas, contrato)
- `PUT /api/v1/workers/profile/personal-info` — Actualizar información personal (campos editables como dirección)
- `PUT /api/v1/workers/profile/professional` — Actualizar información profesional
- `POST /api/v1/workers/profile/languages` — Añadir idioma
- `DELETE /api/v1/workers/profile/languages/:id` — Eliminar idioma

---

#### RF-9.2: Foto de Perfil

**Descripción:**
Subir y actualizar foto de perfil. La foto es **voluntaria**; la app funciona correctamente sin ella.

**Criterios de Aceptación:**
**CA1:** Mostrar foto de perfil actual o placeholder
**CA2:** Tocar foto para cambiar
**CA3:** Elegir foto de galería o hacer nueva foto
**CA4:** Recortar/redimensionar foto antes de subir (relación de aspecto cuadrada)
**CA5:** Compresión automática
**CA6:** Tamaño máximo de archivo 5MB
**CA7:** Formatos aceptados: JPG, PNG
**CA8:** Mostrar progreso de subida
**CA9:** Actualizar foto en toda la aplicación inmediatamente

**Endpoints API Requeridos:**

- `POST /api/v1/workers/profile/photo` — Subir foto de perfil
- `DELETE /api/v1/workers/profile/photo` — Borrar foto de perfil

---

#### RF-9.3: Documentos

**Descripción:**
Ver, subir y gestionar documentos clasificados en dos categorías: **Documentación personal** (DNI/NIE, certificados, etc.) y **Documentación laboral** (contrato, nóminas, llamamientos firmados, etc.). La estructura de carpetas y tipos de documento es **dinámica y configurable desde backoffice**.

**Criterios de Aceptación:**
**CA1:** Mostrar documentos organizados en dos categorías: Documentación personal y Documentación laboral
**CA2:** Las carpetas y tipos de documento dentro de cada categoría son configurables desde backoffice (estructura dinámica)
**CA3:** Tocar documento para ver (visor de PDF en la aplicación, opción de descarga)
**CA4:** **Documentación personal** (DNI/NIE, discapacidad, certificados, etc.): la trabajadora puede **subir y reemplazar** documentos (seleccionar tipo, elegir archivo del dispositivo o hacer foto, descripción opcional; formatos: PDF, DOC, DOCX, JPG, PNG; máx. 10MB; compresión automática de imágenes). **No se permite eliminar** documentos personales; solo reemplazar/actualizar
**CA5:** **Documentación laboral** (contrato/anexos, nóminas, llamamientos firmados, otros de firma rápida): la trabajadora **no puede subir ni eliminar** documentos; solo consultar, descargar y firmar cuando corresponda. La gestión es exclusiva del backoffice
**CA6:** Acceso rápido a **Documentos** desde la **home** (especialmente para nóminas); el acceso desde home conduce a una pantalla unificada con ambas categorías (personal + laboral)
**CA7:** Recibir avisos de caducidad para DNI/certificados desde servidor
**CA8:** Indicador de documentos obligatorios
**CA9:** Badge/aviso en la sección (y en home) para **documentación pendiente de firma**


**Endpoints API Requeridos:**

- `GET /api/v1/workers/profile/documents` — Listar documentos (personal + laboral, con estructura dinámica de carpetas)
- `POST /api/v1/workers/profile/documents` — Subir documento personal (tipo, archivo, descripción)
- `PUT /api/v1/workers/profile/documents/:id` — Reemplazar documento personal existente
- `POST /api/v1/workers/profile/documents/:id/sign` — Firmar documento laboral

---

#### RF-9.4: Firma Digital

**Descripción:**
Capturar firma manuscrita en la pantalla para firma de documentos.

**Criterios de Aceptación:**
**CA1:** Mostrar lienzo de firma en blanco
**CA2:** Capturar entrada táctil/stylus para dibujar firma
**CA3:** Botón borrar/reiniciar firma
**CA4:** Previsualizar firma antes de guardar
**CA5:** Guardar firma como archivo PNG
**CA6:** Firma almacenada en el perfil y documentos
**CA7:** Usar firma guardada para futuras firmas de documentos
**CA8:** Opción de redibujar firma en cualquier momento

**Endpoints API Requeridos:**

- `POST /api/v1/workers/profile/signature` — Guardar firma (imagen PNG)
- `GET /api/v1/workers/profile/signature` — Obtener firma guardada

---

#### RF-9.5: Estado del Contrato

**Se aplica a:** Solo perfil SAD (Felizvita)

**Descripción:**
Mostrar información del contrato actual para trabajadoras SAD.

**Criterios de Aceptación:**
**CA1:** Mostrar tipo de contrato: Indefinido, Fijo Discontinuo ⚠️ *El Swagger v1.6.0 devuelve `contract_type: "Tiempo completo" | "Tiempo parcial"` — pendiente alinear con backend*
**CA2:** Mostrar fecha de inicio del contrato
**CA3:** Mostrar número de empleada
**CA4:** Enlace para descargar PDF del contrato actual
**CA5:** Información del contrato de solo lectura (gestionada por admin)

**Endpoints API Requeridos:**

- `GET /api/v1/workers/profile/contract` — Obtener información del contrato (tipo, fecha inicio, número empleada, enlace PDF) 🔲 pendiente

---

### RF-10: Comunicación

**Se aplica a:** Ambos perfiles

#### RF-10.1: Inicio de Nueva Conversación

**Descripción:**
Desde la app, la trabajadora accede directamente al chat de **Coordinación** (punto de entrada único). El enrutamiento interno a los departamentos específicos se gestiona desde el backoffice de forma transparente para la trabajadora. Al iniciar una conversación, la usuaria selecciona un **asunto predefinido** para facilitar el enrutado interno y los filtros del backoffice.

**Criterios de Aceptación:**
**CA1:** Al crear una nueva conversación, mostrar una selección de **asuntos predefinidos**:
- Vacaciones / Ausencia
- Nómina / Facturación
- Sobre un servicio
- Documentación
- Consulta general
- Otros

**CA2:** La selección del asunto determina el enrutado interno en el backoffice (transparente para la trabajadora)
**CA3:** La conversación se presenta en formato **chat** (inicio claro, primer mensaje obligatorio)
**CA4:** Mostrar el asunto seleccionado en la cabecera de la conversación
**CA5:** Opcionalmente, mostrar un **código de ticket** en la cabecera si el backend lo proporciona
**CA6:** La trabajadora siempre ve el chat como una conversación con "Coordinación", independientemente del enrutado interno
**CA7:** Al crear la conversación, opción de **enlazar contexto** (seleccionar servicio u oferta relacionados) para facilitar la gestión por el backoffice


**Endpoints API Requeridos:**

- `POST /api/v1/workers/communication/conversations` — Iniciar nueva conversación (con asunto predefinido, mensaje inicial y contexto opcional)

---

#### RF-10.2: Listado de Conversaciones

**Descripción:**
Ver todos los hilos de conversación con estado de leído/no leído y previsualización del último mensaje. Las conversaciones pueden ser **cerradas por el equipo de backoffice**, pasando a modo histórico de solo lectura (la trabajadora ya no puede escribir).

**Criterios de Aceptación:**
**CA1:** Listar conversaciones en orden cronológico inverso (por último mensaje)
**CA2:** Mostrar asunto, previsualización del último mensaje y marca de tiempo
**CA3:** Indicador visual para mensajes no leídos (bold, badge)
**CA4:** Indicador visual diferenciado para conversaciones **cerradas** (p. ej. etiqueta "Cerrada" o icono de candado)
**CA5:** Tocar conversación para abrir hilo (tanto abiertas como cerradas, en modo histórico estas últimas)
**CA6:** Pull-to-refresh
**CA7:** Buscar conversaciones
**CA8:** Opción de borrar conversación (con confirmación)

**Endpoints API Requeridos:**

- `GET /api/v1/workers/communication/conversations` — Listar conversaciones (con estado abierta/cerrada, búsqueda)
- `DELETE /api/v1/workers/communication/conversations/:id` — Borrar conversación

---

#### RF-10.3: Hilo de Conversación

**Descripción:**
Enviar y recibir mensajes dentro de un hilo de conversación. Soporta mensajes de texto y mensajes específicos de contexto (por ejemplo, relacionados con un servicio). Las conversaciones pueden ser **cerradas por el equipo de backoffice**; en ese caso, la trabajadora puede consultar el historial completo pero no puede escribir nuevos mensajes.

**Criterios de Aceptación:**
**CA1:** Mostrar todos los mensajes en orden cronológico
**CA2:** Diferenciar los mensajes de la trabajadora de los mensajes de coordinación (alineación, colores)
**CA3:** Mostrar marca de tiempo del mensaje
**CA4:** Mostrar estado de entrega/lectura para mensajes enviados
**CA5:** Campo de entrada de texto en la parte inferior (solo si la conversación está **abierta**)
**CA6:** Botón de enviar (solo si la conversación está **abierta**)
**CA7:** Si la conversación está **cerrada**: ocultar el campo de entrada, mostrar un aviso de "Conversación cerrada" y permitir consultar el historial completo en modo lectura
**CA8:** Desplazamiento automático al último mensaje
**CA9:** Cargar mensajes más antiguos al desplazar hacia arriba (paginación)
**CA10:** Enlazar contexto (servicio/oferta) al mensaje si procede
**CA11:** Actualizaciones de mensajes en tiempo real (realtime database)

**Endpoints API Requeridos:**

- `GET /api/v1/workers/communication/conversations/:id/messages` — Obtener mensajes de la conversación (con paginación)
- `POST /api/v1/workers/communication/conversations/:id/messages` — Enviar mensaje (con contexto opcional)
- `POST /api/v1/workers/communication/conversations/:id/mark-read` — Marcar conversación como leída

---

### RF-11: Notificaciones (Notificaciones Push)

**Se aplica a:** Ambos perfiles

#### RF-11.1: Entrega de Notificaciones Push

**Descripción:**
Recibir notificaciones push para eventos importantes con capacidad de tocar y navegar a la sección relevante de la aplicación (deeplink).

**Criterios de Aceptación:**
**CA1:** Solicitar permiso de notificaciones push **después del primer login**, antes del onboarding, para vincular el token FCM al usuario concreto
**CA2:** Registrar token FCM del dispositivo con el backend
**CA3:** Recibir notificaciones push cuando la aplicación está:
- Primer plano (mostrar alerta dentro de la aplicación)
- Segundo plano (mostrar notificación del sistema)
- Apagada (mostrar notificación del sistema)
    **CA4:** La notificación incluye título, cuerpo, icono
    **CA5:** Tocar notificación abre aplicación en pantalla específica vía deeplink


**Tipos de Notificaciones:**

- Nuevo mensaje recibido
- Conversación cerrada por coordinación (deeplink al historial de la conversación)
- Llamada de servicio disponible
- Cambio de estado de la solicitud
- Cambio de estado de solicitud de ausencia
- Servicio comenzando pronto (ventana de fichaje abierta)
- Servicio próximo mañana
- Documento caducando pronto
- Actualización de incidencia
- Nuevo comunicado en el tablón


**Endpoints API Requeridos:**

- `POST /api/v1/workers/devices/register` — Registrar dispositivo para notificaciones push
- `PUT /api/v1/workers/devices/:device_id/fcm-token` — Actualizar token FCM
- `DELETE /api/v1/workers/devices/:device_id` — Dar de baja dispositivo
- `GET /api/v1/workers/notifications` — Listar historial de notificaciones
- `PUT /api/v1/workers/notifications/mark-all-read` — Marcar todas las notificaciones como leídas

---

#### RF-11.2: Notificaciones Automáticas del Sistema

**Descripción:**
El sistema envía automáticamente notificaciones de recordatorio programadas para acciones importantes.

**Criterios de Aceptación:**
**CA1:** Recordatorio de disponibilidad: si no se ha actualizado en 30 días
**CA2:** Caducidad de documento: 30 días antes de que caduque el DNI/certificado
**CA3:** Recordatorio de servicio: 1 día antes del servicio programado
**CA4:** Recordatorio de fichar entrada: N minutos después de la hora de inicio del servicio si no se ha fichado (N configurable en servidor)
**CA5:** Ausencia próxima: 1 día antes de que comience la ausencia
**CA6:** Las usuarias pueden configurar las preferencias de notificaciones (mejora futura)

**Endpoints API requeridos:**
Las tareas programadas del backend activan estas notificaciones. No son necesarias llamadas a la API iniciadas desde la app.

---

### RF-12: Publicación de la Aplicación

**Se aplica a:** Ambos perfiles

#### RF-12.1: Aplicaciones de Marca Separadas

**Descripción:**
Compilar y publicar dos aplicaciones diferentes desde codebase compartido KMM con branding diferente.

**Criterios de Aceptación:**
**CA1:** **CUIDEO (Hogar)**:
- Nombre de la Aplicación: "CUIDEO"
- Bundle ID: es.cuideo.hogar (iOS) / es.cuideo.hogar (Android)
- Primary Color: Azul (#0066CC o especificado por cliente)
- App Icon: Icono temático azul
- Perfil: Solo funcionalidades Hogar

**CA2:** **Felizvita (SAD)**:
- Nombre de la Aplicación: "Felizvita"
- Bundle ID: es.cuideo.felizvita (iOS) / es.cuideo.felizvita (Android)
- Primary Color: Verde (#00AA55 o especificado por cliente)
- App Icon: Icono temático verde
- Perfil: Solo funcionalidades SAD

**CA3:** Ambas aplicaciones soportan:
- iOS 16+ (App Store)
- Android 8+ / API Level 26 (Google Play)


---

#### RF-12.2: Presentación en el App Store

**Descripción:**
Preparar y presentar aplicaciones a Apple App Store y Google Play Store.

**Criterios de Aceptación:**
**CA1: iOS App Store**
- Configuración de cuenta de App Store Connect
- Metadatos de la app: descripción, palabras clave, capturas de pantalla, vídeo de previsualización
- URL de la política de privacidad
- URL de soporte
- Categorías de la aplicación y clasificación por edades
- Pruebas beta con TestFlight (opcional)
- Presentación para la revisión de la aplicación

**CA2: Google Play Store**
- Configuración de la cuenta de Google Play Console
- Ficha de la aplicación: descripción, capturas de pantalla, imagen destacada
- URL de la política de privacidad
- Cuestionario de clasificación de contenido
- Categorías de la aplicación
- Pistas de pruebas cerradas/abiertas (opcional)
- Presentación para revisión

**CA3: Cumplimiento normativo**
- Documentación de cumplimiento del RGPD
- Privacidad de los datos
- Justificaciones de los permisos de ubicación
- Declaraciones de SDKs de terceros (Firebase)

---

## Requisitos No Funcionales

### RNF-1: Seguridad

#### RNF-1.1: Protección de Datos

**CA1:** Toda la comunicación con la API sobre HTTPS (TLS 1.2+)
**CA2:** Anclaje de certificados para endpoints de la API
**CA3:** Tokens de acceso almacenados en almacenamiento seguro:
- iOS: Keychain
- Android: EncryptedSharedPreferences / Android Keystore

**CA4:** No hay datos sensibles en los registros de la aplicación
**CA5:** Tiempo de espera automático de sesión después de 30 días de inactividad


#### RNF-1.2: Autenticación

**CA1:** Autenticación mediante email y contraseña
**CA2:** Token Sanctum con validez de **30 días**; se invalida al hacer logout o cuando el backend revoca la cuenta
**CA3:** Tokens invalidados al cerrar sesión

#### RNF-1.3: Autorización

**CA1:** Control de acceso a funcionalidades basado en perfil (Hogar vs SAD)
**CA2:** El backend valida los permisos de usuaria para todas las llamadas a la API
**CA3:** No hay comprobaciones de permisos solo del lado del cliente

---

### RNF-2: Usabilidad

#### RNF-2.1: Experiencia de Usuario

**CA1:** Máximo 3 toques para acceder a cualquier funcionalidad principal
**CA2:** Retroalimentación visual clara para todas las interacciones (<100 ms)
**CA3:** Validación de formularios con mensajes de error en línea
**CA4:** Diálogos de confirmación para acciones destructivas
**CA5:** Indicadores de carga para operaciones >500 ms

#### RNF-2.2: Accesibilidad

**CA1:** El tamaño del texto respeta la configuración de tamaño de letra del sistema
**CA2:** Tamaño mínimo del área táctil: 44x44 pts (iOS) / 48x48 dp (Android)
**CA3:** Ratios de contraste de color adecuadas (WCAG AA)
**CA4:** Compatibilidad con lectores de pantalla para los flujos principales (TalkBack/VoiceOver)
**CA5:** Texto alternativo para imágenes e iconos

---

### RNF-3: Internacionalización (i18n)

#### RNF-3.1: Soporte Multiidioma

**CA1:** La arquitectura de la aplicación admite múltiples idiomas
**CA2:** Todos los textos visibles para la usuaria externalizados (sin texto codificado)
**CA3:** Lanzamiento inicial: Solo castellano
**CA4:** Preparada para idiomas futuros: Catalán, Inglés, Francés
**CA5:** El formato de fecha/hora respeta la configuración regional del dispositivo
**CA6:** El formato de números respeta la configuración regional del dispositivo

---

### RNF-4: Compatibilidad

#### RNF-4.1: Soporte de Dispositivos

**CA1:** **iOS**: iPhone 8 y más nuevos (iOS 16+)
**CA2:** **Android**: Dispositivos con Android 8.0+ (API 26+)

---

### RNF-5: Analítica y Monitorización

#### RNF-5.1: Reporte de Crashes

**CA1:** Firebase Crashlytics integrado
**CA2:** Todos los crashes reportados automáticamente con trazas de pila
**CA3:** Metadatos de crash personalizados: usuaria_id, profile_type, app_state

#### RNF-5.2: Analítica

**CA1:** Firebase Analytics integrado de serie
**CA2:** Sin seguimiento de eventos personalizados en el MVP
**CA3:** Seguimiento automático de visualizaciones de pantalla

---

## Diseño y UX

### Referencias de Wireframes

[A proporcionar por el equipo de diseño]

### Guías de Marca

[A proporcionar por el cliente]


---

## Referencias

### Especificación de la API Swagger/OpenAPI

[A desarrollar colaborativamente con el equipo de backend]

---

## Control de Cambios

|   |   |   |   |
|---|---|---|---|
|Versión|Fecha|Autor|Cambios|
|1.0|2026-01-28|Feran Falguera|Borrador inicial para revisión|
|1.1|2026-01-29|Ferran Falguera|Revisión reunión Kick-Off|
|1.2|2026-03-03|Ferran Falguera|Revisión reunión diseño 27-feb: splash + acceso revocado; onboarding reordenado (login→onboarding→permisos), permisos de cámara diferidos; recuperación contraseña por SMS; modelo llamamientos multi-envío, firma obligatoria en aceptación y rechazo, timeout configurable desde back; fichaje sin manual + margen previo + acceso desde detalle de servicio; disponibilidad por domicilio (sin código postal); comunicación con asunto predefinido y enrutado interno transparente; documentos separados personal/laboral con carpetas dinámicas; tareas como listado descriptivo; datos de perfil core no editables|
|1.3|2026-03-03|Ferran Falguera|Resolución de inconsistencias acumuladas: permiso notificaciones push alineado a post-login (I-1); RF-10.4 obsoleta eliminada, CA7 enlace contexto integrado en RF-10.1 (I-2); dirección de domicilio marcada como editable en RF-9.1 (I-3); fuera de alcance distingue gestión activa de acceso lectura a nóminas (I-4); recordatorio fichaje unificado en RF-11.2 con N configurable (I-5); incidencia de fichaje/no asistencia añadida a catálogo RF-5.1 (I-6); numeración RF-4.2 corregida (I-7); copy Puntos Clave y Alcance actualizados al modelo de comunicación sin departamentos (I-8/I-9); splash y acceso revocado añadidos al Alcance (I-10); endpoint departments marcado como solo backoffice (I-11)|
|1.4|2026-03-04|Ferran Falguera|Reunión diseño 04-mar: autenticación cambiada a OTP por SMS sin contraseña (RF-1.3, RF-1.4, RNF-1.2, endpoints); activación SAD por OTP (RF-1.2 CA7); home SAD con acciones rápidas ampliadas + bloque "Últimos avisos" (RF-2.1 CA2); tablón con capacidad de fijar contenido desde backoffice (RF-2.2 CA1); llamamientos: aceptar/rechazar solo desde detalle, bloqueo de navegación hasta decisión (RF-2.1 CA7, RF-3.4); label contacto servicio cambiado a "Contacta coordinador/empresa" (RF-3.2 CA8); privacidad de campos de servicio desde backoffice (RF-3.2 CA11); nuevo RF-3.6 Seguimiento PIA; nuevo RF-3.7 Nuevo Servicio Asignado para indefinidos con distinción puntual/recurrente; fichaje añade opción solicitar ausencia (RF-4.1 CA11); vacaciones por días naturales pendiente confirmar (RF-8.2 CA10); documentos personales sin eliminar, laborales solo backoffice, acceso desde home (RF-9.3 CA4/CA5)|
|1.5|2026-03-10|Ferran Falguera|Revisión completa de endpoints API: eliminados todos los TBD, alineados endpoints con requisitos funcionales. Añadidos endpoints faltantes: mensajes sistema (mark-read, delete), notas servicio (delete), seguimiento PIA (get, sign), asignación servicio (acknowledge), documentos (PUT reemplazar, POST sign; eliminado DELETE personal), conversaciones (delete). Corregido DELETE /api/v1/profile/documents por PUT (no se permite eliminar documentos personales)|
|1.6|2026-03-12|Ferran Falguera|Registro Hogar cambiado a OTP por SMS sin contraseña (RF-1.2): eliminados email, contraseña y email de verificación; el registro se inicia con número de teléfono y se completa con OTP, alineándose con el flujo de SAD. Ambas apps (Hogar y SAD) usan exclusivamente SMS para autenticación y registro. Endpoints de autenticación actualizados en resumen de API.|
|1.7|2026-03-12|Ferran Falguera|Autenticación cambiada de OTP por SMS a email y contraseña en ambas apps (RF-1.2, RF-1.3, RF-1.4, RNF-1.2): registro Hogar con email+contraseña; activación SAD por enlace de email; login con email+contraseña; recuperación de acceso por email con enlace de restablecimiento. Eliminados endpoints /auth/send-otp y /auth/verify-otp; añadidos /auth/login, /auth/activate, /auth/forgot-password y /auth/reset-password.|
|1.8|2026-03-25|Ferran Falguera|Rediseño UX (PDR Disponibilidad SAD v2, 19/03/2026) + alineación con Swagger API v1.6.0: RF-7 rediseñado — calendario único con panel de franjas rápidas + formulario de slot personalizado (hora inicio/fin, tipo disponible/no disponible), elimina Madrugada y drag & drop; RF-2.1 CA9: máx. servicio actual+siguiente en home, "Ver más servicios" en lugar de "+2"; RF-3.2 CA3: dirección clickable que abre Maps; RF-4.1 CA13-15: botón activo 30min antes, estados dinámicos, warning sin bloquear flujo; RF-9.1 CA11-12: flujo completar perfil con bloqueo al aplicar a oferta. Endpoints actualizados a rutas reales del Swagger (/api/v1/workers/...): auth, dashboard, services (con /active, /upcoming, ?type=), time-tracking (service_worker_id, nuevo current-status/:id, history con filtro mes), availability (separate available-slots / unavailable-slots en lugar de slots unificado). Endpoints no definidos aún en Swagger marcados con 🔲.|
|1.9|2026-03-25|Ferran Falguera|RF-7 disponibilidad: solapamiento permitido entre franjas "Disponible" y "No disponible" (eliminada restricción de conflicto entre tipos); nuevo tipo de entrada "Activa" en el calendario (solo lectura, desde planificación) que se muestra solapada sobre franjas disponibles. Actualizado CA2, CA5, CA6b, CA7, descripción de tipos y endpoints GET/POST de available-slots y unavailable-slots.|

---
