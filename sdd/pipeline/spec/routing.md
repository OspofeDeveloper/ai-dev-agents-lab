## Fase Spec — precondiciones, desambiguación y fronteras

> **Audiencia.** El **hilo principal (orquestador)** aplica esto al orientar y enrutar peticiones de Spec. Un subagente que lo herede lo lee como **contexto de proyecto** (invariantes de la fase), no como instrucción de rol.

**Precondición de entrada.** Spec requiere un PRD **en estado revisable** (sin `[ASUNCIÓN]` abiertas y sellado). La readiness se verifica **mecánicamente** (ver "Frontera PRD → Spec" de la disciplina de orquestación: `sdd-prd-ready.py`), no a ojo ni por topología. Si no hay `prd.md`, se redirige a la fase PRD. **Excepción brownfield**: si el sistema ya existe (legacy) y no hay PRD, el onramp es `wf-spec-from-code` (specs de caracterización con el código como fuente de verdad; los `[INFERIDO]` bloquean el plan hasta confirmación humana vía `wf-spec-gap-resolve`).

**"Crea las specs" → `wf-spec-features-first`, NO `wf-spec-discover`.** Ante una petición **general** —"crea las specs", "genera las specs del PRD", "quiero las specs"— el entrypoint es `wf-spec-features-first <prd.md>` (que internamente hace discover + fast-track por feature). `wf-spec-discover` **no** es el entrypoint de "crea las specs".

**Patrón "fase X" / "iteración X" / "subset de features".** Solo cuando el usuario pide explícitamente trabajar por fases/iteración/subset. Las features no existen hasta el discovery (los `F-XXX` no están en el PRD). Procede: si no existe `<basename>_discovery.md`, ejecuta `wf-spec-discover <prd.md>` primero, presenta el mapa de features (ID, nombre, actor, RFs) y **pregunta qué IDs incluir**; luego `wf-spec-features-first <prd.md> --features F-XXX,...`. Las no incluidas quedan `PENDIENTE_GENERACIÓN` y se generan en pasadas posteriores.

**Guardrails de `wf-spec-features-first`** (el workflow corre en el hilo principal y **presenta cada gate con `AskUserQuestion` en el momento**, continuando en el mismo turno con lo que el usuario elija — [[D-045]]; los flags de entrada saltan su gate, y ninguno se auto-arma, [[D-026]]):
- Si no existe `_analysis.md`, lo genera y **se detiene** para que el usuario lo revise.
- Gaps `[CRÍTICO]` pendientes → **se detiene** salvo `--allow-open-critical-gaps`.
- Si las respuestas del analysis introducen expansión de capacidad (entidad persistente nueva, catálogo reutilizable, nueva granularidad, modelo owner nuevo, flujo no comprometido) → **se detiene** y remite a `wf-prd-change`, salvo `--allow-derived-scope-from-analysis`.
- Más de 5 features sin `--features` → **se detiene** y recomienda iterar por subset; full-run solo con `--all-features`.

**Elección del rigor (standard / ligero), por feature.** No se fija en el init: es elección deliberada por feature al crear el spec. El rigor es un **argumento** que se propaga a cada `wf-spec-fast-track`, y esos son `context: fork` (no pueden usar `AskUserQuestion`, ver [[D-002]]), así que tiene que estar resuelto **antes** del fan-out. **El hilo principal ofrece la elección ANTES de invocar**:
1. Si el usuario ya pasó `--light`/`--standard` → respétalo.
2. Si `pipeline_mode` de `.sdd/project-init.json` es `light` → úsalo sin preguntar.
3. Si no, ofrece con `AskUserQuestion`: **Standard (Recomendado)** (spec completo, 8 elementos, ≥3 CAs, análisis como artefacto) vs **Ligero** (núcleo de 4, ≥1 CA, análisis inline, para feature pequeña y acotada; los gates anti-alucinación son idénticos, se relaja ceremonia no rigor). Pasa el flag elegido.
4. En `wf-spec-features-first` (lote) se pregunta **una sola vez** para toda la pasada, nunca feature a feature.

El default seguro es `standard`. Ligero se prohíbe solo (lo fuerza standard) si la feature toca shared models, introduce entidades nuevas o expande alcance — esas reglas viven en `kb-spec-expert` y las aplican las propias workflows.
