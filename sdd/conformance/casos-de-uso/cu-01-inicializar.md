# CU-1 — Inicializar un proyecto SDD

**Objetivo:** verificar que, al abrir un proyecto, el sistema decide correctamente el
modo de trabajo (wizard SDD/libre), inicializa el ecosistema según la **topología de
contenido del repo** (authoring/consumer/standalone/design), repara instalaciones a medias,
avisa de versiones viejas sin bloquear, y encuentra los marcadores hacia arriba en un
monorepo.
**Proyecto a usar:** un repo/carpeta real **FUERA del repo del ecosistema** (p. ej.
`~/sdd-pruebas/mi-proyecto/`): uno **nuevo o virgen** para el wizard de modo, y aparte
uno ya en SDD que manipules para `init-pending`/`init-incomplete`/`version-drift`.
**Cobertura automática:** el hook está muy cubierto por `sdd/tests/test_session_hook.py`
y los installers por `test_install_sh.py` / `test_setup_sh.py`. Lo que prueban a mano
estos escenarios es la **conducta del agente** ante cada directiva (presentar el
wizard antes de nada, invocar el init, no autoaprobar el modo).

> [!CAUTION]
> **CU-1 no se puede probar dentro del repo del ecosistema.** El hook
> `bootstrap/sdd-session-check.sh` calcula el git toplevel del propio ecosistema (vía
> `~/.sdd-home`) y **se silencia** en cualquier sesión bajo él. Para ver el wizard,
> usa un **proyecto real en un directorio externo** y abre Claude Code ahí. Atajo para
> iterar sin wizard: `cd <proyecto> && bash <repo>/sdd/install.sh all`.

---

## 🧪 Qué se prueba aquí (por componente)

CU-1 es un **objetivo de usuario** (inicializar), no una sola skill: sus escenarios ejercitan **dos
componentes**. Marca cada escenario al ejecutarlo. El estado de cobertura autoritativo (ejes
happy/edge/harness/args) vive en [`ROADMAP.md`](../ROADMAP.md) — esta vista es la **transpuesta**
para leer/ejecutar el CU.

### `wf-project-init` — la skill de init (12)
- [x] CU-1.b — Modo SDD arranca el init · ✓ 2026-06-17 · 🔁 **RE-TEST pendiente tras D-011** (Q1 ganó la 4ª opción + esquema nuevo; re-ejecutar tras `bash setup.sh`)
- [ ] CU-1.h — La topología decide qué se instala
- [ ] CU-1.i — Topología consumer
- [ ] CU-1.j — Init desde subpaquete (gate de workflow)
- [ ] CU-1.k — Verificación bloqueante
- [ ] CU-1.l — Evolución authoring→standalone (extend)
- [ ] CU-1.m — Ubicación de artefactos no canónica
- [x] CU-1.n — El init NO pregunta el rigor ([[D-006]]) · ✓ 2026-06-17
- [ ] CU-1.o — Superficie/framework ramifican; caso Mínimo
- [ ] CU-1.p — Los argumentos honran y saltan preguntas
- [ ] CU-1.q — Topología design (repo de solo-diseño, [[D-011]])
- [x] CU-1.r — Aviso de SSoT sin git (advisory, topologías productoras) · ✓ 2026-06-20 (3 corridas: aviso advisory consistente en semántica; literal varía por ser informe NL, no es FALLO)

### hook de sesión `bootstrap/sdd-session-check.sh` — directivas `SDD-PROTOCOL` (6)
- [x] CU-1.a — Wizard de modo en proyecto virgen (`mode-undecided`) · ✓ 2026-06-17
- [x] CU-1.c — Modo libre silencia SDD (`free`) · ✓ 2026-06-17
- [x] CU-1.d — Modo SDD sin init → `init-pending` (invoca wf-project-init) · ✓ 2026-06-17
- [x] CU-1.e — Init a medias → `init-incomplete` (invoca wf-project-init "Completar/ampliar") · ✓ 2026-06-17 (criterio determinista: repair-plan, rol derivado de topología, sin preguntar)
- [x] CU-1.f — Versión anterior → `version-drift` (informativo) · ✓ 2026-06-18
- [x] CU-1.g — Sesión en subdirectorio → búsqueda de marcadores hacia arriba · ✓ 2026-06-18

> **Capa determinista** (no son escenarios manuales): `install.sh`, `sdd-init-detect.py` y el propio
> hook están cubiertos por unittests (`test_install_sh.py`, `test_setup_sh.py`,
> `test_session_hook.py`, `test_sdd_init_detect.py`). En particular, la lógica de reparación de
> CU-1.e — qué fases faltan y el `design_role` derivado de la topología — es la función pura
> `sdd-init-detect.py repair-plan`, cubierta por `RepairPlanTest`; lo manual de CU-1.e es solo que el
> agente **aplique** ese plan sin preguntar el rol. Aquí se prueba la **conducta del agente** ante
> cada directiva / entrevista.

> **Re-test tras [[D-011]] (2026-06-18).** El SKILL `wf-project-init` cambió de forma material: Q1 ganó la
> 4ª opción **Diseño** (topología `design`), la rama consumer ganó **5.C1b** (diseño co-localizado vs repo
> de diseño aparte) y el esquema ganó `design_targets`/`design_source`/`target_platforms`. **A re-probar:**
> el único ✓ que vuelve a ejercitar el SKILL cambiado es **CU-1.b** (arranque del init: el wizard muestra
> ahora 4 opciones y se escribe el esquema nuevo) → marcado 🔁 arriba; re-ejecutar tras `bash setup.sh`.
> **No requieren re-test:** los demás ✓ son del hook de sesión (CU-1.a/c/d/f/g — el hook no cambió con
> D-011) o de la capa determinista ya cubierta por `test_sdd_init_detect.py` — incluida la reparación de
> **CU-1.e** (el caso nuevo de topología `design` lo cubre `RepairPlanTest`; la conducta manual del agente
> no cambia). Lo nuevo a probar de cero (no es re-test) son **CU-1.q** (topología `design`) y **CU-1.i**
> caso 4 (consumer con repo de diseño), ambos `[ ]`.

---

## Modelo de cobertura — qué ejes del wizard hay que probar y cuáles no

El wizard de `wf-project-init` tiene varios ejes (topología, PRD, diseño, superficie,
framework, rigor…). El producto cartesiano de sus valores es grande, pero **no todos los
ejes cambian lo que se instala**. CU-1 prueba **ramas de decisión**, no combinaciones de
valores: un eje solo merece un caso por rama si **cambia el set de fases instaladas o el
flujo de preguntas**. Si solo se persiste en `project-init.json`, basta un único caso
parametrizado que verifique que el valor elegido aterriza.

**El eje primario es la TOPOLOGÍA** (Q1, Paso 5.0): determina el reparto de backbone y qué
ramas siguen. Los demás ejes se gatean dentro de cada topología.

**Ejes que cambian comportamiento (behavior-changing) — un caso por rama.** La columna
"Cobertura" es honesta: `✓` cubierto, `parcial` rama no aseverada explícitamente, `—` sin caso.

| Eje | Pregunta | Qué ramifica | Cobertura |
|---|---|---|---|
| **Topología** | 5.0 (Q1) | el reparto de backbone: `authoring` (prd?/spec/design? sin plan/tasks) · `consumer` (plan/tasks +design si UI, sin prd/spec) · `standalone` (todo) · `design` (solo design rol system, sin prd/spec/plan/tasks) | `✓` (CU-1.h authoring/standalone; CU-1.i consumer; CU-1.q design) |
| PRD sí/no | rama authoring/standalone | antepone (o no) la fase `prd` | `✓` (CU-1.h, CU-1.n) |
| Diseño sí/no | rama authoring/standalone | inserta `design` (rol `system` en authoring, `full` en standalone) | `✓` (CU-1.h) |
| Superficie | consumer (single) / standalone (multiSelect) | `con-UI` (mobile/desktop/web) instala diseño de feature; `backend`/`other` headless; deriva el `stack` | `✓` (CU-1.i con-UI/headless; CU-1.o) |
| Design targets | 5.D1 (topología `design`) / 5.C1b (consumer con repo de diseño aparte) | valida etiquetas `<familia>[-plataforma][-formfactor]` y **deriva** `target_platforms` (familias) — gate determinista `sdd-init-detect.py target-platforms` ([[D-011]]) | `✓` (CU-1.q design; CU-1.i caso 4 consumer; flag `--design-targets` en CU-1.p) |
| Framework | superficie móvil | deriva el `stack` y gatea targets | `✓` (CU-1.o) |
| Carpetas candidatas | 5.6 | gatea la pregunta de ubicación de artefactos | `✓` (CU-1.m) |
| Init previo | 3b | extend / rehacer / dejar | `✓` (CU-1.d, CU-1.e, CU-1.l) |
| Monorepo (marcadores en ancestro) | 3.0 | operar desde la raíz vs anidar | `✓` (CU-1.g, CU-1.j) |
| Modo libre previo | 3a | confirmar conversión a SDD | `✓` (CU-1.c) |
| Repo bajo git (SSoT) | 9b | aviso advisory si una topología productora de SSoT (`authoring`/`design`/`standalone`) no está bajo git (pin de consumers quedaría `unknown`) | `✓` (CU-1.r) |

**Ejes que solo se registran (recorded-only) — un único caso parametrizado (CU-1.n).** No
cambian el install; solo escriben un campo en `project-init.json`.

| Eje | Pregunta | Dónde aterriza | Qué NO cambia |
|---|---|---|---|
| Superficie concreta (mobile vs desktop vs web) | 5.C1/5.S3 | `surfaces[]` y `target_platforms` del diseño | dentro de "con-UI", la familia exacta no cambia las fases instaladas (sí el `target_tool` del prototipo, fase design, no el init) |

> **El rigor (standard/ligero) YA NO es un eje del init** (D-006). El init no lo pregunta:
> `pipeline_mode` arranca **siempre** `standard`. La elección standard/ligero se ofrece
> **por feature al crear el spec** (cubierto en `cu-03-specs.md`, no aquí). CU-1.n verifica
> justamente que el init **no** pregunta el rigor y persiste `pipeline_mode: standard`.

> **Implicación práctica:** dentro de una misma topología y has_ui, la superficie exacta
> (mobile/desktop/web) **instala lo mismo**: la tupla de valores no multiplica los casos del
> init, solo los ejes behavior-changing (topología, PRD, diseño, has_ui, framework) lo hacen.
> **"Mínimo" no es un eje**: es `standalone` + PRD=no + diseño=no + `surfaces=[other]` → solo
> backbone `spec`/`plan`/`tasks` agnóstico (CU-1.o lo cubre).

---

## CU-1.a — Configuración SDD vs libre en un proyecto virgen

**Precondición:** proyecto virgen, sin `.sdd/project-init.json` ni `.claude/sdd-mode.json`.
**Mecanismo:** hook `SessionStart` `bootstrap/sdd-session-check.sh` → directiva
`[SDD-PROTOCOL] mode-undecided` → bloque de protocolo en `~/.claude/CLAUDE.md`.

1. Abres Claude Code en el directorio de proyecto virgen.
   → **Esperado:** el agente presenta el wizard de modo con `AskUserQuestion`
     ("Modo SDD" / "Modo libre") **ANTES** de atender ninguna petición.

**Resultado:** PASS si aparece el wizard antes de cualquier otra cosa · FALLO si no
pregunta, o atiende tu petición sin preguntar.
**Desviación → reportar:** issue citando `CU-1.a`.

## CU-1.b — Elegir "Modo SDD" arranca el init

**Precondición:** wizard de modo presentado (CU-1.a).
**Mecanismo:** bloque de protocolo → escribe `.claude/sdd-mode.json` → invoca el skill
`wf-project-init` (subagente: orquestador del propio skill, `context: fork`).

1. Eliges "Modo SDD".
   → **Esperado:** se crea `.claude/sdd-mode.json` con `{"mode":"sdd",…}` y a
     continuación se invoca `wf-project-init`, cuya **primera pregunta es la topología**, con
     **cuatro opciones** (tope de `AskUserQuestion`): Producto/authoring · Desarrollo/consumer ·
     Autónomo/standalone · **Diseño/design** (repo de solo-diseño: sistema visual + bundles de feature, [[D-011]]) — antes de instalar nada.
2. Completas la entrevista.
   → **Esperado:** instala el backbone que la topología determine (authoring: spec
     +prd?/design?, sin plan/tasks; consumer: plan/tasks +design si UI; standalone: todo;
     **design**: solo `design` rol `system`, sin prd/spec/plan/tasks — ver CU-1.q);
     escribe `.sdd/project-init.json` (con `topology`, `surfaces`, `design_role`, `phases`,
     `artifacts`/`artifacts_source`, `sdd_version`… y, en topología `design`, `design_targets` +
     `target_platforms` derivado), genera el `.claude/CLAUDE.md` raíz, y si hay código con stack
     concreto despacha a `wf-<stack>-init`.

**Resultado:** PASS si escribe el JSON de modo, presenta la topología primero con sus **cuatro**
opciones (incluida Diseño/design) e instala el backbone que la topología decide · FALLO si instala
sin preguntar la topología, si Q1 no ofrece la 4ª opción Diseño, o no escribe `project-init.json`.
**Desviación → reportar:** issue citando `CU-1.b`. La cobertura específica de la topología `design`
(backbone, `design_targets`, `target_platforms`) vive en **CU-1.q**; aquí solo se verifica que Q1 la ofrece.

## CU-1.c — Elegir "Modo libre" silencia SDD para siempre

**Precondición:** wizard de modo presentado (CU-1.a).
**Mecanismo:** bloque de protocolo → escribe `.claude/sdd-mode.json` modo `free`.

1. Eliges "Modo libre".
   → **Esperado:** se crea `.claude/sdd-mode.json` con `{"mode":"free",…}` y la sesión
     continúa con normalidad.
2. Abres una sesión nueva en el mismo proyecto.
   → **Esperado:** el hook lee `mode: free` y **no menciona SDD en el chat** (sin
     wizard, sin init, sin empujar SDD). La única señal de que el proyecto está en SDD
     es **ambiente**, en la status line (`⚙ SDD:libre`) — no en la conversación (D-009).

**Resultado:** PASS si escribe el JSON `free`, no vuelve a preguntar y no menciona SDD en
el chat en sesiones posteriores (que la status line muestre `⚙ SDD:libre` es lo esperado,
no un fallo) · FALLO si reinstala, vuelve a presentar el wizard, o empuja SDD en el chat.
**Desviación → reportar:** issue citando `CU-1.c`.

## CU-1.d — Modo SDD marcado pero init no completado (`init-pending`)

**Precondición:** existe `.claude/sdd-mode.json` con `mode: sdd` pero **no** existe
`.sdd/project-init.json`.
**Mecanismo:** hook → directiva `[SDD-PROTOCOL] init-pending`.

1. Abres Claude Code en ese proyecto.
   → **Esperado:** el agente invoca `wf-project-init` **directamente**, sin repetir el
     wizard de modo.

**Resultado:** PASS si arranca el init sin re-preguntar el modo · FALLO si repite el
wizard, o ignora el init pendiente.
**Desviación → reportar:** issue citando `CU-1.d`.

## CU-1.e — Init a medias: fases declaradas no instaladas (`init-incomplete`)

**Precondición:** `.sdd/project-init.json` declara fases (p. ej. `design`) cuyos
ficheros de instalación no están presentes.
**Mecanismo:** hook → directiva `[SDD-PROTOCOL] init-incomplete`.

1. Abres Claude Code en ese proyecto.
   → **Esperado:** el agente invoca `wf-project-init` en modo **"Completar / ampliar"**
     para reparar las fases que faltan, **antes** de atender tu petición, y sin repetir
     el wizard de modo.
2. (reparación determinista) El init repara el hueco **sin volver a poner la fase en
   cuestión**: `phases` es el contrato. Apoyándose en `sdd-init-detect.py repair-plan`,
   instala las `missing_phases` y fija el `design_role` **derivado de la topología**
   (authoring→`system`, consumer-con-UI→`feature`, standalone→`full`, design→`system`) — **no** presenta
   un `AskUserQuestion` para decidir el rol ni para "instalar vs quitar" la fase
   declarada. Quitar una fase declarada es un cambio de alcance explícito, no reparación.

**Resultado:** PASS si repara las fases ausentes sin re-entrevistar de cero **y de forma
determinista** (deriva el rol de la topología, sin preguntarlo) · FALLO si ignora el
hueco, rehace todo el init, **o abre un `AskUserQuestion` para decidir el rol o el
instalar-vs-quitar de una fase ya declarada**.
**Desviación → reportar:** issue citando `CU-1.e`.

## CU-1.f — Instalación de versión anterior (`version-drift`)

**Precondición:** `.sdd/sdd-version.json` declara una versión/commit anterior a la del
ecosistema (`$SDD_HOME/VERSION`).
**Mecanismo:** hook → directiva `[SDD-PROTOCOL] version-drift` (**solo informativa**).

1. Abres Claude Code en ese proyecto y pides algo normal.
   → **Esperado:** el agente menciona **en una línea** que puedes actualizar con
     `/wf-sdd-update` cuando te convenga, y **atiende tu petición con normalidad**. No
     actualiza sin que lo pidas ni repite el aviso en la misma sesión.

**Resultado:** PASS si avisa en una línea, no bloquea y no actualiza solo · FALLO si
bloquea la petición, o actualiza sin pedírselo, o repite el aviso.
**Desviación → reportar:** issue citando `CU-1.f`.

## CU-1.g — Sesión abierta en un subdirectorio (monorepo)

**Precondición:** los marcadores (`.sdd/`, `.claude/sdd-mode.json`) viven en un
**ancestro** (la raíz del proyecto), y abres la sesión en un subpaquete.
**Mecanismo:** hook → búsqueda de marcadores hacia arriba, con techo en el git toplevel
(`_sdd_find_up`).

1. Abres Claude Code dentro de un subpaquete del monorepo.
   → **Esperado:** el hook encuentra los marcadores en el ancestro más cercano (sin
     pasar del git root) y trata el proyecto como **ya inicializado** — no presenta el
     wizard ni reinicializa el subpaquete.

**Resultado:** PASS si reconoce la instalación del ancestro · FALLO si vuelve a
preguntar el modo o intenta inicializar el subpaquete por su cuenta.
**Desviación → reportar:** issue citando `CU-1.g`.

## CU-1.h — La topología decide qué se instala

**Precondición:** proyecto virgen; eliges "Modo SDD" (CU-1.b).
**Mecanismo:** `wf-project-init` (Q1 topología → ramas; backbone variable, Regla 4).

1. Topología **Producto (authoring)**, con PRD y sistema de diseño.
   → **Esperado:** instala `prd`+`spec`+`design` (rol `system`), **sin `plan`/`tasks`**;
     `stack: "agnostico"`, `surfaces: []`, `design_role: "system"`; `artifacts` con prd/spec/design.
     No despacha a ningún `wf-<stack>-init` (no hay código).
2. Topología **Autónomo (standalone)** con PRD=no, diseño=no, superficie "Otro" (caso **Mínimo**).
   → **Esperado:** instala **solo** el backbone `spec`/`plan`/`tasks`, `stack: "agnostico"`,
     sin `prd`/`design`; `design_role: null`.
3. Topología **Autónomo (standalone)** con diseño y superficie **móvil** sobre un stack detectable.
   → **Esperado:** instala `prd?`+`spec`+`design` (rol `full`)+`plan`+`tasks`, entrevista
     técnica (framework→stack), registra el `stack` y despacha a `wf-<stack>-init` al cerrar.

**Resultado:** PASS si el set de fases y el `design_role` coinciden con la topología/diseño
elegidos (authoring **sin** plan/tasks; standalone completo; mínimo = solo backbone) · FALLO
si instala plan/tasks en authoring, instala diseño donde se dijo que no, o salta la entrevista
técnica en standalone con código.
**Desviación → reportar:** issue citando `CU-1.h`.

## CU-1.i — Topología consumer: repo que consume specs de un SSoT

**Precondición:** un repo técnico (server/app/web) que **no** aloja sus specs; los specs viven
en otro repo SSoT del que tienes un checkout local (sibling `../<repo>` o submodule con
`features/` o `*_features.md`).
**Mecanismo:** `wf-project-init` Q1 → **Desarrollo (consumer)**: pide el path al checkout del SSoT y
la **superficie** (5.C0/5.C1). `consumer` salta PRD/Diseño-sistema; instala `plan`+`tasks` (+`design`
rol `feature` **si la superficie tiene UI** y el diseño es co-localizado); escribe `artifacts_source` +
`artifacts_source_pin` en `project-init.json` (no la clave `artifacts`). Si tiene UI, **5.C1b** decide
dónde vive el diseño: co-localizado en el SSoT (rol feature, flows/views locales) o en un **repo de
diseño aparte** (D-011: `design_source` + `design_targets`, sin design local).

1. Consumer con superficie **Web** (con-UI); das el path al checkout del SSoT.
   → **Esperado:** valida que el path existe y contiene specs; instala `phases: ["design","plan","tasks"]`
     (design rol feature, **sin prd/spec**), `design_role: "feature"`, `has_ui: true`; crea `features/`
     y escribe `artifacts_source` + `artifacts_source_pin` (commit corto del SSoT). El `CLAUDE.md` raíz
     lleva la sección **"Topología: repo consumidor"** (specs **y `DESIGN.md`** del SSoT en solo lectura;
     `flows`/`views` locales de esta superficie).
2. Consumer con superficie **Backend** (headless).
   → **Esperado:** instala **solo `plan`+`tasks`**, `design_role: null`, `has_ui: false`; sin diseño.
3. Das un path que **no** contiene specs.
   → **Esperado:** **no** continúa: re-pregunta el path o detiene con instrucciones de clonar el SSoT;
     no inventa una raíz de specs ni instala como standalone.
4. Consumer con superficie **App móvil** (con-UI) y, en **5.C1b**, "repo de diseño aparte" ([[D-011]]);
   das el path al checkout del repo `design` y el/los design target(s) que consume (p. ej. `mobile-android`).
   → **Esperado:** instala **solo `plan`+`tasks`** (NO la fase `design`), `design_role: null`, `has_ui: true`;
     escribe `artifacts_source`/pin **y** `design_source` + `design_source_pin` + `design_targets`. El
     `CLAUDE.md` raíz indica que los `flows`/`views` se **resuelven en solo lectura** desde `<design_source>`
     (`base ⊕ override` por target, `sdd-design-resolve.py`) — no se autoran aquí. `wf-prepare-plan` resuelve
     el handoff de Design desde el repo `design`, no en local.
5. ([[D-012]]) Como el caso 4, pero el repo SSoT de specs (`artifacts_source`) **también** trae diseño
   co-localizado (su `project-init.json` declara la fase `design`).
   → **Esperado:** el init **avisa** (no bloquea) del **doble SSoT de diseño**: el repo de specs ya trae un
     `DESIGN.md` y vas a apuntar a un repo de diseño aparte → gana `design_source` y el co-localizado queda
     ignorado; sugiere unificar en un solo SSoT. Continúa si el usuario confirma (p. ej. migración). Tras
     escribir el `project-init.json`, `sdd-source-drift.py check` lo reporta como `design_ssot.dual_design_ssot: true`.

**Resultado:** PASS si instala solo plan+tasks con `artifacts_source`/pin, exige un SSoT válido, en el
caso 4 persiste `design_source`/pin/`design_targets` sin instalar design local, y en el caso 5 **avisa**
del doble SSoT de diseño sin bloquear · FALLO si instala prd/spec/design en un consumer, escribe la clave
`artifacts` canónica, acepta un path sin specs, autora flows/views localmente cuando hay `design_source`,
o **calla** ante el doble SSoT de diseño (caso 5).
**Desviación → reportar:** issue citando `CU-1.i`.

## CU-1.j — Init invocado desde un subpaquete de un monorepo ya inicializado (gate de workflow)

**Precondición:** un monorepo con `.sdd/project-init.json` en la **raíz**; pides el init **desde un
subpaquete** (no es el hook de sesión de `CU-1.g`, sino invocar `wf-project-init` explícitamente).
**Mecanismo:** `wf-project-init` Paso 3.0 — busca marcadores hacia arriba hasta el git toplevel; si
el `sdd-root` es un **ancestro distinto del cwd**, presenta `AskUserQuestion`.

1. Le pides inicializar/configurar SDD estando dentro del subpaquete.
   → **Esperado:** detecta que la raíz ya tiene SDD y pregunta **"Operar desde la raíz `<sdd-root>`"** /
     **"Inicializar aquí (subproyecto independiente)"** — **no** inicializa anidado por su cuenta.
2. Eliges "Operar desde la raíz".
   → **Esperado:** se detiene e indica `cd <sdd-root>` y relanzar el init desde ahí; no escribe nada en el subpaquete.

**Resultado:** PASS si pregunta antes de anidar y respeta la raíz · FALLO si inicializa el subpaquete
sin preguntar, o ignora la instalación del ancestro.
**Desviación → reportar:** issue citando `CU-1.j`.

## CU-1.k — Verificación bloqueante: un init sin fases instaladas es un init FALLIDO

**Precondición:** tenías una petición pendiente (una consulta normal) al arrancar el init; el install
de alguna fase declarada **no** dejó su `.claude/rules/sdd-<fase>.md`.
**Mecanismo:** `wf-project-init` Paso 9 (verificación obligatoria) — el workflow es **BLOQUEANTE**.

1. Completas la entrevista y el init llega al Paso 9 con un check en FALLO (fase declarada sin instalar).
   → **Esperado:** **no** da el init por terminado ni atiende tu petición pendiente: reporta el FALLO,
     corrige (re-ejecuta `install.sh <fase>`) y re-verifica hasta tener todos los checks en verde.
2. Pides que atienda tu consulta original mientras el init sigue incompleto.
   → **Esperado:** mantiene el bloqueo — un init con fases declaradas no instaladas no se considera completado.

**Resultado:** PASS si bloquea hasta verificación en verde y no atiende la petición pendiente ·
FALLO si declara el init terminado con checks en FALLO, o atiende la petición dejando fases sin instalar.
**Desviación → reportar:** issue citando `CU-1.k`.

## CU-1.l — La topología evoluciona vía "Completar / ampliar" (authoring → standalone)

**Precondición:** un proyecto inicializado antes como **Producto (authoring)** por un PM
(`project-init.json` con `topology: "authoring"`, sin `plan`/`tasks`); ahora se le añade código en
el mismo repo (pasa a monorepo).
**Mecanismo:** `wf-project-init` `MODE=extend`, Paso 8 — `topology` **se reescribe** (no se acumula:
un repo es lo que es, D-005); el extend recalcula las fases y añade las que falten preservando lo previo.

1. Reinicializas eligiendo **"Completar / ampliar"** y cambias el contenido a **Autónomo (standalone)**.
   → **Esperado:** `topology` pasa de `"authoring"` a `"standalone"`; se **añaden** `plan`+`tasks` (y
     `design` rol `full` si procede) a las fases ya instaladas; se completa la entrevista técnica (stack)
     sin re-preguntar lo ya conocido; `prd`/`spec` previos **no se pierden**.
2. Re-corres el mismo extend sin cambios.
   → **Esperado:** idempotente — no duplica fases ni reescribe estado innecesariamente.

**Resultado:** PASS si reescribe `topology` y añade las fases que faltan preservando la autoría previa ·
FALLO si deja `topology: authoring` con `plan`/`tasks` instalados (estado incoherente), o pierde los
artefactos de autoría.
**Desviación → reportar:** issue citando `CU-1.l`.

## CU-1.m — Ubicación de artefactos no canónica (carpeta propia del proyecto)

**Precondición:** un proyecto que ya tiene una carpeta propia candidata para una fase (p. ej. `specs/`
o `docs/specs/`).
**Mecanismo:** `wf-project-init` Paso 3d (detección de candidatas) + 5.6 (pregunta por fase) + Paso 6
(ajuste del frontmatter `paths:` de `.claude/rules/sdd-<fase>.md`).

1. Inicializas; el init detecta la carpeta candidata.
   → **Esperado:** pregunta dónde deben vivir los artefactos de esa fase ("Usar `<candidata>`" /
     "Usar la canónica (`<fase>/`)") y guarda la elección en el mapa `artifacts` de `project-init.json`.
2. Eliges la carpeta **no canónica** (p. ej. `specs/`).
   → **Esperado:** `artifacts.spec` apunta a `specs/` y el init **edita el glob de directorio** de la
     regla (`"spec/**"` → `"specs/**"`); los globs por nombre de artefacto (`**/*_spec.md`) **no** se tocan.

**Resultado:** PASS si registra la ruta elegida y ajusta solo el glob de directorio de la regla · FALLO
si ignora la candidata, o deja la regla apuntando al directorio canónico que no se usa.
**Desviación → reportar:** issue citando `CU-1.m`.

## CU-1.n — El init NO pregunta el rigor; `pipeline_mode` arranca `standard` (D-006)

**Precondición:** proyecto virgen; eliges "Modo SDD", topología **Producto (authoring)** con PRD
y sistema de diseño.
**Mecanismo:** D-006 — el rigor sale del wizard del init. `wf-project-init` Paso 5 ya **no** tiene
la pregunta de pipeline; Paso 8 escribe `pipeline_mode: "standard"` fijo. La elección standard/ligero
se ofrece por feature al crear el spec (`cu-03-specs.md`), no aquí.

1. Completas la entrevista de init de principio a fin.
   → **Esperado:** en **ningún momento** se pregunta el rigor del pipeline (standard/ligero). La
     entrevista de authoring son Q1 topología + (PRD, sistema de diseño); no aparece una pregunta
     "¿Qué rigor de pipeline…?".
2. Inspeccionas `project-init.json`.
   → **Esperado:** `pipeline_mode` es **`standard`** (valor fijo del init), independientemente de
     nada que hayas elegido. El resumen previo a instalar muestra `Pipeline: standard (default; el
     modo se elige por feature al crear el spec)`.
3. (override de proyecto) Editas a mano `pipeline_mode: "light"` en `project-init.json`.
   → **Esperado:** es un cambio válido y soportado (el campo sigue existiendo como override de
     proyecto); el init no lo revierte en un `extend` posterior salvo "Rehacer desde cero".

**Resultado:** PASS si el init no pregunta el rigor y persiste `pipeline_mode: standard` · FALLO si
reaparece la pregunta de pipeline en la entrevista, o si `pipeline_mode` arranca con un valor distinto
de `standard`.
**Desviación → reportar:** issue citando `CU-1.n`.

## CU-1.o — Superficie y framework SÍ ramifican; el caso "Mínimo"

**Precondición:** proyecto virgen; eliges "Modo SDD". Cierra las ramas behavior-changing de
**superficie** y **framework** (incluido el gate de targets) y el caso **Mínimo** (que sustituye al
antiguo perfil `custom`).
**Mecanismo:** Q1 topología → rama; la **superficie** (5.C1 consumer / 5.S3 standalone) gatea el
diseño de feature (consumer, ver CU-1.i) y el **framework** (solo superficie móvil); el framework
gatea **Targets**; 5.7 deriva el `stack`.

**A — la superficie gatea el diseño de feature en consumer.** Cubierto en CU-1.i: superficie con-UI
(web) instala `design` rol feature; backend (headless) no.

**B — el framework móvil deriva stack distinto y gatea targets.**
1. Standalone + superficie **App móvil** + framework **Compose Multiplatform** (o **Flutter**).
   → **Esperado:** aparece **Targets** (multiSelect Android/iOS/Desktop, mínimo uno); `stack` = `kmm`
     (o `flutter`); `targets` se persiste en `project-init.json`.
2. Standalone + superficie **App móvil** + framework **Android (Nativa)** (o **iOS Nativa**).
   → **Esperado:** **NO** aparece Targets (no es multiplataforma); `stack` = `android` (o `ios`); la
     clave `targets` se **omite** del JSON.

**C — caso "Mínimo" (sustituye al antiguo perfil `custom`).**
3. Standalone + PRD=no + diseño=no + superficie **Otro (librería/CLI/tooling)**.
   → **Esperado:** **NO** pregunta framework ni targets; `stack` = `agnostico`; `phases` = solo el
     backbone `spec`/`plan`/`tasks`; `design_role: null`. Es la configuración mínima del pipeline.

**Resultado:** PASS si el set de preguntas que aparecen y el `stack`/`targets`/`phases` coinciden con
la superficie/framework elegidos · FALLO si pregunta framework sin superficie móvil, deriva un stack
que no corresponde al framework, o instala diseño en el caso mínimo.
**Desviación → reportar:** issue citando `CU-1.o`.

## CU-1.p — Los argumentos honran y saltan preguntas (por usuario o por orquestador)

**Precondición:** proyecto virgen.
**Mecanismo:** `wf-project-init` Paso 1 (`$ARGUMENTS`) + Paso 5 regla 2 ("no preguntar lo que
ya se sabe"). Los args llegan **tecleados** (`/wf-project-init <flags>`) o vía el campo `args`
del Skill tool cuando invoca el **orquestador** (p. ej. desde el hook de sesión o una petición
en lenguaje natural). Ambas vías son equivalentes.

1. `/wf-project-init --topology authoring --prd`.
   → **Esperado:** NO pregunta topología ni PRD (los da por conocidos, a lo sumo confirma); la
     entrevista sigue solo con lo que falta (sistema de diseño, pipeline). `project-init.json`
     registra `topology: authoring` y la fase `prd`.
2. `/wf-project-init --topology standalone --surfaces mobile --stack kmm`.
   → **Esperado:** salta topología, superficie, framework y targets (stack derivado del flag); va
     directo a lo que falte (PRD, diseño, pipeline).
3. (entrada por orquestador) Sin teclear el skill, una petición en lenguaje natural que el
   orquestador mapea a `wf-project-init` pasando `args`.
   → **Esperado:** mismo efecto que tecleado — los flags saltan sus preguntas.
4. ([[D-011]]) `/wf-project-init --topology design --design-targets mobile-android,mobile-ios`.
   → **Esperado:** salta **Q1** (topología) **y 5.D1** (design targets) — los da por conocidos; valida
     los targets con `sdd-init-detect.py target-platforms` y **deriva** `target_platforms: [mobile]`
     (no lo teclea). `project-init.json` registra `topology: design`, `phases: ["design"]` (rol
     `system`), `design_targets: ["mobile-android","mobile-ios"]` y `target_platforms` derivado.
5. (negativo) Un flag con valor fuera del enum (p. ej. `--topology xxx`), o un `--design-targets` con
   etiqueta inválida (p. ej. `mobile_ios`, familia rota).
   → **Esperado:** no se traga en silencio — lo ignora y pregunta, o pide un valor válido; nunca
     inicializa con una topología inexistente ni con design targets inválidos (el subcomando
     `target-platforms` los marca en `invalid` y el init re-pregunta).

**Resultado:** PASS si los flags válidos saltan su pregunta y aterrizan en el estado (incluidos
`--topology design` y `--design-targets`, con `target_platforms` derivado), y un flag inválido no se
acepta · FALLO si re-pregunta algo ya dado por flag, teclea `target_platforms` en vez de derivarlo, o
acepta un valor fuera del enum / design target inválido.
**Nota de testeo:** la entrevista es interactiva (`AskUserQuestion`) → se valida **a mano**. La
parte determinista (detección/verificación) la cubren los unittest de `sdd-init-detect.py`
(`test_sdd_init_detect.py`).
**Desviación → reportar:** issue citando `CU-1.p`.

## CU-1.q — Topología `design`: repo de solo-diseño ([[D-011]])

**Precondición:** proyecto virgen; eliges "Modo SDD" (CU-1.b).
**Mecanismo:** `wf-project-init` Q1 → **Diseño (repo de solo-diseño)** (4ª opción, tope de 4):
rama DESIGN (5.D1) que declara los **design targets** que cubre y deriva `target_platforms` con el
subcomando determinista `sdd-init-detect.py target-platforms`. Backbone: **solo `design`** (rol
`system`), sin prd/spec/plan/tasks. La etiqueta sigue la convención validada
`<familia>[-<plataforma>][-<formfactor>]`, familia ∈ `{mobile,web,desktop}`.

1. Topología **Diseño** con design targets `mobile-android`, `mobile-ios` y (vía "Other") `desktop`.
   → **Esperado:** instala `phases: ["design"]` (rol `system`), **sin prd/spec/plan/tasks**;
     `topology: "design"`, `stack: "agnostico"`, `surfaces: []`, `has_ui: false`,
     `design_role: "system"`; `design_targets: ["mobile-android","mobile-ios","desktop"]` y
     `target_platforms: ["mobile","desktop"]` (derivado, no tecleado). `artifacts` con solo la clave
     `design`; crea `<artifacts.design>/` y `features/`. El `CLAUDE.md` raíz lleva la sección
     **"Topología: repo de diseño (SSoT visual)"**. No despacha a ningún `wf-<stack>-init`.
2. (negativo) Un design target con familia inválida o patrón roto (p. ej. `Mobile`, `tablet`, `mobile_ios`).
   → **Esperado:** el subcomando `target-platforms` lo marca en `invalid` (`all_valid: false`); el init
     **muestra los inválidos y re-pregunta** — no inicializa con targets inválidos ni inventa la familia.

**Resultado:** PASS si instala solo `design` rol `system`, persiste `design_targets` + `target_platforms`
derivado, y rechaza targets inválidos · FALLO si instala plan/tasks/spec, teclea `target_platforms` a
mano (en vez de derivarlo), o acepta una familia fuera de `{mobile,web,desktop}`.
**Nota de testeo:** la entrevista es interactiva (`AskUserQuestion`) → **a mano**. La parte determinista
—derivación/validación de targets y el esquema con topología `design`— la cubren `test_sdd_init_detect.py`
(`DesignTargetsTest`, `VerifyTest.test_design_topology_passes`, `RepairPlanTest.test_design_topology_*`).
**Desviación → reportar:** issue citando `CU-1.q`.

## CU-1.r — Aviso de SSoT sin git (advisory, topologías productoras)

**Precondición:** proyecto virgen **no inicializado como repo git** (`git rev-parse` falla); eliges "Modo SDD".
**Mecanismo:** `wf-project-init` Paso 9b — tras la verificación, si la topología produce un SSoT que los
consumers pinean por SHA (`authoring`/`design`/`standalone`) y `sdd-init-detect.py detect` reporta
`is_git_repo: false`, avisa (no bloquea). El `consumer` queda **excluido** (no es SSoT).

1. Topología **Producto (authoring)** en un directorio que **no** está bajo git.
   → **Esperado:** el init completa la instalación con normalidad y, al final, **avisa** (advisory, no
     bloquea): este repo es un SSoT que los consumers pinearán por SHA pero no está bajo control de
     versiones; recomienda `git init` + primer commit para que el pin no quede `unknown`. No reintenta
     ni aborta el init.
2. La misma topología en un directorio **sí** bajo git (o cualquier topología **consumer**, con o sin git).
   → **Esperado:** **no** emite el aviso (git presente, o consumer = no es SSoT).

**Resultado:** PASS si avisa solo para `authoring`/`design`/`standalone` sin git, sin bloquear, y calla
con git presente o en `consumer` · FALLO si bloquea el init por falta de git, avisa en un `consumer`, o
calla en una topología productora sin git.
**Nota de testeo:** el criterio de consistencia entre corridas es **semántico**, no literal. El estado git
es determinista (`sdd-init-detect.py detect` → `is_git_repo`, cubierto por `DetectStateTest.test_is_git_repo_*`)
y el aviso se emite por **`echo` determinista** (Paso 9b, `case` sobre la topología) — la línea canónica
existe en la salida de la herramienta. Pero el usuario lee el **informe final del agente** (prosa, salida de
Bash colapsada), donde el aviso se **re-narra** y por tanto su redacción literal **varía entre corridas** —
esto es inherente a un informe en lenguaje natural y **no es FALLO** (se observó incluso en el recordatorio
canónico del Paso 11). Dos corridas son consistentes si el aviso **aparece siempre, como advisory, y
transmite las mismas ideas**: no-git · SSoT pineado por SHA · `git init` · pin `unknown` · drift no funciona.
El determinismo literal vive en los scripts (gate `is_git_repo`, checks de instalación), no en el informe.
**Desviación → reportar:** issue citando `CU-1.r`.
