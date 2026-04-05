# Spec: Gestion de Servicios
> Version: 1.0 | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md
> Feature ID: F-003

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora del Servicio de Asistencia Social | Consultar servicios asignados, ver detalle de servicio, gestionar notas, responder a llamamientos, consultar historial, confirmar recepcion de nuevos servicios asignados |

---

## Historias de Usuario

### HU-001: Listado de servicios
Como trabajadora SAD
quiero ver todos mis servicios asignados organizados por estado
para que sepa cuales estan activos, proximos y completados.

### HU-002: Detalle de servicio
Como trabajadora SAD
quiero ver la informacion completa de un servicio
para que conozca los datos del cliente, ubicacion, plan de cuidados y tareas a realizar.

### HU-003: Notas de servicio
Como trabajadora SAD
quiero registrar y consultar notas sobre la evolucion del servicio
para que quede documentada la actividad y las coordinadoras tengan visibilidad.

### HU-004: Respuesta a llamamientos
Como trabajadora SAD
quiero recibir y responder a llamamientos de turnos disponibles
para que pueda aceptar o rechazar oportunidades de servicio.

### HU-005: Historial de servicios
Como trabajadora SAD
quiero consultar mis servicios completados y el historial de llamamientos
para que tenga un registro de mi actividad pasada.

### HU-006: Nuevo servicio asignado (indefinidos)
Como trabajadora SAD con contrato indefinido
quiero recibir notificacion cuando se me asigna un nuevo servicio
para que este informada y pueda comunicar incidencias si no puedo atenderlo.

---

## Recorridos de Usuario

### Journey 1: Consultar servicios
Actor: Trabajadora SAD | Objetivo: Ver sus servicios y acceder al detalle
1. La trabajadora accede a "Mis Servicios" desde el home o menu.
2. Ve la lista de servicios agrupados por estado: Activos, Proximos, Completados.
3. Cada servicio muestra nombre/codigo del cliente, direccion, fecha/hora y tipo.
4. Distincion visual entre servicios recurrentes y puntuales.
5. Toca un servicio para ver el detalle completo.

Estado de exito: La trabajadora ve sus servicios organizados y puede acceder al detalle de cualquiera.
Flujos alternativos:
- Si no hay servicios asignados, se muestra estado vacio.
- Pull-to-refresh actualiza la lista.

### Journey 2: Consultar detalle de servicio
Actor: Trabajadora SAD | Objetivo: Ver toda la informacion de un servicio
1. La trabajadora accede al detalle de un servicio desde la lista o desde el home.
2. Ve la informacion basica: codigo, tipo, fechas, horario.
3. Ve la informacion del cliente: nombre, direccion, edad.
4. Toca la direccion (texto clickable) y se abre la app de Maps del dispositivo.
5. Ve el plan de cuidados y el listado descriptivo de tareas (solo lectura, gestionado desde backend).
6. Ve la documentacion asociada (protocolos).
7. Puede acceder a las notas de servicio, al historial de fichaje, al fichaje directo y al reporte de incidencias.
8. Ve el CTA "Contacta con tu coordinador / empresa" con telefono de coordinacion.

Estado de exito: La trabajadora tiene toda la informacion necesaria para prestar el servicio.
Flujos alternativos:
- Determinados campos del servicio (datos del cliente) son controlables desde backoffice para respetar la privacidad.

### Journey 3: Gestionar notas de servicio
Actor: Trabajadora SAD | Objetivo: Documentar la evolucion del servicio
1. La trabajadora accede a las notas desde el detalle del servicio.
2. Ve la lista cronologica de notas con autora, fecha/hora, contenido y adjuntos.
3. Pulsa "Anadir nota" y escribe texto en campo multilinea.
4. Categoriza la nota: Evolucion, Tareas, Incidencias, Otras.
5. Opcionalmente adjunta fotos o documentos.
6. Confirma y la nota queda visible para las coordinadoras inmediatamente.

Estado de exito: La nota queda registrada, categorizada y visible para coordinadoras.
Flujos alternativos:
- La trabajadora puede borrar sus propias notas (borrado suave para auditoria).

### Journey 4: Responder a un llamamiento
Actor: Trabajadora SAD | Objetivo: Aceptar o rechazar un llamamiento de turno
1. La trabajadora recibe una notificacion push de un nuevo llamamiento.
2. Desde la home (donde se muestra con urgencia y cuenta atras) toca el CTA que lleva al detalle del llamamiento.
3. Ve la informacion basica: codigo de servicio, fecha/hora, ubicacion, urgencia.
4. Toca para ver detalles completos (mas campos que la informacion basica).
5. Una vez dentro del detalle, la navegacion hacia atras queda bloqueada hasta que tome una decision.
6. Para aceptar: firma digitalmente con el dedo sobre un dialogo con copy claro e inequivoco.
7. Para rechazar: selecciona motivo obligatorio (No disponible, Demasiado lejos, Motivos personales, Otros con campo de texto) y firma digitalmente con copy explicito que se distingue del de aceptacion.

Estado de exito: La trabajadora ha aceptado o rechazado el llamamiento con firma digital.
Flujos alternativos:
- Si el llamamiento caduca antes de la decision, se muestra como desactivado/no disponible.
- Si otra trabajadora acepta el llamamiento antes, se muestra como desactivado.
- La cuenta atras visual muestra el tiempo restante para responder.

### Journey 5: Consultar historial
Actor: Trabajadora SAD | Objetivo: Ver servicios pasados y llamamientos historicos
1. La trabajadora accede al historial de servicios.
2. Ve la lista de servicios completados con fechas, nombres de clientes y total de horas trabajadas.
3. Puede filtrar por rango de fechas.
4. Toca un servicio archivado para ver el detalle en solo lectura.
5. Ve el historial completo de llamamientos con su resultado final (aceptado, rechazado, caducado, desactivado).

Estado de exito: La trabajadora tiene acceso a su historial completo de actividad.

### Journey 6: Recibir nuevo servicio asignado (indefinido)
Actor: Trabajadora SAD con contrato indefinido | Objetivo: Confirmar recepcion de nuevo servicio
1. La trabajadora recibe notificacion push "Nuevo servicio asignado" con deeplink al detalle.
2. El nuevo servicio aparece en la home de forma diferenciada de los llamamientos.
3. La trabajadora abre el detalle del servicio y el sistema registra la interaccion "visto/recibido".
4. Si la trabajadora no puede atender el servicio, genera una incidencia desde el detalle.
5. La trabajadora distingue visualmente entre servicios puntuales (con fecha de inicio y fin definidas) y recurrentes (sin fecha de fin, p.ej. martes y jueves de forma continuada).

Estado de exito: El sistema registra que la trabajadora ha visto la asignacion.

---

## Resultados y Exito

- La trabajadora SAD puede consultar todos sus servicios con informacion completa y actualizada.
- Las notas de servicio documentan la evolucion y son visibles para coordinadoras.
- Los llamamientos se gestionan con firma digital obligatoria y sin posibilidad de evasion.
- El historial proporciona una vision completa de la actividad pasada.
- Los servicios asignados a indefinidos quedan registrados como recibidos.

---

## Instrucciones Inambiguas

### Reglas de comportamiento
- La direccion en el detalle de servicio es un texto clickable que abre la app de Maps del dispositivo (Google Maps / Apple Maps). No se incluye mapa embebido.
- El listado de tareas en el detalle del servicio es descriptivo y de solo lectura; deriva de la valoracion/servicio y se gestiona desde backend; la trabajadora no puede editarlo.
- El CTA de contacto en el detalle se etiqueta "Contacta con tu coordinador / empresa" (no "contacto de emergencia").
- La visibilidad de campos del servicio (datos del cliente) es controlable desde backoffice; cada campo puede marcarse como visible o no visible para la cuidadora.
- Un llamamiento puede enviarse a varias trabajadoras simultaneamente; la primera en aceptar lo recibe y el resto queda desactivado (gestion desde backoffice).
- El tiempo limite de exposicion del llamamiento es configurable desde backoffice.
- La aceptacion y el rechazo de un llamamiento requieren firma digital obligatoria.
- Una vez en el detalle del llamamiento, la trabajadora no puede salir sin haber tomado una decision (navegacion hacia atras bloqueada).
- El acceso a aceptar/rechazar un llamamiento es exclusivo desde el detalle del llamamiento (nunca directamente desde la home).
- Si un llamamiento caduca sin respuesta, puede computar como rechazo por inaccion (pendiente de revision legal).
- En la home solo se muestran llamamientos pendientes de respuesta; el historial completo se consulta en la seccion de historial.
- Los motivos de rechazo son: No disponible, Demasiado lejos, Motivos personales, Otros (con campo de texto).
- La trabajadora puede borrar sus propias notas (borrado suave para auditoria); no puede borrar notas de otros.
- Las categorias de notas son: Evolucion, Tareas, Incidencias, Otras.
- La distincion entre servicios puntuales y recurrentes aplica solo a trabajadoras con contrato indefinido en el contexto de nuevos servicios asignados.

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Lista servicios | Tocar servicio | Detalle del servicio |
| Detalle servicio | Tocar direccion | App de Maps del dispositivo |
| Detalle servicio | Tocar "Notas de servicio" | Lista de notas del servicio |
| Detalle servicio | Tocar "Historial de fichaje" | Historial de fichaje para este servicio (F-004) |
| Detalle servicio | Tocar "Fichar entrada/salida" | Pantalla de fichaje (F-004) |
| Detalle servicio | Tocar "Reportar incidencia" | Formulario de reporte de incidencia (F-005) |
| Detalle servicio | Tocar "Contacta con tu coordinador" | Llamada telefonica a coordinacion |
| Home SAD | Tocar llamamiento pendiente | Detalle del llamamiento |
| Detalle llamamiento | Aceptar con firma | Confirmacion de aceptacion |
| Detalle llamamiento | Rechazar con firma y motivo | Confirmacion de rechazo |
| Historial | Tocar servicio archivado | Detalle del servicio (solo lectura) |
| Notificacion push | "Nuevo servicio asignado" | Detalle del servicio asignado |

---

## Criterios de Aceptacion

### CA-001: Listado por estado <- HU-001
GIVEN la trabajadora SAD accede a Mis Servicios
WHEN se carga la lista
THEN los servicios aparecen agrupados por estado: Activos, Proximos, Completados.

### CA-002: Informacion clave del servicio <- HU-001
GIVEN la trabajadora SAD esta en el listado de servicios
WHEN ve la lista
THEN cada servicio muestra nombre/codigo del cliente, direccion, fecha/hora y tipo.

### CA-003: Distincion recurrente vs puntual <- HU-001
GIVEN la trabajadora SAD esta en el listado de servicios
WHEN hay servicios recurrentes y puntuales
THEN se muestra una distincion visual entre ambos tipos.

### CA-004: Navegacion al detalle <- HU-001
GIVEN la trabajadora SAD esta en el listado de servicios
WHEN toca un servicio
THEN navega a la vista detallada del servicio.

### CA-005: Pull-to-refresh en lista <- HU-001
GIVEN la trabajadora SAD esta en el listado de servicios
WHEN realiza gesto de pull-to-refresh
THEN se actualiza la lista de servicios.

### CA-006: Estado vacio <- HU-001
GIVEN la trabajadora SAD no tiene servicios asignados
WHEN accede a Mis Servicios
THEN se muestra un estado vacio informativo.

### CA-007: Info basica del servicio <- HU-002
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN se carga la pantalla
THEN se muestra codigo, tipo, fechas y horario del servicio.

### CA-008: Info del cliente <- HU-002
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN se carga la pantalla
THEN se muestra nombre del cliente, direccion y edad. La visibilidad de determinados campos es controlable desde backoffice.

### CA-009: Direccion clickable <- HU-002
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN toca la direccion
THEN se abre la app de Maps del dispositivo (Google Maps / Apple Maps). No se muestra mapa embebido.

### CA-010: Plan de cuidados y tareas <- HU-002
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN se carga la pantalla
THEN se muestra el plan de cuidados y un listado descriptivo de tareas (sin checklist, solo lectura, gestionado desde backend).

### CA-011: Documentacion asociada <- HU-002
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN hay documentacion asociada (protocolos)
THEN se lista la documentacion disponible.

### CA-012: Accesos desde detalle <- HU-002
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN revisa las opciones disponibles
THEN puede acceder a: notas de servicio, historial de fichaje, fichar entrada/salida y reportar incidencia.

### CA-013: CTA contacto coordinador <- HU-002
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN necesita contactar a coordinacion
THEN ve de forma prominente un CTA "Contacta con tu coordinador / empresa" con el telefono de coordinacion.

### CA-014: Lista cronologica de notas <- HU-003
GIVEN la trabajadora SAD accede a las notas de un servicio
WHEN se carga la lista
THEN se muestran las notas en orden cronologico con autora, fecha/hora, contenido y adjuntos.

### CA-015: Anadir nota con categoria <- HU-003
GIVEN la trabajadora SAD esta en las notas de un servicio
WHEN pulsa "Anadir nota"
THEN puede escribir texto multilinea, seleccionar categoria (Evolucion, Tareas, Incidencias, Otras) y adjuntar archivos opcionales.

### CA-016: Adjuntar archivos a nota <- HU-003
GIVEN la trabajadora SAD esta creando una nota
WHEN decide adjuntar archivos
THEN puede adjuntar fotos y documentos a la nota.

### CA-017: Borrar nota propia <- HU-003
GIVEN la trabajadora SAD esta en las notas de un servicio
WHEN selecciona borrar una nota propia
THEN la nota se elimina con borrado suave (para auditoria).

### CA-018: Notas visibles para coordinadoras <- HU-003
GIVEN la trabajadora SAD anade una nota de servicio
WHEN la nota se guarda
THEN la nota es visible para las coordinadoras inmediatamente.

### CA-019: Listado de llamamientos <- HU-004
GIVEN la trabajadora SAD accede a la lista de llamamientos
WHEN se carga la lista
THEN se muestran los llamamientos con estado (pendiente, aceptada, rechazada, caducada/desactivada).

### CA-020: Info basica del llamamiento <- HU-004
GIVEN la trabajadora SAD esta en la lista de llamamientos
WHEN ve un llamamiento
THEN se muestra codigo de servicio, fecha/hora, ubicacion y urgencia.

### CA-021: Detalle del llamamiento <- HU-004
GIVEN la trabajadora SAD esta en la lista de llamamientos
WHEN toca un llamamiento pendiente
THEN accede al detalle completo (mas campos que la informacion basica).

### CA-022: Aceptar con firma digital <- HU-004
GIVEN la trabajadora SAD esta en el detalle de un llamamiento pendiente
WHEN decide aceptar
THEN se muestra un dialogo donde debe firmar digitalmente con el dedo; el copy es claro e inequivoco.

### CA-023: Rechazar con motivo y firma <- HU-004
GIVEN la trabajadora SAD esta en el detalle de un llamamiento pendiente
WHEN decide rechazar
THEN debe seleccionar un motivo obligatorio (No disponible, Demasiado lejos, Motivos personales, Otros con campo de texto) y firmar digitalmente; el copy es explicito y se distingue del de aceptacion.

### CA-024: Notificacion push de llamamiento <- HU-004
GIVEN se genera un nuevo llamamiento para la trabajadora
WHEN el llamamiento esta disponible
THEN la trabajadora recibe una notificacion push.

### CA-025: Caducidad del llamamiento <- HU-004
GIVEN un llamamiento esta pendiente de respuesta
WHEN se alcanza el tiempo limite configurado desde backoffice
THEN el llamamiento caduca automaticamente y se muestra como desactivado/no disponible.

### CA-026: Cuenta atras visual <- HU-004
GIVEN la trabajadora SAD ve un llamamiento pendiente
WHEN el llamamiento tiene tiempo limite
THEN se muestra una cuenta atras visual con el tiempo restante.

### CA-027: Llamamiento aceptado por otra <- HU-004
GIVEN la trabajadora SAD tiene un llamamiento pendiente
WHEN otra trabajadora acepta el mismo llamamiento
THEN se muestra como desactivado/no disponible en la lista.

### CA-028: Bloqueo de navegacion en detalle <- HU-004
GIVEN la trabajadora SAD esta en el detalle de un llamamiento pendiente
WHEN intenta navegar hacia atras
THEN la navegacion queda bloqueada hasta que acepte o rechace (sin boton de retroceso hasta decision final).

### CA-029: Historial de servicios completados <- HU-005
GIVEN la trabajadora SAD accede al historial
WHEN se carga la lista
THEN se muestran los servicios completados con fechas, nombres de clientes y total de horas trabajadas.

### CA-030: Filtro por fechas en historial <- HU-005
GIVEN la trabajadora SAD esta en el historial
WHEN aplica filtro de fechas
THEN la lista se filtra por el rango de fechas indicado.

### CA-031: Detalle archivado solo lectura <- HU-005
GIVEN la trabajadora SAD esta en el historial
WHEN toca un servicio completado
THEN se muestra el detalle del servicio archivado en solo lectura.

### CA-032: Historial completo de llamamientos <- HU-005
GIVEN la trabajadora SAD accede al historial
WHEN consulta la seccion de llamamientos
THEN se muestra el historial completo con resultado final (aceptado, rechazado, caducado, desactivado).

### CA-033: Notificacion nuevo servicio asignado <- HU-006
GIVEN se asigna un nuevo servicio a una trabajadora SAD con contrato indefinido
WHEN el servicio queda asignado
THEN la trabajadora recibe notificacion push "Nuevo servicio asignado" con deeplink al detalle.

### CA-034: Nuevo servicio en home diferenciado <- HU-006
GIVEN la trabajadora SAD con contrato indefinido tiene un nuevo servicio asignado
WHEN accede a la home
THEN el nuevo servicio se muestra de forma diferenciada de los llamamientos.

### CA-035: Registro de recepcion <- HU-006
GIVEN la trabajadora SAD abre el detalle de un nuevo servicio asignado
WHEN visualiza el detalle
THEN el sistema registra la interaccion "visto/recibido".

### CA-036: Incidencia desde nuevo servicio <- HU-006
GIVEN la trabajadora SAD esta en el detalle de un nuevo servicio asignado
WHEN no puede atender el servicio
THEN puede generar una incidencia desde el detalle (no es un rechazo formal, es comunicacion a coordinacion).

### CA-037: Distincion puntual vs recurrente <- HU-006
GIVEN la trabajadora SAD con contrato indefinido recibe nuevos servicios
WHEN consulta los servicios asignados
THEN distingue visualmente entre servicios puntuales (con fecha de inicio y fin definidas) y recurrentes (sin fecha de fin).

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
- Creacion o edicion de servicios por parte de la trabajadora (gestionado desde backoffice)
- Edicion de tareas del plan de cuidados (solo lectura)
- Checklist interactivo de tareas (es un listado descriptivo)
- Mapa embebido en detalle de servicio (solo enlace a Maps)
- Gestion de llamamientos desde la home (solo visualizacion; aceptar/rechazar es desde el detalle)

---

## Asunciones Aplicadas
| Gap origen | Asuncion aplicada |
|------------|-------------------|
| [P-004] | Los textos oficiales (copy) de aceptacion y rechazo de llamamientos deben ser proporcionados por negocio/legal; hasta entonces se usan textos genericos diferenciados |
| [P-005] | La caducidad de un llamamiento sin respuesta puede computar como rechazo por inaccion, pendiente de confirmacion legal; mientras tanto, se muestra como "caducado" sin implicacion de rechazo |
