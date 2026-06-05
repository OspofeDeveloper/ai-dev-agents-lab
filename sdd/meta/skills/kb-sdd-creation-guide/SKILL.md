---
name: kb-sdd-creation-guide
description: "Guia operativa para crear y registrar skills (kb-* y wf-*), agentes y actualizar el ecosistema SDD. Complementa kb-sdd-skill-architecture (que define cuando crear cada pieza) con el como: convenciones de nombrado, ubicacion por tipo y fase, plantillas de frontmatter, estructura de contenido y checklist de registro. Usar cuando se necesita saber como materializar una decision de diseno del ecosistema."
argument-hint: "[tipo: kb|wf|agent] [nombre] [fase]"
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
- `design-architect` — rol architect en fase design
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

- Workflow en `sdd/design/skills/` → agente en `sdd/design/agents/`
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

`context: fork` es obligatorio en todas las `wf-*` que generan artefactos o delegan a un agente.

**Separación `description` / `when_to_use`:**
- `description`: el QUÉ — funcionalidad, modos soportados, agente al que delega. Conciso, sin triggers.
- `when_to_use`: el CUÁNDO — frases de activación naturales y exclusiones explícitas con la alternativa correcta. Si no hay triggers ni exclusiones relevantes, omitir el campo.

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

- `claude-opus-4-7`: agentes que toman **decisiones arquitectónicas** (diseño visual, arquitectura técnica, redacción de PRDs, autoría del ecosistema) o realizan **codificación agéntica compleja** (implementadores KMM). Usar también cuando el output esperado supera los 64k tokens.
- `claude-sonnet-4-6`: agentes que ejecutan **trabajo estructurado con template definido** (escritura de specs, descomposición de tasks), **exploración**, **auditoría** o **planificación de approach**. Sonnet 4.6 incluye extended thinking — para razonamiento en cadena con output <64k puede superar a Opus en precisión con menor coste.
- `claude-haiku-4-5`: **no usar en este ecosistema**. Su ventana de 200k tokens es insuficiente para agentes que cargan múltiples KBs + artefactos grandes simultáneamente.

Tabla de referencia:

| Tipo de trabajo | Modelo |
|---|---|
| Decisión arquitectónica (diseño, plan técnico, PRD, autoría de ecosistema) | `claude-opus-4-7` |
| Codificación agéntica compleja (implementadores KMM) | `claude-opus-4-7` |
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
