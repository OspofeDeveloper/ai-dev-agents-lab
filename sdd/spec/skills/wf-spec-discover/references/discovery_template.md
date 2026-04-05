# Feature Discovery: [nombre del proyecto]
> PRD origen: [path/prd.md] | Fecha: [YYYY-MM-DD]
> Generado por: wf-spec-discover

---

## Requisitos Funcionales identificados

| RF | Título | Sección PRD |
|----|--------|-------------|
| RF-001 | [título del requisito] | [sección o párrafo del PRD donde aparece] |

<!--
  Si el PRD tiene RFs numerados explícitamente, usar esos IDs.
  Si no, asignar IDs secuenciales RF-001, RF-002... y añadir esta nota:
  > Los IDs de RF son inferidos de las secciones funcionales del PRD — el documento original no los numera explícitamente.
-->

---

## Features identificadas

### F-001: [nombre-kebab-case]
- **Descripción**: [una frase del objetivo funcional de esta feature]
- **Actor principal**: [quién]
- **Objetivo del actor**: [qué quiere lograr]
- **Journeys anticipados**: [Journey 1, Journey 2, ...]
- **CAs derivables**: [mínimo 3 — descripción breve de cada uno]
- **Scope (RFs)**: [RF-001, RF-003, RF-007]
- **Scope (secciones PRD)**: [sección 2.1, sección 3.4]
- **Modelos propios**: [Modelo1, Modelo2]
- **Modelos compartidos (owner)**: [ModeloX] ← esta feature lo define
- **Modelos compartidos (ref)**: [ModeloY (owner: F-00Z)]

<!-- Repetir bloque por cada feature identificada -->

---

## Tabla de shared models

| Modelo | Feature Owner | Features que lo referencian | Criterio de asignación |
|--------|---------------|-----------------------------|------------------------|
| [NombreModelo] | F-00X: [nombre] | F-00Y, F-00Z | [creación / CRUD / cobertura / proximidad] |

<!-- Omitir sección si no hay shared models -->

---

## Trazabilidad RF → Feature

| RF | Título RF | Feature asignada |
|----|-----------|------------------|
| RF-001 | [título] | F-001: [nombre] |

---

## Decisiones de merge

| Candidata original | Fusionada en | Razón |
|---------------------|--------------|-------|
| [nombre] | F-00X: [nombre] | [criterio que no cumplió: journeys no independientes / menos de 3 CAs / actor no claro] |

<!-- Omitir sección si no hubo merges -->

---

## Siguiente paso

Para generar el spec de cada feature individualmente:
```
/wf-spec-fast-track <prd.md> --scope-from <discovery.md> --feature F-001
```

Para generar todos los specs en paralelo (flujo automático):
```
/wf-spec-features-first <prd.md>
```

Para el flujo completo spec-first (spec monolítico):
```
/wf-spec-analyze <prd.md>
```
