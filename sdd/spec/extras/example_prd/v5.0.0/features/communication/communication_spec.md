# Spec: Communication
> Version: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-011 via prd-hogar-sad_discovery.md)
> Feature ID: F-011
> Spec monolitico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora (Hogar y SAD) | Profesional de cuidados que utiliza la aplicacion movil para gestionar su actividad laboral | Iniciar conversaciones con coordinacion, enviar y recibir mensajes, consultar historial de conversaciones, buscar y borrar conversaciones |
| Coordinacion (backoffice) | Equipo de gestion que atiende las consultas de las trabajadoras desde el backoffice | Responder mensajes, cerrar conversaciones, enrutar internamente las conversaciones por departamento |

---

## Historias de Usuario

### HU-001: Iniciar conversacion con coordinacion
Como trabajadora
quiero iniciar una nueva conversacion con coordinacion seleccionando un asunto predefinido
para que mi consulta llegue al departamento adecuado y pueda resolverse de forma agil

### HU-002: Consultar mis conversaciones
Como trabajadora
quiero ver el listado de todas mis conversaciones con su estado y previsualizacion
para que pueda acceder rapidamente a cualquier hilo y saber cuales tienen mensajes nuevos

### HU-003: Enviar y recibir mensajes en tiempo real
Como trabajadora
quiero enviar mensajes de texto y recibir respuestas de coordinacion en tiempo real dentro de un hilo de conversacion
para que la comunicacion sea fluida y no tenga que refrescar manualmente para ver las respuestas

### HU-004: Consultar conversaciones cerradas
Como trabajadora
quiero poder acceder al historial completo de una conversacion que coordinacion ha cerrado
para que pueda revisar la informacion y las instrucciones que me dieron sin perder ese contexto

### HU-005: Buscar y gestionar conversaciones
Como trabajadora
quiero poder buscar entre mis conversaciones y borrar las que ya no necesite
para que pueda mantener organizado mi modulo de comunicacion y encontrar rapidamente lo que busco

---

## Recorridos de Usuario

### Journey 1: Iniciar una nueva conversacion
Actor: Trabajadora | Objetivo: Comunicar una consulta, duda o incidencia administrativa a coordinacion

1. La trabajadora accede al modulo de Comunicacion desde la pantalla principal
2. La trabajadora pulsa "Nueva conversacion"
3. La aplicacion muestra una lista de asuntos predefinidos: Vacaciones / Ausencia, Nomina / Facturacion, Sobre un servicio, Documentacion, Consulta general, Otros
4. La trabajadora selecciona el asunto que mejor describe su consulta
5. Opcionalmente, la trabajadora enlaza un servicio u oferta como contexto de la conversacion
6. La trabajadora escribe el primer mensaje (obligatorio) y lo envia
7. La aplicacion crea la conversacion mostrando el asunto seleccionado en la cabecera y el primer mensaje en el hilo
8. La trabajadora ve la conversacion como un chat con "Coordinacion", independientemente de a que departamento se enrute internamente

Estado de exito: La conversacion queda creada con el asunto seleccionado, el contexto enlazado (si aplica) y el primer mensaje visible en el hilo. La trabajadora puede continuar enviando mensajes.

Flujos alternativos:
- Si la trabajadora no selecciona un asunto y pulsa enviar: la aplicacion le indica que debe seleccionar un asunto antes de continuar
- Si la trabajadora no escribe ningun mensaje: la aplicacion le indica que el primer mensaje es obligatorio

### Journey 2: Consultar el listado de conversaciones
Actor: Trabajadora | Objetivo: Revisar sus conversaciones y acceder a la que necesite

1. La trabajadora accede al modulo de Comunicacion
2. La aplicacion muestra el listado de conversaciones ordenadas de la mas reciente a la mas antigua (por ultimo mensaje)
3. Cada conversacion muestra el asunto, una previsualizacion del ultimo mensaje y la marca de tiempo
4. Las conversaciones con mensajes no leidos muestran un indicador visual destacado
5. Las conversaciones cerradas por backoffice muestran una etiqueta o icono diferenciado ("Cerrada")
6. La trabajadora toca una conversacion para abrir el hilo

Estado de exito: La trabajadora localiza la conversacion que busca y accede a ella.

Flujos alternativos:
- Si no hay conversaciones: la aplicacion muestra un estado vacio con opcion de iniciar nueva conversacion
- Si la trabajadora busca por texto: el listado se filtra mostrando solo las conversaciones que coinciden con la busqueda

### Journey 3: Enviar y recibir mensajes en un hilo
Actor: Trabajadora | Objetivo: Comunicarse con coordinacion dentro de una conversacion abierta

1. La trabajadora abre una conversacion abierta desde el listado
2. La aplicacion muestra todos los mensajes del hilo en orden cronologico, diferenciando visualmente los mensajes propios de los de coordinacion
3. Cada mensaje muestra su marca de tiempo y, para los mensajes de la trabajadora, el estado de entrega/lectura
4. La aplicacion se desplaza automaticamente al ultimo mensaje
5. La trabajadora escribe un mensaje en el campo de entrada situado en la parte inferior y lo envia
6. El mensaje aparece inmediatamente en el hilo
7. Cuando coordinacion responde, el nuevo mensaje aparece automaticamente en la conversacion sin que la trabajadora tenga que refrescar

Estado de exito: El mensaje de la trabajadora se envia correctamente y las respuestas de coordinacion aparecen en tiempo real.

Flujos alternativos:
- Si la trabajadora necesita ver mensajes anteriores: al desplazar hacia arriba se cargan mensajes mas antiguos progresivamente
- Si la trabajadora enlaza un servicio u oferta a un mensaje: el contexto se muestra junto al mensaje

### Journey 4: Consultar una conversacion cerrada
Actor: Trabajadora | Objetivo: Revisar el historial de una conversacion que coordinacion ha cerrado

1. La trabajadora abre una conversacion marcada como "Cerrada" desde el listado
2. La aplicacion muestra todos los mensajes del hilo en orden cronologico (mismo formato que una conversacion abierta)
3. El campo de entrada de texto no se muestra
4. La aplicacion muestra un aviso de "Conversacion cerrada" indicando que no se pueden enviar mas mensajes
5. La trabajadora puede desplazarse por todo el historial de la conversacion

Estado de exito: La trabajadora puede leer el historial completo de la conversacion sin poder enviar mensajes nuevos.

### Journey 5: Buscar y borrar conversaciones
Actor: Trabajadora | Objetivo: Organizar su listado de conversaciones

1. La trabajadora accede al listado de conversaciones
2. La trabajadora introduce texto en el campo de busqueda
3. El listado se filtra mostrando solo las conversaciones relevantes
4. Para borrar una conversacion, la trabajadora selecciona la opcion de borrado sobre la conversacion deseada
5. La aplicacion muestra un dialogo de confirmacion
6. Si la trabajadora confirma, la conversacion desaparece del listado

Estado de exito: La trabajadora encuentra o elimina conversaciones segun su necesidad.

Flujos alternativos:
- Si la trabajadora cancela el borrado: la conversacion permanece sin cambios

---

## Resultados y Exito

La feature de comunicacion se considera exitosa cuando:
- La trabajadora puede iniciar conversaciones con coordinacion de forma autonoma, seleccionando el asunto adecuado
- Los mensajes se envian y reciben en tiempo real sin necesidad de refrescar
- La trabajadora siempre percibe la conversacion como un chat con "Coordinacion" (el enrutamiento interno es transparente)
- Las conversaciones cerradas permanecen accesibles como historico de solo lectura
- La trabajadora puede buscar, localizar y borrar conversaciones de forma agil
- El contexto enlazado (servicio u oferta) facilita la gestion por parte de coordinacion sin requerir que la trabajadora explique detalles repetitivos

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Asuntos predefinidos**: La lista de asuntos disponibles al crear conversacion es: Vacaciones / Ausencia, Nomina / Facturacion, Sobre un servicio, Documentacion, Consulta general, Otros. Esta lista viene configurada desde el backoffice y puede evolucionar, pero en el MVP se muestra esta lista fija.

2. **Primer mensaje obligatorio**: No se puede crear una conversacion sin escribir al menos un mensaje inicial. La seleccion de asunto tambien es obligatoria.

3. **Interlocutor visible**: La trabajadora siempre ve "Coordinacion" como interlocutor. El enrutamiento interno por asunto a departamentos especificos es invisible para ella.

4. **Codigo de ticket**: Si el backend proporciona un codigo de ticket al crear la conversacion, se muestra en la cabecera junto al asunto. Si el backend no lo proporciona, la cabecera muestra solo el asunto.

5. **Enlace de contexto**: Al crear la conversacion, la trabajadora puede opcionalmente seleccionar un servicio u oferta como contexto. Este contexto se muestra en la cabecera y tambien puede enlazarse a mensajes individuales dentro del hilo.

6. **Orden del listado**: Las conversaciones se ordenan siempre por la marca de tiempo del ultimo mensaje, de mas reciente a mas antigua.

7. **Estado de lectura/no lectura**: Las conversaciones con mensajes no leidos se destacan visualmente (indicador prominente). Al abrir una conversacion, se marca automaticamente como leida.

8. **Conversaciones cerradas**: Solo el equipo de backoffice puede cerrar una conversacion. Una vez cerrada, la trabajadora puede consultar el historial completo pero no puede enviar nuevos mensajes. La conversacion cerrada se muestra con un indicador visual diferenciado en el listado.

9. **Borrado de conversaciones**: La trabajadora puede borrar cualquier conversacion (abierta o cerrada) de su listado. El borrado requiere confirmacion explicita. Una vez confirmado, la conversacion desaparece del listado de la trabajadora.

10. **Actualizacion en tiempo real**: Los mensajes nuevos aparecen automaticamente en la conversacion sin que la trabajadora tenga que refrescar la pantalla.

11. **Paginacion de mensajes**: Al abrir un hilo, se muestran los mensajes mas recientes. Al desplazar hacia arriba, se cargan bloques de mensajes mas antiguos progresivamente.

12. **Actualizacion manual del listado**: La trabajadora puede actualizar el listado de conversaciones mediante un gesto de arrastre hacia abajo.

13. **Solo mensajes de texto en el MVP**: Las conversaciones soportan unicamente mensajes de texto. El envio de adjuntos (imagenes, documentos) en el chat queda fuera del alcance de esta version.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Pantalla principal (home) | La trabajadora pulsa acceso directo de Comunicacion | Listado de conversaciones |
| Listado de conversaciones | La trabajadora pulsa "Nueva conversacion" | Pantalla de creacion de conversacion (seleccion de asunto + mensaje) |
| Listado de conversaciones | La trabajadora toca una conversacion abierta | Hilo de conversacion (con campo de entrada activo) |
| Listado de conversaciones | La trabajadora toca una conversacion cerrada | Hilo de conversacion (modo historico: sin campo de entrada, con aviso de "Conversacion cerrada") |
| Creacion de conversacion | La trabajadora envia el primer mensaje | Hilo de la conversacion recien creada |
| Notificacion push de nuevo mensaje | La trabajadora toca la notificacion | Hilo de la conversacion correspondiente |

---

## Criterios de Aceptacion

### CA-001: Creacion de conversacion con asunto predefinido <- HU-001
GIVEN la trabajadora accede a la pantalla de nueva conversacion
WHEN selecciona un asunto predefinido de la lista (Vacaciones / Ausencia, Nomina / Facturacion, Sobre un servicio, Documentacion, Consulta general, Otros)
THEN la aplicacion muestra el asunto seleccionado y habilita el campo de texto para escribir el primer mensaje

### CA-002: Primer mensaje obligatorio <- HU-001
GIVEN la trabajadora ha seleccionado un asunto para la nueva conversacion
WHEN intenta crear la conversacion sin escribir ningun mensaje
THEN la aplicacion le indica que el primer mensaje es obligatorio y no permite crear la conversacion

### CA-003: Enlace de contexto al crear conversacion <- HU-001
GIVEN la trabajadora esta creando una nueva conversacion
WHEN selecciona la opcion de enlazar contexto
THEN la aplicacion permite seleccionar un servicio u oferta de sus listas y lo asocia a la conversacion

### CA-004: Interlocutor visible como "Coordinacion" <- HU-001
GIVEN la trabajadora ha creado una conversacion o accede a una existente
WHEN visualiza la cabecera de la conversacion
THEN el interlocutor se muestra como "Coordinacion" independientemente de a que departamento se haya enrutado internamente

### CA-005: Codigo de ticket en cabecera <- HU-001
GIVEN la trabajadora ha creado una conversacion y el sistema asigna un codigo de ticket
WHEN visualiza la cabecera de la conversacion
THEN el codigo de ticket se muestra junto al asunto en la cabecera

### CA-006: Listado de conversaciones en orden cronologico <- HU-002
GIVEN la trabajadora tiene varias conversaciones
WHEN accede al listado de conversaciones
THEN las conversaciones se muestran ordenadas de mas reciente a mas antigua segun la marca de tiempo del ultimo mensaje, mostrando asunto, previsualizacion del ultimo mensaje y marca de tiempo

### CA-007: Indicador de mensajes no leidos <- HU-002
GIVEN la trabajadora tiene conversaciones con mensajes nuevos que no ha leido
WHEN accede al listado de conversaciones
THEN las conversaciones con mensajes no leidos se destacan visualmente con un indicador prominente

### CA-008: Indicador de conversacion cerrada <- HU-002
GIVEN una conversacion ha sido cerrada por el equipo de backoffice
WHEN la trabajadora ve esa conversacion en el listado
THEN se muestra un indicador visual diferenciado (etiqueta "Cerrada" o icono de candado) que la distingue de las conversaciones abiertas

### CA-009: Marcado automatico como leida <- HU-002
GIVEN la trabajadora tiene una conversacion con mensajes no leidos
WHEN abre esa conversacion
THEN la conversacion se marca automaticamente como leida y el indicador de no leido desaparece del listado

### CA-010: Envio de mensaje en conversacion abierta <- HU-003
GIVEN la trabajadora tiene abierto el hilo de una conversacion con estado "abierta"
WHEN escribe un mensaje en el campo de entrada y pulsa enviar
THEN el mensaje aparece inmediatamente en el hilo con marca de tiempo y estado de entrega

### CA-011: Recepcion de mensajes en tiempo real <- HU-003
GIVEN la trabajadora tiene abierto el hilo de una conversacion
WHEN coordinacion envia un nuevo mensaje en esa conversacion
THEN el mensaje aparece automaticamente en el hilo sin que la trabajadora tenga que refrescar la pantalla

### CA-012: Diferenciacion visual de mensajes <- HU-003
GIVEN la trabajadora esta visualizando un hilo de conversacion
WHEN hay mensajes tanto de la trabajadora como de coordinacion
THEN los mensajes se diferencian visualmente por alineacion y color, distinguiendo claramente quien envio cada mensaje

### CA-013: Estado de entrega y lectura <- HU-003
GIVEN la trabajadora ha enviado un mensaje en una conversacion
WHEN visualiza ese mensaje en el hilo
THEN se muestra el estado de entrega/lectura del mensaje (enviado, entregado, leido)

### CA-014: Desplazamiento automatico al ultimo mensaje <- HU-003
GIVEN la trabajadora abre un hilo de conversacion
WHEN el hilo contiene mensajes
THEN la aplicacion se desplaza automaticamente al mensaje mas reciente

### CA-015: Carga de mensajes antiguos por paginacion <- HU-003
GIVEN la trabajadora esta en un hilo de conversacion con muchos mensajes
WHEN desplaza hacia arriba hasta el inicio de los mensajes cargados
THEN la aplicacion carga y muestra un bloque adicional de mensajes mas antiguos

### CA-016: Conversacion cerrada en modo solo lectura <- HU-004
GIVEN la trabajadora abre una conversacion que ha sido cerrada por backoffice
WHEN visualiza el hilo de la conversacion
THEN se muestran todos los mensajes del historial, el campo de entrada de texto no aparece y se muestra un aviso de "Conversacion cerrada"

### CA-017: Busqueda de conversaciones <- HU-005
GIVEN la trabajadora esta en el listado de conversaciones
WHEN introduce texto en el campo de busqueda
THEN el listado se filtra mostrando solo las conversaciones cuyo asunto o contenido coincida con el texto buscado

### CA-018: Borrado de conversacion con confirmacion <- HU-005
GIVEN la trabajadora quiere borrar una conversacion del listado
WHEN selecciona la opcion de borrado sobre una conversacion
THEN la aplicacion muestra un dialogo de confirmacion y solo borra la conversacion si la trabajadora confirma explicitamente

### CA-019: Actualizacion manual del listado <- HU-002
GIVEN la trabajadora esta en el listado de conversaciones
WHEN realiza un gesto de arrastre hacia abajo
THEN el listado se actualiza con las conversaciones y estados mas recientes

### CA-020: Estado vacio sin conversaciones <- HU-002
GIVEN la trabajadora no tiene ninguna conversacion
WHEN accede al listado de conversaciones
THEN la aplicacion muestra un estado vacio con un mensaje informativo y una opcion para iniciar nueva conversacion

---

## Checklist de Validacion

- [x] Actores identificados (Trabajadora y Coordinacion)
- [x] Flujos principales descritos paso a paso (5 journeys)
- [x] Estados de exito definidos para cada flujo
- [x] Edge cases documentados (estado vacio, conversacion cerrada, busqueda sin resultados, enlace de contexto opcional, codigo de ticket opcional)
- [x] Estados de error definidos (primer mensaje vacio, asunto no seleccionado)
- [x] Ambiguedades resueltas (solo texto en MVP, interlocutor siempre "Coordinacion", enrutamiento transparente)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- **Envio de adjuntos en conversaciones**: en el MVP, las conversaciones solo soportan mensajes de texto. El envio de imagenes, documentos u otros archivos adjuntos dentro del chat queda excluido de esta version.
- **Creacion o cierre de conversaciones desde la app de la trabajadora**: las conversaciones solo pueden ser cerradas desde el backoffice. La trabajadora puede borrar conversaciones de su listado pero no cerrarlas formalmente.
- **Enrutamiento visible por departamento**: la trabajadora no ve a que departamento se enruta su conversacion. El enrutamiento es gestionado internamente por el backoffice.
- **Videollamadas o llamadas de voz**: la comunicacion se limita a mensajes de texto en formato chat.
- **Notificaciones de escritura en tiempo real ("esta escribiendo...")**: no se incluyen indicadores de escritura en curso.

---

## Asunciones Aplicadas

- **[A-001]**: Las conversaciones solo soportan mensajes de texto en el MVP. El envio de adjuntos (imagenes, documentos) en el chat queda fuera del alcance inicial. Basado en gap [P-013][INFORMATIVO] del analysis, cuya asuncion por defecto es: "En el MVP, las conversaciones solo soportan mensajes de texto."
