---
name: kb-sdd-creation-guide
description: "Guia operativa para crear y registrar skills (kb-* y wf-*), agentes y actualizar el ecosistema SDD. Complementa kb-sdd-skill-architecture (que define cuando crear cada pieza) con el como: convenciones de nombrado, ubicacion por tipo y fase, plantillas de frontmatter, estructura de contenido y checklist de registro. Usar cuando se necesita saber como materializar una decision de diseno del ecosistema."
argument-hint: "[tipo: kb|wf|agent] [nombre] [fase]"
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KB SDD Creation Guide

Guia operativa para materializar decisiones de diseno del ecosistema SDD. Las reglas de _cuando_ y _por que_ crear cada pieza viven en `kb-sdd-skill-architecture`. Esta KB cubre el _como_.

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
- `design-architect` — rol architect en fase design
- `sdd-spec-writer` — rol writer en fase spec con prefijo ecosistema
- `plan-architect` — rol architect en fase plan
- `kmm-planner` — rol planner en stack kmm
- `sdd-author` — rol author transversal del ecosistema SDD

## Ubicacion segun tipo y alcance

| Tipo | Alcance | Directorio |
|---|---|---|
| `kb-*` | Fase unica | `sdd/<fase>/skills/kb-<nombre>/SKILL.md` |
| `kb-*` | Cross-fase o transversal | `sdd/.claude/skills/kb-<nombre>/SKILL.md` |
| `kb-*` | Stack, nivel plan | `sdd/tech/<stack>/skills/plan/kb-<nombre>/SKILL.md` |
| `kb-*` | Stack, nivel tasks | `sdd/tech/<stack>/skills/tasks/kb-<nombre>/SKILL.md` |
| `wf-*` | Fase unica | `sdd/<fase>/skills/wf-<nombre>/SKILL.md` |
| `wf-*` | Cross-fase o meta | `sdd/.claude/skills/wf-<nombre>/SKILL.md` |
| `wf-*` | Stack | `sdd/tech/<stack>/skills/wf-<stack>-<nombre>/SKILL.md` |
| Agente | Fase unica | `sdd/<fase>/agents/<nombre>.md` |
| Agente | Cross-fase o meta | `sdd/.claude/agents/<nombre>.md` |
| Agente | Stack | `sdd/tech/<stack>/agents/<nombre>.md` |

**Regla de resolucion de agentes:** cuando una `wf-*` declara `agent: <nombre>`, el agente se busca en el directorio `agents/` al mismo nivel que `skills/` dentro de la misma rama del directorio.

- Workflow en `sdd/design/skills/` → agente en `sdd/design/agents/`
- Workflow en `sdd/.claude/skills/` → agente en `sdd/.claude/agents/`
- Workflow en `sdd/tech/kmm/skills/` → agente en `sdd/tech/kmm/agents/`

## Frontmatter para `kb-*`

```yaml
---
name: kb-<nombre>
description: "<Que conocimiento normativo contiene. Cuando debe cargarse. Que NO cubre.>"
effort: low
allowed-tools: [Read]
user-invocable: false
---
```

Campos obligatorios: `name`, `description`, `effort`, `allowed-tools`, `user-invocable`.
Nunca añadir `context: fork`, `agent:` ni `argument-hint` a una `kb-*`.

## Estructura del cuerpo de una `kb-*`

Dos formatos son válidos; la elección depende del tipo de contenido:

**Formato A — Reglas numeradas (`## Regla N: <enunciado>`):** usar cuando la skill contiene reglas discretas y cross-referenciables. Permite que workflows y agentes citen "Regla N de kb-X". Es el formato preferido para la mayoría de `kb-*` técnicas y de stack.

**Formato B — Secciones descriptivas (`## <Título descriptivo>`):** usar cuando la skill describe un proceso, criterios de decisión complejos o tiene estructura narrativa. Apropiado para skills meta y skills con pocas reglas largas.

No mezclar ambos formatos dentro de una misma skill. Ambos son válidos; lo que no es válido es la inconsistencia interna.

Para `kb-*` de nivel `tasks/`, la estructura mínima recomendada es:
1. Referencia a la `kb-*` de nivel `plan/` equivalente (si existe)
2. Templates o código concreto por sección
3. Checklist de implementación (opcional pero recomendado)

## Frontmatter para `wf-*`

```yaml
---
name: wf-<nombre>
description: "<Qué pipeline orquesta y qué produce. Solo la funcionalidad — sin triggers ni exclusiones.>"
when_to_use: "<Frases de activación naturales. Exclusiones explícitas con alternativa (usa wf-X).>"
argument-hint: "<modo|accion> <input_principal> [flags...]"
effort: low|medium|high
allowed-tools: [Read] | [Read, Write] | [Read, Write, Bash] | [Read, Write, Bash, Agent]
context: fork
agent: <nombre-agente>   # solo si delega siempre al mismo agente
user-invocable: true
---
```

`context: fork` es obligatorio en todas las `wf-*` que generan artefactos o delegan a un agente.

**Separación `description` / `when_to_use`:**
- `description`: el QUÉ — funcionalidad, modos soportados, agente al que delega. Conciso, sin triggers.
- `when_to_use`: el CUÁNDO — frases de activación naturales ("genera specs del PRD", "crea el diseño visual") y exclusiones explícitas con la alternativa correcta ("no activa para X, usa wf-Y"). Si no hay triggers ni exclusiones relevantes, omitir el campo.

**Criterio para `effort`:**
- `low`: <= 3 pasos simples, sin delegacion de agente
- `medium`: 3-6 pasos, puede delegar
- `high`: 6+ pasos o delegacion con contexto rico

**Criterio para `allowed-tools`:**
- `[Read]` — solo lectura o reporte
- `[Read, Write]` — lee y escribe artefactos sin shell
- `[Read, Write, Bash]` — necesita comandos shell (find, grep, lint, etc.)
- `[Read, Write, Bash, Agent]` — delega a agente especializado
- Anadir `WebSearch, WebFetch` solo si el workflow hace research externo

## Estructura del cuerpo de una `wf-*`

Pasos numerados con encabezados `## Paso N: <accion>`. Cada paso incluye:

1. Que hace (una linea)
2. Que verifica o valida
3. Que produce o escribe
4. Como maneja bloqueos (con mensajes estandar)

Patron de mensajes de bloqueo:
```
> "❌ <condicion bloqueante>. <Accion correctiva con comando concreto>."
> "⚠ <advertencia no bloqueante>. <Descripcion del impacto>."
```

Ultimo paso siempre: informar al usuario del output generado y el siguiente paso sugerido.

## Frontmatter para agentes

```yaml
---
name: <nombre>
description: "<Razonamiento especializado. Artefactos que produce. Que NO cubre.>"
skills: [kb-<1>, kb-<2>, ...]
memory: project
permissionMode: acceptEdits
model: claude-opus-4-6 | claude-sonnet-4-6
effort: high                    # solo en agentes escritores/implementadores
disallowedTools: Write, Edit    # solo en auditores/planificadores puros
color: <color-por-fase>
---
```

**Criterio para `model`:**
- `claude-opus-4-6`: agentes que **generan artefactos** (specs, planes, diseños, tasks, PRDs, código) o tienen razonamiento técnico sostenido multi-paso con contexto rico.
- `claude-sonnet-4-6`: agentes que **leen, auditan, diagnostican o planifican el approach** sin producir un artefacto nuevo complejo (auditores, exploradores, planificadores de approach).

**Criterio para `effort`:**
- `effort: high`: agentes escritores/implementadores que generan artefactos complejos (specs, planes técnicos, diseño, tasks, código). Activa razonamiento extendido independientemente del nivel de la sesión principal.
- Omitir (hereda de sesión): auditores, exploradores y planificadores de approach — el nivel de sesión es suficiente para lectura y diagnóstico.

**Criterio para `disallowedTools`:**
- `disallowedTools: Write, Edit`: agentes auditores o planificadores cuyo system prompt declara explícitamente que **no modifican archivos**. Refuerza el contrato estructuralmente, no solo mediante instrucciones.
- No aplicar si el agente produce artefactos diagnósticos intermedios aunque no sea su rol principal (p.ej. un explorador que genera `_analysis.md` o `_discovery.md`).

**Criterio para `color` (por fase/dominio):**

| Fase / Dominio | Color |
|---|---|
| Meta / transversal SDD (`.claude/agents/`) | `purple` |
| PRD (`prd/agents/`) | `blue` |
| Spec (`spec/agents/`) | `green` |
| Design (`design/agents/`) | `pink` |
| Plan (`plan/agents/`) | `orange` |
| Tasks (`tasks/agents/`) | `cyan` |
| Tech targets (`tech/*/agents/`) | `red` |

**Criterio para `skills`:**
- Solo cargar KBs que el agente usa en su razonamiento real
- Ordenar: KB del dominio propio → cross-fase → especializadas
- No cargar KBs de otras fases salvo que el agente sea transversal

## Estructura del cuerpo de un agente

Secciones H2 fijas:

```markdown
## Skills disponibles
<lista de kb con una linea: que aporta cada una a este agente>

## Como operar
### Entrada que recibes
<lista de inputs esperados por el workflow o el orquestador>

### Proceso por modo
<subseccion por cada modo cognitivo que soporta el agente>

## Regla de oro
<maxima de una o dos lineas que define el limite del agente>

## Nota de evolucion (opcional)
<cuando conviene partir el agente; mantener como ancla para decision futura>
```

Secciones prohibidas en el cuerpo de un agente:
- listas de pasos shell o comandos a ejecutar (eso es una `wf-*`)
- politica global de frontmatters o arquitectura del ecosistema (eso es `kb-sdd-skill-architecture`)

## Checklist de registro tras crear una `kb-*`

- [ ] `SKILL.md` con frontmatter correcto en el directorio correcto
- [ ] Agente(s) que la consumen actualizados: añadir a su `skills: [...]`
- [ ] Si es cross-fase: documentar dependencia en el `CLAUDE.md` de la fase consumidora
- [ ] Si formaliza una regla que estaba inline en otros archivos: eliminar los duplicados
- [ ] Si tiene archivos de soporte: referencias usan `${CLAUDE_SKILL_DIR}/<path>`

## Referencias a archivos de soporte con `${CLAUDE_SKILL_DIR}`

Cuando una skill tiene archivos en su directorio (`references/`, `scripts/`, templates, etc.) y el cuerpo del `SKILL.md` los referencia para que el agente los lea, usar siempre la variable `${CLAUDE_SKILL_DIR}`:

```markdown
Ver formato completo en `${CLAUDE_SKILL_DIR}/references/output_template.md`
Ejecutar: `${CLAUDE_SKILL_DIR}/scripts/validate.sh`
```

`${CLAUDE_SKILL_DIR}` se sustituye por el path absoluto del directorio del `SKILL.md` antes de que el agente vea el contenido. Sin ella, el agente resuelve rutas relativas desde el directorio de trabajo actual — que no es el directorio de la skill — y los Read fallan silenciosamente.

No usar rutas relativas simples (`references/template.md`) ni paths hardcoded al proyecto.

## Checklist de registro tras crear una `wf-*`

- [ ] `SKILL.md` en el directorio correcto con `context: fork`
- [ ] `description` contiene solo la funcionalidad; triggers y exclusiones en `when_to_use`
- [ ] Entrada en el rootmap del `CLAUDE.md` de fase (o del orquestador global si es transversal)
- [ ] Si tiene `agent:`: verificar que el agente existe y acepta el modo operativo
- [ ] Precondiciones documentadas en el body del `SKILL.md`
- [ ] Output explicito: que archivo escribe y en que directorio
- [ ] Si tiene archivos de soporte: referencias usan `${CLAUDE_SKILL_DIR}/<path>`

## Checklist de registro tras crear un agente

- [ ] Archivo `.md` con frontmatter correcto en `agents/`
- [ ] `model` seleccionado según criterio escritor (`opus`) vs auditor/explorador (`sonnet`)
- [ ] `effort: high` añadido si el agente genera artefactos complejos
- [ ] `disallowedTools: Write, Edit` añadido si el system prompt declara que no escribe archivos (y el agente no produce artefactos diagnósticos intermedios)
- [ ] `color` asignado según fase/dominio del agente (tabla de criterios anterior)
- [ ] Sección `## Agentes disponibles` del `CLAUDE.md` de fase actualizada
- [ ] Todas las `kb-*` en `skills: [...]` existen fisicamente
- [ ] Si el agente es el target de una `wf-*`: verificar que `agent: <nombre>` apunta al nombre correcto

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

## Estructura de un `CLAUDE.md` de fase

Un `CLAUDE.md` de fase actúa como orquestador local: recibe intenciones del usuario, selecciona el workflow o agente correcto y describe handoffs. No define política global de skills ni duplica conocimiento de las `kb-*`.

Secciones H2 fijas:

```markdown
## Tu rol: <título del orquestador>
<Una o dos frases: qué hace y qué NO hace.>
<Ej: "No ejecutas el trabajo directamente. No construyes prompts manualmente.">

## Rootmap de workflow skills
| Intención del usuario | Skill | Argumentos |
|---|---|---|
| <frase de intención natural> | `/wf-<nombre>` | `<args>` |

## Cómo actuar ante una petición
<Reglas de matching semántico, patrones especiales y bloqueos. Solo lo que no cubre el rootmap.>

## Agentes disponibles  ← solo si los agentes son accesibles directamente desde el orquestador
| Agente | Dominio |
|---|---|
| `<nombre>` | <una línea de dominio> |
```

Secciones prohibidas en `CLAUDE.md`:
- plantillas de frontmatter o convenciones de nombrado (eso es `kb-sdd-creation-guide`)
- reglas de arquitectura transversal (eso es `kb-sdd-skill-architecture`)
- listas de pasos operativos (eso es una `wf-*`)
- descripción interna del razonamiento de skills o agentes

## Checklist para crear un nuevo `CLAUDE.md`

- [ ] Sección `## Tu rol` con límites explícitos (qué hace y qué NO hace)
- [ ] Rootmap completo con todas las `wf-*` y agentes accesibles desde esta fase
- [ ] Cada `wf-*` del rootmap existe físicamente en `skills/`
- [ ] Cada agente referenciado existe físicamente en `agents/`
- [ ] No duplica reglas de `kb-sdd-skill-architecture` ni `kb-sdd-creation-guide`
- [ ] No contiene plantillas de frontmatter, comandos shell ni listas de pasos operativos
- [ ] Si es un `CLAUDE.md` de fase: solo referencia agentes y skills de esa fase

## Checklist para actualizar un `CLAUDE.md` existente

- [ ] Nueva `wf-*` añadida al rootmap con intención, nombre y argumentos correctos
- [ ] Nuevo agente añadido a `## Agentes disponibles` si es accesible directamente
- [ ] Si se eliminó una `wf-*` o agente: entrada eliminada del rootmap
- [ ] Si se renombró: referencia actualizada en rootmap y sección de agentes
- [ ] Sección `## Cómo actuar` sigue siendo coherente con el estado actual del rootmap
