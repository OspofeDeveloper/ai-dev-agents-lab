# Reglas de integración de cambios en el spec (modo apply)

Principios base:
- **No interpretar**: el texto aprobado va tal cual
- **No ampliar**: si la respuesta cubre el gap, no expandirla
- **No inferir**: si algo quedó sin responder pero era [INFORMATIVO], usa solo la Asunción por defecto

Por tipo de cambio:

- **HUs AÑADIDAS**: insertar después de la última HU existente con numeración consecutiva (ej: spec llega hasta HU-006 → primera nueva es HU-007)
- **HUs MODIFICADAS**: reemplazar solo el texto de la HU afectada; mantener el ID original
- **HUs ELIMINADAS**: eliminar la HU y todos sus CAs asociados; renumerar para mantener secuencia sin huecos
- **CAs NUEVOS**: insertar al final de los CAs de su HU padre con numeración consecutiva. Incluir `← HU-XXX`
- **CAs MODIFICADOS**: reemplazar solo el GIVEN/WHEN/THEN del CA afectado; mantener el ID
- **CAs ELIMINADOS**: eliminar y renumerar los CAs restantes para eliminar huecos
- **Journeys**: actualizar añadiendo/modificando/eliminando pasos según los cambios de HUs
- **Instrucciones Inambiguas**: añadir/modificar/eliminar reglas según el delta
- **Fuera de Alcance**: actualizar si el delta lo especifica
