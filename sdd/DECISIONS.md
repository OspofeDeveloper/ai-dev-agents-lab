# Registro de decisiones del ecosistema SDD

Constancia de las **decisiones de diseño** y los **aprendizajes** del ecosistema: por qué se hizo algo de una manera y no de otra, qué aprendimos al equivocarnos. Complementa al `CHANGELOG.md` (qué cambió, por versión) respondiendo al **por qué**.

Formato: una entrada `## D-NNN — <título>` por decisión, **más reciente arriba** (como el CHANGELOG). Cada entrada lleva: fecha, estado, contexto, decisión, alternativas descartadas, consecuencias/aprendizaje y referencias. Las entradas son append-only: si una decisión se revierte, no se borra — se añade una nueva que la supersede y se marca la vieja `Superada por D-MMM`.

---

## D-013 — La topología `design` instala rol `full`, no `system` (corrección de D-011)

- **Fecha:** 2026-06-20 · **Estado:** Adoptada · **Corrige:** D-011 (slice 12.3)

**Contexto.** Probando el init de la topología `design` (CU-1.b/CU-1.q) sobre repos reales se vio que
solo se instalaba `design-system-architect` + workflows de sistema: **faltaban** `design-feature-architect`,
`wf-design-feature-prototype`, `wf-design-variant` y `kb-design-feature-artifacts`. Causa: D-011 (12.3)
fijó `DESIGN_ROLE_BY_TOPOLOGY["design"] = "system"`, y `install.sh --design-role=system` instala solo el
agente de sistema. Pero la **definición** de la topología `design` (en el propio SKILL) es que el repo
autora **ambos** niveles: el sistema visual (`DESIGN.md`/brief/tokens) **y** los bundles de feature
(flows/views/ui_prompt + overrides `base ⊕ override per-view`). Con rol `system`, el repo de diseño **no
podía producir los bundles per-view** — que son el núcleo de D-011 (lo que prueba CU-5.w). El bug era
auto-contradictorio: el `CLAUDE.md` generado y el informe del init prometían `wf-design-feature-prototype`
y `features/<nombre>/design/`, workflows que no quedaban instalados.

**Decisión.** La topología `design` deriva **`design_role: full`** (ambos agentes). `full` aquí significa
"los dos agentes de la fase design" (system + feature); **no** arrastra plan/tasks — eso lo gobierna
`phases` (`["design"]`), no el `design_role`. Distinción que se mantiene: `authoring` con diseño sigue en
rol `system` (ahí los consumers derivan flows/views en SUS repos), mientras que el repo `design` **sí**
autora los bundles localmente — esa es su razón de ser. Cambio en la función pura testeada
(`DESIGN_ROLE_BY_TOPOLOGY`), no en prosa.

**Alternativas descartadas.**
- *Mantener `system` y documentar que los bundles se autoran en otro sitio* → contradice D-011 (el repo
  `design` ES el SSoT de los bundles per-view) y deja `wf-design-feature-prototype` sin hogar.
- *Ampliar el rol `system` para que instale también el feature-architect* → rompe la semántica de `system`
  (que en authoring debe seguir instalando solo el sistema); el rol correcto ya existe: `full`.

**Consecuencias / aprendizaje.** `RepairPlanTest` se endurece: un repo `design` con rol `system` es
**inconsistente** (`needs_repair`), y la reparación determinista lo lleva a `full`. Los proyectos `design`
inicializados antes de este fix tienen el feature-architect ausente: se reparan con `/wf-project-init` →
"Completar / ampliar" (el repair-plan instala lo que falta) tras `bash setup.sh`. Aprendizaje: cuando una
topología declara una capacidad ("autora bundles de feature"), el rol de instalación debe **instalar el
agente que la ejecuta** — el `design_role` no es una etiqueta descriptiva, es el contrato de qué se instala.

**Referencias.** `scripts/sdd-init-detect.py` (`DESIGN_ROLE_BY_TOPOLOGY["design"]`) ·
`tests/test_sdd_init_detect.py` (`RepairPlanTest.test_design_topology_derives_full`,
`test_design_topology_system_role_is_inconsistent`) · `bootstrap/skills/wf-project-init/SKILL.md` (rama
DESIGN, def de topología, esquema) · `conformance/casos-de-uso/cu-01-inicializar.md` (CU-1.q) ·
`install.sh` (`--design-role`) · D-011 (topología design).

---

## D-012 — Un solo SSoT de diseño por producto: las opciones de diseño son un fork excluyente, con guard advisory en el consumer

- **Fecha:** 2026-06-19 · **Estado:** Adoptada

**Contexto.** Tras D-011, el diseño puede vivir en dos sitios: co-localizado en el repo `authoring`
(rol `system`, para equipos pequeños) o en un repo `design` dedicado (topología `design`). Probando
`CU-1.b` se planteó la duda: ¿es contraproducente ofrecer diseño en `authoring` **y** además la
topología `design`? ¿No deberíamos unificar todo el diseño en el repo SSoT y usarlo siempre, aunque
el equipo sea pequeño? El riesgo real percibido: que un producto acabe con **dos `DESIGN.md`**
(uno co-localizado en specs + uno en el repo de diseño), violando la SSoT.

**Decisión.** Las dos opciones **se mantienen** y son un **fork excluyente** (no una duplicación):
el diseño de un producto vive **en exactamente un sitio** — co-localizado en `authoring` (equipo
pequeño, un repo) **o** en un repo `design` dedicado (equipo de diseño / multi-superficie), nunca en
ambos. No se unifica a la fuerza en el repo de diseño: obligar a un equipo de un solo repo a mantener
**dos** repos solo para tener un `DESIGN.md` es el coste que D-011 decidió evitar (regresión de
ergonomía, no mejora). El invariante **«un solo SSoT de diseño por producto»** se protege con un
**guard advisory en el consumer** —el único punto que ve ambos repos a la vez—, no con un hard-block
en el init (los repos se inicializan por separado y no se ven entre sí):
1. Detección **determinista** en `sdd-source-drift.py` (`dual_design_ssot`): un consumer con
   `design_source` cuyo `artifacts_source` **también** declara la fase `design` → `dual_design_ssot:
   true`. Expuesto en `check` (campo `design_ssot`).
2. `wf-prepare-plan` (Paso 2.5) y `wf-project-init` 5.C1b **avisan** (no bloquean): el handoff se
   resuelve por `design_source` y el co-localizado queda ignorado; unifica en un solo SSoT.
3. **Nudge** en la pregunta de diseño de `authoring` (5.A2): responde *No* si el diseño vivirá en un
   repo dedicado.

**Alternativas descartadas.**
- *Quitar diseño de `authoring`* → mata el caso pequeño co-localizado que D-011 protegió expresamente.
- *Unificar siempre en el repo de diseño (obligatorio)* → peaje de dos repos para todo equipo; peor
  ergonomía sin beneficio para quien no tiene función de diseño separada.
- *Hard-block en el init* → inviable: el init es per-repo y no ve de forma fiable el otro checkout. El
  consumer es la única junta donde el conflicto es observable.
- *Dejarlo solo en prosa* → el conflicto quedaba silencioso (el handoff elige `design_source` sin
  avisar de que hay un `DESIGN.md` compitiendo); por eso el veredicto es determinista (script testeado).

**Consecuencias / aprendizaje.** El guard es **advisory**, no bloqueante: una ventana de migración
(mover el diseño de co-localizado a repo dedicado) es legítima y transitoria. La detección vive donde
el conflicto es visible (consumer), no donde se origina (dos inits independientes). `DualDesignSsotTest`
(4 casos) fija el invariante. Conformance: `CU-1.i` (caso 4) y `CU-6.k`.

**Referencias.** `scripts/sdd-source-drift.py` (`dual_design_ssot`) · `tests/test_sdd_source_drift.py`
(`DualDesignSsotTest`) · `bootstrap/skills/wf-project-init/SKILL.md` (5.A2 nudge, 5.C1b guard) ·
`pipeline/plan/skills/wf-prepare-plan/SKILL.md` (Paso 2.5) · D-011 (topologías de diseño).

---

## D-011 — Topología `design`: repo de diseño SSoT con bundles de feature por target (base ⊕ override) y consumer multi-fuente

- **Fecha:** 2026-06-18 · **Estado:** Propuesta (borrador — pendiente de implementación en ciclo aparte)

**Contexto.** El modelo de 3 topologías (D-005) coloca el sistema de diseño (`DESIGN.md`, rol `system`)
dentro de `authoring` y deja que los `consumer` autoren `flows`/`views` localmente (rol `feature`)
consumiendo un único SSoT (`artifacts_source`, CU-1.i). La regla de copia agnóstica de flows/views
(hoy inline en la **Regla 7** de `kb-design-feature-artifacts`, `SKILL.md:131-136` — no hay "Regla 8"
numerada) **fuerza `flows`/`views` a una sola copia agnóstica** + "Notas responsive"; solo el
`ui_prompt` diverge por familia. Eso **no contempla** ni el split de componentes nativos Android/iOS
ni phone/tablet, que exigen divergencia a nivel views/flows. Investigando el init se vio además que
`surfaces`/`targets`/`has_ui` de `project-init.json` son **write-only** (se escriben, nadie los lee
aguas abajo) y que `target_platforms` no se deriva de nada (el template del brief lo hardcodea a
`iOS/Android`, `design_brief_template.md:18`).

**Decisión.** Se adopta una **4ª topología `design`**: un repo SSoT de diseño que autora (a) el
sistema agnóstico (`DESIGN.md`, brief, tokens; `design_role: system`, `phases:["design"]`, sin
prd/spec/plan/tasks) y (b) los **bundles de feature por design target**. Núcleo:
1. **Design target** = etiqueta con convención **validada** `<familia>[-<plataforma>][-<formfactor>]`;
   la **familia es obligatoria** y debe ser una de `{mobile, web, desktop}` (token del que se deriva
   `target_platforms`); el resto de tokens, libres.
2. **base ⊕ override**: `flows`/`views` se autoran una vez como **base agnóstica**; un target añade
   su **override** solo cuando diverge de verdad (componentes nativos, layout tablet). El consumidor
   resuelve `base ⊕ override(target)` (el override gana donde existe). Relaja la regla de copia
   agnóstica preservando el principio de no duplicar (solo se materializa lo que cambia).
3. Los `flows`/`views` de feature **se mueven al repo `design`** en el caso consumer-con-repo-`design`:
   el consumer los resuelve en **solo lectura** y ya no los autora localmente — esto **supersede a
   CU-1.i** para ese caso. El caso co-localizado (`authoring`/`standalone`) los mantiene locales.
4. `target_platforms` (familias) se **deriva** de los design targets declarados.
5. El consumer con UI pasa a ser **multi-fuente**: declara dónde vive el `DESIGN.md` (mismo SSoT de
   specs o repo `design` aparte → `design_source` + pin) y qué `design_targets` consume.
6. **Aditivo, no reemplazo**: el caso co-localizado sigue válido para equipos pequeños.

**Expansión de fit (decisión de producto, no técnica).** El fit declarado de la fase design
(`pipeline/design/CLAUDE.md`, `design/README.md`, ROADMAP 7.1) era **equipos SIN diseñador dedicado,
greenfield, prototipado Stitch/web-generic**; ROADMAP 7.6 descartó Figma con la condición textual
*"reconsiderable solo si el fit se expandiera a equipos con diseñador propio — decisión de producto,
no técnica"*. Esta decisión **es esa expansión**: el caso que motiva D-011 (repo de diseño SSoT
propio, multi-superficie con divergencia nativa Android/iOS y phone/tablet, varios repos de código
consumiendo un diseño compartido) es propio de **organizaciones con función de diseño dedicada y
escala multi-repo**. Se asume conscientemente: el ecosistema pasa a cubrir también ese perfil. No
reabre Figma por sí sola (sigue fuera por 7.6), pero **retira la premisa "sin diseñador" como límite
duro** y la condición de 7.6 queda satisfecha — quien quiera reevaluar Figma ya tiene el gancho. El
fit escrito en `design/CLAUDE.md`/`README.md` se actualizará **cuando la capacidad se implemente**
(no antes, para no anunciar lo que aún no existe); este ciclo solo registra la decisión y reconcilia
el ROADMAP.

**Alternativas descartadas.**
- *Modelar diseño como overlay/tecnología* → rompe el modelo de fases/targets; es topología, no stack.
- *Etiquetas de target totalmente libres* → la derivación de `target_platforms` (familias) deja de ser
  determinista; por eso la familia es token validado obligatorio.
- *Duplicar `flows`/`views` completos por target* → viola el principio de no duplicar; el override
  parcial sobre una base compartida lo respeta.
- *Mantener `flows`/`views` locales en el consumer con repo `design`* → reintroduce duplicación y
  divergencia entre repos; el SSoT único de diseño lo evita (a costa de staleness cross-repo, abajo).
- *Mantener el fit "sin diseñador" y no soportar este caso* → descartado: el equipo objetivo real
  (PM + diseño + devs) lo necesita; el coste de no cubrirlo es que el diseño multi-superficie viva
  fuera del pipeline. La expansión es deliberada (ver arriba).

**Consecuencias / aprendizaje.** (1) La 4ª opción de Q1 **agota el cupo de 4** de `AskUserQuestion`
(`wf-project-init/SKILL.md:283-289`): futuras topologías necesitarían otra UX (pregunta en dos pasos).
(2) Mover flows/views al repo `design` **multiplica la superficie de staleness cross-repo** (specs
SSoT + design SSoT + N repos de código): exige pin de `design_source` y extender `wf-design-sync`
para drift entre repos — es subsistema, no nota al pie. (3) Convierte campos write-only en derivables.
(4) **Corrección factual respecto al borrador inicial:** `derive_target_platforms` **no existe** hoy;
el trabajo previo (2) entregó `derive_design_role` + los write-only, no esta función — hay que
**construirla** net-new siguiendo el patrón de D-010 (función pura testeada en `sdd-init-detect.py`).
(5) **Grano del override (RESUELTO): per-view, con la divergencia de sistema empujada al `DESIGN.md`.**
El override de `views` es **por vista entera** (la unidad ya es la pantalla — `views` es "SSoT de
pantallas"): si un design target tiene override de una vista, gana esa vista completa; si no, hereda la
base intacta. Resolución trivial y determinista (alineada con D-009/D-010), y coherente con el layout
ya bocetado (`targets/<target>/<feature>_views.md` es un fichero de vista completo). **Per-component se
descarta**: `views` es markdown en prosa, no un árbol de componentes con IDs estables, y fusionar prosa
componente-a-componente sería el grano *menos* determinista. La especificidad de **componente nativo**
(Material vs HIG, patrón de navegación) **no es de la vista sino del sistema**: vive en una **capa de
mapeo de componentes por plataforma en el `DESIGN.md`** (esto resuelve también la open Q1) — así la
vista queda agnóstica y solo se overridea cuando la *composición/layout* de la pantalla diverge de
verdad (tablet), o se overridea `flows` si cambia la navegación. *Per-state* queda como refinamiento
futuro opt-in (el vocabulario de estados es cerrado, así que es viable) solo si el uso real muestra
vistas que divergen en un único estado y duplicarlas molesta — YAGNI hasta entonces. Coste aceptado:
una vista overrideada **re-enuncia sus estados no cambiados**; está acotado a las vistas que divergen.
(6) **Vocabulario de familias fijado:** `target_platforms` ∈ `{mobile, web, desktop}` (3 familias).
`tablet` NO es familia: es un **form-factor** dentro de `mobile`/`desktop` (un token más del design
target, p. ej. `mobile-tablet`), tal como `kb-design-layout` ya lo trata como breakpoint. Esto resuelve
la incoherencia del borrador (que en un punto listaba `{mobile, web, desktop, tablet}`).

**Implementación por fases.** Se ejecuta de forma incremental, no en bloque (con el grano del override
ya resuelto —ver (5)—, el **subsistema de staleness cross-repo** es el punto de mayor riesgo restante). **Este ciclo (foundational, valor
independiente):** se construyen en `sdd-init-detect.py` las funciones puras testeadas
`derive_target_platforms` (familias desde design targets) y la validación de la convención de
etiquetas (familia obligatoria), siguiendo el patrón de `derive_design_role` (D-010); y se alinea el
vocabulario del template del brief (`design_brief_template.md`, hoy `iOS/Android`) a familias. Estas
piezas tienen valor por sí solas (dan función a campos hoy write-only) aunque el resto no se construya.
**Ciclos posteriores (diferido, tras cerrar el grano del override):** Q1 (4ª opción `design`), esquema
de `project-init.json` (`design_targets`, `design_source`/pin), `kb-design-feature-artifacts` (promover
la regla de copia agnóstica a una **Regla 8** numerada y relajarla), wiring del consumer multi-fuente,
subsistema de staleness cross-repo y `CU-01`.

**Referencias.** `floating-splashing-eclipse.md` (propuesta completa) ·
`pipeline/design/skills/kb-design-feature-artifacts/SKILL.md:131-136` (regla de copia agnóstica) ·
`bootstrap/skills/wf-project-init/SKILL.md` (Q1, límite de 4 opciones) ·
`scripts/sdd-init-detect.py` (`derive_design_role` como precedente de patrón) ·
`pipeline/design/skills/kb-design-brief/references/design_brief_template.md:18` (familias) ·
D-005 (topologías), D-010 (función pura testeada).

---

## D-010 — La reparación de un init a medias es determinista: `phases` es el contrato, no se repregunta el rol

- **Fecha:** 2026-06-18 · **Estado:** Adoptada

**Contexto.** Probando `CU-1.e` (`init-incomplete`: una fase declarada en `phases` de
`project-init.json` pero sin instalar), dos corridas del mismo escenario divergieron: en authoring
con `design` declarado y `design_role: null`, una corrida abría un `AskUserQuestion` ("instalar design
system / quitar design") y otra resolvía sola a `system`. Ambas pasaban el criterio de entonces
(*"repara sin re-entrevistar de cero"*) porque una pregunta puntual no es re-entrevistar. La causa raíz:
el SKILL recitaba en prosa la lógica de reparación y dejaba latitud al agente, así que el rol —que es
**determinado** por la topología— se trataba como ambiguo.

**Decisión.** La reparación (extend) es **determinista y silenciosa**: `phases` es el contrato (es el
mismo campo con el que el hook declara `init-incomplete`), así que lo declarado-pero-no-instalado **se
instala**, y el `design_role` se **deriva de la topología** (authoring→`system`, consumer-con-UI→
`feature`, standalone→`full`) — sin `AskUserQuestion` para decidir el rol. Quitar una fase declarada
**no** es reparación: es un cambio de alcance explícito (otra acción), no una verja insertada en cada
repair. Para sacar el *qué* de la prosa, la derivación vive como **función pura testeada** en
`sdd-init-detect.py` (`derive_design_role` + subcomando `repair-plan`, con `missing_phases`,
`expected_design_role`, `needs_repair`); el SKILL solo dice "aplica el `repair-plan`, no preguntes". El
agente informa **post-hoc** de lo instalado (p. ej. "instalé `design` rol system porque estaba
declarado; quítalo con 'Completar / ampliar' si no lo querías").

**Alternativas descartadas.**
- *Preguntar siempre instalar-vs-quitar al reparar* → relitiga la misma declaración que disparó el
  repair; añade fricción al caso común; el rol nunca es ambiguo dada la topología.
- *Respetar `design_role: null` como "no hay diseño"* → contradice `phases` (que sí declara design);
  `phases` es el campo autoritativo, `design_role` es metadato derivado a recomputar.
- *Dejar la lógica solo en prosa del SKILL* → es lo que causó la divergencia; no es testeable.

**Consecuencias / aprendizaje.** `CU-1.e` se endurece: abrir un `AskUserQuestion` para decidir el rol
o el instalar-vs-quitar de una fase ya declarada es **FALLO**. El *qué repara* queda como invariante
automático (`RepairPlanTest`, 9 casos); lo único manual es que el agente **aplique** el plan sin
preguntar. Aprendizaje transversal (mismo patrón que D-009): cuando una conducta determinista se deja
en prosa, el agente improvisa y diverge — hay que **codificarla** y dejar a la prosa solo el *cómo
aplicarla*. Requiere `bash setup.sh` para propagar el SKILL nuevo a `~/.claude/skills/` (instala por
copia, no symlink); hasta entonces el agente carga la regla vieja.

**Referencias.** `scripts/sdd-init-detect.py` (`derive_design_role`, `repair-plan`) ·
`tests/test_sdd_init_detect.py` (`RepairPlanTest`) · `bootstrap/skills/wf-project-init/SKILL.md`
(reparación de fase declarada en extend) · `conformance/casos-de-uso/cu-01-inicializar.md` (`CU-1.e`).

---

## D-009 — La visibilidad del modo SDD es AMBIENTE (status line), no anuncios en el chat

- **Fecha:** 2026-06-17 · **Estado:** Adoptada

**Contexto.** Probando `CU-1.c` (modo libre), el agente anunciaba en el chat "el proyecto está en
modo libre" en **cada** sesión. El usuario quería **ver** que el proyecto está en SDD/libre (por si
algún día cambia), pero un anuncio por-sesión en el chat es ruido recurrente que contradice el valor
mismo del modo libre (cero huella de SDD) y, por repetición, se vuelve invisible — no cumple ni el
objetivo de discoverability. El spec ya pedía silencio en chat (`claude-global-block.md` modo libre:
"No vuelvas a mencionar SDD…"); el anuncio era el agente saliéndose del spec.

**Decisión.** Separar **avisar** (chat, puntual) de **recordar** (ambiente, permanente): el chat
permanece en silencio sobre SDD en modo libre, y la visibilidad del estado SDD se da en la **status
line** mediante un helper `bootstrap/sdd-statusline.sh` que imprime un **segmento corto** —
`⚙ SDD:<topology>` (inicializado), `⚙ SDD:libre` (modo libre, tenue), `⚙ SDD:init pendiente` — por
**find-up** (mismo criterio que el hook), o **nada** si SDD no aplica. Es **componible**: imprime solo
el segmento, sin separadores, para encajar en cualquier status line. `setup.sh` lo copia a
`~/.claude/hooks/` y registra una `statusLine` **solo si no hay una** (jamás pisa la del usuario; si
existe, imprime la guía para llamarlo). El helper es **fuente única** de la lógica (sin duplicar en
cada status line); `uninstall` borra el helper y desregistra la status line solo si es la nuestra.

**Alternativas descartadas.**
- *Anuncio por sesión en el chat* → ruido recurrente; se ignora por repetición; rompe el "cero huella".
- *Silencio total sin indicador* → pierde la discoverability que el usuario pedía.
- *Inlinear la lógica en cada status line* → drift entre copias; mejor un helper único.
- *Auto-inyectar el segmento en la status line existente del usuario desde setup.sh* → inviable/invasivo
  (puede ser cualquier comando); se documenta la integración manual en su lugar.

**Consecuencias / aprendizaje.** `CU-1.c` se matiza: silencio en chat = correcto; que la status line
muestre `⚙ SDD:libre` = esperado, no fallo. Para usuarios con status line propia la integración es
manual (en este repo, el `statusline.py` del autor —fuera del repo— llama al helper con `cwd`, envuelto
en try/except para no poder romper la línea). El helper **nunca falla** (siempre exit 0, imprime nada
ante error): una status line no puede permitirse tumbar por un segmento.

**Hueco detectado al implementar:** el silencio en chat estaba solo *implícito*. La rama de modo
libre del wizard sí lo decía ("No vuelvas a mencionar SDD"), pero las secciones **"Sin directiva"** y
el **fallback** del `claude-global-block.md` —que gobiernan las **sesiones recurrentes** (free ya
fijado)— no lo prohibían, así que el agente anunciaba el modo "por transparencia" (visto en `CU-1.c`).
Se endureció el bloque para **prohibir explícitamente anunciar el modo en el chat** (la status line es
el canal). Requiere `bash setup.sh` para propagar el bloque a `~/.claude/CLAUDE.md`; hasta entonces el
contexto del agente lleva el bloque viejo y la línea puede reaparecer.

**Referencias.** `bootstrap/sdd-statusline.sh` · `setup.sh` (paso 4b + limpieza en uninstall) ·
`conformance/casos-de-uso/cu-01-inicializar.md` (`CU-1.c`) · `bootstrap/claude-global-block.md`
(silencio en chat en modo libre).

---

## D-008 — Vista de cobertura "por componente" en cada CU (forward), con checklist de ejecución

- **Fecha:** 2026-06-17 · **Estado:** Adoptada

**Contexto.** La batería de conformance (`conformance/casos-de-uso/cu-*.md`) está organizada por
**objetivo de usuario** (journey), no por skill. El cruce skill→CU existía solo en dirección inversa
y en otro fichero (`conformance/ROADMAP.md`, una fila por `wf-*` con columna "CU que lo ejercitan"),
que además había quedado **stale** (la fila `wf-project-init` decía `--profile`/`--type`/`context: fork`
y le faltaban `CU-1.n/o/p` y `CU-3.r`). Al ejecutar los CU a mano no había forma, abriendo un CU, de
ver **qué componente valida cada escenario** ni de marcar el progreso. Además se descubrió que **CU-1
no prueba solo `wf-project-init`**: es híbrido (10 escenarios de la skill + 6 del hook de sesión).

**Decisión.** Cada `cu-NN.md` lleva una cabecera **`## 🧪 Qué se prueba aquí (por componente)`**
(tras el bloque intro, antes del primer escenario): la **transpuesta forward** (CU → componentes),
con los escenarios agrupados por su componente primario (`wf-*` skill / agente / script / hook /
orquestador, leído de la línea `Mecanismo:` de cada escenario) y un **checklist `- [ ]` por escenario**
para marcar al ejecutar. El **ROADMAP sigue siendo la SSoT backward** del estado de cobertura (ejes
happy/edge/harness/args + Estado); la cabecera del CU **apunta a él** y no duplica el veredicto por
ejes. Convención de marcado (estado de PASS = humano): `- [x] … · ✓ <fecha>` para PASS acordado;
`- [ ] … · ⚠️ FALLO → #issue` para divergencia. Se refrescó la fila stale de `wf-project-init` y se
añadió `CU-3.r` a las filas de spec.

**Alternativas descartadas.**
- *Solo dashboard central en ROADMAP* → descartada: no resuelve el forward al abrir un CU.
- *Reordenar físicamente los escenarios por skill* → descartada: los IDs `CU-N.x` son citables y
  estables; el orden "que tiene sentido" se da en la vista agrupada de la cabecera, no moviendo el cuerpo.
- *Generar la cabecera con script desde el principio* → diferida: las líneas `Mecanismo:` son prosa,
  parsearlas fiable exige estandarizar antes un mini-formato. Se hizo **a mano** el rollout (piloto en
  CU-1, luego los 16 restantes vía subagentes en paralelo).

**Consecuencias / aprendizaje.** Tres representaciones del mismo dato (líneas `Mecanismo:`, columna
del ROADMAP, cabecera del CU) = riesgo de drift — ya mordió con el ROADMAP stale. **Follow-up
pendiente:** extender `scripts/sdd-conformance-coverage.py` para (a) **generar** la cabecera desde las
`Mecanismo:` y (b) un modo **`--check`** que falle si las tres divergen; el generador debe
**preservar** las marcas de PASS (`[x]`/`✓ fecha`/`⚠️ FALLO`) — merge, no clobber, porque el estado
PASS es humano (ejecución manual), no derivable. Verificado en el rollout: los 17 CU tienen la
cabecera con el SET de IDs idéntico al del cuerpo (sin faltantes ni duplicados) y el agregador
determinista sigue parseando el ROADMAP (48/48, exit 0).

**Referencias.** `conformance/casos-de-uso/cu-01-inicializar.md` (piloto) + los 16 restantes ·
`conformance/ROADMAP.md` (fila `wf-project-init` refrescada; `CU-3.r` añadido) · `conformance/README.md`
(formato del CU) · `scripts/sdd-conformance-coverage.py` (follow-up de generación/`--check`).

---

## D-007 — Endurecimiento del bootstrap descubierto al ejecutar el init topología-first E2E

- **Fecha:** 2026-06-17 · **Estado:** Adoptada

**Contexto.** Al correr `/wf-project-init` varias veces sobre un repo greenfield real afloraron asperezas de bootstrap que el test del detector no captura. Primera tanda: (1) `wf-project-init` Paso 2 trataba `~/.sdd-home` como un directorio, cuando `setup.sh` lo escribe como **fichero-puntero** con la ruta dentro → `install.sh: MISSING` en el primer intento y recuperación a mano en **cada** ejecución; (2) `install.sh` copia el `CLAUDE.md` del ecosistema (191 líneas) siempre que hay ≥2 fases, y `wf-sdd-update` reejecuta `install.sh` → en cada update **pisaría** el `CLAUDE.md` lean del proyecto con el genérico (bug latente, solo visible al ejercitar el ciclo init→update); (3) el mensaje final "Reinicia Claude Code" era impreciso — los skills/agents del proyecto ya aparecían vía `/skills` y `/agents` sin reiniciar. Segunda tanda (run posterior): (4) **fricción de escritura recurrente** — `install.sh` sembraba `CLAUDE.md` y el Paso 7 lo sobreescribía con `Write` → choque con la regla del harness "leer antes de sobreescribir" (`Error writing file`); y el Paso 8 creaba `project-init.json` por Bash y luego lo corregía con `Update` (escribía `sdd_version: unknown` y lo parcheaba) → `File must be read first`. Ambos se recuperaban solos, pero ensuciaban cada init. (5) el `CLAUDE.md`/mensaje seguían pidiendo "reiniciar" cuando lo idiomático es `/clear`. (6) la opción Q1 "Producto (specs + diseño)" sobrevende: PRD y diseño son **opcionales** y se preguntan a continuación.

**Decisión.** (1) Paso 2 resuelve `~/.sdd-home` **leyendo su contenido** (es puntero, no directorio), igual que ya hacía `wf-sdd-update`. (2) `install.sh` siembra `CLAUDE.md` **solo si no existe**; contrato: **`install.sh` nunca pisa un `CLAUDE.md` ya presente** — así un `wf-sdd-update` no degrada el específico al genérico. (4) Para eliminar la fricción de escritura: `install.sh` acepta **`--no-claude-md`** y `wf-project-init` lo pasa siempre → en una instalación nueva el `CLAUDE.md` **no existe** y el `Write` del Paso 7 lo crea limpio (en reinit, el Paso 7 hace `Read` antes del `Write`); y el Paso 8 **resuelve `sdd_version` ANTES** y escribe `project-init.json` en **una sola** operación (sin placeholder + `Update`). (3+5) Mensaje final → "Ejecuta `/skills` y `/agents` para revisar que Claude ha cargado correctamente el ecosistema. Si quieres empezar con contexto limpio, ejecuta `/clear`." (6) Q1 → "Producto (specs + PRD/diseño opcionales)" con la opcionalidad explícita en la descripción.

**Consecuencias / aprendizaje.** El clobber de `CLAUDE.md` en update y la fricción de escritura eran invisibles para los tests automáticos: solo se ven **ejecutando el init/update a mano**. La causa raíz de (4) es estructural — el harness exige `Read` antes de sobreescribir/editar; la cura no es "leer y reintentar" sino **no crear el conflicto**: o el fichero no existe cuando el skill lo escribe (`--no-claude-md`), o se computa todo antes de un único write (sin `Update` correctivo). Confirma que las pruebas E2E manuales del init/update son la red que atrapa la regresión de bootstrap, complementaria al `test_sdd_init_detect.py`. (7) Aprendizaje adicional de la tercera pasada: el aviso final de `install.sh` **no llega al usuario** porque su stdout queda colapsado en el output del Paso 6. Se resuelve con un **Paso 11 dedicado** que emite el recordatorio (`/skills`+`/agents`+`/clear`) con un `echo` **determinista** — no prosa del modelo (coherente con [[D-004]]: garantiza texto exacto y presencia siempre, y un `echo` corto en su propia llamada no se colapsa). (8) Cuarta pasada (dos repos en paralelo): las instalaciones salieron **byte-idénticas** (project-init.json, CLAUDE.md, 3 rules, 6 agents, 48 skills, 12 scripts; modulo nombre+timestamp), pero en uno el agente invocó `verify --phases prd spec design` (espacios) → argparse abortó (`unrecognized arguments`) y reintentó. Causa: el placeholder `<SELECTED_PHASES>` del Paso 9 no decía "separadas por coma". Fix: el ejemplo del Paso 9 usa `--phases <fase1,fase2,...>` con nota explícita anti-espacios. Aprendizaje: los placeholders en los comandos del skill deben mostrar el **formato literal** (coma vs espacio), no un nombre abstracto, o el modelo elige formato y a veces falla.

**Referencias.** `bootstrap/skills/wf-project-init/SKILL.md` (Paso 2 · Paso 6 `--no-claude-md` · Paso 7 read-if-exists · Paso 8 `sdd_version` inline · Q1 5.0) · `install.sh` (flag `--no-claude-md`, siembra de `CLAUDE.md`, mensaje final) · `bootstrap/skills/wf-sdd-update/SKILL.md` (Paso 4).

---

## D-006 — El rigor del pipeline (standard/ligero) se elige por feature al crear el spec, no en el init

- **Fecha:** 2026-06-17 · **Estado:** Adoptada · **Refina:** [[D-001]] (el eje "rigor" deja de ser un *recorded-only* del init) · **Se apoya en:** [[D-002]] (la oferta interactiva vive en el hilo principal, no en el fork)

**Contexto.** El init preguntaba el "rigor del pipeline" (standard/ligero) y lo persistía como `pipeline_mode`. En pruebas E2E del init topología-first se vio que esa pregunta se hacía en **t=0, sin features delante** (un PM en authoring no puede decidirla informado), e incluso en topología `consumer` —que no instala la fase `spec`, así que su `pipeline_mode` es inerte—. Riesgo de fondo señalado por el usuario: un default `light` a nivel proyecto **normaliza specs finos por inercia**, convirtiendo un modo proporcional legítimo en un atajo a specs incompletas.

**Decisión.** El init **no pregunta** el rigor; `pipeline_mode` arranca en `standard`. La elección standard/ligero se ofrece **por feature al crear el spec**, donde la información existe. Como las workflows de creación (`wf-spec-fast-track`, `wf-spec-features-first`) son `context: fork` y no pueden usar `AskUserQuestion` ([[D-002]]), **el orquestador de la fase Spec ofrece la elección en el hilo principal antes de delegar**: respeta un flag explícito; respeta `pipeline_mode: light` si el equipo lo fijó a mano; si no, pregunta (default `standard`); en `features-first` pregunta **una sola vez por lote**. `pipeline_mode` se conserva como override de proyecto **editable a mano**.

**Alternativas descartadas.**
- *Mantener la pregunta en el init pero solo si hay `spec` (authoring/standalone)* → descartada: arregla el ruido en consumer pero no el problema de fondo (decisión a ciegas en t=0 y normalización de `light`).
- *Preguntar dentro de `wf-spec-fast-track`* → imposible: es `context: fork` ([[D-002]]); la interacción vive en el hilo principal.
- *Eliminar `pipeline_mode` del todo* → descartada: el escape "proyecto ligero-por-defecto" es legítimo; se conserva como campo editable, solo deja de normalizarse vía wizard.

**Consecuencias / aprendizaje.** El modo ligero queda como **opt-in deliberado**, no atajo: su blindaje contra specs incompletas es estructural (invariantes idénticos a standard, secciones omitidas marcadas `N/A — modo ligero` explícito, marcadores `[INCOMPLETO]`/`[CRÍTICO]` que bloquean igual). Cambia el **modelo de cobertura de CU-1** (el eje "rigor" sale del init) y exige que los CU de la fase Spec ejerciten la **oferta de modo al crear el spec**. La oferta vive en `pipeline/spec/CLAUDE.md`, que `install.sh` instala como `rules/sdd-spec.md` (carga perezosa) → llega a los proyectos sin tocar las workflows-fork.

**Referencias.** `bootstrap/skills/wf-project-init/SKILL.md` (Paso 5 / 5.8 / 7 / 8) · `pipeline/spec/CLAUDE.md` ("Elección del rigor del pipeline") · `pipeline/spec/skills/wf-spec-fast-track/SKILL.md` (Paso 1, resolución de modo) · `kb-spec-expert` ("Modo ligero") · `conformance/casos-de-uso/cu-01-inicializar.md` + `cu-03-specs.md`.

---

## D-005 — El eje primario del init es la TOPOLOGÍA de contenido del repo, no el perfil de quien inicializa

- **Fecha:** 2026-06-17 · **Estado:** Adoptada · **Supersede:** [[D-003]] (backbone-siempre) y el modelo de perfiles (`profiles`)

**Contexto.** El init preguntaba primero un **perfil** (`dev`/`product`/`design`/`minimal`) y, solo para dev, una topología (standalone/consumer). Al modelar un producto multi-superficie real (app móvil + desktop + web sobre los **mismos specs**) afloraron tres defectos: (1) `type` (app/web/backend) era una pregunta **técnica disfrazada de pregunta de proyecto** — para un PM que autora specs agnósticos es incorrecta (el spec no tiene superficie) y operativamente inerte; (2) el verdadero eje que determina qué se instala no es el rol sino **qué contiene el repo** (¿autora specs o los consume?, ¿lleva código?, ¿dónde vive el diseño?); (3) el diseño tiene dos capas —sistema (`DESIGN.md`, compartido entre superficies) y feature (`flows`/`views`/`ui_prompt`, divergentes por superficie)— que el modelo de fase única no separaba.

**Decisión.** La primera pregunta del init es la **topología de contenido**: `authoring` (PRD/specs/sistema de diseño, sin código), `consumer` (código de una superficie que consume specs de un SSoT) o `standalone` (todo junto). El backbone instalado **depende de la topología** (authoring sin plan/tasks; consumer sin spec/prd; standalone completo). `type` se sustituye por `surfaces` (mobile/desktop/web/backend/other), que solo se pregunta en ramas con código y alimenta a la vez el stack y el `target_platforms` del diseño. El consumer se parte en *con-UI* (instala diseño de feature) y *headless*. La fase `design` se reparte en dos agentes (`design-system-architect` / `design-feature-architect`) según `design_role`. El esquema de `project-init.json` rompe compatibilidad: `topology`/`surfaces`/`has_ui`/`design_role` sustituyen a `profiles`/`type` (sin migración; reinit).

**Alternativas descartadas.**
- *Parchear solo `type`→agnóstico para product/minimal, manteniendo perfiles* → descartada: trata el síntoma, no la causa; el eje seguiría siendo el rol, que es una aproximación torpe a la topología.
- *Repo solo-diseño como cuarta topología* → descartada: el caso multi-superficie no lo necesita (el `DESIGN.md` compartido se pliega en authoring y los flows/views por superficie viven en cada repo consumer). Queda como opción organizativa, no estructural.
- *Partir `design` en dos juegos de skills instalables aislados* → descartada: feature-prototype necesita el contrato del sistema en contexto. El split correcto es de **agente** (dos agentes, el de feature carga el contrato como referencia de solo-lectura), no de skills mutuamente excluyentes.

**Consecuencias / aprendizaje.** El "backbone-siempre" de [[D-003]] queda como caso particular (standalone); la regla general es "backbone según topología", espejo simétrico de la excepción consumer que D-003 ya contemplaba. "Mínimo" deja de ser un perfil: es la configuración de standalone con PRD=no/diseño=no/stack agnóstico. **Deuda anotada:** standalone multi-superficie con stacks distintos (app+backend) instala hoy un solo overlay de stack — se elige superficie primaria y el resto se completa con "Completar / ampliar".

**Referencias.** `bootstrap/skills/wf-project-init/SKILL.md` (Regla 4, Paso 5 árbol de llamadas, Paso 6/8) · `sdd/scripts/sdd-init-detect.py` (check `topology`) · `sdd/tests/test_sdd_init_detect.py` · `pipeline/design/agents/design-system-architect.md` + `design-feature-architect.md` · `pipeline/design/skills/kb-design-feature-artifacts` (ui_prompt por superficie) · `conformance/casos-de-uso/cu-01-inicializar.md`.

---

## D-004 — La lógica determinista del init vive en un script, no en bash inline

- **Fecha:** 2026-06-16 · **Estado:** Adoptada · **Versión:** 0.33.0

**Contexto.** `wf-project-init` recitaba en bash inline su lógica determinista (find-up del raíz en monorepos, detección de estado previo, carpetas candidatas, detección de stack, verificación post-install). El modelo la retecleaba cada init: no testeable y propensa a variación. Va contra el principio del ecosistema ("recolección determinista, no agente") y contra la migración prosa→script ya hecha (inventario 11.2).

**Decisión.** Extraer esa lógica a `sdd/scripts/sdd-init-detect.py` (subcomandos `detect` pre-install y `verify --phases` post-install). Es herramienta de **ecosistema**, no de proyecto: NO se distribuye a `.sdd/scripts/`; se invoca vía `$SDD_HOME/scripts/…` — disponible pre-install igual que `$SDD_HOME/install.sh` (mismo modelo que `sdd-structural-lint.py`/`sdd-scaffold.py`). La **entrevista** (`AskUserQuestion`) se queda en el skill: es interactiva, no scriptable. El bash inline se conserva como **fallback explícito** sin python3 (mismo patrón que el cableado de `sdd-resolve-path.py`).

**Alternativas descartadas.**
- *Bundlear el script en `${CLAUDE_SKILL_DIR}/scripts/`* → descartada: estrenaría un patrón sin precedente (ningún skill bundlea scripts hoy) cuando `$SDD_HOME/scripts/` ya es el hogar canónico y está disponible pre-install.
- *Scriptar también la escritura de `project-init.json` (Paso 8)* → fuera de alcance por ahora; el esquema es simple y `verify` lo comprueba.

**Consecuencias / aprendizaje.**
- **Aprendizaje:** lo interactivo no se puede testear headless (`AskUserQuestion` no existe sin hilo principal). Por eso la frontera correcta es *script determinista (testeable) + capa de entrevista delgada (manual)*. Cuanto más se mete en el script, más cae bajo test; el `CU-1.p` (args) queda como prueba manual mínima.
- `verify` arregla de paso un falso negativo latente: el check viejo `grep -q '"artifacts"'` fallaba en topología consumer (que usa `artifacts_source`), reportando FALLO en un init correcto. Ahora acepta ambos.
- Cubierto por `test_sdd_init_detect.py` (17 tests).

**Referencias.** `sdd/scripts/sdd-init-detect.py` · `sdd/tests/test_sdd_init_detect.py` · `bootstrap/skills/wf-project-init/SKILL.md` (Pasos 3/4/9) · `CHANGELOG.md` 0.33.0 · [[D-002]] (mismo principio: lo interactivo en el hilo principal).

---

## D-003 — El backbone `spec`/`plan`/`tasks` siempre se instala (standalone): SDD es un flujo agnóstico a la tecnología

- **Fecha:** 2026-06-16 · **Estado:** Superada por [[D-005]] (el backbone pasa a depender de la topología; el principio agnóstico se conserva en standalone)

**Contexto.** Al analizar `wf-project-init` surgió si el "backbone fijo" (spec/plan/tasks siempre) era correcto en todos los casos. La Regla 4 decía "SIEMPRE" pero la topología consumer instala solo `plan`+`tasks`.

**Decisión.** El backbone-siempre es **deliberado** en topología *standalone* (lo normal, incluida la inicialización de proyectos sin stack especializado, p. ej. C++): SDD se usa como **flujo de trabajo agnóstico a la tecnología** — aun sin skills de stack, se define spec → se genera plan → se generan tasks; nunca se implementa "a pelo". La **única excepción** es la topología *consumer* (repo técnico de un producto multi-repo cuyos specs viven en un repo SSoT): instala solo `plan`+`tasks`, porque la autoría de specs no ocurre ahí. La Regla 4 se reescribe para reflejar esa única excepción; no se cuestiona el backbone en standalone.

**Consecuencias / aprendizaje.** El perfil `custom` prometía "decidir fase a fase qué se instala", pero el backbone no es negociable → etiqueta templada (custom decide `prd`/`design`, no el backbone). El valor de SDD como contrato de proceso (no como tooling de un stack) queda explícito: instalar plan/tasks aunque no haya owner-agent de stack es la feature, no un desperdicio.

**Referencias.** `bootstrap/skills/wf-project-init/SKILL.md` (Regla 4, Paso 5.0b consumer, Paso 5.0 custom) · `conformance/casos-de-uso/cu-01-inicializar.md` (CU-1.i consumer).

---

## D-002 — `context: fork` es incompatible con `AskUserQuestion`

- **Fecha:** 2026-06-16 · **Estado:** Adoptada · **Versión:** 0.33.0

**Contexto.** Durante las pruebas manuales de CU-1, la entrevista de `wf-project-init` salía con orden y descripciones distintos entre ejecuciones, pese a que el SKILL.md exige opciones y secuencia exactas. La causa: el skill llevaba `context: fork` y la entrevista usaba `AskUserQuestion`. La documentación oficial de Claude Code es explícita: `AskUserQuestion` (y otras tools dependientes de la UI del hilo principal) **no está disponible en subagentes ni forks**, falla aunque esté en `allowed-tools`. El fork no podía preguntar, así que el orquestador del hilo principal improvisaba la interacción de memoria. Afectaba a **8 workflows** que compartían el patrón.

**Decisión.** Una `wf-*` que use `AskUserQuestion` **no puede llevar `context: fork`**: corre en el hilo principal. La delegación de trabajo pesado a un agente es **ortogonal al fork** — se hace vía la tool `Agent`, que aísla el contexto igual de bien. El campo `agent:` (destino de inyección del fork) desaparece junto con el fork; el cuerpo nombra al agente y lo invoca por `Agent`.

**Alternativas descartadas.**
- *"El harness debería dejar preguntar al fork"* → descartada: es comportamiento documentado e intencional de la plataforma, no un bug del harness.
- *Round-trip (mantener el fork; que devuelva "necesito decisión" y el hilo principal pregunte y reinvoque)* → descartada: más compleja y frágil, sin ganancia de contexto (el `Agent` ya aísla el trabajo pesado).

**Consecuencias / aprendizaje.**
- 7 skills eran patrón orquestador (delegación limpia) → quitar el fork fue trivial. `wf-prd-review` era "fork-como-agente" (su cuerpo corría *como* `prd-expert` para tener `kb-prd-expert` en contexto) → hubo que reestructurarlo a delegación explícita.
- El bug se **autogeneraba**: el scaffold (`sdd-scaffold.py`) hardcodeaba `context: fork` en todo `wf-*`, y la guía (`kb-sdd-creation-guide`) lo declaraba obligatorio. Arreglar solo los 8 skills no habría bastado: hay que arreglar también las fuentes que reproducen el patrón.
- **Aprendizaje transversal:** la interacción con el usuario vive SIEMPRE en el hilo principal; los subagentes/forks son para trabajo no interactivo. Cualquier patrón nuevo que mezcle ambos es sospechoso.
- Guardarraíl permanente: regla blocking `FORK-ASKUSER-CONFLICT` en el linter — la clase de bug ya no puede regresar en verde.

**Referencias.** `CHANGELOG.md` 0.33.0 · linter `FORK-ASKUSER-CONFLICT` · `kb-sdd-creation-guide` (frontmatter `wf-*`) · incidencia GitHub `[CU-1.b]`.

---

## D-001 — Cobertura de CU-1 por ramas de decisión, no por producto cartesiano

- **Fecha:** 2026-06-16 · **Estado:** Adoptada

**Contexto.** Al probar el wizard de init manualmente, la combinatoria de ejes (perfil × PRD × tipo × rigor …) parecía inabarcable y sin cubrir en los casos de uso. Pero no todos los ejes cambian lo que se instala: en perfil producto, `tipo` y `rigor` no alteran el set de fases — solo se persisten en `project-init.json`.

**Decisión.** CU-1 prueba **ramas de decisión**, no combinaciones de valores. Un eje merece un caso por rama solo si cambia el set instalado o el flujo de preguntas (*behavior-changing*); los ejes que solo se registran (*recorded-only*) se cubren con un único caso parametrizado. `cu-01-inicializar.md` lleva una tabla "Modelo de cobertura" que clasifica cada eje y marca su cobertura honesta (`✓` / `parcial` / `—`).

**Consecuencias / aprendizaje.** Disuelve la explosión combinatoria (`producto/prd/app/standard` y `producto/prd/web/ligero` instalan lo mismo → no son casos distintos). La tabla hace **visibles los gaps reales** en lugar de esconderlos en una falsa sensación de cobertura total. Casos nuevos: `CU-1.n` (ejes recorded-only) y `CU-1.o` (ramas behavior-changing de tipo/framework/custom).

**Referencias.** `conformance/casos-de-uso/cu-01-inicializar.md` (Modelo de cobertura, CU-1.n, CU-1.o).
