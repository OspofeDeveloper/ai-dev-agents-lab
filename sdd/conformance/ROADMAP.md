# ROADMAP de cobertura — batería de conformance vs. skills del ecosistema

Este documento es el **checklist de auditoría** de la batería de conformance (`casos-de-uso/cu-*.md`)
contra las **48 workflow skills `wf-*`** del core del ecosistema. La batería está organizada por
*journey* (CU), no por skill; aquí invertimos la vista: **una fila por `wf-*`**, en orden de pipeline,
para garantizar que ningún skill se queda sin casos en los cuatro ejes de prueba.

## Alcance

- **Solo `wf-*` del core** (48 skills). Agentes, scripts (`sdd-*.py`) y `kb-*` se anotan como cobertura
  *derivada* en la columna Mecanismo cuando un `wf-*` los ejercita; no tienen fila propia.
- **Overlay KMM diferido** a un track aparte (8 `wf-kmm-*` + kb anidadas). CU-12 ya lo cubre parcialmente.

## Leyenda

- **Ejes:** `✅` cubierto · `🟡` parcial · `❌` hueco · `—` no aplica.
  - **Happy** — invocación canónica con precondiciones satisfechas → artefacto correcto + sello.
  - **Edge** — args parciales/ausentes, layout legacy, subset, idempotencia, re-ejecución, monorepo.
  - **Harness** — invocar saltándose una precondición o gate → debe **bloquear** (`[SDD-GATE]`, veredicto no-`LISTO`, parada por gap crítico).
  - **Args OK** — un escenario verifica que el orquestador traduce el lenguaje natural a los **args correctos** del skill (y que **no** inyecta overrides peligrosos sin petición explícita).
- **Estado:** `PENDIENTE` (sin revisar) · `REVISADO` (cruzado, sin huecos) · `CON-HUECOS` (faltan escenarios) · `COMPLETADO` (huecos rellenados).

## Progreso

**Revisadas: 48 / 48** ✅ · Completadas: 48 · Revisadas sin huecos: 0 · Con huecos: 0 · Pendientes: 0

> **Auditoría completa.** Todas las fases del core revisadas: bootstrap (2) · prd (4) · spec (13) ·
> design (14) · plan (2) · tasks (7) · meta (6). Las skills meta entran en la batería vía
> [`cu-17-meta.md`](casos-de-uso/cu-17-meta.md) + routing en `CU-13.h`.
>
> **Track diferido pendiente:** overlay KMM (8 `wf-kmm-*` + kb anidadas) — auditarlo aparte si se decide
> ampliar el alcance. CU-12 lo cubre parcialmente.

> Eje **Args OK** transversal: el contrato de paso de args lo cubren CU-11.b (construcción
> de flags/modos/paths), CU-11.f (overrides peligrosos no auto-inyectados), CU-11.g (input
> oral vs argumento de fichero) y CU-11.h (selección/multivalor). Aplican a todas las fases.

---

## Fase bootstrap (2)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-project-init | `--topology <a\|c\|s\|design>` `--surfaces <…>` `--design-targets <…>` `--prd` `--design` `--stack` `--name` `--sdd-path` `--force` | orquestador en hilo principal (`AskUserQuestion`, sin fork); `sdd-init-detect.py` (detect/verify/target-platforms); `install.sh --no-claude-md`; hook SessionStart; `sdd-version.json` | CU-1.b/d/e/h/i/j/k/l/m/n/o/p/q/r/t/u · CU-10.d | ✅ | ✅ | ✅ | ✅ | COMPLETADO | Flags y enum inválido cubiertos por CU-1.p (incl. `--topology design` + `--design-targets`, D-011); topología `design` y consumer con repo de diseño en CU-1.q / CU-1.i caso 4; guard de doble SSoT de diseño (D-012, CU-1.i caso 5); aviso advisory de SSoT productor sin git (CU-1.r, `is_git_repo`); regla **eager** `sdd-orchestration.md` (D-021, disciplina de orquestación transversal, generada sin `paths:` por `install_orchestration_rule`) — instalación en CU-1.t, carga y aplicación al orientar en CU-14.j; regla **eager** `sdd-routing.md` (D-022, desambiguación por-fase topology-gated, `install_routing_rule`) — instalación on-disk en CU-1.u (backstop `test_routing_rule_*`), enrutado por descriptions + desambiguación eager en CU-11.a sub-caso 1; entrevista interactiva validada a mano (los escenarios hook-only a/c/f/g son cobertura del hook de sesión, sin fila propia) |
| wf-sdd-update | `--force` | `install.sh --prune` + overlay; `CHANGELOG.md`; `sdd-version.json` | CU-1.f · CU-10.a/b/i/j/k | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |

---

## Fase prd (4)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-prd-create | `<dir_proyecto>` `[--source <notas.md>]` `[--output <prd.md>]` | prd-expert; grep `[ASUNCIÓN]`; Regla 12 | CU-2.a/b/c/d/i · CU-13.a · CU-11.b/g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | `--output` a ruta custom cubierto por **CU-2.i** (gate [[D-025]], sellada 2026-07-15); `--source`/oral por CU-11.b/g |
| wf-prd-review | `<prd.md>` | prd-expert (delegación **síncrona**, `run_in_background: false`, [[D-043]]); `sdd-prd-ready.py` (1:1 + veredicto), `sdd-prd-deps.py` (grafo + backstop `--check`), `sdd-prd-apply.py` (`--confirm/--edit/--reject/--seal/--reopen`), `sdd-prd-frontmatter.py` | CU-2.e/f/g/h/j · CU-13.a | ✅ | ✅ | ✅ | — | COMPLETADO | Arg único posicional. Bloque cerrado 2026-07-30: gate de asunciones y no-autoaprobación (2.e/2.f), enrutado por tipo de artefacto (2.g), no-reescritura byte-idéntica (2.h) y cascada determinista de dependencias (2.j: orden del backstop, 3 desenlaces, consecuencia en el momento, ámbito de edición) |
| wf-prd-change | `<prd.md> --new-reqs <cambio.md\|texto> [--defer-decisions]` | **hilo principal** + gate (`AskUserQuestion`); prd-expert (analiza read-only, escribe por delegación; **síncrona**, [[D-043]]); kb-product-change-governance; `sdd-prd-apply.py --reopen`; `changes/CR-XXX/` | CU-7.a/b/c/**n** · CU-13.a · CU-11.g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | Re-arquitecturada por [[D-040]]: gate obligatorio de clasificación + bifurcaciones (**CU-7.n**, nueva) y modo `--defer-decisions` para la cascada. `--new-reqs` admite texto inline → **CU-11.g obsoleto** en su ejemplo canónico de "exige fichero". Precondición de fichero inexistente sin caso propio (patrón ya en CU-2.c) |
| wf-prd-change-cascade | `<prd.md> [--new-reqs] [--features F-…] [--review-before-apply] [--skip-design] [--dry-run]` | orquestador cascade (sin agente); invoca change→sync-impact→spec-sync→conflict/readiness→design-sync | CU-7.f/g/h/i/j/k · CU-13.a · CU-11.f | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |

---

## Fase spec (13)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-spec-analyze | `<archivo.md>` | sdd-spec-explorer; kb-spec-expert; kb-gap-conventions; `sdd-analysis-gaps.py` (`--check`) | CU-3.a/k · CU-13.b · CU-11.f | ✅ | 🟡 | ✅ | ✅ | COMPLETADO | regenerar `_analysis.md` (confirm Paso 7) sin caso (patrón en CU-2.d) |
| wf-spec-discover | `<prd.md> [--analysis <analysis.md>] [--allow-derived-scope-from-analysis]` | sdd-spec-explorer; kb-decompose-expert | CU-3.c/i · CU-13.b | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | `--allow-derived...` cubierto vía CU-11.f; inferencia de RFs sin caso (mecánico) |
| wf-spec-features-first | `<prd.md> [--light\|--standard] [--features F-…\|--all-features] [--allow-open-critical-gaps] [--allow-derived-scope-from-analysis] [--skip-conflict] [--skip-readiness]` | orquestador **en el hilo principal** (sin `context: fork`, [[D-045]]): sostiene sus 4 gates con `AskUserQuestion` sin relanzarse, y delega 5 veces por `Agent` con `run_in_background: false` recibiendo el informe en la propia llamada ([[D-043]]); el delegado ejecuta la sub-skill, no la re-despacha ([[D-044]]); `sdd-features-index.py`; `sdd-analysis-gaps.py --check` (gate de gaps, [[D-042]]) | CU-3.a/b/c/d/l/r · CU-13.b/g · CU-11.f | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-spec-fast-track | `<archivo.md> --capability <n> \| --scope-from <discovery.md> --feature <F-00X> [--light\|--standard] [--analysis] [--allow-derived-scope-from-analysis]` | sdd-spec-writer; `sdd-next-id.py`/`sdd-sync-check.py seal` | CU-3.e/j/r · CU-13.b | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-spec-from-code | `discover <path> [--scope] \| generate <path> --feature <F-C-00X> \| generate <path> --capability <n> --scope <subdir>` | sdd-spec-writer; kb-spec-characterization | CU-4.a/b/c/d · CU-13.b/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | modo directo `--capability --scope` (sin discovery) sin caso propio |
| wf-spec-validate | `<spec.md>` | sdd-spec-auditor; kb-spec-expert (read-only `[Read,Bash]`) | CU-3.f/m · CU-13.b/g | ✅ | ✅ | ✅ | — | COMPLETADO | no-reescritura garantizada por allowed-tools sin Write |
| wf-spec-conflict | `<feature_spec.md> --features-dir <path/features/>` | sdd-spec-auditor; kb-conflict-expert | CU-3.f/n · CU-13.b | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | `.` sobre directorio (todos los specs) sin caso propio |
| wf-spec-readiness | `<path/features/>` | sdd-spec-auditor; kb-gap-conventions; `sdd-features-index.py` | CU-3.f/o · CU-13.b/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | — |
| wf-spec-delta | `analyze <spec.md> --new-reqs <desc.md> \| apply <spec.md> <delta_analysis.md>` | sdd-spec-writer; kb-spec-expert; `sdd-features-index.py` | CU-3.h/p · CU-13.b/g · CU-15.d | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-spec-gap-resolve | `<feature_spec.md> [--analysis <path>]` | sdd-spec-writer; kb-spec-characterization; `sdd-analysis-gaps.py --check` | CU-3.g/p/q · CU-4.c · CU-13.b/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | — |
| wf-spec-amend | `<feature_spec.md> --ca CA-XXX [--from-task T-00X] [--reason 'texto']` | sdd-spec-writer; `sdd-amend.py` | CU-8.d/e · CU-13.b/g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-spec-sync-from-prd | `analyze <prd.md> \| apply <prd.md> --features F-…` | sdd-spec-writer; `sdd-sync-check.py` | CU-7.l/m · CU-13.b · CU-15.a | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-prd-sync-impact | `<prd.md>` | sdd-spec-auditor; `sdd-sync-check.py`; `derived_from_prd_hash` | CU-7.d/e · CU-13.b · CU-15.a | ✅ | ✅ | ✅ | — | COMPLETADO | arg único posicional |

---

## Fase design (14)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-design-intake | `generate <feature_spec.md> [--prd] [--output] [--mode guided\|hybrid\|auto] [--preset <name>] [--learn]` | design-system-architect; kb-design-brief/-style-decision-tree; `sdd-init-detect.py target-platforms` (D-011) | CU-5.a/m · CU-13.c | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | `--learn`/`--preset` vía CU-11.b; `target_platforms` (familias) desde `design_targets` (D-011, CU-5.a.3) |
| wf-design-discover | `<feature_spec.md> [--prd] [--brief] [--output] [--mode interactive\|auto]` | orquestador (sin agente); WebSearch/WebFetch | CU-5.g · CU-13.c | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | modo `auto` (sin validación) vía variante de arg |
| wf-design-moodboard | `<feature_spec.md> [--prd] [--output] [--mode interactive\|auto]` | design-system-architect; kb-design-style-taxonomy/-decision-tree | CU-5.f · CU-13.c/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | alimenta intake, no cierra brief |
| wf-design-system | `generate <feature_spec.md> [--prd] [--brief] [--design-file] [--no-brief]` | design-system-architect; kb-design-system-contract (incl. Regla 11 `## Platform Components`, D-011); `sdd-init-detect.py target-platforms` (gate Paso 3b); linter `@google/design.md` | CU-5.b/k/l · CU-13.c/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | autoría de `## Platform Components` con design targets divergentes (D-011, CU-5.b casos 2-3); gate determinista `requires_platform_components` (Paso 3b → `NATIVE_PLATFORMS`), `PlatformComponentsGateTest` |
| wf-design-validate | `<DESIGN.md> [--brief] [--views] [--lenient] [--pedagogical]` | design-system-architect; linter `@google/design.md`; kb-design-governance R5; kb-design-system-contract R11 + `sdd-init-detect.py target-platforms` (gate Paso 4b, D-011) | CU-5.e/o · CU-13.c/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | promoción provisional→confirmed = única escritura (gated); gate `DESIGN_GAP` por `## Platform Components` ausente con targets divergentes (D-011, CU-5.e caso 6, check 19 del checklist) |
| wf-design-delta | `analyze <DESIGN.md> --new-reqs <cambios.md> [--brief] \| apply <DESIGN.md> <delta.md>` | design-system-architect; kb-design-expert R15 | CU-5.e/p · CU-13.c/g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-design-sync | `<DESIGN.md>` | design-system-architect; kb-design-governance R2 (read-only); `sdd-source-drift.py` (D-011, cross-repo) | CU-5.e/r/x · CU-13.c | ✅ | ✅ | ✅ | — | COMPLETADO | arg único posicional; deriva intra-repo por razonamiento (hash futuro, ROADMAP 11.2); drift cross-repo determinista por pin git (D-011, CU-5.x) |
| wf-design-feature-prototype | `generate <feature_spec.md> [--design-file] [--brief] [--no-brief]` | design-feature-architect; kb-design-feature-artifacts/-conflict-expert; `sdd-resolve-path.py`; `sdd-design-resolve.py` (D-011) | CU-5.c/k/n/w · CU-13.c | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | base⊕override per-view por design target (D-011, CU-5.w); resolución `sdd-design-resolve.py` |
| wf-design-extract | `discover <path_ui> [--scope] \| generate <path_ui> [--from <extraction.md>] [--scope] [--design-file]` | design-system-architect; kb-design-characterization; linter `@google/design.md` | CU-5.d · CU-13.c/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | gate discover→generate cubierto vía CU-5.d |
| wf-design-branch | `create <branch> \| list \| compare <a> <b> \| merge <branch> --into <target> \| discard <branch>` | design-system-architect; kb-design-governance R22 | CU-5.h/s · CU-13.c/g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-design-variant | `create <feature_spec.md> --variants A,B [--hypothesis] \| compare <feature_variants.md>` | design-feature-architect | CU-5.i/t · CU-13.c/g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-design-export | `<DESIGN.md> --platforms <css,style-dictionary,compose,swiftui,tailwind> [--output-dir] [--dry-run]` | sin agente (traduce fielmente); idempotente | CU-5.e/u · CU-13.c · CU-11.h | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-design-a11y-audit | `<DESIGN.md> [--views] [--brief] [--target AA\|AAA] [--lenient]` | design-system-architect; kb-a11y-expert/-web-expert | CU-5.e/q · CU-13.c | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | escribe `a11y_audit_<fecha>.md`; ramifica por plataforma |
| wf-design-feedback | `capture <feedback.md\|texto> [--source] [--feature] \| triage <feedback_capture.md>` | design-feature-architect (7 categorías de triage) | CU-5.j/v · CU-13.c · CU-11.g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |

---

## Fase plan (2)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-prepare-plan | `generate <spec.md>` | plan-architect; kb-plan-expert; `gate_spec_fiable`; `sdd-resolve-path.py`; `sdd-source-drift.py` (drift + `design_ssot`) + `sdd-design-resolve.py` (D-011/D-012, consumer) | CU-6.a/h/k · CU-9.e/f/g/h/i · CU-13.d | ✅ | ✅ | ✅ | — | COMPLETADO | arg único `generate <spec>`; stack KMM solapa con CU-12; consumer con `design_source` resuelve el handoff del repo de diseño en solo lectura + drift cross-repo (D-011, CU-6.k.5); aviso de doble SSoT de diseño (D-012, CU-6.k.6) |
| wf-plan-validate | `<plan.md>` | plan-auditor; `sdd-seal.py` (autor≠sellador) | CU-6.b/i/l · CU-13.d | ✅ | ✅ | ✅ | — | COMPLETADO | gate de plan validado que consume tasks: CU-9.a–d |

---

## Fase tasks (7)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-prepare-tasks | `generate <plan.md>` | task-generator; kb-tasks-expert; gate plan validado | CU-6.c/n · CU-9.a/b/c/d · CU-13.d | ✅ | ✅ | ✅ | — | COMPLETADO | resolución de stack = espejo de CU-6.k |
| wf-task-run | `<feature_tasks.md> [--task T-00X \| --next \| --all] [--no-commit]` | Owner agent (delegación **síncrona**, `run_in_background: false`, [[D-043]]: se valida el DoD y se commitea sobre su reporte); `sdd-task-state.py`; `sdd-gate-check.py`; commit | CU-6.d/j/m/n · CU-9.j/k · CU-15.f · CU-13.d | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-qa-plan | `generate <feature_spec.md>` | qa-engineer; kb-qa-expert; `gate_spec_fiable` | CU-6.e/o · CU-9.e–i · CU-14.f · CU-13.d | ✅ | ✅ | ✅ | — | COMPLETADO | — |
| wf-qa-verify | `<feature_qa_plan.md>` | qa-engineer; evidencia ejecutada; único escritor de `Estado` TC | CU-6.f/o · CU-14.f · CU-13.d | ✅ | ✅ | ✅ | — | COMPLETADO | — |
| wf-release | `<feature_dir\|tasks_path> [--tag <tag>] [--no-tag] [--note <texto>]` | `sdd-release.py` (sin agente); gate QA APTO; git SHA | CU-6.g · CU-14.g · CU-13.d · CU-11.f | ✅ | ✅ | ✅ | ✅ | COMPLETADO | `APTO_CON_RESERVAS` se graba con reservas; re-releases R-00X |
| wf-bug | `<descripcion.md\|texto> [--feature <nombre>]` | Owner (triaje contra CA; fix por delegación **síncrona**, [[D-043]]); `sdd-next-id.py` | CU-8.a/b/c/f · CU-13.d/g · CU-11.g | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-project-status | `[<raíz_artefactos_spec>] [--output <path>]` | `sdd-project-status.py` (sin agente, read-only) | CU-10.f · CU-13.d/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | agrega lo sellado; no razona ni edita |

---

## Fase meta (6)

| Skill | Args | Mecanismo (agente/script/hook) | CU que lo ejercitan | Happy | Edge | Harness | Args OK | Estado | Huecos detectados |
|---|---|---|---|---|---|---|---|---|---|
| wf-skill-create | `<kb\|wf> <nombre> --phase <fase\|global> [--description] [--agent] [--effort] [--force]` | sdd-author; `sdd-scaffold.py`; `sdd-structural-lint.py` (gate) | CU-17.a · CU-13.h | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-agent-create | `<nombre> --phase <fase\|global> --skills <kb…> [--description] [--model] [--effort high] [--read-only]` | sdd-author; `sdd-scaffold.py`; `sdd-structural-lint.py` | CU-17.b · CU-13.h | ✅ | ✅ | ✅ | ✅ | COMPLETADO | no regenera registry (solo indexa skills) |
| wf-stack-create | `<stack> [--type <app\|web\|backend>] [--detect '<cond>'] [--with-agents] [--description]` | sdd-author; kb-sdd-stack-overlay-contract; `sdd-structural-lint.py` | CU-17.c · CU-13.h | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-sdd-audit | `<structural\|content\|full> [--phase <fase\|global>]` | sdd-auditor; `sdd-structural-lint.py`; kb-sdd-audit-structural/-content | CU-17.d · CU-13.h | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-sdd-refactor | `<path-skill-o-agente> [--reason <motivo>]` | sdd-author; `sdd-structural-lint.py` (siempre) | CU-17.e · CU-13.h | ✅ | ✅ | ✅ | ✅ | COMPLETADO | — |
| wf-sdd-status | `[--phase <fase\|global>] [--output <path>]` | sin agente (mecánico); `generate-skill-registry.py` | CU-17.f · CU-13.h/g | ✅ | ✅ | ✅ | 🟡 | COMPLETADO | read-mostly; SIN CONSUMIDOR / SIN REGISTRAR |

---

## Track diferido — overlay KMM

8 `wf-kmm-*` (init, network-setup, auth-setup-keycloak, database-setup, datastore-setup, environments,
testing-setup, stack-setup-ktor-keycloak-koin) + kb anidadas. **Fuera de esta tanda.** CU-12 cubre
parcialmente el init y el scaffolding del overlay.
