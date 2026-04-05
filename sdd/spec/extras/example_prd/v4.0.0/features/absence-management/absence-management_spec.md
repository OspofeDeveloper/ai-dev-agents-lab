# Spec: Absence Management
> Versión: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-010 via prd-hogar-sad_discovery.md)
> Feature ID: F-010
> Spec monolítico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Profesional de servicios de atención domiciliaria (Felizvita) con contrato activo | Solicitar ausencias y permisos, consultar historial de ausencias, cancelar solicitudes pendientes, ver saldos por tipo de ausencia |

---

## Historias de Usuario

### HU-001: Solicitar ausencia
Como trabajadora SAD
quiero solicitar un período de ausencia (vacaciones, baja médica, permiso personal u otros)
para que coordinación pueda gestionarlo y aprobarlo, asegurando que mis servicios quedan cubiertos.

### HU-002: Adjuntar documentación justificativa
Como trabajadora SAD
quiero poder adjuntar un certificado médico u otro documento justificativo al solicitar una ausencia
para que coordinación disponga de la documentación necesaria para tramitar y aprobar mi solicitud.

### HU-003: Consultar saldo de ausencias antes de solicitar
Como trabajadora SAD
quiero ver mi saldo disponible de vacaciones y otros tipos de ausencia antes de enviar una solicitud
para que pueda tomar una decisión informada y no solicitar más días de los que tengo disponibles.

### HU-004: Gestionar el historial de ausencias
Como trabajadora SAD
quiero ver todas mis solicitudes de ausencia con su estado actual y detalle
para que pueda hacer seguimiento del estado de mis solicitudes y consultar comentarios de coordinación.

### HU-005: Cancelar una solicitud de ausencia pendiente
Como trabajadora SAD
quiero cancelar una solicitud de ausencia que aún no ha sido aprobada
para que pueda rectificar errores o cambios de planes antes de que coordinación la procese.

### HU-006: Filtrar y buscar ausencias en el historial
Como trabajadora SAD
quiero filtrar mi historial de ausencias por estado, tipo y año
para que pueda encontrar rápidamente la información que necesito sin revisar todas las entradas.

---

## Recorridos de Usuario

### Journey 1: Solicitar una ausencia
Actor: Trabajadora SAD | Objetivo: Enviar una solicitud de ausencia para aprobación

1. La trabajadora accede al módulo de Mis Ausencias desde el menú principal o el acceso directo del home.
2. Pulsa el botón "Solicitar ausencia".
3. Selecciona el tipo de ausencia de la lista predefinida: Vacaciones, Permiso personal, Baja médica, Baja voluntaria, Asuntos propios, Otros.
4. Selecciona la fecha de inicio y la fecha de fin del período de ausencia.
5. Si desea solicitar medio día para la fecha de inicio o de fin, activa la opción correspondiente.
6. Introduce el motivo o descripción (obligatorio para los tipos que lo requieren; ver Instrucciones Inambiguas).
7. Si el tipo de ausencia es "Baja médica" y la duración supera 3 días, adjunta el certificado médico (obligatorio).
8. El sistema muestra el saldo de vacaciones disponible si el tipo seleccionado es "Vacaciones".
9. Si las fechas seleccionadas entran en conflicto con servicios asignados, el sistema muestra una advertencia (no bloqueante).
10. La trabajadora pulsa "Enviar solicitud".
11. La solicitud queda registrada en estado "Pendiente" y aparece en el historial.

Estado de éxito: La solicitud se crea correctamente en estado "Pendiente", aparece en el historial y la trabajadora recibe confirmación visual inmediata.
Flujos alternativos: Si faltan campos obligatorios → el formulario marca los campos en error y no permite enviar. Si el certificado médico es obligatorio y no se adjunta → el sistema bloquea el envío con mensaje explicativo.

### Journey 2: Cancelar una solicitud de ausencia pendiente
Actor: Trabajadora SAD | Objetivo: Cancelar una solicitud que todavía no ha sido procesada

1. La trabajadora accede al módulo de Mis Ausencias.
2. Localiza en el historial la solicitud con estado "Pendiente".
3. Abre el detalle de la solicitud.
4. Pulsa "Cancelar solicitud".
5. El sistema solicita confirmación.
6. Tras confirmar, la solicitud cambia a estado "Cancelada".

Estado de éxito: La solicitud pasa al estado "Cancelada" y el cambio queda reflejado inmediatamente en el historial.
Flujos alternativos: Si la solicitud ya no está en estado "Pendiente" en el momento de confirmar (p. ej., fue aprobada justo antes) → el sistema informa que la solicitud ya no puede cancelarse y actualiza el estado en pantalla.

### Journey 3: Consultar historial y detalle de una ausencia
Actor: Trabajadora SAD | Objetivo: Revisar el estado de sus solicitudes y leer comentarios de coordinación

1. La trabajadora accede al módulo de Mis Ausencias.
2. Ve el listado de ausencias en orden cronológico inverso con tipo, fechas, recuento de días y estado.
3. Aplica filtros opcionales por estado, tipo de ausencia o año.
4. Consulta los contadores de saldo por tipo de ausencia en la cabecera del listado.
5. Toca una entrada para abrir el detalle.
6. En el detalle ve todos los campos de la solicitud y los comentarios de coordinación.

Estado de éxito: La trabajadora puede ver el estado actual de sus ausencias y los comentarios de coordinación sin necesidad de contactar con el equipo.
Flujos alternativos: Si no hay ausencias que coincidan con los filtros activos → se muestra un estado vacío informativo sin error.

### Journey 4: Recibir notificación de cambio de estado
Actor: Trabajadora SAD | Objetivo: Conocer la resolución de su solicitud en tiempo real

1. Coordinación aprueba, rechaza o gestiona la solicitud desde backoffice.
2. La trabajadora recibe una notificación push informando del cambio de estado.
3. Al tocar la notificación, la app abre directamente el detalle de la ausencia afectada.
4. La trabajadora ve el nuevo estado y, si hay comentarios de coordinación, los lee en el detalle.

Estado de éxito: La trabajadora accede directamente al detalle de la ausencia desde la notificación y conoce el resultado de su solicitud sin pasos intermedios.
Flujos alternativos: Si la app está en primer plano cuando llega la notificación → se muestra como alerta in-app con opción de navegar al detalle.

---

## Resultados y Éxito

La feature de gestión de ausencias se considera completa cuando:

- Una trabajadora SAD puede solicitar cualquier tipo de ausencia definido con fechas, motivo y adjuntos opcionales u obligatorios según el tipo.
- El saldo de vacaciones disponible es visible antes de enviar una solicitud de tipo "Vacaciones".
- El sistema advierte de conflictos con servicios asignados pero no bloquea el envío.
- El historial muestra todas las solicitudes con estado, fechas, recuento de días y comentarios de coordinación.
- Los filtros por estado, tipo y año funcionan correctamente y combinables entre sí.
- Los contadores de saldo por tipo de ausencia (asignado, utilizado, pendiente, disponible) son visibles.
- Las solicitudes en estado "Pendiente" pueden cancelarse con confirmación previa.
- Las notificaciones push de cambio de estado llevan al detalle correcto de la ausencia mediante deeplink.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Tipos de ausencia disponibles:**
Los tipos que puede seleccionar la trabajadora son exactamente: Vacaciones, Permiso personal, Baja médica, Baja voluntaria, Asuntos propios, Otros. No se pueden crear tipos personalizados desde la app.

**Motivo obligatorio por tipo:**
El campo "motivo/descripción" es obligatorio para los siguientes tipos: Baja médica, Baja voluntaria, Asuntos propios, Otros. Para Vacaciones y Permiso personal el campo es opcional.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-002]. Responde en el spec editándolo directamente y ejecuta `/wf-spec-delta resolve` para completar.

**Adjunto obligatorio — certificado médico:**
Para el tipo "Baja médica" con una duración superior a 3 días naturales, adjuntar el certificado médico es obligatorio. Para bajas médicas de 3 días o menos, el certificado es opcional. Para el resto de tipos, los adjuntos son siempre opcionales.

**Cómputo de días:**
Los días de ausencia se computan en la unidad que define el tipo: para Vacaciones, el cómputo es en días (ver gap P-001 pendiente de resolución).

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001]. Responde en el spec editándolo directamente y ejecuta `/wf-spec-delta resolve` para completar.

**Opción de medio día:**
La opción de medio día es aplicable de forma independiente a la fecha de inicio y a la fecha de fin. Se puede activar en una, en ambas, o en ninguna de las dos fechas.

**Conflicto con servicios asignados:**
Cuando las fechas de la ausencia solicitada coinciden con servicios asignados, el sistema muestra una advertencia visible antes de enviar. La advertencia no bloquea el envío: la trabajadora puede continuar y enviar igualmente.

**Saldo de vacaciones:**
El saldo se muestra únicamente cuando el tipo seleccionado es "Vacaciones". Los contadores visibles son: días asignados en el año, días utilizados (aprobados), días pendientes de aprobación, y días disponibles. Para el resto de tipos de ausencia, se muestra el contador específico del tipo si está disponible, o se omite si no aplica.

**Cancelación de solicitudes:**
Solo las solicitudes en estado "Pendiente" pueden cancelarse desde la app. Las solicitudes en cualquier otro estado (Aprobada, Rechazada, Cancelada) no muestran la opción de cancelar.

**Estados posibles de una solicitud de ausencia:**
Pendiente, Aprobada, Rechazada, Cancelada. Estos estados son mutuamente excluyentes y el flujo de transición entre ellos es gestionado por coordinación, salvo la cancelación que puede ejecutar la propia trabajadora desde estado "Pendiente".

**Ordenación del historial:**
Las ausencias se listan en orden cronológico inverso (la más reciente primero). Este orden no es modificable por el usuario.

**Combinación de filtros:**
Los filtros por estado, tipo y año son combinables entre sí. Cuando no hay entradas que coincidan con los filtros activos, se muestra un estado vacío con mensaje informativo; no se muestra un error.

### Destinos de navegación

| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Home (acceso directo "Solicitar Ausencia") | Tocar acceso directo | Formulario de nueva solicitud de ausencia |
| Home (acceso directo "Mis Ausencias") | Tocar acceso directo | Listado del historial de ausencias |
| Historial de ausencias | Tocar una entrada de ausencia | Detalle de la solicitud de ausencia |
| Detalle de ausencia (estado Pendiente) | Tocar "Cancelar solicitud" | Diálogo de confirmación de cancelación; tras confirmar → vuelve al historial con estado actualizado |
| Notificación push de cambio de estado | Tocar la notificación | Detalle de la solicitud de ausencia afectada (deeplink directo) |
| Notificación push (app en primer plano) | Recibir la notificación | Alerta in-app con opción "Ver detalle" → detalle de la solicitud |
| Formulario de solicitud (campos incompletos) | Intentar enviar | Permanece en el formulario; campos en error marcados visualmente |
| Formulario de solicitud (baja médica >3 días sin certificado) | Intentar enviar | Permanece en el formulario; mensaje explicativo sobre certificado obligatorio |

---

## Criterios de Aceptación

### CA-001: Selección de tipo de ausencia ← HU-001
GIVEN la trabajadora SAD está en el formulario de nueva solicitud de ausencia
WHEN visualiza el selector de tipo de ausencia
THEN el sistema muestra exactamente los siguientes tipos: Vacaciones, Permiso personal, Baja médica, Baja voluntaria, Asuntos propios, Otros; sin posibilidad de introducir tipos personalizados

### CA-002: Selección de rango de fechas ← HU-001
GIVEN la trabajadora ha seleccionado un tipo de ausencia
WHEN selecciona la fecha de inicio y la fecha de fin
THEN el sistema valida que la fecha de fin es igual o posterior a la fecha de inicio; si no lo es, muestra un error y no permite continuar

### CA-003: Opción de medio día en fechas extremas ← HU-001
GIVEN la trabajadora ha seleccionado un rango de fechas
WHEN activa la opción "medio día" para la fecha de inicio o la fecha de fin (de forma independiente)
THEN el sistema registra esa selección y la refleja en el resumen de días calculados antes de enviar

### CA-004: Motivo obligatorio para tipos que lo requieren ← HU-001
GIVEN la trabajadora ha seleccionado un tipo de ausencia que requiere motivo (Baja médica, Baja voluntaria, Asuntos propios, Otros)
WHEN intenta enviar la solicitud sin haber rellenado el campo de motivo
THEN el sistema marca el campo como obligatorio, muestra un mensaje de error y bloquea el envío hasta que se complete

### CA-005: Certificado médico obligatorio para baja larga ← HU-002
GIVEN la trabajadora ha seleccionado "Baja médica" y las fechas abarcan más de 3 días
WHEN intenta enviar sin adjuntar el certificado médico
THEN el sistema muestra un mensaje indicando que el certificado es obligatorio para bajas médicas de más de 3 días y bloquea el envío

### CA-006: Certificado médico opcional para baja corta ← HU-002
GIVEN la trabajadora ha seleccionado "Baja médica" y las fechas abarcan 3 días o menos
WHEN visualiza el formulario
THEN el campo de adjunto de certificado está disponible pero no marcado como obligatorio; el envío sin adjunto es válido

### CA-007: Saldo de vacaciones visible al seleccionar ese tipo ← HU-003
GIVEN la trabajadora ha seleccionado "Vacaciones" como tipo de ausencia
WHEN visualiza el formulario de solicitud
THEN el sistema muestra el saldo de vacaciones actual con los siguientes contadores: días asignados en el año, días utilizados, días pendientes de aprobación y días disponibles

### CA-008: Saldo no visible para tipos distintos de Vacaciones ← HU-003
GIVEN la trabajadora ha seleccionado un tipo de ausencia diferente a "Vacaciones"
WHEN visualiza el formulario de solicitud
THEN el sistema no muestra el contador de saldo de vacaciones; si el tipo tiene contador propio disponible, lo muestra; si no aplica, el área de saldo queda oculta

### CA-009: Advertencia de conflicto con servicios ← HU-001
GIVEN la trabajadora ha seleccionado fechas que coinciden con al menos un servicio asignado
WHEN visualiza el formulario antes de enviar
THEN el sistema muestra una advertencia informando del conflicto con los servicios afectados; la advertencia no bloquea el envío

### CA-010: Sin conflicto con servicios ← HU-001
GIVEN la trabajadora ha seleccionado fechas que no coinciden con ningún servicio asignado
WHEN visualiza el formulario
THEN el sistema no muestra ninguna advertencia de conflicto

### CA-011: Envío exitoso de la solicitud ← HU-001
GIVEN todos los campos obligatorios están completos y el adjunto es válido si corresponde
WHEN la trabajadora pulsa "Enviar solicitud"
THEN el sistema registra la solicitud en estado "Pendiente", muestra confirmación visual inmediata y la solicitud aparece en el historial en primer lugar (cronológico inverso)

### CA-012: Listado de ausencias en orden cronológico inverso ← HU-004
GIVEN la trabajadora accede al historial de Mis Ausencias
WHEN no ha aplicado ningún filtro
THEN las solicitudes se muestran en orden cronológico inverso (la más reciente primero), con tipo, fechas, recuento de días y estado visible en cada tarjeta

### CA-013: Contadores de saldo por tipo en historial ← HU-004
GIVEN la trabajadora está en el listado de Mis Ausencias
WHEN visualiza la cabecera o sección de saldos
THEN el sistema muestra los contadores por tipo de ausencia disponibles (asignado, utilizado, pendiente, disponible) para los tipos que tienen contador activo

### CA-014: Detalle de ausencia con comentarios de coordinación ← HU-004
GIVEN la trabajadora toca una entrada en el historial de ausencias
WHEN se abre el detalle
THEN el sistema muestra todos los campos de la solicitud (tipo, fechas, motivo, adjunto si lo hubo, estado) y los comentarios de coordinación si existen

### CA-015: Cancelar solicitud pendiente ← HU-005
GIVEN la trabajadora está en el detalle de una solicitud en estado "Pendiente"
WHEN pulsa "Cancelar solicitud" y confirma en el diálogo de confirmación
THEN la solicitud cambia al estado "Cancelada" y el cambio se refleja inmediatamente en el historial y en el detalle

### CA-016: Cancelación no disponible para estados no cancelables ← HU-005
GIVEN la trabajadora está en el detalle de una solicitud en estado "Aprobada", "Rechazada" o "Cancelada"
WHEN visualiza el detalle
THEN el sistema no muestra la opción de cancelar

### CA-017: Filtro por estado ← HU-006
GIVEN la trabajadora está en el historial de Mis Ausencias
WHEN aplica el filtro por estado (uno o varios valores: Pendiente, Aprobada, Rechazada, Cancelada)
THEN el listado muestra únicamente las ausencias que coinciden con los estados seleccionados; si no hay coincidencias, muestra estado vacío informativo

### CA-018: Filtro por tipo de ausencia ← HU-006
GIVEN la trabajadora está en el historial de Mis Ausencias
WHEN aplica el filtro por tipo de ausencia
THEN el listado muestra únicamente las ausencias del tipo seleccionado; si no hay coincidencias, muestra estado vacío informativo

### CA-019: Filtro por año ← HU-006
GIVEN la trabajadora está en el historial de Mis Ausencias
WHEN aplica el filtro por año
THEN el listado muestra únicamente las ausencias cuya fecha de inicio corresponde al año seleccionado; si no hay coincidencias, muestra estado vacío informativo

### CA-020: Combinación de filtros ← HU-006
GIVEN la trabajadora ha activado filtros de más de un tipo simultáneamente (p. ej., estado + año)
WHEN visualiza el listado
THEN el sistema aplica todos los filtros activos de forma conjunta (intersección); el estado vacío informa de que no hay resultados para los filtros aplicados

### CA-021: Notificación push de cambio de estado ← HU-004
GIVEN coordinación ha cambiado el estado de una solicitud de ausencia de la trabajadora
WHEN la trabajadora recibe la notificación push y la toca
THEN la app abre directamente el detalle de la solicitud de ausencia afectada (deeplink)

### CA-022: Notificación push en primer plano ← HU-004
GIVEN la app está en primer plano cuando llega una notificación de cambio de estado de ausencia
WHEN el sistema detecta la notificación
THEN se muestra como alerta in-app con opción de navegar directamente al detalle de la ausencia

---

## Checklist de Validación

- [x] Actores identificados (Trabajadora SAD)
- [x] Flujos principales descritos paso a paso (solicitar, cancelar, consultar historial, recibir notificación)
- [x] Estados de éxito definidos para cada Journey
- [x] Edge cases documentados (baja médica sin certificado, fechas con conflicto, solicitud ya procesada al intentar cancelar, filtros sin resultados)
- [x] Estados de error definidos (campos obligatorios vacíos, certificado obligatorio ausente, cancelación no disponible)
- [x] Ambigüedades resueltas en Instrucciones Inambiguas (excepto las documentadas en gaps críticos P-001 y P-002)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes

---

## Fuera de Alcance

- **Aprobación o rechazo de ausencias desde la app**: la gestión de solicitudes por parte de coordinación se realiza desde el backoffice; la app es solo el canal de solicitud y seguimiento para la trabajadora.
- **Creación de tipos de ausencia personalizados**: los tipos disponibles son los definidos en el sistema; la trabajadora no puede añadir tipos propios.
- **Edición de una solicitud enviada**: una vez enviada, la solicitud no es editable desde la app; si la trabajadora necesita corregirla, debe cancelarla y crear una nueva.
- **Cancelación de solicitudes aprobadas, rechazadas o ya canceladas**: solo las solicitudes en estado "Pendiente" pueden cancelarse desde la app.
- **Gestión de saldo de ausencias (asignación anual)**: el saldo es asignado desde backoffice; la app solo lo consulta.
- **Ausencias de trabajadoras del perfil Hogar (CUIDEO)**: este módulo aplica exclusivamente al perfil SAD (Felizvita).
- **Historial de solicitudes de ausencia anterior al MVP**: el historial muestra las solicitudes gestionadas en el sistema; no se importan registros históricos anteriores al lanzamiento.

---

## Items Pendientes

> Este spec tiene gaps **críticos** sin resolver. Las HUs afectadas están marcadas `[INCOMPLETO]` y `/wf-prepare-plan` quedará bloqueado hasta que se resuelvan.
> Para resolverlos: edita este spec respondiendo los gaps, luego ejecuta `/wf-spec-validate features/absence-management/absence-management_spec.md`.

### [P-001][CRÍTICO] Cómputo de días de ausencia: ¿naturales o hábiles?
- **Afecta**: HU-001, HU-003, CA-002, CA-003, CA-007
- **Pregunta**: El PRD indica explícitamente que las vacaciones se computan por "días naturales (pendiente de confirmar con cliente/legal)". ¿Se confirma que el cómputo para Vacaciones es por días naturales? ¿Y para el resto de tipos de ausencia (Permiso personal, Baja médica, etc.) también se usan días naturales, o difieren?
- **Respuesta**: [CRÍTICO]_(pendiente)_

### [P-002][CRÍTICO] ¿Para qué tipos de ausencia es obligatorio el motivo/descripción?
- **Afecta**: HU-001, CA-004
- **Pregunta**: El PRD indica que el motivo es "obligatorio para algunos tipos" sin especificar cuáles. ¿Cuáles son los tipos que requieren motivo obligatorio? (El spec asume: Baja médica, Baja voluntaria, Asuntos propios, Otros — ¿es correcto?)
- **Respuesta**: [CRÍTICO]_(pendiente)_

---

## Asunciones Aplicadas

- **[A-001]**: La opción de medio día es independiente para la fecha de inicio y la fecha de fin: se puede activar en una, en ambas, o en ninguna. El PRD no especifica si son mutuamente excluyentes; se asume la opción más flexible (independientes) como comportamiento más conservador funcionalmente.
- **[A-002]**: Los adjuntos para tipos de ausencia distintos de "Baja médica" son siempre opcionales. El PRD menciona "documentación justificativa" de forma genérica pero solo especifica obligatoriedad para baja médica >3 días. Se asume que el campo de adjunto está disponible para todos los tipos pero solo es obligatorio en el caso descrito.
- **[A-003]**: Solo las solicitudes en estado "Pendiente" pueden cancelarse. El PRD menciona cancelar "solicitudes pendientes" pero no especifica si solicitudes aprobadas también pueden cancelarse desde la app. Se asume la interpretación más restrictiva: solo "Pendiente" es cancelable desde la app.
- **[A-004]**: La notificación push de confirmación de solicitud enviada (CA9 del PRD, RF-8.1) se gestiona desde el módulo de push-notifications (F-009); este spec solo especifica el comportamiento funcional resultante (estado "Pendiente" visible en historial). La entrega del push en sí es responsabilidad de F-009.
