# Plantillas de frontmatter

Plantillas de referencia para los tres tipos de piezas del ecosistema SDD. Copiar y adaptar. Los criterios de decisión para cada campo viven en el `SKILL.md` de `kb-sdd-creation-guide`.

---

## Plantilla: `kb-*`

```yaml
---
name: kb-<nombre>
description: "<El QUÉ, caso de uso clave primero. Sin triggers. Objetivo <= ~220 caracteres. Puede cerrar con qué NO cubre.>"
effort: low
allowed-tools: [Read]
user-invocable: false
---
```

Campos obligatorios: `name`, `description`, `effort`, `allowed-tools`, `user-invocable`.
Nunca añadir `context: fork`, `agent:`, `when_to_use` ni `argument-hint` a una `kb-*`: no se enrutan, se inyectan en agentes vía su frontmatter `skills:`. Una `kb-*` lleva **solo `description` lean** (los triggers invitarían a auto-invocación no deseada y cuestan contexto eager). La regla canónica de `description`/`when_to_use` vive en el `SKILL.md` de `kb-sdd-creation-guide` (sección "Separación description / when_to_use").

---

## Plantilla: `wf-*`

```yaml
---
name: wf-<nombre>
description: "<El QUÉ: pipeline que orquesta, qué produce, modos/agente que soporta. Caso clave primero. Sin triggers. Objetivo <= ~220 caracteres.>"
when_to_use: "<El CUÁNDO: frases de activación naturales + exclusiones explícitas con alternativa (No activa para X, usa wf-Y).>"
argument-hint: "<modo|accion> <input_principal> [flags...]"
effort: low|medium|high
allowed-tools: [Read] | [Read, Write] | [Read, Write, Bash] | [Read, Write, Bash, Agent]
context: fork
agent: <nombre-agente>   # solo si delega siempre al mismo agente
user-invocable: true
---
```

`context: fork` es obligatorio en todas las `wf-*` que generan artefactos o delegan a un agente.

Separación `description` / `when_to_use` (regla canónica en el `SKILL.md` de `kb-sdd-creation-guide`):
- `description`: el QUÉ — funcionalidad, modos soportados, agente al que delega. Caso clave primero, conciso, **sin triggers**. Objetivo ≤ ~220 caracteres.
- `when_to_use` (**solo `wf-*`**): el CUÁNDO — frases de activación naturales **+ exclusiones explícitas** con la alternativa ("No activa para X, usa `wf-Y`"). Si una `description` arrastra triggers, muévelos aquí.
- **TOPE DURO:** `description` + `when_to_use` combinados ≤ **1.536 caracteres** (límite oficial del listado de skills de Claude Code, que trunca para reducir contexto). Si se supera, recortar.

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
