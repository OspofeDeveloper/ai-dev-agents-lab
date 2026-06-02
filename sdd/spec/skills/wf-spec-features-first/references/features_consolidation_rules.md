# Reglas de consolidación incremental de `_features.md`

1. Si existe `_features.md` previo, léelo para preservar el estado de iteraciones anteriores (features LISTA, BLOQUEADA, PENDIENTE_GENERACIÓN, REQUIERE_CAMBIO_PRD) y las entradas del Historial de cambios.

2. Lee el `_discovery.md` para obtener el universo completo de features (todas las F-XXX), shared models y mapping RF→Feature.

3. Lee todos los specs de feature en `features/*/` (recién generados + preexistentes de iteraciones anteriores).

4. Construye el `_features.md` con **TODAS las features del discovery**, no solo el subset de esta iteración:
   - Con spec: indexar con su metadata (descripción, actor, journeys, CAs, modelos). Estado provisional según contenido del spec.
   - Sin spec todavía: indexar con metadata mínima del discovery y estado `PENDIENTE_GENERACIÓN`. Incluir: `> Esta feature está identificada en el discovery pero aún no se ha generado spec. Ejecuta /wf-spec-features-first <prd.md> --features <F-XXX> cuando quieras procesarla.`

5. Reconciliar la tabla de shared models entre discovery y specs generados.

6. Mantener la trazabilidad RF → HU → Feature consolidada (RFs de features PENDIENTE_GENERACIÓN se anotan como "HUs no generadas todavía").

7. Usar solo estados canónicos: `LISTA`, `PENDIENTE_GENERACIÓN`, `BLOQUEADA`, `REQUIERE_CAMBIO_PRD`. No usar variantes como `Completado`, `LISTA_PARA_PLAN` o `BLOQUEADA_POR_GAPS`.

8. Añadir entrada al Historial de cambios:
   - Con `--features`: `[YYYY-MM-DD] | features-first (subset) | Iteración sobre [F-001, F-002, ...] — N nuevas + M preservadas`
   - Sin `--features`: `[YYYY-MM-DD] | features-first (full) | Generación completa de las N features del discovery`

9. Escribir el `_features.md` en el mismo directorio que el PRD.
