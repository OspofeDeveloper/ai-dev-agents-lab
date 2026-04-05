# Spec: Job Offers (Ofertas de Trabajo)
> Versión: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-006 via prd-hogar-sad_discovery.md)
> Feature ID: F-006
> Spec monolítico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado domiciliario con contrato fijo discontinuo registrada en la aplicación CUIDEO | Navegar ofertas de trabajo disponibles, aplicar a ofertas, ver y gestionar sus solicitudes, retirar solicitudes pendientes |

---

## Historias de Usuario

### HU-001: Explorar ofertas disponibles
Como trabajadora Hogar
quiero ver el listado de ofertas de trabajo disponibles con sus detalles principales y filtrarlas por criterios relevantes
para que pueda identificar rápidamente las oportunidades que mejor se adaptan a mi disponibilidad y zona geográfica

### HU-002: Solicitar una oferta de trabajo
Como trabajadora Hogar
quiero poder aplicar a una oferta de trabajo con una confirmación explícita antes de enviarla
para que pueda expresar mi interés en una oportunidad laboral de forma deliberada, sabiendo que la coordinación la revisará

### HU-003: Consultar y gestionar mis solicitudes
Como trabajadora Hogar
quiero ver todas mis solicitudes enviadas con su estado actual y poder retirar las que aún están pendientes
para que pueda hacer seguimiento de mis candidaturas y mantener actualizada mi situación con la coordinación

---

## Recorridos de Usuario

### Journey 1: Explorar y filtrar ofertas disponibles
Actor: Trabajadora Hogar | Objetivo: Encontrar ofertas ajustadas a su zona y horario

1. La trabajadora accede a la sección de Ofertas desde el menú principal.
2. Visualiza el listado de ofertas disponibles, cada una con: título del trabajo, ubicación (código postal y ciudad), horario, tarifa horaria e insignia "Nuevo" si fue publicada en las últimas 48 horas.
3. Aplica filtros: por zona/código postal, por franja horaria (mañana, tarde, noche, madrugada, 24h) o por rango de fecha de inicio.
4. Ordena las ofertas por: más recientes, ubicación más cercana o tarifa más alta.
5. Si no hay ofertas coincidentes con los filtros, se muestra un estado vacío.
6. Toca una oferta para acceder al detalle completo.

Estado de éxito: La trabajadora ve la información relevante de cada oferta y puede acotar el listado según sus criterios antes de decidir si aplica.

Flujos alternativos:
- Si no hay ofertas disponibles (sin filtros activos) → se muestra estado vacío con mensaje informativo.

---

### Journey 2: Aplicar a una oferta
Actor: Trabajadora Hogar | Objetivo: Expresar interés en una oferta y enviar su solicitud

1. Desde el listado de ofertas o desde el detalle de una oferta, la trabajadora pulsa el botón "Aplicar".
2. Se muestra un diálogo de confirmación con un resumen de la oferta (título, ubicación, horario, tarifa).
3. La trabajadora confirma la solicitud con un solo toque.
4. El sistema envía la solicitud, incluyendo automáticamente los datos del perfil de la trabajadora, y muestra un mensaje de confirmación in-app.
5. La solicitud aparece en "Mis solicitudes" con estado "Pendiente".

Estado de éxito: La solicitud queda registrada y visible en "Mis solicitudes". La coordinación la recibe para revisión.

Flujos alternativos:
- Si la trabajadora ya ha aplicado a esa oferta → el botón "Aplicar" está deshabilitado y se indica que ya hay una solicitud activa para esa oferta.
- Si el perfil de la trabajadora está incompleto → antes de mostrar el diálogo de confirmación, se muestra una advertencia indicando los campos obligatorios del perfil que faltan, con acceso directo para completarlos. La trabajadora puede completar el perfil y retomar el proceso.
- Si la trabajadora cancela el diálogo de confirmación → no se envía ninguna solicitud y se regresa a la pantalla anterior.

---

### Journey 3: Consultar el estado de mis solicitudes
Actor: Trabajadora Hogar | Objetivo: Conocer en qué estado están sus candidaturas

1. La trabajadora accede a "Mis solicitudes" desde el menú principal o desde la sección de Ofertas.
2. Visualiza la lista de solicitudes en orden cronológico inverso, mostrando para cada una: título de la oferta, ubicación, fecha de solicitud y estado actual.
3. Las solicitudes aceptadas tienen distinción visual respecto al resto.
4. La trabajadora puede filtrar por estado (Pendiente, En revisión, Aceptada, Rechazada, Oferta cerrada).
5. Toca una solicitud para ver los detalles completos de la oferta asociada.

Estado de éxito: La trabajadora tiene visibilidad completa del estado de todas sus solicitudes activas e históricas.

Flujos alternativos:
- Si no hay solicitudes enviadas aún → se muestra estado vacío con acceso directo a explorar ofertas.

---

### Journey 4: Retirar una solicitud pendiente
Actor: Trabajadora Hogar | Objetivo: Cancelar una solicitud que ya no desea mantener

1. Desde "Mis solicitudes", la trabajadora localiza una solicitud en estado "Pendiente".
2. Accede al detalle de esa solicitud.
3. Selecciona la opción de retirar la solicitud.
4. Se muestra una confirmación antes de proceder.
5. Tras confirmar, la solicitud desaparece del listado activo o queda marcada como "Retirada".

Estado de éxito: La solicitud queda cancelada y la coordinación ya no la considera activa.

Flujos alternativos:
- Solo las solicitudes en estado "Pendiente" pueden retirarse. Para solicitudes en cualquier otro estado, la opción de retirar no está disponible.

---

## Resultados y Éxito

La feature de Ofertas de Trabajo queda completada cuando:
- La trabajadora Hogar puede acceder a un listado actualizado de ofertas disponibles, aplicar filtros y ordenación, y consultar el detalle de cualquier oferta.
- La trabajadora puede aplicar a una oferta con confirmación explícita, sin posibilidad de duplicar solicitudes, y con protección ante perfil incompleto.
- La trabajadora puede consultar en cualquier momento el estado de todas sus solicitudes y filtrarlas por estado.
- La trabajadora puede retirar solicitudes que aún están en estado pendiente.
- Los cambios de estado en las solicitudes generan una notificación push hacia la trabajadora (coordinada con F-009: push-notifications).

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Acceso**: La sección de Ofertas es exclusiva del perfil Hogar (CUIDEO). Las trabajadoras del perfil SAD no tienen acceso a esta sección.

**Insignia "Nuevo"**: Una oferta muestra la insignia "Nuevo" si fue publicada en las últimas 48 horas en relación a la fecha/hora actual de la trabajadora.

**Prevención de duplicados**: Una trabajadora no puede tener más de una solicitud activa (Pendiente o En revisión) para la misma oferta. Si ya existe una solicitud activa, el botón "Aplicar" se muestra deshabilitado con indicación de solicitud existente.

**Datos de la solicitud**: Al aplicar a una oferta, la solicitud incluye automáticamente los datos del perfil actual de la trabajadora. No se le pide que introduzca información adicional en el flujo de solicitud.

**Perfil incompleto**: Si la trabajadora intenta aplicar a una oferta y su perfil no cumple los campos obligatorios definidos por el sistema, se muestra una advertencia con los campos pendientes y un acceso directo para completarlos. La trabajadora no queda bloqueada para navegar el resto de la app, pero no puede enviar la solicitud hasta completar los campos obligatorios.

**Estados de solicitud**: Los estados posibles de una solicitud son: Pendiente, En revisión, Aceptada, Rechazada, Oferta cerrada. Las transiciones de estado son gestionadas exclusivamente por la coordinación desde el back-office; la trabajadora no puede cambiarlos salvo la acción de retirar una solicitud Pendiente.

**Retirar solicitud**: Solo se puede retirar una solicitud cuando está en estado "Pendiente". Una vez que pasa a "En revisión" o cualquier estado posterior, la opción de retirar deja de estar disponible.

**Distinción visual de Aceptadas**: Las solicitudes en estado "Aceptada" se destacan visualmente en el listado para facilitar su identificación.

**Notificación de cambio de estado**: Cuando el estado de una solicitud cambia (cualquier transición), la trabajadora recibe una notificación push. La gestión del envío de notificaciones es responsabilidad de F-009: push-notifications.

**Confirmación al aplicar**: Tras enviar correctamente una solicitud, se muestra un mensaje de confirmación in-app. No se genera una notificación push por el mero acto de aplicar — la notificación push es para cambios de estado posteriores.

**Ordenación**: El sistema soporta tres criterios de ordenación del listado: más recientes (por defecto), ubicación más cercana (basada en la dirección de domicilio de la trabajadora) y tarifa más alta.

### Destinos de navegación

| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Menú principal | Pulsar "Ofertas" | Listado de ofertas disponibles |
| Listado de ofertas | Pulsar tarjeta de oferta | Detalle de la oferta |
| Detalle de oferta | Pulsar "Aplicar" (perfil completo, sin solicitud activa) | Diálogo de confirmación de solicitud |
| Detalle de oferta | Pulsar "Aplicar" (perfil incompleto) | Advertencia de campos obligatorios pendientes, con acceso directo al perfil |
| Diálogo de confirmación | Confirmar solicitud | Mensaje de éxito in-app; regreso a detalle de oferta con botón "Aplicar" deshabilitado |
| Diálogo de confirmación | Cancelar | Regreso a detalle de oferta sin enviar solicitud |
| Menú principal o sección de Ofertas | Pulsar "Mis solicitudes" | Listado de mis solicitudes |
| Listado de mis solicitudes | Pulsar solicitud | Detalle de la oferta asociada |
| Detalle de solicitud Pendiente | Pulsar "Retirar solicitud" | Diálogo de confirmación de retirada |
| Diálogo de confirmación de retirada | Confirmar | Solicitud retirada; regreso al listado de mis solicitudes |
| Diálogo de confirmación de retirada | Cancelar | Regreso al detalle de solicitud sin cambios |
| Advertencia de perfil incompleto | Pulsar "Completar perfil" | Sección de perfil (F-008: profile-management), con retorno a la oferta tras completar |
| Estado vacío (sin ofertas) | Ver ofertas | Estado vacío con mensaje informativo |
| Estado vacío (sin solicitudes) | Ver solicitudes | Estado vacío con enlace a explorar ofertas |

---

## Criterios de Aceptación

### CA-001: Listado de ofertas en formato tarjeta ← HU-001
GIVEN la trabajadora Hogar está autenticada y accede a la sección de Ofertas
WHEN el sistema carga el listado de ofertas disponibles
THEN se muestra cada oferta en formato tarjeta con: título del trabajo, ubicación (código postal/ciudad), horario, tarifa horaria

### CA-002: Insignia "Nuevo" en ofertas recientes ← HU-001
GIVEN una oferta fue publicada hace menos de 48 horas
WHEN la trabajadora Hogar visualiza esa oferta en el listado
THEN la tarjeta de la oferta muestra la insignia "Nuevo"

### CA-003: Estado vacío cuando no hay ofertas coincidentes ← HU-001
GIVEN la trabajadora Hogar aplica filtros que no coinciden con ninguna oferta disponible
WHEN el sistema procesa los filtros
THEN se muestra un estado vacío con mensaje informativo (sin tarjetas de oferta)

### CA-004: Filtrar por zona/código postal ← HU-001
GIVEN la trabajadora Hogar está en el listado de ofertas
WHEN aplica el filtro de zona introduciendo un código postal o ciudad
THEN el listado muestra únicamente las ofertas cuya ubicación coincide con el criterio introducido

### CA-005: Filtrar por franja horaria ← HU-001
GIVEN la trabajadora Hogar está en el listado de ofertas
WHEN selecciona uno o más filtros de franja horaria (mañana, tarde, noche, madrugada, 24h)
THEN el listado muestra únicamente las ofertas cuyo horario corresponde a la franja seleccionada

### CA-006: Filtrar por rango de fecha de inicio ← HU-001
GIVEN la trabajadora Hogar está en el listado de ofertas
WHEN define un rango de fecha de inicio en el filtro correspondiente
THEN el listado muestra únicamente las ofertas cuya fecha de inicio está dentro del rango seleccionado

### CA-007: Ordenar el listado de ofertas ← HU-001
GIVEN la trabajadora Hogar está en el listado de ofertas
WHEN selecciona un criterio de ordenación (más recientes, ubicación más cercana, tarifa más alta)
THEN el listado se reordena según el criterio seleccionado; la ordenación por defecto es "más recientes"

### CA-008: Acceder al detalle de una oferta ← HU-001
GIVEN la trabajadora Hogar está en el listado de ofertas
WHEN toca cualquier tarjeta del listado
THEN se navega a la pantalla de detalle completo de esa oferta

### CA-009: Botón "Aplicar" visible en tarjeta y en detalle ← HU-002
GIVEN la trabajadora Hogar visualiza el listado de ofertas o el detalle de una oferta específica
WHEN la oferta está disponible y la trabajadora no tiene ya una solicitud activa para ella
THEN el botón "Aplicar" está visible y habilitado

### CA-010: Diálogo de confirmación al aplicar ← HU-002
GIVEN la trabajadora Hogar pulsa "Aplicar" en una oferta (sin solicitud activa previa, perfil completo)
WHEN el sistema procesa la acción
THEN se muestra un diálogo de confirmación con el resumen de la oferta (título, ubicación, horario, tarifa)

### CA-011: Envío de solicitud con un solo toque ← HU-002
GIVEN se muestra el diálogo de confirmación de solicitud
WHEN la trabajadora confirma con un solo toque
THEN el sistema envía la solicitud incluyendo automáticamente los datos del perfil de la trabajadora, muestra un mensaje de éxito in-app y deshabilita el botón "Aplicar" para esa oferta

### CA-012: Prevención de solicitudes duplicadas ← HU-002
GIVEN la trabajadora Hogar ya tiene una solicitud activa (Pendiente o En revisión) para una oferta
WHEN visualiza esa oferta en el listado o en el detalle
THEN el botón "Aplicar" está deshabilitado con indicación de que ya existe una solicitud activa

### CA-013: Advertencia por perfil incompleto al aplicar ← HU-002
GIVEN la trabajadora Hogar tiene campos obligatorios del perfil sin completar
WHEN pulsa "Aplicar" en cualquier oferta
THEN se muestra una advertencia que indica los campos obligatorios pendientes y ofrece acceso directo a la sección de perfil para completarlos; no se muestra el diálogo de confirmación de solicitud

### CA-014: Listado de mis solicitudes en orden cronológico inverso ← HU-003
GIVEN la trabajadora Hogar accede a "Mis solicitudes"
WHEN el sistema carga la lista
THEN se muestran todas las solicitudes enviadas en orden cronológico inverso (la más reciente primero), con: título de la oferta, ubicación, fecha de solicitud y estado actual

### CA-015: Distinción visual para solicitudes aceptadas ← HU-003
GIVEN la trabajadora Hogar visualiza el listado de "Mis solicitudes"
WHEN una solicitud tiene estado "Aceptada"
THEN esa solicitud tiene una distinción visual diferenciada respecto a las demás

### CA-016: Filtrar mis solicitudes por estado ← HU-003
GIVEN la trabajadora Hogar está en el listado de "Mis solicitudes"
WHEN selecciona un estado como filtro (Pendiente, En revisión, Aceptada, Rechazada, Oferta cerrada)
THEN el listado muestra únicamente las solicitudes con ese estado

### CA-017: Ver detalle de oferta desde solicitud ← HU-003
GIVEN la trabajadora Hogar está en el listado de "Mis solicitudes"
WHEN toca una solicitud
THEN se navega al detalle de la oferta asociada a esa solicitud

### CA-018: Estado vacío en "Mis solicitudes" ← HU-003
GIVEN la trabajadora Hogar no ha enviado ninguna solicitud todavía
WHEN accede a "Mis solicitudes"
THEN se muestra un estado vacío con un enlace directo a explorar ofertas

### CA-019: Retirar solicitud pendiente ← HU-003
GIVEN la trabajadora Hogar tiene una solicitud en estado "Pendiente"
WHEN selecciona la opción de retirar esa solicitud y confirma en el diálogo de confirmación
THEN la solicitud queda retirada y desaparece del listado de solicitudes activas

### CA-020: Opción de retirar disponible solo para solicitudes Pendientes ← HU-003
GIVEN la trabajadora Hogar visualiza el detalle de una solicitud en estado distinto de "Pendiente" (En revisión, Aceptada, Rechazada, Oferta cerrada)
WHEN accede a las acciones disponibles
THEN la opción de retirar la solicitud no está disponible

---

## Checklist de Validación

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de éxito definidos
- [x] Edge cases documentados (perfil incompleto, solicitud duplicada, cancelar confirmación, solicitud en estado no retirable)
- [x] Estados de error definidos (estado vacío sin ofertas, estado vacío sin solicitudes)
- [x] Ambigüedades resueltas (confirmación de solicitud: in-app, no push; notificación push es para cambios de estado via F-009)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes

---

## Fuera de Alcance

- **Gestión de ofertas por coordinación**: La creación, edición, publicación y cierre de ofertas en el back-office no es parte de este spec. Este spec cubre únicamente la perspectiva de la trabajadora Hogar como consumidora de ofertas.
- **Perfil de la trabajadora**: La visualización y edición del perfil que se adjunta a las solicitudes está cubierta en F-008: profile-management. Este spec únicamente valida la completitud del perfil como precondición para aplicar.
- **Notificaciones push**: El envío de notificaciones push por cambio de estado de solicitud es responsabilidad de F-009: push-notifications. Este spec declara cuándo debe dispararse la notificación, pero no define la infraestructura de entrega.
- **Disponibilidad de la trabajadora**: La gestión del calendario de disponibilidad no es parte de este spec. Está cubierta en F-007: availability-management.
- **Comunicación con coordinación sobre una oferta**: El chat relacionado con una oferta específica está cubierto en F-011: communication. Este spec no incluye la gestión de conversaciones.
- **Valoraciones y reputación**: La publicación de valoraciones entre trabajadoras y clientes está explícitamente excluida del MVP.
- **Perfil SAD**: Las trabajadoras del perfil Felizvita (SAD) no tienen acceso a la sección de Ofertas.

---

## Asunciones Aplicadas

- **[A-001]**: El CA7 de RF-6.2 del PRD indica "La trabajadora recibe notificación de confirmación" al aplicar. Se interpreta como un mensaje de confirmación in-app (toast o mensaje de éxito en pantalla), no como una notificación push. La notificación push se emite únicamente por cambios de estado posteriores de la solicitud (CA8 de RF-6.3), coordinada con F-009: push-notifications. Esta asunción se adopta porque una notificación push inmediata al aplicar (cuando la acción fue iniciada por la propia trabajadora) no aporta valor funcional y podría resultar intrusiva.
