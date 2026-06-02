# Guía de actualización del índice de features en fast-track

## Actualizar o crear `_features.md`

Busca si existe algún `*_features.md` en el directorio del archivo de input:

- **Si existe**: léelo y añade la nueva feature con el siguiente ID disponible. Actualiza la tabla de shared models si la feature declara alguno.
- **Si no existe**: genera un `_features.md` nuevo con esta feature como primera entrada `F-001`.

En ambos casos:
- Usa solo estados canónicos: `LISTA`, `PENDIENTE_GENERACIÓN`, `BLOQUEADA`, `REQUIERE_CAMBIO_PRD`
- Añade en la entrada de la feature:
  - `- **Origen de alcance**: [PRD | PRD + analysis respondido]`
  - `- **Avisos de gobernanza**: [ninguno | alcance derivado desde P-00X]`
- Si el resultado se generó con alcance derivado, no lo presentes como PRD puro.

## Trazabilidad RF→HU (solo modo scoped)

Si se usó `--scope-from`, el discovery contiene el mapping RF→Feature. Al actualizar `_features.md`, añade o actualiza `## Trazabilidad RF → HU → Feature` con las filas de esta feature: para cada RF del scope, mapea las HUs generadas. Si la sección ya existía, añade las filas nuevas sin eliminar las existentes.
