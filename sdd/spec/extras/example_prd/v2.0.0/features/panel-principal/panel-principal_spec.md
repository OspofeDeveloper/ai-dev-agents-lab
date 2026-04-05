# Spec: Panel Principal
> Version: 1.0 | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md
> Feature ID: F-002

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo | Ver home con accesos directos a Ofertas, Disponibilidad, Perfil, Comunicacion; ver comunicados y mensajes del sistema |
| Trabajadora SAD | Trabajadora del Servicio de Asistencia Social | Ver home con accesos directos a Servicios, Fichaje, Incidencias, Ausencias, Disponibilidad, Documentacion, Perfil, Comunicacion; ver comunicados, mensajes del sistema, llamamientos pendientes y documentacion pendiente de firma |

---

## Historias de Usuario

### HU-001: Accesos directos del panel
Como trabajadora (Hogar o SAD)
quiero tener accesos rapidos a las secciones principales desde la pantalla de inicio
para que pueda navegar eficientemente a las funcionalidades que necesito.

### HU-002: Tablon de anuncios
Como trabajadora (Hogar o SAD)
quiero consultar los comunicados y anuncios de la empresa
para que este informada de protocolos, novedades y recordatorios.

### HU-003: Mensajes del sistema
Como trabajadora (Hogar o SAD)
quiero recibir y consultar mensajes administrativos
para que este al tanto de comunicaciones importantes de la administracion.

---

## Recorridos de Usuario

### Journey 1: Consultar Home y navegar a seccion
Actor: Trabajadora (Hogar o SAD) | Objetivo: Acceder rapidamente a una funcionalidad
1. La trabajadora accede a la pantalla principal tras el login o al abrir la app.
2. Ve su nombre y foto de perfil en la cabecera.
3. Ve los accesos directos a las secciones principales segun su perfil.
4. (SAD) Ve el servicio activo y el siguiente servicio en un bloque resumido; si hay mas, ve "Ver mas servicios".
5. (SAD) Si tiene un llamamiento pendiente, lo ve de forma destacada con cuenta atras de caducidad.
6. (SAD) Si tiene documentacion pendiente de firma, ve un badge/contador destacado.
7. Ve el bloque "Ultimos avisos" con 2-3 comunicados recientes.
8. Toca un acceso directo y navega al modulo correspondiente.

Estado de exito: La trabajadora ve informacion relevante y navega a la seccion deseada con un solo toque.
Flujos alternativos:
- Si hay notificaciones no leidas, se muestran badges en los accesos directos correspondientes.
- Pull-to-refresh actualiza los datos del panel.

### Journey 2: Consultar comunicado
Actor: Trabajadora (Hogar o SAD) | Objetivo: Leer un comunicado de la empresa
1. La trabajadora ve la lista de comunicados diferenciando contenidos fijos (protocolo, calendario laboral, PRL) de comunicaciones variables (recordatorios, novedades).
2. Los contenidos fijados por el backoffice aparecen en la parte superior.
3. La trabajadora toca un comunicado para ver el detalle completo.
4. El comunicado se marca como leido automaticamente al abrirlo.
5. La trabajadora puede ver imagenes y adjuntos en el detalle.

Estado de exito: La trabajadora lee el comunicado completo y el sistema registra la lectura.
Flujos alternativos:
- Indicador visual para comunicados no leidos (badge en menu/tab).
- Notificacion push cuando se publica un nuevo comunicado.

### Journey 3: Consultar mensaje del sistema
Actor: Trabajadora (Hogar o SAD) | Objetivo: Leer un mensaje administrativo
1. La trabajadora accede a la seccion de mensajes del sistema.
2. Ve la lista con remitente, asunto y fecha, diferenciando por nivel de criticidad (alta primero, normal debajo).
3. Ve indicador visual para mensajes no leidos.
4. Toca un mensaje para ver el contenido completo y adjuntos.
5. El mensaje se marca como leido automaticamente al abrirlo.

Estado de exito: La trabajadora lee el mensaje y el sistema registra la lectura.
Flujos alternativos:
- La trabajadora puede borrar mensajes.
- Los mensajes no se pueden responder.

---

## Resultados y Exito

- Cada trabajadora ve una home personalizada segun su perfil (Hogar o SAD) con accesos directos a las funcionalidades relevantes.
- La trabajadora SAD ve informacion priorizada: servicio activo, llamamientos pendientes y documentacion pendiente de firma.
- Los comunicados y mensajes del sistema son accesibles y se marcan como leidos al consultarlos.

---

## Instrucciones Inambiguas

### Reglas de comportamiento
- Home Hogar muestra accesos directos a: Ofertas, Mi Disponibilidad, Perfil, Comunicacion.
- Home SAD muestra accesos directos a: Mis Servicios, Fichar, Incidencias, Solicitar Ausencia, Mis Ausencias, Mi Disponibilidad, Documentacion, Perfil, Comunicacion. El servicio activo y el fichaje son la accion principal.
- El bloque de servicios en Home SAD muestra como maximo el servicio activo + el siguiente servicio. Si hay mas, se muestra "Ver mas servicios" (no un contador "+2" o similar). Tocar una tarjeta de servicio navega al detalle completo del servicio.
- Un llamamiento pendiente en Home SAD se muestra de forma muy visible con indicacion de urgencia y cuenta atras de caducidad. El CTA lleva al detalle del llamamiento (no permite aceptar/rechazar directamente desde la home).
- Documentacion pendiente de firma se muestra como badge/contador destacado de alta prioridad en la home SAD.
- El bloque "Ultimos avisos" muestra 2-3 items con acceso al listado completo.
- Pull-to-refresh esta disponible en la home.
- Los comunicados fijados por backoffice aparecen en la parte superior de la lista de anuncios (no necesariamente separados en bloques rigidos).
- Los mensajes del sistema tienen dos niveles de criticidad: alta (se muestran primero con apariencia diferenciada) y normal (se muestran debajo).
- Los mensajes del sistema no se pueden responder (sin boton de redactar).

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home Hogar | Tocar "Ofertas" | Listado de ofertas (F-006) |
| Home Hogar | Tocar "Mi Disponibilidad" | Calendario de disponibilidad (F-007) |
| Home Hogar | Tocar "Perfil" | Pantalla de perfil (F-009) |
| Home Hogar | Tocar "Comunicacion" | Listado de conversaciones (F-010) |
| Home SAD | Tocar "Mis Servicios" | Listado de servicios (F-003) |
| Home SAD | Tocar "Fichar" | Pantalla de fichaje (F-004) |
| Home SAD | Tocar "Incidencias" | Listado de incidencias (F-005) |
| Home SAD | Tocar "Solicitar Ausencia" | Formulario de solicitud de ausencia (F-008) |
| Home SAD | Tocar "Mis Ausencias" | Historial de ausencias (F-008) |
| Home SAD | Tocar "Mi Disponibilidad" | Calendario de disponibilidad (F-007) |
| Home SAD | Tocar "Documentacion" | Pantalla de documentos (F-009) |
| Home SAD | Tocar "Perfil" | Pantalla de perfil (F-009) |
| Home SAD | Tocar "Comunicacion" | Listado de conversaciones (F-010) |
| Home SAD | Tocar tarjeta de servicio | Detalle del servicio (F-003) |
| Home SAD | Tocar llamamiento pendiente | Detalle del llamamiento (F-003) |
| Home | Tocar acceso directo con badge | Modulo correspondiente |
| Ultimos avisos | Tocar comunicado | Detalle del comunicado |
| Ultimos avisos | Tocar "ver todos" | Listado completo de comunicados |
| Lista comunicados | Tocar comunicado | Detalle del comunicado (titulo, texto, imagenes, adjuntos) |
| Lista mensajes sistema | Tocar mensaje | Detalle del mensaje (contenido, adjuntos) |

---

## Criterios de Aceptacion

### CA-001: Home Hogar con accesos directos <- HU-001
GIVEN la trabajadora Hogar esta en la pantalla principal
WHEN la pantalla se carga
THEN se muestran accesos directos a: Ofertas, Mi Disponibilidad, Perfil, Comunicacion.

### CA-002: Home SAD con accesos directos <- HU-001
GIVEN la trabajadora SAD esta en la pantalla principal
WHEN la pantalla se carga
THEN se muestran accesos directos a: Mis Servicios, Fichar, Incidencias, Solicitar Ausencia, Mis Ausencias, Mi Disponibilidad, Documentacion, Perfil, Comunicacion. El servicio activo y el fichaje se priorizan como accion principal. Se muestra un bloque "Ultimos avisos" con 2-3 items y acceso al listado completo.

### CA-003: Badges en accesos directos <- HU-001
GIVEN la trabajadora esta en la pantalla principal
WHEN hay notificaciones no leidas o acciones pendientes en algun modulo
THEN se muestra un badge en el acceso directo correspondiente.

### CA-004: Navegacion desde acceso directo <- HU-001
GIVEN la trabajadora esta en la pantalla principal
WHEN toca un acceso directo
THEN la app navega al modulo correspondiente.

### CA-005: Cabecera con nombre y foto <- HU-001
GIVEN la trabajadora esta en la pantalla principal
WHEN la pantalla se carga
THEN se muestra el nombre de la usuaria y su foto de perfil en la cabecera.

### CA-006: Pull-to-refresh en home <- HU-001
GIVEN la trabajadora esta en la pantalla principal
WHEN realiza gesto de pull-to-refresh
THEN se actualizan los datos del panel.

### CA-007: Llamamiento pendiente en home SAD <- HU-001
GIVEN la trabajadora SAD tiene un llamamiento pendiente de respuesta
WHEN accede a la pantalla principal
THEN el llamamiento se muestra de forma muy visible con indicacion de urgencia y cuenta atras de caducidad. El CTA lleva al detalle del llamamiento; no se permite aceptar/rechazar directamente desde la home.

### CA-008: Documentacion pendiente de firma en home SAD <- HU-001
GIVEN la trabajadora SAD tiene documentacion pendiente de firma
WHEN accede a la pantalla principal
THEN se muestra un badge/contador destacado de alta prioridad para la documentacion pendiente.

### CA-009: Bloque de servicios limitado en home SAD <- HU-001
GIVEN la trabajadora SAD tiene servicios asignados
WHEN accede a la pantalla principal
THEN el bloque de servicios muestra como maximo el servicio activo + el siguiente servicio. Si hay mas servicios, se muestra "Ver mas servicios". Tocar una tarjeta navega al detalle completo del servicio.

### CA-010: Listado de comunicados con fijados <- HU-002
GIVEN la trabajadora accede al tablon de anuncios
WHEN se carga la lista de comunicados
THEN se muestran comunicados diferenciando contenidos fijos (protocolo, calendario laboral, PRL) y comunicaciones variables (recordatorios, novedades). Los contenidos fijados por backoffice aparecen en la parte superior.

### CA-011: Previsualizar comunicado <- HU-002
GIVEN la trabajadora esta en el listado de comunicados
WHEN ve la lista
THEN cada comunicado muestra titulo, fecha y texto de previsualizacion.

### CA-012: Detalle de comunicado <- HU-002
GIVEN la trabajadora esta en el listado de comunicados
WHEN toca un comunicado
THEN se muestra el detalle completo del comunicado.

### CA-013: Marcar comunicado como leido <- HU-002
GIVEN la trabajadora esta en el listado de comunicados
WHEN abre un comunicado
THEN se marca como leido automaticamente.

### CA-014: Indicador de no leidos en comunicados <- HU-002
GIVEN hay comunicados no leidos
WHEN la trabajadora ve el menu o tab de comunicados
THEN se muestra un indicador visual (badge) para comunicados no leidos.

### CA-015: Adjuntos en comunicados <- HU-002
GIVEN la trabajadora esta viendo el detalle de un comunicado
WHEN el comunicado tiene imagenes o adjuntos
THEN se muestran las imagenes y los adjuntos disponibles.

### CA-016: Notificacion push de nuevo comunicado <- HU-002
GIVEN el backoffice publica un nuevo comunicado
WHEN se registra la publicacion
THEN la trabajadora recibe una notificacion push.

### CA-017: Badge de comunicados nuevos <- HU-002
GIVEN hay comunicados nuevos no leidos
WHEN la trabajadora ve la seccion correspondiente
THEN se muestra un badge en el icono de la seccion indicando contenido nuevo.

### CA-018: Listado de mensajes del sistema <- HU-003
GIVEN la trabajadora accede a la seccion de mensajes del sistema
WHEN se carga la lista
THEN se muestran los mensajes con remitente, asunto y fecha, diferenciados por nivel de criticidad (alta primero, normal debajo).

### CA-019: Indicador de no leidos en mensajes <- HU-003
GIVEN hay mensajes del sistema no leidos
WHEN la trabajadora ve la lista de mensajes
THEN se muestra un indicador visual para mensajes no leidos.

### CA-020: Detalle de mensaje del sistema <- HU-003
GIVEN la trabajadora esta en la lista de mensajes del sistema
WHEN toca un mensaje
THEN se muestra el contenido completo del mensaje.

### CA-021: Marcar mensaje como leido <- HU-003
GIVEN la trabajadora esta en la lista de mensajes
WHEN abre un mensaje
THEN se marca como leido automaticamente.

### CA-022: Mensajes no se pueden responder <- HU-003
GIVEN la trabajadora esta viendo un mensaje del sistema
WHEN revisa las opciones disponibles
THEN no existe opcion de responder (sin boton de redactar).

### CA-023: Borrar mensaje del sistema <- HU-003
GIVEN la trabajadora esta viendo un mensaje del sistema o la lista de mensajes
WHEN selecciona la opcion de borrar
THEN el mensaje se elimina.

### CA-024: Adjuntos en mensajes del sistema <- HU-003
GIVEN la trabajadora esta viendo el detalle de un mensaje del sistema
WHEN el mensaje tiene adjuntos
THEN se muestran los adjuntos disponibles para visualizacion.

---

## Checklist de Validacion
- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [x] Ambiguedades resueltas
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance
- Configuracion de preferencias de notificaciones desde la home (mejora futura)
- Personalizacion del orden de accesos directos
- Widget de home configurable por la trabajadora
- Respuesta a mensajes del sistema (son de solo lectura)

---

## Asunciones Aplicadas
| Gap origen | Asuncion aplicada |
|------------|-------------------|
| [P-003] | El nivel de criticidad de los mensajes del sistema (alta/normal) viene definido por el backend; la app solo los muestra diferenciados visualmente |
