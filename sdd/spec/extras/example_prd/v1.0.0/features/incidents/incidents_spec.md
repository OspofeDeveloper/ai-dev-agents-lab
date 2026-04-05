# Spec: Incidents
> Versión: 1.0 | Fecha: 2026-04-02
> Spec monolítico origen: prd-hogar-sad_spec.md
> Feature ID: F-005

---

## Actores
| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona servicios asignados. Usa la app Felizvita (identidad visual verde). | Reportar incidencias con adjuntos, consultar historial de incidencias reportadas y sus estados. |
| Sistema / Backoffice | Equipo de coordinación y administración que gestiona el backend y los datos. | Revisar incidencias, cambiar su estado y añadir comentarios. No es un actor de la app móvil pero sus acciones generan estados visibles para las trabajadoras. |

---

## Historias de Usuario

### HU-021: Reportar una incidencia (SAD)
Como trabajadora SAD / quiero reportar una incidencia del servicio o del cliente con descripción y adjuntos / para que coordinación sea informada de inmediato.

### HU-034: Consultar historial de incidencias (SAD)
Como trabajadora SAD / quiero ver todas las incidencias que he reportado con su estado y los comentarios de coordinación / para que pueda hacer seguimiento de su resolución.

---

## Recorridos de Usuario

### Journey 1: Reportar una incidencia desde el detalle del servicio
Actor: Trabajadora SAD | Objetivo: Comunicar a coordinación una incidencia del servicio o del cliente

1. La trabajadora accede al detalle del servicio (o a la pantalla de fichaje).
2. Pulsa "Reportar incidencia".
3. Se muestra el formulario de reporte de incidencia.
4. La trabajadora selecciona el tipo de incidencia (Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros).
5. La trabajadora selecciona el servicio relacionado (si no está preseleccionado).
6. Introduce la descripción (obligatorio, mínimo 20 caracteres).
7. Adjunta fotos y/o documentos de forma opcional (hasta 5 fotos y hasta 3 documentos).
8. Envía el reporte.
9. La app muestra confirmación de envío.

Estado de éxito: La incidencia es inmediatamente visible para las coordinadoras. La trabajadora puede seguir su estado desde el historial de incidencias.

Flujos alternativos:
- Si la descripción tiene menos de 20 caracteres → la app muestra error de validación antes de enviar.
- Si un archivo no puede enviarse → la app informa antes de intentar la subida.

---

## Resultados y Éxito

- **Servicio gestionado correctamente**: Las coordinadoras pueden ver las notas e incidencias registradas sobre el servicio en tiempo real.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Experiencia general:**
- Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse.
- La trabajadora puede adjuntar fotos y documentos. El sistema informa si un archivo no puede enviarse antes de intentar la subida.

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Detalle del servicio | Pulsa "Reportar incidencia" | Formulario de reporte de incidencia |
| Pantalla de fichaje | Pulsa "Reportar incidencia de fichaje" | Formulario de incidencia |

---

## Criterios de Aceptación

### CA-001: Reportar incidencia — formulario completo ← HU-021
GIVEN la trabajadora SAD accede al formulario de reporte de incidencia
WHEN completa el formulario
THEN puede seleccionar el tipo (Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros), seleccionar servicio relacionado, introducir descripción (obligatorio, mínimo 20 caracteres), adjuntar hasta 5 fotos y hasta 3 documentos de forma opcional.

---

### CA-002: Reportar incidencia — confirmación y visibilidad ← HU-021
GIVEN la trabajadora SAD envía un reporte de incidencia válido
WHEN la solicitud se procesa
THEN la app muestra confirmación de envío; la incidencia es inmediatamente visible para las coordinadoras.

---

### CA-003: Historial de incidencias ← HU-034
GIVEN la trabajadora SAD accede al historial de incidencias
WHEN la lista se carga
THEN las incidencias aparecen en orden cronológico inverso con número, tipo, fecha y estado (Reportada, En revisión, Resuelta, Cerrada); puede filtrar por estado, por rango de fechas y buscar por número o descripción; al tocar una incidencia ve los detalles completos y los comentarios de las coordinadoras.

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
