# Spec: Panel Principal y Contenidos

> Version: 1.0 | Fecha: 2026-04-05
> Spec monolitico origen: prd-hogar-sad_spec.md
> Feature ID: F-002

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades de empleo a traves de la app CUIDEO (tema azul) | Navegar panel principal con accesos directos, consultar comunicados, consultar mensajes del sistema, usar app de marca diferenciada |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios asignados a traves de la app Felizvita (tema verde) | Navegar panel principal con accesos directos priorizando servicios y fichaje, consultar comunicados, consultar mensajes del sistema, usar app de marca diferenciada |
| Coordinadora / Backoffice | Profesional de gestion interna que supervisa a las trabajadoras. No usa la app movil directamente; interactua a traves del sistema de backoffice | Publicar comunicados, fijar comunicados, enviar mensajes del sistema |

---

## Historias de Usuario

### HU-010: Panel principal con accesos directos
Como trabajadora (Hogar o SAD)
quiero ver un panel principal con accesos rapidos a las secciones mas importantes
para que pueda navegar eficientemente a las funcionalidades que mas uso.

### HU-011: Tablon de anuncios y comunicados
Como trabajadora (Hogar o SAD)
quiero consultar los comunicados y contenidos informativos de la empresa
para que este al dia con protocolos, novedades y comunicaciones importantes.

### HU-012: Mensajes del sistema
Como trabajadora (Hogar o SAD)
quiero consultar los mensajes de administracion enviados por el sistema
para que no pierda informacion importante de gestion.

### HU-043: Aplicaciones de marca diferenciada
Como trabajadora (Hogar o SAD)
quiero usar una app con la marca correspondiente a mi perfil (CUIDEO o Felizvita)
para que la experiencia visual sea coherente con el servicio al que pertenezco.

---

## Recorridos de Usuario

Esta feature no tiene un journey dedicado independiente. El panel principal es el punto de llegada de los Journeys 1, 2 y 3 (feature authentication) y el punto de partida para los journeys de todas las demas features. Los comunicados y mensajes del sistema se consultan como flujos secundarios desde el panel principal.

Flujo de consulta de comunicados:
1. La trabajadora accede al panel principal.
2. El bloque "Ultimos avisos" muestra 2-3 items de comunicados recientes.
3. La trabajadora toca "Ultimos avisos" para acceder al tablon completo.
4. Los comunicados fijados aparecen en la parte superior.
5. La trabajadora toca un comunicado para ver el detalle completo con imagenes y adjuntos.
6. El comunicado se marca como leido automaticamente.

Flujo de consulta de mensajes del sistema:
1. La trabajadora accede a la lista de mensajes del sistema.
2. Los mensajes de criticidad alta se muestran primero con diferenciacion visual.
3. La trabajadora toca un mensaje para ver el contenido completo con adjuntos.
4. El mensaje se marca como leido automaticamente. No hay opcion de responder.

---

## Resultados y Exito

- Las trabajadoras acceden al panel principal con accesos rapidos a las funcionalidades mas relevantes segun su perfil (Hogar o SAD).
- Las trabajadoras consultan comunicados y contenidos informativos de la empresa y estan al dia con protocolos y novedades.
- Las trabajadoras consultan mensajes del sistema sin perder informacion importante de gestion.
- Cada app presenta la marca correspondiente al perfil de la trabajadora (CUIDEO azul para Hogar, Felizvita verde para SAD).

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Doble perfil**: Existen dos aplicaciones diferenciadas por marca (CUIDEO tema azul para Hogar, Felizvita tema verde para SAD). Cada app muestra unicamente las funcionalidades correspondientes a su perfil.
- **Home SAD — bloque de servicios**: Muestra como maximo el servicio activo y el siguiente servicio. Si hay mas, se muestra enlace "Ver mas servicios" (no contador "+2" o similar).
- **Mensajes del sistema**: Son de solo lectura, no se pueden responder. Se diferencian en dos niveles de criticidad: alta (se muestran primero y con diferenciacion visual) y normal.
- **Maximo 3 toques**: Cualquier funcionalidad principal es accesible en un maximo de 3 toques desde el panel principal.
- **Idioma inicial**: Solo castellano. La arquitectura soporta multiples idiomas (catalan, ingles, frances preparados para el futuro).
- **Formato de fechas y numeros**: Respeta la configuracion regional del dispositivo.
- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Panel principal (SAD) | Tocar tarjeta de servicio | Detalle del servicio (RF-3.2) |
| Panel principal (SAD) | Tocar llamamiento pendiente | Detalle del llamamiento (RF-3.4) |
| Panel principal (SAD) | Tocar "Ver mas servicios" | Listado de servicios (RF-3.1) |
| Panel principal (SAD) | Tocar "Ultimos avisos" | Tablon de anuncios completo (RF-2.2) |
| Panel principal (Hogar) | Tocar acceso directo Ofertas | Listado de ofertas (RF-6.1) |
| Panel principal (Hogar) | Tocar acceso directo Disponibilidad | Calendario de disponibilidad (RF-7.1) |
| Panel principal (Hogar) | Tocar acceso directo Perfil | Pantalla de perfil (RF-9.1) |
| Panel principal (Hogar) | Tocar acceso directo Comunicacion | Listado de conversaciones (RF-10.2) |
| Home o Perfil | Tocar "Documentos" | Pantalla de documentos unificada (RF-9.3) |

---

## Criterios de Aceptacion

### CA-001: Panel principal Hogar ← HU-010
GIVEN la trabajadora Hogar esta autenticada
WHEN accede al panel principal
THEN ve accesos directos a: Ofertas, Mi Disponibilidad, Perfil, Comunicacion. Se muestra su nombre y foto de perfil en la cabecera

### CA-002: Panel principal SAD ← HU-010
GIVEN la trabajadora SAD esta autenticada
WHEN accede al panel principal
THEN ve los accesos directos priorizando servicio activo y fichaje: Mis Servicios, Fichar, Incidencias, Solicitar Ausencia, Mis Ausencias, Mi Disponibilidad, Documentacion, Perfil, Comunicacion. El bloque "Ultimos avisos" muestra 2-3 items con acceso al listado completo. Se muestra su nombre y foto de perfil en la cabecera

### CA-003: Bloque de servicios en home SAD ← HU-010
GIVEN la trabajadora SAD tiene multiples servicios asignados
WHEN accede al panel principal
THEN el bloque de servicios muestra como maximo el servicio activo y el siguiente servicio. Si hay mas, se muestra el enlace "Ver mas servicios"

### CA-004: Llamamiento pendiente destacado en home SAD ← HU-010
GIVEN existe un llamamiento pendiente de respuesta para la trabajadora SAD
WHEN accede al panel principal
THEN el llamamiento se muestra de forma prominente con indicacion de urgencia y cuenta atras de caducidad. El CTA lleva al detalle del llamamiento (no permite aceptar/rechazar desde la home)

### CA-005: Documentacion pendiente de firma en home SAD ← HU-010
GIVEN hay documentos laborales pendientes de firma para la trabajadora SAD
WHEN accede al panel principal
THEN se muestra un badge/contador destacado para documentacion pendiente de firma como elemento de alta prioridad

### CA-006: Badges en accesos directos ← HU-010
GIVEN la trabajadora esta en el panel principal
WHEN hay mensajes no leidos en Comunicacion o documentos pendientes de firma o llamamientos pendientes de respuesta
THEN el acceso directo correspondiente muestra un badge con el numero de items pendientes

### CA-007: Pull-to-refresh en panel ← HU-010
GIVEN la trabajadora esta en el panel principal
WHEN hace pull-to-refresh
THEN los datos del panel se actualizan con la informacion mas reciente del servidor

### CA-008: Listado de comunicados con fijados ← HU-011
GIVEN la trabajadora accede al tablon de anuncios
WHEN se muestra la lista de comunicados
THEN los comunicados fijados desde backoffice aparecen en la parte superior. Se diferencian contenidos fijos (protocolos, calendario laboral, PRL, documentos de referencia) y comunicaciones variables (recordatorios, campanas, novedades). Cada comunicado muestra titulo, fecha y texto de previsualizacion

### CA-009: Detalle de comunicado ← HU-011
GIVEN la trabajadora esta en el tablon de anuncios
WHEN toca un comunicado
THEN se abre el detalle completo con soporte para imagenes y adjuntos. El comunicado se marca como leido automaticamente

### CA-010: Badge de comunicados no leidos ← HU-011
GIVEN hay comunicados no leidos
WHEN la trabajadora consulta el tablon o la home
THEN se muestra un indicador visual (badge) en el icono de la seccion indicando contenido nuevo

### CA-011: Notificacion push de nuevo comunicado ← HU-011
GIVEN se publica un nuevo comunicado desde backoffice
WHEN la trabajadora tiene notificaciones habilitadas
THEN recibe una notificacion push informando del nuevo comunicado

### CA-012: Lista de mensajes del sistema por criticidad ← HU-012
GIVEN hay mensajes del sistema con diferentes niveles de criticidad
WHEN la trabajadora accede a la lista de mensajes del sistema
THEN los mensajes de criticidad alta se muestran primero con diferenciacion visual clara respecto a los de criticidad normal. Cada mensaje muestra remitente, asunto y fecha con indicador visual para no leidos

### CA-013: Detalle de mensaje del sistema ← HU-012
GIVEN la trabajadora esta en la lista de mensajes del sistema
WHEN toca un mensaje
THEN se abre el contenido completo con soporte para adjuntos. El mensaje se marca como leido automaticamente. No hay opcion de responder

### CA-014: Borrar mensaje del sistema ← HU-012
GIVEN la trabajadora esta en la lista de mensajes del sistema
WHEN elige borrar un mensaje
THEN el mensaje se elimina de su lista

### CA-015: Aplicaciones de marca diferenciada ← HU-043
GIVEN las aplicaciones estan disponibles para descarga
WHEN una trabajadora instala la app correspondiente a su perfil
THEN CUIDEO (Hogar) se presenta con tema azul y solo funcionalidades Hogar; Felizvita (SAD) se presenta con tema verde y solo funcionalidades SAD. Ambas disponibles en iOS y Android

### CA-016: Accesibilidad basica ← HU-043
GIVEN la trabajadora usa la app
WHEN interactua con los elementos de la interfaz
THEN los elementos interactivos tienen tamano adecuado para interaccion tactil, los contrastes de color cumplen nivel adecuado de accesibilidad, los flujos principales son compatibles con lectores de pantalla, y todas las imagenes e iconos tienen texto alternativo

---

## Checklist de Validacion

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [x] Ambiguedades resueltas
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- Funciones sociales (perfiles publicos, valoraciones entre trabajadoras): no incluidas.
- Eventos de analytics personalizados: solo analitica basica automatica; sin eventos personalizados en el MVP.
