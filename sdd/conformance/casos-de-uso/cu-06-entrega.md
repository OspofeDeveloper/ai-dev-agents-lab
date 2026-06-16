# CU-6 — De spec a entrega

**Objetivo:** verificar el tramo final del pipeline — plan → validación → tasks →
ejecución → QA → release — comprobando que cada sello se gana con sus condiciones, que
las tasks se ejecutan con estado y commit trazables, que QA exige evidencia ejecutada y
que la release solo cierra con QA apto.
**Proyecto a usar:** un proyecto real con un `_spec.md` fiable (sin items pendientes,
salido de CU-3) y un **stack que puedas compilar y testear** — QA exige evidencia
ejecutada (CU-6.f).
**Cobertura automática:** alta en lo determinista — `sdd/tests/` cubre `sdd-seal.py`,
`sdd-task-state.py` y `sdd-release.py`. Lo manual es la conducta del agente (no
autovalidar, no ajustar un TC que falla, no teclear el SHA).

> [!IMPORTANT]
> **El sello se gana, no se declara.** El `Estado: VALIDADO` del plan lo escribe
> `sdd-seal.py` solo con sus condiciones; degrada a `BORRADOR` si el archivo se altera
> a mano. Los gates en negativo de este tramo viven en [`cu-09-gates.md`](cu-09-gates.md);
> aquí se verifica el camino **en positivo**.

---

## CU-6.a — Generar el plan técnico desde el spec

**Precondición:** `_spec.md` validado, sin `[INCOMPLETO]`/`[CRÍTICO]`/`[INFERIDO]`.
**Mecanismo:** skill `wf-prepare-plan generate` → subagente **`plan-architect`**.
Output: `features/<n>/plan/<n>_plan.md`.

1. Le pides generar el plan de la feature.
   → **Esperado:** `plan-architect` traduce el "qué funcional" del spec al "cómo
     técnico" fundamentado en el repo; genera `_plan.md` en estado **BORRADOR** (no se
     autovalida).

**Resultado:** PASS si genera el plan en BORRADOR cubriendo los CAs · FALLO si nace
`VALIDADO` por su cuenta, o mete decisiones sin base en el repo.
**Desviación → reportar:** issue citando `CU-6.a`.

## CU-6.b — Validar el plan (gate formal + deuda asumida)

**Precondición:** `_plan.md` en BORRADOR.
**Mecanismo:** skill `wf-plan-validate` → subagente **`plan-auditor`**; el sello lo
escribe `sdd-seal.py`.

1. Le pides validar el plan.
   → **Esperado:** `plan-auditor` lo audita contra el spec, el handoff de Design y
     `kb-plan-expert`; si cumple las condiciones, **`sdd-seal.py`** lo sella `VALIDADO`;
     si no, lo deja `BORRADOR` con los items a corregir. La deuda técnica asumida queda
     como `TD-00X`, no como gap silencioso.

**Resultado:** PASS si el veredicto refleja el estado real y el sello lo pone el script
· FALLO si "valida" sin auditar, o sella a mano.
**Desviación → reportar:** issue citando `CU-6.b`.

## CU-6.c — Generar las tasks desde el plan

**Precondición:** `_plan.md` en `VALIDADO` sin enmiendas pendientes.
**Mecanismo:** skill `wf-prepare-tasks generate` → subagente **`task-generator`**.
Output: `features/<n>/tasks/<n>_tasks.md`.

1. Le pides generar las tasks.
   → **Esperado:** `task-generator` produce `_tasks.md` con tasks accionables,
     dependencias, DoD y referencia al `Spec CA` de cada una.

**Resultado:** PASS si genera tasks trazables al plan y a los CAs · FALLO si genera
tasks sobre un plan no validado (eso es `CU-9.c`), o sin trazar al CA.
**Desviación → reportar:** issue citando `CU-6.c`.

## CU-6.d — Ejecutar las tasks con estado y commit

**Precondición:** `_tasks.md` generado; plan origen vigente.
**Mecanismo:** skill `wf-task-run` (director de ejecución; estado vía
`sdd-task-state.py`, owners según `stack` de `project-init.json`). Commit por task.

1. Le pides ejecutar las tasks ("implementa la siguiente").
   → **Esperado:** selecciona la task elegible (`--next` por defecto), la delega a su
     **Owner agent** (agente del overlay de stack, u orquestador en modo agnóstico),
     valida el DoD con evidencia, y registra estado y un **commit por task** con
     mensaje trazable `T-00X [CA-XXX]`. **No marca estados a mano**: todo pasa por
     `sdd-task-state.py` (autor ≠ marcador).

**Resultado:** PASS si ejecuta con estado persistente y commit trazable · FALLO si
marca estados a mano, reordena tasks, o ejecuta una retenida por enmienda (ver `CU-9.k`).
**Desviación → reportar:** issue citando `CU-6.d`.

## CU-6.e — Derivar el plan de QA desde los CAs

**Precondición:** un `_spec.md` fiable (puede derivarse desde que el spec lo es).
**Mecanismo:** skill `wf-qa-plan generate` → subagente **`qa-engineer`**. Output:
`features/<n>/tasks/<n>_qa_plan.md`.

1. Le pides el plan de pruebas de la feature.
   → **Esperado:** deriva la matriz `TC-XXX` **desde los CAs** del spec (trazable
     CA→TC), sin inventar casos fuera del contrato.

**Resultado:** PASS si los TC trazan a los CAs · FALLO si fabrica casos sin CA, o
ignora algún CA.
**Desviación → reportar:** issue citando `CU-6.e`.

## CU-6.f — Verificar cobertura real con evidencia ejecutada

**Precondición:** feature implementada y `_qa_plan.md` existente.
**Mecanismo:** skill `wf-qa-verify` → **`qa-engineer`**. Output: `<n>_qa_report.md` con
veredicto `APTO` / `APTO_CON_RESERVAS` / `NO_APTO`.

1. Le pides verificar que la feature pasa QA.
   → **Esperado:** ejecuta los tests de cada TC, registra evidencia y escribe el
     veredicto. **Regla de oro: cobertura sin evidencia ejecutada no existe.**
2. Un test falla contra un CA.
   → **Esperado:** ese TC es **`DIVERGENTE`** → la acción es `/wf-bug` citando el CA;
     **no toca código ni test ni "ajusta" el TC**.
3. Veredicto `APTO`/`APTO_CON_RESERVAS`.
   → **Esperado:** pide el rol aprobador con `AskUserQuestion` (default `QA`) y solo
     entonces escribe `Aprobado por:`; **no autoaprueba** si no respondes; con
     `NO_APTO` no escribe la línea.

**Resultado:** PASS si verifica con evidencia, marca divergencias sin tocarlas y no
autoaprueba · FALLO si ajusta un TC que falla, o sella la aprobación sin respuesta.
**Desviación → reportar:** issue citando `CU-6.f`.

## CU-6.g — Vincular el cierre a producción (release)

**Precondición:** QA con veredicto `APTO` o `APTO_CON_RESERVAS`.
**Mecanismo:** skill `wf-release` (**sin agente**, mecánico); gate y SHA los aplica
`sdd-release.py`. Output: `features/<n>/tasks/<n>_release.md`.

1. Le pides marcar la release de la feature.
   → **Esperado:** `sdd-release.py` captura el **commit SHA con git** (no se teclea),
     registra la coordenada en `_release.md` y, si pides tag, lo crea **solo con
     confirmación**.
2. La feature no tiene QA `APTO` (o es `NO_APTO`).
   → **Esperado:** **rechaza (exit 2)**; no insiste, remite a cerrar QA con `/wf-qa-verify`
     (o `/wf-bug` si hay divergencias). Releasar algo sin QA está prohibido.

**Resultado:** PASS si solo cierra con QA apto y el SHA lo da git · FALLO si releasa sin
QA apto, o teclea/inventa el SHA.
**Desviación → reportar:** issue citando `CU-6.g`.

---

## CU-6.h — Design es saltable: feature sin UI pasa a Plan directo

**Precondición:** un `_spec.md` validado de una feature **sin superficie de UI visible**
(p. ej. un job de backend), sin `DESIGN.md` ni artefactos de Design.
**Mecanismo:** skill `wf-prepare-plan` aplica la **regla canónica de `kb-plan-expert`**
sobre si Design es obligatorio.

1. Le pides el plan de esa feature sin UI.
   → **Esperado:** la regla decide que **no requiere handoff de Design**; genera el plan
     dejando trazado que es una feature sin superficie UI, **sin exigir `DESIGN.md`**.
2. Le pides el plan de una feature **con** UI cuyos artefactos de Design **faltan**.
   → **Esperado:** se detiene con *"❌ La feature requiere handoff de Design pero falta
     uno o más artefactos (`DESIGN.md`, `<feature>_flows.md`, `<feature>_views.md`)…"*
     y pide ejecutar `/wf-design-system` y `/wf-design-feature-prototype` primero.

**Resultado:** PASS si salta Design solo cuando no hay UI y lo exige cuando sí · FALLO
si bloquea una feature sin UI por falta de Design, o planifica una con UI sin su handoff.
**Desviación → reportar:** issue citando `CU-6.h`.

## CU-6.i — Sello degradado al editar el plan a mano

**Precondición:** un `_plan.md` sellado `VALIDADO`.
**Mecanismo:** `sdd-seal.py` (el sello vale solo con sus condiciones; la edición manual
lo invalida).

1. Editas el contenido del plan a mano y vuelves a pedir avanzar (tasks).
   → **Esperado:** el plan se considera **degradado a BORRADOR** (el sello ya no es
     válido); el agente **no "re-sella" por su cuenta** ni avanza — te remite a
     re-validar con `/wf-plan-validate` (enlaza con el gate `CU-9.c`).

**Resultado:** PASS si detecta la alteración y no re-sella solo · FALLO si trata el plan
como vigente tras editarlo, o lo re-sella a mano.
**Desviación → reportar:** issue citando `CU-6.i`.

## CU-6.j — Máquina de estados de tasks: dependencias y reapertura

**Precondición:** un `_tasks.md` con dependencias entre tasks.
**Mecanismo:** `sdd-task-state.py` (transiciones válidas; autor ≠ marcador).

1. Le pides ejecutar una task cuyas dependencias **no están HECHAS**.
   → **Esperado:** no la ejecuta; informa qué dependencias faltan (`check`) y se detiene
     — `next` la salta como no elegible.
2. Le pides reabrir/re-ejecutar una task ya `HECHA`.
   → **Esperado:** solo la reabre con `--force` explícito; sin `--force`, respeta el
     estado y no la re-ejecuta. Nunca marca estados a mano (todo vía
     `sdd-task-state.py`).

**Resultado:** PASS si respeta deps y solo reabre con `--force` · FALLO si ejecuta con
dependencias abiertas, o marca/reabre estados a mano.
**Desviación → reportar:** issue citando `CU-6.j`.

## CU-6.k — Prepare-plan: resolución de stack y gate de accesibilidad del handoff

**Precondición:** según el sub-escenario — `.sdd/project-init.json` con `stack` `null` / `agnostico` /
especialista (p. ej. KMM); o una feature con UI cuyo `DESIGN.md` no tiene `## Accessibility`.
**Mecanismo:** `wf-prepare-plan` (Paso 2 resolución de stack; Paso 4 handoff de Design) → `plan-architect`.

1. El proyecto tiene `stack: null` (entrevista técnica no hecha).
   → **Esperado:** **detiene** pidiendo `/wf-project-init` → "Completar / ampliar" (perfil Desarrollo); no genera el plan sin stack.
2. El proyecto tiene `stack: agnostico`.
   → **Esperado:** modo genérico — **no** exige ningún `<stack>_project_state.md`; funda el plan en la exploración del repo y `kb-plan-expert`.
3. El proyecto tiene stack especialista (KMM) **sin** `<stack>_project_state.md`.
   → **Esperado:** **detiene** pidiendo `/wf-<stack>-init` antes de producir el plan.
4. La feature requiere Design y el `DESIGN.md` no tiene la sección `## Accessibility`.
   → **Esperado:** **detiene** pidiendo validar/corregir Design antes del plan.

**Resultado:** PASS si ramifica por stack (null/agnostico/especialista) y exige `## Accessibility` cuando
hay Design · FALLO si genera el plan con `stack: null`, exige project_state en agnóstico, o planifica con un `DESIGN.md` sin Accessibility.
**Desviación → reportar:** issue citando `CU-6.k`.

## CU-6.l — Plan-validate: aprobación de deuda técnica y sellado determinista

**Precondición:** un `_plan.md` en BORRADOR; según el sub-escenario con sección `## Deuda técnica asumida`
(`TD-00X` `Aprobada por: PENDIENTE`), con `Spec origen` ausente, o que el auditor apruebe/falle la verificación mecánica.
**Mecanismo:** `wf-plan-validate` → `plan-auditor`; el `Estado:` lo escribe **solo** `sdd-seal.py`; las
aprobaciones (deuda y gate) vía `AskUserQuestion`.

1. El plan declara `TD-00X` con `Aprobada por: PENDIENTE`.
   → **Esperado:** presenta cada TD (decisión, riesgo asumido) y pide decisión explícita; **Aprobar** →
     escribe `<rol> (<fecha>)`; **Rechazar** → no sella y remite a regenerar; **no autoaprueba** (si queda `PENDIENTE`, el sellado falla).
2. El auditor devuelve `OK`.
   → **Esperado:** `sdd-seal.py … --seal` exit 0 → `Estado: VALIDADO` (lo escribe el script, **no** a mano) +
     pide el rol aprobador (default `Tech Lead`) y escribe `Aprobado por:`; no autoaprueba sin respuesta.
3. El auditor devuelve `OK` pero la verificación mecánica **falla** (exit 2: CA sin cubrir, gap abierto…).
   → **Esperado:** el plan queda `BORRADOR`; muestra los checks `✗`; no sugiere pasar a tasks.
4. Falta el `Spec origen` resoluble.
   → **Esperado:** **detiene**; no valida un plan sin su spec.

**Resultado:** PASS si las TD requieren aprobación humana, el sello lo pone el script y exit 2 deja
`BORRADOR` · FALLO si autoaprueba una TD, sella a mano, o valida con exit 2 / sin `Spec origen`.
**Desviación → reportar:** issue citando `CU-6.l`.

## CU-6.m — Task-run: verificación ejecutable del DoD y disciplina de commit

**Precondición:** un `_tasks.md` con plan vigente y tasks por ejecutar.
**Mecanismo:** `wf-task-run` (Paso 6 verificación; Paso 8 commit) → Owner agent / orquestador; `sdd-task-state.py`.

1. El owner reporta una task como hecha.
   → **Esperado:** no acepta el reporte sin evidencia — verifica que los archivos declarados existen y
     ejecuta build/tests del módulo (comandos de `<stack>_project_state.md` o runner detectado); marca `HECHA` solo si el DoD se cumple con evidencia.
2. No hay forma razonable de ejecutar build/tests.
   → **Esperado:** registra "verificación ejecutable: no disponible" explícitamente; **nunca** presenta la task como verificada sin evidencia.
3. Es una task `Layer: test` en orden TDD.
   → **Esperado:** el DoD esperado es **RED** (compila y falla con mensaje claro); verde prematuro = fallo de DoD.
4. Commitea la task.
   → **Esperado:** un commit por task con mensaje `T-00X [CA-XXX]`, añadiendo **solo** lo que la task tocó +
     el `_tasks.md`; nunca `git add -A`; si hay cambios ajenos en el working tree, los deja fuera y avisa.

**Resultado:** PASS si verifica con evidencia, declara la ausencia de ejecución y commitea acotado · FALLO
si acepta un DoD sin evidencia, presenta como verificado lo que no ejecutó, o commitea con `git add -A`.
**Desviación → reportar:** issue citando `CU-6.m`.

## CU-6.n — Deuda técnica de plan a tasks a owner

**Precondición:** un `_plan.md` `VALIDADO` con sección `## Deuda técnica asumida` (`TD-00X` aprobada); tasks por generar/ejecutar.
**Mecanismo:** `wf-prepare-tasks` (Paso 4 propagación) + `wf-task-run` (Paso 5 restricción) → `task-generator` / Owner.

1. Generas las tasks de un plan con `TD-00X`.
   → **Esperado:** cada task cuyo componente aparece en "Componentes afectados" de la TD lleva
     `- **Deuda asumida:** TD-00X — <título>`; no se "resuelve" la limitación al trocear.
2. Ejecutas una task con deuda asumida.
   → **Esperado:** `task-run` pasa la TD al owner como **restricción a respetar** (implementa conforme a la
     decisión documentada); si el owner cree que la deuda ya no aplica o hay mejor salida, **lo reporta, no lo decide**.

**Resultado:** PASS si la deuda se propaga a las tasks afectadas y el owner la respeta como restricción ·
FALLO si las tasks ignoran la TD, o el owner "resuelve" la limitación por su cuenta.
**Desviación → reportar:** issue citando `CU-6.n`.

## CU-6.o — QA: anti-fabricación de cobertura (qa-plan y qa-verify)

**Precondición:** un `_spec.md` fiable (qa-plan); una feature implementada con `_qa_plan.md` (qa-verify).
**Mecanismo:** `wf-qa-plan` (Paso 4) / `wf-qa-verify` (Pasos 3-4) → `qa-engineer`. `wf-qa-verify` es el único escritor del campo `Estado` del TC.

1. (qa-plan) El spec sugiere un comportamiento que necesita prueba pero **ningún CA** lo respalda.
   → **Esperado:** **no** deriva el TC; lo lista como **gap de spec** y recomienda `wf-spec-delta`; no fabrica un caso sin CA.
2. (qa-verify) Un TC automatizable no tiene test que lo ejercite.
   → **Esperado:** `SIN_COBERTURA` (no `CUBIERTO`).
3. (qa-verify) No hay forma de ejecutar los tests.
   → **Esperado:** declara "verificación ejecutable: no disponible"; los TC quedan `PENDIENTE`, **nunca** `CUBIERTO`.
4. (qa-verify) Un TC manual.
   → **Esperado:** `CUBIERTO` solo con confirmación humana explícita en la sesión (registrada como evidencia); sin confirmación, `MANUAL_PENDIENTE`.

**Resultado:** PASS si no deriva TCs sin CA y nunca marca `CUBIERTO` sin evidencia/confirmación · FALLO si
fabrica un TC sin CA, marca `CUBIERTO` sin test ejecutado, o da por bueno un manual sin confirmación.
**Desviación → reportar:** issue citando `CU-6.o`.
