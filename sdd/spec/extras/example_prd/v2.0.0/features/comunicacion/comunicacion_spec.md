# Spec: Comunicacion
> Version: 1.0 | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md
> Feature ID: F-010

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo | Iniciar conversaciones con coordinacion, enviar y recibir mensajes, consultar historial |
| Trabajadora SAD | Trabajadora del Servicio de Asistencia Social | Iniciar conversaciones con coordinacion, enviar y recibir mensajes, consultar historial |

---

## Historias de Usuario

### HU-001: Iniciar conversacion
Como trabajadora (Hogar o SAD)
quiero iniciar una conversacion con coordinacion seleccionando un asunto
para que mi consulta sea atendida por el area correspondiente.

### HU-002: Consultar conversaciones
Como trabajadora (Hogar o SAD)
quiero ver todas mis conversaciones con su estado
para que pueda hacer seguimiento de mis consultas.

### HU-003: Enviar y recibir mensajes
Como trabajadora (Hogar o SAD)
quiero enviar y recibir mensajes dentro de una conversacion
para que pueda comunicarme con coordinacion.

---

## Recorridos de Usuario

### Journey 1: Iniciar nueva conversacion
Actor: Trabajadora (Hogar o SAD) | Objetivo: Contactar con coordinacion
1. La trabajadora accede a "Comunicacion" desde el home o menu.
2. Pulsa "Nueva conversacion".
3. Selecciona un asunto predefinido: Vacaciones / Ausencia, Nomina / Facturacion, Sobre un servicio, Documentacion, Consulta general, Otros.
4. La seleccion del asunto determina el enrutado interno en el backoffice (transparente para la trabajadora).
5. Opcionalmente enlaza contexto (selecciona servicio u oferta relacionados) para facilitar la gestion por el backoffice.
6. Escribe el primer mensaje (obligatorio) en formato chat.
7. Ve el asunto seleccionado en la cabecera de la conversacion.
8. Opcionalmente, ve un codigo de ticket si el backend lo proporciona.
9. La trabajadora siempre ve el chat como conversacion con "Coordinacion", independientemente del enrutado interno.

Estado de exito: La conversacion queda creada con asunto, primer mensaje y contexto opcional.

### Journey 2: Consultar conversaciones
Actor: Trabajadora (Hogar o SAD) | Objetivo: Revisar sus conversaciones
1. La trabajadora accede al listado de conversaciones.
2. Ve la lista en orden cronologico inverso (por ultimo mensaje).
3. Cada conversacion muestra asunto, previsualizacion del ultimo mensaje y marca de tiempo.
4. Indicador visual para mensajes no leidos (bold, badge).
5. Indicador visual diferenciado para conversaciones cerradas (etiqueta "Cerrada" o candado).
6. Puede buscar conversaciones.
7. Puede borrar conversaciones (con confirmacion).
8. Pull-to-refresh actualiza la lista.

Estado de exito: La trabajadora puede localizar y acceder a cualquier conversacion.

### Journey 3: Intercambiar mensajes en un hilo
Actor: Trabajadora (Hogar o SAD) | Objetivo: Comunicarse con coordinacion
1. La trabajadora toca una conversacion para abrir el hilo.
2. Ve todos los mensajes en orden cronologico.
3. Los mensajes de la trabajadora se diferencian visualmente de los de coordinacion (alineacion, colores).
4. Cada mensaje muestra marca de tiempo y estado de entrega/lectura.
5. Si la conversacion esta abierta: escribe un mensaje en el campo de entrada y pulsa enviar.
6. Puede enlazar contexto (servicio/oferta) al mensaje.
7. Los mensajes se actualizan en tiempo real.
8. Si la conversacion esta cerrada: no hay campo de entrada, se muestra aviso "Conversacion cerrada" y puede consultar el historial completo en modo lectura.
9. Al desplazar hacia arriba, se cargan mensajes mas antiguos (paginacion).
10. El hilo se desplaza automaticamente al ultimo mensaje al abrirlo.

Estado de exito: La trabajadora envia su mensaje y recibe respuestas en tiempo real.
Flujos alternativos:
- Si la conversacion es cerrada por el backoffice, la trabajadora recibe notificacion push con deeplink al historial de la conversacion.

---

## Resultados y Exito

- La trabajadora puede contactar a coordinacion de forma organizada por asuntos predefinidos.
- El enrutado interno es transparente; la trabajadora siempre interactua con "Coordinacion".
- Las conversaciones cerradas quedan accesibles en modo lectura.
- La comunicacion en tiempo real reduce latencia en la resolucion de consultas.

---

## Instrucciones Inambiguas

### Reglas de comportamiento
- Los asuntos predefinidos son: Vacaciones / Ausencia, Nomina / Facturacion, Sobre un servicio, Documentacion, Consulta general, Otros.
- La seleccion del asunto determina el enrutado interno (transparente para la trabajadora).
- La trabajadora siempre ve "Coordinacion" como interlocutor, independientemente del enrutado.
- El primer mensaje de la conversacion es obligatorio.
- El contexto (servicio/oferta) es opcional y facilita la gestion del backoffice.
- El codigo de ticket en la cabecera es opcional (depende del backend).
- Las conversaciones pueden ser cerradas por el backoffice; pasan a modo historico de solo lectura.
- En conversaciones cerradas: no hay campo de entrada ni boton de enviar; se muestra aviso "Conversacion cerrada".
- Los mensajes se actualizan en tiempo real.
- La paginacion de mensajes antiguos se activa al desplazar hacia arriba.
- Al borrar una conversacion se requiere confirmacion.

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home | Tocar "Comunicacion" | Listado de conversaciones |
| Listado conversaciones | Tocar conversacion abierta | Hilo de mensajes (lectura + escritura) |
| Listado conversaciones | Tocar conversacion cerrada | Hilo de mensajes (solo lectura) |
| Listado conversaciones | Pulsar "Nueva conversacion" | Selector de asunto > primer mensaje > hilo |
| Notificacion push | "Conversacion cerrada" | Historial de la conversacion cerrada |
| Notificacion push | "Nuevo mensaje" | Hilo de la conversacion |

---

## Criterios de Aceptacion

### CA-001: Asuntos predefinidos <- HU-001
GIVEN la trabajadora quiere iniciar una nueva conversacion
WHEN accede al formulario de nueva conversacion
THEN puede seleccionar un asunto predefinido: Vacaciones / Ausencia, Nomina / Facturacion, Sobre un servicio, Documentacion, Consulta general, Otros.

### CA-002: Enrutado transparente <- HU-001
GIVEN la trabajadora selecciona un asunto
WHEN la conversacion se crea
THEN el enrutado interno en el backoffice se determina por el asunto; la trabajadora ve la conversacion como chat con "Coordinacion".

### CA-003: Formato chat con primer mensaje <- HU-001
GIVEN la trabajadora esta creando una conversacion
WHEN completa el asunto
THEN la conversacion se presenta en formato chat y el primer mensaje es obligatorio.

### CA-004: Asunto en cabecera <- HU-001
GIVEN la trabajadora ha creado una conversacion
WHEN ve el hilo
THEN el asunto seleccionado se muestra en la cabecera de la conversacion.

### CA-005: Codigo de ticket <- HU-001
GIVEN la trabajadora ha creado una conversacion
WHEN el backend proporciona un codigo de ticket
THEN se muestra opcionalmente en la cabecera.

### CA-006: Enlazar contexto <- HU-001
GIVEN la trabajadora esta creando una conversacion
WHEN quiere relacionarla con un servicio u oferta
THEN puede enlazar contexto (seleccionar servicio u oferta) para facilitar la gestion.

### CA-007: Listado cronologico <- HU-002
GIVEN la trabajadora accede a Comunicacion
WHEN se carga la lista de conversaciones
THEN se muestran en orden cronologico inverso (por ultimo mensaje).

### CA-008: Info de conversacion <- HU-002
GIVEN la trabajadora esta en el listado de conversaciones
WHEN ve la lista
THEN cada conversacion muestra asunto, previsualizacion del ultimo mensaje y marca de tiempo.

### CA-009: Indicador no leidos <- HU-002
GIVEN hay conversaciones con mensajes no leidos
WHEN la trabajadora ve la lista
THEN se muestra indicador visual para mensajes no leidos (bold, badge).

### CA-010: Indicador conversacion cerrada <- HU-002
GIVEN hay conversaciones cerradas
WHEN la trabajadora ve la lista
THEN se muestra indicador visual diferenciado (etiqueta "Cerrada" o candado).

### CA-011: Acceso a conversacion <- HU-002
GIVEN la trabajadora esta en el listado
WHEN toca una conversacion (abierta o cerrada)
THEN accede al hilo de mensajes (lectura+escritura si abierta; solo lectura si cerrada).

### CA-012: Pull-to-refresh <- HU-002
GIVEN la trabajadora esta en el listado de conversaciones
WHEN realiza gesto de pull-to-refresh
THEN se actualiza la lista.

### CA-013: Buscar conversaciones <- HU-002
GIVEN la trabajadora esta en el listado de conversaciones
WHEN usa la funcion de busqueda
THEN puede buscar entre sus conversaciones.

### CA-014: Borrar conversacion <- HU-002
GIVEN la trabajadora esta en el listado de conversaciones
WHEN decide borrar una conversacion
THEN se muestra confirmacion antes de borrar.

### CA-015: Mensajes cronologicos <- HU-003
GIVEN la trabajadora abre un hilo de conversacion
WHEN se cargan los mensajes
THEN se muestran todos los mensajes en orden cronologico.

### CA-016: Diferenciacion visual <- HU-003
GIVEN la trabajadora esta en un hilo de conversacion
WHEN ve los mensajes
THEN los mensajes de la trabajadora se diferencian de los de coordinacion (alineacion, colores).

### CA-017: Marca de tiempo <- HU-003
GIVEN la trabajadora esta en un hilo de conversacion
WHEN ve un mensaje
THEN se muestra la marca de tiempo del mensaje.

### CA-018: Estado de entrega/lectura <- HU-003
GIVEN la trabajadora ha enviado un mensaje
WHEN ve el mensaje enviado
THEN se muestra el estado de entrega/lectura.

### CA-019: Campo de entrada en conversacion abierta <- HU-003
GIVEN la trabajadora esta en un hilo de conversacion abierta
WHEN ve la parte inferior de la pantalla
THEN se muestra campo de entrada de texto y boton de enviar.

### CA-020: Sin entrada en conversacion cerrada <- HU-003
GIVEN la trabajadora esta en un hilo de conversacion cerrada
WHEN ve la pantalla
THEN no hay campo de entrada; se muestra aviso "Conversacion cerrada"; puede consultar el historial completo.

### CA-021: Desplazamiento al ultimo mensaje <- HU-003
GIVEN la trabajadora abre un hilo de conversacion
WHEN se cargan los mensajes
THEN el hilo se desplaza automaticamente al ultimo mensaje.

### CA-022: Paginacion de mensajes antiguos <- HU-003
GIVEN la trabajadora esta en un hilo de conversacion
WHEN desplaza hacia arriba
THEN se cargan mensajes mas antiguos (paginacion).

### CA-023: Contexto en mensaje <- HU-003
GIVEN la trabajadora esta escribiendo un mensaje
WHEN quiere enlazar contexto
THEN puede enlazar servicio/oferta al mensaje.

### CA-024: Actualizaciones en tiempo real <- HU-003
GIVEN la trabajadora esta en un hilo de conversacion abierta
WHEN coordinacion envia un mensaje
THEN el mensaje aparece en tiempo real sin necesidad de recargar.

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
- Envio de archivos adjuntos en mensajes (solo texto)
- Llamadas de voz o video dentro de la app
- Chat entre trabajadoras (solo con coordinacion)
- Gestion de departamentos por parte de la trabajadora (el enrutado es interno y transparente)
- Reapertura de conversaciones cerradas por la trabajadora (solo el backoffice puede cerrar y reabrir)
