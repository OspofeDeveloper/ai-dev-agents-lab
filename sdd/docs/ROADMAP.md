# ROADMAP — Guía unificada de mejoras del ecosistema SDD

**Creado:** 2026-06-05
**Fuentes consolidadas (ya eliminadas tras la consolidación):** auditoría profunda 2026-06-05 (5 ejes: pipeline core, design, meta/instalación, tech, adopción) + `IMPROVEMENTS.md` (mejoras gentle-ai y backlog A/B/C) + `GENTLE_AI_COMPARISON.md` (persistencia/memoria) + `audit_full_global.md` (audit 2026-05-31, estado re-verificado a fecha de hoy).

**Cómo usar este documento:** es la SSoT única del trabajo pendiente sobre el ecosistema. Cada ítem tiene checkbox, severidad y evidencia. Al completar un ítem: marcar `[x]`, anotar fecha y commit. Cuando una sección quede completa, moverla a "Completado" al final.

**Leyenda severidad:** 🔴 crítico · 🟠 alto · 🟡 medio · 🟢 bajo

---

## FASE 0 — Bugs concretos (arreglables ya, días no semanas)

Errores reproducibles, no decisiones de diseño. Orden sugerido de ejecución inmediata.

- [x] 🔴 **0.1 — `tech/kmm/install.sh` no copia `kb-kmm-project-state-protocol`.** La KB vive en la raíz de `skills/` y los bucles solo iteran `plan`, `tasks` y `wf-*`. Es precondición dura de 6 agentes ("si `kmm_project_state.md` no existe… detente"): el stack llega roto de fábrica. → Añadir la raíz de `skills/` (o la KB explícita) al installer. ✅ *2026-06-05: añadido bucle `kb-*/` de raíz en `tech/kmm/install.sh`; verificado con instalación real en tmpdir (42 skills, KB desplegada, 6 agentes consumidores OK).*
- [x] 🔴 **0.2 — Variante `optimized` de `kmm/install.sh` rota.** Referencia `agents_optimized/`, `skills_optimized/`, `CLAUDE_optimized.md` — ninguno existe; con `set -e` peta a medias dejando el proyecto inconsistente (`tech/kmm/install.sh:20-22`). → Eliminar la variante o crear los directorios. ✅ *2026-06-05: variante eliminada por completo (case, SKILL_VARIANT y uso); el script ya no acepta argumento. Verificado: ningún invocador la pasaba; instalación en tmpdir OK (42 skills, 9 agentes).*
- [x] 🟠 **0.3 — `install.sh` sobreescribe `.claude/settings.json` del proyecto sin merge** (`install.sh:213`), y `tech/kmm/install.sh:90` lo vuelve a pisar. Destruye permisos/hooks propios del equipo. `setup.sh:52-77` ya tiene un merge idempotente con python3 para el global — replicar ese patrón a nivel proyecto. ✅ *2026-06-05: creado helper compartido `sdd/scripts/merge-claude-settings.py` (SSoT del merge: añade matchers ausentes por evento, preserva todo lo del proyecto, idempotente) usado por ambos installers; fallback seguro sin python3 (no modifica, avisa). Verificado: 3 escenarios (sin settings previo, settings del equipo preservados, re-run + overlay KMM sin duplicados).*
- [ ] 🟠 **0.4 — `wf-design-validate`: flag `--strict` inyectado al agente nunca se parsea.** El frontmatter declara `--lenient`/`--pedagogical` pero el prompt del Paso (línea ~76) inyecta `Flag --strict: <true|false>` que el Paso 1 no llena. Además semántica invertida respecto a `wf-design-a11y-audit` (`--lenient` opt-out vs `--strict` opt-in). → Unificar semántica de severidad entre ambos y corregir el prompt.
- [ ] 🟠 **0.5 — `skill-registry.md` desincronizado y sin mecanismo de regeneración.** Header con totales/fecha obsoletos (`meta/skill-registry.md:3-4`); nada lo regenera al crear/borrar skills. → Mínimo: que `wf-skill-create`/`wf-agent-create`/`wf-stack-create` regeneren el registry al cerrar (o invoquen el paso de `wf-sdd-status`). Definir autoridad única de regeneración (hoy `wf-sdd-status` y `wf-sdd-audit` solapan).
- [ ] 🟡 **0.6 — Parseo frágil de `project-init.json` en el hook.** `bootstrap/sdd-session-check.sh:31` extrae `phases` con `grep -o` + glob de substring; un reformateo manual da falsos `init-incomplete` (muy intrusivo: relanza `wf-project-init` cada sesión). → Parsear con python3 (con fallback) o endurecer el matching.
- [ ] 🟡 **0.7 — El hook no excluye el repo contenedor del ecosistema.** Solo excluye `$SDD_HOME` (= `…/ai-dev-agents-lab/sdd`); abrir sesión en `ai-dev-agents-lab/` dispara el wizard (ocurrió el 2026-06-05). → Excluir también el repo git que contiene `$SDD_HOME` (p. ej. `git -C "$SDD_HOME" rev-parse --show-toplevel`).
- [ ] 🟡 **0.8 — Reinstalar con menos fases deja skills huérfanas invocables.** `install.sh:126` hace `rm -rf`+`cp` solo de lo que instala; nunca limpia lo que ya no aplica. → Modo de reconciliación: eliminar skills/agents de fases no seleccionadas (con confirmación).
- [ ] 🟡 **0.9 — `setup.sh` depende de `python3` sin verificar** (`setup.sh:52`); en macOS sin python3 falla a mitad dejando el bootstrap inconsistente (hook copiado pero sin registrar). → `command -v python3` + fallback o mensaje claro y rollback del paso.
- [ ] 🟢 **0.10 — `sdd/.claude/settings.local.json` trackeado en git con paths personales.** El `.gitignore` raíz ignora `sdd/.claude/` pero el fichero quedó dentro. → `git rm --cached` + reforzar gitignore.

---

## FASE 1 — Enforcement mecánico (el riesgo central del sistema)

Hoy todo el rigor es prosa que el modelo debe obedecer; los gates son auto-aprobables. Convertir lo "obligatorio" en verificable.

- [ ] 🔴 **1.1 — Hooks `PreToolUse` para gates de fase.** Bloquear mecánicamente: `wf-prepare-tasks` sin `_plan.md` con `Estado: VALIDADO` (grep determinista), `wf-prepare-plan` sin spec en `status_sync: in_sync`, `wf-design-feature-prototype` sin spec validado. Los `!test -f` actuales solo verifican existencia, nunca contenido.
- [ ] 🔴 **1.2 — Separar autor de auditor en los sellados.** `wf-plan-validate` = el agente emite "OK" en prosa y el orquestador hace find-replace `BORRADOR→VALIDADO`. Mínimo: que el sellado lo haga un script determinista que verifique condiciones comprobables (CAs del spec presentes en el plan por ID, cero `[INCOMPLETO]`), no el mismo flujo que generó el artefacto.
- [ ] 🟠 **1.3 — Detección automática de deriva PRD→spec.** `status_sync` es manual y miente en silencio si alguien edita el PRD fuera de `wf-prd-change`. → Sellar hash/mtime del PRD origen en la metadata del spec (`derived_from_prd_version` ya existe — hacerlo verificable) y un check barato que marque `stale` al detectar divergencia (puede ir en el hook SessionStart o en los gates).
- [ ] 🟠 **1.4 — Revisar el auto-allow universal de Skills.** `settings.json` aprueba `Skill(.*)`: elimina toda fricción incluso para saltarse fases. → Evaluar lista explícita o combinarlo con los hooks de 1.1 (el gate compensa el auto-allow).
- [ ] 🟡 **1.5 — KB Load Status verificable.** El "KB Load Status" es auto-reportado por el propio agente. → Que el orquestador verifique la existencia de las KBs declaradas antes de delegar (check determinista), dejando el auto-reporte solo como señal secundaria.
- [ ] 🟡 **1.6 — Red anti-fabricación en el origen (PRD).** `wf-prd-create` sin `--source` puede inventar actores/alcance desde un brief pobre y `wf-prd-review` solo valida estructura. → Exigir que cada afirmación de negocio trace a la fuente o quede marcada `[ASUNCIÓN]` con confirmación humana explícita en el review.

---

## FASE 2 — Ciclo de vida completo (de "documentador" a "entregador")

El pipeline hoy termina en `_tasks.md` y solo conoce "feature nueva". Más del 50% del trabajo real de una empresa queda fuera.

- [ ] 🔴 **2.1 — `wf-task-run` — ejecución de tasks con estado persistente** en `_tasks.md`, validación de DoD por task y commits trazables (`T-00X`, `CA-XXX`). Cierra el ciclo spec→plan→tasks→implementación. *(= B1 de IMPROVEMENTS)*
- [ ] 🔴 **2.2 — `wf-bug` / fast-lane de mantenimiento.** Un bug es divergencia entre spec y código, no un cambio de spec: flujo ligero que (a) localiza el CA violado, (b) registra el fix con trazabilidad, (c) solo escala a `wf-spec-delta` si el comportamiento esperado cambia. Sin esto el equipo abandona el pipeline al primer sprint de mantenimiento y los artefactos se vuelven mentira documental.
- [ ] 🟠 **2.3 — Verificación ejecutable en agentes implementadores.** `kmm-feature-implementer`, `kmm-network-auth-implementer`, `kmm-platform-integrator` no compilan ni corren tests (grep de `gradle|build|run test`: solo el DoD textual del RED). → Instrucción dura de cierre: build verde + suite pasando usando los comandos del `kmm_project_state.md`, con reporte honesto si falla. Generalizar al contrato de overlay.
- [ ] 🟠 **2.4 — Perfil QA (`wf-qa-plan` + `wf-qa-verify`)** — trazabilidad CA → caso de prueba y verificación de cobertura de CAs tras implementar. La promesa "CAs testables GIVEN/WHEN/THEN" hoy no se cierra nunca. *(= B3 de IMPROVEMENTS)*
- [ ] 🟡 **2.5 — Work Unit Commits + Chained PRs** (kb de criterio de tamaño de commit, tests junto al código, división de PRs). *(= IMPROVEMENTS #4, generalizar más allá de KMM si es viable)*
- [ ] 🟡 **2.6 — `wf-project-status` — informe PM read-only**: features por estado del pipeline, bloqueos, siguiente acción. *(= B2 de IMPROVEMENTS)*
- [ ] 🟢 **2.7 — Noción mínima de release**: vincular el cierre de una feature a tag/SHA para que la trazabilidad llegue a producción.

---

## FASE 3 — Legacy / brownfield (la puerta al trabajo real de empresa)

Hoy el único onramp es PRD greenfield. La mayoría del software de una empresa ya existe.

- [ ] 🔴 **3.1 — `wf-spec-from-code` — ingeniería inversa de specs.** Generar specs de caracterización ("esto es lo que el sistema hace hoy, verificado contra el código") como entrada alternativa al pipeline, con HUs/CAs derivados de comportamiento observable y marcados como `characterization` (no intención de negocio). Es el prerequisito de toda adopción brownfield.
- [ ] 🟠 **3.2 — Registro de deuda técnica en el plan.** El `plan-architect` ante incertidumbre solo puede emitir gap y detenerse. → Sección de deuda/restricciones en `_plan.md` ("lo hacemos así a pesar de X, queda pendiente Y") para que el pipeline no se bloquee ni pierda la información en legacy.
- [ ] 🟡 **3.3 — Guía para stacks sin tooling moderno.** El contrato de overlay exige "comandos build/test"; un PHP 5 sin tests no encaja. → Degradación documentada: project_state con `tests: none`, estrategia de characterization tests primero, criterios de plan para monolitos sin módulos.
- [ ] 🟡 **3.4 — `wf-design-extract` — ingeniería inversa de UI existente.** `wf-design-system` solo sabe "leer DESIGN.md" o "crear desde cero"; falta derivar el `DESIGN.md` de la UI ya en producción (CSS/capturas/componentes) para proyectos que no se van a rediseñar.

---

## FASE 4 — Scrum cambiante: coste de sincronización y modo ligero

El camino feliz son ~13 invocaciones + 4-5 checkpoints humanos por feature. En sprints de 2 semanas, el overhead mata la adopción.

- [ ] 🟠 **4.1 — Modo ligero declarado del pipeline.** Camino spec→plan→tasks con discovery/moodboard/design opcionales por feature, para features pequeñas y proyectos sin UI. Hoy hasta el `fast-track` exige los 8 elementos y ≥3 CAs. Definir explícitamente qué gates son irrenunciables y cuáles son proporcionales al tamaño de la feature.
- [ ] 🟠 **4.2 — Back-edge tasks→spec.** Cuando el dev descubre implementando que un CA es ambiguo, hoy el coste es re-descender 4 fases. → Flujo corto de "enmienda desde implementación": corrige el CA, marca los artefactos intermedios afectados como stale puntual, sin re-correr todo el waterfall.
- [ ] 🟡 **4.3 — `wf-design-sync` o equivalente.** Tras un cambio de spec/`DESIGN.md`, nada detecta qué `_views.md`/tokens quedaron stale (el "considerar regenerar" de `wf-design-delta` es manual). Réplica del patrón `wf-prd-sync-impact` para la fase design.
- [ ] 🟡 **4.4 — Compactar la cadena de re-sync.** Un cambio de producto dispara ~9 workflows encadenados a mano. → Orquestar la cadena completa con un solo comando (`wf-prd-change --cascade`) que pare solo en los checkpoints humanos reales.

---

## FASE 5 — Multi-desarrollador, distribución y CI

Diseñado hoy para un operador omnisciente en una máquina. Una empresa son N devs, N repos, CI.

- [ ] 🔴 **5.1 — Versionado del ecosistema + update no destructivo.** No existe `VERSION` en ninguna parte y `wf-project-init` prohíbe sellar versión. → `VERSION`/commit sellado como `sdd_version` en `project-init.json` + `wf-project-update` que reinstale fases respetando overlays, sin re-entrevistar. *(= C1 de IMPROVEMENTS)*
- [ ] 🟠 **5.2 — Modo CI/headless.** Todo el arranque depende de `AskUserQuestion` bloqueante. → Variable de entorno o flag (`SDD_NON_INTERACTIVE=1`) que suprima el protocolo de sesión, y documentar `.claude/sdd-mode.json` commiteado como opt-out válido para runners.
- [ ] 🟠 **5.3 — Política documentada de qué se commitea.** Qué va a git de `.claude/` y `.sdd/` (artefactos sí, skills copiadas ¿sí/no?, `settings.local.json` nunca), plantilla de `.gitignore` que `wf-project-init` deje en el proyecto, y guía de onboarding del dev nuevo (clonar ecosistema + `setup.sh` + `~/.sdd-home`).
- [ ] 🟠 **5.4 — Estrategia de concurrencia para artefactos hub.** `_features.md` y `stack_workflows_run[]` garantizan conflicto de merge con 2 devs en paralelo. → Formato append-only o por-feature (un fichero por feature en vez de hub monolítico) + guía "una feature por rama".
- [ ] 🟡 **5.5 — Roles y aprobaciones diferenciadas.** Todos los checkpoints son "el humano valida" (singular). → Mínimo viable: campo `approved_by: <rol>` en los sellados (PM en PRD, tech lead en plan, QA en verify) para que la autoría de cada gate quede trazada.
- [ ] 🟡 **5.6 — Opt-out/desinstalación del bootstrap global.** No existe `setup.sh --uninstall`; el hook dispara el wizard en todos los proyectos del dev. → Uninstall limpio + allowlist/denylist de rutas en el hook.
- [ ] 🟡 **5.7 — Soporte de monorepo en el hook y el init.** Abrir en raíz vs subpaquete da estados SDD distintos. Relacionado con A3 (multi-stack); como mínimo, que el hook busque `.sdd/` hacia arriba hasta la raíz git.
- [ ] 🟢 **5.8 — Multi-perfil acumulado** — `profiles: [...]` en `project-init.json` (hoy solo guarda el último). *(= C2 de IMPROVEMENTS)*

---

## FASE 6 — Multi-stack real

Solo existe KMM; los overlays son mutuamente excluyentes por diseño; el proyecto políglota (backend+front+móvil) no está soportado.

- [ ] 🟠 **6.1 — Resolver la exclusividad mutua de overlays.** El override por `basename` (`plan-architect.md`…) hace imposible dos stacks en un repo. → Diseñar resolución por ruta/módulo (`stacks: [{path, stack}]` en `project-init.json`, gates resolviendo stack por ubicación de la feature). *(= A3 de IMPROVEMENTS — esperar a 2-3 overlays reales, pero diseñar el contrato ya para no cavar más hondo)*
- [ ] 🟠 **6.2 — Extraer el núcleo metodológico compartido de los agentes override.** El cuerpo de `plan-architect`/`plan-auditor`/`task-generator` está copiado a mano entre genérico y KMM; con 5 stacks, cada cambio metodológico = 6 ediciones manuales. → Mover el contrato común a una KB compartida que ambas variantes carguen.
- [ ] 🟡 **6.3 — Adaptación al repo destino en los implementadores.** La variante KMM de `plan-architect` eliminó la instrucción genérica "fundamenta toda decisión en la exploración real del repo" y la sustituyó por dogma KMM (Koin, AppResult…). Un repo KMM real con otras convenciones recibirá imposiciones. → Restaurar la regla de "el repo manda sobre el dogma" en todos los overlays.
- [ ] 🟡 **6.4 — Completar huecos del propio stack KMM** (de `tech/kmm/BACKLOG.md`): `kb-kmm-gradle-modules`, persistencia (Room), `kb-kmm-offline-strategy`, `kb-kmm-secrets-cicd`.
- [ ] 🟢 **6.5 — Primer overlay adicional con `wf-stack-create`** (orden sugerido: `android`, `flutter`, `ios`, `next`, `fastapi`/`ktor`) — servirá además de test real del contrato de overlay y de 6.1/6.2.

---

## FASE 7 — Fase Design: declarar el fit y cerrar grietas

Su encaje natural hoy es greenfield mobile sin diseñador con Stitch como destino — pero no está declarado, y genera falsas expectativas.

- [ ] 🟠 **7.1 — Declarar el fit explícitamente** en `design/README.md` y `design/CLAUDE.md`: para quién es (equipos sin diseñador / greenfield), qué no cubre (integración Figma, reverse de UI existente), y que es saltable por feature sin UI (hoy esa señal solo vive en `plan/`; propagarla a `sdd/CLAUDE.md` y a la propia fase).
- [ ] 🟡 **7.2 — Anclar la dirección visual cuando no hay brief.** Con `--no-brief` + research pobre, `style_family`/paleta/motion son invención plausible con formato de autoridad. → Exigir confirmación humana explícita de la dirección visual en modo `auto`, o marcar el `DESIGN.md` resultante como `provisional` hasta validación.
- [ ] 🟡 **7.3 — Variante web de a11y y prototipado no-Stitch** (WCAG completo, targets no-táctiles). *(= B4 de IMPROVEMENTS)*
- [ ] 🟡 **7.4 — Resolver solapamiento `kb-design-style-decision-tree` vs `kb-design-style-taxonomy`.** El árbol re-deriva los mismos criterios (B2B→high density…) que la taxonomy define — divergencia futura asegurada. → Una de las dos es la SSoT; la otra referencia.
- [ ] 🟢 **7.5 — Evaluar consolidación de workflows pre-DESIGN.md** (`intake`+`discover`+`moodboard`) y la pareja `branch`/`variant` para equipos pequeños — la gobernanza ya necesita un decision-tree solo para explicar la diferencia, síntoma de sobre-segmentación.
- [ ] 🟢 **7.6 — Integración Figma (evaluar).** Import de tokens/variables y export Figma Tokens en `wf-design-export`. Solo si el fit declarado en 7.1 decide cubrir equipos con diseñadores; si no, descartar explícitamente y documentarlo.

---

## FASE 8 — Persistencia y memoria entre sesiones *(de GENTLE_AI_COMPARISON)*

- [ ] 🟡 **8.1 — State Recovery post-compactación.** Estado del DAG por feature persistido en artefacto (`phase`, `completed[]`, `pending[]`) para que el orquestador se reoriente tras compactar sin re-preguntar al usuario. El pipeline de 13 pasos es exactamente donde la sesión se compacta.
- [ ] 🟡 **8.2 — Configuración de proyecto persistente** (tipo `config.yaml`): "TDD estricto", comandos de test, reglas — leída en el init y propagada a agentes. Parcialmente cubierto por `kmm_project_state.md`; generalizar al nivel de proyecto.
- [ ] 🟢 **8.3 — Session Close Protocol** formalizado (Goal / Instructions / Discoveries / Accomplished / Next Steps / Relevant Files) al cierre de sesión.
- [ ] 🟢 **8.4 — Proactive Save Triggers** — lista normativa de cuándo guardar en memoria sin esperar al usuario (decisión arquitectónica, gotcha, convención establecida…).

---

## FASE 9 — Higiene de frontmatter y meta *(restos de audit_full_global, estado re-verificado 2026-06-05)*

- [ ] 🟡 **9.1 — `argument-hint` en 49 `kb-*`** (re-verificado: subió de 47). El template canónico lo prohíbe en KBs. → Limpieza masiva por lotes con `/wf-sdd-refactor`, o actualizar el template si se decide mantenerlo — pero decidir una política y aplicarla. El meta-ecosistema incumple su propio canon en ~90% de sus KBs.
- [ ] 🟡 **9.2 — `wf-prd-create`: falta `Agent` en `allowed-tools`** (re-verificado: sigue `[Read, Write, Bash]` con `agent: prd-expert`).
- [ ] 🟡 **9.3 — `agent: prd-expert` fantasma en `wf-prd-change` y `wf-prd-review`** (re-verificado: sigue presente; los cuerpos operan inline). → Eliminar el campo o delegar de verdad.
- [ ] 🟢 **9.4 — `when_to_use` en 4 `kb-*` restantes** (re-verificado: bajó de 37 a 4). Rematar la limpieza.
- [ ] 🟢 **9.5 — `plan-auditor` no carga `kb-plan-cmp-ui`/`kb-cmp-resources`** que sí carga `plan-architect` — evaluar si el auditor debe verificar decisiones CMP.
- [ ] 🟢 **9.6 — Documentar en `wf-design-intake` que es autónoma** (no delega a agente) para que la tabla de capas del CLAUDE.md de design no confunda.
- [ ] 🟢 **9.7 — Cognitive Doc Design** — principios de calidad cognitiva en `kb-sdd-creation-guide` (respuesta primero, tablas > prosa, referencias > repetición). *(= IMPROVEMENTS #5)*
- [ ] 🟢 **9.8 — Enforcement del ciclo de calidad meta:** la detección de duplicados de `wf-skill-create` es por substring del nombre (frágil); el audit estructural es manual. → Evaluar pre-commit/CI que corra el chequeo estructural básico.

---

## Orden de ataque recomendado

| Prioridad | Qué | Por qué primero |
|---|---|---|
| 1 | **Fase 0** completa | Bugs reproducibles, bajo esfuerzo, varios "roto de fábrica" |
| 2 | **2.2** (`wf-bug`) + **2.1** (`wf-task-run`) | Sin ciclo de vida real, el sistema muere al primer sprint de mantenimiento |
| 3 | **1.1 + 1.2** (enforcement de gates) | Es el riesgo central: gates auto-aprobables = alucinación sin detección |
| 4 | **3.1** (`wf-spec-from-code`) | Abre todo el mercado brownfield — la mayoría del trabajo real |
| 5 | **5.1** (versionado + update) | Prerequisito para usar el ecosistema en >1 repo / >1 dev |
| 6 | **4.1** (modo ligero) | La diferencia entre adopción y abandono en scrum |
| 7 | **7.1** (declarar fit de design) | Barato y elimina falsas expectativas |
| 8 | Resto por severidad | — |

---

## Completado

*(mover aquí los ítems al cerrarlos, con fecha y commit)*

- [x] **Skill Registry** (`meta/skill-registry.md` + Regla 18) — *IMPROVEMENTS #1, previo a 2026-06-05* — ⚠️ pendiente de fiabilidad: ver 0.5
- [x] **Token budget / criterios de densidad** en `kb-sdd-creation-guide` — *IMPROVEMENTS #3, commit 985bd5d*
- [x] **`wf-kmm-init` + `kmm_project_state.md`** — *IMPROVEMENTS #2* — ⚠️ el installer no despliega la KB del protocolo: ver 0.1
- [x] **Contrato de overlay + `wf-stack-create`** (A1+A2 del backlog de IMPROVEMENTS)
- [x] **`model: claude-opus-4-6` no canónico en `wf-spec-features-first`** — re-verificado 2026-06-05: campo eliminado
- [x] **`kb-plan-expert` movida a `plan/skills/`** — re-verificado 2026-06-05: existe la genérica en `plan/` y la variante KMM como override (conforme al contrato de overlay)
- [x] **`when_to_use` en kb-*: limpieza principal** — de 37 a 4 ficheros (resto: ver 9.4)
