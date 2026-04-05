# Spec: Reporte y Seguimiento de Incidencias
> Version: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-006 via prd-hogar-sad_discovery.md)
> Feature ID: F-006
> Spec monolitico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Profesional contratada del Servicio de Asistencia Social que presta servicios de cuidado a domicilio | Reportar incidencias del servicio o del usuario atendido, consultar historial de incidencias, ver detalle con respuestas de coordinacion |
| Coordinadora | Gestora de backoffice que supervisa los servicios y atiende incidencias | Recibir incidencias reportadas, responder con comentarios (gestionado desde backoffice, fuera del scope de esta feature) |

---

## Historias de Usuario

### HU-001: Reportar una incidencia del servicio
Como trabajadora SAD
quiero reportar una incidencia relacionada con el servicio o el usuario atendido indicando tipo, descripcion y adjuntos
para que coordinacion quede informada de inmediato y pueda actuar en consecuencia

### HU-002: Consultar el historial de incidencias
Como trabajadora SAD
quiero ver todas las incidencias que he reportado con su estado actual
para que pueda hacer seguimiento de su resolucion y saber si coordinacion ha respondido

### HU-003: Ver el detalle de una incidencia con respuestas
Como trabajadora SAD
quiero acceder al detalle de una incidencia y leer los comentarios de coordinacion
para que pueda entender las acciones tomadas y aportar informacion adicional si es necesario

---

## Recorridos de Usuario

### Journey 1: Reportar una nueva incidencia
Actor: Trabajadora SAD | Objetivo: Comunicar una incidencia del servicio a coordinacion

1. La trabajadora accede a la seccion de Incidencias desde el menu principal o desde el detalle de un servicio
2. La trabajadora pulsa "Reportar incidencia"
3. La trabajadora selecciona el tipo de incidencia de una lista predefinida (Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros)
4. La trabajadora selecciona el servicio relacionado (si la incidencia esta vinculada a un servicio concreto)
5. La trabajadora introduce una descripcion obligatoria (minimo 20 caracteres)
6. Opcionalmente, la trabajadora adjunta fotos (maximo 5) desde la camara o la galeria
7. Opcionalmente, la trabajadora adjunta documentos (maximo 3)
8. La aplicacion muestra el tamano estimado de la subida antes de enviar
9. La trabajadora confirma y envia la incidencia
10. La aplicacion muestra confirmacion de envio exitoso

Estado de exito: La incidencia queda registrada y es inmediatamente visible para las coordinadoras en backoffice. La trabajadora ve la confirmacion de envio.

Flujos alternativos:
- Si la descripcion tiene menos de 20 caracteres → la aplicacion muestra un mensaje indicando el minimo requerido y no permite el envio
- Si la trabajadora no selecciona tipo de incidencia → la aplicacion indica que el tipo es obligatorio
- Si falla la conexion durante el envio → la aplicacion muestra un mensaje de error de conexion y la trabajadora debe reintentar manualmente cuando disponga de conexion

### Journey 2: Consultar el historial de incidencias
Actor: Trabajadora SAD | Objetivo: Revisar las incidencias reportadas y su estado

1. La trabajadora accede a la seccion de Incidencias
2. La aplicacion muestra el listado de incidencias en orden cronologico inverso (mas recientes primero)
3. Cada incidencia en el listado muestra: numero de incidencia, tipo, fecha de reporte y estado actual
4. La trabajadora puede filtrar por estado (Reportada, En revision, Resuelta, Cerrada)
5. La trabajadora puede filtrar por rango de fechas
6. La trabajadora puede buscar por numero de incidencia o texto de la descripcion

Estado de exito: La trabajadora localiza la incidencia que busca y puede ver su estado actual de un vistazo.

Flujos alternativos:
- Si no hay incidencias reportadas → la aplicacion muestra un estado vacio con mensaje informativo
- Si los filtros no devuelven resultados → la aplicacion indica que no hay incidencias que coincidan con los criterios

### Journey 3: Ver el detalle de una incidencia con respuestas de coordinacion
Actor: Trabajadora SAD | Objetivo: Conocer las acciones tomadas por coordinacion sobre una incidencia

1. La trabajadora toca una incidencia en el listado del historial
2. La aplicacion muestra el detalle completo: tipo, servicio relacionado, descripcion, adjuntos, fecha de reporte y estado
3. Debajo del detalle, se muestran los comentarios/respuestas de coordinadoras en orden cronologico
4. La trabajadora lee los comentarios y puede volver al listado

Estado de exito: La trabajadora comprende el estado de su incidencia y las acciones o respuestas proporcionadas por coordinacion.

Flujos alternativos:
- Si la incidencia no tiene comentarios de coordinacion → la seccion de comentarios muestra un mensaje indicando que aun no hay respuestas

---

## Resultados y Exito

Esta feature se considera completa cuando:
- La trabajadora SAD puede reportar una incidencia con tipo, descripcion y adjuntos opcionales, y esta queda inmediatamente disponible para coordinacion
- La trabajadora SAD puede consultar todas sus incidencias reportadas, filtrarlas por estado y fecha, y buscar por numero o texto
- La trabajadora SAD puede acceder al detalle de cualquier incidencia y ver los comentarios de coordinacion
- Los estados de las incidencias reflejan correctamente su ciclo de vida: Reportada, En revision, Resuelta, Cerrada

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Tipos de incidencia**: La lista de tipos es predefinida y fija para el MVP: Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros. Los tipos se gestionan desde backoffice y no son editables por la trabajadora.

2. **Naturaleza de las incidencias**: Las incidencias son principalmente del servicio o del usuario atendido (incidencias medicas, de seguridad, materiales). No son incidencias de la propia trabajadora (las ausencias tienen su propio flujo en la feature de gestion de ausencias). La excepcion es el tipo "Incidencia de fichaje / No asistencia" para problemas operativos directamente relacionados con la prestacion del servicio. La taxonomia y el copy deben dejar claro este punto.

3. **Servicio relacionado**: Seleccionar un servicio relacionado es opcional. Si la incidencia ocurre durante un servicio, la trabajadora puede vincularlo. Si accede al reporte desde el detalle de un servicio, el servicio se preselecciona automaticamente.

4. **Descripcion obligatoria**: Minimo 20 caracteres. La validacion se realiza antes de permitir el envio.

5. **Adjuntos — fotos**: Maximo 5 fotos. Se pueden tomar desde la camara del dispositivo o seleccionar de la galeria. Las imagenes se comprimen automaticamente para no superar 1MB por imagen manteniendo calidad visual aceptable.

6. **Adjuntos — documentos**: Maximo 3 documentos.

7. **Tamano estimado de subida**: Antes de enviar, la aplicacion muestra una estimacion del tamano total de la subida (descripcion + adjuntos) para que la trabajadora sea consciente del volumen de datos, especialmente si esta usando datos moviles.

8. **Visibilidad inmediata**: Una vez enviada, la incidencia es inmediatamente visible para las coordinadoras en backoffice. No hay estado intermedio de "borrador" ni "cola de envio".

9. **Estados del ciclo de vida**: Una incidencia pasa por los estados: Reportada (estado inicial al enviar) → En revision (coordinacion ha abierto el caso) → Resuelta (coordinacion ha dado una solucion) → Cerrada (caso finalizado). Las transiciones de estado son gestionadas exclusivamente desde backoffice.

10. **Orden del listado**: Las incidencias se listan en orden cronologico inverso (la mas reciente primero).

11. **Filtros y busqueda**: Se puede filtrar por estado, por rango de fechas, y buscar por numero de incidencia o texto contenido en la descripcion. Los filtros son acumulables.

12. **Comentarios de coordinacion**: Los comentarios se muestran en orden cronologico (el mas antiguo primero) debajo del detalle de la incidencia. Son de solo lectura para la trabajadora en esta version.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Menu principal (home SAD) | Pulsar acceso directo "Incidencias" | Listado de incidencias (historial) |
| Detalle de un servicio (feature service-management) | Pulsar "Reportar incidencia" | Formulario de nueva incidencia con servicio preseleccionado |
| Listado de incidencias | Pulsar "Reportar incidencia" | Formulario de nueva incidencia (sin servicio preseleccionado) |
| Listado de incidencias | Tocar una incidencia de la lista | Detalle de la incidencia |
| Formulario de nueva incidencia | Enviar con exito | Confirmacion de envio → listado de incidencias |
| Detalle de la incidencia | Pulsar "Volver" | Listado de incidencias |

---

## Criterios de Aceptacion

### CA-001: Seleccion de tipo de incidencia ← HU-001
GIVEN la trabajadora SAD ha accedido al formulario de nueva incidencia
WHEN visualiza el campo de tipo de incidencia
THEN la aplicacion muestra una lista con los tipos: Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros

### CA-002: Vinculacion opcional de servicio ← HU-001
GIVEN la trabajadora SAD esta completando el formulario de nueva incidencia
WHEN selecciona un servicio relacionado
THEN la incidencia queda vinculada a ese servicio y se muestra el nombre del servicio en el formulario

### CA-003: Servicio preseleccionado desde detalle ← HU-001
GIVEN la trabajadora SAD accede al formulario de nueva incidencia desde el detalle de un servicio
WHEN se carga el formulario
THEN el campo de servicio relacionado aparece preseleccionado con el servicio desde el que se accedio

### CA-004: Descripcion obligatoria con minimo de caracteres ← HU-001
GIVEN la trabajadora SAD ha completado el formulario de incidencia con una descripcion de menos de 20 caracteres
WHEN intenta enviar la incidencia
THEN la aplicacion muestra un mensaje de error indicando que la descripcion debe tener al menos 20 caracteres y no permite el envio

### CA-005: Adjuntar fotos desde camara o galeria ← HU-001
GIVEN la trabajadora SAD esta completando el formulario de nueva incidencia
WHEN pulsa la opcion de adjuntar foto
THEN puede elegir entre tomar una foto con la camara o seleccionar una de la galeria, hasta un maximo de 5 fotos

### CA-006: Limite maximo de fotos adjuntas ← HU-001
GIVEN la trabajadora SAD ya ha adjuntado 5 fotos al formulario de incidencia
WHEN intenta adjuntar una foto adicional
THEN la aplicacion muestra un mensaje indicando que se ha alcanzado el maximo de 5 fotos

### CA-007: Adjuntar documentos con limite ← HU-001
GIVEN la trabajadora SAD esta completando el formulario de nueva incidencia
WHEN adjunta documentos
THEN puede adjuntar hasta 3 documentos, y si intenta superar el limite la aplicacion le informa que se ha alcanzado el maximo

### CA-008: Compresion automatica de imagenes ← HU-001
GIVEN la trabajadora SAD ha adjuntado fotos al formulario de incidencia
WHEN la aplicacion procesa los adjuntos antes del envio
THEN las imagenes se comprimen automaticamente para reducir su tamano manteniendo calidad visual aceptable

### CA-009: Tamano estimado de subida ← HU-001
GIVEN la trabajadora SAD ha completado el formulario de incidencia con adjuntos
WHEN revisa el formulario antes de enviar
THEN la aplicacion muestra el tamano estimado total de la subida

### CA-010: Confirmacion de envio exitoso ← HU-001
GIVEN la trabajadora SAD ha completado todos los campos obligatorios del formulario de incidencia
WHEN pulsa el boton de enviar
THEN la aplicacion envia la incidencia, muestra una confirmacion de envio exitoso y la incidencia queda inmediatamente visible para las coordinadoras

### CA-011: Listado de incidencias en orden cronologico inverso ← HU-002
GIVEN la trabajadora SAD ha reportado al menos una incidencia
WHEN accede a la seccion de historial de incidencias
THEN las incidencias se muestran en orden cronologico inverso, mostrando numero de incidencia, tipo, fecha y estado

### CA-012: Filtrar incidencias por estado ← HU-002
GIVEN la trabajadora SAD esta en el listado de incidencias
WHEN aplica un filtro por estado (Reportada, En revision, Resuelta o Cerrada)
THEN el listado muestra solo las incidencias que coincidan con el estado seleccionado

### CA-013: Filtrar incidencias por rango de fechas ← HU-002
GIVEN la trabajadora SAD esta en el listado de incidencias
WHEN aplica un filtro de rango de fechas
THEN el listado muestra solo las incidencias reportadas dentro del rango seleccionado

### CA-014: Buscar incidencias por numero o descripcion ← HU-002
GIVEN la trabajadora SAD esta en el listado de incidencias
WHEN introduce un texto en el campo de busqueda
THEN el listado se filtra mostrando las incidencias cuyo numero o descripcion contengan el texto buscado

### CA-015: Ver detalle completo de una incidencia ← HU-003
GIVEN la trabajadora SAD esta en el listado de incidencias
WHEN toca una incidencia
THEN la aplicacion muestra el detalle completo: tipo, servicio relacionado, descripcion, adjuntos, fecha de reporte y estado actual

### CA-016: Ver comentarios de coordinacion ← HU-003
GIVEN la trabajadora SAD esta viendo el detalle de una incidencia que tiene comentarios de coordinacion
WHEN se carga la pantalla de detalle
THEN los comentarios se muestran en orden cronologico debajo del detalle de la incidencia

### CA-017: Incidencia sin comentarios ← HU-003
GIVEN la trabajadora SAD esta viendo el detalle de una incidencia que no tiene comentarios
WHEN se carga la pantalla de detalle
THEN la seccion de comentarios muestra un mensaje indicando que aun no hay respuestas de coordinacion

### CA-018: Estado vacio del historial ← HU-002
GIVEN la trabajadora SAD no ha reportado ninguna incidencia
WHEN accede a la seccion de historial de incidencias
THEN la aplicacion muestra un estado vacio con un mensaje informativo y la opcion de reportar una nueva incidencia

### CA-019: Error de conexion al enviar incidencia ← HU-001
GIVEN la trabajadora SAD ha completado el formulario de incidencia y no tiene conexion a internet
WHEN intenta enviar la incidencia
THEN la aplicacion muestra un mensaje de error indicando la falta de conexion y la trabajadora debe reintentar manualmente cuando disponga de conexion

---

## Checklist de Validacion

- [x] Actores identificados (Trabajadora SAD como actor principal, Coordinadora como actor secundario de backoffice)
- [x] Flujos principales descritos paso a paso (3 journeys: reportar, consultar historial, ver detalle)
- [x] Estados de exito definidos para cada journey
- [x] Edge cases documentados (estado vacio, sin comentarios, error de conexion, limites de adjuntos)
- [x] Estados de error definidos (descripcion corta, limites de adjuntos, fallo de conexion)
- [x] Ambiguedades resueltas (naturaleza de incidencias, preseleccion de servicio, compresion de imagenes)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- **Responder a incidencias desde la app**: En esta version, la trabajadora solo puede ver los comentarios de coordinacion. No puede responder a los comentarios ni aportar informacion adicional desde la pantalla de detalle. La comunicacion adicional se canaliza a traves de la feature de comunicacion (F-011).
- **Editar o eliminar incidencias reportadas**: Una vez enviada, la incidencia no se puede modificar ni eliminar desde la app.
- **Notificaciones push de cambio de estado**: Las notificaciones push cuando una incidencia cambia de estado se gestionan en la feature de push-notifications (F-012), no en esta feature.
- **Gestion de incidencias desde backoffice**: La interfaz de coordinadoras para gestionar, responder y cambiar estados de incidencias es parte del sistema de backoffice, fuera del scope de esta aplicacion movil.

---

## Asunciones Aplicadas

- **[A-001]**: Las imagenes adjuntadas a las incidencias se comprimen automaticamente para no superar 1MB por imagen manteniendo calidad visual aceptable. El tamano exacto se ajustara en el Plan segun las capacidades del dispositivo y la velocidad de red tipica. (Derivada de [P-015][INFORMATIVO] del analysis sin respuesta del cliente.)

- **[A-002]**: Cuando la trabajadora pierde conexion a internet durante el envio de una incidencia, la aplicacion muestra un mensaje de error indicando la falta de conexion y la trabajadora debe reintentar manualmente cuando disponga de conexion. No hay cola de reintentos automaticos. (Derivada de [P-014][INFORMATIVO] del analysis sin respuesta del cliente — el modo offline con sincronizacion esta explicitamente fuera de alcance del proyecto.)

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-04-05 | Version inicial generada via fast-track desde PRD (scope F-006) |
