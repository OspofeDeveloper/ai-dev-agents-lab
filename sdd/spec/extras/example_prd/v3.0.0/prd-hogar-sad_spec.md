> ⚠️ **ARCHIVO** — Este spec monolitico ha sido descompuesto en features independientes.
> Consulta `prd-hogar-sad_features.md` como hub del proyecto y `features/` para los specs individuales.
> Fecha de archivo: 2026-04-05

# Spec: Aplicaciones Moviles CUIDEO - Hogar & SAD

> Version: 1.0 | Fecha: 2026-04-05 | Generado desde: prd-hogar-sad.md

---

## Resumen de generacion

### Estado de los 8 elementos SDD

| Elemento | Estado |
|----------|--------|
| Actores | COMPLETO — 4 actores identificados con capacidades |
| Historias de Usuario | INCOMPLETO — 44 HUs generadas; 15 marcadas [INCOMPLETO] por gaps criticos pendientes |
| Recorridos de Usuario | INCOMPLETO — journeys generados para todos los flujos principales; los asociados a HUs incompletas tienen pasos parciales |
| Resultados y Exito | INCOMPLETO — definidos para todos los flujos; los asociados a HUs incompletas son parciales |
| Instrucciones Inambiguas | INCOMPLETO — reglas de comportamiento documentadas; tabla de destinos de navegacion pendiente (gap P-002) |
| Criterios de Aceptacion | INCOMPLETO — CAs en formato GIVEN/WHEN/THEN generados; los asociados a HUs incompletas son parciales o estan omitidos |
| Checklist de Validacion | COMPLETO — checklist presente con items verificados |
| Fuera de Alcance | COMPLETO — exclusiones funcionales definidas |

### HUs incompletas

| HU | Titulo | Gaps pendientes |
|----|--------|-----------------|
| HU-003 | Pantallas de bienvenida (onboarding) | P-001 |
| HU-020 | Deeplinks de notificaciones push | P-002 |
| HU-021 | Notificaciones automaticas del sistema | P-002 |
| HU-014 | Detalle del servicio | P-003 |
| HU-016 | Detalle del llamamiento | P-004, P-006 |
| HU-017 | Aceptar o rechazar llamamiento | P-005, P-006 |
| HU-032 | Ver y editar perfil | P-007 |
| HU-037 | Solicitar oferta de trabajo | P-008 |
| HU-026 | Solicitar ausencia | P-009 |
| HU-027 | Historial de ausencias | P-009 |
| HU-033 | Estado del contrato | P-010 |
| HU-022 | Fichar entrada y salida | P-011 |

### Asunciones por defecto aplicadas

| Seccion | Asuncion aplicada | Origen (gap) |
|---------|-------------------|--------------|
| Comportamiento sin conexion | Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico. | P-012 |
| Adjuntos en notas de servicio | Maximo 5 adjuntos por nota, maximo 10 MB por adjunto | P-013 |
| Busqueda de conversaciones | La busqueda filtra por asunto de la conversacion unicamente | P-014 |
| Historial de notificaciones | Las notificaciones se listan en orden cronologico inverso mostrando titulo, cuerpo y fecha. Se pueden marcar todas como leidas pero no se pueden borrar individualmente | P-015 |
| Notificacion de conversacion cerrada | La app navega directamente al hilo de la conversacion cerrada, mostrando el historial completo en modo lectura | P-016 |
| Wireframes y guias de marca | Se genera el spec con la informacion funcional disponible. Los detalles visuales se incorporaran cuando se disponga de los wireframes y guias de marca | P-017 |
| Franjas horarias predefinidas | Los rangos horarios seran configurados desde el servidor y la app los mostrara tal como los recibe. Si no los provee el servidor, se aplicaran valores por defecto razonables (Manana: 07:00-15:00, Tarde: 15:00-22:00, Noche: 22:00-07:00, Interna: 08:00-20:00, Finde: 07:00-22:00 sabados y domingos) | P-018 |
| Cuenta atras del llamamiento | Contador numerico mostrando horas y minutos restantes (formato "Xh Xmin restantes") | P-019 |
| Edicion de notas de servicio | Las trabajadoras pueden editar sus propias notas de servicio mientras no hayan sido leidas por la coordinadora. Una vez leidas, solo se puede borrar (borrado suave) | P-020 |

### Contaminaciones de Pureza procesadas

| ID | Accion | Detalle |
|----|--------|---------|
| C-001 | ACEPTAR | Eliminada referencia a KMM del descriptor del producto |
| C-002 | ACEPTAR | Eliminada seccion completa "Arquitectura del Sistema" |
| C-003 | ACEPTAR | Reemplazadas referencias a Firebase por descripciones funcionales |
| C-004 | ACEPTAR | Eliminada seccion "Logica de Negocio Compartida (KMM)" |
| C-005 | ACEPTAR | Eliminados todos los endpoints API de cada RF |
| C-006 | ACEPTAR | Reemplazadas referencias a tokens Sanctum/JWT/Keychain/Keystore por descripcion funcional de sesion |
| C-007 | ACEPTAR | Eliminado RF-1.5 como RF independiente; comportamiento integrado en sesion persistente |
| C-008 | ACEPTAR | Reemplazado "iOS Keychain / Android Keystore" por "almacenamiento seguro" |
| C-009 | ACEPTAR | Reformulados detalles de compresion, formatos y protocolos en terminos funcionales |
| C-010 | ACEPTAR | Reducido RF-12 a descripcion funcional de dos apps diferenciadas por marca |
| C-011 | ACEPTAR | Reformulados RNFs eliminando nombres de herramientas y medidas de plataforma |
| C-012 | ACEPTAR | Reemplazada referencia a API REST/JSON/JWT por descripcion funcional |
| C-013 | ACEPTAR | Reemplazado "realtime database" por "mensajes se actualizan automaticamente" |
| C-014 | ACEPTAR | Reemplazado "token FCM" por "dispositivo registrado para notificaciones push" |

---

## Actores

| Actor | Descripcion | Capacidades en este spec |
|-------|-------------|--------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades de empleo a traves de la app CUIDEO (tema azul) | Registrarse, iniciar sesion, navegar y aplicar a ofertas de trabajo, gestionar disponibilidad, gestionar perfil y documentos, comunicarse con coordinacion, recibir notificaciones |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios asignados a traves de la app Felizvita (tema verde) | Iniciar sesion (cuenta activada desde backoffice), gestionar servicios asignados, fichar entrada/salida con geolocalizacion, registrar notas de servicio, responder llamamientos, reportar incidencias, solicitar ausencias, gestionar disponibilidad, gestionar perfil y documentos, firmar documentos, comunicarse con coordinacion, recibir notificaciones, ver estado del contrato |
| Coordinadora / Backoffice | Profesional de gestion interna que supervisa a las trabajadoras. No usa la app movil directamente; interactua a traves del sistema de backoffice | Asignar servicios, enviar llamamientos, gestionar conversaciones (responder, cerrar), publicar comunicados, configurar tipos de documento y carpetas, gestionar visibilidad de campos de servicio, aprobar/rechazar ausencias, responder incidencias, configurar parametros del sistema |
| Sistema | El propio sistema automatizado que ejecuta acciones programadas sin intervencion humana | Enviar notificaciones push automaticas (recordatorios de fichaje, caducidad de documentos, servicio proximo, disponibilidad), gestionar expiracion de sesiones, desactivar llamamientos caducados |

---

## Historias de Usuario

### HU-001: Pantalla de splash
Como trabajadora (Hogar o SAD)
quiero ver una pantalla de bienvenida con el logo de la app al abrirla
para que tenga una experiencia de carga fluida y sepa que la app esta iniciando correctamente.

### HU-002: Registro de cuenta (Hogar)
Como trabajadora Hogar
quiero registrarme en la app con mi email y contrasena
para que pueda acceder a las ofertas de trabajo y funcionalidades de la app.

### HU-003: Pantallas de bienvenida (onboarding)
Como trabajadora (Hogar o SAD)
quiero ver una guia de bienvenida tras mi primer inicio de sesion
para que entienda las funcionalidades principales de la app antes de empezar a usarla.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-004: Activacion de cuenta (SAD)
Como trabajadora SAD
quiero activar mi cuenta a traves de un enlace de email enviado desde el backoffice
para que pueda establecer mis credenciales y acceder a la app por primera vez.

### HU-005: Inicio de sesion
Como trabajadora (Hogar o SAD)
quiero iniciar sesion con mi email y contrasena
para que pueda acceder a las funcionalidades de la app de forma segura.

### HU-006: Sesion persistente
Como trabajadora (Hogar o SAD)
quiero que mi sesion se mantenga activa entre usos de la app
para que no tenga que iniciar sesion cada vez que abro la app.

### HU-007: Recuperacion de acceso
Como trabajadora (Hogar o SAD)
quiero poder recuperar el acceso a mi cuenta si olvido mi contrasena
para que no pierda el acceso a la app de forma permanente.

### HU-008: Cierre de sesion
Como trabajadora (Hogar o SAD)
quiero poder cerrar mi sesion de forma explicita
para que nadie mas pueda acceder a mi cuenta desde mi dispositivo.

### HU-009: Pantalla de acceso revocado (SAD)
Como trabajadora SAD cuya cuenta ha sido suspendida o dada de baja
quiero ver una pantalla informativa clara cuando intento acceder
para que entienda por que no puedo entrar y sepa como contactar a soporte.

### HU-010: Panel principal con accesos directos
Como trabajadora (Hogar o SAD)
quiero ver un panel principal con accesos rapidos a las secciones mas importantes
para que pueda navegar eficientemente a las funcionalidades que mas uso.

### HU-011: Tablon de anuncios y comunicados
Como trabajadora (Hogar o SAD)
quiero consultar los comunicados y contenidos informativos de la empresa
para que este al dia con protocolos, novedades y comunicaciones importantes.

### HU-012: Mensajes del sistema
Como trabajadora (Hogar o SAD)
quiero consultar los mensajes de administracion enviados por el sistema
para que no pierda informacion importante de gestion.

### HU-013: Listado de servicios (SAD)
Como trabajadora SAD
quiero ver todos mis servicios asignados con su estado
para que pueda organizar mi jornada y saber que servicios tengo activos, proximos y completados.

### HU-014: Detalle del servicio (SAD)
Como trabajadora SAD
quiero ver la informacion completa de un servicio especifico
para que pueda conocer los datos del cliente, ubicacion, plan de cuidados y tareas antes de acudir.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-003]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-015: Notas de servicio (SAD)
Como trabajadora SAD
quiero registrar notas sobre la evolucion del servicio con adjuntos
para que las coordinadoras tengan constancia de las tareas realizadas y las incidencias observadas.

### HU-016: Detalle del llamamiento (SAD)
Como trabajadora SAD
quiero ver la informacion completa de un llamamiento recibido
para que pueda tomar una decision informada sobre si acepto o rechazo el turno ofrecido.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-004], [P-006]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-017: Aceptar o rechazar llamamiento (SAD)
Como trabajadora SAD
quiero poder aceptar o rechazar un llamamiento con firma digital
para que quede constancia formal de mi decision sobre el turno ofrecido.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-005], [P-006]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-018: Listado de llamamientos (SAD)
Como trabajadora SAD
quiero ver todas las llamadas de servicio recibidas con su estado
para que pueda hacer seguimiento de mis llamamientos pendientes, aceptados, rechazados y caducados.

### HU-019: Nuevo servicio asignado - contratos indefinidos (SAD)
Como trabajadora SAD con contrato indefinido
quiero recibir una notificacion cuando se me asigna un nuevo servicio
para que este informada de mis nuevos servicios y pueda comunicar si no puedo atenderlos.

### HU-020: Deeplinks de notificaciones push
Como trabajadora (Hogar o SAD)
quiero que al tocar una notificacion push la app me lleve directamente a la pantalla relevante
para que pueda actuar rapidamente sobre el evento notificado sin buscar manualmente.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-002]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-021: Notificaciones automaticas del sistema
Como trabajadora (Hogar o SAD)
quiero recibir recordatorios automaticos de acciones importantes
para que no olvide fichar, actualizar disponibilidad, renovar documentos o preparar servicios proximos.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-002]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-022: Fichar entrada y salida (SAD)
Como trabajadora SAD
quiero fichar mi entrada y salida de un servicio con captura de ubicacion
para que quede constancia verificable del tiempo trabajado en cada servicio.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-011]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-023: Historial de seguimiento de tiempo (SAD)
Como trabajadora SAD
quiero ver todos mis registros de entrada y salida agrupados por servicio
para que pueda revisar mi historial de tiempo trabajado.

### HU-024: Reportar incidencia (SAD)
Como trabajadora SAD
quiero reportar incidencias del servicio o del cliente con descripcion y adjuntos
para que las coordinadoras esten informadas de problemas que requieren atencion.

### HU-025: Historial de incidencias (SAD)
Como trabajadora SAD
quiero ver todas las incidencias que he reportado con su estado y respuestas
para que pueda hacer seguimiento de los problemas comunicados.

### HU-026: Solicitar ausencia (SAD)
Como trabajadora SAD
quiero solicitar tiempo libre indicando tipo, fechas y justificacion
para que coordinacion pueda gestionar mi ausencia y reorganizar los servicios.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-009]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-027: Historial de ausencias (SAD)
Como trabajadora SAD
quiero ver todas mis solicitudes de ausencia con su estado y saldo de vacaciones
para que pueda planificar mis ausencias y conocer los dias disponibles.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-009]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-028: Navegar ofertas de trabajo (Hogar)
Como trabajadora Hogar
quiero consultar las ofertas de trabajo disponibles con filtros
para que pueda encontrar oportunidades de empleo que se ajusten a mi zona y horario.

### HU-029: Calendario de disponibilidad
Como trabajadora (Hogar o SAD)
quiero gestionar mi disponibilidad semanal mediante un calendario con franjas horarias
para que el sistema de planificacion pueda asignarme servicios en los horarios que he declarado como disponibles.

### HU-030: Historial de servicios (SAD)
Como trabajadora SAD
quiero ver mi historial de servicios completados y llamamientos pasados
para que pueda consultar mi actividad anterior y el resultado de cada llamamiento.

### HU-031: Registrar dispositivo para notificaciones push
Como trabajadora (Hogar o SAD)
quiero que mi dispositivo quede registrado para recibir notificaciones push
para que me lleguen avisos importantes de servicios, mensajes y recordatorios.

### HU-032: Ver y editar perfil
Como trabajadora (Hogar o SAD)
quiero ver mi informacion personal y profesional y editar los campos permitidos
para que mi perfil este actualizado y completo.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-007]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-033: Estado del contrato (SAD)
Como trabajadora SAD
quiero ver la informacion de mi contrato actual
para que conozca mi tipo de contrato, fecha de inicio y pueda descargar el documento.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-010]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-034: Foto de perfil
Como trabajadora (Hogar o SAD)
quiero subir y actualizar mi foto de perfil
para que mi cuenta tenga una imagen personal identificable.

### HU-035: Gestion de documentos
Como trabajadora (Hogar o SAD)
quiero ver, subir y gestionar mis documentos personales y consultar la documentacion laboral
para que toda mi documentacion este accesible y pueda firmar los documentos que se requieran.

### HU-036: Firma digital
Como trabajadora (Hogar o SAD)
quiero capturar mi firma manuscrita en la pantalla
para que pueda firmar documentos y llamamientos de forma digital sin necesidad de papel.

### HU-037: Solicitar oferta de trabajo (Hogar)
Como trabajadora Hogar
quiero solicitar una oferta de trabajo desde la app
para que mi candidatura sea enviada a las coordinadoras para su revision.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-008]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-038: Mis solicitudes (Hogar)
Como trabajadora Hogar
quiero ver todas las solicitudes que he presentado con su estado
para que pueda hacer seguimiento de mis candidaturas y saber si han sido aceptadas o rechazadas.

### HU-039: Iniciar conversacion con coordinacion
Como trabajadora (Hogar o SAD)
quiero iniciar una nueva conversacion con coordinacion seleccionando un asunto
para que mi consulta llegue al departamento correcto de forma transparente.

### HU-040: Listado de conversaciones
Como trabajadora (Hogar o SAD)
quiero ver todos mis hilos de conversacion con estado de lectura
para que pueda gestionar mis comunicaciones con coordinacion.

### HU-041: Hilo de conversacion
Como trabajadora (Hogar o SAD)
quiero enviar y recibir mensajes dentro de una conversacion
para que pueda comunicarme de forma fluida con coordinacion sobre temas de servicio, ausencias o consultas.

### HU-042: Historial de notificaciones
Como trabajadora (Hogar o SAD)
quiero consultar el historial de notificaciones recibidas
para que pueda revisar avisos pasados que haya podido perder.

### HU-043: Aplicaciones de marca diferenciada
Como trabajadora (Hogar o SAD)
quiero usar una app con la marca correspondiente a mi perfil (CUIDEO o Felizvita)
para que la experiencia visual sea coherente con el servicio al que pertenezco.

### HU-044: Completar perfil antes de aplicar (Hogar)
Como trabajadora Hogar
quiero ser informada de los campos obligatorios pendientes al intentar aplicar a una oferta
para que pueda completar mi perfil y no perder oportunidades por tener datos incompletos.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-008]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

---

## Recorridos de Usuario

### Journey 1: Registro y primer acceso (Hogar)
Actor: Trabajadora Hogar | Objetivo: Registrarse en la app y acceder por primera vez

1. La trabajadora abre la app CUIDEO y ve la pantalla de splash con el logo azul.
2. Tras la pantalla de splash, la app muestra la pantalla de inicio de sesion (no hay sesion previa).
3. La trabajadora pulsa "Registrarse".
4. La trabajadora introduce su email y elige una contrasena (minimo 8 caracteres, al menos una mayuscula y un numero).
5. La trabajadora envia el formulario de registro.
6. El sistema valida los datos y completa el registro. La trabajadora queda autenticada automaticamente.
7. El sistema solicita permiso de notificaciones push.
8. Se muestra el flujo de bienvenida (onboarding) con pantallas informativas sobre las funcionalidades de la app.
9. La trabajadora completa el onboarding (se muestra solo una vez).
10. La trabajadora accede al panel principal (home) con accesos directos a: Ofertas, Mi Disponibilidad, Perfil, Comunicacion.

Estado de exito: La trabajadora ha creado su cuenta, ha completado el onboarding y esta en el panel principal con todas las funcionalidades accesibles.

Flujos alternativos:
- Si el email ya esta registrado: el sistema muestra un mensaje de error indicando que el email ya existe.
- Si la contrasena no cumple los requisitos: se muestra el error de validacion en linea.

### Journey 2: Activacion y primer acceso (SAD)
Actor: Trabajadora SAD | Objetivo: Activar su cuenta y acceder por primera vez

1. La trabajadora recibe un email de activacion enviado desde el backoffice.
2. La trabajadora abre el enlace de activacion del email.
3. El enlace la lleva a una pantalla donde puede establecer su contrasena (el email ya esta preconfigurado).
4. La trabajadora establece su contrasena y confirma.
5. La trabajadora abre la app Felizvita y ve la pantalla de splash con el logo verde.
6. La app muestra la pantalla de inicio de sesion.
7. La trabajadora introduce su email y contrasena.
8. El sistema valida las credenciales y establece la sesion.
9. El sistema solicita permiso de notificaciones push.
10. Se muestra el flujo de bienvenida (onboarding).
11. La trabajadora completa el onboarding y accede al panel principal (home) con accesos directos priorizando el servicio activo y el fichaje.

Estado de exito: La trabajadora SAD ha activado su cuenta, ha iniciado sesion y esta en el panel principal con todas las funcionalidades accesibles.

Flujos alternativos:
- Si la cuenta ha sido revocada o suspendida: se muestra la pantalla de acceso revocado con mensaje "Ya no tienes permisos para acceder a esta aplicacion" e informacion de contacto de soporte.

### Journey 3: Inicio de sesion habitual
Actor: Trabajadora (Hogar o SAD) | Objetivo: Acceder a la app tras haberla cerrado

1. La trabajadora abre la app y ve la pantalla de splash.
2. El sistema verifica la validez de la sesion almacenada.
3. Si la sesion es valida: la app navega directamente al panel principal sin mostrar la pantalla de inicio de sesion.
4. Si la sesion ha expirado o ha sido revocada: la app muestra la pantalla de inicio de sesion.

Estado de exito: La trabajadora accede al panel principal sin friccion si tiene sesion valida, o puede iniciar sesion si la sesion expiro.

Flujos alternativos:
- Si la cuenta ha sido dada de baja (solo SAD): se muestra la pantalla de acceso revocado.

### Journey 4: Recuperacion de acceso
Actor: Trabajadora (Hogar o SAD) | Objetivo: Recuperar el acceso a su cuenta tras olvidar la contrasena

1. La trabajadora esta en la pantalla de inicio de sesion y pulsa "Olvidaste tu contrasena?" o similar.
2. El sistema muestra la pantalla de recuperacion con un campo de email.
3. La trabajadora introduce su email y pulsa enviar.
4. El sistema muestra un mensaje de confirmacion generico (sin revelar si el email existe en el sistema).
5. Si el email es valido, la trabajadora recibe un email con un enlace de recuperacion.
6. La trabajadora abre el enlace y accede a la pantalla de establecer nueva contrasena.
7. La trabajadora introduce su nueva contrasena (cumpliendo los mismos requisitos de seguridad que el registro).
8. El sistema confirma el cambio y la trabajadora puede iniciar sesion con la nueva contrasena.

Estado de exito: La trabajadora ha restablecido su contrasena y puede acceder nuevamente a la app.

Flujos alternativos:
- Si el enlace ha caducado: el sistema informa que el enlace ya no es valido e invita a solicitar uno nuevo.
- Si la cuenta esta dada de baja o suspendida: el enlace no permite el acceso y se muestra la pantalla de acceso revocado.

### Journey 5: Consultar servicios y ver detalle (SAD)
Actor: Trabajadora SAD | Objetivo: Revisar sus servicios asignados y consultar detalles

1. La trabajadora accede al panel principal. El bloque de servicios muestra como maximo el servicio activo y el siguiente servicio; si hay mas, se muestra un enlace "Ver mas servicios".
2. La trabajadora pulsa sobre un servicio o navega a "Mis Servicios".
3. El sistema muestra la lista de servicios agrupados por estado: Activos, Proximos, Completados.
4. Cada servicio muestra informacion clave: nombre/codigo del cliente, direccion, fecha/hora, tipo (con distincion visual entre recurrentes y puntuales).
5. La trabajadora toca un servicio para ver el detalle.
6. El detalle muestra: informacion basica (codigo, tipo, fechas, horario), informacion del cliente (nombre, direccion, edad — la visibilidad de campos es controlable desde backoffice), plan de cuidados, listado descriptivo de tareas (no editable), documentacion asociada.
7. La direccion del servicio se muestra como texto clickable que abre la app de mapas del dispositivo.
8. Desde el detalle, la trabajadora puede acceder a: notas de servicio, historial de fichaje del servicio, fichar entrada/salida, reportar incidencia, contactar con coordinacion.

Estado de exito: La trabajadora ha consultado el detalle completo de un servicio y sabe donde acudir, que tareas realizar y como contactar con coordinacion.

### Journey 6: Fichar entrada y salida de servicio (SAD)
Actor: Trabajadora SAD | Objetivo: Registrar el inicio y fin de un servicio

1. La trabajadora recibe una notificacion push indicando que puede fichar (configurable, enviada antes del inicio del servicio). El mensaje incluye su nombre y el nombre del receptor del servicio.
2. La trabajadora accede al fichaje desde la home, el detalle del servicio o el tab de fichaje.
3. El boton de fichaje muestra estados dinamicos: "Disponible en X min" (antes de los 30 minutos previos), "Fichar entrada" (activo 30 minutos antes del inicio del servicio), "Fichada - en servicio", "Fichar salida", "Servicio finalizado".
4. La trabajadora selecciona el servicio de la lista de servicios activos (si accede desde home o tab de fichaje).
5. La trabajadora pulsa "Fichar entrada".
6. El sistema captura las coordenadas GPS. Si la precision de ubicacion es baja, muestra una advertencia (espera maximo 2 segundos) pero permite continuar.
7. Se confirma la entrada y el sistema muestra un contador de tiempo transcurrido.
8. Al finalizar, la trabajadora pulsa "Fichar salida".
9. El sistema muestra un dialogo de confirmacion.
10. La trabajadora confirma y se registra la salida con coordenadas GPS.

Estado de exito: La trabajadora ha fichado entrada y salida correctamente con registro de ubicacion y tiempo.

Flujos alternativos:
- Si la trabajadora no ficha la salida tras finalizar: se muestra un aviso visible (banner o notificacion in-app) recordando la accion pendiente. El aviso no bloquea la navegacion.
- Si la trabajadora necesita reportar un problema de fichaje: desde la pantalla de fichaje puede reportar una incidencia de fichaje o solicitar una ausencia.
- Si no hay fichajes entre servicios del mismo dia: cada servicio se gestiona de forma independiente.

### Journey 7: Responder a un llamamiento (SAD)
Actor: Trabajadora SAD | Objetivo: Decidir sobre un turno ofrecido

1. La trabajadora recibe una notificacion push de nuevo llamamiento.
2. En la home, el llamamiento pendiente se muestra de forma prominente con indicacion de urgencia y cuenta atras de caducidad (formato "Xh Xmin restantes").
3. La trabajadora toca el llamamiento, accediendo al detalle.
4. El detalle muestra la informacion basica (codigo de servicio, fecha/hora, ubicacion, urgencia) y campos adicionales.
5. Una vez en el detalle, la trabajadora no puede salir sin tomar una decision (la navegacion hacia atras esta bloqueada).
6. Para aceptar: la trabajadora pulsa "Aceptar" y se le muestra un dialogo donde debe firmar digitalmente con el dedo.
7. Para rechazar: la trabajadora pulsa "Rechazar", selecciona un motivo obligatorio (No disponible, Demasiado lejos, Motivos personales, Otros con texto libre) y firma digitalmente.
8. Tras la decision, el sistema confirma y el llamamiento cambia de estado.

Estado de exito: La trabajadora ha tomado una decision sobre el llamamiento, firmada digitalmente, y el sistema ha registrado su respuesta.

Flujos alternativos:
- Si el llamamiento caduca antes de la respuesta: se muestra como desactivado/no disponible.
- Si otra trabajadora acepta el llamamiento: se muestra como desactivado/no disponible.

### Journey 8: Reportar incidencia (SAD)
Actor: Trabajadora SAD | Objetivo: Comunicar un problema ocurrido en el servicio

1. La trabajadora accede al reporte de incidencias desde el detalle del servicio, la pantalla de fichaje o la seccion de incidencias.
2. Selecciona el tipo de incidencia: Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros.
3. Selecciona el servicio relacionado (si aplica).
4. Introduce la descripcion (obligatorio, minimo 20 caracteres).
5. Opcionalmente adjunta fotos (maximo 5, desde camara o galeria) y/o documentos (maximo 3). Las imagenes se optimizan automaticamente antes de enviarse.
6. El sistema muestra el tamano estimado de subida.
7. La trabajadora envia la incidencia.
8. El sistema confirma el envio. La incidencia queda inmediatamente visible para las coordinadoras.

Estado de exito: La incidencia ha sido reportada con toda la informacion necesaria y es visible para coordinacion.

### Journey 9: Solicitar ausencia (SAD)
Actor: Trabajadora SAD | Objetivo: Solicitar tiempo libre

1. La trabajadora accede a "Solicitar Ausencia" desde la home o la seccion de ausencias.
2. Selecciona el tipo de ausencia: Vacaciones, Permiso personal, Baja medica, Baja voluntaria, Asuntos propios, Otros.
3. Selecciona rango de fechas (con opcion de medio dia para inicio y final).
4. Si es baja medica de mas de 3 dias: debe adjuntar certificado medico.
5. Introduce motivo/descripcion (obligatorio para algunos tipos).
6. El sistema muestra el saldo de vacaciones disponible antes de enviar.
7. Si las fechas entran en conflicto con servicios asignados: se muestra una advertencia.
8. La trabajadora envia la solicitud.
9. Recibe notificacion push de confirmacion de envio.

Estado de exito: La solicitud de ausencia ha sido enviada para aprobacion por coordinacion.

### Journey 10: Navegar y solicitar oferta (Hogar)
Actor: Trabajadora Hogar | Objetivo: Encontrar y aplicar a una oferta de trabajo

1. La trabajadora accede a "Ofertas" desde la home.
2. El sistema muestra una lista de ofertas disponibles en formato de tarjeta (titulo, ubicacion, horario, tarifa horaria). Las publicadas en las ultimas 48h muestran insignia "Nuevo".
3. La trabajadora puede filtrar por codigo postal/zona, horario (manana, tarde, noche, madrugada, 24h), rango de fecha de inicio.
4. Puede ordenar por: mas recientes, ubicacion mas cercana, tarifa mas alta.
5. La trabajadora toca una oferta para ver el detalle completo.
6. Pulsa "Aplicar".
7. El sistema muestra un dialogo de confirmacion con resumen de la oferta.
8. La trabajadora confirma y la solicitud se envia.
9. Recibe notificacion de confirmacion.

Estado de exito: La trabajadora ha encontrado una oferta relevante, la ha revisado y ha enviado su solicitud.

Flujos alternativos:
- Si intenta aplicar con perfil incompleto: se muestra advertencia con los campos obligatorios pendientes y acceso directo a completarlos.
- Si ya ha aplicado a esa oferta: se previene la solicitud duplicada.
- Si no hay ofertas coincidentes: se muestra estado vacio.

### Journey 11: Gestionar disponibilidad
Actor: Trabajadora (Hogar o SAD) | Objetivo: Declarar sus franjas horarias disponibles en la semana

1. La trabajadora accede a "Mi Disponibilidad".
2. La pantalla muestra en la cabecera la informacion de horas trabajadas vs. horas de contrato (ej: "30 / 40 h" o "Te faltan X horas").
3. Se muestra una vista semanal (Lun-Dom) con los slots existentes: Disponible (color diferenciado), No disponible (color diferenciado), Activa (color diferenciado, solo lectura).
4. La trabajadora selecciona un dia.
5. Se activa el panel de franjas rapidas (Manana, Tarde, Noche, Interna, Finde) y el formulario de slot personalizado.
6. Al pulsar una franja rapida, se crea inmediatamente un slot de tipo "Disponible" con el rango horario correspondiente.
7. Para crear un slot personalizado: la trabajadora introduce hora de inicio y fin, y selecciona tipo (Disponible o No disponible).
8. Los slots de distinto tipo pueden solaparse. Los del mismo tipo no pueden solaparse (la API devuelve error).
9. La trabajadora puede tocar un slot Disponible o No disponible para editarlo o eliminarlo. Los slots Activa son solo lectura.
10. Los cambios se guardan inmediatamente al confirmar cada slot.

Estado de exito: La trabajadora ha declarado sus franjas de disponibilidad y puede ver como se reflejan en el calendario junto con las asignaciones activas del sistema.

### Journey 12: Comunicarse con coordinacion
Actor: Trabajadora (Hogar o SAD) | Objetivo: Consultar o comunicar algo a coordinacion

1. La trabajadora accede a "Comunicacion".
2. Ve el listado de conversaciones (ordenadas por ultimo mensaje) con asunto, preview y marca de tiempo. Las conversaciones cerradas se muestran con indicador visual diferenciado.
3. Para iniciar una nueva conversacion, pulsa "Nueva conversacion".
4. Selecciona un asunto predefinido: Vacaciones/Ausencia, Nomina/Facturacion, Sobre un servicio, Documentacion, Consulta general, Otros.
5. Opcionalmente enlaza contexto (servicio u oferta relacionados).
6. Escribe su primer mensaje y envia.
7. La conversacion se presenta en formato chat. Siempre ve la conversacion como comunicacion con "Coordinacion", independientemente del enrutado interno.
8. Los mensajes nuevos del equipo de coordinacion aparecen automaticamente sin necesidad de refrescar.

Estado de exito: La trabajadora ha iniciado o continuado una conversacion con coordinacion y ha recibido respuesta.

Flujos alternativos:
- Si la conversacion ha sido cerrada por coordinacion: la trabajadora puede ver el historial completo en modo lectura pero no puede escribir nuevos mensajes.

### Journey 13: Gestionar documentos
Actor: Trabajadora (Hogar o SAD) | Objetivo: Consultar, subir y firmar documentos

1. La trabajadora accede a "Documentos" desde la home o el perfil.
2. La pantalla muestra dos categorias: Documentacion personal y Documentacion laboral (estructura de carpetas dinamica, configurable desde backoffice).
3. Para documentacion personal (DNI/NIE, certificados, etc.): la trabajadora puede subir y reemplazar documentos (formatos PDF, DOC, DOCX, JPG, PNG; maximo 10 MB; imagenes optimizadas automaticamente).
4. Para documentacion laboral (contrato, nominas, llamamientos firmados, etc.): solo puede consultar, descargar y firmar cuando corresponda. La gestion es exclusiva del backoffice.
5. Si hay documentos pendientes de firma: se muestra un aviso tanto en la seccion como en la home.
6. Si hay documentos proximos a caducar: el sistema envia avisos de caducidad.

Estado de exito: La trabajadora ha gestionado su documentacion personal y firmado los documentos laborales pendientes.

### Journey 14: Consultar historial de incidencias (SAD)
Actor: Trabajadora SAD | Objetivo: Revisar el estado de incidencias reportadas

1. La trabajadora accede a la seccion de incidencias.
2. El sistema muestra la lista de incidencias en orden cronologico inverso con: numero, tipo, fecha y estado (Reportada, En revision, Resuelta, Cerrada).
3. La trabajadora puede filtrar por estado, rango de fechas, o buscar por numero/descripcion.
4. Toca una incidencia para ver el detalle completo y los comentarios/respuestas de las coordinadoras.

Estado de exito: La trabajadora ha consultado el estado de sus incidencias y las respuestas de coordinacion.

### Journey 15: Consultar historial de ausencias (SAD)
Actor: Trabajadora SAD | Objetivo: Revisar sus solicitudes de ausencia y saldo

1. La trabajadora accede a "Mis Ausencias".
2. El sistema muestra la lista de ausencias en orden cronologico inverso con: tipo, fechas, recuento de dias y estado (Pendiente, Aprobada, Rechazada, Cancelada).
3. Se muestran los contadores por tipo de ausencia (vacaciones: asignacion total, dias utilizados, dias pendientes de aprobacion, dias disponibles).
4. La trabajadora puede filtrar por estado, tipo y ano.
5. Toca una ausencia para ver detalle y comentarios de coordinadora.
6. Puede cancelar solicitudes que esten en estado Pendiente.

Estado de exito: La trabajadora ha consultado su historial de ausencias y conoce su saldo disponible.

---

## Resultados y Exito

El sistema se considera exitoso cuando:

- **Acceso y sesion**: Las trabajadoras pueden registrarse (Hogar) o activar su cuenta (SAD), iniciar sesion y mantener una sesion persistente sin necesidad de autenticarse cada vez. La sesion solo se interrumpe por cierre explicito, revocacion de cuenta o expiracion por inactividad prolongada.
- **Servicios (SAD)**: Las trabajadoras SAD pueden consultar todos sus servicios asignados con informacion completa, navegar al detalle y conocer la ubicacion, plan de cuidados y tareas de cada servicio.
- **Fichaje (SAD)**: Las trabajadoras SAD fichan entrada y salida con captura de ubicacion de forma fluida desde multiples puntos de acceso. El fichaje se activa en la ventana temporal correcta y el sistema registra tanto el tiempo como las coordenadas.
- **Llamamientos (SAD)**: Las trabajadoras SAD reciben llamamientos con toda la informacion necesaria, pueden aceptar o rechazar con firma digital, y el sistema gestiona la caducidad y la competencia entre trabajadoras de forma transparente.
- **Incidencias (SAD)**: Las trabajadoras SAD pueden reportar incidencias con toda la informacion relevante y hacer seguimiento de su resolucion.
- **Ausencias (SAD)**: Las trabajadoras SAD pueden solicitar ausencias con la documentacion requerida y consultar su saldo de vacaciones.
- **Ofertas (Hogar)**: Las trabajadoras Hogar pueden navegar, filtrar y aplicar a ofertas de trabajo y hacer seguimiento de sus solicitudes.
- **Disponibilidad**: Las trabajadoras pueden declarar su disponibilidad semanal a traves de un calendario intuitivo y el sistema de planificacion utiliza esa informacion para la asignacion de servicios.
- **Comunicacion**: Las trabajadoras pueden comunicarse con coordinacion de forma fluida a traves de un sistema de chat con actualizacion en tiempo real.
- **Documentos y perfil**: Las trabajadoras pueden gestionar su documentacion personal, firmar documentos laborales y mantener su perfil actualizado.
- **Notificaciones**: Las trabajadoras reciben notificaciones push oportunas para todos los eventos importantes y pueden actuar rapidamente desde la notificacion.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Doble perfil**: Existen dos aplicaciones diferenciadas por marca (CUIDEO tema azul para Hogar, Felizvita tema verde para SAD). Cada app muestra unicamente las funcionalidades correspondientes a su perfil.
- **Sesion persistente**: La sesion se mantiene activa tras el primer inicio de sesion. Solo se solicita nuevo login si la trabajadora cierra sesion explicitamente, si la cuenta es revocada, o tras un periodo de inactividad prolongado configurado por el sistema.
- **Verificacion de sesion al arrancar**: Al abrir la app, el sistema verifica que la sesion almacenada sigue siendo valida. Si es valida, navega directamente al panel principal. Si no, muestra la pantalla de inicio de sesion.
- **Respuestas 401 del servidor**: Cualquier respuesta de sesion invalida del servidor redirige al inicio de sesion. Si multiples solicitudes simultaneas reciben esta respuesta, solo se redirige una vez.
- **Datos de sesion al cerrar sesion**: Al cerrar sesion se borran todos los datos de sesion almacenados localmente y se invalida la sesion en el servidor.
- **Onboarding unico**: Las pantallas de bienvenida se muestran una sola vez. El estado de completacion se almacena localmente.
- **Contenido general del onboarding**: El contenido del onboarding es general y valido para ambos tipos de contrato (fijo discontinuo e indefinido).
- **Permiso de notificaciones**: Se solicita despues del primer login y antes del onboarding, para vincular el dispositivo al usuario autenticado.
- **Permiso de camara/archivos**: Se solicita solo en el momento en que se necesite (ej: al subir un documento), no durante el onboarding.
- **Acceso revocado (SAD)**: Si la cuenta de una trabajadora SAD ha sido suspendida, dada de baja o desactivada, al intentar acceder se muestra una pantalla informativa con mensaje claro y datos de contacto de soporte. No se permite navegar a ninguna seccion de la app. No se almacenan datos de sesion.
- **Fichaje sin bloqueo por ubicacion**: El fichaje esta permitido incluso sin precision optima de ubicacion. Si la precision es baja, se muestra advertencia y se espera maximo 2 segundos antes de permitir continuar.
- **Ventana de fichaje**: El boton de fichaje de entrada se activa 30 minutos antes del inicio del servicio. Fuera de esa ventana aparece deshabilitado con indicacion visual del tiempo restante.
- **Warning de fichaje de salida pendiente**: Si la trabajadora no ficha la salida tras finalizar el servicio, se muestra un aviso visible (banner o notificacion in-app). Este aviso no bloquea la navegacion ni el acceso al resto de la app.
- **Fichaje independiente por servicio**: Los fichajes entre servicios del mismo dia se gestionan de forma independiente (no se bloquean entre si).
- **No hay fichaje manual**: Las correcciones de fichaje se gestionan desde backoffice, no desde la app de la trabajadora.
- **Llamamientos multi-envio**: El mismo llamamiento puede enviarse a varias trabajadoras simultaneamente. La primera en aceptar lo recibe y el resto queda desactivado (gestion desde backoffice).
- **Decision obligatoria en llamamiento**: Una vez dentro del detalle del llamamiento, la navegacion hacia atras queda bloqueada hasta que la trabajadora acepte o rechace (sin boton de retroceso).
- **Firma digital obligatoria**: Tanto la aceptacion como el rechazo de un llamamiento requieren firma digital de la trabajadora.
- **Caducidad de llamamientos**: Las llamadas caducan automaticamente tras el tiempo limite configurado desde backoffice.
- **Notas de servicio con adjuntos**: Maximo 5 adjuntos por nota, maximo 10 MB por adjunto (asuncion aplicada de P-013). Las trabajadoras pueden editar sus propias notas mientras no hayan sido leidas por la coordinadora. Una vez leidas, solo borrado suave (asuncion aplicada de P-020).
- **Incidencias - taxonomia**: Las incidencias son principalmente del servicio o del usuario atendido, no de la propia cuidadora (las ausencias tienen su propio flujo). Excepcion: "Incidencia de fichaje / No asistencia" para problemas operativos directos.
- **Tareas de servicio no editables**: El listado de tareas del servicio es descriptivo y no editable por la cuidadora; proviene de backend.
- **Visibilidad de campos del servicio controlada desde backoffice**: Cada campo del detalle del servicio (datos del cliente) puede marcarse como visible o no visible para la cuidadora desde backoffice.
- **Contacto de servicio**: Se muestra como "Contacta con tu coordinador / empresa" (no "contacto de emergencia") con el telefono de coordinacion.
- **Home SAD — bloque de servicios**: Muestra como maximo el servicio activo y el siguiente servicio. Si hay mas, se muestra enlace "Ver mas servicios" (no contador "+2" o similar).
- **Comunicacion con enrutado transparente**: La trabajadora siempre ve la conversacion como comunicacion con "Coordinacion". El enrutado interno a departamentos lo gestiona el backoffice de forma transparente.
- **Conversaciones cerradas**: Las conversaciones pueden ser cerradas por el equipo de backoffice. Quedan en modo historico de solo lectura (la trabajadora puede consultar pero no escribir).
- **Mensajes del sistema**: Son de solo lectura, no se pueden responder. Se diferencian en dos niveles de criticidad: alta (se muestran primero y con diferenciacion visual) y normal.
- **Documentacion personal**: La trabajadora puede subir y reemplazar documentos personales pero no eliminarlos. Formatos: PDF, DOC, DOCX, JPG, PNG. Maximo 10 MB. Imagenes optimizadas automaticamente.
- **Documentacion laboral**: Solo consulta, descarga y firma. La gestion es exclusiva del backoffice.
- **Estructura de documentos dinamica**: Las carpetas y tipos de documento son configurables desde backoffice.
- **Foto de perfil voluntaria**: La app funciona correctamente sin foto de perfil.
- **Porcentaje de completitud del perfil**: Visible en la pantalla principal del perfil y desde la home (Hogar).
- **Solapamiento de disponibilidad**: Los slots de distinto tipo (Disponible y No disponible) pueden solaparse. Los del mismo tipo no pueden solaparse (la API devuelve error).
- **Slots "Activa"**: Horas con servicio asignado por planificacion. Solo lectura, no editables ni eliminables desde la app.
- **Reglas de negocio de disponibilidad**: Maximo 8 horas de trabajo por dia, minimo 12 horas de descanso entre jornadas. Estas reglas las valida el servidor; la app muestra los errores que el servidor devuelva.
- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico (asuncion aplicada de P-012).
- **Busqueda de conversaciones**: Filtra por asunto de la conversacion unicamente (asuncion aplicada de P-014).
- **Cuenta atras de llamamientos**: Formato numerico mostrando horas y minutos restantes ("Xh Xmin restantes") (asuncion aplicada de P-019).
- **Mensajes en tiempo real**: Los mensajes nuevos en conversaciones aparecen automaticamente sin que la usuaria tenga que refrescar.
- **Maximo 3 toques**: Cualquier funcionalidad principal es accesible en un maximo de 3 toques desde el panel principal.
- **Idioma inicial**: Solo castellano. La arquitectura soporta multiples idiomas (catalan, ingles, frances preparados para el futuro).
- **Formato de fechas y numeros**: Respeta la configuracion regional del dispositivo.

### Destinos de navegacion

> ⚠ Tabla de destinos de navegacion para deeplinks de notificaciones push pendiente de definicion (gap P-002). Los tipos de notificacion definidos son:
> - Nuevo mensaje recibido
> - Conversacion cerrada por coordinacion
> - Llamada de servicio disponible
> - Cambio de estado de solicitud
> - Cambio de estado de solicitud de ausencia
> - Servicio comenzando pronto (ventana de fichaje abierta)
> - Servicio proximo manana
> - Documento caducando pronto
> - Actualizacion de incidencia
> - Nuevo comunicado en el tablon
>
> Asuncion aplicada (P-016): La notificacion de "Conversacion cerrada" navega directamente al hilo de la conversacion cerrada en modo lectura.

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Panel principal (SAD) | Tocar tarjeta de servicio | Detalle del servicio (RF-3.2) |
| Panel principal (SAD) | Tocar llamamiento pendiente | Detalle del llamamiento (RF-3.4) |
| Panel principal (SAD) | Tocar "Ver mas servicios" | Listado de servicios (RF-3.1) |
| Panel principal (SAD) | Tocar "Ultimos avisos" | Tablon de anuncios completo (RF-2.2) |
| Panel principal (Hogar) | Tocar acceso directo Ofertas | Listado de ofertas (RF-6.1) |
| Panel principal (Hogar) | Tocar acceso directo Disponibilidad | Calendario de disponibilidad (RF-7.1) |
| Panel principal (Hogar) | Tocar acceso directo Perfil | Pantalla de perfil (RF-9.1) |
| Panel principal (Hogar) | Tocar acceso directo Comunicacion | Listado de conversaciones (RF-10.2) |
| Listado de servicios | Tocar servicio | Detalle del servicio (RF-3.2) |
| Detalle del servicio | Tocar direccion | App de mapas del dispositivo (Google Maps / Apple Maps) |
| Detalle del servicio | Tocar "Notas de servicio" | Listado de notas del servicio (RF-3.3) |
| Detalle del servicio | Tocar "Fichar" | Pantalla de fichaje (RF-4.1) |
| Detalle del servicio | Tocar "Reportar incidencia" | Formulario de incidencia (RF-5.1) |
| Detalle del servicio | Tocar "Contacta coordinador" | Llamada telefonica a coordinacion |
| Detalle del servicio | Tocar "Historial de fichaje" | Historial de seguimiento de tiempo del servicio (RF-4.2) |
| Listado de llamamientos | Tocar llamamiento | Detalle del llamamiento (RF-3.4) |
| Detalle del llamamiento | Aceptar + firma | Confirmacion y vuelta a listado |
| Detalle del llamamiento | Rechazar + motivo + firma | Confirmacion y vuelta a listado |
| Listado de ofertas | Tocar oferta | Detalle de oferta (RF-6.1) |
| Detalle de oferta | Pulsar "Aplicar" | Dialogo confirmacion, luego vuelta a detalle con estado "Aplicada" |
| Listado de conversaciones | Tocar conversacion | Hilo de conversacion (RF-10.3) |
| Listado de conversaciones | Pulsar "Nueva conversacion" | Selector de asunto + formulario de primer mensaje (RF-10.1) |
| Home o Perfil | Tocar "Documentos" | Pantalla de documentos unificada (RF-9.3) |
| Splash | Sesion valida | Panel principal |
| Splash | Sesion invalida/no existe | Pantalla de inicio de sesion |
| Login | Cuenta revocada (SAD) | Pantalla de acceso revocado (RF-1.7) |

---

## Criterios de Aceptacion

### CA-001: Splash con logo de marca ← HU-001
GIVEN la trabajadora abre la app
WHEN la app inicia la carga
THEN se muestra la pantalla de splash con el logo de la aplicacion sobre fondo de marca durante un maximo de 3 segundos

### CA-002: Redireccion desde splash segun sesion ← HU-001
GIVEN la pantalla de splash ha finalizado
WHEN el sistema verifica el estado de la sesion
THEN si hay sesion valida, navega al panel principal; si no hay sesion o la sesion es invalida, navega a la pantalla de inicio de sesion

### CA-003: Registro con email y contrasena (Hogar) ← HU-002
GIVEN la trabajadora Hogar esta en la pantalla de registro
WHEN introduce un email valido y una contrasena que cumple los requisitos (minimo 8 caracteres, al menos una mayuscula y un numero)
THEN el sistema completa el registro y la trabajadora queda autenticada automaticamente con sesion activa

### CA-004: Validacion de registro (Hogar) ← HU-002
GIVEN la trabajadora Hogar esta en la pantalla de registro
WHEN introduce un email con formato invalido o una contrasena que no cumple los requisitos
THEN se muestran mensajes de error de validacion en linea indicando el problema especifico

### CA-005: Activacion de cuenta SAD ← HU-004
GIVEN una trabajadora SAD ha recibido un email de activacion desde el backoffice
WHEN abre el enlace del email
THEN puede establecer su contrasena (el email ya esta preconfigurado) y acceder a la app

### CA-006: Inicio de sesion con credenciales ← HU-005
GIVEN la trabajadora esta en la pantalla de inicio de sesion
WHEN introduce email y contrasena validos
THEN el sistema autentica a la trabajadora, establece la sesion y navega al panel principal

### CA-007: Error de credenciales ← HU-005
GIVEN la trabajadora esta en la pantalla de inicio de sesion
WHEN introduce credenciales incorrectas
THEN se muestra un mensaje de error claro indicando que las credenciales no son validas

### CA-008: Bloqueo temporal por intentos fallidos ← HU-005
GIVEN la trabajadora ha introducido credenciales incorrectas N veces consecutivas (N definido por el servidor)
WHEN intenta un nuevo inicio de sesion
THEN el sistema muestra un mensaje indicando que la cuenta esta temporalmente bloqueada y el tiempo de espera restante

### CA-009: Sesion persistente entre usos ← HU-006
GIVEN la trabajadora ha iniciado sesion previamente y no ha cerrado sesion
WHEN abre la app
THEN el sistema verifica la sesion almacenada y, si es valida, navega directamente al panel principal sin mostrar pantalla de login

### CA-010: Redireccion a login por sesion invalida ← HU-006
GIVEN la sesion de la trabajadora ha expirado o ha sido revocada por el servidor
WHEN la app detecta la invalidez de la sesion (al arrancar o en cualquier solicitud al servidor)
THEN redirige a la pantalla de inicio de sesion. Si multiples solicitudes simultaneas detectan sesion invalida, solo se redirige una vez

### CA-011: Flujo de recuperacion de contrasena ��� HU-007
GIVEN la trabajadora esta en la pantalla de inicio de sesion
WHEN pulsa "Olvidaste tu contrasena?" o similar
THEN accede a la pantalla de recuperacion con campo de email

### CA-012: Envio de enlace de recuperacion ← HU-007
GIVEN la trabajadora esta en la pantalla de recuperacion
WHEN introduce su email y pulsa enviar
THEN el sistema muestra un mensaje de confirmacion generico (sin revelar si el email existe en el sistema)

### CA-013: Restablecimiento de contrasena ← HU-007
GIVEN la trabajadora ha recibido el email de recuperacion y abre el enlace
WHEN introduce una nueva contrasena que cumple los requisitos de seguridad
THEN la contrasena se restablece y la trabajadora puede iniciar sesion con la nueva contrasena

### CA-014: Enlace de recuperacion caducado ← HU-007
GIVEN la trabajadora abre un enlace de recuperacion que ha expirado
WHEN intenta restablecer la contrasena
THEN el sistema informa que el enlace ya no es valido e invita a solicitar uno nuevo

### CA-015: Cierre de sesion con confirmacion ← HU-008
GIVEN la trabajadora esta autenticada
WHEN pulsa cerrar sesion
THEN se muestra un dialogo de confirmacion. Al confirmar: se borran todos los datos de sesion locales, se invalida la sesion en el servidor y se redirige a la pantalla de inicio de sesion

### CA-016: Pantalla de acceso revocado (SAD) ← HU-009
GIVEN una trabajadora SAD cuya cuenta ha sido suspendida o dada de baja
WHEN intenta acceder a la app
THEN se muestra una pantalla informativa con mensaje "Ya no tienes permisos para acceder a esta aplicacion" e informacion de contacto de soporte. No se permite navegar a ninguna seccion ni se almacenan datos de sesion

### CA-017: Panel principal Hogar ← HU-010
GIVEN la trabajadora Hogar esta autenticada
WHEN accede al panel principal
THEN ve accesos directos a: Ofertas, Mi Disponibilidad, Perfil, Comunicacion. Se muestra su nombre y foto de perfil en la cabecera

### CA-018: Panel principal SAD ← HU-010
GIVEN la trabajadora SAD esta autenticada
WHEN accede al panel principal
THEN ve los accesos directos priorizando servicio activo y fichaje: Mis Servicios, Fichar, Incidencias, Solicitar Ausencia, Mis Ausencias, Mi Disponibilidad, Documentacion, Perfil, Comunicacion. El bloque "Ultimos avisos" muestra 2-3 items con acceso al listado completo. Se muestra su nombre y foto de perfil en la cabecera

### CA-019: Bloque de servicios en home SAD ← HU-010
GIVEN la trabajadora SAD tiene multiples servicios asignados
WHEN accede al panel principal
THEN el bloque de servicios muestra como maximo el servicio activo y el siguiente servicio. Si hay mas, se muestra el enlace "Ver mas servicios"

### CA-020: Llamamiento pendiente destacado en home SAD ← HU-010
GIVEN existe un llamamiento pendiente de respuesta para la trabajadora SAD
WHEN accede al panel principal
THEN el llamamiento se muestra de forma prominente con indicacion de urgencia y cuenta atras de caducidad. El CTA lleva al detalle del llamamiento (no permite aceptar/rechazar desde la home)

### CA-021: Documentacion pendiente de firma en home SAD ← HU-010
GIVEN hay documentos laborales pendientes de firma para la trabajadora SAD
WHEN accede al panel principal
THEN se muestra un badge/contador destacado para documentacion pendiente de firma como elemento de alta prioridad

### CA-022: Badges en accesos directos ← HU-010
GIVEN la trabajadora esta en el panel principal
WHEN hay mensajes no leidos en Comunicacion o documentos pendientes de firma o llamamientos pendientes de respuesta
THEN el acceso directo correspondiente muestra un badge con el numero de items pendientes

### CA-023: Pull-to-refresh en panel ← HU-010
GIVEN la trabajadora esta en el panel principal
WHEN hace pull-to-refresh
THEN los datos del panel se actualizan con la informacion mas reciente del servidor

### CA-024: Listado de comunicados con fijados ← HU-011
GIVEN la trabajadora accede al tablon de anuncios
WHEN se muestra la lista de comunicados
THEN los comunicados fijados desde backoffice aparecen en la parte superior. Se diferencian contenidos fijos (protocolos, calendario laboral, PRL, documentos de referencia) y comunicaciones variables (recordatorios, campanas, novedades). Cada comunicado muestra titulo, fecha y texto de previsualizacion

### CA-025: Detalle de comunicado ← HU-011
GIVEN la trabajadora esta en el tablon de anuncios
WHEN toca un comunicado
THEN se abre el detalle completo con soporte para imagenes y adjuntos. El comunicado se marca como leido automaticamente

### CA-026: Badge de comunicados no leidos ← HU-011
GIVEN hay comunicados no leidos
WHEN la trabajadora consulta el tablon o la home
THEN se muestra un indicador visual (badge) en el icono de la seccion indicando contenido nuevo

### CA-027: Notificacion push de nuevo comunicado ← HU-011
GIVEN se publica un nuevo comunicado desde backoffice
WHEN la trabajadora tiene notificaciones habilitadas
THEN recibe una notificacion push informando del nuevo comunicado

### CA-028: Lista de mensajes del sistema por criticidad ← HU-012
GIVEN hay mensajes del sistema con diferentes niveles de criticidad
WHEN la trabajadora accede a la lista de mensajes del sistema
THEN los mensajes de criticidad alta se muestran primero con diferenciacion visual clara respecto a los de criticidad normal. Cada mensaje muestra remitente, asunto y fecha con indicador visual para no leidos

### CA-029: Detalle de mensaje del sistema ← HU-012
GIVEN la trabajadora esta en la lista de mensajes del sistema
WHEN toca un mensaje
THEN se abre el contenido completo con soporte para adjuntos. El mensaje se marca como leido automaticamente. No hay opcion de responder

### CA-030: Borrar mensaje del sistema ← HU-012
GIVEN la trabajadora esta en la lista de mensajes del sistema
WHEN elige borrar un mensaje
THEN el mensaje se elimina de su lista

### CA-031: Listado de servicios por estado (SAD) ← HU-013
GIVEN la trabajadora SAD accede a "Mis Servicios"
WHEN se carga la lista
THEN se muestran los servicios agrupados por estado: Activos, Proximos, Completados. Cada servicio muestra nombre/codigo del cliente, direccion, fecha/hora, tipo. Hay distincion visual entre recurrentes y puntuales. Estado vacio cuando no hay servicios

### CA-032: Pull-to-refresh en listado de servicios ��� HU-013
GIVEN la trabajadora SAD esta en el listado de servicios
WHEN hace pull-to-refresh
THEN la lista se actualiza con la informacion mas reciente del servidor

### CA-033: Detalle de servicio con datos del cliente (SAD) ← HU-014
GIVEN la trabajadora SAD toca un servicio en el listado
WHEN se abre el detalle
THEN se muestra: informacion basica (codigo, tipo, fechas, horario), informacion del cliente (nombre, direccion, edad — la visibilidad de cada campo es controlable desde backoffice), plan de cuidados, listado descriptivo de tareas (no editable), documentacion asociada, CTA "Contacta con tu coordinador / empresa" con telefono

> ⚠ Parcial: La visibilidad de datos de salud del cliente depende de la resolucion de gap P-003.

### CA-034: Direccion clickable a app de mapas ← HU-014
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN toca la direccion del servicio
THEN se abre la app de mapas del dispositivo (Google Maps / Apple Maps) con la direccion del servicio

### CA-035: Accesos desde detalle de servicio ← HU-014
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN necesita realizar acciones sobre el servicio
THEN puede acceder a: notas de servicio, historial de fichaje, fichar entrada/salida, reportar incidencia

### CA-036: Listado de notas de servicio ← HU-015
GIVEN la trabajadora SAD accede a las notas de un servicio
WHEN se carga la lista
THEN se muestran las notas en orden cronologico con autora, fecha/hora, contenido, adjuntos y categoria (Evolucion, Tareas, Incidencias, Otras)

### CA-037: Crear nota de servicio con adjuntos ← HU-015
GIVEN la trabajadora SAD esta en las notas de un servicio
WHEN pulsa "Anadir nota"
THEN puede escribir texto multilinea, seleccionar categoria, y adjuntar archivos (maximo 5 adjuntos, maximo 10 MB por adjunto). La nota queda visible inmediatamente para las coordinadoras

### CA-038: Editar nota de servicio propia ← HU-015
GIVEN la trabajadora SAD tiene una nota propia que no ha sido leida por la coordinadora
WHEN toca la nota para editarla
THEN puede modificar el texto y los adjuntos de la nota

### CA-039: Borrar nota de servicio propia ← HU-015
GIVEN la trabajadora SAD tiene una nota propia
WHEN elige borrar la nota
THEN la nota se elimina con borrado suave (queda registrada para auditoria)

### CA-040: Listado de llamamientos con estado ← HU-018
GIVEN la trabajadora SAD accede al listado de llamamientos
WHEN se carga la lista
THEN se muestran todos los llamamientos con su estado (pendiente, aceptada, rechazada, caducada/desactivada). Cada uno muestra informacion basica: codigo de servicio, fecha/hora, ubicacion, urgencia

### CA-041: Cuenta atras en llamamiento pendiente ← HU-018
GIVEN hay un llamamiento en estado pendiente
WHEN la trabajadora lo ve en el listado o la home
THEN se muestra un contador numerico con horas y minutos restantes ("Xh Xmin restantes")

### CA-042: Llamamiento desactivado ← HU-018
GIVEN un llamamiento caduca o es aceptado por otra trabajadora
WHEN la trabajadora consulta el listado
THEN el llamamiento se muestra como desactivado/no disponible

### CA-043: Notificacion push nuevo servicio asignado (indefinido) ← HU-019
GIVEN una trabajadora SAD con contrato indefinido recibe un nuevo servicio
WHEN el servicio se asigna desde backoffice
THEN la trabajadora recibe notificacion push "Nuevo servicio asignado" con enlace al detalle del servicio

### CA-044: Visualizacion de servicio asignado en home (indefinido) ← HU-019
GIVEN una trabajadora SAD con contrato indefinido tiene un nuevo servicio asignado
WHEN accede al panel principal
THEN el nuevo servicio se muestra de forma visible y diferenciada de los llamamientos, con distincion visual entre servicios puntuales (con fecha inicio y fin) y recurrentes (sin fecha de fin)

### CA-045: Confirmacion de recepcion de servicio asignado ← HU-019
GIVEN una trabajadora SAD abre el detalle de un nuevo servicio asignado
WHEN el sistema registra que la trabajadora ha visto el servicio
THEN se registra la interaccion "visto/recibido". Desde el detalle, la trabajadora puede generar una incidencia si no puede atender el servicio

### CA-046: Fichar entrada con geolocalizacion ← HU-022
GIVEN la trabajadora SAD ha seleccionado un servicio activo y faltan 30 minutos o menos para el inicio
WHEN pulsa "Fichar entrada"
THEN el sistema captura las coordenadas GPS y registra la entrada. Se muestra un contador de tiempo transcurrido

### CA-047: Advertencia de precision baja al fichar ← HU-022
GIVEN la trabajadora SAD esta fichando entrada o salida
WHEN la precision de ubicacion GPS es baja
THEN se muestra una advertencia (espera maximo 2 segundos) pero se permite continuar con el fichaje

### CA-048: Fichar salida con confirmacion ← HU-022
GIVEN la trabajadora SAD esta fichada en un servicio
WHEN pulsa "Fichar salida"
THEN se muestra un dialogo de confirmacion. Al confirmar, se capturan las coordenadas GPS y se registra la salida

### CA-049: Estados dinamicos del boton de fichaje ← HU-022
GIVEN la trabajadora SAD ve el boton de fichaje de un servicio
WHEN consulta el estado del boton en diferentes momentos
THEN el boton muestra: "Disponible en X min" (fuera de ventana), "Fichar entrada" (en ventana de 30 min), "Fichada - en servicio" (fichada), "Fichar salida" (disponible para salida), "Servicio finalizado" (tras fichar salida)

### CA-050: Warning de salida pendiente ← HU-022
GIVEN la trabajadora SAD no ha fichado la salida tras finalizar el horario del servicio
WHEN continua usando la app
THEN se muestra un aviso visible (banner o notificacion in-app) recordando la accion pendiente, sin bloquear la navegacion

### CA-051: Incidencia de fichaje o solicitud de ausencia desde fichaje ← HU-022
GIVEN la trabajadora SAD esta en la pantalla de fichaje
WHEN necesita reportar un problema o ausencia
THEN tiene opcion de reportar una incidencia de fichaje o solicitar una ausencia directamente desde la pantalla

### CA-052: Notificacion de fichaje previo al servicio ← HU-022
GIVEN se acerca la hora de inicio de un servicio
WHEN faltan N minutos (configurado por el servidor)
THEN la trabajadora recibe una notificacion push con su nombre y el nombre del receptor del servicio (ej: "Buenos dias [nombre], ya puedes fichar para el servicio del Sr./Sra. [nombre_receptor]")

### CA-053: Historial de fichajes por servicio ← HU-023
GIVEN la trabajadora SAD accede al historial de seguimiento de tiempo
WHEN se carga el historial
THEN se muestran todos los registros agrupados por servicio y por dias con: fecha, hora de entrada, hora de salida, duracion. Se puede filtrar por rango de fechas y por servicio. No se muestran conteos de horas extra ni diferencias respecto a horas contratadas

### CA-054: Reportar incidencia con tipo y adjuntos ← HU-024
GIVEN la trabajadora SAD accede al formulario de incidencia
WHEN selecciona tipo (Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros), servicio relacionado, introduce descripcion (minimo 20 caracteres) y opcionalmente adjunta fotos (max 5) y documentos (max 3)
THEN se muestra el tamano estimado de subida. Las imagenes se optimizan automaticamente. Al enviar, la incidencia queda confirmada e inmediatamente visible para las coordinadoras

### CA-055: Historial de incidencias con filtros ← HU-025
GIVEN la trabajadora SAD accede al historial de incidencias
WHEN se carga la lista
THEN se muestran las incidencias en orden cronologico inverso con: numero, tipo, fecha, estado (Reportada, En revision, Resuelta, Cerrada). Se puede filtrar por estado, rango de fechas, y buscar por numero o descripcion

### CA-056: Detalle de incidencia con respuestas ← HU-025
GIVEN la trabajadora SAD toca una incidencia en el historial
WHEN se abre el detalle
THEN se muestra la informacion completa de la incidencia y los comentarios/respuestas de las coordinadoras

### CA-057: Solicitar ausencia con documentacion ← HU-026
GIVEN la trabajadora SAD accede a "Solicitar Ausencia"
WHEN selecciona tipo (Vacaciones, Permiso personal, Baja medica, Baja voluntaria, Asuntos propios, Otros), rango de fechas (con opcion de medio dia), motivo y adjuntos si procede
THEN el sistema muestra el saldo de vacaciones disponible. Si las fechas entran en conflicto con servicios asignados, muestra advertencia. Al enviar, la trabajadora recibe notificacion de confirmacion

> ⚠ Parcial: El calculo del saldo de vacaciones depende de la resolucion de gap P-009 (dias naturales vs. laborables).

### CA-058: Certificado medico obligatorio para baja larga ← HU-026
GIVEN la trabajadora SAD solicita una baja medica de mas de 3 dias
WHEN intenta enviar la solicitud sin adjuntar certificado medico
THEN el sistema bloquea el envio e indica que el certificado medico es obligatorio

### CA-059: Historial de ausencias con contadores ← HU-027
GIVEN la trabajadora SAD accede a "Mis Ausencias"
WHEN se carga la lista
THEN se muestran las ausencias en orden cronologico inverso con: tipo, fechas, recuento de dias, estado (Pendiente, Aprobada, Rechazada, Cancelada). Se muestran contadores por tipo de ausencia. Se puede filtrar por estado, tipo y ano

> ⚠ Parcial: El computo de vacaciones (dias naturales o laborables) depende de la resolucion de gap P-009.

### CA-060: Cancelar ausencia pendiente ← HU-027
GIVEN la trabajadora SAD tiene una solicitud de ausencia en estado Pendiente
WHEN elige cancelarla
THEN la solicitud cambia a estado Cancelada

### CA-061: Detalle de ausencia con comentarios ← HU-027
GIVEN la trabajadora SAD toca una ausencia en el historial
WHEN se abre el detalle
THEN se muestra la informacion completa y los comentarios de la coordinadora

### CA-062: Listado de ofertas con filtros (Hogar) ← HU-028
GIVEN la trabajadora Hogar accede a "Ofertas"
WHEN se carga la lista
THEN se muestran ofertas en formato de tarjeta con: titulo, ubicacion (codigo postal/ciudad), horario, tarifa horaria. Las publicadas en las ultimas 48h muestran insignia "Nuevo". Estado vacio si no hay ofertas. Se puede filtrar por codigo postal/zona, horario (manana, tarde, noche, madrugada, 24h), rango de fecha de inicio. Se puede ordenar por: mas recientes, ubicacion mas cercana, tarifa mas alta

### CA-063: Detalle de oferta (Hogar) ← HU-028
GIVEN la trabajadora Hogar toca una oferta en el listado
WHEN se abre el detalle
THEN se muestra la informacion completa de la oferta con boton "Aplicar"

### CA-064: Calendario de disponibilidad con franjas ← HU-029
GIVEN la trabajadora accede a "Mi Disponibilidad"
WHEN se carga el calendario
THEN se muestra: cabecera con horas trabajadas vs. contrato ("30 / 40 h" o "Te faltan X horas"), vista semanal (Lun-Dom) con slots de Disponible, No disponible y Activa diferenciados por color. Los slots de distinto tipo pueden solaparse visualmente

### CA-065: Crear slot con franja rapida ← HU-029
GIVEN la trabajadora ha seleccionado un dia en el calendario
WHEN pulsa una franja rapida (Manana, Tarde, Noche, Interna, Finde)
THEN se crea inmediatamente un slot de tipo "Disponible" con el rango horario correspondiente. El slot se guarda al momento

### CA-066: Crear slot personalizado ← HU-029
GIVEN la trabajadora ha seleccionado un dia en el calendario
WHEN introduce hora de inicio, hora de fin y selecciona tipo (Disponible o No disponible) en el formulario
THEN se crea el slot con los datos indicados. No se permiten solapamientos entre slots del mismo tipo (la API devuelve error)

### CA-067: Editar y eliminar slots ← HU-029
GIVEN la trabajadora ve un slot de tipo Disponible o No disponible en el calendario
WHEN toca el slot
THEN puede editarlo (modificar hora inicio/fin o tipo) o eliminarlo. Los slots de tipo Activa solo muestran informacion (no editables)

### CA-068: Guardado inmediato de disponibilidad ← HU-029
GIVEN la trabajadora ha creado, editado o eliminado un slot
WHEN confirma la accion
THEN el cambio se guarda de forma inmediata (no hay boton "guardar todo"). Pull-to-refresh disponible para sincronizar

### CA-069: Recordatorio de actualizacion de disponibilidad ← HU-029
GIVEN la trabajadora no ha actualizado su disponibilidad en 30 dias
WHEN el sistema detecta la inactividad
THEN la trabajadora recibe una notificacion de recordatorio

### CA-070: Historial de servicios completados (SAD) ← HU-030
GIVEN la trabajadora SAD accede al historial de servicios
WHEN se carga la lista
THEN se muestran los servicios completados con fechas, nombres de clientes y total de horas trabajadas por servicio. Se puede filtrar por rango de fechas. Se puede tocar para ver detalle en solo lectura

### CA-071: Historial completo de llamamientos ← HU-030
GIVEN la trabajadora SAD accede al historial de servicios
WHEN consulta la seccion de llamamientos
THEN se muestra el historial completo de todos los llamamientos con su resultado final (aceptado, rechazado, caducado, desactivado)

### CA-072: Registro de dispositivo para notificaciones ← HU-031
GIVEN la trabajadora ha iniciado sesion por primera vez
WHEN el sistema solicita permiso de notificaciones push (despues del login, antes del onboarding)
THEN si acepta, el dispositivo se registra para recibir notificaciones push vinculadas a su usuario

### CA-073: Recepcion de notificaciones push ← HU-031
GIVEN la trabajadora tiene notificaciones habilitadas
WHEN ocurre un evento relevante (nuevo mensaje, llamamiento, cambio de estado, recordatorio, etc.)
THEN recibe la notificacion push con titulo, cuerpo e icono tanto si la app esta en primer plano (alerta in-app), segundo plano (notificacion del sistema) o cerrada (notificacion del sistema)

### CA-074: Historial de notificaciones ← HU-042
GIVEN la trabajadora accede al historial de notificaciones
WHEN se carga la lista
THEN se muestran las notificaciones en orden cronologico inverso con titulo, cuerpo y fecha. Se pueden marcar todas como leidas. No se pueden borrar individualmente

### CA-075: Solicitar oferta (Hogar) ← HU-037
GIVEN la trabajadora Hogar esta en el detalle de una oferta
WHEN pulsa "Aplicar"
THEN se muestra un dialogo de confirmacion con resumen de la oferta. Al confirmar, la solicitud se envia y la trabajadora recibe notificacion de confirmacion. Se previenen solicitudes duplicadas

> ⚠ Parcial: El bloqueo por perfil incompleto depende de la resolucion de gap P-008 (lista de campos obligatorios).

### CA-076: Mis solicitudes con estados (Hogar) ← HU-038
GIVEN la trabajadora Hogar accede a "Mis Solicitudes"
WHEN se carga la lista
THEN se muestran las solicitudes en orden cronologico inverso con: titulo oferta, ubicacion, fecha solicitud, estado (Pendiente, En revision, Aceptada, Rechazada, Oferta cerrada). Distincion visual para aceptadas. Se puede filtrar por estado. Se puede retirar solicitud pendiente

### CA-077: Notificacion push de cambio de estado de solicitud (Hogar) ← HU-038
GIVEN una solicitud de la trabajadora Hogar cambia de estado
WHEN el backoffice actualiza el estado
THEN la trabajadora recibe notificacion push informando del cambio

### CA-078: Iniciar conversacion con asunto ← HU-039
GIVEN la trabajadora accede a nueva conversacion
WHEN selecciona un asunto (Vacaciones/Ausencia, Nomina/Facturacion, Sobre un servicio, Documentacion, Consulta general, Otros), opcionalmente enlaza contexto (servicio u oferta) y escribe su primer mensaje
THEN se crea la conversacion en formato chat. El asunto se muestra en la cabecera. Si el backend proporciona codigo de ticket, se muestra. La trabajadora siempre ve la conversacion como comunicacion con "Coordinacion"

### CA-079: Listado de conversaciones ← HU-040
GIVEN la trabajadora accede a "Comunicacion"
WHEN se carga la lista
THEN se muestran las conversaciones en orden cronologico inverso por ultimo mensaje, con asunto, preview y marca de tiempo. Indicador visual para no leidos. Indicador diferenciado para conversaciones cerradas (etiqueta o icono). Pull-to-refresh disponible. Se puede buscar por asunto

### CA-080: Borrar conversacion ← HU-040
GIVEN la trabajadora esta en el listado de conversaciones
WHEN elige borrar una conversacion
THEN se muestra confirmacion. Al confirmar, la conversacion se elimina de su lista

### CA-081: Chat en conversacion abierta ← HU-041
GIVEN la trabajadora abre una conversacion en estado abierta
WHEN interactua con el hilo
THEN ve todos los mensajes en orden cronologico con diferenciacion visual (mensajes propios vs. coordinacion), marca de tiempo y estado de entrega/lectura. Campo de entrada de texto en la parte inferior con boton de enviar. Auto-scroll al ultimo mensaje. Paginacion al desplazar hacia arriba. Mensajes nuevos aparecen automaticamente sin refrescar

### CA-082: Conversacion cerrada en modo lectura ← HU-041
GIVEN la trabajadora abre una conversacion cerrada por coordinacion
WHEN se muestra el hilo
THEN se oculta el campo de entrada, se muestra aviso "Conversacion cerrada" y se permite consultar el historial completo en modo lectura

### CA-083: Perfil con secciones organizadas ← HU-032
GIVEN la trabajadora accede a su perfil
WHEN se carga la informacion
THEN se muestra organizada en secciones: Informacion Personal (nombre, email, telefono, direccion, fecha nacimiento, DNI/NIE), Profesional (experiencia, especializaciones, certificaciones), Educacion (titulos, cursos), Idiomas (idioma + nivel). Se muestra indicador de porcentaje de completitud del perfil

> ⚠ Parcial: La clasificacion de campos editables vs. solo-lectura vs. propuesta-de-cambio depende de la resolucion de gap P-007.

### CA-084: Direccion de domicilio editable ← HU-032
GIVEN la trabajadora esta en su perfil
WHEN accede al campo de direccion de domicilio
THEN puede editarlo directamente (ya que afecta a la zona de disponibilidad)

### CA-085: Vencimiento de DNI/NIE ← HU-032
GIVEN la trabajadora tiene un DNI/NIE con fecha de vencimiento
WHEN accede a su perfil
THEN ve la fecha de vencimiento y tiene acceso a un flujo de "proponer nueva fecha + adjuntar documento" (sin editar el dato existente; el backoffice valida)

### CA-086: Porcentaje de completitud en home (Hogar) ← HU-044
GIVEN la trabajadora Hogar accede al panel principal
WHEN su perfil no esta completo al 100%
THEN ve el porcentaje de completitud visible en la home para incentivar su cumplimentacion

### CA-087: Estado del contrato (SAD) ← HU-033
GIVEN la trabajadora SAD accede a la informacion de su contrato
WHEN se carga la pantalla
THEN se muestra: tipo de contrato, fecha de inicio, numero de empleada, enlace para descargar PDF del contrato. Informacion de solo lectura

> ⚠ Parcial: Los valores del tipo de contrato dependen de la resolucion de gap P-010 (Indefinido/Fijo Discontinuo vs. Tiempo completo/Tiempo parcial).

### CA-088: Foto de perfil ← HU-034
GIVEN la trabajadora accede a su foto de perfil
WHEN toca la foto o el placeholder
THEN puede elegir foto de galeria o hacer nueva foto. Puede recortar/redimensionar (aspecto cuadrado). La imagen se optimiza automaticamente (maximo 5 MB, formatos JPG/PNG). Se muestra progreso de subida. La foto se actualiza en toda la aplicacion inmediatamente

### CA-089: Documentos personales - subir y reemplazar ← HU-035
GIVEN la trabajadora accede a Documentacion Personal
WHEN quiere subir un documento
THEN puede seleccionar tipo, elegir archivo del dispositivo o hacer foto (formatos: PDF, DOC, DOCX, JPG, PNG; max 10 MB; imagenes optimizadas automaticamente). Puede reemplazar documentos existentes pero no eliminarlos

### CA-090: Documentos laborales - solo consulta y firma ← HU-035
GIVEN la trabajadora accede a Documentacion Laboral
WHEN consulta los documentos
THEN puede ver (visor de PDF en la app), descargar y firmar cuando corresponda. No puede subir ni eliminar. Indicador de documentos obligatorios y avisos de caducidad

### CA-091: Acceso a documentos desde home ← HU-035
GIVEN la trabajadora esta en el panel principal
WHEN toca el acceso a Documentos
THEN navega a la pantalla unificada con ambas categorias (personal + laboral)

### CA-092: Captura de firma digital ← HU-036
GIVEN la trabajadora accede al lienzo de firma
WHEN dibuja su firma con entrada tactil
THEN puede previsualizar la firma, borrarla y redibujarla. Al guardar, la firma se almacena en su perfil y puede reutilizarse para futuras firmas de documentos. Puede redibujar su firma en cualquier momento

### CA-093: Aplicaciones de marca diferenciada ← HU-043
GIVEN las aplicaciones estan disponibles para descarga
WHEN una trabajadora instala la app correspondiente a su perfil
THEN CUIDEO (Hogar) se presenta con tema azul y solo funcionalidades Hogar; Felizvita (SAD) se presenta con tema verde y solo funcionalidades SAD. Ambas disponibles en iOS y Android

### CA-094: Accesibilidad basica ← HU-043
GIVEN la trabajadora usa la app
WHEN interactua con los elementos de la interfaz
THEN los elementos interactivos tienen tamano adecuado para interaccion tactil, los contrastes de color cumplen nivel adecuado de accesibilidad, los flujos principales son compatibles con lectores de pantalla, y todas las imagenes e iconos tienen texto alternativo

---

## Checklist de Validacion

- [x] Actores identificados — 4 actores con descripcion y capacidades
- [x] Flujos principales descritos paso a paso — 15 journeys detallados
- [x] Estados de exito definidos — cada journey tiene estado de exito
- [x] Edge cases documentados — flujos alternativos en journeys, reglas de comportamiento
- [x] Estados de error definidos — errores de login, validacion, conexion, permisos
- [ ] Ambiguedades resueltas — quedan 11 gaps criticos pendientes (P-001 a P-011) que afectan a 12 HUs
- [x] Cada CA referencia su HU padre — todos los CAs incluyen referencia ← HU-XXX
- [x] Cada CA es testable de forma independiente — formato GIVEN/WHEN/THEN verificable
- [x] Destinos de navegacion enumerados con sus variantes — tabla de destinos incluida (parcial: deeplinks de notificaciones pendientes de P-002)

---

## Fuera de Alcance

- Autenticacion biometrica (Face ID, huella digital): no incluida en esta version.
- Autenticacion de dos factores (2FA): no incluida en esta version.
- Deteccion de GPS simulado: no incluida en esta version.
- Modo offline con sincronizacion: no incluido. Toda accion requiere conexion a internet.
- Gestion activa de pagos/nominas: fuera de alcance (el acceso de solo lectura a documentos de nomina SI esta incluido como parte de Documentacion laboral).
- Funciones sociales (perfiles publicos, valoraciones entre trabajadoras): no incluidas.
- Eventos de analytics personalizados: solo analitica basica automatica; sin eventos personalizados en el MVP.
- Seguimiento PIA: funcionalidad descartada (eliminada en v1.4 del PRD).
- Gestion de contrasenas desde la app (cambiar contrasena activa): el cambio de contrasena solo es posible via flujo de recuperacion de acceso.
- Funcionalidades de backoffice/coordinacion: este spec cubre exclusivamente la experiencia desde la app movil de la trabajadora.

---

## Excepciones de Pureza

Ninguna. Todas las contaminaciones detectadas (C-001 a C-014) fueron aceptadas y sus reescrituras aplicadas.

---

## Anexo: Trazabilidad RF → HU

> Los IDs de RF provienen directamente del PRD (prd-hogar-sad.md), que los numera explicitamente.

| RF | Titulo RF | HU | Titulo HU |
|----|-----------|-----|-----------|
| RF-1 | Autenticacion y Onboarding | HU-001 | Pantalla de splash |
| RF-1 | Autenticacion y Onboarding | HU-002 | Registro de cuenta (Hogar) |
| RF-1 | Autenticacion y Onboarding | HU-003 | Pantallas de bienvenida (onboarding) |
| RF-1 | Autenticacion y Onboarding | HU-004 | Activacion de cuenta (SAD) |
| RF-1 | Autenticacion y Onboarding | HU-005 | Inicio de sesion |
| RF-1 | Autenticacion y Onboarding | HU-006 | Sesion persistente |
| RF-1 | Autenticacion y Onboarding | HU-007 | Recuperacion de acceso |
| RF-1 | Autenticacion y Onboarding | HU-008 | Cierre de sesion |
| RF-1 | Autenticacion y Onboarding | HU-009 | Pantalla de acceso revocado (SAD) |
| RF-2 | Panel Principal | HU-010 | Panel principal con accesos directos |
| RF-2 | Panel Principal | HU-011 | Tablon de anuncios y comunicados |
| RF-2 | Panel Principal | HU-012 | Mensajes del sistema |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-013 | Listado de servicios (SAD) |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-014 | Detalle del servicio (SAD) |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-015 | Notas de servicio (SAD) |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-016 | Detalle del llamamiento (SAD) |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-017 | Aceptar o rechazar llamamiento (SAD) |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-018 | Listado de llamamientos (SAD) |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-019 | Nuevo servicio asignado - contratos indefinidos (SAD) |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-030 | Historial de servicios (SAD) |
| RF-4 | Control Horario (Seguimiento de Tiempo) | HU-022 | Fichar entrada y salida (SAD) |
| RF-4 | Control Horario (Seguimiento de Tiempo) | HU-023 | Historial de seguimiento de tiempo (SAD) |
| RF-5 | Incidencias | HU-024 | Reportar incidencia (SAD) |
| RF-5 | Incidencias | HU-025 | Historial de incidencias (SAD) |
| RF-6 | Ofertas (Ofertas de Trabajo) | HU-028 | Navegar ofertas de trabajo (Hogar) |
| RF-6 | Ofertas (Ofertas de Trabajo) | HU-037 | Solicitar oferta de trabajo (Hogar) |
| RF-6 | Ofertas (Ofertas de Trabajo) | HU-038 | Mis solicitudes (Hogar) |
| RF-6 | Ofertas (Ofertas de Trabajo) | HU-044 | Completar perfil antes de aplicar (Hogar) |
| RF-7 | Mi Disponibilidad (Gestion de Disponibilidad) | HU-029 | Calendario de disponibilidad |
| RF-8 | Mis Ausencias (Gestion de Ausencias) | HU-026 | Solicitar ausencia (SAD) |
| RF-8 | Mis Ausencias (Gestion de Ausencias) | HU-027 | Historial de ausencias (SAD) |
| RF-9 | Perfil (Gestion de Perfil) | HU-032 | Ver y editar perfil |
| RF-9 | Perfil (Gestion de Perfil) | HU-033 | Estado del contrato (SAD) |
| RF-9 | Perfil (Gestion de Perfil) | HU-034 | Foto de perfil |
| RF-9 | Perfil (Gestion de Perfil) | HU-035 | Gestion de documentos |
| RF-9 | Perfil (Gestion de Perfil) | HU-036 | Firma digital |
| RF-10 | Comunicacion | HU-039 | Iniciar conversacion con coordinacion |
| RF-10 | Comunicacion | HU-040 | Listado de conversaciones |
| RF-10 | Comunicacion | HU-041 | Hilo de conversacion |
| RF-11 | Notificaciones (Notificaciones Push) | HU-020 | Deeplinks de notificaciones push |
| RF-11 | Notificaciones (Notificaciones Push) | HU-021 | Notificaciones automaticas del sistema |
| RF-11 | Notificaciones (Notificaciones Push) | HU-031 | Registrar dispositivo para notificaciones push |
| RF-11 | Notificaciones (Notificaciones Push) | HU-042 | Historial de notificaciones |
| RF-12 | Publicacion de la Aplicacion | HU-043 | Aplicaciones de marca diferenciada |

### Cobertura por RF

| RF | Titulo RF | HUs asignadas |
|----|-----------|---------------|
| RF-1 | Autenticacion y Onboarding | HU-001, HU-002, HU-003, HU-004, HU-005, HU-006, HU-007, HU-008, HU-009 |
| RF-2 | Panel Principal | HU-010, HU-011, HU-012 |
| RF-3 | Mis Servicios (Gestion de Servicios) | HU-013, HU-014, HU-015, HU-016, HU-017, HU-018, HU-019, HU-030 |
| RF-4 | Control Horario (Seguimiento de Tiempo) | HU-022, HU-023 |
| RF-5 | Incidencias | HU-024, HU-025 |
| RF-6 | Ofertas (Ofertas de Trabajo) | HU-028, HU-037, HU-038, HU-044 |
| RF-7 | Mi Disponibilidad (Gestion de Disponibilidad) | HU-029 |
| RF-8 | Mis Ausencias (Gestion de Ausencias) | HU-026, HU-027 |
| RF-9 | Perfil (Gestion de Perfil) | HU-032, HU-033, HU-034, HU-035, HU-036 |
| RF-10 | Comunicacion | HU-039, HU-040, HU-041 |
| RF-11 | Notificaciones (Notificaciones Push) | HU-020, HU-021, HU-031, HU-042 |
| RF-12 | Publicacion de la Aplicacion | HU-043 |

---

## Items pendientes

- [PENDIENTE] [P-001]: Contenido de las pantallas de onboarding — afecta HU-003
- [PENDIENTE] [P-002]: Tabla de destinos de navegacion para deeplinks de notificaciones push — afecta HU-020, HU-021
- [PENDIENTE] [P-003]: Visibilidad de datos de salud del cliente en detalle de servicio — afecta HU-014
- [PENDIENTE] [P-004]: Datos completos del detalle de un llamamiento — afecta HU-016
- [PENDIENTE] [P-005]: Consecuencia de no responder un llamamiento (inaccion = rechazo o no) — afecta HU-017
- [PENDIENTE] [P-006]: Textos oficiales de aceptacion y rechazo de llamamientos — afecta HU-016, HU-017
- [PENDIENTE] [P-007]: Reglas de campos editables vs. no editables del perfil — afecta HU-032
- [PENDIENTE] [P-008]: Campos obligatorios para completar perfil antes de aplicar a oferta (Hogar) — afecta HU-037, HU-044
- [PENDIENTE] [P-009]: Computo de vacaciones: dias naturales o laborables — afecta HU-026, HU-027
- [PENDIENTE] [P-010]: Tipo de contrato: valores correctos — afecta HU-033
- [PENDIENTE] [P-011]: Comportamiento cuando la app no tiene permiso de ubicacion al fichar — afecta HU-022
