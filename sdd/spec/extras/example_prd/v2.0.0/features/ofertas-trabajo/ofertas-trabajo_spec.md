# Spec: Ofertas de Trabajo
> Version: 1.0 | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md
> Feature ID: F-006

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo | Navegar ofertas, aplicar a ofertas, consultar estado de sus solicitudes, retirar solicitudes pendientes |

---

## Historias de Usuario

### HU-001: Navegar ofertas disponibles
Como trabajadora Hogar
quiero consultar las ofertas de trabajo disponibles con filtros
para que pueda encontrar oportunidades que se ajusten a mis preferencias.

### HU-002: Solicitar oferta
Como trabajadora Hogar
quiero aplicar a una oferta de trabajo
para que las coordinadoras revisen mi candidatura.

### HU-003: Consultar mis solicitudes
Como trabajadora Hogar
quiero ver todas mis solicitudes con su estado actual
para que pueda hacer seguimiento de mis candidaturas.

---

## Recorridos de Usuario

### Journey 1: Buscar y aplicar a una oferta
Actor: Trabajadora Hogar | Objetivo: Encontrar y solicitar una oferta de trabajo
1. La trabajadora accede a "Ofertas" desde el home.
2. Ve la lista de ofertas disponibles en formato de tarjeta.
3. Cada tarjeta muestra: titulo del trabajo, ubicacion (codigo postal/ciudad), horario, tarifa horaria.
4. Las ofertas publicadas en las ultimas 48h muestran insignia "Nuevo".
5. La trabajadora aplica filtros: codigo postal/zona, horario (manana, tarde, noche, madrugada, 24h), rango de fecha de inicio.
6. Ordena por: mas recientes, ubicacion mas cercana, tarifa mas alta.
7. Toca una oferta para ver detalles completos.
8. Pulsa "Aplicar" en la pantalla de detalle.
9. Ve un dialogo de confirmacion con el resumen de la oferta.
10. Confirma y la solicitud se envia con un solo toque.
11. Ve mensaje de exito y recibe notificacion de confirmacion.

Estado de exito: La solicitud queda registrada y la trabajadora recibe confirmacion.
Flujos alternativos:
- Si el perfil esta incompleto al intentar aplicar: se muestra advertencia o bloqueo informando de los campos obligatorios pendientes, con acceso directo a completarlos (F-009).
- Si ya ha aplicado a la misma oferta: se previene la solicitud duplicada.
- Si no hay ofertas coincidentes: se muestra estado vacio.

### Journey 2: Seguimiento de solicitudes
Actor: Trabajadora Hogar | Objetivo: Revisar el estado de sus solicitudes
1. La trabajadora accede a "Mis solicitudes".
2. Ve la lista en orden cronologico inverso con titulo de oferta, ubicacion, fecha de solicitud y estado.
3. Los estados posibles son: Pendiente, En revision, Aceptada, Rechazada, Oferta cerrada.
4. Las solicitudes aceptadas tienen distincion visual.
5. Puede filtrar por estado.
6. Toca una solicitud para ver detalles de la oferta.
7. Puede retirar una solicitud que este en estado Pendiente.
8. Recibe notificacion push cuando cambia el estado.

Estado de exito: La trabajadora puede ver el estado actualizado de todas sus solicitudes.

---

## Resultados y Exito

- La trabajadora Hogar puede encontrar ofertas relevantes usando filtros y ordenacion.
- Las solicitudes se envian con datos del perfil automaticamente incluidos.
- El seguimiento de solicitudes permite visibilidad del ciclo completo de candidatura.

---

## Instrucciones Inambiguas

### Reglas de comportamiento
- La solicitud incluye automaticamente los datos del perfil de la trabajadora.
- No se permiten solicitudes duplicadas a la misma oferta.
- Los filtros de horario son: manana, tarde, noche, madrugada, 24h.
- Las ofertas publicadas en las ultimas 48h muestran insignia "Nuevo".
- Los estados de solicitud son: Pendiente, En revision, Aceptada, Rechazada, Oferta cerrada.
- Solo se pueden retirar solicitudes en estado Pendiente.
- Si el perfil esta incompleto, se bloquea la aplicacion a ofertas con advertencia y acceso directo a completar el perfil.

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home Hogar | Tocar "Ofertas" | Listado de ofertas |
| Listado ofertas | Tocar oferta | Detalle de la oferta |
| Detalle oferta | Pulsar "Aplicar" | Dialogo de confirmacion |
| Detalle oferta | Aplicar con perfil incompleto | Advertencia + acceso directo a Perfil (F-009) |
| Home / Menu | Tocar "Mis solicitudes" | Listado de solicitudes |
| Listado solicitudes | Tocar solicitud | Detalle de la oferta |

---

## Criterios de Aceptacion

### CA-001: Listado en tarjetas <- HU-001
GIVEN la trabajadora Hogar accede a Ofertas
WHEN se carga la lista
THEN se muestran las ofertas disponibles en formato de tarjeta.

### CA-002: Resumen de oferta <- HU-001
GIVEN la trabajadora Hogar esta en el listado de ofertas
WHEN ve una tarjeta
THEN muestra titulo del trabajo, ubicacion (codigo postal/ciudad), horario y tarifa horaria.

### CA-003: Filtro por zona <- HU-001
GIVEN la trabajadora Hogar esta en el listado de ofertas
WHEN aplica filtro por codigo postal/zona
THEN la lista se filtra por la zona indicada.

### CA-004: Filtro por horario <- HU-001
GIVEN la trabajadora Hogar esta en el listado de ofertas
WHEN aplica filtro por horario
THEN puede filtrar por: manana, tarde, noche, madrugada, 24h.

### CA-005: Filtro por fecha inicio <- HU-001
GIVEN la trabajadora Hogar esta en el listado de ofertas
WHEN aplica filtro por rango de fecha de inicio
THEN la lista se filtra por el rango indicado.

### CA-006: Ordenacion <- HU-001
GIVEN la trabajadora Hogar esta en el listado de ofertas
WHEN selecciona criterio de ordenacion
THEN puede ordenar por: mas recientes, ubicacion mas cercana, tarifa mas alta.

### CA-007: Detalle de oferta <- HU-001
GIVEN la trabajadora Hogar esta en el listado de ofertas
WHEN toca una oferta
THEN accede a los detalles completos de la oferta.

### CA-008: Boton aplicar en tarjeta <- HU-001
GIVEN la trabajadora Hogar esta en el listado de ofertas
WHEN ve una tarjeta de oferta
THEN se muestra un boton "Aplicar" en cada tarjeta.

### CA-009: Insignia nuevo <- HU-001
GIVEN una oferta ha sido publicada en las ultimas 48 horas
WHEN la trabajadora ve la tarjeta
THEN se muestra una insignia "Nuevo".

### CA-010: Estado vacio <- HU-001
GIVEN la trabajadora Hogar aplica filtros
WHEN no hay ofertas coincidentes
THEN se muestra un estado vacio informativo.

### CA-011: Confirmacion de solicitud <- HU-002
GIVEN la trabajadora Hogar esta en el detalle de una oferta
WHEN pulsa "Aplicar"
THEN se muestra un dialogo de confirmacion con el resumen de la oferta.

### CA-012: Envio con un toque <- HU-002
GIVEN la trabajadora Hogar ve el dialogo de confirmacion
WHEN confirma la solicitud
THEN la solicitud se envia con un solo toque.

### CA-013: Mensaje de exito <- HU-002
GIVEN la trabajadora Hogar ha enviado la solicitud
WHEN se confirma el envio
THEN se muestra un mensaje de exito.

### CA-014: Prevencion de duplicados <- HU-002
GIVEN la trabajadora Hogar ya ha aplicado a una oferta
WHEN intenta aplicar de nuevo a la misma oferta
THEN se previene la solicitud duplicada.

### CA-015: Datos de perfil incluidos <- HU-002
GIVEN la trabajadora Hogar envia una solicitud
WHEN se procesa la solicitud
THEN incluye automaticamente los datos del perfil de la trabajadora.

### CA-016: Notificacion de confirmacion <- HU-002
GIVEN la trabajadora Hogar ha enviado una solicitud
WHEN se registra la solicitud
THEN recibe una notificacion de confirmacion.

### CA-017: Bloqueo por perfil incompleto <- HU-002
GIVEN la trabajadora Hogar tiene el perfil incompleto
WHEN intenta aplicar a una oferta
THEN se muestra una advertencia informando de los campos obligatorios pendientes, con acceso directo a completarlos.

### CA-018: Listado de solicitudes <- HU-003
GIVEN la trabajadora Hogar accede a Mis solicitudes
WHEN se carga la lista
THEN se muestran las solicitudes en orden cronologico inverso.

### CA-019: Info de solicitud <- HU-003
GIVEN la trabajadora Hogar esta en Mis solicitudes
WHEN ve la lista
THEN cada solicitud muestra titulo de la oferta, ubicacion, fecha de solicitud y estado.

### CA-020: Estados de solicitud <- HU-003
GIVEN la trabajadora Hogar ve una solicitud
WHEN consulta el estado
THEN los valores posibles son: Pendiente, En revision, Aceptada, Rechazada, Oferta cerrada.

### CA-021: Detalle desde solicitud <- HU-003
GIVEN la trabajadora Hogar esta en Mis solicitudes
WHEN toca una solicitud
THEN accede a los detalles de la oferta.

### CA-022: Distincion visual aceptada <- HU-003
GIVEN la trabajadora Hogar esta en Mis solicitudes
WHEN hay solicitudes aceptadas
THEN se muestran con distincion visual.

### CA-023: Filtro por estado <- HU-003
GIVEN la trabajadora Hogar esta en Mis solicitudes
WHEN aplica filtro por estado
THEN la lista se filtra por el estado seleccionado.

### CA-024: Retirar solicitud <- HU-003
GIVEN la trabajadora Hogar esta en Mis solicitudes
WHEN tiene una solicitud en estado Pendiente
THEN puede retirar la solicitud.

### CA-025: Notificacion de cambio de estado <- HU-003
GIVEN una solicitud de la trabajadora cambia de estado
WHEN se actualiza el estado
THEN la trabajadora recibe notificacion push.

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
- Creacion o edicion de ofertas (gestionado desde backoffice)
- Valoraciones o resenas de trabajadoras
- Chat directo con el publicador de la oferta (la comunicacion va por el modulo de Comunicacion)
- Recomendaciones automaticas de ofertas
