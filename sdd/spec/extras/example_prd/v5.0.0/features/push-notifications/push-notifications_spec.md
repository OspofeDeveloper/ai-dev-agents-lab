# Spec: Notificaciones Push
> Version: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-012 via prd-hogar-sad_discovery.md)
> Feature ID: F-012
> Spec monolitico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora | Profesional de cuidados (perfil Hogar o SAD) que usa la aplicacion movil | Conceder permiso de notificaciones, recibir notificaciones push, consultar historial de notificaciones, navegar a pantalla relevante desde la notificacion |

---

## Historias de Usuario

### HU-001: Conceder permiso de notificaciones
Como trabajadora
quiero que la aplicacion me solicite permiso para enviarme notificaciones push despues de mi primer inicio de sesion
para que pueda recibir avisos oportunos de eventos importantes en mi dispositivo

### HU-002: Recibir notificaciones push
Como trabajadora
quiero recibir notificaciones push cuando ocurren eventos importantes (nuevos mensajes, llamamientos, cambios de estado, recordatorios)
para que me entere de forma inmediata sin tener que abrir la aplicacion constantemente

### HU-003: Navegar a contenido desde la notificacion
Como trabajadora
quiero que al tocar una notificacion la aplicacion me lleve directamente a la pantalla con la informacion relevante
para que pueda actuar rapidamente sin tener que buscar manualmente el contenido

> [INCOMPLETO] -- Pendiente de gap(s): [P-001]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-004: Consultar historial de notificaciones
Como trabajadora
quiero poder consultar un historial de las notificaciones que he recibido y marcarlas como leidas
para que no pierda informacion importante aunque no haya visto la notificacion en el momento

### HU-005: Recibir recordatorios automaticos del sistema
Como trabajadora
quiero recibir recordatorios automaticos sobre acciones pendientes o proximas (disponibilidad desactualizada, documentos por caducar, servicios proximos, fichaje pendiente, ausencia proxima)
para que no se me pasen plazos ni tareas importantes

---

## Recorridos de Usuario

### Journey 1: Conceder permiso de notificaciones tras primer login
Actor: Trabajadora | Objetivo: Habilitar la recepcion de notificaciones push en su dispositivo

1. La trabajadora completa su primer inicio de sesion en la aplicacion
2. La aplicacion muestra una solicitud de permiso de notificaciones push, explicando brevemente para que se usaran ("Recibiras avisos de nuevos mensajes, servicios, recordatorios y mas")
3. La trabajadora concede el permiso
4. La aplicacion registra el dispositivo para recibir notificaciones push
5. La aplicacion continua con el flujo de onboarding

Estado de exito: El dispositivo queda registrado para recibir notificaciones push y la trabajadora continua con el onboarding.

Flujos alternativos:
- Si la trabajadora deniega el permiso → la aplicacion continua con el onboarding normalmente. Se puede solicitar de nuevo desde la configuracion del dispositivo. La trabajadora no recibira notificaciones push hasta que conceda el permiso.
- Si la trabajadora ya ha concedido el permiso en una sesion anterior → no se vuelve a solicitar.

### Journey 2: Recibir y consultar una notificacion push
Actor: Trabajadora | Objetivo: Enterarse de un evento importante y actuar si es necesario

1. Ocurre un evento relevante en el sistema (nuevo mensaje, llamamiento disponible, cambio de estado, nuevo comunicado, etc.)
2. La trabajadora recibe una notificacion push en su dispositivo con titulo, cuerpo e icono
3. Si la aplicacion esta en primer plano: se muestra una alerta dentro de la aplicacion (in-app)
4. Si la aplicacion esta en segundo plano o cerrada: se muestra una notificacion del sistema operativo
5. La trabajadora toca la notificacion
6. La aplicacion se abre (si estaba cerrada) y navega a la pantalla relevante segun el tipo de notificacion

Estado de exito: La trabajadora accede directamente al contenido relevante desde la notificacion.

Flujos alternativos:
- Si la trabajadora no toca la notificacion → la notificacion queda registrada en el historial para consulta posterior.
- Si la trabajadora no tiene la aplicacion instalada o ha revocado permisos → no recibe la notificacion push (no hay fallback dentro del alcance de este feature).

### Journey 3: Consultar el historial de notificaciones
Actor: Trabajadora | Objetivo: Revisar notificaciones pasadas que pudo haber perdido

1. La trabajadora accede a la seccion de historial de notificaciones
2. La aplicacion muestra una lista cronologica inversa (mas recientes primero) de las notificaciones recibidas
3. Las notificaciones no leidas se distinguen visualmente de las leidas
4. La trabajadora puede tocar una notificacion para navegar a su contenido asociado
5. La trabajadora puede marcar todas las notificaciones como leidas

Estado de exito: La trabajadora revisa sus notificaciones pasadas y puede actuar sobre las que requieran atencion.

Flujos alternativos:
- Si no hay notificaciones en el historial → se muestra un estado vacio con mensaje informativo ("No tienes notificaciones").
- Las notificaciones con mas de 90 dias de antiguedad dejan de mostrarse en el historial.

### Journey 4: Recibir recordatorio automatico del sistema
Actor: Trabajadora | Objetivo: Ser avisada de acciones pendientes o proximos vencimientos

1. El sistema detecta una condicion que requiere recordatorio (disponibilidad no actualizada en 30 dias, documento por caducar en 30 dias, servicio programado para manana, fichaje no realizado tras inicio de servicio, ausencia programada para manana)
2. El sistema envia automaticamente una notificacion push a la trabajadora
3. La trabajadora recibe la notificacion y puede tocarla para navegar a la seccion relevante

Estado de exito: La trabajadora recibe el aviso a tiempo y puede tomar accion preventiva.

Flujos alternativos:
- Si la trabajadora tiene los permisos de notificaciones revocados → el recordatorio queda registrado en el historial pero no se recibe como push.

---

## Resultados y Exito

La feature se considera exitosa cuando:
1. La trabajadora recibe notificaciones push de forma fiable en los tres estados de la aplicacion (primer plano, segundo plano, cerrada)
2. La navegacion desde la notificacion lleva a la pantalla correcta sin pasos intermedios innecesarios
3. El historial de notificaciones permite a la trabajadora recuperar informacion que no vio en tiempo real
4. Los recordatorios automaticos llegan con la antelacion suficiente para que la trabajadora pueda actuar
5. La solicitud de permisos se realiza en un momento contextualmente apropiado (post-login, pre-onboarding) maximizando la tasa de aceptacion

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Momento de solicitud de permiso**: El permiso de notificaciones push se solicita una sola vez, despues del primer inicio de sesion exitoso y antes de las pantallas de onboarding/bienvenida. Si la trabajadora deniega, no se vuelve a solicitar desde la aplicacion (debera habilitarlo desde la configuracion del sistema operativo).

2. **Comportamiento segun estado de la aplicacion**:
   - **Primer plano**: la notificacion se muestra como alerta in-app (banner temporal en la parte superior) sin interrumpir la accion en curso. La trabajadora puede tocarla para navegar o descartarla.
   - **Segundo plano**: se muestra la notificacion estandar del sistema operativo con titulo, cuerpo e icono de la aplicacion.
   - **Aplicacion cerrada**: se muestra la notificacion estandar del sistema operativo. Al tocarla, la aplicacion se abre y navega a la pantalla correspondiente.

3. **Contenido de cada notificacion**: Toda notificacion incluye titulo descriptivo, cuerpo con el detalle relevante e icono de la aplicacion. El contenido incluye la informacion de contexto necesaria para que la aplicacion pueda navegar a la pantalla correcta al tocar la notificacion.

4. **Historial de notificaciones**:
   - Se muestran en orden cronologico inverso (mas recientes primero)
   - Las no leidas se distinguen visualmente de las leidas
   - Se retienen las notificaciones de los ultimos 90 dias; las mas antiguas dejan de mostrarse
   - Se soporta paginacion para historiales extensos
   - Existe una accion de "marcar todas como leidas"

5. **Tipos de notificaciones y eventos que las generan**:
   - **Nuevo mensaje recibido**: cuando se recibe un mensaje en una conversacion activa
   - **Conversacion cerrada por coordinacion**: cuando coordinacion cierra una conversacion
   - **Llamamiento de servicio disponible**: cuando hay un nuevo llamamiento pendiente de respuesta (solo SAD con contrato fijo discontinuo)
   - **Cambio de estado de solicitud de oferta**: cuando cambia el estado de una solicitud a una oferta (solo Hogar)
   - **Cambio de estado de solicitud de ausencia**: cuando se aprueba, rechaza o cancela una solicitud de ausencia
   - **Servicio comenzando pronto (ventana de fichaje abierta)**: cuando se abre la ventana de fichaje para un servicio proximo
   - **Servicio proximo manana**: recordatorio un dia antes del servicio programado
   - **Documento caducando pronto**: aviso 30 dias antes de la caducidad de DNI/certificados
   - **Actualizacion de incidencia**: cuando coordinacion responde o cambia el estado de una incidencia reportada
   - **Nuevo comunicado en el tablon**: cuando se publica un nuevo comunicado/anuncio
   - **Nuevo servicio asignado**: cuando se asigna un nuevo servicio a trabajadora con contrato indefinido
   - **Confirmacion de solicitud de ausencia enviada**: cuando se confirma la recepcion de una solicitud de ausencia

6. **Recordatorios automaticos del sistema**:
   - Disponibilidad no actualizada: se envia si la trabajadora no ha modificado su disponibilidad en los ultimos 30 dias
   - Caducidad de documento: se envia 30 dias antes de que caduque un documento (DNI, certificado)
   - Servicio programado manana: se envia 1 dia antes del servicio
   - Fichaje no realizado: se envia un tiempo configurable despues de la hora de inicio del servicio si la trabajadora no ha fichado entrada
   - Ausencia proxima: se envia 1 dia antes de que comience una ausencia programada

7. **Preferencias de notificaciones**: La configuracion individual de preferencias de notificaciones por la trabajadora queda fuera del alcance de esta version (mejora futura). Todas las trabajadoras que concedan permiso reciben todos los tipos de notificaciones.

### Destinos de navegacion

> **NOTA**: La tabla de destinos de navegacion esta incompleta debido al gap critico [P-001] sin resolver. Los destinos listados son los que se pueden inferir del PRD, pero requieren validacion del cliente.

| Tipo de notificacion | Destino al tocar (inferido del PRD) |
|----------------------|-------------------------------------|
| Nuevo mensaje recibido | Pantalla del hilo de conversacion con el remitente |
| Conversacion cerrada por coordinacion | Pantalla del historial de la conversacion cerrada |
| Llamamiento de servicio disponible | Pantalla de detalle del llamamiento pendiente |
| Cambio de estado de solicitud de oferta | Pantalla de detalle de la solicitud (Mis solicitudes) |
| Cambio de estado de solicitud de ausencia | Pantalla de detalle de la ausencia |
| Servicio comenzando pronto | Pantalla de fichaje del servicio |
| Servicio proximo manana | Pantalla de detalle del servicio |
| Documento caducando pronto | Pantalla de documentos del perfil |
| Actualizacion de incidencia | Pantalla de detalle de la incidencia |
| Nuevo comunicado en el tablon | Pantalla de detalle del comunicado |
| Nuevo servicio asignado | Pantalla de detalle del servicio asignado |
| Confirmacion de solicitud de ausencia | Pantalla de detalle de la ausencia |
| Recordatorio de disponibilidad | Pantalla del calendario de disponibilidad |
| Recordatorio de fichaje | Pantalla de fichaje del servicio |

---

## Criterios de Aceptacion

### CA-001: Solicitud de permiso en primer login ← HU-001
GIVEN la trabajadora ha completado su primer inicio de sesion exitoso
WHEN la aplicacion va a mostrar las pantallas de onboarding/bienvenida
THEN la aplicacion muestra primero una solicitud de permiso de notificaciones push con un texto explicativo del uso que se les dara

### CA-002: Permiso denegado no bloquea el flujo ← HU-001
GIVEN la trabajadora ve la solicitud de permiso de notificaciones push
WHEN deniega el permiso
THEN la aplicacion continua con el flujo de onboarding normalmente sin mostrar error ni volver a solicitar el permiso

### CA-003: Registro de dispositivo tras conceder permiso ← HU-001
GIVEN la trabajadora concede el permiso de notificaciones push
WHEN el permiso se otorga exitosamente
THEN el dispositivo queda registrado para recibir notificaciones push y la aplicacion continua con el onboarding

### CA-004: Notificacion en primer plano ← HU-002
GIVEN la trabajadora tiene la aplicacion abierta en primer plano
WHEN se recibe una notificacion push
THEN se muestra una alerta in-app (banner temporal en la parte superior de la pantalla) con titulo y cuerpo de la notificacion, sin interrumpir la accion en curso

### CA-005: Notificacion en segundo plano ← HU-002
GIVEN la trabajadora tiene la aplicacion en segundo plano
WHEN se recibe una notificacion push
THEN se muestra una notificacion del sistema operativo con titulo, cuerpo e icono de la aplicacion

### CA-006: Notificacion con aplicacion cerrada ← HU-002
GIVEN la trabajadora tiene la aplicacion cerrada
WHEN se recibe una notificacion push
THEN se muestra una notificacion del sistema operativo con titulo, cuerpo e icono de la aplicacion

### CA-007: Navegacion desde notificacion a pantalla relevante ← HU-003
GIVEN la trabajadora ha recibido una notificacion push
WHEN toca la notificacion (desde segundo plano, app cerrada o alerta in-app)
THEN la aplicacion abre (si estaba cerrada) y navega directamente a la pantalla relevante segun el tipo de notificacion, sin pasos intermedios

> [INCOMPLETO] -- Pendiente de gap(s): [P-001]. Los destinos exactos por tipo de notificacion requieren validacion del cliente. Los destinos inferidos del PRD estan documentados en la tabla de Destinos de Navegacion.

### CA-008: Historial de notificaciones en orden cronologico inverso ← HU-004
GIVEN la trabajadora tiene notificaciones recibidas en los ultimos 90 dias
WHEN accede a la seccion de historial de notificaciones
THEN se muestra una lista con las notificaciones ordenadas de la mas reciente a la mas antigua, distinguiendo visualmente las no leidas de las leidas

### CA-009: Marcar todas las notificaciones como leidas ← HU-004
GIVEN la trabajadora tiene notificaciones no leidas en el historial
WHEN selecciona la accion "marcar todas como leidas"
THEN todas las notificaciones del historial se marcan como leidas y se actualiza su apariencia visual

### CA-010: Historial vacio ← HU-004
GIVEN la trabajadora no tiene notificaciones en los ultimos 90 dias
WHEN accede al historial de notificaciones
THEN se muestra un estado vacio con el mensaje informativo "No tienes notificaciones"

### CA-011: Retencion de 90 dias en historial ← HU-004
GIVEN la trabajadora tiene notificaciones con mas de 90 dias de antiguedad
WHEN accede al historial de notificaciones
THEN solo se muestran las notificaciones de los ultimos 90 dias; las mas antiguas no aparecen

### CA-012: Recordatorio de disponibilidad no actualizada ← HU-005
GIVEN la trabajadora no ha modificado su disponibilidad en los ultimos 30 dias
WHEN el sistema ejecuta la verificacion periodica de recordatorios
THEN la trabajadora recibe una notificacion push recordandole actualizar su disponibilidad

### CA-013: Recordatorio de caducidad de documento ← HU-005
GIVEN la trabajadora tiene un documento (DNI, certificado) que caduca en 30 dias
WHEN el sistema ejecuta la verificacion periodica de recordatorios
THEN la trabajadora recibe una notificacion push avisandole de la proxima caducidad del documento

### CA-014: Recordatorio de servicio programado manana ← HU-005
GIVEN la trabajadora tiene un servicio programado para el dia siguiente
WHEN el sistema ejecuta la verificacion periodica de recordatorios (1 dia antes)
THEN la trabajadora recibe una notificacion push recordandole el servicio de manana

### CA-015: Recordatorio de fichaje no realizado ← HU-005
GIVEN la trabajadora no ha fichado entrada y ha transcurrido el tiempo configurado desde la hora de inicio del servicio
WHEN el sistema detecta la ausencia de fichaje
THEN la trabajadora recibe una notificacion push recordandole que fiche su entrada

### CA-016: Recordatorio de ausencia proxima ← HU-005
GIVEN la trabajadora tiene una ausencia aprobada que comienza al dia siguiente
WHEN el sistema ejecuta la verificacion periodica de recordatorios (1 dia antes)
THEN la trabajadora recibe una notificacion push avisandole del inicio de su ausencia programada

### CA-017: Notificacion de nuevo mensaje ← HU-002
GIVEN la trabajadora tiene una conversacion activa con coordinacion
WHEN coordinacion envia un nuevo mensaje en la conversacion
THEN la trabajadora recibe una notificacion push con titulo indicando que tiene un nuevo mensaje y cuerpo con un extracto del contenido

### CA-018: Notificacion de llamamiento disponible ← HU-002
GIVEN la trabajadora SAD tiene contrato fijo discontinuo
WHEN se publica un nuevo llamamiento de servicio disponible para ella
THEN la trabajadora recibe una notificacion push indicando que tiene un llamamiento pendiente de respuesta

### CA-019: Notificacion de nuevo comunicado ← HU-002
GIVEN la empresa publica un nuevo comunicado en el tablon
WHEN el comunicado se hace visible para las trabajadoras
THEN la trabajadora recibe una notificacion push informando del nuevo comunicado

### CA-020: Notificacion de cambio de estado de solicitud de oferta ← HU-002
GIVEN la trabajadora Hogar ha solicitado una oferta de trabajo
WHEN el estado de su solicitud cambia (Aceptada, Rechazada, Oferta cerrada)
THEN la trabajadora recibe una notificacion push informando del nuevo estado de su solicitud

### CA-021: Notificacion de cambio de estado de ausencia ← HU-002
GIVEN la trabajadora ha solicitado una ausencia
WHEN el estado de la solicitud cambia (Aprobada, Rechazada)
THEN la trabajadora recibe una notificacion push informando del nuevo estado de su solicitud de ausencia

### CA-022: Notificacion de nuevo servicio asignado ← HU-002
GIVEN la trabajadora SAD tiene contrato indefinido
WHEN se le asigna un nuevo servicio
THEN la trabajadora recibe una notificacion push informando de la nueva asignacion con el nombre del servicio

### CA-023: Notificacion de actualizacion de incidencia ← HU-002
GIVEN la trabajadora ha reportado una incidencia
WHEN coordinacion responde o cambia el estado de la incidencia
THEN la trabajadora recibe una notificacion push informando de la actualizacion

---

## Checklist de Validacion

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos para cada journey
- [x] Edge cases documentados (permiso denegado, historial vacio, app en diferentes estados, permisos revocados)
- [x] Estados de error definidos (sin permisos, sin notificaciones)
- [ ] Ambiguedades resueltas — **PENDIENTE**: [P-001] destinos de navegacion por tipo de notificacion requieren validacion del cliente
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [ ] Destinos de navegacion enumerados con sus variantes — **PARCIAL**: tabla inferida del PRD, pendiente de validacion [P-001]

---

## Fuera de Alcance

- **Configuracion individual de preferencias de notificaciones**: La posibilidad de que la trabajadora active/desactive tipos especificos de notificaciones queda fuera de esta version (mejora futura mencionada en RF-11.2 CA6). Todas las trabajadoras reciben todos los tipos.
- **Notificaciones por email o SMS**: Este feature cubre exclusivamente notificaciones push. No hay canal alternativo de notificacion.
- **Programacion personalizada de recordatorios**: Los intervalos de los recordatorios automaticos son fijos (30 dias para disponibilidad, 30 dias para caducidad de documentos, 1 dia para servicio/ausencia). La trabajadora no puede personalizar estos intervalos.
- **Modo offline / cola de notificaciones**: Si la trabajadora no tiene conexion, las notificaciones push se entregan cuando el sistema operativo lo permita. No hay mecanismo adicional de cola o reintento dentro de la aplicacion.
- **Notificaciones rich media**: Las notificaciones contienen solo texto (titulo + cuerpo) e icono. No incluyen imagenes, botones de accion ni contenido multimedia embebido.

---

## Items Pendientes

> Este spec tiene gaps **criticos** sin resolver. Las HUs afectadas estan marcadas `[INCOMPLETO]` y `/wf-prepare-plan` quedara bloqueado hasta que se resuelvan.
> Para resolverlos: edita este spec respondiendo los gaps, luego ejecuta `/wf-spec-validate <path>_spec.md`.

### [P-001][CRITICO] Destinos de navegacion (deeplinks) por tipo de notificacion
- **Afecta**: [HU-003, CA-007]
- **Pregunta**: Para cada tipo de notificacion, cual es la pantalla exacta de destino al tocar la notificacion? La tabla de destinos incluida en este spec contiene valores inferidos del PRD pero requiere validacion explicita del cliente.
- **Respuesta**: [CRITICO]_(pendiente)_

---

## Asunciones Aplicadas

- **[A-001]**: El historial de notificaciones retiene las notificaciones de los ultimos 90 dias con paginacion; las mas antiguas dejan de mostrarse. Justificacion: el PRD no especifica periodo de retencion (gap [P-016] del analysis). Se aplica 90 dias como valor conservador que equilibra utilidad e historico, sin sobrecargar al usuario con notificaciones muy antiguas.

- **[A-002]**: La notificacion de "servicio comenzando pronto" se envia cuando se abre la ventana de fichaje (configurable, por defecto 30 minutos antes del inicio del servicio, segun lo definido en F-005 time-tracking). El tiempo exacto es configurable desde backoffice. Justificacion: el PRD indica "N minutos antes" como configurable en servidor; el valor por defecto de 30 minutos proviene del CA de fichaje de F-005.

- **[A-003]**: El recordatorio de fichaje no realizado se envia un tiempo configurable despues de la hora de inicio del servicio. El valor exacto es configurable desde backoffice. Justificacion: el PRD indica "N minutos despues" como configurable, sin definir el valor por defecto.

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-04-05 | Generacion inicial via fast-track scoped desde F-012 del discovery |
