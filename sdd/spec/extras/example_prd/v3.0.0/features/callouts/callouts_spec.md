# Spec: Llamamientos

> Version: 1.0 | Fecha: 2026-04-05
> Spec monolitico origen: prd-hogar-sad_spec.md
> Feature ID: F-004

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios asignados a traves de la app Felizvita (tema verde) | Ver listado de llamamientos, ver detalle del llamamiento, aceptar o rechazar llamamientos con firma digital |
| Coordinadora / Backoffice | Profesional de gestion interna que supervisa a las trabajadoras. No usa la app movil directamente; interactua a traves del sistema de backoffice | Enviar llamamientos, configurar tiempo de caducidad |
| Sistema | El propio sistema automatizado que ejecuta acciones programadas sin intervencion humana | Desactivar llamamientos caducados |

---

## Historias de Usuario

### HU-016: Detalle del llamamiento (SAD)
Como trabajadora SAD
quiero ver la informacion completa de un llamamiento recibido
para que pueda tomar una decision informada sobre si acepto o rechazo el turno ofrecido.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-004], [P-006]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-017: Aceptar o rechazar llamamiento (SAD)
Como trabajadora SAD
quiero poder aceptar o rechazar un llamamiento con firma digital
para que quede constancia formal de mi decision sobre el turno ofrecido.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-005], [P-006]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-018: Listado de llamamientos (SAD)
Como trabajadora SAD
quiero ver todas las llamadas de servicio recibidas con su estado
para que pueda hacer seguimiento de mis llamamientos pendientes, aceptados, rechazados y caducados.

---

## Recorridos de Usuario

### Journey 7: Responder a un llamamiento (SAD)
Actor: Trabajadora SAD | Objetivo: Decidir sobre un turno ofrecido

1. La trabajadora recibe una notificacion push de nuevo llamamiento.
2. En la home, el llamamiento pendiente se muestra de forma prominente con indicacion de urgencia y cuenta atras de caducidad (formato "Xh Xmin restantes").
3. La trabajadora toca el llamamiento, accediendo al detalle.
4. El detalle muestra la informacion basica (codigo de servicio, fecha/hora, ubicacion, urgencia) y campos adicionales.
5. Una vez en el detalle, la trabajadora no puede salir sin tomar una decision (la navegacion hacia atras esta bloqueada).
6. Para aceptar: la trabajadora pulsa "Aceptar" y se le muestra un dialogo donde debe firmar digitalmente con el dedo.
7. Para rechazar: la trabajadora pulsa "Rechazar", selecciona un motivo obligatorio (No disponible, Demasiado lejos, Motivos personales, Otros con texto libre) y firma digitalmente.
8. Tras la decision, el sistema confirma y el llamamiento cambia de estado.

Estado de exito: La trabajadora ha tomado una decision sobre el llamamiento, firmada digitalmente, y el sistema ha registrado su respuesta.

Flujos alternativos:
- Si el llamamiento caduca antes de la respuesta: se muestra como desactivado/no disponible.
- Si otra trabajadora acepta el llamamiento: se muestra como desactivado/no disponible.

---

## Resultados y Exito

- **Llamamientos (SAD)**: Las trabajadoras SAD reciben llamamientos con toda la informacion necesaria, pueden aceptar o rechazar con firma digital, y el sistema gestiona la caducidad y la competencia entre trabajadoras de forma transparente.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Llamamientos multi-envio**: El mismo llamamiento puede enviarse a varias trabajadoras simultaneamente. La primera en aceptar lo recibe y el resto queda desactivado (gestion desde backoffice).
- **Decision obligatoria en llamamiento**: Una vez dentro del detalle del llamamiento, la navegacion hacia atras queda bloqueada hasta que la trabajadora acepte o rechace (sin boton de retroceso).
- **Firma digital obligatoria**: Tanto la aceptacion como el rechazo de un llamamiento requieren firma digital de la trabajadora.
- **Caducidad de llamamientos**: Las llamadas caducan automaticamente tras el tiempo limite configurado desde backoffice.
- **Cuenta atras de llamamientos**: Formato numerico mostrando horas y minutos restantes ("Xh Xmin restantes").
- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Listado de llamamientos | Tocar llamamiento | Detalle del llamamiento (RF-3.4) |
| Detalle del llamamiento | Aceptar + firma | Confirmacion y vuelta a listado |
| Detalle del llamamiento | Rechazar + motivo + firma | Confirmacion y vuelta a listado |

---

## Criterios de Aceptacion

### CA-001: Listado de llamamientos con estado ← HU-018
GIVEN la trabajadora SAD accede al listado de llamamientos
WHEN se carga la lista
THEN se muestran todos los llamamientos con su estado (pendiente, aceptada, rechazada, caducada/desactivada). Cada uno muestra informacion basica: codigo de servicio, fecha/hora, ubicacion, urgencia

### CA-002: Cuenta atras en llamamiento pendiente ← HU-018
GIVEN hay un llamamiento en estado pendiente
WHEN la trabajadora lo ve en el listado o la home
THEN se muestra un contador numerico con horas y minutos restantes ("Xh Xmin restantes")

### CA-003: Llamamiento desactivado ← HU-018
GIVEN un llamamiento caduca o es aceptado por otra trabajadora
WHEN la trabajadora consulta el listado
THEN el llamamiento se muestra como desactivado/no disponible

---

## Checklist de Validacion

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [ ] Ambiguedades resueltas — gaps P-004, P-005, P-006 pendientes (datos del llamamiento, consecuencia de inaccion, textos oficiales)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- Funcionalidades de backoffice/coordinacion: este spec cubre exclusivamente la experiencia desde la app movil de la trabajadora.
