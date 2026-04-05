# Spec: Control Horario

> Version: 1.0 | Fecha: 2026-04-05
> Spec monolitico origen: prd-hogar-sad_spec.md
> Feature ID: F-005

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios asignados a traves de la app Felizvita (tema verde) | Fichar entrada y salida con geolocalizacion, consultar historial de seguimiento de tiempo |
| Sistema | El propio sistema automatizado que ejecuta acciones programadas sin intervencion humana | Enviar notificaciones de recordatorio de fichaje |

---

## Historias de Usuario

### HU-022: Fichar entrada y salida (SAD)
Como trabajadora SAD
quiero fichar mi entrada y salida de un servicio con captura de ubicacion
para que quede constancia verificable del tiempo trabajado en cada servicio.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-011]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-023: Historial de seguimiento de tiempo (SAD)
Como trabajadora SAD
quiero ver todos mis registros de entrada y salida agrupados por servicio
para que pueda revisar mi historial de tiempo trabajado.

---

## Recorridos de Usuario

### Journey 6: Fichar entrada y salida de servicio (SAD)
Actor: Trabajadora SAD | Objetivo: Registrar el inicio y fin de un servicio

1. La trabajadora recibe una notificacion push indicando que puede fichar (configurable, enviada antes del inicio del servicio). El mensaje incluye su nombre y el nombre del receptor del servicio.
2. La trabajadora accede al fichaje desde la home, el detalle del servicio o el tab de fichaje.
3. El boton de fichaje muestra estados dinamicos: "Disponible en X min" (antes de los 30 minutos previos), "Fichar entrada" (activo 30 minutos antes del inicio del servicio), "Fichada - en servicio", "Fichar salida", "Servicio finalizado".
4. La trabajadora selecciona el servicio de la lista de servicios activos (si accede desde home o tab de fichaje).
5. La trabajadora pulsa "Fichar entrada".
6. El sistema captura las coordenadas GPS. Si la precision de ubicacion es baja, muestra una advertencia (espera maximo 2 segundos) pero permite continuar.
7. Se confirma la entrada y el sistema muestra un contador de tiempo transcurrido.
8. Al finalizar, la trabajadora pulsa "Fichar salida".
9. El sistema muestra un dialogo de confirmacion.
10. La trabajadora confirma y se registra la salida con coordenadas GPS.

Estado de exito: La trabajadora ha fichado entrada y salida correctamente con registro de ubicacion y tiempo.

Flujos alternativos:
- Si la trabajadora no ficha la salida tras finalizar: se muestra un aviso visible (banner o notificacion in-app) recordando la accion pendiente. El aviso no bloquea la navegacion.
- Si la trabajadora necesita reportar un problema de fichaje: desde la pantalla de fichaje puede reportar una incidencia de fichaje o solicitar una ausencia.
- Si no hay fichajes entre servicios del mismo dia: cada servicio se gestiona de forma independiente.

---

## Resultados y Exito

- **Fichaje (SAD)**: Las trabajadoras SAD fichan entrada y salida con captura de ubicacion de forma fluida desde multiples puntos de acceso. El fichaje se activa en la ventana temporal correcta y el sistema registra tanto el tiempo como las coordenadas.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Fichaje sin bloqueo por ubicacion**: El fichaje esta permitido incluso sin precision optima de ubicacion. Si la precision es baja, se muestra advertencia y se espera maximo 2 segundos antes de permitir continuar.
- **Ventana de fichaje**: El boton de fichaje de entrada se activa 30 minutos antes del inicio del servicio. Fuera de esa ventana aparece deshabilitado con indicacion visual del tiempo restante.
- **Warning de fichaje de salida pendiente**: Si la trabajadora no ficha la salida tras finalizar el servicio, se muestra un aviso visible (banner o notificacion in-app). Este aviso no bloquea la navegacion ni el acceso al resto de la app.
- **Fichaje independiente por servicio**: Los fichajes entre servicios del mismo dia se gestionan de forma independiente (no se bloquean entre si).
- **No hay fichaje manual**: Las correcciones de fichaje se gestionan desde backoffice, no desde la app de la trabajadora.
- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.

---

## Criterios de Aceptacion

### CA-001: Fichar entrada con geolocalizacion ← HU-022
GIVEN la trabajadora SAD ha seleccionado un servicio activo y faltan 30 minutos o menos para el inicio
WHEN pulsa "Fichar entrada"
THEN el sistema captura las coordenadas GPS y registra la entrada. Se muestra un contador de tiempo transcurrido

### CA-002: Advertencia de precision baja al fichar ← HU-022
GIVEN la trabajadora SAD esta fichando entrada o salida
WHEN la precision de ubicacion GPS es baja
THEN se muestra una advertencia (espera maximo 2 segundos) pero se permite continuar con el fichaje

### CA-003: Fichar salida con confirmacion ← HU-022
GIVEN la trabajadora SAD esta fichada en un servicio
WHEN pulsa "Fichar salida"
THEN se muestra un dialogo de confirmacion. Al confirmar, se capturan las coordenadas GPS y se registra la salida

### CA-004: Estados dinamicos del boton de fichaje ← HU-022
GIVEN la trabajadora SAD ve el boton de fichaje de un servicio
WHEN consulta el estado del boton en diferentes momentos
THEN el boton muestra: "Disponible en X min" (fuera de ventana), "Fichar entrada" (en ventana de 30 min), "Fichada - en servicio" (fichada), "Fichar salida" (disponible para salida), "Servicio finalizado" (tras fichar salida)

### CA-005: Warning de salida pendiente ← HU-022
GIVEN la trabajadora SAD no ha fichado la salida tras finalizar el horario del servicio
WHEN continua usando la app
THEN se muestra un aviso visible (banner o notificacion in-app) recordando la accion pendiente, sin bloquear la navegacion

### CA-006: Incidencia de fichaje o solicitud de ausencia desde fichaje ← HU-022
GIVEN la trabajadora SAD esta en la pantalla de fichaje
WHEN necesita reportar un problema o ausencia
THEN tiene opcion de reportar una incidencia de fichaje o solicitar una ausencia directamente desde la pantalla

### CA-007: Notificacion de fichaje previo al servicio ← HU-022
GIVEN se acerca la hora de inicio de un servicio
WHEN faltan N minutos (configurado por el servidor)
THEN la trabajadora recibe una notificacion push con su nombre y el nombre del receptor del servicio (ej: "Buenos dias [nombre], ya puedes fichar para el servicio del Sr./Sra. [nombre_receptor]")

### CA-008: Historial de fichajes por servicio ← HU-023
GIVEN la trabajadora SAD accede al historial de seguimiento de tiempo
WHEN se carga el historial
THEN se muestran todos los registros agrupados por servicio y por dias con: fecha, hora de entrada, hora de salida, duracion. Se puede filtrar por rango de fechas y por servicio. No se muestran conteos de horas extra ni diferencias respecto a horas contratadas

---

## Checklist de Validacion

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [ ] Ambiguedades resueltas — gap P-011 pendiente (comportamiento sin permiso de ubicacion)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- Deteccion de GPS simulado: no incluida en esta version.
- Modo offline con sincronizacion: no incluido. Toda accion requiere conexion a internet.
