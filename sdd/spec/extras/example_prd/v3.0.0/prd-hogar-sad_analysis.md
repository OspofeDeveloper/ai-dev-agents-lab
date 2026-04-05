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
> El PRD es extenso y muy detallado en funcionalidades, pero esta fuertemente contaminado con detalles tecnicos (endpoints API, stack tecnologico, arquitectura, tokens, almacenamiento seguro) que pertenecen al Plan, no al Spec. Faltan elementos estructurales obligatorios del Spec (actores formales, historias de usuario en formato Como/quiero/para, recorridos de usuario paso a paso, resultados y exito, checklist de validacion). Los criterios de aceptacion no usan formato GIVEN/WHEN/THEN. Hay varias ambiguedades funcionales que requieren respuesta del cliente.

---

## Completitud: 2/8 elementos presentes

- [ ] **Actores** — parcial: se mencionan perfiles (Hogar, SAD, Coordinadoras, Backoffice) pero no hay tabla formal de actores con capacidades. Los roles estan dispersos en el documento sin definicion estructurada
- [ ] **Historias de Usuario (Como/quiero/para que)** — ausente: no hay ninguna HU en formato "Como [rol] quiero [accion] para que [beneficio]". Los requisitos estan descritos como funcionalidades, no como historias
- [ ] **Recorridos de Usuario** — ausente: no hay journeys paso a paso. Las descripciones funcionales son de alto nivel sin recorrido detallado de la interaccion
- [ ] **Resultados y Exito** — ausente: no se definen estados de exito claros para cada flujo. Algunos CAs implican resultados pero no hay seccion dedicada
- [ ] **Instrucciones Inambiguas** — parcial: hay bastante detalle funcional en los CAs, pero faltan tablas de destinos de navegacion para deeplinks/notificaciones, y hay varias ambiguedades documentadas en los gaps
- [x] **Criterios de Aceptacion (GIVEN/WHEN/THEN)** — parcial: hay CAs numerados para cada RF, pero ninguno usa formato GIVEN/WHEN/THEN ni referencia una HU padre. Son declaraciones de comportamiento sin precondicion/accion/resultado estructurados
- [ ] **Checklist de Validacion** — ausente: no hay checklist de validacion
- [x] **Fuera de Alcance** — presente: seccion "Fuera de Alcance - Posibles fases futuras" bien definida con exclusiones funcionales claras

---

## Pureza: CONTAMINADO

El documento presenta contaminacion tecnica significativa. Se listan las instancias mas relevantes agrupadas por tipo.

### Contaminacion de stack tecnologico y arquitectura

#### [C-001] Stack tecnologico KMM en descripcion del producto
- **Cita**: > "Dos aplicaciones moviles nativas desarrolladas con Kotlin Multiplatform Mobile (KMM)"
- **Problema**: Mencionar KMM hace el spec dependiente de una tecnologia concreta. El spec debe describir que se construye, no con que.
- **Reescritura sugerida**: "Dos aplicaciones moviles que sirven dos perfiles de usuaria diferentes dentro del ecosistema CUIDEO"
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

#### [C-002] Seccion completa de Arquitectura del Sistema
- **Cita**: > "Stack Tecnologico: Framework: Kotlin Multiplatform Mobile (KMM), Codigo Compartido: Logica de negocio, red, modelos de datos, Especifico de Plataforma: UI (Jetpack Compose para Android e iOS), APIs de plataforma"
- **Problema**: Toda la seccion "Arquitectura del Sistema" (stack tecnologico, diagrama de arquitectura, modulos KMM, integraciones) pertenece al Plan. Es implementacion pura.
- **Reescritura sugerida**: Eliminar la seccion completa "Arquitectura del Sistema" del spec. Si se necesita referenciar integraciones funcionales (ej: "el sistema envia notificaciones push"), hacerlo sin nombrar la tecnologia.
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

#### [C-003] Integraciones externas con nombres de servicios tecnicos
- **Cita**: > "Firebase Cloud Messaging (notificaciones push), Firebase Realtime Database (mensajeria), Firebase Crashlytics (reporte de caidas), Firebase Analytics (analitica basica)"
- **Problema**: Los proveedores de servicios son decisiones de implementacion. El spec solo necesita decir que funcionalidad proporcionan (notificaciones, mensajeria en tiempo real, etc.).
- **Reescritura sugerida**: "El sistema proporciona: notificaciones push, mensajeria en tiempo real, reporte automatico de errores y analitica basica de uso"
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

#### [C-004] Modulos KMM en detalle
- **Cita**: > "Logica de Negocio Compartida (KMM): Modulo de Red, Modulo de Autenticacion, Modulo de Perfil de Usuaria, Modulo de Servicios..."
- **Problema**: La descomposicion en modulos de codigo es arquitectura tecnica, pertenece al Plan.
- **Reescritura sugerida**: Eliminar seccion completa "Logica de Negocio Compartida (KMM)".
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

### Contaminacion de endpoints API

#### [C-005] Especificacion de endpoints API en cada RF
- **Cita**: > "Endpoints API Requeridos: POST /api/v1/workers/auth/login — Autenticar con email y contrasena; retorna token Sanctum..." (se repite en todos los RFs)
- **Problema**: Los endpoints API, sus rutas, metodos HTTP, parametros y detalles de la respuesta son implementacion tecnica. El resumen de endpoints API y los endpoints listados en cada RF deben ir al Plan. El spec solo necesita describir que informacion necesita o produce cada funcionalidad.
- **Reescritura sugerida**: Eliminar todas las subsecciones "Endpoints API Requeridos" de cada RF y la seccion "Resumen de Endpoints API". Si un RF necesita clarificar que datos se intercambian, describirlo funcionalmente (ej: "La trabajadora envia su email y contrasena; el sistema valida las credenciales y establece la sesion").
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

### Contaminacion de detalles de seguridad e implementacion

#### [C-006] Token Sanctum y mecanismo de autenticacion
- **Cita**: > "Autenticacion basada en JWT", "token Sanctum valido 30 dias", "iOS Keychain / Android Keystore", "EncryptedSharedPreferences"
- **Problema**: JWT, Sanctum, Keychain, Keystore y EncryptedSharedPreferences son detalles de implementacion de seguridad. El spec solo necesita decir que la sesion se mantiene activa de forma segura durante un periodo configurable.
- **Reescritura sugerida**: "La sesion de la usuaria se mantiene activa tras el primer inicio de sesion. La sesion expira si la usuaria cierra sesion explicitamente, si la cuenta es revocada, o tras un periodo de inactividad prolongado (configurado por el sistema)"
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

#### [C-007] RF-1.5 Gestion del Token de Sesion como RF completo
- **Cita**: > "La API utiliza un unico token Sanctum valido 30 dias (no hay mecanismo de access token + refresh token en la version actual). La app verifica la validez del token llamando a /auth/validate-token al arrancar"
- **Problema**: Todo el RF-1.5 describe un mecanismo tecnico de gestion de tokens. Funcionalmente, el comportamiento relevante (sesion persistente, redireccion a login si expira) ya esta cubierto en RF-1.3. Este RF completo pertenece al Plan.
- **Reescritura sugerida**: Eliminar RF-1.5 como RF independiente. Integrar el comportamiento funcional relevante (la sesion persiste entre usos, si la sesion ya no es valida el sistema redirige al login) en RF-1.3.
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

#### [C-008] Almacenamiento seguro especifico de plataforma
- **Cita**: > "CA8: Almacenar tokens de forma segura (iOS Keychain / Android Keystore)"
- **Problema**: La tecnologia de almacenamiento es especifica de plataforma. Funcionalmente basta con decir que los datos de sesion se almacenan de forma segura.
- **Reescritura sugerida**: "Los datos de sesion se almacenan de forma segura en el dispositivo"
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

#### [C-009] Detalles de compresion y formatos tecnicos
- **Cita**: > "Guardar firma como archivo PNG", "Compresion automatica", "TLS 1.2+", "Anclaje de certificados"
- **Problema**: Formatos de archivo de almacenamiento interno, protocolos de cifrado y tecnicas de seguridad de red son implementacion. Funcionalmente: "la firma se guarda y puede reutilizarse", "las imagenes se optimizan antes de subir", "la comunicacion es segura".
- **Reescritura sugerida**: Reformular cada instancia en terminos funcionales: "La firma capturada se almacena y puede reutilizarse", "Las imagenes se optimizan automaticamente antes de enviarse", "Toda la comunicacion con el servidor es segura"
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

### Contaminacion de publicacion y plataforma

#### [C-010] RF-12 Publicacion de la Aplicacion
- **Cita**: > "Bundle ID: es.cuideo.hogar (iOS) / es.cuideo.hogar (Android)", "App Store Connect", "Google Play Console", "TestFlight", "Jetpack Compose"
- **Problema**: Todo el RF-12 (bundle IDs, configuracion de stores, TestFlight, metadatos de tienda) es proceso de despliegue tecnico. Los colores hex especificos tambien son diseno visual tecnico. Funcionalmente, lo relevante es que son dos apps con marca diferenciada.
- **Reescritura sugerida**: Reducir a: "Se publican dos aplicaciones diferenciadas por marca: CUIDEO (tema azul, perfil Hogar) y Felizvita (tema verde, perfil SAD). Ambas disponibles en iOS y Android." Los detalles de publicacion van al Plan.
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

### Contaminacion en Requisitos No Funcionales

#### [C-011] RNFs con detalles de implementacion
- **Cita**: > "Firebase Crashlytics integrado", "Firebase Analytics integrado", "Metadatos de crash personalizados: usuaria_id, profile_type, app_state", "44x44 pts (iOS) / 48x48 dp (Android)"
- **Problema**: Las herramientas de monitorizacion, los nombres de campos de metadatos, y las unidades de medida especificas de plataforma son implementacion. Funcionalmente: "los errores se reportan automaticamente", "se registra el uso basico de la app", "los elementos interactivos tienen tamano adecuado para interaccion tactil".
- **Reescritura sugerida**: Reformular cada RNF en terminos funcionales, eliminando nombres de herramientas y medidas de plataforma.
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

#### [C-012] Backend como API REST con JSON
- **Cita**: > "Backend: API RESTful, Formato de respuesta JSON, Autenticacion basada en JWT"
- **Problema**: El protocolo de comunicacion, formato de datos y mecanismo de autenticacion son arquitectura tecnica.
- **Reescritura sugerida**: "La aplicacion se comunica con un servicio de backend gestionado por el equipo del cliente para obtener y enviar datos"
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

#### [C-013] Realtime database para mensajeria
- **Cita**: > "CA11: Actualizaciones de mensajes en tiempo real (realtime database)"
- **Problema**: "Realtime database" es una tecnologia especifica (Firebase Realtime Database). La necesidad funcional es que los mensajes se actualicen en tiempo real.
- **Reescritura sugerida**: "Los mensajes nuevos aparecen automaticamente en la conversacion sin que la usuaria tenga que refrescar"
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

#### [C-014] Token FCM en notificaciones
- **Cita**: > "Registrar token FCM del dispositivo con el backend", "vincular el token FCM al usuario concreto"
- **Problema**: FCM (Firebase Cloud Messaging) y el concepto de "token FCM" son detalles de implementacion de notificaciones push.
- **Reescritura sugerida**: "El dispositivo se registra para recibir notificaciones push vinculadas al usuario autenticado"
- **Accion**: `[X] ACEPTAR` . `[ ] EDITAR` . `[ ] RECHAZAR (justificar)`

---

## Testabilidad: REQUIERE_MEJORA

Ningun CA del documento usa formato GIVEN/WHEN/THEN, ninguno referencia una HU padre (porque no hay HUs formales), y muchos son declaraciones de comportamiento sin precondicion clara. Se listan los CAs mas problematicos que requieren reformulacion prioritaria.

#### [CA-001] RF-1.0 CA2 — Duracion de splash ambigua
- **CA actual**: "Duracion de 2-3 segundos antes de redirigir automaticamente"
- **Problema**: Rango impreciso (2 o 3 segundos). No es verificable de forma objetiva porque el resultado depende de la interpretacion del rango.
- **Sugerencia de reformulacion**:
  ```
  GIVEN la app se esta iniciando
  WHEN se muestra la pantalla de splash
  THEN la pantalla se muestra durante un maximo de 3 segundos antes de redirigir automaticamente
  ```

#### [CA-002] RF-1.1 CA1 — Numero de pantallas de bienvenida ambiguo
- **CA actual**: "Mostrar 3-5 pantallas de bienvenida (ideal 3, maximo 5), priorizando los highlights principales"
- **Problema**: "3-5" con "ideal 3" es vago. No se definen los contenidos de las pantallas, por lo que no se puede verificar que muestran "highlights principales".
- **Sugerencia de reformulacion**:
  ```
  GIVEN la usuaria ha iniciado sesion por primera vez y no ha completado el onboarding
  WHEN se muestra el flujo de bienvenida
  THEN se presentan exactamente N pantallas con los siguientes contenidos: [definir contenidos]
  ```

#### [CA-003] RF-1.3 CA4 — Bloqueo temporal sin definicion de N
- **CA actual**: "Bloqueo temporal tras N intentos fallidos (N configurable en servidor)"
- **Problema**: "N" no esta definido. Tampoco se especifica que ve la usuaria durante el bloqueo ni cuanto dura.
- **Sugerencia de reformulacion**:
  ```
  GIVEN la usuaria ha introducido credenciales incorrectas N veces consecutivas (N definido por el servidor)
  WHEN intenta un nuevo inicio de sesion
  THEN el sistema muestra un mensaje indicando que la cuenta esta temporalmente bloqueada y el tiempo de espera restante
  ```

#### [CA-004] RF-2.1 CA3 — Badges sin definicion de origen
- **CA actual**: "Mostrar notificaciones de badge en los accesos directos (mensajes no leidos, acciones pendientes)"
- **Problema**: "Acciones pendientes" es vago. No se especifica que acciones generan badge ni como se calcula el contador.
- **Sugerencia de reformulacion**:
  ```
  GIVEN la usuaria esta en el panel principal
  WHEN hay mensajes no leidos en Comunicacion O documentos pendientes de firma O llamamientos pendientes de respuesta
  THEN el acceso directo correspondiente muestra un badge con el numero de items pendientes
  ```

#### [CA-005] RF-2.3 CA1 — Criticidad de mensajes sin definicion
- **CA actual**: "Mostrar lista de mensajes con remitente, asunto, fecha" (y en la descripcion: "dos niveles de criticidad, alta se mostraran diferentes y primero y normal se mostraran debajo")
- **Problema**: Se menciona "alta" y "normal" criticidad pero no se define como se determina, como se diferencia visualmente, ni que criterios aplican.
- **Sugerencia de reformulacion**:
  ```
  GIVEN hay mensajes del sistema con diferentes niveles de criticidad
  WHEN la usuaria accede a la lista de mensajes del sistema
  THEN los mensajes de criticidad alta se muestran primero, con diferenciacion visual clara respecto a los de criticidad normal
  ```

#### [CA-006] RF-3.2 CA2 — Datos de salud pendientes de RGPD
- **CA actual**: "Mostrar informacion del cliente (nombre, direccion, edad). Informacion de salud: pendiente de revision RGPD"
- **Problema**: El CA contiene una decision pendiente ("pendiente de revision RGPD") que lo hace no verificable. No se puede testear algo que aun no esta decidido.
- **Sugerencia de reformulacion**: Requiere respuesta del cliente (ver gap [P-003]).

#### [CA-007] RF-3.4 CA8 — Inaccion como rechazo pendiente de revision legal
- **CA actual**: "Las llamadas caducan automaticamente tras el tiempo limite configurado desde backoffice; si no hay respuesta puede computar como rechazo por inaccion (pendiente de revision legal)"
- **Problema**: "Puede computar" y "pendiente de revision legal" hacen que el CA sea no verificable. Hay dos comportamientos posibles sin decision.
- **Sugerencia de reformulacion**: Requiere respuesta del cliente (ver gap [P-005]).

#### [CA-008] RF-5.1 CA7 — Compresion automatica sin criterio
- **CA actual**: "Comprimir imagenes automaticamente"
- **Problema**: No se define el criterio de compresion ni el resultado esperado verificable. Ademas "comprimir" es un detalle tecnico; funcionalmente importa que las imagenes se puedan enviar de forma eficiente.
- **Sugerencia de reformulacion**:
  ```
  GIVEN la usuaria adjunta imagenes a una incidencia
  WHEN las imagenes superan un tamano razonable para el envio
  THEN el sistema las optimiza automaticamente antes de enviarlas, manteniendo calidad suficiente para su proposito
  ```

#### [CA-009] RF-8.2 CA10 — Vacaciones por dias naturales pendiente de confirmar
- **CA actual**: "Las vacaciones se computan por dias naturales (pendiente de confirmar con cliente/legal)"
- **Problema**: Decision pendiente de confirmar. No se puede verificar un comportamiento que no esta decidido.
- **Sugerencia de reformulacion**: Requiere respuesta del cliente (ver gap [P-009]).

#### [CA-010] RF-9.1 CA1 — Tipo de contrato con inconsistencia Swagger
- **CA actual**: "Contrato (solo SAD): Tipo (Indefinido, Fijo Discontinuo), Fecha de inicio. El Swagger v1.6.0 devuelve contract_type: 'Tiempo completo' | 'Tiempo parcial' — pendiente alinear con backend"
- **Problema**: Hay una inconsistencia conocida entre los valores esperados y los del backend. Esto hace que el CA sea no verificable hasta que se resuelva.
- **Sugerencia de reformulacion**: Requiere respuesta del cliente (ver gap [P-010]).

---

## Puntos pendientes de validacion con cliente

> Estos puntos **no fueron inferidos por el sistema**. Son ambiguedades o informacion ausente
> que debe ser definida por el cliente antes de generar el `.spec` final.
> **Instruccion**: escribe la respuesta del cliente en el campo "Respuesta" de cada punto.
>
> - `[CRITICO]`: afecta directamente a las HUs indicadas en "Afecta". Si se deja sin responder, esas HUs se marcaran como `[INCOMPLETO]` en el spec — se generaran con la informacion disponible pero no podran avanzar a plan/tasks hasta completarse.
> - `[INFORMATIVO]`: si no se responde, se aplicara la "Asuncion por defecto" indicada.

### [P-001][CRITICO] Contenido de las pantallas de onboarding
- **Contexto**: RF-1.1 CA1 indica "3-5 pantallas de bienvenida priorizando los highlights principales" pero no define el contenido de cada pantalla.
- **Problema**: Sin saber que contenido se muestra en cada pantalla de onboarding, no se pueden redactar los CAs verificables ni los journeys del flujo de bienvenida.
- **Afecta**: funcionalidad de onboarding (RF-1.1)
- **Pregunta para el cliente**: Cuales son los contenidos especificos de cada pantalla de onboarding? Cuantas pantallas exactas se mostraran y que mensaje/informacion contiene cada una?
- **Respuesta**: _(pendiente)_

### [P-002][CRITICO] Tabla de destinos de navegacion para deeplinks de notificaciones push
- **Contexto**: RF-11.1 CA5 indica "Tocar notificacion abre aplicacion en pantalla especifica via deeplink" y lista 10 tipos de notificaciones, pero no especifica a que pantalla exacta navega cada tipo.
- **Problema**: Sin una tabla de destinos de navegacion, cada tipo de notificacion es ambiguo. Dos personas podrian implementar destinos diferentes para la misma notificacion (ej: "Nuevo comunicado en el tablon" podria llevar al listado o al detalle del comunicado).
- **Afecta**: funcionalidad de notificaciones push (RF-11.1), funcionalidad de panel principal (RF-2.1)
- **Pregunta para el cliente**: Para cada uno de los 10 tipos de notificacion listados, a que pantalla exacta de la app debe navegar el deeplink al tocar la notificacion?
- **Respuesta**: _(pendiente)_

### [P-003][CRITICO] Visibilidad de datos de salud del cliente en detalle de servicio
- **Contexto**: RF-3.2 CA2 dice "Informacion de salud: pendiente de revision RGPD — consultar con legal antes de mostrar medicacion u otros datos persistentes de salud en el lado de la cuidadora"
- **Problema**: La decision sobre si se muestran o no datos de salud del cliente impacta directamente el diseno del detalle de servicio y los CAs asociados. Sin esta decision, el comportamiento no es verificable.
- **Afecta**: funcionalidad de detalle de servicio (RF-3.2)
- **Pregunta para el cliente**: Tras la revision RGPD, se mostraran datos de salud del cliente (medicacion, condiciones) a la cuidadora en el detalle de servicio? Si es asi, cuales exactamente?
- **Respuesta**: _(pendiente)_

### [P-004][CRITICO] Datos completos del detalle de un llamamiento
- **Contexto**: RF-3.4 CA2 muestra la "informacion basica" (codigo de servicio, fecha/hora, ubicacion, urgencia) y CA3 dice "Tocar llamada para ver detalles completos (mas campos que la informacion basica)" sin especificar cuales son esos campos adicionales.
- **Problema**: Sin saber que campos adicionales aparecen en el detalle del llamamiento, no se puede verificar que la pantalla de detalle muestra la informacion correcta. Ademas, la trabajadora debe tomar una decision (aceptar/rechazar) basandose en esa informacion, por lo que es critico saber que ve.
- **Afecta**: funcionalidad de llamamientos (RF-3.4)
- **Pregunta para el cliente**: Que informacion adicional se muestra en el detalle completo de un llamamiento, mas alla de la informacion basica (codigo, fecha/hora, ubicacion, urgencia)?
- **Respuesta**: _(pendiente)_

### [P-005][CRITICO] Consecuencia de no responder un llamamiento (inaccion = rechazo o no)
- **Contexto**: RF-3.4 CA8 indica "si no hay respuesta puede computar como rechazo por inaccion (pendiente de revision legal)"
- **Problema**: Esta decision legal afecta directamente al comportamiento del sistema y a los CAs del flujo de llamamientos. "Puede computar" no es verificable.
- **Afecta**: funcionalidad de llamamientos (RF-3.4)
- **Pregunta para el cliente**: Tras la revision legal, la inaccion ante un llamamiento caducado computa como rechazo formal o simplemente como "no respondido"? Que consecuencias tiene para la trabajadora en cada caso?
- **Respuesta**: _(pendiente)_

### [P-006][CRITICO] Textos oficiales de aceptacion y rechazo de llamamientos
- **Contexto**: RF-3.4 CA4 dice "el copy de aceptacion debe ser claro e inequivoco (solicitar textos oficiales a negocio/legal)" y CA5 dice "el copy de rechazo debe ser explicito y distinguirse claramente del de aceptacion"
- **Problema**: Los textos legales de aceptacion y rechazo son esenciales para la firma digital y tienen implicaciones legales. Sin ellos, los CAs del flujo de firma no son verificables.
- **Afecta**: funcionalidad de llamamientos (RF-3.4)
- **Pregunta para el cliente**: Cuales son los textos oficiales exactos que debe mostrar la app para la aceptacion y el rechazo de un llamamiento (los que la trabajadora firma digitalmente)?
- **Respuesta**: _(pendiente)_

### [P-007][CRITICO] Reglas de campos editables vs. no editables del perfil
- **Contexto**: RF-9.1 describe que los datos "core" no son editables y la direccion si, pero no se define de forma exhaustiva que campos son editables, cuales solo-lectura, y cuales admiten "propuesta de cambio".
- **Problema**: Sin una clasificacion clara de cada campo (editable / solo-lectura / propuesta-de-cambio), los CAs del perfil no son verificables y la implementacion sera ambigua.
- **Afecta**: funcionalidad de perfil (RF-9.1)
- **Pregunta para el cliente**: Para cada campo del perfil (nombre, email, telefono, direccion, fecha nacimiento, DNI/NIE, experiencia, especializaciones, certificaciones, educacion, idiomas), cual es su clasificacion: editable directamente, solo lectura, o admite propuesta de cambio con justificacion?
- **Respuesta**: _(pendiente)_

### [P-008][CRITICO] Campos obligatorios para completar perfil antes de aplicar a oferta (Hogar)
- **Contexto**: RF-9.1 CA11 indica "al intentar aplicar a una oferta, se muestra una advertencia o bloqueo informando de los campos obligatorios pendientes" pero no especifica cuales son esos campos obligatorios.
- **Problema**: Sin la lista de campos obligatorios, no se pueden verificar los CAs del flujo de "completar perfil" ni el bloqueo al aplicar a ofertas.
- **Afecta**: funcionalidad de perfil (RF-9.1), funcionalidad de ofertas (RF-6.2)
- **Pregunta para el cliente**: Cuales son los campos del perfil que son obligatorios para poder aplicar a una oferta en el perfil Hogar?
- **Respuesta**: _(pendiente)_

### [P-009][CRITICO] Computo de vacaciones: dias naturales o laborables
- **Contexto**: RF-8.2 CA10 indica "Las vacaciones se computan por dias naturales (pendiente de confirmar con cliente/legal)"
- **Problema**: La forma de computo afecta directamente al calculo del saldo de vacaciones y a los CAs del historial de ausencias. Es una regla de negocio fundamental.
- **Afecta**: funcionalidad de ausencias (RF-8.1, RF-8.2)
- **Pregunta para el cliente**: Se confirma que las vacaciones se computan por dias naturales? O se computan por dias laborables?
- **Respuesta**: _(pendiente)_

### [P-010][CRITICO] Tipo de contrato: valores correctos
- **Contexto**: RF-9.1 CA1 y RF-9.5 CA1 esperan "Indefinido / Fijo Discontinuo" pero notan que el Swagger devuelve "Tiempo completo / Tiempo parcial". Se pregunta si son el mismo campo o dos dimensiones distintas.
- **Problema**: Si son dos campos distintos (tipo de contrato + jornada), el perfil y la pantalla de contrato necesitan mostrar ambos. Si es uno solo, hay que decidir cuales son los valores correctos. Afecta a todos los CAs que muestran informacion del contrato.
- **Afecta**: funcionalidad de perfil (RF-9.1), funcionalidad de estado del contrato (RF-9.5)
- **Pregunta para el cliente**: "Indefinido/Fijo Discontinuo" y "Tiempo completo/Tiempo parcial" son el mismo campo con valores diferentes, o son dos dimensiones distintas del contrato (tipo de relacion + tipo de jornada)?
- **Respuesta**: _(pendiente)_

### [P-011][CRITICO] Comportamiento cuando la app no tiene permiso de ubicacion al fichar
- **Contexto**: RF-4.1 describe que se capturan coordenadas GPS al fichar y CA5 dice "Permitir fichar incluso sin precision de ubicacion optima", pero no se aclara que ocurre si la usuaria denego el permiso de ubicacion completamente.
- **Problema**: Hay diferencia entre "precision baja" (permiso concedido pero senal debil) y "sin permiso" (la usuaria lo denego). El comportamiento en el segundo caso no esta definido y es critico porque el fichaje con geolocalizacion es una funcionalidad central.
- **Afecta**: funcionalidad de fichaje (RF-4.1)
- **Pregunta para el cliente**: Si la trabajadora ha denegado el permiso de ubicacion, puede fichar sin coordenadas GPS? O se le debe pedir que habilite la ubicacion como requisito para fichar?
- **Respuesta**: _(pendiente)_

### [P-012][INFORMATIVO] Comportamiento de la app sin conexion a internet
- **Contexto**: El PRD menciona "Modo offline con sincronizacion" como fuera de alcance, pero no especifica que ocurre cuando la usuaria intenta realizar acciones sin conexion (fichar, enviar incidencia, etc.).
- **Pregunta para el cliente**: Cual es el comportamiento esperado cuando la usuaria no tiene conexion a internet? Se muestra un mensaje generico de error? Se permite algun tipo de cola local para fichajes?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.

### [P-013][INFORMATIVO] Limite de tamano por adjunto en notas de servicio
- **Contexto**: RF-3.3 permite "Adjuntar archivos (fotos, documentos) a las notas" pero no especifica limite de tamano ni numero maximo de adjuntos por nota.
- **Pregunta para el cliente**: Cual es el limite de tamano por adjunto y el numero maximo de adjuntos permitidos en las notas de servicio?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Maximo 5 adjuntos por nota, maximo 10 MB por adjunto. Mismas restricciones que en el modulo de incidencias (RF-5.1).

### [P-014][INFORMATIVO] Busqueda de conversaciones: por que campos
- **Contexto**: RF-10.2 CA7 dice "Buscar conversaciones" pero no especifica por que campos se busca (asunto, contenido de mensajes, nombre del coordinador, etc.).
- **Pregunta para el cliente**: La busqueda de conversaciones filtra por asunto, por contenido de los mensajes, o por ambos?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: La busqueda filtra por asunto de la conversacion unicamente.

### [P-015][INFORMATIVO] Comportamiento del historial de notificaciones
- **Contexto**: RF-11.1 lista el endpoint "GET /api/v1/workers/notifications" para listar historial, pero no se describe la pantalla de historial de notificaciones como funcionalidad: que muestra, como se ordena, si se pueden borrar.
- **Pregunta para el cliente**: Existe una pantalla de historial de notificaciones accesible para la usuaria? Que informacion muestra cada notificacion en el historial? Se pueden borrar notificaciones individuales?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Las notificaciones se listan en orden cronologico inverso mostrando titulo, cuerpo y fecha. Se pueden marcar todas como leidas pero no se pueden borrar individualmente.

### [P-016][INFORMATIVO] Accion al tocar una notificacion de "Conversacion cerrada"
- **Contexto**: En la lista de tipos de notificaciones (RF-11.1) aparece "Conversacion cerrada por coordinacion (deeplink al historial de la conversacion)" que es el unico tipo con destino explicito, pero plantea la duda de si "historial de la conversacion" se refiere a la propia conversacion cerrada (en modo lectura) o al listado de conversaciones.
- **Pregunta para el cliente**: Al tocar la notificacion de "Conversacion cerrada", la app navega al hilo de esa conversacion en modo lectura, o al listado general de conversaciones?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: La app navega directamente al hilo de la conversacion cerrada, mostrando el historial completo en modo lectura.

### [P-017][INFORMATIVO] Wireframes y guias de marca
- **Contexto**: El documento indica "[A proporcionar por el equipo de diseno]" para wireframes y "[A proporcionar por el cliente]" para guias de marca.
- **Pregunta para el cliente**: Se dispone ya de wireframes o guias de marca? Si no, hay fecha prevista para su entrega?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Se generara el spec con la informacion funcional disponible. Los detalles visuales se incorporaran cuando se disponga de los wireframes y guias de marca, sin bloquear la generacion del spec.

### [P-018][INFORMATIVO] Franjas horarias predefinidas: rangos exactos
- **Contexto**: RF-7.1 CA4 menciona franjas predefinidas "Manana, Tarde, Noche, Interna, Finde" pero no define los rangos horarios exactos de cada franja (ej: Manana = 07:00-15:00?).
- **Pregunta para el cliente**: Cuales son los rangos horarios exactos de cada franja predefinida (Manana, Tarde, Noche, Interna, Finde)?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Los rangos horarios seran configurados desde el servidor y la app los mostrara tal como los recibe. Si no los provee el servidor, se aplicaran valores por defecto razonables (Manana: 07:00-15:00, Tarde: 15:00-22:00, Noche: 22:00-07:00, Interna: 08:00-20:00, Finde: 07:00-22:00 sabados y domingos).

### [P-019][INFORMATIVO] Formato y duracion de la cuenta atras del llamamiento
- **Contexto**: RF-3.4 CA9 menciona "Cuenta atras visual para llamadas pendientes" y RF-2.1 CA7 menciona "cuenta atras de caducidad", pero no se define si es un contador numerico (hh:mm:ss), una barra de progreso, o ambos.
- **Pregunta para el cliente**: En que formato se muestra la cuenta atras del llamamiento (contador numerico, barra de progreso, otro)?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Contador numerico mostrando horas y minutos restantes (formato "Xh Xmin restantes").

### [P-020][INFORMATIVO] Edicion de notas de servicio
- **Contexto**: RF-3.3 CA6 menciona "Borrar notas propias (borrado suave)" y hay endpoint PUT para editar notas, pero los CAs no mencionan explicitamente la funcionalidad de editar una nota ya creada.
- **Pregunta para el cliente**: Las trabajadoras pueden editar notas de servicio ya creadas, o solo crearlas y borrarlas?
- **Respuesta**: _(pendiente)_
- **Asuncion por defecto**: Las trabajadoras pueden editar sus propias notas de servicio mientras no hayan sido leidas por la coordinadora. Una vez leidas, solo se puede borrar (borrado suave).

---

## Proximos pasos

1. En la seccion "Pureza", para cada contaminacion marca **una** de las tres acciones:
   - `[x] ACEPTAR` — se usara la reescritura tal cual en el spec
   - `[x] EDITAR` — modifica el texto de "Reescritura sugerida" y marca esta opcion
   - `[x] RECHAZAR (justificar)` — anade tu justificacion; el texto original se conservara como excepcion documentada
2. Responder los puntos `[CRITICO]` que puedas — los que queden sin respuesta marcaran sus HUs como `[INCOMPLETO]` en el spec (se generaran pero no podran avanzar a plan/tasks)
3. Responder los puntos `[INFORMATIVO]` si tienes la informacion — si no, se aplicara la asuncion por defecto
4. Una vez revisado, ejecutar:
   ```
   /wf-spec-finalize prd-hogar-sad.md
   ```
5. Para completar HUs marcadas `[INCOMPLETO]` despues: responde los gaps pendientes en este archivo y ejecuta `/wf-spec-delta resolve <feature_spec.md>`
