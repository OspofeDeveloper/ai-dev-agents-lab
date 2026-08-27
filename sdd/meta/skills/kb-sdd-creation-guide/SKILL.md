---
name: kb-sdd-creation-guide
description: "El COMO de crear y registrar piezas del ecosistema SDD: convenciones de nombrado, ubicacion por tipo y fase, plantillas de frontmatter, estructura de contenido y checklist de registro de skills (kb-*, wf-*) y agentes. Complementa kb-sdd-skill-architecture, que define el cuando."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KB SDD Creation Guide

Guia operativa para materializar decisiones de diseño del ecosistema SDD. Las reglas de _cuando_ y _por que_ crear cada pieza viven en `kb-sdd-skill-architecture`. Esta KB cubre el _como_.

## Convenciones de nombrado

### `kb-*`

Patron: `kb-<fase>-<dominio>` para skills de fase. `kb-sdd-<dominio>` para skills transversales.

Correcto:
- `kb-spec-expert` — dominio de lectura de specs en fase spec
- `kb-design-expert` — contrato visual en fase design
- `kb-plan-expert` — reglas de plan tecnico en fase plan
- `kb-sdd-skill-architecture` — arquitectura transversal del ecosistema

Incorrecto:
- `kb-spec` — demasiado generico, no describe el dominio
- `kb-design-expert-v2` — no versionar con sufijo; actualizar la KB existente

### `wf-*`

Patron: `wf-<fase>-<accion>[-<complemento>]` para workflows de fase. `wf-<accion>[-<complemento>]` para workflows transversales.

Correcto:
- `wf-spec-analyze` — accion: analizar en fase spec
- `wf-design-system` — artefacto destino: system en fase design
- `wf-prepare-plan` — accion: preparar artefacto plan
- `wf-skill-create` — workflow transversal de creacion de skills

Incorrecto:
- `wf-spec-and-design-create` — dos acciones, violar SRP
- `wf-generar-spec` — mezcla idiomas; usar ingles para la nomenclatura tecnica

### Agentes

Patron: `<fase>-<rol>` para agentes de fase. `<stack>-<rol>` para agentes de stack. `sdd-<rol>` para agentes transversales.

Correcto:
- `design-system-architect` — rol architect en fase design
- `sdd-spec-writer` — rol writer en fase spec con prefijo ecosistema
- `plan-architect` — rol architect en fase plan
- `kmm-planner` — rol planner en stack kmm
- `sdd-author` — rol author transversal del ecosistema SDD

## Ubicacion segun tipo y alcance

| Tipo | Alcance | Directorio |
|---|---|---|
| `kb-*` | Fase unica | `sdd/<fase>/skills/kb-<nombre>/SKILL.md` |
| `kb-*` | Cross-fase o transversal | `sdd/meta/skills/kb-<nombre>/SKILL.md` |
| `kb-*` | Stack, nivel plan | `sdd/tech/<stack>/skills/plan/kb-<nombre>/SKILL.md` |
| `kb-*` | Stack, nivel tasks | `sdd/tech/<stack>/skills/tasks/kb-<nombre>/SKILL.md` |
| `wf-*` | Fase unica | `sdd/<fase>/skills/wf-<nombre>/SKILL.md` |
| `wf-*` | Cross-fase o meta | `sdd/meta/skills/wf-<nombre>/SKILL.md` |
| `wf-*` | Stack | `sdd/tech/<stack>/skills/wf-<stack>-<nombre>/SKILL.md` |
| Agente | Fase unica | `sdd/<fase>/agents/<nombre>.md` |
| Agente | Cross-fase o meta | `sdd/meta/agents/<nombre>.md` |
| Agente | Stack | `sdd/tech/<stack>/agents/<nombre>.md` |

**Regla de resolucion de agentes:** cuando una `wf-*` declara `agent: <nombre>`, el agente se busca en el directorio `agents/` al mismo nivel que `skills/` dentro de la misma rama del directorio.

- Workflow en `sdd/pipeline/design/skills/` → agente en `sdd/pipeline/design/agents/`
- Workflow en `sdd/meta/skills/` → agente en `sdd/meta/agents/`
- Workflow en `sdd/tech/kmm/skills/` → agente en `sdd/tech/kmm/agents/`

## Frontmatter para `kb-*`

Campos obligatorios: `name`, `description`, `effort`, `allowed-tools`, `user-invocable`.
Nunca añadir `context: fork`, `agent:` ni `argument-hint` a una `kb-*`.

→ Template completo: `${CLAUDE_SKILL_DIR}/references/frontmatter-templates.md`

## Estructura del cuerpo de una `kb-*`

Dos formatos válidos; la elección depende del tipo de contenido:

**Formato A — Reglas numeradas (`## Regla N: <enunciado>`):** usar cuando la skill contiene reglas discretas y cross-referenciables. Permite que workflows y agentes citen "Regla N de kb-X". Es el formato preferido para la mayoría de `kb-*` técnicas y de stack.

**Formato B — Secciones descriptivas (`## <Título descriptivo>`):** usar cuando la skill describe un proceso, criterios de decisión complejos o tiene estructura narrativa. Apropiado para skills meta y skills con pocas reglas largas.

No mezclar ambos formatos dentro de una misma skill.

Para `kb-*` de nivel `tasks/`, la estructura mínima recomendada es:
1. Referencia a la `kb-*` de nivel `plan/` equivalente (si existe)
2. Templates o código concreto por sección
3. Checklist de implementación (opcional pero recomendado)

→ Template de estructura: `${CLAUDE_SKILL_DIR}/references/body-templates.md`

## Criterios de densidad

Los límites son señales de SRP, no hard caps. Superarlos es una invitación a revisar si la pieza está bien cortada, no un error automático.

| Tipo | Objetivo (líneas de body) | Si supera |
|---|---|---|
| `kb-*` normativa o meta | ≤ 300 | Revisar SRP: candidata a dividir → `wf-sdd-refactor` |
| `kb-*` de stack `tasks/` | ≤ 500 | Contiene templates de código — si supera, dividir por submódulo |
| `wf-*` body (sin frontmatter) | ≤ 150 | Mover pasos detallados a `references/` |

El frontmatter no cuenta. El contador parte desde la primera línea del body (`# <Título>`).

## Frontmatter para `wf-*`

`context: fork` se usa en las `wf-*` **no interactivas** que generan artefactos o delegan a un agente: aísla el contexto del trabajo pesado.

**Excepción dura — fork ⊥ `AskUserQuestion`:** una `wf-*` que use `AskUserQuestion` **NO puede llevar `context: fork`**. `AskUserQuestion` (y otras tools que dependen de la UI del hilo principal) **no está disponible en subagentes ni forks** — falla aunque esté en `allowed-tools`. Una skill forkeada que intente preguntar falla en silencio y el orquestador acaba improvisando la interacción (no determinista). Por tanto:

- Skill **interactiva** (usa `AskUserQuestion`) → **sin `context: fork`**: corre en el hilo principal, donde sí puede preguntar.
- ¿Necesita además trabajo pesado / un agente? La delegación es **ortogonal al fork**: invoca al agente vía la tool `Agent` (declara `Agent` en `allowed-tools` y nómbralo en el cuerpo). El subagente aísla su contexto igual de bien, y la interacción se queda donde debe estar.
- El campo `agent:` es el destino de inyección del fork; **sin `context: fork` no se usa** (delega por `Agent` en el cuerpo).

El linter aplica esto como blocking: `FORK-ASKUSER-CONFLICT`.

**Un fork no orquesta ([[D-045]]).** Si una `wf-*` **delega** por la tool `Agent`, **no lleva `context: fork`**: corre en el hilo principal. Dos motivos independientes, y basta cualquiera de los dos:

- **No puede preguntar.** Una skill que delega casi siempre tiene gates —precondiciones, overrides `--allow-*`, elección de alcance— y `AskUserQuestion` no existe dentro de un subagente. El fork acaba parando y devolviendo el bloqueo para que el hilo principal improvise la pregunta y **re-invoque el workflow entero**, repitiendo todo lo ya hecho.
- **No puede conseguir el primer plano.** Con fork mode activo —el default en sesiones interactivas— Claude Code lanza los subagentes en background y **un subagente no puede pedir el primer plano para sus delegados**. La delegación síncrona solo se obtiene desde el hilo principal. (El campo `background: false` del frontmatter, Claude Code ≥ v2.1.218, gobierna el fork **propio** de la skill, no las delegaciones que ese fork emite.)

`context: fork` es para **workers**: skills que hacen su trabajo y le reportan a quien las llamó. Esas declaran `agent:` y no delegan. Una skill sin `agent:` que delega es un orquestador, y su sitio es main.

**Delegación: un solo mecanismo, y el resultado se recibe, no se deduce ([[D-043]], corregida por [[D-045]]).** Una `wf-*` que delega **nombra la tool exacta en cada punto de delegación**, no "invoca `/wf-x`": un hueco lo rellena el agente en ejecución y elige mal — y `allowed-tools` no lo impide, porque **no es enforcement duro** ([[D-038]]). Si dentro de una misma skill hay varios puntos de delegación, todos usan **el mismo** mecanismo; prescribir la tool en uno y dejar "invoca" en los de al lado es la forma exacta del hueco.

- **Si delega por la tool `Agent`, pide `run_in_background: false`** — es la vía que devuelve el informe dentro de la propia llamada. **Donde hay barrera, es obligatorio y se dice por qué** ([[D-047]]): un fan-out de N delegados seguido de un paso que lee lo que escribieron **todos** (regenerar un índice, auditar el conjunto) solo se sostiene con **las N llamadas en un único mensaje + el flag**, que juntos dan una sola barrera para toda la tanda. Mensajes separados **serializan** el fan-out en cuanto el flag surte efecto.
- **Define qué es haber esperado, y hazlo autocomprobable — nombrando las vías legítimas ([[D-047]]).** Se ha esperado cuando **el informe del delegado está en el contexto porque se lo han entregado**, y eso ocurre por dos vías: el `tool_result` de la propia llamada `Agent`, o la **notificación de fin** del agente si el harness lo lanzó en segundo plano (se cede el turno y el informe llega en uno posterior). Lo que separa esperar de deducir no es en qué turno llega, es **quién lo trae**: que el artefacto exista, que su tamaño se estabilice, que un script dé veredicto sobre él o que **el agente vaya a leer** el `.output`/log del harness **no** cuenta.
  > Escribir el criterio con una sola vía tiene un coste medido (CU-3.a pasada 4): el agente eligió la notificación **10 de 10 veces**, esperó de forma impecable, y el contrato lo declaraba fallo. Una regla que la conducta correcta incumple deja de gobernar nada y genera FALLOS falsos (Regla 9.4 de conformance).
- **Da la salida sancionada, no solo la prohibición.** Prohibir sin decir qué hacer cuando el agente se ve sin resultado es invitarle a improvisar: entre "prohibido" y "tarea imposible", elige violar la prohibición. La salida es **parar y decirlo**, nunca reconstruir. Y **nunca presentar como dicho por el delegado un dato obtenido por cuenta propia** — sube con la misma apariencia de verdad y el error deja de notarse.
- **El delegado ejecuta la sub-skill; no la re-despacha ([[D-044]]).** Si el prompt dice *"Ejecuta el skill `/wf-X`"*, el delegado usará el `Skill` tool — y como toda `wf-*` worker lleva `context: fork`, eso **forkea un subagente más**. Cuando la sub-skill declara `agent:` y ese agente es el `subagent_type` que acabas de lanzar, el fork es un **clon del delegado**: un envoltorio que solo recibe el reporte del de abajo y lo re-emite. Medido: ~210 KB de contexto duplicado **por delegación**, y el salto extra vuelve a ser asíncrono. El prompt correcto le dice que **lea el `SKILL.md` y ejecute sus pasos él mismo**, le prohíbe el `Skill` tool, le resuelve `${CLAUDE_SKILL_DIR}` a `.claude/skills/<skill>/` y le pide qué informar al terminar.

El linter aplica esto como blocking: `FORK-ORCHESTRATOR`, `AGENT-DISPATCH-UNSYNCED` y `AGENT-PROMPT-REDISPATCH`.

**El primer plano se habilita en el proyecto, y solo se fija lo contrario ([[D-050]]).** El `settings.json` del ecosistema declara `CLAUDE_CODE_FORK_SUBAGENT=0`. Con fork mode activo —el default interactivo— el harness lanza los subagentes en segundo plano y **no evalúa ninguna petición de primer plano**: ni `run_in_background: false` en la llamada ni `background:` en el frontmatter del agente. Apagándolo, esas dos palancas vuelven a aplicar.

Sobre esa base, el frontmatter de un agente **solo se usa para fijar lo contrario**: `background: true` lo clava en segundo plano incluso cuando el llamante querría el resultado. El campo es **asimétrico** — existe el pin hacia background y **no existe pin hacia foreground** (medido: un `background: false` en `sdd-spec-explorer` no forzó nada). Así que:

- **Ningún agente del ecosistema lleva `background: true` hoy, y es a propósito.** El informe de todos ellos lo consume el paso siguiente: el analyze abre un gate, el discovery decide el subset, el fan-off de escritores tiene barrera en la regeneración del índice, el owner de una task se valida y se commitea sobre su reporte. La lista vacía es una decisión, no un olvido.
- **Añade el pin solo si el resultado de ese agente no lo consume nadie** — trabajo de fondo genuino, cuyo fallo o retraso no cambia el paso siguiente. Si dudas, no lo pongas: el coste de esperar de más es tiempo; el de no esperar es operar sobre un artefacto a medio escribir.
- **Y no escribas `background: false` esperando garantías.** No las da. Lo que pide el primer plano es el flag de la llamada, y lo que lo permite es la variable del proyecto.

**La frontera de un orquestador no es la tool, es cargar el artefacto ([[D-048]]).** [[D-030]]/[[D-031]]/[[D-038]] prohíben que el hilo principal haga `Read`/`Write` del artefacto, pero **no dicen nada de `Bash`** — y un `cat` y un `grep -A 12` meten el mismo texto en el mismo contexto. Con [[D-045]], los orquestadores corren en main y tienen `Bash`, así que la ocasión es constante. La línea que hay que escribir en cada Regla de oro: una **extracción acotada** es legítima si es **determinista** (patrón fijo), **delimitada** (`-c`, `-o`, `head` corto — no `-A`/`-B` generosos) y **de metadatos** (IDs, veredictos, recuentos, paths). Traer prosa del artefacto para interpretarla es analizar contenido, que es el trabajo del delegado — y normalmente el informe del delegado ya lo traía. *Medido dos veces en CU-3.a: un `grep -A 12` sobre el analysis después de tener el informe (pasada 2) y un `cat` del índice entero (pasada 4).*

**Quien escribe y quien lee buscan en el mismo sitio — y no encontrarlo no es una advertencia blanda ([[D-046]]).** Cuando una pieza escribe un artefacto y otra lo consume, las dos rutas se escriben **juntas y se comprueban a la vez**. Si divergen, el consumidor no falla: no encuentra nada y sigue con lo que sí tiene, produciendo un artefacto **parcial con apariencia de completo** — que es peor que un error, porque nadie lo revisa. Dos casos medidos en CU-3.a pasada 4, misma forma exacta:

- `sdd-features-index.py` buscaba el discovery **dentro de la raíz spec**; en topología `authoring` vive con el PRD. El índice registró **3 de 9** features y las 6 `PENDIENTE_GENERACIÓN` desaparecieron del hub.
- `wf-spec-readiness` buscaba `*_conflict_report.md` **solo en la raíz** de features; el fan-out de `wf-spec-features-first` los escribe **junto a cada spec**. El readiness se declaraba "sin análisis de conflictos" con N informes en disco.

Al escribir la pieza consumidora, pregúntate **quién produce esto y dónde lo deja en cada topología** (`artifacts.prd` != `artifacts.spec`) y **en cada layout** (subcarpeta de fase / plano legacy). Y cuando no aparezca lo que esperabas: **dilo en voz alta** — en el propio artefacto y por `stderr` si es un script. Una ausencia silenciosa se hereda pasada tras pasada.

**Una prohibición no nombra la herramienta ([[D-045]]).** El cuerpo de un `SKILL.md` **viaja al contexto del agente**: enumerar ahí las tools prohibidas se las **enseña**. Medido en CU-3.a pasada 3: la cláusula anti-sondeo nombraba `Monitor` —una tool *deferred*, que el agente no tenía cargada— y los dos forks fueron a buscarla (`ToolSearch select:Monitor`) justo después de delegar. Escribe la **conducta obligatoria** ("has esperado cuando tienes el informe"), no el catálogo de pecados. Las señales de FALLO sí pueden nombrar tools: viven en `conformance/`, que no se instala en el proyecto del usuario.

**Separación `description` / `when_to_use` (convención oficial de metadata de skills — SSoT):**

Esta es la regla canónica para los campos `description` y `when_to_use` del frontmatter de cualquier `SKILL.md` del ecosistema. Aplica el mismo contrato que Claude Code usa para enrutar skills.

- `description` (**TODAS** las skills, `kb-*` y `wf-*`): el QUÉ hace la skill, con el **caso de uso clave primero**. Conciso, **sin frases-trigger** ("activa cuando...", "úsalo si...", "en frases como..."). **Objetivo ≤ ~220 caracteres.** Es la señal con la que Claude decide aplicar la skill y alimenta el `skill-registry.md`. Recortar **preservando el significado**: no amputar; debe seguir describiendo con precisión qué hace y qué modos/agente soporta.
- `when_to_use` (**SOLO `wf-*`**): el CUÁNDO — frases de activación naturales **+ exclusiones explícitas** con la alternativa correcta ("No activa para X, usa `wf-Y`"). Lo necesario, sin relleno. Si una `description` de `wf-*` arrastra triggers dentro, **muévelos a `when_to_use`** y deja la `description` como el QUÉ.
- `kb-*` (`user-invocable: false`, se inyectan en agentes vía su frontmatter `skills:`, **no se enrutan** por el orquestador): **solo `description` lean**. NADA de `when_to_use` ni `argument-hint` — los triggers invitarían a auto-invocación no deseada y cuestan contexto eager. Si una `kb-*` aún tuviera `when_to_use` o `argument-hint`, **elimínalos**.
- **TOPE DURO:** el texto combinado `description` + `when_to_use` se trunca a **1.536 caracteres** en el listado de skills de Claude Code (límite oficial, para reducir uso de contexto). Nunca superarlo; si se supera, recortar.

No tocar `name`, `allowed-tools`, `effort`, `context`, `agent`, `user-invocable` ni el cuerpo de la skill al ajustar estos campos. Solo `description` y `when_to_use`.

**Criterio para `effort`:**
- `low`: <= 3 pasos simples, sin delegacion de agente
- `medium`: 3-6 pasos, puede delegar
- `high`: 6+ pasos o delegacion con contexto rico

**Criterio para `allowed-tools`:**
- `[Read]` — solo lectura o reporte
- `[Read, Write]` — lee y escribe artefactos sin shell
- `[Read, Write, Bash]` — necesita comandos shell (find, grep, lint, etc.)
- `[Read, Write, Bash, Agent]` — delega a agente especializado
- Añadir `WebSearch, WebFetch` solo si el workflow hace research externo

→ Template completo de frontmatter y cuerpo: `${CLAUDE_SKILL_DIR}/references/frontmatter-templates.md` y `${CLAUDE_SKILL_DIR}/references/body-templates.md`

## Frontmatter para agentes

**Criterio para `model`:**

El modelo se asigna por **tipo de trabajo**, no por si el agente genera un artefacto o no.

- `claude-opus-4-8`: agentes que toman **decisiones arquitectónicas** (diseño visual, arquitectura técnica, redacción de PRDs, autoría del ecosistema) o realizan **codificación agéntica compleja** (implementadores KMM). Usar también cuando el output esperado supera los 64k tokens.
- `claude-sonnet-4-6`: agentes que ejecutan **trabajo estructurado con template definido** (escritura de specs, descomposición de tasks), **exploración**, **auditoría** o **planificación de approach**. Sonnet 4.6 incluye extended thinking — para razonamiento en cadena con output <64k puede superar a Opus en precisión con menor coste.
- `claude-haiku-4-5`: **no usar en este ecosistema**. Su ventana de 200k tokens es insuficiente para agentes que cargan múltiples KBs + artefactos grandes simultáneamente.

Tabla de referencia:

| Tipo de trabajo | Modelo |
|---|---|
| Decisión arquitectónica (diseño, plan técnico, PRD, autoría de ecosistema) | `claude-opus-4-8` |
| Codificación agéntica compleja (implementadores KMM) | `claude-opus-4-8` |
| Escritura estructurada con template (specs, tasks) | `claude-sonnet-4-6` |
| Exploración, auditoría, planificación de approach | `claude-sonnet-4-6` |

**Criterio para `effort`:**
- `effort: high`: agentes escritores/implementadores que generan artefactos complejos (specs, planes técnicos, diseño, tasks, código). Activa razonamiento extendido independientemente del nivel de la sesión principal.
- Omitir (hereda de sesión): auditores, exploradores y planificadores de approach.

**Criterio para `disallowedTools`:**
- `disallowedTools: Write, Edit`: agentes auditores o planificadores cuyo system prompt declara explícitamente que **no modifican archivos**. Refuerza el contrato estructuralmente, no solo mediante instrucciones.
- No aplicar si el agente produce artefactos diagnósticos intermedios.

**Criterio para `skills`:**
- Solo cargar KBs que el agente usa en su razonamiento real
- Ordenar: KB del dominio propio → cross-fase → especializadas
- No cargar KBs de otras fases salvo que el agente sea transversal

→ Template completo (frontmatter + tabla de colores por fase): `${CLAUDE_SKILL_DIR}/references/frontmatter-templates.md`
→ Template de estructura del cuerpo: `${CLAUDE_SKILL_DIR}/references/body-templates.md`

## Referencias a archivos de soporte con `${CLAUDE_SKILL_DIR}`

Cuando una skill tiene archivos en su directorio (`references/`, `scripts/`, templates, etc.) y el cuerpo del `SKILL.md` los referencia para que el agente los lea, usar siempre la variable `${CLAUDE_SKILL_DIR}`:

```markdown
Ver formato completo en `${CLAUDE_SKILL_DIR}/references/output_template.md`
Ejecutar: `${CLAUDE_SKILL_DIR}/scripts/validate.sh`
```

`${CLAUDE_SKILL_DIR}` se sustituye por el path absoluto del directorio del `SKILL.md` antes de que el agente vea el contenido. Sin ella, el agente resuelve rutas relativas desde el directorio de trabajo actual — que no es el directorio de la skill — y los Read fallan silenciosamente.

No usar rutas relativas simples (`references/template.md`) ni paths hardcoded al proyecto.

## Prevencion de duplicados

Antes de crear cualquier artefacto, buscar si ya existe algo con el mismo dominio o responsabilidad:

```bash
find sdd/ -name "SKILL.md" | xargs grep -l "<dominio>"
find sdd/ -name "*.md" -path "*/agents/*" | xargs grep -l "<responsabilidad>"
```

Si existe algo similar:
1. Evaluar si es mejor extender la pieza existente (nueva regla o seccion)
2. Si la existente es demasiado ancha, extraer SSoT y hacer que delegue
3. Solo crear una pieza nueva si la responsabilidad es claramente distinta

**Señal de duplicado peligroso:** dos archivos que responden la misma pregunta con formulaciones distintas. Resolver siempre consolidando en la SSoT mas estable.

## Registro tras crear o actualizar piezas

→ Checklists completos (kb-*, wf-*, agente, CLAUDE.md): `${CLAUDE_SKILL_DIR}/references/checklists.md`
