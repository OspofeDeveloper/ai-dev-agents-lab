# Spec: Control Horario (Fichaje y Seguimiento de Tiempo)
> Version: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-005 via prd-hogar-sad_discovery.md)
> Feature ID: F-005
> Spec monolitico origen: N/A (features-first via discover)

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Profesional contratada del Servicio de Asistencia Social (Felizvita) que gestiona servicios asignados | Fichar entrada y salida en cada servicio, consultar historial de fichajes, reportar incidencia de fichaje, solicitar ausencia desde la pantalla de fichaje |

---

## Historias de Usuario

### HU-001: Fichar entrada en un servicio
Como trabajadora SAD
quiero fichar mi entrada al comenzar un servicio asignado
para que quede registrado oficialmente el inicio de mi jornada en ese servicio con la ubicacion donde me encuentro

### HU-002: Fichar salida de un servicio
Como trabajadora SAD
quiero fichar mi salida al finalizar un servicio
para que quede registrado oficialmente el fin de mi jornada en ese servicio y se calcule la duracion trabajada

### HU-003: Consultar historial de fichajes
Como trabajadora SAD
quiero consultar mi historial de fichajes agrupado por servicio y por dias
para que pueda revisar mis horas trabajadas y verificar que los registros son correctos

### HU-004: Reportar incidencia de fichaje
Como trabajadora SAD
quiero reportar una incidencia de fichaje directamente desde la pantalla de fichaje
para que coordinacion sepa que no he podido asistir o fichar y gestione la situacion

### HU-005: Solicitar ausencia desde fichaje
Como trabajadora SAD
quiero solicitar una ausencia directamente desde la pantalla de fichaje
para que pueda distinguir claramente entre una incidencia operativa (no he podido fichar) y una ausencia planificada o sobrevenida

---

## Recorridos de Usuario

### Journey 1: Fichar entrada en un servicio activo
Actor: Trabajadora SAD | Objetivo: Registrar el inicio de su jornada en un servicio

1. La trabajadora accede a la funcionalidad de fichaje desde la home, el detalle del servicio o el tab de fichaje
2. Si tiene mas de un servicio activo, selecciona el servicio de la lista de servicios activos del dia
3. El boton de fichaje muestra el estado "Fichar entrada" (se activa 30 minutos antes del inicio del servicio; antes de esa ventana aparece deshabilitado con indicacion del tiempo restante)
4. La trabajadora pulsa "Fichar entrada"
5. La aplicacion captura las coordenadas de ubicacion de la trabajadora
6. Si la precision de la ubicacion es baja, la aplicacion muestra una advertencia visual informando de la baja precision, espera brevemente, y permite continuar con el fichaje igualmente
7. La entrada queda registrada y el boton cambia a estado "Fichada - en servicio"
8. Se muestra un contador de tiempo transcurrido desde el fichaje de entrada

Estado de exito: La trabajadora ha fichado su entrada, ve el estado "Fichada - en servicio" con el contador de tiempo activo, y su ubicacion ha quedado registrada junto al fichaje.

Flujos alternativos:
- Si la trabajadora intenta fichar fuera de la ventana de 30 minutos antes del servicio -> el boton aparece deshabilitado con el texto "Disponible en X min"
- Si la trabajadora pierde la conexion durante el fichaje -> se muestra un mensaje de error indicando la falta de conexion y se le pide que lo reintente manualmente cuando tenga conexion
- Si la trabajadora tiene servicios de manana y tarde el mismo dia -> cada servicio gestiona su fichaje de forma independiente, sin bloquear el fichaje del otro

### Journey 2: Fichar salida de un servicio
Actor: Trabajadora SAD | Objetivo: Registrar el fin de su jornada en un servicio

1. La trabajadora tiene un fichaje de entrada activo y el boton muestra "Fichar salida"
2. La trabajadora pulsa "Fichar salida"
3. La aplicacion muestra un dialogo de confirmacion para evitar fichajes de salida accidentales
4. La trabajadora confirma la salida
5. La aplicacion captura las coordenadas de ubicacion de la trabajadora
6. La salida queda registrada y el boton cambia a estado "Servicio finalizado"

Estado de exito: La trabajadora ha fichado su salida, la duracion de la jornada se ha calculado, y el estado del servicio se muestra como "Servicio finalizado".

Flujos alternativos:
- Si la trabajadora cancela el dialogo de confirmacion -> permanece en estado "Fichada - en servicio" sin registrar salida
- Si la trabajadora no ficha la salida tras finalizar el servicio -> se muestra un warning visible (banner o notificacion in-app) que recuerda la accion pendiente; este warning no bloquea la navegacion ni el acceso al resto de la app

### Journey 3: Consultar historial de fichajes
Actor: Trabajadora SAD | Objetivo: Revisar sus registros de tiempo trabajado

1. La trabajadora accede a la seccion de historial de fichajes
2. Los registros se muestran agrupados por servicio y por dias
3. Cada registro muestra: fecha, hora de entrada, hora de salida y duracion
4. La trabajadora puede filtrar los registros por rango de fechas
5. La trabajadora puede filtrar los registros por servicio

Estado de exito: La trabajadora visualiza sus fichajes filtrados segun sus criterios, con la informacion de fecha, hora de entrada, hora de salida y duracion claramente visible para cada registro.

Flujos alternativos:
- Si no hay fichajes para los filtros aplicados -> se muestra un estado vacio con mensaje informativo

### Journey 4: Reportar incidencia o solicitar ausencia desde fichaje
Actor: Trabajadora SAD | Objetivo: Comunicar a coordinacion una incidencia de fichaje o solicitar una ausencia

1. La trabajadora accede a la pantalla de fichaje
2. La trabajadora ve las opciones "Reportar incidencia de fichaje" y "Solicitar ausencia" claramente diferenciadas
3. Si elige reportar incidencia -> la aplicacion la redirige al flujo de reporte de incidencias con el tipo "Incidencia de fichaje / No asistencia" preseleccionado
4. Si elige solicitar ausencia -> la aplicacion la redirige al flujo de solicitud de ausencia

Estado de exito: La trabajadora ha iniciado el flujo correcto (incidencia o ausencia) desde la pantalla de fichaje, evitando confusion entre ambos conceptos.

---

## Resultados y Exito

El control horario se considera exitoso cuando:
- Cada fichaje de entrada y salida queda registrado con la ubicacion de la trabajadora capturada automaticamente
- La trabajadora puede consultar su historial completo de fichajes con datos claros de fecha, hora y duracion
- Los estados del boton de fichaje reflejan en todo momento la situacion real (tiempo restante, disponible, fichada, salida pendiente, finalizado)
- La trabajadora nunca queda bloqueada por problemas de precision de ubicacion: el fichaje siempre se permite aunque la precision sea baja
- No se muestran conteos de horas extra ni diferencias respecto a las horas contratadas; esta informacion queda reservada para gestion interna
- No se permite fichaje manual desde la app; las correcciones de fichaje se gestionan exclusivamente desde backoffice

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Puntos de acceso al fichaje**: La accion de fichar es accesible desde tres puntos: la pantalla principal (home), el detalle del servicio y el tab de fichaje. Los tres puntos llevan al mismo flujo de fichaje.

2. **Seleccion de servicio**: Antes de fichar entrada, la trabajadora debe seleccionar el servicio de la lista de servicios activos del dia. Si solo tiene un servicio activo, ese servicio se preselecciona automaticamente.

3. **Ventana de fichaje de entrada**: El boton de fichaje de entrada se activa 30 minutos antes del inicio programado del servicio. Fuera de esa ventana, el boton aparece deshabilitado con indicacion visual del tiempo restante.

4. **Notificacion previa al fichaje**: El sistema envia una notificacion push antes del inicio del servicio (el tiempo de antelacion es configurable desde backoffice). El mensaje de la notificacion incluye el nombre de la trabajadora y el nombre del receptor del servicio (ejemplo: "Buenos dias [nombre], ya puedes fichar para el servicio del Sr./Sra. [nombre_receptor]").

5. **Estados dinamicos del boton de fichaje**: El boton muestra estados segun la situacion temporal:
   - "Disponible en X min" — antes de la ventana de 30 minutos
   - "Fichar entrada" — dentro de la ventana de fichaje, sin fichaje activo
   - "Fichada - en servicio" — tras fichar entrada, con contador de tiempo transcurrido
   - "Fichar salida" — para finalizar el servicio (visible junto al estado "Fichada")
   - "Servicio finalizado" — tras fichar salida

6. **Captura de ubicacion**: La ubicacion se captura automaticamente al fichar entrada y al fichar salida. Si la precision de la ubicacion es baja, se muestra una advertencia visual informativa. Tras un breve periodo de espera, se permite continuar con el fichaje igualmente. La baja precision nunca bloquea el fichaje.

7. **Confirmacion de salida**: Al fichar salida se muestra siempre un dialogo de confirmacion para prevenir fichajes accidentales.

8. **Warning de salida pendiente**: Si la trabajadora no ficha la salida tras la hora de fin programada del servicio, se muestra un warning visible (banner o notificacion in-app). Este warning no bloquea la navegacion ni el acceso al resto de la aplicacion.

9. **Independencia entre servicios del mismo dia**: Si la trabajadora tiene multiples servicios en el mismo dia (por ejemplo manana y tarde), el fichaje de cada servicio se gestiona de forma independiente. Fichar salida del servicio de manana no afecta al fichaje del servicio de tarde.

10. **Prohibicion de fichaje manual**: No se permite fichaje manual desde la aplicacion de la trabajadora. Cualquier correccion de fichaje (fichaje olvidado, error de hora) se gestiona internamente desde backoffice.

11. **Restriccion de informacion en historial**: El historial de fichajes no muestra conteos de horas extra ni diferencias respecto a las horas contratadas. Esta informacion queda reservada para gestion interna.

12. **Comportamiento sin conexion**: Si la trabajadora pierde la conexion durante un fichaje, se muestra un mensaje de error indicando la falta de conexion y se le pide que lo reintente manualmente cuando tenga conexion. No hay cola de reintentos automaticos.

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home SAD | Pulsar acceso directo de fichaje | Pantalla de fichaje con servicio activo preseleccionado (si solo hay uno) |
| Detalle del servicio | Pulsar boton de fichar | Pantalla de fichaje con ese servicio preseleccionado |
| Tab de fichaje | Acceder via tab de navegacion inferior | Pantalla de fichaje |
| Pantalla de fichaje | Pulsar "Reportar incidencia de fichaje" | Flujo de reporte de incidencias (F-006) con tipo "Incidencia de fichaje / No asistencia" preseleccionado |
| Pantalla de fichaje | Pulsar "Solicitar ausencia" | Flujo de solicitud de ausencia (F-008) |
| Notificacion push de servicio proximo | Tocar la notificacion | Pantalla de fichaje con el servicio correspondiente preseleccionado |

---

## Criterios de Aceptacion

### CA-001: Fichaje de entrada desde home ← HU-001
GIVEN la trabajadora SAD tiene un servicio activo y esta dentro de la ventana de 30 minutos antes del inicio
WHEN pulsa el acceso directo de fichaje en la home y selecciona el servicio (o este se preselecciona si es el unico)
THEN la aplicacion captura su ubicacion, registra la entrada y el boton cambia a estado "Fichada - en servicio" con contador de tiempo activo

### CA-002: Fichaje de entrada desde detalle del servicio ← HU-001
GIVEN la trabajadora SAD esta en el detalle de un servicio activo y dentro de la ventana de fichaje
WHEN pulsa el boton de fichar entrada
THEN la aplicacion captura su ubicacion, registra la entrada y el boton cambia a estado "Fichada - en servicio"

### CA-003: Boton deshabilitado fuera de ventana de fichaje ← HU-001
GIVEN la trabajadora SAD tiene un servicio programado pero faltan mas de 30 minutos para su inicio
WHEN accede a la pantalla de fichaje
THEN el boton aparece deshabilitado y muestra "Disponible en X min" con la indicacion del tiempo restante

### CA-004: Advertencia de baja precision de ubicacion sin bloqueo ← HU-001
GIVEN la trabajadora SAD intenta fichar entrada o salida
WHEN la precision de su ubicacion no alcanza el umbral minimo aceptable
THEN la aplicacion muestra una advertencia de baja precision y, tras un breve periodo de espera, permite continuar con el fichaje igualmente

### CA-005: Fichaje permitido sin precision optima ← HU-001
GIVEN la trabajadora SAD ha recibido la advertencia de baja precision de ubicacion
WHEN decide continuar con el fichaje
THEN la entrada o salida se registra correctamente con la ubicacion disponible, sin bloquear la operacion

### CA-006: Contador de tiempo tras fichar entrada ← HU-001
GIVEN la trabajadora SAD ha fichado entrada en un servicio
WHEN permanece en la pantalla de fichaje o vuelve a ella
THEN se muestra un contador de tiempo transcurrido desde el momento del fichaje de entrada

### CA-007: Confirmacion al fichar salida ← HU-002
GIVEN la trabajadora SAD tiene un fichaje de entrada activo
WHEN pulsa "Fichar salida"
THEN la aplicacion muestra un dialogo de confirmacion antes de registrar la salida

### CA-008: Registro de salida tras confirmacion ← HU-002
GIVEN la trabajadora SAD ha pulsado "Fichar salida" y el dialogo de confirmacion esta visible
WHEN confirma la accion
THEN la aplicacion captura su ubicacion, registra la salida, y el boton cambia a estado "Servicio finalizado"

### CA-009: Cancelacion de fichaje de salida ← HU-002
GIVEN la trabajadora SAD ha pulsado "Fichar salida" y el dialogo de confirmacion esta visible
WHEN cancela la accion
THEN permanece en estado "Fichada - en servicio" sin registrar la salida

### CA-010: Warning de salida pendiente ← HU-002
GIVEN la trabajadora SAD ha fichado entrada pero no ha fichado salida tras la hora de fin del servicio
WHEN navega por la aplicacion
THEN se muestra un warning visible (banner o notificacion in-app) que recuerda fichar la salida, sin bloquear la navegacion ni el acceso al resto de la app

### CA-011: Estados dinamicos del boton de fichaje ← HU-001, HU-002
GIVEN la trabajadora SAD accede a la pantalla de fichaje de un servicio
WHEN consulta el boton de fichaje en diferentes momentos del dia
THEN el boton muestra el estado correspondiente: "Disponible en X min" (antes de la ventana), "Fichar entrada" (dentro de la ventana), "Fichada - en servicio" (tras fichar entrada), "Fichar salida" (para finalizar), "Servicio finalizado" (tras fichar salida)

### CA-012: Notificacion previa al fichaje ← HU-001
GIVEN la trabajadora SAD tiene un servicio programado
WHEN se alcanza el momento configurado de antelacion al servicio (configurable desde backoffice)
THEN el sistema envia una notificacion push con el mensaje "Buenos dias [nombre], ya puedes fichar para el servicio del Sr./Sra. [nombre_receptor]" y al tocarla se abre la pantalla de fichaje con el servicio correspondiente preseleccionado

### CA-013: Independencia de fichajes entre servicios del mismo dia ← HU-001, HU-002
GIVEN la trabajadora SAD tiene dos servicios el mismo dia (por ejemplo manana y tarde)
WHEN ficha entrada y salida del primer servicio
THEN el fichaje del segundo servicio no se ve afectado y puede ficharse de forma independiente

### CA-014: Prohibicion de fichaje manual ← HU-001, HU-002
GIVEN la trabajadora SAD quiere corregir un fichaje incorrecto o registrar uno olvidado
WHEN busca en la aplicacion la opcion de fichaje manual
THEN no existe ninguna opcion de fichaje manual; las correcciones se gestionan exclusivamente desde backoffice

### CA-015: Historial agrupado por servicio y dias ← HU-003
GIVEN la trabajadora SAD accede a la seccion de historial de fichajes
WHEN se muestran los registros
THEN aparecen agrupados por servicio y por dias, mostrando fecha, hora de entrada, hora de salida y duracion de cada registro

### CA-016: Filtro por rango de fechas en historial ← HU-003
GIVEN la trabajadora SAD esta en el historial de fichajes
WHEN aplica un filtro por rango de fechas
THEN solo se muestran los registros que caen dentro del rango seleccionado

### CA-017: Filtro por servicio en historial ← HU-003
GIVEN la trabajadora SAD esta en el historial de fichajes
WHEN aplica un filtro por servicio
THEN solo se muestran los registros correspondientes a ese servicio

### CA-018: Ocultacion de horas extra en historial ← HU-003
GIVEN la trabajadora SAD consulta el historial de fichajes
WHEN revisa los registros y totales
THEN no se muestran conteos de horas extra ni diferencias respecto a las horas contratadas

### CA-019: Reportar incidencia desde pantalla de fichaje ← HU-004
GIVEN la trabajadora SAD esta en la pantalla de fichaje
WHEN pulsa la opcion "Reportar incidencia de fichaje"
THEN la aplicacion la redirige al flujo de reporte de incidencias (F-006) con el tipo "Incidencia de fichaje / No asistencia" preseleccionado

### CA-020: Solicitar ausencia desde pantalla de fichaje ← HU-005
GIVEN la trabajadora SAD esta en la pantalla de fichaje
WHEN pulsa la opcion "Solicitar ausencia"
THEN la aplicacion la redirige al flujo de solicitud de ausencia (F-008)

### CA-021: Seleccion de servicio antes de fichar ← HU-001
GIVEN la trabajadora SAD tiene multiples servicios activos en el dia
WHEN accede a la pantalla de fichaje
THEN debe seleccionar el servicio de la lista de servicios activos antes de poder fichar entrada

### CA-022: Comportamiento sin conexion al fichar ← HU-001, HU-002
GIVEN la trabajadora SAD intenta fichar entrada o salida
WHEN no tiene conexion a internet
THEN la aplicacion muestra un mensaje de error indicando la falta de conexion y le pide que reintente manualmente cuando tenga conexion

---

## Checklist de Validacion
- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados (baja precision de ubicacion, sin conexion, multiples servicios mismo dia, salida no fichada)
- [x] Estados de error definidos (sin conexion, fuera de ventana de fichaje)
- [x] Ambiguedades resueltas (baja precision de ubicacion no bloquea, fichaje manual no permitido, horas extra no visibles)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance
- Fichaje manual desde la aplicacion de la trabajadora (las correcciones se gestionan desde backoffice)
- Visualizacion de horas extra o diferencias respecto a horas contratadas (reservado para gestion interna)
- Deteccion de ubicacion simulada (listado como fase futura en el PRD)
- Modo offline con sincronizacion automatica de fichajes (listado como fase futura en el PRD; si no hay conexion, la trabajadora debe reintentar manualmente)
- Gestion del contenido o logica interna de incidencias (pertenece a F-006: incident-reporting)
- Gestion del contenido o logica interna de ausencias (pertenece a F-008: absence-management)
- Calculo o visualizacion del cumplimiento horario del contrato

---

## Asunciones Aplicadas

- **[A-001]**: Cuando la trabajadora pierde la conexion a internet durante un fichaje, se muestra un mensaje de error y se le pide que reintente manualmente. No hay cola de reintentos automaticos ni sincronizacion offline (el modo offline con sincronizacion esta explicitamente fuera de alcance en el PRD). Origen: [P-014][INFORMATIVO] del analysis.
- **[A-002]**: Los elementos de la home SAD (incluyendo el acceso directo de fichaje) se muestran siempre en el orden listado en el PRD. El acceso de fichaje esta siempre visible pero se habilita/deshabilita segun si hay servicio activo. Origen: [P-017][INFORMATIVO] del analysis.
- **[A-003]**: El umbral de "baja precision de ubicacion" y el tiempo de espera antes de permitir continuar son parametros que se definiran en el Plan. En el spec, la regla funcional es: advertencia informativa + permitir continuar siempre. No se bloquea el fichaje por precision insuficiente.

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-04-05 | Generacion inicial via fast-track desde PRD (scope F-005 via discovery) |
