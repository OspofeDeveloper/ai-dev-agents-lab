## Fase Design — precondiciones, desambiguación y fronteras

> **Audiencia.** El **hilo principal (orquestador)** aplica esto al orientar y enrutar peticiones de Design. Un subagente que lo herede lo lee como **contexto de proyecto** (invariantes de la fase), no como instrucción de rol.

**Precondición de entrada.** Design requiere un **`*_spec.md` validado** y, antes de `wf-design-system`/`wf-design-feature-prototype`, un **`DESIGN_BRIEF.md` cerrado**. Si el spec tiene HUs `[INCOMPLETO]`, gaps `[CRÍTICO]` pendientes o `status_sync` no fiable → **para y redirige a la fase Spec**. Si no hay brief → `wf-design-intake` primero (los workflows aguas abajo se detienen sin brief salvo override explícito `--no-brief`, reservado a legacy/experimental).

**Onramp brownfield.** Si la UI **ya existe en producción** y no se va a rediseñar, la entrada **alternativa** es `wf-design-extract` (ingeniería inversa → `DESIGN.md` con `origin: extracted`); no exige spec ni brief. Es el espejo de `wf-spec-from-code` en Spec.

**Design es saltable por feature.** Una feature **sin superficie de UI visible** pasa de Spec a Plan directamente; la regla canónica de cuándo Design es obligatorio vive en `kb-plan-expert` y la aplica `wf-prepare-plan`. Esta fase no fuerza su propio uso. Si el proyecto encaja en un "NO cubre" (Figma), dilo al usuario en cuanto se detecte, antes de generar artefactos que no va a usar.

**Desambiguaciones críticas (las trampas reales):**
- Cambio que toca `style_family` o `clarity_vs_brand` → **no es delta, es brief**: `wf-design-intake` para actualizar el brief antes, **no** `wf-design-delta`.
- "Que decida menos la IA" / "quiero que el usuario elija el estilo" → `wf-design-intake` **antes** de `wf-design-system`.
- Explorar sin comprometer main → `wf-design-branch`, **no** `wf-design-delta`.
- Rama del **sistema completo** (`wf-design-branch`) vs A/B de **una feature** (`wf-design-variant`): propósitos distintos, no se solapan (desambiguación canónica en `kb-design-governance` Regla 4: branch/delta/intake/variant).
- Falta `DESIGN.md` → `wf-design-system`; faltan `*_flows.md`/`*_views.md` de una feature que va a plan → `wf-design-feature-prototype`; problemas de accesibilidad → `wf-design-a11y-audit`; feedback no estructurado de stakeholders → `wf-design-feedback capture` primero, luego `triage`.

**Design no redefine lo funcional.** Si la petición mezcla decisiones funcionales con visuales, el Spec sigue siendo la **SSoT funcional**: la fase Design no redefine HUs, journeys ni CAs.
