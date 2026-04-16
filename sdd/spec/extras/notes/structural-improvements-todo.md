# TODO: Mejoras estructurales del proyecto (v2)

> Generado: 2026-04-07 | v2
> Referencia: análisis profundo de agent-teams-lite-main — `sdd-phase-common.md`, `persistence-contract.md`, `skill-resolver.md`, `judgment-day`, `sdd-init`, `sdd-verify`, `sdd-explore`, `docs/architecture.md`, `docs/token-economics.md`, `examples/claude-code/CLAUDE.md`.
> Scope: cambios de arquitectura del sistema de agentes, no modificaciones específicas de archivos individuales.

---

## Contexto

SDD Lab y Agent Teams Lite (ATL) comparten filosofía (el orquestador no hace trabajo real; la lógica vive en los skills) pero difieren en madurez estructural. Los puntos de este documento son mejoras de arquitectura que ATL ha resuelto y que SDD Lab debería adoptar para ser más robusto a medida que el pipeline crece hacia la fase de plan, tasks e implementación.

**Novedad v2:** Añadidos A-10 a A-16 tras lectura profunda de `sdd-phase-common.md`, `judgment-day`, `sdd-init`, `sdd-verify` y `persistence-contract.md`. Refinados A-01, A-02 y A-03 con detalles adicionales encontrados en esa lectura.

---

## DONE

_(vacío por ahora)_

---

## PENDING

---

### [A-01] Return envelope estandarizado para todos los skills

**Referencia ATL:** `skills/_shared/sdd-phase-common.md` → Sección D / `docs/architecture.md` → Sub-Agent Result Contract

**Problema actual:** Cada skill de SDD Lab devuelve output en formato libre — algunos con bullet points, otros con headers markdown, otros con texto plano. El orquestador (CLAUDE.md) no tiene forma de parsear el estado de un skill de forma programática. Si un skill falla parcialmente o hay un bloqueo, el orquestador lo detecta leyendo el texto, no leyendo un campo estructurado.

**Por qué importa estructuralmente:** A medida que el pipeline crece (plan → tasks → apply → verify), el orquestador necesita saber el estado de cada fase para decidir qué ejecutar a continuación. Sin un contrato de retorno, esa lógica queda en el criterio del LLM que interpreta texto libre — lo que introduce inconsistencia y bugs silenciosos.

**Qué adoptar de ATL:**
Cada skill/agente worker debe terminar devolviendo un envelope estructurado:

```markdown
**Status**: success | partial | blocked
**Summary**: [1-3 frases de qué se hizo]
**Artifacts**: [lista de paths de artefactos escritos]
**Next**: [siguiente skill recomendado en el pipeline, o "ninguno"]
**Risks**: [riesgos detectados, o "Ninguno"]
**Skill Resolution**: injected | fallback | none — [detalle de cómo se cargaron los kb-]
```

El campo `skill_resolution` es crítico para A-06 (self-healing). El orquestador lee `Status` para decidir si continuar o escalar, `Next` para sugerir el siguiente paso, `Risks` para escalar advertencias, y `Skill Resolution` para detectar pérdida de caché.

**Refinamiento v2:** ATL también tiene un campo `detail_level` que el orquestador puede pasar al skill para controlar verbosidad de output (`concise | standard | deep`), sin que eso afecte lo que se persiste — siempre se persiste el artefacto completo. Útil para que el orquestador pida un status rápido vs. un informe completo.

**Esfuerzo de adopción:** Bajo — es añadir instrucciones al paso "Informar al usuario" de cada skill. No cambia la lógica, solo estandariza el formato de cierre.

---

### [A-02] Protocolo compartido entre todos los skills (`_shared/`)

**Referencia ATL:** `skills/_shared/sdd-phase-common.md`, `skills/_shared/persistence-contract.md`

**Problema actual:** Cada skill de SDD Lab es completamente autónomo. El comportamiento común (cómo carga sus knowledge bases, cómo verifica precondiciones, cómo informa al finalizar) está replicado en cada SKILL.md con variaciones sutiles. Cuando hay que cambiar un comportamiento común (por ejemplo, añadir el return envelope de A-01), hay que editar cada skill individualmente.

**Por qué importa estructuralmente:** La falta de protocolo compartido hace que el sistema no escale. Con 18 skills actuales y más en camino, cualquier cambio transversal es costoso y propenso a inconsistencias. ATL tiene 9 skills y ya tiene protocolo compartido — en SDD Lab es más urgente.

**Qué adoptar de ATL:**
Crear `spec/skills/_shared/` con al menos dos archivos:

1. **`phase-common.md`** — protocolo que todo skill de workflow debe seguir:
   - Cómo carga sus knowledge bases (orden, fallback)
   - Cómo verifica precondiciones antes de ejecutar
   - Formato del return envelope (A-01) incluyendo `skill_resolution`
   - Qué hacer si el agente detecta pérdida de contexto (A-06)
   - Regla de "no crear archivos placeholder" — ningún skill debe crear archivos vacíos o con contenido de plantilla sin rellenar. Si no tiene información suficiente para generar el artefacto, debe bloquearse con `Status: blocked` y preguntar, no crear un archivo vacío que confundirá al siguiente skill del pipeline.

2. **`skill-contracts.md`** — tabla de contratos input/output por skill (fuente de verdad del DAG):
   ```
   | Skill               | Precondiciones (lee)         | Produce (escribe)          |
   |---------------------|------------------------------|----------------------------|
   | wf-spec-analyze     | <prd.md>                     | _analysis.md               |
   | wf-spec-discover    | <prd.md>, [_analysis.md]     | _discovery.md              |
   | wf-spec-fast-track  | <prd.md>, _discovery.md      | <feature>_spec.md          |
   | wf-spec-conflict    | <spec.md>, features/         | _conflict_report.md        |
   | wf-spec-readiness   | features/                    | _readiness_report.md       |
   | wf-spec-repair      | _readiness_report.md         | specs modificados          |
   | wf-spec-delta       | <spec.md>, [<delta.md>]      | <spec.md> actualizado      |
   | wf-prepare-plan     | <spec.md>                    | <feature>_plan.md          |
   | wf-prepare-tasks    | <plan.md>                    | <feature>_tasks.md         |
   ```

**Esfuerzo de adopción:** Medio — crear los archivos compartidos y añadir una referencia en cada SKILL.md existente. No cambia lógica interna.

---

### [A-03] DAG de fases con contratos explícitos y estado por proyecto

**Referencia ATL:** `docs/architecture.md` → The Dependency Graph, `examples/claude-code/CLAUDE.md` → Dependency Graph + Phase read/write table, `skills/_shared/persistence-contract.md` → State Persistence

**Problema actual:** El pipeline está documentado en CLAUDE.md como un diagrama ASCII. No hay una definición formal de precondiciones/postcondiciones por skill, ni un mecanismo para persistir el estado del pipeline entre sesiones. Si el usuario interrumpe el pipeline y vuelve al día siguiente, el orquestador no sabe en qué estado está sin releer y analizar todos los artefactos del proyecto.

**Por qué importa estructuralmente:** ATL tiene un `state.yaml` por change que registra el estado del DAG y permite recuperación tras compactación o interrupción. Es la pieza que hace el pipeline recuperable.

**Qué adoptar de ATL:**

1. **Tabla de contratos en CLAUDE.md** — misma tabla que A-02 `skill-contracts.md` pero desde la perspectiva del orquestador. Permite verificar precondiciones antes de invocar un skill sin leer su lógica interna.

2. **`_sdd_state.yaml` por proyecto** — generado por `wf-init-sdd`, actualizado por cada skill al terminar via return envelope:
   ```yaml
   project: nombre-del-proyecto
   prd: prd.md
   updated: 2026-04-07
   phases:
     analyze:   { status: done, artifact: prd_analysis.md }
     discover:  { status: done, artifact: prd_discovery.md }
     features:
       auth:    { spec: done, conflict: done, readiness: ready, plan: pending, tasks: pending }
       profile: { spec: done, conflict: done, readiness: blocked, plan: pending, tasks: pending }
   ```

3. **Separación clara de quién lee qué** — adoptada de ATL `persistence-contract.md`:
   - Para phases sin dependencias (analyze, discover): nadie lee; el skill genera desde cero.
   - Para phases con dependencias (fast-track, plan, tasks): el skill lee directamente sus artefactos de entrada; el orquestador pasa la referencia (path), no el contenido.
   - Razón: los artefactos SDD son grandes — inlinarlos en el prompt del orquestador consumiría el contexto entero.

**Esfuerzo de adopción:** Medio-alto — requiere que cada skill escriba su status al `_sdd_state.yaml` al terminar, y que `wf-init-sdd` lo cree. El mayor ROI del proyecto a largo plazo.

---

### [A-04] Routing de modelos como contrato explícito en CLAUDE.md

**Referencia ATL:** `examples/claude-code/CLAUDE.md` → Model Assignments table

**Problema actual:** Solo `plan-architect` tiene model asignado explícitamente (Opus). El resto de agentes no tienen asignación documentada — el sistema usa el modelo por defecto sin justificación. Cuando el modelo por defecto cambia o el usuario quiere optimizar costes, no hay una fuente de verdad para saber qué modelo usa qué fase.

**Por qué importa estructuralmente:** El modelo correcto por fase importa en coste y calidad. Sin tabla explícita, el sistema es inconsistente y las decisiones de modelo quedan implícitas en los frontmatters dispersos de los agentes.

**Qué adoptar de ATL:**
Añadir en CLAUDE.md una tabla de asignación con fallback explícito:

```markdown
## Asignación de modelos por fase

| Agente / Skill           | Modelo    | Razón                                          |
|--------------------------|-----------|------------------------------------------------|
| Orquestador (CLAUDE.md)  | opus      | Coordina, toma decisiones de routing           |
| sdd-analyst (spec)       | sonnet    | Escritura estructurada, análisis de requisitos  |
| plan-architect (plan)    | opus      | Decisiones arquitectónicas KMM, trade-offs     |
| task-generator (tasks)   | sonnet    | Desglose mecánico con trazabilidad             |
| wf-spec-repair           | sonnet    | Aplicación quirúrgica de fixes                 |
| wf-spec-contracts        | sonnet    | Escritura estructurada de CIs                  |

Fallback: si el modelo asignado no está disponible → opus → sonnet → haiku. Registrar downgrade en el return envelope.
```

**Esfuerzo de adopción:** Muy bajo — añadir sección a CLAUDE.md y verificar frontmatters de agentes worker.

---

### [A-05] Reglas explícitas de delegación en el orquestador (inline vs. sub-agente)

**Referencia ATL:** `examples/claude-code/CLAUDE.md` → Delegation Rules, `docs/token-economics.md`

**Problema actual:** CLAUDE.md declara que el orquestador "no ejecuta el trabajo directamente", pero no define cuándo algo es "trabajo directo" vs. una acción legítima del orquestador. El LLM puede derivar hacia trabajo inline sin violar las instrucciones actuales.

**Por qué importa estructuralmente:** ATL mide el coste en `token-economics.md`: el trabajo inline en el orquestador infla su contexto y acelera la compactación. Para un pipeline de 9+ fases es un problema de diseño real — el contexto del orquestador crece con cada fase y la calidad de las decisiones de routing degrada.

**Qué adoptar de ATL:**
Añadir en CLAUDE.md una tabla de reglas y anti-patrones explícitos:

```markdown
## Reglas de delegación

| Acción                                             | Inline | Delegar |
|----------------------------------------------------|--------|---------|
| Leer 1-3 archivos para verificar estado            | ✅     | —       |
| Leer 4+ archivos para entender el proyecto         | —      | ✅      |
| Escribir 1 archivo mecánico (sabes exactamente qué)| ✅     | —       |
| Escribir con análisis (múltiples archivos, lógica) | —      | ✅      |
| Comandos de estado (git status, ls, wc)            | ✅     | —       |
| Ejecutar tests o builds                            | —      | ✅      |

Anti-patrones prohibidos:
- Leer specs para "entender el proyecto" antes de invocar un skill → invocar el skill directamente
- Construir el análisis de un PRD inline → invocar wf-spec-analyze
- Sintetizar resultados de múltiples artefactos leyéndolos todos → el skill siguiente lo hace
```

**Esfuerzo de adopción:** Muy bajo — añadir sección a CLAUDE.md.

---

### [A-06] Self-healing: detección de pérdida de contexto por compactación

**Referencia ATL:** `skills/_shared/sdd-phase-common.md` → Sección A, `skills/_shared/skill-resolver.md` → Feedback Loop

**Problema actual:** Cuando Claude Code compacta el contexto (el orquestador lleva muchas fases), los knowledge bases y el estado de la sesión pueden perderse silenciosamente. El orquestador degradado no sabe que está degradado y produce output de menor calidad sin señales de advertencia.

**Por qué importa estructuralmente:** ATL mide que la compactación puede costar 15.000-55.000 tokens en re-lecturas si no se gestiona. La degradación silenciosa es peor que el error explícito — el usuario no lo detecta hasta ver el artefacto final.

**Qué adoptar de ATL:**
El campo `skill_resolution` del return envelope (A-01) es la señal de detección:
- `injected` — los kb- llegaron correctamente inyectados desde el orquestador
- `fallback` — el agente tuvo que auto-cargarse sus skills (el orquestador perdió el caché)
- `none` — no se cargaron skills en absoluto

Regla de auto-corrección en CLAUDE.md: si cualquier skill reporta `fallback` o `none`, el orquestador debe:
1. Avisar al usuario: "Detectada pérdida de caché de skills — recargando para las siguientes fases."
2. Re-leer los kb- relevantes antes de la siguiente delegación.
3. Asegurarse de que las siguientes delegaciones incluyen los kb- explícitamente en el prompt.

**Esfuerzo de adopción:** Bajo una vez que A-01 está implementado.

---

### [A-07] Meta-comandos para flujos comunes en el orquestador

**Referencia ATL:** `examples/claude-code/CLAUDE.md` → Meta-commands: `/sdd-continue`, `/sdd-ff`, `/sdd-new`

**Problema actual:** El usuario debe conocer y teclear la secuencia correcta de comandos para ejecutar el pipeline. Si interrumpe y vuelve, no sabe en qué paso está sin leer los artefactos.

**Por qué importa estructuralmente:** La usabilidad del pipeline depende de que el orquestador gestione flujos comunes sin que el usuario recuerde la secuencia exacta. Los meta-comandos son lógica del orquestador declarada en CLAUDE.md — no requieren skills nuevos.

**Qué adoptar de ATL:**

- `/sdd-continue [proyecto]` — el orquestador lee `_sdd_state.yaml` (A-03), determina la siguiente fase pendiente y la ejecuta. Si hay fases en paralelo disponibles, las lanza en paralelo.
- `/sdd-ff <prd.md>` — fast-forward: ejecuta `wf-spec-analyze` → `wf-spec-features-first` → `wf-spec-readiness` en secuencia, pausando solo si hay gaps CRÍTICO sin responder.
- `/sdd-status [proyecto]` — reporta el estado actual del pipeline: qué features existen, cuáles bloqueadas, cuáles listas para plan.

Distinción importante de ATL: estos meta-comandos los maneja el ORQUESTADOR directamente (no invocan un skill por nombre) — son instrucciones al LLM en CLAUDE.md que derivan a los skills correctos según el estado. No aparecen en el autocomplete de skills.

**Esfuerzo de adopción:** Medio — `/sdd-status` funciona sin A-03; `/sdd-continue` y `/sdd-ff` se benefician mucho de A-03 para ser confiables.

---

### [A-08] Presupuestos de tamaño por artefacto

**Referencia ATL:** `docs/token-economics.md` → Optimization #2, skill files con word budgets explícitos (proposal: 400 words, spec: 650 words, design: 800 words, tasks: 530 words)

**Problema actual:** Los artefactos de SDD Lab no tienen presupuesto de tamaño. Un spec inflado hace que el plan-architect procese más tokens de los necesarios; un plan inflado hace lo mismo con el task-generator. Los artefactos inflados en fases tempranas se multiplican en todas las fases downstream.

**Por qué importa estructuralmente:** ATL mide ~14.000 tokens ahorrados por pipeline completo solo por reducir el tamaño de los artefactos. Es un multiplicador: cada palabra extra en el spec aparece en el plan, en las tasks, y en el verify.

**Qué adoptar de ATL:**
Presupuestos orientativos por artefacto (señales de revisión, no límites duros):

| Artefacto               | Presupuesto orientativo | Señal si se supera                          |
|-------------------------|-------------------------|---------------------------------------------|
| `_analysis.md`          | ~600 palabras           | Revisar si hay gaps duplicados o vagos      |
| `_discovery.md`         | ~400 palabras           | Revisar si hay features sobredimensionadas  |
| `<feature>_spec.md`     | ~800 palabras           | Revisar si la feature debe dividirse        |
| `<feature>_plan.md`     | ~1.200 palabras         | Revisar si el plan está sobredetallado      |
| `<feature>_tasks.md`    | ~600 palabras           | Revisar si hay tasks demasiado granulares   |

El agente que genera el artefacto debe autocontrolarse. Si supera el presupuesto, debe indicarlo en el return envelope (A-01) como riesgo, no silenciosamente.

**Esfuerzo de adopción:** Bajo — añadir guidelines a los kb- y al phase-common (A-02).

---

### [A-09] Skill Registry con compact rules (migración futura de los kb-)

**Referencia ATL:** `skills/skill-registry/SKILL.md`, `skills/_shared/skill-resolver.md`

**Problema actual:** Los kb- son archivos completos que se cargan como skills en el frontmatter de los agentes. No se puede cargar solo la regla relevante para la tarea actual. A medida que el pipeline crece (spec + plan + tasks + apply + verify), los kb- se multiplican y el coste de cargarlos todos al arrancar sube.

**Por qué importa estructuralmente:** ATL resuelve esto con compact rules: versiones condensadas (5-15 líneas) de cada skill, pre-digeridas por el orquestador, inyectadas solo cuando son relevantes. El ahorro por pipeline completo es ~11.400 tokens según `token-economics.md`.

**Qué adoptar de ATL:**
Cuando el pipeline esté completo (spec + plan + tasks al menos):

1. Crear `skill-registry/SKILL.md` — escanea todos los kb- y genera `.atl/skill-registry.md` con compact rules por skill (5-15 líneas cada una, con trigger de activación).
2. El orquestador ejecuta `skill-registry` una vez por sesión y cachea las compact rules.
3. Para cada delegación, el orquestador inyecta solo las compact rules relevantes en el prompt como `## Reglas del proyecto (auto-resueltas)`.
4. Los agentes worker dejan de tener `skills: [kb-spec-expert, ...]` en su frontmatter.

**Nota:** Requiere A-01, A-02 y A-06 primero — el `skill_resolution` del envelope es la señal de que la inyección funcionó.

**Esfuerzo de adopción:** Alto — es el cambio arquitectónico más profundo. Prioridad baja hasta que el pipeline esté completo.

---

### [A-10] Executor boundary: prohibición explícita de sub-delegación en agentes worker

**Referencia ATL:** `skills/_shared/sdd-phase-common.md` apertura — "every SDD phase agent is an EXECUTOR, not an orchestrator. Do the work yourself. Do NOT launch sub-agents, do NOT call delegate/task, and do NOT bounce work back unless the phase skill explicitly says to stop."

**Problema actual:** Los agentes worker de SDD Lab (`sdd-analyst`, `plan-architect`, `task-generator`) no tienen una declaración explícita de que son ejecutores, no orquestadores. No hay ninguna instrucción que les prohíba lanzar sub-agentes propios. Para tasks complejas, el LLM puede derivar hacia crear sub-agentes dentro de un agente worker, lo que crea una cadena de delegación no controlada por el orquestador.

**Por qué importa estructuralmente:** La cadena de delegación no controlada tiene dos efectos graves: (1) el orquestador pierde visibilidad de qué está pasando — el return envelope nunca llega porque hay un agente intermedio haciendo más trabajo del esperado; (2) el contexto crece de forma no predecible. El principio de ATL es simple: solo el orquestador delega. Los executors ejecutan.

**Qué adoptar de ATL:**
Añadir al inicio de cada agente worker (`sdd-analyst.md`, `plan-architect.md`, `task-generator.md`) y al `phase-common.md` (A-02):

```
Eres un EXECUTOR, no un orquestador.
- Haz el trabajo tú directamente.
- NO lances sub-agentes, NO uses el Agent tool, NO delegues tareas a otros.
- Si encuentras un bloqueo real que no puedes resolver, reporta Status: blocked en el return envelope y detente.
- El único momento en que puedes escalar es hacia arriba (return envelope al orquestador), nunca hacia abajo (delegando a un sub-agente).
```

**Esfuerzo de adopción:** Muy bajo — añadir 4 líneas a cada agente worker y al phase-common.

---

### [A-11] Adversarial review: dual blind review como quality gate

**Referencia ATL:** `skills/judgment-day/SKILL.md` — Parallel Blind Review pattern + Fix loop + Verdict synthesis

**Problema actual:** SDD Lab no tiene un quality gate formal para revisar artefactos. `wf-spec-validate` valida formato y completitud, pero es un único agente que hace una revisión lineal. Un solo revisor tiene puntos ciegos: si el agente generó el spec y el mismo tipo de agente lo valida, los mismos sesgos se reproducen.

**Por qué importa estructuralmente:** El patrón de revisión dual ciega de ATL es genuinamente diferente: dos agentes independientes revisan el mismo artefacto sin saber el uno del otro, sus findings se sintetizan (Confirmed = encontrado por ambos → alta confianza, Suspect = solo uno lo encontró → triage), y solo los confirmed se pasan a un fix agent. Máximo 2 iteraciones; si persisten problemas: escalar al usuario. La tasa de falsos positivos baja dramáticamente.

**Qué adoptar de ATL:**
Skill nuevo `wf-spec-judgment` (análogo a `judgment-day` pero para artefactos SDD) aplicable a:
- Revisión de un spec (`wf-spec-judgment <spec.md>`) — dos agentes revisan el mismo spec en paralelo buscando violaciones de pureza, gaps de cobertura, ambigüedades en CAs, y conflictos con otros specs.
- Revisión del pipeline completo de una feature antes de pasar al plan (`wf-spec-judgment --feature <nombre>`) — revisan spec + discovery + analysis juntos.

Output: tabla de findings con columnas `Judge A | Judge B | Severity | Status (Confirmed/Suspect/Contradiction)`.

El fix loop de ATL (auto-fix de confirmed + re-review) puede adaptarse: los confirmed issues se pasan a `wf-spec-repair` o `wf-spec-delta resolve` automáticamente; los suspects se reportan al usuario para decisión manual.

**Esfuerzo de adopción:** Medio — es un skill nuevo pero el patrón está bien definido en ATL. Puede implementarse cuando el pipeline de specs esté maduro.

---

### [A-12] Config por proyecto: `sdd_config.yaml`

**Referencia ATL:** `skills/sdd-init/SKILL.md` → Step 3 Generate Config, `openspec/config.yaml` structure

**Problema actual:** SDD Lab no tiene configuración por proyecto. Todos los proyectos usan el mismo comportamiento de los skills, con los mismos kb- y las mismas reglas. Si un proyecto tiene convenciones específicas (naming de módulos KMM, estructura de repositorio, reglas de negocio transversales), no hay un lugar donde declararlas para que los agentes las lean al arrancar.

**Por qué importa estructuralmente:** ATL genera un `openspec/config.yaml` en cada proyecto con el stack detectado y reglas por fase. Esto permite que el mismo pipeline se adapte a proyectos distintos sin tocar los skills. En SDD Lab, con el foco en KMM, la config por proyecto permitiría declarar el naming de módulos, las reglas de Clean Architecture del proyecto específico, y el threshold de cobertura de tests esperado.

**Qué adoptar de ATL:**
`wf-init-sdd` genera `sdd_config.yaml` en la raíz del proyecto:

```yaml
# sdd_config.yaml — generado por wf-init-sdd, no editar manualmente
schema: sdd-v1
project: nombre-del-proyecto
stack:
  platform: KMM
  modules: [":app", ":feature:X", ":core:Y"]   # detectado del build.gradle
  architecture: clean-architecture

rules:
  spec:
    - Pureza funcional estricta — ningún componente técnico KMM en specs
    - Shared models solo en la feature owner declarada en _features.md
  plan:
    - Cada componente del plan debe referenciar su CA de origen
    - No duplicar modelos de dominio declarados como shared en _features.md
  tasks:
    - Máximo 4h de trabajo estimado por task
    - Cada task debe referenciar su skill de implementación
  verify:
    coverage_threshold: 80
    test_command: ./gradlew test
```

Los agentes worker leen este archivo al arrancar (antes de procesar cualquier PRD o spec) para adaptar su comportamiento al proyecto concreto. Es la capa de personalización entre el pipeline genérico y el proyecto específico.

**Esfuerzo de adopción:** Medio — requiere actualizar `wf-init-sdd` para generar el archivo y añadir la lectura de config al protocol `phase-common.md` (A-02).

---

### [A-13] Parámetro `detail_level` para controlar verbosidad de output

**Referencia ATL:** `skills/_shared/persistence-contract.md` → Detail Level section

**Problema actual:** Los skills de SDD Lab siempre producen el mismo nivel de detalle en su output al usuario, independientemente del contexto. A veces el orquestador solo necesita saber si el skill terminó correctamente (`Status: success`) sin leer el informe completo. Otras veces necesita el informe detallado para reportar al usuario. No hay forma de solicitarlo.

**Por qué importa estructuralmente:** ATL distingue que el nivel de detalle del output y lo que se persiste son independientes. Siempre se persiste el artefacto completo; la verbosidad del output al orquestador es configurable. Esto reduce el tráfico de tokens entre fases cuando el orquestador solo necesita confirmación de estado.

**Qué adoptar de ATL:**
El orquestador puede pasar `detail_level` al invocar un skill:
- `concise` — solo el return envelope (Status, Summary, Artifacts, Next, Risks). Sin el artefacto completo en el output.
- `standard` — envelope + resumen del artefacto generado (headers y puntos clave).
- `deep` — envelope + artefacto completo en el output.

Regla invariante: **el artefacto siempre se persiste completo en el filesystem**, independientemente del detail_level. El detail_level controla lo que el skill devuelve al orquestador en el mensaje de respuesta, no lo que escribe en disco.

Uso típico: el orquestador usa `concise` cuando lanza múltiples skills en paralelo (solo necesita confirmar que terminaron), y `standard` o `deep` cuando el output va a mostrarse al usuario.

**Esfuerzo de adopción:** Bajo — añadir soporte en el `phase-common.md` (A-02) y en el "Paso N: Informar al usuario" de cada skill.

---

### [A-14] Rollback plan como concepto de primera clase

**Referencia ATL:** `skills/sdd-propose/SKILL.md` → Rollback Plan (sección obligatoria), `skills/sdd-init/SKILL.md` → config.yaml rules.proposal

**Problema actual:** SDD Lab no tiene ningún concepto de reversibilidad en ninguna parte del pipeline. Los specs describen qué debe hacer el sistema cuando la feature existe, pero no qué pasa si hay que deshacer la feature o revertir un cambio en un spec. Si un delta apply introduce un error en un spec, o si una feature en producción tiene que desactivarse, no hay artefacto de referencia para hacerlo.

**Por qué importa estructuralmente:** ATL obliga a declarar el rollback plan antes de empezar cualquier change. Esto no es burocracia — es un filtro de calidad. Si no puedes articular cómo deshacer algo, probablemente no entiendes bien qué estás construyendo. Para SDD Lab, la reversibilidad aplica en dos niveles: (1) a nivel de spec (cómo deshacer un delta apply), y (2) a nivel de feature (qué implica desactivar esta feature para el usuario y el sistema).

**Qué adoptar de ATL:**
Dos cambios:

1. **En `wf-spec-propose` (A-S09 del TODO de specs)**: el documento de propuesta debe incluir obligatoriamente:
   ```
   ## Rollback
   Si esta feature hay que desactivarla tras implementación: [descripción funcional de qué deja de funcionar y qué datos/estado quedan afectados]
   ```

2. **En `wf-spec-delta apply`**: antes de sobreescribir el spec, además del archive (S-08 del TODO de specs), añadir en el Changelog del spec una sección "Reversión":
   ```
   ### Cómo revertir v1.1 → v1.0
   - Restaurar desde `archive/<nombre>_spec_v1.0.md`
   - Eliminar HU-007, HU-008 y sus CAs CA-012 a CA-018
   - Revertir la sección "Instrucciones Inambiguas" — eliminar reglas R-004 y R-005
   ```
   Esta sección la genera el agente automáticamente a partir del delta analysis — sabe exactamente qué añadió y qué modificó, así que puede invertirlo.

**Esfuerzo de adopción:** Bajo-medio — modificar `wf-spec-delta apply` para generar la sección de reversión, y añadir el campo al template del proposal skill.

---

### [A-15] Versioning en el frontmatter de los SKILL.md

**Referencia ATL:** todos los SKILL.md tienen `metadata: { author: ..., version: "2.0" }` y `license: MIT|Apache-2.0`

**Problema actual:** Los skills de SDD Lab no tienen versión en su frontmatter. Cuando un skill se modifica, no hay forma de saber qué versión del skill generó un artefacto determinado. En proyectos en los que el artefacto (`_spec.md`) fue generado hace meses, no hay trazabilidad entre el artefacto y la versión del skill que lo produjo.

**Por qué importa estructuralmente:** Cuando el sistema tenga varios proyectos activos usando el pipeline, la versión del skill que generó un artefacto se vuelve relevante para entender por qué el artefacto tiene determinada estructura o por qué le falta algo. La versión también es la señal de que un artefacto debe regenerarse porque el skill que lo produjo fue actualizado sustancialmente.

**Qué adoptar de ATL:**
Añadir en el frontmatter de cada SKILL.md:
```yaml
metadata:
  version: "1.0"
  changelog: |
    1.0 — inicial
```

Y en el header de cada artefacto generado, añadir el skill y versión que lo produjo:
```markdown
> Generado via: wf-spec-fast-track v1.2 | wf-spec-features-first v1.0
> Fecha: 2026-04-07
```

El campo `Generado via` ya existe en el template del spec (`feature_spec_template.md`) — solo falta añadir la versión del skill.

**Esfuerzo de adopción:** Muy bajo — añadir el campo `metadata.version` a cada SKILL.md y actualizar el template para incluir la versión en el header del artefacto.

---

### [A-16] Simplificar la capa de agentes worker (alinearse con el modelo ATL)

**Referencia ATL:** no existe una capa de "agentes worker" separada — cada SKILL.md es directamente las instrucciones del agente executor. No hay intermediario.

**Problema actual:** SDD Lab tiene tres capas: (1) workflow skills (`wf-`), (2) agentes worker (`sdd-analyst.md`, `plan-architect.md`, `task-generator.md`), y (3) knowledge bases (`kb-`). Los workflow skills delegan a los agentes worker que cargan los kb- via su frontmatter `skills: [...]`. Esto crea una cadena de indirección: el skill dice qué hacer, el agente sabe las reglas, los kb- contienen el conocimiento.

La capa de agentes worker tiene valor hoy porque agrupa los `skills: [...]` que cargan los kb-. Pero con A-09 (Skill Registry + compact rules), esa capa pierde su razón de ser — el orquestador inyecta las reglas directamente, los agentes no necesitan un frontmatter con los kb-.

**Por qué importa estructuralmente:** Tres capas es más complejo de mantener que dos. Cada vez que se añade un kb- nuevo, hay que actualizar el agente worker. Cada vez que se añade un workflow skill, hay que decidir si necesita un agente worker nuevo o reutiliza uno existente. ATL demuestra que una arquitectura de dos capas (orquestador + executors) es suficiente.

**Qué adoptar de ATL:**
Esta es una migración a largo plazo, no inmediata:

1. **Fase actual (ahora):** mantener los tres niveles. Los agentes worker siguen siendo la capa de configuración de skills.
2. **Tras A-09 (Skill Registry):** los agentes worker se simplifican a solo una declaración de `model:` y `permissionMode:`, sin `skills: [...]` en el frontmatter.
3. **Madurez final:** evaluar si la capa de agentes worker puede colapsar directamente en el frontmatter de cada workflow skill (`wf-spec-fast-track` declara su propio `model: sonnet` y `permissionMode: acceptEdits`), eliminando los archivos de agentes worker por completo.

La simplificación final solo tiene sentido con A-09 implementado. Sin el Skill Registry, los agentes worker son necesarios para gestionar los kb-.

**Esfuerzo de adopción:** Bajo inicialmente (no hacer nada hasta A-09). Alto como migración final (requiere reescribir frontmatters y eliminar archivos). Marcar como dependiente de A-09.

---

## Orden de implementación sugerido (v2)

### Bloque 1 — CLAUDE.md (sin dependencias, máximo ROI mínimo esfuerzo)

| # | Mejora | Esfuerzo |
|---|---|---|
| 1 | [A-04] Routing de modelos | Muy bajo |
| 2 | [A-05] Reglas de delegación + anti-patrones | Muy bajo |
| 3 | [A-10] Executor boundary en agentes worker | Muy bajo |
| 4 | [A-15] Version metadata en SKILL.md | Muy bajo |

### Bloque 2 — Protocolo de comunicación entre fases

| # | Mejora | Dependencias | Esfuerzo |
|---|---|---|---|
| 5 | [A-01] Return envelope estandarizado | — | Bajo |
| 6 | [A-02] Protocolo compartido `_shared/` | A-01 | Medio |
| 7 | [A-08] Presupuestos de tamaño | A-02 | Bajo |
| 8 | [A-13] Parámetro detail_level | A-01, A-02 | Bajo |
| 9 | [A-06] Self-healing detección de compactación | A-01, A-02 | Bajo |

### Bloque 3 — Estado del pipeline y UX

| # | Mejora | Dependencias | Esfuerzo |
|---|---|---|---|
| 10 | [A-12] Config por proyecto sdd_config.yaml | A-02 | Medio |
| 11 | [A-03] DAG con _sdd_state.yaml | A-01, A-02, A-12 | Medio-alto |
| 12 | [A-07] Meta-comandos orquestador | A-03 | Medio |
| 13 | [A-14] Rollback plan como concepto | A-02 | Bajo-medio |

### Bloque 4 — Calidad y escala (cuando pipeline esté completo)

| # | Mejora | Dependencias | Esfuerzo |
|---|---|---|---|
| 14 | [A-11] Adversarial dual review | A-02 + specs maduros | Medio |
| 15 | [A-09] Skill Registry + compact rules | Pipeline completo | Alto |
| 16 | [A-16] Simplificar capa agentes worker | A-09 | Alto |

---

## Resumen de nuevos items en v2

Los A-01 a A-09 son del documento v1 (refinados). Los siguientes son nuevos en v2:

| Item | Origen en ATL | Por qué no estaba en v1 |
|---|---|---|
| A-10 | `sdd-phase-common.md` apertura | No se había leído el archivo en detalle |
| A-11 | `judgment-day/SKILL.md` completo | Skill no analizado en detalle en v1 |
| A-12 | `sdd-init/SKILL.md` Step 3 + config.yaml | Lectura superficial de sdd-init en v1 |
| A-13 | `persistence-contract.md` Detail Level | No se había leído persistence-contract |
| A-14 | `sdd-propose/SKILL.md` + reglas de config | Propuesta no analizada en detalle |
| A-15 | Frontmatter de todos los SKILL.md ATL | Detalle de frontmatter no analizado |
| A-16 | Arquitectura general ATL (2 capas vs 3) | Análisis implícito, no explicitado |
