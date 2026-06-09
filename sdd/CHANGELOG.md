# Changelog del ecosistema SDD

Formato: `## <versión> — <fecha>`. Las líneas con `⚠` son cambios que afectan a proyectos ya inicializados (`wf-sdd-update` las muestra al actualizar).

## 0.18.0 — 2026-06-09

Soporte de monorepo en el hook y el init (ROADMAP 5.7):

- Abrir sesión en la raíz de un monorepo vs. en un subpaquete daba estados SDD distintos: el hook solo miraba el cwd, así que en un subpaquete (cuyo `.sdd/` vive en la raíz) volvía a disparar el wizard de modo. Ahora el **hook busca los marcadores SDD (`.sdd/project-init.json`, `.claude/sdd-mode.json`) hacia arriba hasta el toplevel git** (techo); fuera de git, solo el cwd (comportamiento previo intacto). Gana el ancestro más cercano: un `.sdd/` propio del subpaquete prevalece sobre el de la raíz. Los checks de init-incomplete y version-drift se anclan en la raíz encontrada.
- **`wf-project-init` (Paso 3.0)** aplica la misma lógica de techo git: si se ejecuta desde un subpaquete de un monorepo ya inicializado, detecta el init/modo en un ancestro y **no crea un `.sdd/` anidado** — pregunta si operar desde la raíz (recomendado: `cd <raíz>` y relanzar) o inicializar aquí como subproyecto independiente (caso raro pero legítimo). Cuando el marcador está en el cwd o no hay, el flujo es idéntico al actual.
- Capa bootstrap (hook + skill global de init): se sincroniza con `bash setup.sh --update`, no con `/wf-sdd-update`. El fallback manual del bloque `SDD-BOOTSTRAP` también se documentó como monorepo-aware. Sin scripts de enforcement nuevos. NO incluye multi-stack por ruta ni topología multi-root (eso es 6.1/A3). Verificado: `bash -n` + 6 casos del hook (raíz, subpaquete, init-incomplete desde subpaquete, modo free en raíz, `.sdd/` propio del subpaquete que gana, no-git intacto) + 4 casos de la detección del init.

## 0.17.0 — 2026-06-09

Opt-out por ruta y desinstalación del bootstrap global (ROADMAP 5.6):

- **`bash setup.sh --uninstall`** — antes no había forma limpia de retirar el bootstrap global: el hook seguía disparando el wizard en todos los proyectos del dev. Ahora revierte exactamente lo que instala `setup.sh` (skills globales `wf-project-init`/`wf-sdd-update`, `~/.sdd-home`, hook, registro en `~/.claude/settings.json`, bloque `SDD-BOOTSTRAP` de `~/.claude/CLAUDE.md`) y los symlinks de `--dev`. **Preserva todo lo ajeno**: otros hooks del equipo, `PreToolUse`, permisos, skills propias y las notas personales del `CLAUDE.md`. Best-effort e idempotente; NO toca los proyectos consumidores (`.sdd/`, `.claude/sdd-mode.json` son de cada repo).
- **Allowlist/denylist de rutas en el hook** — el dev puede silenciar el hook en proyectos concretos sin marcar cada repo, con dos listas opcionales de prefijos de ruta en `~/.claude/` (`#` comenta, `~` se expande a `$HOME`, un prefijo por línea): `sdd-denylist` (calla bajo esos prefijos) y `sdd-allowlist` (si tiene prefijos, el hook **solo** actúa dentro — modo opt-in). La denylist gana sobre la allowlist. El opt-out por repo y commiteable sigue siendo `.claude/sdd-mode.json`.
- Documentado en el bloque `SDD-BOOTSTRAP` (`claude-global-block.md`) y en el resumen de `setup.sh`. Cambio de la **capa bootstrap global** (no del install por proyecto): se sincroniza con `bash setup.sh --update`, no con `/wf-sdd-update`. Sin scripts de enforcement nuevos. Verificado: 6 casos del hook (deny, allow opt-in, allow vacía, deny>allow, `~`) + uninstall en HOME falso (preserva hook de equipo/permisos/notas, idempotente).

## 0.16.0 — 2026-06-09

Roles y aprobaciones diferenciadas en los gates (ROADMAP 5.5):

- Hasta ahora todos los checkpoints eran "el humano valida" (singular, anónimo). En un equipo multi-desarrollador no quedaba traza de **qué rol** aprobó cada gate. Nuevo campo `Aprobado por: <rol> (<YYYY-MM-DD>)` que cada gate escribe en el header de su artefacto al pasar: **PM/Product Owner** en el PRD (`wf-prd-review` con veredicto `LISTO`), **Tech Lead** en el plan (`wf-plan-validate` tras sello `VALIDADO`), **QA** en el report (`wf-qa-verify` con `APTO`/`APTO_CON_RESERVAS`). El rol se captura con `AskUserQuestion` (default por fase, el usuario confirma o da nombre); solo se escribe si el gate pasa, nunca se autoaprueba.
- **Es un registro de checkpoint humano, no un sello determinista**: `Aprobado por` es un dato humano **no verificable mecánicamente**, así que lo escribe el orquestador/workflow en el gate — NO un script. `sdd-seal.py` y los gates **no lo verifican** (no podrían). Mismo patrón que las dos atribuciones humanas que ya existían (`Aprobada por` per-TD de deuda técnica en `wf-plan-validate`, `confirmado por` de TCs manuales en `wf-qa-verify`). **Sin cambios en ningún script.**
- **SSoT única**: convenio (nombre, formato, semántica autor≠sellador, tabla de los 3 gates) definido una sola vez en `kb-traceability-rules` **Regla 10** (misma KB cross-fase que ya posee el eje "anotación de header del orquestador vs. sello de script": `derived_from_prd_hash` Regla 1, `Enmienda pendiente` Regla 9). Las KBs de fase (`kb-plan-expert` "Estados del Plan", `kb-qa-expert`, `kb-prd-expert` Regla 13 nueva) la **referencian**, no la redefinen. Plantillas de header (plan, qa_report, PRD) nacen con la línea como placeholder hasta la aprobación; el override KMM de `kb-plan-expert` conserva el contrato del header.
- 11 archivos (solo `SKILL.md`/`references`), sin scripts ni gates nuevos, registry sin cambios de inventario. ⚠ Proyectos ya inicializados: `/wf-sdd-update` para que sus gates empiecen a registrar el aprobador (sin actualizar, el comportamiento previo sigue válido — el campo simplemente no se escribe).

## 0.15.0 — 2026-06-09

Cascade de cambio de producto en un solo comando (ROADMAP 4.4):

- Nuevo `wf-prd-change-cascade <prd.md> --new-reqs <cambio.md>` — compacta en un solo comando la cadena de ~9 workflows que hoy se encadenan a mano tras un cambio de PRD: `wf-prd-change` → `wf-prd-sync-impact` → `wf-spec-sync-from-prd analyze` → `apply` → `wf-spec-conflict` + `wf-spec-readiness` → `wf-design-sync` → reporte de planes/tasks stale. Produce `<basename>_cascade_report.md`.
- **Orquestador puro** (mismo patrón que `wf-spec-features-first`: sin campo `agent:`, no analiza ni escribe contenido — invoca los workflows existentes en orden y cada uno delega a su agente). `allowed-tools: [Read, Write, Bash, Skill]`.
- **Autonomía: mecánico auto + parar en gates reales.** Corre sin fricción todo el pegamento mecánico/read-only **y auto-aplica los deltas de spec inequívocos** (`severidad: minor` + `acción: delta`). Para solo en los 4 checkpoints humanos reales: (1) aprobación del cambio de producto, (2) features con cambio no trivial (`major`/`manual_review`/`rediscover`, que se listan sin aplicar y sin abortar el cascade), (3) decisiones visuales de Design (`wf-design-sync` solo diagnostica), (4) revalidación de plan + aprobación de deuda. `--review-before-apply` restaura la parada conservadora antes de cualquier escritura; `--dry-run` solo diagnostica; `--features` acota el subset; `--skip-design` omite Design.
- **Profundidad adaptativa**: solo entra en Design si existe `DESIGN.md` y la fase está instalada; solo reporta planes/tasks si existen artefactos; resuelve `phases`/`artifacts` de `.sdd/project-init.json`. **Degradación con gracia**: un sub-workflow no instalado se reporta como `no disponible` sin abortar el cascade.
- Vive en la fase `prd` (es donde nace el disparador: el cambio de PRD); `install.sh prd` lo recoge por glob. Rootmaps (raíz + prd) y nota de pipeline de cambios de producto actualizados; registry 120 skills (+1 wf). Sin scripts nuevos. Proyectos ya inicializados lo reciben con `/wf-sdd-update`.

## 0.14.0 — 2026-06-08

Detección de deriva en la fase Design (ROADMAP 4.3):

- Nuevo `wf-design-sync <DESIGN.md>` — réplica del patrón `wf-prd-sync-impact` para Design. Hasta ahora, tras cambiar el `DESIGN.md`, el brief o un spec, nada detectaba qué artefactos derivados quedaban stale (el "considera regenerar" de `wf-design-delta` era manual). Ahora se diagnostica explícitamente.
- Descubre los derivados (DESIGN_BRIEF, `_flows`/`_views`/`_ui_prompt` por feature en subcarpeta o layout plano legacy, exports de tokens, specs fuente) y asigna estado `in_sync`/`needs_review`/`stale`/`unknown` por artefacto siguiendo el **grafo de dependencias** de la fase (brief→DESIGN.md→views/ui_prompt/exports; spec→flows/views/ui_prompt) con criterio conservador (`kb-design-governance`/`kb-design-expert`: si no se puede probar alineación, no es `in_sync`). Produce `<basename>_design_sync_report.md` con matriz y acción recomendada por fila (`wf-design-delta` / `wf-design-feature-prototype` / `wf-design-export`). Delega a `design-architect`; read-only sobre los derivados.
- Alcance: análisis de impacto, no sellado por hash. El sellado determinista de deriva en Design (hash de DESIGN.md/spec en el header de cada artefacto, à la `sdd-sync-check.py`) queda como endurecimiento futuro anotado en ROADMAP 11.2.
- Rootmaps (raíz + design) y tabla de precondiciones de design actualizados; registry 119 skills (+1 wf). Sin scripts nuevos. Proyectos ya inicializados lo reciben con `/wf-sdd-update`.

## 0.13.0 — 2026-06-08

El repo destino manda sobre el dogma del stack (ROADMAP 6.3):

- La variante de stack de los agentes (la KMM de `plan-architect` y los implementadores) imponía el canon del stack (Koin, `AppResult`, `compose-resources`, Clean Architecture por capas) como dogma; un repo KMM real con otras convenciones recibía imposiciones. Fix sistémico (no parche KMM), en tres capas que ya comparten genérico y overlay tras 6.2:
- **`kb-plan-method` / `kb-tasks-method`** (hook "Overlay de stack"): reformulado — la arquitectura prescriptiva del stack es el **default para greenfield o donde el repo no se ha pronunciado**, pero **el repo destino manda cuando diverge** (convenciones reales capturadas en `<stack>_project_state.md`). El canon rellena huecos, no sobrescribe lo que el repo ya hace. Imponerlo es el mismo fallo que inventar en modo genérico.
- **`kb-kmm-project-state-protocol`** Regla 7 nueva: el `kmm_project_state.md` (= repo real) manda sobre el canon KMM cuando divergen (Hilt vs Koin, `Result` vs `AppResult`, módulos distintos, `R.*` en target único...). Aplica a TODOS los agentes KMM, incluidos los implementadores (que cargan esta KB, no el method). El `plan-architect` KMM lleva además un puntero corto de precedencia junto a su declaración de canon.
- **`kb-sdd-stack-overlay-contract`** invariante 6 nuevo + ítem de checklist: "el repo destino manda sobre el dogma" como contrato para todo overlay futuro (conecta con el invariante 1 "no romper el modo genérico"). Los overlays creados con `wf-stack-create` lo heredan (sdd-author carga esta KB).
- Refactor de criterio, sin cambios en gates/sellador. Registry 118 skills (una description actualizada). ⚠ Proyectos ya inicializados: `/wf-sdd-update` para recibir las method KB y el protocolo KMM actualizados (sin actualizar, los agentes siguen prescribiendo el canon como antes).

## 0.12.0 — 2026-06-08

KB Load Status verificable (ROADMAP 1.5 — cierra la Fase 1 de enforcement):

- El `## KB Load Status` que cada agente incluye al final de su respuesta es **auto-reportado** (misma debilidad que cualquier veredicto auto-emitido). Nuevo script determinista `sdd-kb-check.py`: lee el frontmatter `skills:` de cada agente instalado y verifica que cada KB existe como `.claude/skills/<kb>/SKILL.md`. `--all` / `--agent <name>`, exit 2 si falta alguna (CI). El set de KBs de un agente es fijo → se verifica en **instalación y arranque**, no por delegación.
- `install.sh` y el overlay KMM ejecutan la verificación al cerrar (paso nuevo, no bloqueante): avisan de instalaciones incompletas (agente presente con alguna KB de su frontmatter sin instalar — el fallo real que hacía importar el auto-reporte). Capta además dependencias cross-phase no traídas y overlays no re-aplicados.
- **Regla 19 de `kb-sdd-skill-architecture`** actualizada: el check determinista es la señal **autoritativa**; el `## KB Load Status` del agente queda como sanity-check **secundario** en contexto. Reflejado en el template de agente (`body-templates.md`). Cierra el hilo "verdad mecánica sobre auto-reporte" que comparten sellador, gates, features-index y project-status.
- ⚠ Proyectos ya inicializados: `/wf-sdd-update` trae `sdd-kb-check.py` a `.sdd/scripts/` y la verificación en el installer. Sin cambios de comportamiento en los agentes (su auto-reporte sigue igual, solo se reclasifica como secundario).

## 0.11.0 — 2026-06-08

Informe PM read-only del estado del proyecto (ROADMAP 2.6):

- Nuevo `wf-project-status` (fase tasks) + script determinista `sdd-project-status.py`: por cada feature determina la **fase alcanzada** (PENDIENTE/Spec/Plan/Tasks/QA/Cerrada por presencia de artefactos), el **estado** de esa fase (spec vía `_features.md` o marcadores; plan `BORRADOR`/`VALIDADO` + enmienda pendiente; tasks `X/total HECHA` + bloqueadas; qa `APTO`/`APTO_CON_RESERVAS`/`NO_APTO`), el **bloqueo** y la **siguiente acción concreta** (`/wf-*`). Tabla por feature + resumen + "Siguiente foco".
- **Read-only y mecánico, sin agente** (como `wf-sdd-status`): agrega el estado ya sellado en los artefactos por `sdd-seal.py` / `sdd-task-state.py` / `wf-qa-verify` / `sdd-features-index.py` — no razona ni edita. Aprovecha que `_features.md` es ya un índice generado fiable (0.9.0). Soporta layout plano legacy e incluye las features `PENDIENTE_GENERACIÓN` del índice sin carpeta.
- `install.sh` distribuye el script a `.sdd/scripts/` (ejecutable en CI); rootmaps de `CLAUDE.md` raíz y `tasks/CLAUDE.md` actualizados; registry regenerado (118 skills).
- Cierra el hueco de visibilidad para PM ("¿en qué punto está cada feature y qué falta?"). Sin ⚠: es capacidad nueva, no altera artefactos ni comportamiento existente. Proyectos ya inicializados lo reciben con `/wf-sdd-update`.

## 0.10.0 — 2026-06-08

Red anti-fabricación en el origen (PRD) (ROADMAP 1.6):

- Nueva **Regla 12 de `kb-prd-expert`** (SSoT): toda afirmación de negocio del PRD (actor, capacidad, exclusión, regla transversal, objetivo) **traza al material fuente / al brief del usuario, o se marca `[ASUNCIÓN]`**. Prohibida la invención silenciosa: lo que la generación infiere para completar el PRD se marca inline y se recopila en `## Asunciones del PRD` con un `[ASN-XXX]` por entrada (hueco que rellena + casilla de confirmación). IDs propios del PRD, sin colisión con `[P-XXX]` (gaps) ni `[A-XXX]` (asunciones aplicadas del spec). Tabla asunción≠gap incluida.
- `wf-prd-create` instruye la regla al `prd-expert` (énfasis agresivo cuando no hay `--source`: casi todo lo que exceda el brief es inferencia), incluye `## Asunciones del PRD` en la salida y reporta el nº de asunciones marcadas como señal de cuán débil era la fuente.
- `wf-prd-review` gana el **Paso 5.5 (gate de confirmación humana)**: detecta `[ASUNCIÓN]` con un check determinista (`grep`), presenta cada `[ASN-XXX]` al usuario (`AskUserQuestion`) para confirmar / rechazar / editar, y edita el PRD solo según esa decisión. Un PRD con asunciones sin confirmar **no puede ser `LISTO`**. Es la primera vez que el review edita el documento — acotado a resolver asunciones, nunca de cosecha propia.
- `prd-expert` (agente) alinea su flujo de creación y su regla de oro con la Regla 12; `kb-gap-conventions` añade un puntero cruzado al marcador del PRD (acota su propio ámbito a la fase Spec en adelante, sin absorber el marcador de otra fase).
- ⚠ Proyectos ya inicializados: `/wf-sdd-update` trae el `wf-prd-review` más estricto (bloquea `LISTO` con asunciones sin confirmar) y el `wf-prd-create`/`prd-expert` que marcan `[ASUNCIÓN]`. Un PRD existente sin marcadores se comporta igual que antes; el endurecimiento aplica a PRDs nuevos o a los que se vuelvan a revisar. Sin scripts nuevos (la verificación es un `grep` dentro del review).

## 0.9.0 — 2026-06-08

Concurrencia de artefactos hub — `_features.md` generado y `stack_workflows_run` como log append-only (ROADMAP 5.4):

- `_features.md` deja de ser un hub monolítico editado a mano (que varios fast-tracks pisaban en paralelo y dos devs en ramas distintas colisionaban en cada merge) y pasa a ser un **índice GENERADO** por el script determinista nuevo `sdd-features-index.py`. La salida es función pura de las fuentes (sin timestamp de reloj) → idempotente: regenerar tras un merge da bytes idénticos y un conflicto sobre el hub es ruido. Mismo principio que `generate-skill-registry.py`.
- SSoT repartido y co-localizado: `_discovery.md` = universo de features + shared models + RF→Feature; cada `spec` = que la feature está generada + sus marcadores reales + HUs/CAs; `_readiness_report.md` (su `## Matriz de readiness`) = veredicto autoritativo del estado. El script agrega fuentes estructuradas, no parsea prosa libre. Cierra de paso el candidato de prosa→script anotado en 11.2.
- Productores reconectados (ya no escriben `_features.md` a mano; llaman al script): `wf-spec-fast-track`, `wf-spec-features-first` (pasada autoritativa final), `wf-spec-readiness` (regenera desde su report — realinea con su propia declaración de "no modifica artefactos"), `wf-spec-delta` y `wf-spec-from-code`. Escritura atómica (tempfile + `os.replace`) → segura ante regeneraciones concurrentes. Eliminadas 4 guías de referencia huérfanas; `kb-decompose-expert` documenta el formato generado (sin `## Historial de cambios` manual: el audit-trail vive en el changelog de cada spec + git).
- `stack_workflows_run` sale de `project-init.json` (un array creciente en config compartida = conflicto garantizado) → log **append-only** `.sdd/stack-runs.jsonl`, una línea JSON por run. Escrito por `wf-<stack>-init` con `>>`. `project-init.json` queda como config estable.
- Guía "una feature por rama" + `_features.md` generado en el CLAUDE.md raíz que genera `wf-project-init` y en el README. `sdd-features-index.py --check` (exit 2 si está desactualizado) sirve como check de CI.
- ⚠ Proyectos ya inicializados: `/wf-sdd-update` para recibir `sdd-features-index.py` en `.sdd/scripts/` y las piezas de spec/stack actualizadas. El campo `stack_workflows_run` de un `project-init.json` antiguo queda obsoleto pero inerte (nadie lo lee); los nuevos runs de stack se anotan en `.sdd/stack-runs.jsonl`. Un `_features.md` heredado (escrito a mano) sigue siendo legible; se normaliza al formato generado en la primera regeneración.

## 0.8.0 — 2026-06-08

Núcleo metodológico compartido de los agentes override (ROADMAP 6.2):

- El procedimiento operativo de los agentes de plan/tasks deja de estar copiado a mano entre la variante genérica y la del overlay. Dos KBs nuevas son la SSoT del *cómo operar*: `kb-plan-method` (Sección A: producir un Plan — plan-architect; Sección B: auditar — plan-auditor) y `kb-tasks-method` (descomponer plan→tasks — task-generator). Stack-agnósticas, con hooks `‹especialización de stack›` en los puntos que varían.
- Los 6 agentes (genérico + KMM de plan-architect, plan-auditor, task-generator) adelgazan: cargan la method KB en `skills:` y conservan solo su capa de especialización (genérico: "el repo manda"; KMM: Clean Architecture / Koin / expect-actual / Compose / AppResult). Un cambio metodológico ahora se hace una vez en la KB, no 6 veces en los agentes.
- Las method KB **no se sobreescriben** por el overlay (no tienen variante de stack): viven en `plan/skills/` y `tasks/skills/`, las instala la base y las cargan por nombre ambas variantes (mismo mecanismo cross-fase que `kb-a11y-expert`). `kb-sdd-stack-overlay-contract` documenta el patrón (regla nueva + ítem de checklist) para que los overlays futuros lo hereden.
- Registry: 117 skills (+2 kb). Sin cambios de comportamiento — refactor de organización del conocimiento; las reglas normativas siguen en `kb-plan-expert`/`kb-tasks-expert`, los gates y el sellador intactos.
- ⚠ Proyectos ya inicializados: `/wf-sdd-update` para recibir `kb-plan-method`, `kb-tasks-method` y los 6 agentes adelgazados (sin actualizar, los agentes antiguos con metodología inline siguen funcionando — no hay ruptura, solo no se benefician de la SSoT compartida).

## 0.7.0 — 2026-06-08

Registro de deuda técnica en el plan (ROADMAP 3.2):

- Un Plan puede registrar **deuda técnica asumida** (`TD-00X`) en vez de bloquearse, pero solo cuando la incertidumbre es de **CÓMO** (técnico: legacy sin tests, módulo opaco, librería sin doc) y no de **QUÉ** (funcional → sigue siendo `TECH_GAP` y bloquea). SSoT de la frontera y el test de admisión (camino viable + no contradice el Spec + riesgo acotado) en `kb-plan-expert` (genérico y overlay KMM), con formato canónico `## Deuda técnica asumida` / `### TD-00X` (Decisión, A pesar de, Riesgo asumido, Queda pendiente, Componentes afectados, Aprobada por).
- **Gobernanza autor≠aprobador**: `plan-architect` (genérico + KMM) propone deuda con `Aprobada por: PENDIENTE` y continúa produciendo el Plan (la deuda no detiene como un gap); `plan-auditor` verifica que cada TD es deuda real y no un gap disfrazado; `wf-plan-validate` añade el **Paso 4b**: checkpoint humano explícito (AskUserQuestion) que aprueba o rechaza cada TD antes del sellado.
- **Enforcement determinista**: `sdd-seal.py` gana la condición 8 — una TD incompleta o con `Aprobada por: PENDIENTE` bloquea el sellado igual que un gap; la deuda **aprobada no bloquea** (esa es su razón de ser). Sin sección de deuda, el comportamiento es idéntico al de siempre.
- **Herencia en tasks**: `wf-prepare-tasks`/`task-generator` (genérico + KMM) propagan `- **Deuda asumida:** TD-00X` a las tasks cuyos componentes están afectados; `wf-task-run` la pasa al owner como restricción a respetar (no "resuelve" la limitación por su cuenta). Saldar la deuda es trabajo futuro del `Queda pendiente`, no genera tasks de feature.
- Desbloquea el brownfield abierto por 3.1: un legacy sin tooling genera incertidumbre técnica en cada plan; ahora se documenta y asume con trazabilidad en vez de bloquear el pipeline.
- ⚠ Proyectos ya inicializados: `/wf-sdd-update` para recibir la versión nueva de `sdd-seal.py` y las piezas de plan/tasks actualizadas (sin actualizar, los planes sin sección de deuda siguen sellándose igual; la vía de deuda simplemente no está disponible).

## 0.6.0 — 2026-06-07

Back-edge tasks→spec — enmienda desde implementación (ROADMAP 4.2):

- Nueva `wf-spec-amend` (fase spec): cuando el dev descubre implementando que un CA es ambiguo, la vía corta corrige el texto del CA (solo ACLARACIÓN estricta — cualquier cambio de comportamiento escala a `wf-spec-delta`), con confirmación humana, versión menor y entrada de changelog trazable `E-00X: aclaración CA-XXX desde T-00X`.
- Stale puntual sobre el plan: nuevo script de enforcement `sdd-amend.py` (único escritor de la anotación `> **Enmienda pendiente:** CA-XXX (E-00X, fecha)` en el header del plan; asigna la numeración E-00X escaneando plan + changelog del spec). El plan conserva `Estado: VALIDADO`: solo se retienen las tasks que referencian el CA enmendado.
- Retención selectiva determinista: `sdd-gate-check.py` deniega `wf-task-run --task` sobre tasks retenidas y `wf-prepare-tasks` sobre planes con enmiendas abiertas; `sdd-task-state.py next` salta las retenidas (`RETENIDAS_POR_ENMIENDA` si no queda otra cosa), `check` las marca y `set EN_CURSO` las rechaza salvo `--force`. Cierre por revisión scoped (`sdd-amend.py clear`) o re-validación completa (`sdd-seal.py --seal` absorbe las anotaciones).
- `wf-task-run` integra la salida: el owner que detecta un CA ambiguo lo reporta sin elegir interpretación; bloqueo por ambigüedad → `BLOQUEADA` + remisión a `/wf-spec-amend` (ya no se re-desciende el waterfall por una aclaración). Semántica documentada como Regla 9 de `kb-traceability-rules`.
- ⚠ Proyectos ya inicializados: `/wf-sdd-update` para recibir `sdd-amend.py` en `.sdd/scripts/` y las versiones nuevas de `sdd-gate-check.py`/`sdd-task-state.py`/`sdd-seal.py` (sin actualizar, los gates antiguos siguen funcionando como hasta ahora; la retención selectiva simplemente no aplica).

## 0.5.0 — 2026-06-07

Modo CI/headless y política de git (ROADMAP 5.2 y 5.3):

- El hook de sesión se silencia por completo con `SDD_NON_INTERACTIVE=1` (opt-out explícito) o `CI=true` (estándar de runners): sin wizard, sin init, sin aviso de versión. El opt-out commiteable por repo sigue siendo `.claude/sdd-mode.json`. Documentado en el bloque global de protocolo.
- Política de git documentada y aplicada: se commitea TODO `.claude/` y `.sdd/` (el proyecto funciona para cualquier dev y en CI sin el ecosistema instalado); única excepción `.claude/settings.local.json`, que `wf-project-init` añade a `.gitignore` (check nuevo en su Paso 9) y la plantilla del CLAUDE.md raíz declara. Guía de onboarding (dev nuevo + CI) en el README del ecosistema, con la sección de instalación reescrita al modelo actual (setup.sh global + install por proyecto — describía el modelo antiguo de copiar a `~/.claude/`).
- ⚠ `wf-sdd-update` ahora asegura la línea de `.gitignore` al actualizar (Paso 5b): los proyectos pre-0.5.0 la reciben con el update.
- ⚠ Pendiente del usuario tras actualizar el ecosistema: `bash sdd/setup.sh --update` para sincronizar el hook y el bloque global de `~/.claude` (cambiados por 5.2).

## 0.4.0 — 2026-06-07

Perfil QA — cierre del ciclo "CAs testables" (ROADMAP 2.4):

- Piezas nuevas en la fase tasks: `kb-qa-expert` (SSoT de metodología QA: formato TC-XXX, derivación CA→TC, niveles, criterios de cobertura con evidencia, veredictos), agente `qa-engineer` y workflows `wf-qa-plan` (CAs → matriz de casos de prueba en `<feature>_qa_plan.md`) y `wf-qa-verify` (localiza y ejecuta los tests de cada TC, estados con evidencia, `<feature>_qa_report.md` con veredicto APTO/APTO_CON_RESERVAS/NO_APTO). Un test que falla contra un CA es DIVERGENTE → `/wf-bug`, nunca se ajusta el TC.
- `wf-qa-plan` entra en la tabla de gates deterministas (`sdd-gate-check.py`): mismo gate de spec fiable que `wf-prepare-plan`.
- ⚠ Corregido bug preexistente de los gates y el sellador: `status_sync: unknown` ya NO bloquea (es legítimo en specs sin PRD, fast-track directo — la deriva real la caza el hash de 1.3); bloquean solo `stale` y `needs_review`, conforme a `kb-traceability-rules` Regla 8.
- ⚠ La rule de tasks ahora también se activa con `*_bugs.md`, `*_qa_plan.md` y `*_qa_report.md` (el glob de `_bugs.md` faltaba desde 2.2). Requiere `/wf-sdd-update` para refrescar piezas y rules.

## 0.3.0 — 2026-06-07

Cierre verificable de implementadores, overlay a prueba de reinstalación y pins de modelo (ROADMAP 2.3, 6.6 y 9.10):

- Contrato de cierre verificable dentro de los agentes implementadores: nueva Regla 6 en `kb-kmm-project-state-protocol` (build + tests con los comandos del `kmm_project_state.md`, RED esperado en orden TDD, reporte honesto del comando y salida real, ausencia de verificación declarada explícitamente) y sección dura de cierre en `kmm-feature-implementer`, `kmm-network-auth-implementer`, `kmm-platform-integrator` y `kmm-tester`. Generalizado al contrato de overlay (`kb-sdd-stack-overlay-contract`, invariante 5 + checklist): los stacks futuros nacen con la obligación.
- ⚠ `install.sh` ya no degrada proyectos con overlay: si `.sdd/project-init.json` declara `stack`, re-aplica `tech/<stack>/install.sh` al final de instalar plan/tasks (las variantes del overlay sobreviven a la reinstalación manual); si el ecosistema no tiene ese overlay, avisa en vez de callar.
- Pins de modelo actualizados a `claude-opus-4-8` (canon de `kb-sdd-creation-guide` + 7 agentes); los 13 `claude-sonnet-4-6` se mantienen (versión Sonnet vigente, asignación por rol conforme al canon).

## 0.2.0 — 2026-06-07

Enforcement de sincronía PRD→spec y auto-allow acotado (ROADMAP 1.3 y 1.4):

- Detección determinista de deriva PRD→spec: `sdd-sync-check.py` (script de enforcement nuevo) sella `derived_from_prd_hash` (sha256 del PRD origen) en el header del spec; `seal` al generar/resincronizar, `check`/`check-all --mark` para detectar divergencia (degrada `status_sync` a `needs_review`). Único escritor del campo: el script (separación autor/verificador).
- ⚠ Los gates (`sdd-gate-check.py`) y el sellador de planes (`sdd-seal.py`) ahora verifican el hash: si el PRD cambió desde que se generó/sincronizó el spec, `wf-prepare-plan`/`wf-design-*` se deniegan y el plan no se sella hasta resincronizar (`/wf-prd-sync-impact` + `/wf-spec-sync-from-prd`). Los specs sin sello (legacy) no bloquean.
- Auto-allow de Skills acotado: el `Skill(.*)` universal del `settings.json` se sustituye por `sdd-skill-allow.py` (PermissionRequest), que solo auto-aprueba workflows SDD (`wf-*`); cualquier otra skill sigue el flujo normal de permisos. Los gates PreToolUse prevalecen sobre el allow.
- ⚠ Migración automática al actualizar: `merge-claude-settings.py` elimina del settings del proyecto la entrada antigua de auto-allow universal (identificada por su comando exacto; los hooks propios del equipo no se tocan) y añade la acotada. Hace falta re-ejecutar la instalación (`/wf-sdd-update`) para distribuir los scripts nuevos a `.sdd/scripts/`.

## 0.1.0 — 2026-06-07

Primera versión sellada. Estado consolidado tras las fases 0-3 del ROADMAP:

- Enforcement determinista: `sdd-seal.py` (sellado de planes, autor≠sellador), `sdd-gate-check.py` (gates PreToolUse), `sdd-task-state.py` (estados de tasks).
- Ciclo de vida completo: `wf-task-run` (ejecución con estado persistente y commits trazables) y `wf-bug` (fast-lane de mantenimiento con triaje contra CA).
- Onramp brownfield: `wf-spec-from-code` + `kb-spec-characterization` (specs de caracterización con evidencia obligatoria).
- ⚠ Los specs con CAs `[INFERIDO]` bloquean `wf-prepare-plan` y el sellado de planes (igual que `[INCOMPLETO]`).
- ⚠ Layout de feature por subcarpetas (`features/<n>/spec|design|plan|tasks/`); el layout plano anterior sigue siendo válido (los workflows leen ambos, no los mezclan).
- ⚠ Infraestructura única: un solo `.claude/` raíz con rules de carga perezosa por `paths:` (`.claude/rules/sdd-<fase>.md`); los layouts antiguos (`.claude/phases/`, `<fase>/.claude/`) siguen reconocidos por el hook.
- Mapa `artifacts` en `project-init.json` (ubicación de artefactos por fase).
- Versionado del ecosistema: `VERSION` + sello `.sdd/sdd-version.json` + `wf-sdd-update`.
