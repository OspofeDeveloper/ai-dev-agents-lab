# Features Index: [nombre del proyecto]
> Spec origen: [path/_spec.md] | Fecha: [YYYY-MM-DD]

---

## Features identificadas

### F-001: [nombre-kebab-case]
- **Descripción**: [una frase del objetivo de esta feature]
- **Actor principal**: [quién]
- **Journeys propios**: [Journey 1, Journey 2, ...]
- **CAs propios**: [CA-001 a CA-00X en el spec de esta feature]
- **Modelos propios**: [Modelo1, Modelo2]
- **Modelos compartidos (owner)**: [ModeloX] ← esta feature lo define
- **Modelos compartidos (ref)**: [ModeloY (owner: F-00Z)]
- **Ruta spec**: features/[nombre]/[nombre]_spec.md
- **Estado**: pendiente-readiness

<!-- Repetir bloque por cada feature identificada -->

---

## Resumen de estado

| Feature | Estado | Bloqueantes |
|---------|--------|-------------|
<!-- Se completa tras ejecutar /wf-spec-readiness -->

---

## Tabla de shared models

| Modelo | Feature Owner | Features que lo referencian |
|--------|---------------|-----------------------------|
| [NombreModelo] | F-00X: [nombre] | F-00Y, F-00Z |

---

## Trazabilidad RF → HU → Feature

| RF | Título RF | HU | Título HU | Feature | Estado |
|----|-----------|-----|-----------|---------|--------|
| RF-001 | [título] | HU-001 | [título] | [nombre-feature] | activo |

<!--
  Estado posibles valores:
  - activo              : HU asignada a feature
  - modificado vX.Y     : HU modificada por wf-spec-delta apply en esa versión
  - eliminado vX.Y      : HU eliminada por wf-spec-delta apply (fila conservada para auditoría)
-->

---

## Cobertura por RF

| RF | Título RF | HUs asignadas | Features involucradas |
|----|-----------|---------------|-----------------------|
| RF-001 | [título] | HU-001, HU-002 | [nombre-feature] |

---

## Historial de cambios

| Versión | Fecha | Tipo | Descripción |
|---------|-------|------|-------------|
| 1.0 | [YYYY-MM-DD] | decompose | Features asignadas desde wf-spec-decompose |

<!--
  Tipos de historial:
  - decompose     : generación inicial por wf-spec-decompose
  - delta apply   : cambios aplicados por wf-spec-delta apply (indica versión del spec)
  - readiness     : estado actualizado por wf-spec-readiness
-->
