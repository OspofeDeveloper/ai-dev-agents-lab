# check-conflicts — Detectar Conflictos entre Features

**Caso de uso**: verificar que los Specs SDD de las features de un mismo proyecto son coherentes entre sí.

Comando: `/check-conflicts <archivo_spec.md> [--features-dir <directorio>]`

---

## Orquestador: `check-conflicts` (`SKILL.md`)

Localiza todos los specs de feature del proyecto, delega la comparación al agente `sdd-analyst` en modo `conflict`, y escribe el informe de conflictos si se detecta alguno.

**Salida**:
- `_conflict_report.md` — si hay conflictos, con ID, features afectadas, severidad y sugerencias de resolución
- Sin archivo — si no hay conflictos (solo informa al usuario)

**Nota**: este mismo análisis se ejecuta automáticamente al final de `/decompose-spec` en modo no bloqueante. `/check-conflicts` es para ejecución manual, especialmente tras modificar un spec con `/prepare-delta` o añadir una feature con `/prepare-spec fast-track`.

---

## Workflow (Capa 3)

### `spec-conflict/`

**Modo**: `conflict`

Aplica las 5 reglas de `conflict-expert` comparando todos los specs de feature recibidos:

1. **HUs duplicadas**: mismo actor + verbo + objetivo en features distintas → `ALTA`
2. **CAs contradictorios**: mismo GIVEN/WHEN, THEN incompatibles → `ALTA`
3. **Scope overlap**: el journey de una feature es el core de otra → `ALTA`
4. **Shared models inconsistentes**: mismo modelo con definiciones distintas entre features → `MEDIA`
5. **Out-of-scope contradictorios**: lo que una feature declara fuera de alcance, otra lo incluye explícitamente → `MEDIA`

**Severidad**:
- `ALTA` — bloquea la fase de planificación; debe resolverse antes de `/prepare-plan`
- `MEDIA` — problema de frontera; puede seguirse pero con riesgo de inconsistencias en el plan

**Output**: informe con tabla de conflictos (ID, features afectadas, severidad, descripción, sugerencia de resolución).

Template en `references/conflict_report_template.md`.

---

## Flujo típico

```
# Tras añadir o modificar una feature:
/check-conflicts features/notifications/notifications_spec.md --features-dir features/
  → _conflict_report.md (si hay conflictos)

# O para verificar todo el proyecto:
/check-conflicts --features-dir features/
  → _conflict_report.md (si hay conflictos)
```

Los conflictos `ALTA` deben resolverse editando manualmente los specs afectados y re-validando con `/prepare-spec validate` antes de continuar con `/prepare-plan`.
