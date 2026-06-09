---
name: kb-qa-expert
description: "Metodologia QA del pipeline SDD: derivacion de casos de prueba TC-XXX desde los CAs GIVEN/WHEN/THEN del spec, niveles y tipos de prueba, trazabilidad CA→TC y criterios de cobertura con evidencia para el informe de verificacion. No cubre la estrategia de testing del stack (kb del overlay) ni la escritura de tests (implementador/tester)."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# QA Expert — Metodología de verificación de CAs

Esta KB es la SSoT de la metodología QA del pipeline: cómo se derivan casos de prueba desde los CAs de un spec, y con qué criterio se declara un CA cubierto tras la implementación. La promesa del spec ("CAs testables GIVEN/WHEN/THEN") se cierra aquí.

## ¿Qué es un caso de prueba (TC)?

Un TC es la unidad verificable de QA: la concreción ejecutable de **exactamente un CA**. Deriva del comportamiento observable que el CA promete, nunca de la estructura interna del código.

- ID `TC-XXX`, secuencial dentro del `_qa_plan.md` de la feature (TC-001 si es nuevo).
- Todo TC referencia un único `CA-XXX` del spec origen. Si un caso parece cubrir varios CAs, se descompone.

## Formato obligatorio del TC

```markdown
### TC-001 — <título corto del caso>
- **CA origen**: CA-001
- **Nivel**: unit | integration | e2e | manual
- **Tipo**: happy | error | edge
- **GIVEN**: <precondición concreta, con datos reales — no placeholders>
- **WHEN**: <acción concreta>
- **THEN**: <resultado observable y CÓMO se observa (assert, pantalla, respuesta)>
- **Datos/fixtures**: <datos de prueba necesarios | ninguno>
- **Automatizable**: sí (<suite/source set sugerido>) | no — <justificación>
- **Estado**: PENDIENTE
```

El campo `Estado` lo escribe **solo** `wf-qa-verify` (separación derivador/verificador). Valores: `PENDIENTE | CUBIERTO | PARCIAL | SIN_COBERTURA | MANUAL_PENDIENTE | DIVERGENTE`.

## Reglas de derivación CA → TC

1. **Cobertura total**: todo CA del spec tiene ≥1 TC. Un CA sin TC = qa_plan incompleto, no se entrega.
2. **Ramas observables**: si el CA define comportamiento de fallo, límites o permisos, cada rama observable tiene su TC — mínimo `happy` + `error` cuando el CA promete ambos. No inflar: una rama que el CA no promete no genera TC.
3. **Sin TC huérfano**: si durante la derivación aparece un comportamiento que necesita prueba pero ningún CA lo cubre, NO se inventa el TC — se reporta como gap de spec (vía `/wf-spec-delta`), igual que el triaje `UNSPEC` de `wf-bug`.
4. **Pureza**: el TC observa comportamiento (entrada → resultado observable), no implementación (nombres de clases, estructura de capas). Un refactor que conserva comportamiento no debe invalidar TCs.
5. **Concreción**: GIVEN/WHEN/THEN del TC usa datos concretos (valores, estados, usuarios) aunque el CA del spec sea más abstracto. Un TC que no se puede ejecutar tal como está escrito no está terminado.

## Niveles de prueba (criterio de asignación)

| Nivel | Cuándo | Ejemplo |
|---|---|---|
| `unit` | El THEN es observable en lógica pura, sin IO ni framework | UseCase, ViewModel, validación, mapper |
| `integration` | El THEN cruza una frontera entre piezas (contratos, persistencia, navegación) | Repository + API fake, DB in-memory, grafo de navegación |
| `e2e` | El THEN solo es observable en el flujo completo de usuario | login → home, compra completa |
| `manual` | No hay forma razonable de automatizar | criterio visual subjetivo, hardware, integración de terceros sin sandbox |

Default: automatizable al nivel más bajo que observe el THEN completo. `manual` exige justificación en el campo `Automatizable`. Si existe `<stack>_project_state.md`, sus suites y source sets declarados mandan sobre esta tabla genérica.

## Modo ligero

Si el spec declara `> Modo: ligero` (proporcionalidad de `kb-spec-expert`): mínimo 1 TC `happy` por CA + TC `error` solo para los CAs que prometen fallo. Las reglas 3-5 (sin huérfanos, pureza, concreción) son invariantes — no se relajan.

## Criterios de cobertura (verificación)

**Regla de oro: cobertura sin evidencia ejecutada no existe.** Declarar CUBIERTO exige haber ejecutado algo y registrar comando + salida (o confirmación humana en TC manuales). Es el mismo principio que el contrato de cierre de los implementadores y que `kb-spec-characterization`.

| Estado | Condición |
|---|---|
| `CUBIERTO` | Test automatizado localizado, ejecutado y en verde que ejercita el THEN completo del TC — o TC manual ejecutado y confirmado explícitamente por el humano |
| `PARCIAL` | Existe test pero no ejercita el THEN completo (p. ej. solo la rama happy de un CA con error) |
| `SIN_COBERTURA` | No existe test que ejercite el TC |
| `MANUAL_PENDIENTE` | TC manual aún sin confirmación humana |
| `DIVERGENTE` | El test ejecuta y FALLA: el código viola el CA. No se "arregla" el TC ni el test — es un bug, vía `/wf-bug` (triaje CODE_BUG contra ese CA) |

Estado por CA = el peor de sus TCs (`DIVERGENTE` > `SIN_COBERTURA` > `PARCIAL` > `MANUAL_PENDIENTE` > `CUBIERTO`).

## Formato del `_qa_report.md`

```markdown
# QA Report: <Feature>
> QA plan origen: <ruta relativa al _qa_plan.md>
> Spec origen: <ruta relativa al _spec.md>
> Fecha: YYYY-MM-DD | Commit verificado: <sha corto | working tree>
> Veredicto: APTO | APTO_CON_RESERVAS | NO_APTO
> Aprobado por: <rol> (<YYYY-MM-DD>)   ← solo si el veredicto es APTO o APTO_CON_RESERVAS; ausente en NO_APTO

## Resumen por CA
| CA | TCs | Estado CA | Evidencia |
|---|---|---|---|
| CA-001 | TC-001 ✓, TC-002 ✓ | CUBIERTO | `<comando>` → verde |

## Detalle de hallazgos
(solo TCs no CUBIERTOS: estado, qué falta, acción recomendada)

## Acciones recomendadas
- SIN_COBERTURA / PARCIAL → task de test (owner según dominio) o `/wf-task-run` si quedan tasks de test pendientes
- DIVERGENTE → `/wf-bug <descripción> --feature <nombre>` citando el CA
- MANUAL_PENDIENTE → checklist humana pendiente
```

**Veredicto global**:
- `APTO`: todos los CAs `CUBIERTO`.
- `APTO_CON_RESERVAS`: hay `MANUAL_PENDIENTE` o `PARCIAL`, pero ningún `SIN_COBERTURA` ni `DIVERGENTE`. Las reservas se listan.
- `NO_APTO`: algún CA `SIN_COBERTURA` o `DIVERGENTE`.

El veredicto describe cobertura verificada; no sustituye al sellado del plan ni al estado de las tasks — los complementa al final del ciclo.

La línea `Aprobado por: <rol> (<YYYY-MM-DD>)` del header (default de fase `QA`) registra la atribución humana del gate cuando el veredicto es `APTO` o `APTO_CON_RESERVAS`; en `NO_APTO` no se escribe. La escribe el orquestador (`wf-qa-verify`), es un dato humano no verificable y ningún script la valida. Convenio completo: `kb-traceability-rules` Regla 10.
