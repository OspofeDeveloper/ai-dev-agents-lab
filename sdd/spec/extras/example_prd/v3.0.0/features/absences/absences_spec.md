# Spec: Gestion de Ausencias

> Version: 1.0 | Fecha: 2026-04-05
> Spec monolitico origen: prd-hogar-sad_spec.md
> Feature ID: F-007

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios asignados a traves de la app Felizvita (tema verde) | Solicitar ausencias con tipo, fechas, justificacion y documentacion; consultar historial de ausencias y saldo de vacaciones; cancelar solicitudes pendientes |
| Coordinadora / Backoffice | Profesional de gestion interna que supervisa a las trabajadoras. No usa la app movil directamente; interactua a traves del sistema de backoffice | Aprobar/rechazar ausencias, comentar solicitudes |

---

## Historias de Usuario

### HU-026: Solicitar ausencia (SAD)
Como trabajadora SAD
quiero solicitar tiempo libre indicando tipo, fechas y justificacion
para que coordinacion pueda gestionar mi ausencia y reorganizar los servicios.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-009]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-027: Historial de ausencias (SAD)
Como trabajadora SAD
quiero ver todas mis solicitudes de ausencia con su estado y saldo de vacaciones
para que pueda planificar mis ausencias y conocer los dias disponibles.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-009]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

---

## Recorridos de Usuario

### Journey 9: Solicitar ausencia (SAD)
Actor: Trabajadora SAD | Objetivo: Solicitar tiempo libre

1. La trabajadora accede a "Solicitar Ausencia" desde la home o la seccion de ausencias.
2. Selecciona el tipo de ausencia: Vacaciones, Permiso personal, Baja medica, Baja voluntaria, Asuntos propios, Otros.
3. Selecciona rango de fechas (con opcion de medio dia para inicio y final).
4. Si es baja medica de mas de 3 dias: debe adjuntar certificado medico.
5. Introduce motivo/descripcion (obligatorio para algunos tipos).
6. El sistema muestra el saldo de vacaciones disponible antes de enviar.
7. Si las fechas entran en conflicto con servicios asignados: se muestra una advertencia.
8. La trabajadora envia la solicitud.
9. Recibe notificacion push de confirmacion de envio.

Estado de exito: La solicitud de ausencia ha sido enviada para aprobacion por coordinacion.

### Journey 15: Consultar historial de ausencias (SAD)
Actor: Trabajadora SAD | Objetivo: Revisar sus solicitudes de ausencia y saldo

1. La trabajadora accede a "Mis Ausencias".
2. El sistema muestra la lista de ausencias en orden cronologico inverso con: tipo, fechas, recuento de dias y estado (Pendiente, Aprobada, Rechazada, Cancelada).
3. Se muestran los contadores por tipo de ausencia (vacaciones: asignacion total, dias utilizados, dias pendientes de aprobacion, dias disponibles).
4. La trabajadora puede filtrar por estado, tipo y ano.
5. Toca una ausencia para ver detalle y comentarios de coordinadora.
6. Puede cancelar solicitudes que esten en estado Pendiente.

Estado de exito: La trabajadora ha consultado su historial de ausencias y conoce su saldo disponible.

---

## Resultados y Exito

- **Ausencias (SAD)**: Las trabajadoras SAD pueden solicitar ausencias con la documentacion requerida y consultar su saldo de vacaciones.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.
- **Permiso de camara/archivos**: Se solicita solo en el momento en que se necesite (ej: al adjuntar certificado medico), no durante el onboarding.

---

## Criterios de Aceptacion

### CA-001: Solicitar ausencia con documentacion ← HU-026
GIVEN la trabajadora SAD accede a "Solicitar Ausencia"
WHEN selecciona tipo (Vacaciones, Permiso personal, Baja medica, Baja voluntaria, Asuntos propios, Otros), rango de fechas (con opcion de medio dia), motivo y adjuntos si procede
THEN el sistema muestra el saldo de vacaciones disponible. Si las fechas entran en conflicto con servicios asignados, muestra advertencia. Al enviar, la trabajadora recibe notificacion de confirmacion

> ⚠ Parcial: El calculo del saldo de vacaciones depende de la resolucion de gap P-009 (dias naturales vs. laborables).

### CA-002: Certificado medico obligatorio para baja larga ← HU-026
GIVEN la trabajadora SAD solicita una baja medica de mas de 3 dias
WHEN intenta enviar la solicitud sin adjuntar certificado medico
THEN el sistema bloquea el envio e indica que el certificado medico es obligatorio

### CA-003: Historial de ausencias con contadores ← HU-027
GIVEN la trabajadora SAD accede a "Mis Ausencias"
WHEN se carga la lista
THEN se muestran las ausencias en orden cronologico inverso con: tipo, fechas, recuento de dias, estado (Pendiente, Aprobada, Rechazada, Cancelada). Se muestran contadores por tipo de ausencia. Se puede filtrar por estado, tipo y ano

> ⚠ Parcial: El computo de vacaciones (dias naturales o laborables) depende de la resolucion de gap P-009.

### CA-004: Cancelar ausencia pendiente ← HU-027
GIVEN la trabajadora SAD tiene una solicitud de ausencia en estado Pendiente
WHEN elige cancelarla
THEN la solicitud cambia a estado Cancelada

### CA-005: Detalle de ausencia con comentarios ← HU-027
GIVEN la trabajadora SAD toca una ausencia en el historial
WHEN se abre el detalle
THEN se muestra la informacion completa y los comentarios de la coordinadora

---

## Checklist de Validacion

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [ ] Ambiguedades resueltas — gap P-009 pendiente (dias naturales vs. laborables)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- Funcionalidades de backoffice/coordinacion: este spec cubre exclusivamente la experiencia desde la app movil de la trabajadora.
