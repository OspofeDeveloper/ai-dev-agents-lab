# Spec: Dashboard and Announcements
> Version: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde /Users/oscar/Documents/AI_labs/Specs Test/project/prd-hogar-sad.md (scope: F-002 via prd-hogar-sad_discovery.md)
> Feature ID: F-002
> Spec monolitico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio que busca oportunidades laborales a traves de la app CUIDEO | Acceder al panel principal con accesos directos a Ofertas, Disponibilidad, Perfil y Comunicacion; consultar anuncios y comunicados; leer mensajes del sistema |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios a traves de la app Felizvita | Acceder al panel principal con accesos directos contextuales a sus servicios, fichaje, incidencias y mas; consultar anuncios y comunicados; leer mensajes del sistema; ver llamamiento pendiente destacado en home |
| Backoffice | Equipo de coordinacion y administracion de CUIDEO/Felizvita | Publicar y fijar anuncios/comunicados; enviar mensajes del sistema con nivel de criticidad; configurar contenido visible en home |

---

## Historias de Usuario

### HU-001: Acceder al panel principal adaptado a mi perfil
Como trabajadora (Hogar o SAD)
quiero ver un panel principal con accesos directos a las funcionalidades mas relevantes para mi perfil
para que pueda navegar rapidamente a las acciones que necesito sin buscar en menus

### HU-002: Ver badges de acciones pendientes en el panel
Como trabajadora (Hogar o SAD)
quiero ver indicadores numericos en los accesos directos del panel cuando tengo acciones pendientes
para que sepa de un vistazo que requiere mi atencion sin tener que entrar en cada seccion

### HU-003: Consultar anuncios y comunicados de la empresa
Como trabajadora (Hogar o SAD)
quiero acceder al tablon de anuncios donde la empresa publica comunicados, protocolos y novedades
para que este informada de las comunicaciones relevantes de la organizacion

### HU-004: Leer y gestionar mensajes del sistema
Como trabajadora (Hogar o SAD)
quiero recibir y consultar mensajes de administracion diferenciados por importancia
para que pueda priorizar los avisos urgentes y gestionar los informativos a mi ritmo

> **[INCOMPLETO]** -- Pendiente de gap(s): [P-001]. Los criterios que determinan la criticidad "alta" vs "normal" de los mensajes no estan definidos. Los CAs de diferenciacion visual y ordenacion por criticidad se generan parcialmente.

### HU-005: Ver informacion contextual de servicios y llamamientos en el panel SAD
Como trabajadora SAD
quiero ver en el panel principal mi servicio activo, el siguiente servicio, y cualquier llamamiento pendiente de forma destacada
para que tenga visibilidad inmediata de mi situacion laboral actual sin navegar a otras secciones

---

## Recorridos de Usuario

### Journey 1: Acceder al panel principal y navegar a una seccion
Actor: Trabajadora (Hogar o SAD) | Objetivo: Consultar el panel y acceder a una funcionalidad especifica

1. La trabajadora abre la aplicacion y accede al panel principal (home)
2. El panel muestra en la cabecera el nombre de la trabajadora y su foto de perfil
3. La trabajadora ve los accesos directos organizados segun su perfil:
   - **Hogar**: Ofertas, Mi Disponibilidad, Perfil, Comunicacion
   - **SAD**: Servicio activo + fichaje como accion principal, seguido de: Mis Servicios, Fichar, Incidencias, Solicitar Ausencia, Mis Ausencias, Mi Disponibilidad, Documentacion, Perfil, Comunicacion; y un bloque de "Ultimos avisos" con 2-3 comunicados recientes
4. Los accesos directos muestran badges con contadores de acciones pendientes (mensajes no leidos, documentos por firmar)
5. La trabajadora toca un acceso directo y navega al modulo correspondiente

Estado de exito: La trabajadora accede al panel, identifica las acciones pendientes gracias a los badges, y navega a la seccion deseada con un solo toque.

Flujos alternativos:
- Si la trabajadora desliza hacia abajo (pull-to-refresh) → los datos del panel se actualizan
- Si no hay acciones pendientes → no se muestran badges en ningun acceso directo

### Journey 2: Consultar servicio activo y llamamiento pendiente en home SAD
Actor: Trabajadora SAD | Objetivo: Ver su situacion laboral actual desde el panel

1. La trabajadora SAD accede al home y ve el bloque de servicios que muestra como maximo el servicio activo y el siguiente servicio programado
2. Si hay mas servicios, se muestra un enlace "Ver mas servicios" que navega al listado completo (RF-3.1)
3. Si existe un llamamiento pendiente de respuesta, este se muestra de forma muy visible con indicacion de urgencia y cuenta atras de caducidad
4. La trabajadora toca la tarjeta del llamamiento en el home, que la lleva al detalle del llamamiento (RF-3.4) donde puede aceptar o rechazar — no es posible aceptar o rechazar desde el home directamente
5. Si hay documentacion pendiente de firma, se muestra un badge/contador destacado como elemento de alta prioridad
6. La trabajadora toca una tarjeta de servicio para navegar al detalle completo del servicio (RF-3.2)

Estado de exito: La trabajadora SAD visualiza su servicio activo, identifica si hay un llamamiento pendiente o documentacion por firmar, y accede al detalle correspondiente.

Flujos alternativos:
- Si no hay servicio activo → el bloque de servicios muestra los proximos servicios programados o un estado vacio
- Si no hay llamamiento pendiente → el panel no muestra la seccion de llamamiento
- Si no hay documentacion pendiente de firma → no se muestra el badge de firma

### Journey 3: Consultar el tablon de anuncios y leer un comunicado
Actor: Trabajadora (Hogar o SAD) | Objetivo: Informarse de los comunicados de la empresa

1. La trabajadora accede al tablon de anuncios desde el acceso directo del panel o desde el bloque de "Ultimos avisos" (SAD)
2. El tablon muestra los comunicados diferenciando entre contenidos fijos (protocolos, calendario laboral, PRL, documentos de referencia permanente) y comunicaciones variables (recordatorios, campanas, novedades)
3. Los contenidos fijados por backoffice aparecen en la parte superior del listado
4. Cada comunicado muestra titulo, fecha y texto de previsualizacion
5. Los comunicados no leidos se distinguen visualmente de los ya leidos
6. La trabajadora toca un comunicado para ver su contenido completo, incluyendo imagenes y adjuntos si los tiene
7. Al abrir el comunicado, se marca automaticamente como leido

Estado de exito: La trabajadora lee el comunicado deseado, que pasa a marcarse como leido, y el indicador de no leido desaparece.

Flujos alternativos:
- Si no hay comunicados publicados → se muestra un estado vacio
- Si la trabajadora recibe una notificacion push de nuevo comunicado → al tocarla accede directamente al tablon con el nuevo comunicado

### Journey 4: Consultar mensajes del sistema
Actor: Trabajadora (Hogar o SAD) | Objetivo: Leer mensajes administrativos y gestionar su bandeja

1. La trabajadora accede a la seccion de mensajes del sistema
2. Los mensajes se listan mostrando remitente, asunto y fecha
3. Los mensajes se diferencian en dos niveles de criticidad: alta (mostrados primero con diferenciacion visual) y normal (mostrados debajo)
4. Los mensajes no leidos tienen un indicador visual distintivo
5. La trabajadora toca un mensaje para ver su contenido completo, incluyendo adjuntos si los tiene
6. Al abrir el mensaje, se marca automaticamente como leido
7. La trabajadora puede borrar mensajes que ya no necesita
8. Los mensajes no se pueden responder (son de solo lectura)

Estado de exito: La trabajadora lee los mensajes del sistema priorizando los de criticidad alta, gestiona su bandeja borrando mensajes innecesarios.

Flujos alternativos:
- Si no hay mensajes del sistema → se muestra un estado vacio
- Si la trabajadora intenta responder → no hay opcion de respuesta visible (sin boton de redactar)

---

## Resultados y Exito

| Resultado | Definicion de exito |
|-----------|---------------------|
| Panel principal operativo | La trabajadora accede al home y ve accesos directos adaptados a su perfil (Hogar o SAD) con informacion actualizada |
| Badges de pendientes visibles | Los contadores de acciones pendientes (mensajes no leidos, documentos por firmar) se muestran correctamente y se actualizan al resolver cada accion |
| Tablon de anuncios funcional | Los comunicados se listan diferenciando fijos de variables, se abren en detalle, se marcan como leidos automaticamente, y soportan imagenes y adjuntos |
| Mensajes del sistema gestionables | Los mensajes se reciben, se muestran diferenciados por criticidad, se leen, y se pueden borrar; no hay funcionalidad de respuesta |
| Contexto de servicios SAD visible | La trabajadora SAD ve su servicio activo, siguiente servicio, llamamientos pendientes y documentacion por firmar directamente desde el home |

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Contenido del home por perfil**: El panel principal adapta su contenido segun el perfil de la trabajadora:
   - **Hogar**: accesos directos a Ofertas, Mi Disponibilidad, Perfil, Comunicacion
   - **SAD**: servicio activo + fichaje como accion principal; accesos a Mis Servicios, Fichar, Incidencias, Solicitar Ausencia, Mis Ausencias, Mi Disponibilidad, Documentacion, Perfil, Comunicacion; bloque de "Ultimos avisos" con 2-3 items y acceso al listado completo

2. **Cabecera del panel**: Siempre muestra el nombre de la trabajadora y su foto de perfil (ambos perfiles).

3. **Limite de servicios en home SAD**: El bloque de servicios muestra como maximo el servicio activo + el siguiente servicio. Si hay mas, se muestra un enlace "Ver mas servicios" (no un contador tipo "+2").

4. **Informacion resumida de servicios en home**: Las tarjetas de servicio en el home muestran informacion resumida. Tocar una tarjeta navega al detalle completo del servicio.

5. **Llamamiento pendiente en home SAD**: Si existe un llamamiento pendiente, se muestra de forma muy visible con urgencia y cuenta atras de caducidad. El CTA del llamamiento en el home navega al detalle del llamamiento; aceptar o rechazar solo es posible dentro del detalle, nunca desde el home.

6. **Documentacion pendiente de firma en home SAD**: Se muestra un badge/contador destacado como elemento de alta prioridad cuando hay documentos pendientes de firma.

7. **Badges en accesos directos**: Los accesos directos muestran badges con contadores numericos para acciones pendientes. Los tipos de badge incluyen: mensajes no leidos (en acceso de Comunicacion), documentos pendientes de firma (en acceso de Documentacion).

8. **Pull-to-refresh**: El panel principal soporta pull-to-refresh para actualizar todos los datos mostrados.

9. **Anuncios fijados**: Los contenidos fijados por backoffice aparecen en la parte superior del tablon, por encima de los no fijados, independientemente de la fecha de publicacion.

10. **Tipologia de anuncios**: El tablon diferencia entre contenidos fijos (protocolos de actuacion, calendario laboral, PRL, documentos de referencia permanente) y comunicaciones variables (recordatorios, campanas, formacion, novedades). El backoffice puede fijar contenidos importantes en la parte superior sin necesidad de separar en bloques rigidos.

11. **Marcado automatico de lectura**: Tanto anuncios como mensajes del sistema se marcan como leidos automaticamente al abrirlos. No existe accion manual de "marcar como leido".

12. **Notificacion push de nuevo comunicado**: Cuando se publica un nuevo comunicado, se envia notificacion push a las trabajadoras. Se muestra un badge en el icono de la seccion indicando contenido nuevo no leido.

13. **Mensajes del sistema de solo lectura**: Los mensajes del sistema no pueden responderse. No se muestra ningun boton de redactar ni campo de entrada de texto.

14. **Criticidad de mensajes del sistema**: Los mensajes se diferencian en dos niveles de criticidad (alta y normal). Los de criticidad alta se muestran primero con diferenciacion visual; los normales se muestran debajo. Los criterios que determinan cada nivel estan pendientes de definicion (ver Items Pendientes [P-001]).

15. **Borrado de mensajes**: La trabajadora puede borrar mensajes del sistema de su bandeja.

16. **Adjuntos**: Tanto los anuncios como los mensajes del sistema soportan imagenes y adjuntos visualizables.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home Hogar | Tocar acceso "Ofertas" | Listado de ofertas (RF-6.1) |
| Home Hogar | Tocar acceso "Mi Disponibilidad" | Calendario de disponibilidad (RF-7.1) |
| Home Hogar | Tocar acceso "Perfil" | Ver y editar perfil (RF-9.1) |
| Home Hogar | Tocar acceso "Comunicacion" | Listado de conversaciones (RF-10.2) |
| Home SAD | Tocar tarjeta de servicio activo | Detalle del servicio (RF-3.2) |
| Home SAD | Tocar "Fichar" | Fichaje entrada/salida (RF-4.1) |
| Home SAD | Tocar acceso "Mis Servicios" | Listado de servicios (RF-3.1) |
| Home SAD | Tocar acceso "Incidencias" | Reportar incidencia (RF-5.1) |
| Home SAD | Tocar acceso "Solicitar Ausencia" | Solicitar ausencia (RF-8.1) |
| Home SAD | Tocar acceso "Mis Ausencias" | Historial de ausencias (RF-8.2) |
| Home SAD | Tocar acceso "Mi Disponibilidad" | Calendario de disponibilidad (RF-7.1) |
| Home SAD | Tocar acceso "Documentacion" | Documentos (RF-9.3) |
| Home SAD | Tocar acceso "Perfil" | Ver y editar perfil (RF-9.1) |
| Home SAD | Tocar acceso "Comunicacion" | Listado de conversaciones (RF-10.2) |
| Home SAD | Tocar tarjeta de llamamiento pendiente | Detalle del llamamiento (RF-3.4) |
| Home SAD | Tocar "Ver mas servicios" | Listado de servicios (RF-3.1) |
| Home SAD | Tocar item en bloque "Ultimos avisos" | Detalle del comunicado (tablon de anuncios) |
| Tablon de anuncios | Tocar comunicado en la lista | Detalle completo del comunicado |
| Mensajes del sistema | Tocar mensaje en la lista | Detalle completo del mensaje |

---

## Criterios de Aceptacion

### CA-001: Home Hogar muestra accesos directos del perfil Hogar <- HU-001
GIVEN la trabajadora tiene perfil Hogar
WHEN accede al panel principal
THEN ve accesos directos a Ofertas, Mi Disponibilidad, Perfil y Comunicacion

### CA-002: Home SAD muestra servicio activo y fichaje como accion principal <- HU-001
GIVEN la trabajadora tiene perfil SAD y tiene un servicio activo
WHEN accede al panel principal
THEN ve el servicio activo con fichaje como accion principal, seguido de los accesos directos a Mis Servicios, Fichar, Incidencias, Solicitar Ausencia, Mis Ausencias, Mi Disponibilidad, Documentacion, Perfil y Comunicacion, y un bloque de "Ultimos avisos" con 2-3 comunicados recientes

### CA-003: Cabecera del panel muestra nombre y foto <- HU-001
GIVEN la trabajadora ha iniciado sesion (cualquier perfil)
WHEN accede al panel principal
THEN la cabecera muestra su nombre y su foto de perfil

### CA-004: Acceso directo navega al modulo correspondiente <- HU-001
GIVEN la trabajadora esta en el panel principal
WHEN toca un acceso directo
THEN la aplicacion navega al modulo correspondiente segun la tabla de destinos de navegacion

### CA-005: Pull-to-refresh actualiza datos del panel <- HU-001
GIVEN la trabajadora esta en el panel principal
WHEN desliza hacia abajo (pull-to-refresh)
THEN los datos del panel se actualizan mostrando la informacion mas reciente

### CA-006: Badge de mensajes no leidos en acceso de Comunicacion <- HU-002
GIVEN la trabajadora tiene mensajes no leidos en el modulo de Comunicacion
WHEN accede al panel principal
THEN el acceso directo de Comunicacion muestra un badge con el numero de mensajes no leidos

### CA-007: Badge de documentos pendientes de firma en acceso de Documentacion (SAD) <- HU-002
GIVEN la trabajadora SAD tiene documentos pendientes de firma
WHEN accede al panel principal
THEN el acceso directo de Documentacion muestra un badge/contador destacado como elemento de alta prioridad

### CA-008: Badges se actualizan al resolver acciones <- HU-002
GIVEN la trabajadora tiene un badge con contador en un acceso directo
WHEN completa la accion pendiente (lee un mensaje, firma un documento) y vuelve al panel
THEN el badge refleja el nuevo conteo o desaparece si no quedan acciones pendientes

### CA-009: Tablon de anuncios lista comunicados diferenciando tipos <- HU-003
GIVEN el backoffice ha publicado comunicados de tipo fijo y de tipo variable
WHEN la trabajadora accede al tablon de anuncios
THEN ve los comunicados diferenciados entre contenidos fijos (protocolos, calendario laboral, PRL, documentos de referencia) y comunicaciones variables (recordatorios, campanas, novedades)

### CA-010: Anuncios fijados aparecen primero en el tablon <- HU-003
GIVEN el backoffice ha fijado uno o mas comunicados como destacados
WHEN la trabajadora accede al tablon de anuncios
THEN los comunicados fijados aparecen en la parte superior del listado, por encima de los no fijados

### CA-011: Previsualizacion de comunicado en el listado <- HU-003
GIVEN existen comunicados publicados en el tablon
WHEN la trabajadora ve el listado de comunicados
THEN cada comunicado muestra titulo, fecha y texto de previsualizacion

### CA-012: Abrir comunicado muestra detalle completo y marca como leido <- HU-003
GIVEN la trabajadora tiene un comunicado no leido en el tablon
WHEN toca el comunicado en el listado
THEN se abre el detalle completo del comunicado (incluyendo imagenes y adjuntos si los tiene) y se marca automaticamente como leido

### CA-013: Indicador visual de comunicados no leidos <- HU-003
GIVEN la trabajadora tiene comunicados no leidos
WHEN ve el listado de comunicados
THEN los comunicados no leidos se distinguen visualmente de los ya leidos

### CA-014: Badge en icono de seccion por contenido nuevo <- HU-003
GIVEN se ha publicado un nuevo comunicado que la trabajadora no ha leido
WHEN la trabajadora ve el menu o tabs de la aplicacion
THEN el icono de la seccion de anuncios muestra un badge indicando contenido nuevo

### CA-015: Notificacion push de nuevo comunicado <- HU-003
GIVEN el backoffice publica un nuevo comunicado
WHEN la publicacion se completa
THEN la trabajadora recibe una notificacion push informando del nuevo comunicado

### CA-016: Mensajes del sistema se listan con remitente, asunto y fecha <- HU-004
GIVEN existen mensajes del sistema dirigidos a la trabajadora
WHEN la trabajadora accede a la seccion de mensajes del sistema
THEN ve una lista de mensajes mostrando remitente, asunto y fecha de cada uno

### CA-017: Mensajes de criticidad alta se muestran primero y diferenciados <- HU-004
GIVEN existen mensajes del sistema de criticidad alta y de criticidad normal
WHEN la trabajadora accede a la seccion de mensajes del sistema
THEN los mensajes de criticidad alta se muestran primero con diferenciacion visual respecto a los de criticidad normal, que aparecen debajo

> **Nota**: Los criterios que determinan que un mensaje sea de criticidad "alta" vs "normal" estan pendientes de definicion por parte del cliente (ver [P-001]). Este CA asume que el nivel de criticidad es asignado por el remitente desde backoffice.

### CA-018: Indicador visual de mensajes no leidos <- HU-004
GIVEN la trabajadora tiene mensajes del sistema no leidos
WHEN ve el listado de mensajes
THEN los mensajes no leidos tienen un indicador visual distintivo

### CA-019: Abrir mensaje muestra contenido y marca como leido <- HU-004
GIVEN la trabajadora tiene un mensaje del sistema no leido
WHEN toca el mensaje en el listado
THEN se abre el contenido completo del mensaje (incluyendo adjuntos si los tiene) y se marca automaticamente como leido

### CA-020: Borrar mensaje del sistema <- HU-004
GIVEN la trabajadora esta en el listado de mensajes del sistema
WHEN selecciona la opcion de borrar un mensaje
THEN el mensaje se elimina de su bandeja

### CA-021: Mensajes del sistema no permiten respuesta <- HU-004
GIVEN la trabajadora esta viendo el detalle de un mensaje del sistema
WHEN observa las opciones disponibles
THEN no existe boton de redactar, responder ni campo de entrada de texto

### CA-022: Llamamiento pendiente visible con urgencia y cuenta atras en home SAD <- HU-005
GIVEN la trabajadora SAD tiene un llamamiento pendiente de respuesta
WHEN accede al panel principal
THEN el llamamiento se muestra de forma muy visible con indicacion de urgencia y cuenta atras de caducidad

### CA-023: CTA de llamamiento en home navega al detalle <- HU-005
GIVEN la trabajadora SAD ve un llamamiento pendiente en el panel principal
WHEN toca la tarjeta del llamamiento
THEN navega al detalle del llamamiento donde puede aceptar o rechazar; no es posible aceptar o rechazar directamente desde el home

### CA-024: Bloque de servicios en home SAD muestra maximo dos servicios <- HU-005
GIVEN la trabajadora SAD tiene mas de dos servicios (activo + siguientes)
WHEN accede al panel principal
THEN el bloque de servicios muestra como maximo el servicio activo y el siguiente servicio, con un enlace "Ver mas servicios" para acceder al listado completo

### CA-025: Tarjeta de servicio en home navega al detalle <- HU-005
GIVEN la trabajadora SAD ve una tarjeta de servicio en el panel principal
WHEN toca la tarjeta
THEN navega al detalle completo del servicio

---

## Checklist de Validacion

- [x] Actores identificados (Trabajadora Hogar, Trabajadora SAD, Backoffice)
- [x] Flujos principales descritos paso a paso (4 journeys)
- [x] Estados de exito definidos para cada journey
- [x] Edge cases documentados (sin servicios, sin llamamientos, sin comunicados, sin mensajes)
- [x] Estados de error definidos (estados vacios)
- [ ] Ambiguedades resueltas — **Pendiente**: criterios de criticidad de mensajes del sistema [P-001]
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes (19 destinos)

---

## Fuera de Alcance

- **Gestion de llamamientos**: la aceptacion y rechazo de llamamientos pertenece a F-004 (service-calls). Esta feature solo muestra el llamamiento pendiente en el home con navegacion al detalle.
- **Gestion de servicios**: el listado completo, detalle, notas e historial de servicios pertenecen a F-003 (service-management). Esta feature solo muestra informacion resumida de servicios en el home.
- **Fichaje**: la funcionalidad de fichar entrada/salida pertenece a F-005 (time-tracking). El home solo provee un acceso directo.
- **Chat y comunicacion**: las conversaciones pertenecen a F-011 (communication). Esta feature solo muestra el badge de mensajes no leidos.
- **Notificaciones push**: la gestion de notificaciones pertenece a F-012 (push-notifications). Esta feature solo recibe la notificacion push de nuevo comunicado como evento externo.
- **Creacion de anuncios y mensajes**: la publicacion de contenido se realiza desde backoffice, fuera del ambito de la app movil.

---

## Items Pendientes

> Este spec tiene gaps **criticos** sin resolver. Las HUs afectadas estan marcadas `[INCOMPLETO]` y `/wf-prepare-plan` quedara bloqueado hasta que se resuelvan.
> Para resolverlos: edita este spec respondiendo los gaps, luego ejecuta `/wf-spec-validate features/dashboard-and-announcements/dashboard-and-announcements_spec.md`.

### [P-001][CRITICO] Criterios de criticidad de mensajes del sistema
- **Afecta**: [HU-004]
- **Pregunta**: Que criterios determinan que un mensaje del sistema sea de "criticidad alta" vs "normal"? Lo decide el remitente al crearlo desde backoffice, o hay reglas automaticas basadas en el contenido?
- **Respuesta**: [CRITICO]_(pendiente)_

---

## Asunciones Aplicadas

- **[A-001]**: El orden de los accesos directos en el home SAD sigue el orden listado en el PRD: Mis Servicios, Fichar, Incidencias, Solicitar Ausencia, Mis Ausencias, Mi Disponibilidad, Documentacion, Perfil, Comunicacion. El acceso de "Fichar" se muestra siempre pero se habilita/deshabilita segun si hay servicio activo. Los accesos no se ocultan por contexto para mantener una navegacion consistente. (Origen: [P-017][INFORMATIVO] del analysis)
