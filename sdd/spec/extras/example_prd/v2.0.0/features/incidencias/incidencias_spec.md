# Spec: Incidencias
> Version: 1.0 | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md
> Feature ID: F-005

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora del Servicio de Asistencia Social | Reportar incidencias del servicio o del usuario, consultar historial de incidencias, ver respuestas de coordinadoras |

---

## Historias de Usuario

### HU-001: Reportar incidencia
Como trabajadora SAD
quiero reportar incidencias del servicio o del usuario con descripcion y adjuntos
para que las coordinadoras esten informadas y puedan actuar.

### HU-002: Consultar historial de incidencias
Como trabajadora SAD
quiero ver todas las incidencias que he reportado con su estado y respuestas
para que pueda hacer seguimiento de las incidencias.

---

## Recorridos de Usuario

### Journey 1: Reportar una incidencia
Actor: Trabajadora SAD | Objetivo: Informar de un problema durante el servicio
1. La trabajadora accede al reporte de incidencias desde el detalle del servicio, la pantalla de fichaje o el menu.
2. Selecciona el tipo de incidencia: Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros.
3. Selecciona el servicio relacionado (si la incidencia ocurre durante el servicio).
4. Introduce la descripcion de la incidencia (obligatorio, minimo 20 caracteres).
5. Opcionalmente adjunta fotos de camara o galeria (maximo 5).
6. Opcionalmente adjunta documentos (maximo 3).
7. Ve el tamano estimado de subida antes de enviar.
8. Las imagenes se comprimen automaticamente.
9. Confirma el envio y ve mensaje de confirmacion.
10. La incidencia es visible para coordinadoras inmediatamente.

Estado de exito: La incidencia queda registrada con todos los datos y adjuntos, visible para coordinadoras.

### Journey 2: Consultar historial de incidencias
Actor: Trabajadora SAD | Objetivo: Revisar incidencias pasadas
1. La trabajadora accede al historial de incidencias.
2. Ve la lista en orden cronologico inverso con numero de incidencia, tipo, fecha y estado.
3. Puede filtrar por estado, rango de fechas o buscar por numero/descripcion.
4. Toca una incidencia para ver detalles completos y comentarios/respuestas de coordinadoras.

Estado de exito: La trabajadora puede consultar el estado de cualquier incidencia reportada.

---

## Resultados y Exito

- Las incidencias quedan documentadas con tipo, descripcion, adjuntos y servicio asociado.
- Las coordinadoras tienen visibilidad inmediata de cada incidencia.
- El historial permite seguimiento del ciclo de vida completo de cada incidencia.

---

## Instrucciones Inambiguas

### Reglas de comportamiento
- Las incidencias son principalmente del servicio/usuario atendido, no de la propia cuidadora (las ausencias de la trabajadora tienen su propio flujo en F-008).
- El tipo "Incidencia de fichaje / No asistencia" es la excepcion para reportar problemas operativos de la propia cuidadora relacionados directamente con la prestacion del servicio.
- La taxonomia y el copy deben dejar claro que las incidencias son del servicio/usuario, excepto el tipo de fichaje/no asistencia.
- Los tipos de incidencia son: Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros.
- La descripcion es obligatoria con minimo 20 caracteres.
- Las fotos se comprimen automaticamente antes de subir.
- Maximo 5 fotos y 3 documentos adjuntos.
- Los estados de una incidencia son: Reportada, En revision, Resuelta, Cerrada.

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Detalle servicio | Tocar "Reportar incidencia" | Formulario de reporte de incidencia |
| Pantalla fichaje | Tocar "Reportar incidencia de fichaje" | Formulario de reporte de incidencia (preseleccionado tipo fichaje) |
| Menu / Home | Tocar "Incidencias" | Historial de incidencias |
| Historial | Tocar incidencia | Detalle de la incidencia con comentarios |

---

## Criterios de Aceptacion

### CA-001: Seleccion de tipo <- HU-001
GIVEN la trabajadora SAD esta creando una incidencia
WHEN accede al formulario
THEN puede seleccionar tipo de lista predefinida: Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros.

### CA-002: Seleccion de servicio <- HU-001
GIVEN la trabajadora SAD esta creando una incidencia
WHEN el formulario se presenta
THEN puede seleccionar el servicio relacionado.

### CA-003: Descripcion obligatoria <- HU-001
GIVEN la trabajadora SAD esta creando una incidencia
WHEN introduce la descripcion
THEN la descripcion es obligatoria con un minimo de 20 caracteres.

### CA-004: Adjuntar fotos <- HU-001
GIVEN la trabajadora SAD esta creando una incidencia
WHEN decide adjuntar fotos
THEN puede tomar fotos con la camara o seleccionar de galeria, con un maximo de 5 fotos.

### CA-005: Adjuntar documentos <- HU-001
GIVEN la trabajadora SAD esta creando una incidencia
WHEN decide adjuntar documentos
THEN puede adjuntar un maximo de 3 documentos.

### CA-006: Tamano estimado de subida <- HU-001
GIVEN la trabajadora SAD ha adjuntado archivos a la incidencia
WHEN revisa antes de enviar
THEN se muestra el tamano estimado de subida.

### CA-007: Compresion automatica de imagenes <- HU-001
GIVEN la trabajadora SAD adjunta fotos a la incidencia
WHEN las fotos se preparan para envio
THEN se comprimen automaticamente.

### CA-008: Confirmacion de envio <- HU-001
GIVEN la trabajadora SAD ha completado el formulario de incidencia
WHEN pulsa enviar
THEN se muestra confirmacion de envio exitoso.

### CA-009: Visibilidad inmediata para coordinadoras <- HU-001
GIVEN la trabajadora SAD ha enviado una incidencia
WHEN la incidencia se registra
THEN es visible para las coordinadoras inmediatamente.

### CA-010: Listado cronologico <- HU-002
GIVEN la trabajadora SAD accede al historial de incidencias
WHEN se carga la lista
THEN las incidencias se muestran en orden cronologico inverso.

### CA-011: Info de la incidencia <- HU-002
GIVEN la trabajadora SAD esta en el historial de incidencias
WHEN ve la lista
THEN cada incidencia muestra numero, tipo, fecha y estado.

### CA-012: Estados de incidencia <- HU-002
GIVEN la trabajadora SAD ve una incidencia
WHEN consulta su estado
THEN los valores posibles son: Reportada, En revision, Resuelta, Cerrada.

### CA-013: Detalle de incidencia <- HU-002
GIVEN la trabajadora SAD esta en el historial de incidencias
WHEN toca una incidencia
THEN ve los detalles completos de la incidencia.

### CA-014: Comentarios de coordinadoras <- HU-002
GIVEN la trabajadora SAD esta en el detalle de una incidencia
WHEN hay respuestas de coordinadoras
THEN se muestran los comentarios/respuestas.

### CA-015: Filtro por estado <- HU-002
GIVEN la trabajadora SAD esta en el historial de incidencias
WHEN aplica filtro por estado
THEN la lista se filtra por el estado seleccionado.

### CA-016: Filtro por fechas <- HU-002
GIVEN la trabajadora SAD esta en el historial de incidencias
WHEN aplica filtro por rango de fechas
THEN la lista se filtra por el rango indicado.

### CA-017: Busqueda <- HU-002
GIVEN la trabajadora SAD esta en el historial de incidencias
WHEN busca por numero de incidencia o descripcion
THEN la lista muestra los resultados coincidentes.

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
- Edicion de incidencias ya reportadas
- Cierre de incidencias por parte de la trabajadora (solo coordinadoras)
- Chat dentro del hilo de incidencia (las respuestas se ven pero la comunicacion bidireccional se gestiona via el modulo de Comunicacion)
