# Guía de actualización de trazabilidad en `_features.md` tras delta apply

## Localizar el archivo

- Si el spec está en `features/<nombre>/`: busca dos niveles arriba (`../../*_features.md`)
- Si el spec es monolítico: busca en el mismo directorio

Si no existe el archivo o no tiene `## Trazabilidad RF → HU → Feature`: omitir este paso silenciosamente.

## Actualizaciones por tipo de cambio

**HUs AÑADIDAS**: añadir fila nueva con:
- RF inferido del delta analysis o del documento de nuevos requisitos
- HU con su nuevo ID y título
- Feature: nombre del feature spec actual
- Estado: `activo`

**HUs MODIFICADAS**: actualizar el Título HU en la fila correspondiente. El ID y el RF no cambian.

**HUs ELIMINADAS**: cambiar el Estado de la fila a `eliminado vX.Y` (nueva versión del spec). **NO eliminar la fila** — se conserva para auditoría.

## Cobertura y historial

- Actualizar la tabla `## Cobertura por RF` con las HUs y features modificadas.
- Añadir fila al `## Historial de cambios` con la nueva versión del spec, fecha, tipo "delta apply" y descripción breve del conjunto de cambios.
