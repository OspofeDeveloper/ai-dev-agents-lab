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

`context: fork` es obligatorio en las `wf-*` **worker**: las que generan artefactos por sí mismas. Van siempre con `agent:` y **no delegan**.

> [!IMPORTANT]
> **Una `wf-*` que delega NO lleva `context: fork`** ([[D-045]]): corre en el hilo principal, como
> `wf-prd-review` o `wf-spec-features-first`. Un fork no puede presentar gates (`AskUserQuestion`
> no existe en un subagente) y **no puede conseguir el primer plano para sus delegados** — con
> fork mode activo, el default interactivo, Claude Code los manda a background y el subagente no
> puede pedir lo contrario. Un fork que delega acaba parando para que main improvise la pregunta
> y **re-invoque el workflow entero**, o deduciendo del disco un resultado que no ha recibido.
>
> **Toda delegación por la tool `Agent` lleva `run_in_background: false`** ([[D-043]]), se nombra la
> tool exacta en **cada** punto del cuerpo —no "invoca `/wf-x`"— y se usa el mismo mecanismo en
> todos. El cuerpo define además **qué es haber esperado**: tener el informe del delegado como
> resultado de la propia llamada. Y el prompt del delegado le pide **leer el `SKILL.md` y ejecutar
> sus pasos él mismo**, nunca *"Ejecuta el skill `/wf-X`"* ([[D-044]]): eso le hace usar el `Skill`
> tool, que forkea **otro** subagente —un clon del delegado cuando la sub-skill declara ese mismo
> `agent:`— y reintroduce la asincronía un nivel más abajo. Lo verifica `sdd-structural-lint.py`
> (reglas `FORK-ORCHESTRATOR`, `AGENT-DISPATCH-UNSYNCED` y `AGENT-PROMPT-REDISPATCH`).

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
permissionMode: acceptEdits
model: claude-opus-4-8 | claude-sonnet-4-6
effort: high                    # solo en agentes escritores/implementadores
disallowedTools: Write, Edit    # solo en auditores/planificadores puros
color: <color-por-fase>
---
```

> [!IMPORTANT]
> **Ningún agente SDD declara `memory:`** ([[D-041]]). El estado del proyecto vive en sus
> **artefactos** —que es la premisa entera de SDD— y la memoria de agente es estado que
> sobrevive **fuera** de ellos: ningún gate, script ni check la ve, ninguna regeneración
> del artefacto la invalida, y nada garantiza que el agente prefiera el fichero a lo que
> recuerda. Si tu agente parece necesitar memoria, lo que necesita es **leer su artefacto**
> o recibir el dato en el brief. Lo verifica `sdd-structural-lint.py` (regla
> `AGENT-MEMORY-DECLARED`).

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
