# Guía de actualización de `_features.md` tras readiness

## 8.5a — Estado por feature

Para cada bloque de feature en `## Features identificadas`, actualizar (o añadir si no existe):
```
- **Estado**: [LISTA | BLOQUEADA | PENDIENTE_GENERACIÓN | REQUIERE_CAMBIO_PRD]
```

Usar el estado de mayor prioridad si hay múltiples bloqueos: CAMBIO_PRD > GAPS > CONFLICTOS > DEPENDENCIAS > AMBIGÜEDAD_DE_ARTEFACTO.

## 8.5b — Resumen de estado

Añadir o actualizar `## Resumen de estado` (justo después de `## Features identificadas`, antes de `## Tabla de shared models`):

```markdown
## Resumen de estado

> Última actualización: [YYYY-MM-DD] | Fuente: `<path>_readiness_report.md`

| Feature | Estado | Bloqueantes |
|---------|--------|-------------|
| F-001: [nombre] | LISTA | — |
| F-002: [nombre] | BLOQUEADA | gaps: P-001, P-002 |
```

## 8.5c — Historial de cambios

Si existe `## Historial de cambios` en `_features.md`, añadir fila:
```
| [versión+1] | [YYYY-MM-DD] | readiness | Estado actualizado desde wf-spec-readiness |
```
