# Spec: Notifications
> Versión: 1.0 | Fecha: 2026-04-02
> Spec monolítico origen: prd-hogar-sad_spec.md
> Feature ID: F-011

---

## Actores
| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades. Usa la app CUIDEO (identidad visual azul). | Recibir notificaciones push para eventos relevantes, consultar historial de notificaciones. |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona servicios asignados. Usa la app Felizvita (identidad visual verde). | Recibir notificaciones push para eventos relevantes, consultar historial de notificaciones. |
| Sistema / Backoffice | Equipo de coordinación y administración que gestiona el backend y los datos. | Disparar notificaciones automáticas del sistema (recordatorios, avisos de cambio de estado, etc.). No es un actor de la app móvil pero sus acciones generan estados visibles para las trabajadoras. |

---

## Historias de Usuario

### HU-030: Recibir notificaciones push
Como trabajadora (Hogar o SAD) / quiero recibir notificaciones push para eventos relevantes (mensajes, llamamientos, cambios de estado, recordatorios) / para que pueda reaccionar a tiempo sin necesidad de abrir la app constantemente.

### HU-031: Consultar el historial de notificaciones
Como trabajadora (Hogar o SAD) / quiero ver un historial de las notificaciones recibidas / para que pueda revisar avisos que no leí en el momento.

---

## Recorridos de Usuario

### Journey 1: Recibir y actuar sobre una notificación push
Actor: Trabajadora Hogar o SAD | Objetivo: Recibir una notificación y navegar a la pantalla correspondiente

1. El sistema genera un evento que requiere notificar a la trabajadora (nuevo mensaje, llamamiento, cambio de estado de ausencia, recordatorio).
2. La trabajadora recibe la notificación push en su dispositivo.
3. La trabajadora toca la notificación.
4. La app se abre (o pasa a primer plano) y navega directamente a la pantalla específica relacionada vía deeplink.

Estado de éxito: La trabajadora llega a la pantalla relacionada con la notificación sin pasos de navegación adicionales.

Flujos alternativos:
- Si la app está en primer plano → se muestra una alerta in-app (en lugar de notificación del sistema).
- Si la app está en segundo plano o cerrada → se muestra notificación del sistema.

---

## Resultados y Éxito

- **Comunicación efectiva**: Las notificaciones push se entregan incluso cuando la app está en segundo plano o cerrada.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Comunicación:**
- Las notificaciones push se entregan incluso cuando la app está en segundo plano o cerrada.

**Experiencia general:**
- Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse.

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Notificación push | Toca notificación | Pantalla específica relacionada via deeplink |
| Historial de notificaciones | Toca una notificación | Contenido relacionado via deeplink |

---

## Criterios de Aceptación

### CA-001: Notificaciones push — solicitud de permiso ← HU-030
GIVEN la trabajadora acaba de hacer login por primera vez
WHEN se inicia el flujo de onboarding
THEN la app solicita permiso de notificaciones push antes de mostrar las pantallas de onboarding; el token del dispositivo queda vinculado al usuario concreto.

---

### CA-002: Notificaciones push — recepción en todos los estados ← HU-030
GIVEN la trabajadora tiene permiso de notificaciones activado
WHEN llega una notificación
THEN la notificación se recibe y muestra independientemente de si la app está en primer plano (alerta dentro de la app), segundo plano (notificación del sistema) o cerrada (notificación del sistema); la notificación incluye título, cuerpo e icono; tocar la notificación abre la app en la pantalla específica relacionada vía deeplink.

---

### CA-003: Historial de notificaciones ← HU-031
GIVEN la trabajadora accede al historial de notificaciones (asunción P-009)
WHEN la pantalla se carga
THEN se muestra un listado de notificaciones recibidas con título, cuerpo y fecha; tocar una notificación abre el contenido relacionado vía deeplink; existe la opción de marcar todas como leídas; no se pueden borrar notificaciones individuales desde el historial.

---

### CA-004: Notificaciones automáticas del sistema ← HU-030
GIVEN el sistema detecta condiciones que requieren recordatorio
WHEN se cumplen las condiciones
THEN se envían automáticamente: recordatorio de disponibilidad si no se actualiza en 30 días; aviso de caducidad de documento 30 días antes; recordatorio de servicio 1 día antes; recordatorio de fichar entrada N minutos después del inicio si no se ha fichado (N configurable); aviso de ausencia próxima 1 día antes.

---

### CA-005: Notificación de servicio próximo mañana — múltiples servicios ← HU-030
GIVEN la trabajadora tiene más de un servicio programado para mañana (asunción P-010)
WHEN el sistema envía las notificaciones de servicio próximo mañana
THEN se envía una notificación separada por cada servicio programado para el día siguiente, cada una con deeplink al detalle del servicio correspondiente.

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
- Configuración de preferencias de notificaciones por tipo (previsto para una fase futura)
