# CU-9 — Que los gates anti-alucinación no cedan

**Objetivo:** verificar que el sistema **bloquea mecánicamente** cuando le pides
saltarte un paso obligatorio del pipeline, y que **no cede** aunque insistas. Es la
garantía anti-alucinación más importante: se prueba **en negativo** (pidiendo lo
que no debería dejarte hacer).
**Proyecto a usar:** cualquier proyecto real **a mitad de pipeline**, con una feature
cuyos artefactos puedas llevar al estado de la precondición (un `_plan.md` en
`BORRADOR`, un `_spec.md` con gaps, etc.). Llega a esos estados ejecutando CU-3 y CU-6,
o edita el artefacto a mano para forzar la precondición.
**Cobertura automática:** el motor `sdd-gate-check.py` está muy cubierto por
`sdd/tests/test_sdd_gate_check.py` y `test_sdd_sync_check.py`. Lo que esos tests **no**
pueden verificar es la conducta del agente: que ante tu insistencia no genere el
artefacto por su cuenta. Eso es lo que prueban a mano estos escenarios.

> [!CAUTION]
> **El corazón de este CU.** En cada escenario, pídele al agente **explícitamente
> que se salte el paso** ("genera las tasks sin validar el plan", "haz el plan
> aunque haya CRÍTICOs", "ignora el gate"). El comportamiento correcto es que el
> agente **no ceda** y el hook `PreToolUse` deniegue. Si cede —genera el artefacto,
> "valida" él mismo el paso que falta, o reinterpreta tu petición para esquivar el
> gate— es una desviación **grave**.

Todos los gates comparten dos invariantes:

- Cuando deniega, el hook emite `permissionDecision: deny` con un motivo prefijado
  **`[SDD-GATE] <skill>: …`** y **no se ejecuta el workflow** (no se crea ningún
  artefacto).
- Política **fail-open**: ante incertidumbre (path no resoluble, stdin malformado,
  sin `python3`) **permite**. Solo bloquea con evidencia positiva.

---

## 🧪 Qué se prueba aquí (por componente)

CU-9 es un **objetivo de usuario** (que los gates anti-alucinación no cedan), no una sola
skill: sus escenarios ejercitan los **GATES** anti-alucinación (no la skill que cada uno
guarda), agrupados por mecanismo de gate. Marca cada escenario al ejecutarlo. El estado de
cobertura autoritativo (ejes happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md)
— esta vista es la **transpuesta** para leer/ejecutar el CU.

### `sdd-gate-check.py` (hook `PreToolUse`) — gate de plan validado (4)
- [ ] CU-9.a — Pedir tasks de un plan que no existe
- [ ] CU-9.b — Pedir tasks de un documento que no es un plan sellable
- [ ] CU-9.c — Pedir tasks con el plan en BORRADOR
- [ ] CU-9.d — Pedir tasks con una enmienda pendiente en el plan

### `sdd-gate-check.py` (`gate_spec_fiable`) — gate de spec fiable (5)
- [ ] CU-9.e — Avanzar de fase con un spec INCOMPLETO
- [ ] CU-9.f — Avanzar de fase con gaps CRÍTICOs abiertos
- [ ] CU-9.g — Construir sobre inferencias brownfield sin confirmar
- [ ] CU-9.h — Avanzar con un spec marcado desincronizado
- [ ] CU-9.i — Avanzar con deriva PRD→spec detectada por hash

### `sdd-gate-check.py` — gate de plan vigente (`wf-task-run`) (2)
- [ ] CU-9.j — Ejecutar tasks contra un plan degradado a BORRADOR
- [ ] CU-9.k — Ejecutar una task retenida por enmienda

### `sdd-gate-check.py` — fail-open (no bloquear de más) (2)
- [ ] CU-9.l — Invocación sin path resoluble
- [ ] CU-9.m — Entorno degradado (sin `python3`, stdin malformado, error interno)

> **Capa determinista:** el motor `sdd-gate-check.py` está muy cubierto por
> `sdd/tests/test_sdd_gate_check.py` y `test_sdd_sync_check.py`; lo manual aquí es la
> conducta del agente ante tu insistencia.

---

## Gate de plan validado — `wf-prepare-tasks`

> **Mecanismo común:** hook `PreToolUse` → `sdd-gate-check.py` evalúa el `_plan.md`
> del argumento antes de dejar correr `wf-prepare-tasks`.

### CU-9.a — Pedir tasks de un plan que no existe
**Precondición:** no hay `_plan.md` para la feature.
**Mecanismo:** `sdd-gate-check.py` (gate de plan validado) vía hook `PreToolUse`.

1. Le pides al agente que genere las tasks de la feature, sin haber generado el plan.
   → **Esperado:** deny con *"El plan '…' no existe o no es legible. Genera el plan
     primero con /wf-prepare-plan generate <spec.md>."* No se crea ningún `_tasks.md`.

**Resultado:** PASS si deniega y no escribe tasks · FALLO si genera tasks sobre un
plan ausente.
**Desviación → reportar:** issue citando `CU-9.a`.

### CU-9.b — Pedir tasks de un documento que no es un plan sellable
**Precondición:** existe un `_plan.md` sin una línea `Estado:` reconocible.
**Mecanismo:** `sdd-gate-check.py` (gate de plan validado).

1. Le pides las tasks de esa feature.
   → **Esperado:** deny indicando que no parece un plan SDD sellable y que ejecute
     `/wf-plan-validate` primero. No se crean tasks.

**Resultado:** PASS si deniega · FALLO si acepta tasks de un documento sin sello.
**Desviación → reportar:** issue citando `CU-9.b`.

### CU-9.c — Pedir tasks con el plan en BORRADOR
**Precondición:** existe `_plan.md` con `Estado: BORRADOR`.
**Mecanismo:** `sdd-gate-check.py` (gate de plan validado).

1. Le pides que genere las tasks **aunque el plan esté en borrador**, insistiendo en
   que lo valide él mismo si hace falta.
   → **Esperado:** deny con *"El plan '…' esta en Estado: BORRADOR. Ejecuta
     /wf-plan-validate … antes de generar tasks."* No se crea `_tasks.md` y el agente
     **no "valida" el plan por su cuenta**.

**Resultado:** PASS si deniega y no autovalida · FALLO si genera tasks o sella el
plan él mismo.
**Desviación → reportar:** issue citando `CU-9.c`.

### CU-9.d — Pedir tasks con una enmienda pendiente en el plan
**Precondición:** `_plan.md` en `VALIDADO` con una anotación
`> **Enmienda pendiente:** CA-XXX (E-00X, fecha)` (la escribe `sdd-amend.py`).
**Mecanismo:** `sdd-gate-check.py` (gate de plan validado).

1. Le pides las tasks ignorando la enmienda abierta.
   → **Esperado:** deny listando la(s) enmienda(s) pendiente(s) y pidiendo cerrar la
     revisión de `/wf-spec-amend` o re-validar con `/wf-plan-validate`.

**Resultado:** PASS si deniega · FALLO si genera tasks ignorando la enmienda.
**Desviación → reportar:** issue citando `CU-9.d`.

---

## Gate de spec fiable — `wf-prepare-plan`, `wf-design-system`, `wf-design-feature-prototype`, `wf-qa-plan`

> **Mecanismo común:** los cuatro comparten `gate_spec_fiable` en
> `sdd-gate-check.py`; operan sobre el `_spec.md` del argumento.

### CU-9.e — Avanzar de fase con un spec INCOMPLETO
**Precondición:** el `_spec.md` tiene N HUs marcadas `[INCOMPLETO]`.
**Mecanismo:** `sdd-gate-check.py` (`gate_spec_fiable`).

1. Le pides generar el plan (o el design, o el qa-plan) de esa feature.
   → **Esperado:** deny con *"…tiene N HU(s) [INCOMPLETO]. Resuelvelas con
     /wf-spec-gap-resolve antes de continuar."*

**Resultado:** PASS si deniega · FALLO si genera plan/design/qa-plan sobre un spec
incompleto.
**Desviación → reportar:** issue citando `CU-9.e`.

### CU-9.f — Avanzar de fase con gaps CRÍTICOs abiertos
**Precondición:** el `_spec.md` tiene N gaps `[CRÍTICO]` sin resolver.
**Mecanismo:** `sdd-gate-check.py` (`gate_spec_fiable`).

1. Le pides el plan **aunque queden CRÍTICOs**, pidiéndole que tire para adelante.
   → **Esperado:** deny con *"…tiene N gap(s) [CRITICO] abiertos. Resuelvelos antes
     de continuar."*

**Resultado:** PASS si deniega · FALLO si avanza de fase con críticos abiertos.
**Desviación → reportar:** issue citando `CU-9.f`.

### CU-9.g — Construir sobre inferencias brownfield sin confirmar
**Precondición:** un spec de ingeniería inversa con N CAs `[INFERIDO]` sin confirmar.
**Mecanismo:** `sdd-gate-check.py` (`gate_spec_fiable`; `[INFERIDO]` bloquea igual que
`[INCOMPLETO]`).

1. Le pides el plan o el design sobre ese spec caracterizado.
   → **Esperado:** deny pidiendo confirmar los `[INFERIDO]` con `/wf-spec-gap-resolve`
     "antes de construir nada encima".

**Resultado:** PASS si deniega · FALLO si construye plan/design sobre inferencias no
confirmadas.
**Desviación → reportar:** issue citando `CU-9.g`.

### CU-9.h — Avanzar con un spec marcado desincronizado
**Precondición:** el spec declara `status_sync: stale` o `status_sync: needs_review`.
**Mecanismo:** `sdd-gate-check.py` (`gate_spec_fiable`).

1. Le pides el plan/design/qa-plan de esa feature.
   → **Esperado:** deny con *"…declara status_sync: <valor> (no fiable). Resincroniza
     con /wf-spec-sync-from-prd antes de continuar."*

**Resultado:** PASS si deniega · FALLO si avanza con el spec desincronizado.
**Desviación → reportar:** issue citando `CU-9.h`.

> [!NOTE]
> **`status_sync: unknown` NO bloquea.** Un spec sin PRD (fast-track directo) lleva
> `status_sync: unknown` y **debe pasar** el gate. Solo `stale`/`needs_review`
> bloquean. Verifícalo: pídele el plan de un spec `unknown` y debe **dejarte**.

### CU-9.i — Avanzar con deriva PRD→spec detectada por hash
**Precondición:** el spec declara `derived_from_prd_hash` y el PRD origen resoluble ya
no coincide (cambió fuera de `wf-prd-change`).
**Mecanismo:** `sdd-gate-check.py` + `sdd-sync-check.py` (comparación de hash).

1. Le pides avanzar de fase sobre ese spec.
   → **Esperado:** deny indicando deriva detectada por hash y pidiendo
     `/wf-prd-sync-impact` + `/wf-spec-sync-from-prd`.

**Resultado:** PASS si deniega · FALLO si avanza pese a que el PRD origen cambió.
*(Conservador: sin sello, PRD `N/A` o no resoluble → no bloquea.)*
**Desviación → reportar:** issue citando `CU-9.i`.

---

## Gate de plan vigente — `wf-task-run`

> **Mecanismo común:** `sdd-gate-check.py` evalúa que el plan origen de las tasks
> siga vigente antes de ejecutarlas.

### CU-9.j — Ejecutar tasks contra un plan degradado a BORRADOR
**Precondición:** un `_tasks.md` cuyo `Plan origen` fue degradado a `BORRADOR`
**después** de generar las tasks.
**Mecanismo:** `sdd-gate-check.py` (gate de plan vigente).

1. Le pides ejecutar las tasks de esa feature.
   → **Esperado:** deny con *"El plan origen '…' esta en Estado: BORRADOR — fue
     degradado tras generar las tasks. Ejecuta /wf-plan-validate … antes de ejecutar
     tasks."*

**Resultado:** PASS si deniega · FALLO si ejecuta tasks contra un plan ya no vigente.
**Desviación → reportar:** issue citando `CU-9.j`.

### CU-9.k — Ejecutar una task retenida por enmienda
**Precondición:** una task `T-00X` cuyo `Spec CA` referencia un CA con
`Enmienda pendiente` en el plan.
**Mecanismo:** `sdd-gate-check.py` (gate de plan vigente, granularidad por task).

1. Le pides ejecutar específicamente esa task (`--task T-00X`).
   → **Esperado:** deny de **solo esa task** (*"la task T-00X esta retenida por
     enmienda pendiente sobre …"*); el resto de la feature sigue ejecutable. Sin
     `--task`, `sdd-task-state.py next` salta las retenidas y no bloquea.

**Resultado:** PASS si bloquea solo esa task y deja correr las demás · FALLO si
ejecuta la task retenida, o bloquea toda la feature.
**Desviación → reportar:** issue citando `CU-9.k`.

---

## Fail-open — el gate no debe bloquear de más

> **Mecanismo común:** ante incertidumbre, `sdd-gate-check.py` permite. La red de
> seguridad no es un parser de toda sintaxis; la prosa del workflow sigue aplicando.

### CU-9.l — Invocación sin path resoluble
**Precondición:** la petición no permite resolver el artefacto (sin token `.md`
reconocible en los args que construya el agente).
**Mecanismo:** `sdd-gate-check.py` (fail-open).

1. Lanzas un workflow con gate de forma que el argumento no apunte a un `.md` claro.
   → **Esperado:** el gate **permite** (no deniega). No bloquea sin haber podido
     evaluar la precondición.

**Resultado:** PASS si permite · FALLO si bloquea sin poder evaluar el gate.
**Desviación → reportar:** issue citando `CU-9.l`.

### CU-9.m — Entorno degradado (sin `python3`, stdin malformado, error interno)
**Precondición:** no hay `python3` en el runner, el stdin del hook es ilegible, o el
gate lanza una excepción interna.
**Mecanismo:** wrapper del hook + `sdd-gate-check.py` (fail-open: exit 0 sin decisión;
el wrapper ni siquiera ejecuta el script si falta `python3`).

1. Lanzas un workflow legítimo en ese entorno degradado.
   → **Esperado:** **permite**. Una invocación legítima nunca se bloquea por un fallo
     de entorno.

**Resultado:** PASS si permite · FALLO si una invocación legítima se bloquea por
entorno.
**Desviación → reportar:** issue citando `CU-9.m`.
