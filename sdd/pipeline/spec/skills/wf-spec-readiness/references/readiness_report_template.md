# Readiness Report: [Nombre del proyecto]

> **Generado por**: sdd-spec-auditor
> **Fecha**: [YYYY-MM-DD]
> **Features analizadas**: [N]
> **Conflict report**: [SIN_CONFLICTOS — path | CONFLICTOS_DETECTADOS — path | No encontrado | Ambiguo — revisar path]
> **Vigencia de los informes de conflicto**: [uno por informe: `path` — VIGENTE (comparó los N specs
> que hay ahora) | ESTANCADO (comparó F-00X, F-00Y; no vio F-00Z) | VIGENCIA DESCONOCIDA (sin campo
> `Conjunto comparado`). Se lee del campo de su cabecera, no de la fecha (D-090).]
> **Fuente**: [path/_features.md]

---

## Estado general

> **[TODAS_LISTAS | PARCIALMENTE_LISTAS | NINGUNA_LISTA]**
>
> [N] de [M] features listas para planificar. [Resumen en 1 frase de los bloqueos principales si los hay.]

---

## Matriz de readiness

| Feature | Estado | HUs [INCOMPLETO] | Conflictos ALTA | Bloqueantes |
|---------|--------|:-----------------:|:---------------:|-------------|
| F-001: [nombre] | LISTA | 0 | 0 | — |
| F-002: [nombre] | BLOQUEADA | 2 | 0 | gaps: P-001 |
| F-003: [nombre] | BLOQUEADA | 0 | 1 | conflictos: CF-F003-01 |
| F-004: [nombre] | BLOQUEADA | 0 | 0 | dependencias: F-002 |
| F-005: [nombre] | REQUIERE_CAMBIO_PRD | 0 | 0 | gobernanza: alcance derivado desde P-007 |
| F-006: [nombre] | RETIRADA | — | — | CR-007 — [razón de la baja] |
| F-007: [nombre] | BLOQUEADA | 0 | 0 | pendiente de validación (el spec sigue en BORRADOR) |

<!-- Ordenar por Feature ID. Mostrar todos los bloqueos de cada feature si tiene varios. -->

---

## Fases de implementacion

> Orden recomendado basado en el grafo de dependencias. Dentro de cada fase, las features pueden planificarse e implementarse en paralelo.

### Fase 1 (sin dependencias)

| Feature | Estado | Accion requerida |
|---------|--------|------------------|
| F-001: [nombre] | LISTA | Lista para planificar |
| F-005: [nombre] | REQUIERE_CAMBIO_PRD | Consolidar el cambio en PRD y resincronizar derivados antes de planificar |
| F-007: [nombre] | BLOQUEADA | Validar el spec: su contenido está completo, solo falta que alguien lo dé por bueno |

### Fase 2 (depende de Fase 1)

| Feature | Depende de | Estado | Accion requerida |
|---------|------------|--------|------------------|
| F-003: [nombre] | F-001 | LISTA | Lista para planificar, despues de F-001 |
| F-004: [nombre] | F-001, F-003 | BLOQUEADA | Resolver CF-F004-01 y volver a revisar conflictos |

### Fase N

<!-- Repetir por cada fase adicional -->

---

## Inventario de gaps bloqueantes

<!-- Omitir esta seccion completa si no hay features BLOQUEADA por gaps -->

> Los siguientes gaps criticos impiden que las HUs afectadas se completen. Hasta que se resuelvan, las features no pueden pasar a planificacion.

| Gap | Severidad | HUs afectadas | Features afectadas | Accion |
|-----|-----------|---------------|-------------------|--------|
| [P-001] | CRITICO | HU-003 | F-001 | Responder el gap y completar las historias incompletas del spec |
| [P-003] | CRITICO | HU-010 | F-003 | Responder el gap y completar las historias incompletas del spec |

<!-- Agrupar por gap ID. Un mismo gap puede afectar a multiples HUs y features. -->

---

## Conflictos ALTA no resueltos

<!-- Omitir esta seccion completa si no hay _conflict_report.md o no hay conflictos ALTA -->

> Los siguientes conflictos de severidad ALTA deben resolverse antes de planificar las features afectadas.

| ID | Tipo | Features afectadas | Descripcion breve | Referencia |
|----|------|-------------------|-------------------|------------|
| CF-F003-01 | CA contradictorio | F-003, F-006 | [descripcion corta del conflicto] | `_conflict_report.md` |

<!-- El ID se cita TAL CUAL viene del informe de origen (D-090): ya es único, porque cada auditor
     numera con su feature delante. No renumerar: la trazabilidad contra el informe es lo que abre
     quien va a arreglar el choque. Informes viejos con IDs colisionados → citar <feature>:<ID>. -->

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
1. Planifica cada feature siguiendo el orden de fases indicado
2. Empieza por las features de Fase 1 (sin dependencias)
3. Las features de fases posteriores pueden planificarse en paralelo dentro de su fase

<!-- PARCIALMENTE_LISTAS -->
1. **Features listas**: planifica las features LISTA de las primeras fases
2. **Features con gaps**: responde los gaps pendientes y pide completar las historias incompletas de cada feature afectada
3. **Features con conflictos**: resuelve los conflictos ALTA en los specs y pide una nueva revision de conflictos
4. **Re-evaluar**: despues de resolver bloqueos, pide de nuevo el estado de readiness para verificar el progreso

<!-- NINGUNA_LISTA -->
1. Prioriza resolver los gaps `[CRITICO]` — afectan a [N] features
2. Resuelve los conflictos ALTA — afectan a [N] features
3. Pide de nuevo el estado de readiness despues de cada correccion para verificar el progreso

<!-- SIEMPRE que la seccion de vigencia liste algun informe ESTANCADO (D-093): un punto mas, con
     su accion. Di primero quien cubre los pares que ese informe no vio —normalmente los informes
     vigentes, porque cada spec nuevo se compara contra todos— y luego que puede rehacerse cuando
     se quiera tener el documento al dia. Si al cruzarlo aparece un par que no ha mirado NADIE,
     eso no es documento viejo: es analisis que falta, y va como accion prioritaria. -->
N. **Informes de conflicto estancados**: [path] describe un conjunto de [N] specs que ya no es el
   actual. Los choques de [F-00X] con [las features nuevas] estan cubiertos por los informes
   vigentes de estas; el documento puede rehacerse cuando convenga tenerlo al dia.
