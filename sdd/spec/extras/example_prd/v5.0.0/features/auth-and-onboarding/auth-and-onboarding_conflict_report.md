# Conflict Report: Aplicaciones Moviles CUIDEO - Hogar & SAD

> **Generado por**: sdd-analyst (modo conflict)
> **Fecha**: 2026-04-05
> **Specs analizados**: 12 features
> **Spec objetivo**: F-001 auth-and-onboarding
> **Features**: F-001 auth-and-onboarding, F-002 dashboard-and-announcements, F-003 service-management, F-004 service-calls, F-005 time-tracking, F-006 incident-reporting, F-007 job-offers, F-008 absence-management, F-009 availability-management, F-010 profile-and-documents, F-011 communication, F-012 push-notifications

---

## Estado general

> **CONFLICTOS_DETECTADOS**
>
> Se detectaron 5 conflictos entre los 12 specs analizados: 2 de severidad ALTA y 3 de severidad MEDIA. Los conflictos afectan principalmente a la interseccion entre el flujo de onboarding/permisos (F-001), el sistema de notificaciones (F-012), la gestion de incidencias desde multiples features, y la visualizacion de llamamientos en la home.

---

## Resumen de conflictos

| ID | Tipo | Severidad | Features involucradas |
|----|------|:---------:|-----------------------|
| CF-001 | Shared model inconsistente | ALTA | F-001 (auth-and-onboarding), F-012 (push-notifications) |
| CF-002 | HU duplicada | ALTA | F-005 (time-tracking), F-006 (incident-reporting) |
| CF-003 | Scope overlap | MEDIA | F-002 (dashboard-and-announcements), F-004 (service-calls) |
| CF-004 | Scope overlap | MEDIA | F-003 (service-management), F-004 (service-calls) |
| CF-005 | Scope overlap | MEDIA | F-006 (incident-reporting), F-003 (service-management) |

---

## Detalle de conflictos

### [CF-001] Shared model inconsistente — Severidad: ALTA

**Features involucradas**: `F-001 auth-and-onboarding`, `F-012 push-notifications`

**Descripcion**: Ambas features definen el flujo de solicitud de permiso de notificaciones push tras el primer login con reglas de comportamiento potencialmente inconsistentes en cuanto al orden y la descripcion del momento exacto.

**En `F-001 auth-and-onboarding`**:
> Instrucciones Inambiguas, regla 2: "Orden del flujo post-primer-login: login -> solicitud de permiso de notificaciones push -> pantallas de onboarding (con solicitud de permiso de ubicacion) -> home."
> CA-017: "GIVEN la trabajadora ha iniciado sesion por primera vez [...] THEN la app solicita permiso de notificaciones push con una explicacion clara del beneficio **antes de mostrar el onboarding**"

**En `F-012 push-notifications`**:
> Instrucciones Inambiguas, regla 1: "El permiso de notificaciones push se solicita una sola vez, despues del primer inicio de sesion exitoso y **antes de las pantallas de onboarding/bienvenida**."
> CA-001: "GIVEN la trabajadora ha completado su primer inicio de sesion exitoso WHEN la aplicacion va a mostrar las pantallas de onboarding/bienvenida THEN la aplicacion muestra primero una solicitud de permiso de notificaciones push"
> HU-001: "Como trabajadora quiero que la aplicacion me solicite permiso para enviarme notificaciones push despues de mi primer inicio de sesion"

**Por que es un conflicto**: Ambas features definen como propia la regla de comportamiento sobre cuando y como se solicita el permiso de notificaciones. Aunque actualmente son consistentes en el orden (post-login, pre-onboarding), la duplicacion de la definicion en dos specs distintos crea un riesgo de divergencia: si se modifica la regla en uno de los specs sin actualizar el otro, el comportamiento queda indefinido. Ademas, F-012 define HU-001 y CA-001 a CA-003 completamente dedicados a esta solicitud de permiso, mientras que F-001 define CA-017 cubriendo lo mismo. Esto constituye una definicion dual del mismo requisito funcional en dos features.

**Sugerencia de resolucion**: Designar una unica feature como owner de la regla de solicitud de permiso. Lo mas coherente seria que F-001 (auth-and-onboarding) sea owner del **momento y flujo** de la solicitud (ya que es parte del journey de onboarding), y F-012 (push-notifications) se limite a **registrar el dispositivo y gestionar las notificaciones posteriores**. En F-012, reemplazar HU-001 y CA-001 a CA-003 por una referencia explicita a F-001: "La solicitud de permiso de notificaciones se gestiona como parte del onboarding (F-001). Esta feature asume que el permiso ya fue solicitado."

---

### [CF-002] HU duplicada — Severidad: ALTA

**Features involucradas**: `F-005 time-tracking`, `F-006 incident-reporting`

**Descripcion**: Ambas features incluyen el reporte de incidencias de fichaje como funcionalidad propia, con HUs y CAs que describen la misma accion para el mismo actor.

**En `F-005 time-tracking`**:
> HU-004: "Como trabajadora SAD quiero reportar una incidencia de fichaje directamente desde la pantalla de fichaje para que coordinacion sepa que no he podido asistir o fichar y gestione la situacion"
> CA-019: "GIVEN la trabajadora SAD esta en la pantalla de fichaje WHEN pulsa 'Reportar incidencia de fichaje' THEN la aplicacion la redirige al flujo de reporte de incidencias (F-006) con el tipo 'Incidencia de fichaje / No asistencia' preseleccionado"

**En `F-006 incident-reporting`**:
> Instrucciones Inambiguas, regla 2: "La excepcion es el tipo 'Incidencia de fichaje / No asistencia' para problemas operativos directamente relacionados con la prestacion del servicio."
> Journey 1, paso 3: lista "Incidencia de fichaje / No asistencia" como uno de los tipos de incidencia

**Por que es un conflicto**: F-005 tiene una HU completa (HU-004) y un CA (CA-019) dedicados a reportar incidencias de fichaje, pero su CA-019 ya aclara que "redirige al flujo de reporte de incidencias (F-006)". Esto significa que F-005 define el punto de entrada y F-006 define el flujo completo. Sin embargo, tener una HU formalmente definida en F-005 para una accion que es esencialmente una navegacion a F-006 crea duplicacion: el mismo actor (Trabajadora SAD) con el mismo objetivo funcional (reportar incidencia de fichaje) aparece como HU en dos features. Si la HU de F-005 se implementa como algo mas que una redireccion, se generaria implementacion doble.

**Sugerencia de resolucion**: Reclasificar HU-004 de F-005 como un **punto de navegacion** en lugar de una HU formal. El reporte de incidencias de fichaje es funcionalmente propiedad de F-006. En F-005, mantener solo el destino de navegacion en la tabla ("Pantalla de fichaje -> Reportar incidencia -> F-006 con tipo preseleccionado") y un CA que valide la navegacion, pero eliminar la HU-004 como historia independiente. Aplicar el mismo tratamiento a HU-005 de F-005 (solicitar ausencia desde fichaje -> redireccion a F-008).

---

### [CF-003] Scope overlap — Severidad: MEDIA

**Features involucradas**: `F-002 dashboard-and-announcements`, `F-004 service-calls`

**Descripcion**: Ambas features definen como se muestra el llamamiento pendiente en la home SAD con urgencia y cuenta atras, con descripciones que se solapan.

**En `F-002 dashboard-and-announcements`**:
> Journey 2, paso 3: "Si existe un llamamiento pendiente de respuesta, este se muestra de forma muy visible con indicacion de urgencia y cuenta atras de caducidad"
> CA-022: "GIVEN la trabajadora SAD tiene un llamamiento pendiente [...] THEN el llamamiento se muestra de forma muy visible con indicacion de urgencia y cuenta atras de caducidad"
> CA-023: "[...] navega al detalle del llamamiento donde puede aceptar o rechazar"

**En `F-004 service-calls`**:
> CA-009: "GIVEN la trabajadora SAD tiene al menos un llamamiento pendiente de respuesta WHEN accede a la pantalla principal (home) THEN el llamamiento pendiente se muestra de forma muy visible con indicacion de urgencia y cuenta atras de caducidad"
> Instrucciones Inambiguas, regla 7: "Acceso desde home: el llamamiento pendiente se muestra de forma prominente en la home SAD con indicacion de urgencia y cuenta atras."

**Por que es un conflicto**: Ambas features definen CAs y reglas para la presentacion del llamamiento en la home, incluyendo la visualizacion de urgencia y cuenta atras. F-002 lo define como parte del layout de la home; F-004 lo define como parte del comportamiento del llamamiento. Si se modifica la visualizacion en un spec sin actualizar el otro, se tendran dos definiciones divergentes del mismo elemento visual.

**Sugerencia de resolucion**: F-002 (dashboard-and-announcements) deberia ser owner de **como se muestra** el llamamiento en la home (layout, posicion, estilo visual). F-004 (service-calls) deberia ser owner de **que datos** tiene el llamamiento (urgencia, cuenta atras, caducidad). En F-004, eliminar CA-009 y la regla 7, reemplazandolos por una nota: "La visualizacion del llamamiento en la home es responsabilidad de F-002; esta feature define el modelo de datos y el comportamiento del llamamiento."

---

### [CF-004] Scope overlap — Severidad: MEDIA

**Features involucradas**: `F-003 service-management`, `F-004 service-calls`

**Descripcion**: F-003 incluye el historial completo de llamamientos como parte de su seccion de historial de servicios, pero los llamamientos son propiedad de F-004.

**En `F-003 service-management`**:
> Journey 4, paso 6: "Dentro del historial se muestra tambien el historial completo de todos los llamamientos con su resultado final (aceptado, rechazado, caducado, desactivado), referenciando la entidad Llamamiento gestionada por F-004."
> CA-024: "GIVEN la trabajadora SAD accede al historial de servicios WHEN visualiza la seccion THEN se muestra el historial completo de llamamientos con su resultado final"

**En `F-004 service-calls`**:
> Journey 5: "La trabajadora accede a la seccion de historial de servicios [...] se muestra la seccion de llamamientos pasados con su resultado final"
> A-002: "Se asume que el historial de llamamientos se muestra dentro de la seccion de historial de servicios (F-003)"

**Por que es un conflicto**: Ambas features definen journeys y CAs para mostrar el historial de llamamientos. F-003 lo incluye como parte de su historial de servicios y F-004 lo incluye como journey propio (Journey 5). Aunque F-004 reconoce en su asuncion A-002 que la visualizacion se integra en F-003, mantiene un journey completo que solapa con el CA-024 de F-003. Esto puede generar duplicacion de trabajo: dos equipos implementando la misma pantalla de historial de llamamientos.

**Sugerencia de resolucion**: El historial de llamamientos como **visualizacion** deberia ser responsabilidad de F-003 (ya que se muestra dentro de su seccion de historial de servicios). F-004 deberia eliminar Journey 5 o convertirlo en una referencia: "El historial de llamamientos se visualiza dentro del historial de servicios de F-003. F-004 provee los datos de la entidad Llamamiento."

---

### [CF-005] Scope overlap — Severidad: MEDIA

**Features involucradas**: `F-006 incident-reporting`, `F-003 service-management`

**Descripcion**: F-003 incluye el acceso directo a reportar incidencia como parte del detalle de servicio, con un CA propio para esta navegacion, mientras que F-006 define el formulario y el flujo completo.

**En `F-003 service-management`**:
> Instrucciones Inambiguas, regla 6: "Desde el detalle del servicio, la trabajadora puede acceder directamente a: [...] reportar incidencia (F-006)"
> CA-014: "GIVEN la trabajadora SAD esta en el detalle de un servicio WHEN busca reportar una incidencia del servicio THEN encuentra un boton para reportar incidencia accesible desde el propio detalle"
> Destinos de navegacion: "Detalle del servicio -> Toca 'Reportar incidencia' -> Formulario de incidencia (F-006)"

**En `F-006 incident-reporting`**:
> Destinos de navegacion: "Detalle de un servicio (feature service-management) -> Pulsar 'Reportar incidencia' -> Formulario de nueva incidencia con servicio preseleccionado"

**Por que es un conflicto**: Ambas features definen la existencia del punto de entrada "Reportar incidencia" desde el detalle del servicio. F-003 tiene un CA que valida la presencia del boton, y F-006 tiene un destino de navegacion que asume que ese punto de entrada existe. La duplicacion es menor que en CF-002 ya que no hay HU formal duplicada, pero la existencia del CA-014 en F-003 podria generar trabajo redundante si ambos equipos implementan la presencia del mismo boton.

**Sugerencia de resolucion**: F-003 es owner del detalle del servicio y por tanto es razonable que defina que botones/accesos existen en esa pantalla. F-006 deberia confiar en que F-003 provee el punto de entrada y no redefinirlo. El solapamiento actual es manejable como esta, pero se recomienda documentar explicitamente que CA-014 de F-003 es el CA canonico para la existencia del boton, y que F-006 comienza su flujo una vez la trabajadora llega al formulario.

---

## Inventario de comparaciones realizadas

> Esta seccion garantiza trazabilidad de que se comparo contra que.

| Check | Features comparadas | Conflictos encontrados |
|-------|---------------------|:---------------------:|
| HUs duplicadas | Todos los pares (66 pares) | 1 (CF-002) |
| CAs contradictorios | Todos los pares (66 pares) | 0 |
| Scope overlap | Todos los pares (66 pares) | 3 (CF-003, CF-004, CF-005) |
| Shared models inconsistentes | Todos los specs (12) vs tabla _features.md | 1 (CF-001) |
| Fuera de alcance contradictorio | Todos los pares (66 pares) | 0 |

### Notas sobre checks sin conflictos

**CAs contradictorios**: No se encontraron CAs con GIVEN+WHEN equivalentes y THENs incompatibles entre features distintas. Los CAs de features diferentes que comparten precondiciones similares (ej: "trabajadora en la home") producen resultados complementarios, no contradictorios.

**Fuera de alcance contradictorio**: Las secciones de fuera de alcance son consistentes entre si. Las exclusiones de cada feature referencian correctamente a la feature responsable. Ejemplos verificados:
- F-001 excluye "Perfil de la trabajadora" y referencia F-010 correctamente
- F-001 excluye "Notificaciones push (recepcion)" y referencia F-012 correctamente
- F-003 excluye "Llamamientos (ciclo aceptar/rechazar)" y referencia F-004 correctamente
- F-006 excluye "Notificaciones push de cambio de estado" y referencia F-012 correctamente
- F-005 excluye "Gestion de incidencias" y referencia F-006 correctamente

**Shared models**: La tabla de shared models en `_features.md` es consistente con las referencias en los specs. Todos los modelos referenciados en cada spec estan declarados en la tabla con su owner correcto. No se encontraron modelos "huerfanos" (referenciados en un spec pero sin owner declarado).

---

## Proximos pasos

1. Revisar cada conflicto de severidad **ALTA** (CF-001, CF-002) — deben resolverse antes de iniciar `/wf-prepare-plan` en las features afectadas (F-001, F-005, F-006, F-012)
2. Los conflictos de severidad **MEDIA** (CF-003, CF-004, CF-005) pueden documentarse como decisiones de diseno y resolverse en la fase de implementacion, aunque se recomienda resolverlos para evitar trabajo duplicado
3. Para cada conflicto resuelto: editar los specs afectados y re-ejecutar `/wf-spec-conflict` para verificar que se elimino
