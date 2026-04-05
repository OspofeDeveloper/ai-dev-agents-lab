# Spec: Llamamientos de Servicio
> Version: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-004 via prd-hogar-sad_discovery.md)
> Feature ID: F-004
> Spec monolitico origen: N/A (features-first via discover)

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD (fijo discontinuo) | Profesional del Servicio de Asistencia Social con contrato fijo discontinuo que recibe ofertas de turnos via llamamientos | Consultar llamamientos recibidos, ver detalle del llamamiento, aceptar llamamiento con firma digital, rechazar llamamiento con motivo y firma digital, consultar historial de llamamientos |
| Coordinacion (backoffice) | Equipo de gestion que administra la asignacion de servicios y llamamientos | Enviar llamamientos a una o varias trabajadoras, configurar tiempo limite de exposicion, desactivar llamamientos aceptados por otra trabajadora (actor externo, no interactua directamente en la app) |

---

## Historias de Usuario

### HU-001: Consultar llamamientos recibidos
Como trabajadora SAD con contrato fijo discontinuo
quiero ver la lista de todos los llamamientos que he recibido con su estado
para que pueda identificar rapidamente cuales requieren mi respuesta y cuales ya estan resueltos

### HU-002: Evaluar un llamamiento pendiente
Como trabajadora SAD con contrato fijo discontinuo
quiero acceder al detalle completo de un llamamiento pendiente con toda la informacion del servicio, ubicacion y urgencia
para que pueda tomar una decision informada sobre si acepto o rechazo el turno

### HU-003: Aceptar un llamamiento
Como trabajadora SAD con contrato fijo discontinuo
quiero aceptar un llamamiento mediante firma digital con un texto legal claro
para que mi aceptacion quede formalizada con validez legal

> **[INCOMPLETO]** — Pendiente de gap(s): [P-002]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-004: Rechazar un llamamiento
Como trabajadora SAD con contrato fijo discontinuo
quiero rechazar un llamamiento indicando el motivo y firmando digitalmente
para que mi decision quede registrada formalmente junto con la razon del rechazo

> **[INCOMPLETO]** — Pendiente de gap(s): [P-002]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-005: Conocer la urgencia y tiempo restante de un llamamiento
Como trabajadora SAD con contrato fijo discontinuo
quiero ver una cuenta atras visible del tiempo que me queda para responder a un llamamiento
para que no se me pase el plazo y pueda priorizar mi respuesta

### HU-006: Ver llamamientos caducados o desactivados
Como trabajadora SAD con contrato fijo discontinuo
quiero ver claramente cuando un llamamiento ha caducado o ha sido aceptado por otra trabajadora
para que no intente responder a un llamamiento que ya no esta disponible

### HU-007: Consultar el historial de llamamientos
Como trabajadora SAD con contrato fijo discontinuo
quiero consultar el historial completo de todos mis llamamientos con su resultado final
para que pueda llevar un registro de mis respuestas pasadas

---

## Recorridos de Usuario

### Journey 1: Recibir y acceder a un llamamiento pendiente
Actor: Trabajadora SAD (fijo discontinuo) | Objetivo: Enterarse de un nuevo llamamiento y acceder a su detalle

1. La trabajadora recibe una notificacion push indicando que tiene un nuevo llamamiento disponible
2. La trabajadora abre la aplicacion (o toca la notificacion) y accede a la pantalla principal (home)
3. En la home, el llamamiento pendiente se muestra de forma prominente con indicacion de urgencia y cuenta atras del tiempo restante
4. La trabajadora toca el elemento del llamamiento en la home para acceder al detalle completo

Estado de exito: La trabajadora esta en la pantalla de detalle del llamamiento con toda la informacion necesaria para tomar una decision
Flujos alternativos:
- Si la trabajadora accede desde el listado de llamamientos en lugar de la home, navega al mismo detalle
- Si el llamamiento ya ha caducado o fue aceptado por otra trabajadora antes de que la trabajadora acceda, se muestra como desactivado/no disponible

### Journey 2: Evaluar y aceptar un llamamiento
Actor: Trabajadora SAD (fijo discontinuo) | Objetivo: Aceptar un turno disponible

1. La trabajadora esta en el detalle del llamamiento y revisa la informacion: codigo de servicio, fecha/hora, ubicacion y nivel de urgencia
2. La trabajadora decide aceptar y pulsa el boton de aceptacion
3. Se muestra un dialogo con el texto legal de aceptacion y un area para firma digital
4. La trabajadora lee el texto legal y firma con el dedo en el area de firma
5. La trabajadora confirma la aceptacion
6. La aplicacion registra la aceptacion con la firma y muestra confirmacion de exito
7. La navegacion se desbloquea y la trabajadora puede volver a la pantalla anterior

Estado de exito: El llamamiento queda registrado como aceptado con firma digital de la trabajadora; el servicio pasa a formar parte de sus servicios asignados
Flujos alternativos:
- Si mientras la trabajadora evaluaba el llamamiento otra trabajadora lo acepto primero, al intentar aceptar se muestra un aviso de que el llamamiento ya no esta disponible

### Journey 3: Evaluar y rechazar un llamamiento
Actor: Trabajadora SAD (fijo discontinuo) | Objetivo: Rechazar un turno indicando el motivo

1. La trabajadora esta en el detalle del llamamiento y revisa la informacion
2. La trabajadora decide rechazar y pulsa el boton de rechazo
3. Se muestra un dialogo con seleccion obligatoria de motivo de rechazo: No disponible, Demasiado lejos, Motivos personales, Otros (con campo de texto obligatorio)
4. La trabajadora selecciona el motivo (y escribe detalle si elige "Otros")
5. Se muestra el texto legal de rechazo y un area para firma digital
6. La trabajadora lee el texto legal, firma con el dedo y confirma el rechazo
7. La aplicacion registra el rechazo con motivo y firma, y muestra confirmacion
8. La navegacion se desbloquea y la trabajadora puede volver a la pantalla anterior

Estado de exito: El llamamiento queda registrado como rechazado con motivo y firma digital de la trabajadora
Flujos alternativos:
- Si la trabajadora pulsa "Otros" como motivo, debe escribir un texto explicativo antes de poder continuar

### Journey 4: Llamamiento caduca o es desactivado
Actor: Trabajadora SAD (fijo discontinuo) | Objetivo: Saber que un llamamiento ya no esta disponible

1. La trabajadora tiene un llamamiento pendiente cuyo tiempo limite ha expirado (o que fue aceptado por otra trabajadora)
2. Al acceder al listado de llamamientos o a la home, el llamamiento se muestra como desactivado/no disponible
3. La trabajadora puede ver la informacion del llamamiento en modo consulta pero no puede aceptar ni rechazar

Estado de exito: La trabajadora entiende que el llamamiento ya no requiere su respuesta y conoce el motivo (caducado o aceptado por otra)
Flujos alternativos:
- Si la trabajadora estaba en el detalle del llamamiento cuando caduca, se muestra un aviso en tiempo real indicando que el llamamiento ya no esta disponible y se desbloquea la navegacion

### Journey 5: Consultar historial de llamamientos
Actor: Trabajadora SAD (fijo discontinuo) | Objetivo: Revisar llamamientos pasados y sus resultados

1. La trabajadora accede a la seccion de historial de servicios
2. Dentro del historial, se muestra la seccion de llamamientos pasados con su resultado final (aceptado, rechazado, caducado, desactivado)
3. La trabajadora puede consultar el detalle de un llamamiento pasado en modo solo lectura

Estado de exito: La trabajadora puede ver el historial completo de todos sus llamamientos con el resultado final de cada uno

---

## Resultados y Exito

La feature se considera exitosa cuando:

1. **Respuesta informada**: la trabajadora puede evaluar cada llamamiento con toda la informacion relevante (servicio, ubicacion, urgencia, tiempo restante) antes de tomar una decision
2. **Formalidad legal**: tanto la aceptacion como el rechazo quedan registrados con firma digital de la trabajadora y texto legal claro
3. **Decision obligatoria**: una vez que la trabajadora accede al detalle de un llamamiento pendiente, no puede salir sin haber aceptado o rechazado (la navegacion hacia atras esta bloqueada)
4. **Competencia justa**: cuando un llamamiento es aceptado por otra trabajadora o caduca, se refleja inmediatamente como no disponible para el resto
5. **Trazabilidad completa**: el historial de llamamientos con resultado final (aceptado, rechazado, caducado, desactivado) esta siempre disponible para consulta

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Bloqueo de navegacion en detalle**: cuando la trabajadora accede al detalle de un llamamiento pendiente, la navegacion hacia atras queda bloqueada. No se muestra boton de retroceso ni se permite gesto de navegacion atras. La unica forma de salir es aceptar o rechazar el llamamiento. Esto aplica solo a llamamientos en estado pendiente; los caducados, desactivados, aceptados o rechazados se muestran en modo consulta sin bloqueo
2. **Competencia multi-trabajadora**: el mismo llamamiento puede enviarse a varias trabajadoras simultaneamente. La primera en aceptar lo recibe y el resto queda desactivado automaticamente. La gestion de envio simultaneo se realiza desde backoffice
3. **Tiempo limite configurable**: el tiempo de exposicion de cada llamamiento es configurable desde backoffice. La cuenta atras se muestra al lado del llamamiento tanto en la home como en el detalle
4. **Caducidad automatica**: cuando el tiempo limite de un llamamiento expira sin respuesta de ninguna trabajadora, el llamamiento pasa automaticamente a estado caducado
5. **Firma digital obligatoria**: tanto la aceptacion como el rechazo requieren firma digital de la trabajadora. La firma se captura en el dialogo de aceptacion/rechazo. Si la trabajadora tiene una firma guardada en su perfil (feature F-010: profile-and-documents), puede reutilizarla; si no, debe firmar en el momento
6. **Motivo de rechazo obligatorio**: al rechazar, la trabajadora debe seleccionar un motivo de la lista predefinida (No disponible, Demasiado lejos, Motivos personales, Otros). Si selecciona "Otros", el campo de texto es obligatorio
7. **Acceso desde home**: el llamamiento pendiente se muestra de forma prominente en la home SAD con indicacion de urgencia y cuenta atras. El elemento en la home lleva al detalle del llamamiento. No se permite aceptar ni rechazar directamente desde la home
8. **Copy legal diferenciado**: el texto de aceptacion y el texto de rechazo deben ser claramente diferentes entre si para evitar confusion. Ambos textos requieren validacion del departamento legal antes de su uso

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home SAD | Tocar elemento de llamamiento pendiente | Detalle del llamamiento (con bloqueo de navegacion) |
| Listado de llamamientos | Tocar llamamiento pendiente | Detalle del llamamiento (con bloqueo de navegacion) |
| Listado de llamamientos | Tocar llamamiento resuelto (aceptado/rechazado/caducado/desactivado) | Detalle del llamamiento (modo consulta, sin bloqueo) |
| Detalle del llamamiento (pendiente) | Aceptar con firma | Confirmacion de aceptacion → pantalla anterior (navegacion desbloqueada) |
| Detalle del llamamiento (pendiente) | Rechazar con motivo y firma | Confirmacion de rechazo → pantalla anterior (navegacion desbloqueada) |
| Historial de servicios | Tocar llamamiento en seccion de historial | Detalle del llamamiento (modo consulta, sin bloqueo) |
| Notificacion push "Llamada de servicio disponible" | Tocar notificacion | Detalle del llamamiento (con bloqueo de navegacion si esta pendiente) |

---

## Criterios de Aceptacion

### CA-001: Listado de llamamientos recibidos ← HU-001
GIVEN la trabajadora SAD con contrato fijo discontinuo accede a la seccion de llamamientos
WHEN se carga la pantalla
THEN se muestra la lista de todos los llamamientos recibidos con su estado (pendiente, aceptada, rechazada, caducada/desactivada)

### CA-002: Informacion basica del llamamiento en listado ← HU-001
GIVEN la trabajadora SAD esta en el listado de llamamientos
WHEN visualiza un llamamiento en la lista
THEN se muestra la informacion basica: codigo de servicio, fecha/hora, ubicacion y nivel de urgencia

### CA-003: Acceso al detalle completo del llamamiento ← HU-002
GIVEN la trabajadora SAD esta en el listado de llamamientos o en la home
WHEN toca un llamamiento pendiente
THEN se abre el detalle completo del llamamiento con toda la informacion del servicio, ubicacion, urgencia y cuenta atras del tiempo restante

### CA-004: Bloqueo de navegacion en detalle de llamamiento pendiente ← HU-002
GIVEN la trabajadora SAD ha accedido al detalle de un llamamiento en estado pendiente
WHEN intenta navegar hacia atras (boton de retroceso o gesto)
THEN la navegacion esta bloqueada y no se permite salir de la pantalla sin aceptar o rechazar

### CA-005: Aceptacion con firma digital ← HU-003
GIVEN la trabajadora SAD esta en el detalle de un llamamiento pendiente
WHEN pulsa el boton de aceptar
THEN se muestra un dialogo con el texto legal de aceptacion y un area de firma digital donde la trabajadora debe firmar con el dedo antes de confirmar

> **[INCOMPLETO]** — Pendiente de gap(s): [P-002]. El texto legal exacto de aceptacion no esta definido. Se genera el CA con la estructura completa pero el contenido del texto legal queda pendiente de validacion por el departamento legal.

### CA-006: Rechazo con motivo obligatorio y firma digital ← HU-004
GIVEN la trabajadora SAD esta en el detalle de un llamamiento pendiente
WHEN pulsa el boton de rechazar
THEN se muestra un dialogo con seleccion obligatoria de motivo (No disponible, Demasiado lejos, Motivos personales, Otros) y, tras seleccionar motivo, se muestra el texto legal de rechazo con area de firma digital

> **[INCOMPLETO]** — Pendiente de gap(s): [P-002]. El texto legal exacto de rechazo no esta definido. Se genera el CA con la estructura completa pero el contenido del texto legal queda pendiente de validacion por el departamento legal.

### CA-007: Campo de texto obligatorio para motivo "Otros" ← HU-004
GIVEN la trabajadora SAD esta rechazando un llamamiento
WHEN selecciona "Otros" como motivo de rechazo
THEN se muestra un campo de texto obligatorio que debe completar antes de poder continuar con la firma y confirmacion del rechazo

### CA-008: Cuenta atras visual en llamamiento pendiente ← HU-005
GIVEN la trabajadora SAD tiene un llamamiento en estado pendiente
WHEN visualiza el llamamiento en la home o en el detalle
THEN se muestra una cuenta atras visual con el tiempo restante antes de que el llamamiento caduque

### CA-009: Llamamiento prominente en home SAD ← HU-005
GIVEN la trabajadora SAD tiene al menos un llamamiento pendiente de respuesta
WHEN accede a la pantalla principal (home)
THEN el llamamiento pendiente se muestra de forma muy visible con indicacion de urgencia y cuenta atras de caducidad, y al tocarlo navega al detalle del llamamiento

### CA-010: Caducidad automatica de llamamientos ← HU-006
GIVEN un llamamiento ha superado el tiempo limite configurado desde backoffice sin que ninguna trabajadora haya respondido
WHEN la trabajadora accede al listado de llamamientos o a la home
THEN el llamamiento se muestra con estado caducado y no permite aceptar ni rechazar

> **[INCOMPLETO]** — Pendiente de gap(s): [P-001]. No esta definido si la caducidad sin respuesta se registra como "rechazo por inaccion" (con implicaciones legales) o simplemente como "caducado sin respuesta". Se genera el CA con el comportamiento visual pero la consecuencia funcional queda pendiente.

### CA-011: Llamamiento desactivado por aceptacion de otra trabajadora ← HU-006
GIVEN un llamamiento fue aceptado por otra trabajadora antes de que la trabajadora actual respondiera
WHEN la trabajadora accede al listado de llamamientos o al detalle
THEN el llamamiento se muestra como desactivado/no disponible y no permite aceptar ni rechazar

### CA-012: Historial completo de llamamientos ← HU-007
GIVEN la trabajadora SAD accede a la seccion de historial de servicios
WHEN visualiza la subseccion de llamamientos
THEN se muestra el historial completo de todos sus llamamientos con su resultado final (aceptado, rechazado, caducado, desactivado)

### CA-013: Reutilizacion de firma guardada ← HU-003, HU-004
GIVEN la trabajadora SAD tiene una firma digital guardada en su perfil
WHEN accede al dialogo de aceptacion o rechazo de un llamamiento
THEN puede reutilizar su firma guardada en lugar de firmar de nuevo, con opcion de redibujar si lo desea

### CA-014: Notificacion push de nuevo llamamiento ← HU-001
GIVEN la trabajadora SAD tiene notificaciones push habilitadas
WHEN se le asigna un nuevo llamamiento desde backoffice
THEN recibe una notificacion push indicando que tiene una nueva llamada de servicio disponible

### CA-015: Desactivacion en tiempo real durante evaluacion ← HU-006
GIVEN la trabajadora SAD esta en el detalle de un llamamiento pendiente (con navegacion bloqueada)
WHEN el llamamiento caduca o es aceptado por otra trabajadora mientras lo esta evaluando
THEN se muestra un aviso indicando que el llamamiento ya no esta disponible, el estado cambia a caducado/desactivado y la navegacion hacia atras se desbloquea

---

## Checklist de Validacion
- [x] Actores identificados (Trabajadora SAD fijo discontinuo, Coordinacion backoffice)
- [x] Flujos principales descritos paso a paso (5 journeys)
- [x] Estados de exito definidos para cada journey
- [x] Edge cases documentados (caducidad durante evaluacion, aceptacion por otra trabajadora, motivo "Otros")
- [x] Estados de error definidos (llamamiento no disponible, caducado, desactivado)
- [x] Ambiguedades resueltas (excepto gaps criticos documentados)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance
- La gestion de envio de llamamientos desde backoffice (la trabajadora solo recibe y responde; el envio es responsabilidad del sistema de coordinacion)
- La logica de planificacion que determina a que trabajadoras se envia cada llamamiento (pertenece al backoffice)
- Los servicios asignados a trabajadoras con contrato indefinido (no son llamamientos; se gestionan en F-003: service-management via RF-3.7)
- La captura y almacenamiento de la firma digital como funcionalidad independiente (pertenece a F-010: profile-and-documents; esta feature solo la utiliza como referencia)
- Las notificaciones push como sistema (pertenecen a F-012: push-notifications; esta feature solo describe que se recibe una notificacion al llegar un nuevo llamamiento)

---

## Items Pendientes

> **Este spec tiene gaps criticos sin resolver. Las HUs afectadas estan marcadas `[INCOMPLETO]` y `/wf-prepare-plan` quedara bloqueado hasta que se resuelvan.**
> Para resolverlos: edita este spec respondiendo los gaps, luego ejecuta `/wf-spec-validate features/service-calls/service-calls_spec.md`.

### [P-001][CRITICO] Caducidad de llamamientos: consecuencia de la inaccion
- **Afecta**: [HU-006, CA-010]
- **Pregunta**: Cuando un llamamiento caduca sin respuesta de la trabajadora, que consecuencia tiene? Se registra como "rechazo por inaccion" (con las implicaciones legales que eso conlleve) o simplemente como "caducado sin respuesta"?
- **Respuesta**: [CRITICO]_(pendiente)_

### [P-002][CRITICO] Copy legal de aceptacion y rechazo de llamamientos
- **Afecta**: [HU-003, HU-004, CA-005, CA-006]
- **Pregunta**: Cuales son los textos legales oficiales que la trabajadora vera al aceptar y al rechazar un llamamiento? Son textos que ha validado el departamento legal?
- **Respuesta**: [CRITICO]_(pendiente)_

---

## Asunciones Aplicadas

- **[A-001]**: Se asume que la firma digital reutilizable del perfil (F-010) esta disponible para esta feature. Si la trabajadora no tiene firma guardada, firma en el momento dentro del dialogo de aceptacion/rechazo. Justificacion: el PRD describe la firma como funcionalidad transversal (RF-9.4) y el discovery asigna FirmaDigital como shared model con owner en F-010.
- **[A-002]**: Se asume que el historial de llamamientos se muestra dentro de la seccion de historial de servicios (F-003) y no como seccion independiente. Justificacion: el PRD (RF-3.5) establece explicitamente que "el historial completo de todos los llamamientos se muestra en esta seccion" refiriendose al historial de servicios. F-004 es owner de la entidad Llamamiento pero la visualizacion del historial se integra en F-003.
- **[A-003]**: Se asume que "urgencia" del llamamiento es un campo informativo que viene definido desde backoffice (no calculado por la app) y se muestra como indicador visual junto a la informacion basica. Justificacion: el PRD menciona "urgencia" como dato a mostrar (RF-3.4 CA2) sin especificar niveles; se trata como campo de solo lectura recibido del servidor.
