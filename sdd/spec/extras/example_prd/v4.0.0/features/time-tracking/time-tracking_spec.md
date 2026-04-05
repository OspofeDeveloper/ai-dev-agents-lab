# Spec: Control Horario (Time Tracking)
> Versión: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-004 via prd-hogar-sad_discovery.md)
> Feature ID: F-004
> Spec monolítico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD (Felizvita) | Profesional del Servicio de Asistencia Social contratada que presta servicios domiciliarios | Fichar entrada y salida de sus servicios, consultar historial de fichajes, reportar incidencia de fichaje |
| Sistema | Backend y lógica de la aplicación | Capturar geolocalización, calcular duración trabajada, enviar notificaciones de apertura de ventana de fichaje, mantener estados dinámicos del botón |

---

## Historias de Usuario

### HU-001: Fichar entrada al inicio del servicio
Como trabajadora SAD
quiero fichar mi entrada cuando comienzo a prestar un servicio
para que quede registrado el inicio de mi jornada de forma precisa y verificable por ubicación

### HU-002: Fichar salida al finalizar el servicio
Como trabajadora SAD
quiero fichar mi salida cuando termino un servicio
para que quede registrado el fin de la jornada y pueda consultarse la duración total del servicio

### HU-003: Ser notificada cuando se abre la ventana de fichaje
Como trabajadora SAD
quiero recibir una notificación antes del inicio de mi servicio
para que sepa cuándo puedo comenzar a fichar y no lo olvide

### HU-004: Ver el tiempo transcurrido mientras estoy fichada
Como trabajadora SAD
quiero ver un contador de tiempo activo mientras tengo un servicio en curso
para que pueda hacer seguimiento del tiempo que llevo prestando el servicio

### HU-005: Reportar una incidencia desde la pantalla de fichaje
Como trabajadora SAD
quiero reportar una incidencia o solicitar una ausencia directamente desde la pantalla de fichaje
para que pueda gestionar una situación imprevista (no asistencia, problema operativo) sin salir del flujo de fichaje

### HU-006: Consultar el historial de fichajes
Como trabajadora SAD
quiero ver todos mis registros de entrada y salida organizados por servicio y por mes
para que pueda comprobar mis horas trabajadas y resolver cualquier duda sobre mis registros

---

## Recorridos de Usuario

### Journey 1: Fichar entrada antes del inicio del servicio
Actor: Trabajadora SAD | Objetivo: Registrar el inicio de un servicio

1. La trabajadora recibe una notificación push indicando que puede fichar para el servicio del Sr./Sra. [nombre_receptor]. Esta notificación llega N minutos antes de la hora de inicio del servicio (N configurable por el sistema).
2. La trabajadora accede a la pantalla de fichaje desde la home, desde el detalle del servicio o desde el tab de fichaje.
3. El sistema muestra el botón de fichaje en estado "Fichar entrada" para el servicio cuya ventana de fichaje está activa (a partir de 30 minutos antes del inicio).
4. Si hay más de un servicio activo disponible, la trabajadora selecciona el servicio para el que quiere fichar.
5. El sistema solicita la ubicación del dispositivo y captura las coordenadas.
6. Si la precisión de la ubicación es baja (inferior a 50 metros), el sistema muestra una advertencia; la trabajadora puede continuar igualmente transcurrido un máximo de 2 segundos.
7. La trabajadora confirma el fichaje de entrada.
8. El sistema registra la entrada con la hora exacta y las coordenadas. La pantalla muestra el estado "Fichada · en servicio" con un contador de tiempo transcurrido en marcha.

Estado de éxito: La trabajadora ve la confirmación de fichaje y el contador de tiempo activo. El fichaje queda registrado en el sistema con hora y ubicación.

Flujos alternativos:
- Si el botón de fichaje aún no está activo (faltan más de 30 minutos para el inicio): el sistema muestra el estado "Disponible en X min" con el tiempo restante; el botón aparece deshabilitado.
- Si la trabajadora intenta fichar fuera de la ventana de 30 minutos antes del inicio: el sistema no permite la acción; el botón permanece deshabilitado con indicación del tiempo restante.

### Journey 2: Fichar salida al finalizar el servicio
Actor: Trabajadora SAD | Objetivo: Registrar el fin de un servicio

1. La trabajadora termina de prestar el servicio. La pantalla de fichaje muestra el estado "Fichar salida".
2. La trabajadora pulsa el botón "Fichar salida".
3. El sistema muestra un diálogo de confirmación antes de registrar la salida.
4. La trabajadora confirma la salida.
5. El sistema captura las coordenadas de salida, registra la hora exacta y calcula la duración total del servicio.
6. La pantalla pasa al estado "Servicio finalizado" y muestra el resumen del tiempo trabajado en ese servicio.

Estado de éxito: La trabajadora ve el estado "Servicio finalizado" con la duración total del servicio registrado.

Flujos alternativos:
- Si la trabajadora no ficha la salida una vez que la hora de fin programada ha pasado: el sistema muestra un aviso visible (banner o alerta in-app) recordando que hay una salida pendiente. Este aviso no bloquea la navegación ni el acceso al resto de la app.

### Journey 3: Reportar incidencia de fichaje desde la pantalla de fichaje
Actor: Trabajadora SAD | Objetivo: Comunicar que no ha podido asistir o fichar

1. La trabajadora no puede asistir al servicio o no puede realizar el fichaje.
2. Desde la pantalla de fichaje, la trabajadora accede a la opción de reportar incidencia o solicitar ausencia.
3. El sistema redirige al flujo de reporte de incidencias (tipo "Incidencia de fichaje / No asistencia") o al flujo de solicitud de ausencia, según lo que la trabajadora seleccione.
4. La trabajadora completa y envía la incidencia o la solicitud de ausencia.

Estado de éxito: La incidencia o la solicitud de ausencia queda registrada. La coordinación puede verla inmediatamente.

### Journey 4: Consultar historial de fichajes
Actor: Trabajadora SAD | Objetivo: Revisar sus registros de tiempo trabajado

1. La trabajadora accede al historial de seguimiento de tiempo.
2. El sistema muestra los registros agrupados por servicio y por días para el mes actual.
3. Cada registro muestra la fecha, la hora de entrada, la hora de salida y la duración.
4. La trabajadora puede filtrar por mes o por servicio concreto para localizar un registro específico.

Estado de éxito: La trabajadora puede ver todos sus registros de fichaje para el período y servicio seleccionados.

---

## Resultados y Éxito

La feature de control horario se considera completada cuando:

- La trabajadora puede fichar entrada y salida desde la home, el detalle del servicio y el tab de fichaje de forma indistinta.
- El botón de fichaje refleja en todo momento el estado correcto según la situación del servicio: "Disponible en X min", "Fichar entrada", "Fichada · en servicio", "Fichar salida" o "Servicio finalizado".
- Cada fichaje queda registrado con la hora exacta y las coordenadas de ubicación del dispositivo.
- El sistema avisa antes del inicio del servicio mediante notificación push con el nombre de la trabajadora y del receptor del servicio.
- La trabajadora puede consultar su historial completo de fichajes filtrado por servicio y por mes.
- Los servicios del mismo día (mañana y tarde) pueden ficharse de forma independiente sin interferencia entre ellos.
- La trabajadora puede reportar una incidencia de fichaje o solicitar una ausencia directamente desde la pantalla de fichaje sin necesidad de navegar a otro módulo.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Ventana de fichaje y estados del botón:**
- El botón de fichaje de entrada se activa 30 minutos antes de la hora de inicio del servicio. Fuera de esa ventana, el botón aparece deshabilitado con una indicación del tiempo restante ("Disponible en X min").
- Los estados posibles del botón son exactamente: "Disponible en X min", "Fichar entrada", "Fichada · en servicio", "Fichar salida", "Servicio finalizado". No existen estados intermedios.
- Si hay múltiples servicios activos simultáneamente con ventana de fichaje abierta, la trabajadora selecciona el servicio antes de realizar el fichaje.
- Los servicios del mismo día son independientes: fichar salida de un servicio de mañana no afecta al estado del botón del servicio de tarde; cada servicio gestiona su propio ciclo entrada/salida.

**Geolocalización:**
- El sistema captura las coordenadas del dispositivo tanto en la entrada como en la salida.
- Si la precisión de ubicación es baja (inferior a 50 metros), el sistema muestra una advertencia pero espera máximo 2 segundos antes de permitir que la trabajadora continúe con el fichaje. La ubicación baja no bloquea el fichaje; la trazabilidad se mantiene igualmente.
- La trabajadora no puede introducir ni modificar coordenadas manualmente desde la app.

**Correcciones y fichaje manual:**
- No se permite ningún tipo de fichaje manual desde la app. Si la trabajadora necesita corregir un fichaje, la corrección se gestiona exclusivamente desde el sistema de gestión interno (backoffice).

**Warning de salida pendiente:**
- Si la hora de fin programada del servicio ha pasado y la trabajadora no ha fichado la salida, el sistema muestra un aviso visible (banner o alerta in-app) recordando la acción pendiente.
- Este aviso no interrumpe ni bloquea ninguna navegación; la trabajadora puede seguir usando el resto de la app con normalidad.

**Historial:**
- El historial muestra únicamente la fecha, la hora de entrada, la hora de salida y la duración de cada registro.
- No se muestran conteos de horas extra ni diferencias respecto a las horas contratadas; esa información es de uso interno exclusivo.

**Acceso a incidencias y ausencias desde fichaje:**
- La pantalla de fichaje ofrece acceso directo al flujo de reporte de incidencias (con tipo preseleccionado "Incidencia de fichaje / No asistencia") y al flujo de solicitud de ausencia. El sistema diferencia visualmente ambas opciones para que la trabajadora elija la adecuada según su situación.

### Destinos de navegación

| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Notificación push de apertura de ventana de fichaje | La trabajadora pulsa la notificación | Pantalla de fichaje del servicio correspondiente |
| Home | La trabajadora pulsa el acceso directo de fichaje | Pantalla de fichaje (con lista de servicios activos si hay más de uno) |
| Detalle del servicio | La trabajadora pulsa "Fichar entrada/salida" | Pantalla de fichaje del servicio correspondiente |
| Tab de fichaje | Acceso directo desde la barra de navegación | Pantalla de fichaje (con lista de servicios activos si hay más de uno) |
| Pantalla de fichaje | La trabajadora pulsa "Reportar incidencia" | Flujo de reporte de incidencia (tipo "Incidencia de fichaje / No asistencia" preseleccionado) |
| Pantalla de fichaje | La trabajadora pulsa "Solicitar ausencia" | Flujo de solicitud de ausencia |
| Pantalla de fichaje / historial | La trabajadora pulsa "Ver historial" | Historial de seguimiento de tiempo |

---

## Criterios de Aceptación

### CA-001: Acceso al fichaje desde tres puntos de entrada ← HU-001
GIVEN la trabajadora SAD está autenticada y tiene al menos un servicio con ventana de fichaje activa
WHEN la trabajadora accede a la pantalla de fichaje desde la home, desde el detalle del servicio o desde el tab de fichaje
THEN la pantalla de fichaje muestra el botón en el estado correcto para ese servicio y la trabajadora puede realizar el fichaje desde cualquiera de los tres puntos de acceso

### CA-002: Botón deshabilitado fuera de la ventana de 30 minutos ← HU-001
GIVEN la trabajadora tiene un servicio programado cuya hora de inicio está a más de 30 minutos
WHEN la trabajadora accede a la pantalla de fichaje para ese servicio
THEN el botón de fichaje aparece deshabilitado con el estado "Disponible en X min" indicando el tiempo restante hasta la apertura de la ventana

### CA-003: Botón activo a partir de 30 minutos antes del inicio ← HU-001
GIVEN la trabajadora tiene un servicio programado cuya hora de inicio está entre 0 y 30 minutos en el futuro
WHEN la trabajadora accede a la pantalla de fichaje para ese servicio
THEN el botón muestra el estado "Fichar entrada" y la trabajadora puede pulsarlo para iniciar el fichaje

### CA-004: Selección de servicio cuando hay múltiples activos ← HU-001
GIVEN la trabajadora tiene más de un servicio con ventana de fichaje activa simultáneamente
WHEN la trabajadora accede a la pantalla de fichaje
THEN el sistema muestra la lista de servicios activos disponibles y la trabajadora debe seleccionar uno antes de proceder al fichaje

### CA-005: Captura de coordenadas en la entrada ← HU-001
GIVEN la trabajadora ha pulsado "Fichar entrada" para un servicio
WHEN el sistema procesa el fichaje de entrada
THEN el sistema registra las coordenadas de ubicación del dispositivo junto con la hora exacta de la entrada

### CA-006: Advertencia por precisión de ubicación baja (sin bloqueo) ← HU-001
GIVEN la trabajadora intenta fichar y la precisión de la ubicación del dispositivo es inferior a 50 metros
WHEN el sistema detecta la baja precisión
THEN el sistema muestra una advertencia informativa y, transcurridos máximo 2 segundos, permite a la trabajadora continuar con el fichaje igualmente

### CA-007: Estado "Fichada · en servicio" con contador de tiempo ← HU-004
GIVEN la trabajadora ha fichado la entrada de un servicio correctamente
WHEN la pantalla de fichaje está visible
THEN el botón muestra el estado "Fichada · en servicio" y se muestra un contador de tiempo transcurrido activo desde el momento del fichaje de entrada

### CA-008: Botón "Fichar salida" visible tras haber fichado entrada ← HU-002
GIVEN la trabajadora ha fichado la entrada de un servicio
WHEN accede a la pantalla de fichaje para ese servicio
THEN el sistema muestra el botón en estado "Fichar salida" (el estado "Fichar entrada" ya no es visible para ese servicio)

### CA-009: Diálogo de confirmación al fichar salida ← HU-002
GIVEN la trabajadora está en estado "Fichada · en servicio" y pulsa "Fichar salida"
WHEN el sistema muestra el diálogo de confirmación de salida
THEN el diálogo solicita confirmación explícita antes de registrar la salida; si la trabajadora cancela, el estado vuelve a "Fichada · en servicio" sin registrar ningún cambio

### CA-010: Registro de salida con hora, coordenadas y duración ← HU-002
GIVEN la trabajadora ha confirmado el fichaje de salida
WHEN el sistema procesa la salida
THEN el sistema registra la hora exacta de salida, las coordenadas del dispositivo y calcula la duración total del servicio; el botón pasa al estado "Servicio finalizado"

### CA-011: Notificación push de apertura de ventana de fichaje ← HU-003
GIVEN el sistema tiene configurado el parámetro N (minutos de antelación, configurable en el servidor)
WHEN se alcanza el momento N minutos antes del inicio del servicio de la trabajadora
THEN el sistema envía una notificación push que incluye el nombre de la trabajadora y el nombre del receptor del servicio (ej.: "Buenos días [nombre], ya puedes fichar para el servicio del Sr./Sra. [nombre_receptor]"); al pulsar la notificación, la app abre la pantalla de fichaje del servicio correspondiente

### CA-012: Independencia de fichajes entre servicios del mismo día ← HU-001, HU-002
GIVEN la trabajadora tiene dos servicios el mismo día (uno de mañana y otro de tarde)
WHEN la trabajadora ficha la salida del servicio de mañana
THEN el estado del botón del servicio de tarde no se ve afectado; el ciclo entrada/salida de cada servicio es completamente independiente

### CA-013: Warning de salida pendiente (no bloqueante) ← HU-002
GIVEN la hora de fin programada de un servicio ha pasado y la trabajadora no ha fichado la salida
WHEN la trabajadora navega por la app
THEN el sistema muestra un aviso visible (banner o alerta in-app) recordando la salida pendiente; este aviso no impide el acceso a ninguna pantalla ni bloquea ninguna acción

### CA-014: Sin fichaje manual desde la app ← HU-001, HU-002
GIVEN la trabajadora intenta introducir o modificar un fichaje manualmente
WHEN el sistema recibe la solicitud
THEN el sistema no ofrece ningún mecanismo de fichaje manual; la única forma de corregir fichajes es mediante el sistema de gestión interno (backoffice); la app muestra un mensaje informativo indicando que las correcciones deben solicitarse a coordinación

### CA-015: Acceso directo a incidencia de fichaje desde pantalla de fichaje ← HU-005
GIVEN la trabajadora está en la pantalla de fichaje
WHEN la trabajadora pulsa la opción de reportar incidencia
THEN el sistema navega al flujo de reporte de incidencias con el tipo "Incidencia de fichaje / No asistencia" preseleccionado

### CA-016: Acceso directo a solicitud de ausencia desde pantalla de fichaje ← HU-005
GIVEN la trabajadora está en la pantalla de fichaje
WHEN la trabajadora pulsa la opción de solicitar ausencia
THEN el sistema navega al flujo de solicitud de ausencia

### CA-017: Historial agrupado por servicio y por días ← HU-006
GIVEN la trabajadora accede al historial de seguimiento de tiempo
WHEN el sistema carga los registros
THEN los fichajes se muestran agrupados por servicio y por días; cada registro muestra la fecha, la hora de entrada, la hora de salida y la duración

### CA-018: Filtro del historial por mes ← HU-006
GIVEN la trabajadora está visualizando el historial de fichajes
WHEN la trabajadora selecciona un mes concreto como filtro
THEN el historial muestra únicamente los registros del mes seleccionado, agrupados por servicio y por días

### CA-019: Filtro del historial por servicio ← HU-006
GIVEN la trabajadora está visualizando el historial de fichajes
WHEN la trabajadora selecciona un servicio concreto como filtro
THEN el historial muestra únicamente los registros de fichaje correspondientes a ese servicio

### CA-020: No se muestran horas extra ni diferencias respecto al contrato ← HU-006
GIVEN la trabajadora visualiza el historial de fichajes
WHEN el sistema presenta los registros
THEN el historial muestra exclusivamente la fecha, hora de entrada, hora de salida y duración; no se muestran conteos de horas extra, desviaciones respecto a las horas contratadas ni ninguna información de gestión interna

---

## Checklist de Validación

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de éxito definidos
- [x] Edge cases documentados (precisión baja, múltiples servicios, salida pendiente, correcciones)
- [x] Estados de error definidos (botón deshabilitado fuera de ventana, aviso sin bloqueo)
- [x] Ambigüedades resueltas
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes

---

## Fuera de Alcance

- **Fichaje manual desde la app**: la trabajadora no puede introducir ni corregir fichajes; las correcciones son exclusivas del backoffice.
- **Horas extra y diferencias con el contrato**: el cálculo y la visualización de desviaciones respecto a horas contratadas no están incluidos en esta feature.
- **Descansos intermedios**: el ciclo de fichaje solo cubre la entrada y salida del servicio completo; no se gestionan pausas o descansos intermedios dentro de un servicio desde esta feature.
- **Corrección de fichajes por la trabajadora**: cualquier modificación de fichajes ya registrados queda fuera del alcance de esta app; se gestiona por backoffice.
- **Detección de GPS simulado**: fuera del alcance del MVP (declarado como fuera de alcance en el PRD).
- **Modo offline con sincronización**: fuera del alcance del MVP.
- **Seguimiento de tiempo para perfil Hogar (CUIDEO)**: el control horario aplica exclusivamente al perfil SAD (Felizvita).

---

## Asunciones Aplicadas

- **[A-001]**: El tipo de fichaje `worker|rest` que aparece en la documentación interna del backend hace referencia a una distinción de implementación técnica, no a un flujo diferenciado para la trabajadora en la app. Desde la perspectiva de la trabajadora, solo existe un tipo de fichaje (entrada y salida del servicio). Si el sistema requiere distinguir pausas de descanso, esta funcionalidad se añadiría en una fase futura.
- **[A-002]**: El warning de salida pendiente (CA-013) se activa en el momento en que la hora de fin programada del servicio ha pasado y no se ha registrado la salida. No se aplica ningún margen de gracia adicional; el aviso aparece de forma inmediata una vez superada la hora de fin programada.
