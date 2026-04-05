# Spec: Availability Management
> Version: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-009 via prd-hogar-sad_discovery.md)
> Feature ID: F-009
> Spec monolitico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora | Profesional de cuidado (perfil Hogar o SAD) con sesion activa en la aplicacion | Visualizar calendario semanal de disponibilidad, crear slots mediante franjas rapidas o personalizados, editar y eliminar slots propios, consultar horas contratadas vs trabajadas |

---

## Historias de Usuario

### HU-001: Visualizar mi disponibilidad semanal
Como trabajadora
quiero ver mi calendario semanal con todos mis slots de disponibilidad, no disponibilidad y servicios activos asignados
para que pueda tener una vision clara de mi semana y decidir donde necesito declarar mas disponibilidad.

### HU-002: Crear un slot de disponibilidad mediante franja rapida
Como trabajadora
quiero crear rapidamente un slot de disponibilidad pulsando una franja predefinida (Manana, Tarde, Noche, Interna, Finde) para un dia seleccionado
para que pueda declarar mi disponibilidad de forma agil sin tener que introducir horas manualmente.

### HU-003: Crear un slot personalizado con horas especificas
Como trabajadora
quiero crear un slot con hora de inicio y fin personalizadas y elegir si es de tipo Disponible o No disponible
para que pueda declarar disponibilidad o excepciones en rangos horarios especificos que no coinciden con las franjas rapidas.

### HU-004: Editar o eliminar un slot existente
Como trabajadora
quiero poder editar las horas o el tipo de un slot que he creado, o eliminarlo si ya no aplica
para que mi disponibilidad refleje siempre mi situacion real.

### HU-005: Consultar mis horas contratadas frente a trabajadas
Como trabajadora
quiero ver en la cabecera del calendario cuantas horas he trabajado respecto a mis horas de contrato
para que sepa si necesito declarar mas disponibilidad para completar mis horas.

---

## Recorridos de Usuario

### Journey 1: Visualizar el calendario semanal de disponibilidad
Actor: Trabajadora | Objetivo: Conocer su disponibilidad declarada y servicios asignados de la semana

1. La trabajadora accede a la seccion "Mi Disponibilidad" desde el menu principal o un acceso directo en la home.
2. La aplicacion muestra la cabecera con las horas trabajadas frente a las horas de contrato (ej: "30 / 40 h" o "Te faltan 10 horas").
3. Debajo se muestra el calendario semanal (Lunes a Domingo) con todos los slots existentes como bloques horarios diferenciados por color segun tipo: Disponible, No disponible, Activa.
4. Los slots de distintos tipos pueden aparecer solapados visualmente en el calendario.
5. La trabajadora puede desplazarse entre semanas o usar pull-to-refresh para sincronizar con el servidor.

Estado de exito: La trabajadora ve su semana completa con todos los slots de disponibilidad, no disponibilidad y servicios activos diferenciados visualmente, y sabe cuantas horas le faltan respecto a su contrato.
Flujos alternativos: Si no hay slots creados para la semana, el calendario se muestra vacio con un mensaje invitando a declarar disponibilidad.

### Journey 2: Crear un slot con franja rapida
Actor: Trabajadora | Objetivo: Declarar disponibilidad rapidamente usando una franja predefinida

1. La trabajadora selecciona un dia en el calendario semanal.
2. Se activa el panel de franjas rapidas con los botones: Manana, Tarde, Noche, Interna, Finde.
3. La trabajadora pulsa una franja (ej: "Manana").
4. Se crea inmediatamente un slot de tipo "Disponible" con el rango horario correspondiente a esa franja para el dia seleccionado.
5. El slot aparece en el calendario como un bloque horario verde (o color de tipo Disponible).
6. El cambio se guarda de forma inmediata.

Estado de exito: El slot de franja rapida aparece en el calendario del dia seleccionado y esta guardado en el servidor.
Flujos alternativos: Si el slot generado por la franja rapida se solapa con otro slot existente del mismo tipo (Disponible), la aplicacion muestra un mensaje de error indicando el solapamiento.

### Journey 3: Crear un slot personalizado
Actor: Trabajadora | Objetivo: Declarar disponibilidad o no disponibilidad en un rango horario especifico

1. La trabajadora selecciona un dia en el calendario semanal.
2. Se muestra el formulario de creacion de slot personalizado junto con el panel de franjas rapidas.
3. La trabajadora introduce hora de inicio y hora de fin mediante selectores de hora.
4. La trabajadora elige el tipo: Disponible o No disponible.
5. La trabajadora confirma la creacion del slot.
6. El slot aparece en el calendario con el color correspondiente a su tipo.
7. El cambio se guarda de forma inmediata.

Estado de exito: El slot personalizado aparece en el calendario y esta guardado en el servidor.
Flujos alternativos:
- Si el slot se solapa con otro slot del mismo tipo en el mismo dia, la aplicacion muestra un mensaje de error y no crea el slot.
- Si el slot de tipo "No disponible" se solapa con un slot "Disponible", se permite la creacion (solapamiento entre tipos distintos es valido).

### Journey 4: Editar o eliminar un slot existente
Actor: Trabajadora | Objetivo: Modificar o borrar un slot que ya no refleja su disponibilidad real

1. La trabajadora toca un slot de tipo "Disponible" o "No disponible" en el calendario.
2. Se muestra la informacion del slot con opciones para editar (modificar hora inicio/fin o tipo) o eliminar.
3a. Si elige editar: modifica los campos deseados, confirma, y el slot se actualiza inmediatamente.
3b. Si elige eliminar: confirma la eliminacion y el slot desaparece del calendario.
4. El cambio se guarda de forma inmediata.

Estado de exito: El slot editado refleja los nuevos valores, o el slot eliminado ya no aparece en el calendario.
Flujos alternativos:
- Si la trabajadora toca un slot de tipo "Activa" (servicio asignado), solo se muestra la informacion del servicio sin opciones de edicion ni eliminacion.
- Si la edicion genera un solapamiento con otro slot del mismo tipo, la aplicacion muestra un mensaje de error y no aplica el cambio.

### Journey 5: Consultar horas contratadas vs trabajadas
Actor: Trabajadora | Objetivo: Saber si necesita declarar mas disponibilidad

1. La trabajadora accede a la seccion "Mi Disponibilidad".
2. En la cabecera, ve de forma prominente sus horas trabajadas frente a las horas de contrato (ej: "30 / 40 h").
3. Si le faltan horas, ve un mensaje indicativo (ej: "Te faltan 10 horas").

Estado de exito: La trabajadora conoce su situacion de horas y puede decidir si declarar mas disponibilidad.

---

## Resultados y Exito

La feature se considera completa cuando:
- La trabajadora puede visualizar su calendario semanal con los tres tipos de slots diferenciados visualmente
- La trabajadora puede crear slots mediante franjas rapidas con un solo toque
- La trabajadora puede crear slots personalizados con hora de inicio, hora de fin y tipo
- La trabajadora puede editar y eliminar sus propios slots (Disponible y No disponible)
- Los slots de tipo Activa se muestran como solo lectura
- Se impiden solapamientos entre slots del mismo tipo en el mismo dia
- Se permiten solapamientos entre slots de distinto tipo
- La cabecera muestra de forma prominente las horas trabajadas frente a las contratadas
- Los cambios se guardan de forma inmediata al confirmar cada accion
- Se envia un recordatorio si la disponibilidad no se actualiza en 30 dias

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Tipos de slot y editabilidad**: Existen tres tipos de entradas en el calendario:
   - **Disponible**: declarado por la trabajadora. Editable y eliminable.
   - **No disponible**: declarado por la trabajadora como excepcion dentro de un rango de disponibilidad. Editable y eliminable.
   - **Activa**: asignado por el sistema de planificacion (servicio programado). Solo lectura: no se puede editar ni eliminar desde la aplicacion.

2. **Solapamiento entre tipos**: Los slots de distintos tipos pueden solaparse (ej: un slot "No disponible" de 10:00 a 12:00 dentro de un slot "Disponible" de 08:00 a 16:00). Los slots del mismo tipo no pueden solaparse en el mismo dia; si se intenta, la aplicacion muestra un mensaje de error.

3. **Prioridad de no disponibilidad**: Un slot de tipo "No disponible" bloquea la asignacion de servicios en ese rango horario, aunque haya disponibilidad declarada en la misma franja. Esta logica la gestiona el servidor.

4. **Franjas rapidas disponibles**: Manana, Tarde, Noche, Interna, Finde. La franja Madrugada esta eliminada. Al pulsar una franja rapida se crea un slot de tipo "Disponible" con el rango horario correspondiente.

5. **Guardado inmediato**: Cada creacion, edicion o eliminacion de slot se guarda de forma inmediata al confirmar. No existe un boton "guardar todo".

6. **Sin drag & drop**: Toda la interaccion es mediante seleccion de dia + inputs (selectores de hora, botones de franja rapida). No se implementa arrastrar y soltar.

7. **Ventana operativa**: La ventana operativa de cada dia esta basada en 12 horas desde el inicio de jornada, respetando el descanso minimo legal. Esta logica la provee el servidor; la aplicacion puede mostrar informacion al respecto pero no la calcula.

8. **Reglas de negocio del servidor**: Las siguientes reglas las valida y gestiona exclusivamente el servidor. Si un slot no las cumple, el servidor devuelve un error y la aplicacion lo muestra a la trabajadora:
   - Maximo 8 horas de trabajo por dia
   - Minimo 12 horas de descanso entre jornadas
   - La disponibilidad declarada se usa para completar las horas del contrato mediante asignacion automatica de servicios

9. **Sincronizacion**: La trabajadora puede usar pull-to-refresh para sincronizar el estado del calendario con el servidor.

10. **Recordatorio de actualizacion**: Si la disponibilidad no se actualiza en 30 dias, se envia una notificacion de recordatorio a la trabajadora.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home (Hogar) | Pulsar acceso directo "Mi Disponibilidad" | Pantalla del calendario semanal de disponibilidad |
| Home (SAD) | Pulsar acceso directo "Mi Disponibilidad" | Pantalla del calendario semanal de disponibilidad |
| Calendario semanal | Seleccionar un dia | Se activa el panel de franjas rapidas y el formulario de slot personalizado para ese dia |
| Calendario semanal | Tocar un slot Disponible o No disponible | Vista de edicion/eliminacion del slot |
| Calendario semanal | Tocar un slot Activa | Vista de solo lectura con informacion del servicio asignado |
| Notificacion de recordatorio (30 dias) | Tocar la notificacion | Pantalla del calendario semanal de disponibilidad |

---

## Criterios de Aceptacion

### CA-001: Cabecera de horas contratadas vs trabajadas <- HU-005
GIVEN la trabajadora accede a la pantalla de disponibilidad
WHEN la pantalla se carga
THEN la cabecera muestra de forma prominente las horas trabajadas frente a las horas de contrato en formato "X / Y h" o un mensaje equivalente como "Te faltan Z horas"

### CA-002: Vista semanal con tipos de slot diferenciados <- HU-001
GIVEN la trabajadora tiene slots de tipo Disponible, No disponible y Activa creados para la semana
WHEN accede al calendario semanal
THEN cada tipo de slot se muestra como bloque horario con color diferenciado: Disponible (ej: verde), No disponible (ej: rojo/gris), Activa (ej: azul), y los slots de distintos tipos pueden aparecer solapados visualmente

### CA-003: Seleccionar dia activa panel de creacion <- HU-002, HU-003
GIVEN la trabajadora esta en el calendario semanal
WHEN selecciona un dia concreto
THEN se activan el panel de franjas rapidas y el formulario de creacion de slot personalizado para ese dia

### CA-004: Creacion de slot con franja rapida <- HU-002
GIVEN la trabajadora ha seleccionado un dia en el calendario
WHEN pulsa una franja rapida (Manana, Tarde, Noche, Interna o Finde)
THEN se crea inmediatamente un slot de tipo "Disponible" con el rango horario correspondiente a esa franja para el dia seleccionado y el slot aparece en el calendario

### CA-005: Franja Madrugada eliminada <- HU-002
GIVEN la trabajadora esta en el panel de franjas rapidas
WHEN visualiza las opciones disponibles
THEN solo aparecen las franjas Manana, Tarde, Noche, Interna y Finde; la franja Madrugada no esta disponible

### CA-006: Creacion de slot personalizado <- HU-003
GIVEN la trabajadora ha seleccionado un dia en el calendario
WHEN introduce hora de inicio, hora de fin, selecciona tipo (Disponible o No disponible) y confirma la creacion
THEN se crea un slot con los datos indicados para ese dia, aparece en el calendario con el color de su tipo y el cambio se guarda de forma inmediata

### CA-007: Solapamiento entre tipos distintos permitido <- HU-003
GIVEN la trabajadora tiene un slot de tipo "Disponible" de 08:00 a 16:00 para un dia
WHEN crea un slot de tipo "No disponible" de 10:00 a 12:00 para el mismo dia
THEN el slot "No disponible" se crea correctamente y ambos se muestran solapados en el calendario

### CA-008: Solapamiento entre slots del mismo tipo rechazado <- HU-003
GIVEN la trabajadora tiene un slot de tipo "Disponible" de 09:00 a 13:00 para un dia
WHEN intenta crear otro slot de tipo "Disponible" de 11:00 a 15:00 para el mismo dia
THEN la aplicacion muestra un mensaje de error indicando que no es posible crear franjas del mismo tipo que se solapen y no se crea el slot

### CA-009: Slots Activa son de solo lectura <- HU-001
GIVEN existen slots de tipo "Activa" (servicios asignados por planificacion) en el calendario
WHEN la trabajadora toca un slot de tipo "Activa"
THEN la aplicacion muestra la informacion del servicio asignado en modo solo lectura, sin opciones de edicion ni eliminacion

### CA-010: Editar slot propio <- HU-004
GIVEN la trabajadora tiene un slot de tipo "Disponible" o "No disponible" en el calendario
WHEN toca el slot y modifica la hora de inicio, la hora de fin o el tipo, y confirma
THEN el slot se actualiza con los nuevos valores, el cambio se refleja en el calendario y se guarda de forma inmediata

### CA-011: Eliminar slot propio <- HU-004
GIVEN la trabajadora tiene un slot de tipo "Disponible" o "No disponible" en el calendario
WHEN toca el slot y elige eliminarlo y confirma
THEN el slot desaparece del calendario y el cambio se guarda de forma inmediata

### CA-012: Guardado inmediato por accion <- HU-002, HU-003, HU-004
GIVEN la trabajadora crea, edita o elimina un slot
WHEN confirma la accion
THEN el cambio se guarda de forma inmediata en el servidor sin necesidad de pulsar un boton de "guardar todo"

### CA-013: Sin interaccion de arrastrar y soltar <- HU-004
GIVEN la trabajadora esta en el calendario semanal
WHEN interactua con los slots
THEN toda la interaccion es mediante seleccion de dia e inputs (selectores de hora, botones); no existe funcionalidad de arrastrar y soltar

### CA-014: No disponibilidad bloquea asignacion <- HU-003
GIVEN la trabajadora tiene un slot "Disponible" de 08:00 a 16:00 y un slot "No disponible" de 10:00 a 12:00 para el mismo dia
WHEN el sistema de planificacion intenta asignar un servicio en el rango 10:00 a 12:00
THEN el rango de no disponibilidad bloquea la asignacion en esas horas aunque haya disponibilidad declarada en la franja mas amplia

### CA-015: Pull-to-refresh sincroniza calendario <- HU-001
GIVEN la trabajadora esta en la pantalla de disponibilidad
WHEN realiza un gesto de pull-to-refresh
THEN la aplicacion sincroniza el estado del calendario con el servidor y muestra los datos actualizados

### CA-016: Recordatorio si no se actualiza en 30 dias <- HU-001
GIVEN la trabajadora no ha actualizado su disponibilidad en los ultimos 30 dias
WHEN se cumple el plazo de 30 dias sin actualizacion
THEN la trabajadora recibe una notificacion de recordatorio invitandola a actualizar su disponibilidad

### CA-017: Error del servidor por regla de negocio <- HU-003
GIVEN la trabajadora intenta crear un slot que infringe una regla de negocio del servidor (ej: exceder 8 horas de trabajo por dia o no respetar 12 horas de descanso entre jornadas)
WHEN confirma la creacion o edicion del slot
THEN la aplicacion muestra el mensaje de error devuelto por el servidor y no se crea ni modifica el slot

### CA-018: Ventana operativa informativa <- HU-001
GIVEN la trabajadora accede al calendario de un dia
WHEN visualiza la informacion de ese dia
THEN la aplicacion puede mostrar de forma informativa la ventana operativa del dia (12 horas desde inicio de jornada con descanso minimo legal), basada en los datos que provee el servidor

### CA-019: Calendario vacio invita a declarar disponibilidad <- HU-001
GIVEN la trabajadora no tiene ningun slot creado para la semana visible
WHEN accede al calendario semanal
THEN el calendario se muestra vacio con un mensaje invitando a la trabajadora a declarar su disponibilidad

---

## Checklist de Validacion

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados (solapamiento mismo tipo, slot Activa solo lectura, calendario vacio, errores de servidor)
- [x] Estados de error definidos (solapamiento rechazado, regla de negocio infringida)
- [x] Ambiguedades resueltas
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- Gestion de disponibilidad por zonas geograficas (modelo anterior, redefinido en v1.8 del PRD)
- Calculo de reglas de negocio en la aplicacion (maximo horas, descanso entre jornadas): la logica reside exclusivamente en el servidor
- Modo offline con sincronizacion posterior de slots de disponibilidad
- Drag & drop para mover o redimensionar slots en el calendario
- Franja rapida "Madrugada" (eliminada explicitamente)
- Asignacion automatica de servicios: esta feature declara disponibilidad; la asignacion la gestiona el sistema de planificacion fuera de esta feature

---

## Asunciones Aplicadas

- **[A-001]**: Los rangos horarios especificos de cada franja rapida (Manana, Tarde, Noche, Interna, Finde) no estan definidos en el PRD. Se asume que son configuraciones predefinidas por el sistema y la aplicacion los obtiene del servidor. Si el cliente desea rangos especificos fijos, debera indicarlos.
- **[A-002]**: El formato exacto del mensaje de horas en la cabecera ("30 / 40 h" o "Te faltan 10 horas") se asume que es decision de diseno visual. El spec define que debe mostrarse de forma prominente la relacion entre horas trabajadas y contratadas.
- **[A-003]**: La notificacion de recordatorio de 30 dias (CA-016) se asume gestionada por la feature F-012 (push-notifications) como notificacion automatica del sistema. Esta feature solo declara la regla de negocio.
