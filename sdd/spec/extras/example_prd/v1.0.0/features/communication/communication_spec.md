# Spec: Communication
> Versión: 1.0 | Fecha: 2026-04-02
> Spec monolítico origen: prd-hogar-sad_spec.md
> Feature ID: F-010

---

## Actores
| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades. Usa la app CUIDEO (identidad visual azul). | Iniciar conversaciones con coordinación, enviar mensajes, consultar historial de conversaciones, borrar conversaciones. |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona servicios asignados. Usa la app Felizvita (identidad visual verde). | Iniciar conversaciones con coordinación, enviar mensajes, consultar historial de conversaciones, borrar conversaciones. |
| Sistema / Backoffice | Equipo de coordinación y administración que gestiona el backend y los datos. | Responder mensajes, cerrar conversaciones. No es un actor de la app móvil pero sus acciones generan estados visibles para las trabajadoras. |

---

## Historias de Usuario

### HU-027: Comunicarme con coordinación mediante chat
Como trabajadora (Hogar o SAD) / quiero iniciar conversaciones y enviar mensajes al equipo de coordinación / para que pueda resolver dudas, gestionar incidencias o tratar temas laborales de forma ágil.

### HU-028: Ver mi historial de conversaciones
Como trabajadora (Hogar o SAD) / quiero ver todas mis conversaciones con coordinación, incluyendo las cerradas / para que pueda consultar el historial de comunicaciones previas.

---

## Recorridos de Usuario

### Journey 8: Iniciar una conversación con coordinación
Actor: Trabajadora Hogar o SAD | Objetivo: Contactar con coordinación para tratar un tema laboral

1. La trabajadora accede al módulo de Comunicación.
2. Pulsa el botón de nueva conversación.
3. La app muestra una selección de asuntos predefinidos: Vacaciones/Ausencia, Nómina/Facturación, Sobre un servicio, Documentación, Consulta general, Otros.
4. La trabajadora selecciona el asunto.
5. Opcionalmente, enlaza contexto (selecciona servicio u oferta relacionados).
6. La trabajadora escribe su primer mensaje (obligatorio).
7. La conversación se crea y la trabajadora ve el hilo de chat. La cabecera muestra el asunto seleccionado (y el código de ticket si el backend lo provee).
8. La trabajadora ve la conversación como si fuera con "Coordinación", independientemente del enrutado interno.

Estado de éxito: La conversación aparece en el listado con el último mensaje visible. La trabajadora puede continuar enviando mensajes. Los mensajes se actualizan en tiempo real sin necesidad de recargar.

Flujos alternativos:
- Si la conversación ha sido cerrada por coordinación → la trabajadora puede leer el historial pero no puede enviar nuevos mensajes; se muestra el aviso "Conversación cerrada".

---

## Resultados y Éxito

- **Comunicación efectiva**: Los mensajes enviados a coordinación se entregan y la trabajadora recibe respuesta en la misma conversación. Los mensajes nuevos llegan en tiempo real.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Comunicación:**
- Los mensajes del chat se actualizan en tiempo real sin necesidad de recargar la pantalla.
- Las notificaciones push se entregan incluso cuando la app está en segundo plano o cerrada.
- Al crear una conversación, la trabajadora siempre ve el chat como una conversación con "Coordinación", independientemente del enrutado interno del backoffice.

**Experiencia general:**
- Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse.

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Notificación push | Toca notificación de mensaje nuevo | Hilo de la conversación correspondiente via deeplink |

---

## Criterios de Aceptación

### CA-001: Nueva conversación — asunto predefinido ← HU-027
GIVEN la trabajadora (Hogar o SAD) pulsa "Nueva conversación"
WHEN se muestra la selección de asuntos
THEN puede elegir entre: Vacaciones/Ausencia, Nómina/Facturación, Sobre un servicio, Documentación, Consulta general, Otros; puede enlazar contexto (servicio u oferta relacionados) opcionalmente; debe escribir un primer mensaje para crear la conversación.

---

### CA-002: Hilo de conversación — mensajes en tiempo real ← HU-027
GIVEN la trabajadora tiene una conversación abierta
WHEN coordinación envía un mensaje
THEN el mensaje aparece en el hilo en tiempo real sin necesidad de recargar la pantalla.

---

### CA-003: Hilo de conversación — conversación cerrada ← HU-027 / HU-028
GIVEN una conversación ha sido cerrada por coordinación
WHEN la trabajadora accede al hilo
THEN el campo de entrada está oculto, se muestra el aviso "Conversación cerrada", y puede consultar el historial completo en modo lectura.

---

### CA-004: Listado de conversaciones ← HU-028
GIVEN la trabajadora accede al listado de conversaciones
WHEN la lista se carga
THEN las conversaciones aparecen en orden cronológico inverso (por último mensaje) con asunto, previsualización del último mensaje y marca de tiempo; las conversaciones con mensajes no leídos están diferenciadas visualmente (bold, badge); las conversaciones cerradas tienen indicador diferenciado (etiqueta "Cerrada" o icono de candado).

---

### CA-005: Borrar conversación ← HU-028
GIVEN la trabajadora está en el listado de conversaciones
WHEN selecciona la opción de borrar una conversación
THEN se muestra un diálogo de confirmación; al confirmar, la conversación queda borrada independientemente del estado de lectura de los mensajes (asunción P-012).

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
No se han definido exclusiones explícitas para esta feature.
