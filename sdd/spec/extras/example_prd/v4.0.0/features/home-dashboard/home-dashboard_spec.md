# Spec: Home Dashboard
> Versión: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-002 via prd-hogar-sad_discovery.md)
> Feature ID: F-002
> Spec monolítico origen: N/A (features-first via discover)

---

## 0. Actores

| Actor | Descripción | Capacidades en este spec |
|-------|-------------|--------------------------|
| Trabajadora Hogar | Cuidadora que opera bajo el perfil CUIDEO Hogar | Ver panel con accesos directos (Ofertas, Disponibilidad, Perfil, Comunicación), ver comunicados del tablón, ver mensajes del sistema |
| Trabajadora SAD | Cuidadora que opera bajo el perfil Felizvita SAD | Ver panel con servicio activo + siguiente servicio, llamamiento pendiente, badge de documentación, accesos directos, ver comunicados del tablón, ver mensajes del sistema |

---

## 1. Historias de Usuario

### HU-001: Ver el panel principal con accesos directos
Como trabajadora (Hogar o SAD)
quiero ver al abrir la app una pantalla principal con accesos directos a las secciones más importantes
para que pueda navegar rápidamente a cualquier módulo de la aplicación sin perder tiempo buscando

### HU-002: Ver llamamiento pendiente en el panel (SAD)
Como trabajadora SAD
quiero que el llamamiento pendiente de respuesta sea visible de forma prominente en el panel principal con cuenta atrás de caducidad
para que no se me pase el tiempo límite para responder y pueda acceder directamente al detalle

### HU-003: Ver servicios activos y próximos en el panel (SAD)
Como trabajadora SAD
quiero ver en el panel principal el servicio activo y el siguiente servicio programado
para que tenga un resumen del día sin necesidad de ir a la sección de servicios

### HU-004: Ver comunicados del tablón de anuncios
Como trabajadora (Hogar o SAD)
quiero acceder al tablón de anuncios desde la app y leer los comunicados de la empresa
para que esté informada de novedades, protocolos y comunicaciones internas de la organización

### HU-005: Ver y gestionar mensajes del sistema
Como trabajadora (Hogar o SAD)
quiero recibir mensajes del sistema de solo lectura con diferentes niveles de prioridad y poder borrarlos cuando ya no los necesite
para que mantenga mi bandeja organizada y pueda identificar rápidamente los mensajes más urgentes

---

## 2. Recorridos de Usuario

### Journey 1 (Ambos perfiles): Abrir app y navegar desde el panel principal

1. La trabajadora abre la aplicación con sesión activa.
2. El sistema muestra el panel principal con la cabecera con nombre y foto de perfil de la trabajadora.
3. El panel muestra los accesos directos adaptados al perfil:
   - **Hogar**: Ofertas, Mi Disponibilidad, Perfil, Comunicación.
   - **SAD**: Mis Servicios, Fichar, Incidencias, Solicitar Ausencia, Mis Ausencias, Mi Disponibilidad, Documentación, Perfil, Comunicación.
4. Los accesos directos con pendientes muestran un badge con el contador correspondiente (mensajes no leídos, acciones pendientes).
5. El panel muestra el bloque "Últimos avisos" con 2-3 comunicados recientes y un enlace al listado completo del tablón.
6. La trabajadora toca un acceso directo y el sistema navega al módulo correspondiente.

### Journey 2 (SAD): Ver llamamiento pendiente y navegar al detalle

1. La trabajadora SAD abre el panel principal.
2. El sistema detecta que existe al menos un llamamiento pendiente de respuesta.
3. El panel muestra el bloque de llamamiento de forma muy visible, con indicador de urgencia y cuenta atrás hasta la caducidad.
4. La trabajadora toca el bloque del llamamiento.
5. El sistema navega a la pantalla de detalle del llamamiento. Desde el panel nunca es posible aceptar o rechazar directamente.

### Journey 3 (SAD): Ver servicios activos en el panel y navegar al detalle

1. La trabajadora SAD abre el panel principal.
2. El sistema muestra en el bloque de servicios el servicio activo en curso (si lo hay) y el siguiente servicio programado.
3. Si existen más servicios más allá del siguiente, el sistema muestra el enlace "Ver más servicios" en lugar de un contador numérico.
4. La trabajadora toca la tarjeta de un servicio.
5. El sistema navega a la pantalla de detalle completo de ese servicio.

### Journey 4 (Ambos perfiles): Leer un comunicado del tablón

1. La trabajadora accede a la sección del tablón de anuncios desde el panel o el menú de navegación.
2. El sistema muestra el listado de comunicados diferenciando entre contenidos fijos (protocolos, calendario laboral, PRL, documentos de referencia permanente) y comunicaciones variables (recordatorios, campañas, novedades). Los contenidos fijados por backoffice aparecen en la parte superior.
3. Los comunicados no leídos tienen un indicador visual que los distingue de los ya leídos.
4. La trabajadora toca un comunicado.
5. El sistema abre el detalle completo del comunicado con título, fecha, texto, imágenes y adjuntos si los hubiera.
6. El sistema marca automáticamente el comunicado como leído al abrirlo.

### Journey 5 (Ambos perfiles): Gestionar mensajes del sistema

1. La trabajadora accede a la sección de mensajes del sistema.
2. El sistema muestra el listado de mensajes con remitente, asunto y fecha. Los mensajes de criticidad alta aparecen en la parte superior con una distinción visual clara respecto a los de criticidad normal.
3. Los mensajes no leídos tienen un indicador visual.
4. La trabajadora toca un mensaje para leer el contenido completo.
5. El sistema marca el mensaje como leído automáticamente al abrirlo.
6. La trabajadora puede borrar un mensaje. El sistema elimina el mensaje de la lista.

---

## 3. Resultados y Éxito

### Definición de "hecho" para esta feature

El panel principal se considera completo y exitoso cuando:

- La trabajadora ve en su panel la información y accesos directos adaptados a su perfil (Hogar o SAD) en el momento de abrir la app.
- La trabajadora SAD puede identificar de un vistazo si tiene un llamamiento pendiente urgente y puede acceder a su detalle con un solo toque.
- La trabajadora SAD puede ver el servicio activo y el próximo sin necesidad de navegar a la sección de servicios.
- La trabajadora puede acceder a comunicados de empresa, leerlos y saber cuáles son nuevos.
- La trabajadora puede leer y borrar mensajes del sistema, diferenciando los urgentes de los normales.
- El panel se actualiza con pull-to-refresh mostrando la información más reciente.
- Los badges de pendientes son precisos y se actualizan tras realizar la acción correspondiente.

---

## 4. Instrucciones Inambiguas

### Comportamiento del panel principal

- El panel carga todos sus datos en una única operación al abrirse. No se realizan cargas parciales por bloque que deje el panel incompleto visible al usuario durante la carga.
- Si la carga falla, el panel muestra un mensaje de error genérico con opción de reintentar. No se muestra contenido parcial en estado de error.
- El pull-to-refresh actualiza todos los datos del panel: accesos directos, badges, bloque de llamamiento, bloque de servicios y bloque de "Últimos avisos".

### Cabecera del panel

- La cabecera muestra siempre el nombre de la trabajadora y su foto de perfil.
- Si la trabajadora no tiene foto de perfil, se muestra un avatar con sus iniciales.

### Accesos directos y badges

- Un badge en un acceso directo se muestra solo cuando hay elementos pendientes de atención del usuario. Si no hay pendientes, no se muestra badge.
- El badge de mensajes muestra el número de mensajes no leídos (conversaciones del chat de coordinación). Si hay más de 99, muestra "99+".
- El badge de documentación pendiente de firma (SAD) se muestra únicamente cuando existe al menos un documento que requiere firma de la trabajadora. Si no hay documentos pendientes de firma, no se muestra ningún badge en ese acceso directo.

### Bloque de llamamiento (SAD)

- El bloque de llamamiento solo aparece en el panel cuando existe al menos un llamamiento en estado "pendiente de respuesta" para la trabajadora.
- Si no hay llamamiento pendiente, el bloque no aparece en el panel.
- La cuenta atrás del llamamiento es en tiempo real y visible mientras la trabajadora está en el panel.
- Al tocar el bloque de llamamiento, la navegación destino es la pantalla de **Detalle del Llamamiento**. No existe acción de aceptar o rechazar directamente desde el panel.

### Bloque de servicios (SAD)

- El bloque de servicios muestra como máximo: el servicio activo en curso (si lo hay) y el siguiente servicio programado.
- Si no hay servicio activo ni próximo, el bloque muestra un estado vacío apropiado (ej.: "No tienes servicios próximos").
- Si hay más de un servicio más allá del mostrado, se muestra el enlace "Ver más servicios". Al tocarlo, la navegación destino es la pantalla de **Listado de Servicios**.
- Al tocar la tarjeta de un servicio, la navegación destino es la pantalla de **Detalle del Servicio** de ese servicio concreto.
- Las tarjetas del panel muestran información resumida: nombre o código del cliente, fecha/hora del servicio y estado.

### Bloque "Últimos avisos" (ambos perfiles)

- Este bloque está siempre presente en el panel y muestra entre 2 y 3 comunicados recientes.
- Si no hay comunicados publicados, el bloque muestra un estado vacío.
- Al tocar "Ver todos" o equivalente en el bloque, la navegación destino es la pantalla de **Tablón de Anuncios**.
- Al tocar un comunicado individual del bloque, la navegación destino es la pantalla de **Detalle del Comunicado** correspondiente.

### Tablón de anuncios

- Los comunicados se organizan en dos grupos: contenidos fijos y comunicaciones variables. Los contenidos fijados manualmente desde backoffice aparecen en la parte superior de la lista, independientemente de su grupo.
- Un comunicado muestra en el listado: título, fecha de publicación y texto de previsualización (primeras líneas del texto).
- El comunicado se marca como leído en el momento en que la trabajadora lo abre. No hay botón de "marcar como leído".
- El detalle del comunicado puede contener imágenes y archivos adjuntos. Los adjuntos son descargables/visualizables desde el detalle.
- Si hay comunicados no leídos, el icono del tablón en la barra de navegación muestra un badge. El badge desaparece cuando todos los comunicados están leídos.
- Cuando se publica un nuevo comunicado, la trabajadora recibe una notificación push. Esta notificación está especificada en el scope de F-009 (push-notifications).

### Mensajes del sistema

- Los mensajes del sistema son de solo lectura. No existe ningún botón ni opción de respuesta.
- Los mensajes de criticidad alta se muestran en la parte superior del listado con un tratamiento visual diferenciado (distinto a los de criticidad normal). La asignación de criticidad es responsabilidad del administrador en backoffice.
- Al abrir un mensaje, se marca automáticamente como leído. El indicador de no leído desaparece.
- El borrado de un mensaje es permanente y no requiere confirmación previa. El mensaje desaparece de la lista inmediatamente.
- Los mensajes del sistema pueden incluir adjuntos. Los adjuntos son visualizables desde el detalle del mensaje.
- Los mensajes del sistema no pueden ser respondidos por la trabajadora.

### Tabla de destinos de navegación

| Origen | Acción del usuario | Destino |
|--------|-------------------|---------|
| Panel — acceso directo | Tocar cualquier acceso directo | Pantalla principal del módulo correspondiente |
| Panel — bloque llamamiento (SAD) | Tocar el bloque | Detalle del Llamamiento |
| Panel — tarjeta de servicio (SAD) | Tocar una tarjeta de servicio | Detalle del Servicio |
| Panel — bloque "Últimos avisos" | Tocar "Ver todos" | Tablón de Anuncios (listado completo) |
| Panel — bloque "Últimos avisos" | Tocar un comunicado | Detalle del Comunicado |
| Tablón de Anuncios — listado | Tocar un comunicado | Detalle del Comunicado |
| Mensajes del sistema — listado | Tocar un mensaje | Detalle del Mensaje |

---

## 5. Criterios de Aceptación

### CA-001: Panel Hogar — accesos directos correctos ← HU-001
GIVEN una trabajadora del perfil Hogar con sesión activa
WHEN abre el panel principal
THEN el panel muestra accesos directos a: Ofertas, Mi Disponibilidad, Perfil y Comunicación

### CA-002: Panel SAD — accesos directos correctos ← HU-001
GIVEN una trabajadora del perfil SAD con sesión activa
WHEN abre el panel principal
THEN el panel muestra accesos directos a: Mis Servicios, Fichar, Incidencias, Solicitar Ausencia, Mis Ausencias, Mi Disponibilidad, Documentación, Perfil y Comunicación

### CA-003: Cabecera con nombre y foto de perfil ← HU-001
GIVEN una trabajadora con sesión activa y foto de perfil cargada
WHEN abre el panel principal
THEN la cabecera muestra su nombre y su foto de perfil

### CA-004: Cabecera con avatar cuando no hay foto ← HU-001
GIVEN una trabajadora con sesión activa que no ha subido foto de perfil
WHEN abre el panel principal
THEN la cabecera muestra su nombre y un avatar con sus iniciales en lugar de foto

### CA-005: Badge de mensajes no leídos ← HU-001
GIVEN una trabajadora con 3 mensajes de chat de coordinación no leídos
WHEN abre el panel principal
THEN el acceso directo de Comunicación muestra un badge con el número "3"

### CA-006: Sin badge cuando no hay pendientes ← HU-001
GIVEN una trabajadora sin mensajes no leídos ni acciones pendientes
WHEN abre el panel principal
THEN ningún acceso directo muestra badge

### CA-007: Navegación desde acceso directo ← HU-001
GIVEN la trabajadora está en el panel principal
WHEN toca el acceso directo de cualquier módulo
THEN el sistema navega a la pantalla principal de ese módulo

### CA-008: Pull-to-refresh actualiza el panel ← HU-001
GIVEN la trabajadora está en el panel principal
WHEN realiza el gesto de pull-to-refresh
THEN el sistema recarga todos los datos del panel: accesos directos, badges, bloque de llamamiento (SAD), bloque de servicios (SAD) y bloque "Últimos avisos"

### CA-009: Bloque llamamiento visible en panel SAD ← HU-002
GIVEN una trabajadora SAD con un llamamiento en estado "pendiente de respuesta"
WHEN abre el panel principal
THEN el bloque de llamamiento aparece de forma prominente con indicador de urgencia y cuenta atrás de tiempo hasta caducidad

### CA-010: Sin bloque llamamiento cuando no hay pendientes ← HU-002
GIVEN una trabajadora SAD sin llamamientos pendientes de respuesta
WHEN abre el panel principal
THEN el bloque de llamamiento no aparece en el panel

### CA-011: CTA del llamamiento navega al detalle, nunca acepta/rechaza ← HU-002
GIVEN una trabajadora SAD visualiza un llamamiento pendiente en el panel
WHEN toca el bloque del llamamiento
THEN el sistema navega a la pantalla de Detalle del Llamamiento y no existe ninguna opción de aceptar o rechazar directamente desde el panel

### CA-012: Bloque servicios SAD — máximo servicio activo + siguiente ← HU-003
GIVEN una trabajadora SAD con servicio activo en curso y dos servicios próximos
WHEN abre el panel principal
THEN el bloque de servicios muestra el servicio activo y solo el siguiente servicio próximo; para los servicios adicionales muestra el enlace "Ver más servicios"

### CA-013: Enlace "Ver más servicios" navega al listado ← HU-003
GIVEN el bloque de servicios del panel muestra el enlace "Ver más servicios"
WHEN la trabajadora SAD toca ese enlace
THEN el sistema navega a la pantalla de Listado de Servicios

### CA-014: Tarjeta de servicio navega al detalle ← HU-003
GIVEN el bloque de servicios del panel muestra la tarjeta de un servicio
WHEN la trabajadora SAD toca esa tarjeta
THEN el sistema navega a la pantalla de Detalle del Servicio correspondiente

### CA-015: Estado vacío en bloque de servicios ← HU-003
GIVEN una trabajadora SAD sin ningún servicio activo ni próximo
WHEN abre el panel principal
THEN el bloque de servicios muestra un estado vacío sin tarjetas de servicio

### CA-016: Badge de documentación pendiente de firma (SAD) ← HU-001
GIVEN una trabajadora SAD con al menos un documento pendiente de firma
WHEN abre el panel principal
THEN el acceso directo de Documentación muestra un badge destacado indicando que hay documentación pendiente de firma

### CA-017: Sin badge de documentación cuando no hay pendientes ← HU-001
GIVEN una trabajadora SAD sin documentos pendientes de firma
WHEN abre el panel principal
THEN el acceso directo de Documentación no muestra ningún badge

### CA-018: Listado de comunicados del tablón ← HU-004
GIVEN la trabajadora accede al tablón de anuncios
WHEN el sistema carga el listado
THEN muestra los comunicados con su título, fecha de publicación y previsualización del texto; los contenidos fijados desde backoffice aparecen en la parte superior de la lista

### CA-019: Indicador visual de comunicado no leído ← HU-004
GIVEN el tablón contiene comunicados que la trabajadora no ha abierto todavía
WHEN la trabajadora accede al listado del tablón
THEN los comunicados no leídos tienen un indicador visual que los diferencia de los ya leídos

### CA-020: Marcar comunicado como leído al abrirlo ← HU-004
GIVEN la trabajadora abre el detalle de un comunicado no leído
WHEN el detalle del comunicado se muestra en pantalla
THEN el sistema marca ese comunicado como leído automáticamente y el indicador visual de no leído desaparece

### CA-021: Detalle del comunicado con adjuntos ← HU-004
GIVEN la trabajadora abre el detalle de un comunicado que incluye imágenes y archivos adjuntos
WHEN el detalle del comunicado se muestra en pantalla
THEN el contenido completo es visible incluyendo texto, imágenes y adjuntos descargables

### CA-022: Badge en tablón desaparece cuando todo está leído ← HU-004
GIVEN la trabajadora ha leído todos los comunicados del tablón
WHEN regresa al panel principal o a la barra de navegación
THEN el icono del tablón no muestra ningún badge de contenido nuevo

### CA-023: Listado de mensajes del sistema con niveles de criticidad ← HU-005
GIVEN la trabajadora accede a la sección de mensajes del sistema
WHEN el sistema muestra el listado
THEN los mensajes de criticidad alta aparecen en la parte superior con tratamiento visual diferenciado respecto a los mensajes de criticidad normal; cada mensaje muestra remitente, asunto y fecha

### CA-024: Marcar mensaje del sistema como leído al abrirlo ← HU-005
GIVEN la trabajadora abre el detalle de un mensaje del sistema no leído
WHEN el detalle se muestra en pantalla
THEN el sistema marca el mensaje como leído automáticamente y el indicador de no leído desaparece

### CA-025: Mensajes del sistema sin opción de respuesta ← HU-005
GIVEN la trabajadora abre el detalle de cualquier mensaje del sistema
WHEN el detalle se muestra en pantalla
THEN no existe ningún botón, campo de texto ni opción para responder el mensaje

### CA-026: Borrar mensaje del sistema ← HU-005
GIVEN la trabajadora está en el listado de mensajes del sistema
WHEN selecciona la opción de borrar un mensaje
THEN el mensaje desaparece permanentemente de la lista

### CA-027: Bloque "Últimos avisos" en el panel ← HU-001, HU-004
GIVEN la trabajadora abre el panel principal y existen comunicados publicados
WHEN el panel carga
THEN el bloque "Últimos avisos" muestra entre 2 y 3 comunicados recientes con acceso directo al listado completo del tablón

### CA-028: Error de carga del panel ← HU-001
GIVEN la trabajadora abre el panel principal y el sistema no puede cargar los datos
WHEN la carga falla
THEN el panel muestra un mensaje de error genérico con opción de reintentar; no se muestra contenido parcial

---

## 6. Checklist de Validación

- [x] Todos los roles/actores identificados (Trabajadora Hogar y Trabajadora SAD con capacidades diferenciadas)
- [x] Todos los flujos principales descritos paso a paso (5 journeys cubriendo panel, llamamiento, servicios, tablón y mensajes)
- [x] Estados de éxito definidos para cada flujo (sección "Resultados y Éxito")
- [x] Casos límite y edge cases documentados (sin llamamiento, sin servicios, sin foto de perfil, error de carga, estado vacío)
- [x] Estados de error y fallo definidos (error de carga con opción de reintentar, CA-028)
- [x] Todas las ambigüedades resueltas (tabla de destinos de navegación completa, comportamiento de badges, reglas de bloque de servicios)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Cada destino de navegación está enumerado con sus variantes (tabla de destinos de navegación en sección 4)

---

## 7. Fuera de Alcance

- **Gestión de llamamientos** (aceptar, rechazar, ver historial): esta funcionalidad pertenece a F-003 (service-management). El panel únicamente muestra el estado urgente del llamamiento y navega a su detalle.
- **Detalle y gestión de servicios**: el panel solo muestra tarjetas resumidas. El CRUD de servicios pertenece a F-003 (service-management).
- **Registro de dispositivo para notificaciones push**: el registro FCM y la entrega de notificaciones push es responsabilidad de F-009 (push-notifications). Este spec solo documenta que el tablón muestra un badge y estado actualizado tras recibir notificación.
- **Chat con coordinación**: el módulo de mensajería entre trabajadora y coordinación pertenece a F-011 (communication). El panel solo muestra el badge de mensajes no leídos.
- **Gestión de documentos y firma digital**: la subida, descarga y firma de documentos pertenece a F-008 (profile-management). El panel solo muestra el badge de documentos pendientes de firma (SAD).
- **Creación y publicación de comunicados**: la publicación de comunicados desde backoffice no es parte de esta feature. Este spec cubre únicamente la visualización y lectura por parte de la trabajadora.
- **Gestión de perfil y foto**: la edición del perfil y la subida de foto de perfil pertenece a F-008 (profile-management). El panel solo muestra los datos del perfil en la cabecera.
- **Funcionalidades de páginas de detalle**: cada acceso directo del panel conduce a su feature correspondiente, que tiene su propio spec.

---

## Asunciones Aplicadas

- **[A-001]**: La distinción visual entre comunicados de "contenidos fijos" y "comunicaciones variables" en el tablón no tiene una separación en bloques rígidos visualmente; la diferencia entre tipos se indica mediante etiquetas o metadatos en cada comunicado. Los contenidos fijados desde backoffice aparecen siempre en la parte superior independientemente de su tipo. Justificación: el PRD especifica que los tipos no están "necesariamente separados en bloques rígidos" (RF-2.2 CA1) y que el backoffice puede fijar contenidos.

- **[A-002]**: La criticidad de los mensajes del sistema (alta vs. normal) se asigna exclusivamente desde backoffice al crear el mensaje. La trabajadora no puede cambiar la criticidad de un mensaje. Justificación: el PRD no especifica mecanismo de asignación de criticidad desde la app; se aplica la opción más conservadora (solo lectura para la trabajadora).

- **[A-003]**: El pull-to-refresh del panel principal actualiza la totalidad de los datos visibles en el panel en una única operación. Si la trabajadora está en la sección del tablón o mensajes del sistema y realiza pull-to-refresh en esas pantallas, solo se actualiza el contenido de esa pantalla específica. Justificación: comportamiento estándar de pull-to-refresh por pantalla, conserva el patrón esperado por el usuario.

- **[A-004]**: El borrado de un mensaje del sistema no requiere diálogo de confirmación. La acción es permanente e inmediata. Justificación: el PRD especifica únicamente "opción de borrar mensajes" (RF-2.3 CA6) sin indicar confirmación; se aplica la implementación más sencilla funcional. Si el cliente desea confirmación, debe indicarlo.
