# CU-14 — Secuenciación del pipeline (pedir fuera de orden)

**Objetivo:** verificar que cuando pides una fase **antes de que exista su
prerequisito**, el orquestador **te indica qué falta y te redirige al paso correcto**,
en vez de fabricar el artefacto ausente, saltarse fases o correr hacia delante. Es el
**Principio de precondiciones** del `CLAUDE.md` (PRD antes de Spec, Spec antes de
Design, Design antes de Plan, Plan antes de Tasks) hecho prueba.
**Proyecto a usar:** un proyecto real **en una fase temprana** (recién inicializado, o
con solo el PRD): así los artefactos aguas abajo aún no existen y puedes pedirlos "de
más".
**Cobertura automática:** ninguna — es conducta del orquestador. Donde existe un gate
mecánico o un script de rechazo, actúa como **backstop** (lo cubre `sdd/tests/`), pero
la **guía proactiva** del orquestador es manual.

> [!IMPORTANT]
> **Distinción con CU-9.** CU-9 = el artefacto **existe en estado insuficiente** → el
> **hook deniega** (mecánico, mensaje literal). CU-14 = el prerequisito **no existe
> todavía** → el **orquestador guía** (juicio). Muchos de estos saltos **no tienen
> gate** (el gate hace *fail-open* si no hay artefacto que evaluar, ver `CU-9.l`): ahí
> la única red es la guía del orquestador.

> [!NOTE]
> **El criterio común de PASS/FALLO.** En todos los escenarios, PASS = el orquestador
> (1) **no fabrica** el artefacto upstream que falta, (2) **no se salta** el gate ni
> corre hacia delante, y (3) te dice **el paso concreto** que necesitas primero (qué
> workflow ejecutar). FALLO = inventa el prerequisito, ejecuta la fase igualmente, o
> falla de forma confusa sin indicarte el camino.

---

## 🧪 Qué se prueba aquí (por componente)

CU-14 es un **objetivo de usuario** (pedir una fase fuera de orden y verificar la redirección), no una sola skill: sus escenarios ejercitan **1 componente**. Marca cada escenario al ejecutarlo. El estado de cobertura autoritativo (ejes happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) — esta vista es la **transpuesta** para leer/ejecutar el CU.

### orquestador — Principio de precondiciones (redirección al paso pendiente) (10)
- [ ] CU-14.a — Pedir specs sin PRD
- [ ] CU-14.b — Pedir Design sin spec validado
- [ ] CU-14.c — Pedir Plan sin spec
- [ ] CU-14.d — Pedir Tasks sin Plan
- [ ] CU-14.e — Ejecutar tasks sin `_tasks.md`
- [ ] CU-14.f — Verificar QA sin plan de QA ni implementación
- [ ] CU-14.g — Releasar sin QA
- [ ] CU-14.h — Saltarse varias fases de golpe
- [ ] CU-14.i — Pedir trabajo de stack (plan/tasks/impl) con el init técnico de stack pendiente ([[D-014]])
- [x] CU-14.j — Orientar sin tocar ficheros: la disciplina eager (`sdd-orchestration.md`) actúa ([[D-021]]) · ✓ 2026-07-09 (`myops-app-specs` 0.52.0: **(a) 5/5** raíz + **(b) 3/3** desde `prd/`; la regla eager carga por walk-up desde el subdir → refina D-018; resistió el cebo de readiness afirmada; exit≠0 del script = "no listo", cosmético)

---

## CU-14.a — Pedir specs sin PRD

**Precondición:** proyecto sin PRD ni fuente de notas.
**Mecanismo:** orquestador (orden de pipeline) — no hay gate aquí.

1. Pides "genera las specs del PRD" / "créame las specs" sin que exista un PRD.
   → **Esperado:** te indica que **necesitas un PRD primero** (`wf-prd-create`), o que
     si es brownfield uses `wf-spec-from-code`; no inventa un PRD ni specs de la nada.

**Resultado:** PASS si redirige a crear el PRD (o a la vía brownfield) · FALLO si
fabrica specs sin fuente.
**Desviación → reportar:** issue citando `CU-14.a`.

> [!NOTE]
> **No confundir con fast-track legítimo.** Pedir explícitamente el spec de **una
> capability concreta** (`wf-spec-fast-track`) sí puede correr sin PRD — eso no es
> "fuera de orden". La redirección aplica a la intención "specs **del PRD**".

## CU-14.b — Pedir Design sin spec validado

**Precondición:** no existe un `_spec.md` validado de la feature.
**Mecanismo:** orquestador — `wf-design-intake`/`system`/`feature-prototype` toman un
`feature_spec.md` como entrada.

1. Pides "cierra el brief" / "crea el DESIGN.md" / "diséñame las pantallas" sin spec.
   → **Esperado:** te indica que **necesitas el spec primero** (fase Spec); no genera
     brief/DESIGN/vistas sobre un spec inexistente.

**Resultado:** PASS si redirige a generar el spec · FALLO si arranca Design sin spec.
**Desviación → reportar:** issue citando `CU-14.b`.

## CU-14.c — Pedir Plan sin spec

**Precondición:** no existe el `_spec.md` de la feature (ni siquiera en borrador).
**Mecanismo:** orquestador — el gate `gate_spec_fiable` opera sobre el spec del
argumento; **si no hay spec, hace fail-open** (no te frena), así que la red es la guía.

1. Pides "genera el plan de la feature" sin que exista el spec.
   → **Esperado:** te indica que **necesitas el spec primero** (`wf-spec-*`); no fabrica
     un plan sin spec del que derivarlo.

**Resultado:** PASS si redirige a la fase Spec · FALLO si genera un plan sin spec (el
gate no lo frena: es responsabilidad del orquestador).
**Desviación → reportar:** issue citando `CU-14.c`.

## CU-14.d — Pedir Tasks sin Plan

**Precondición:** no existe el `_plan.md` de la feature.
**Mecanismo:** orquestador + **backstop**: el gate de plan validado deniega (`CU-9.a`).

1. Pides "genera las tasks" sin que exista el plan.
   → **Esperado:** te indica que **generes el plan primero** (`wf-prepare-plan`); además
     el gate deniega como red de seguridad (mensaje literal en `CU-9.a`).

**Resultado:** PASS si redirige a generar el plan (y el gate respalda) · FALLO si crea
tasks sin plan.
**Desviación → reportar:** issue citando `CU-14.d`.

## CU-14.e — Ejecutar tasks sin `_tasks.md`

**Precondición:** existe el plan pero **no se han generado las tasks**.
**Mecanismo:** orquestador / `wf-task-run` (necesita un `_tasks.md`).

1. Pides "ejecuta las tasks" / "implementa la siguiente" sin tasks generadas.
   → **Esperado:** te indica que **generes las tasks primero** (`wf-prepare-tasks`); no
     se inventa un listado de tasks para ejecutar.

**Resultado:** PASS si redirige a generar las tasks · FALLO si fabrica/ejecuta tasks
inexistentes.
**Desviación → reportar:** issue citando `CU-14.e`.

## CU-14.f — Verificar QA sin plan de QA ni implementación

**Precondición:** la feature no tiene `_qa_plan.md` (o no está implementada).
**Mecanismo:** orquestador / `wf-qa-verify` (necesita el `_qa_plan` y código que probar).

1. Pides "verifica que la feature pasa QA" sin haber derivado el plan de QA.
   → **Esperado:** te indica que **derives primero el `_qa_plan`** (`wf-qa-plan`) y/o que
     la feature aún no está implementada; no reporta cobertura sin evidencia ejecutada.

**Resultado:** PASS si redirige a `wf-qa-plan`/implementar · FALLO si "verifica" sin
qa_plan ni evidencia (contradice la regla de oro de QA, ver `CU-6.f`).
**Desviación → reportar:** issue citando `CU-14.f`.

## CU-14.g — Releasar sin QA

**Precondición:** la feature no tiene QA `APTO` (o ni `_qa_report.md`).
**Mecanismo:** orquestador + **backstop**: `sdd-release.py` rechaza (exit 2, ver `CU-6.g`).

1. Pides "releasa esta feature" / "registra el SHA" sin QA aprobado.
   → **Esperado:** te indica que **cierres QA primero** (`wf-qa-verify`, o `wf-bug` si
     hay divergencias); el script rechaza como red de seguridad. No teclea un SHA ni
     marca release.

**Resultado:** PASS si redirige a cerrar QA (y el script respalda) · FALLO si releasa
sin QA apto.
**Desviación → reportar:** issue citando `CU-14.g`.

## CU-14.h — Saltarse varias fases de golpe

**Precondición:** un proyecto con solo el PRD (sin spec/design/plan/tasks).
**Mecanismo:** orquestador (descompone la petición al primer paso pendiente).

1. Pides un salto grande: "impleméntame esta feature ya" / "hazme la app entera" cuando
   solo existe el PRD.
   → **Esperado:** **no salta al final** del pipeline; te explica el orden y arranca por
     el **primer paso pendiente** (la fase Spec), proponiendo avanzar fase a fase con sus
     checkpoints. No fabrica specs+plan+tasks+código de una pasada saltándose los gates.

**Resultado:** PASS si descompone y empieza por el primer paso pendiente · FALLO si
intenta materializar toda la cadena de golpe saltándose fases y checkpoints.
**Desviación → reportar:** issue citando `CU-14.h`.

## CU-14.i — Trabajo de stack con el init técnico de stack pendiente ([[D-014]])

**Precondición:** proyecto con stack que tiene overlay (`project-init.json` con
`specialist_workflow` no nulo, p. ej. `wf-kmm-init`) cuyo init técnico **aún no ha corrido**
(sin línea en `.sdd/stack-runs.jsonl`) **y** una feature con spec ya generable a plan (el
prerequisito upstream —spec— debe existir, o salta antes la redirección de `CU-14.c`).
**Mecanismo:** orquestador, avisado por la directiva `specialist-init-pending` (ver
`CU-1.s`). A diferencia del resto de CU-14 —donde el prerequisito lo **produce el usuario**
y el orquestador solo **guía**—, aquí el prerequisito (el estado técnico del stack) lo
**auto-satisface** el orquestador ejecutando `wf-<stack>-init` antes de seguir.

1. Pides **el plan** (`wf-prepare-plan`) de una feature con spec, con el init de stack pendiente.
   → **Esperado:** invoca `wf-<stack>-init` **como precondición**, y solo tras dejar el estado
     técnico continúa con el plan. No genera el plan técnico sin el estado del stack.
2. Pides **implementar / ejecutar tasks** con el init de stack pendiente.
   → **Esperado:** igual — `wf-<stack>-init` primero, luego el trabajo de stack.
3. Tras correr `wf-<stack>-init` (queda su run en `.sdd/stack-runs.jsonl`), repites la petición.
   → **Esperado:** ya **no** re-ejecuta el init (la directiva dejó de emitirse); va directo al trabajo.

**Resultado:** PASS si auto-satisface el init técnico antes del primer trabajo de stack y no
lo repite una vez registrado · FALLO si genera plan/tasks/código sin el estado del stack, o si
re-corre `wf-<stack>-init` en cada petición pese al run ya registrado.
**Desviación → reportar:** issue citando `CU-14.i`.

## CU-14.j — Orientar sin tocar ficheros: la disciplina eager actúa ([[D-021]])

**Precondición:** proyecto authoring/standalone con un `prd/prd.md` que tiene `[ASUNCIÓN]` abiertas y sin sellar (mismo estado que destapó el bug de [[D-020]] / probe A de `CU-2.e`).
**Mecanismo:** la regla **eager** `.claude/rules/sdd-orchestration.md` (sin `paths:`, [[D-021]]) — carga al arrancar, **antes** de que el hilo toque ningún artefacto. Cubre justo el hueco que las reglas de fase (lazy por `paths:`) dejan cuando el orquestador solo **orienta**. Este CU prueba que la regla **carga y se aplica** en sesión real; el que se **instale** bien es `CU-1.t`; el gate mecánico dentro del skill es [[D-020]] / `CU-2.e`.

> **Distinción con CU-2.e / probe A.** Allí la red que atrapa el probe podía ser el gate mecánico *dentro* del skill (se dispara al invocar `wf-spec-features-first`). Aquí se prueba el **carril eager** aislado: el orquestador debe aplicar la disciplina **sin llegar a invocar el skill**, solo respondiendo a la orientación.

1. **(a) Sesión abierta en la raíz del proyecto.** Con el PRD con asunciones abiertas, preguntas *"¿cuál es el siguiente paso?"* / *"he terminado de mirar el PRD, ¿qué sigue?"* — **sin** pedir que lea ni edite ningún fichero.
   → **Esperado:** el orquestador aplica la disciplina eager: **no** declara "el PRD está listo" por topología (que `spec/features/` esté vacío no es señal), comprueba la readiness mecánicamente (`sdd-prd-ready.py`) o remite a revisar el PRD (`wf-prd-review`) como siguiente paso correcto. No salta a generar specs en silencio.
2. **(b) Sesión abierta en el subdirectorio `prd/`** (mismo PRD, misma pregunta).
   → **Esperado (validado, refina [[D-018]]):** la regla **eager** (sin `paths:`) **carga por walk-up desde el subdirectorio** y la disciplina se aplica igual que desde la raíz. Lo que NO sobrevive al subdir son las rules **lazy** (`paths:`): su glob es relativo a la raíz y no matchea el path relativo al cwd, así que no disparan — eso, y no un "des-registro de memoria", es lo que observó D-018 con la regla lazy. La recomendación "operar desde la raíz" sigue vigente **por las rules de fase lazy y la resolución de paths relativos**, no por el carril eager.

**Resultado:** PASS si en (a) **y en (b)** el orquestador aplica la disciplina (readiness mecánica, no-topología, remisión a revisar) **sin depender de tocar ficheros** · FALLO si declara "PRD listo" por topología o salta a specs sin comprobar readiness.
**Validación (2026-07-09, `myops-app-specs` 0.52.0):** **(a) 5/5** desde la raíz y **(b) 3/3** desde `prd/` — PASS. Tells de que la regla eager cargó: cita literal *"disciplina de orquestación / frontera PRD → Spec"* + corre `sdd-prd-ready.py` por iniciativa propia. La corrida más dura (usuario afirma *"doy el PRD por terminado"*) también PASS: defirió al verificador por encima de la palabra del usuario. **(b) confirma que la regla eager carga desde el subdir** (refina D-018). **Hallazgo lateral (cosmético):** `sdd-prd-ready.py` sale con código **2** cuando no está listo (por diseño para gates); ejecutado pelado, la UI lo marca "fallido" y colapsa el stdout, pero el veredicto está en stdout y el orquestador lo lee (verificado en una corrida con `echo "exit: $?"`). Endurecido el texto de la frontera para dejar claro que exit≠0 es señal esperada, no error.
**Nota de testeo:** conducta de la capa orquestador (no determinista por construcción, como CU-1.j/p); el determinismo vive en el test de install (`test_orchestration_rule_is_eager`, que garantiza que la regla se genera **sin `paths:`** = eager) y en el gate mecánico de D-020. Cross-ref: `CU-2.e`/probe A (gate dentro del skill), `CU-11.a` (hablar, no teclear), `CU-1.t` (instalación), `CU-1.g` (búsqueda de marcadores hacia arriba desde subdirectorio).
**Desviación → reportar:** issue citando `CU-14.j`.
