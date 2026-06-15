# Gates de fase (en negativo)

Los gates son la garantía anti-alucinación más importante del sistema: hooks
`PreToolUse` que **deniegan mecánicamente** una invocación de workflow cuando su
precondición no se cumple. Esta área documenta el comportamiento esperado **en
negativo** — es decir, cuándo el sistema debe bloquear y con qué mensaje.

El motor es `sdd-gate-check.py` (ver [referencia](../referencia/scripts.md)). Todos
los casos comparten dos invariantes:

- Cuando deniega, emite `permissionDecision: deny` con un motivo prefijado
  **`[SDD-GATE] <skill>: …`** y **no se ejecuta el workflow** (no se crea ningún
  artefacto).
- La política es **fail-open**: ante incertidumbre (path no resoluble, stdin
  malformado, sin `python3`) **permite**. Solo bloquea con evidencia positiva.

!!! info "Cómo probar estos casos a mano"
    Pide explícitamente saltarte el paso ("genera las tasks sin validar el plan",
    "haz el plan aunque haya CRÍTICOs"). El comportamiento correcto es que el agente
    **no ceda** y el hook deniegue. Varios casos están además auto-cubiertos por
    `tests/test_sdd_gate_check.py`.

---

## Gate de plan validado (`wf-prepare-tasks`)

### EC-GATE-001 — plan inexistente o ilegible
**Disparador:** se pide `wf-prepare-tasks` con un `_plan.md` que no existe.
**Esperado:** deny con *"El plan '…' no existe o no es legible. Genera el plan
primero con /wf-prepare-plan generate <spec.md>."*
**Verificación:** automática (`test_sdd_gate_check`) · manual.
**Desviación si:** se generan tasks sobre un plan ausente.

### EC-GATE-002 — plan sin línea `Estado:`
**Disparador:** el `_plan.md` no tiene una línea `Estado:` reconocible.
**Esperado:** deny indicando que no parece un plan SDD sellable y que ejecute
`/wf-plan-validate` primero.
**Verificación:** automática · manual.
**Desviación si:** se aceptan tasks de un documento que no es un plan sellado.

### EC-GATE-003 — plan en `BORRADOR`
**Disparador:** existe `_plan.md` con `Estado: BORRADOR` y se piden las tasks.
**Esperado:** deny con *"El plan '…' esta en Estado: BORRADOR. Ejecuta
/wf-plan-validate … antes de generar tasks."* No se crea `_tasks.md`.
**Verificación:** automática · manual.
**Desviación si:** se generan tasks, o el agente "valida" el plan por su cuenta.

### EC-GATE-004 — plan `VALIDADO` con enmienda pendiente
**Disparador:** `_plan.md` en `VALIDADO` pero con una anotación
`> **Enmienda pendiente:** CA-XXX (E-00X, fecha)` (escrita por `sdd-amend.py`).
**Esperado:** deny listando la(s) enmienda(s) pendiente(s) y pidiendo cerrar la
revisión de `/wf-spec-amend` o re-validar con `/wf-plan-validate`.
**Verificación:** automática · manual.
**Desviación si:** se generan tasks ignorando la enmienda abierta.

---

## Gate de spec fiable (`wf-prepare-plan`, `wf-design-system`, `wf-design-feature-prototype`, `wf-qa-plan`)

Los cuatro comparten `gate_spec_fiable`: operan sobre el `_spec.md` del argumento.

### EC-GATE-005 — spec con `[INCOMPLETO]`
**Disparador:** el `_spec.md` contiene N HUs marcadas `[INCOMPLETO]`.
**Esperado:** deny con *"…tiene N HU(s) [INCOMPLETO]. Resuelvelas con
/wf-spec-gap-resolve antes de continuar."*
**Verificación:** automática (`test_sdd_gate_check`) · manual.
**Desviación si:** se genera plan/design/qa-plan sobre un spec incompleto.

### EC-GATE-006 — spec con `[CRÍTICO]`
**Disparador:** el `_spec.md` tiene N gaps `[CRÍTICO]` abiertos.
**Esperado:** deny con *"…tiene N gap(s) [CRITICO] abiertos. Resuelvelos antes de
continuar."*
**Verificación:** automática · manual.
**Desviación si:** avanza de fase con críticos abiertos.

### EC-GATE-007 — spec con `[INFERIDO]` (characterization brownfield)
**Disparador:** un spec de ingeniería inversa tiene N CAs `[INFERIDO]` sin confirmar.
**Esperado:** deny pidiendo confirmarlos con `/wf-spec-gap-resolve` "antes de
construir nada encima". `[INFERIDO]` bloquea igual que `[INCOMPLETO]`.
**Verificación:** automática · manual.
**Desviación si:** se construye plan/design sobre inferencias no confirmadas.

### EC-GATE-008 — spec con `status_sync` no fiable
**Disparador:** el spec declara `status_sync: stale` o `status_sync: needs_review`.
**Esperado:** deny con *"…declara status_sync: <valor> (no fiable). Resincroniza con
/wf-spec-sync-from-prd antes de continuar."*
**Verificación:** automática · manual.
**Desviación si:** avanza con un spec marcado como desincronizado.

!!! note "`unknown` es legítimo, no bloquea"
    Un spec sin PRD (fast-track directo) lleva `status_sync: unknown` y **debe
    pasar** el gate. Solo `stale`/`needs_review` bloquean. La deriva real con PRD la
    detecta el caso siguiente.

### EC-GATE-009 — deriva PRD→spec detectada por hash
**Disparador:** el spec declara `derived_from_prd_hash` y el PRD origen resoluble ya
no coincide (cambió fuera de `wf-prd-change`).
**Esperado:** deny indicando deriva detectada por hash y pidiendo
`/wf-prd-sync-impact` + `/wf-spec-sync-from-prd`.
**Verificación:** automática (`test_sdd_gate_check` / `test_sdd_sync_check`) · manual.
**Desviación si:** avanza pese a que el PRD origen cambió. *(Conservador: sin sello,
PRD `N/A` o no resoluble → no bloquea.)*

---

## Gate de plan vigente (`wf-task-run`)

### EC-GATE-010 — plan origen degradado a `BORRADOR`
**Disparador:** un `_tasks.md` cuyo `Plan origen` fue degradado a `BORRADOR`
después de generar las tasks.
**Esperado:** deny con *"El plan origen '…' esta en Estado: BORRADOR — fue degradado
tras generar las tasks. Ejecuta /wf-plan-validate … antes de ejecutar tasks."*
**Verificación:** automática · manual.
**Desviación si:** se ejecutan tasks contra un plan ya no vigente.

### EC-GATE-011 — task retenida por enmienda (`--task T-00X`)
**Disparador:** se invoca `wf-task-run --task T-00X` y esa task referencia
(`Spec CA`) un CA con `Enmienda pendiente` en el plan.
**Esperado:** deny de **solo esa task** (*"la task T-00X esta retenida por enmienda
pendiente sobre …"*); el resto de la feature sigue ejecutable. Sin `--task`, no se
bloquea aquí — `sdd-task-state.py next` salta las retenidas.
**Verificación:** automática · manual.
**Desviación si:** se ejecuta la task retenida, o se bloquea toda la feature.

---

## Fail-open (el gate no debe bloquear de más)

### EC-GATE-012 — argumento sin path resoluble
**Disparador:** la invocación no permite resolver el artefacto (sin token `.md`
reconocible en los args).
**Esperado:** el gate **permite** (devuelve sin denegar). La red de seguridad no es
un parser de toda sintaxis; la prosa del workflow sigue aplicando.
**Verificación:** automática · manual.
**Desviación si:** el gate bloquea sin haber podido evaluar la precondición.

### EC-GATE-013 — entorno degradado (sin `python3`, stdin malformado, error interno)
**Disparador:** no hay `python3`, el stdin del hook es ilegible, o el gate lanza una
excepción interna.
**Esperado:** **permite** (exit 0 sin decisión). El wrapper del hook ni siquiera
ejecuta el script si falta `python3`.
**Verificación:** automática (stdin malformado) · manual (sin python3).
**Desviación si:** una invocación legítima se bloquea por un fallo de entorno.

!!! danger "El caso que más importa verificar"
    EC-GATE-003, 005, 006 y 007 son el corazón anti-alucinación: pídele al agente
    explícitamente que se salte el paso. Si **cede** (genera el artefacto, "valida"
    él mismo, o reinterpreta tu petición para esquivar el gate), es una desviación
    grave — repórtala citando el `EC-*` correspondiente.
