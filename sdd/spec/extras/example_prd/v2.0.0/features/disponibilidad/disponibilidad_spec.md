# Spec: Disponibilidad
> Version: 1.0 | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md
> Feature ID: F-007

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo | Gestionar su disponibilidad semanal por franjas horarias |
| Trabajadora SAD | Trabajadora del Servicio de Asistencia Social | Gestionar su disponibilidad semanal por franjas horarias, ver franjas activas de planificacion |

---

## Historias de Usuario

### HU-001: Gestionar calendario de disponibilidad
Como trabajadora (Hogar o SAD)
quiero declarar mis franjas de disponibilidad y no disponibilidad en un calendario semanal
para que el sistema pueda asignarme servicios en los horarios que declaro.

---

## Recorridos de Usuario

### Journey 1: Gestionar disponibilidad semanal
Actor: Trabajadora (Hogar o SAD) | Objetivo: Declarar sus franjas de disponibilidad
1. La trabajadora accede a "Mi Disponibilidad" desde el home.
2. Ve la cabecera con informacion de horas trabajadas vs. horas de contrato (p.ej. "30 / 40 h" o "Te faltan X horas").
3. Ve el calendario semanal (Lun-Dom) con los slots de disponibilidad existentes, mostrados como bloques horarios con color diferenciado: Disponible (verde), No disponible (rojo/gris), Activa (azul, solo lectura).
4. Los slots de distintos tipos pueden solaparse visualmente en el calendario.
5. Selecciona un dia para activar el panel de franjas rapidas y el formulario de slot personalizado.
6. Puede pulsar una franja rapida predefinida (Manana, Tarde, Noche, Interna, Finde) para crear inmediatamente un slot de tipo "Disponible" para ese dia.
7. Puede usar el formulario de slot personalizado: introduce hora de inicio y hora de fin (time picker), selecciona tipo (Disponible o No disponible), y confirma.
8. Se permiten solapamientos entre slots de distinto tipo (p.ej. una franja amplia Disponible con una excepcion corta No disponible dentro). No se permiten solapamientos entre slots del mismo tipo en el mismo dia.
9. Los cambios se guardan de forma inmediata al confirmar cada slot (no hay boton "guardar todo").
10. Puede tocar un slot Disponible o No disponible para editarlo (modificar hora inicio/fin o tipo) o eliminarlo.
11. Los slots Activa (planificacion) son de solo lectura; al tocarlos solo muestran informacion.

Estado de exito: La trabajadora tiene su disponibilidad semanal actualizada y reflejada en el calendario.
Flujos alternativos:
- Si un slot no cumple las reglas de negocio del servidor (max 8h/dia, min 12h descanso), la API devuelve error y la app lo muestra.
- Pull-to-refresh sincroniza con el servidor.
- Notificacion de recordatorio si la disponibilidad no se actualiza en 30 dias.

---

## Resultados y Exito

- La trabajadora tiene una vision clara de su disponibilidad semanal con diferenciacion visual por tipo.
- Puede gestionar franjas de forma rapida con presets o de forma personalizada.
- Los servicios asignados (Activa) se muestran superpuestos para referencia pero no son editables.
- Los cambios se persisten inmediatamente sin boton de guardado global.

---

## Instrucciones Inambiguas

### Reglas de comportamiento
- La cabecera muestra horas trabajadas vs. horas de contrato en formato prominente.
- El panel de franjas rapidas incluye: Manana, Tarde, Noche, Interna, Finde. La franja Madrugada esta eliminada.
- Pulsar una franja rapida con un dia seleccionado crea inmediatamente un slot de tipo "Disponible" con el rango horario correspondiente.
- El formulario de slot personalizado permite seleccionar hora de inicio y fin (time picker) y tipo: Disponible o No disponible.
- Se permiten solapamientos entre slots de distinto tipo. No se permiten solapamientos entre slots del mismo tipo en el mismo dia; la API devuelve error en este caso.
- Los slots "No disponible" bloquean la asignacion de servicios en ese rango, aunque haya disponibilidad declarada. Esta logica la gestiona el backend.
- Los slots "Activa" representan horas con servicio asignado por planificacion. Son de solo lectura: no se pueden editar ni eliminar desde la app.
- No se implementa drag & drop; toda la interaccion es mediante seleccion + inputs.
- La ventana operativa de cada dia esta basada en 12 horas desde el inicio de jornada, respetando el descanso minimo legal. Esta logica la provee la API; la app puede mostrarla de forma informativa pero no la calcula.
- Los cambios se guardan de forma inmediata al confirmar cada slot.
- Las reglas de negocio (max 8h/dia, min 12h descanso entre jornadas, completar horas de contrato) las valida exclusivamente el servidor. La app muestra los errores devueltos por la API.

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home | Tocar "Mi Disponibilidad" | Calendario de disponibilidad |
| Calendario | Seleccionar dia | Panel de franjas rapidas + formulario slot personalizado |
| Calendario | Tocar slot Disponible o No disponible | Dialogo de edicion/eliminacion del slot |
| Calendario | Tocar slot Activa | Informacion del slot (solo lectura) |

---

## Criterios de Aceptacion

### CA-001: Cabecera de horas <- HU-001
GIVEN la trabajadora accede a Mi Disponibilidad
WHEN se carga la pantalla
THEN se muestra en la cabecera la informacion de horas trabajadas vs. horas de contrato en formato prominente (p.ej. "30 / 40 h" o "Te faltan X horas").

### CA-002: Calendario semanal con tipos <- HU-001
GIVEN la trabajadora accede a Mi Disponibilidad
WHEN se carga el calendario
THEN se muestra una vista semanal (Lun-Dom) con los slots de disponibilidad como bloques horarios, con color diferenciado: Disponible (verde), No disponible (rojo/gris), Activa (azul). Los slots de distintos tipos pueden solaparse visualmente.

### CA-003: Seleccion de dia activa panel <- HU-001
GIVEN la trabajadora esta en el calendario de disponibilidad
WHEN selecciona un dia
THEN se activa el panel de franjas rapidas y el formulario de creacion de slot personalizado para ese dia.

### CA-004: Panel de franjas rapidas <- HU-001
GIVEN la trabajadora ha seleccionado un dia en el calendario
WHEN ve el panel de franjas rapidas
THEN se muestran las franjas predefinidas: Manana, Tarde, Noche, Interna, Finde. La franja Madrugada esta eliminada. Pulsar una franja crea inmediatamente un slot de tipo "Disponible" con el rango horario de esa franja.

### CA-005: Formulario de slot personalizado <- HU-001
GIVEN la trabajadora ha seleccionado un dia en el calendario
WHEN usa el formulario de slot personalizado
THEN puede introducir hora de inicio y hora de fin (time picker), seleccionar tipo Disponible o No disponible, y crear el slot. Se permiten solapamientos entre slots de distinto tipo. No se permiten solapamientos entre slots del mismo tipo en el mismo dia; la API devuelve error.

### CA-006: Slots No disponible bloquean asignacion <- HU-001
GIVEN la trabajadora ha creado un slot de tipo "No disponible"
WHEN el backend procesa la disponibilidad
THEN ese rango horario queda bloqueado para asignacion de servicios, aunque haya disponibilidad declarada en la misma franja. Esta logica la gestiona el backend.

### CA-007: Slots Activa solo lectura <- HU-001
GIVEN la trabajadora ve el calendario de disponibilidad
WHEN hay slots de tipo "Activa" (servicios asignados por planificacion)
THEN se muestran solapados sobre las franjas Disponible correspondientes. Son de solo lectura: no se pueden editar ni eliminar.

### CA-008: Editar o eliminar slot <- HU-001
GIVEN la trabajadora ve el calendario de disponibilidad
WHEN toca un slot de tipo "Disponible" o "No disponible"
THEN puede editar (modificar hora inicio/fin o tipo) o eliminarlo. Tocar un slot "Activa" solo muestra informacion.

### CA-009: Sin drag and drop <- HU-001
GIVEN la trabajadora esta gestionando su disponibilidad
WHEN interactua con el calendario
THEN no hay drag & drop; toda la interaccion es mediante seleccion + inputs.

### CA-010: Ventana operativa informativa <- HU-001
GIVEN la trabajadora ve el calendario de disponibilidad
WHEN consulta la ventana operativa de un dia
THEN la ventana basada en 12 horas desde inicio de jornada se muestra de forma informativa. La logica la provee la API; la app no la calcula.

### CA-011: Guardado inmediato <- HU-001
GIVEN la trabajadora confirma un slot (creacion, edicion o eliminacion)
WHEN se confirma la accion
THEN los cambios se guardan de forma inmediata (no hay boton "guardar todo").

### CA-012: Pull-to-refresh <- HU-001
GIVEN la trabajadora esta en el calendario de disponibilidad
WHEN realiza gesto de pull-to-refresh
THEN el estado se sincroniza con el servidor.

### CA-013: Recordatorio de actualizacion <- HU-001
GIVEN la trabajadora no ha actualizado su disponibilidad en 30 dias
WHEN se cumple el plazo
THEN recibe una notificacion de recordatorio.

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
- Calculo local de reglas de negocio (max horas, descanso minimo) — lo valida exclusivamente el servidor
- Drag & drop para gestionar slots
- Franja "Madrugada" (eliminada)
- Gestion de disponibilidad por zonas/codigo postal (sustituida por disponibilidad basada en direccion de domicilio)
