# Spec: Ofertas de Trabajo

> Version: 1.0 | Fecha: 2026-04-05
> Spec monolitico origen: prd-hogar-sad_spec.md
> Feature ID: F-008

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades de empleo a traves de la app CUIDEO (tema azul) | Navegar ofertas de trabajo con filtros, ver detalle de oferta, solicitar oferta, consultar estado de solicitudes, completar perfil antes de aplicar |
| Coordinadora / Backoffice | Profesional de gestion interna que supervisa a las trabajadoras. No usa la app movil directamente; interactua a traves del sistema de backoffice | Publicar ofertas, cambiar estado de solicitudes |

---

## Historias de Usuario

### HU-028: Navegar ofertas de trabajo (Hogar)
Como trabajadora Hogar
quiero consultar las ofertas de trabajo disponibles con filtros
para que pueda encontrar oportunidades de empleo que se ajusten a mi zona y horario.

### HU-037: Solicitar oferta de trabajo (Hogar)
Como trabajadora Hogar
quiero solicitar una oferta de trabajo desde la app
para que mi candidatura sea enviada a las coordinadoras para su revision.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-008]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-038: Mis solicitudes (Hogar)
Como trabajadora Hogar
quiero ver todas las solicitudes que he presentado con su estado
para que pueda hacer seguimiento de mis candidaturas y saber si han sido aceptadas o rechazadas.

### HU-044: Completar perfil antes de aplicar (Hogar)
Como trabajadora Hogar
quiero ser informada de los campos obligatorios pendientes al intentar aplicar a una oferta
para que pueda completar mi perfil y no perder oportunidades por tener datos incompletos.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-008]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

---

## Recorridos de Usuario

### Journey 10: Navegar y solicitar oferta (Hogar)
Actor: Trabajadora Hogar | Objetivo: Encontrar y aplicar a una oferta de trabajo

1. La trabajadora accede a "Ofertas" desde la home.
2. El sistema muestra una lista de ofertas disponibles en formato de tarjeta (titulo, ubicacion, horario, tarifa horaria). Las publicadas en las ultimas 48h muestran insignia "Nuevo".
3. La trabajadora puede filtrar por codigo postal/zona, horario (manana, tarde, noche, madrugada, 24h), rango de fecha de inicio.
4. Puede ordenar por: mas recientes, ubicacion mas cercana, tarifa mas alta.
5. La trabajadora toca una oferta para ver el detalle completo.
6. Pulsa "Aplicar".
7. El sistema muestra un dialogo de confirmacion con resumen de la oferta.
8. La trabajadora confirma y la solicitud se envia.
9. Recibe notificacion de confirmacion.

Estado de exito: La trabajadora ha encontrado una oferta relevante, la ha revisado y ha enviado su solicitud.

Flujos alternativos:
- Si intenta aplicar con perfil incompleto: se muestra advertencia con los campos obligatorios pendientes y acceso directo a completarlos.
- Si ya ha aplicado a esa oferta: se previene la solicitud duplicada.
- Si no hay ofertas coincidentes: se muestra estado vacio.

---

## Resultados y Exito

- **Ofertas (Hogar)**: Las trabajadoras Hogar pueden navegar, filtrar y aplicar a ofertas de trabajo y hacer seguimiento de sus solicitudes.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Porcentaje de completitud del perfil**: Visible en la pantalla principal del perfil y desde la home (Hogar).
- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Listado de ofertas | Tocar oferta | Detalle de oferta (RF-6.1) |
| Detalle de oferta | Pulsar "Aplicar" | Dialogo confirmacion, luego vuelta a detalle con estado "Aplicada" |

---

## Criterios de Aceptacion

### CA-001: Listado de ofertas con filtros (Hogar) ← HU-028
GIVEN la trabajadora Hogar accede a "Ofertas"
WHEN se carga la lista
THEN se muestran ofertas en formato de tarjeta con: titulo, ubicacion (codigo postal/ciudad), horario, tarifa horaria. Las publicadas en las ultimas 48h muestran insignia "Nuevo". Estado vacio si no hay ofertas. Se puede filtrar por codigo postal/zona, horario (manana, tarde, noche, madrugada, 24h), rango de fecha de inicio. Se puede ordenar por: mas recientes, ubicacion mas cercana, tarifa mas alta

### CA-002: Detalle de oferta (Hogar) ← HU-028
GIVEN la trabajadora Hogar toca una oferta en el listado
WHEN se abre el detalle
THEN se muestra la informacion completa de la oferta con boton "Aplicar"

### CA-003: Solicitar oferta (Hogar) ← HU-037
GIVEN la trabajadora Hogar esta en el detalle de una oferta
WHEN pulsa "Aplicar"
THEN se muestra un dialogo de confirmacion con resumen de la oferta. Al confirmar, la solicitud se envia y la trabajadora recibe notificacion de confirmacion. Se previenen solicitudes duplicadas

> ⚠ Parcial: El bloqueo por perfil incompleto depende de la resolucion de gap P-008 (lista de campos obligatorios).

### CA-004: Mis solicitudes con estados (Hogar) ← HU-038
GIVEN la trabajadora Hogar accede a "Mis Solicitudes"
WHEN se carga la lista
THEN se muestran las solicitudes en orden cronologico inverso con: titulo oferta, ubicacion, fecha solicitud, estado (Pendiente, En revision, Aceptada, Rechazada, Oferta cerrada). Distincion visual para aceptadas. Se puede filtrar por estado. Se puede retirar solicitud pendiente

### CA-005: Notificacion push de cambio de estado de solicitud (Hogar) ← HU-038
GIVEN una solicitud de la trabajadora Hogar cambia de estado
WHEN el backoffice actualiza el estado
THEN la trabajadora recibe notificacion push informando del cambio

### CA-006: Porcentaje de completitud en home (Hogar) ← HU-044
GIVEN la trabajadora Hogar accede al panel principal
WHEN su perfil no esta completo al 100%
THEN ve el porcentaje de completitud visible en la home para incentivar su cumplimentacion

---

## Checklist de Validacion

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [ ] Ambiguedades resueltas — gap P-008 pendiente (campos obligatorios para perfil)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- Funciones sociales (perfiles publicos, valoraciones entre trabajadoras): no incluidas.
