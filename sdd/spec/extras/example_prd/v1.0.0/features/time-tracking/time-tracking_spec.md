# Spec: Time Tracking
> Versión: 1.0 | Fecha: 2026-04-02
> Spec monolítico origen: prd-hogar-sad_spec.md
> Feature ID: F-004

---

## Actores
| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona servicios asignados. Usa la app Felizvita (identidad visual verde). | Fichar entrada y salida con geolocalización, consultar historial de fichajes. |
| Sistema / Backoffice | Equipo de coordinación y administración que gestiona el backend y los datos. | Corregir fichajes (no desde la app móvil). No es un actor de la app móvil pero sus acciones generan estados visibles para las trabajadoras. |

---

## Historias de Usuario

### HU-018: Fichar entrada y salida en un servicio (SAD)
Como trabajadora SAD / quiero fichar mi entrada y salida en un servicio con geolocalización / para que quede registro verificado del tiempo que he trabajado.

### HU-033: Consultar historial de fichajes (SAD)
Como trabajadora SAD / quiero ver el registro de mis entradas y salidas agrupado por servicio y día / para que pueda revisar las horas registradas en cada servicio.

---

## Recorridos de Usuario

### Journey 4: Fichar entrada y salida en un servicio (SAD)
Actor: Trabajadora SAD | Objetivo: Registrar inicio y fin de un servicio con geolocalización

1. La trabajadora abre la app cuando está próxima la hora del servicio.
2. El botón de fichaje está habilitado (se activa 30 minutos antes del inicio del servicio).
3. La trabajadora accede al fichaje desde la home, el tab de fichaje o el detalle del servicio.
4. La trabajadora selecciona el servicio de la lista de servicios activos.
5. La trabajadora pulsa "Fichar entrada".
6. La app captura las coordenadas GPS. Si la precisión es baja, muestra una advertencia; espera máximo 2 segundos y permite continuar igualmente.
7. El fichaje se registra. La app muestra un contador de tiempo transcurrido y el botón "Fichar salida".
8. Al finalizar el servicio, la trabajadora pulsa "Fichar salida".
9. La app muestra un diálogo de confirmación.
10. Al confirmar, se registra la salida.

Estado de éxito: Ambos fichajes quedan registrados con coordenadas y hora. La trabajadora ve el tiempo trabajado en el historial de ese servicio.

Flujos alternativos:
- Si el botón está aún deshabilitado → muestra "Disponible en X min" con indicación visual del tiempo restante.
- Si la trabajadora no ficha la salida tras finalizar el servicio → la app muestra un aviso visible (banner o notificación in-app) recordando la acción pendiente; este aviso no bloquea la navegación.
- Si la trabajadora no puede fichar (no asistencia) → puede reportar una incidencia de fichaje directamente desde la pantalla de fichaje.
- La trabajadora también puede solicitar una ausencia desde la pantalla de fichaje.

---

## Resultados y Éxito

- **Servicio gestionado correctamente**: La trabajadora SAD ha fichado entrada y salida con geolocalización; los registros aparecen en el historial con hora, fecha y duración.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Control horario (SAD):**
- El botón de fichaje de entrada se activa 30 minutos antes del inicio del servicio; fuera de esa ventana aparece deshabilitado con indicación visual del tiempo restante.
- El botón de fichaje muestra estados dinámicos según la hora: "Disponible en X min", "Fichar entrada", "Fichada · en servicio", "Fichar salida", "Servicio finalizado".
- No se permite fichaje manual desde la app; las correcciones de fichaje se gestionan desde backoffice.
- Si la trabajadora no ficha la salida tras finalizar el servicio, se muestra un aviso visible (banner o notificación in-app) que recuerda la acción pendiente. Este aviso no bloquea la navegación.
- Múltiples servicios en el mismo día se fichan de forma independiente; no se bloquean entre sí.

**Experiencia general:**
- Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse.

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Home SAD / Tab fichaje / Detalle servicio | Pulsa fichar entrada | Selección de servicio activo → Confirmación de fichaje |
| Pantalla de fichaje | Pulsa "Reportar incidencia de fichaje" | Formulario de incidencia |
| Pantalla de fichaje | Pulsa "Solicitar ausencia" | Formulario de solicitud de ausencia |

---

## Criterios de Aceptación

### CA-001: Fichaje — botón activo solo 30 minutos antes ← HU-018
GIVEN la trabajadora SAD tiene un servicio programado
WHEN consulta el botón de fichaje antes de la ventana de 30 minutos previos al inicio
THEN el botón aparece deshabilitado con indicación visual del tiempo restante ("Disponible en X min").

---

### CA-002: Fichaje — habilitar y estados dinámicos ← HU-018
GIVEN la trabajadora SAD está dentro de la ventana de fichaje (30 minutos antes del inicio del servicio)
WHEN consulta el botón de fichaje
THEN el botón muestra "Fichar entrada" y está habilitado; los estados posibles del botón son: "Disponible en X min", "Fichar entrada", "Fichada · en servicio", "Fichar salida", "Servicio finalizado".

---

### CA-003: Fichaje — captura de geolocalización ← HU-018
GIVEN la trabajadora SAD pulsa "Fichar entrada" o "Fichar salida"
WHEN se ejecuta el fichaje
THEN la app captura las coordenadas GPS del dispositivo en ese momento.

---

### CA-004: Fichaje — advertencia de baja precisión ← HU-018
GIVEN la trabajadora SAD inicia el fichaje y la precisión del GPS es baja
WHEN la app detecta precisión insuficiente
THEN muestra una advertencia; espera máximo 2 segundos y permite continuar igualmente (el fichaje no queda bloqueado por ubicación).

---

### CA-005: Fichaje — confirmación de salida ← HU-018
GIVEN la trabajadora SAD pulsa "Fichar salida"
WHEN se muestra el diálogo de confirmación
THEN la trabajadora debe confirmar la salida; tras confirmar, el fichaje queda registrado.

---

### CA-006: Fichaje — aviso si no se ficha salida ← HU-018
GIVEN la trabajadora SAD ha fichado entrada en un servicio y el servicio ha terminado sin fichar salida
WHEN la trabajadora usa la app
THEN se muestra un aviso visible (banner o notificación in-app) recordando fichar la salida; este aviso no bloquea la navegación ni el acceso al resto de la app.

---

### CA-007: Fichaje — sin bloqueo entre servicios del mismo día ← HU-018
GIVEN la trabajadora SAD tiene dos servicios en el mismo día (mañana y tarde)
WHEN ficha salida del primero
THEN puede fichar entrada del segundo de forma independiente, sin bloqueo entre servicios.

---

### CA-008: Historial de fichajes — agrupado por servicio y día ← HU-033
GIVEN la trabajadora SAD accede al historial de fichajes
WHEN la lista se carga
THEN los registros aparecen agrupados por servicio y por días, con fecha, hora de entrada, hora de salida y duración de cada registro. No se muestran conteos de horas extra ni diferencias respecto a horas contratadas.

---

### CA-009: Historial de fichajes — filtros ← HU-033
GIVEN la trabajadora SAD está en el historial de fichajes
WHEN aplica filtros
THEN puede filtrar por rango de fechas y por servicio.

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

---

## Fuera de Alcance
- Fichaje manual desde la app (las correcciones se gestionan desde backoffice)
- Conteo de horas extra o diferencias respecto a horas contratadas en el historial
