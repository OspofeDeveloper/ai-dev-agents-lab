# Reglas de integración de cambios en el spec (modo apply)

Principios base:
- **No interpretar**: el texto aprobado va tal cual
- **No ampliar**: si la respuesta cubre el gap, no expandirla
- **No inferir**: si algo quedó sin responder pero era [INFORMATIVO], usa solo la Asunción por defecto
- **Una respuesta con `Dueño` se integra como cita** (v0.127.1): si el gap lleva `- **Dueño**: F-00Y`,
  la regla es de esa feature y se escribe en su spec. Aquí va solo lo que hace la operación de este
  spec, citando al dueño (*"…lo que se puede hacer con ese movimiento lo fija el contrato de
  Movimiento, F-001"*). No es interpretar la respuesta: es dónde se escribe. Copiarla y añadir la
  cita sigue siendo una regla fuera de su dueño — medido en la pasada 2 de `CU-3.ac`, hizo fallar la
  validación de objetivos de ahorro.

Por tipo de cambio:

- **HUs AÑADIDAS**: insertar después de la última HU existente con numeración consecutiva (ej: spec llega hasta HU-006 → primera nueva es HU-007)
- **HUs MODIFICADAS**: reemplazar solo el texto de la HU afectada; mantener el ID original
- **HUs ELIMINADAS**: marcar la HU y todos sus CAs asociados como tombstone preservando sus IDs y el hueco en la secuencia (`HU-XXX [ELIMINADO en vX: <razón>]`). **Nunca renumerar** — los IDs son inmutables (SSoT: `kb-traceability-rules` Regla 12). El siguiente ID nuevo toma el siguiente número libre, no el hueco.
- **CAs NUEVOS**: insertar al final de los CAs de su HU padre con numeración consecutiva. Incluir `← HU-XXX`
- **CAs MODIFICADOS**: reemplazar solo el GIVEN/WHEN/THEN del CA afectado; mantener el ID
- **CAs ELIMINADOS**: marcar como tombstone preservando su ID y el hueco (`CA-XXX [ELIMINADO en vX: <razón>]`). **Nunca renumerar** los CAs restantes — un CA/TC/task downstream apunta a ese ID y renumerar lo corrompe (SSoT: `kb-traceability-rules` Regla 12)
- **Journeys**: actualizar añadiendo/modificando/eliminando pasos según los cambios de HUs
- **Instrucciones Inambiguas**: añadir/modificar/eliminar reglas según el delta
- **Fuera de Alcance**: actualizar si el delta lo especifica
