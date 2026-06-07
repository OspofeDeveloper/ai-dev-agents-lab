# Plantillas de frontmatter

Plantillas de referencia para los tres tipos de piezas del ecosistema SDD. Copiar y adaptar. Los criterios de decisión para cada campo viven en el `SKILL.md` de `kb-sdd-creation-guide`.

---

## Plantilla: `kb-*`

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

---

## Plantilla: `wf-*`

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

Separación `description` / `when_to_use`:
- `description`: el QUÉ — funcionalidad, modos soportados, agente al que delega. Conciso, sin triggers.
- `when_to_use`: el CUÁNDO — frases de activación y exclusiones con alternativa. Omitir si no hay triggers relevantes.

---

## Plantilla: agente

```yaml
---
name: <nombre>
description: "<Razonamiento especializado. Artefactos que produce. Que NO cubre.>"
skills: [kb-<1>, kb-<2>, ...]
memory: project
permissionMode: acceptEdits
model: claude-opus-4-8 | claude-sonnet-4-6
effort: high                    # solo en agentes escritores/implementadores
disallowedTools: Write, Edit    # solo en auditores/planificadores puros
color: <color-por-fase>
---
```

Tabla de colores por fase/dominio:

| Fase / Dominio | Color |
|---|---|
| Meta / transversal SDD (`meta/agents/`) | `purple` |
| PRD (`prd/agents/`) | `blue` |
| Spec (`spec/agents/`) | `green` |
| Design (`design/agents/`) | `pink` |
| Plan (`plan/agents/`) | `orange` |
| Tasks (`tasks/agents/`) | `cyan` |
| Tech targets (`tech/*/agents/`) | `red` |
