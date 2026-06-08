# Changelog del ecosistema SDD

Formato: `## <versión> — <fecha>`. Las líneas con `⚠` son cambios que afectan a proyectos ya inicializados (`wf-sdd-update` las muestra al actualizar).

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
