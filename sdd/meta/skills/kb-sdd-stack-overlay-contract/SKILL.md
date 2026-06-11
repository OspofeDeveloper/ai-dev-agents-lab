---
name: kb-sdd-stack-overlay-contract
description: "Contrato que debe cumplir un overlay de stack (tech/<stack>): piezas obligatorias y opcionales, override por nombre sobre las genericas de plan/tasks, init especialista con project state, registro en project-init.json e integracion con wf-project-init y los gates. No cubre la estructura de directorios (kb-sdd-skill-architecture R16) ni las convenciones de creacion (kb-sdd-creation-guide)."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KB SDD Stack Overlay Contract

Un **overlay de stack** es el paquete `tech/<stack>/` que especializa las fases `plan` y `tasks` (y opcionalmente la implementación) para una tecnología concreta. Las fases `prd`, `spec` y `design` son neutrales: un overlay nunca las modifica.

Principio rector: **el modo genérico es el caso base; el overlay especializa, nunca habilita.** Un proyecto sin overlay debe poder recorrer el pipeline completo (specs → plan → tasks → implementación por el orquestador). El overlay sustituye piezas genéricas por variantes expertas, no añade capacidades que el pipeline genérico no tenga.

---

## Piezas obligatorias

| Pieza | Path | Responsabilidad |
|---|---|---|
| Installer del overlay | `tech/<stack>/install.sh` | Copia agentes y skills del overlay al `.claude` del proyecto destino. Se ejecuta SIEMPRE después del install base de fases |
| Init especialista | `tech/<stack>/skills/wf-<stack>-init/` | Genera `<stack>_project_state.md` con el estado técnico real del proyecto. Modos `detect` (exploración de proyecto existente) y `configure` (preguntas para proyecto nuevo). Registra su ejecución (append-only, una línea JSON por run) en `.sdd/stack-runs.jsonl` — nunca en un array dentro de `project-init.json` (config compartida = conflicto de merge) |
| Project state | `<stack>_project_state.md` (raíz del proyecto destino) | SSoT del estado técnico: targets, arquitectura, librerías, comandos de build/test. Lo leen todos los agentes del stack antes de operar. Puede declarar legítimamente comandos degradados o ausentes (`tests: none`, `build: manual\|none`) — ver "Estado de tooling degradado" |
| CLAUDE.md del overlay | `tech/<stack>/CLAUDE.md` | Orquestador del stack: rootmap de sus `wf-*`, tabla de sus agentes y principios de delegación |

## Piezas opcionales

| Pieza | Cuándo aportarla |
|---|---|
| Variantes por override de `plan-architect`, `plan-auditor`, `task-generator` (`tech/<stack>/agents/`, mismo nombre de archivo) | Cuando el stack tiene arquitectura prescriptiva propia (capas, módulos, convenciones) que el plan/tasks debe imponer |
| Variantes por override de `kb-plan-expert` (`skills/plan/`) y `kb-tasks-expert` (`skills/tasks/`) | Acompañan a las variantes de agentes: mismo contrato metodológico, contenido especializado |
| KBs de stack para plan (`skills/plan/kb-*`) y tasks (`skills/tasks/kb-*`) | Conocimiento por dominio (DI, networking, navegación, testing...). Separación estricta: KBs de plan planifican, KBs de tasks implementan |
| Agentes de implementación propios (`agents/<stack>-*.md`) | Cuando las tasks se delegan a workers especializados en vez del orquestador |
| Workflows de setup (`skills/wf-<stack>-*`) | Pipelines cerradas de configuración (auth, networking, environments...) |
| Protocolo de project state (`skills/kb-<stack>-project-state-protocol`) | Cuando hay agentes propios que deben leer el project state como precondición |

---

## Mecanismo de override por nombre

1. `install.sh` (base) instala las piezas genéricas de fase en `<fase>/.claude/` del proyecto.
2. `tech/<stack>/install.sh` se ejecuta **después** y copia por basename (`rm -rf` + copia): toda pieza del overlay con el mismo nombre que una genérica la **sustituye**.

> **Limitación transitoria conocida (single-stack).** El override por basename sobre un único `.claude/` raíz hace que **solo pueda haber un overlay activo por repositorio**: dos stacks compartiendo proyecto colisionarían sobre los mismos archivos genéricos. Es una limitación reconocida, no un invariante de diseño. El modelo objetivo que la levanta vive en la sección [Modelo objetivo: multi-stack por ubicación](#modelo-objetivo-multi-stack-por-ubicación-roadmap-61--diseño-no-implementado). Hasta entonces: **ningún overlay ni pieza nueva debe profundizar la suposición de stack único** (objetivo "no cavar más hondo" de ROADMAP 6.1). En concreto, las piezas nuevas no deben leer un stack global como verdad fija más allá de lo que ya hacen los gates de hoy, ni hardcodear el supuesto de "un solo `<stack>_project_state.md`" en sitios nuevos.

Reglas para una variante válida:

- **Conserva el contrato externo**: misma metodología, misma taxonomía de gaps (`DESIGN_GAP`/`TECH_GAP`/`TRACE_GAP`/`PLAN_GAP`), mismos estados (`BORRADOR`/`VALIDADO`), mismo formato de artefacto de salida y misma regla canónica de Design. Solo especializa el **cómo** (capas, librerías, owners, templates).
- **No re-copies el procedimiento metodológico**: el cuerpo de las variantes de `plan-architect`, `plan-auditor` y `task-generator` **carga la KB de método compartida** (`kb-plan-method` para los de plan, `kb-tasks-method` para task-generator) en su frontmatter `skills:` y solo aporta la **capa de especialización** sobre los hooks `‹especialización de stack›` que esas KBs marcan. Las method KB **no se sobreescriben** (no tienen variante de stack): viven en `plan/skills/` y `tasks/skills/`, las instala la base y las cargan por nombre tanto la variante genérica como la del overlay (mismo mecanismo cross-fase que `kb-a11y-expert`). Esto evita que cada cambio metodológico haya que replicarlo en N agentes.
- Los workflows de fase (`wf-prepare-plan`, `wf-prepare-tasks`, `wf-plan-validate`) **nunca** se sobreescriben: son neutrales y resuelven el stack por los gates.
- Los owners de tasks en la variante son los agentes del stack; en la genérica, `orquestador`.

---

## Puntos de integración con el ecosistema

| Punto | Qué debe ocurrir |
|---|---|
| `wf-project-init` Paso 4 (detección silenciosa) | Añadir la condición de detección del stack a la tabla (archivos/patrones que lo delatan) |
| `wf-project-init` Paso 8 (despacho) | Si las fases incluyen `plan`/`tasks` y existe `wf-<stack>-init`, se invoca via Skill tool. El overlay queda registrado: `"stack": "<stack>"`, `"specialist_workflow": "wf-<stack>-init"` |
| Gates de `wf-prepare-plan` / `wf-prepare-tasks` | Con `specialist_workflow` no nulo exigen `<stack>_project_state.md`; el init especialista DEBE generarlo o el pipeline queda bloqueado |
| `sdd/meta/skill-registry.md` | Ejecutar `wf-sdd-status` tras crear o modificar el overlay |

---

## Invariantes

1. **No romper el modo genérico**: eliminar el overlay de un proyecto (o no instalarlo) deja un pipeline funcional.
2. **Idempotencia**: reinstalar el overlay produce el mismo resultado; `wf-<stack>-init` detecta estado previo y pregunta antes de rehacer.
3. **Project state como precondición, no como cache**: si el proyecto cambia de forma relevante, se regenera con `wf-<stack>-init --force`; los agentes no lo editan a mano.
4. **El overlay no toca `prd/`, `spec/` ni `design/`** del proyecto destino.
5. **Cierre verificable de los agentes implementadores**: todo agente del overlay que modifique código debe cerrar con verificación ejecutable — build de los módulos afectados y tests relevantes usando los comandos declarados en `<stack>_project_state.md`, reporte honesto del comando y su salida real (un fallo se reporta tal cual, nunca como éxito), y declaración explícita "verificación ejecutable: no disponible — <motivo>" cuando no se pueda ejecutar nada. Es la contraparte dentro del agente de lo que `wf-task-run` (Paso 6) y `wf-bug` (Paso 4) exigen desde fuera. La concreción del contrato vive en la KB de protocolo del stack (referencia canónica: `kb-kmm-project-state-protocol`, Regla 6) y los agentes la referencian con una sección corta de cierre, sin reescribirla inline. **Degradación con `tests: none`**: cuando el `<stack>_project_state.md` declara `tests: none` (sin runner) o un `build:` degradado, el invariante se satisface con la declaración explícita ya prevista por el contrato ("verificación ejecutable: no disponible — `tests: none` declarado en `<stack>_project_state.md`"), no exigiendo una suite verde inexistente — ver "Estado de tooling degradado". La honestidad queda intacta: prohibido declarar "tests pasan" sin tests o maquillar la ausencia como verificación.
6. **El repo destino manda sobre el dogma del stack**: la arquitectura prescriptiva de un overlay (capas, DI, tipo de resultado, organización de módulos, recursos...) es el **default del stack para greenfield o donde el repo no se ha pronunciado**, no una imposición. Cuando el repositorio destino ya resuelve algo de otra forma —reflejado en `<stack>_project_state.md`— **sus convenciones reales tienen precedencia** y el plan/tasks/implementación las respetan, justificándolo. El canon del stack solo rellena los huecos donde el repo no tiene opinión; nunca sobrescribe convenciones divergentes ya presentes. Imponer el dogma del stack sobre un repo que diverge rompe el invariante 1 (no romper el modo genérico) y es el mismo fallo que inventar en agnóstico. La concreción por stack vive en su KB de protocolo (referencia canónica: `kb-kmm-project-state-protocol`, Regla 7); el método de plan/tasks lo aplica vía el hook "Overlay de stack" de `kb-plan-method` / `kb-tasks-method`.

---

## Estado de tooling degradado (stacks legacy sin tests ni módulos)

El contrato asume un stack con tooling moderno (runner de tests, build reproducible, sistema de módulos). Un stack o repo **legacy** (PHP 5 plano, scripts sin runner, monolito de paquete único) puede no tenerlo. Eso **no lo deja fuera del ecosistema**: el contrato degrada con gracia declarando el estado honestamente, sin inventar comandos inexistentes ni fingir verificación.

### `tests: none` / `build: manual|none` como estado declarado válido

El `<stack>_project_state.md` puede declarar legítimamente, en su sección de comandos build/test:

- `tests: none` — el proyecto no tiene runner de tests instalado.
- `build: manual` / `build: none` — no hay paso de build reproducible (deploy por copia, intérprete directo).

Esto es un **estado HONESTO declarado**, no una instalación rota ni un hueco a rellenar inventando un comando que no existe. El init especialista (`wf-<stack>-init`) lo escribe cuando la detección no encuentra tooling; los agentes lo leen y operan en consecuencia. Declarar `tests: none` es correcto; inventar un `npm test` que nadie puede ejecutar, no.

### Degradación del invariante 5

Con `tests: none` declarado, el cierre verificable (invariante 5) se satisface con la **declaración explícita** ya prevista por el propio invariante:

> `verificación ejecutable: no disponible — tests: none declarado en <stack>_project_state.md`

No se exige una suite verde que no existe. Lo que el invariante sigue prohibiendo sin excepción: declarar "tests pasan" sin tests, o maquillar la ausencia de tooling como si fuera verificación. La honestidad del reporte es innegociable; lo que se relaja es la *exigencia de suite verde*, no la *exigencia de honestidad*. Análogamente, un `build: manual` cierra reportando el paso manual real ejecutado (o su no disponibilidad), no un build verde ficticio.

### Characterization-first: `tests: none` es punto de partida, no estado final

`tests: none` es un punto de **partida a remontar**, no un estado final cómodo. La guía para un repo legacy que entra al pipeline es establecer **characterization tests primero** —tests que fijan el comportamiento observable actual antes de tocar nada— para construir la red de seguridad de la que el legacy carece. Esa es la SSoT de `kb-spec-characterization` (specs de caracterización brownfield, degradación sin tests) y el onramp es `wf-spec-from-code`. Aquí solo se apunta: el overlay no redefine cómo se caracteriza, lo referencia.

### Monolitos sin módulos en plan/tasks

Cuando el repo es un monolito sin sistema de módulos, la descomposición del plan y los cortes de PR no pueden apoyarse en fronteras de módulo. El criterio de descomposición por **capas/fronteras lógicas** vive en `kb-plan-expert` (genérico); el de empaquetado de PRs a lo largo de esas costuras, en `kb-delivery-discipline`. El overlay no los reescribe: hereda el caso base genérico, que ya contempla el monolito.

---

## Modelo objetivo: multi-stack por ubicación (ROADMAP 6.1 — diseño, no implementado)

Esta sección es **normativa para la dirección del diseño, no para la implementación de hoy**. Describe el contrato OBJETIVO al que el ecosistema debe poder migrar sin reescritura cuando exista un 2º overlay real (ROADMAP 6.5). No hay resolver implementado todavía (ROADMAP 6.1 explícitamente lo difiere); el propósito de fijarlo ahora es evitar que las piezas nuevas caven más hondo en el supuesto de stack único.

### Declaración de stacks en `project-init.json`

| Forma | Declaración | Estado |
|---|---|---|
| **Stack único (transitoria)** | `"stack": "<stack\|agnostico\|null>"` + `"specialist_workflow": "<wf-<stack>-init\|null>"` | Forma **actual y transitoria**. Es el caso de un solo overlay (o ninguno) por repo. Sigue siendo válida y es lo que produce hoy `wf-project-init`. |
| **Multi-stack (objetivo)** | `"stacks": [ { "path": "<ruta-raíz-del-subproyecto>", "stack": "<stack>", "specialist_workflow": "wf-<stack>-init" }, ... ]` | Forma **destino**. Cada entrada asocia una **ubicación del repo** (módulo, paquete, subdirectorio) con su stack y su init especialista. `"stack": "<único>"` se reinterpreta entonces como el azúcar de un `stacks` de un solo elemento con `path` = raíz del proyecto. |

La migración es aditiva: un proyecto single-stack existente equivale a `stacks: [{ path: ".", stack: <su stack>, specialist_workflow: <el suyo> }]`. Ningún consumidor del modelo objetivo debe romper al leer la forma transitoria.

### Regla de resolución por ubicación de la feature

En el modelo objetivo, **qué variante de stack aplica se resuelve por la UBICACIÓN de la feature, no por una variable global del proyecto**. Los gates de `wf-prepare-plan`/`wf-prepare-tasks` (y los workflows que dependen de ellos) resuelven, para la feature concreta sobre la que operan, qué entrada de `stacks` cubre su ruta — y exigen el `<stack>_project_state.md` de ESE stack, no de un stack único global. Una feature cuya ubicación no cae bajo ninguna entrada de `stacks` opera en modo genérico (caso base del pipeline).

Hoy esa resolución vive en **prosa de los workflows/gates** (la tabla de "Puntos de integración" decide por el campo global `specialist_workflow`). El modelo objetivo la lleva a una **resolución determinista por ruta en los gates**: misma decisión, pero parametrizada por la ubicación de la feature en lugar de por un único campo de proyecto. Mientras 6.1 no se implemente, los gates siguen leyendo el campo único; lo que esta sección fija es que el punto de decisión correcto es el gate (determinista), no nueva prosa dispersa ni una variable global ampliada.

### Qué NO incluye este diseño

- **No** especifica el algoritmo del resolver (prefijo más largo de ruta, glob, precedencia entre entradas solapadas): queda para 6.1-implementación, cuando un 2º overlay real (6.5) dé los casos de prueba.
- **No** cambia el mecanismo de override por basename: levantar la exclusividad mutua de overlays sobre un único `.claude/` raíz es parte de la implementación, no del contrato.
- **No** toca `install.sh`, el schema real de `project-init.json` ni los gates. Es solo el contrato/diseño.

---

## Checklist de conformidad

- [ ] `tech/<stack>/install.sh` ejecutable y con el mismo mecanismo de copia por basename
- [ ] `wf-<stack>-init` con modos detect/configure, manejo de estado previo y registro del run (append-only) en `.sdd/stack-runs.jsonl`
- [ ] `<stack>_project_state.md` generado con secciones mínimas: targets/runtime, arquitectura, dependencias clave, y comandos build/test **o** su ausencia declarada explícitamente (`tests: none`, `build: manual\|none`) con la estrategia de caracterización — ver "Estado de tooling degradado"
- [ ] Agentes implementadores con contrato de cierre verificable (invariante 5): sección de cierre que referencia la regla del protocolo del stack
- [ ] El repo destino manda sobre el dogma (invariante 6): el canon del stack es default para greenfield/silencio del repo; la KB de protocolo del stack declara que las convenciones reales del `<stack>_project_state.md` tienen precedencia cuando divergen
- [ ] Variantes de override (si las hay) conservan el contrato externo de la pieza genérica
- [ ] Variantes de `plan-architect`/`plan-auditor`/`task-generator` cargan la method KB compartida (`kb-plan-method`/`kb-tasks-method`) y solo aportan la especialización de stack — no re-copian el procedimiento
- [ ] Condición de detección añadida a `wf-project-init` Paso 4
- [ ] No cava más hondo en stack único (ROADMAP 6.1): la pieza nueva no introduce una nueva variable global de stack ni hardcodea "un solo `<stack>_project_state.md`" en sitios nuevos; la resolución de stack, si la necesita, la delega al gate
- [ ] Registrado en `skill-registry.md` via `wf-sdd-status`
