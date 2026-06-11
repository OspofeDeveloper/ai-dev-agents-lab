# FABLE_REPORT — Auditoría integral del ecosistema SDD

> Auditoría externa realizada el 2026-06-11 sobre la versión `0.29.0` (branch `develop`, commit `2f5feee`, con cambios sin commitear).
> Alcance: coherencia global, arquitectura de skills, agentes y orquestación, auditoría específica de `sdd/.claude/`, fitness para equipo multidisciplinar y mejoras aprovechables del harness de Claude Code.
> Método: 6 auditorías paralelas (meta/, prd/+spec/, design/, plan/+tasks/, tech/kmm/+bootstrap/+instalación, .claude/) + verificación estructural directa (diffs instalación↔fuente, symlinks, git, registry).
> Regla de rigor aplicada: toda afirmación tiene ruta de archivo; las inferencias van marcadas `[INFERENCIA]`.

---

## 1. Veredicto ejecutivo

**El ecosistema está bien planteado y es inusualmente disciplinado para su tamaño (131 skills, 5 fases + meta + overlay KMM).** El modelo de 3 capas (kb-* normativo / wf-* operativo / agente worker) está definido formalmente en `meta/skills/kb-sdd-skill-architecture/SKILL.md` (R1–R19), se aplica de forma consistente en plan/, tasks/, meta/ y el overlay KMM, y el eje "autor ≠ verificador mecánico" (sellador, gates, registry generado, índices generados) es real, no aspiracional. La gobernanza (ROADMAP con evidencia `archivo:línea` por ítem, CHANGELOG con avisos de breaking consumidos mecánicamente por `wf-sdd-update`) es de las mejores que se ven en plataformas internas.

**Pero el último gran refactor (split de `kb-design-expert` en 4 KBs, ROADMAP 7.x) quedó a medio cablear**, y eso deja la fase design — la más grande del sistema — citando ~25 reglas que ya no existen, con una checklist de validación anclada a numeración fantasma, un handoff Design→Plan declarado pero no cableado, y paths absolutos `/Users/oscar/...` que rompen cualquier instalación fuera de esta máquina. La documentación raíz (`sdd/README.md`) describe un ecosistema de hace ~25 versiones (KMM-céntrico, instalación en `~/.claude/` global, 27 piezas de 131).

**`sdd/.claude/` está parcialmente alineado.** Su núcleo (symlinks a meta/ y bootstrap/ vía `setup.sh --dev`, CLAUDE.md → `meta/CLAUDE.md`, todo gitignorado deliberadamente) es dogfooding intencional y sano. Pero arrastra una instalación física de design+plan (10-jun) que ya divergió de sus fuentes, sin `.sdd/` (gates no-op), con rules desactualizadas y descripciones de skill obsoletas que afectan al triggering en vivo. Es un híbrido entre workspace de desarrollo y proyecto consumidor que no es ninguna de las dos cosas.

**No existe `AGENTS.md` en el repo** (verificado con find), así que no hay conflicto en ese frente. El conflicto real de fuentes es: `sdd/README.md` (legacy) ↔ `sdd/CLAUDE.md` (casi al día) ↔ realidad del filesystem.

**Nivel de riesgo global: MEDIO.**
- Bajo en infraestructura (instalación, gates, overlay, gobernanza): coherente y verificada.
- Alto y concentrado en la fase design (referencias rotas post-split + paths absolutos = la validación de design es hoy parcialmente ficción).
- Medio en deuda documental (README raíz, READMEs de fase, tasks/ sin README) que confunde a perfiles no-dev.

---

## 2. Hallazgos críticos

### C1 — Referencias masivas a reglas inexistentes de `kb-design-expert` tras el split
- **Severidad: crítica**
- **Evidencia:** `kb-design-expert` hoy tiene 3 reglas (`design/skills/kb-design-expert/SKILL.md`); el contrato se movió a `kb-design-system-contract`, `kb-design-feature-artifacts` y `kb-design-governance`. Siguen citando las Reglas 4–23 antiguas: `design/agents/design-architect.md:60,88` ("Reglas 6, 11, 12, 13, 14 de kb-design-expert"), `design/skills/wf-design-validate/references/validation-checklist.md` (8 secciones ancladas a reglas inexistentes), `design/skills/wf-design-feature-prototype/SKILL.md:109`, `design/skills/kb-design-forms/SKILL.md:11,52`, `design/skills/kb-design-voice/SKILL.md:67`, `design/skills/kb-design-system-contract/SKILL.md:160`, `design/README.md:258,294`. También `design/skills/wf-design-sync/SKILL.md:16` cita "kb-design-governance Regla 15" (governance tiene 5 reglas).
- **Por qué rompe el modelo:** el aparato de validación (`wf-design-validate`) y el propio agente citan norma que no resuelve a ningún texto. La SSoT existe pero los punteros apuntan al pasado: es el "duplicado peligroso" que `kb-sdd-creation-guide` define, en versión "puntero colgante".
- **Impacto:** un `design-architect` o un validador que siga la checklist literal aplica criterios fantasma o se los inventa; un maintainer no puede confiar en que una cita "Regla N" sea verificable.
- **Corrección:** pase mecánico de renumeración: grep de `Regla \d+ de .?kb-design-expert` y de citas a governance/contract, remapear a la KB y numeración nuevas. Añadir al `kb-sdd-audit-structural` un check de "regla citada existe en la KB citada" (hoy solo verifica que la skill exista).

### C2 — Paths absolutos `/Users/oscar/...` en KBs normativas
- **Severidad: crítica**
- **Evidencia:** `design/skills/kb-design-feature-artifacts/SKILL.md:46,67,163` referencian los templates con ruta absoluta `/Users/oscar/Documents/GitHub/ai-dev-agents-lab/sdd/design/skills/kb-design-expert/references/...`. También `design/README.md:14,54`.
- **Por qué rompe:** viola la regla `${CLAUDE_SKILL_DIR}` de `kb-sdd-creation-guide` ("Sin ella... los Read fallan silenciosamente") y rompe toda instalación en otra máquina o en CI — exactamente lo que la política de git del README ("el proyecto funciona para cualquier dev") promete.
- **Impacto:** cualquier proyecto consumidor con fase design instalada tiene una KB cuyo contrato de artefactos no puede cargar sus templates.
- **Corrección:** sustituir por `${CLAUDE_SKILL_DIR}` y, dado que los templates de flows/views/ui_prompt son SSoT contractual de `kb-design-feature-artifacts`, **moverlos físicamente** desde `kb-design-expert/references/` a `kb-design-feature-artifacts/references/` (R9: "la ubicación física la decide la fuente de verdad"). Añadir a CI un grep prohibiendo `/Users/` en `sdd/**/*.md`.

### C3 — Doble SSoT divergente: `component_anatomy_checklist.md` duplicado
- **Severidad: crítica**
- **Evidencia:** existe en `design/skills/kb-design-expert/references/` y en `design/skills/kb-design-system-contract/references/` con contenido **divergente** (toggle "off/on" vs "checked/unchecked como subestados"; criterios de severidad redactados distinto). `kb-design-system-contract/SKILL.md` Regla 7 apunta a su propia copia "(cargado por `kb-design-expert`)" — autocontradictorio.
- **Por qué rompe:** violación literal de R14 ("references no deben contener la única copia de una regla normativa") elevada al cuadrado: dos copias normativas que ya divergieron. El check de estados de componente de `wf-design-validate` tiene dos verdades.
- **Impacto:** dos auditorías del mismo DESIGN.md pueden dar veredictos distintos según qué copia cargue el agente.
- **Corrección:** una sola copia en `kb-design-system-contract/references/` (su SSoT declarada), borrar la de `kb-design-expert`, reconciliar el contenido a mano antes de borrar.

### C4 — Handoff Design→Plan declarado pero no cableado
- **Severidad: alta**
- **Evidencia:** `design/skills/kb-design-governance/SKILL.md:30`: "plan-architect carga esta KB cross-fase…". Falso: `plan/agents/plan-architect.md` declara `skills: [kb-spec-expert, kb-plan-method, kb-plan-expert, kb-a11y-expert, kb-a11y-web-expert]` — sin `kb-design-governance`. Asimetría adicional: `plan/agents/plan-auditor.md` no carga `kb-a11y-web-expert` aunque el architect sí.
- **Por qué rompe:** el contrato de qué campos del DESIGN.md son estables para Plan es precisamente el handoff entre fases; hoy el agente de plan no lo recibe. El auditor de plan no puede verificar la materialización a11y web que el architect produce.
- **Impacto:** en targets web/desktop, el plan puede tratar como mutable lo que design declaró contrato, sin que nadie lo detecte.
- **Corrección:** añadir `kb-design-governance` al `skills:` de `plan-architect` (y valorar `kb-a11y-web-expert` en `plan-auditor`), o corregir la afirmación de la KB si la decisión es no cablearlo. `install.sh` ya resuelve dependencias cross-fase (líneas 184-192), solo hay que declararla.

### C5 — Renumeración de CAs en `wf-spec-delta` rompe la cadena de trazabilidad
- **Severidad: alta**
- **Evidencia:** `spec/skills/wf-spec-delta/references/spec_delta_integration_rules.md`: "CAs ELIMINADOS: eliminar y **renumerar** para mantener secuencia sin huecos". `kb-traceability-rules` R6/R11 definen la cadena `CA → TC → task → commit → release` por ID.
- **Por qué rompe:** renumerar CAs desplaza los IDs a los que apuntan tasks (`Spec CA: CA-003`), TCs y gates (`sdd-gate-check.py` cruza `Spec CA` contra enmiendas). Ningún mecanismo detecta el desplazamiento. Además esa regla normativa vive **solo** en un `references/` (violación R14).
- **Impacto:** tras un delta que elimina una HU, las tasks/QA existentes pueden apuntar al CA equivocado silenciosamente — corrupción de trazabilidad, el activo central del sistema.
- **Corrección:** cambiar la norma a "los IDs de CA nunca se reutilizan ni renumeran; un CA eliminado se marca tombstone" (consistente con cómo funcionan los CR-XXX y E-00X), y subir la regla a `kb-traceability-rules` o al SKILL.md de `wf-spec-delta`.

### C6 — Referencia rota `compose-mp-navigation` en la fase plan
- **Severidad: alta (estructural)**
- **Evidencia:** `plan/README.md:69` y `plan/DIAGRAMS.md:130` referencian la skill `compose-mp-navigation` "en `sdd/design/skills/`" — no existe (verificado); el dominio vive en el overlay (`tech/kmm/skills/...`).
- **Impacto:** doc de fase base apuntando a una pieza inexistente y además contaminada de stack.
- **Corrección:** eliminar la mención de la fase base; si procede, citar la KB real del overlay desde `tech/kmm/`.

### C7 — `allowed-tools` insuficiente en workflows del camino crítico
- **Severidad: alta**
- **Evidencia:** `plan/skills/wf-prepare-plan/SKILL.md` declara `allowed-tools: [Read, Write, Agent]` pero su Paso 2.5 ejecuta `git -C ... rev-parse` y su Paso 7 `!test -f` (Bash). Ídem `tasks/skills/wf-prepare-tasks/SKILL.md`. En design: `wf-design-validate` delega al agente (Paso 5) sin `Agent` en allowed-tools; `wf-design-sync` declara `agent: design-architect` y **nunca delega** (frontmatter mentiroso según R11).
- **Impacto:** fallos en runtime según el enforcement de tools del harness, y contratos de frontmatter en los que no se puede confiar para auditoría mecánica.
- **Corrección:** pase de consistencia frontmatter↔body en las ~10 wf afectadas; añadir ese check a `kb-sdd-audit-structural` (es mecanizable: grep de `!`/`git `/`Invoca` contra allowed-tools).

### C8 — `sdd/README.md` describe un ecosistema que ya no existe
- **Severidad: alta (documental, pero es la puerta de entrada)**
- **Evidencia:** `sdd/README.md:3` "sobre proyectos Kotlin Multiplatform Mobile (KMM)"; líneas 184-300 árbol bajo `~/.claude/` (la instalación real es por proyecto, como dice el mismo README en "Instalación" — el archivo se contradice a sí mismo); líneas 160-168 "kb-plan-expert + KMM arch" (hoy el overlay); línea 61 "spec monolítico limpio (_spec.md)" (ningún workflow actual lo produce); tabla "Estado de implementación" con 27 piezas de 131, sin nada de design (16 kb + 14 wf), QA/release/bug, `plan-auditor`, `qa-engineer`, methods…; "agentes Spec → modelo por defecto" (falso: declaran sonnet-4-6).
- **Impacto:** PMs, designers y devs nuevos que entren por el README construyen un modelo mental erróneo del sistema (KMM-only, instalación global, pipeline sin QA). Para una plataforma multidisciplinar, la puerta de entrada es parte del producto.
- **Corrección:** reescribir el README raíz desde `sdd/CLAUDE.md` + `meta/skill-registry.md` (que SÍ están al día), eliminando la tabla manual de estado (el registry generado ya cumple ese rol — mismo principio que `_features.md`).

---

## 3. Hallazgos de coherencia y diseño

### Duplicidades (SSoT debilitada)
1. **"Señales de expansión de capacidad" enumeradas en 6 sitios**: SSoT en `kb-product-change-governance` R4.1; copias casi literales en `spec/CLAUDE.md`, `wf-spec-features-first` (Paso 2.5.7), `wf-spec-fast-track` (Paso 5), `spec/README.md`, `sdd/CLAUDE.md`. Deriva asegurada; los 5 satélites deberían citar "R4.1" sin reenumerar.
2. **Procedimiento duplicado expert↔method**: `tasks/skills/kb-tasks-expert/SKILL.md:120-134` ("Cómo generar Tasks", pasos 1-6) duplica lo que `kb-tasks-method` declara poseer como SSoT (pasos 1-8). Eco menor entre `kb-plan-expert` ("Cómo validar un Plan") y `kb-plan-method` Sección B.
3. **Microcopy por vista** definida en `kb-design-feature-artifacts` Regla 5 y `kb-design-voice` Regla 10 (misma lista, dos KBs).
4. **Semántica de estados de feature** en `kb-decompose-expert` ("Derivación de Estado") y `wf-spec-readiness` Paso 6 (tabla propia). Hoy compatibles, sin SSoT declarada.
5. **Plantillas copiadas sin aviso**: `spec/shared/templates/*` ≡ `wf-spec-fast-track/references/*` (copia que hace `install.sh:85-89`); nada documenta que las copias en `references/` son generadas — quien edite la copia diverge en silencio.
6. **`tech/kmm/settings.json` byte-idéntico a `sdd/settings.json`**: dos fuentes del mismo hook config; si la base cambia, el merge del overlay re-introduce lo viejo.

### Contradicciones
7. **`meta/.../references/skill-architecture-patterns.md` contradice la política canónica de frontmatter**: recomienda `argument-hint` en `kb-*` cuando `kb-sdd-creation-guide` lo prohíbe ("Nunca añadir `context: fork`, `agent:` ni `argument-hint` a una `kb-*`"). La segunda SSoT contradictoria vive en las references de la skill que enuncia la regla anti-segunda-SSoT.
8. **Punteros SSoT cruzados desactualizados en design** tras el split: `kb-design-system-contract:13` atribuye a `kb-design-expert` lo que vive en feature-artifacts/governance; `kb-design-governance:13` y `kb-design-feature-artifacts:13` igual. `kb-design-characterization:16,56` declara "`DESIGN_GAP` SSoT en kb-design-expert" — kb-design-expert no lo define.
9. **`kb-qa-expert:41` cita a `wf-bug` como fuente normativa** del triaje `UNSPEC` — una kb apuntando a una wf invierte la dirección de delegación (R5/R6). La taxonomía `CODE_BUG/SPEC_CHANGE/UNSPEC` debería vivir en una kb.
10. **`kb-design-style-decision-tree:154` cita "Regla 6 de wf-design-intake"** — las wf no tienen Reglas, tienen Pasos: inversión de capas + referencia rota.
11. **Inconsistencias numéricas en design**: 13 vs 14 variables del brief (`kb-design-style-decision-tree` R1 vs `design/README.md:70` vs `kb-design-brief` R5); el agente "cubre seis modos" (`design-architect.md:159`) vs 8 declarados (`:43`) vs "siete" (`design/CLAUDE.md:131`); "siete capas" con 9 bullets (`design/CLAUDE.md:166`).
12. **Drift Room en el overlay**: `tech/kmm/agents/kmm-platform-integrator.md:52` describe `kb-tasks-kmm-room` como "expect/actual" cuando la KB corregida dice "**No es un par expect/actual**… son factories de plataforma" (`tech/kmm/skills/tasks/kb-tasks-kmm-room/SKILL.md:45-53`).
13. **`kb-sdd-audit-content` Criterio 5 cita la "Regla 19"** para exigir la sección `## Verificación de contexto`, pero esa norma solo existe en `kb-sdd-creation-guide/references/body-templates.md` — norma global viviendo solo en un references (violación de R14 dentro del propio meta).

### Sobrecargas de responsabilidad y particiones
14. **`design-architect` carga 17 KBs eager (~152 KB ≈ 38-45k tokens)** en sus 10 modos (`design/agents/design-architect.md:4`). La partición en 16 KBs es conceptualmente correcta (cada una posee una dimensión de decisión) pero su beneficio de contexto es nulo mientras un único agente las cargue todas: un triage de feedback paga foldables e iconografía. La "Nota de evolucion" del propio agente ya anticipa el split intaker/writer/auditor — está madura para ejecutarse. Comparativa: plan-architect carga 5.
15. **`tasks/` aloja una fase delivery/QA implícita**: 7 wf + 4 kb + 2 agentes, de los cuales QA/release/bug/status no son "descomposición y ejecución" (la definición de la propia fase, `tasks/CLAUDE.md:82`). `[INFERENCIA]` candidata natural a split (`delivery/` o `qa/`) si crece; explica que sea la única fase sin README.
16. **`kb-sdd-skill-architecture` con 304 líneas** (su propio umbral: ≤300) mezclando arquitectura (R1-15), tech targets (R16), registry (R18) y protocolo runtime con comandos (R19) — candidatas a extracción R16/R18/R19.
17. **`wf-design-a11y-audit` ejecuta el juicio experto inline** (Pasos 3-7b en el fork; la delegación al agente es "opcional") — el trabajo intelectual vive en la wf, contra R1/R17. `wf-design-discover` similar (research + juicio inline, sin agente).
18. **`wf-spec-from-code` mezcla modos cognitivos**: corre entero como `sdd-spec-writer` pero sus Pasos 2-4 son exploración (dominio del explorer) y el Paso 5 se auto-delega anidadamente.

### Naming y frontmatter
19. **`kb-spec-characterization` sin 3 campos obligatorios** (`spec/skills/kb-spec-characterization/SKILL.md`: solo `name` y `description`; faltan `effort`, `allowed-tools`, `user-invocable: false`).
20. **`user-invocable` ausente de forma no uniforme**: 0/6 wf de meta, 0/25 de prd+spec, 7/9 de plan+tasks lo omiten; 2 lo declaran. La plantilla canónica lo incluye. O se exige o se quita de la plantilla.
21. **Descriptions por encima del objetivo ≤220 chars que el meta fija**, empezando por el propio meta (`kb-sdd-stack-overlay-contract` 391, `kb-sdd-audit-content` 328) y siguiendo por `wf-spec-amend` (424), `kb-delivery-discipline` (~430).
22. **`effort` desviado del criterio propio en meta**: `wf-skill-create`/`wf-agent-create` (8 pasos, delegan) declaran `medium` cuando el criterio dice `high` para "6+ pasos o delegación con contexto rico".
23. **`permissionMode: acceptEdits` + `disallowedTools: Write, Edit` conviven** en los 4 auditores (plan-auditor, sdd-auditor, sdd-spec-auditor, sdd-spec-planner) — redundancia heredada de la plantilla.
24. **Naming overlay heredado** `kb-kmm-<dominio>` vs convención nueva `kb-<fase>-kmm-*` — deuda consciente y documentada (aceptable).

### Knowledge mal situada / gaps de cableado
25. **`kb-delivery-discipline` sin consumidor vía `skills:`** en ningún agente (solo referencias textuales desde wf). Funciona "por prosa", pero según el modelo de carga (R19) es huérfana de inyección; merece documentarse como excepción o cablearse.
26. **`sdd-spec-auditor` no carga `kb-decompose-expert`** aunque `kb-conflict-expert` Regla 3 le ordena consultarla.
27. **Modos no declarados**: `wf-design-feedback` invoca `Modo: design-feedback-triage` y `wf-design-variant` `design-variant-generate`, ausentes del contrato de `design-architect.md`. Además `wf-design-validate:58` habla de "invocar al agente cargando KBs" — el set de KBs es fijo por frontmatter; una wf no puede inyectar.
28. **`task_sizing.md` como única copia de norma** (señales de task grande/pequeña, DoD por tipo) — `tasks/skills/kb-tasks-expert/references/task_sizing.md` vs un SKILL.md que solo dice "consulta…". Violación R14 suave.
29. **`wf-spec-analyze` usa ruta relativa** (`Consulta [output_template.md](output_template.md)`) y el archivo vive en la raíz de la skill, no en `references/` — única skill con ese layout.
30. **Residuo "spec monolítico"**: `kb-decompose-expert` define el spec de feature como "extraído del spec monolítico" con header `Spec monolítico origen:` que ningún workflow actual produce (el pipeline real es features-first/fast-track desde PRD).
31. **Contaminación tecnológica puntual en fases base**: `kb-decompose-expert` "responsabilidades de módulos `:core:*`" (notación Gradle en kb de spec); `plan/README.md:3` "_plan.md técnico KMM" y `expect/actual` (línea 13) contradiciendo a su propia kb stack-agnóstica.
32. **`design/shared/templates/` vacío y huérfano** (0 archivos, 0 referencias).

### Gaps de gobernanza
33. **`tasks/` sin README.md ni DIAGRAMS.md** — la única fase sin mapa humano, justo la de mayor alcance. `sdd/CLAUDE.md` aún dice "`sdd/tasks/CLAUDE.md` cuando exista" (existe) y su tabla de agentes omite `plan-auditor`.
34. **Gates fail-open por diseño** (`sdd-gate-check.py`: cualquier excepción, python3 ausente o script ausente → permitir) y solo disparan si el orquestador invoca la wf vía Skill tool. Documentado y fichado (ROADMAP 11.x), pero conviene saber que borrar `.sdd/scripts/` desactiva el enforcement sin ruido. En monorepos, sesión abierta en subpaquete → `$CLAUDE_PROJECT_DIR/.sdd/` no se encuentra → gates no-op silencioso `[INFERENCIA sobre el valor de CLAUDE_PROJECT_DIR]`.
35. **Re-aplicación de overlay se omite en silencio sin python3** (`install.sh:406`: la lectura del stack está envuelta en `command -v python3`) — el escenario que el Paso 7 quería cubrir degrada sin aviso.
36. **El sellador valida cobertura de CAs por mención textual** (`\bCA-XXX\b` en el plan): citar sin cubrir pasa el check (el juicio real sigue en plan-auditor — aceptable, pero es bueno tenerlo explícito).
37. **`docs/audit_full_global.md` posiblemente huérfano** (el header del ROADMAP dice que las fuentes consolidadas fueron eliminadas).
38. **Drift no vigilado de la capa bootstrap**: el hook de sesión y el bloque global solo se actualizan con `setup.sh --update` manual; el aviso `version-drift` cubre la instalación del proyecto, no el hook de la máquina.

### Lo que está bien y conviene proteger (anti-hallazgos)
- `meta/skill-registry.md` 100% sincronizado con el filesystem (131/131, 0 discrepancias) — el patrón "índice generado, nunca editado" funciona.
- Overlay KMM con cumplimiento alto del contrato: variantes por override que cargan las method-KBs y solo aportan hooks ‹especialización de stack›; agentes kmm-* fundamentados en KBs por referencia, no por copia; 0 referencias residuales al agente eliminado `kmm-feature-implementer`.
- Separación autor/auditor/sellador en plan y QA: de libro (`wf-plan-validate:110` "el veredicto del agente es necesario pero no suficiente").
- Pares con fronteras explícitas: audit-structural↔audit-content, taxonomy↔decision-tree, a11y↔a11y-web — el patrón "No cubre X (ver Y)" debería ser plantilla obligatoria.
- ROADMAP/CHANGELOG: 0 ítems marcados hechos cuyo artefacto no exista (muestreado).
- Instalación: 0 referencias rotas entre install.sh/setup.sh/tech/kmm/install.sh y el filesystem.

---

## 4. Auditoría específica de `sdd/.claude/`

### Qué está bien
- **El núcleo meta es dogfooding intencional y correcto**: `CLAUDE.md → meta/CLAUDE.md` (symlink), agentes `sdd-author`/`sdd-auditor` y skills de meta/bootstrap symlinkeados por `setup.sh --dev` (líneas 192-205, documentado). Editas la fuente y el workspace lo ve al instante — cero drift en esa capa.
- **Higiene git deliberada**: todo `sdd/.claude/` está en `.gitignore` (línea 5) con comentario explicativo; `git ls-files sdd/.claude` → 0 archivos. No contradice la política "commitea .claude/" del README: esa aplica a proyectos consumidores, este es el repo fuente.
- **Frontmatter de los 5 agentes conforme** a `frontmatter-templates.md` (modelos, effort, disallowedTools, colores por fase correctos). 0 referencias rotas agente→skill: las 17 KBs de design-architect y las de plan-* están todas instaladas (la dependencia cross-fase `kb-spec-expert` la resolvió bien `install.sh`).
- **Cobertura wf↔agente íntegra**: ninguna wf instalada delega a un agente ausente (verificado por grep de `agent:` contra `.claude/agents/`).
- **`rules/sdd-plan.md` idéntico a su fuente y solo routing** — ambas rules delegan explícitamente la normativa a las kbs ("No las redefinas aqui"). No hay segunda SSoT en rules.
- **`agent-memory/` correctamente fuera de git**; la memoria de `sdd-author` (`project_human-checkpoint-ssot.md`) es de calidad — documenta por qué `kb-traceability-rules` R10 es la SSoT del sello `Aprobado por`.

### Qué está incompleto
- **Instalación sin `.sdd/`**: `install.sh` paso 4b instala los scripts de enforcement incondicionalmente, pero `.sdd/` no existe en el repo → los hooks de `settings.json` (PermissionRequest→`sdd-skill-allow.py`, PreToolUse→`sdd-gate-check.py`) son no-op permanente. `[INFERENCIA]` se borró deliberadamente para no tener un `.sdd/` de consumidor dentro del repo del ecosistema — pero entonces los hooks instalados son teatro: una instalación a medias.
- **Pipeline truncado conscientemente en plan**: `rules/sdd-plan.md` apunta a `wf-prepare-tasks` como siguiente paso y la fase tasks no está instalada. Informativo (es prosa, no delegación), pero quien siga el camino canónico aquí choca.

### Qué está desalineado
- **Las copias físicas divergen de sus fuentes**: 26 de 33 skills copiadas difieren de `design|plan|spec/skills/` (verificado con diff -rq), y `agents/design-architect.md` difiere en 8 líneas de su fuente (la fuente ya es tool-agnostic "Stitch|web-generic"; la copia sigue "para Stitch"). Causa: fuentes editadas sin commitear después de la instalación del 10-jun 15:11. **Efecto operativo real**: las descriptions instaladas son las que ve el harness para triggering — p. ej. la `kb-spec-expert` instalada conserva `when_to_use`/frases de activación que la política prohíbe en kb-* y que la fuente ya eliminó (visible hoy en el listado vivo de skills de la sesión).
- **`rules/sdd-design.md` desactualizada en 17 líneas** vs `design/CLAUDE.md` (decisión Figma 7.6 del 2026-06-10, wording tool-agnostic, sección "Camino minimo" nueva).
- **El glob `design/**` de `rules/sdd-design.md` matchea `sdd/design/`** — el directorio FUENTE. `[INFERENCIA]` al editar skills de la fase design en este repo, el harness carga las reglas de orquestador operativo de design encima del meta-orquestador: contaminación de contexto del dogfooding.

### Qué parece legacy o accidental
- **La instalación física de design+plan es una instalación de prueba que se quedó** `[INFERENCIA]`: coincide con el trabajo del roadmap 7.x (commits del 10-jun), no tiene `.sdd/`, divergió a las pocas horas y nadie ejecuta el pipeline design→plan dentro del repo del ecosistema. Funcional pero accidental.
- `settings.local.json` con permisos fósiles hiperespecíficos de un refactor de renombrado (`sed -i ... kb-conflict-expert ...`) de hace meses.
- `.DS_Store` ×2; `agent-memory/sdd-auditor/` vacío.

### Qué mover, eliminar, fusionar o recrear
1. **Eliminar las copias físicas** de design/plan/spec en `.claude/skills/` y los 3 agentes copiados, y decidir el modelo del workspace: o **dev puro** (extender `setup.sh --dev` para symlinkear también las fases que se quieran probar) o **consumidor real** (re-ejecutar `install.sh` tras cada cambio relevante / commitear y mantener `.sdd/`). El estado híbrido actual es el peor de los dos mundos.
2. **Regenerar o eliminar `rules/`** según esa decisión; si se quedan, anclar los globs para que no matcheen `sdd/design/**` fuente (p. ej. globs relativos a artefactos de proyecto, no `design/**` genérico — afecta también a `install.sh phase_globs()` para cualquier consumidor cuyo repo tenga un directorio `design/` de código).
3. **Quitar los hooks de `settings.json`** del workspace si no va a existir `.sdd/`, o restaurar `.sdd/scripts/` si se quiere dogfoodear el enforcement.
4. **Limpiar `settings.local.json`** (dejar los genéricos `Bash(grep:*)`, `Bash(ls:*)`, etc.).
5. Conservar tal cual: symlinks meta/bootstrap, CLAUDE.md symlink, agent-memory ignorada.

---

## 5. Propuesta de refactor del ecosistema

### 5.1 Cambios inmediatos (horas, sin decisiones de diseño)
1. **Pase de renumeración post-split en design** (C1): remapear las ~25 citas "Regla N de kb-design-expert" + checklist de `wf-design-validate` + punteros SSoT cruzados de las 4 KBs hermanas (hallazgo 8) + `DESIGN_GAP`.
2. **Eliminar paths absolutos** (C2): `${CLAUDE_SKILL_DIR}` + mover los templates de feature a `kb-design-feature-artifacts/references/`.
3. **Unificar `component_anatomy_checklist.md`** (C3): reconciliar y dejar una copia.
4. **Cablear `kb-design-governance` en `plan-architect`** y `kb-decompose-expert` en `sdd-spec-auditor`; valorar `kb-a11y-web-expert` en `plan-auditor` (C4, 26).
5. **Corregir frontmatter mecánico**: `kb-spec-characterization` (3 campos), `allowed-tools` de `wf-prepare-plan`/`wf-prepare-tasks`/`wf-design-validate`, `agent:` falso de `wf-design-sync`, modos no declarados de design-architect (C7, 19, 27).
6. **Borrar la referencia `compose-mp-navigation`** (C6) y el texto Room stale de `kmm-platform-integrator.md:52` (12).
7. **Decidir y aplicar la regla de no-renumeración de CAs** (C5).
8. **Sanear `sdd/.claude/`** según §4 (eliminar copias o re-sync, hooks, settings.local).
9. **Corregir `skill-architecture-patterns.md`** del meta (7): alinear sus templates con la política canónica o reducirlo a patrones sin frontmatter.

### 5.2 Cambios estructurales (días, requieren decisión)
1. **Reescribir `sdd/README.md` raíz** desde el estado real (C8), eliminando la tabla manual de estado a favor del registry generado, y crear `tasks/README.md` (33). Actualizar `plan/README.md`/`plan/DIAGRAMS.md` (neutralidad + plan-auditor/sellador) y los inventarios de `spec/README.md`, `prd/README.md`, `design/README.md` (12/16 kbs listadas).
2. **Consolidar las duplicidades de SSoT** (1-6): señales de expansión → solo R4.1; procedimiento de tasks → solo `kb-tasks-method`; microcopy → una KB referencia a la otra; estados de feature → SSoT en `kb-decompose-expert` referenciada por `wf-spec-readiness`; taxonomía de triaje de `wf-bug` → subirla a `kb-qa-expert` o kb propia (9); documentar que las copias de templates en `references/` son generadas (5); hacer que `tech/kmm/install.sh` consuma `sdd/settings.json` en vez de llevar copia (6).
3. **Split del `design-architect` por modo cognitivo** (14): intaker (brief/moodboard/discover: ~5 KBs), writer (system/prototype/extract/delta: ~10), auditor (validate/a11y/conflict: ~6, con `disallowedTools`). Sigue la "Nota de evolucion" ya escrita en el agente. Alternativa más barata si no se quiere multiplicar agentes: ver §7.3 (lazy loading vía Skill tool).
4. **Extraer R16/R18/R19 de `kb-sdd-skill-architecture`** (16) a una `kb-sdd-runtime-protocol` o similar, y subir la norma `## Verificación de contexto` de `body-templates.md` a un SKILL.md (13).
5. **Nombrar la fase delivery/QA implícita** (15): o renombrar el alcance declarado de `tasks/` o split en `tasks/` + `delivery/`. Decisión de gobernanza, no urgente.
6. **Re-delegar los wf de design que ejecutan juicio inline** (17): `wf-design-a11y-audit` → auditor; `wf-design-discover` → valorar agente o declararlo mecánico honesto. Aclarar el diseño de `wf-spec-from-code` (18) y el conflict-check cross-agente de `wf-spec-delta`.
7. **Robustecer instalación**: aviso (no silencio) cuando la re-aplicación de overlay se omite sin python3 (35); fix del filtro `README.md` a cualquier profundidad; búsqueda de `.sdd/` hacia arriba en los hooks de gates para monorepos (34).

### 5.3 Cambios opcionales de mejora
1. **Checks nuevos en `kb-sdd-audit-structural`/scripts**: regla-citada-existe (anti-C1), no-paths-absolutos (anti-C2), frontmatter↔body de allowed-tools (anti-C7), description ≤220 y user-invocable presente (20-21). Idealmente como script determinista en CI, no solo como criterio de agente.
2. **Tombstones de CA/HU** formalizados en `kb-traceability-rules` (complemento de C5).
3. **Plantilla obligatoria "No cubre X (ver Y)"** en descriptions de kb (generalizar el patrón de los pares buenos).
4. **Resolver el residuo "spec monolítico"** en `kb-decompose-expert` (30) y neutralizar `:core:*` (31).
5. **Fecha de caducidad para el fallback `kmm_project_state.md`** en `wf-prepare-plan`/`wf-prepare-tasks` o resolverlo por glob `*_project_state.md`.
6. **Promover la memoria de `sdd-author`** (`human-checkpoint-ssot`) a doc versionada si se quiere compartir entre maintainers.
7. Limpieza: `design/shared/` vacío, `docs/audit_full_global.md` huérfano, `.DS_Store` (añadir check pre-commit).

### Orden recomendado
5.1.1–5.1.3 primero (design es la fase con más usuarios potenciales no-dev y hoy su validación cita norma fantasma), después 5.1.4–5.1.9 en un solo PR de "consistencia mecánica", después 5.2.1 (documentación de entrada) y 5.2.2 (SSoT). El resto según apetito. Casi todo 5.1 es ejecutable con el propio `wf-sdd-refactor` del ecosistema — buen test de dogfooding.

---

## 6. Mapa final de confianza

| Área | Estado | Nota |
|---|---|---|
| Modelo conceptual 3 capas (meta/) | **Sólido** | R1–R19 bien formuladas; 2 fugas de norma a references y 1 reference contradictoria |
| `meta/skill-registry.md` | **Sólido** | 131/131 sincronizado, generado, nunca a mano |
| Gobernanza (ROADMAP/CHANGELOG/VERSION) | **Sólido** | Evidencia por ítem, pendientes honestos, 0 promesas falsas detectadas |
| Instalación (install.sh/setup.sh) y bootstrap | **Sólido** | 0 refs rotas; fragilidades menores documentadas (fail-open, python3, monorepo) |
| Overlay KMM (tech/kmm/) | **Sólido** | Cumplimiento alto del contrato; drift documental puntual (Room) |
| Fase prd/ | **Aceptable** | Limpia; duplicidades de R4.1 y README incompleto |
| Fase spec/ | **Aceptable** | Bien particionada; 1 frontmatter roto, regla de renumeración de CAs peligrosa, residuo monolítico |
| Fase plan/ | **Aceptable** | Núcleo limpio y neutral; README/DIAGRAMS legacy con ref rota; allowed-tools |
| Fase tasks/ (incl. QA/release/bug) | **Aceptable** | Piezas bien cortadas; fase implícita sin nombre, sin README, kb huérfana de inyección |
| Fase design/ — KBs y partición | **Frágil** | Partición conceptual correcta pero split a medio cablear: refs rotas, doble SSoT, punteros cruzados |
| Fase design/ — validación (`wf-design-validate` + checklist) | **Roto** | La checklist ancla 8 secciones a reglas inexistentes; doble checklist divergente |
| Handoff Design→Plan | **Frágil** | Declarado en governance, no cableado en plan-architect |
| `sdd/CLAUDE.md` raíz | **Aceptable** | Rootmap casi al día; 2 punteros stale (tasks "cuando exista", plan-auditor omitido) |
| `sdd/README.md` raíz | **Roto** | Describe el ecosistema pre-overlay; se contradice a sí mismo; puerta de entrada errónea |
| `sdd/.claude/` — núcleo meta (symlinks, CLAUDE.md, git hygiene) | **Sólido** | Dogfooding intencional, documentado y sin drift |
| `sdd/.claude/` — instalación design+plan | **Frágil** | Copias stale, hooks no-op sin `.sdd/`, rules desactualizadas, glob que pisa fuentes |
| Enforcement (gates + sellador + scripts .sdd/) | **Aceptable** | Bien diseñado y honesto; fail-open por diseño, cobertura por mención textual, huecos fichados en ROADMAP 11.x |
| Fitness por perfil — developers | **Aceptable** | Pipeline plan→tasks→run→QA completo y con gates; depende del overlay para su stack |
| Fitness por perfil — PMs/producto | **Aceptable** | prd/spec maduros (governance de cambios, cascade); el README los desorienta |
| Fitness por perfil — designers | **Frágil** | La fase más rica del sistema es la que tiene la validación rota y el agente más sobrecargado |
| Fitness por perfil — QA | **Aceptable** | Ciclo TC/verify/bug/release trazable; vive sin nombre dentro de tasks/ |
| Fitness por perfil — maintainers del ecosistema | **Sólido** | meta + registry + auditorías + dogfooding real; los checks estructurales deberían ser script, no solo agente |

---

## 7. Mejoras aprovechables del harness (Claude Code) sobre el ecosistema

El ecosistema ya explota bien varias capacidades del harness: hooks `SessionStart`/`PreToolUse`/`PermissionRequest`, rules con `paths:` (lazy loading nativo), `context: fork` en wf, agentes con `skills:`, `memory: project`, `disallowedTools` y `model` por complejidad. Mejoras concretas pendientes:

1. **Empaquetar SDD como plugin de Claude Code** (la mejora de mayor impacto). El mecanismo actual de copia (`install.sh` → `.claude/` del proyecto) es la causa raíz del drift observado en `sdd/.claude/` y en cualquier consumidor entre updates. Un plugin distribuye skills+agentes+hooks+settings versionados como unidad, con update centralizado, y eliminaría `install.sh`/`wf-sdd-update`/el sello de versión para la capa de piezas (los scripts de enforcement commiteados en `.sdd/` seguirían viajando en git para CI). El overlay KMM encaja como segundo plugin o como módulo del mismo. Evaluar contra el requisito "funciona clonando sin nada instalado": hoy ese requisito lo cubre la copia commiteada; un plugin lo cubre con instalación declarativa por equipo.

2. **Lazy loading real de KBs vía Skill tool en agentes** (alternativa barata al split del design-architect). El frontmatter `skills:` es inyección eager. El harness permite que un agente con `Skill` en sus tools invoque skills bajo demanda. Para `design-architect`: mantener en `skills:` el núcleo (expert, system-contract, feature-artifacts, brief, governance) y cargar por modo las especializadas (forms, motion, iconography, layout, voice, a11y-web) con una tabla "modo → KBs a cargar" en el body. Reduce ~40k tokens eager a ~15k + bajo demanda. Requiere ajustar el protocolo KB Load Status (R19) para distinguir "inyectada" de "cargada bajo demanda".

3. **Hook `SessionStart` adicional para drift de instalación**: el hook actual detecta `version-drift` proyecto↔ecosistema; añadir (o extender `sdd-session-check.sh`) un check barato de drift bootstrap (comparar hash del hook instalado en `~/.claude/hooks/` con la fuente cuando `~/.sdd-home` resuelve) — cierra el hallazgo 38 sin intervención manual.

4. **Hook `PostToolUse` para el sellador**: hoy el gate es preventivo (PreToolUse en la siguiente fase). Un PostToolUse sobre Write/Edit de `*_plan.md` podría ejecutar `sdd-seal.py --check` y degradar a BORRADOR inmediatamente cuando una edición manual invalida el sello, en lugar de descubrirlo en el siguiente gate. Mismo patrón para `_features.md` con `sdd-features-index.py --check`.

5. **Hook `Stop`/`SubagentStop` para KB Load Status**: el auto-reporte `## KB Load Status` de los agentes es no-autoritativo (lo reconoce ROADMAP 1.5). Un hook SubagentStop que ejecute `sdd-kb-check.py` contra el agente recién terminado convertiría la señal en determinista.

6. **`permissions.allow` curado y commiteado**: los proyectos consumidores sufrirán prompts por los comandos read-only que las wf ejecutan (`git rev-parse`, `test -f`, `python3 .sdd/scripts/...`). Incluir en el `settings.json` instalado una allowlist mínima (`Bash(python3 .sdd/scripts/*)`, `Bash(test -f *)`, `Bash(git rev-parse*)`) reduce fricción sin abrir nada peligroso. (En este repo, además, limpiar los permisos fósiles de `settings.local.json`.)

7. **Globs de rules anclados a artefactos, no a directorios genéricos**: `phase_globs()` en `install.sh:222-230` genera `design/**`, que colisiona con cualquier repo que tenga un directorio `design/` de código (y en este repo matchea las fuentes del ecosistema). Anclar a los artefactos (`**/DESIGN*.md`, `**/features/*/design/**`) y al mapa `artifacts` de `project-init.json`, que `wf-project-init` ya conoce.

8. **Auditoría periódica programada**: `wf-sdd-audit structural` es mecanizable y barato; ejecutarlo como rutina programada (cron del harness o CI) sobre el repo del ecosistema convertiría hallazgos tipo C1/C6 (refs rotas) en alertas del día siguiente en vez de descubrimientos de auditoría. Los checks nuevos propuestos en §5.3.1 entran aquí.

9. **Worktrees para `wf-design-branch`**: el workflow de variantes paralelas del DESIGN.md gestiona ramas como archivos (`DESIGN.<branch>.md`). El harness soporta aislamiento por git worktree para agentes; para variantes que toquen más de un artefacto (DESIGN + views + tokens exportados) un worktree por rama daría aislamiento real con merge por git en lugar de archivos paralelos. `[INFERENCIA]` solo vale la pena si las variantes crecen más allá del DESIGN.md.

10. **Higiene de descriptions para triggering**: el harness selecciona skills por `description`/`when_to_use`; las copias instaladas stale (p. ej. la `kb-spec-expert` con frases de activación visibles hoy en el listado de la sesión) degradan el routing en vivo. La regla "kb-* sin triggers" ya existe — falta que la instalación nunca quede atrás (refuerza el punto 1: plugin o re-sync automático).

---

*Informe generado por Claude (Fable 5) — auditoría de solo lectura; ningún archivo del ecosistema fue modificado salvo la creación de este documento.*
