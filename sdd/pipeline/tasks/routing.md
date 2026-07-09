## Fase Tasks — precondiciones, desambiguación y fronteras

> **Audiencia.** El **hilo principal (orquestador)** aplica esto al orientar y enrutar peticiones de Tasks/entrega. Un subagente que lo herede lo lee como **contexto de proyecto** (invariantes de la fase), no como instrucción de rol.

**Precondición de entrada.** Tasks requiere un **`_plan.md` en estado `VALIDADO`** (sin gaps abiertos `DESIGN_GAP`/`TECH_GAP`/`TRACE_GAP`/`PLAN_GAP` y con `Estado: VALIDADO` en el header) y **`status_sync` fiable** (no `stale` ni `needs_review`). Si el plan está en `BORRADOR` o tiene gaps → redirige a `wf-plan-validate`; si el `status_sync` es `stale`/`needs_review` → resincronizar Spec/Plan antes de generar tasks.

**Las tres vías de ejecución (desambiguación clave):**
- **Task pendiente** del `_tasks.md` → `wf-task-run` (la siguiente con `--next`, una con `--task T-00X`, o el lote con `--all`).
- **Divergencia entre spec y código ya entregado** → `wf-bug`: triajea contra el CA del spec y **solo** escala a `wf-spec-delta` si el comportamiento esperado cambia. Fix silencioso sin CA = prohibido.
- **CA ambiguo descubierto al implementar** (la task se bloquea porque el spec admite varias lecturas) → `wf-spec-amend <spec.md> --ca CA-XXX --from-task T-00X` ⚠ (vive en la fase Spec; back-edge correcto desde la ejecución). Solo aclara texto **sin cambiar comportamiento**; el plan recibe `Enmienda pendiente` que retiene SOLO las tasks que referencian ese CA (el resto sigue ejecutable). Si el comportamiento esperado cambia, no es enmienda: es `wf-spec-delta`.

**Integridad de estados (no se edita a mano).** Los estados de task (`PENDIENTE|EN_CURSO|HECHA|BLOQUEADA`) los escribe **solo** `sdd-task-state.py`; el `Estado` de cada `TC-XXX` lo escribe **solo** `wf-qa-verify` con evidencia ejecutada — cobertura sin evidencia no existe. Nunca a mano.

**QA y release (fronteras de salida).** Un `DIVERGENTE` en `wf-qa-verify` se canaliza por `wf-bug`, **nunca** se ajusta el TC para que pase. `wf-release` solo acepta features con QA `APTO`/`APTO_CON_RESERVAS` (gate determinista en `sdd-release.py`) y captura el commit SHA con git (no se teclea). El `wf-qa-plan` puede derivarse desde que el spec es fiable, antes o en paralelo a la implementación.
