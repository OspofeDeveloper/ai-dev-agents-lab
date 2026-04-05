# Spec: Gestion de Servicios
> Version: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-003 via prd-hogar-sad_discovery.md)
> Feature ID: F-003
> Spec monolitico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social (perfil Felizvita) que gestiona sus servicios asignados | Consultar listado de servicios, ver detalle de servicio, anadir y borrar notas de servicio, consultar historial de servicios completados, confirmar recepcion de nuevo servicio asignado |
| Trabajadora SAD (contrato indefinido) | Subconjunto de Trabajadora SAD con contrato indefinido; recibe asignaciones directas sin llamamiento | Recibir notificacion de nuevo servicio asignado, confirmar recepcion, generar incidencia si no puede atenderlo |

---

## Historias de Usuario

### HU-001: Consultar listado de servicios asignados
Como Trabajadora SAD
quiero ver todos mis servicios asignados agrupados por estado
para que pueda organizar mi jornada y saber que servicios tengo activos, proximos y completados.

### HU-002: Ver detalle completo de un servicio
Como Trabajadora SAD
quiero acceder a la informacion completa de un servicio (datos del cliente, ubicacion, plan de cuidados, tareas y documentacion)
para que pueda prestar el servicio con toda la informacion necesaria sin depender de llamadas a coordinacion.

> :warning: [INCOMPLETO] -- Pendiente de gap(s): [P-008]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-003: Registrar notas de servicio
Como Trabajadora SAD
quiero anadir notas sobre la evolucion del servicio con adjuntos y categorias
para que coordinacion tenga un registro actualizado del estado del servicio y pueda tomar decisiones informadas.

> :warning: [INCOMPLETO] -- Pendiente de gap(s): [P-010]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-004: Consultar historial de servicios completados
Como Trabajadora SAD
quiero ver un historial de mis servicios finalizados con horas trabajadas y filtros por fecha
para que pueda llevar un registro de mi actividad y consultar datos de servicios pasados.

### HU-005: Recibir y confirmar nuevo servicio asignado (contrato indefinido)
Como Trabajadora SAD con contrato indefinido
quiero recibir una notificacion cuando se me asigne un nuevo servicio y poder confirmar que la he recibido
para que coordinacion sepa que estoy informada y pueda comunicar si no puedo atenderlo.

---

## Recorridos de Usuario

### Journey 1: Consultar el listado de servicios
Actor: Trabajadora SAD | Objetivo: Ver el estado de todos sus servicios asignados

1. La trabajadora accede a la seccion "Mis Servicios" desde la navegacion principal.
2. La aplicacion muestra los servicios agrupados en tres secciones: Activos, Proximos, Completados.
3. Cada tarjeta de servicio muestra informacion clave: nombre o codigo del cliente, direccion, fecha/hora y tipo de servicio.
4. Los servicios recurrentes y puntuales se distinguen visualmente.
5. La trabajadora toca un servicio para acceder a su detalle completo.

Estado de exito: La trabajadora ve todos sus servicios organizados por estado y puede acceder al detalle de cualquiera de ellos con un toque.
Flujos alternativos: Si no tiene servicios asignados, se muestra un estado vacio con un mensaje informativo. Si quiere refrescar la lista, desliza hacia abajo para actualizar.

### Journey 2: Ver el detalle de un servicio
Actor: Trabajadora SAD | Objetivo: Consultar toda la informacion necesaria para prestar el servicio

1. La trabajadora toca un servicio del listado.
2. La aplicacion muestra la informacion basica del servicio: codigo, tipo (recurrente o puntual), fechas y horario.
3. Se muestra la informacion del cliente: nombre, direccion y edad. La direccion es un texto clickable que abre la aplicacion de mapas del dispositivo.
4. Se muestra el plan de cuidados con un listado descriptivo de tareas (no editable por la trabajadora).
5. Se muestra la documentacion asociada al servicio (protocolos de cuidado).
6. La trabajadora tiene acceso directo a: notas de servicio, historial de fichajes del servicio, fichar entrada/salida, reportar incidencia y contactar con coordinacion.
7. De forma prominente se muestra un boton "Contacta con tu coordinador / empresa" con el telefono de coordinacion.

Estado de exito: La trabajadora tiene toda la informacion del servicio disponible en una sola pantalla y puede navegar a las acciones relacionadas.
Flujos alternativos: Si la visibilidad de determinados campos del cliente esta restringida desde backoffice, esos campos no se muestran. Si es un servicio archivado (del historial), se muestra en modo solo lectura.

### Journey 3: Anadir una nota de servicio
Actor: Trabajadora SAD | Objetivo: Registrar informacion sobre la evolucion del servicio

1. Desde el detalle del servicio, la trabajadora accede a la seccion de notas.
2. La aplicacion muestra las notas existentes en orden cronologico, con autora, fecha/hora, contenido y adjuntos.
3. La trabajadora pulsa "Anadir nota".
4. La trabajadora selecciona una categoria para la nota: Evolucion, Tareas, Incidencias u Otras.
5. La trabajadora escribe el contenido de la nota en un campo de texto multilinea.
6. Opcionalmente, adjunta archivos (fotos o documentos).
7. La trabajadora confirma y la nota queda visible para coordinacion de forma inmediata.

Estado de exito: La nota queda registrada con su categoria, contenido y adjuntos, y es visible para coordinacion.
Flujos alternativos: Si la trabajadora desea borrar una nota propia, puede hacerlo (la nota queda eliminada de la vista pero se conserva internamente para auditoria).

### Journey 4: Consultar el historial de servicios completados
Actor: Trabajadora SAD | Objetivo: Revisar sus servicios finalizados y las horas trabajadas

1. La trabajadora accede a la seccion de historial dentro de "Mis Servicios".
2. La aplicacion muestra los servicios completados con fecha y nombre del cliente.
3. Cada entrada del historial muestra el total de horas trabajadas en ese servicio.
4. La trabajadora puede filtrar por rango de fechas.
5. La trabajadora puede tocar un servicio archivado para ver su detalle en modo solo lectura.
6. Dentro del historial se muestra tambien el historial completo de llamamientos con su resultado final (aceptado, rechazado, caducado, desactivado), referenciando la entidad Llamamiento gestionada por F-004.

Estado de exito: La trabajadora consulta sus servicios pasados con las horas trabajadas y puede filtrar para encontrar informacion especifica.
Flujos alternativos: Si no hay servicios completados, se muestra un estado vacio.

### Journey 5: Recibir y confirmar nuevo servicio asignado (contrato indefinido)
Actor: Trabajadora SAD (contrato indefinido) | Objetivo: Tomar conocimiento de un nuevo servicio asignado

1. La trabajadora recibe una notificacion informando de un nuevo servicio asignado.
2. Al tocar la notificacion o al acceder a la home, el nuevo servicio aparece de forma destacada y diferenciada de los llamamientos.
3. La trabajadora toca el nuevo servicio para ver su detalle.
4. Al abrir el detalle, la aplicacion registra automaticamente que la trabajadora ha visto la notificacion (confirmacion de recepcion).
5. Si la trabajadora no puede atender el servicio, puede generar una incidencia desde el detalle para comunicarlo a coordinacion.
6. Los servicios se distinguen visualmente entre puntuales (con fecha de inicio y fin definidas) y recurrentes (sin fecha de fin).

Estado de exito: La trabajadora ha visto el nuevo servicio, la recepcion queda registrada y, si no puede atenderlo, ha generado una incidencia.
Flujos alternativos: Si la trabajadora no abre el detalle, la confirmacion de recepcion no se registra y el servicio sigue apareciendo como nuevo.

---

## Resultados y Exito

La feature "Gestion de Servicios" se considera exitosa cuando:

1. La trabajadora SAD puede consultar todos sus servicios asignados organizados por estado (Activos, Proximos, Completados) en un unico punto de acceso.
2. El detalle de cada servicio proporciona toda la informacion necesaria para prestar el servicio (cliente, ubicacion navegable a mapas, plan de cuidados, tareas, documentacion) y ofrece accesos directos a acciones relacionadas (fichaje, incidencias, notas, comunicacion).
3. La trabajadora puede registrar notas categorizadas con adjuntos que coordinacion ve de forma inmediata.
4. El historial muestra los servicios completados con horas trabajadas y permite filtrar por fecha.
5. Las trabajadoras con contrato indefinido reciben la asignacion de nuevos servicios como notificacion informativa, confirman recepcion y pueden generar incidencia si no pueden atenderlo.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Agrupacion de servicios**: Los servicios se agrupan en tres estados: Activos (servicio en curso), Proximos (con fecha de inicio posterior a hoy), Completados (finalizados). Cada grupo se muestra como una seccion diferenciada en el listado.

2. **Distincion recurrente vs puntual**: Los servicios puntuales tienen fecha de inicio y fecha de fin definidas (pueden durar dias o semanas). Los servicios recurrentes no tienen fecha de fin (ej: martes y jueves de forma continuada). La distincion es visual y conceptual en el listado y el detalle.

3. **Direccion clickable**: La direccion del cliente en el detalle del servicio es un texto interactivo que, al tocarlo, abre la aplicacion de mapas nativa del dispositivo (no se incluye mapa embebido en la pantalla de detalle).

4. **Plan de cuidados y tareas**: El listado de tareas del servicio es descriptivo y de solo lectura para la trabajadora. Se deriva de la valoracion o configuracion del servicio gestionada desde backoffice. La trabajadora no puede editar ni marcar tareas como completadas.

5. **Contacto con coordinacion**: El boton "Contacta con tu coordinador / empresa" se muestra de forma prominente en el detalle del servicio con el telefono de coordinacion. No se denomina "contacto de emergencia" ya que no es una emergencia real.

6. **Accesos directos desde detalle**: Desde el detalle del servicio, la trabajadora puede acceder directamente a: fichar entrada/salida (F-005), reportar incidencia (F-006), notas de servicio, historial de fichajes del servicio y contacto con coordinacion.

7. **Visibilidad de campos controlada por backoffice**: La visibilidad de determinados campos del cliente en el detalle del servicio es controlable desde backoffice. Cada campo puede marcarse como visible o no visible para la trabajadora. Si un campo esta marcado como no visible, no se muestra en la app.

8. **Notas de servicio - categorias**: Las notas se categorizan en: Evolucion, Tareas, Incidencias, Otras. La categoria es obligatoria al crear una nota.

9. **Notas de servicio - adjuntos**: Las notas admiten adjuntos de archivos (fotos y documentos). No hay limite especificado en el PRD para el numero de adjuntos por nota.

10. **Notas de servicio - borrado**: La trabajadora puede borrar sus propias notas. El borrado es suave (la nota se conserva internamente para auditoria pero desaparece de la vista de la trabajadora).

11. **Notas de servicio - visibilidad**: Las notas creadas por la trabajadora son visibles para coordinacion de forma inmediata tras su creacion.

12. **Historial - horas trabajadas**: El historial muestra el total de horas trabajadas por servicio. No se muestran conteos de horas extra ni diferencias respecto a horas contratadas (esa logica corresponde a F-005: time-tracking si aplica).

13. **Historial - llamamientos**: El historial de servicios incluye el historial completo de llamamientos con su resultado final (aceptado, rechazado, caducado, desactivado). La entidad Llamamiento es propiedad de F-004: service-calls; esta feature solo la referencia y muestra.

14. **Nuevo servicio asignado (indefinidos) - no es llamamiento**: Para trabajadoras con contrato indefinido, la asignacion de un nuevo servicio es una notificacion informativa, no un llamamiento. No requiere aceptacion ni rechazo formal.

15. **Confirmacion de recepcion**: La confirmacion de que la trabajadora ha visto el nuevo servicio se registra automaticamente cuando la trabajadora abre el detalle del servicio.

16. **Incidencia por imposibilidad de atencion**: Si la trabajadora con contrato indefinido no puede atender un servicio asignado, puede generar una incidencia desde el detalle del servicio. Esto no es un rechazo formal sino una comunicacion a coordinacion (la gestion de incidencias corresponde a F-006: incident-reporting).

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Navegacion principal / Home SAD | Toca "Mis Servicios" | Listado de servicios agrupado por estado |
| Listado de servicios | Toca una tarjeta de servicio | Detalle del servicio |
| Listado de servicios | Desliza hacia abajo (pull-to-refresh) | Recarga del listado |
| Detalle del servicio | Toca la direccion del cliente | Aplicacion de mapas nativa del dispositivo |
| Detalle del servicio | Toca "Notas de servicio" | Listado de notas del servicio |
| Detalle del servicio | Toca "Fichar entrada/salida" | Pantalla de fichaje (F-005) |
| Detalle del servicio | Toca "Reportar incidencia" | Formulario de incidencia (F-006) |
| Detalle del servicio | Toca "Historial de fichajes" | Historial de fichajes del servicio (F-005) |
| Detalle del servicio | Toca "Contacta con tu coordinador / empresa" | Llamada telefonica a coordinacion |
| Listado de notas | Toca "Anadir nota" | Formulario de nueva nota |
| Formulario de nueva nota | Confirma la nota | Listado de notas (nota nueva visible) |
| Historial de servicios | Toca servicio archivado | Detalle del servicio en modo solo lectura |
| Historial de servicios | Toca entrada de llamamiento | Detalle del llamamiento (F-004) |
| Notificacion "Nuevo servicio asignado" | Toca la notificacion | Detalle del nuevo servicio |
| Detalle del nuevo servicio | Toca "Generar incidencia" | Formulario de incidencia (F-006) |

---

## Criterios de Aceptacion

### CA-001: Servicios agrupados por estado <- HU-001
GIVEN la trabajadora SAD tiene servicios asignados en diferentes estados
WHEN accede al listado de "Mis Servicios"
THEN los servicios se muestran agrupados en tres secciones: Activos, Proximos y Completados

### CA-002: Informacion clave en tarjeta de servicio <- HU-001
GIVEN la trabajadora SAD accede al listado de servicios
WHEN visualiza una tarjeta de servicio
THEN la tarjeta muestra nombre o codigo del cliente, direccion, fecha/hora y tipo de servicio

### CA-003: Distincion visual recurrente vs puntual <- HU-001
GIVEN la trabajadora SAD tiene servicios recurrentes y puntuales asignados
WHEN visualiza el listado de servicios
THEN los servicios recurrentes y puntuales se distinguen visualmente entre si

### CA-004: Navegacion a detalle desde tarjeta <- HU-001
GIVEN la trabajadora SAD visualiza el listado de servicios
WHEN toca una tarjeta de servicio
THEN la aplicacion muestra el detalle completo de ese servicio

### CA-005: Actualizacion del listado <- HU-001
GIVEN la trabajadora SAD esta en el listado de servicios
WHEN desliza hacia abajo (pull-to-refresh)
THEN el listado se actualiza con los datos mas recientes del servidor

### CA-006: Estado vacio sin servicios <- HU-001
GIVEN la trabajadora SAD no tiene ningun servicio asignado
WHEN accede al listado de "Mis Servicios"
THEN se muestra un estado vacio con un mensaje informativo

### CA-007: Informacion basica del servicio en detalle <- HU-002
GIVEN la trabajadora SAD accede al detalle de un servicio
WHEN se carga la pantalla de detalle
THEN se muestra el codigo del servicio, tipo (recurrente o puntual), fechas y horario

### CA-008: Informacion del cliente en detalle <- HU-002
GIVEN la trabajadora SAD accede al detalle de un servicio cuyo cliente tiene campos visibles
WHEN se carga la pantalla de detalle
THEN se muestra nombre, direccion y edad del cliente

> :warning: [INCOMPLETO] -- Pendiente de gap(s): [P-008]. La informacion de salud del cliente (medicacion, condiciones medicas) queda excluida de este CA hasta que se resuelva la revision RGPD. Si la revision confirma que pueden mostrarse, se anadira un CA adicional.

### CA-009: Direccion clickable abre mapas <- HU-002
GIVEN la trabajadora SAD esta en el detalle de un servicio que tiene direccion del cliente
WHEN toca la direccion del cliente
THEN se abre la aplicacion de mapas nativa del dispositivo con esa direccion

### CA-010: Plan de cuidados y tareas en detalle <- HU-002
GIVEN la trabajadora SAD accede al detalle de un servicio que tiene plan de cuidados
WHEN se carga la pantalla de detalle
THEN se muestra el plan de cuidados y un listado descriptivo de tareas en modo solo lectura

### CA-011: Documentacion del servicio <- HU-002
GIVEN la trabajadora SAD accede al detalle de un servicio que tiene documentacion asociada
WHEN se carga la pantalla de detalle
THEN se muestran los protocolos de cuidado y documentacion asociada al servicio

### CA-012: Boton de contacto con coordinacion <- HU-002
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN visualiza la pantalla
THEN se muestra de forma prominente un boton "Contacta con tu coordinador / empresa" con el telefono de coordinacion

### CA-013: Acceso directo a fichaje desde detalle <- HU-002
GIVEN la trabajadora SAD esta en el detalle de un servicio activo
WHEN busca la opcion de fichar
THEN encuentra un acceso directo para fichar entrada/salida sin necesidad de volver a la home

### CA-014: Acceso directo a reportar incidencia <- HU-002
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN busca reportar una incidencia del servicio
THEN encuentra un boton para reportar incidencia accesible desde el propio detalle

### CA-015: Visibilidad de campos controlada por backoffice <- HU-002
GIVEN el backoffice ha marcado determinados campos del cliente como no visibles para la trabajadora
WHEN la trabajadora accede al detalle de ese servicio
THEN los campos marcados como no visibles no se muestran en la pantalla de detalle

### CA-016: Listado cronologico de notas <- HU-003
GIVEN la trabajadora SAD accede a las notas de un servicio que tiene notas registradas
WHEN se carga la seccion de notas
THEN las notas se muestran en orden cronologico con autora, fecha/hora, contenido y adjuntos

### CA-017: Crear nota con categoria <- HU-003
GIVEN la trabajadora SAD esta en la seccion de notas de un servicio
WHEN pulsa "Anadir nota", selecciona una categoria (Evolucion, Tareas, Incidencias u Otras), escribe el contenido y confirma
THEN la nota queda registrada con la categoria seleccionada y es visible para coordinacion de forma inmediata

### CA-018: Adjuntar archivos a nota <- HU-003
GIVEN la trabajadora SAD esta creando una nueva nota de servicio
WHEN adjunta archivos (fotos o documentos) y confirma la nota
THEN la nota queda registrada con los adjuntos incluidos

### CA-019: Borrar nota propia <- HU-003
GIVEN la trabajadora SAD tiene notas propias registradas en un servicio
WHEN selecciona borrar una nota propia
THEN la nota desaparece de la vista de la trabajadora pero se conserva internamente para auditoria

### CA-020: Historial de servicios completados <- HU-004
GIVEN la trabajadora SAD tiene servicios completados
WHEN accede al historial de servicios
THEN se muestran los servicios completados con fecha y nombre del cliente

### CA-021: Horas trabajadas por servicio en historial <- HU-004
GIVEN la trabajadora SAD consulta el historial de servicios
WHEN visualiza la lista de servicios completados
THEN cada entrada muestra el total de horas trabajadas en ese servicio

### CA-022: Filtrado del historial por fecha <- HU-004
GIVEN la trabajadora SAD esta en el historial de servicios
WHEN aplica un filtro por rango de fechas
THEN solo se muestran los servicios completados dentro del rango seleccionado

### CA-023: Detalle de servicio archivado en solo lectura <- HU-004
GIVEN la trabajadora SAD esta en el historial de servicios
WHEN toca un servicio completado
THEN se muestra el detalle de ese servicio en modo solo lectura

### CA-024: Historial de llamamientos en seccion de historial <- HU-004
GIVEN la trabajadora SAD accede al historial de servicios
WHEN visualiza la seccion de historial
THEN se muestra el historial completo de llamamientos con su resultado final (aceptado, rechazado, caducado, desactivado)

### CA-025: Notificacion de nuevo servicio asignado (indefinido) <- HU-005
GIVEN la trabajadora SAD con contrato indefinido tiene un nuevo servicio asignado por backoffice
WHEN recibe la notificacion
THEN la notificacion indica "Nuevo servicio asignado" y permite navegar al detalle del servicio

### CA-026: Nuevo servicio destacado en home <- HU-005
GIVEN la trabajadora SAD con contrato indefinido tiene un nuevo servicio asignado sin confirmar
WHEN accede a la home o al listado de servicios
THEN el nuevo servicio se muestra de forma destacada y diferenciada visualmente de los llamamientos

### CA-027: Confirmacion automatica de recepcion <- HU-005
GIVEN la trabajadora SAD con contrato indefinido tiene un nuevo servicio asignado pendiente de confirmacion
WHEN abre el detalle de ese servicio
THEN la aplicacion registra automaticamente que la trabajadora ha visto la notificacion (estado: recibido/confirmado)

### CA-028: Generar incidencia desde nuevo servicio <- HU-005
GIVEN la trabajadora SAD con contrato indefinido esta en el detalle de un servicio recien asignado y no puede atenderlo
WHEN selecciona la opcion de generar una incidencia
THEN la aplicacion la dirige al formulario de incidencia con el contexto del servicio prellenado

### CA-029: Distincion puntual vs recurrente en asignacion <- HU-005
GIVEN la trabajadora SAD con contrato indefinido recibe un nuevo servicio asignado
WHEN accede al detalle del servicio
THEN puede distinguir visualmente si el servicio es puntual (con fecha de inicio y fin definidas) o recurrente (sin fecha de fin)

---

## Checklist de Validacion

- [x] Actores identificados (Trabajadora SAD, Trabajadora SAD con contrato indefinido)
- [x] Flujos principales descritos paso a paso (5 journeys)
- [x] Estados de exito definidos para cada journey
- [x] Edge cases documentados (estado vacio, servicio archivado en solo lectura, campos ocultos por backoffice, trabajadora sin servicios)
- [x] Estados de error definidos (estado vacio sin servicios, campos no visibles por privacidad)
- [ ] Ambiguedades resueltas -- Pendiente: [P-008] datos de salud RGPD, [P-010] edicion de notas
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- **Llamamientos (ciclo de aceptar/rechazar)**: Gestionados por F-004: service-calls. Esta feature solo referencia el historial de llamamientos en la seccion de historial.
- **Fichaje de entrada/salida**: Gestionado por F-005: time-tracking. Esta feature ofrece acceso directo al fichaje desde el detalle del servicio pero no gestiona la funcionalidad de fichaje.
- **Reporte de incidencias**: Gestionado por F-006: incident-reporting. Esta feature ofrece acceso directo al formulario de incidencia pero no gestiona la funcionalidad de incidencias.
- **Seguimiento PIA**: Funcionalidad descartada en el PRD (RF-3.6 eliminado).
- **Edicion de plan de cuidados o tareas por parte de la trabajadora**: El plan de cuidados y las tareas son de solo lectura; su gestion se realiza desde backoffice.
- **Fichaje manual o correccion de fichajes**: Las correcciones se gestionan internamente desde backoffice.
- **Conteos de horas extra o diferencias respecto a horas contratadas**: No se muestran en el historial de esta feature.

---

## Items Pendientes

> :warning: Este spec tiene gaps **criticos** sin resolver. Las HUs afectadas estan marcadas `[INCOMPLETO]` y `/wf-prepare-plan` quedara bloqueado hasta que se resuelvan.
> Para resolverlos: edita el `_analysis.md` respondiendo los gaps, luego ejecuta `/wf-spec-delta resolve features/service-management/service-management_spec.md`.

### [P-008][CRITICO] Revision RGPD sobre datos de salud del cliente
- **Afecta**: [HU-002]
- **Pregunta**: Se ha completado la revision RGPD? Se pueden mostrar datos de salud del cliente (medicacion, condiciones medicas) a la cuidadora en la app, o deben excluirse?
- **Respuesta**: [CRITICO]_(pendiente)_

### [P-010][CRITICO] Notas de servicio: posibilidad de editar notas propias
- **Afecta**: [HU-003]
- **Pregunta**: La trabajadora puede editar sus propias notas de servicio despues de crearlas? Si es asi, hay un plazo maximo para editarlas?
- **Respuesta**: [CRITICO]_(pendiente)_

---

## Asunciones Aplicadas

- **[A-001]**: Los adjuntos en notas de servicio no tienen un limite maximo especificado. Se asume que el limite sera el que establezca el servidor. Si se requiere un limite funcional concreto, debe definirse en la respuesta a este spec.
- **[A-002]**: El historial de llamamientos mostrado en la seccion de historial de servicios referencia la entidad Llamamiento de F-004 y se limita a mostrar el resultado final (aceptado, rechazado, caducado, desactivado). La interaccion con llamamientos activos no forma parte de esta feature.
- **[A-003]**: La confirmacion de recepcion de nuevo servicio asignado (contrato indefinido) se registra al abrir el detalle del servicio. No se requiere una accion explicita adicional de la trabajadora (no hay boton "Confirmar recepcion"); la apertura del detalle es suficiente.

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-04-05 | Version inicial generada via fast-track desde PRD (scope F-003) |
