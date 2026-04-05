# Spec: Gestion de Ausencias
> Version: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-008 via prd-hogar-sad_discovery.md)
> Feature ID: F-008
> Spec monolitico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Profesional del Servicio de Asistencia Social contratada que gestiona sus servicios | Solicitar ausencias, consultar historial de ausencias, ver saldos de vacaciones, cancelar solicitudes pendientes |

---

## Historias de Usuario

### HU-001: Solicitar una ausencia
Como trabajadora SAD
quiero solicitar una ausencia indicando el tipo, las fechas, el motivo y la documentacion justificativa si aplica
para que coordinacion pueda gestionar mi cobertura y yo tenga constancia formal de mi solicitud.

### HU-002: Consultar el historial de ausencias
Como trabajadora SAD
quiero consultar todas mis solicitudes de ausencia con su estado actual y poder filtrarlas
para que pueda hacer seguimiento de mis solicitudes y conocer su resultado.

### HU-003: Consultar saldo de vacaciones
Como trabajadora SAD
quiero ver mis contadores de vacaciones (asignacion anual, dias utilizados, pendientes de aprobacion, disponibles)
para que pueda planificar mis ausencias conociendo cuantos dias tengo disponibles.

### HU-004: Cancelar una solicitud de ausencia pendiente
Como trabajadora SAD
quiero cancelar una solicitud de ausencia que aun no ha sido aprobada ni rechazada
para que pueda rectificar si mis planes cambian antes de que coordinacion la procese.

---

## Recorridos de Usuario

### Journey 1: Solicitar una ausencia
Actor: Trabajadora SAD | Objetivo: Registrar formalmente una solicitud de ausencia

1. La trabajadora accede a la seccion "Mis Ausencias"
2. La trabajadora pulsa "Solicitar ausencia"
3. La trabajadora selecciona el tipo de ausencia de la lista predefinida (Vacaciones, Permiso personal, Baja medica, Baja voluntaria, Asuntos propios, Otros)
4. La trabajadora selecciona la fecha de inicio y la fecha de fin, con opcion de marcar medio dia para la fecha de inicio y/o la fecha de fin
5. Si el tipo seleccionado requiere motivo obligatorio, la trabajadora introduce el motivo o descripcion
6. Si el tipo es baja medica y la duracion supera los 3 dias, la trabajadora adjunta el certificado medico
7. Antes de enviar, la trabajadora visualiza su saldo de vacaciones disponible (si el tipo es Vacaciones)
8. Si las fechas seleccionadas coinciden con servicios asignados, la trabajadora ve una advertencia informativa
9. La trabajadora pulsa "Enviar solicitud"
10. La solicitud queda registrada en estado "Pendiente" y la trabajadora recibe una confirmacion visual
11. La trabajadora recibe una notificacion push de confirmacion del envio

Estado de exito: La solicitud de ausencia queda registrada con estado "Pendiente" y visible en el historial de ausencias. La trabajadora ha recibido confirmacion del envio.

Flujos alternativos:
- Si el certificado medico es obligatorio y no se adjunta -> la solicitud no puede enviarse, se indica el campo pendiente
- Si las fechas coinciden con servicios asignados -> se muestra advertencia pero se permite continuar con el envio

### Journey 2: Consultar historial y filtrar ausencias
Actor: Trabajadora SAD | Objetivo: Revisar el estado de sus solicitudes de ausencia

1. La trabajadora accede a la seccion "Mis Ausencias"
2. La trabajadora ve el listado de ausencias en orden cronologico inverso
3. Cada ausencia muestra: tipo, fechas, recuento de dias, estado (Pendiente, Aprobada, Rechazada, Cancelada)
4. La trabajadora puede filtrar por estado, tipo de ausencia o ano
5. La trabajadora toca una ausencia para ver su detalle completo, incluyendo comentarios de la coordinadora si los hay

Estado de exito: La trabajadora puede localizar cualquier solicitud de ausencia y conocer su estado actual y los comentarios de coordinacion.

Flujos alternativos:
- Si no hay ausencias registradas -> se muestra un estado vacio con indicacion de como solicitar la primera ausencia

### Journey 3: Consultar saldos de vacaciones
Actor: Trabajadora SAD | Objetivo: Conocer cuantos dias de vacaciones tiene disponibles

1. La trabajadora accede a la seccion "Mis Ausencias"
2. En la zona de contadores, la trabajadora ve los contadores de vacaciones: asignacion anual total, dias utilizados, dias pendientes de aprobacion y dias disponibles
3. Tambien se muestran contadores para otros tipos de ausencia segun aplique

Estado de exito: La trabajadora conoce con exactitud su saldo de vacaciones y puede tomar decisiones informadas antes de solicitar una ausencia.

> **Nota**: El metodo de computo de vacaciones (dias naturales vs dias laborables) queda pendiente de confirmacion con el cliente (ver Items Pendientes [P-001]).

### Journey 4: Cancelar una solicitud pendiente
Actor: Trabajadora SAD | Objetivo: Retirar una solicitud de ausencia antes de que sea procesada

1. La trabajadora accede al detalle de una ausencia en estado "Pendiente"
2. La trabajadora pulsa "Cancelar solicitud"
3. La aplicacion muestra un dialogo de confirmacion
4. La trabajadora confirma la cancelacion
5. La solicitud cambia a estado "Cancelada"

Estado de exito: La solicitud pasa a estado "Cancelada" y deja de estar pendiente de aprobacion. El saldo de vacaciones se actualiza si aplica.

Flujos alternativos:
- Si la solicitud ya no esta en estado "Pendiente" (fue aprobada o rechazada entre tanto) -> se muestra un mensaje indicando que el estado ha cambiado y no es posible cancelar

---

## Resultados y Exito

La feature se considera completada cuando:
- La trabajadora SAD puede solicitar ausencias de cualquier tipo con toda la informacion requerida
- Las solicitudes quedan registradas y la trabajadora recibe confirmacion
- El historial muestra todas las ausencias con filtros funcionales y acceso al detalle con comentarios de coordinacion
- Los contadores de vacaciones reflejan la situacion real de la trabajadora (asignacion, utilizados, pendientes, disponibles)
- La trabajadora puede cancelar solicitudes pendientes antes de su aprobacion
- Se advierte al solicitar ausencias que coinciden con servicios asignados
- Se exige certificado medico para bajas medicas de mas de 3 dias

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Tipos de ausencia disponibles**: Vacaciones, Permiso personal, Baja medica, Baja voluntaria, Asuntos propios, Otros. La lista es fija y se presenta al crear la solicitud.

2. **Seleccion de fechas**: Se selecciona fecha de inicio y fecha de fin. Para ambas existe la opcion de marcar "medio dia" (la ausencia comienza o termina a mitad de jornada).

3. **Motivo obligatorio**: El campo de motivo/descripcion es obligatorio para algunos tipos de ausencia. La configuracion de que tipos requieren motivo se gestiona desde backoffice.

4. **Certificado medico obligatorio**: Para ausencias de tipo "Baja medica" con duracion superior a 3 dias, es obligatorio adjuntar un certificado medico. Sin el adjunto, la solicitud no puede enviarse.

5. **Saldo de vacaciones visible**: Antes de enviar una solicitud de tipo "Vacaciones", se muestra el saldo disponible actual para que la trabajadora tome una decision informada. El saldo se muestra aunque no sea del tipo "Vacaciones" en la zona de contadores del historial.

6. **Advertencia de conflicto con servicios**: Si las fechas solicitadas coinciden con servicios asignados a la trabajadora, se muestra una advertencia visible. La advertencia es informativa y no bloquea el envio de la solicitud.

7. **Estados de una solicitud**: Pendiente (recien enviada, esperando aprobacion), Aprobada (aceptada por coordinacion), Rechazada (denegada por coordinacion), Cancelada (retirada por la trabajadora). Las transiciones de estado son: Pendiente -> Aprobada, Pendiente -> Rechazada, Pendiente -> Cancelada. Una vez en estado final (Aprobada, Rechazada, Cancelada), la solicitud no puede cambiar de estado desde la app.

8. **Cancelacion**: Solo se pueden cancelar solicitudes en estado "Pendiente". Si el estado cambia entre la consulta y la accion de cancelar, se muestra un mensaje informativo.

9. **Orden del historial**: Las ausencias se listan en orden cronologico inverso (mas recientes primero).

10. **Filtros del historial**: Se puede filtrar por estado, por tipo de ausencia y por ano. Los filtros son combinables.

11. **Contadores de vacaciones**: Se muestran en el historial de ausencias: asignacion anual total, dias utilizados, dias pendientes de aprobacion, dias disponibles. Se muestran contadores adicionales para otros tipos de ausencia segun aplique (la configuracion de que tipos muestran contadores se gestiona desde backoffice).

12. **Detalle de ausencia**: Al tocar una ausencia del listado, se abre el detalle con toda la informacion (tipo, fechas, dias, estado, motivo, adjuntos) y los comentarios de la coordinadora si los hay.

13. **Notificacion push de confirmacion**: Al enviar una solicitud, la trabajadora recibe una notificacion push de confirmacion.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home SAD | Pulsar acceso directo "Solicitar Ausencia" | Formulario de nueva solicitud de ausencia |
| Home SAD | Pulsar acceso directo "Mis Ausencias" | Historial de ausencias |
| Pantalla de fichaje | Pulsar "Solicitar ausencia" | Formulario de nueva solicitud de ausencia |
| Historial de ausencias | Pulsar una ausencia del listado | Detalle de la ausencia |
| Historial de ausencias | Pulsar "Solicitar ausencia" | Formulario de nueva solicitud de ausencia |
| Detalle de ausencia | Pulsar "Cancelar solicitud" (si estado Pendiente) | Dialogo de confirmacion de cancelacion |

---

## Criterios de Aceptacion

### CA-001: Seleccion de tipo de ausencia <- HU-001
GIVEN la trabajadora SAD accede al formulario de solicitud de ausencia
WHEN visualiza el selector de tipo de ausencia
THEN se muestran las opciones: Vacaciones, Permiso personal, Baja medica, Baja voluntaria, Asuntos propios, Otros

### CA-002: Seleccion de rango de fechas con medio dia <- HU-001
GIVEN la trabajadora esta completando el formulario de solicitud de ausencia
WHEN selecciona la fecha de inicio y la fecha de fin
THEN puede marcar la opcion de "medio dia" tanto para la fecha de inicio como para la fecha de fin

### CA-003: Motivo obligatorio segun tipo <- HU-001
GIVEN la trabajadora ha seleccionado un tipo de ausencia que requiere motivo obligatorio
WHEN intenta enviar la solicitud sin completar el campo de motivo
THEN la aplicacion impide el envio y senala el campo de motivo como obligatorio

### CA-004: Certificado medico obligatorio para baja medica larga <- HU-001
GIVEN la trabajadora ha seleccionado tipo "Baja medica" y la duracion supera los 3 dias
WHEN intenta enviar la solicitud sin adjuntar un certificado medico
THEN la aplicacion impide el envio e indica que el certificado medico es obligatorio para bajas medicas de mas de 3 dias

### CA-005: Visualizacion del saldo de vacaciones antes de enviar <- HU-001, HU-003
GIVEN la trabajadora esta completando una solicitud de ausencia de tipo "Vacaciones"
WHEN visualiza el formulario antes de enviar
THEN se muestra su saldo de vacaciones disponible actual (dias restantes)

### CA-006: Advertencia de conflicto con servicios asignados <- HU-001
GIVEN la trabajadora ha seleccionado fechas para su solicitud de ausencia
WHEN las fechas seleccionadas coinciden con al menos un servicio asignado
THEN se muestra una advertencia visible indicando el conflicto, sin bloquear el envio de la solicitud

### CA-007: Envio exitoso y confirmacion <- HU-001
GIVEN la trabajadora ha completado todos los campos obligatorios del formulario de ausencia
WHEN pulsa "Enviar solicitud"
THEN la solicitud se registra en estado "Pendiente", se muestra una confirmacion visual en pantalla y la trabajadora recibe una notificacion push de confirmacion

### CA-008: Listado de ausencias en orden cronologico inverso <- HU-002
GIVEN la trabajadora SAD accede al historial de ausencias
WHEN se carga el listado
THEN las ausencias se muestran en orden cronologico inverso (mas recientes primero) con tipo, fechas, recuento de dias y estado visible para cada una

### CA-009: Estados de ausencia visibles <- HU-002
GIVEN la trabajadora consulta el historial de ausencias
WHEN visualiza una solicitud
THEN el estado se muestra como uno de: Pendiente, Aprobada, Rechazada o Cancelada

### CA-010: Filtros del historial de ausencias <- HU-002
GIVEN la trabajadora esta en el historial de ausencias
WHEN aplica filtros por estado, tipo de ausencia o ano
THEN el listado se actualiza mostrando solo las ausencias que cumplen los criterios seleccionados, y los filtros son combinables entre si

### CA-011: Detalle de ausencia con comentarios de coordinadora <- HU-002
GIVEN la trabajadora toca una ausencia del listado
WHEN se abre el detalle
THEN se muestra toda la informacion de la solicitud (tipo, fechas, dias, estado, motivo, adjuntos) y los comentarios de la coordinadora si los hay

### CA-012: Contadores de vacaciones <- HU-003 [INCOMPLETO]
GIVEN la trabajadora SAD accede al historial de ausencias
WHEN visualiza la zona de contadores
THEN se muestran los contadores de vacaciones: asignacion anual total, dias utilizados, dias pendientes de aprobacion y dias disponibles

> **Nota**: El computo de dias (naturales vs laborables) queda pendiente de definicion (ver [P-001]).

### CA-013: Contadores por tipo de ausencia <- HU-003 [INCOMPLETO]
GIVEN la trabajadora SAD accede al historial de ausencias
WHEN visualiza la zona de contadores
THEN se muestran contadores adicionales para otros tipos de ausencia segun la configuracion establecida desde backoffice

> **Nota**: El computo de dias para contadores depende de la resolucion de [P-001].

### CA-014: Cancelar solicitud pendiente <- HU-004
GIVEN la trabajadora esta en el detalle de una ausencia en estado "Pendiente"
WHEN pulsa "Cancelar solicitud" y confirma en el dialogo de confirmacion
THEN la solicitud cambia a estado "Cancelada" y deja de estar pendiente de aprobacion

### CA-015: No permitir cancelar solicitudes ya procesadas <- HU-004
GIVEN la trabajadora esta en el detalle de una ausencia en estado "Aprobada", "Rechazada" o "Cancelada"
WHEN visualiza las opciones disponibles
THEN no se muestra la opcion de cancelar la solicitud

### CA-016: Cambio de estado concurrente al cancelar <- HU-004
GIVEN la trabajadora intenta cancelar una solicitud que estaba en estado "Pendiente"
WHEN el estado de la solicitud ha cambiado a "Aprobada" o "Rechazada" entre la consulta y la accion de cancelar
THEN la aplicacion muestra un mensaje indicando que el estado ha cambiado y que no es posible cancelar la solicitud

---

## Checklist de Validacion

- [x] Actores identificados (Trabajadora SAD)
- [x] Flujos principales descritos paso a paso (solicitar, historial, contadores, cancelar)
- [x] Estados de exito definidos para cada journey
- [x] Edge cases documentados (cancelacion concurrente, certificado faltante, conflicto con servicios)
- [x] Estados de error definidos (campos obligatorios, certificado faltante, cambio de estado concurrente)
- [ ] Ambiguedades resueltas — Pendiente: [P-001] computo de vacaciones (dias naturales vs laborables)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- **Aprobacion o rechazo de solicitudes**: la gestion de aprobacion/rechazo se realiza exclusivamente desde backoffice, no desde la app de la trabajadora.
- **Edicion de solicitudes enviadas**: una vez enviada, la solicitud no se puede modificar; solo se puede cancelar si esta en estado "Pendiente".
- **Gestion de reglas de aprobacion automatica**: las reglas de aprobacion (si las hay) se configuran en backoffice.
- **Notificaciones de cambio de estado de la solicitud**: la recepcion de notificaciones push al cambiar el estado de la solicitud es responsabilidad de la feature de notificaciones push (F-012: push-notifications).
- **Configuracion de tipos de ausencia**: la lista de tipos y sus reglas (motivo obligatorio, contadores) se gestiona desde backoffice.

---

## Items Pendientes

> Este spec tiene gaps **criticos** sin resolver. Las HUs afectadas estan marcadas `[INCOMPLETO]` y `/wf-prepare-plan` quedara bloqueado hasta que se resuelvan.
> Para resolverlos: edita este spec respondiendo los gaps, luego ejecuta `/wf-spec-validate <path>_spec.md`.

### [P-001][CRITICO] Computo de vacaciones: dias naturales o laborables
- **Afecta**: [HU-003]
- **Pregunta**: Las vacaciones se computan por dias naturales o por dias laborables? Esta decision afecta al calculo del saldo de vacaciones, los contadores de dias disponibles y la visualizacion de dias al solicitar ausencias.
- **Respuesta**: [CRITICO]_(pendiente)_

---

## Asunciones Aplicadas

- **[A-001]**: Se asume que la opcion de medio dia aplica tanto a la fecha de inicio como a la fecha de fin de la ausencia, ya que el PRD menciona "Opciones de medio dia para fechas de inicio/final" (RF-8.1 CA3) sin especificar restricciones adicionales.
- **[A-002]**: Se asume que el campo de motivo/descripcion es obligatorio solo para algunos tipos de ausencia (segun configuracion de backoffice), ya que el PRD dice "obligatorio para algunos tipos" (RF-8.1 CA4) sin especificar cuales. Se documenta la regla generica y se delega la configuracion concreta a backoffice.
- **[A-003]**: Se asume que la advertencia de conflicto con servicios asignados es informativa y no bloquea el envio, ya que el PRD (RF-8.1 CA7) usa el termino "Advertencia" sin mencionar bloqueo.
- **[A-004]**: Se asume que los contadores por tipo de ausencia distintos de vacaciones son configurables desde backoffice, ya que el PRD (RF-8.2 CA9) dice "otros tipos segun aplique" sin definir cuales.
