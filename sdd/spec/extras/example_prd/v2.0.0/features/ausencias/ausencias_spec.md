# Spec: Ausencias
> Version: 1.0 | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md
> Feature ID: F-008

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora del Servicio de Asistencia Social | Solicitar ausencias, consultar historial y saldo de vacaciones, cancelar solicitudes pendientes |

---

## Historias de Usuario

### HU-001: Solicitar ausencia
Como trabajadora SAD
quiero solicitar tiempo libre (vacaciones, baja medica, permisos)
para que la coordinacion gestione mi ausencia.

### HU-002: Consultar historial y saldo
Como trabajadora SAD
quiero ver mi historial de ausencias y mi saldo de vacaciones
para que sepa cuantos dias tengo disponibles y el estado de mis solicitudes.

---

## Recorridos de Usuario

### Journey 1: Solicitar una ausencia
Actor: Trabajadora SAD | Objetivo: Solicitar tiempo libre
1. La trabajadora accede a "Solicitar Ausencia" desde el home o el menu.
2. Selecciona tipo de ausencia: Vacaciones, Permiso personal, Baja medica, Baja voluntaria, Asuntos propios, Otros.
3. Selecciona rango de fechas (fecha de inicio, fecha final) con opciones de medio dia para fechas de inicio/final.
4. Introduce motivo/descripcion (obligatorio para algunos tipos).
5. Si es baja medica de mas de 3 dias, adjunta certificado medico (obligatorio).
6. Ve el saldo de vacaciones disponible antes de enviar.
7. Si las fechas solicitadas entran en conflicto con servicios asignados, recibe advertencia.
8. Envia la solicitud para aprobacion.
9. Recibe notificacion push de confirmacion.

Estado de exito: La solicitud queda registrada y enviada para aprobacion.

### Journey 2: Consultar historial y saldo
Actor: Trabajadora SAD | Objetivo: Ver sus ausencias y saldo
1. La trabajadora accede a "Mis Ausencias".
2. Ve contadores por tipo de ausencia (vacaciones: asignacion anual, dias utilizados, dias pendientes de aprobacion, dias disponibles; otros tipos segun aplique).
3. Ve la lista de ausencias en orden cronologico inverso con tipo, fechas, recuento de dias y estado.
4. Puede filtrar por estado, tipo de ausencia y ano.
5. Toca una ausencia para ver detalles y comentarios de coordinadora.
6. Puede cancelar solicitudes en estado Pendiente.

Estado de exito: La trabajadora tiene visibilidad completa de su historial y saldo de ausencias.

---

## Resultados y Exito

- La trabajadora SAD puede solicitar ausencias de forma autonoma con toda la documentacion necesaria.
- Los contadores de saldo de vacaciones y otros tipos estan visibles antes de solicitar.
- El historial permite seguimiento del ciclo de vida de cada solicitud.

---

## Instrucciones Inambiguas

### Reglas de comportamiento
- Tipos de ausencia: Vacaciones, Permiso personal, Baja medica, Baja voluntaria, Asuntos propios, Otros.
- El motivo/descripcion es obligatorio para algunos tipos de ausencia.
- El certificado medico es obligatorio para baja medica de mas de 3 dias.
- Se muestran opciones de medio dia para las fechas de inicio y final.
- Se muestra advertencia si las fechas entran en conflicto con servicios asignados.
- Las vacaciones se computan por dias naturales (pendiente de confirmar con cliente/legal).
- Los estados de solicitud son: Pendiente, Aprobada, Rechazada, Cancelada.
- Solo se pueden cancelar solicitudes en estado Pendiente.
- Los contadores por tipo de ausencia incluyen: asignacion anual total, dias utilizados, dias pendientes de aprobacion, dias disponibles.

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home SAD | Tocar "Solicitar Ausencia" | Formulario de solicitud de ausencia |
| Home SAD | Tocar "Mis Ausencias" | Historial de ausencias |
| Pantalla fichaje | Tocar "Solicitar ausencia" | Formulario de solicitud de ausencia |
| Historial | Tocar ausencia | Detalle de la ausencia con comentarios |

---

## Criterios de Aceptacion

### CA-001: Seleccion de tipo <- HU-001
GIVEN la trabajadora SAD esta solicitando una ausencia
WHEN accede al formulario
THEN puede seleccionar tipo: Vacaciones, Permiso personal, Baja medica, Baja voluntaria, Asuntos propios, Otros.

### CA-002: Seleccion de fechas <- HU-001
GIVEN la trabajadora SAD esta solicitando una ausencia
WHEN selecciona las fechas
THEN puede elegir fecha de inicio y fecha final, con opciones de medio dia para ambas.

### CA-003: Motivo obligatorio <- HU-001
GIVEN la trabajadora SAD esta solicitando una ausencia de tipo que lo requiere
WHEN completa el formulario
THEN el campo de motivo/descripcion es obligatorio.

### CA-004: Certificado medico obligatorio <- HU-001
GIVEN la trabajadora SAD solicita baja medica de mas de 3 dias
WHEN completa el formulario
THEN debe adjuntar certificado medico obligatoriamente.

### CA-005: Saldo visible antes de enviar <- HU-001
GIVEN la trabajadora SAD esta solicitando una ausencia
WHEN revisa el formulario
THEN se muestra el saldo de vacaciones disponible.

### CA-006: Advertencia de conflicto <- HU-001
GIVEN la trabajadora SAD selecciona fechas que coinciden con servicios asignados
WHEN revisa antes de enviar
THEN se muestra una advertencia informando del conflicto.

### CA-007: Envio de solicitud <- HU-001
GIVEN la trabajadora SAD ha completado el formulario de ausencia
WHEN pulsa enviar
THEN la solicitud se envia para aprobacion.

### CA-008: Notificacion de confirmacion <- HU-001
GIVEN la trabajadora SAD ha enviado la solicitud
WHEN se registra la solicitud
THEN recibe notificacion push de confirmacion.

### CA-009: Listado de ausencias <- HU-002
GIVEN la trabajadora SAD accede a Mis Ausencias
WHEN se carga la lista
THEN se muestran las ausencias en orden cronologico inverso.

### CA-010: Info de ausencia <- HU-002
GIVEN la trabajadora SAD esta en el historial de ausencias
WHEN ve la lista
THEN cada ausencia muestra tipo, fechas, recuento de dias y estado.

### CA-011: Estados de solicitud <- HU-002
GIVEN la trabajadora SAD ve una ausencia
WHEN consulta el estado
THEN los valores posibles son: Pendiente, Aprobada, Rechazada, Cancelada.

### CA-012: Detalle con comentarios <- HU-002
GIVEN la trabajadora SAD esta en el historial
WHEN toca una ausencia
THEN ve detalles completos y comentarios de coordinadora.

### CA-013: Cancelar solicitud pendiente <- HU-002
GIVEN la trabajadora SAD tiene una solicitud en estado Pendiente
WHEN selecciona cancelar
THEN la solicitud se cancela.

### CA-014: Filtro por estado <- HU-002
GIVEN la trabajadora SAD esta en el historial de ausencias
WHEN aplica filtro por estado
THEN la lista se filtra por el estado seleccionado.

### CA-015: Filtro por tipo <- HU-002
GIVEN la trabajadora SAD esta en el historial de ausencias
WHEN aplica filtro por tipo de ausencia
THEN la lista se filtra por el tipo seleccionado.

### CA-016: Filtro por ano <- HU-002
GIVEN la trabajadora SAD esta en el historial de ausencias
WHEN aplica filtro por ano
THEN la lista se filtra por el ano indicado.

### CA-017: Contadores por tipo <- HU-002
GIVEN la trabajadora SAD accede a Mis Ausencias
WHEN se carga la pantalla
THEN se muestran contadores por tipo de ausencia (vacaciones: asignacion anual total, dias utilizados, dias pendientes de aprobacion, dias disponibles; otros tipos segun aplique).

### CA-018: Vacaciones por dias naturales <- HU-002
GIVEN la trabajadora SAD consulta su saldo de vacaciones
WHEN ve los contadores
THEN las vacaciones se computan por dias naturales.

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
- Aprobacion o rechazo de solicitudes (gestionado por coordinadoras desde backoffice)
- Calculo automatico de dias por convenio o legislacion (el saldo lo provee el backend)
- Ausencias de la trabajadora Hogar (perfil Hogar no tiene este modulo)

---

## Asunciones Aplicadas
| Gap origen | Asuncion aplicada |
|------------|-------------------|
| [P-007] | Las vacaciones se computan por dias naturales, como indica el PRD, pendiente de confirmacion con cliente/legal. Si se confirma otro calculo, se ajustara via delta |
