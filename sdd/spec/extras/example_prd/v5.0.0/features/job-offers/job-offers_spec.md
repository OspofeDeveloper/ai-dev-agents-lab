# Spec: Ofertas de Trabajo
> Version: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-007 via prd-hogar-sad_discovery.md)
> Feature ID: F-007
> Spec monolitico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio del perfil CUIDEO (Hogar) que busca oportunidades de trabajo | Navegar ofertas disponibles, ver detalle de oferta, solicitar oferta, consultar solicitudes presentadas, retirar solicitud pendiente |

---

## Historias de Usuario

### HU-001: Navegar ofertas disponibles
Como trabajadora Hogar
quiero ver las ofertas de trabajo disponibles con posibilidad de filtrar y ordenar
para que pueda encontrar oportunidades adecuadas a mis preferencias de zona, horario y condiciones.

### HU-002: Ver detalle de una oferta
Como trabajadora Hogar
quiero ver la informacion completa de una oferta de trabajo
para que pueda evaluarla y decidir si me interesa solicitarla.

### HU-003: Solicitar una oferta
Como trabajadora Hogar
quiero solicitar una oferta de trabajo con un solo toque
para que pueda aplicar de forma rapida sin tener que rellenar formularios adicionales.

### HU-004: Consultar mis solicitudes
Como trabajadora Hogar
quiero ver el listado de todas mis solicitudes presentadas con su estado actual
para que pueda hacer seguimiento de mis candidaturas.

### HU-005: Retirar una solicitud pendiente
Como trabajadora Hogar
quiero poder retirar una solicitud que aun este pendiente de revision
para que pueda desistir de una oferta si ya no me interesa.

### HU-006: Recibir notificacion de cambio de estado
Como trabajadora Hogar
quiero recibir una notificacion cuando cambie el estado de alguna de mis solicitudes
para que pueda estar informada sin tener que entrar a consultar manualmente.

---

## Recorridos de Usuario

### Journey 1: Navegar y buscar ofertas de trabajo
**Actor**: Trabajadora Hogar | **Objetivo**: Encontrar ofertas de trabajo adecuadas

1. La trabajadora accede a la seccion de Ofertas desde la pantalla principal (Home Hogar).
2. La aplicacion muestra el listado de ofertas disponibles en formato de tarjeta, cada una con titulo, ubicacion, horario y tarifa.
3. Las ofertas publicadas en las ultimas 48 horas muestran una insignia "Nuevo".
4. La trabajadora aplica filtros (zona/codigo postal, horario, rango de fecha de inicio) y/o cambia el criterio de ordenacion (mas recientes, cercania, tarifa mas alta).
5. El listado se actualiza mostrando solo las ofertas que cumplen los filtros seleccionados.
6. Si no hay ofertas que coincidan con los filtros, la aplicacion muestra un estado vacio informativo.

**Estado de exito**: La trabajadora visualiza un listado filtrado y ordenado de ofertas relevantes para su busqueda.
**Flujos alternativos**: Si no hay ofertas disponibles en absoluto, se muestra un estado vacio con mensaje informativo.

### Journey 2: Evaluar una oferta y solicitarla
**Actor**: Trabajadora Hogar | **Objetivo**: Evaluar y solicitar una oferta de interes

1. La trabajadora toca una tarjeta de oferta en el listado.
2. La aplicacion muestra el detalle completo de la oferta.
3. La trabajadora revisa toda la informacion y decide solicitar la oferta.
4. La trabajadora pulsa el boton de solicitar.
5. La aplicacion muestra un dialogo de confirmacion con el resumen de la oferta.
6. La trabajadora confirma la solicitud.
7. La solicitud se envia incluyendo automaticamente los datos del perfil de la trabajadora.
8. La aplicacion muestra un mensaje de exito confirmando que la solicitud fue enviada correctamente.

**Estado de exito**: La solicitud queda registrada con estado "Pendiente" y la trabajadora recibe confirmacion visual inmediata.
**Flujos alternativos**:
- Si la trabajadora ya ha solicitado esta oferta previamente, el boton de solicitar aparece deshabilitado con indicacion de "Ya solicitada".
- Si la trabajadora tiene el perfil incompleto, la solicitud se bloquea mostrando los campos pendientes de completar (ver Asunciones Aplicadas A-001).

### Journey 3: Consultar estado de solicitudes y retirar una solicitud
**Actor**: Trabajadora Hogar | **Objetivo**: Hacer seguimiento de sus solicitudes y retirar alguna si lo desea

1. La trabajadora accede a la seccion "Mis solicitudes".
2. La aplicacion muestra el listado de solicitudes en orden cronologico inverso, cada una con titulo de la oferta, ubicacion, fecha de solicitud y estado.
3. Las solicitudes aceptadas se distinguen visualmente del resto.
4. La trabajadora puede filtrar las solicitudes por estado.
5. La trabajadora toca una solicitud para ver el detalle de la oferta asociada.
6. Si la solicitud esta en estado "Pendiente", la trabajadora tiene la opcion de retirarla.
7. La trabajadora pulsa retirar y confirma la accion.
8. La solicitud desaparece del listado activo o cambia a estado correspondiente.

**Estado de exito**: La trabajadora tiene visibilidad completa del estado de todas sus solicitudes y puede retirar las que estan pendientes.
**Flujos alternativos**: Si la solicitud ya no esta en estado "Pendiente" (ha pasado a "En revision", "Aceptada", etc.), la opcion de retirar no esta disponible.

---

## Resultados y Exito

| Journey | Resultado esperado |
|---------|-------------------|
| Navegar y buscar ofertas | La trabajadora encuentra ofertas relevantes usando filtros y ordenacion, pudiendo evaluar rapidamente cada oportunidad desde la tarjeta |
| Evaluar y solicitar oferta | La solicitud queda registrada correctamente con los datos del perfil de la trabajadora y se muestra confirmacion inmediata |
| Consultar y gestionar solicitudes | La trabajadora conoce el estado actual de todas sus solicitudes y puede retirar las que estan pendientes |

**Exito global de la feature**: La trabajadora Hogar puede encontrar oportunidades de trabajo adecuadas, aplicar a ellas de forma agil, y hacer seguimiento de sus candidaturas hasta su resolucion.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Exclusividad de perfil**: Esta feature es exclusiva del perfil Hogar (CUIDEO). Las trabajadoras SAD no tienen acceso a la seccion de Ofertas.

2. **Formato de tarjeta en listado**: Cada oferta se muestra como tarjeta con cuatro datos visibles: titulo del trabajo, ubicacion (codigo postal o ciudad), horario y tarifa horaria. Adicionalmente, se muestra un boton de solicitar directamente en la tarjeta.

3. **Insignia "Nuevo"**: Las ofertas publicadas en las ultimas 48 horas muestran una insignia "Nuevo" en la tarjeta. La insignia desaparece automaticamente pasadas las 48 horas desde la publicacion.

4. **Filtros disponibles**:
   - Por codigo postal o zona geografica
   - Por horario (manana, tarde, noche, madrugada, 24h)
   - Por rango de fecha de inicio
   - Los filtros son acumulativos (se aplican todos los seleccionados simultaneamente)

5. **Criterios de ordenacion**: Mas recientes (por defecto), ubicacion mas cercana, tarifa mas alta. Solo se aplica un criterio de ordenacion a la vez.

6. **Prevencion de solicitudes duplicadas**: Una trabajadora no puede solicitar la misma oferta mas de una vez. Si ya la ha solicitado, el boton de solicitar aparece deshabilitado con indicacion de "Ya solicitada" tanto en la tarjeta del listado como en el detalle.

7. **Datos automaticos en la solicitud**: La solicitud incluye automaticamente los datos del perfil de la trabajadora. No se solicitan datos adicionales al momento de aplicar.

8. **Estados de solicitud**: Cada solicitud tiene uno de los siguientes estados: Pendiente, En revision, Aceptada, Rechazada, Oferta cerrada. Los estados son asignados por coordinacion desde backoffice; la trabajadora no puede modificar el estado de su solicitud.

9. **Retirada de solicitud**: Solo se permite retirar solicitudes en estado "Pendiente". Una vez la solicitud pasa a "En revision" o cualquier otro estado posterior, la opcion de retirar deja de estar disponible.

10. **Distincion visual de solicitudes aceptadas**: Las solicitudes en estado "Aceptada" se muestran con diferenciacion visual clara (por ejemplo, color o icono distintivo) para que la trabajadora las identifique rapidamente.

11. **Notificaciones por cambio de estado**: Cuando el estado de una solicitud cambia, la trabajadora recibe una notificacion push. La gestion de la entrega de notificaciones es responsabilidad de la feature F-012 (push-notifications); esta feature define unicamente que el evento "cambio de estado de solicitud" es un disparador de notificacion.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home Hogar | Toca acceso directo "Ofertas" | Listado de ofertas disponibles |
| Listado de ofertas | Toca una tarjeta de oferta | Detalle completo de la oferta |
| Listado de ofertas | Toca "Aplicar" en tarjeta | Dialogo de confirmacion de solicitud |
| Detalle de oferta | Toca boton "Aplicar" | Dialogo de confirmacion de solicitud |
| Dialogo de confirmacion | Confirma la solicitud | Mensaje de exito y retorno al listado/detalle |
| Dialogo de confirmacion | Cancela la solicitud | Retorno al detalle de la oferta |
| Tab / Acceso "Mis solicitudes" | Accede a la seccion | Listado de solicitudes presentadas |
| Listado de solicitudes | Toca una solicitud | Detalle de la oferta asociada |
| Detalle de solicitud | Toca "Retirar solicitud" (solo si Pendiente) | Dialogo de confirmacion de retirada |
| Dialogo de retirada | Confirma la retirada | Listado de solicitudes actualizado |

---

## Criterios de Aceptacion

### CA-001: Listado de ofertas en formato tarjeta ← HU-001
GIVEN la trabajadora Hogar accede a la seccion de Ofertas
WHEN se carga el listado de ofertas disponibles
THEN cada oferta se muestra en formato de tarjeta con titulo del trabajo, ubicacion (codigo postal o ciudad), horario, tarifa horaria y boton de solicitar

### CA-002: Insignia de oferta nueva ← HU-001
GIVEN una oferta fue publicada hace menos de 48 horas
WHEN la trabajadora visualiza el listado de ofertas
THEN la tarjeta de esa oferta muestra una insignia "Nuevo"

### CA-003: Filtrado por zona geografica ← HU-001
GIVEN la trabajadora esta en el listado de ofertas
WHEN aplica un filtro por codigo postal o zona
THEN el listado muestra unicamente las ofertas ubicadas en la zona seleccionada

### CA-004: Filtrado por horario ← HU-001
GIVEN la trabajadora esta en el listado de ofertas
WHEN aplica un filtro por horario (manana, tarde, noche, madrugada o 24h)
THEN el listado muestra unicamente las ofertas que coinciden con el horario seleccionado

### CA-005: Filtrado por rango de fecha de inicio ← HU-001
GIVEN la trabajadora esta en el listado de ofertas
WHEN aplica un filtro por rango de fecha de inicio
THEN el listado muestra unicamente las ofertas cuya fecha de inicio esta dentro del rango seleccionado

### CA-006: Ordenacion del listado ← HU-001
GIVEN la trabajadora esta en el listado de ofertas
WHEN selecciona un criterio de ordenacion (mas recientes, ubicacion mas cercana o tarifa mas alta)
THEN el listado se reordena segun el criterio seleccionado

### CA-007: Estado vacio sin ofertas coincidentes ← HU-001
GIVEN la trabajadora ha aplicado filtros en el listado de ofertas
WHEN no hay ninguna oferta que coincida con los filtros seleccionados
THEN la aplicacion muestra un estado vacio informativo indicando que no se encontraron ofertas con esos criterios

### CA-008: Ver detalle completo de una oferta ← HU-002
GIVEN la trabajadora esta en el listado de ofertas
WHEN toca una tarjeta de oferta
THEN la aplicacion muestra el detalle completo de la oferta con toda su informacion

### CA-009: Solicitar oferta con confirmacion ← HU-003
GIVEN la trabajadora esta viendo el detalle de una oferta que no ha solicitado previamente
WHEN pulsa el boton de solicitar
THEN la aplicacion muestra un dialogo de confirmacion con el resumen de la oferta antes de enviar la solicitud

### CA-010: Envio de solicitud con un solo toque ← HU-003
GIVEN la trabajadora esta viendo el dialogo de confirmacion de solicitud
WHEN confirma la solicitud
THEN la solicitud se envia incluyendo automaticamente los datos del perfil de la trabajadora y se muestra un mensaje de exito

### CA-011: Prevencion de solicitudes duplicadas ← HU-003
GIVEN la trabajadora ya ha solicitado una oferta previamente
WHEN visualiza esa oferta en el listado o en su detalle
THEN el boton de solicitar aparece deshabilitado con indicacion de "Ya solicitada"

### CA-012: Listado de solicitudes en orden cronologico inverso ← HU-004
GIVEN la trabajadora accede a la seccion "Mis solicitudes"
WHEN se carga el listado de solicitudes
THEN las solicitudes se muestran en orden cronologico inverso con titulo de la oferta, ubicacion, fecha de solicitud y estado

### CA-013: Estados de solicitud visibles ← HU-004
GIVEN la trabajadora esta viendo el listado de sus solicitudes
WHEN consulta el estado de cada solicitud
THEN cada solicitud muestra uno de los siguientes estados: Pendiente, En revision, Aceptada, Rechazada u Oferta cerrada

### CA-014: Distincion visual de solicitudes aceptadas ← HU-004
GIVEN la trabajadora tiene al menos una solicitud en estado "Aceptada"
WHEN visualiza el listado de solicitudes
THEN las solicitudes aceptadas se muestran con diferenciacion visual clara respecto al resto de estados

### CA-015: Filtrado de solicitudes por estado ← HU-004
GIVEN la trabajadora esta en el listado de solicitudes
WHEN aplica un filtro por estado
THEN el listado muestra unicamente las solicitudes con el estado seleccionado

### CA-016: Ver detalle de oferta desde solicitud ← HU-004
GIVEN la trabajadora esta viendo el listado de solicitudes
WHEN toca una solicitud
THEN la aplicacion muestra el detalle de la oferta asociada a esa solicitud

### CA-017: Retirar solicitud pendiente ← HU-005
GIVEN la trabajadora tiene una solicitud en estado "Pendiente"
WHEN elige la opcion de retirar esa solicitud y confirma la accion
THEN la solicitud se retira y deja de estar activa en el listado

### CA-018: Retirada no disponible para solicitudes no pendientes ← HU-005
GIVEN la trabajadora tiene una solicitud en estado "En revision", "Aceptada", "Rechazada" u "Oferta cerrada"
WHEN consulta el detalle de esa solicitud
THEN la opcion de retirar no esta disponible

### CA-019: Notificacion push por cambio de estado ← HU-006
GIVEN la trabajadora ha solicitado una oferta
WHEN el estado de su solicitud cambia (de Pendiente a En revision, Aceptada, Rechazada u Oferta cerrada)
THEN la trabajadora recibe una notificacion push informandole del cambio de estado

---

## Checklist de Validacion

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos para cada journey
- [x] Edge cases documentados (duplicados, perfil incompleto, sin resultados, retirada no disponible)
- [x] Estados de error definidos (estado vacio, solicitud duplicada bloqueada)
- [x] Ambiguedades resueltas
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- La gestion de las ofertas desde backoffice (creacion, edicion, cierre de ofertas) no es parte de esta feature. Esta feature cubre unicamente la perspectiva de la trabajadora Hogar.
- La entrega de notificaciones push es responsabilidad de F-012 (push-notifications). Esta feature solo define que el cambio de estado de solicitud es un evento que dispara notificacion.
- La gestion del perfil y la logica de completitud de perfil es responsabilidad de F-010 (profile-and-documents). Esta feature referencia la regla de bloqueo por perfil incompleto pero no la implementa.
- El chat o comunicacion con coordinacion sobre una oferta es responsabilidad de F-011 (communication). Esta feature no incluye mensajeria directa.
- Valoraciones o reviews de ofertas/empleadores no estan contemplados (fuera de alcance del MVP segun el PRD).
- Alertas o suscripciones automaticas a ofertas que coincidan con un perfil de busqueda guardado no estan contempladas.

---

## Asunciones Aplicadas

- **[A-001]**: Cuando una trabajadora Hogar intenta solicitar una oferta y su perfil esta incompleto, la solicitud se bloquea y la aplicacion muestra indicacion de los campos pendientes de completar. Esta regla se deriva del discovery (F-010 CA6: "Solo Hogar, al aplicar a una oferta con perfil incompleto, se bloquea con indicacion de campos pendientes") y se aplica como interaccion cross-feature. La logica de evaluacion de completitud del perfil es responsabilidad de F-010.

- **[A-002]**: El orden por defecto del listado de ofertas es "mas recientes" (cronologico inverso por fecha de publicacion). El PRD lista tres criterios de ordenacion sin indicar cual es el predeterminado; se aplica "mas recientes" por ser el mas conservador y habitual en listados de ofertas de empleo.

- **[A-003]**: La insignia "Nuevo" se calcula a partir de la fecha de publicacion de la oferta, usando un umbral de 48 horas. El PRD indica "ofertas publicadas en las ultimas 48h" sin especificar si el calculo es exacto al minuto o al dia; se asume calculo exacto (al momento).

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-04-05 | Generacion inicial via fast-track desde PRD (scope F-007 via discovery) |
