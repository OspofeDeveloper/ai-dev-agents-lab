# CU-5 — Diseñar una feature

**Objetivo:** verificar que la fase Design respeta su gate (no hay `DESIGN.md` sin
brief cerrado), genera el sistema visual y los artefactos de feature trazados al spec,
deriva un `DESIGN.md` por ingeniería inversa cuando la UI ya existe, y audita/evoluciona
sin romper el contrato.
**Proyecto a usar:** para intake → system → prototype, un producto real con UI (app o
web) y su spec; para `wf-design-extract`, un **frontend real en producción** (CSS,
componentes), p. ej. tu propia web o un repo con design system.
**Cobertura automática:** ninguna directa — todo el contenido visual es juicio del
agente `design-system-architect` / `design-feature-architect` → **manual**.

> [!IMPORTANT]
> **Design es saltable por feature.** Si la feature no tiene superficie de UI visible,
> Spec pasa a Plan directamente. Cuando sí aplica, **el `DESIGN_BRIEF.md` es gate
> obligatorio**: no hay `DESIGN.md` sin brief cerrado. Todos los workflows de la fase
> delegan en **`design-system-architect`** / **`design-feature-architect`**.

---

## 🧪 Qué se prueba aquí (por componente)

CU-5 es un **objetivo de usuario** (diseñar una feature), no una sola skill: sus escenarios ejercitan **15 componentes** de la fase Design. Marca cada escenario al ejecutarlo. El estado de cobertura autoritativo (ejes happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) — esta vista es la **transpuesta** para leer/ejecutar el CU.

### `wf-design-intake` — cierra el brief (gate obligatorio) (2)
- [ ] CU-5.a — El brief es gate obligatorio (intake)
- [ ] CU-5.m — Intake: `DESIGN_GAP`, modo `auto` y brief existente

### `wf-design-system` — crea el sistema visual del producto (2)
- [ ] CU-5.b — Crear el sistema visual del producto (system)
- [ ] CU-5.l — System: anclaje de dirección visual (provisional vs confirmed) y policy de referencias

### `wf-design-feature-prototype` — deriva flows/views/ui_prompt de feature (4)
- [ ] CU-5.c — Derivar flows, views y prompt de feature (feature-prototype)
- [ ] CU-5.n — Feature-prototype: resolución de `target_tool` y conflicto cross-feature
- [ ] CU-5.w — Feature con design targets divergentes: base + overrides per-view ([[D-011]])
- [ ] CU-5.y — Feature-prototype sobre un `DESIGN.md` de otra familia de plataforma (mismatch co-localizado, [[D-011]]) · **AÑADIDO 2026-06-26 — pendiente de implementar la detección; en rojo hasta entonces**

### `wf-design-extract` — ingeniería inversa del `DESIGN.md` (1)
- [ ] CU-5.d — Onramp brownfield: derivar `DESIGN.md` de una UI en producción (extract)

### `wf-design-validate` — audita el `DESIGN.md` sin regenerarlo (2)
- [ ] CU-5.e — Auditar, accesibilidad, evolucionar y medir impacto
- [ ] CU-5.o — Validate: read-only y promoción acotada de dirección (provisional → confirmed)

### `wf-design-moodboard` — captura inspiración antes del brief (1)
- [ ] CU-5.f — Capturar inspiración antes del brief (moodboard)

### `wf-design-discover` — research de apps de referencia (orquestador) (1)
- [ ] CU-5.g — Descubrir apps de referencia con research validado (discover)

### `wf-design-branch` — ramas paralelas del `DESIGN.md` (2)
- [ ] CU-5.h — Explorar una rama paralela del `DESIGN.md` (branch)
- [ ] CU-5.s — Branch: confirmación ante merge breaking y discard

### `wf-design-variant` — A/B testing visual de una feature (2)
- [ ] CU-5.i — A/B testing visual de una feature (variant)
- [ ] CU-5.t — Variant: hipótesis y métrica obligatorias

### `wf-design-feedback` — captura y triaje de feedback (2)
- [ ] CU-5.j — Capturar y triajear feedback de stakeholders (feedback)
- [ ] CU-5.v — Feedback: triage completo, `functional_change` a Spec y `out_of_scope`

### gate de spec fiable (`wf-design-system` / `wf-design-feature-prototype`) (1)
- [ ] CU-5.k — Gate de spec fiable en Design (system y feature-prototype)

### `wf-design-delta` — evolución incremental del `DESIGN.md` (1)
- [ ] CU-5.p — Delta: `[BRIEF_CHANGE_REQUIRED]` y precondiciones de apply

### `wf-design-a11y-audit` — auditoría de accesibilidad (1)
- [ ] CU-5.q — A11y-audit: ramificación por plataforma

### `wf-design-sync` — impacto de la deriva (read-only) (2)
- [ ] CU-5.r — Sync: propagación conservadora de la deriva (read-only)
- [ ] CU-5.x — Sync cross-repo: drift del repo de diseño en un consumer ([[D-011]])

### `wf-design-export` — exporta tokens a formatos de código (1)
- [ ] CU-5.u — Export: idempotencia, `EXPORT_GAP` y `--dry-run`

---

## CU-5.a — El brief es gate obligatorio (intake)

**Precondición:** un `_spec.md` validado de una feature con UI; sin `DESIGN_BRIEF.md`.
**Mecanismo:** skill `wf-design-intake generate` → **`design-system-architect`** (modo
`design-intake`). Output: `DESIGN_BRIEF.md`.

1. Le pides directamente "crea el DESIGN.md" sin brief.
   → **Esperado:** no genera el sistema visual; te lleva primero a cerrar el brief con
     el intake (gate obligatorio).
2. Le pides cerrar el brief.
   → **Esperado:** `design-system-architect` cierra modo de decisión, preset, familia visual,
     densidad, profundidad, motion y policy de referencias/autonomía, y escribe
     `DESIGN_BRIEF.md` (en `artifacts.design` o la raíz del producto).
3. ([[D-011]]) El proyecto declara `design_targets` (topología `design` o consumer con repo de diseño).
   → **Esperado:** el `target_platforms` del brief se **deriva** de los design targets (familias
     `{mobile,web,desktop}`, Paso 5b / `kb-design-brief` Regla 11), vía `sdd-init-detect.py target-platforms` —
     no se teclea ni se usa `iOS`/`Android`. Sin design targets, se fija desde las superficies (default `mobile`).

**Resultado:** PASS si exige el brief antes del sistema, lo cierra delegando en el
agente y deriva `target_platforms` en familias · FALLO si genera `DESIGN.md` sin brief, o escribe
`target_platforms` con plataformas (iOS/Android) en vez de familias cuando hay design targets.
**Desviación → reportar:** issue citando `CU-5.a`.

## CU-5.b — Crear el sistema visual del producto (system)

**Precondición:** `DESIGN_BRIEF.md` cerrado.
**Mecanismo:** skill `wf-design-system generate` (gate de spec fiable + brief) →
**`design-system-architect`**. Output: `DESIGN.md`.

1. Le pides crear el sistema visual desde el spec.
   → **Esperado:** genera `DESIGN.md` (frontmatter con visual_personality, color
     light/dark, type scale, iconography, motion, voice, reference apps; `origin:
     generated`) conforme al contrato, sin contradecir el brief ni inventar dirección
     no anclada.
2. ([[D-011]]) El proyecto declara `design_targets` que **divergen nativamente dentro de una familia**
   (p. ej. `mobile-android` + `mobile-ios`, Material vs HIG; leídos de `.sdd/project-init.json`).
   → **Esperado:** el `DESIGN.md` incluye la sección custom **`## Platform Components`**
     (`kb-design-system-contract` Regla 11), posicionada **tras `## Components` y antes de
     `## Accessibility`**: mapea el **rol abstracto** de cada componente que **realmente diverja** a su
     realización nativa por plataforma (android/Material, ios/HIG, web/desktop), **sin redeclarar lo
     compartido** (tokens/color/tipografía/voz/motion siguen siendo el sistema común). El sistema sigue
     siendo **uno solo**: no forkea el `DESIGN.md` por plataforma.
3. ([[D-011]]) El proyecto tiene una **sola base** (`target_platforms: [mobile]`, o una sola plataforma).
   → **Esperado:** **no** emite `## Platform Components` (no hay nada que mapear; añadirla sería ruido).

**Resultado:** PASS si genera un `DESIGN.md` conforme al contrato y al brief, y emite
`## Platform Components` **solo** cuando los design targets divergen nativamente (en la posición de
sección correcta, mapeando rol→realización nativa sin redeclarar lo compartido) · FALLO si ignora el
brief, deja el frontmatter incompleto, **omite `## Platform Components` con targets divergentes
declarados**, **la añade con una sola base**, o la usa para forkear/duplicar el sistema en vez de mapear
solo los componentes que divergen.
**Nota de testeo ([[D-011]]):** los casos 2-3 ejercitan el **lado productor** de la Regla 11. El gate es
**determinista**: `wf-design-system` Paso 3b lee `design_targets` de `.sdd/project-init.json` y resuelve
`requires_platform_components`/`native_platforms` con `sdd-init-detect.py target-platforms` (cubierto por
`PlatformComponentsGateTest` en `test_sdd_init_detect.py`); lo manual es que el agente **emita** (o no) la
sección según `NATIVE_PLATFORMS`. Un form-factor (`mobile-android` + `mobile-android-tablet`) **no** debe
disparar la capa (es layout → override per-view, CU-5.w), solo el split nativo (android+ios).
**Desviación → reportar:** issue citando `CU-5.b`.

## CU-5.c — Derivar flows, views y prompt de feature (feature-prototype)

**Precondición:** `DESIGN.md` y, si existe, `DESIGN_BRIEF.md`.
**Mecanismo:** skill `wf-design-feature-prototype generate` (gate de spec fiable +
brief + DESIGN.md) → **`design-feature-architect`**. Output:
`features/<n>/design/<n>_flows.md`, `_views.md`, `_ui_prompt.md`.

1. Le pides preparar las pantallas/flows para la feature.
   → **Esperado:** genera `flows` (secuencias y transiciones), `views` (SSoT de
     pantallas con **todos los estados aplicables**: default/loading/empty/error/…) y
     `ui_prompt` (ensamblaje tool-agnostic, `target_tool` stitch|web-generic), todo
     trazado a journeys y CAs del spec, **sin redefinir la funcionalidad**.

**Resultado:** PASS si genera los 3 artefactos trazados al spec con estados completos
· FALLO si redefine funcionalidad, o omite estados aplicables.
**Desviación → reportar:** issue citando `CU-5.c`.

## CU-5.d — Onramp brownfield: derivar `DESIGN.md` de una UI en producción (extract)

**Precondición:** una UI ya existente (CSS/componentes/capturas), sin spec ni brief.
**Mecanismo:** skill `wf-design-extract` `discover` → **gate humano** → `generate` →
**`design-system-architect`** (carga `kb-design-characterization`). Output: `DESIGN.md` con
`origin: extracted`.

1. Le pides documentar el sistema visual que ya tenéis ("extrae el DESIGN.md de esta UI").
   → **Esperado:** `discover` descubre tokens/paleta/tipografía/componentes con
     **evidencia** (archivo:línea, mediciones) y **se detiene** en un gate humano antes
     de generar.
2. Confirmas y le pides generar.
   → **Esperado:** escribe un `DESIGN.md` `origin: extracted` con evidencia por token;
     **documenta las inconsistencias reales** sin promediarlas, y marca `[INFERIDO]` lo
     no evidenciado. No exige spec validado ni brief.

**Resultado:** PASS si extrae con evidencia, para en el gate y respeta inconsistencias
· FALLO si promedia inconsistencias, o genera sin evidencia.
**Desviación → reportar:** issue citando `CU-5.d`.

## CU-5.e — Auditar, accesibilidad, evolucionar y medir impacto

**Precondición:** un `DESIGN.md` existente (generado o extraído).
**Mecanismo:** `wf-design-validate` / `wf-design-a11y-audit` / `wf-design-delta` /
`wf-design-sync` / `wf-design-export` → **`design-system-architect`** (export es mecánico).

1. Le pides auditar el `DESIGN.md` (lo editaste a mano).
   → **Esperado:** `wf-design-validate` reporta `OK` o `DESIGN_GAP` **sin regenerar** el
     archivo.
2. Le pides una auditoría de accesibilidad.
   → **Esperado:** `wf-design-a11y-audit` verifica contraste real, touch targets y focus
     order con severidad, contra WCAG.
3. Le pides un cambio incremental ("cambia el style_family").
   → **Esperado:** `wf-design-delta analyze` produce el informe delta; `apply` integra
     lo validado **preservando lo previo** (no regenera desde cero).
4. Tras un cambio, le pides saber qué quedó stale.
   → **Esperado:** `wf-design-sync` reporta qué flows/views/ui_prompt/exports quedaron
     desactualizados, con estado por artefacto.
5. Le pides exportar los tokens.
   → **Esperado:** `wf-design-export` genera los formatos pedidos (css, style-dictionary,
     compose, swiftui, tailwind) sin duplicar la SSoT.
6. ([[D-011]]) Auditas un `DESIGN.md` de un producto con `design_targets` que **divergen nativamente**
   (p. ej. `mobile-android` + `mobile-ios`) pero **sin** sección `## Platform Components`.
   → **Esperado:** `wf-design-validate` reporta **`DESIGN_GAP`** (Regla 11: la capa es obligatoria con
     targets divergentes declarados), **sin regenerar** el archivo. Con una **sola base**, su ausencia
     **no** es gap (no la exige).

**Resultado:** PASS si cada acción respeta su contrato (validar/auditar no regeneran;
delta preserva; sync no edita) y validate marca `DESIGN_GAP` por `## Platform Components` ausente solo
cuando hay targets divergentes · FALLO si validate reescribe el `DESIGN.md`, delta pisa lo previo, o
validate **ignora** la ausencia de `## Platform Components` con targets divergentes (o la exige con una
sola base).
**Nota de testeo ([[D-011]]):** el caso 6 ejercita el **gate de validación** de la Regla 11. `wf-design-validate`
Paso 4b resuelve `requires_platform_components` con el mismo subcomando determinista (`sdd-init-detect.py
target-platforms`) y pasa `REQUIRES_PLATFORM_COMPONENTS`/`NATIVE_PLATFORMS` al agente; el check 19 del
`validation-checklist.md` marca `DESIGN_GAP` si falta la capa con el gate en `true`. Sin `design_targets`
declarados (DESIGN.md suelto), el gate es `false` y su ausencia no es hallazgo.
**Desviación → reportar:** issue citando `CU-5.e`.

---

**Exploración de dirección visual (antes y alrededor del sistema).** Piezas opcionales
que anclan o exploran la dirección visual sin comprometer el `DESIGN.md` principal.
Todas delegan en **`design-system-architect`** / **`design-feature-architect`** salvo `wf-design-discover` (orquestador con
research web).

## CU-5.f — Capturar inspiración antes del brief (moodboard)

**Precondición:** un `_spec.md` de feature; aún sin brief cerrado.
**Mecanismo:** skill `wf-design-moodboard` → **`design-system-architect`**. Output:
`<basename>_design_moodboard.md`.

1. Le describes vibes ("quiero algo cálido, fotográfico, tipo Airbnb").
   → **Esperado:** captura las vibes (paletas, atmósfera, ilustración, texturas) en un
     `_design_moodboard.md` que alimenta el intake con material concreto; **no cierra el
     brief ni genera el sistema visual** (eso es intake/system).

**Resultado:** PASS si captura la inspiración sin saltarse el intake · FALLO si cierra
el brief o genera `DESIGN.md` desde el moodboard.
**Desviación → reportar:** issue citando `CU-5.f`.

## CU-5.g — Descubrir apps de referencia con research validado (discover)

**Precondición:** un `_spec.md` validado de la feature.
**Mecanismo:** skill `wf-design-discover` (**orquestador**, `WebSearch`/`WebFetch`,
modo `interactive` por defecto). Output: `<basename>_design_discovery.md`.

1. Le pides buscar apps de referencia para el sistema visual.
   → **Esperado:** hace research web de 3-5 apps reales del mercado y **valida cada una
     contigo** (no las da por buenas solas) antes de escribir
     `_design_discovery.md`, reutilizable aguas abajo por system/feature-prototype.

**Resultado:** PASS si propone referencias reales y las valida contigo · FALLO si
inventa apps, o no pide validación en modo interactivo.
**Desviación → reportar:** issue citando `CU-5.g`.

## CU-5.h — Explorar una rama paralela del `DESIGN.md` (branch)

**Precondición:** un `DESIGN.md` existente.
**Mecanismo:** skill `wf-design-branch` → **`design-system-architect`**. Output:
`DESIGN.<branch>.md` (no toca `DESIGN.md` salvo en `merge`).

1. Le pides explorar una variante ("prueba una versión más brand-forward").
   → **Esperado:** `create` escribe `DESIGN.<branch>.md` **sin tocar el principal**;
     `compare` enfrenta dos ramas; `merge --into` integra una rama solo cuando lo pides;
     `discard` la descarta.

**Resultado:** PASS si la rama vive aislada y `main` solo cambia en `merge` explícito ·
FALLO si modifica `DESIGN.md` al crear/comparar una rama.
**Desviación → reportar:** issue citando `CU-5.h`.

## CU-5.i — A/B testing visual de una feature (variant)

**Precondición:** un `_spec.md` y un `DESIGN.md`.
**Mecanismo:** skill `wf-design-variant` → **`design-feature-architect`**. Output:
`<feature>_variants.md`.

1. Le pides probar dos versiones de la feature ("haz un A/B del checkout").
   → **Esperado:** `create` genera 2+ variantes de los `_views.md`/`_ui_prompt.md`
     **compartiendo el mismo spec y `DESIGN.md`**, con hipótesis y métrica esperada
     declaradas; `compare` produce la tabla comparativa. No altera el contrato funcional.

**Resultado:** PASS si genera variantes con hipótesis sobre el mismo spec · FALLO si
diverge la funcionalidad entre variantes, o no declara hipótesis/métrica.
**Desviación → reportar:** issue citando `CU-5.i`.

## CU-5.j — Capturar y triajear feedback de stakeholders (feedback)

**Precondición:** feedback no estructurado de cliente/PM/dev/QA.
**Mecanismo:** skill `wf-design-feedback` → **`design-feature-architect`**. Output:
`<…>_feedback_capture.md` (capture) → triaje (triage).

1. Le pasas un comentario suelto ("al cliente no le gusta el color de los botones").
   → **Esperado:** `capture` lo registra como `_feedback_capture.md` con
     `status: pending_triage`, sin clasificar todavía.
2. Le pides triajearlo.
   → **Esperado:** `triage` lo clasifica en categorías accionables —**cambio de brief /
     delta visual / ajuste de feature / fuera de scope**— preservando la trazabilidad,
     sin redefinir el contrato visual por su cuenta.

**Resultado:** PASS si captura y luego triajea en las 4 categorías · FALLO si actúa el
feedback sin triaje, o lo clasifica de forma no accionable.
**Desviación → reportar:** issue citando `CU-5.j`.

---

## CU-5.k — Gate de spec fiable en Design (system y feature-prototype)

**Precondición:** un spec con HUs `[INCOMPLETO]`, items `[CRÍTICO]_(pendiente)_`, o
`status_sync: stale|needs_review`.
**Mecanismo:** `wf-design-system` / `wf-design-feature-prototype` (Paso 2) — se detienen
antes de delegar al agente.

1. Pides crear el `DESIGN.md` (o las pantallas) sobre un spec con HUs `[INCOMPLETO]` o `[CRÍTICO]` pendiente.
   → **Esperado:** **detiene** y redirige a la fase Spec (`wf-spec-gap-resolve`/`wf-spec-delta`/`wf-spec-validate`);
     no genera sistema visual ni prototipo sobre un spec no fiable.
2. El spec tiene `status_sync: stale|needs_review` (el PRD cambió).
   → **Esperado:** **detiene** igual y remite a resincronizar (`wf-spec-sync-from-prd`); no diseña sobre un spec derivado de un PRD viejo.

**Resultado:** PASS si ambos skills paran ante un spec no fiable y redirigen a Spec · FALLO si
generan diseño sobre un spec con `[INCOMPLETO]`/`[CRÍTICO]`/`stale`.
**Desviación → reportar:** issue citando `CU-5.k`.

## CU-5.l — System: anclaje de dirección visual (provisional vs confirmed) y policy de referencias

**Precondición:** un brief cerrado en modo `auto` (`autonomy_policy: ai-default`), o invocado
con `--no-brief`, o con research de referencias pobre/ausente.
**Mecanismo:** `wf-design-system` (Paso 5b anclaje; Paso 2e `reference_apps_policy`) → `design-system-architect`.

1. Generas el `DESIGN.md` con la dirección **no anclada**.
   → **Esperado:** antes de escribir, pide confirmación de la dirección inferida (`style_family`, paleta, `motion_level`) con `AskUserQuestion`.
2. Confirmas la dirección.
   → **Esperado:** nace `origin: generated`, `direction_confidence: confirmed`; sin `[INFERIDO]` de dirección.
3. No confirmas, o entorno headless (`CI=true` / `SDD_NON_INTERACTIVE=1`).
   → **Esperado:** nace `origin: generated-provisional`, `direction_confidence: provisional`, con los
     campos de dirección `[INFERIDO]` (informativo, **no bloquea**); **no aborta** indefinidamente.
4. El brief exige `reference_apps_policy: required` y no hubo research suficiente.
   → **Esperado:** **detiene**; no delega al agente con Reference Apps vacías.

**Resultado:** PASS si confirma o cae a provisional sin bloquear, y respeta `reference_apps_policy` ·
FALLO si escribe `generated` (no provisional) sin confirmación, o ignora la policy `required`.
**Desviación → reportar:** issue citando `CU-5.l`.

## CU-5.m — Intake: `DESIGN_GAP`, modo `auto` y brief existente

**Precondición:** según el sub-escenario.
**Mecanismo:** `wf-design-intake generate` (Pasos 4, 6, 7) → `design-system-architect`.

1. Una decisión crítica del brief no puede tomarse (usuario no responde, contradicción irresoluble).
   → **Esperado:** el agente devuelve `DESIGN_GAP` con la variable concreta y el workflow **NO escribe el brief**; reporta las variables pendientes.
2. Cierras el brief en modo `auto`.
   → **Esperado:** marca `autonomy_policy: ai-default` y registra la fuente de cada variable en
     `## Inferencias automáticas` (dejando la dirección no anclada aguas abajo, ver CU-5.l).
3. Ya existe un `DESIGN_BRIEF.md`.
   → **Esperado:** pregunta (a) actualizar variables / (b) sobrescribir desde cero / (c) cancelar; los
     cambios quedan en `## Update log`; no lo pisa en silencio.

**Resultado:** PASS si no escribe el brief ante `DESIGN_GAP`, marca `ai-default` en `auto` y pregunta
ante brief existente · FALLO si escribe un brief incompleto, o clobbea el brief existente sin preguntar.
**Desviación → reportar:** issue citando `CU-5.m`.

## CU-5.n — Feature-prototype: resolución de `target_tool` y conflicto cross-feature

**Precondición:** `DESIGN.md` y brief listos; el brief declara distintas `target_platforms` y hay
features ya prototipadas en el producto.
**Mecanismo:** `wf-design-feature-prototype` (Paso 3c target; Pasos 4-5 conflicto) → `design-feature-architect`
(`kb-design-conflict-expert`).

1. El brief/`DESIGN.md` declara `target_platforms: mobile` (o `web`/`desktop`).
   → **Esperado:** resuelve `target_tool: stitch` para mobile, `web-generic` para web/desktop;
     `both` → el agente decide y lo documenta en el `_ui_prompt.md`. Si nada lo declara, asume `mobile` y lo avisa.
2. Ya hay otras features prototipadas y la nueva entra en conflicto visual/navegación con ellas.
   → **Esperado:** aplica `kb-design-conflict-expert`, lista los conflictos y **NO escribe los
     artefactos** hasta que decidas; los falsos positivos se marcan `[POSIBLE-CONFLICTO-DESIGN-XX]`.

**Resultado:** PASS si deriva el `target_tool` correcto y para ante un conflicto real sin escribir ·
FALLO si fija un `target_tool` equivocado, o escribe artefactos pisando un conflicto cross-feature sin avisar.
**Desviación → reportar:** issue citando `CU-5.n`.

## CU-5.o — Validate: read-only y promoción acotada de dirección (provisional → confirmed)

**Precondición:** un `DESIGN.md` (a) editado a mano para auditar, o (b) con `direction_confidence: provisional`.
**Mecanismo:** `wf-design-validate` → `design-system-architect`. Read-only **salvo** la promoción acotada del Paso 5b (gated por confirmación humana, mismo patrón que el sello de `wf-prd-review`).

1. Le pides auditar un `DESIGN.md` que editaste a mano.
   → **Esperado:** reporta `OK`/`DESIGN_GAP` con severidad **sin regenerar ni parchear** el archivo (read-only).
2. El `DESIGN.md` es `provisional` y la auditoría de dirección **pasa** (sin `[CRÍTICO]`/`[ALTO]` en Visual Personality/Colors/Motion).
   → **Esperado:** presenta la dirección inferida y pide confirmación con `AskUserQuestion`; si confirmas →
     promueve `origin: generated-provisional → generated` y `direction_confidence: provisional → confirmed`,
     elimina los `[INFERIDO]` **de dirección**, bump **PATCH** y entrada de `## Changelog`; no toca tokens.
3. No confirmas, o entorno headless, o la auditoría de dirección tiene hallazgos abiertos.
   → **Esperado:** **no toca el archivo**; permanece `provisional`.

**Resultado:** PASS si audita read-only y solo promueve con confirmación humana y dirección sin hallazgos ·
FALLO si reescribe el `DESIGN.md` fuera de la promoción, o autopromueve sin confirmación.
**Desviación → reportar:** issue citando `CU-5.o`.

## CU-5.p — Delta: `[BRIEF_CHANGE_REQUIRED]` y precondiciones de apply

**Precondición:** un `DESIGN.md`; según el sub-escenario, nuevos requisitos que tocan
`style_family`/`clarity_vs_brand`/`autonomy_policy`, o un delta analysis inexistente/mal nombrado o con `[CRÍTICO]` pendiente.
**Mecanismo:** `wf-design-delta analyze` (Paso 4) / `apply` (Paso 2) → `design-system-architect`.

1. Pides un delta que cambia `style_family` (o `clarity_vs_brand`).
   → **Esperado:** el `analyze` lo marca `[BRIEF_CHANGE_REQUIRED]` y **NO** propone el cambio como delta;
     remite a actualizar el brief con `wf-design-intake` primero.
2. Pides `apply` con un segundo argumento que no termina en `_delta_analysis.md`.
   → **Esperado:** se detiene pidiendo un delta analysis generado por `analyze`.
3. El delta analysis tiene items `[CRÍTICO]_(pendiente)_` sin responder.
   → **Esperado:** se detiene y pide resolverlos antes de aplicar; `apply` preserva lo previo (extiende,
     muta solo lo listado), no regenera desde cero.

**Resultado:** PASS si frena la mutación de brief, exige un `_delta_analysis.md` válido y no aplica con
críticos pendientes · FALLO si aplica un cambio de `style_family` como delta, o aplica sin delta analysis/con críticos abiertos.
**Desviación → reportar:** issue citando `CU-5.p`.

## CU-5.q — A11y-audit: ramificación por plataforma

**Precondición:** un `DESIGN.md` con `target_platforms` declarado (táctil, web/desktop, o `both`); opcionalmente `--views`.
**Mecanismo:** `wf-design-a11y-audit` → `design-system-architect` (`kb-a11y-expert` + `kb-a11y-web-expert`). Escribe `a11y_audit_<fecha>.md`.

1. El producto es **táctil** (mobile).
   → **Esperado:** verifica targets táctiles (≥44pt iOS / ≥48dp Android) y contraste WCAG real por par; **no** aplica el criterio de puntero fino.
2. El producto es **web/desktop**.
   → **Esperado:** aplica el criterio de puntero fino (≥24×24px AA / 44×44 AAA) y los checks web (teclado,
     hover/focus content, reflow, focus visible); carga `kb-a11y-web-expert`.
3. El producto declara **`both`**.
   → **Esperado:** ejecuta los dos criterios de target; **ninguno relaja al otro**.
4. Pasas `--views` con un form sin labels asociados.
   → **Esperado:** lo marca `[CRÍTICO]`; reporta con severidad y escribe el reporte.

**Resultado:** PASS si ramifica por plataforma sin que un target relaje al otro y reporta por severidad ·
FALLO si aplica el criterio equivocado, relaja un target con el otro, o no detecta un form sin labels.
**Desviación → reportar:** issue citando `CU-5.q`.

## CU-5.r — Sync: propagación conservadora de la deriva (read-only)

**Precondición:** un `DESIGN.md` con artefactos de feature derivados; un cambio en el brief, en el `DESIGN.md` o en un `_spec.md`.
**Mecanismo:** `wf-design-sync` → `design-system-architect` (criterio conservador). Read-only; solo escribe su `_design_sync_report.md`.

1. Cambió el `DESIGN_BRIEF.md`.
   → **Esperado:** `DESIGN.md` → `needs_review` y, transitivamente, **todos** los artefactos de feature → `needs_review`.
2. Cambió el `DESIGN.md` (tokens/componentes).
   → **Esperado:** `views`/`ui_prompt` de las features que lo consumieron → `needs_review`; exports de tokens →
     `stale`; `flows` suele quedar `in_sync` salvo que el cambio afecte navegación.
3. Cambió un `_spec.md` de feature.
   → **Esperado:** `flows`/`views`/`ui_prompt` de **esa** feature → `needs_review`; el `DESIGN.md` solo si introduce una superficie nueva.
4. Un artefacto sin header/evidencia suficiente.
   → **Esperado:** `unknown` (nunca `in_sync` por optimismo); no regenera nada (solo su reporte).

**Resultado:** PASS si propaga la deriva conservadora por el grafo y no edita artefactos · FALLO si marca
`in_sync` algo cuya fuente cambió, o regenera artefactos.
**Desviación → reportar:** issue citando `CU-5.r`.

## CU-5.s — Branch: confirmación ante merge breaking y discard

**Precondición:** un `DESIGN.md` y una rama `DESIGN.<branch>.md` con cambios.
**Mecanismo:** `wf-design-branch` `merge` (Paso 5) / `discard` (Paso 6) → `design-system-architect`.

1. Pides mergear una rama cuyo diff es **breaking** (cambia `style_family`, `primary`, tipografía, o elimina componentes).
   → **Esperado:** ejecuta `compare` internamente, detecta el cambio MAJOR (Regla 22) y pide confirmación
     explícita antes de sobrescribir el target y bumpear versión; no mergea breaking en silencio.
2. Pides descartar una rama.
   → **Esperado:** pide confirmación (es irreversible) antes de borrar `DESIGN.<branch>.md`; deja entrada en el `## Changelog` de main.
3. Creas o comparas una rama.
   → **Esperado:** `DESIGN.md` (main) **no se toca**; solo un `merge` explícito lo modifica.

**Resultado:** PASS si confirma el merge breaking y el discard, y main solo cambia en `merge` · FALLO si
mergea breaking sin confirmar, borra sin confirmación, o toca main al crear/comparar.
**Desviación → reportar:** issue citando `CU-5.s`.

## CU-5.t — Variant: hipótesis y métrica obligatorias

**Precondición:** un spec y un `DESIGN.md`; un brief con o sin `Success Metrics`.
**Mecanismo:** `wf-design-variant create` (Paso 2) → `design-feature-architect`.

1. Pides crear variantes sin una hipótesis clara.
   → **Esperado:** **se detiene** ("sin hipótesis el A/B es decoración"); no genera variantes hasta que definas qué esperas que cambie.
2. El brief no declara `Success Metrics`.
   → **Esperado:** advierte que sin métricas no se puede evaluar la variante ganadora y pide confirmación antes de continuar.
3. Generas las variantes con hipótesis.
   → **Esperado:** comparten spec y `DESIGN.md`, solo difieren en cómo materializan la feature; no introducen
     funcionalidad nueva (eso serían features distintas).

**Resultado:** PASS si exige hipótesis, avisa de métricas ausentes y mantiene la funcionalidad entre variantes ·
FALLO si genera variantes sin hipótesis, o diverge la funcionalidad entre ellas.
**Desviación → reportar:** issue citando `CU-5.t`.

## CU-5.u — Export: idempotencia, `EXPORT_GAP` y `--dry-run`

**Precondición:** un `DESIGN.md` (con o sin alguna sección de tokens incompleta).
**Mecanismo:** `wf-design-export` (**sin agente** — traduce fielmente). Output: `tokens/<formato>` + `manifest.md`.

1. Exportas dos veces a las mismas plataformas.
   → **Esperado:** **idempotente** — el segundo run produce el mismo output, sin duplicar ni divergir.
2. Falta una sección crítica del `DESIGN.md` (p. ej. `colors` incompleto).
   → **Esperado:** marca `EXPORT_GAP: <sección>` y omite ese bloque; **no inventa** valores.
3. Exportas con `--dry-run`.
   → **Esperado:** imprime el contenido **sin escribir** ningún archivo (preview); no toca `tokens/`.

**Resultado:** PASS si es idempotente, marca `EXPORT_GAP` y `--dry-run` no escribe · FALLO si diverge entre
runs, fabrica valores ausentes, o `--dry-run` escribe archivos.
**Desviación → reportar:** issue citando `CU-5.u`.

## CU-5.v — Feedback: triage completo, `functional_change` a Spec y `out_of_scope`

**Precondición:** feedback no estructurado de un stakeholder.
**Mecanismo:** `wf-design-feedback` `capture` → `triage` → `design-feature-architect` (7 categorías).

1. Capturas un comentario.
   → **Esperado:** lo registra **literal** en `_feedback_capture.md` con `status: pending_triage`; no lo reformula ni clasifica todavía.
2. Le pides triajear un feedback que en realidad es un cambio **funcional** (no visual).
   → **Esperado:** lo clasifica `functional_change` y remite a la fase Spec (`wf-spec-delta` / `wf-prd-change`),
     no lo trata como delta de design.
3. El feedback es opinión sin dirección accionable.
   → **Esperado:** lo clasifica `out_of_scope` y lo documenta con justificación, sin actuarlo.

**Resultado:** PASS si captura literal, distingue `functional_change` (→Spec) y `out_of_scope` · FALLO si
actúa el feedback sin triaje, o trata un cambio funcional como delta visual.
**Desviación → reportar:** issue citando `CU-5.v`.

## CU-5.w — Feature con design targets divergentes: base + overrides per-view ([[D-011]])

**Precondición:** topología `design` (o consumer con repo de diseño) cuyo `project-init.json` declara
`design_targets` que **divergen nativamente** (p. ej. `mobile-android` + `mobile-ios`); `DESIGN.md` con
capa `## Platform Components` (`kb-design-system-contract` Regla 11) y brief listos.
**Mecanismo:** `wf-design-feature-prototype` (Paso 3d divergencia + Paso 4 paths `targets/<target>/` +
Paso 5 instrucción de overrides) → `design-feature-architect`. Resolución determinista:
`.sdd/scripts/sdd-design-resolve.py` (cubierta por `test_sdd_design_resolve.py`).

1. Le pides preparar las pantallas de la feature en un repo con design targets divergentes.
   → **Esperado:** genera la **base agnóstica** (`<feature>_flows.md`/`_views.md`) y, **solo para las
     vistas que divergen de verdad**, overrides **per-view** bajo `targets/<target>/<feature>_views.md`
     (`kb-design-feature-artifacts` Regla 8). La especificidad de componente nativo (Material vs HIG) la
     toma de `## Platform Components` del `DESIGN.md`, **no** la redefine en la vista. **No duplica** las
     vistas que no divergen (heredan la base); un target sin divergencia real no genera `targets/`.
2. Resuelves un target para un consumidor.
   → **Esperado:** `sdd-design-resolve.py resolve --base … --override targets/<target>/… --merged` devuelve
     `base ⊕ override` (la vista overrideada gana completa; las no overrideadas heredan la base intacta).
     Sin override para ese target → base intacta.

**Resultado:** PASS si emite base + overrides solo donde hay divergencia real y la resolución per-view es
determinista · FALLO si duplica la base entera por target, mete condicionales de plataforma inline en la
base, o baja la divergencia de componente nativo a la vista en vez del `DESIGN.md`.
**Desviación → reportar:** issue citando `CU-5.w`.

## CU-5.x — Sync cross-repo: drift del repo de diseño en un consumer ([[D-011]])

**Precondición:** un repo consumer cuyo `project-init.json` declara `design_source` + `design_source_pin`
(repo de diseño aparte, 5.C1b) y el repo de diseño **ha avanzado** desde el pin.
**Mecanismo:** `wf-design-sync` (Paso 2b cross-repo) apoyado en `.sdd/scripts/sdd-source-drift.py check`
(SHA y diff los da git, **advisory**; cubierto por `test_sdd_source_drift.py`).

1. El repo de diseño avanzó (cambió un `_views.md` base o el `DESIGN.md`) respecto al pin de este repo.
   → **Esperado:** `sdd-source-drift.py` marca la fuente `design` como `drifted: true` y lista los
     artefactos relevantes cambiados (`changed`); `wf-design-sync` lo refleja como **deriva cross-repo**:
     los artefactos resueltos `base ⊕ override` y, transitivamente, `_plan.md`/`_tasks.md` → `needs_review`.
     Recomienda revisar, re-resolver (`sdd-design-resolve.py`) y actualizar `design_source_pin`.
2. El repo de diseño NO avanzó (pin == HEAD).
   → **Esperado:** `drifted: false`; no marca deriva cross-repo.

**Resultado:** PASS si detecta el drift del repo de diseño por pin git y lo propaga conservadoramente ·
FALLO si ignora el avance del repo de diseño, o el veredicto de drift lo decide el agente en vez de git.
**Desviación → reportar:** issue citando `CU-5.x`.

## CU-5.y — Feature-prototype sobre un `DESIGN.md` de otra familia de plataforma (mismatch co-localizado, [[D-011]])

**Precondición:** una feature con superficie **móvil** que consume un `DESIGN.md` **co-localizado** autorado
para **web** — el `DESIGN.md` declara `target_platforms: [web]` (referencias, breakpoints y tokens sesgados a
puntero/desktop). Caso típico: un consumer móvil cuyo `artifacts_source` trae diseño co-localizado web, o un
standalone cuyas superficies viran de web a móvil. **No hay repo de diseño aparte** — si lo hubiera, el mismatch
lo caza el guard de cobertura **en el init** (→ `CU-1.i` caso 7); aquí el `DESIGN.md` es el contrato y su
frontmatter `target_platforms` es la única señal, detectable solo al **autorar la feature**.
**Mecanismo:** `wf-design-feature-prototype` → `design-feature-architect`, que al derivar flows/views **compara
la familia de la superficie de la feature con el `target_platforms` del `DESIGN.md`** (frontmatter,
`kb-design-system-contract`). Es **advisory** (no bloquea): la familia ausente se resuelve evolucionando el
`DESIGN.md` (`wf-design-delta`), no fabricando tokens fuera de contrato.

1. Pides derivar las pantallas **móviles** de la feature contra un `DESIGN.md` cuyo `target_platforms` es `[web]`.
   → **Esperado:** el agente **detecta el mismatch de familia** y lo **señala** (advisory): el contrato visual se
     autoró para `web` (layout de puntero, breakpoints desktop, sin touch targets) y la feature es `mobile`;
     derivar pantallas móviles heredaría ese sesgo. Recomienda **evolucionar el `DESIGN.md`** a la familia móvil
     (`wf-design-delta`) o confirmar que es intencional, **antes** de producir los artefactos como si el contrato
     encajara. **No fabrica** tokens/escala/touch targets móviles que el `DESIGN.md` no define, ni los baja a la vista.
2. El `DESIGN.md` cubre la familia de la feature (`target_platforms` incluye `mobile`).
   → **Esperado:** sin aviso; deriva con normalidad.

**Resultado:** PASS si señala el mismatch de familia entre la superficie de la feature y el `target_platforms`
del `DESIGN.md` (advisory, sin bloquear ni inventar capa visual fuera de contrato) y calla cuando hay cobertura ·
FALLO si produce silenciosamente pantallas de una familia que el `DESIGN.md` no cubre, o **inventa** la capa
visual de la plataforma ausente en vez de remitir a evolucionar el `DESIGN.md`.
**Desviación → reportar:** issue citando `CU-5.y`.
