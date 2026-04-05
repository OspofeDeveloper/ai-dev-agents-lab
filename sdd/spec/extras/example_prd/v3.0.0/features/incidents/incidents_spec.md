# Spec: Incidencias

> Version: 1.0 | Fecha: 2026-04-05
> Spec monolitico origen: prd-hogar-sad_spec.md
> Feature ID: F-006

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios asignados a traves de la app Felizvita (tema verde) | Reportar incidencias del servicio o del cliente con descripcion y adjuntos, consultar historial de incidencias con estado y respuestas |
| Coordinadora / Backoffice | Profesional de gestion interna que supervisa a las trabajadoras. No usa la app movil directamente; interactua a traves del sistema de backoffice | Responder incidencias, cambiar estado de incidencias |

---

## Historias de Usuario

### HU-024: Reportar incidencia (SAD)
Como trabajadora SAD
quiero reportar incidencias del servicio o del cliente con descripcion y adjuntos
para que las coordinadoras esten informadas de problemas que requieren atencion.

### HU-025: Historial de incidencias (SAD)
Como trabajadora SAD
quiero ver todas las incidencias que he reportado con su estado y respuestas
para que pueda hacer seguimiento de los problemas comunicados.

---

## Recorridos de Usuario

### Journey 8: Reportar incidencia (SAD)
Actor: Trabajadora SAD | Objetivo: Comunicar un problema ocurrido en el servicio

1. La trabajadora accede al reporte de incidencias desde el detalle del servicio, la pantalla de fichaje o la seccion de incidencias.
2. Selecciona el tipo de incidencia: Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros.
3. Selecciona el servicio relacionado (si aplica).
4. Introduce la descripcion (obligatorio, minimo 20 caracteres).
5. Opcionalmente adjunta fotos (maximo 5, desde camara o galeria) y/o documentos (maximo 3). Las imagenes se optimizan automaticamente antes de enviarse.
6. El sistema muestra el tamano estimado de subida.
7. La trabajadora envia la incidencia.
8. El sistema confirma el envio. La incidencia queda inmediatamente visible para las coordinadoras.

Estado de exito: La incidencia ha sido reportada con toda la informacion necesaria y es visible para coordinacion.

### Journey 14: Consultar historial de incidencias (SAD)
Actor: Trabajadora SAD | Objetivo: Revisar el estado de incidencias reportadas

1. La trabajadora accede a la seccion de incidencias.
2. El sistema muestra la lista de incidencias en orden cronologico inverso con: numero, tipo, fecha y estado (Reportada, En revision, Resuelta, Cerrada).
3. La trabajadora puede filtrar por estado, rango de fechas, o buscar por numero/descripcion.
4. Toca una incidencia para ver el detalle completo y los comentarios/respuestas de las coordinadoras.

Estado de exito: La trabajadora ha consultado el estado de sus incidencias y las respuestas de coordinacion.

---

## Resultados y Exito

- **Incidencias (SAD)**: Las trabajadoras SAD pueden reportar incidencias con toda la informacion relevante y hacer seguimiento de su resolucion.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Incidencias - taxonomia**: Las incidencias son principalmente del servicio o del usuario atendido, no de la propia cuidadora (las ausencias tienen su propio flujo). Excepcion: "Incidencia de fichaje / No asistencia" para problemas operativos directos.
- **Permiso de camara/archivos**: Se solicita solo en el momento en que se necesite (ej: al adjuntar foto a incidencia), no durante el onboarding.
- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.

---

## Criterios de Aceptacion

### CA-001: Reportar incidencia con tipo y adjuntos ← HU-024
GIVEN la trabajadora SAD accede al formulario de incidencia
WHEN selecciona tipo (Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros), servicio relacionado, introduce descripcion (minimo 20 caracteres) y opcionalmente adjunta fotos (max 5) y documentos (max 3)
THEN se muestra el tamano estimado de subida. Las imagenes se optimizan automaticamente. Al enviar, la incidencia queda confirmada e inmediatamente visible para las coordinadoras

### CA-002: Historial de incidencias con filtros ← HU-025
GIVEN la trabajadora SAD accede al historial de incidencias
WHEN se carga la lista
THEN se muestran las incidencias en orden cronologico inverso con: numero, tipo, fecha, estado (Reportada, En revision, Resuelta, Cerrada). Se puede filtrar por estado, rango de fechas, y buscar por numero o descripcion

### CA-003: Detalle de incidencia con respuestas ← HU-025
GIVEN la trabajadora SAD toca una incidencia en el historial
WHEN se abre el detalle
THEN se muestra la informacion completa de la incidencia y los comentarios/respuestas de las coordinadoras

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

- Funcionalidades de backoffice/coordinacion: este spec cubre exclusivamente la experiencia desde la app movil de la trabajadora.
