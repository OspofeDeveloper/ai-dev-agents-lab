# Trazabilidad de Requisitos: [nombre del proyecto]
> Generado por: wf-spec-finalize | Fecha: [YYYY-MM-DD]
> Spec origen: [path/_spec.md]

---

## Tabla RF → HU → Feature

| RF | Título RF | HU | Título HU | Feature | Estado |
|----|-----------|-----|-----------|---------|--------|
| RF-001 | [título] | HU-001 | [título] | — | pendiente-decompose |
| RF-001 | [título] | HU-002 | [título] | — | pendiente-decompose |
| RF-002 | [título] | HU-003 | [título] | — | pendiente-decompose |

<!--
  Estado posibles valores:
  - pendiente-decompose : HU registrada, feature no asignada aún (estado inicial tras finalize)
  - activo              : HU asignada a feature (se rellena tras wf-spec-decompose)
  - modificado vX.Y     : HU modificada por wf-spec-delta apply en esa versión
  - eliminado vX.Y      : HU eliminada por wf-spec-delta apply (fila se conserva para auditoría)
-->

---

## Cobertura por RF

| RF | Título RF | HUs asignadas | Features involucradas |
|----|-----------|---------------|-----------------------|
| RF-001 | [título] | HU-001, HU-002 | — |
| RF-002 | [título] | HU-003 | — |

> La columna "Features involucradas" se completa tras ejecutar `/wf-spec-decompose`.

---

## Historial de cambios

| Versión | Fecha | Tipo | Descripción |
|---------|-------|------|-------------|
| 1.0 | [YYYY-MM-DD] | inicial | Generado desde spec monolítico |

<!--
  Tipos de historial:
  - inicial       : generación del documento por wf-spec-finalize
  - decompose     : asignación de features por wf-spec-decompose
  - delta apply   : cambios aplicados por wf-spec-delta apply (indica versión del spec)
-->
