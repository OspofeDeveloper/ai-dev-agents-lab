# Spec: Services Management
> Versión: 1.0 | Fecha: 2026-04-02
> Spec monolítico origen: prd-hogar-sad_spec.md
> Feature ID: F-003

---

## Actores
| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona servicios asignados. Usa la app Felizvita (identidad visual verde). | Ver listado de servicios, ver detalle de un servicio, gestionar notas, responder llamamientos con firma digital, recibir y confirmar nuevos servicios asignados. |
| Sistema / Backoffice | Equipo de coordinación y administración que gestiona el backend y los datos. | Asignar servicios, enviar llamamientos, visualizar notas de servicio en tiempo real. No es un actor de la app móvil pero sus acciones generan estados visibles para las trabajadoras. |

---

## Historias de Usuario

### HU-010: Ver el detalle de un servicio (SAD)
Como trabajadora SAD / quiero ver toda la información de un servicio asignado (datos del cliente, ubicación, plan de cuidados, tareas, documentos) / para que pueda prepararme y ejecutar el servicio correctamente.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-003]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

### HU-011: Consultar mis servicios asignados (SAD)
Como trabajadora SAD / quiero ver el listado de todos mis servicios agrupados por estado / para que pueda saber qué servicios tengo activos, próximos y completados.

### HU-012: Responder a un llamamiento (SAD)
Como trabajadora SAD / quiero aceptar o rechazar un llamamiento con mi firma digital / para que quede constancia legal de mi decisión sobre el turno ofrecido.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-004], [P-008]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

### HU-013: Gestionar notas de un servicio (SAD)
Como trabajadora SAD / quiero añadir, editar y borrar notas sobre la evolución del servicio / para que las coordinadoras estén informadas de lo que ocurre en el servicio en tiempo real.

### HU-014: Recibir y confirmar un nuevo servicio asignado (SAD — contrato indefinido)
Como trabajadora SAD con contrato indefinido / quiero recibir una notificación cuando me asignan un nuevo servicio y confirmar que lo he visto / para que quede registrado que he recibido la información.

---

## Recorridos de Usuario

### Journey 5: Responder a un llamamiento (SAD)
Actor: Trabajadora SAD | Objetivo: Aceptar o rechazar un turno ofrecido con firma digital

1. La trabajadora recibe una notificación push de nuevo llamamiento.
2. La trabajadora abre la notificación y llega al detalle del llamamiento en la app, o accede desde la home donde el llamamiento se muestra de forma muy visible con cuenta atrás.
3. Desde la home, la trabajadora pulsa el CTA que lleva al detalle del llamamiento (no puede aceptar/rechazar directamente desde la home).
4. La trabajadora está en el detalle del llamamiento. La navegación hacia atrás queda bloqueada hasta que tome una decisión.
5. La trabajadora ve la información completa del llamamiento: código de servicio, fecha/hora, ubicación, urgencia y cuenta atrás de caducidad.
6a. Si la trabajadora acepta: se muestra un diálogo con el texto de aceptación. La trabajadora firma digitalmente con el dedo y confirma.
6b. Si la trabajadora rechaza: se muestra un diálogo para seleccionar el motivo (No disponible, Demasiado lejos, Motivos personales, Otros — con campo de texto). La trabajadora firma digitalmente con el dedo y confirma.
7. El llamamiento queda registrado como aceptado o rechazado.

Estado de éxito: La firma digital queda registrada. El llamamiento aparece en el historial con su resultado. Si fue aceptado, el servicio aparece en la lista de servicios de la trabajadora.

Flujos alternativos:
- Si el llamamiento caduca mientras la trabajadora está en el detalle → [PENDIENTE P-004: comportamiento al caducar sin respuesta].
- Si otro compañero acepta primero el llamamiento → el llamamiento aparece como desactivado/no disponible en la lista.
- Los textos legales de los diálogos de firma → [PENDIENTE P-008].

---

## Resultados y Éxito

- **Servicio gestionado correctamente**: La trabajadora SAD ha fichado entrada y salida con geolocalización; los registros aparecen en el historial con hora, fecha y duración. Las coordinadoras pueden ver las notas registradas sobre el servicio.
- **Llamamiento respondido**: La firma digital de la trabajadora queda almacenada junto a la decisión (aceptación o rechazo) y el llamamiento aparece en el historial con su resultado y fecha.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Llamamientos (SAD):**
- La aceptación y el rechazo de llamamientos solo son posibles desde el detalle del llamamiento, nunca directamente desde la home.
- Una vez dentro del detalle del llamamiento, la navegación hacia atrás queda bloqueada hasta que la trabajadora acepte o rechace.
- Tanto la aceptación como el rechazo requieren firma digital de la trabajadora.
- Los motivos de rechazo disponibles son: No disponible, Demasiado lejos, Motivos personales, Otros (con campo de texto libre).
- Cuando un llamamiento caduca o es aceptado por otra trabajadora, se muestra como desactivado/no disponible en la lista.
- [PENDIENTE P-004]: comportamiento exacto cuando un llamamiento caduca sin respuesta (¿estado "sin respuesta" o "rechazo por inacción"? ¿notificación a la trabajadora?).

**Experiencia general:**
- Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse.
- La trabajadora puede adjuntar fotos y documentos. El sistema informa si un archivo no puede enviarse antes de intentar la subida.

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Home SAD | Toca CTA de llamamiento pendiente | Detalle del llamamiento |
| Detalle del llamamiento | Decisión tomada (acepta o rechaza) | Desbloqueo de navegación → Home u otra sección |
| Detalle del servicio | Pulsa dirección | App de Maps del dispositivo (Google Maps / Apple Maps) |
| Detalle del servicio | Pulsa "Reportar incidencia" | Formulario de reporte de incidencia |
| Detalle del servicio | Pulsa "Contacta con tu coordinador / empresa" | Información de teléfono de coordinación |

---

## Criterios de Aceptación

### CA-001: Listado de servicios — agrupado por estado ← HU-011
GIVEN la trabajadora SAD accede a "Mis Servicios"
WHEN la lista se carga
THEN los servicios aparecen agrupados en tres grupos: Activos, Próximos, Completados; con información clave de cada uno (nombre/código del cliente, dirección, fecha/hora, tipo).

---

### CA-002: Listado de servicios — distinción recurrente/puntual ← HU-011
GIVEN la trabajadora SAD ve la lista de servicios
WHEN revisa las tarjetas de servicio
THEN hay distinción visual entre servicios recurrentes (sin fecha de fin) y puntuales (con fecha de inicio y fin definidas).

---

### CA-003: Detalle del servicio — información básica y del cliente ← HU-010
GIVEN la trabajadora SAD toca un servicio en la lista
WHEN se abre el detalle del servicio
THEN se muestra la información básica del servicio (código, tipo, fechas, horario) y la información del cliente (nombre, dirección, edad); la visibilidad de determinados campos del cliente es controlable desde backoffice.

---

### CA-004: Detalle del servicio — datos de salud pendientes ← HU-010

> [INCOMPLETO] — Pendiente de gap [P-003]: qué datos de salud del cliente (si alguno) puede ver la trabajadora no está definido. CA no puede completarse hasta resolver el gap.

---

### CA-005: Detalle del servicio — dirección abre Maps ← HU-010
GIVEN la trabajadora SAD está en el detalle de un servicio
WHEN toca la dirección del cliente
THEN la app de Maps del dispositivo (Google Maps o Apple Maps, según el dispositivo) se abre con la dirección del servicio. No hay mapa embebido en la pantalla de detalle.

---

### CA-006: Detalle del servicio — plan de cuidados y tareas ← HU-010
GIVEN la trabajadora SAD está en el detalle de un servicio
WHEN consulta el plan de cuidados
THEN se muestra el listado descriptivo de tareas (sin checklist); la trabajadora no puede editarlo.

---

### CA-007: Detalle del servicio — CTA de contacto coordinador ← HU-010
GIVEN la trabajadora SAD está en el detalle de un servicio
WHEN ve la pantalla de detalle
THEN se muestra de forma prominente un CTA "Contacta con tu coordinador / empresa" con el teléfono de coordinación.

---

### CA-008: Detalle del servicio — accesos rápidos a fichaje e incidencias ← HU-010
GIVEN la trabajadora SAD está en el detalle de un servicio
WHEN ve la pantalla de detalle
THEN hay acceso directo para fichar entrada/salida y para reportar incidencia del servicio.

---

### CA-009: Notas de servicio — lista cronológica y añadir nota ← HU-013
GIVEN la trabajadora SAD accede a las notas de un servicio
WHEN ve la pantalla de notas
THEN se muestra la lista cronológica de notas con autora, fecha/hora, contenido y adjuntos; hay opción de añadir una nueva nota con texto multilínea y adjuntos (fotos o documentos); la nota se puede categorizar como: Evolución, Tareas, Incidencias, Otras.

---

### CA-010: Notas de servicio — borrar nota propia ← HU-013
GIVEN la trabajadora SAD ve una nota que ha creado ella misma
WHEN selecciona la opción de borrar
THEN la nota desaparece de la lista (borrado suave para auditoría). Las notas de otras autoras no tienen opción de borrar.

---

### CA-011: Llamamientos — lista con estados ← HU-012
GIVEN la trabajadora SAD accede al listado de llamamientos
WHEN la lista se carga
THEN se muestran todas las llamadas de servicio recibidas con estado (pendiente, aceptada, rechazada, caducada/desactivada) e información básica (código de servicio, fecha/hora, ubicación, urgencia).

---

### CA-012: Llamamientos — cuenta atrás para pendientes ← HU-012
GIVEN la trabajadora SAD tiene un llamamiento con estado "pendiente"
WHEN ve la lista o el detalle del llamamiento
THEN se muestra una cuenta atrás visual del tiempo restante para responder.

---

### CA-013: Llamamientos — bloqueo de navegación en detalle ← HU-012
GIVEN la trabajadora SAD entra al detalle de un llamamiento pendiente
WHEN intenta navegar hacia atrás sin haber tomado una decisión
THEN la navegación hacia atrás queda bloqueada hasta que acepte o rechace el llamamiento.

---

### CA-014: Llamamientos — aceptar con firma digital ← HU-012
GIVEN la trabajadora SAD está en el detalle de un llamamiento pendiente y pulsa aceptar
WHEN se muestra el diálogo de aceptación
THEN la trabajadora debe firmar digitalmente con el dedo para confirmar la aceptación; [PENDIENTE P-008: textos legales del diálogo de aceptación].

---

### CA-015: Llamamientos — rechazar con motivo y firma digital ← HU-012
GIVEN la trabajadora SAD está en el detalle de un llamamiento pendiente y pulsa rechazar
WHEN se muestra el diálogo de rechazo
THEN la trabajadora debe seleccionar un motivo (No disponible, Demasiado lejos, Motivos personales, Otros — con campo de texto) y firmar digitalmente con el dedo; [PENDIENTE P-008: textos legales del diálogo de rechazo].

---

### CA-016: Llamamientos — caducado sin respuesta (pendiente) ← HU-012

> [INCOMPLETO] — Pendiente de gap [P-004]: comportamiento cuando el llamamiento caduca sin respuesta (estado, consecuencias, notificación) no definido.

---

### CA-017: Llamamientos — desactivado cuando acepta otra trabajadora ← HU-012
GIVEN otro compañero ha aceptado un llamamiento al que la trabajadora también tenía acceso
WHEN la trabajadora ve su lista de llamamientos
THEN ese llamamiento aparece como desactivado/no disponible.

---

### CA-018: Nuevo servicio asignado (contrato indefinido) — notificación y confirmación ← HU-014
GIVEN la trabajadora SAD con contrato indefinido recibe un nuevo servicio asignado
WHEN llega la notificación push
THEN la notificación tiene deeplink al detalle del servicio; al abrir el detalle, se registra que la trabajadora ha recibido/visto la asignación; el nuevo servicio aparece en la home de forma diferenciada de los llamamientos.

---

### CA-019: Nuevo servicio asignado — generar incidencia si no puede atender ← HU-014
GIVEN la trabajadora SAD con contrato indefinido está en el detalle de un nuevo servicio asignado
WHEN decide que no puede atender el servicio
THEN puede generar una incidencia para comunicarlo a coordinación (no es un rechazo formal).

---

## Checklist de Validación
- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de éxito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [x] Ambigüedades resueltas (las resolubles; las pendientes marcadas como [INCOMPLETO])
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes
- [ ] Datos de salud y RGPD revisados por legal ([P-003])
- [ ] Textos legales de llamamientos revisados por legal ([P-008])
- [ ] Comportamiento de llamamiento caducado revisado con legal ([P-004])

---

## Fuera de Alcance
- Pantalla de historial de servicios completados (RF-3.5 del PRD): el historial completo de llamamientos con su resultado está incluido en el alcance; el historial de servicios completados con filtro por fechas y detalle de horas trabajadas no está incluido en este spec.
