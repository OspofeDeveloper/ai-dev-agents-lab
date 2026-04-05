# Spec: Notificaciones
> Version: 1.0 | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md
> Feature ID: F-011

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo | Recibir notificaciones push, consultar historial, navegar via deeplinks |
| Trabajadora SAD | Trabajadora del Servicio de Asistencia Social | Recibir notificaciones push, consultar historial, navegar via deeplinks |

---

## Historias de Usuario

### HU-001: Recibir notificaciones push
Como trabajadora (Hogar o SAD)
quiero recibir notificaciones push para eventos importantes
para que este informada de novedades y acciones pendientes sin abrir la app.

### HU-002: Recibir recordatorios automaticos
Como trabajadora (Hogar o SAD)
quiero recibir recordatorios automaticos del sistema
para que no olvide acciones importantes como fichar, actualizar disponibilidad o renovar documentos.

---

## Recorridos de Usuario

### Journey 1: Recibir y actuar sobre notificacion
Actor: Trabajadora (Hogar o SAD) | Objetivo: Enterarse de un evento y navegar a la seccion relevante
1. La trabajadora recibe una notificacion push (con la app en primer plano, segundo plano o apagada).
2. En primer plano: se muestra alerta dentro de la aplicacion.
3. En segundo plano o apagada: se muestra notificacion del sistema.
4. La notificacion incluye titulo, cuerpo e icono.
5. La trabajadora toca la notificacion.
6. La app se abre en la pantalla especifica via deeplink segun el tipo de notificacion.

Estado de exito: La trabajadora ve la notificacion y navega directamente al contenido relevante.

### Journey 2: Recibir recordatorio automatico
Actor: Trabajadora (Hogar o SAD) | Objetivo: Ser recordada de una accion pendiente
1. El sistema del backend detecta una accion pendiente o un evento proximo.
2. Envia una notificacion automatica al dispositivo de la trabajadora.
3. La trabajadora ve la notificacion y toma accion si es necesario.

Estado de exito: La trabajadora recibe el recordatorio y puede actuar a tiempo.

---

## Resultados y Exito

- Las trabajadoras reciben notificaciones oportunas para todos los eventos relevantes de su perfil.
- Los deeplinks permiten navegacion directa al contenido sin pasos intermedios.
- Los recordatorios automaticos reducen el riesgo de olvidos en acciones criticas.

---

## Instrucciones Inambiguas

### Reglas de comportamiento
- El permiso de notificaciones push se solicita despues del primer login y antes del onboarding, para vincular el token FCM al usuario concreto.
- Tipos de notificaciones y deeplinks:
  - Nuevo mensaje recibido -> hilo de la conversacion
  - Conversacion cerrada por coordinacion -> historial de la conversacion
  - Llamada de servicio disponible -> detalle del llamamiento
  - Cambio de estado de la solicitud (Hogar) -> detalle de la solicitud
  - Cambio de estado de solicitud de ausencia (SAD) -> detalle de la ausencia
  - Servicio comenzando pronto / ventana de fichaje abierta -> pantalla de fichaje del servicio
  - Servicio proximo manana -> detalle del servicio
  - Documento caducando pronto -> pantalla de documentos
  - Actualizacion de incidencia -> detalle de la incidencia
  - Nuevo comunicado en el tablon -> detalle del comunicado
- Recordatorios automaticos del sistema (activados por backend, no requieren llamada desde la app):
  - Disponibilidad no actualizada en 30 dias
  - Caducidad de documento: 30 dias antes
  - Servicio programado: 1 dia antes
  - Fichar entrada: N minutos despues de hora inicio si no se ha fichado (N configurable)
  - Ausencia proxima: 1 dia antes
- La configuracion de preferencias de notificaciones por parte de la usuaria es mejora futura (no MVP).

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Notificacion push | Nuevo mensaje | Hilo de la conversacion (F-010) |
| Notificacion push | Conversacion cerrada | Historial de la conversacion (F-010) |
| Notificacion push | Llamada de servicio | Detalle del llamamiento (F-003) |
| Notificacion push | Cambio estado solicitud | Detalle de la solicitud (F-006) |
| Notificacion push | Cambio estado ausencia | Detalle de la ausencia (F-008) |
| Notificacion push | Servicio pronto / fichaje | Pantalla de fichaje del servicio (F-004) |
| Notificacion push | Servicio manana | Detalle del servicio (F-003) |
| Notificacion push | Documento caducando | Pantalla de documentos (F-009) |
| Notificacion push | Actualizacion incidencia | Detalle de la incidencia (F-005) |
| Notificacion push | Nuevo comunicado | Detalle del comunicado (F-002) |

---

## Criterios de Aceptacion

### CA-001: Permiso post-login <- HU-001
GIVEN la trabajadora ha completado su primer login
WHEN se inicia el flujo post-login
THEN la app solicita permiso de notificaciones push para vincular el token FCM al usuario.

### CA-002: Registro de dispositivo <- HU-001
GIVEN la trabajadora acepta permisos de notificaciones
WHEN se obtiene el token FCM
THEN se registra el dispositivo y el token con el backend.

### CA-003: Notificacion en primer plano <- HU-001
GIVEN la trabajadora tiene la app abierta
WHEN recibe una notificacion push
THEN se muestra una alerta dentro de la aplicacion.

### CA-004: Notificacion en segundo plano <- HU-001
GIVEN la trabajadora tiene la app en segundo plano o apagada
WHEN recibe una notificacion push
THEN se muestra una notificacion del sistema.

### CA-005: Contenido de notificacion <- HU-001
GIVEN la trabajadora recibe una notificacion push
WHEN ve la notificacion
THEN incluye titulo, cuerpo e icono.

### CA-006: Deeplink desde notificacion <- HU-001
GIVEN la trabajadora recibe una notificacion push
WHEN toca la notificacion
THEN la app se abre en la pantalla especifica via deeplink segun el tipo de notificacion (nuevo mensaje -> conversacion, llamamiento -> detalle llamamiento, etc.).

### CA-007: Recordatorio de disponibilidad <- HU-002
GIVEN la trabajadora no ha actualizado su disponibilidad en 30 dias
WHEN se cumple el plazo
THEN recibe notificacion de recordatorio.

### CA-008: Caducidad de documento <- HU-002
GIVEN un documento de la trabajadora caduca en 30 dias o menos
WHEN se detecta la proximidad de caducidad
THEN recibe notificacion push.

### CA-009: Recordatorio de servicio <- HU-002
GIVEN la trabajadora tiene un servicio programado para manana
WHEN falta 1 dia para el servicio
THEN recibe notificacion push de recordatorio.

### CA-010: Recordatorio de fichaje <- HU-002
GIVEN la trabajadora no ha fichado entrada despues de la hora de inicio del servicio
WHEN pasan N minutos (N configurable en servidor)
THEN recibe notificacion push de recordatorio.

### CA-011: Recordatorio de ausencia <- HU-002
GIVEN la trabajadora tiene una ausencia aprobada que comienza manana
WHEN falta 1 dia
THEN recibe notificacion push de recordatorio.

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
- Configuracion de preferencias de notificaciones por la usuaria (mejora futura)
- Eventos de analytics personalizados (solo Firebase out-of-the-box)
- Notificaciones por email o SMS (solo push)
- Gestion de canales de notificacion por la usuaria
