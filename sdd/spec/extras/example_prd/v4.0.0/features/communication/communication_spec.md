# Spec: Communication
> Versión: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-011 via prd-hogar-sad_discovery.md)
> Feature ID: F-011
> Spec monolítico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|-----------------------------|
| Trabajadora Hogar | Cuidadora contratada a través de CUIDEO que usa la app Hogar | Iniciar conversación con coordinación, ver historial de conversaciones, leer y responder mensajes en hilos abiertos, buscar y borrar conversaciones |
| Trabajadora SAD | Cuidadora contratada a través de Felizvita que usa la app SAD | Iniciar conversación con coordinación, ver historial de conversaciones, leer y responder mensajes en hilos abiertos, buscar y borrar conversaciones |
| Coordinación (back-office) | Equipo interno que gestiona las conversaciones desde el backoffice | Recibir conversaciones enrutadas por asunto, cerrar conversaciones (acción que convierte el hilo en solo lectura para la trabajadora) |

> Nota: La Coordinación no opera desde la app móvil. Su capacidad de cerrar conversaciones impacta el comportamiento de la app pero se gestiona desde el backoffice. Se incluye como actor para claridad de los journeys.

---

## Historias de Usuario

### HU-001: Iniciar conversación con coordinación
Como trabajadora (Hogar o SAD)
quiero iniciar una conversación con coordinación seleccionando un asunto predefinido
para que mi consulta llegue al departamento correcto sin que tenga que conocer la estructura interna del equipo

### HU-002: Enlazar contexto a una conversación
Como trabajadora (Hogar o SAD)
quiero poder vincular un servicio o una oferta a la conversación que estoy iniciando
para que coordinación tenga el contexto necesario para gestionar mi consulta más rápidamente

### HU-003: Ver listado de conversaciones
Como trabajadora (Hogar o SAD)
quiero ver todas mis conversaciones con coordinación ordenadas por actividad reciente
para que pueda identificar rápidamente cuáles tienen mensajes nuevos y cuáles están cerradas

### HU-004: Buscar y borrar conversaciones
Como trabajadora (Hogar o SAD)
quiero buscar entre mis conversaciones y poder borrar las que ya no necesito
para que mantener mi historial de comunicaciones ordenado y encontrar fácilmente lo que busco

### HU-005: Leer y responder mensajes en un hilo abierto
Como trabajadora (Hogar o SAD)
quiero abrir un hilo de conversación activo y enviar mensajes a coordinación
para que pueda mantener una comunicación fluida sobre mi consulta

### HU-006: Consultar historial de una conversación cerrada
Como trabajadora (Hogar o SAD)
quiero poder leer el historial completo de una conversación cerrada por coordinación
para que pueda consultar decisiones o información comunicada en el pasado

### HU-007: Recibir mensajes en tiempo real
Como trabajadora (Hogar o SAD)
quiero que los mensajes nuevos de coordinación aparezcan en el hilo de conversación sin tener que actualizar manualmente
para que no me pierda ninguna respuesta durante una conversación activa

---

## Recorridos de Usuario

### Journey 1: Iniciar nueva conversación con asunto y contexto opcional
Actor: Trabajadora (Hogar o SAD) | Objetivo: Comunicar una consulta a coordinación

1. La trabajadora accede a la sección de Comunicación desde el menú principal.
2. Pulsa el botón para iniciar una nueva conversación.
3. Se presenta una pantalla con la selección de asunto predefinido: Vacaciones / Ausencia, Nómina / Facturación, Sobre un servicio, Documentación, Consulta general, Otros.
4. La trabajadora selecciona el asunto que mejor describe su consulta.
5. Opcionalmente, la trabajadora enlaza contexto: selecciona un servicio o una oferta relacionada.
6. La trabajadora escribe el primer mensaje (obligatorio para crear la conversación).
7. La trabajadora pulsa "Enviar". La conversación se crea y el hilo se abre mostrando el mensaje enviado.
8. La cabecera del hilo muestra el asunto seleccionado y "Coordinación" como interlocutor.

Estado de éxito: La conversación aparece en el listado de conversaciones como la más reciente. El asunto es visible en la cabecera del hilo. El primer mensaje se muestra enviado.

Flujos alternativos:
- Si la trabajadora no escribe ningún mensaje y pulsa "Enviar" → el sistema muestra un aviso de que el primer mensaje es obligatorio y no crea la conversación.
- Si la trabajadora abandona el flujo antes de enviar → no se crea ninguna conversación.

---

### Journey 2: Ver listado de conversaciones y abrir un hilo
Actor: Trabajadora (Hogar o SAD) | Objetivo: Acceder a una conversación existente

1. La trabajadora accede a la sección de Comunicación.
2. Ve el listado de conversaciones ordenado por fecha del último mensaje (más reciente primero).
3. Cada conversación muestra: asunto, previsualización del último mensaje y marca de tiempo.
4. Las conversaciones con mensajes no leídos aparecen resaltadas (texto en negrita, indicador visual).
5. Las conversaciones cerradas muestran un indicador diferenciado ("Cerrada" o icono de candado).
6. La trabajadora toca una conversación para abrir el hilo.

Estado de éxito: El hilo se abre mostrando todos los mensajes en orden cronológico. Si la conversación tenía mensajes no leídos, el indicador desaparece al abrir el hilo.

Flujos alternativos:
- Si la trabajadora no tiene conversaciones → se muestra un estado vacío con opción de iniciar la primera conversación.
- Deslizar hacia abajo (pull-to-refresh) → actualiza el listado con las conversaciones más recientes.

---

### Journey 3: Leer y responder en un hilo abierto
Actor: Trabajadora (Hogar o SAD) | Objetivo: Mantener comunicación activa con coordinación

1. La trabajadora abre un hilo de conversación en estado abierto.
2. Ve todos los mensajes en orden cronológico: los suyos (alineados a la derecha) y los de coordinación (alineados a la izquierda).
3. Cada mensaje muestra su marca de tiempo y, para los mensajes de la trabajadora, el estado de entrega/lectura.
4. Al desplazarse hacia arriba, se cargan automáticamente mensajes más antiguos (paginación).
5. Al abrir el hilo, la vista se desplaza automáticamente al último mensaje.
6. La trabajadora escribe un nuevo mensaje en el campo de texto de la parte inferior.
7. Pulsa "Enviar". El mensaje aparece inmediatamente en el hilo.
8. Los mensajes nuevos de coordinación aparecen en tiempo real sin necesidad de actualizar manualmente.

Estado de éxito: El mensaje se muestra en el hilo con estado de entrega. El hilo refleja en tiempo real cualquier mensaje nuevo de coordinación.

---

### Journey 4: Consultar historial de conversación cerrada
Actor: Trabajadora (Hogar o SAD) | Objetivo: Consultar el historial de una conversación ya cerrada

1. La trabajadora abre una conversación marcada como cerrada en el listado.
2. El hilo se abre en modo solo lectura: todos los mensajes son visibles en orden cronológico.
3. La parte inferior muestra el aviso "Conversación cerrada" en lugar del campo de texto.
4. La trabajadora puede desplazarse por el historial y cargar mensajes más antiguos, pero no puede escribir.

Estado de éxito: La trabajadora puede consultar el contenido completo de la conversación sin posibilidad de escribir nuevos mensajes.

---

### Journey 5: Buscar y borrar conversación
Actor: Trabajadora (Hogar o SAD) | Objetivo: Encontrar o eliminar conversaciones del historial

1. La trabajadora accede al listado de conversaciones.
2. Usa la función de búsqueda para filtrar conversaciones por texto (asunto o contenido del último mensaje).
3. Los resultados se filtran en tiempo real o al confirmar la búsqueda.
4. Para borrar una conversación, la trabajadora selecciona la opción de borrar (por ejemplo, deslizando o desde el menú de la conversación).
5. Se muestra un diálogo de confirmación antes de borrar.
6. Al confirmar, la conversación desaparece del listado.

Estado de éxito: La conversación eliminada ya no aparece en el listado. El badge de mensajes no leídos se actualiza inmediatamente si la conversación borrada tenía mensajes no leídos.

---

## Resultados y Éxito

La feature de Comunicación se considera completa cuando:

- La trabajadora puede iniciar conversaciones con coordinación seleccionando un asunto predefinido, con primer mensaje obligatorio.
- Las conversaciones enlazadas con contexto (servicio u oferta) llegan a coordinación con dicha información disponible.
- El listado de conversaciones refleja el estado real (abierta/cerrada) y los indicadores de mensajes no leídos.
- Los hilos de conversación abiertos permiten enviar y recibir mensajes en tiempo real.
- Los hilos cerrados son consultables en modo solo lectura con aviso claro del estado.
- La búsqueda de conversaciones funciona y el borrado requiere confirmación explícita.
- Al marcar una conversación como leída (al abrirla), el indicador de no leído desaparece.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Punto de entrada único a coordinación**: La trabajadora siempre ve el interlocutor como "Coordinación", independientemente del departamento interno al que el backoffice enrute la conversación. El enrutado es completamente transparente para la trabajadora.

2. **Asuntos predefinidos**: Los asuntos disponibles al crear una conversación son exactamente los siguientes (sin posibilidad de escribir un asunto libre): Vacaciones / Ausencia, Nómina / Facturación, Sobre un servicio, Documentación, Consulta general, Otros.

3. **Primer mensaje obligatorio**: No se puede crear una conversación sin escribir al menos un mensaje. El botón de envío permanece inactivo o muestra error si el campo está vacío.

4. **Estado de conversación — Abierta vs. Cerrada**: El estado de la conversación lo controla exclusivamente el backoffice. La trabajadora no puede abrir ni cerrar conversaciones. Una conversación cerrada pasa a modo solo lectura: el campo de texto desaparece y se muestra el aviso "Conversación cerrada".

5. **Mensajes en tiempo real**: Los mensajes nuevos de coordinación aparecen en el hilo sin que la trabajadora tenga que actualizar manualmente la pantalla. Esta actualización ocurre siempre que la trabajadora tenga el hilo abierto.

6. **Paginación de mensajes**: El hilo carga los mensajes más recientes al abrirse y carga mensajes anteriores al desplazarse hacia arriba. No se cargan todos los mensajes de golpe.

7. **Desplazamiento automático**: Al abrir un hilo o al recibir un mensaje nuevo mientras el hilo está abierto, la vista se desplaza automáticamente al último mensaje.

8. **Estado de entrega/lectura**: Solo se muestran estados de entrega/lectura para los mensajes enviados por la trabajadora. Los mensajes de coordinación no muestran estado de lectura.

9. **Enlace de contexto**: Al crear una conversación, la trabajadora puede enlazar un servicio o una oferta como contexto. Esta vinculación es opcional. Si se selecciona "Sobre un servicio" como asunto, se recomienda (pero no se obliga) enlazar el servicio correspondiente.

10. **Borrado de conversaciones**: Borrar una conversación requiere confirmación explícita. Una vez borrada, no se puede recuperar desde la app. El badge de mensajes no leídos se actualiza inmediatamente.

11. **Indicadores de no leído**: Al abrir una conversación, todos sus mensajes pasan a estado leído. El indicador de no leído del listado desaparece al abrir el hilo, sin necesidad de ninguna acción adicional de la trabajadora.

12. **Código de ticket**: Si el backend proporciona un código de ticket al crear la conversación, se muestra en la cabecera del hilo. Si no lo proporciona, no se muestra ningún elemento en ese espacio.

### Destinos de navegación

| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Menú principal / Tab bar | Tocar icono de Comunicación | Listado de conversaciones |
| Listado de conversaciones | Tocar conversación abierta | Hilo de conversación (modo escritura activo) |
| Listado de conversaciones | Tocar conversación cerrada | Hilo de conversación (modo solo lectura) |
| Listado de conversaciones | Tocar botón "Nueva conversación" | Pantalla de selección de asunto |
| Pantalla de selección de asunto | Seleccionar asunto + escribir mensaje + enviar | Hilo de la conversación recién creada |
| Notificación push (nuevo mensaje) | Tocar notificación | Hilo de la conversación correspondiente |
| Notificación push (conversación cerrada) | Tocar notificación | Hilo de la conversación en modo solo lectura |
| Hilo de conversación | Pulsar botón atrás | Listado de conversaciones |

---

## Criterios de Aceptación

### CA-001: Selección de asunto obligatoria al crear conversación ← HU-001
GIVEN la trabajadora está en la pantalla de nueva conversación
WHEN intenta enviar sin haber seleccionado un asunto
THEN el sistema no crea la conversación y muestra un aviso indicando que el asunto es obligatorio

### CA-002: Asuntos predefinidos disponibles ← HU-001
GIVEN la trabajadora inicia una nueva conversación
WHEN se muestra la selección de asunto
THEN se presentan exactamente estos 6 asuntos: "Vacaciones / Ausencia", "Nómina / Facturación", "Sobre un servicio", "Documentación", "Consulta general", "Otros"

### CA-003: Primer mensaje obligatorio para crear conversación ← HU-001
GIVEN la trabajadora ha seleccionado un asunto pero no ha escrito ningún mensaje
WHEN intenta enviar la conversación
THEN el sistema no crea la conversación y muestra un aviso indicando que el primer mensaje es obligatorio

### CA-004: Conversación creada correctamente ← HU-001
GIVEN la trabajadora ha seleccionado un asunto y ha escrito al menos un mensaje
WHEN pulsa "Enviar"
THEN la conversación se crea, el hilo se abre mostrando el mensaje enviado, la cabecera muestra el asunto seleccionado y "Coordinación" como interlocutor, y la nueva conversación aparece en la primera posición del listado

### CA-005: Enlace de contexto opcional ← HU-002
GIVEN la trabajadora está creando una nueva conversación
WHEN elige enlazar un servicio o una oferta como contexto
THEN el sistema asocia esa entidad a la conversación y el contexto es visible en el hilo (enlace o referencia al servicio/oferta)

### CA-006: Conversación sin contexto ← HU-002
GIVEN la trabajadora está creando una nueva conversación
WHEN no enlaza ningún contexto
THEN la conversación se crea correctamente sin ningún elemento de contexto asociado

### CA-007: Listado de conversaciones en orden cronológico inverso ← HU-003
GIVEN la trabajadora tiene conversaciones existentes
WHEN accede a la sección de Comunicación
THEN ve el listado ordenado por fecha del último mensaje, de más reciente a más antigua

### CA-008: Información visible en tarjeta de conversación ← HU-003
GIVEN la trabajadora ve el listado de conversaciones
WHEN observa una tarjeta de conversación
THEN puede ver el asunto de la conversación, la previsualización del último mensaje y la marca de tiempo de ese mensaje

### CA-009: Indicador visual de mensajes no leídos ← HU-003
GIVEN existe al menos una conversación con mensajes no leídos
WHEN la trabajadora ve el listado de conversaciones
THEN esa conversación aparece visualmente resaltada (texto en negrita o indicador equivalente) diferenciándose de las conversaciones ya leídas

### CA-010: Indicador visual de conversación cerrada ← HU-003
GIVEN existe al menos una conversación cerrada por coordinación
WHEN la trabajadora ve el listado de conversaciones
THEN esa conversación muestra un indicador diferenciado respecto a las conversaciones abiertas (etiqueta "Cerrada" o icono equivalente)

### CA-011: Pull-to-refresh en el listado ← HU-003
GIVEN la trabajadora está en el listado de conversaciones
WHEN desliza hacia abajo para refrescar
THEN el listado se actualiza con el estado más reciente de todas las conversaciones

### CA-012: Estado vacío en listado sin conversaciones ← HU-003
GIVEN la trabajadora no tiene ninguna conversación
WHEN accede a la sección de Comunicación
THEN se muestra un estado vacío con la opción de iniciar la primera conversación

### CA-013: Búsqueda de conversaciones ← HU-004
GIVEN la trabajadora está en el listado de conversaciones
WHEN escribe texto en el campo de búsqueda
THEN el listado se filtra mostrando solo las conversaciones que coinciden con el texto buscado (por asunto o previsualización del último mensaje)

### CA-014: Sin resultados en búsqueda ← HU-004
GIVEN la trabajadora realiza una búsqueda
WHEN ninguna conversación coincide con el texto buscado
THEN se muestra un estado vacío de búsqueda indicando que no hay resultados

### CA-015: Borrado de conversación con confirmación ← HU-004
GIVEN la trabajadora selecciona la opción de borrar una conversación
WHEN se muestra el diálogo de confirmación
THEN puede cancelar (la conversación permanece) o confirmar (la conversación desaparece del listado inmediatamente)

### CA-016: Badge actualizado tras borrar conversación con mensajes no leídos ← HU-004
GIVEN la trabajadora borra una conversación que tenía mensajes no leídos
WHEN confirma el borrado
THEN el badge o contador de mensajes no leídos de la sección de Comunicación se actualiza inmediatamente

### CA-017: Mensajes en orden cronológico en el hilo ← HU-005
GIVEN la trabajadora abre un hilo de conversación abierto
WHEN se carga el hilo
THEN los mensajes se muestran en orden cronológico ascendente (el más antiguo arriba, el más reciente abajo)

### CA-018: Diferenciación visual de mensajes propios y de coordinación ← HU-005
GIVEN la trabajadora está en un hilo de conversación
WHEN observa los mensajes
THEN sus propios mensajes están alineados a la derecha y los mensajes de coordinación a la izquierda, con estilos visuales diferenciados

### CA-019: Marca de tiempo en cada mensaje ← HU-005
GIVEN la trabajadora está en un hilo de conversación
WHEN observa cualquier mensaje
THEN ese mensaje muestra su marca de tiempo (fecha y hora de envío)

### CA-020: Estado de entrega/lectura en mensajes enviados ← HU-005
GIVEN la trabajadora ha enviado al menos un mensaje en el hilo
WHEN observa sus mensajes enviados
THEN cada mensaje muestra su estado de entrega/lectura (enviado, entregado, leído)

### CA-021: Campo de texto disponible en conversación abierta ← HU-005
GIVEN la trabajadora abre un hilo de conversación en estado abierto
WHEN ve la parte inferior del hilo
THEN hay un campo de texto activo y un botón de enviar disponibles

### CA-022: Envío de mensaje en hilo abierto ← HU-005
GIVEN la trabajadora ha escrito un mensaje en el campo de texto del hilo
WHEN pulsa el botón de enviar
THEN el mensaje aparece inmediatamente en el hilo y el campo de texto queda vacío

### CA-023: Desplazamiento automático al último mensaje ← HU-005
GIVEN la trabajadora abre un hilo de conversación
WHEN el hilo termina de cargar
THEN la vista se desplaza automáticamente al mensaje más reciente

### CA-024: Paginación de mensajes antiguos ← HU-005
GIVEN la trabajadora está en un hilo de conversación con más mensajes de los que caben en pantalla
WHEN se desplaza hacia arriba hasta el inicio de los mensajes visibles
THEN el sistema carga automáticamente mensajes anteriores sin que la trabajadora tenga que realizar ninguna acción adicional

### CA-025: Mensajes en tiempo real ← HU-007
GIVEN la trabajadora tiene el hilo de conversación abierto
WHEN coordinación envía un mensaje nuevo
THEN ese mensaje aparece en el hilo sin que la trabajadora tenga que actualizar manualmente, y la vista se desplaza al nuevo mensaje

### CA-026: Hilo cerrado en modo solo lectura ← HU-006
GIVEN la trabajadora abre una conversación cerrada por coordinación
WHEN se carga el hilo
THEN no hay campo de texto ni botón de enviar, se muestra el aviso "Conversación cerrada", y todos los mensajes históricos son visibles y navegables

### CA-027: Mensajes de una conversación cerrada accesibles ← HU-006
GIVEN la trabajadora está en un hilo de conversación cerrada
WHEN se desplaza hacia arriba
THEN puede cargar y leer todos los mensajes históricos de la conversación (misma paginación que en conversaciones abiertas)

### CA-028: Marcar conversación como leída al abrirla ← HU-003, HU-005
GIVEN la trabajadora abre una conversación que tenía mensajes no leídos
WHEN el hilo se carga
THEN los mensajes pasan a estado leído y el indicador de no leído desaparece del listado de conversaciones

---

## Checklist de Validación

- [x] Actores identificados (Trabajadora Hogar, Trabajadora SAD, Coordinación)
- [x] Flujos principales descritos paso a paso (5 journeys completos)
- [x] Estados de éxito definidos para cada journey
- [x] Edge cases documentados (conversación sin asunto, sin mensaje, conversación cerrada, búsqueda sin resultados, estado vacío)
- [x] Estados de error definidos (mensaje obligatorio, asunto obligatorio, confirmación de borrado)
- [x] Ambigüedades resueltas (código de ticket opcional, contexto opcional, enrutado transparente)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes

---

## Fuera de Alcance

- **Mensajes del sistema (RF-2.3)**: Los mensajes de solo lectura enviados por administración (avisos del sistema) son gestionados en la feature `home-dashboard` (F-002), no en esta feature de comunicación bidireccional.
- **Gestión de notificaciones push**: El registro del dispositivo, la entrega de notificaciones push y el historial de notificaciones son responsabilidad de la feature `push-notifications` (F-009). Esta feature solo recibe el deeplink resultante de una notificación de mensaje nuevo o conversación cerrada.
- **Comunicación con otras trabajadoras**: El chat es exclusivamente entre la trabajadora y coordinación. No existe mensajería entre trabajadoras.
- **Archivos adjuntos en mensajes**: El PRD no especifica soporte de adjuntos en los mensajes del chat. Queda fuera de este spec. Si se requiere en el futuro, se gestionará vía delta.
- **Historial de notificaciones push**: La visualización del listado de notificaciones push recibidas pertenece a `push-notifications` (F-009).
- **Cierre de conversaciones desde la app**: La trabajadora no puede cerrar conversaciones. Esta acción es exclusiva del backoffice.
- **Creación de asuntos personalizados**: La trabajadora no puede escribir un asunto libre. Solo puede seleccionar de los 6 asuntos predefinidos.

---

## Asunciones Aplicadas

- **[A-001]**: El campo "código de ticket" en la cabecera del hilo es opcional. Si el backend no lo proporciona en la respuesta de creación de conversación, no se muestra ningún elemento en ese espacio de la cabecera. Justificación: el PRD indica "opcionalmente, mostrar un código de ticket si el backend lo proporciona", lo que implica que su ausencia es un estado válido. Se aplica la asunción más conservadora.

- **[A-002]**: No se especifica un límite de caracteres para el cuerpo del mensaje en el PRD. Se asume un límite de 2000 caracteres por mensaje, que es el comportamiento más conservador para aplicaciones de mensajería profesional. Si el cliente requiere un límite distinto, debe especificarlo.

- **[A-003]**: Al borrar una conversación con mensajes no leídos, el badge o contador de la sección de Comunicación (en el menú principal o tab bar) se actualiza inmediatamente al confirmar el borrado, sin necesidad de refrescar manualmente. Justificación: comportamiento conservador y esperado por usabilidad.
