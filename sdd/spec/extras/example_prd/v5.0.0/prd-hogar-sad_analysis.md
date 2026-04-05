# Analisis SDD: PRD Aplicaciones Moviles CUIDEO - Hogar & SAD

> **Generado por**: sdd-analyst (modo analyze)
> **Fecha**: 2026-04-05
> **Archivo origen**: prd-hogar-sad.md

---

## Leyenda de notacion

| Codigo | Significado | Donde aparece |
|--------|-------------|---------------|
| `[C-XXX]` | Contaminacion tecnica detectada | Seccion Pureza |
| `[CA-XXX]` | Criterio de Aceptacion problematico | Seccion Testabilidad |
| `[P-XXX]` | Pregunta pendiente de validacion con el cliente | Seccion Puntos pendientes |
| `[CRITICO]` | Gap que impide completar las HUs afectadas — quedaran marcadas `[INCOMPLETO]` en el spec si no se responde | Seccion Puntos pendientes |
| `[INFORMATIVO]` | Gap con asuncion por defecto — se aplica automaticamente si no se responde | Seccion Puntos pendientes |
| `_(pendiente)_` | Respuesta aun no proporcionada por el cliente | Campo "Respuesta" de cada gap |

---

## Estado general

> **REQUIERE_TRABAJO**
>
> El PRD es extenso, detallado y bien estructurado como documento de requisitos de producto, pero **no es un Spec SDD**: carece de la mayoria de los 8 elementos obligatorios (Historias de Usuario formales, Recorridos de Usuario paso a paso, Resultados y Exito, Instrucciones Inambiguas con tabla de navegacion, CAs en GIVEN/WHEN/THEN, y Checklist de Validacion). Contiene **contaminacion tecnica significativa** (stack tecnologico, endpoints de API, detalles de implementacion) que pertenece al Plan. Hay ademas **varios gaps funcionales criticos** que requieren respuesta del cliente antes de generar specs validos.

---

## Completitud: 2/8 elementos presentes

- [x] **Actores** — presente: se identifican dos perfiles (Hogar y SAD) con sus casos de uso principales, aunque falta formalizar como tabla de actores con capacidades
- [ ] **Historias de Usuario (Como/quiero/para que)** — ausente: no hay ninguna HU en formato "Como [actor] quiero [accion] para que [beneficio]"; los requisitos se describen como funcionalidades, no como necesidades del usuario
- [ ] **Recorridos de Usuario** — ausente: no hay journeys paso a paso que describan como el usuario interactua con cada funcionalidad; los RF describen "que" hace el sistema pero no el recorrido del usuario
- [ ] **Resultados y Exito** — ausente: no se define que significa "exito" para cada flujo desde la perspectiva del usuario
- [ ] **Instrucciones Inambiguas** — parcial: algunos RF tienen reglas de comportamiento detalladas (RF-3.4, RF-4.1, RF-7.1), pero falta tabla de destinos de navegacion para deeplinks/notificaciones (RF-11.1 lista tipos pero no detalla destinos exactos para cada uno)
- [ ] **Criterios de Aceptacion (GIVEN/WHEN/THEN)** — ausente: los CAs existentes son descriptivos ("Mostrar X", "Listar Y") pero ninguno usa el formato GIVEN/WHEN/THEN verificable con referencia a HU padre
- [ ] **Checklist de Validacion** — ausente: no hay checklist de validacion
- [x] **Fuera de Alcance** — presente: seccion "Fuera de Alcance - Posibles fases futuras" bien definida con exclusiones claras

---

## Pureza: CONTAMINADO

El documento contiene contaminacion tecnica significativa que pertenece al Plan, no al Spec. Se listan las instancias principales agrupadas por categoria.

#### [C-001] Stack tecnologico: Kotlin Multiplatform Mobile (KMM)
- **Cita**: > "Kotlin Multiplatform Mobile (KMM)" / "Código Compartido: Lógica de negocio, red, modelos de datos" / "Específico de Plataforma: UI (Jetpack Compose para Android e iOS), APIs de plataforma"
- **Problema**: El Spec no debe mencionar tecnologias de implementacion. Si se pasara de KMM a Flutter o a web, la funcionalidad no cambiaria.
- **Reescritura sugerida**: Eliminar toda la seccion "Stack Tecnologico". La decision de KMM pertenece al Plan. En el Spec solo importa que las dos aplicaciones comparten funcionalidades comunes y tienen funcionalidades especificas por perfil.
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-002] Seccion completa de Arquitectura del Sistema
- **Cita**: > "Arquitectura del Sistema" / "Diagrama de Arquitectura" / "API REST" / "Backend del cliente" / "Base de Datos"
- **Problema**: La arquitectura tecnica (diagramas, capas, API REST, base de datos) pertenece al Plan. El Spec debe describir que hace el sistema para el usuario, no como esta construido.
- **Reescritura sugerida**: Eliminar la seccion "Arquitectura del Sistema" completa. Si es necesario referir integraciones externas, hacerlo como: "El sistema envia notificaciones push a las trabajadoras" (funcional) en lugar de "Firebase Cloud Messaging" (tecnico).
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-003] Modulos de Logica de Negocio Compartida (KMM)
- **Cita**: > "Módulos en shared: 1. Módulo de Red: Cliente API, gestión de solicitudes/respuestas 2. Módulo de Autenticación..."
- **Problema**: La descomposicion en modulos de codigo es arquitectura tecnica que pertenece al Plan. Los 12 modulos listados son decisiones de implementacion.
- **Reescritura sugerida**: Eliminar seccion completa. La organizacion en modulos se decidira en el Plan.
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-004] Especificacion completa de endpoints API
- **Cita**: > "POST /api/v1/workers/auth/login" / "GET /api/v1/workers/services" / todas las secciones "Endpoints API Requeridos" en cada RF
- **Problema**: Los endpoints de API, sus rutas, metodos HTTP, parametros de body y referencia a Swagger son detalles tecnicos de implementacion. Un Spec funcional no debe contener rutas de API.
- **Reescritura sugerida**: Eliminar todas las secciones "Endpoints API Requeridos" de cada RF y eliminar la seccion "Resumen de Endpoints API" completa. La informacion de que datos necesita cada funcionalidad ya esta cubierta por los CAs funcionales. Los endpoints se definiran en el Plan.
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-005] Integraciones externas con nombres de servicio
- **Cita**: > "Firebase Cloud Messaging (notificaciones push)" / "Firebase Realtime Database (mensajería)" / "Firebase Crashlytics (reporte de caídas)" / "Firebase Analytics (analítica básica)"
- **Problema**: Los nombres de servicio especificos (Firebase) son decisiones tecnicas. La funcionalidad es "el sistema envia notificaciones", no "Firebase Cloud Messaging".
- **Reescritura sugerida**: Reemplazar por descripciones funcionales: "El sistema envia notificaciones push a las trabajadoras para eventos relevantes", "El sistema registra automaticamente los errores para su analisis por el equipo tecnico", "La mensajeria se actualiza en tiempo real".
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-006] Detalles de autenticacion tecnica: JWT, Sanctum, tokens
- **Cita**: > "Autenticación basada en JWT" / "token Sanctum válido 30 días" / "iOS Keychain / Android Keystore" / "EncryptedSharedPreferences"
- **Problema**: JWT, Sanctum, Keychain, Keystore y EncryptedSharedPreferences son detalles de implementacion. Lo funcional es "la sesion se mantiene activa durante 30 dias" y "las credenciales se almacenan de forma segura".
- **Reescritura sugerida**: "La sesion de la usuaria se mantiene activa durante 30 dias desde el ultimo inicio de sesion. Si expira, la usuaria debe volver a autenticarse. Las credenciales se almacenan de forma segura en el dispositivo."
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-007] Bundle IDs y colores hexadecimales
- **Cita**: > "Bundle ID: es.cuideo.hogar (iOS) / es.cuideo.hogar (Android)" / "Primary Color: Azul (#0066CC o especificado por cliente)" / "Primary Color: Verde (#00AA55 o especificado por cliente)"
- **Problema**: Los Bundle IDs son identificadores de implementacion y los colores hex son especificaciones esteticas profundas. Pertenecen al Plan/diseno.
- **Reescritura sugerida**: "La aplicacion CUIDEO usa una identidad visual azul y la aplicacion Felizvita usa una identidad visual verde. Ambas se publican como aplicaciones independientes en las tiendas de aplicaciones."
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-008] Requisitos No Funcionales tecnicos: TLS, certificate pinning, API levels
- **Cita**: > "HTTPS (TLS 1.2+)" / "Anclaje de certificados para endpoints de la API" / "iOS: Keychain" / "Android 8.0+ (API 26+)" / "iOS 16+"
- **Problema**: Los protocolos de seguridad (TLS, certificate pinning), las versiones de SO y API levels son restricciones tecnicas de implementacion.
- **Reescritura sugerida**: Los RNF tecnicos pertenecen al Plan. En el Spec solo cabe: "La comunicacion entre la app y el servidor es segura", "La app es compatible con los sistemas operativos moviles mas comunes en las versiones que usan las trabajadoras".
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-009] Analitica y monitorizacion: Firebase Crashlytics, Firebase Analytics
- **Cita**: > "Firebase Crashlytics integrado" / "Firebase Analytics integrado de serie" / "Metadatos de crash personalizados: usuaria_id, profile_type, app_state"
- **Problema**: Los nombres de herramientas (Crashlytics, Analytics) y los metadatos de crash son detalles de implementacion.
- **Reescritura sugerida**: Eliminar. La decision de que herramientas de monitorizacion usar y que metadatos enviar pertenece al Plan.
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-010] Detalles de plataforma en usabilidad
- **Cita**: > "44x44 pts (iOS) / 48x48 dp (Android)" / "TalkBack/VoiceOver"
- **Problema**: Las medidas especificas por plataforma (pts, dp) y los nombres de lectores de pantalla son detalles de implementacion.
- **Reescritura sugerida**: "Los elementos interactivos tienen un tamano minimo que permite su uso comodo con el dedo" y "La app es compatible con los lectores de pantalla nativos de cada plataforma".
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-011] Internacionalizacion tecnica
- **Cita**: > "La arquitectura de la aplicación admite múltiples idiomas" / "Todos los textos visibles para la usuaria externalizados (sin texto codificado)"
- **Problema**: "Arquitectura admite multiples idiomas" y "textos externalizados (sin texto codificado)" son restricciones de implementacion.
- **Reescritura sugerida**: "La app se lanza en castellano. Estara preparada para incorporar catalan, ingles y frances en fases futuras. Los formatos de fecha, hora y numeros respetan la configuracion regional del dispositivo de la usuaria."
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-012] Referencia a mecanismo de almacenamiento local
- **Cita**: > "Almacenar el estado de completación del onboarding localmente" (RF-1.1 CA6)
- **Problema**: "Almacenar localmente" es una decision de implementacion. Lo funcional es que el onboarding solo se muestra una vez.
- **Reescritura sugerida**: Eliminar CA6. El CA5 ("Mostrar el onboarding solo una vez") ya cubre la funcionalidad. Como se persiste es decision del Plan.
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-013] Referencia a token FCM y registro de dispositivo
- **Cita**: > "vincular el token FCM al usuario concreto" (RF-1.1 CA3 y RF-11.1 CA1) / "Registrar token FCM del dispositivo con el backend" (RF-11.1 CA2)
- **Problema**: FCM (Firebase Cloud Messaging) y el concepto de "token FCM" son detalles de implementacion de notificaciones push.
- **Reescritura sugerida**: "Solicitar permiso de notificaciones push despues del primer inicio de sesion para que la usuaria reciba notificaciones en su dispositivo" y "Registrar el dispositivo para recibir notificaciones push".
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-014] Referencia a Realtime Database
- **Cita**: > "Actualizaciones de mensajes en tiempo real (realtime database)" (RF-10.3 CA11)
- **Problema**: "Realtime database" es una tecnologia especifica (Firebase Realtime Database). Lo funcional es que los mensajes se actualizan en tiempo real.
- **Reescritura sugerida**: "Los mensajes nuevos aparecen automaticamente en la conversacion sin que la usuaria tenga que refrescar la pantalla."
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-015] Formato de archivo de firma
- **Cita**: > "Guardar firma como archivo PNG" (RF-9.4 CA5)
- **Problema**: El formato de archivo (PNG) es un detalle de implementacion. Lo funcional es que la firma se guarda y puede reutilizarse.
- **Reescritura sugerida**: "La firma capturada se guarda en el perfil de la usuaria y puede reutilizarse para futuras firmas de documentos."
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

#### [C-016] RF-12 completo: Publicacion de la Aplicacion
- **Cita**: > "RF-12: Publicación de la Aplicación" / "Compilar y publicar dos aplicaciones diferentes desde codebase compartido KMM con branding diferente"
- **Problema**: Todo el RF-12 (compilacion, submission a stores, TestFlight, configuracion de consolas, SDKs de terceros) es proceso de despliegue e implementacion que pertenece al Plan, no es funcionalidad para el usuario final.
- **Reescritura sugerida**: Eliminar RF-12 del Spec. Si es necesario documentar las diferencias de marca funcionales (nombre, identidad visual por perfil), incluirlas como nota en la descripcion general. El proceso de publicacion es Plan.
- **Accion**: `[X] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

## Testabilidad: REQUIERE_MEJORA

Ningun CA del documento usa el formato GIVEN/WHEN/THEN. Todos los CAs son descriptivos ("Mostrar X", "Listar Y", "Tocar para Z"). Esto los hace no verificables de forma objetiva e independiente. A continuacion se listan los casos mas representativos que requieren reformulacion.

#### [CA-001] RF-1.0 CA3: Redireccion desde splash
- **CA actual**: "Redirigir al login si no hay sesión activa; al home si hay sesión válida"
- **Problema**: No tiene formato GIVEN/WHEN/THEN, no es verificable de forma independiente, no referencia HU padre.
- **Sugerencia de reformulacion**:
  ```
  GIVEN la usuaria arranca la aplicacion y no tiene una sesion activa
  WHEN la pantalla de splash completa su visualizacion
  THEN la aplicacion muestra la pantalla de inicio de sesion
  ```
  ```
  GIVEN la usuaria arranca la aplicacion y tiene una sesion activa valida
  WHEN la pantalla de splash completa su visualizacion
  THEN la aplicacion muestra la pantalla principal (home)
  ```

#### [CA-002] RF-1.3 CA4: Bloqueo por intentos fallidos
- **CA actual**: "Bloqueo temporal tras N intentos fallidos (N configurable en servidor)"
- **Problema**: N no esta definido, no se especifica que ve la usuaria ni cuanto dura el bloqueo desde su perspectiva. No tiene formato GIVEN/WHEN/THEN.
- **Sugerencia de reformulacion**:
  ```
  GIVEN la usuaria ha introducido credenciales incorrectas N veces consecutivas
  WHEN intenta iniciar sesion una vez mas
  THEN la aplicacion muestra un mensaje indicando que la cuenta esta temporalmente bloqueada y el tiempo estimado de espera
  ```

#### [CA-003] RF-2.1 CA3: Badges en accesos directos
- **CA actual**: "Mostrar notificaciones de badge en los accesos directos (mensajes no leídos, acciones pendientes)"
- **Problema**: No especifica que tipos de badges, en que accesos directos aparecen, ni que numeros muestran. No tiene formato GIVEN/WHEN/THEN.
- **Sugerencia de reformulacion**:
  ```
  GIVEN la usuaria tiene mensajes no leidos en el modulo de Comunicacion
  WHEN accede a la pantalla principal (home)
  THEN el acceso directo de Comunicacion muestra un badge con el numero de mensajes no leidos
  ```

#### [CA-004] RF-3.4 CA8: Caducidad de llamamientos
- **CA actual**: "Las llamadas caducan automáticamente tras el tiempo límite configurado desde backoffice; si no hay respuesta puede computar como rechazo por inacción (pendiente de revisión legal)"
- **Problema**: El "puede computar" y "pendiente de revision legal" lo hacen ambiguo e indeterminado. No hay GIVEN/WHEN/THEN.
- **Sugerencia de reformulacion**: Requiere primero la resolucion del gap [P-004] sobre la consecuencia de la inaccion.

#### [CA-005] RF-4.1 CA4: Advertencia de precision de ubicacion
- **CA actual**: "Mostrar advertencia si la precisión de la ubicación es baja (<50m); esperar máximo 2s antes de permitir continuar"
- **Problema**: "<50m" y "2s" mezclan umbrales tecnicos con funcionalidad. No tiene formato GIVEN/WHEN/THEN.
- **Sugerencia de reformulacion**:
  ```
  GIVEN la usuaria intenta fichar entrada o salida
  WHEN la precision de su ubicacion no alcanza el umbral minimo aceptable
  THEN la aplicacion muestra una advertencia de baja precision y, tras un breve periodo de espera, permite continuar con el fichaje igualmente
  ```

#### [CA-006] RF-7.1 CA5: Solapamiento de slots
- **CA actual**: "No se permiten solapamientos entre slots del mismo tipo en el mismo día (dos franjas 'Disponible' o dos 'No disponible' no pueden solaparse); la API devuelve error en este caso"
- **Problema**: "La API devuelve error" es un detalle tecnico. No tiene formato GIVEN/WHEN/THEN.
- **Sugerencia de reformulacion**:
  ```
  GIVEN la usuaria tiene un slot de tipo "Disponible" de 09:00 a 13:00 para un dia concreto
  WHEN intenta crear otro slot de tipo "Disponible" de 11:00 a 15:00 para el mismo dia
  THEN la aplicacion muestra un mensaje de error indicando que no es posible crear franjas del mismo tipo que se solapen
  ```

---

## Puntos pendientes de validacion con cliente

> Estos puntos **no fueron inferidos por el sistema**. Son ambiguedades o informacion ausente
> que debe ser definida por el cliente antes de generar el `.spec` final.
> **Instruccion**: escribe la respuesta del cliente en el campo "Respuesta" de cada punto.
>
> - `[CRITICO]`: afecta directamente a las HUs indicadas en "Afecta". Si se deja sin responder, esas HUs se marcaran como `[INCOMPLETO]` en el spec — se generaran con la informacion disponible pero no podran avanzar a plan/tasks hasta completarse.
> - `[INFORMATIVO]`: si no se responde, se aplicara la "Asuncion por defecto" indicada.

### [P-001][CRITICO] Destinos de navegacion (deeplinks) por tipo de notificacion
- **Contexto**: RF-11.1 lista 10 tipos de notificaciones push con "deeplink" pero no especifica a que pantalla exacta navega cada tipo. Dice "Tocar notificación abre aplicación en pantalla específica vía deeplink" sin enumerar los destinos.
- **Problema**: Sin una tabla explicita de "tipo de notificacion -> pantalla de destino", el spec sera ambiguo y dos implementadores podrian interpretar destinos diferentes.
- **Afecta**: funcionalidades de notificaciones push (RF-11.1), panel principal (RF-2.1 — llamamientos en home con deeplink al detalle)
- **Pregunta para el cliente**: Para cada tipo de notificacion, cual es la pantalla exacta de destino al tocar la notificacion? Por ejemplo: "Nuevo mensaje recibido" -> abre la conversacion con ese remitente; "Llamada de servicio disponible" -> abre el detalle del llamamiento; etc. Por favor, complete la tabla para los 10 tipos listados.
- **Respuesta**: _(pendiente)_

### [P-002][CRITICO] Registro de trabajadoras Hogar: campos del formulario
- **Contexto**: RF-1.2 describe que las trabajadoras Hogar se registran con email y contrasena, pero no especifica si hay campos adicionales obligatorios en el registro (nombre, telefono, etc.) ni si el perfil se completa despues del registro.
- **Problema**: Sin saber que datos se solicitan en el registro, no se pueden definir CAs verificables para el flujo de alta de Hogar.
- **Afecta**: funcionalidades de registro de usuario Hogar (RF-1.2)
- **Pregunta para el cliente**: Que campos se solicitan en el formulario de registro de trabajadoras Hogar? Solo email y contrasena, o tambien nombre, telefono u otros datos? El perfil se completa en un paso posterior?
- **Respuesta**: _(pendiente)_

### [P-003][CRITICO] Activacion SAD: flujo detallado del enlace de activacion
- **Contexto**: RF-1.2 CA6 menciona "la trabajadora recibe un email con un enlace de activación; al acceder al enlace puede establecer su contraseña y acceder a la app" pero no detalla el flujo completo.
- **Problema**: No queda claro si al pulsar el enlace se abre la app directamente o una web, si se solicita solo contrasena o tambien otros datos, ni que pasa si el enlace caduca.
- **Afecta**: funcionalidades de registro/activacion SAD (RF-1.2)
- **Pregunta para el cliente**: Cuando la trabajadora SAD pulsa el enlace de activacion del email, que sucede exactamente? Se abre la app o una pagina web? Que campos debe completar (solo contrasena o algo mas)? Tiene caducidad el enlace? Que pasa si caduca?
- **Respuesta**: En este caso no hay nada a implementar por parte de la app. Esa gestión es por parte de otro servicio, en la app solamente tendrá que hacer el inicio de sesion con la nueva contraseña y ya está.

### [P-004][CRITICO] Caducidad de llamamientos: consecuencia de la inaccion
- **Contexto**: RF-3.4 CA8 dice "si no hay respuesta puede computar como rechazo por inacción (pendiente de revisión legal)".
- **Problema**: El "puede computar" y "pendiente de revision legal" dejan indeterminada una regla de negocio critica: si la trabajadora no responde un llamamiento a tiempo, se computa como rechazo formal o simplemente como "no respondido"? Esto afecta al historial de la trabajadora y potencialmente a consecuencias laborales.
- **Afecta**: funcionalidades de llamamientos (RF-3.4), historial de servicios (RF-3.5)
- **Pregunta para el cliente**: Cuando un llamamiento caduca sin respuesta de la trabajadora, que consecuencia tiene? Se registra como "rechazo por inaccion" (con las implicaciones legales que eso conlleve) o simplemente como "caducado sin respuesta"?
- **Respuesta**: _(pendiente)_

### [P-005][CRITICO] Copy legal de aceptacion y rechazo de llamamientos
- **Contexto**: RF-3.4 CA4 y CA5 indican que "el copy de aceptación debe ser claro e inequívoco (solicitar textos oficiales a negocio/legal)" y "el copy de rechazo debe ser explícito y distinguirse claramente del de aceptación".
- **Problema**: Los textos exactos de aceptacion y rechazo son esenciales porque van acompanados de firma digital y tienen implicaciones legales. Sin ellos, no se puede generar un spec completo para esta funcionalidad.
- **Afecta**: funcionalidades de llamamientos (RF-3.4)
- **Pregunta para el cliente**: Cuales son los textos legales oficiales que la trabajadora vera al aceptar y al rechazar un llamamiento? Son textos que ha validado el departamento legal?
- **Respuesta**: _(pendiente)_

### [P-006][CRITICO] Tipo de contrato: discrepancia entre PRD y Swagger
- **Contexto**: RF-9.1 CA1 y RF-9.5 CA1 mencionan tipos de contrato "Indefinido, Fijo Discontinuo" pero anotan: "El Swagger v1.6.0 devuelve contract_type: 'Tiempo completo' | 'Tiempo parcial' — pendiente alinear con backend si son el mismo campo o dos dimensiones distintas".
- **Problema**: Si "Tiempo completo/Tiempo parcial" y "Indefinido/Fijo discontinuo" son dos dimensiones distintas, hay cuatro combinaciones posibles y la UI debe reflejar ambas. Si son el mismo campo con nomenclatura diferente, hay que alinear cual es la correcta.
- **Afecta**: funcionalidades de perfil y contrato (RF-9.1, RF-9.5)
- **Pregunta para el cliente**: Los tipos de contrato "Indefinido / Fijo Discontinuo" del PRD y los valores "Tiempo completo / Tiempo parcial" del Swagger, son el mismo campo con nombres distintos o son dos dimensiones independientes del contrato?
- **Respuesta**: _(pendiente)_

### [P-007][CRITICO] Vacaciones: computo por dias naturales o laborables
- **Contexto**: RF-8.2 CA10 dice "Las vacaciones se computan por días naturales (pendiente de confirmar con cliente/legal)".
- **Problema**: La diferencia entre dias naturales y laborables afecta al calculo del saldo de vacaciones, la visualizacion de dias disponibles y la logica de solicitud. Es una regla de negocio critica.
- **Afecta**: funcionalidades de ausencias (RF-8.1, RF-8.2)
- **Pregunta para el cliente**: Las vacaciones se computan por dias naturales o por dias laborables?
- **Respuesta**: _(pendiente)_

### [P-008][CRITICO] Revision RGPD sobre datos de salud del cliente
- **Contexto**: RF-3.2 CA2 anota "Información de salud: pendiente de revisión RGPD — consultar con legal antes de mostrar medicación u otros datos persistentes de salud en el lado de la cuidadora".
- **Problema**: Sin saber si se pueden mostrar datos de salud del cliente a la cuidadora, no se puede definir completamente que informacion aparece en el detalle del servicio.
- **Afecta**: funcionalidad de detalle de servicio (RF-3.2)
- **Pregunta para el cliente**: Se ha completado la revision RGPD? Se pueden mostrar datos de salud del cliente (medicacion, condiciones medicas) a la cuidadora en la app, o deben excluirse?
- **Respuesta**: _(pendiente)_

### [P-009][CRITICO] Mensajes del sistema: criterios de "criticidad alta" vs "normal"
- **Contexto**: RF-2.3 dice "Se diferenciarán en dos niveles de criticidad, alta se mostrarán diferentes y primero y normal se mostrarán debajo" pero no define que criterios determinan cada nivel.
- **Problema**: Sin definicion clara de que hace que un mensaje sea de "criticidad alta", la implementacion sera arbitraria. Esto afecta al orden de presentacion y la diferenciacion visual.
- **Afecta**: funcionalidad de mensajes del sistema (RF-2.3)
- **Pregunta para el cliente**: Que criterios determinan que un mensaje del sistema sea de "criticidad alta" vs "normal"? Lo decide el remitente al crearlo desde backoffice, o hay reglas automaticas basadas en el contenido?
- **Respuesta**: _(pendiente)_

### [P-010][CRITICO] Notas de servicio: posibilidad de editar notas propias
- **Contexto**: RF-3.3 lista un endpoint de edicion de notas (PUT) y el CA6 menciona "Borrar notas propias", pero no hay ningun CA que describa la funcionalidad de editar una nota ya creada.
- **Problema**: El endpoint de edicion esta listado pero la funcionalidad de edicion no esta descrita como CA. No esta claro si la trabajadora puede editar sus notas una vez creadas, ni si hay un plazo para hacerlo.
- **Afecta**: funcionalidad de notas de servicio (RF-3.3)
- **Pregunta para el cliente**: La trabajadora puede editar sus propias notas de servicio despues de crearlas? Si es asi, hay un plazo maximo para editarlas?
- **Respuesta**: _(pendiente)_

### [P-011][INFORMATIVO] Numero de pantallas de bienvenida (onboarding)
- **Contexto**: RF-1.1 CA1 dice "3-5 pantallas de bienvenida (ideal 3, máximo 5)" sin especificar el contenido de cada pantalla.
- **Pregunta para el cliente**: Cuales son los contenidos especificos de las 3 pantallas de onboarding (titulos, textos, ilustraciones)?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Se generaran 3 pantallas de onboarding con contenido generico: 1) Bienvenida y descripcion general de la app, 2) Funcionalidades principales, 3) Primeros pasos. El contenido exacto se ajustara cuando diseno proporcione los wireframes.

### [P-012][INFORMATIVO] Tiempo de visualizacion de la pantalla de splash
- **Contexto**: RF-1.0 CA2 dice "Duración de 2-3 segundos" sin especificar si es un tiempo fijo o si se usa para cargar datos en paralelo.
- **Pregunta para el cliente**: La pantalla de splash tiene una duracion fija (ej: 2 segundos) o se muestra mientras la aplicacion verifica la sesion y carga los datos iniciales?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: La pantalla de splash se muestra durante un tiempo fijo de 2 segundos mientras la aplicacion realiza la verificacion de sesion en segundo plano. Si la verificacion tarda mas de 2 segundos, se extiende hasta completarla.

### [P-013][INFORMATIVO] Adjuntos en conversaciones de chat
- **Contexto**: RF-10.3 describe el hilo de conversacion con envio de mensajes de texto pero no menciona si se pueden enviar imagenes, archivos u otros adjuntos en el chat.
- **Pregunta para el cliente**: La trabajadora puede enviar imagenes o archivos adjuntos en las conversaciones con coordinacion, o solo mensajes de texto?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: En el MVP, las conversaciones solo soportan mensajes de texto. El envio de adjuntos en chat queda fuera del alcance inicial.

### [P-014][INFORMATIVO] Comportamiento offline
- **Contexto**: El documento lista "Modo offline con sincronización" en Fuera de Alcance, pero no define que sucede cuando la trabajadora pierde conexion durante el uso normal (ej: durante un fichaje, al enviar una incidencia).
- **Pregunta para el cliente**: Cuando la trabajadora pierde la conexion a internet durante una accion (fichaje, envio de nota, etc.), que comportamiento espera? Se muestra un error generico o se reintenta automaticamente al recuperar conexion?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Se muestra un mensaje de error indicando la falta de conexion y se pide a la usuaria que lo reintente manualmente cuando tenga conexion. No hay cola de reintentos automaticos (el modo offline con sincronizacion esta explicitamente fuera de alcance).

### [P-015][INFORMATIVO] Compresion automatica de imagenes: umbral de tamano
- **Contexto**: RF-5.1 CA7 dice "Comprimir imágenes automáticamente" y RF-9.2 CA5 dice "Compresión automática", sin especificar a que tamano o calidad se comprimen.
- **Pregunta para el cliente**: Hay algun requisito de tamano maximo o calidad minima para las imagenes comprimidas, o basta con que sean "razonablemente ligeras" para la subida?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Las imagenes se comprimen automaticamente para no superar 1MB manteniendo calidad visual aceptable. El tamano exacto se ajustara en el Plan segun las capacidades del dispositivo y la velocidad de red tipica.

### [P-016][INFORMATIVO] Historial de notificaciones: retencion y limpieza
- **Contexto**: RF-11.1 menciona "Listar historial de notificaciones" sin especificar cuanto tiempo se retienen ni si hay limite.
- **Pregunta para el cliente**: El historial de notificaciones tiene un periodo de retencion (ej: ultimos 30 dias) o se muestra todo el historico?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Se muestran las notificaciones de los ultimos 90 dias con paginacion. Las mas antiguas dejan de mostrarse.

### [P-017][INFORMATIVO] Panel SAD: orden de prioridad de elementos en home
- **Contexto**: RF-2.1 CA2 lista multiples secciones para la home SAD (Mis Servicios, Fichar, Incidencias, Solicitar Ausencia, etc.) sin definir un orden fijo de prioridad ni si son todas visibles siempre o contextuales.
- **Pregunta para el cliente**: Cual es el orden de prioridad de los elementos en la home SAD? Todos son visibles siempre o algunos aparecen solo en contexto (ej: "Fichar" solo si hay servicio activo)?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Los elementos se muestran en el orden listado en el PRD. "Fichar" se muestra siempre pero se habilita/deshabilita segun si hay servicio activo. Los accesos directos no se ocultan por contexto para mantener una navegacion consistente.

### [P-018][INFORMATIVO] Propuesta de cambio de datos core del perfil
- **Contexto**: RF-9.1 menciona que para datos core no editables se puede enviar una "propuesta de cambio" con documentacion justificativa, pero no detalla el flujo (que campos lo permiten, que documentos, como se notifica el resultado).
- **Pregunta para el cliente**: Que campos core permiten enviar propuesta de cambio? Se necesita documentacion justificativa para todos? Como se notifica a la trabajadora si la propuesta es aceptada o rechazada?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Solo el DNI/NIE (renovacion) permite propuesta de cambio con documento adjunto. El resultado se notifica via mensaje del sistema. El resto de datos core (nombre, apellidos) solo se modifican desde backoffice sin intervencion de la trabajadora desde la app.

---

## Proximos pasos

1. En la seccion "Pureza", para cada contaminacion marca **una** de las tres acciones:
   - `[x] ACEPTAR` — se usara la reescritura tal cual en el spec
   - `[x] EDITAR` — modifica el texto de "Reescritura sugerida" y marca esta opcion
   - `[x] RECHAZAR (justificar)` — anade tu justificacion; el texto original se conservara como excepcion documentada
2. Responder los puntos `[CRITICO]` que puedas — los que queden sin respuesta marcaran sus HUs como `[INCOMPLETO]` en el spec (se generaran pero no podran avanzar a plan/tasks)
3. Responder los puntos `[INFORMATIVO]` si tienes la informacion — si no, se aplicara la asuncion por defecto
4. Una vez revisado, ejecutar el flujo completo automatico:
   ```
   /wf-spec-features-first prd-hogar-sad.md
   ```
   O para el paso a paso (solo discovery):
   ```
   /wf-spec-discover prd-hogar-sad.md --analysis prd-hogar-sad_analysis.md
   ```
5. Para completar HUs marcadas `[INCOMPLETO]` despues: responde los gaps pendientes en este archivo y ejecuta `/wf-spec-delta resolve <feature_spec.md>`
