# CU-13 — Matriz de enrutado (disparador → skill)

**Objetivo:** verificar que cuando dices algo en lenguaje natural, el orquestador
**invoca el workflow correcto** (y no uno confundible). Donde CU-11 prueba el
*mecanismo* del enrutado, CU-13 es la **matriz exhaustiva**: una frase representativa
por cada uno de los 50 workflows + los pares de desambiguación.
**Proyecto a usar:** cualquier proyecto real con SDD instalado (transversal). No hace
falta dejar correr el workflow hasta el final: basta observar **qué skill anuncia/invoca
el orquestador** antes de ejecutarlo.
**Cobertura automática:** ninguna — el acierto del routing es decisión del LLM. La SSoT
de disparadores efectiva son las **`description`** de cada `SKILL.md` (cargan *eager* y
hacen el enrutado intención→skill, [[D-022]]) y, para lo que la `description` no expresa,
la desambiguación *eager* de `sdd-routing.md`; el rootmap intención→skill de `CLAUDE.md`
es **referencia** (podría lint-earse contra drift; el acierto en sí es **manual**).

> [!NOTE]
> **Cada fila valida de paso el mecanismo de [[D-022]] en su fase.** La hipótesis de D-022
> es que las `description` (eager) + la desambiguación de `sdd-routing.md` (eager) bastan
> para enrutar bien **sin** el rootmap-tabla lazy. Como estas filas se validan **en orden
> de fase** durante la campaña de conformance (`CU-13.a` PRD primero, luego `.b` Spec, …),
> un PASS de `CU-13.x` confirma además que el enrutado de esa fase aguanta con el carril
> eager. Cuando todas las fases con `routing.md` pasen, se habilita **borrar el rootmap
> plano** de las reglas lazy (el único paso irreversible de D-022, hoy gated). El
> *mecanismo* transversal (hablar, no teclear; narración sin surfacear `wf-*`) es `CU-11.a`.

> [!IMPORTANT]
> **Cómo se prueba cada fila.** Dices la frase de la columna **Dices** (en lenguaje
> natural, **sin teclear `/wf-*`**) → observas qué skill propone el orquestador → **PASS**
> si coincide con **Debe disparar** y **no** cae en el **No confundir con**. Cada fila es
> citable como su `CU-13.x` (p. ej. *CU-13.b, fila "crea las specs"*).

> [!NOTE]
> **Las `kb-*` no entran aquí.** No se disparan por frases: se cargan *eager* en el
> subagente vía su frontmatter `skills:`. "Que cargue la kb correcta" = "que corra el
> agente correcto" (lo verifica `sdd-kb-check.py` + el bloque **Mecanismo** de cada CU).

---

## 🧪 Qué se prueba aquí (por componente)

CU-13 es un **objetivo de usuario** (que cada frase enrute al workflow correcto), no una
sola skill: sus escenarios ejercitan el **enrutado del orquestador** (la matriz exhaustiva
frase→skill), separado en el orquestador del pipeline y el meta-orquestador del ecosistema.
Marca cada escenario al ejecutarlo. El estado de cobertura autoritativo (ejes
happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) — esta vista es la
**transpuesta** para leer/ejecutar el CU.

### Orquestador — matriz frase→skill (rootmap de `CLAUDE.md` + `when_to_use`) (7)
- [ ] CU-13.a — Fase PRD
- [ ] CU-13.b — Fase Spec
- [ ] CU-13.c — Fase Design
- [ ] CU-13.d — Plan, Tasks y entrega
- [ ] CU-13.e — Arranque e instalación
- [ ] CU-13.f — Overlay de stack KMM
- [ ] CU-13.g — Desambiguaciones críticas (las trampas reales)

### Meta-orquestador — autoría y mantenimiento del ecosistema (rootmap de `sdd/meta/CLAUDE.md`) (1)
- [ ] CU-13.h — Autoría y mantenimiento del ecosistema (meta)

---

## CU-13.a — Fase PRD

**Mecanismo:** orquestador enrutando por las **`description`** de los skills (eager) + la desambiguación *eager* de `sdd-routing.md` (frontera create → review, crear vs revisar; [[D-022]]); el rootmap de `sdd-prd.md` es referencia.

| Dices | Debe disparar | No confundir con |
|---|---|---|
| "convierte estas notas en un PRD" / "genera un PRD" | `wf-prd-create` | — |
| "revisa mi PRD" / "haz preflight del PRD" | `wf-prd-review` | crear (`wf-prd-create`) |
| "cambia el alcance del PRD" / "gestiona este cambio de producto" | `wf-prd-change` | propagar (`wf-prd-change-cascade`) |
| "propaga este cambio de PRD por todo el pipeline" | `wf-prd-change-cascade` | cambio aislado (`wf-prd-change`) · medir sin aplicar (`wf-prd-sync-impact`) · solo specs (`wf-spec-sync-from-prd`) |

**Resultado:** PASS si cada frase enruta a su skill y respeta los negativos · FALLO si
confunde change con cascade, o crea con revisa.
**Desviación → reportar:** issue citando `CU-13.a`.

## CU-13.b — Fase Spec

**Mecanismo:** orquestador + `when_to_use`.

| Dices | Debe disparar | No confundir con |
|---|---|---|
| "analiza este PRD para empezar los specs" | `wf-spec-analyze` | — |
| "crea las specs" / "genera las specs del PRD" | `wf-spec-features-first` | **`wf-spec-discover`** (ver CU-13.g) |
| "identifica las features del PRD" / "mapa de features" | `wf-spec-discover` | generar las specs (`wf-spec-features-first`) |
| "genera el spec directo de esta feature" | `wf-spec-fast-track` | — |
| "valida el spec" | `wf-spec-validate` | validar plan/DESIGN (`wf-plan-validate`/`wf-design-validate`) |
| "hay conflictos entre features" | `wf-spec-conflict` | — |
| "qué features están listas" / "orden de implementación" | `wf-spec-readiness` | estado de delivery (`wf-project-status`) |
| "completa los incompletos desde el analysis" | `wf-spec-gap-resolve` | añadir funcionalidad (`wf-spec-delta`) · aclarar CA (`wf-spec-amend`) |
| "añade funcionalidad al spec" / "requisitos nuevos" | `wf-spec-delta` | completar `[INCOMPLETO]` (`wf-spec-gap-resolve`) |
| "sincroniza los specs con el PRD" | `wf-spec-sync-from-prd` | medir impacto (`wf-prd-sync-impact`) |
| "qué specs han quedado stale tras cambiar el PRD" | `wf-prd-sync-impact` | aplicar (`wf-spec-sync-from-prd`) · todo el cascade (`wf-prd-change-cascade`) |
| "genera specs del código existente" / "caracteriza este módulo" | `wf-spec-from-code` | si hay PRD (`wf-spec-features-first`) |
| "este CA es ambiguo, aclara CA-XXX" | `wf-spec-amend` | cambia comportamiento (`wf-spec-delta`) · bug (`wf-bug`) · `[INCOMPLETO]` (`wf-spec-gap-resolve`) |

**Resultado:** PASS si cada frase enruta a su skill y respeta los negativos · FALLO en
cualquier confusión (sobre todo "crea las specs" → discover).
**Desviación → reportar:** issue citando `CU-13.b`.

## CU-13.c — Fase Design

**Mecanismo:** orquestador enrutando por las **`description`** de los skills (eager) + la desambiguación *eager* de `sdd-routing.md` (precondición spec+brief, trampas intake/delta/branch/variant; [[D-022]]); el rootmap de `sdd-design.md` es referencia.

| Dices | Debe disparar | No confundir con |
|---|---|---|
| "cierra el brief de diseño" / "genera el DESIGN_BRIEF.md" | `wf-design-intake` | actualizar brief existente (`wf-design-delta`) |
| "captura inspiración / vibes antes del brief" | `wf-design-moodboard` | cerrar brief (`wf-design-intake`) · sistema (`wf-design-system`) |
| "busca apps de referencia" | `wf-design-discover` | crear DESIGN.md (`wf-design-system`) |
| "crea el DESIGN.md" / "genera el sistema visual" | `wf-design-system` | cambio incremental (`wf-design-delta`) |
| "actualiza el DESIGN.md con estos cambios" / "cambia el style_family" | `wf-design-delta` | **desde cero (`wf-design-system`)** (ver CU-13.g) |
| "genera las vistas/flows para Stitch" | `wf-design-feature-prototype` | — |
| "valida el DESIGN.md" | `wf-design-validate` | accesibilidad (`wf-design-a11y-audit`) |
| "valida la accesibilidad / contraste WCAG" | `wf-design-a11y-audit` | validación general (`wf-design-validate`) |
| "qué artefactos de diseño quedaron stale" | `wf-design-sync` | evolucionar (`wf-design-delta`) · auditar (`wf-design-validate`) |
| "exporta los tokens" / "tokens para iOS" | `wf-design-export` | — |
| "extrae el DESIGN.md de la UI existente" | `wf-design-extract` | desde cero (`wf-design-system`) · cambiar extraído (`wf-design-delta`) |
| "crea una rama del DESIGN para probar otra familia" | `wf-design-branch` | A/B de feature (`wf-design-variant`) |
| "haz un A/B del checkout" | `wf-design-variant` | rama del sistema (`wf-design-branch`) |
| "incorpora este feedback del cliente sobre el diseño" | `wf-design-feedback` | — |

**Resultado:** PASS si cada frase enruta a su skill y respeta los negativos · FALLO
sobre todo en "actualiza el DESIGN.md" (system vs delta) o validate vs a11y.
**Desviación → reportar:** issue citando `CU-13.c`.

## CU-13.d — Plan, Tasks y entrega

**Mecanismo:** orquestador enrutando por las **`description`** de los skills (eager) + la desambiguación *eager* de `sdd-routing.md` (Plan: gate BORRADOR → VALIDADO; Tasks/entrega: precondición plan VALIDADO y las 3 vías task-run/bug/amend; [[D-022]]); los rootmaps de `sdd-plan.md`/`sdd-tasks.md` son referencia.

| Dices | Debe disparar | No confundir con |
|---|---|---|
| "genera el plan desde el spec" | `wf-prepare-plan` | analizar spec (`wf-spec-analyze`) · validar (`wf-plan-validate`) · tasks (`wf-prepare-tasks`) |
| "valida el plan" | `wf-plan-validate` | generar plan/tasks |
| "genera las tasks del plan" / "trocea el plan" | `wf-prepare-tasks` | generar/validar plan |
| "ejecuta las tasks" / "implementa la siguiente" | `wf-task-run` | generar tasks (`wf-prepare-tasks`) · bug (`wf-bug`) |
| "genera el plan de QA" / "deriva los casos de prueba" | `wf-qa-plan` | escribir tests · verificar (`wf-qa-verify`) |
| "verifica la cobertura" / "pasa QA la feature" | `wf-qa-verify` | derivar TCs (`wf-qa-plan`) · bug (`wf-bug`) |
| "releasa esta feature" / "registra el SHA" | `wf-release` | ejecutar tasks (`wf-task-run`) · QA (`wf-qa-verify`) · estado (`wf-project-status`) |
| "hay un bug" / "la app crashea cuando…" | `wf-bug` | cambia comportamiento (`wf-spec-delta`) · implementar (`wf-task-run`) |
| "cómo va el proyecto" / "qué está bloqueado" | `wf-project-status` | inventario del ecosistema (`wf-sdd-status`) · readiness funcional (`wf-spec-readiness`) |

**Resultado:** PASS si cada frase enruta a su skill y respeta los negativos · FALLO si
confunde la cadena plan→validate→tasks→run o bug con task-run.
**Desviación → reportar:** issue citando `CU-13.d`.

## CU-13.e — Arranque e instalación

**Mecanismo:** orquestador + `when_to_use` (+ protocolo de sesión para el init).

| Dices | Debe disparar | No confundir con |
|---|---|---|
| "inicializa el proyecto" / "prepara este repo para SDD" | `wf-project-init` | crear skills/agentes (`wf-skill-create`/`wf-agent-create`) · init de stack ya conocido (`wf-<stack>-init`) |
| "actualiza el sdd del proyecto" / "sdd update" | `wf-sdd-update` | inicializar nuevo (`wf-project-init`) · ampliar fases (`wf-project-init` → Completar/ampliar) |

**Resultado:** PASS si distingue init de update y no confunde con autoría de ecosistema
· FALLO si lanza `wf-project-init` para un update, o al revés.
**Desviación → reportar:** issue citando `CU-13.e`.

## CU-13.f — Overlay de stack KMM

**Mecanismo:** orquestador + `when_to_use` (aplica solo en proyectos `stack: kmm`).

| Dices | Debe disparar | No confundir con |
|---|---|---|
| "init de KMM" / "detecta el estado KMM" | `wf-kmm-init` | init genérico (`wf-project-init`) · piezas concretas (auth/network/stack) |
| "configura el stack completo KMM" | `wf-kmm-stack-setup-ktor-keycloak-koin` | piezas sueltas (network/auth/datastore) |
| "configura networking en KMM" / "setup de Ktor" | `wf-kmm-network-setup` | si también auth (`wf-kmm-auth-setup-keycloak`) · stack completo |
| "configura auth con Keycloak" | `wf-kmm-auth-setup-keycloak` | stack completo · networking sin auth |
| "configura Room" / "DB local en KMM" | `wf-kmm-database-setup` | clave-valor (`wf-kmm-datastore-setup`) · networking |
| "configura DataStore" / "Preferences" | `wf-kmm-datastore-setup` | networking · stack completo |
| "configura pre y pro" / "multi-brand" | `wf-kmm-environments` | stack completo · solo networking |
| "configura testing en el proyecto KMM" | `wf-kmm-testing-setup` | — |

**Resultado:** PASS si distingue "stack completo" de las piezas sueltas y Room de
DataStore · FALLO si una pieza concreta dispara el stack completo, o al revés.
**Desviación → reportar:** issue citando `CU-13.f`.

## CU-13.h — Autoría y mantenimiento del ecosistema (meta)

**Mecanismo:** meta-orquestador (rootmap de `sdd/meta/CLAUDE.md`) + `when_to_use`.

| Dices | Debe disparar | No confundir con |
|---|---|---|
| "crea una kb de X" / "necesito un workflow para Y" | `wf-skill-create` | crear agente (`wf-agent-create`) · crear las skills del pipeline (wf-* de fase) |
| "crea un agente para X" / "necesito un agente que" | `wf-agent-create` | crear skill (`wf-skill-create`) |
| "crea el overlay de android" / "soporta el stack X" | `wf-stack-create` | skill suelta (`wf-skill-create`) · init de stack ya soportado (`wf-project-init`) |
| "audita el ecosistema" / "busca contradicciones/SSoT" | `wf-sdd-audit` | validar spec/plan/DESIGN (`wf-spec/plan/design-validate`) |
| "refactoriza esta skill" / "esta kb es muy ancha" | `wf-sdd-refactor` | crear piezas nuevas (`wf-skill-create`/`wf-agent-create`) |
| "qué skills tenemos" / "inventario del ecosistema" | `wf-sdd-status` | estado de delivery (`wf-project-status`) · readiness de specs (`wf-spec-readiness`) |

**Resultado:** PASS si cada frase enruta a su skill meta y respeta los negativos (sobre todo audit vs
validate de artefactos, y sdd-status vs project-status) · FALLO si confunde crear con refactorizar, o auditar el ecosistema con validar un artefacto del pipeline.
**Desviación → reportar:** issue citando `CU-13.h`.

---

## CU-13.g — Desambiguaciones críticas (las trampas reales)

**Mecanismo:** orquestador + rootmap de `CLAUDE.md` (que tiene reglas explícitas para
varias de estas).

Las confusiones de mayor riesgo, donde más de un skill comparte vocabulario. Cada una
es **citable como `CU-13.g`** y conviene probarla aparte:

1. **"crea / genera las specs (del PRD)"** → `wf-spec-features-first`, **NO**
   `wf-spec-discover` — aunque el `when_to_use` de discover liste "features-first" y
   "mapa de features". Discover solo cuando pides **explícitamente** un subset / "fase 1"
   / "estas N features" / el mapa de features. *(Regla explícita en `CLAUDE.md`.)*
2. **"actualiza el DESIGN.md"** → ambiguo a propósito: **desde cero / regenerar** =
   `wf-design-system`; **cambio incremental** ("con estos cambios", "cambia el
   style_family") = `wf-design-delta`. El orquestador debe inferir por el matiz o
   preguntar; no elegir a ciegas.
3. **"valida el …"** → por **tipo de artefacto**: spec → `wf-spec-validate`; plan →
   `wf-plan-validate`; DESIGN.md → `wf-design-validate`; accesibilidad →
   `wf-design-a11y-audit`.
4. **Familia "cambiar un spec"** → aclarar un CA ambiguo (mismo comportamiento) =
   `wf-spec-amend`; completar `[INCOMPLETO]` con respuestas del analysis =
   `wf-spec-gap-resolve`; añadir/cambiar funcionalidad = `wf-spec-delta`; defecto de
   código contra el CA = `wf-bug`; cambio que baja del PRD = `wf-spec-sync-from-prd`.
5. **"qué está listo / estado"** → delivery del proyecto = `wf-project-status`;
   readiness **funcional** de specs = `wf-spec-readiness`; inventario del **ecosistema**
   = `wf-sdd-status` (meta-skill).
6. **Origen de los specs** → desde **código** existente = `wf-spec-from-code`; desde un
   **PRD** = `wf-spec-features-first`.
7. **Diseño: desde cero vs UI existente** → greenfield (desde spec) = `wf-design-system`;
   UI **ya en producción** (ingeniería inversa) = `wf-design-extract`.

**Resultado:** PASS si el orquestador acierta cada desambiguación (y, en la #2, pide
aclaración si el matiz no es claro) · FALLO si cae en la confusión obvia — especialmente
"crea las specs" → discover, o "actualiza el DESIGN" → la opción equivocada sin preguntar.
**Desviación → reportar:** issue citando `CU-13.g`.
