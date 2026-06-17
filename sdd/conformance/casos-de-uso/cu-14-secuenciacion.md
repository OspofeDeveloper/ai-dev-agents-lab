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

### orquestador — Principio de precondiciones (redirección al paso pendiente) (8)
- [ ] CU-14.a — Pedir specs sin PRD
- [ ] CU-14.b — Pedir Design sin spec validado
- [ ] CU-14.c — Pedir Plan sin spec
- [ ] CU-14.d — Pedir Tasks sin Plan
- [ ] CU-14.e — Ejecutar tasks sin `_tasks.md`
- [ ] CU-14.f — Verificar QA sin plan de QA ni implementación
- [ ] CU-14.g — Releasar sin QA
- [ ] CU-14.h — Saltarse varias fases de golpe

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
