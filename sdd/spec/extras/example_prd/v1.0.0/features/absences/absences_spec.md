# Spec: Absences
> Versión: 1.0 | Fecha: 2026-04-02
> Spec monolítico origen: prd-hogar-sad_spec.md
> Feature ID: F-008

---

## Actores
| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona servicios asignados. Usa la app Felizvita (identidad visual verde). | Solicitar ausencias, consultar historial de ausencias y contadores de vacaciones, cancelar solicitudes pendientes. |
| Sistema / Backoffice | Equipo de coordinación y administración que gestiona el backend y los datos. | Aprobar o rechazar solicitudes de ausencia. No es un actor de la app móvil pero sus acciones generan estados visibles para las trabajadoras. |

---

## Historias de Usuario

### HU-019: Consultar historial de ausencias y saldo de vacaciones (SAD)
Como trabajadora SAD / quiero ver todas mis solicitudes de ausencia con su estado y los contadores de vacaciones disponibles / para que pueda planificar mis ausencias conociendo mi saldo real.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-005]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

### HU-020: Solicitar una ausencia (SAD)
Como trabajadora SAD / quiero solicitar vacaciones, baja médica u otro tipo de ausencia / para que coordinación pueda revisarla y aprobarla.

---

## Recorridos de Usuario

### Journey 6: Solicitar una ausencia (SAD)
Actor: Trabajadora SAD | Objetivo: Enviar una solicitud de ausencia para aprobación

1. La trabajadora accede a "Solicitar Ausencia" desde la home o el menú.
2. Selecciona el tipo de ausencia (Vacaciones, Permiso personal, Baja médica, Baja voluntaria, Asuntos propios, Otros).
3. Selecciona el rango de fechas (inicio y fin, con opción de medio día en ambas).
4. La app muestra el saldo de vacaciones disponible (si aplica al tipo seleccionado).
5. Si las fechas entran en conflicto con servicios asignados, la app muestra una advertencia.
6. La trabajadora introduce el motivo/descripción (obligatorio en los tipos que lo requieren).
7. Si es baja médica de más de 3 días, adjunta el certificado médico (obligatorio).
8. La trabajadora envía la solicitud.
9. La app confirma el envío y la trabajadora recibe una notificación push de confirmación.

Estado de éxito: La solicitud aparece en el historial de ausencias con estado "Pendiente" y la trabajadora recibe notificación de cambio de estado cuando coordinación la resuelve.

Flujos alternativos:
- Si la trabajadora quiere cancelar una solicitud pendiente → puede hacerlo desde el historial de ausencias.

---

## Resultados y Éxito

- **Ausencia solicitada**: La solicitud aparece en el historial con estado "Pendiente"; los contadores de vacaciones reflejan los días pendientes de aprobación.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Experiencia general:**
- Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse.
- La trabajadora puede adjuntar fotos y documentos. El sistema informa si un archivo no puede enviarse antes de intentar la subida.

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Pantalla de fichaje | Pulsa "Solicitar ausencia" | Formulario de solicitud de ausencia |

---

## Criterios de Aceptación

### CA-001: Solicitar ausencia — formulario completo ← HU-020
GIVEN la trabajadora SAD accede al formulario de solicitud de ausencia
WHEN completa el formulario
THEN puede seleccionar el tipo (Vacaciones, Permiso personal, Baja médica, Baja voluntaria, Asuntos propios, Otros), el rango de fechas con opción de medio día en fechas de inicio/fin, y el motivo/descripción (obligatorio en los tipos que lo requieren); se muestra el saldo de vacaciones disponible; si las fechas conflictan con servicios asignados, se muestra una advertencia.

---

### CA-002: Solicitar ausencia — certificado médico obligatorio para baja > 3 días ← HU-020
GIVEN la trabajadora SAD solicita una baja médica de más de 3 días
WHEN completa el formulario
THEN el campo de adjuntar certificado médico es obligatorio para enviar la solicitud.

---

### CA-003: Historial de ausencias — lista, contadores y cancelar ← HU-019
GIVEN la trabajadora SAD accede al historial de ausencias
WHEN la pantalla se carga
THEN las ausencias aparecen en orden cronológico inverso con tipo, fechas, recuento de días y estado (Pendiente, Aprobada, Rechazada, Cancelada); se muestran los contadores por tipo de ausencia (asignación anual total, días utilizados, días pendientes de aprobación, días disponibles); puede filtrar por estado, tipo de ausencia y año; puede cancelar solicitudes con estado "Pendiente".

---

### CA-004: Contadores de vacaciones — cómputo pendiente ← HU-019

> [INCOMPLETO] — Pendiente de gap [P-005]: el criterio de cómputo de vacaciones (días naturales o días laborables) no está definido. El CA de contadores no puede completarse hasta resolver el gap.

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
- [ ] Cómputo de vacaciones confirmado con cliente/legal ([P-005])

---

## Fuera de Alcance
No se han definido exclusiones explícitas para esta feature.
