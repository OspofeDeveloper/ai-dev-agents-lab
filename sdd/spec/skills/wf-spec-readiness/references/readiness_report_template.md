# Readiness Report: [Nombre del proyecto]

> **Generado por**: sdd-analyst (modo readiness)
> **Fecha**: [YYYY-MM-DD]
> **Features analizadas**: [N]
> **Conflict report**: [Si — path | No encontrado]
> **Fuente**: [path/_features.md]

---

## Estado general

> **[TODAS_LISTAS | PARCIALMENTE_LISTAS | NINGUNA_LISTA]**
>
> [N] de [M] features listas para `/wf-prepare-plan`. [Resumen en 1 frase de los bloqueos principales si los hay.]

---

## Matriz de readiness

| Feature | Estado | HUs [INCOMPLETO] | Conflictos ALTA | Dependencias pendientes |
|---------|--------|:-----------------:|:---------------:|------------------------|
| F-001: [nombre] | LISTA | 0 | 0 | — |
| F-002: [nombre] | BLOQUEADA_POR_GAPS | 2 | 0 | — |
| F-003: [nombre] | BLOQUEADA_POR_CONFLICTOS | 0 | 1 | — |
| F-004: [nombre] | ESPERANDO_DEPENDENCIAS | 0 | 0 | F-002 |
| F-005: [nombre] | LISTA_PARA_PLAN | 0 | 0 | F-001 (bloqueada) |

<!-- Ordenar por Feature ID. Mostrar todos los bloqueos de cada feature si tiene varios. -->

---

## Fases de implementacion

> Orden recomendado basado en el grafo de dependencias. Dentro de cada fase, las features pueden planificarse e implementarse en paralelo.

### Fase 1 (sin dependencias)

| Feature | Estado | Accion requerida |
|---------|--------|------------------|
| F-001: [nombre] | LISTA | `/wf-prepare-plan generate features/[nombre]/[nombre]_spec.md` |
| F-005: [nombre] | BLOQUEADA_POR_GAPS | Resolver gaps [P-XXX] antes de planificar |

### Fase 2 (depende de Fase 1)

| Feature | Depende de | Estado | Accion requerida |
|---------|------------|--------|------------------|
| F-003: [nombre] | F-001 | LISTA_PARA_PLAN | `/wf-prepare-plan generate features/[nombre]/[nombre]_spec.md` (implementar despues de F-001) |
| F-004: [nombre] | F-001, F-003 | BLOQUEADA_POR_CONFLICTOS | Resolver CF-XXX y re-ejecutar `/wf-spec-conflict` |

### Fase N

<!-- Repetir por cada fase adicional -->

---

## Inventario de gaps bloqueantes

<!-- Omitir esta seccion completa si no hay features BLOQUEADA_POR_GAPS -->

> Los siguientes gaps criticos impiden que las HUs afectadas se completen. Hasta que se resuelvan, las features no pueden pasar a `/wf-prepare-plan`.

| Gap | Severidad | HUs afectadas | Features afectadas | Accion |
|-----|-----------|---------------|-------------------|--------|
| [P-001] | CRITICO | HU-003 | F-001 | Responder y ejecutar `/wf-spec-delta resolve` sobre el spec afectado |
| [P-003] | CRITICO | HU-010 | F-003 | Responder y ejecutar `/wf-spec-delta resolve` sobre el spec afectado |

<!-- Agrupar por gap ID. Un mismo gap puede afectar a multiples HUs y features. -->

---

## Conflictos ALTA no resueltos

<!-- Omitir esta seccion completa si no hay _conflict_report.md o no hay conflictos ALTA -->

> Los siguientes conflictos de severidad ALTA deben resolverse antes de planificar las features afectadas.

| ID | Tipo | Features afectadas | Descripcion breve | Referencia |
|----|------|-------------------|-------------------|------------|
| CF-001 | CA contradictorio | F-003, F-006 | [descripcion corta del conflicto] | `_conflict_report.md` |

---

## Dependencias circulares

<!-- Omitir esta seccion completa si no hay ciclos -->

> Se detectaron dependencias circulares que impiden determinar el orden de implementacion para las features involucradas.

| Ciclo | Features involucradas | Causa probable |
|-------|----------------------|----------------|
| 1 | F-007 -> F-009 -> F-007 | Shared model [Nombre] referenciado mutuamente |

---

## Proximos pasos

<!-- Elegir la variante que aplique segun el Estado general -->

<!-- TODAS_LISTAS -->
1. Ejecuta `/wf-prepare-plan generate <feature_spec.md>` para cada feature, siguiendo el orden de fases
2. Empieza por las features de Fase 1 (sin dependencias)
3. Las features de fases posteriores pueden planificarse en paralelo dentro de su fase

<!-- PARCIALMENTE_LISTAS -->
1. **Features listas**: ejecuta `/wf-prepare-plan generate <feature_spec.md>` para las features LISTA y LISTA_PARA_PLAN de las primeras fases
2. **Features con gaps**: responde los gaps pendientes y ejecuta `/wf-spec-delta resolve` para cada feature afectada
3. **Features con conflictos**: edita los specs para resolver los conflictos ALTA y re-ejecuta `/wf-spec-conflict`
4. **Re-evaluar**: despues de resolver bloqueos, ejecuta `/wf-spec-readiness` de nuevo para verificar el progreso

<!-- NINGUNA_LISTA -->
1. Prioriza resolver los gaps `[CRITICO]` — afectan a [N] features
2. Resuelve los conflictos ALTA — afectan a [N] features
3. Re-ejecuta `/wf-spec-readiness` despues de cada correccion para verificar el progreso
