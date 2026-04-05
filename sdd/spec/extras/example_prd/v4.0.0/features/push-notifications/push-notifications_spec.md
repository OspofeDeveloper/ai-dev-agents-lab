# Spec: Push Notifications
> Versión: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-009 via prd-hogar-sad_discovery.md)
> Feature ID: F-009
> Spec monolítico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora | Profesional registrada en la plataforma, perfil Hogar (CUIDEO) o SAD (Felizvita) | Conceder permiso de notificaciones, recibir notificaciones con deeplink, consultar historial de notificaciones, marcar notificaciones como leídas |
| Sistema | Backend de la plataforma y tareas programadas | Enviar notificaciones push ante eventos relevantes, enviar recordatorios automáticos programados |

---

## Historias de Usuario

### HU-001: Registro de dispositivo para notificaciones
Como trabajadora,
quiero que la app solicite mi permiso de notificaciones y registre mi dispositivo en el sistema tras el primer inicio de sesión,
para que pueda recibir alertas en tiempo real sobre eventos importantes de mi trabajo.

### HU-002: Recepción de notificaciones con deeplink
Como trabajadora,
quiero recibir notificaciones push en cualquier estado de la app (primer plano, segundo plano o apagada) con acceso directo a la sección relevante,
para que pueda actuar sobre cada evento sin tener que navegar manualmente.

### HU-003: Historial de notificaciones
Como trabajadora,
quiero consultar el historial de notificaciones recibidas y marcarlas todas como leídas,
para que pueda revisar eventos que haya podido perder y mantener mi bandeja ordenada.

### HU-004: Actualización y baja del dispositivo
Como trabajadora,
quiero que el sistema mantenga actualizada la información de mi dispositivo durante toda la sesión y la elimine al cerrar sesión,
para que las notificaciones lleguen siempre al dispositivo correcto y no reciba alertas tras cerrar sesión.

### HU-005: Notificaciones automáticas de recordatorio
Como trabajadora,
quiero recibir notificaciones de recordatorio automáticas enviadas por el sistema (disponibilidad, caducidad de documentos, servicios próximos, fichaje pendiente, ausencias próximas),
para que no olvide acciones importantes sin necesidad de consultar la app activamente.

---

## Recorridos de Usuario

### Journey 1: Primer login y solicitud de permiso
Actor: Trabajadora | Objetivo: Registrar su dispositivo para recibir notificaciones

1. La trabajadora completa el primer inicio de sesión con éxito.
2. La app muestra el diálogo de solicitud de permiso de notificaciones del sistema operativo, antes de la pantalla de onboarding.
3. La trabajadora concede el permiso.
4. El sistema registra el identificador de dispositivo vinculado a la cuenta de la trabajadora.
5. La app continúa con el flujo de onboarding.

Estado de éxito: el dispositivo queda registrado y la trabajadora comenzará a recibir notificaciones push desde ese momento.

Flujos alternativos:
- Si la trabajadora deniega el permiso → la app continúa al onboarding sin registrar el dispositivo; la trabajadora no recibirá notificaciones push hasta que conceda el permiso desde los ajustes del sistema operativo.
- Si el registro del dispositivo falla → la app continúa al onboarding; el sistema reintenta el registro en el siguiente inicio de sesión.

---

### Journey 2: Recepción de notificación y navegación por deeplink
Actor: Trabajadora | Objetivo: Acceder directamente al contenido relevante desde una notificación

1. Se produce un evento relevante en la plataforma (nuevo mensaje, llamamiento disponible, cambio de estado, etc.).
2. El sistema envía una notificación push al dispositivo registrado de la trabajadora.
3. La trabajadora recibe la notificación:
   - Si la app está en primer plano: se muestra una alerta dentro de la propia app.
   - Si la app está en segundo plano o el dispositivo está apagado: aparece como notificación del sistema operativo.
4. La trabajadora toca la notificación.
5. La app se abre (o pasa a primer plano) y navega directamente a la pantalla correspondiente al evento.

Estado de éxito: la trabajadora llega a la pantalla exacta relacionada con el evento sin pasos intermedios adicionales.

Flujos alternativos:
- Si el contenido al que apunta el deeplink ya no existe (fue eliminado o cerrado) → la app navega al inicio (home) y muestra un mensaje informativo indicando que el contenido ya no está disponible.

---

### Journey 3: Consulta del historial de notificaciones
Actor: Trabajadora | Objetivo: Revisar notificaciones recibidas y limpiar la bandeja

1. La trabajadora accede a la sección de historial de notificaciones.
2. La app muestra el listado de notificaciones recibidas con título, cuerpo y fecha/hora, ordenadas de más reciente a más antigua.
3. La trabajadora puede tocar una notificación del historial para navegar a la sección correspondiente (mismo comportamiento que el deeplink directo).
4. La trabajadora selecciona "Marcar todas como leídas".
5. Todas las notificaciones del historial quedan marcadas como leídas y los badges numéricos del icono de notificaciones se resetean a cero.

Estado de éxito: el historial muestra todas las notificaciones sin notificaciones no leídas pendientes.

Flujos alternativos:
- Si el historial está vacío → se muestra un estado vacío con mensaje informativo.

---

### Journey 4: Actualización automática del registro de dispositivo
Actor: Sistema | Objetivo: Mantener el identificador de dispositivo actualizado

1. El identificador de dispositivo del sistema operativo se renueva (evento iniciado por el SO o la plataforma de mensajería).
2. La app detecta el cambio en segundo plano.
3. La app actualiza automáticamente el identificador de dispositivo registrado en el backend con el nuevo valor.

Estado de éxito: el dispositivo sigue recibiendo notificaciones tras la renovación del identificador, sin que la trabajadora tenga que hacer nada.

Flujos alternativos:
- Si la trabajadora cierra sesión → el registro del dispositivo es eliminado del backend; el dispositivo deja de recibir notificaciones push para esa cuenta.

---

## Resultados y Éxito

La feature de push notifications se considera completada cuando:

- La trabajadora recibe notificaciones push en todos los estados de la app (primer plano, segundo plano y con dispositivo apagado).
- La navegación por deeplink dirige a la trabajadora a la pantalla exacta del evento sin pasos intermedios.
- El historial de notificaciones está disponible y permite marcar todas como leídas.
- El dispositivo se registra automáticamente tras el primer login y se da de baja al cerrar sesión.
- Los recordatorios automáticos del sistema se reciben sin que la trabajadora tenga que iniciar ninguna acción.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Solicitud de permiso:**
- El permiso de notificaciones se solicita únicamente en el primer inicio de sesión, inmediatamente después de autenticarse y antes de mostrar el onboarding.
- Si la trabajadora ya concedió el permiso en sesiones anteriores, no se vuelve a solicitar.
- Si la trabajadora denegó el permiso previamente, la app no vuelve a solicitarlo automáticamente; puede indicar en la pantalla de perfil o ajustes que las notificaciones están desactivadas y ofrecer acceso directo a los ajustes del sistema operativo.

**Registro y ciclo de vida del dispositivo:**
- El registro del dispositivo se vincula siempre a la cuenta de la trabajadora autenticada, no al dispositivo en sí.
- Si la misma trabajadora inicia sesión en un dispositivo diferente, ambos dispositivos quedan registrados y reciben notificaciones.
- Al cerrar sesión, el registro del dispositivo actual se elimina del backend; el dispositivo deja de recibir notificaciones para esa cuenta.
- La actualización del identificador de dispositivo ocurre de forma automática y transparente para la trabajadora, sin ninguna acción requerida por su parte.

**Comportamiento de notificaciones según estado de la app:**
- Primer plano: la notificación se muestra como alerta dentro de la app (banner o diálogo interno); no se muestra como notificación del sistema operativo.
- Segundo plano o dispositivo apagado: la notificación se muestra como notificación nativa del sistema operativo con título, cuerpo e icono de la app.

**Deeplinks:**
- Cada tipo de notificación tiene un destino de navegación exacto y único (ver tabla de destinos de navegación).
- Al llegar por deeplink a una pantalla, el contexto de la notificación (identidad del elemento relacionado) debe estar disponible para abrir directamente ese elemento sin pasos de búsqueda manual.
- Si el elemento al que apunta el deeplink ya no existe o ya no es accesible para la trabajadora, la app navega al home y muestra un mensaje informativo.

**Historial de notificaciones:**
- El historial muestra todas las notificaciones recibidas por la trabajadora, ordenadas de más reciente a más antigua.
- Las notificaciones no leídas se distinguen visualmente de las leídas.
- La acción "Marcar todas como leídas" marca todas las notificaciones del historial y elimina cualquier badge o contador de no leídas en el icono de la sección.
- Al tocar una notificación en el historial, se navega al mismo destino que si se hubiera tocado la notificación en tiempo real.

**Recordatorios automáticos del sistema:**
- Los recordatorios automáticos son enviados por el backend mediante tareas programadas; la app no inicia ninguna solicitud para generarlos.
- Los recordatorios se reciben y muestran como cualquier otra notificación push: con deeplink y registro en el historial.
- Las preferencias de configuración de notificaciones (activar/desactivar tipos) quedan fuera del alcance del MVP.

### Destinos de navegación

| Tipo de notificación | Destino al tocar |
|----------------------|-----------------|
| Nuevo mensaje recibido | Hilo de conversación del mensaje recibido |
| Conversación cerrada por coordinación | Hilo de la conversación cerrada (modo solo lectura) |
| Llamamiento de servicio disponible | Pantalla de detalle del llamamiento |
| Cambio de estado de solicitud de oferta (Hogar) | Pantalla de detalle de la solicitud de oferta |
| Cambio de estado de solicitud de ausencia (SAD) | Pantalla de detalle de la solicitud de ausencia |
| Servicio comenzando pronto (ventana de fichaje abierta) | Pantalla de fichaje del servicio correspondiente |
| Servicio próximo mañana | Pantalla de detalle del servicio |
| Documento caducando pronto | Pantalla de documentos en el perfil |
| Actualización de incidencia | Pantalla de detalle de la incidencia actualizada |
| Nuevo comunicado en el tablón | Pantalla de detalle del comunicado |
| Nuevo servicio asignado (contratos indefinidos, SAD) | Pantalla de detalle del servicio asignado |
| Recordatorio de disponibilidad no actualizada | Pantalla del calendario de disponibilidad |
| Recordatorio de caducidad de documento | Pantalla de documentos en el perfil |
| Recordatorio de servicio próximo | Pantalla de detalle del servicio |
| Recordatorio de fichaje pendiente | Pantalla de fichaje del servicio correspondiente |
| Recordatorio de ausencia próxima | Pantalla de detalle de la solicitud de ausencia |
| Contenido no disponible (elemento eliminado o inaccesible) | Home de la app + mensaje informativo |

---

## Criterios de Aceptación

### CA-001: Solicitud de permiso en primer login ← HU-001
GIVEN una trabajadora acaba de autenticarse por primera vez en la app
WHEN el sistema detecta que no hay ningún registro de permiso de notificaciones para esta cuenta en este dispositivo
THEN la app muestra el diálogo de permiso de notificaciones del sistema operativo antes de navegar a la pantalla de onboarding

### CA-002: No se repite la solicitud en sesiones posteriores ← HU-001
GIVEN una trabajadora ya concedió o denegó el permiso de notificaciones en una sesión anterior
WHEN la trabajadora inicia sesión de nuevo
THEN la app no vuelve a mostrar el diálogo de solicitud de permiso

### CA-003: Registro del dispositivo tras conceder permiso ← HU-001
GIVEN una trabajadora acaba de conceder el permiso de notificaciones
WHEN la app obtiene el identificador de dispositivo de la plataforma de mensajería
THEN el dispositivo queda registrado en el backend vinculado a la cuenta de la trabajadora antes de que finalice el flujo de onboarding

### CA-004: Recepción de notificación en primer plano ← HU-002
GIVEN la trabajadora tiene la app abierta en primer plano
WHEN el sistema envía una notificación push a su dispositivo
THEN la app muestra una alerta o banner dentro de la propia interfaz con el título y el cuerpo de la notificación, sin mostrar una notificación del sistema operativo

### CA-005: Recepción de notificación en segundo plano ← HU-002
GIVEN la trabajadora tiene la app en segundo plano o el dispositivo está apagado
WHEN el sistema envía una notificación push a su dispositivo
THEN aparece una notificación nativa del sistema operativo con el título, el cuerpo y el icono de la app

### CA-006: Deeplink a pantalla específica ← HU-002
GIVEN la trabajadora recibe una notificación push con un tipo de evento reconocido
WHEN la trabajadora toca la notificación
THEN la app se abre (o pasa a primer plano) y navega directamente a la pantalla correspondiente indicada en la tabla de destinos de navegación, sin pasos intermedios adicionales

### CA-007: Deeplink a contenido no disponible ← HU-002
GIVEN la trabajadora recibe una notificación push que apunta a un elemento que ya no existe o al que ya no tiene acceso
WHEN la trabajadora toca la notificación
THEN la app navega al home y muestra un mensaje informativo indicando que el contenido ya no está disponible

### CA-008: Notificación incluye título, cuerpo e icono ← HU-002
GIVEN el sistema envía cualquier notificación push
WHEN la notificación llega al dispositivo (en segundo plano o apagado)
THEN la notificación muestra como mínimo: título descriptivo del evento, cuerpo con el detalle relevante e icono de la app correspondiente (CUIDEO o Felizvita)

### CA-009: Listado del historial de notificaciones ← HU-003
GIVEN la trabajadora accede a la sección de historial de notificaciones
WHEN la pantalla carga
THEN se muestra el listado de todas las notificaciones recibidas, ordenadas de más reciente a más antigua, con título, cuerpo y fecha/hora; las no leídas se distinguen visualmente de las leídas

### CA-010: Estado vacío del historial ← HU-003
GIVEN la trabajadora no ha recibido ninguna notificación
WHEN accede al historial de notificaciones
THEN se muestra un estado vacío con un mensaje informativo

### CA-011: Navegación desde el historial ← HU-003
GIVEN la trabajadora está en el historial de notificaciones y toca una notificación
WHEN la notificación tiene un tipo de evento reconocido
THEN la app navega al mismo destino que si la notificación hubiera sido tocada en tiempo real

### CA-012: Marcar todas las notificaciones como leídas ← HU-003
GIVEN la trabajadora tiene notificaciones no leídas en el historial
WHEN selecciona la acción "Marcar todas como leídas"
THEN todas las notificaciones del historial quedan marcadas como leídas y cualquier badge o contador de no leídas visible en la sección de notificaciones se resetea a cero

### CA-013: Baja del dispositivo al cerrar sesión ← HU-004
GIVEN la trabajadora está autenticada con su dispositivo registrado
WHEN la trabajadora cierra sesión
THEN el registro del dispositivo es eliminado del backend y el dispositivo deja de recibir notificaciones push para esa cuenta a partir de ese momento

### CA-014: Actualización automática del identificador de dispositivo ← HU-004
GIVEN el identificador de dispositivo de la plataforma de mensajería se renueva
WHEN la app detecta el nuevo identificador
THEN la app actualiza automáticamente el registro en el backend con el nuevo valor, sin acción requerida por parte de la trabajadora, y las notificaciones push continúan llegando sin interrupción

### CA-015: Recordatorio de disponibilidad no actualizada ← HU-005
GIVEN la trabajadora no ha actualizado su disponibilidad en 30 días
WHEN el sistema ejecuta la tarea programada de recordatorio de disponibilidad
THEN la trabajadora recibe una notificación push con deeplink al calendario de disponibilidad

### CA-016: Recordatorio de caducidad de documento ← HU-005
GIVEN el DNI, NIE u otro certificado de la trabajadora caduca en 30 días o menos
WHEN el sistema ejecuta la tarea programada de revisión de documentos
THEN la trabajadora recibe una notificación push con deeplink a la pantalla de documentos de su perfil

### CA-017: Recordatorio de servicio próximo ← HU-005
GIVEN la trabajadora tiene un servicio programado para el día siguiente
WHEN el sistema ejecuta la tarea programada de recordatorio de servicios
THEN la trabajadora recibe una notificación push con deeplink al detalle de ese servicio

### CA-018: Recordatorio de fichaje pendiente ← HU-005
GIVEN la trabajadora no ha fichado entrada N minutos después de la hora de inicio de un servicio (N configurable en el backend)
WHEN el sistema ejecuta la tarea programada de recordatorio de fichaje
THEN la trabajadora recibe una notificación push con deeplink a la pantalla de fichaje de ese servicio

### CA-019: Recordatorio de ausencia próxima ← HU-005
GIVEN la trabajadora tiene una ausencia aprobada que comienza al día siguiente
WHEN el sistema ejecuta la tarea programada de recordatorio de ausencias
THEN la trabajadora recibe una notificación push con deeplink al detalle de esa solicitud de ausencia

---

## Checklist de Validación

- [x] Actores identificados (Trabajadora y Sistema)
- [x] Flujos principales descritos paso a paso (4 journeys)
- [x] Estados de éxito definidos para cada journey
- [x] Edge cases documentados (permiso denegado, deeplink a contenido eliminado, historial vacío, fallo de registro)
- [x] Estados de error definidos (contenido no disponible → home + mensaje; fallo de registro → reintento en siguiente login)
- [x] Ambigüedades resueltas (solicitud de permiso solo en primer login, comportamiento por estado de app, tabla de deeplinks completa)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes (tabla completa en Instrucciones Inambiguas)

---

## Fuera de Alcance

- **Configuración de preferencias de notificaciones por tipo**: la trabajadora no puede activar ni desactivar tipos específicos de notificaciones en el MVP. Mejora futura declarada en el PRD.
- **Gestión de múltiples dispositivos desde la app**: la trabajadora no puede ver ni gestionar sus dispositivos registrados desde la app. La gestión de dispositivos es responsabilidad del backend/backoffice.
- **Notificaciones push entre trabajadoras**: esta feature cubre únicamente notificaciones del sistema hacia la trabajadora. Las comunicaciones entre trabajadoras y coordinación se gestionan en la feature `F-011: communication`.
- **Envío de notificaciones push desde la app**: la trabajadora no puede iniciar el envío de notificaciones push a otras personas desde esta feature.
- **Contenido de recordatorios automáticos más allá del MVP**: los recordatorios cubiertos son los cinco definidos en RF-11.2. Cualquier tipo adicional queda fuera de este spec.

---

## Asunciones Aplicadas

- **[A-001]**: El deeplink a "cambio de estado de solicitud de ausencia" se incluye en la tabla de destinos de navegación. El discovery (F-009) lo declara explícitamente aunque el listado de RF-11.1 del PRD no lo menciona de forma literal. Se asume que forma parte del alcance dado que el módulo de ausencias (F-010) existe en el PRD y el discovery lo incluye. Asunción conservadora aplicada.
- **[A-002]**: La solicitud de permiso de notificaciones no se vuelve a mostrar de forma automática si la trabajadora la denegó. La app puede indicar el estado de las notificaciones en ajustes o perfil, pero no muestra el diálogo del sistema operativo de nuevo (el SO no lo permite en iOS sin que el usuario acuda a ajustes manualmente). Comportamiento más conservador aplicado.
- **[A-003]**: El tipo de notificación "Nuevo servicio asignado (contratos indefinidos, SAD)" se incluye en la tabla de deeplinks aunque RF-11.1 no lo lista explícitamente. El discovery y RF-3.7 lo definen como parte del comportamiento del sistema. Asunción conservadora aplicada.
