# Spec: Availability
> Versión: 1.0 | Fecha: 2026-04-02
> Spec monolítico origen: prd-hogar-sad_spec.md
> Feature ID: F-007

---

## Actores
| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades. Usa la app CUIDEO (identidad visual azul). | Declarar y gestionar franjas de disponibilidad y no disponibilidad semanales. |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona servicios asignados. Usa la app Felizvita (identidad visual verde). | Declarar y gestionar franjas de disponibilidad y no disponibilidad semanales; los slots Activa son de solo lectura. |
| Sistema / Backoffice | Equipo de coordinación y administración que gestiona el backend y los datos. | Configurar reglas de negocio de disponibilidad; los slots Activa son generados por planificación. No es un actor de la app móvil pero sus acciones generan estados visibles para las trabajadoras. |

---

## Historias de Usuario

### HU-026: Gestionar mi disponibilidad semanal
Como trabajadora (Hogar o SAD) / quiero declarar mis franjas de disponibilidad y no disponibilidad en el calendario semanal / para que el sistema pueda asignarme servicios en los horarios en que estoy disponible.

---

## Recorridos de Usuario

### Journey 1: Declarar disponibilidad semanal
Actor: Trabajadora Hogar o SAD | Objetivo: Configurar los horarios disponibles para recibir servicios

1. La trabajadora accede a "Mi Disponibilidad" desde la home o el menú.
2. La pantalla muestra la vista semanal (Lun–Dom) con los slots existentes como bloques horarios.
3. La trabajadora selecciona un día.
4a. Para crear un slot rápido: pulsa una franja predefinida (Mañana, Tarde, Noche, Interna, Finde). Se crea inmediatamente un slot "Disponible" con el rango horario de la franja.
4b. Para crear un slot personalizado: usa el formulario de slot con hora inicio, hora fin y tipo (Disponible o No disponible).
5. El slot se guarda de forma inmediata al confirmar (sin botón "guardar todo").
6. La trabajadora puede tocar cualquier slot propio para editarlo o eliminarlo.

Estado de éxito: Los slots se reflejan inmediatamente en el calendario. El sistema puede utilizarlos para la asignación de servicios.

Flujos alternativos:
- Si hay solapamiento entre slots del mismo tipo → la API devuelve error y la app lo muestra.
- Si la trabajadora toca un slot Activa → solo puede ver información, sin opción de editar ni eliminar.
- Si la trabajadora no actualiza disponibilidad en 30 días → recibe una notificación de recordatorio.

---

## Resultados y Éxito

- **Perfil actualizado**: Los cambios guardados se reflejan inmediatamente en la app.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Disponibilidad:**
- Los cambios en franjas de disponibilidad se guardan de forma inmediata al confirmar cada slot (no hay botón "guardar todo").
- Los slots de tipo "Activa" (horas con servicio asignado por planificación) son de solo lectura; no se pueden editar ni eliminar desde la app.
- Se permiten solapamientos entre slots de distinto tipo (Disponible + No disponible); no se permiten solapamientos entre slots del mismo tipo.
- Las reglas de negocio de disponibilidad (máx. 8h/día, mínimo 12h de descanso entre jornadas) las valida y gestiona exclusivamente el servidor; la app muestra el error si la API lo devuelve.

**Experiencia general:**
- Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse.

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Pantalla de fichaje | Pulsa "Solicitar ausencia" | Formulario de solicitud de ausencia |

---

## Criterios de Aceptación

### CA-001: Disponibilidad — vista semanal ← HU-026
GIVEN la trabajadora (Hogar o SAD) accede a "Mi Disponibilidad"
WHEN la pantalla se carga
THEN se muestra una vista semanal (Lun–Dom) con los slots de disponibilidad existentes como bloques horarios con color diferenciado por tipo: Disponible, No disponible, Activa (solo lectura). En la cabecera se muestran las horas trabajadas vs. horas de contrato de forma prominente.

---

### CA-002: Disponibilidad — crear slot con franja rápida ← HU-026
GIVEN la trabajadora selecciona un día en el calendario de disponibilidad
WHEN pulsa una franja predefinida (Mañana, Tarde, Noche, Interna, Finde)
THEN se crea inmediatamente un slot de tipo "Disponible" con el rango horario de esa franja para el día seleccionado. La franja Madrugada no está disponible.

---

### CA-003: Disponibilidad — crear slot personalizado ← HU-026
GIVEN la trabajadora selecciona un día en el calendario de disponibilidad
WHEN usa el formulario de slot personalizado
THEN puede introducir hora de inicio y hora de fin, y elegir el tipo (Disponible o No disponible); se permiten solapamientos entre slots de distinto tipo; no se permiten solapamientos entre slots del mismo tipo (la API devuelve error si ocurre).

---

### CA-004: Disponibilidad — editar y borrar slot ← HU-026
GIVEN la trabajadora toca un slot de tipo "Disponible" o "No disponible"
WHEN selecciona editar o eliminar
THEN puede modificar la hora inicio/fin o el tipo, o eliminar el slot; los cambios se guardan de forma inmediata al confirmar.

---

### CA-005: Disponibilidad — slot Activa es de solo lectura ← HU-026
GIVEN la trabajadora toca un slot de tipo "Activa"
WHEN interacciona con él
THEN se muestra solo información del slot; no hay opción de editar ni eliminar.

---

### CA-006: Disponibilidad — recordatorio si no se actualiza ← HU-026
GIVEN la trabajadora no ha actualizado su disponibilidad en 30 días
WHEN el sistema detecta la inactividad
THEN envía una notificación de recordatorio a la trabajadora.

---

## Checklist de Validación
- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de éxito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [x] Ambigüedades resueltas (las resolubles; las pendientes marcadas como [INCOMPLETO])
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes

---

## Fuera de Alcance
No se han definido exclusiones explícitas para esta feature.
