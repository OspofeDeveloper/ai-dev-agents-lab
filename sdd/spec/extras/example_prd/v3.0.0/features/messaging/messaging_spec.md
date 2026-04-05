# Spec: Comunicacion

> Version: 1.0 | Fecha: 2026-04-05
> Spec monolitico origen: prd-hogar-sad_spec.md
> Feature ID: F-010

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades de empleo a traves de la app CUIDEO (tema azul) | Iniciar conversaciones con coordinacion, enviar y recibir mensajes, consultar listado de conversaciones |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios asignados a traves de la app Felizvita (tema verde) | Iniciar conversaciones con coordinacion, enviar y recibir mensajes, consultar listado de conversaciones |
| Coordinadora / Backoffice | Profesional de gestion interna que supervisa a las trabajadoras. No usa la app movil directamente; interactua a traves del sistema de backoffice | Responder conversaciones, cerrar conversaciones |

---

## Historias de Usuario

### HU-039: Iniciar conversacion con coordinacion
Como trabajadora (Hogar o SAD)
quiero iniciar una nueva conversacion con coordinacion seleccionando un asunto
para que mi consulta llegue al departamento correcto de forma transparente.

### HU-040: Listado de conversaciones
Como trabajadora (Hogar o SAD)
quiero ver todos mis hilos de conversacion con estado de lectura
para que pueda gestionar mis comunicaciones con coordinacion.

### HU-041: Hilo de conversacion
Como trabajadora (Hogar o SAD)
quiero enviar y recibir mensajes dentro de una conversacion
para que pueda comunicarme de forma fluida con coordinacion sobre temas de servicio, ausencias o consultas.

---

## Recorridos de Usuario

### Journey 12: Comunicarse con coordinacion
Actor: Trabajadora (Hogar o SAD) | Objetivo: Consultar o comunicar algo a coordinacion

1. La trabajadora accede a "Comunicacion".
2. Ve el listado de conversaciones (ordenadas por ultimo mensaje) con asunto, preview y marca de tiempo. Las conversaciones cerradas se muestran con indicador visual diferenciado.
3. Para iniciar una nueva conversacion, pulsa "Nueva conversacion".
4. Selecciona un asunto predefinido: Vacaciones/Ausencia, Nomina/Facturacion, Sobre un servicio, Documentacion, Consulta general, Otros.
5. Opcionalmente enlaza contexto (servicio u oferta relacionados).
6. Escribe su primer mensaje y envia.
7. La conversacion se presenta en formato chat. Siempre ve la conversacion como comunicacion con "Coordinacion", independientemente del enrutado interno.
8. Los mensajes nuevos del equipo de coordinacion aparecen automaticamente sin necesidad de refrescar.

Estado de exito: La trabajadora ha iniciado o continuado una conversacion con coordinacion y ha recibido respuesta.

Flujos alternativos:
- Si la conversacion ha sido cerrada por coordinacion: la trabajadora puede ver el historial completo en modo lectura pero no puede escribir nuevos mensajes.

---

## Resultados y Exito

- **Comunicacion**: Las trabajadoras pueden comunicarse con coordinacion de forma fluida a traves de un sistema de chat con actualizacion en tiempo real.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Comunicacion con enrutado transparente**: La trabajadora siempre ve la conversacion como comunicacion con "Coordinacion". El enrutado interno a departamentos lo gestiona el backoffice de forma transparente.
- **Conversaciones cerradas**: Las conversaciones pueden ser cerradas por el equipo de backoffice. Quedan en modo historico de solo lectura (la trabajadora puede consultar pero no escribir).
- **Busqueda de conversaciones**: Filtra por asunto de la conversacion unicamente.
- **Mensajes en tiempo real**: Los mensajes nuevos en conversaciones aparecen automaticamente sin que la usuaria tenga que refrescar.
- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Listado de conversaciones | Tocar conversacion | Hilo de conversacion (RF-10.3) |
| Listado de conversaciones | Pulsar "Nueva conversacion" | Selector de asunto + formulario de primer mensaje (RF-10.1) |

---

## Criterios de Aceptacion

### CA-001: Iniciar conversacion con asunto ← HU-039
GIVEN la trabajadora accede a nueva conversacion
WHEN selecciona un asunto (Vacaciones/Ausencia, Nomina/Facturacion, Sobre un servicio, Documentacion, Consulta general, Otros), opcionalmente enlaza contexto (servicio u oferta) y escribe su primer mensaje
THEN se crea la conversacion en formato chat. El asunto se muestra en la cabecera. Si el backend proporciona codigo de ticket, se muestra. La trabajadora siempre ve la conversacion como comunicacion con "Coordinacion"

### CA-002: Listado de conversaciones ← HU-040
GIVEN la trabajadora accede a "Comunicacion"
WHEN se carga la lista
THEN se muestran las conversaciones en orden cronologico inverso por ultimo mensaje, con asunto, preview y marca de tiempo. Indicador visual para no leidos. Indicador diferenciado para conversaciones cerradas (etiqueta o icono). Pull-to-refresh disponible. Se puede buscar por asunto

### CA-003: Borrar conversacion ← HU-040
GIVEN la trabajadora esta en el listado de conversaciones
WHEN elige borrar una conversacion
THEN se muestra confirmacion. Al confirmar, la conversacion se elimina de su lista

### CA-004: Chat en conversacion abierta ← HU-041
GIVEN la trabajadora abre una conversacion en estado abierta
WHEN interactua con el hilo
THEN ve todos los mensajes en orden cronologico con diferenciacion visual (mensajes propios vs. coordinacion), marca de tiempo y estado de entrega/lectura. Campo de entrada de texto en la parte inferior con boton de enviar. Auto-scroll al ultimo mensaje. Paginacion al desplazar hacia arriba. Mensajes nuevos aparecen automaticamente sin refrescar

### CA-005: Conversacion cerrada en modo lectura ← HU-041
GIVEN la trabajadora abre una conversacion cerrada por coordinacion
WHEN se muestra el hilo
THEN se oculta el campo de entrada, se muestra aviso "Conversacion cerrada" y se permite consultar el historial completo en modo lectura

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

- Funcionalidades de backoffice/coordinacion: este spec cubre exclusivamente la experiencia desde la app movil de la trabajadora.
