## Fase Plan — precondiciones, desambiguación y fronteras

> **Audiencia.** El **hilo principal (orquestador)** aplica esto al orientar y enrutar peticiones de Plan. Un subagente que lo herede lo lee como **contexto de proyecto** (invariantes de la fase), no como instrucción de rol.

**Precondición de entrada.** Plan requiere un **`*_spec.md` validado** (sin HUs `[INCOMPLETO]`, gaps `[CRÍTICO]` pendientes ni `status_sync` no fiable), el **handoff de Design completo** cuando la regla canónica de `kb-plan-expert` determine que Design es obligatorio, y **shared models claros** si existe `_features.md`. Si falta cualquiera → **bloquea y redirige**: bloqueos de spec → fase Spec; falta `DESIGN.md`/`*_flows.md`/`*_views.md` → fase Design. La regla exacta de cuándo Design es obligatorio y la taxonomía de gaps viven en `kb-plan-expert`; esta fase solo las resume.

**Gate BORRADOR → VALIDADO (frontera Plan → Tasks).** `wf-prepare-plan` genera el `_plan.md` en estado **`BORRADOR`**; `wf-plan-validate` lo sella **`VALIDADO`** (o lo deja `BORRADOR` si falla). `wf-prepare-tasks` **solo consume planes `VALIDADO`**: si el plan sigue en BORRADOR, el siguiente paso correcto es validarlo, no generar tasks. La fase Plan cierra decisiones arquitectónicas; no trocea implementación.

**Gaps del handoff.** `DESIGN_GAP`, `TECH_GAP`, `TRACE_GAP` o `PLAN_GAP` → remite a corregir el handoff, el spec o el propio plan antes de reintentar; no se bypasean.
