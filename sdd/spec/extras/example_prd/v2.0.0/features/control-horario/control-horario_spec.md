# Spec: Control Horario
> Version: 1.0 | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md
> Feature ID: F-004

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora del Servicio de Asistencia Social | Fichar entrada/salida con geolocalizacion, consultar historial de fichajes, reportar incidencia de fichaje |

---

## Historias de Usuario

### HU-001: Fichar entrada y salida
Como trabajadora SAD
quiero fichar mi entrada y salida del servicio con captura de ubicacion
para que quede registrada mi jornada de forma verificable.

### HU-002: Consultar historial de fichaje
Como trabajadora SAD
quiero ver el historial de mis fichajes por servicio
para que pueda revisar mis registros de tiempo.

---

## Recorridos de Usuario

### Journey 1: Fichar entrada de servicio
Actor: Trabajadora SAD | Objetivo: Registrar el inicio de un servicio
1. La trabajadora recibe notificacion push N minutos antes del inicio del servicio con mensaje personalizado ("Buenos dias [nombre], ya puedes fichar para el servicio del Sr./Sra. [nombre_receptor]").
2. El boton de fichaje de entrada se activa 30 minutos antes del inicio del servicio; fuera de esa ventana aparece deshabilitado con indicacion visual del tiempo restante.
3. La trabajadora accede al fichaje desde el home, el detalle del servicio o el tab de fichaje.
4. Si tiene multiples servicios activos, selecciona el servicio de la lista.
5. La app captura las coordenadas GPS.
6. Si la precision de la ubicacion es baja (<50m), se muestra advertencia; se espera maximo 2 segundos antes de permitir continuar.
7. La trabajadora ficha entrada incluso sin precision optima (no se bloquea por ubicacion).
8. El boton cambia a estado "Fichada - en servicio" y se muestra un contador de tiempo transcurrido.

Estado de exito: La entrada queda registrada con coordenadas GPS y la trabajadora ve el contador de tiempo.
Flujos alternativos:
- Si la trabajadora necesita reportar una incidencia de fichaje (no ha podido ir/fichar), puede hacerlo desde la pantalla de fichaje.
- Si la trabajadora necesita solicitar una ausencia, puede hacerlo desde la pantalla de fichaje.

### Journey 2: Fichar salida de servicio
Actor: Trabajadora SAD | Objetivo: Registrar la finalizacion de un servicio
1. La trabajadora ve el boton "Fichar salida" mientras esta fichada.
2. Pulsa "Fichar salida".
3. La app muestra un dialogo de confirmacion.
4. La trabajadora confirma la salida.
5. La app captura coordenadas GPS al fichar salida.
6. El boton cambia a estado "Servicio finalizado".

Estado de exito: La salida queda registrada con coordenadas GPS y se calculan las horas trabajadas.
Flujos alternativos:
- Si la trabajadora no ficha la salida tras finalizar el servicio, se muestra un warning visible (banner o notificacion in-app) recordando la accion pendiente. Este warning no bloquea la navegacion ni el acceso al resto de la app.

### Journey 3: Consultar historial de fichajes
Actor: Trabajadora SAD | Objetivo: Revisar sus registros de tiempo
1. La trabajadora accede al historial de fichajes.
2. Ve los registros agrupados por servicio y por dias.
3. Cada registro muestra fecha, hora de entrada, hora de salida y duracion.
4. Puede filtrar por rango de fechas.
5. Puede filtrar por servicio.

Estado de exito: La trabajadora consulta sus registros de fichaje organizados.
Flujos alternativos:
- No se muestran conteos de horas extra ni diferencias respecto a las horas contratadas (reservado para gestion interna).

---

## Resultados y Exito

- Cada fichaje queda registrado con coordenadas GPS para verificabilidad.
- La trabajadora puede fichar desde multiples puntos de acceso (home, detalle del servicio, tab de fichaje).
- El historial de fichajes proporciona un registro completo y filtrable.
- No se bloquea el fichaje por problemas de ubicacion; la trazabilidad se mantiene.

---

## Instrucciones Inambiguas

### Reglas de comportamiento
- El fichaje es accesible desde tres puntos: home, detalle del servicio y tab de fichaje.
- No se permite fichaje manual desde la app; las correcciones se gestionan desde backoffice.
- El boton de fichaje de entrada se activa 30 minutos antes del inicio del servicio; fuera de esa ventana aparece deshabilitado con indicacion visual del tiempo restante.
- El boton de fichaje muestra estados dinamicos segun la hora: "Disponible en X min", "Fichar entrada", "Fichada - en servicio", "Fichar salida", "Servicio finalizado".
- Si la precision de la ubicacion es baja (<50m), se muestra advertencia y se espera maximo 2 segundos antes de permitir continuar. Se permite fichar igualmente.
- Si la trabajadora no ficha la salida tras finalizar el servicio, se muestra un warning visible (banner o notificacion in-app) que recuerda la accion pendiente. Este warning no bloquea la navegacion ni el acceso al resto de la app.
- No se bloquean fichajes entre servicios del mismo dia; cada servicio gestiona su inicio/fin de forma independiente.
- La notificacion push de servicio proximo incluye el nombre de la trabajadora y el nombre del receptor del servicio.
- No se muestran al trabajador conteos de horas extra ni diferencias respecto a las horas contratadas.
- Desde la pantalla de fichaje hay opcion de reportar incidencia de fichaje y opcion de solicitar ausencia, para evitar confusion entre ambas.

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home SAD | Tocar "Fichar" | Pantalla de fichaje |
| Detalle servicio | Tocar "Fichar entrada/salida" | Pantalla de fichaje (servicio preseleccionado) |
| Tab fichaje | Seleccionar servicio | Pantalla de fichaje del servicio |
| Pantalla fichaje | Tocar "Reportar incidencia de fichaje" | Formulario de reporte de incidencia (F-005) |
| Pantalla fichaje | Tocar "Solicitar ausencia" | Formulario de solicitud de ausencia (F-008) |
| Pantalla fichaje | Consultar historial | Historial de fichajes |

---

## Criterios de Aceptacion

### CA-001: Accesibilidad del fichaje <- HU-001
GIVEN la trabajadora SAD tiene servicios activos
WHEN necesita fichar
THEN puede acceder al fichaje desde el home, el detalle del servicio y el tab de fichaje.

### CA-002: Seleccion de servicio <- HU-001
GIVEN la trabajadora SAD tiene multiples servicios activos
WHEN accede al fichaje
THEN debe seleccionar el servicio de la lista antes de fichar entrada.

### CA-003: Captura GPS al fichar <- HU-001
GIVEN la trabajadora SAD ficha entrada o salida
WHEN se ejecuta el fichaje
THEN se capturan las coordenadas GPS.

### CA-004: Advertencia de precision baja <- HU-001
GIVEN la trabajadora SAD esta fichando
WHEN la precision de la ubicacion es baja (menor a 50m)
THEN se muestra advertencia y se espera maximo 2 segundos antes de permitir continuar.

### CA-005: Fichaje sin bloqueo por ubicacion <- HU-001
GIVEN la trabajadora SAD esta fichando y la precision no es optima
WHEN confirma el fichaje
THEN se permite fichar igualmente; la trazabilidad de ubicacion se mantiene sin bloquear.

### CA-006: Contador de tiempo <- HU-001
GIVEN la trabajadora SAD ha fichado entrada
WHEN esta en servicio
THEN se muestra un contador de tiempo transcurrido.

### CA-007: Boton fichar salida <- HU-001
GIVEN la trabajadora SAD ha fichado entrada
WHEN ve la pantalla de fichaje
THEN se muestra el boton "Fichar salida".

### CA-008: Confirmacion al fichar salida <- HU-001
GIVEN la trabajadora SAD quiere fichar salida
WHEN pulsa "Fichar salida"
THEN se muestra un dialogo de confirmacion antes de proceder.

### CA-009: Notificacion push de servicio proximo <- HU-001
GIVEN un servicio esta programado para la trabajadora SAD
WHEN faltan N minutos para el inicio (N configurable en servidor)
THEN la trabajadora recibe una notificacion push personalizada: "Buenos dias [nombre], ya puedes fichar para el servicio del Sr./Sra. [nombre_receptor]".

### CA-010: Fichajes independientes por servicio <- HU-001
GIVEN la trabajadora SAD tiene multiples servicios el mismo dia (manana/tarde)
WHEN ficha en uno
THEN no se bloquea el fichaje del otro; cada servicio gestiona su inicio/fin de forma independiente.

### CA-011: Incidencia de fichaje <- HU-001
GIVEN la trabajadora SAD esta en la pantalla de fichaje
WHEN no ha podido ir o fichar
THEN puede reportar una incidencia de fichaje directamente desde la pantalla de fichaje.

### CA-012: Solicitar ausencia desde fichaje <- HU-001
GIVEN la trabajadora SAD esta en la pantalla de fichaje
WHEN necesita solicitar una ausencia
THEN puede acceder a solicitar ausencia desde la misma pantalla para evitar confusion con la incidencia de fichaje.

### CA-013: Sin fichaje manual <- HU-001
GIVEN la trabajadora SAD necesita corregir un fichaje
WHEN busca la opcion en la app
THEN no existe opcion de fichaje manual; las correcciones se gestionan desde backoffice.

### CA-014: Boton activo 30 min antes <- HU-001
GIVEN un servicio esta programado
WHEN faltan mas de 30 minutos para el inicio
THEN el boton de fichaje de entrada aparece deshabilitado con indicacion visual del tiempo restante. Se activa 30 minutos antes del inicio del servicio.

### CA-015: Estados dinamicos del boton <- HU-001
GIVEN la trabajadora SAD ve la pantalla de fichaje
WHEN cambia la hora respecto al servicio
THEN el boton muestra estados dinamicos: "Disponible en X min", "Fichar entrada", "Fichada - en servicio", "Fichar salida", "Servicio finalizado".

### CA-016: Warning de salida pendiente <- HU-001
GIVEN la trabajadora SAD no ficha la salida tras finalizar el servicio
WHEN el servicio deberia haber terminado
THEN se muestra un warning visible (banner o notificacion in-app) recordando la accion pendiente. Este warning no bloquea la navegacion ni el acceso al resto de la app.

### CA-017: Historial agrupado <- HU-002
GIVEN la trabajadora SAD accede al historial de fichajes
WHEN se carga la lista
THEN se muestran los registros agrupados por servicio y por dias.

### CA-018: Detalle de cada registro <- HU-002
GIVEN la trabajadora SAD esta en el historial de fichajes
WHEN ve los registros
THEN cada registro muestra fecha, hora de entrada, hora de salida y duracion.

### CA-019: Filtro por fechas en historial <- HU-002
GIVEN la trabajadora SAD esta en el historial de fichajes
WHEN aplica filtro de fechas
THEN la lista se filtra por el rango indicado.

### CA-020: Filtro por servicio <- HU-002
GIVEN la trabajadora SAD esta en el historial de fichajes
WHEN aplica filtro por servicio
THEN la lista muestra solo los registros del servicio seleccionado.

### CA-021: Sin horas extra visibles <- HU-002
GIVEN la trabajadora SAD consulta el historial de fichajes
WHEN revisa los registros
THEN no se muestran conteos de horas extra ni diferencias respecto a las horas contratadas.

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
- Fichaje manual desde la app (las correcciones se gestionan desde backoffice)
- Deteccion de GPS simulado
- Modo offline con sincronizacion de fichajes
- Conteos de horas extra visibles para la trabajadora
- Calculo de diferencias respecto a horas contratadas

---

## Asunciones Aplicadas
| Gap origen | Asuncion aplicada |
|------------|-------------------|
| [P-006] | La precision GPS "baja" se define como menor a 50 metros, segun indica el PRD; el timeout de espera es de 2 segundos |
