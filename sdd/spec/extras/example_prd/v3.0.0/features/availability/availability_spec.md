# Spec: Gestion de Disponibilidad

> Version: 1.0 | Fecha: 2026-04-05
> Spec monolitico origen: prd-hogar-sad_spec.md
> Feature ID: F-009

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades de empleo a traves de la app CUIDEO (tema azul) | Gestionar disponibilidad semanal mediante calendario con franjas horarias |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios asignados a traves de la app Felizvita (tema verde) | Gestionar disponibilidad semanal mediante calendario con franjas horarias |
| Sistema | El propio sistema automatizado que ejecuta acciones programadas sin intervencion humana | Enviar notificacion de recordatorio de actualizacion de disponibilidad |

---

## Historias de Usuario

### HU-029: Calendario de disponibilidad
Como trabajadora (Hogar o SAD)
quiero gestionar mi disponibilidad semanal mediante un calendario con franjas horarias
para que el sistema de planificacion pueda asignarme servicios en los horarios que he declarado como disponibles.

---

## Recorridos de Usuario

### Journey 11: Gestionar disponibilidad
Actor: Trabajadora (Hogar o SAD) | Objetivo: Declarar sus franjas horarias disponibles en la semana

1. La trabajadora accede a "Mi Disponibilidad".
2. La pantalla muestra en la cabecera la informacion de horas trabajadas vs. horas de contrato (ej: "30 / 40 h" o "Te faltan X horas").
3. Se muestra una vista semanal (Lun-Dom) con los slots existentes: Disponible (color diferenciado), No disponible (color diferenciado), Activa (color diferenciado, solo lectura).
4. La trabajadora selecciona un dia.
5. Se activa el panel de franjas rapidas (Manana, Tarde, Noche, Interna, Finde) y el formulario de slot personalizado.
6. Al pulsar una franja rapida, se crea inmediatamente un slot de tipo "Disponible" con el rango horario correspondiente.
7. Para crear un slot personalizado: la trabajadora introduce hora de inicio y fin, y selecciona tipo (Disponible o No disponible).
8. Los slots de distinto tipo pueden solaparse. Los del mismo tipo no pueden solaparse (la API devuelve error).
9. La trabajadora puede tocar un slot Disponible o No disponible para editarlo o eliminarlo. Los slots Activa son solo lectura.
10. Los cambios se guardan inmediatamente al confirmar cada slot.

Estado de exito: La trabajadora ha declarado sus franjas de disponibilidad y puede ver como se reflejan en el calendario junto con las asignaciones activas del sistema.

---

## Resultados y Exito

- **Disponibilidad**: Las trabajadoras pueden declarar su disponibilidad semanal a traves de un calendario intuitivo y el sistema de planificacion utiliza esa informacion para la asignacion de servicios.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Solapamiento de disponibilidad**: Los slots de distinto tipo (Disponible y No disponible) pueden solaparse. Los del mismo tipo no pueden solaparse (la API devuelve error).
- **Slots "Activa"**: Horas con servicio asignado por planificacion. Solo lectura, no editables ni eliminables desde la app.
- **Reglas de negocio de disponibilidad**: Maximo 8 horas de trabajo por dia, minimo 12 horas de descanso entre jornadas. Estas reglas las valida el servidor; la app muestra los errores que el servidor devuelva.
- **Franjas horarias predefinidas**: Los rangos horarios seran configurados desde el servidor y la app los mostrara tal como los recibe. Si no los provee el servidor, se aplicaran valores por defecto razonables (Manana: 07:00-15:00, Tarde: 15:00-22:00, Noche: 22:00-07:00, Interna: 08:00-20:00, Finde: 07:00-22:00 sabados y domingos).
- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.

---

## Criterios de Aceptacion

### CA-001: Calendario de disponibilidad con franjas ← HU-029
GIVEN la trabajadora accede a "Mi Disponibilidad"
WHEN se carga el calendario
THEN se muestra: cabecera con horas trabajadas vs. contrato ("30 / 40 h" o "Te faltan X horas"), vista semanal (Lun-Dom) con slots de Disponible, No disponible y Activa diferenciados por color. Los slots de distinto tipo pueden solaparse visualmente

### CA-002: Crear slot con franja rapida ← HU-029
GIVEN la trabajadora ha seleccionado un dia en el calendario
WHEN pulsa una franja rapida (Manana, Tarde, Noche, Interna, Finde)
THEN se crea inmediatamente un slot de tipo "Disponible" con el rango horario correspondiente. El slot se guarda al momento

### CA-003: Crear slot personalizado ← HU-029
GIVEN la trabajadora ha seleccionado un dia en el calendario
WHEN introduce hora de inicio, hora de fin y selecciona tipo (Disponible o No disponible) en el formulario
THEN se crea el slot con los datos indicados. No se permiten solapamientos entre slots del mismo tipo (la API devuelve error)

### CA-004: Editar y eliminar slots ← HU-029
GIVEN la trabajadora ve un slot de tipo Disponible o No disponible en el calendario
WHEN toca el slot
THEN puede editarlo (modificar hora inicio/fin o tipo) o eliminarlo. Los slots de tipo Activa solo muestran informacion (no editables)

### CA-005: Guardado inmediato de disponibilidad ← HU-029
GIVEN la trabajadora ha creado, editado o eliminado un slot
WHEN confirma la accion
THEN el cambio se guarda de forma inmediata (no hay boton "guardar todo"). Pull-to-refresh disponible para sincronizar

### CA-006: Recordatorio de actualizacion de disponibilidad ← HU-029
GIVEN la trabajadora no ha actualizado su disponibilidad en 30 dias
WHEN el sistema detecta la inactividad
THEN la trabajadora recibe una notificacion de recordatorio

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

- No se han definido exclusiones explicitas para esta feature.
