# Spec: Gestión de Disponibilidad
> Versión: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-007 via prd-hogar-sad_discovery.md)
> Feature ID: F-007
> Spec monolítico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora (Hogar o SAD) | Profesional de cuidados que utiliza la aplicación móvil para gestionar su disponibilidad horaria semanal | Declarar, editar y eliminar franjas de disponibilidad y no disponibilidad; usar franjas rápidas predefinidas; consultar horas trabajadas vs. horas de contrato |

---

## Historias de Usuario

### HU-001: Consultar resumen semanal de horas
Como trabajadora, quiero ver mis horas trabajadas frente a mis horas de contrato en la pantalla de disponibilidad, para saber cuántas horas me quedan por cubrir en la semana.

### HU-002: Visualizar disponibilidad semanal en el calendario
Como trabajadora, quiero ver todos mis slots de disponibilidad, no disponibilidad y horas activas (planificadas) en un calendario semanal, para tener una visión clara de mis franjas declaradas y las horas que ya tengo asignadas.

### HU-003: Crear disponibilidad usando franjas rápidas
Como trabajadora, quiero seleccionar un día y aplicar una franja rápida predefinida (Mañana, Tarde, Noche, Interna o Finde), para declarar mi disponibilidad de forma ágil sin introducir horas manualmente.

### HU-004: Crear slot de disponibilidad personalizado
Como trabajadora, quiero definir manualmente la hora de inicio, la hora de fin y el tipo (disponible o no disponible) de un nuevo slot, para declarar franjas horarias adaptadas a mis circunstancias concretas.

### HU-005: Editar o eliminar un slot existente
Como trabajadora, quiero tocar un slot de disponibilidad o no disponibilidad ya creado para modificar su horario o tipo, o para eliminarlo, para mantener mi disponibilidad actualizada ante cualquier cambio en mi situación.

### HU-006: Consultar información de slots activos de planificación
Como trabajadora, quiero poder tocar un slot de tipo "Activa" (asignado por planificación) para ver su información, para saber qué servicio tengo asignado en ese bloque horario, aunque no pueda modificarlo.

### HU-007: Recibir recordatorio de disponibilidad no actualizada
Como trabajadora, quiero recibir una notificación de recordatorio cuando no haya actualizado mi disponibilidad en 30 días, para no olvidar declarar mis franjas horarias y evitar que el sistema me asigne servicios incorrectamente.

---

## Recorridos de Usuario

### Journey 1: Declarar disponibilidad con franja rápida
Actor: Trabajadora (Hogar o SAD) | Objetivo: Declarar rápidamente la disponibilidad de un día concreto

1. La trabajadora accede al módulo de disponibilidad desde el menú o acceso directo del panel principal.
2. El sistema muestra el calendario semanal (Lunes a Domingo) con los slots ya existentes y la cabecera con el resumen de horas.
3. La trabajadora selecciona un día en el calendario.
4. El sistema activa el panel de franjas rápidas y el formulario de slot personalizado para el día seleccionado.
5. La trabajadora pulsa una franja rápida (p. ej., "Mañana").
6. El sistema crea inmediatamente un slot de tipo "Disponible" con el rango horario correspondiente a esa franja y lo muestra en el calendario.

Estado de éxito: El slot aparece en el calendario del día seleccionado con el color correspondiente a "Disponible".
Flujos alternativos: Si el sistema rechaza el slot por solapamiento con otro del mismo tipo → la trabajadora ve un mensaje de error explicativo y el slot no se crea.

---

### Journey 2: Crear slot personalizado con hora de inicio y fin
Actor: Trabajadora (Hogar o SAD) | Objetivo: Declarar una franja horaria específica no cubierta por las franjas rápidas

1. La trabajadora selecciona un día en el calendario.
2. El sistema activa el formulario de slot personalizado.
3. La trabajadora introduce la hora de inicio y la hora de fin mediante selectores de hora y elige el tipo: "Disponible" o "No disponible".
4. La trabajadora confirma el slot.
5. El sistema valida que no haya solapamiento con otro slot del mismo tipo y guarda el slot de forma inmediata.
6. El nuevo slot aparece en el calendario con el color correspondiente a su tipo.

Estado de éxito: El slot queda guardado y visible en el calendario sin necesidad de acción adicional.
Flujos alternativos: Si el sistema detecta solapamiento con un slot del mismo tipo → muestra error y no guarda el slot hasta que la trabajadora corrija las horas o el tipo.

---

### Journey 3: Editar o eliminar un slot existente
Actor: Trabajadora (Hogar o SAD) | Objetivo: Actualizar o retirar un slot de disponibilidad ya declarado

1. La trabajadora toca un slot de tipo "Disponible" o "No disponible" en el calendario.
2. El sistema muestra las opciones de edición (modificar hora inicio/fin o tipo) y de eliminación.
3. La trabajadora elige editar: modifica las horas o el tipo y confirma.
4. El sistema valida y guarda el cambio de forma inmediata.

Estado de éxito: El slot actualizado se refleja en el calendario con los nuevos valores o desaparece si fue eliminado.
Flujos alternativos: Si la trabajadora toca un slot de tipo "Activa" → el sistema solo muestra información del slot, sin opción de edición ni eliminación.

---

### Journey 4: Consultar resumen de horas de contrato
Actor: Trabajadora (Hogar o SAD) | Objetivo: Conocer cuántas horas trabajadas lleva en la semana vs. su contrato

1. La trabajadora accede al módulo de disponibilidad.
2. El sistema muestra en la cabecera de la pantalla el resumen de horas en formato prominente (p. ej., "30 / 40 h" o "Te faltan 10 horas").
3. La trabajadora consulta el dato sin necesidad de interacción adicional.

Estado de éxito: La trabajadora ve el dato actualizado de horas trabajadas vs. horas contratadas de la semana en curso.
Flujos alternativos: Si la trabajadora actualiza la pantalla → el sistema sincroniza con el servidor y refresca los datos de horas y los slots del calendario.

---

## Resultados y Éxito

La feature de gestión de disponibilidad se considera completa cuando:

- La trabajadora puede consultar su disponibilidad semanal en un calendario visual con slots diferenciados por tipo (Disponible, No disponible, Activa).
- La trabajadora puede crear slots de disponibilidad y no disponibilidad, tanto mediante franjas rápidas predefinidas como mediante un formulario de slot personalizado.
- La trabajadora puede editar y eliminar slots de tipo Disponible y No disponible; los slots de tipo Activa son consultables pero no editables desde la app.
- Los cambios se persisten de forma inmediata al confirmar cada slot, sin necesidad de una acción de guardado global.
- La cabecera muestra siempre el resumen de horas trabajadas vs. horas de contrato de la semana en curso.
- La trabajadora recibe una notificación de recordatorio cuando no ha actualizado su disponibilidad en 30 días.
- Las reglas de solapamiento se aplican correctamente: no se permiten solapamientos entre slots del mismo tipo en el mismo día; sí se permiten entre tipos distintos.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Tipos de slots en el calendario**: existen exactamente tres tipos de entradas en el calendario: "Disponible" (editables, creadas por la trabajadora), "No disponible" (editables, creadas por la trabajadora) y "Activa" (de solo lectura, creadas por planificación y visibles solapadas sobre franjas "Disponible").

2. **Solapamientos permitidos e impedidos**: se permiten solapamientos entre slots de tipos distintos (p. ej., una franja "Disponible" amplia con una "No disponible" de excepción dentro). No se permiten solapamientos entre slots del mismo tipo en el mismo día. Si se intenta crear un slot que solaparía con otro del mismo tipo, el sistema rechaza la operación y muestra un mensaje de error.

3. **Franjas rápidas predefinidas**: el sistema ofrece exactamente cinco franjas rápidas: Mañana, Tarde, Noche, Interna y Finde. La franja Madrugada queda eliminada del sistema.

4. **Guardado inmediato**: cada slot se guarda en el momento en que la trabajadora lo confirma. No existe un botón de "guardar todo" ni un estado de edición en borrador.

5. **Slots Activa — solo lectura absoluta**: los slots de tipo "Activa" no pueden ser editados ni eliminados desde la aplicación. Tocar un slot "Activa" muestra únicamente información; no activa ninguna opción de edición.

6. **Efecto de slots "No disponible" sobre asignación**: cuando una trabajadora declara una franja "No disponible" dentro de un rango en el que también tiene declarada disponibilidad, el sistema de planificación excluye ese rango de la asignación automática de servicios. Esta lógica la gestiona exclusivamente el sistema; la app solo refleja el estado de los slots.

7. **Ventana operativa diaria**: el sistema informa de la ventana operativa de cada día (basada en el descanso mínimo legal). La app puede mostrar esta información de forma orientativa, pero no la calcula; si un slot excede la ventana operativa, es el sistema quien lo comunica con el error correspondiente.

8. **Sincronización manual**: la trabajadora puede solicitar una actualización de datos en cualquier momento. El sistema recupera del servidor el estado actualizado de horas y slots.

9. **Recordatorio por inactividad**: si la trabajadora no ha creado, editado ni eliminado ningún slot en los últimos 30 días, el sistema envía automáticamente una notificación de recordatorio. Esta notificación es de tipo informativo y no requiere acción desde la app.

10. **Resumen de horas en cabecera**: el resumen muestra las horas contratadas, las asignadas y las fichadas de la semana en curso. El formato predeterminado es `[horas asignadas] / [horas contratadas] h`. Si hay diferencia, puede mostrarse un mensaje complementario (p. ej., "Te faltan X horas").

### Destinos de navegación

| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Panel principal (home) | Pulsar acceso directo "Mi Disponibilidad" | Pantalla principal de disponibilidad (calendario semanal) |
| Pantalla de disponibilidad | Seleccionar un día en el calendario | Panel de franjas rápidas + formulario de slot personalizado activos para ese día |
| Pantalla de disponibilidad | Tocar slot "Disponible" o "No disponible" | Vista de edición/eliminación del slot |
| Pantalla de disponibilidad | Tocar slot "Activa" | Vista informativa del slot (solo lectura) |

---

## Criterios de Aceptación

### CA-001: Resumen de horas en cabecera ← HU-001
GIVEN que la trabajadora accede a la pantalla de disponibilidad
WHEN el sistema carga los datos de la semana en curso
THEN la cabecera muestra de forma prominente las horas asignadas sobre las horas contratadas (formato `X / Y h`) y, si hay diferencia, un mensaje complementario indicando las horas restantes

---

### CA-002: Vista semanal con slots diferenciados por tipo ← HU-002
GIVEN que la trabajadora accede a la pantalla de disponibilidad
WHEN el sistema muestra el calendario
THEN se presenta una vista semanal de Lunes a Domingo con los slots de disponibilidad como bloques horarios con color diferenciado: "Disponible" en un color (p. ej., verde), "No disponible" en otro (p. ej., rojo/gris) y "Activa" en un tercer color (p. ej., azul); los slots de distintos tipos pueden solaparse visualmente

---

### CA-003: Seleccionar día activa panel de creación ← HU-003, HU-004
GIVEN que la trabajadora está en la pantalla de disponibilidad con el calendario visible
WHEN la trabajadora toca un día en el calendario
THEN el sistema activa para ese día el panel de franjas rápidas y el formulario de creación de slot personalizado

---

### CA-004: Crear slot con franja rápida ← HU-003
GIVEN que la trabajadora ha seleccionado un día en el calendario
WHEN la trabajadora pulsa una de las cinco franjas rápidas disponibles (Mañana, Tarde, Noche, Interna o Finde)
THEN el sistema crea inmediatamente un slot de tipo "Disponible" con el rango horario correspondiente a esa franja para el día seleccionado, y el slot aparece en el calendario sin pasos adicionales

---

### CA-005: Crear slot personalizado con selector de hora y tipo ← HU-004
GIVEN que la trabajadora ha seleccionado un día y tiene visible el formulario de slot personalizado
WHEN la trabajadora introduce hora de inicio y hora de fin mediante el selector de hora, elige el tipo ("Disponible" o "No disponible") y confirma
THEN el sistema guarda el slot de forma inmediata y lo muestra en el calendario del día seleccionado con el color correspondiente a su tipo

---

### CA-006: Validación de solapamiento entre slots del mismo tipo ← HU-004
GIVEN que la trabajadora intenta crear o editar un slot que solaparía en el mismo día con otro slot del mismo tipo
WHEN la trabajadora confirma la acción
THEN el sistema rechaza la operación, muestra un mensaje de error explicativo y el slot no se crea ni modifica; el calendario permanece con el estado anterior

---

### CA-007: Solapamiento permitido entre tipos distintos ← HU-004
GIVEN que la trabajadora tiene declarada una franja "Disponible" en un día
WHEN la trabajadora crea un slot "No disponible" cuyo horario se solapa con la franja "Disponible" existente
THEN el sistema acepta la operación y muestra ambos slots solapados visualmente en el calendario

---

### CA-008: Slots "Activa" de solo lectura ← HU-006
GIVEN que el calendario muestra uno o más slots de tipo "Activa" (planificados por el sistema)
WHEN la trabajadora toca un slot "Activa"
THEN el sistema muestra únicamente información del slot (datos de la franja planificada) sin ofrecer opciones de edición ni eliminación

---

### CA-009: Editar slot existente ← HU-005
GIVEN que la trabajadora toca un slot de tipo "Disponible" o "No disponible" en el calendario
WHEN el sistema muestra las opciones de edición y la trabajadora modifica la hora de inicio, la hora de fin o el tipo y confirma
THEN el sistema valida los cambios, los guarda de forma inmediata y el calendario refleja el slot actualizado

---

### CA-010: Eliminar slot existente ← HU-005
GIVEN que la trabajadora toca un slot de tipo "Disponible" o "No disponible" en el calendario
WHEN el sistema muestra las opciones de edición y la trabajadora elige eliminar el slot y confirma
THEN el sistema elimina el slot de forma inmediata y desaparece del calendario

---

### CA-011: Guardado inmediato sin acción global ← HU-004, HU-005
GIVEN que la trabajadora crea, edita o elimina un slot
WHEN la trabajadora confirma la acción
THEN el cambio se persiste de forma inmediata; no existe ningún botón de "guardar todo" ni estado de pendiente de guardado

---

### CA-012: Sincronización de datos desde el servidor ← HU-002
GIVEN que la trabajadora está en la pantalla de disponibilidad
WHEN la trabajadora solicita una actualización de los datos
THEN el sistema recupera del servidor el estado actualizado de horas y slots y refresca la pantalla completa (cabecera y calendario)

---

### CA-013: Notificación de recordatorio por inactividad ← HU-007
GIVEN que la trabajadora no ha creado, editado ni eliminado ningún slot en los últimos 30 días
WHEN el sistema detecta dicha inactividad
THEN la trabajadora recibe una notificación de recordatorio instándola a revisar y actualizar su disponibilidad

---

### CA-014: No se implementa drag & drop ← HU-004, HU-005
GIVEN que la trabajadora accede al calendario de disponibilidad
WHEN la trabajadora interactúa con los slots
THEN toda la interacción de creación y edición se realiza mediante selección del día y uso de los controles de entrada (panel de franjas rápidas y formulario con selectores de hora); no existe la posibilidad de arrastrar o soltar slots en el calendario

---

## Checklist de Validación
- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de éxito definidos
- [x] Edge cases documentados (solapamientos, slots Activa, inactividad 30 días)
- [x] Estados de error definidos (solapamiento mismo tipo, slot Activa no editable)
- [x] Ambigüedades resueltas (franjas rápidas sin Madrugada, guardado inmediato, ventana operativa en backend)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes

---

## Fuera de Alcance

- **Gestión de disponibilidad por zonas geográficas**: el modelo basado en zonas fue reemplazado por el modelo de franjas horarias en v1.8. La gestión de zonas no forma parte de esta feature.
- **Franja rápida "Madrugada"**: eliminada del sistema. No se implementa.
- **Drag & drop de slots en el calendario**: no se implementa en esta versión; toda la interacción es mediante selección y formularios.
- **Cálculo de reglas laborales en la app**: las reglas de máximo horas por día, descanso mínimo entre jornadas y ventana operativa las calcula y valida exclusivamente el sistema de planificación; la app solo muestra los errores que devuelve el servidor.
- **Corrección de registros desde la app**: no se permite modificar registros de horas confirmadas desde la app; las correcciones se gestionan desde el backoffice.
- **Notificaciones push**: el mecanismo de envío de la notificación de recordatorio de inactividad pertenece al scope de la feature F-009 (push-notifications). Esta feature solo define el trigger funcional (30 días sin actualización).

---

## Asunciones Aplicadas

- **[A-001]**: Los rangos horarios exactos de las franjas rápidas predefinidas (Mañana, Tarde, Noche, Interna, Finde) no están especificados en el PRD. Se asume que el sistema de planificación los define y los provee a través del mismo endpoint que devuelve la disponibilidad semanal. La app los presenta con el nombre de la franja tal como los devuelve el servidor, sin calcularlos de forma autónoma. Si se requiere mostrar el rango horario en el botón de franja rápida, deberá confirmarse con el equipo de producto. [Asunción por defecto: los botones muestran solo el nombre de la franja, sin rango horario explícito.]

- **[A-002]**: El PRD menciona que la ventana operativa diaria "la provee la API" y que "la app puede mostrarla de forma informativa". Se asume que su visualización es un indicador de referencia (texto o banda sombreada en el calendario) que no bloquea la creación de slots fuera de ella; solo el servidor lo impide con el error correspondiente. [Asunción por defecto: la ventana operativa se muestra como información contextual, no como restricción visual de la interfaz.]
