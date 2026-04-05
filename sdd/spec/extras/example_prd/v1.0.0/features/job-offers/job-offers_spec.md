# Spec: Job Offers
> Versión: 1.0 | Fecha: 2026-04-02
> Spec monolítico origen: prd-hogar-sad_spec.md
> Feature ID: F-006

---

## Actores
| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades. Usa la app CUIDEO (identidad visual azul). | Navegar y filtrar ofertas de trabajo, solicitar ofertas, consultar y retirar solicitudes enviadas. |
| Sistema / Backoffice | Equipo de coordinación y administración que gestiona el backend y los datos. | Publicar y gestionar ofertas. No es un actor de la app móvil pero sus acciones generan estados visibles para las trabajadoras. |

---

## Historias de Usuario

### HU-015: Navegar y filtrar ofertas de trabajo (Hogar)
Como trabajadora Hogar / quiero consultar las ofertas disponibles con filtros de zona, horario y fecha / para que pueda encontrar oportunidades de trabajo que se ajusten a mis preferencias.

### HU-016: Solicitar una oferta de trabajo (Hogar)
Como trabajadora Hogar / quiero enviar mi solicitud a una oferta con un solo toque / para que coordinación pueda revisar mi candidatura.

### HU-017: Consultar mis solicitudes de oferta (Hogar)
Como trabajadora Hogar / quiero ver el estado de todas mis solicitudes enviadas / para que pueda hacer seguimiento de mis candidaturas y retirar las que ya no me interesan.

---

## Recorridos de Usuario

### Journey 7: Solicitar una oferta de trabajo (Hogar)
Actor: Trabajadora Hogar | Objetivo: Enviar candidatura a una oferta que le interesa

1. La trabajadora accede al listado de ofertas desde la home.
2. Navega por las ofertas (puede filtrar por zona, horario, rango de fechas; ordenar por recientes, más cercanas o tarifa más alta).
3. La trabajadora toca una oferta para ver los detalles completos.
4. Pulsa el botón "Aplicar".
5. La app muestra un diálogo de confirmación con el resumen de la oferta.
6. La trabajadora confirma con un toque.
7. La solicitud se envía. La app muestra un mensaje de éxito y la trabajadora recibe notificación de confirmación.

Estado de éxito: La solicitud aparece en "Mis solicitudes" con estado "Pendiente". La trabajadora recibe notificación push cuando el estado cambia.

Flujos alternativos:
- Si el perfil de la trabajadora está incompleto al intentar aplicar → la app muestra una advertencia con los campos obligatorios pendientes y acceso directo para completarlos.
- Si la trabajadora ya ha enviado una solicitud a esa oferta → la app impide enviar un duplicado.
- Si no hay ofertas que coincidan con los filtros → se muestra el mensaje "No se han encontrado ofertas con los filtros actuales" con un botón para limpiar filtros (asunción P-011).

---

## Resultados y Éxito

- **Oferta solicitada (Hogar)**: La candidatura aparece en "Mis solicitudes" con estado "Pendiente"; la trabajadora recibe notificación push en cada cambio de estado.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Completitud del perfil (Hogar):**
- Al intentar aplicar a una oferta con perfil incompleto, se muestra una advertencia o bloqueo informando de los campos obligatorios pendientes, con acceso directo a completarlos.
- [P-013 — asunción aplicada]: El porcentaje de completitud computa los campos de Información Personal, Profesional e Idiomas. La foto de perfil suma al porcentaje pero es opcional. El indicador visible en home solo aplica al perfil Hogar.

**Experiencia general:**
- Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse.

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Oferta (detalle) | Pulsa "Aplicar" (perfil completo) | Diálogo de confirmación → Mensaje de éxito |
| Oferta (detalle) | Pulsa "Aplicar" (perfil incompleto — Hogar) | Advertencia con campos pendientes y acceso a completar perfil |

---

## Criterios de Aceptación

### CA-001: Navegar ofertas — lista con filtros ← HU-015
GIVEN la trabajadora Hogar accede a la sección de ofertas
WHEN la lista se carga
THEN se muestran las ofertas disponibles en formato de tarjeta con: título del trabajo, ubicación (código postal/ciudad), horario y tarifa horaria; puede filtrar por zona, horario, rango de fecha de inicio; puede ordenar por más recientes, ubicación más cercana o tarifa más alta.

---

### CA-002: Navegar ofertas — badge "Nuevo" ← HU-015
GIVEN hay ofertas publicadas en las últimas 48 horas
WHEN la trabajadora Hogar ve el listado
THEN esas ofertas muestran la insignia "Nuevo".

---

### CA-003: Navegar ofertas — estado vacío ← HU-015
GIVEN la trabajadora Hogar aplica filtros que no devuelven resultados
WHEN la lista se actualiza
THEN se muestra el mensaje "No se han encontrado ofertas con los filtros actuales" con un botón para limpiar filtros (asunción P-011).

---

### CA-004: Solicitar oferta — confirmación y prevención de duplicados ← HU-016
GIVEN la trabajadora Hogar pulsa "Aplicar" en una oferta
WHEN se muestra el diálogo de confirmación
THEN aparece el resumen de la oferta; al confirmar, la solicitud se envía con un solo toque, se muestra mensaje de éxito y la trabajadora recibe notificación de confirmación. No se puede enviar solicitud duplicada a la misma oferta.

---

### CA-005: Mis solicitudes — lista y estados ← HU-017
GIVEN la trabajadora Hogar accede a "Mis solicitudes"
WHEN la lista se carga
THEN las solicitudes aparecen en orden cronológico inverso con título de la oferta, ubicación, fecha de solicitud y estado (Pendiente, En revisión, Aceptada, Rechazada, Oferta cerrada); puede filtrar por estado; las solicitudes aceptadas tienen distinción visual.

---

### CA-006: Mis solicitudes — retirar solicitud ← HU-017
GIVEN la trabajadora Hogar tiene una solicitud con estado "Pendiente"
WHEN pulsa la opción de retirar solicitud
THEN la solicitud queda retirada y desaparece de las pendientes activas.

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
- Funciones sociales (perfiles públicos, valoraciones entre trabajadoras)
