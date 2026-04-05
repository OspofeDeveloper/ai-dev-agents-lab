# Spec: Gestion de Servicios

> Version: 1.0 | Fecha: 2026-04-05
> Spec monolitico origen: prd-hogar-sad_spec.md
> Feature ID: F-003

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios asignados a traves de la app Felizvita (tema verde) | Consultar listado de servicios, ver detalle del servicio, registrar notas de servicio, recibir notificacion de nuevo servicio asignado, consultar historial de servicios |
| Coordinadora / Backoffice | Profesional de gestion interna que supervisa a las trabajadoras. No usa la app movil directamente; interactua a traves del sistema de backoffice | Asignar servicios, configurar visibilidad de campos de servicio |
| Sistema | El propio sistema automatizado que ejecuta acciones programadas sin intervencion humana | Enviar notificacion de servicio proximo |

---

## Historias de Usuario

### HU-013: Listado de servicios (SAD)
Como trabajadora SAD
quiero ver todos mis servicios asignados con su estado
para que pueda organizar mi jornada y saber que servicios tengo activos, proximos y completados.

### HU-014: Detalle del servicio (SAD)
Como trabajadora SAD
quiero ver la informacion completa de un servicio especifico
para que pueda conocer los datos del cliente, ubicacion, plan de cuidados y tareas antes de acudir.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-003]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-015: Notas de servicio (SAD)
Como trabajadora SAD
quiero registrar notas sobre la evolucion del servicio con adjuntos
para que las coordinadoras tengan constancia de las tareas realizadas y las incidencias observadas.

### HU-019: Nuevo servicio asignado - contratos indefinidos (SAD)
Como trabajadora SAD con contrato indefinido
quiero recibir una notificacion cuando se me asigna un nuevo servicio
para que este informada de mis nuevos servicios y pueda comunicar si no puedo atenderlos.

### HU-030: Historial de servicios (SAD)
Como trabajadora SAD
quiero ver mi historial de servicios completados y llamamientos pasados
para que pueda consultar mi actividad anterior y el resultado de cada llamamiento.

---

## Recorridos de Usuario

### Journey 5: Consultar servicios y ver detalle (SAD)
Actor: Trabajadora SAD | Objetivo: Revisar sus servicios asignados y consultar detalles

1. La trabajadora accede al panel principal. El bloque de servicios muestra como maximo el servicio activo y el siguiente servicio; si hay mas, se muestra un enlace "Ver mas servicios".
2. La trabajadora pulsa sobre un servicio o navega a "Mis Servicios".
3. El sistema muestra la lista de servicios agrupados por estado: Activos, Proximos, Completados.
4. Cada servicio muestra informacion clave: nombre/codigo del cliente, direccion, fecha/hora, tipo (con distincion visual entre recurrentes y puntuales).
5. La trabajadora toca un servicio para ver el detalle.
6. El detalle muestra: informacion basica (codigo, tipo, fechas, horario), informacion del cliente (nombre, direccion, edad — la visibilidad de campos es controlable desde backoffice), plan de cuidados, listado descriptivo de tareas (no editable), documentacion asociada.
7. La direccion del servicio se muestra como texto clickable que abre la app de mapas del dispositivo.
8. Desde el detalle, la trabajadora puede acceder a: notas de servicio, historial de fichaje del servicio, fichar entrada/salida, reportar incidencia, contactar con coordinacion.

Estado de exito: La trabajadora ha consultado el detalle completo de un servicio y sabe donde acudir, que tareas realizar y como contactar con coordinacion.

---

## Resultados y Exito

- **Servicios (SAD)**: Las trabajadoras SAD pueden consultar todos sus servicios asignados con informacion completa, navegar al detalle y conocer la ubicacion, plan de cuidados y tareas de cada servicio.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Notas de servicio con adjuntos**: Maximo 5 adjuntos por nota, maximo 10 MB por adjunto. Las trabajadoras pueden editar sus propias notas mientras no hayan sido leidas por la coordinadora. Una vez leidas, solo borrado suave.
- **Tareas de servicio no editables**: El listado de tareas del servicio es descriptivo y no editable por la cuidadora; proviene de backend.
- **Visibilidad de campos del servicio controlada desde backoffice**: Cada campo del detalle del servicio (datos del cliente) puede marcarse como visible o no visible para la cuidadora desde backoffice.
- **Contacto de servicio**: Se muestra como "Contacta con tu coordinador / empresa" (no "contacto de emergencia") con el telefono de coordinacion.
- **Home SAD — bloque de servicios**: Muestra como maximo el servicio activo y el siguiente servicio. Si hay mas, se muestra enlace "Ver mas servicios" (no contador "+2" o similar).
- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.
- **Permiso de camara/archivos**: Se solicita solo en el momento en que se necesite (ej: al subir un documento), no durante el onboarding.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Listado de servicios | Tocar servicio | Detalle del servicio (RF-3.2) |
| Detalle del servicio | Tocar direccion | App de mapas del dispositivo (Google Maps / Apple Maps) |
| Detalle del servicio | Tocar "Notas de servicio" | Listado de notas del servicio (RF-3.3) |
| Detalle del servicio | Tocar "Fichar" | Pantalla de fichaje (RF-4.1) |
| Detalle del servicio | Tocar "Reportar incidencia" | Formulario de incidencia (RF-5.1) |
| Detalle del servicio | Tocar "Contacta coordinador" | Llamada telefonica a coordinacion |
| Detalle del servicio | Tocar "Historial de fichaje" | Historial de seguimiento de tiempo del servicio (RF-4.2) |

---

## Criterios de Aceptacion

### CA-001: Listado de servicios por estado (SAD) ← HU-013
GIVEN la trabajadora SAD accede a "Mis Servicios"
WHEN se carga la lista
THEN se muestran los servicios agrupados por estado: Activos, Proximos, Completados. Cada servicio muestra nombre/codigo del cliente, direccion, fecha/hora, tipo. Hay distincion visual entre recurrentes y puntuales. Estado vacio cuando no hay servicios

### CA-002: Pull-to-refresh en listado de servicios ← HU-013
GIVEN la trabajadora SAD esta en el listado de servicios
WHEN hace pull-to-refresh
THEN la lista se actualiza con la informacion mas reciente del servidor

### CA-003: Detalle de servicio con datos del cliente (SAD) ← HU-014
GIVEN la trabajadora SAD toca un servicio en el listado
WHEN se abre el detalle
THEN se muestra: informacion basica (codigo, tipo, fechas, horario), informacion del cliente (nombre, direccion, edad — la visibilidad de cada campo es controlable desde backoffice), plan de cuidados, listado descriptivo de tareas (no editable), documentacion asociada, CTA "Contacta con tu coordinador / empresa" con telefono

> ⚠ Parcial: La visibilidad de datos de salud del cliente depende de la resolucion de gap P-003.

### CA-004: Direccion clickable a app de mapas ← HU-014
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN toca la direccion del servicio
THEN se abre la app de mapas del dispositivo (Google Maps / Apple Maps) con la direccion del servicio

### CA-005: Accesos desde detalle de servicio ← HU-014
GIVEN la trabajadora SAD esta en el detalle de un servicio
WHEN necesita realizar acciones sobre el servicio
THEN puede acceder a: notas de servicio, historial de fichaje, fichar entrada/salida, reportar incidencia

### CA-006: Listado de notas de servicio ← HU-015
GIVEN la trabajadora SAD accede a las notas de un servicio
WHEN se carga la lista
THEN se muestran las notas en orden cronologico con autora, fecha/hora, contenido, adjuntos y categoria (Evolucion, Tareas, Incidencias, Otras)

### CA-007: Crear nota de servicio con adjuntos ← HU-015
GIVEN la trabajadora SAD esta en las notas de un servicio
WHEN pulsa "Anadir nota"
THEN puede escribir texto multilinea, seleccionar categoria, y adjuntar archivos (maximo 5 adjuntos, maximo 10 MB por adjunto). La nota queda visible inmediatamente para las coordinadoras

### CA-008: Editar nota de servicio propia ← HU-015
GIVEN la trabajadora SAD tiene una nota propia que no ha sido leida por la coordinadora
WHEN toca la nota para editarla
THEN puede modificar el texto y los adjuntos de la nota

### CA-009: Borrar nota de servicio propia ← HU-015
GIVEN la trabajadora SAD tiene una nota propia
WHEN elige borrar la nota
THEN la nota se elimina con borrado suave (queda registrada para auditoria)

### CA-010: Notificacion push nuevo servicio asignado (indefinido) ← HU-019
GIVEN una trabajadora SAD con contrato indefinido recibe un nuevo servicio
WHEN el servicio se asigna desde backoffice
THEN la trabajadora recibe notificacion push "Nuevo servicio asignado" con enlace al detalle del servicio

### CA-011: Visualizacion de servicio asignado en home (indefinido) ← HU-019
GIVEN una trabajadora SAD con contrato indefinido tiene un nuevo servicio asignado
WHEN accede al panel principal
THEN el nuevo servicio se muestra de forma visible y diferenciada de los llamamientos, con distincion visual entre servicios puntuales (con fecha inicio y fin) y recurrentes (sin fecha de fin)

### CA-012: Confirmacion de recepcion de servicio asignado ← HU-019
GIVEN una trabajadora SAD abre el detalle de un nuevo servicio asignado
WHEN el sistema registra que la trabajadora ha visto el servicio
THEN se registra la interaccion "visto/recibido". Desde el detalle, la trabajadora puede generar una incidencia si no puede atender el servicio

### CA-013: Historial de servicios completados (SAD) ← HU-030
GIVEN la trabajadora SAD accede al historial de servicios
WHEN se carga la lista
THEN se muestran los servicios completados con fechas, nombres de clientes y total de horas trabajadas por servicio. Se puede filtrar por rango de fechas. Se puede tocar para ver detalle en solo lectura

### CA-014: Historial completo de llamamientos ← HU-030
GIVEN la trabajadora SAD accede al historial de servicios
WHEN consulta la seccion de llamamientos
THEN se muestra el historial completo de todos los llamamientos con su resultado final (aceptado, rechazado, caducado, desactivado)

---

## Checklist de Validacion

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [ ] Ambiguedades resueltas — gap P-003 pendiente (visibilidad datos de salud)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- Funcionalidades de backoffice/coordinacion: este spec cubre exclusivamente la experiencia desde la app movil de la trabajadora.
