# Spec: Notificaciones Push

> Version: 1.0 | Fecha: 2026-04-05
> Spec monolitico origen: prd-hogar-sad_spec.md
> Feature ID: F-012

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades de empleo a traves de la app CUIDEO (tema azul) | Registrar dispositivo para notificaciones, recibir notificaciones push, consultar historial de notificaciones, navegar a destino desde notificacion |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios asignados a traves de la app Felizvita (tema verde) | Registrar dispositivo para notificaciones, recibir notificaciones push, consultar historial de notificaciones, navegar a destino desde notificacion |
| Sistema | El propio sistema automatizado que ejecuta acciones programadas sin intervencion humana | Enviar notificaciones push automaticas (recordatorios de fichaje, caducidad de documentos, servicio proximo, disponibilidad) |

---

## Historias de Usuario

### HU-020: Deeplinks de notificaciones push
Como trabajadora (Hogar o SAD)
quiero que al tocar una notificacion push la app me lleve directamente a la pantalla relevante
para que pueda actuar rapidamente sobre el evento notificado sin buscar manualmente.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-002]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-021: Notificaciones automaticas del sistema
Como trabajadora (Hogar o SAD)
quiero recibir recordatorios automaticos de acciones importantes
para que no olvide fichar, actualizar disponibilidad, renovar documentos o preparar servicios proximos.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-002]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-031: Registrar dispositivo para notificaciones push
Como trabajadora (Hogar o SAD)
quiero que mi dispositivo quede registrado para recibir notificaciones push
para que me lleguen avisos importantes de servicios, mensajes y recordatorios.

### HU-042: Historial de notificaciones
Como trabajadora (Hogar o SAD)
quiero consultar el historial de notificaciones recibidas
para que pueda revisar avisos pasados que haya podido perder.

---

## Recorridos de Usuario

Esta feature no tiene un journey dedicado independiente. Las notificaciones push son transversales a todas las features y actuan como mecanismo de comunicacion del sistema con la trabajadora. El registro de dispositivo ocurre durante el primer acceso (Journey 1 y 2 de la feature authentication). Los deeplinks de notificaciones llevan a las pantallas correspondientes de cada feature.

Flujo de registro de dispositivo:
1. La trabajadora inicia sesion por primera vez.
2. El sistema solicita permiso de notificaciones push (despues del login, antes del onboarding).
3. Si la trabajadora acepta, el dispositivo se registra para recibir notificaciones push vinculadas a su usuario.

Flujo de recepcion y actuacion:
1. La trabajadora recibe una notificacion push (app en primer plano, segundo plano o cerrada).
2. La notificacion muestra titulo, cuerpo e icono.
3. Al tocar la notificacion, la app navega a la pantalla relevante.

Flujo de consulta de historial:
1. La trabajadora accede al historial de notificaciones.
2. Se muestran las notificaciones en orden cronologico inverso con titulo, cuerpo y fecha.
3. Puede marcar todas como leidas.

---

## Resultados y Exito

- **Notificaciones**: Las trabajadoras reciben notificaciones push oportunas para todos los eventos importantes y pueden actuar rapidamente desde la notificacion.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Permiso de notificaciones**: Se solicita despues del primer login y antes del onboarding, para vincular el dispositivo al usuario autenticado.
- **Historial de notificaciones**: Las notificaciones se listan en orden cronologico inverso mostrando titulo, cuerpo y fecha. Se pueden marcar todas como leidas pero no se pueden borrar individualmente.
- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.

### Destinos de navegacion

> ⚠ Tabla de destinos de navegacion para deeplinks de notificaciones push pendiente de definicion (gap P-002). Los tipos de notificacion definidos son:
> - Nuevo mensaje recibido
> - Conversacion cerrada por coordinacion
> - Llamada de servicio disponible
> - Cambio de estado de solicitud
> - Cambio de estado de solicitud de ausencia
> - Servicio comenzando pronto (ventana de fichaje abierta)
> - Servicio proximo manana
> - Documento caducando pronto
> - Actualizacion de incidencia
> - Nuevo comunicado en el tablon
>
> Asuncion aplicada (P-016): La notificacion de "Conversacion cerrada" navega directamente al hilo de la conversacion cerrada en modo lectura.

---

## Criterios de Aceptacion

### CA-001: Registro de dispositivo para notificaciones ← HU-031
GIVEN la trabajadora ha iniciado sesion por primera vez
WHEN el sistema solicita permiso de notificaciones push (despues del login, antes del onboarding)
THEN si acepta, el dispositivo se registra para recibir notificaciones push vinculadas a su usuario

### CA-002: Recepcion de notificaciones push ← HU-031
GIVEN la trabajadora tiene notificaciones habilitadas
WHEN ocurre un evento relevante (nuevo mensaje, llamamiento, cambio de estado, recordatorio, etc.)
THEN recibe la notificacion push con titulo, cuerpo e icono tanto si la app esta en primer plano (alerta in-app), segundo plano (notificacion del sistema) o cerrada (notificacion del sistema)

### CA-003: Historial de notificaciones ← HU-042
GIVEN la trabajadora accede al historial de notificaciones
WHEN se carga la lista
THEN se muestran las notificaciones en orden cronologico inverso con titulo, cuerpo y fecha. Se pueden marcar todas como leidas. No se pueden borrar individualmente

---

## Checklist de Validacion

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [ ] Ambiguedades resueltas — gap P-002 pendiente (tabla de destinos de deeplinks)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [ ] Destinos de navegacion enumerados con sus variantes — pendiente de gap P-002

---

## Fuera de Alcance

- Eventos de analytics personalizados: solo analitica basica automatica; sin eventos personalizados en el MVP.
