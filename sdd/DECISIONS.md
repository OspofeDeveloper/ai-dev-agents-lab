# Registro de decisiones del ecosistema SDD

Constancia de las **decisiones de diseño** y los **aprendizajes** del ecosistema: por qué se hizo algo de una manera y no de otra, qué aprendimos al equivocarnos. Complementa al `CHANGELOG.md` (qué cambió, por versión) respondiendo al **por qué**.

Formato: una entrada `## D-NNN — <título>` por decisión, **más reciente arriba** (como el CHANGELOG). Cada entrada lleva: fecha, estado, contexto, decisión, alternativas descartadas, consecuencias/aprendizaje y referencias. Las entradas son append-only: si una decisión se revierte, no se borra — se añade una nueva que la supersede y se marca la vieja `Superada por D-MMM`.

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
