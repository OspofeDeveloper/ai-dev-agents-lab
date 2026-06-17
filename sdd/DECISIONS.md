# Registro de decisiones del ecosistema SDD

Constancia de las **decisiones de diseño** y los **aprendizajes** del ecosistema: por qué se hizo algo de una manera y no de otra, qué aprendimos al equivocarnos. Complementa al `CHANGELOG.md` (qué cambió, por versión) respondiendo al **por qué**.

Formato: una entrada `## D-NNN — <título>` por decisión, **más reciente arriba** (como el CHANGELOG). Cada entrada lleva: fecha, estado, contexto, decisión, alternativas descartadas, consecuencias/aprendizaje y referencias. Las entradas son append-only: si una decisión se revierte, no se borra — se añade una nueva que la supersede y se marca la vieja `Superada por D-MMM`.

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
