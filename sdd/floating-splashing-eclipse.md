# Propuesta de arquitectura — Topología `design` (repo de diseño SSoT)

> **Esto es diseño, no implementación.** Deliverable: esta propuesta + un borrador `D-011`.
> La implementación es un ciclo posterior, una vez aprobada la forma.

## Context

Investigando el (2) descubrimos que `surfaces`/`targets`/`has_ui` de `project-init.json` son
**write-only** y que `target_platforms` del design no se deriva de nada. El usuario propone un
**repo de diseño SSoT propio** (`myopps-design`) paralelo al repo de specs y a los de código,
que **además del sistema agnóstico aloja los bundles de feature por superficie/plataforma/
form-factor**. Decisiones tomadas:
- Diseñar la topología primero, **sin implementar**.
- Topología nueva se llama **`design`** (label de Q1: "Diseño").
- Design targets = **etiquetas libres** con convención `<familia>[-<plataforma>][-<formfactor>]`.
- Divergencia = **base agnóstica + overrides por target** (no duplicar lo idéntico).

## Modelo actual (recap, con refs) y por qué no basta
- 3 topologías (D-005): el sistema de diseño (`DESIGN.md`, rol `system`) hoy vive **dentro de
  `authoring`**; los `consumer` autoran `flows`/`views` localmente (rol `feature`) consumiendo el
  `DESIGN.md` de un único SSoT (`artifacts_source`) — CU-1.i. `SKILL.md:29-31`.
- **Bloqueo clave**: la regla de copia agnóstica de flows/views (cita inline dentro de la **Regla 7**
  de `kb-design-feature-artifacts`, `SKILL.md:131-136` — NO hay una "Regla 8" numerada hoy) **fuerza
  `flows`/`views` a una sola copia agnóstica** + "Notas responsive"; **solo `ui_prompt` diverge**
  por familia (`mobile`/`web`/`desktop`). No contempla split Android/iOS ni phone/tablet. Los
  escenarios (b) componentes nativos y (d) phone/tablet **exigen divergencia a nivel views/flows**.

## Arquitectura propuesta

### A. Nueva topología `design`
- **Q1 gana una 4ª opción**: `Producto (authoring) · Desarrollo (consumer) · Autónomo (standalone)
  · Diseño`. → Q1 en **exactamente 4 opciones** (límite `AskUserQuestion`; sin "Other"). *Flag:
  sin sitio para una 5ª topología sin anidar.*
- El repo `design` es **SSoT de diseño**: autora (a) el **sistema agnóstico** (`DESIGN.md`, brief,
  tokens, rol `system`) y (b) los **bundles de feature por design target**. **Sin** prd/spec/plan/
  tasks. `stack: agnostico`, `design_role: system`.
- **Entrevista del init**: declarar los **design targets** que cubre (etiquetas libres con
  convención `<familia>[-<plataforma>][-<formfactor>]`, p. ej. `mobile`, `mobile-android`,
  `mobile-ios`, `web`, `desktop`, `mobile-tablet`). De ahí se deriva `target_platforms` (familias).
- **`project-init.json`**: `topology:"design"`, `phases:["design"]`, `design_role:"system"`,
  `design_targets:[...]`, `target_platforms:[...]` (familias derivadas), `artifacts:{design:"<dir>"}`.

### B. Design targets + modelo base/override (el núcleo)
- **Design target** = contexto de UX que puede necesitar su propio diseño. Etiqueta con convención
  **validada** `<familia>[-<plataforma>][-<formfactor>]`: la **familia es obligatoria** y debe ser
  una de `{mobile, web, desktop}` (es el token del que se deriva `target_platforms`, ver E); el
  resto de tokens (plataforma, form-factor) son libres. *Decisión cerrada (antes open Q4).*
- **Divergencia base + override**: `flows`/`views` se autoran **una vez como base agnóstica**; un
  design target solo añade su **override** cuando DIVERGE realmente (componentes nativos, layout
  tablet). Resolución para un consumidor: `base ⊕ override(target)` (el override gana donde existe).
  El `ui_prompt` sigue siendo por superficie/target. **Riesgo técnico central (open Q2): el grano
  del override.** ¿El override gana por vista entera, por estado de pantalla, o por componente dentro
  de la vista? En `views` —SSoT de pantallas + estados— el grano del merge es *la* decisión difícil,
  no un detalle; queda para implementación pero es el punto que más condiciona el modelo.
- **Requiere extender la regla de copia agnóstica** (hoy inline en la Regla 7 de
  `kb-design-feature-artifacts`; la implementación puede **promoverla a una Regla 8 numerada** al
  relajarla): hoy prohíbe divergencia de views/flows; el modelo nuevo la permite **vía override por
  target**, preservando el principio de no duplicar (la base se comparte; solo se materializa lo que
  cambia).
- Layout (boceto; el detalle es de implementación):
  ```
  <design>/features/<feature>/
    <feature>_flows.md            # base agnóstica
    <feature>_views.md            # base agnóstica
    <feature>_ui_prompt.<surface>.md
    targets/<design-target>/      # SOLO si ese target diverge
      <feature>_views.md          # override (componentes nativos / tablet)
      <feature>_flows.md          # override (si la navegación cambia)
      <feature>_ui_prompt.md
  ```

### C. Mapeo de los 4 escenarios
| Escenario | Design targets | Qué se materializa |
|---|---|---|
| a) Android + iOS, diseño idéntico | `mobile` | solo base; 2 repos la consumen |
| b) Android + iOS nativos especializados | `mobile-android`, `mobile-ios` | base + 2 overrides (views nativas) |
| c) móvil + desktop, código KMM | `mobile`, `desktop` | base + override desktop si procede; 1 repo KMM consume ambos |
| d) Android phone + tablet | `mobile-phone`, `mobile-tablet` | base + override tablet (layout) |

### D. `consumer` multi-fuente + binding a design targets
- `consumer` con UI: pregunta **"¿Dónde vive el `DESIGN.md`?"** → mismo SSoT de specs (hoy) o
  **repo `design` aparte** → persistir `design_source` + `design_source_pin`.
- Además declara **qué design target(s) consume** (`design_targets` en su `project-init.json`):
  p. ej. el repo Android-nativo consume `mobile-android`; el repo KMM consume `mobile` + `desktop`.
- El consumidor resuelve cada target como `base ⊕ override` desde el repo de diseño (solo lectura);
  ya **no autora flows/views localmente** (se mueven al repo de diseño). **Decisión comprometida, no
  matiz.** Esto **supersede a CU-1.i** para el caso consumer-con-repo-`design`: hoy el consumer
  autora `flows`/`views` localmente; con repo de diseño dedicado el ownership de esos artefactos pasa
  al repo `design` y el consumer solo los lee. Es el cambio que **más staleness cross-repo introduce**
  (specs SSoT + design SSoT + N repos de código), así que la open question 3 (drift cross-repo, pin
  de `design_source`, extender `wf-design-sync`) **deja de ser opcional**: es subsistema, no nota.
  El caso co-localizado (`authoring`/`standalone`) conserva flows/views locales (ver F).

### E. `target_platforms` derivado (función NET-NEW, no reutilización)
- `target_platforms` (familias `{mobile, web, desktop}` — **3 familias**; `tablet` NO es familia sino
  form-factor dentro de `mobile`/`desktop`, ver B) se **deriva de los design targets** declarados (de
  su token de familia validado, ver B). **Corrección factual:** una versión previa de
  esta propuesta afirmaba reutilizar `derive_target_platforms(surfaces, targets)` "del (2)" como
  pieza ya existente y testeada en `sdd-init-detect.py`. **Esa función NO existe.** El trabajo (2)
  entregó `derive_design_role` + los campos write-only (`surfaces`/`targets`/`has_ui`); la derivación
  de `target_platforms` es **net-new y hay que construirla**. Lo reutilizable del (2) es el **patrón**
  (D-010): función pura testeada en `sdd-init-detect.py` + subcomando, no esta función concreta.
- También cubre los casos **co-localizados** (`standalone`/`authoring` con diseño), derivando de
  surfaces+targets (incl. "target desktop de MP ⇒ familia desktop").
- Vocabulario de familias unificado; alinear el ejemplo del template del brief
  (`design_brief_template.md:18`, hoy `iOS/Android`) a familias.

### F. Coexistencia (aditivo, no reemplazo)
- El caso co-localizado (`authoring`/`standalone` con diseño) **se mantiene** (equipos pequeños).
- El repo `design` dedicado es para sistema visual compartido por varias superficies/productos.

## Preguntas abiertas a cerrar en implementación
1. **`DESIGN.md` y componentes nativos**: el sistema (identidad, tokens, voz, motion) se comparte;
   ¿basta con que los overrides por target lleven la especificidad de componente (Material vs HIG),
   o el `DESIGN.md` necesita una capa de mapeo de componentes por plataforma? (recomendado: sistema
   compartido + override; revisar si se queda corto).
2. Mecanismo de generación: ¿`wf-design-feature-prototype` aprende a emitir base + overrides, o se
   apoya en el eje de `wf-design-variant` (hoy A/B por feature)? Resolución `base ⊕ override`.
3. Staleness cross-repo (**ya no opcional**, ver D): un override traza a su base + spec + `DESIGN.md`;
   pin de `design_source`; **extender `wf-design-sync` para drift entre repos** — subsistema a diseñar.

> **Cerradas en este ciclo** (ya no son preguntas abiertas):
> - *Convención de etiquetas* (antes Q4) → **se valida** el patrón `<familia>[-<plataforma>][-<formfactor>]`
>   con familia obligatoria de `{mobile,web,desktop}`; resto de tokens libres (ver B y E).
> - *Ownership de flows/views en consumer* → se **mueven al repo `design`** (ver D, supersede CU-1.i).

## Out of scope (de esta propuesta)
- Implementar nada: ciclo posterior.
- Modelar diseño como "tecnología"/overlay: **rechazado** (rompe fases/targets, Regla 16). Es topología.
- Integración Figma (ya fuera de alcance, ROADMAP 7.6).

## Ficheros que cambiarían (implementación futura — listados, NO se tocan ahora)
- `bootstrap/skills/wf-project-init/SKILL.md` — Q1 4ª opción `design`; rama `design` (declara design
  targets); esquema (`design_targets`, `target_platforms`, `design_source`/pin en consumer).
- `scripts/sdd-init-detect.py` + `tests/test_sdd_init_detect.py` — **`derive_target_platforms`
  (net-new, NO existe hoy)** + validación de la convención de design targets (familia obligatoria).
- **`pipeline/design/skills/kb-design-feature-artifacts/SKILL.md`** — relajar la regla de copia
  agnóstica (hoy inline en Regla 7; **promoverla a Regla 8 numerada** al relajarla): permitir
  override de `flows`/`views` por design target (base + overrides) y definir la resolución/grano.
- `pipeline/design/skills/wf-design-feature-prototype/SKILL.md` + `pipeline/design/agents/
  design-feature-architect.md` — emitir/consumir base + overrides; resolver design target.
- `pipeline/design/skills/wf-design-intake/SKILL.md` + `kb-design-brief/` — `target_platforms` desde
  design targets; vocabulario de familias.
- Wiring `consumer`: plantilla CLAUDE.md "repo consumidor" + resolución `design_source`/`design_targets`.
- `DECISIONS.md` — **D-011** (topología `design` + bundles por target + consumer multi-fuente).
- `conformance/casos-de-uso/cu-01-inicializar.md` — escenarios nuevos (topología `design` con design
  targets; consumer con `design_source` + `design_targets`).

## Verification (para la implementación futura)
1. **Unit:** tests de `derive_target_platforms` (familias desde design targets) y de validación de
   la convención de etiquetas; suite completa verde.
2. **Init E2E:** init de un repo `design` con `design_targets:[mobile-android, mobile-ios, desktop]`
   → `project-init.json` con esos targets y `target_platforms:[mobile,desktop]`. Init de un consumer
   Android-nativo apuntando `design_source` + `design_targets:[mobile-android]`.
3. **Generación:** una feature con base + override `mobile-android` → el consumidor resuelve
   `base ⊕ override` y obtiene las views nativas; un target sin override hereda la base intacta.

## Próximo paso tras aprobar
Registrar **D-011** en `DECISIONS.md` (append-only, más reciente arriba). La implementación se
planifica como ciclo aparte; la pieza foundational es **construir** `derive_target_platforms`
(net-new) siguiendo el patrón de `derive_design_role` del (2) — función pura testeada en
`sdd-init-detect.py` (D-010), no una reutilización directa.
