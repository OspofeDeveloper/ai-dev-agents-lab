# Spec: Incident Reporting
> Versión: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-005 via prd-hogar-sad_discovery.md)
> Feature ID: F-005
> Spec monolítico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD (Felizvita) | Profesional de atención domiciliaria que presta servicios de cuidado a clientes asignados | Reportar incidencias del servicio o del usuario atendido; adjuntar fotos y documentos; consultar el historial de incidencias propias; filtrar y buscar incidencias; ver respuestas de coordinación |

---

## Historias de Usuario

### HU-001: Reportar incidencia del servicio o del usuario
Como trabajadora SAD
quiero reportar una incidencia ocurrida durante la prestación del servicio
para que coordinación tenga constancia inmediata y pueda actuar en consecuencia

### HU-002: Adjuntar evidencia a una incidencia
Como trabajadora SAD
quiero adjuntar fotos y documentos a la incidencia que estoy reportando
para que coordinación cuente con pruebas visuales o documentales que faciliten la resolución

### HU-003: Consultar el historial de incidencias propias
Como trabajadora SAD
quiero ver todas las incidencias que he reportado con su estado y las respuestas de coordinación
para que pueda hacer seguimiento de su evolución y saber si se han resuelto

### HU-004: Reportar una incidencia de fichaje o no asistencia
Como trabajadora SAD
quiero reportar desde la pantalla de fichaje que no he podido asistir al servicio o que he tenido un problema operativo
para que coordinación esté informada de la incidencia sin necesidad de acceder al módulo de incidencias

---

## Recorridos de Usuario

### Journey 1: Reportar incidencia durante un servicio
Actor: Trabajadora SAD | Objetivo: comunicar a coordinación una incidencia ocurrida durante el servicio

1. La trabajadora detecta una incidencia durante la prestación del servicio.
2. Accede al módulo de Incidencias desde la navegación principal o desde el detalle del servicio activo.
3. Selecciona "Nueva incidencia".
4. Selecciona el tipo de incidencia de la lista predefinida.
5. Selecciona el servicio relacionado (opcional — puede dejarse sin seleccionar si la incidencia no está vinculada a un servicio concreto).
6. Escribe la descripción de la incidencia (mínimo 20 caracteres).
7. Opcionalmente adjunta fotos desde cámara o galería (máximo 5) y/o documentos (máximo 3).
8. Revisa el tamaño estimado del adjunto antes de enviar.
9. Confirma el envío y recibe confirmación visual de que la incidencia ha sido registrada.

Estado de éxito: La trabajadora ve una pantalla de confirmación con el número de incidencia asignado. La incidencia queda disponible de inmediato para el equipo de coordinación.

Flujos alternativos:
- Si la descripción tiene menos de 20 caracteres al intentar enviar → el sistema muestra un aviso y no permite continuar hasta cumplir el requisito mínimo.
- Si se intenta adjuntar más de 5 fotos → el sistema informa del límite y no permite añadir más.
- Si se intenta adjuntar más de 3 documentos → el sistema informa del límite y no permite añadir más.

---

### Journey 2: Consultar historial y respuesta de coordinación
Actor: Trabajadora SAD | Objetivo: hacer seguimiento de las incidencias reportadas

1. La trabajadora accede al módulo de Incidencias.
2. Ve el listado de sus incidencias en orden cronológico inverso con número, tipo, fecha y estado.
3. Aplica filtros opcionales por estado, rango de fechas o búsqueda por número/descripción.
4. Toca una incidencia para abrir su detalle.
5. Lee la descripción completa, los adjuntos y los comentarios o respuestas del equipo de coordinación.

Estado de éxito: La trabajadora puede leer el hilo completo de la incidencia incluyendo las respuestas de coordinación y sabe en qué estado se encuentra.

Flujos alternativos:
- Si no hay incidencias que coincidan con los filtros aplicados → el sistema muestra un estado vacío informativo.

---

### Journey 3: Reportar incidencia de fichaje o no asistencia desde la pantalla de fichaje
Actor: Trabajadora SAD | Objetivo: comunicar que no puede asistir o ha tenido un problema operativo relacionado con el fichaje

1. La trabajadora está en la pantalla de fichaje de un servicio.
2. Selecciona la opción "Reportar incidencia" disponible en esa pantalla.
3. El formulario de incidencia se abre con el tipo "Incidencia de fichaje / No asistencia" preseleccionado y el servicio relacionado preseleccionado automáticamente.
4. La trabajadora introduce la descripción de la incidencia (mínimo 20 caracteres).
5. Opcionalmente adjunta evidencia (fotos o documentos).
6. Confirma el envío y recibe confirmación visual.

Estado de éxito: La incidencia queda registrada con el tipo y servicio correctos sin que la trabajadora tenga que navegar al módulo de Incidencias.

---

## Resultados y Éxito

Una incidencia se considera reportada con éxito cuando:
- La trabajadora recibe confirmación visual con el número de incidencia asignado.
- La incidencia aparece en el historial de la trabajadora con estado "Reportada".
- El equipo de coordinación tiene acceso inmediato a la incidencia y sus adjuntos.

El historial de incidencias se considera funcional cuando:
- La trabajadora puede consultar todas sus incidencias reportadas, filtrarlas y buscarlas.
- Puede leer los comentarios y respuestas de coordinación desde el detalle de cada incidencia.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Tipos de incidencia predefinidos y alcance:**
Los tipos de incidencia disponibles son exactamente: Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros. La taxonomía y el texto de la interfaz deben dejar claro que la mayoría de tipos corresponden a incidencias del servicio o del usuario atendido; solo el tipo "Incidencia de fichaje / No asistencia" puede referirse a una situación de la propia trabajadora en relación con la prestación del servicio.

**Selección de servicio relacionado:**
La selección de servicio es opcional en todos los tipos de incidencia. Si la trabajadora accede al formulario desde el detalle de un servicio o desde la pantalla de fichaje, el servicio se preselecciona automáticamente. La trabajadora puede modificar esta preselección o dejarla vacía.

**Restricciones de adjuntos:**
- Fotos: máximo 5 por incidencia, aceptadas desde cámara o galería. El sistema aplica compresión de forma transparente para optimizar el tamaño de subida.
- Documentos: máximo 3 por incidencia.
- Antes de confirmar el envío, el sistema muestra el tamaño estimado total de los adjuntos.

**Descripción mínima:**
La descripción es obligatoria y debe tener al menos 20 caracteres. El sistema valida este requisito al intentar enviar y muestra el aviso si no se cumple. El contador de caracteres es visible mientras se escribe.

**Estados del ciclo de vida de una incidencia:**
Los estados posibles son (en orden habitual de progresión): Reportada → En revisión → Resuelta → Cerrada. Solo el equipo de coordinación puede cambiar el estado de una incidencia; la trabajadora solo puede leer el estado.

**Visibilidad inmediata para coordinación:**
Una vez enviada, la incidencia está disponible para coordinación de forma inmediata. La trabajadora no realiza ninguna acción adicional tras la confirmación de envío.

**Búsqueda en el historial:**
La búsqueda en el historial es bajo demanda: la trabajadora introduce el término (número de incidencia o fragmento de descripción) y confirma la búsqueda. No se realiza búsqueda en tiempo real al escribir.

**Acceso al formulario de nueva incidencia:**
El formulario de nueva incidencia es accesible desde dos puntos de entrada: (1) el módulo de Incidencias (botón "Nueva incidencia"), y (2) el detalle de un servicio activo (botón "Reportar incidencia" del servicio). Existe un tercer punto de entrada específico para el tipo "Incidencia de fichaje / No asistencia" desde la pantalla de fichaje (ver Journey 3).

### Destinos de navegación

| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Detalle de un servicio | Tocar "Reportar incidencia" | Formulario nueva incidencia con servicio preseleccionado |
| Pantalla de fichaje | Tocar "Reportar incidencia" | Formulario nueva incidencia con tipo "Incidencia de fichaje / No asistencia" y servicio preseleccionados |
| Módulo de Incidencias | Tocar "Nueva incidencia" | Formulario nueva incidencia sin preselecciones |
| Formulario nueva incidencia | Confirmar envío con éxito | Pantalla de confirmación con número de incidencia → volver al listado de incidencias |
| Listado de incidencias | Tocar una incidencia | Detalle de la incidencia (descripción, adjuntos, comentarios de coordinación) |
| Detalle de incidencia | Botón atrás | Listado de incidencias |

---

## Criterios de Aceptación

### CA-001: Seleccionar tipo de incidencia ← HU-001
GIVEN la trabajadora está en el formulario de nueva incidencia
WHEN visualiza el campo de tipo de incidencia
THEN el sistema muestra exactamente estos tipos seleccionables: "Salud del cliente", "Seguridad", "Material/equipamiento", "Incidencia de fichaje / No asistencia", "Otros"

### CA-002: Selección de servicio relacionado es opcional ← HU-001
GIVEN la trabajadora está en el formulario de nueva incidencia sin haber llegado desde un servicio o fichaje
WHEN visualiza el campo de servicio relacionado
THEN el campo aparece vacío y la trabajadora puede enviarlo sin seleccionar ningún servicio

### CA-003: Preselección de servicio desde detalle de servicio ← HU-001
GIVEN la trabajadora accede al formulario de nueva incidencia desde el detalle de un servicio activo
WHEN el formulario se abre
THEN el campo de servicio relacionado aparece preseleccionado con ese servicio; la trabajadora puede modificar o limpiar la preselección

### CA-004: Descripción obligatoria con mínimo 20 caracteres ← HU-001
GIVEN la trabajadora está en el formulario de nueva incidencia con la descripción vacía o con menos de 20 caracteres
WHEN intenta enviar el formulario
THEN el sistema muestra un aviso indicando que la descripción debe tener al menos 20 caracteres y el formulario no se envía

### CA-005: Contador de caracteres visible al escribir descripción ← HU-001
GIVEN la trabajadora está escribiendo la descripción de la incidencia
WHEN escribe cualquier carácter
THEN el contador de caracteres se actualiza en tiempo real mostrando los caracteres introducidos

### CA-006: Adjuntar fotos con límite máximo ← HU-002
GIVEN la trabajadora está en el formulario de nueva incidencia
WHEN adjunta fotos (desde cámara o galería) y alcanza el límite de 5
THEN el sistema informa del límite y no permite añadir fotos adicionales; las 5 fotos ya adjuntadas se mantienen

### CA-007: Adjuntar documentos con límite máximo ← HU-002
GIVEN la trabajadora está en el formulario de nueva incidencia
WHEN adjunta documentos y alcanza el límite de 3
THEN el sistema informa del límite y no permite añadir documentos adicionales; los 3 documentos ya adjuntados se mantienen

### CA-008: Tamaño estimado de adjuntos visible antes de enviar ← HU-002
GIVEN la trabajadora ha adjuntado al menos un archivo (foto o documento) al formulario de nueva incidencia
WHEN visualiza el formulario antes de enviarlo
THEN el sistema muestra el tamaño estimado total de los adjuntos que se van a enviar

### CA-009: Confirmación de envío con número de incidencia ← HU-001
GIVEN la trabajadora ha completado el formulario de nueva incidencia con al menos tipo y descripción válidos
WHEN confirma el envío
THEN el sistema muestra una pantalla de confirmación con el número de incidencia asignado y la incidencia aparece en el historial de la trabajadora con estado "Reportada"

### CA-010: Incidencia disponible para coordinación inmediatamente ← HU-001
GIVEN la trabajadora acaba de enviar una incidencia con éxito
WHEN coordinación accede al sistema de gestión
THEN la incidencia aparece disponible de inmediato con todos sus datos y adjuntos; no es necesaria ninguna acción adicional de la trabajadora

### CA-011: Listar incidencias en orden cronológico inverso ← HU-003
GIVEN la trabajadora accede al módulo de Incidencias
WHEN visualiza el listado de sus incidencias
THEN las incidencias aparecen ordenadas de más reciente a más antigua, mostrando número de incidencia, tipo, fecha y estado para cada una

### CA-012: Estados del historial de incidencias ← HU-003
GIVEN la trabajadora visualiza el listado o el detalle de una incidencia
WHEN lee el estado de la incidencia
THEN el estado corresponde a uno de los siguientes valores: "Reportada", "En revisión", "Resuelta" o "Cerrada"

### CA-013: Filtrar historial por estado ← HU-003
GIVEN la trabajadora está en el listado de incidencias
WHEN aplica un filtro por estado (por ejemplo, "Resuelta")
THEN el listado muestra únicamente las incidencias con ese estado; si no hay coincidencias, se muestra un estado vacío informativo

### CA-014: Filtrar historial por rango de fechas ← HU-003
GIVEN la trabajadora está en el listado de incidencias
WHEN selecciona un rango de fechas como filtro
THEN el listado muestra únicamente las incidencias con fecha dentro del rango seleccionado

### CA-015: Buscar incidencia por número o descripción ← HU-003
GIVEN la trabajadora está en el listado de incidencias
WHEN introduce un término de búsqueda (número de incidencia o fragmento de descripción) y confirma
THEN el listado muestra únicamente las incidencias que coinciden con el término buscado; si no hay coincidencias, se muestra un estado vacío informativo

### CA-016: Ver detalle completo de incidencia con respuestas de coordinación ← HU-003
GIVEN la trabajadora toca una incidencia en el listado
WHEN se abre el detalle de la incidencia
THEN se muestran: descripción completa, tipo, fecha, estado, adjuntos enviados y los comentarios o respuestas del equipo de coordinación en orden cronológico

### CA-017: Reportar incidencia de fichaje desde pantalla de fichaje ← HU-004
GIVEN la trabajadora está en la pantalla de fichaje de un servicio
WHEN selecciona la opción "Reportar incidencia"
THEN el formulario de nueva incidencia se abre con el tipo "Incidencia de fichaje / No asistencia" preseleccionado y el servicio del fichaje preseleccionado; la trabajadora puede modificar ambos campos antes de enviar

---

## Checklist de Validación

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de éxito definidos
- [x] Edge cases documentados (límites de adjuntos, descripción insuficiente, filtros sin resultados)
- [x] Estados de error definidos (descripción demasiado corta, límite de adjuntos superado)
- [x] Ambigüedades resueltas (véase sección Instrucciones Inambiguas y Asunciones Aplicadas)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes

---

## Fuera de Alcance

- **Gestión de incidencias por coordinación**: la creación, asignación, cambio de estado y cierre de incidencias por parte del equipo de coordinación queda fuera de este spec. Este spec cubre únicamente la perspectiva de la trabajadora SAD.
- **Incidencias de tipo ausencia de la trabajadora**: las ausencias planificadas (vacaciones, bajas, permisos) tienen su propio flujo en la feature F-010: absence-management. El tipo "Incidencia de fichaje / No asistencia" cubre únicamente situaciones operativas imprevistas directamente relacionadas con la prestación del servicio.
- **Notificaciones push de actualización de incidencia**: la entrega de notificaciones push al actualizarse el estado de una incidencia es responsabilidad de la feature F-009: push-notifications.
- **Reporte de incidencias desde el perfil Hogar (CUIDEO)**: esta feature aplica exclusivamente al perfil SAD (Felizvita). Las trabajadoras del perfil Hogar no tienen acceso al módulo de Incidencias.
- **Edición o eliminación de incidencias ya enviadas**: una vez enviada, la trabajadora no puede modificar ni eliminar su incidencia. Las correcciones son gestionadas por coordinación.

---

## Asunciones Aplicadas

- **[A-001]**: La selección de servicio relacionado es opcional para todos los tipos de incidencia. El PRD indica "si la incidencia ocurre durante el servicio" como condición, lo que implica que hay incidencias no vinculadas a un servicio concreto. Asunción conservadora: el campo es siempre opcional, y solo se preselecciona automáticamente cuando el formulario se abre desde un contexto de servicio o fichaje.
- **[A-002]**: Al acceder al formulario de nueva incidencia desde la pantalla de fichaje, el tipo "Incidencia de fichaje / No asistencia" y el servicio correspondiente se preseleccionan automáticamente. El PRD no lo especifica explícitamente pero es el comportamiento más coherente con el contexto y el que ofrece menos fricción a la trabajadora.
- **[A-003]**: La búsqueda en el historial de incidencias (número o descripción) es bajo demanda: la trabajadora confirma explícitamente la búsqueda. Asunción conservadora frente a búsqueda en tiempo real (que podría causar llamadas excesivas al servicio).
