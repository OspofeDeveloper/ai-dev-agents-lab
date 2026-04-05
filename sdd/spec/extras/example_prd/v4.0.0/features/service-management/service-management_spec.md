# Spec: Service Management (Gestión de Servicios SAD)
> Versión: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-003 via prd-hogar-sad_discovery.md)
> Feature ID: F-003
> Spec monolítico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Cuidadora profesional contratada por Felizvita (SAD) que atiende servicios de asistencia a domicilio | Ver listado de servicios asignados; consultar detalle del servicio; gestionar notas del servicio; responder llamamientos (aceptar o rechazar con firma digital); ver historial de servicios y llamamientos; recibir y confirmar nuevos servicios asignados (contratos indefinidos) |
| Coordinadora | Gestora interna de backoffice que asigna servicios y revisa notas e incidencias | Configura la visibilidad de campos del servicio; gestiona los llamamientos desde backoffice; recibe notas e incidencias de las trabajadoras. *(La coordinadora no actúa directamente en la app móvil — es receptora de las acciones de la trabajadora.)* |

---

## Historias de Usuario

### HU-001: Ver listado de servicios asignados
Como trabajadora SAD
quiero ver todos mis servicios asignados agrupados por estado
para que pueda saber rápidamente qué servicios tengo activos, próximos y completados

### HU-002: Consultar el detalle de un servicio
Como trabajadora SAD
quiero ver la información completa de un servicio específico
para que pueda conocer los datos del cliente, la ubicación, el plan de cuidados y las tareas a realizar

### HU-003: Gestionar notas de servicio
Como trabajadora SAD
quiero registrar, editar y borrar notas sobre la evolución de un servicio
para que pueda comunicar a coordinación incidencias, tareas completadas y observaciones relevantes con adjuntos

### HU-004: Responder a un llamamiento [INCOMPLETO]
Como trabajadora SAD
quiero aceptar o rechazar un llamamiento firmando digitalmente
para que pueda confirmar o declinar mi disponibilidad para un turno disponible de forma vinculante

### HU-005: Consultar historial de servicios y llamamientos
Como trabajadora SAD
quiero ver el historial completo de mis servicios completados y el resultado de todos mis llamamientos
para que pueda hacer seguimiento de mi actividad pasada y conocer el estado final de cada llamamiento

### HU-006: Recibir y confirmar un nuevo servicio asignado (contratos indefinidos)
Como trabajadora SAD con contrato indefinido
quiero recibir notificación de un nuevo servicio asignado y registrar que lo he recibido
para que coordinación sepa que he sido informada del servicio y pueda comunicar cualquier impedimento

---

## Recorridos de Usuario

### Journey 1: Consultar servicios y ver detalle
Actor: Trabajadora SAD | Objetivo: Conocer sus servicios asignados y el detalle de uno concreto

1. La trabajadora accede a la sección "Mis Servicios" desde el menú de navegación o desde la home.
2. La app muestra el listado de servicios agrupado en tres secciones: Activos, Próximos, Completados.
3. Cada servicio en el listado muestra: nombre o código del cliente, dirección, fecha y hora, tipo de servicio (puntual o recurrente), con distinción visual entre ambos tipos.
4. Si no hay servicios en alguna sección, se muestra un estado vacío informativo para esa sección.
5. La trabajadora puede deslizar hacia abajo para actualizar el listado (pull-to-refresh).
6. La trabajadora pulsa un servicio para acceder a su detalle.
7. El detalle muestra: información básica (código, tipo, fechas, horario), datos del cliente (nombre, dirección, edad — solo los campos marcados como visibles por backoffice), plan de cuidados con listado descriptivo de tareas, documentación asociada, acceso a notas del servicio, acceso al historial de seguimiento de tiempo de ese servicio y botón CTA "Contacta con tu coordinador / empresa" con el teléfono de coordinación.
8. La dirección del cliente se muestra como texto interactivo que, al pulsarlo, abre la aplicación de mapas del dispositivo con esa dirección como destino.
9. Desde el detalle, la trabajadora puede acceder directamente a fichar entrada/salida o a reportar una incidencia del servicio.

Estado de éxito: La trabajadora ve la información completa del servicio y puede navegar a las subsecciones relacionadas sin ambigüedad.

Flujos alternativos:
- Si un campo del cliente está marcado como no visible desde backoffice → ese campo no se muestra en el detalle; no aparece en blanco ni como "sin datos", simplemente no existe en la pantalla.
- Si no hay documentación asociada al servicio → la sección de documentación no se muestra o muestra estado vacío.

---

### Journey 2: Responder a un llamamiento
Actor: Trabajadora SAD | Objetivo: Aceptar o rechazar formalmente un turno disponible

1. La trabajadora recibe una notificación push de nuevo llamamiento.
2. La home muestra el llamamiento pendiente de forma muy visible, con indicación de urgencia y cuenta atrás del tiempo disponible para responder; el botón CTA de la home lleva al detalle del llamamiento (no permite aceptar/rechazar desde la home).
3. La trabajadora pulsa el llamamiento y accede a su detalle completo (código de servicio, fecha/hora, ubicación, urgencia y demás campos del detalle).
4. Una vez dentro del detalle del llamamiento, la navegación hacia atrás queda bloqueada: la trabajadora no puede salir de la pantalla sin haber tomado una decisión (aceptar o rechazar).
5. Para **aceptar**: la trabajadora pulsa "Aceptar", se muestra un diálogo de confirmación donde debe firmar digitalmente con el dedo sobre un lienzo táctil; el copy es inequívoco e informa de las implicaciones de la aceptación.
6. Para **rechazar**: la trabajadora pulsa "Rechazar", debe seleccionar un motivo de rechazo obligatorio (No disponible, Demasiado lejos, Motivos personales, Otros — con campo de texto libre para "Otros") y firmar digitalmente; el copy distingue claramente esta acción de la aceptación.
7. Tras confirmar (aceptar o rechazar), la navegación queda desbloqueada y el llamamiento actualiza su estado en el listado.
8. Si el llamamiento caduca mientras la trabajadora lo está consultando, se muestra como desactivado/no disponible y las acciones quedan inhabilitadas.

Estado de éxito: El llamamiento queda registrado como aceptado o rechazado con la firma digital de la trabajadora; la trabajadora puede continuar navegando normalmente por la app.

Flujos alternativos:
- Si el llamamiento es aceptado por otra trabajadora antes de que la actual responda → se muestra como "desactivado" y la trabajadora queda liberada del bloqueo de navegación.
- Si el tiempo límite configurable expira sin respuesta → el llamamiento pasa a estado "caducado"; el comportamiento sobre si computa como rechazo por inacción es objeto del gap [P-001].

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001]. Responde en el spec y ejecuta `/wf-spec-delta resolve` para completar.

---

### Journey 3: Añadir una nota a un servicio
Actor: Trabajadora SAD | Objetivo: Comunicar a coordinación una observación del servicio

1. Desde el detalle de un servicio activo o próximo, la trabajadora accede a la sección de notas.
2. La app muestra la lista cronológica de notas existentes del servicio: autora, fecha/hora, categoría, texto y adjuntos.
3. La trabajadora pulsa "Añadir nota".
4. Se abre el formulario de nueva nota: campo de texto multilínea, selector de categoría (Evolución, Tareas, Incidencias, Otras) y opción de adjuntar archivos (fotos o documentos).
5. La trabajadora escribe el contenido, selecciona la categoría y, de forma opcional, adjunta uno o más archivos.
6. La trabajadora confirma el envío de la nota.
7. La nota aparece inmediatamente en la lista cronológica del servicio y es visible para coordinadoras.
8. La trabajadora puede editar o borrar sus propias notas; el borrado es suave (la nota no desaparece del registro de auditoría, deja de ser visible para la trabajadora).

Estado de éxito: La nota queda registrada en el servicio con su categoría y adjuntos, visible para coordinación de forma inmediata.

Flujos alternativos:
- Si la trabajadora intenta borrar una nota propia → se muestra diálogo de confirmación antes de proceder.
- Si el adjunto no puede procesarse → se informa del error y la nota puede enviarse igualmente sin el adjunto.

---

### Journey 4: Recibir un nuevo servicio asignado (contratos indefinidos)
Actor: Trabajadora SAD con contrato indefinido | Objetivo: Tomar conocimiento de un nuevo servicio asignado

1. La trabajadora recibe una notificación push "Nuevo servicio asignado" con enlace directo al detalle del servicio.
2. En la home, el nuevo servicio asignado se muestra de forma visible, con distinción visual respecto a los llamamientos pendientes.
3. La trabajadora abre el detalle del nuevo servicio.
4. Al abrir el detalle, la app registra automáticamente que la trabajadora ha recibido/visto la notificación (estado: recibido/acknowledeged).
5. El detalle muestra la información completa del servicio e indica si es de tipo puntual (con fecha de inicio y fin definidas) o recurrente (sin fecha de fin, con recurrencia semanal definida).
6. Si la trabajadora no puede atender el servicio, puede iniciar el flujo de reporte de incidencia directamente desde el detalle; se trata de una comunicación a coordinación, no de un rechazo formal.

Estado de éxito: La trabajadora ha visualizado el nuevo servicio y el sistema ha registrado la confirmación de recepción; coordinación sabe que la trabajadora ha sido informada.

Flujos alternativos:
- Si la trabajadora no abre el detalle → la confirmación de recepción no se registra hasta que abra el detalle del servicio.

---

### Journey 5: Consultar historial de servicios y llamamientos
Actor: Trabajadora SAD | Objetivo: Revisar actividad pasada

1. La trabajadora accede a la sección de historial desde el listado de servicios o desde la navegación principal.
2. La app muestra los servicios completados con fecha, nombre del cliente y total de horas trabajadas en cada servicio.
3. La trabajadora puede filtrar por rango de fechas.
4. La trabajadora puede pulsar un servicio completado para ver su detalle en modo solo lectura.
5. La sección también muestra el historial completo de llamamientos con su resultado final: aceptado, rechazado, caducado, desactivado. Los llamamientos pendientes de respuesta no se muestran en el historial (se muestran en la home y en el listado principal de llamamientos).

Estado de éxito: La trabajadora puede revisar su historial completo de actividad pasada, incluidos los resultados de todos sus llamamientos.

---

## Resultados y Éxito

Esta feature se considera completada cuando:

- La trabajadora SAD puede visualizar todos sus servicios asignados agrupados correctamente por estado (Activos, Próximos, Completados) y acceder al detalle de cada uno con la información filtrada según la configuración de visibilidad de backoffice.
- La dirección del cliente en el detalle del servicio abre la aplicación de mapas nativa del dispositivo sin necesidad de mapa embebido en la app.
- La trabajadora puede registrar, editar y borrar sus propias notas de servicio con adjuntos, con visibilidad inmediata para coordinación.
- Los llamamientos se responden exclusivamente desde su pantalla de detalle, con bloqueo de navegación hasta decisión, firma digital obligatoria en aceptación y rechazo, y cuenta atrás visual del tiempo disponible.
- Los llamamientos caducados o aceptados por otra trabajadora quedan desactivados y son visibles como tales en el listado.
- Las trabajadoras con contrato indefinido reciben notificación de nuevo servicio asignado, confirman su recepción al abrir el detalle y pueden reportar un impedimento vía incidencia.
- El historial de servicios completados y el historial completo de llamamientos (con resultado final) son accesibles con filtro por fecha.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Listado de servicios:**
- Los servicios se agrupan en tres secciones excluyentes: Activos (en curso en este momento o dentro de la ventana de fichaje), Próximos (con fecha de inicio posterior a hoy, fuera de ventana de fichaje), Completados. Cada servicio pertenece a una sola sección.
- La distinción visual entre servicios recurrentes (sin fecha de fin, con patrón semanal) y puntuales (con fecha de inicio y fin definidas) es obligatoria en el listado.
- Si una sección no tiene servicios, se muestra un estado vacío informativo específico de esa sección (no un estado vacío global).

**Detalle del servicio:**
- La visibilidad de los campos del cliente (nombre, dirección, edad, información de salud, medicación) es controlada individualmente desde backoffice. Solo se muestran los campos marcados como visibles; los no visibles no aparecen en la pantalla (ni como vacíos ni como censurados).
- La información de salud del cliente (medicación y datos persistentes de salud) requiere revisión RGPD; por defecto se trata como campo no visible hasta resolución legal.
- El plan de cuidados y el listado de tareas son de solo lectura para la trabajadora; la gestión es exclusiva de backoffice.
- El botón CTA "Contacta con tu coordinador / empresa" siempre se muestra en el detalle del servicio con el teléfono de coordinación.

**Notas de servicio:**
- Las categorías de nota son fijas: Evolución, Tareas, Incidencias, Otras. La trabajadora debe seleccionar una categoría al crear una nota.
- El borrado de una nota es suave: la nota deja de ser visible para la trabajadora pero permanece en el registro de auditoría del sistema.
- La trabajadora solo puede editar o borrar sus propias notas; no puede modificar notas de otras autoras.
- Las notas son visibles para coordinadoras inmediatamente tras el envío, sin necesidad de aprobación.

**Llamamientos:**
- El mismo llamamiento puede enviarse simultáneamente a varias trabajadoras; la primera en aceptar lo recibe y el sistema desactiva el llamamiento para el resto (gestión desde backoffice).
- El tiempo límite de exposición del llamamiento es configurable desde backoffice.
- Aceptar o rechazar un llamamiento requiere firma digital de la trabajadora en ambos casos.
- Una vez dentro del detalle del llamamiento, la navegación hacia atrás queda inhabilitada hasta que la trabajadora tome una decisión (aceptar o rechazar). No existe botón de retroceso activo.
- Los motivos de rechazo son: No disponible, Demasiado lejos, Motivos personales, Otros. Seleccionar "Otros" habilita un campo de texto libre obligatorio.
- El copy de aceptación y el copy de rechazo deben ser inequívocos y distinguibles entre sí visualmente y en contenido. Los textos oficiales deben ser solicitados a negocio/legal antes de implementar.
- Los llamamientos en home solo muestran los pendientes de respuesta. El historial completo (con resultado: aceptado, rechazado, caducado, desactivado) se muestra en la sección de historial.

**Nuevo servicio asignado (contratos indefinidos):**
- Este flujo aplica exclusivamente a trabajadoras con contrato indefinido; las de contrato fijo discontinuo reciben llamamientos, no asignaciones directas.
- La confirmación de recepción (acknowledged) se registra automáticamente cuando la trabajadora abre el detalle del servicio, sin acción adicional requerida.
- La opción de reportar un impedimento genera una incidencia (flujo del spec de Incident Reporting); no es un rechazo formal del servicio ni modifica el estado de asignación del mismo.
- La distinción visual entre el nuevo servicio asignado (indefinidos) y los llamamientos pendientes (fijo discontinuo) debe ser clara en la home.

### Destinos de navegación

| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Home (SAD) | Pulsar tarjeta de llamamiento pendiente | Detalle del llamamiento |
| Home (SAD) | Pulsar tarjeta de servicio activo o próximo | Detalle del servicio |
| Home (SAD) | Pulsar "Ver más servicios" | Listado completo de servicios (RF-3.1) |
| Home (SAD) | Pulsar nuevo servicio asignado (indefinidos) | Detalle del nuevo servicio |
| Listado de servicios | Pulsar un servicio | Detalle del servicio |
| Detalle del servicio | Pulsar dirección del cliente | Aplicación de mapas nativa del dispositivo con la dirección como destino |
| Detalle del servicio | Pulsar "Notas" | Lista de notas del servicio |
| Detalle del servicio | Pulsar acceso a historial de tiempo | Historial de seguimiento de tiempo filtrado a ese servicio (F-004) |
| Detalle del servicio | Pulsar "Fichar entrada/salida" | Pantalla de fichaje (F-004) |
| Detalle del servicio | Pulsar "Reportar incidencia" | Formulario de nueva incidencia pre-vinculada al servicio (F-005) |
| Detalle del servicio | Pulsar "Contacta con tu coordinador / empresa" | Llamada telefónica al número de coordinación (acción nativa del dispositivo) |
| Detalle del nuevo servicio (indefinidos) | Pulsar "Reportar impedimento" | Formulario de nueva incidencia (F-005) |
| Detalle del llamamiento | Sin decisión tomada (back inhabilitado) | La trabajadora permanece en el detalle hasta aceptar o rechazar |
| Detalle del llamamiento | Llamamiento desactivado o caducado | Botón de retroceso habilitado; estado del llamamiento visible como "desactivado/caducado" |
| Listado de servicios | Pulsar pestaña/sección "Historial" | Historial de servicios completados y llamamientos pasados |

---

## Criterios de Aceptación

### CA-001: Listado de servicios agrupado por estado ← HU-001
GIVEN la trabajadora SAD está autenticada y navega a "Mis Servicios"
WHEN la app carga el listado de servicios
THEN los servicios se muestran en tres secciones diferenciadas: "Activos", "Próximos" y "Completados"; cada servicio aparece en una sola sección

### CA-002: Información clave en cada tarjeta de servicio ← HU-001
GIVEN la trabajadora SAD está en el listado de servicios con al menos un servicio asignado
WHEN visualiza la tarjeta de un servicio
THEN la tarjeta muestra: nombre o código del cliente, dirección, fecha y hora del servicio, y tipo (puntual o recurrente) con distinción visual entre ambos

### CA-003: Estado vacío por sección ← HU-001
GIVEN la trabajadora SAD no tiene servicios en una de las tres secciones del listado
WHEN la app carga esa sección
THEN se muestra un estado vacío informativo específico para esa sección, sin ocultar las otras secciones

### CA-004: Pull-to-refresh en el listado ← HU-001
GIVEN la trabajadora está en el listado de servicios
WHEN desliza hacia abajo para refrescar
THEN la app actualiza el listado con los datos más recientes del servidor

### CA-005: Detalle del servicio — información básica y del cliente ← HU-002
GIVEN la trabajadora pulsa un servicio del listado
WHEN se abre el detalle del servicio
THEN se muestran: código del servicio, tipo, fechas, horario; y solo los campos del cliente marcados como visibles desde backoffice (nombre, dirección, edad). Los campos marcados como no visibles no aparecen en la pantalla.

### CA-006: Dirección del cliente como enlace a mapas ← HU-002
GIVEN la trabajadora está en el detalle de un servicio con dirección del cliente visible
WHEN pulsa sobre la dirección
THEN la app abre la aplicación de mapas nativa del dispositivo con esa dirección como destino; no se muestra ningún mapa embebido en la pantalla de detalle

### CA-007: Plan de cuidados y tareas de solo lectura ← HU-002
GIVEN la trabajadora está en el detalle de un servicio
WHEN visualiza la sección de plan de cuidados y tareas
THEN se muestra un listado descriptivo de tareas derivado del plan del servicio, sin casillas de verificación, y sin opción de edición para la trabajadora

### CA-008: CTA de contacto con coordinación ← HU-002
GIVEN la trabajadora está en el detalle de cualquier servicio
WHEN visualiza la pantalla
THEN el botón "Contacta con tu coordinador / empresa" con el teléfono de coordinación es visible de forma prominente; al pulsarlo, inicia una llamada al número de coordinación

### CA-009: Lista cronológica de notas del servicio ← HU-003
GIVEN la trabajadora accede a la sección de notas de un servicio
WHEN se carga la lista
THEN las notas se muestran en orden cronológico, mostrando autora, fecha y hora, categoría, contenido de texto y adjuntos de cada nota

### CA-010: Añadir nota con categoría y adjuntos ← HU-003
GIVEN la trabajadora está en la sección de notas de un servicio
WHEN pulsa "Añadir nota", completa el texto, selecciona una categoría y, opcionalmente, adjunta archivos y confirma
THEN la nota aparece inmediatamente en la lista cronológica del servicio, visible también para coordinación desde su sistema

### CA-011: Editar nota propia ← HU-003
GIVEN la trabajadora tiene al menos una nota propia registrada en un servicio
WHEN selecciona la opción de editar sobre su nota y modifica el contenido
THEN la nota se actualiza con el nuevo contenido; la fecha de modificación queda registrada

### CA-012: Borrar nota propia (borrado suave) ← HU-003
GIVEN la trabajadora tiene al menos una nota propia registrada en un servicio
WHEN selecciona borrar su nota y confirma en el diálogo de confirmación
THEN la nota deja de ser visible para la trabajadora en la lista, pero el registro permanece en el sistema para auditoría; la nota no puede ser recuperada desde la app

### CA-013: Llamamiento pendiente en home con cuenta atrás ← HU-004
GIVEN existe un llamamiento pendiente de respuesta asignado a la trabajadora
WHEN la trabajadora abre la home
THEN el llamamiento se muestra de forma muy visible con indicación de urgencia y cuenta atrás del tiempo disponible para responder

### CA-014: Acceso al detalle del llamamiento desde home ← HU-004
GIVEN hay un llamamiento pendiente visible en la home
WHEN la trabajadora pulsa el CTA del llamamiento
THEN navega al detalle completo del llamamiento (no puede aceptar ni rechazar desde la home)

### CA-015: Bloqueo de navegación en detalle del llamamiento ← HU-004
GIVEN la trabajadora está en el detalle de un llamamiento pendiente
WHEN intenta pulsar el botón de retroceso o salir de la pantalla sin haber tomado una decisión
THEN la navegación hacia atrás está bloqueada; la trabajadora permanece en el detalle del llamamiento hasta aceptar o rechazar

### CA-016: Aceptar llamamiento con firma digital ← HU-004
GIVEN la trabajadora está en el detalle de un llamamiento pendiente
WHEN pulsa "Aceptar" y firma digitalmente en el lienzo táctil y confirma
THEN el llamamiento queda registrado como aceptado con la firma de la trabajadora; la navegación se desbloquea; el estado del llamamiento se actualiza en el listado

### CA-017: Rechazar llamamiento con motivo y firma digital ← HU-004
GIVEN la trabajadora está en el detalle de un llamamiento pendiente
WHEN pulsa "Rechazar", selecciona un motivo (o escribe el texto si seleccionó "Otros"), firma digitalmente y confirma
THEN el llamamiento queda registrado como rechazado con el motivo y la firma; la navegación se desbloquea; el estado del llamamiento se actualiza en el listado

### CA-018: Llamamiento caducado o desactivado ← HU-004 [INCOMPLETO]
GIVEN un llamamiento ha superado el tiempo límite sin respuesta de la trabajadora, o ha sido aceptado por otra trabajadora
WHEN la trabajadora visualiza ese llamamiento en el listado o intenta acceder a su detalle
THEN el llamamiento se muestra como "caducado" o "desactivado" respectivamente; las acciones de aceptar/rechazar están inhabilitadas; la navegación no está bloqueada

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001]. La consecuencia de la caducidad sin respuesta (si computa como rechazo por inacción) no puede especificarse hasta resolución legal. Responde en este spec y ejecuta `/wf-spec-delta resolve` para completar.

### CA-019: Historial completo de servicios completados ← HU-005
GIVEN la trabajadora accede a la sección de historial
WHEN se carga el historial
THEN se muestran los servicios completados con: fecha, nombre del cliente y total de horas trabajadas en ese servicio; la trabajadora puede filtrar por rango de fechas

### CA-020: Detalle de servicio archivado en modo lectura ← HU-005
GIVEN la trabajadora pulsa un servicio en el historial
WHEN se abre el detalle
THEN se muestra la información completa del servicio en modo solo lectura, sin posibilidad de añadir notas ni fichar

### CA-021: Historial completo de llamamientos con resultado final ← HU-005
GIVEN la trabajadora accede a la sección de historial
WHEN visualiza los llamamientos pasados
THEN se muestran todos los llamamientos con su resultado final: aceptado, rechazado, caducado, desactivado. Los llamamientos pendientes de respuesta no aparecen en esta sección.

### CA-022: Notificación de nuevo servicio asignado (contratos indefinidos) ← HU-006
GIVEN la trabajadora SAD tiene contrato indefinido y se le asigna un nuevo servicio
WHEN el sistema procesa la asignación
THEN la trabajadora recibe una notificación push que incluye información del nuevo servicio y enlace directo a su detalle

### CA-023: Visualización diferenciada del nuevo servicio en home ← HU-006
GIVEN la trabajadora tiene un nuevo servicio asignado aún no confirmado
WHEN visualiza la home
THEN el nuevo servicio asignado se muestra con distinción visual respecto a los llamamientos pendientes; no se confunden visualmente

### CA-024: Confirmación automática de recepción ← HU-006
GIVEN la trabajadora pulsa el nuevo servicio asignado y se abre el detalle
WHEN la pantalla de detalle se carga completamente
THEN la app registra automáticamente que la trabajadora ha recibido y visto la notificación (estado: acknowledged), sin requerir acción adicional de la trabajadora

### CA-025: Distinción puntual vs recurrente en nuevo servicio ← HU-006
GIVEN la trabajadora está en el detalle de un nuevo servicio asignado
WHEN visualiza la información del servicio
THEN se indica claramente si el servicio es puntual (con fecha de inicio y fin definidas) o recurrente (sin fecha de fin, con patrón semanal definido)

### CA-026: Reportar impedimento desde nuevo servicio asignado ← HU-006
GIVEN la trabajadora está en el detalle de un nuevo servicio asignado (contrato indefinido) y no puede atenderlo
WHEN pulsa "Reportar impedimento"
THEN se abre el formulario de nueva incidencia (F-005) pre-vinculado a ese servicio, sin que esto modifique el estado de asignación del servicio ni constituya un rechazo formal

---

## Checklist de Validación

- [x] Actores identificados (Trabajadora SAD, Coordinadora como receptora)
- [x] Flujos principales descritos paso a paso (5 journeys completos)
- [x] Estados de éxito definidos para cada journey
- [x] Edge cases documentados (campos no visibles RGPD, llamamiento desactivado por otra trabajadora, servicio sin notas, etc.)
- [x] Estados de error definidos (adjunto no procesable, llamamiento caducado)
- [ ] Ambigüedades resueltas — PENDIENTE: consecuencia legal de caducidad de llamamiento sin respuesta [P-001]
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes

---

## Fuera de Alcance

- **Seguimiento PIA (RF-3.6)**: eliminado del PRD y excluido de este spec.
- **Creación o modificación de servicios por la trabajadora**: la gestión del ciclo de vida de los servicios (creación, asignación, modificación, cancelación) es exclusiva de backoffice. La trabajadora solo consulta y actúa sobre los servicios ya asignados.
- **Autenticación biométrica y 2FA**: excluidos del MVP; aplica al spec de Auth & Onboarding (F-001).
- **Modo offline**: los datos de servicios requieren conexión. El comportamiento en ausencia de red no se especifica en esta versión del MVP.
- **Fichaje de entrada/salida**: el acceso a fichar se ofrece desde el detalle del servicio como punto de entrada, pero la lógica de fichaje pertenece al spec de Control Horario (F-004).
- **Reporte de incidencias**: el acceso a reportar incidencia se ofrece desde el detalle del servicio como punto de entrada, pero la lógica de incidencias pertenece al spec de Incident Reporting (F-005).
- **Firma digital como entidad de perfil**: el lienzo de firma digital y su gestión pertenecen al spec de Profile Management (F-008). Este spec solo referencia la firma digital como mecanismo de confirmación en llamamientos.
- **Notificaciones push de llamamientos y nuevos servicios**: la entrega de notificaciones push pertenece al spec de Push Notifications (F-009). Este spec describe el comportamiento de la app al recibir esas notificaciones, no su envío.
- **Gestión de contratos**: el estado del contrato (indefinido vs puntual) es un dato de perfil gestionado en F-008; este spec lo consume como precondición para determinar el flujo aplicable.

---

## Items Pendientes

> ⚠ Este spec tiene gaps **críticos** sin resolver. Las HUs afectadas están marcadas `[INCOMPLETO]` y `/wf-prepare-plan` quedará bloqueado hasta que se resuelvan.
> Para resolverlos: edita este spec respondiendo los gaps, luego ejecuta `/wf-spec-validate features/service-management/service-management_spec.md`.

### [P-001][CRÍTICO] Consecuencia legal de la caducidad de un llamamiento sin respuesta
- **Afecta**: HU-004, CA-018
- **Pregunta**: ¿La caducidad de un llamamiento sin respuesta de la trabajadora computa como rechazo por inacción (con las implicaciones laborales/legales correspondientes) o simplemente caduca sin consecuencias registradas para la trabajadora? ¿Debe mostrarse algún aviso específico a la trabajadora cuando su llamamiento caduca sin respuesta?
- **Respuesta**: [CRÍTICO]_(pendiente)_

---

## Asunciones Aplicadas

- **[A-001]**: La información de salud del cliente (medicación y datos persistentes de salud) se trata como campo no visible por defecto en el detalle del servicio, hasta que se resuelva la revisión RGPD mencionada en RF-3.2 CA2. Esto es la opción más conservadora desde el punto de vista de privacidad.
- **[A-002]**: La trabajadora puede editar sus propias notas, además de crearlas y borrarlas. El PRD incluye el endpoint de edición (PUT) y este comportamiento es coherente con un CRUD estándar de notas. Se asume que la edición es posible sin restricción temporal (si hay restricciones, deberán especificarse en una revisión del PRD).
- **[A-003]**: Los servicios "Activos" en el listado corresponden a servicios cuya ventana de fichaje está abierta (inicio del servicio ≤ ahora ≤ fin del servicio, o dentro del margen de 30 minutos previos al inicio). Los servicios completados (con salida fichada o cuya fecha de fin ha pasado) van a "Completados". Los servicios con fecha de inicio futura fuera de la ventana de fichaje van a "Próximos".
